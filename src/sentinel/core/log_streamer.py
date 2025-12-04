"""
Log Streamer
============

Streams and parses logs from Kubernetes pods/jobs, extracting test events
and error signatures.
"""

import logging
import re
import threading
from datetime import datetime
from typing import Dict, List, Optional, Callable, Pattern
from queue import Queue

from kubernetes import client
from kubernetes.client.rest import ApiException

from src.sentinel.core.models import (
    RunContext,
    TestEvent,
    TestStatus,
    AnomalySeverity
)
from config.config_manager import ConfigManager


class LogStreamer:
    """
    Streams logs from Kubernetes pods and parses them into structured events.
    
    Recognizes:
    - Test markers (TEST_START, TEST_PASS, TEST_FAIL, etc.)
    - Suite markers (SUITE_START, SUITE_END)
    - Run markers (RUN_START, RUN_END)
    - Error signatures (exceptions, stack traces)
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        config: Optional[Dict] = None
    ):
        """
        Initialize log streamer.
        
        Args:
            config_manager: ConfigManager instance
            config: Configuration dictionary
        """
        self.config_manager = config_manager
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Kubernetes client
        self.core_v1: Optional[client.CoreV1Api] = None
        self._init_k8s_client()
        
        # Log patterns
        self.test_patterns = self._load_test_patterns()
        self.error_patterns = self._load_error_patterns()
        
        # Active streams
        self._active_streams: Dict[str, threading.Thread] = {}
        self._stream_queues: Dict[str, Queue] = {}
        self._streaming = False
        
        # Callbacks
        self.on_test_event_callbacks: List[Callable[[TestEvent, RunContext], None]] = []
        self.on_error_callbacks: List[Callable[[str, RunContext], None]] = []
        
        # Run contexts
        self._run_contexts: Dict[str, RunContext] = {}
    
    def _init_k8s_client(self):
        """Initialize Kubernetes client."""
        try:
            from kubernetes import config
            try:
                config.load_kube_config()
            except:
                config.load_incluster_config()
            
            self.core_v1 = client.CoreV1Api()
            self.logger.info("Kubernetes client initialized for log streaming")
        except Exception as e:
            self.logger.error(f"Failed to initialize K8s client: {e}")
    
    def _load_test_patterns(self) -> Dict[str, Pattern]:
        """Load regex patterns for test event detection."""
        patterns = {}
        
        # Default patterns
        default_patterns = {
            "TEST_START": re.compile(
                r"(?:TEST_START|test.*started|starting test).*?test[=:]\s*(?P<test_name>[^\s,]+)",
                re.IGNORECASE
            ),
            "TEST_PASS": re.compile(
                r"(?:TEST_PASS|test.*passed|PASSED).*?test[=:]\s*(?P<test_name>[^\s,]+)",
                re.IGNORECASE
            ),
            "TEST_FAIL": re.compile(
                r"(?:TEST_FAIL|test.*failed|FAILED).*?test[=:]\s*(?P<test_name>[^\s,]+)",
                re.IGNORECASE
            ),
            "TEST_SKIP": re.compile(
                r"(?:TEST_SKIP|test.*skipped|SKIPPED).*?test[=:]\s*(?P<test_name>[^\s,]+)",
                re.IGNORECASE
            ),
            "SUITE_START": re.compile(
                r"(?:SUITE_START|suite.*started|starting suite).*?suite[=:]\s*(?P<suite_name>[^\s,]+)",
                re.IGNORECASE
            ),
            "SUITE_END": re.compile(
                r"(?:SUITE_END|suite.*ended|completed suite).*?suite[=:]\s*(?P<suite_name>[^\s,]+)",
                re.IGNORECASE
            ),
            "RUN_START": re.compile(
                r"(?:RUN_START|run.*started|starting run)",
                re.IGNORECASE
            ),
            "RUN_END": re.compile(
                r"(?:RUN_END|run.*ended|completed run)",
                re.IGNORECASE
            ),
        }
        
        # Load from config or use defaults
        config_patterns = self.config.get("log_patterns", {})
        for event_type, pattern_str in config_patterns.items():
            try:
                patterns[event_type] = re.compile(pattern_str, re.IGNORECASE)
            except Exception as e:
                self.logger.warning(f"Invalid pattern for {event_type}: {e}")
        
        # Merge with defaults
        for event_type, pattern in default_patterns.items():
            if event_type not in patterns:
                patterns[event_type] = pattern
        
        return patterns
    
    def _load_error_patterns(self) -> List[Pattern]:
        """Load regex patterns for error detection."""
        patterns = []
        
        # Default error patterns
        default_patterns = [
            re.compile(r"\b(?:error|ERROR|Error)\b.*", re.IGNORECASE),
            re.compile(r"\b(?:exception|Exception|EXCEPTION)\b.*", re.IGNORECASE),
            re.compile(r"\b(?:failed|FAILED|Failed)\b.*", re.IGNORECASE),
            re.compile(r"\b(?:timeout|TIMEOUT|Timeout)\b.*", re.IGNORECASE),
            re.compile(r"\b(?:panic|PANIC|Panic)\b.*", re.IGNORECASE),
            re.compile(r"\b(?:fatal|FATAL|Fatal)\b.*", re.IGNORECASE),
            re.compile(r"\b(?:crash|CRASH|Crash)\b.*", re.IGNORECASE),
            re.compile(r"\btraceback\b.*", re.IGNORECASE),
            re.compile(r"\bstack trace\b.*", re.IGNORECASE),
        ]
        
        # Load from config
        config_patterns = self.config.get("error_patterns", [])
        for pattern_str in config_patterns:
            try:
                patterns.append(re.compile(pattern_str, re.IGNORECASE))
            except Exception as e:
                self.logger.warning(f"Invalid error pattern: {e}")
        
        # Merge with defaults
        patterns.extend(default_patterns)
        
        return patterns
    
    def register_run(self, context: RunContext):
        """Register a run context for log streaming."""
        self._run_contexts[context.run_id] = context
        self.logger.info(f"Registered run for log streaming: {context.run_id}")
        
        # Start streaming logs for pods in this run
        if context.k8s_pod_names:
            for pod_name in context.k8s_pod_names:
                self.start_streaming(pod_name, context.k8s_namespace or "default", context.run_id)
    
    def unregister_run(self, run_id: str):
        """Unregister a run and stop streaming its logs."""
        if run_id in self._run_contexts:
            del self._run_contexts[run_id]
            # Stop streams associated with this run
            streams_to_stop = [
                stream_id for stream_id in self._active_streams.keys()
                if stream_id.startswith(f"{run_id}:")
            ]
            for stream_id in streams_to_stop:
                self.stop_streaming(stream_id)
    
    def register_test_event_callback(
        self,
        callback: Callable[[TestEvent, RunContext], None]
    ):
        """Register callback for test events."""
        self.on_test_event_callbacks.append(callback)
    
    def register_error_callback(
        self,
        callback: Callable[[str, RunContext], None]
    ):
        """Register callback for error detection."""
        self.on_error_callbacks.append(callback)
    
    def start_streaming(self, pod_name: str, namespace: str, run_id: str):
        """
        Start streaming logs from a pod.
        
        Args:
            pod_name: Pod name
            namespace: Kubernetes namespace
            run_id: Associated run ID
        """
        if not self.core_v1:
            self.logger.warning("K8s client not initialized, cannot stream logs")
            return
        
        stream_id = f"{run_id}:{pod_name}:{namespace}"
        if stream_id in self._active_streams:
            self.logger.debug(f"Already streaming logs from {stream_id}")
            return
        
        # Create queue for log lines
        log_queue = Queue()
        self._stream_queues[stream_id] = log_queue
        
        # Start streaming thread
        stream_thread = threading.Thread(
            target=self._stream_pod_logs,
            args=(pod_name, namespace, run_id, log_queue),
            daemon=True,
            name=f"log-stream-{pod_name}"
        )
        stream_thread.start()
        self._active_streams[stream_id] = stream_thread
        
        self.logger.info(f"Started streaming logs from {pod_name} in {namespace}")
    
    def stop_streaming(self, stream_id: str):
        """Stop streaming logs from a pod."""
        if stream_id in self._active_streams:
            # Thread will stop when queue is closed or pod is deleted
            del self._active_streams[stream_id]
            if stream_id in self._stream_queues:
                del self._stream_queues[stream_id]
            self.logger.info(f"Stopped streaming logs: {stream_id}")
    
    def _stream_pod_logs(self, pod_name: str, namespace: str, run_id: str, log_queue: Queue):
        """Stream logs from a pod and process them."""
        try:
            # Get run context
            context = self._run_contexts.get(run_id)
            if not context:
                self.logger.warning(f"Run context not found: {run_id}")
                return
            
            # Stream logs
            w = client.Watch()
            for event in w.stream(
                self.core_v1.read_namespaced_pod_log,
                name=pod_name,
                namespace=namespace,
                follow=True,
                _preload_content=False
            ):
                if event['type'] == 'ERROR':
                    break
                
                log_line = event['object']
                if log_line:
                    # Process log line
                    self._process_log_line(log_line, pod_name, context)
        
        except ApiException as e:
            if e.status == 404:
                self.logger.debug(f"Pod {pod_name} not found (may have been deleted)")
            else:
                self.logger.error(f"Error streaming logs from {pod_name}: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error streaming logs: {e}", exc_info=True)
    
    def _process_log_line(self, log_line: str, source: str, context: RunContext):
        """
        Process a single log line and extract events.
        
        Args:
            log_line: Log line content
            source: Source identifier (pod name)
            context: RunContext
        """
        try:
            # Check for test events
            for event_type, pattern in self.test_patterns.items():
                match = pattern.search(log_line)
                if match:
                    test_event = self._create_test_event(event_type, match, log_line, source)
                    if test_event:
                        # Notify callbacks
                        for callback in self.on_test_event_callbacks:
                            try:
                                callback(test_event, context)
                            except Exception as e:
                                self.logger.error(f"Error in test event callback: {e}", exc_info=True)
                        break
            
            # Check for errors
            for error_pattern in self.error_patterns:
                if error_pattern.search(log_line):
                    # Notify error callbacks
                    for callback in self.on_error_callbacks:
                        try:
                            callback(log_line, context)
                        except Exception as e:
                            self.logger.error(f"Error in error callback: {e}", exc_info=True)
                    break
        
        except Exception as e:
            self.logger.error(f"Error processing log line: {e}", exc_info=True)
    
    def _create_test_event(
        self,
        event_type: str,
        match: re.Match,
        log_line: str,
        source: str
    ) -> Optional[TestEvent]:
        """Create a TestEvent from a regex match."""
        try:
            test_name = match.groupdict().get("test_name")
            suite_name = match.groupdict().get("suite_name")
            
            # Map event type to test status
            status_map = {
                "TEST_START": TestStatus.RUNNING,
                "TEST_PASS": TestStatus.PASSED,
                "TEST_FAIL": TestStatus.FAILED,
                "TEST_SKIP": TestStatus.SKIPPED,
            }
            status = status_map.get(event_type)
            
            return TestEvent(
                event_type=event_type,
                timestamp=datetime.now(),
                test_name=test_name,
                suite_name=suite_name,
                status=status,
                message=log_line,
                metadata={"source": source}
            )
        
        except Exception as e:
            self.logger.error(f"Error creating test event: {e}", exc_info=True)
            return None
    
    def stream_logs_from_job(self, job_name: str, namespace: str, run_id: str):
        """
        Stream logs from all pods belonging to a job.
        
        Args:
            job_name: Job name
            namespace: Kubernetes namespace
            run_id: Associated run ID
        """
        if not self.core_v1:
            return
        
        try:
            # Get pods for this job
            pods = self.core_v1.list_namespaced_pod(
                namespace=namespace,
                label_selector=f"job-name={job_name}"
            )
            
            for pod in pods.items:
                self.start_streaming(pod.metadata.name, namespace, run_id)
        
        except Exception as e:
            self.logger.error(f"Error streaming logs from job {job_name}: {e}", exc_info=True)




