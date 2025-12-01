"""
Kubernetes Watcher
=================

Continuously monitors Kubernetes resources (pods, jobs, services) in real time
and reports health events to the anomaly engine.
"""

import logging
import threading
from datetime import datetime
from typing import Dict, List, Optional, Callable, Set
from queue import Queue, Empty

from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException

from src.sentinel.core.models import (
    RunContext,
    PodHealthEvent,
    JobStatusEvent,
    AnomalySeverity,
    AnomalyCategory
)
from config.config_manager import ConfigManager


class K8sWatcher:
    """
    Watches Kubernetes resources for automation runs.
    
    Monitors:
    - Pods (phase, restarts, errors)
    - Jobs (status, failures)
    - Services (health)
    - Events (OOM, ImagePullBackOff, etc.)
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        namespaces: Optional[List[str]] = None,
        label_selectors: Optional[Dict[str, str]] = None
    ):
        """
        Initialize Kubernetes watcher.
        
        Args:
            config_manager: ConfigManager instance
            namespaces: List of namespaces to watch (default: all)
            label_selectors: Label selectors for filtering resources
        """
        self.config_manager = config_manager
        self.namespaces = namespaces or ["default", "panda"]
        self.label_selectors = label_selectors or {}
        self.logger = logging.getLogger(__name__)
        
        # Kubernetes clients
        self.core_v1: Optional[client.CoreV1Api] = None
        self.batch_v1: Optional[client.BatchV1Api] = None
        self.apps_v1: Optional[client.AppsV1Api] = None
        
        # Event queues
        self.pod_events: Queue = Queue()
        self.job_events: Queue = Queue()
        
        # Tracking
        self._watching = False
        self._watch_threads: List[threading.Thread] = []
        self._run_contexts: Dict[str, RunContext] = {}
        
        # Callbacks
        self.on_pod_event_callbacks: List[Callable[[PodHealthEvent, RunContext], None]] = []
        self.on_job_event_callbacks: List[Callable[[JobStatusEvent, RunContext], None]] = []
        
        # Initialize K8s clients
        self._init_k8s_clients()
    
    def _init_k8s_clients(self):
        """Initialize Kubernetes API clients."""
        try:
            # Try to load kubeconfig
            try:
                config.load_kube_config()
            except config.ConfigException:
                # Try in-cluster config
                config.load_incluster_config()
            
            # Create API clients
            self.core_v1 = client.CoreV1Api()
            self.batch_v1 = client.BatchV1Api()
            self.apps_v1 = client.AppsV1Api()
            
            self.logger.info("Kubernetes clients initialized successfully")
        
        except Exception as e:
            self.logger.error(f"Failed to initialize Kubernetes clients: {e}")
            self.logger.warning("K8sWatcher will operate in degraded mode")
    
    def register_run(self, context: RunContext):
        """
        Register a run context for monitoring.
        
        Args:
            context: RunContext to monitor
        """
        self._run_contexts[context.run_id] = context
        self.logger.info(f"Registered run for K8s monitoring: {context.run_id}")
    
    def unregister_run(self, run_id: str):
        """Unregister a run from monitoring."""
        if run_id in self._run_contexts:
            del self._run_contexts[run_id]
            self.logger.info(f"Unregistered run from K8s monitoring: {run_id}")
    
    def register_pod_event_callback(
        self,
        callback: Callable[[PodHealthEvent, RunContext], None]
    ):
        """Register callback for pod health events."""
        self.on_pod_event_callbacks.append(callback)
    
    def register_job_event_callback(
        self,
        callback: Callable[[JobStatusEvent, RunContext], None]
    ):
        """Register callback for job status events."""
        self.on_job_event_callbacks.append(callback)
    
    def start_watching(self):
        """Start watching Kubernetes resources."""
        if self._watching:
            self.logger.warning("K8sWatcher is already watching")
            return
        
        if not self.core_v1:
            self.logger.error("Kubernetes clients not initialized, cannot start watching")
            return
        
        self._watching = True
        
        # Start pod watcher thread
        pod_thread = threading.Thread(
            target=self._watch_pods,
            daemon=True,
            name="k8s-pod-watcher"
        )
        pod_thread.start()
        self._watch_threads.append(pod_thread)
        
        # Start job watcher thread
        job_thread = threading.Thread(
            target=self._watch_jobs,
            daemon=True,
            name="k8s-job-watcher"
        )
        job_thread.start()
        self._watch_threads.append(job_thread)
        
        self.logger.info("K8sWatcher started watching")
    
    def stop_watching(self):
        """Stop watching Kubernetes resources."""
        self._watching = False
        self.logger.info("K8sWatcher stopped watching")
    
    def _watch_pods(self):
        """Watch pods in configured namespaces."""
        while self._watching:
            try:
                for namespace in self.namespaces:
                    if not self._watching:
                        break
                    
                    try:
                        # Build label selector string
                        label_selector = self._build_label_selector()
                        
                        # Watch pods
                        w = watch.Watch()
                        for event in w.stream(
                            self.core_v1.list_namespaced_pod,
                            namespace=namespace,
                            label_selector=label_selector,
                            timeout_seconds=30
                        ):
                            if not self._watching:
                                break
                            
                            pod = event['object']
                            event_type = event['type']
                            
                            # Process pod event
                            self._process_pod_event(pod, event_type, namespace)
                    
                    except ApiException as e:
                        if e.status != 404:  # Namespace not found is OK
                            self.logger.error(f"Error watching pods in {namespace}: {e}")
                        continue
                    
                    except Exception as e:
                        self.logger.error(f"Unexpected error watching pods: {e}", exc_info=True)
                        continue
            
            except Exception as e:
                self.logger.error(f"Fatal error in pod watcher: {e}", exc_info=True)
                if self._watching:
                    import time
                    time.sleep(5)  # Back off before retrying
    
    def _watch_jobs(self):
        """Watch jobs in configured namespaces."""
        while self._watching:
            try:
                for namespace in self.namespaces:
                    if not self._watching:
                        break
                    
                    try:
                        # Build label selector string
                        label_selector = self._build_label_selector()
                        
                        # Watch jobs
                        w = watch.Watch()
                        for event in w.stream(
                            self.batch_v1.list_namespaced_job,
                            namespace=namespace,
                            label_selector=label_selector,
                            timeout_seconds=30
                        ):
                            if not self._watching:
                                break
                            
                            job = event['object']
                            event_type = event['type']
                            
                            # Process job event
                            self._process_job_event(job, event_type, namespace)
                    
                    except ApiException as e:
                        if e.status != 404:
                            self.logger.error(f"Error watching jobs in {namespace}: {e}")
                        continue
                    
                    except Exception as e:
                        self.logger.error(f"Unexpected error watching jobs: {e}", exc_info=True)
                        continue
            
            except Exception as e:
                self.logger.error(f"Fatal error in job watcher: {e}", exc_info=True)
                if self._watching:
                    import time
                    time.sleep(5)
    
    def _process_pod_event(self, pod, event_type: str, namespace: str):
        """Process a pod event and create PodHealthEvent."""
        try:
            # Extract pod information
            pod_name = pod.metadata.name
            phase = pod.status.phase
            
            # Get container statuses
            container_statuses = []
            if pod.status.container_statuses:
                for cs in pod.status.container_statuses:
                    container_statuses.append({
                        "name": cs.name,
                        "ready": cs.ready,
                        "restart_count": cs.restart_count,
                        "state": str(cs.state) if cs.state else None,
                        "last_state": str(cs.last_state) if cs.last_state else None,
                    })
            
            # Calculate total restarts
            total_restarts = sum(
                cs.restart_count for cs in pod.status.container_statuses or []
            )
            
            # Extract reason and message
            reason = None
            message = None
            if pod.status.container_statuses:
                for cs in pod.status.container_statuses:
                    if cs.state and cs.state.waiting:
                        reason = cs.state.waiting.reason
                        message = cs.state.waiting.message
                    elif cs.state and cs.state.terminated:
                        reason = cs.state.terminated.reason
                        message = cs.state.terminated.message
            
            # Create pod health event
            pod_event = PodHealthEvent(
                pod_name=pod_name,
                namespace=namespace,
                phase=phase,
                container_statuses=container_statuses,
                restarts=total_restarts,
                reason=reason,
                message=message,
                timestamp=datetime.now()
            )
            
            # Find associated run context
            run_context = self._find_run_context_for_pod(pod)
            
            # Notify callbacks
            for callback in self.on_pod_event_callbacks:
                try:
                    callback(pod_event, run_context)
                except Exception as e:
                    self.logger.error(f"Error in pod event callback: {e}", exc_info=True)
        
        except Exception as e:
            self.logger.error(f"Error processing pod event: {e}", exc_info=True)
    
    def _process_job_event(self, job, event_type: str, namespace: str):
        """Process a job event and create JobStatusEvent."""
        try:
            job_name = job.metadata.name
            status = job.status
            
            job_event = JobStatusEvent(
                job_name=job_name,
                namespace=namespace,
                status=event_type,
                succeeded=status.succeeded or 0,
                failed=status.failed or 0,
                active=status.active or 0,
                timestamp=datetime.now()
            )
            
            # Find associated run context
            run_context = self._find_run_context_for_job(job)
            
            # Notify callbacks
            for callback in self.on_job_event_callbacks:
                try:
                    callback(job_event, run_context)
                except Exception as e:
                    self.logger.error(f"Error in job event callback: {e}", exc_info=True)
        
        except Exception as e:
            self.logger.error(f"Error processing job event: {e}", exc_info=True)
    
    def _find_run_context_for_pod(self, pod) -> Optional[RunContext]:
        """Find RunContext associated with a pod."""
        pod_name = pod.metadata.name
        labels = pod.metadata.labels or {}
        annotations = pod.metadata.annotations or {}
        
        # Try to match by run-id label/annotation
        run_id = labels.get("run-id") or annotations.get("run-id")
        if run_id:
            return self._run_contexts.get(run_id)
        
        # Try to match by job name
        owner_refs = pod.metadata.owner_references or []
        for owner in owner_refs:
            if owner.kind == "Job":
                job_name = owner.name
                # Find run context with matching job name
                for context in self._run_contexts.values():
                    if context.k8s_job_name == job_name:
                        return context
        
        return None
    
    def _find_run_context_for_job(self, job) -> Optional[RunContext]:
        """Find RunContext associated with a job."""
        job_name = job.metadata.name
        
        # Try to match by job name
        for context in self._run_contexts.values():
            if context.k8s_job_name == job_name:
                return context
        
        # Try to match by run-id label/annotation
        labels = job.metadata.labels or {}
        annotations = job.metadata.annotations or {}
        run_id = labels.get("run-id") or annotations.get("run-id")
        if run_id:
            return self._run_contexts.get(run_id)
        
        return None
    
    def _build_label_selector(self) -> Optional[str]:
        """Build label selector string from label_selectors dict."""
        if not self.label_selectors:
            return None
        
        selectors = [f"{k}={v}" for k, v in self.label_selectors.items()]
        return ",".join(selectors)
    
    def get_pod_health(self, pod_name: str, namespace: str) -> Optional[PodHealthEvent]:
        """
        Get current health status of a specific pod.
        
        Args:
            pod_name: Pod name
            namespace: Namespace
            
        Returns:
            PodHealthEvent if found, None otherwise
        """
        if not self.core_v1:
            return None
        
        try:
            pod = self.core_v1.read_namespaced_pod(pod_name, namespace)
            self._process_pod_event(pod, "MODIFIED", namespace)
            # Event will be created by _process_pod_event
            return None  # Return value not used, event goes to callbacks
        except ApiException as e:
            self.logger.error(f"Error reading pod {pod_name}: {e}")
            return None




