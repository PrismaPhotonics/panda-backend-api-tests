"""
Xray Integration Support for pytest
===================================

This module adds Xray integration to pytest without requiring
external plugins.

Features:
- Collect Xray test keys from @pytest.mark.xray markers
- Store test execution results
- Generate Xray JSON or enriched JUnit XML

Usage:
1. Add marker to test:
   @pytest.mark.xray("PZ-1234")
   def test_something():
       pass

2. Add multiple test keys:
   @pytest.mark.xray("PZ-2001", "PZ-2002")  # One test covers multiple Xray tests
   def test_comprehensive():
       pass

3. Mark Anchor Tests:
   @pytest.mark.anchor("PZ-5000")
   def test_high_level_workflow():
       pass
"""

import pytest
import logging
from datetime import datetime
from typing import List, Dict, Any
import json

logger = logging.getLogger(__name__)

# Store Xray keys per test
_xray_results: Dict[str, Dict[str, Any]] = {}


def pytest_configure(config):
    """Configure Xray markers."""
    config.addinivalue_line(
        "markers",
        "xray(test_keys...): Mark test with Xray test keys (e.g., PZ-1234)"
    )
    config.addinivalue_line(
        "markers",
        "anchor(test_key): Mark test as Xray Anchor Test"
    )


def pytest_runtest_makereport(item, call):
    """Store Xray test keys and results."""
    # Collect Xray test keys from markers
    xray_keys: List[str] = []
    
    # Get all xray markers
    for marker in item.iter_markers(name="xray"):
        xray_keys.extend(marker.args)
    
    # Get anchor marker (single key)
    anchor_marker = item.get_closest_marker("anchor")
    if anchor_marker and anchor_marker.args:
        xray_keys.extend(anchor_marker.args)
    
    # Store on item for later use
    if xray_keys:
        item._xray_keys = list(dict.fromkeys(xray_keys))  # Remove duplicates
        
        # Log Xray mapping
        logger.info(f"Test '{item.name}' → Xray: {item._xray_keys}")
    
    # Store results for Xray JSON generation
    if call.when == "call":
        # Test execution result
        outcome = "PASSED" if call.excinfo is None else "FAILED"
        
        # Create evidence list (for attachments)
        evidences = []
        if call.excinfo:
            evidences.append({
                "filename": f"{item.name}.log",
                "content": str(call.excinfo.value)
            })
        
        # Store results for each Xray key
        if hasattr(item, '_xray_keys'):
            for xray_key in item._xray_keys:
                if xray_key not in _xray_results:
                    _xray_results[xray_key] = {
                        "testKey": xray_key,
                        "status": outcome,
                        "start": datetime.now().isoformat(),
                        "finish": None,
                        "comment": f"Test: {item.name}",
                        "evidences": evidences
                    }
                else:
                    # Update existing entry
                    _xray_results[xray_key]["status"] = outcome
                    _xray_results[xray_key]["comment"] = f"{_xray_results[xray_key]['comment']}; {item.name}"
                    _xray_results[xray_key]["evidences"].extend(evidences)


def pytest_sessionfinish(session, exitstatus):
    """Generate Xray execution JSON at end of test run."""
    if not _xray_results:
        logger.info("No Xray test keys found in this run")
        return
    
    # Generate Xray JSON
    xray_json = {
        "info": {
            "summary": "Focus Server Automation - pytest execution",
            "description": f"Automated test execution completed with exit status: {exitstatus}",
            "startDate": datetime.now().isoformat(),
            "finishDate": datetime.now().isoformat(),
            "testPlanKey": None,  # Optional: Link to Test Plan
            "testEnvironments": [session.config.getoption("--environment", default="staging")]
        },
        "tests": list(_xray_results.values())
    }
    
    # Write to file
    import os
    os.makedirs("reports", exist_ok=True)
    
    output_file = "reports/xray-exec.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(xray_json, f, ensure_ascii=False, indent=2)
    
    logger.info(f"✅ Xray JSON written to: {output_file}")
    logger.info(f"📊 Total Xray tests in run: {len(_xray_results)}")


def get_xray_keys(item) -> List[str]:
    """Get Xray test keys for a test item."""
    if hasattr(item, '_xray_keys'):
        return item._xray_keys
    return []


def pytest_addoption(parser):
    """Add command-line options for Xray."""
    parser.addoption(
        "--xray",
        action="store_true",
        help="Enable Xray integration"
    )
    parser.addoption(
        "--environment",
        default="staging",
        help="Test environment name"
    )


@pytest.fixture
def xray_keys(request):
    """Fixture to access Xray test keys in test."""
    return getattr(request.node, '_xray_keys', [])

