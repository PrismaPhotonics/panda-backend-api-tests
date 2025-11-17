#!/usr/bin/env python3
"""
Create Error Handling Tests in Jira Xray
=========================================

Creates 8 error handling test tickets in Jira Xray for Focus Server API.

Tests:
- 500 Internal Server Error Handling
- 503 Service Unavailable Handling
- 504 Gateway Timeout Handling
- Network Timeout Handling
- Connection Refused Handling
- Invalid JSON Payload Handling
- Malformed Request Handling
- Error Message Format

Usage:
    python scripts/jira/create_error_handling_tests.py
    python scripts/jira/create_error_handling_tests.py --dry-run
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

# Error Handling Tests Definitions
ERROR_HANDLING_TESTS = {
    "ERR-001": {
        "summary": "Error Handling - 500 Internal Server Error",
        "description": """h2. Objective
Verify that API endpoints properly handle internal server errors and return appropriate error responses.

h2. Pre-Conditions
* Focus Server API is running and accessible
* Error handling is configured

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Trigger internal server error (if possible) | Invalid operation | HTTP 500 Internal Server Error |
| 2 | Verify error response format | Check response body | Proper error structure |
| 3 | Verify error message | Check error message | Generic error message (no sensitive data) |
| 4 | Verify error logging | Check server logs | Error logged appropriately |

h2. Expected Result
Internal server errors return HTTP 500 with proper error format and no sensitive data exposure.

h2. Assertions
* HTTP status code is 500
* Error response has proper structure
* Error message is generic and safe
* Error is logged for debugging

h2. Automation Status
✅ Automated

*Test Function:* `test_500_internal_server_error`
*Test File:* `tests/integration/error_handling/test_server_errors.py`
*Test Class:* `TestServerErrors`
""",
        "priority": "Highest",
        "labels": ["error-handling", "api", "server-errors", "automation"],
        "components": ["focus-server", "api"]
    },
    "ERR-002": {
        "summary": "Error Handling - 503 Service Unavailable",
        "description": """h2. Objective
Verify that API endpoints properly handle service unavailable scenarios.

h2. Pre-Conditions
* Focus Server API is running
* Dependencies (MongoDB, RabbitMQ) can be temporarily unavailable

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Stop MongoDB service | N/A | MongoDB unavailable |
| 2 | Send POST /configure request | Valid payload | HTTP 503 Service Unavailable |
| 3 | Verify error response | Check response | Proper 503 error format |
| 4 | Restore MongoDB service | N/A | Service restored |
| 5 | Verify service recovery | Send request again | Request succeeds |

h2. Expected Result
Service unavailable scenarios return HTTP 503 with proper error format.

h2. Assertions
* HTTP status code is 503
* Error message indicates service unavailable
* Service recovery is possible
* Error is logged appropriately

h2. Automation Status
✅ Automated

*Test Function:* `test_503_service_unavailable`
*Test File:* `tests/integration/error_handling/test_service_availability.py`
*Test Class:* `TestServiceAvailability`
""",
        "priority": "Highest",
        "labels": ["error-handling", "api", "service-availability", "automation"],
        "components": ["focus-server", "api"]
    },
    "ERR-003": {
        "summary": "Error Handling - 504 Gateway Timeout",
        "description": """h2. Objective
Verify that API endpoints properly handle gateway timeout scenarios.

h2. Pre-Conditions
* Focus Server API is running and accessible
* Timeout configuration is set

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Send request that exceeds timeout | Long-running operation | HTTP 504 Gateway Timeout |
| 2 | Verify error response | Check response | Proper 504 error format |
| 3 | Verify timeout duration | Check timing | Timeout occurs within configured limit |

h2. Expected Result
Gateway timeout scenarios return HTTP 504 with proper error format.

h2. Assertions
* HTTP status code is 504
* Error message indicates timeout
* Timeout occurs within configured limit
* Error is logged appropriately

h2. Automation Status
✅ Automated

*Test Function:* `test_504_gateway_timeout`
*Test File:* `tests/integration/error_handling/test_timeouts.py`
*Test Class:* `TestTimeouts`
""",
        "priority": "High",
        "labels": ["error-handling", "api", "timeout", "automation"],
        "components": ["focus-server", "api"]
    },
    "ERR-004": {
        "summary": "Error Handling - Network Timeout",
        "description": """h2. Objective
Verify that API client properly handles network timeout scenarios.

h2. Pre-Conditions
* Focus Server API is running
* Network can be simulated as slow/unavailable

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Simulate network timeout | Slow network | Request times out |
| 2 | Verify timeout handling | Check client behavior | Timeout exception handled |
| 3 | Verify retry mechanism (if applicable) | Check retry logic | Retries or fails gracefully |
| 4 | Verify error message | Check error | Clear timeout error message |

h2. Expected Result
Network timeouts are handled gracefully with appropriate error messages.

h2. Assertions
* Timeout exception is caught
* Error message indicates timeout
* Client handles timeout gracefully
* No resource leaks

h2. Automation Status
✅ Automated

*Test Function:* `test_network_timeout`
*Test File:* `tests/integration/error_handling/test_timeouts.py`
*Test Class:* `TestTimeouts`
""",
        "priority": "High",
        "labels": ["error-handling", "api", "network", "timeout", "automation"],
        "components": ["focus-server", "api"]
    },
    "ERR-005": {
        "summary": "Error Handling - Connection Refused",
        "description": """h2. Objective
Verify that API client properly handles connection refused scenarios.

h2. Pre-Conditions
* Focus Server API can be stopped
* Connection can be refused

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Stop Focus Server | N/A | Server unavailable |
| 2 | Send API request | Valid request | Connection refused error |
| 3 | Verify error handling | Check client behavior | Error handled gracefully |
| 4 | Verify error message | Check error | Clear connection error message |
| 5 | Restore Focus Server | N/A | Server available |
| 6 | Verify recovery | Send request again | Request succeeds |

h2. Expected Result
Connection refused errors are handled gracefully with appropriate error messages.

h2. Assertions
* Connection refused exception is caught
* Error message indicates connection issue
* Client handles error gracefully
* Recovery is possible when service restored

h2. Automation Status
✅ Automated

*Test Function:* `test_connection_refused`
*Test File:* `tests/integration/error_handling/test_connection_errors.py`
*Test Class:* `TestConnectionErrors`
""",
        "priority": "High",
        "labels": ["error-handling", "api", "connection", "automation"],
        "components": ["focus-server", "api"]
    },
    "ERR-006": {
        "summary": "Error Handling - Invalid JSON Payload",
        "description": """h2. Objective
Verify that API endpoints properly handle invalid JSON payloads.

h2. Pre-Conditions
* Focus Server API is running and accessible

h2. Test Data
* Invalid JSON: `{"invalid": json}`, `{invalid json}`, `not json at all`

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Send POST /configure with invalid JSON | Invalid JSON string | HTTP 400 Bad Request |
| 2 | Verify error response | Check response | Proper error format |
| 3 | Verify error message | Check error message | Clear indication of JSON parsing error |
| 4 | Send request with malformed JSON | Malformed JSON | HTTP 400 Bad Request |

h2. Expected Result
Invalid JSON payloads return HTTP 400 with clear error messages.

h2. Assertions
* HTTP status code is 400
* Error message indicates JSON parsing error
* Error response has proper structure
* No sensitive data exposed

h2. Automation Status
✅ Automated

*Test Function:* `test_invalid_json_payload`
*Test File:* `tests/integration/error_handling/test_payload_validation.py`
*Test Class:* `TestPayloadValidation`
""",
        "priority": "High",
        "labels": ["error-handling", "api", "json", "validation", "automation"],
        "components": ["focus-server", "api"]
    },
    "ERR-007": {
        "summary": "Error Handling - Malformed Request",
        "description": """h2. Objective
Verify that API endpoints properly handle malformed requests.

h2. Pre-Conditions
* Focus Server API is running and accessible

h2. Test Data
* Missing Content-Type header
* Wrong Content-Type (e.g., text/plain instead of application/json)
* Missing required headers
* Invalid HTTP method

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Send request without Content-Type header | No Content-Type | HTTP 400 or 415 |
| 2 | Send request with wrong Content-Type | text/plain | HTTP 415 Unsupported Media Type |
| 3 | Send request with missing required headers | Missing headers | HTTP 400 Bad Request |
| 4 | Send request with invalid HTTP method | PUT instead of POST | HTTP 405 Method Not Allowed |

h2. Expected Result
Malformed requests return appropriate HTTP error codes with clear error messages.

h2. Assertions
* Appropriate HTTP status codes returned
* Error messages are clear and helpful
* Error response has proper structure

h2. Automation Status
✅ Automated

*Test Function:* `test_malformed_request`
*Test File:* `tests/integration/error_handling/test_request_validation.py`
*Test Class:* `TestRequestValidation`
""",
        "priority": "High",
        "labels": ["error-handling", "api", "validation", "automation"],
        "components": ["focus-server", "api"]
    },
    "ERR-008": {
        "summary": "Error Handling - Error Message Format",
        "description": """h2. Objective
Verify that all error responses follow a consistent format and structure.

h2. Pre-Conditions
* Focus Server API is running and accessible

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Trigger various error scenarios | Multiple error types | Errors returned |
| 2 | Verify error response structure | Check all error responses | Consistent format |
| 3 | Verify error fields | Check error fields | Required fields present |
| 4 | Verify error message consistency | Check error messages | Consistent format |

h2. Expected Result
All error responses follow a consistent format with required fields.

h2. Assertions
* Error responses have consistent structure
* Required fields present: error code, message, timestamp
* Error messages are clear and consistent
* No sensitive data in error messages

h2. Automation Status
✅ Automated

*Test Function:* `test_error_message_format`
*Test File:* `tests/integration/error_handling/test_error_format.py`
*Test Class:* `TestErrorFormat`
""",
        "priority": "High",
        "labels": ["error-handling", "api", "error-format", "automation"],
        "components": ["focus-server", "api"]
    }
}


def create_error_handling_test(
    client: JiraClient,
    test_id: str,
    test_data: Dict[str, Any],
    dry_run: bool = False
) -> str:
    """
    Create an error handling test in Jira Xray.
    
    Args:
        client: JiraClient instance
        test_id: Test identifier (e.g., "ERR-001")
        test_data: Test data dictionary
        dry_run: If True, only preview without creating
        
    Returns:
        Created issue key (e.g., "PZ-14775")
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
        description='Create error handling tests in Jira Xray'
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
        logger.info(f"{'[DRY RUN] ' if args.dry_run else ''}Creating Error Handling Tests")
        logger.info("=" * 80)
        
        created_tests = []
        failed_tests = []
        
        for test_id, test_data in ERROR_HANDLING_TESTS.items():
            try:
                issue_key = create_error_handling_test(
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
        print(f"Total tests: {len(ERROR_HANDLING_TESTS)}")
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

