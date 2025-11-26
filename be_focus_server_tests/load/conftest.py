"""
Pytest Configuration for Load Tests
===================================

Fixtures and configuration specific to load testing.
"""

import pytest
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


# ===================================================================
# Pytest Configuration
# ===================================================================

def pytest_configure(config):
    """Configure pytest for load tests."""
    # Register custom markers
    config.addinivalue_line(
        "markers", "load: Load testing marker"
    )
    config.addinivalue_line(
        "markers", "database: Database performance and query tests"
    )
    config.addinivalue_line(
        "markers", "network: Network bandwidth and connectivity tests"
    )
    config.addinivalue_line(
        "markers", "streaming: Streaming performance tests"
    )
    config.addinivalue_line(
        "markers", "baseline: Baseline performance tests"
    )
    config.addinivalue_line(
        "markers", "linear: Linear load progression tests"
    )
    config.addinivalue_line(
        "markers", "stress: Stress testing (high load)"
    )
    config.addinivalue_line(
        "markers", "soak: Soak testing (sustained load over time)"
    )
    config.addinivalue_line(
        "markers", "recovery: System recovery tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    for item in items:
        # Auto-mark slow tests
        if "stress" in item.keywords or "soak" in item.keywords:
            item.add_marker(pytest.mark.slow)


# ===================================================================
# Shared Fixtures
# ===================================================================

@pytest.fixture(scope="session")
def load_test_config() -> Dict[str, Any]:
    """
    קונפיגורציה משותפת לכל בדיקות העומס.
    """
    return {
        "default_timeout": 60,
        "max_retries": 3,
        "recovery_wait_time": 30,
        "between_tests_delay": 5
    }


@pytest.fixture(scope="function")
def cleanup_jobs(focus_server_api):
    """
    Fixture שמנקה jobs אחרי כל test.
    
    Usage:
        def test_something(focus_server_api, cleanup_jobs):
            # Your test code
            # Jobs will be cleaned up automatically after test
    """
    created_job_ids = []
    
    # Yield to test
    yield created_job_ids
    
    # Cleanup after test
    if created_job_ids:
        logger.info(f"Cleaning up {len(created_job_ids)} jobs...")
        for job_id in created_job_ids:
            try:
                focus_server_api.cancel_job(job_id)
            except Exception as e:
                logger.debug(f"Failed to clean up job {job_id}: {e}")


@pytest.fixture(scope="function")
def system_monitor():
    """
    Fixture למעקב אחר משאבי מערכת.
    
    Usage:
        def test_something(system_monitor):
            system_monitor.start()
            # Your test code
            metrics = system_monitor.stop()
    """
    import psutil
    from datetime import datetime
    
    class SystemMonitor:
        def __init__(self):
            self.monitoring = False
            self.samples = []
            self.start_time = None
            self.end_time = None
        
        def start(self):
            """התחל ניטור."""
            self.monitoring = True
            self.start_time = datetime.now()
            self.samples = []
            self._sample()
        
        def stop(self) -> Dict[str, Any]:
            """עצור ניטור והחזר מטריקות."""
            self.monitoring = False
            self.end_time = datetime.now()
            self._sample()
            
            if not self.samples:
                return {}
            
            cpu_values = [s['cpu'] for s in self.samples]
            mem_values = [s['memory'] for s in self.samples]
            
            return {
                'duration_seconds': (self.end_time - self.start_time).total_seconds(),
                'cpu': {
                    'mean': sum(cpu_values) / len(cpu_values),
                    'max': max(cpu_values),
                    'min': min(cpu_values)
                },
                'memory': {
                    'mean': sum(mem_values) / len(mem_values),
                    'max': max(mem_values),
                    'min': min(mem_values)
                },
                'samples_count': len(self.samples)
            }
        
        def _sample(self):
            """אסוף דגימה."""
            self.samples.append({
                'timestamp': datetime.now(),
                'cpu': psutil.cpu_percent(interval=0.1),
                'memory': psutil.virtual_memory().percent
            })
    
    return SystemMonitor()


# ===================================================================
# Hooks
# ===================================================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook לתיעוד תוצאות בדיקות.
    """
    outcome = yield
    report = outcome.get_result()
    
    # Log test results
    if report.when == "call":
        if report.passed:
            logger.info(f"✅ {item.name} - PASSED")
        elif report.failed:
            logger.error(f"❌ {item.name} - FAILED")
        elif report.skipped:
            logger.warning(f"⏭️ {item.name} - SKIPPED")

