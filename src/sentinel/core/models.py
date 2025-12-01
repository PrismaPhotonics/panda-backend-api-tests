"""
Data Models for Automation Run Sentinel
========================================

Defines all data structures used throughout the Sentinel system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Set, TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
    from typing import ForwardRef


class RunStatus(str, Enum):
    """Status of an automation run."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    STUCK = "stuck"


class AnomalySeverity(str, Enum):
    """Severity level of an anomaly."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AnomalyCategory(str, Enum):
    """Category of an anomaly."""
    INFRASTRUCTURE = "infrastructure"
    APPLICATION = "application"
    TEST = "test"
    STRUCTURE = "structure"


class TestStatus(str, Enum):
    """Status of a test case."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class RunContext:
    """
    Context for a single automation run.
    
    Contains all metadata and state for tracking a run from start to finish.
    """
    run_id: str = field(default_factory=lambda: str(uuid4()))
    pipeline: str = ""  # smoke, regression, nightly, load, etc.
    environment: str = ""  # staging, qa, perf, etc.
    branch: str = ""
    commit: str = ""
    triggered_by: str = ""  # user or schedule
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: RunStatus = RunStatus.PENDING
    
    # CI/CD metadata
    ci_run_id: Optional[str] = None
    ci_workflow_id: Optional[str] = None
    ci_job_id: Optional[str] = None
    
    # Kubernetes resources associated with this run
    k8s_job_name: Optional[str] = None
    k8s_namespace: Optional[str] = None
    k8s_pod_names: List[str] = field(default_factory=list)
    
    # Test structure
    suites: Dict[str, Any] = field(default_factory=dict)  # SuiteRun
    tests: Dict[str, Any] = field(default_factory=dict)  # TestCaseRun
    
    # Anomalies detected during run
    anomalies: List['Anomaly'] = field(default_factory=list)
    
    # Infrastructure snapshots
    infra_snapshots: List['InfraSnapshot'] = field(default_factory=list)
    
    def duration_seconds(self) -> Optional[float]:
        """Calculate run duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        elif self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return None
    
    def is_active(self) -> bool:
        """Check if run is currently active."""
        return self.status == RunStatus.RUNNING
    
    def total_tests(self) -> int:
        """Get total number of tests in this run."""
        return len(self.tests)
    
    def passed_tests(self) -> int:
        """Get number of passed tests."""
        return sum(1 for t in self.tests.values() if t.status == TestStatus.PASSED)
    
    def failed_tests(self) -> int:
        """Get number of failed tests."""
        return sum(1 for t in self.tests.values() if t.status == TestStatus.FAILED)


@dataclass
class SuiteRun:
    """Represents a test suite execution within a run."""
    suite_name: str
    run_id: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    test_ids: List[str] = field(default_factory=list)
    
    def duration_seconds(self) -> Optional[float]:
        """Calculate suite duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        elif self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return None


@dataclass
class TestCaseRun:
    """Represents a single test case execution."""
    test_id: str  # Unique test identifier
    test_name: str  # Human-readable test name
    suite_name: str
    run_id: str
    status: TestStatus = TestStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    # Test metadata
    tags: Set[str] = field(default_factory=set)
    xray_id: Optional[str] = None  # Jira Xray test ID
    markers: Set[str] = field(default_factory=set)  # pytest markers
    
    # Error information (if failed)
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None
    
    # Logs associated with this test
    log_lines: List[str] = field(default_factory=list)
    
    def duration_seconds(self) -> Optional[float]:
        """Calculate test duration in seconds."""
        if self.duration_seconds is not None:
            return self.duration_seconds
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        elif self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return None


@dataclass
class Anomaly:
    """Represents an anomaly detected during a run."""
    anomaly_id: str = field(default_factory=lambda: str(uuid4()))
    run_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    severity: AnomalySeverity = AnomalySeverity.WARNING
    category: AnomalyCategory = AnomalyCategory.INFRASTRUCTURE
    
    # Description
    title: str = ""
    description: str = ""
    
    # Context
    affected_component: Optional[str] = None  # pod name, service name, test name, etc.
    affected_pod: Optional[str] = None
    affected_service: Optional[str] = None
    affected_test: Optional[str] = None
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Root cause hints
    root_cause_hints: List[str] = field(default_factory=list)
    
    # Alert status
    alerted: bool = False
    alert_timestamp: Optional[datetime] = None


@dataclass
class InfraSnapshot:
    """Snapshot of infrastructure state at a point in time."""
    snapshot_id: str = field(default_factory=lambda: str(uuid4()))
    run_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Pod metrics
    pod_count: int = 0
    pod_restarts: int = 0
    pods_crash_loop: int = 0
    pods_image_pull_error: int = 0
    
    # Resource metrics (aggregated)
    avg_cpu_percent: Optional[float] = None
    avg_memory_percent: Optional[float] = None
    
    # Error counts
    error_count: int = 0
    warning_count: int = 0
    
    # Service health
    services_healthy: int = 0
    services_unhealthy: int = 0
    
    # Additional metrics
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestEvent:
    """Structured event parsed from logs."""
    event_type: str  # TEST_START, TEST_PASS, TEST_FAIL, SUITE_START, etc.
    timestamp: datetime = field(default_factory=datetime.now)
    test_name: Optional[str] = None
    suite_name: Optional[str] = None
    status: Optional[TestStatus] = None
    message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PodHealthEvent:
    """Event representing pod health status change."""
    pod_name: str
    namespace: str
    phase: str  # Pending, Running, Succeeded, Failed, etc.
    container_statuses: List[Dict[str, Any]] = field(default_factory=list)
    restarts: int = 0
    reason: Optional[str] = None
    message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class JobStatusEvent:
    """Event representing job status change."""
    job_name: str
    namespace: str
    status: str  # Active, Succeeded, Failed, etc.
    succeeded: int = 0
    failed: int = 0
    active: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class StructureRule:
    """Rule defining expected structure for a pipeline."""
    pipeline: str
    required_suites: List[str] = field(default_factory=list)
    forbidden_suites: List[str] = field(default_factory=list)
    required_tags: List[str] = field(default_factory=list)
    expected_test_count: Dict[str, int] = field(default_factory=dict)  # min, max
    required_test_ids: List[str] = field(default_factory=list)


@dataclass
class StructureViolation:
    """Represents a violation of structure rules."""
    violation_type: str  # MISSING_SUITE, FORBIDDEN_SUITE, TEST_COUNT_BELOW_MIN, etc.
    rule: StructureRule
    actual_value: Any
    expected_value: Any
    description: str
    timestamp: datetime = field(default_factory=datetime.now)

