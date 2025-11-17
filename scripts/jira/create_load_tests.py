#!/usr/bin/env python3
"""
Create Load Tests in Jira Xray
================================

Creates 8 load test tickets in Jira Xray for Focus Server API.

Tests:
- Concurrent Job Creation Load
- Sustained Load - 1 Hour
- Peak Load - High RPS
- Ramp-Up Load Profile
- Spike Load Profile
- Steady-State Load Profile
- Recovery After Load
- Resource Exhaustion Under Load

Usage:
    python scripts/jira/create_load_tests.py
    python scripts/jira/create_load_tests.py --dry-run
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Dict, Any

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

# Load Tests Definitions
LOAD_TESTS = {
    "LOAD-001": {
        "summary": "Load - Concurrent Job Creation Load",
        "description": """h2. Objective
Verify that system handles concurrent job creation efficiently up to capacity limits.

h2. Pre-Conditions
* Focus Server API is running and accessible
* System is at baseline load

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Send 100 concurrent POST /configure requests | 100 parallel requests | All requests sent |
| 2 | Monitor system response | Check response times and errors | System responds |
| 3 | Verify all jobs created | Check job creation success rate | Success rate > 95% |
| 4 | Verify system stability | Check for errors and timeouts | System remains stable |

h2. Expected Result
System handles 100 concurrent job creations successfully with > 95% success rate.

h2. Assertions
* Success rate > 95%
* Average response time < 5 seconds
* No system crashes or unhandled errors
* System remains responsive

h2. Automation Status
✅ Automated

*Test Function:* `test_concurrent_job_creation_load`
*Test File:* `tests/load/test_concurrent_load.py`
*Test Class:* `TestConcurrentLoad`
""",
        "priority": "High",
        "labels": ["load", "api", "concurrent", "automation"],
        "components": ["focus-server", "api"]
    },
    "LOAD-002": {
        "summary": "Load - Sustained Load - 1 Hour",
        "description": """h2. Objective
Verify that system maintains performance and stability under sustained load for extended period.

h2. Pre-Conditions
* Focus Server API is running and accessible
* System resources are available

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Apply sustained load (50 requests/minute) | 1 hour duration | Load applied |
| 2 | Monitor system metrics | CPU, memory, response times | Metrics recorded |
| 3 | Verify performance stability | Check for degradation | Performance stable |
| 4 | Verify no memory leaks | Check memory usage trend | No memory leaks |
| 5 | Verify error rate | Check error percentage | Error rate < 1% |

h2. Expected Result
System maintains stable performance under sustained load for 1 hour with no memory leaks.

h2. Assertions
* Error rate < 1% throughout test
* Memory usage stable (no continuous growth)
* Response times remain within SLA
* System remains responsive

h2. Automation Status
✅ Automated

*Test Function:* `test_sustained_load_1_hour`
*Test File:* `tests/load/test_sustained_load.py`
*Test Class:* `TestSustainedLoad`
""",
        "priority": "High",
        "labels": ["load", "api", "sustained", "soak", "automation"],
        "components": ["focus-server", "api"]
    },
    "LOAD-003": {
        "summary": "Load - Peak Load - High RPS",
        "description": """h2. Objective
Verify that system handles peak load scenarios with high requests per second.

h2. Pre-Conditions
* Focus Server API is running and accessible
* System can handle peak load

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Apply peak load (1000 requests/second) | 1 minute duration | Peak load applied |
| 2 | Monitor system response | Check response times and errors | System responds |
| 3 | Verify graceful degradation | Check error handling | Graceful handling |
| 4 | Verify recovery | Check system after load stops | System recovers |

h2. Expected Result
System handles peak load gracefully with acceptable error rate and recovers quickly.

h2. Assertions
* Error rate < 5% during peak load
* System does not crash
* Response times degrade gracefully
* System recovers within 30 seconds

h2. Automation Status
✅ Automated

*Test Function:* `test_peak_load_high_rps`
*Test File:* `tests/load/test_peak_load.py`
*Test Class:* `TestPeakLoad`
""",
        "priority": "High",
        "labels": ["load", "api", "peak", "stress", "automation"],
        "components": ["focus-server", "api"]
    },
    "LOAD-004": {
        "summary": "Load - Ramp-Up Load Profile",
        "description": """h2. Objective
Verify that system handles gradual ramp-up load profile efficiently.

h2. Pre-Conditions
* Focus Server API is running and accessible
* System is at baseline

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Start with 10 requests/second | Baseline load | Baseline established |
| 2 | Gradually increase to 100 requests/second | Over 5 minutes | Load ramped up |
| 3 | Monitor system response | Check metrics | System adapts |
| 4 | Verify performance | Check response times | Performance acceptable |
| 5 | Gradually decrease load | Ramp down | Load decreased |

h2. Expected Result
System handles ramp-up load profile efficiently with smooth adaptation.

h2. Assertions
* System adapts smoothly to increasing load
* Response times increase gradually
* Error rate remains low (< 2%)
* No sudden failures

h2. Automation Status
✅ Automated

*Test Function:* `test_ramp_up_load_profile`
*Test File:* `tests/load/test_load_profiles.py`
*Test Class:* `TestLoadProfiles`
""",
        "priority": "Medium",
        "labels": ["load", "api", "ramp-up", "automation"],
        "components": ["focus-server", "api"]
    },
    "LOAD-005": {
        "summary": "Load - Spike Load Profile",
        "description": """h2. Objective
Verify that system handles sudden spike load profile efficiently.

h2. Pre-Conditions
* Focus Server API is running and accessible
* System is at baseline load

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Maintain baseline load (20 requests/second) | 2 minutes | Baseline maintained |
| 2 | Apply sudden spike (200 requests/second) | 30 seconds | Spike applied |
| 3 | Monitor system response | Check metrics | System responds |
| 4 | Return to baseline | 20 requests/second | Load returned to baseline |
| 5 | Verify recovery | Check system state | System recovered |

h2. Expected Result
System handles sudden spike load efficiently and recovers quickly.

h2. Assertions
* System handles spike without crashing
* Error rate during spike < 10%
* System recovers within 1 minute
* Performance returns to baseline

h2. Automation Status
✅ Automated

*Test Function:* `test_spike_load_profile`
*Test File:* `tests/load/test_load_profiles.py`
*Test Class:* `TestLoadProfiles`
""",
        "priority": "Medium",
        "labels": ["load", "api", "spike", "automation"],
        "components": ["focus-server", "api"]
    },
    "LOAD-006": {
        "summary": "Load - Steady-State Load Profile",
        "description": """h2. Objective
Verify that system maintains consistent performance under steady-state load.

h2. Pre-Conditions
* Focus Server API is running and accessible
* System is ready for steady load

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Apply steady load (50 requests/second) | 30 minutes | Steady load applied |
| 2 | Monitor system metrics | CPU, memory, response times | Metrics recorded |
| 3 | Verify consistency | Check for variations | Performance consistent |
| 4 | Verify stability | Check for errors | System stable |

h2. Expected Result
System maintains consistent performance under steady-state load.

h2. Assertions
* Response time variance < 20%
* Error rate < 1%
* Resource usage stable
* No performance degradation

h2. Automation Status
✅ Automated

*Test Function:* `test_steady_state_load_profile`
*Test File:* `tests/load/test_load_profiles.py`
*Test Class:* `TestLoadProfiles`
""",
        "priority": "Medium",
        "labels": ["load", "api", "steady-state", "automation"],
        "components": ["focus-server", "api"]
    },
    "LOAD-007": {
        "summary": "Load - Recovery After Load",
        "description": """h2. Objective
Verify that system recovers properly after high load conditions.

h2. Pre-Conditions
* Focus Server API is running and accessible
* System has been under high load

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Apply high load (100 requests/second) | 10 minutes | High load applied |
| 2 | Stop load | Load stopped | Load removed |
| 3 | Monitor recovery | Check system metrics | Recovery monitored |
| 4 | Verify return to baseline | Check performance | Performance returns to baseline |
| 5 | Verify resource cleanup | Check resource usage | Resources cleaned up |

h2. Expected Result
System recovers quickly after high load and returns to baseline performance.

h2. Assertions
* Recovery time < 2 minutes
* Performance returns to baseline
* Resource usage returns to normal
* No lingering errors

h2. Automation Status
✅ Automated

*Test Function:* `test_recovery_after_load`
*Test File:* `tests/load/test_recovery.py`
*Test Class:* `TestRecovery`
""",
        "priority": "Medium",
        "labels": ["load", "api", "recovery", "automation"],
        "components": ["focus-server", "api"]
    },
    "LOAD-008": {
        "summary": "Load - Resource Exhaustion Under Load",
        "description": """h2. Objective
Verify that system handles resource exhaustion scenarios gracefully.

h2. Pre-Conditions
* Focus Server API is running and accessible
* System resources can be monitored

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Apply increasing load | Until resource limits | Load increased |
| 2 | Monitor resource usage | CPU, memory, connections | Resources monitored |
| 3 | Verify graceful handling | Check error handling | Graceful handling |
| 4 | Verify no crashes | Check system stability | No crashes |
| 5 | Verify error messages | Check error responses | Clear error messages |

h2. Expected Result
System handles resource exhaustion gracefully with clear error messages and no crashes.

h2. Assertions
* System does not crash
* Error messages are clear and helpful
* System remains partially functional
* Recovery is possible after resource availability

h2. Automation Status
✅ Automated

*Test Function:* `test_resource_exhaustion_under_load`
*Test File:* `tests/load/test_resource_exhaustion.py`
*Test Class:* `TestResourceExhaustion`
""",
        "priority": "Medium",
        "labels": ["load", "api", "resource-exhaustion", "automation"],
        "components": ["focus-server", "api"]
    }
}


def create_load_test(
    client: JiraClient,
    test_id: str,
    test_data: Dict[str, Any],
    dry_run: bool = False
) -> str:
    """
    Create a load test in Jira Xray.
    
    Args:
        client: JiraClient instance
        test_id: Test identifier (e.g., "LOAD-001")
        test_data: Test data dictionary
        dry_run: If True, only preview without creating
        
    Returns:
        Created issue key (e.g., "PZ-14799")
    """
    if dry_run:
        logger.info(f"[DRY RUN] Would create test: {test_data['summary']}")
        return f"PZ-DRY-RUN-{test_id}"
    
    try:
        # Create issue using client.create_issue (handles components properly)
        issue = client.create_issue(
            summary=f"Infrastructure - {test_data['summary']}",
            description=test_data['description'],
            issue_type="Test",
            priority=test_data['priority'],
            labels=test_data['labels'],
            components=test_data['components'],
            project_key="PZ"
        )
        
        # Set Test Type to "Automation" after creation
        try:
            issue_obj = client.jira.issue(issue['key'])
            issue_obj.update(fields={"customfield_10951": {"value": "Automation"}})
            logger.info(f"✅ Set Test Type to 'Automation' for {issue['key']}")
        except Exception as e:
            logger.warning(f"⚠️  Could not set Test Type for {issue['key']}: {e}")
        
        logger.info(f"[OK] Created test: {issue['key']} - {test_data['summary']}")
        
        return issue['key']
        
    except Exception as e:
        logger.error(f"[FAIL] Failed to create test {test_id}: {e}")
        raise


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Create load tests in Jira Xray'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without creating tests'
    )
    
    args = parser.parse_args()
    
    try:
        client = JiraClient()
        
        logger.info("=" * 80)
        logger.info(f"{'[DRY RUN] ' if args.dry_run else ''}Creating Load Tests")
        logger.info("=" * 80)
        
        created_tests = []
        failed_tests = []
        
        for test_id, test_data in LOAD_TESTS.items():
            try:
                issue_key = create_load_test(
                    client,
                    test_id,
                    test_data,
                    dry_run=args.dry_run
                )
                created_tests.append({
                    'test_id': test_id,
                    'issue_key': issue_key,
                    'summary': test_data['summary']
                })
            except Exception as e:
                logger.error(f"Failed to create {test_id}: {e}")
                failed_tests.append(test_id)
        
        # Summary
        print("\n" + "=" * 80)
        print("CREATION SUMMARY")
        print("=" * 80)
        print(f"Total tests: {len(LOAD_TESTS)}")
        print(f"[OK] Created: {len(created_tests)}")
        print(f"[FAIL] Failed: {len(failed_tests)}")
        
        if created_tests:
            print("\nCreated Tests:")
            print("-" * 80)
            for test in created_tests:
                print(f"  {test['test_id']}: {test['issue_key']} - {test['summary']}")
        
        if failed_tests:
            print(f"\nFailed Tests: {', '.join(failed_tests)}")
        
        if args.dry_run:
            print("\n[DRY RUN] No tests were actually created")
        
        client.close()
        
        return 0 if len(failed_tests) == 0 else 1
        
    except Exception as e:
        logger.error(f"Failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

