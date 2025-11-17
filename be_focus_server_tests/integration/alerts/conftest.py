"""
Pytest Configuration for Alert Integration Tests
=================================================

This module provides fixtures and hooks specific to alert integration tests,
including automatic cleanup of alerts created during test execution.
"""

import pytest
import logging
from datetime import datetime
from typing import List, Set

from be_focus_server_tests.integration.alerts import alert_test_helpers
from be_focus_server_tests.integration.alerts.alert_test_helpers import (
    delete_alerts,
    authenticate_session
)

logger = logging.getLogger(__name__)

# Module-level set to track alert IDs created during test session
_alert_ids_created: Set[str] = set()


@pytest.fixture(scope="session", autouse=True)
def alert_test_session_cleanup(config_manager, request):
    """
    Automatic cleanup fixture for alert tests.
    
    This fixture:
    1. Initializes tracking of alert IDs created during tests
    2. Runs all tests
    3. Cleans up all alerts created during the session
    
    Args:
        config_manager: Configuration manager instance
        request: Pytest request object
    """
    # Initialize module-level set
    global _alert_ids_created
    _alert_ids_created.clear()
    
    # Set reference in alert_test_helpers module
    alert_test_helpers._alert_ids_created = _alert_ids_created
    
    logger.info("=" * 80)
    logger.info("ALERT TESTS SESSION: Starting")
    logger.info("Alert cleanup tracking initialized")
    logger.info("=" * 80)
    
    # Yield control to tests
    yield
    
    # Cleanup after all tests complete
    alert_ids = list(_alert_ids_created)
    logger.info("=" * 80)
    logger.info("ALERT TESTS SESSION: Cleanup")
    logger.info(f"Found {len(alert_ids)} alert IDs to cleanup")
    logger.info("=" * 80)
    
    if not alert_ids:
        logger.info("No alerts to cleanup")
        return
    
    try:
        # Get base URL for authentication
        api_config = config_manager.get("focus_server", {})
        base_url = api_config.get("frontend_api_url", "https://10.10.10.100/prisma/api/")
        if "/internal/sites/" in base_url:
            base_url = base_url.split("/internal/sites/")[0]
        if not base_url.endswith("/"):
            base_url += "/"
        
        # Create session for cleanup
        session = authenticate_session(base_url)
        
        # Delete alerts in batches
        batch_size = 100
        deleted_count = 0
        
        for i in range(0, len(alert_ids), batch_size):
            batch = alert_ids[i:i + batch_size]
            try:
                delete_alerts(
                    config_manager=config_manager,
                    alert_ids=batch,
                    base_url=base_url,
                    session=session
                )
                deleted_count += len(batch)
            except Exception as e:
                logger.error(f"Failed to delete alert batch {i//batch_size + 1}: {e}")
        
        logger.info("=" * 80)
        logger.info(f"ALERT TESTS SESSION: Cleanup completed")
        logger.info(f"Deleted {deleted_count}/{len(alert_ids)} alerts")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Failed to cleanup alerts after test session: {e}")
        logger.error("Alerts may remain in the system - manual cleanup may be required")

