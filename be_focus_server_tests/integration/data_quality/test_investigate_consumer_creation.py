"""
Test to investigate consumer creation issues.
"""

import pytest
import logging
import sys
import os
from pathlib import Path

# Add project root to path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.investigate_consumer_creation_issue import ConsumerCreationInvestigator
except ImportError as e:
    # Skip this test if the module is not available (e.g., in CI or missing dependencies)
    pytest.skip(f"investigate_consumer_creation_issue module not available: {e}", allow_module_level=True)

logger = logging.getLogger(__name__)


@pytest.mark.integration
@pytest.mark.data_quality
@pytest.mark.debug
def test_investigate_consumer_creation_issue():
    """
    Investigate consumer creation issue for a specific job_id.
    
    This test runs comprehensive investigation:
    1. Check Backend Logs
    2. Check MongoDB
    3. Check Consumer Service
    4. Check K8s Pods and Labels
    """
    job_id = "19-7"  # From the test run
    
    investigator = ConsumerCreationInvestigator(environment="staging")
    results = investigator.investigate(job_id)
    
    # Assertions
    assert results["job_id"] == job_id, f"Job ID mismatch: {results['job_id']} != {job_id}"
    
    # Log results summary
    logger.info("=" * 80)
    logger.info("INVESTIGATION COMPLETE")
    logger.info("=" * 80)
    
    # Don't fail the test - just report findings
    if results["mongodb"].get("status") == "error":
        logger.error("❌ MongoDB investigation failed")
    elif not results["mongodb"].get("job_found"):
        logger.warning("⚠️  Job not found in MongoDB")
    else:
        logger.info("✅ Job found in MongoDB")

