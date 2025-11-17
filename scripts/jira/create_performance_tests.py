#!/usr/bin/env python3
"""
Create Performance Tests in Jira Xray
======================================

Creates 10 performance test tickets in Jira Xray for Focus Server API.

Tests:
- POST /configure Response Time
- GET /waterfall Response Time
- GET /metadata Response Time
- Concurrent Requests Performance
- Large Payload Handling
- Memory Usage Under Load
- CPU Usage Under Load
- Database Query Performance
- Network Latency Impact
- End-to-End Latency

Usage:
    python scripts/jira/create_performance_tests.py
    python scripts/jira/create_performance_tests.py --dry-run
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

# Performance Tests Definitions
PERFORMANCE_TESTS = {
    "PERF-001": {
        "summary": "Performance - POST /configure Response Time",
        "description": """h2. Objective
Verify that POST /configure endpoint responds within acceptable time limits under normal load.

h2. Pre-Conditions
* Focus Server API is running and accessible
* System is under normal load conditions

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Send POST /configure request | Valid configuration payload | Request sent successfully |
| 2 | Measure response time | Time from request to response | Response time recorded |
| 3 | Verify response time | Compare against SLA | Response time within SLA limits |

h2. Expected Result
POST /configure endpoint responds within SLA limits (typically < 2 seconds for P95).

h2. Assertions
* P50 response time < 500ms
* P95 response time < 2000ms
* P99 response time < 5000ms
* No timeouts occur

h2. Automation Status
✅ Automated

*Test Function:* `test_configure_response_time`
*Test File:* `tests/integration/performance/test_api_performance.py`
*Test Class:* `TestAPIPerformance`
""",
        "priority": "High",
        "labels": ["performance", "api", "response-time", "automation"],
        "components": ["focus-server", "api"]
    },
    "PERF-002": {
        "summary": "Performance - GET /waterfall Response Time",
        "description": """h2. Objective
Verify that GET /waterfall endpoint responds within acceptable time limits.

h2. Pre-Conditions
* Focus Server API is running and accessible
* Active streaming job exists with data available

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Send GET /waterfall/{job_id}/{row_count} request | Valid job_id and row_count | Request sent successfully |
| 2 | Measure response time | Time from request to response | Response time recorded |
| 3 | Verify response time | Compare against SLA | Response time within SLA limits |

h2. Expected Result
GET /waterfall endpoint responds within SLA limits (typically < 1 second for P95).

h2. Assertions
* P50 response time < 200ms
* P95 response time < 1000ms
* P99 response time < 2000ms
* Response contains valid waterfall data

h2. Automation Status
✅ Automated

*Test Function:* `test_waterfall_response_time`
*Test File:* `tests/integration/performance/test_api_performance.py`
*Test Class:* `TestAPIPerformance`
""",
        "priority": "High",
        "labels": ["performance", "api", "response-time", "waterfall", "automation"],
        "components": ["focus-server", "api"]
    },
    "PERF-003": {
        "summary": "Performance - GET /metadata Response Time",
        "description": """h2. Objective
Verify that GET /metadata endpoint responds within acceptable time limits.

h2. Pre-Conditions
* Focus Server API is running and accessible
* Active streaming job exists

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Send GET /metadata/{job_id} request | Valid job_id | Request sent successfully |
| 2 | Measure response time | Time from request to response | Response time recorded |
| 3 | Verify response time | Compare against SLA | Response time within SLA limits |

h2. Expected Result
GET /metadata endpoint responds within SLA limits (typically < 500ms for P95).

h2. Assertions
* P50 response time < 100ms
* P95 response time < 500ms
* P99 response time < 1000ms
* Response contains valid metadata

h2. Automation Status
✅ Automated

*Test Function:* `test_metadata_response_time`
*Test File:* `tests/integration/performance/test_api_performance.py`
*Test Class:* `TestAPIPerformance`
""",
        "priority": "High",
        "labels": ["performance", "api", "response-time", "metadata", "automation"],
        "components": ["focus-server", "api"]
    },
    "PERF-004": {
        "summary": "Performance - Concurrent Requests Performance",
        "description": """h2. Objective
Verify that API handles concurrent requests efficiently without significant performance degradation.

h2. Pre-Conditions
* Focus Server API is running and accessible
* System resources are available

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Send 50 concurrent POST /configure requests | 50 parallel requests | All requests sent |
| 2 | Measure response times | Time for each request | Response times recorded |
| 3 | Verify performance degradation | Compare with single request | Acceptable degradation |
| 4 | Verify all requests succeed | Check response status | All requests return 200 OK |

h2. Expected Result
API handles concurrent requests efficiently with acceptable performance degradation (< 20% increase in response time).

h2. Assertions
* All concurrent requests complete successfully
* Average response time increase < 20% compared to single request
* No request timeouts
* System remains stable

h2. Automation Status
✅ Automated

*Test Function:* `test_concurrent_requests_performance`
*Test File:* `tests/integration/performance/test_concurrent_performance.py`
*Test Class:* `TestConcurrentPerformance`
""",
        "priority": "High",
        "labels": ["performance", "api", "concurrent", "load", "automation"],
        "components": ["focus-server", "api"]
    },
    "PERF-005": {
        "summary": "Performance - Large Payload Handling",
        "description": """h2. Objective
Verify that API handles large payloads efficiently without performance degradation.

h2. Pre-Conditions
* Focus Server API is running and accessible
* System can handle large payloads

h2. Test Data
* Large payload: Maximum channel range (1-2223), maximum frequency range (0-1000)

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Send POST /configure with large payload | Maximum channel/frequency ranges | Request sent successfully |
| 2 | Measure response time | Time from request to response | Response time recorded |
| 3 | Verify performance | Compare with normal payload | Acceptable performance |
| 4 | Verify request succeeds | Check response status | Request returns 200 OK |

h2. Expected Result
API handles large payloads efficiently with acceptable performance (response time increase < 30%).

h2. Assertions
* Large payload request completes successfully
* Response time increase < 30% compared to normal payload
* No memory issues
* System remains stable

h2. Automation Status
✅ Automated

*Test Function:* `test_large_payload_performance`
*Test File:* `tests/integration/performance/test_payload_performance.py`
*Test Class:* `TestPayloadPerformance`
""",
        "priority": "Medium",
        "labels": ["performance", "api", "payload", "automation"],
        "components": ["focus-server", "api"]
    },
    "PERF-006": {
        "summary": "Performance - Memory Usage Under Load",
        "description": """h2. Objective
Verify that API memory usage remains within acceptable limits under sustained load.

h2. Pre-Conditions
* Focus Server API is running and accessible
* Memory monitoring is enabled

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Record baseline memory usage | Before load test | Baseline recorded |
| 2 | Send sustained load (100 requests/minute for 10 minutes) | Continuous requests | Load applied |
| 3 | Monitor memory usage | During load test | Memory usage recorded |
| 4 | Verify memory stability | Check for memory leaks | Memory usage stable |

h2. Expected Result
Memory usage remains stable under sustained load with no memory leaks.

h2. Assertions
* Memory usage increase < 50% from baseline
* No memory leaks detected
* Memory usage stabilizes after initial increase
* System remains responsive

h2. Automation Status
✅ Automated

*Test Function:* `test_memory_usage_under_load`
*Test File:* `tests/integration/performance/test_resource_usage.py`
*Test Class:* `TestResourceUsage`
""",
        "priority": "Medium",
        "labels": ["performance", "api", "memory", "resource-usage", "automation"],
        "components": ["focus-server", "api"]
    },
    "PERF-007": {
        "summary": "Performance - CPU Usage Under Load",
        "description": """h2. Objective
Verify that API CPU usage remains within acceptable limits under sustained load.

h2. Pre-Conditions
* Focus Server API is running and accessible
* CPU monitoring is enabled

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Record baseline CPU usage | Before load test | Baseline recorded |
| 2 | Send sustained load (100 requests/minute for 10 minutes) | Continuous requests | Load applied |
| 3 | Monitor CPU usage | During load test | CPU usage recorded |
| 4 | Verify CPU stability | Check for CPU spikes | CPU usage acceptable |

h2. Expected Result
CPU usage remains within acceptable limits under sustained load.

h2. Assertions
* Average CPU usage < 80%
* Peak CPU usage < 95%
* CPU usage returns to baseline after load stops
* System remains responsive

h2. Automation Status
✅ Automated

*Test Function:* `test_cpu_usage_under_load`
*Test File:* `tests/integration/performance/test_resource_usage.py`
*Test Class:* `TestResourceUsage`
""",
        "priority": "Medium",
        "labels": ["performance", "api", "cpu", "resource-usage", "automation"],
        "components": ["focus-server", "api"]
    },
    "PERF-008": {
        "summary": "Performance - Database Query Performance",
        "description": """h2. Objective
Verify that database queries perform efficiently and do not cause performance bottlenecks.

h2. Pre-Conditions
* Focus Server API is running and accessible
* MongoDB is accessible
* Database contains test data

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Execute database query (e.g., GET /channels) | Query for channel list | Query executed |
| 2 | Measure query execution time | Time for query to complete | Execution time recorded |
| 3 | Verify query performance | Compare against SLA | Query within SLA limits |
| 4 | Verify query results | Check result correctness | Results are correct |

h2. Expected Result
Database queries execute efficiently within acceptable time limits.

h2. Assertions
* Query execution time < 500ms (P95)
* Query results are correct
* No query timeouts
* Database indexes are utilized

h2. Automation Status
✅ Automated

*Test Function:* `test_database_query_performance`
*Test File:* `tests/integration/performance/test_database_performance.py`
*Test Class:* `TestDatabasePerformance`
""",
        "priority": "Medium",
        "labels": ["performance", "api", "database", "mongodb", "automation"],
        "components": ["focus-server", "api", "database"]
    },
    "PERF-009": {
        "summary": "Performance - Network Latency Impact",
        "description": """h2. Objective
Verify that network latency does not significantly impact API performance.

h2. Pre-Conditions
* Focus Server API is running and accessible
* Network latency can be simulated

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Measure baseline response time | Normal network conditions | Baseline recorded |
| 2 | Simulate network latency (100ms) | Add artificial latency | Latency applied |
| 3 | Measure response time with latency | Under latency conditions | Response time recorded |
| 4 | Verify impact | Compare with baseline | Acceptable impact |

h2. Expected Result
Network latency has acceptable impact on API performance (increase < 150ms for 100ms latency).

h2. Assertions
* Response time increase approximately matches added latency
* No additional performance degradation
* System remains stable
* Requests complete successfully

h2. Automation Status
✅ Automated

*Test Function:* `test_network_latency_impact`
*Test File:* `tests/integration/performance/test_network_performance.py`
*Test Class:* `TestNetworkPerformance`
""",
        "priority": "Low",
        "labels": ["performance", "api", "network", "latency", "automation"],
        "components": ["focus-server", "api"]
    },
    "PERF-010": {
        "summary": "Performance - End-to-End Latency",
        "description": """h2. Objective
Verify that end-to-end latency (from request to data availability) is within acceptable limits.

h2. Pre-Conditions
* Focus Server API is running and accessible
* Full system pipeline is operational

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Send POST /configure request | Valid configuration | Request sent |
| 2 | Measure time until data available | Time to first waterfall data | Latency recorded |
| 3 | Verify end-to-end latency | Compare against SLA | Latency within SLA limits |
| 4 | Verify data quality | Check waterfall data | Data is correct |

h2. Expected Result
End-to-end latency (configure to first data) is within acceptable limits (typically < 5 seconds).

h2. Assertions
* End-to-end latency < 5 seconds (P95)
* Data becomes available within SLA
* Data quality is maintained
* System remains stable

h2. Automation Status
✅ Automated

*Test Function:* `test_end_to_end_latency`
*Test File:* `tests/integration/performance/test_e2e_performance.py`
*Test Class:* `TestE2EPerformance`
""",
        "priority": "High",
        "labels": ["performance", "api", "e2e", "latency", "automation"],
        "components": ["focus-server", "api"]
    }
}


def create_performance_test(
    client: JiraClient,
    test_id: str,
    test_data: Dict[str, Any],
    dry_run: bool = False
) -> str:
    """
    Create a performance test in Jira Xray.
    
    Args:
        client: JiraClient instance
        test_id: Test identifier (e.g., "PERF-001")
        test_data: Test data dictionary
        dry_run: If True, only preview without creating
        
    Returns:
        Created issue key (e.g., "PZ-14789")
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
        description='Create performance tests in Jira Xray'
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
        logger.info(f"{'[DRY RUN] ' if args.dry_run else ''}Creating Performance Tests")
        logger.info("=" * 80)
        
        created_tests = []
        failed_tests = []
        
        for test_id, test_data in PERFORMANCE_TESTS.items():
            try:
                issue_key = create_performance_test(
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
        print(f"Total tests: {len(PERFORMANCE_TESTS)}")
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

