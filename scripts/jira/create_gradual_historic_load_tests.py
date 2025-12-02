#!/usr/bin/env python3
"""
Create Gradual Historic Load Tests in Jira Xray
================================================

Creates Test Cases for Gradual Historic Job Load Tests.

Tests Created:
- PZ-LOAD-400: Gradual Load to 100 Jobs
- PZ-LOAD-401: Quick Gradual Load
- PZ-LOAD-402: Gradual Load Health Tracking
- PZ-LOAD-403: Gradual Load Cleanup Verification
- PZ-LOAD-410: High Concurrency Gradual

Total: 5 Test Cases

Usage:
    python scripts/jira/create_gradual_historic_load_tests.py
    python scripts/jira/create_gradual_historic_load_tests.py --dry-run

Author: QA Automation Architect
Date: 2025-12-02
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# GRADUAL HISTORIC LOAD TESTS
# =============================================================================

GRADUAL_HISTORIC_LOAD_TESTS = {
    "LOAD-400": {
        "summary": "Load - Historic - Gradual Load to 100 Jobs",
        "description": """h2. Objective
Verify that system handles gradual load increase from 5 to 100 concurrent Historic jobs.

h2. Background
This test uses the SAME intervals as Live gradual load tests for consistency:
* Initial: 5 jobs
* Step Increment: +5 jobs every 10 seconds
* Maximum: 100 jobs

This allows direct comparison between Live and Historic performance under similar load patterns.

h2. Pre-Conditions
* Focus Server API is running
* MongoDB base_paths collection contains recordings
* Recordings available for Historic playback
* gRPC services are available

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Start with 5 Historic jobs | Using MongoDB recordings | 5 jobs created |
| 2 | Wait 10 seconds | Step interval | Interval elapsed |
| 3 | Add 5 more jobs | Total: 10 jobs | 10 jobs running |
| 4 | Verify health at step | Check API and job connectivity | Health status recorded |
| 5 | Repeat steps 2-4 | Until 100 jobs reached | Load increases gradually |
| 6 | Final health check | At maximum load | System health verified |
| 7 | Cleanup all jobs | Disconnect gRPC | All jobs cleaned |

h2. Expected Result
* At least 70% of steps should pass health check
* System should remain responsive under load
* Maximum 100 concurrent jobs reached
* Cleanup completes successfully (90%+ jobs cleaned)

h2. Health Status Criteria
* ✅ HEALTHY: >= 50% jobs connected
* ⚠️ DEGRADED: 30-50% jobs connected
* ❌ UNHEALTHY: < 30% jobs connected

h2. Assertions
* Max jobs reached >= 80
* Steps healthy >= 70% of total steps
* Cleanup ratio >= 90%

h2. Automation Status
✅ Automated

*Test Function:* `test_gradual_load_to_100_jobs`
*Test File:* `be_focus_server_tests/load/test_gradual_historic_load.py`
*Test Class:* `TestGradualHistoricJobLoad`
*Xray Marker:* `PZ-LOAD-400`
*Test Type:* Gradual Load Test (Step-by-Step)

h2. Related Tests
* PZ-LOAD-300: Live Gradual Load (same intervals for comparison)
* PZ-LOAD-401: Quick Gradual Load (faster version)
""",
        "priority": "High",
        "labels": ["load", "historic", "gradual_load", "capacity", "automation", "job_load", "mongodb"],
        "components": ["focus-server", "grpc", "mongodb"]
    },
    "LOAD-401": {
        "summary": "Load - Historic - Quick Gradual Load (2→10 Jobs)",
        "description": """h2. Objective
Verify gradual load mechanism works correctly with a faster, smaller-scale test.

h2. Background
This is a faster version suitable for CI/CD pipelines:
* Initial: 2 jobs
* Step Increment: +2 jobs every 5 seconds
* Maximum: 10 jobs

h2. Pre-Conditions
* Focus Server API is running
* MongoDB base_paths collection contains recordings
* gRPC services are available

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Start with 2 Historic jobs | Using MongoDB recordings | 2 jobs created |
| 2 | Wait 5 seconds | Step interval | Interval elapsed |
| 3 | Add 2 more jobs | Total: 4 jobs | 4 jobs running |
| 4 | Repeat until 10 jobs | Continue adding | 10 jobs reached |
| 5 | Verify health | Check system status | Health verified |
| 6 | Cleanup | Disconnect all jobs | Cleanup complete |

h2. Expected Result
* At least 3 steps completed
* Maximum 6+ concurrent jobs reached
* Cleanup successful

h2. Automation Status
✅ Automated

*Test Function:* `test_quick_gradual_load`
*Test File:* `be_focus_server_tests/load/test_gradual_historic_load.py`
*Test Class:* `TestGradualHistoricJobLoad`
*Xray Marker:* `PZ-LOAD-401`
*Test Type:* Quick Gradual Load Test (CI/CD)

h2. Use Cases
* CI/CD pipeline validation
* Quick smoke testing
* Development testing
""",
        "priority": "Medium",
        "labels": ["load", "historic", "gradual_load", "quick", "ci", "automation", "job_load"],
        "components": ["focus-server", "grpc"]
    },
    "LOAD-402": {
        "summary": "Load - Historic - Gradual Load Health Tracking",
        "description": """h2. Objective
Verify that health status is properly tracked during gradual load increase and system doesn't become unhealthy during normal load progression.

h2. Pre-Conditions
* Focus Server API is running
* MongoDB base_paths collection contains recordings
* System in healthy state

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Start gradual load test | 5 → 100 jobs | Test running |
| 2 | Track health at each step | Monitor API and jobs | Health recorded |
| 3 | Calculate health ratio | Healthy steps / Total steps | Ratio calculated |
| 4 | Verify health progression | Check step-by-step status | Progression logged |
| 5 | Analyze health trends | Identify degradation patterns | Trends identified |

h2. Expected Result
* At least 5 steps completed
* At least 60% of steps are healthy
* Health progression tracked and logged
* No unexpected degradation detected

h2. Health Tracking Metrics
* Step number
* Target jobs vs actual jobs
* Success rate per step
* Health status (HEALTHY/DEGRADED/UNHEALTHY)
* API response time
* Job connectivity ratio

h2. Automation Status
✅ Automated

*Test Function:* `test_gradual_load_health_tracking`
*Test File:* `be_focus_server_tests/load/test_gradual_historic_load.py`
*Test Class:* `TestGradualHistoricJobLoad`
*Xray Marker:* `PZ-LOAD-402`
*Test Type:* Health Monitoring Test

h2. Analysis
This test provides valuable insights into:
* System capacity limits
* Performance degradation patterns
* Breaking point identification
* Resource utilization trends
""",
        "priority": "High",
        "labels": ["load", "historic", "gradual_load", "health", "monitoring", "automation", "job_load"],
        "components": ["focus-server", "grpc", "monitoring"]
    },
    "LOAD-403": {
        "summary": "Load - Historic - Gradual Load Cleanup Verification",
        "description": """h2. Objective
Verify that all jobs are properly cleaned up after gradual load test and system returns to healthy state.

h2. Pre-Conditions
* Gradual load test completed
* Multiple jobs created during test
* System under load

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Complete gradual load test | 5 → 100 jobs | Test completed |
| 2 | Initiate cleanup | Disconnect all gRPC connections | Cleanup started |
| 3 | Verify jobs disconnected | Check connection status | All disconnected |
| 4 | Calculate cleanup ratio | Cleaned / Created | Ratio >= 90% |
| 5 | Verify post-cleanup health | Check system health | System healthy |
| 6 | Verify resource release | Check resource usage | Resources released |

h2. Expected Result
* Cleanup ratio >= 90%
* All gRPC connections disconnected
* System returns to healthy state
* Resources properly released
* No orphaned jobs or connections

h2. Cleanup Process
1. Disconnect gRPC connections for all active jobs
2. Wait for Kubernetes cleanup-job to detect low CPU
3. Verify pods are terminated
4. Verify system health restored

h2. Automation Status
✅ Automated

*Test Function:* `test_gradual_load_cleanup_verification`
*Test File:* `be_focus_server_tests/load/test_gradual_historic_load.py`
*Test Class:* `TestGradualHistoricJobLoad`
*Xray Marker:* `PZ-LOAD-403`
*Test Type:* Cleanup Verification Test

h2. Importance
Proper cleanup is critical for:
* Preventing resource leaks
* Ensuring system stability
* Allowing subsequent tests to run cleanly
* Maintaining production system health
""",
        "priority": "High",
        "labels": ["load", "historic", "gradual_load", "cleanup", "resource_management", "automation", "job_load"],
        "components": ["focus-server", "grpc", "kubernetes"]
    },
    "LOAD-410": {
        "summary": "Load - Historic - High Concurrency Gradual Load",
        "description": """h2. Objective
Verify system behavior under high concurrency gradual load with larger step increments.

h2. Background
This test uses larger increments for faster load buildup:
* Initial: 10 jobs
* Step Increment: +10 jobs every 8 seconds
* Maximum: 100 jobs
* Total Steps: 10 steps

This tests system scalability with larger concurrent job batches.

h2. Pre-Conditions
* Focus Server API is running
* MongoDB base_paths collection contains recordings
* Sufficient system resources available

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Start with 10 Historic jobs | Large initial batch | 10 jobs created |
| 2 | Wait 8 seconds | Step interval | Interval elapsed |
| 3 | Add 10 more jobs | Total: 20 jobs | 20 jobs running |
| 4 | Verify health | Check system status | Health verified |
| 5 | Repeat until 100 jobs | Continue adding | 100 jobs reached |
| 6 | Final health check | At maximum load | Health verified |
| 7 | Cleanup | Disconnect all jobs | Cleanup complete |

h2. Expected Result
* At least 8 steps completed
* Maximum 100 concurrent jobs reached
* System remains responsive
* Cleanup successful

h2. Comparison with Standard Gradual Load
* Standard: 5+5+5 every 10s (20 steps)
* High Concurrency: 10+10+10 every 8s (10 steps)
* Faster execution while maintaining gradual pattern

h2. Automation Status
✅ Automated

*Test Function:* `test_high_concurrency_gradual`
*Test File:* `be_focus_server_tests/load/test_gradual_historic_load.py`
*Test Class:* `TestGradualHistoricLoadCustomConfig`
*Xray Marker:* `PZ-LOAD-410`
*Test Type:* High Concurrency Gradual Load Test

h2. Use Cases
* Faster capacity testing
* Large batch validation
* Scalability verification
* Performance optimization testing
""",
        "priority": "Medium",
        "labels": ["load", "historic", "gradual_load", "high_concurrency", "scalability", "automation", "job_load"],
        "components": ["focus-server", "grpc"]
    },
}


def create_test_case(
    client: JiraClient,
    test_id: str,
    test_data: Dict[str, Any],
    dry_run: bool = False
) -> Optional[str]:
    """
    Create a test case in Jira Xray.
    
    Args:
        client: JiraClient instance
        test_id: Test identifier (e.g., "LOAD-400")
        test_data: Test data dictionary
        dry_run: If True, only preview without creating
        
    Returns:
        Created issue key (e.g., "PZ-15000") or None if dry_run
    """
    if dry_run:
        logger.info(f"[DRY RUN] Would create: {test_data['summary']}")
        return f"PZ-DRY-{test_id}"
    
    try:
        # Create issue
        issue = client.create_issue(
            summary=test_data['summary'],
            description=test_data['description'],
            issue_type="Test",
            priority=test_data['priority'],
            labels=test_data['labels'],
            components=test_data.get('components', []),
            project_key="PZ"
        )
        
        issue_key = issue['key']
        
        # Set Test Type to "Automation"
        try:
            issue_obj = client.jira.issue(issue_key)
            issue_obj.update(fields={"customfield_10951": {"value": "Automation"}})
            logger.debug(f"Set Test Type to 'Automation' for {issue_key}")
        except Exception as e:
            logger.warning(f"Could not set Test Type for {issue_key}: {e}")
        
        logger.info(f"✅ Created: {issue_key} - {test_data['summary'][:50]}...")
        logger.info(f"   URL: {issue.get('url', 'N/A')}")
        return issue_key
        
    except Exception as e:
        logger.error(f"❌ Failed to create {test_id}: {e}")
        return None


def main():
    """Main function for creating Gradual Historic Load tests."""
    parser = argparse.ArgumentParser(
        description="Create Gradual Historic Load Tests in Jira Xray"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview tests without creating them"
    )
    
    args = parser.parse_args()
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("Creating Gradual Historic Load Tests in Jira Xray")
    logger.info("=" * 80)
    logger.info(f"Mode: {'DRY RUN' if args.dry_run else 'CREATE'}")
    logger.info(f"Tests to create: {len(GRADUAL_HISTORIC_LOAD_TESTS)}")
    logger.info("")
    
    # Initialize Jira client
    try:
        client = JiraClient()
    except Exception as e:
        logger.error(f"Failed to initialize Jira client: {e}")
        logger.error("Make sure JIRA_API_TOKEN is set in environment")
        sys.exit(1)
    
    # Create tests
    created = []
    failed = []
    
    for test_id, test_data in GRADUAL_HISTORIC_LOAD_TESTS.items():
        logger.info(f"\n{'─' * 60}")
        logger.info(f"Processing: {test_id} - {test_data['summary']}")
        logger.info(f"{'─' * 60}")
        
        issue_key = create_test_case(
            client=client,
            test_id=test_id,
            test_data=test_data,
            dry_run=args.dry_run
        )
        
        if issue_key:
            created.append((test_id, issue_key))
        else:
            failed.append(test_id)
    
    # Summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Created: {len(created)}")
    logger.info(f"Failed: {len(failed)}")
    logger.info("")
    
    if created:
        logger.info("Created Tests:")
        for test_id, issue_key in created:
            logger.info(f"  {test_id} → {issue_key}")
    
    if failed:
        logger.warning("Failed Tests:")
        for test_id in failed:
            logger.warning(f"  {test_id}")
    
    logger.info("")
    logger.info("=" * 80)
    
    if args.dry_run:
        logger.info("DRY RUN completed - no tests were actually created")
        logger.info("Run without --dry-run to create tests in Jira")
    else:
        logger.info(f"✅ Created {len(created)} tests in Jira Xray")
    
    return 0 if len(failed) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

