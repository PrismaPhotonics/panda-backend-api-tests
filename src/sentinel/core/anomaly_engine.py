"""
Anomaly Engine
==============

Central brain for anomaly detection across infrastructure, application behavior, and tests.
"""

import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Set
from collections import defaultdict, deque

from src.sentinel.core.models import (
    RunContext,
    Anomaly,
    AnomalySeverity,
    AnomalyCategory,
    PodHealthEvent,
    JobStatusEvent,
    TestEvent,
    TestStatus,
    StructureViolation
)


class AnomalyEngine:
    """
    Detects anomalies in automation runs.
    
    Monitors:
    - Infrastructure (pod crashes, restarts, OOM)
    - Application (5xx spikes, DB errors, timeouts)
    - Test behavior (failure spikes, hanging tests, flaky tests)
    - Structure violations
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize anomaly engine.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Thresholds from config
        self.thresholds = self._load_thresholds()
        
        # Tracking state
        self._run_contexts: Dict[str, RunContext] = {}
        self._error_signatures: Set[str] = set()  # Known error signatures
        self._test_failure_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10))
        self._pod_restart_counts: Dict[str, int] = defaultdict(int)
        self._error_rate_windows: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Callbacks
        self.on_anomaly_callbacks: List[Callable[[Anomaly, RunContext], None]] = []
    
    def _load_thresholds(self) -> Dict:
        """Load anomaly detection thresholds from config."""
        defaults = {
            "pod_restart_threshold": 3,
            "pod_crash_loop_threshold": 2,
            "test_failure_rate_threshold": 0.5,  # 50%
            "test_stuck_threshold_minutes": 30,
            "error_rate_spike_threshold": 0.2,  # 20% increase
            "test_duration_deviation_threshold": 0.5,  # 50% increase
        }
        
        config_thresholds = self.config.get("anomaly_thresholds", {})
        defaults.update(config_thresholds)
        
        return defaults
    
    def register_run(self, context: RunContext):
        """Register a run for anomaly detection."""
        self._run_contexts[context.run_id] = context
        self.logger.debug(f"Registered run for anomaly detection: {context.run_id}")
    
    def unregister_run(self, run_id: str):
        """Unregister a run."""
        if run_id in self._run_contexts:
            del self._run_contexts[run_id]
            # Clean up tracking data
            self._pod_restart_counts = {
                k: v for k, v in self._pod_restart_counts.items()
                if not k.startswith(f"{run_id}:")
            }
    
    def register_anomaly_callback(
        self,
        callback: Callable[[Anomaly, RunContext], None]
    ):
        """Register callback for detected anomalies."""
        self.on_anomaly_callbacks.append(callback)
    
    def detect_pod_anomaly(
        self,
        pod_event: PodHealthEvent,
        context: RunContext
    ) -> Optional[Anomaly]:
        """
        Detect anomalies from pod health events.
        
        Args:
            pod_event: PodHealthEvent
            context: RunContext
            
        Returns:
            Anomaly if detected, None otherwise
        """
        anomalies = []
        
        # Check for CrashLoopBackOff
        if pod_event.reason == "CrashLoopBackOff":
            anomaly = Anomaly(
                run_id=context.run_id,
                timestamp=datetime.now(),
                severity=AnomalySeverity.CRITICAL,
                category=AnomalyCategory.INFRASTRUCTURE,
                title=f"Pod {pod_event.pod_name} in CrashLoopBackOff",
                description=(
                    f"Pod {pod_event.pod_name} in namespace {pod_event.namespace} "
                    f"is in CrashLoopBackOff state. Message: {pod_event.message or 'N/A'}"
                ),
                affected_pod=pod_event.pod_name,
                root_cause_hints=[
                    "Check pod logs for application errors",
                    "Verify resource limits",
                    "Check image pull permissions",
                    "Review recent deployment changes"
                ]
            )
            anomalies.append(anomaly)
        
        # Check for ImagePullBackOff
        elif pod_event.reason == "ImagePullBackOff":
            anomaly = Anomaly(
                run_id=context.run_id,
                timestamp=datetime.now(),
                severity=AnomalySeverity.CRITICAL,
                category=AnomalyCategory.INFRASTRUCTURE,
                title=f"Pod {pod_event.pod_name} ImagePullBackOff",
                description=(
                    f"Pod {pod_event.pod_name} cannot pull container image. "
                    f"Message: {pod_event.message or 'N/A'}"
                ),
                affected_pod=pod_event.pod_name,
                root_cause_hints=[
                    "Check image registry access",
                    "Verify image tag exists",
                    "Check image pull secrets"
                ]
            )
            anomalies.append(anomaly)
        
        # Check for excessive restarts
        pod_key = f"{context.run_id}:{pod_event.pod_name}"
        self._pod_restart_counts[pod_key] = pod_event.restarts
        
        if pod_event.restarts >= self.thresholds["pod_restart_threshold"]:
            anomaly = Anomaly(
                run_id=context.run_id,
                timestamp=datetime.now(),
                severity=AnomalySeverity.WARNING,
                category=AnomalyCategory.INFRASTRUCTURE,
                title=f"Pod {pod_event.pod_name} has {pod_event.restarts} restarts",
                description=(
                    f"Pod {pod_event.pod_name} has restarted {pod_event.restarts} times, "
                    f"exceeding threshold of {self.thresholds['pod_restart_threshold']}"
                ),
                affected_pod=pod_event.pod_name,
                metadata={"restart_count": pod_event.restarts},
                root_cause_hints=[
                    "Check pod logs for crash reasons",
                    "Review resource limits and requests",
                    "Check for OOM kills"
                ]
            )
            anomalies.append(anomaly)
        
        # Notify callbacks
        for anomaly in anomalies:
            self._notify_anomaly(anomaly, context)
        
        return anomalies[0] if anomalies else None
    
    def detect_job_anomaly(
        self,
        job_event: JobStatusEvent,
        context: RunContext
    ) -> Optional[Anomaly]:
        """
        Detect anomalies from job status events.
        
        Args:
            job_event: JobStatusEvent
            context: RunContext
            
        Returns:
            Anomaly if detected, None otherwise
        """
        if job_event.failed > 0:
            anomaly = Anomaly(
                run_id=context.run_id,
                timestamp=datetime.now(),
                severity=AnomalySeverity.CRITICAL,
                category=AnomalyCategory.INFRASTRUCTURE,
                title=f"Job {job_event.job_name} has {job_event.failed} failed pods",
                description=(
                    f"Job {job_event.job_name} in namespace {job_event.namespace} "
                    f"has {job_event.failed} failed pod(s)"
                ),
                affected_component=job_event.job_name,
                metadata={
                    "succeeded": job_event.succeeded,
                    "failed": job_event.failed,
                    "active": job_event.active
                },
                root_cause_hints=[
                    "Check job pod logs",
                    "Review job configuration",
                    "Check resource constraints"
                ]
            )
            self._notify_anomaly(anomaly, context)
            return anomaly
        
        return None
    
    def detect_test_anomaly(
        self,
        test_event: TestEvent,
        context: RunContext
    ) -> Optional[Anomaly]:
        """
        Detect anomalies from test events.
        
        Args:
            test_event: TestEvent
            context: RunContext
            
        Returns:
            Anomaly if detected, None otherwise
        """
        anomalies = []
        
        # Check for test failures
        if test_event.status == TestStatus.FAILED:
            test_name = test_event.test_name or "unknown"
            
            # Track failure history
            self._test_failure_history[test_name].append(datetime.now())
            
            # Check if test is flaky (fails intermittently)
            recent_failures = [
                t for t in self._test_failure_history[test_name]
                if (datetime.now() - t).total_seconds() < 3600  # Last hour
            ]
            
            if len(recent_failures) >= 3:
                anomaly = Anomaly(
                    run_id=context.run_id,
                    timestamp=datetime.now(),
                    severity=AnomalySeverity.WARNING,
                    category=AnomalyCategory.TEST,
                    title=f"Flaky test detected: {test_name}",
                    description=(
                        f"Test {test_name} has failed {len(recent_failures)} times "
                        f"in the last hour, indicating flakiness"
                    ),
                    affected_test=test_name,
                    metadata={"failure_count": len(recent_failures)},
                    root_cause_hints=[
                        "Review test for race conditions",
                        "Check for timing dependencies",
                        "Verify test data isolation"
                    ]
                )
                anomalies.append(anomaly)
        
        # Check for run stuck (no test events for threshold period)
        if test_event.event_type == "TEST_START":
            # Reset stuck timer
            pass
        else:
            # Check if run is stuck
            if context.start_time:
                time_since_start = (datetime.now() - context.start_time).total_seconds()
                if time_since_start > self.thresholds["test_stuck_threshold_minutes"] * 60:
                    if context.total_tests() == 0:
                        anomaly = Anomaly(
                            run_id=context.run_id,
                            timestamp=datetime.now(),
                            severity=AnomalySeverity.CRITICAL,
                            category=AnomalyCategory.TEST,
                            title=f"Run {context.run_id} appears stuck",
                            description=(
                                f"Run has been running for {time_since_start/60:.1f} minutes "
                                f"with no tests started"
                            ),
                            root_cause_hints=[
                                "Check if tests are actually running",
                                "Review test configuration",
                                "Check for infrastructure blocking tests"
                            ]
                        )
                        anomalies.append(anomaly)
        
        # Check failure rate
        if context.total_tests() > 0:
            failure_rate = context.failed_tests() / context.total_tests()
            if failure_rate > self.thresholds["test_failure_rate_threshold"]:
                anomaly = Anomaly(
                    run_id=context.run_id,
                    timestamp=datetime.now(),
                    severity=AnomalySeverity.CRITICAL,
                    category=AnomalyCategory.TEST,
                    title=f"High test failure rate: {failure_rate:.1%}",
                    description=(
                        f"Test failure rate {failure_rate:.1%} exceeds threshold "
                        f"of {self.thresholds['test_failure_rate_threshold']:.1%}"
                    ),
                    metadata={
                        "failure_rate": failure_rate,
                        "failed_tests": context.failed_tests(),
                        "total_tests": context.total_tests()
                    },
                    root_cause_hints=[
                        "Check for infrastructure issues",
                        "Review recent code changes",
                        "Check test data setup"
                    ]
                )
                anomalies.append(anomaly)
        
        # Notify callbacks
        for anomaly in anomalies:
            self._notify_anomaly(anomaly, context)
        
        return anomalies[0] if anomalies else None
    
    def detect_structure_violation(
        self,
        violation: StructureViolation,
        context: RunContext
    ) -> Anomaly:
        """
        Create anomaly from structure violation.
        
        Args:
            violation: StructureViolation
            context: RunContext
            
        Returns:
            Anomaly
        """
        # Determine severity based on violation type
        severity_map = {
            "MISSING_SUITE": AnomalySeverity.CRITICAL,
            "FORBIDDEN_SUITE": AnomalySeverity.WARNING,
            "TEST_COUNT_BELOW_MIN": AnomalySeverity.WARNING,
            "TEST_COUNT_ABOVE_MAX": AnomalySeverity.INFO,
            "MISSING_REQUIRED_TAG": AnomalySeverity.WARNING,
            "MISSING_REQUIRED_TEST": AnomalySeverity.CRITICAL,
        }
        
        severity = severity_map.get(violation.violation_type, AnomalySeverity.WARNING)
        
        anomaly = Anomaly(
            run_id=context.run_id,
            timestamp=violation.timestamp,
            severity=severity,
            category=AnomalyCategory.STRUCTURE,
            title=f"Structure violation: {violation.violation_type}",
            description=violation.description,
            metadata={
                "violation_type": violation.violation_type,
                "actual_value": violation.actual_value,
                "expected_value": violation.expected_value
            },
            root_cause_hints=[
                "Review pipeline configuration",
                "Check test selection criteria",
                "Verify test suite definitions"
            ]
        )
        
        self._notify_anomaly(anomaly, context)
        return anomaly
    
    def detect_error_signature(
        self,
        error_message: str,
        context: RunContext,
        source: str = "unknown"
    ) -> Optional[Anomaly]:
        """
        Detect new error signatures.
        
        Args:
            error_message: Error message
            context: RunContext
            source: Source identifier
            
        Returns:
            Anomaly if new signature detected, None otherwise
        """
        # Create signature hash
        error_hash = hashlib.md5(error_message.encode()).hexdigest()
        
        # Check if this is a known error
        if error_hash in self._error_signatures:
            return None  # Known error, not an anomaly
        
        # New error signature detected
        self._error_signatures.add(error_hash)
        
        anomaly = Anomaly(
            run_id=context.run_id,
            timestamp=datetime.now(),
            severity=AnomalySeverity.WARNING,
            category=AnomalyCategory.APPLICATION,
            title=f"New error signature detected in {source}",
            description=f"New error pattern detected: {error_message[:200]}...",
            affected_component=source,
            metadata={"error_hash": error_hash},
            root_cause_hints=[
                "Review application logs",
                "Check for recent code changes",
                "Verify external service dependencies"
            ]
        )
        
        self._notify_anomaly(anomaly, context)
        return anomaly
    
    def _notify_anomaly(self, anomaly: Anomaly, context: RunContext):
        """Notify all registered callbacks of an anomaly."""
        # Add to context
        context.anomalies.append(anomaly)
        
        # Notify callbacks
        for callback in self.on_anomaly_callbacks:
            try:
                callback(anomaly, context)
            except Exception as e:
                self.logger.error(f"Error in anomaly callback: {e}", exc_info=True)




