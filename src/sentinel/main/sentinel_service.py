"""
Sentinel Service
===============

Main service that orchestrates all Sentinel components.
"""

import logging
import threading
from typing import Dict, Optional

from config.config_manager import ConfigManager

from src.sentinel.core.run_context import RunContextManager
from src.sentinel.core.run_detector import RunDetector
from src.sentinel.core.k8s_watcher import K8sWatcher
from src.sentinel.core.log_streamer import LogStreamer
from src.sentinel.core.structure_analyzer import StructureAnalyzer
from src.sentinel.core.anomaly_engine import AnomalyEngine
from src.sentinel.core.run_history_store import RunHistoryStore
from src.sentinel.core.alert_dispatcher import AlertDispatcher
from src.sentinel.core.models import (
    RunContext,
    PodHealthEvent,
    JobStatusEvent,
    TestEvent,
    StructureViolation
)


class SentinelService:
    """
    Main service that orchestrates all Sentinel components.
    
    Coordinates:
    - Run detection
    - Kubernetes monitoring
    - Log streaming
    - Structure analysis
    - Anomaly detection
    - Alerting
    - History storage
    """
    
    def __init__(self, config_manager: ConfigManager, config: Optional[Dict] = None):
        """
        Initialize Sentinel service.
        
        Args:
            config_manager: ConfigManager instance
            config: Sentinel-specific configuration
        """
        self.config_manager = config_manager
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.context_manager = RunContextManager()
        self.run_detector = RunDetector(self.context_manager, self.config)
        self.k8s_watcher = K8sWatcher(
            config_manager,
            namespaces=self.config.get("k8s_namespaces", ["default", "panda"]),
            label_selectors=self.config.get("k8s_label_selectors", {})
        )
        self.log_streamer = LogStreamer(config_manager, self.config)
        self.structure_analyzer = StructureAnalyzer(self.config)
        self.anomaly_engine = AnomalyEngine(self.config)
        self.history_store = RunHistoryStore(self.config)
        self.alert_dispatcher = AlertDispatcher(self.config)
        
        # Service state
        self._running = False
        self._shutdown_event = threading.Event()
        
        # Wire up component callbacks
        self._wire_callbacks()
    
    def _wire_callbacks(self):
        """Wire up callbacks between components."""
        # Run detector -> K8s watcher, log streamer
        self.run_detector.register_run_start_callback(self._on_run_start)
        self.run_detector.register_run_end_callback(self._on_run_end)
        
        # K8s watcher -> Anomaly engine
        self.k8s_watcher.register_pod_event_callback(self._on_pod_event)
        self.k8s_watcher.register_job_event_callback(self._on_job_event)
        
        # Log streamer -> Structure analyzer, anomaly engine
        self.log_streamer.register_test_event_callback(self._on_test_event)
        self.log_streamer.register_error_callback(self._on_error)
        
        # Anomaly engine -> Alert dispatcher
        self.anomaly_engine.register_anomaly_callback(self._on_anomaly)
    
    def start(self):
        """Start the Sentinel service."""
        if self._running:
            self.logger.warning("Sentinel service is already running")
            return
        
        self.logger.info("Starting Automation Run Sentinel service...")
        
        # Start K8s watcher
        self.k8s_watcher.start_watching()
        
        # Start log streaming (will be activated per-run)
        # self.log_streamer is ready but not actively streaming yet
        
        self._running = True
        self.logger.info("Sentinel service started successfully")
    
    def stop(self):
        """Stop the Sentinel service."""
        if not self._running:
            return
        
        self.logger.info("Stopping Sentinel service...")
        
        self._running = False
        self._shutdown_event.set()
        
        # Stop K8s watcher
        self.k8s_watcher.stop_watching()
        
        # Stop log streaming
        # Log streams will stop when pods/jobs are deleted
        
        self.logger.info("Sentinel service stopped")
    
    def detect_run_from_webhook(self, webhook_data: Dict) -> Optional[RunContext]:
        """
        Detect run from CI/CD webhook.
        
        Args:
            webhook_data: Webhook payload
            
        Returns:
            RunContext if detected, None otherwise
        """
        return self.run_detector.detect_from_webhook(webhook_data)
    
    def detect_run_from_k8s_job(
        self,
        job_name: str,
        namespace: str,
        labels: Dict[str, str],
        annotations: Dict[str, str]
    ) -> Optional[RunContext]:
        """
        Detect run from Kubernetes Job.
        
        Args:
            job_name: Job name
            namespace: Kubernetes namespace
            labels: Job labels
            annotations: Job annotations
            
        Returns:
            RunContext if detected, None otherwise
        """
        return self.run_detector.detect_from_k8s_job(job_name, namespace, labels, annotations)
    
    def process_log_line(self, log_line: str, source: str = "unknown") -> Optional[RunContext]:
        """
        Process a log line for run detection.
        
        Args:
            log_line: Log line content
            source: Source identifier
            
        Returns:
            RunContext if detected, None otherwise
        """
        return self.run_detector.detect_from_log(log_line, source)
    
    def _on_run_start(self, context: RunContext):
        """Handle run start event."""
        self.logger.info(f"Run started: {context.run_id}")
        
        # Register with components
        self.k8s_watcher.register_run(context)
        self.log_streamer.register_run(context)
        self.anomaly_engine.register_run(context)
        
        # Mark as running
        self.context_manager.mark_running(context.run_id)
        
        # Start streaming logs from job if available
        if context.k8s_job_name and context.k8s_namespace:
            self.log_streamer.stream_logs_from_job(
                context.k8s_job_name,
                context.k8s_namespace,
                context.run_id
            )
    
    def _on_run_end(self, context: RunContext):
        """Handle run end event."""
        self.logger.info(f"Run ended: {context.run_id}")
        
        # Perform final structure analysis
        violations = self.structure_analyzer.analyze_run_structure(context)
        for violation in violations:
            anomaly = self.anomaly_engine.detect_structure_violation(violation, context)
        
        # Save to history
        self.history_store.save_run(context)
        
        # Update baseline
        self.structure_analyzer.update_baseline(context)
        
        # Unregister from components
        self.k8s_watcher.unregister_run(context.run_id)
        self.log_streamer.unregister_run(context.run_id)
        self.anomaly_engine.unregister_run(context.run_id)
    
    def _on_pod_event(self, pod_event: PodHealthEvent, context: Optional[RunContext]):
        """Handle pod health event."""
        if not context:
            return
        
        # Detect anomalies
        anomaly = self.anomaly_engine.detect_pod_anomaly(pod_event, context)
        
        # Update context with pod information
        if pod_event.pod_name not in context.k8s_pod_names:
            context.k8s_pod_names.append(pod_event.pod_name)
    
    def _on_job_event(self, job_event: JobStatusEvent, context: Optional[RunContext]):
        """Handle job status event."""
        if not context:
            return
        
        # Detect anomalies
        anomaly = self.anomaly_engine.detect_job_anomaly(job_event, context)
    
    def _on_test_event(self, test_event: TestEvent, context: RunContext):
        """Handle test event."""
        # Update context with test information
        if test_event.test_name:
            test_id = f"{test_event.suite_name}:{test_event.test_name}" if test_event.suite_name else test_event.test_name
            
            if test_id not in context.tests:
                from src.sentinel.core.models import TestCaseRun, TestStatus
                test_case = TestCaseRun(
                    test_id=test_id,
                    test_name=test_event.test_name,
                    suite_name=test_event.suite_name or "unknown",
                    run_id=context.run_id,
                    status=test_event.status or TestStatus.PENDING,
                    start_time=test_event.timestamp if test_event.event_type == "TEST_START" else None,
                    end_time=test_event.timestamp if test_event.event_type in ["TEST_PASS", "TEST_FAIL", "TEST_SKIP"] else None
                )
                context.tests[test_id] = test_case
            else:
                test_case = context.tests[test_id]
                if test_event.status:
                    test_case.status = test_event.status
                if test_event.event_type in ["TEST_PASS", "TEST_FAIL", "TEST_SKIP"]:
                    test_case.end_time = test_event.timestamp
                    if test_case.start_time:
                        test_case.duration_seconds = (test_event.timestamp - test_case.start_time).total_seconds()
            
            # Update suite
            if test_event.suite_name:
                if test_event.suite_name not in context.suites:
                    from src.sentinel.core.models import SuiteRun
                    suite = SuiteRun(
                        suite_name=test_event.suite_name,
                        run_id=context.run_id,
                        start_time=test_event.timestamp if test_event.event_type == "SUITE_START" else None
                    )
                    context.suites[test_event.suite_name] = suite
                else:
                    suite = context.suites[test_event.suite_name]
                    if test_event.event_type == "SUITE_END":
                        suite.end_time = test_event.timestamp
                    suite.test_ids.append(test_id)
                    if test_case.status == TestStatus.PASSED:
                        suite.passed_tests += 1
                    elif test_case.status == TestStatus.FAILED:
                        suite.failed_tests += 1
                    elif test_case.status == TestStatus.SKIPPED:
                        suite.skipped_tests += 1
                    suite.total_tests += 1
        
        # Detect anomalies
        anomaly = self.anomaly_engine.detect_test_anomaly(test_event, context)
    
    def _on_error(self, error_message: str, context: RunContext):
        """Handle error detection."""
        # Detect new error signatures
        anomaly = self.anomaly_engine.detect_error_signature(error_message, context)
    
    def _on_anomaly(self, anomaly, context: RunContext):
        """Handle anomaly detection."""
        # Dispatch alert
        self.alert_dispatcher.dispatch_anomaly(anomaly, context)
    
    def get_run(self, run_id: str) -> Optional[RunContext]:
        """Get a run context by ID."""
        return self.context_manager.get_context(run_id)
    
    def get_active_runs(self) -> Dict[str, RunContext]:
        """Get all active runs."""
        return self.context_manager.get_active_runs()
    
    def query_runs(self, **filters) -> list:
        """Query historical runs."""
        return self.history_store.query_runs(**filters)




