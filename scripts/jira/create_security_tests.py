#!/usr/bin/env python3
"""
Create Security Tests in Jira Xray
===================================

Creates 10 security test tickets in Jira Xray for Focus Server API.

Tests:
- Authentication Required
- Invalid Authentication Token
- Expired Authentication Token
- SQL Injection Prevention
- XSS Prevention
- CSRF Protection
- Rate Limiting
- Input Sanitization
- HTTPS Only
- Sensitive Data Exposure

Usage:
    python scripts/jira/create_security_tests.py
    python scripts/jira/create_security_tests.py --dry-run
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List

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

# Security Tests Definitions
SECURITY_TESTS = {
    "SEC-001": {
        "summary": "Security - API Authentication Required",
        "description": """h2. Objective
Verify that API endpoints require proper authentication and reject unauthorized requests.

h2. Pre-Conditions
* Focus Server API is running and accessible
* Authentication mechanism is configured

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Send request to POST /configure without authentication | No auth headers | HTTP 401 Unauthorized |
| 2 | Send request to GET /waterfall/{task_id}/{row_count} without authentication | No auth headers | HTTP 401 Unauthorized |
| 3 | Send request to GET /metadata/{task_id} without authentication | No auth headers | HTTP 401 Unauthorized |

h2. Expected Result
All API endpoints reject requests without proper authentication with HTTP 401 Unauthorized.

h2. Assertions
* All endpoints return 401 for unauthenticated requests
* Error message indicates authentication required
* No sensitive data exposed in error response

h2. Automation Status
✅ Automated

*Test Function:* `test_api_authentication_required`
*Test File:* `tests/integration/security/test_api_authentication.py`
*Test Class:* `TestAPIAuthentication`
""",
        "priority": "Highest",
        "labels": ["security", "api", "authentication", "automation"],
        "components": ["focus-server", "api", "security"]
    },
    "SEC-002": {
        "summary": "Security - Invalid Authentication Token",
        "description": """h2. Objective
Verify that API endpoints properly reject requests with invalid or malformed authentication tokens.

h2. Pre-Conditions
* Focus Server API is running and accessible
* Authentication mechanism is configured

h2. Test Data
* Invalid tokens: "invalid_token", "malformed.token", "", null

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Send request with invalid token format | Token: "invalid_token" | HTTP 401 Unauthorized |
| 2 | Send request with malformed token | Token: "malformed.token" | HTTP 401 Unauthorized |
| 3 | Send request with empty token | Token: "" | HTTP 401 Unauthorized |
| 4 | Send request with null token | Token: null | HTTP 401 Unauthorized |

h2. Expected Result
All invalid authentication tokens are rejected with HTTP 401 Unauthorized.

h2. Assertions
* Invalid tokens return 401
* Error message indicates invalid authentication
* No sensitive information leaked in error response

h2. Automation Status
✅ Automated

*Test Function:* `test_invalid_authentication_token`
*Test File:* `tests/integration/security/test_api_authentication.py`
*Test Class:* `TestAPIAuthentication`
""",
        "priority": "Highest",
        "labels": ["security", "api", "authentication", "automation"],
        "components": ["focus-server", "api", "security"]
    },
    "SEC-003": {
        "summary": "Security - Expired Authentication Token",
        "description": """h2. Objective
Verify that API endpoints properly reject requests with expired authentication tokens.

h2. Pre-Conditions
* Focus Server API is running and accessible
* Token expiration mechanism is configured

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Obtain valid authentication token | N/A | Token obtained successfully |
| 2 | Wait for token expiration | Wait until token expires | Token expires |
| 3 | Send request with expired token | Expired token | HTTP 401 Unauthorized |

h2. Expected Result
Expired authentication tokens are rejected with HTTP 401 Unauthorized.

h2. Assertions
* Expired tokens return 401
* Error message indicates token expired
* Clear indication that token refresh is required

h2. Automation Status
✅ Automated

*Test Function:* `test_expired_authentication_token`
*Test File:* `tests/integration/security/test_api_authentication.py`
*Test Class:* `TestAPIAuthentication`
""",
        "priority": "Highest",
        "labels": ["security", "api", "authentication", "automation"],
        "components": ["focus-server", "api", "security"]
    },
    "SEC-004": {
        "summary": "Security - SQL Injection Prevention",
        "description": """h2. Objective
Verify that API endpoints properly sanitize input and prevent SQL injection attacks.

h2. Pre-Conditions
* Focus Server API is running and accessible
* Database backend is configured

h2. Test Data
* SQL injection payloads:
  * `' OR '1'='1`
  * `'; DROP TABLE users; --`
  * `' UNION SELECT * FROM users --`
  * `1' OR '1'='1' --`

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Send POST /configure with SQL injection in task_id | task_id: "test' OR '1'='1" | Request rejected or sanitized |
| 2 | Send POST /configure with SQL injection in payload fields | Various SQL payloads | Request rejected or sanitized |
| 3 | Verify database integrity | Check database state | No SQL executed, database intact |

h2. Expected Result
SQL injection attempts are prevented and do not execute against the database.

h2. Assertions
* SQL injection payloads are rejected or sanitized
* Database remains intact
* Error messages do not expose database structure

h2. Automation Status
✅ Automated

*Test Function:* `test_sql_injection_prevention`
*Test File:* `tests/integration/security/test_input_validation.py`
*Test Class:* `TestInputValidation`
""",
        "priority": "High",
        "labels": ["security", "api", "sql-injection", "input-validation", "automation"],
        "components": ["focus-server", "api", "security"]
    },
    "SEC-005": {
        "summary": "Security - XSS Prevention",
        "description": """h2. Objective
Verify that API endpoints properly sanitize input and prevent Cross-Site Scripting (XSS) attacks.

h2. Pre-Conditions
* Focus Server API is running and accessible
* Input sanitization is configured

h2. Test Data
* XSS payloads:
  * `<script>alert('XSS')</script>`
  * `<img src=x onerror=alert('XSS')>`
  * `javascript:alert('XSS')`
  * `<svg onload=alert('XSS')>`

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Send POST /configure with XSS in task_id | task_id: "<script>alert('XSS')</script>" | Request rejected or sanitized |
| 2 | Send POST /configure with XSS in payload fields | Various XSS payloads | Request rejected or sanitized |
| 3 | Verify response does not contain executable scripts | Check response content | No scripts in response |

h2. Expected Result
XSS attempts are prevented and input is properly sanitized.

h2. Assertions
* XSS payloads are rejected or sanitized
* Response does not contain executable scripts
* HTML/JavaScript is properly escaped

h2. Automation Status
✅ Automated

*Test Function:* `test_xss_prevention`
*Test File:* `tests/integration/security/test_input_validation.py`
*Test Class:* `TestInputValidation`
""",
        "priority": "High",
        "labels": ["security", "api", "xss", "input-validation", "automation"],
        "components": ["focus-server", "api", "security"]
    },
    "SEC-006": {
        "summary": "Security - CSRF Protection",
        "description": """h2. Objective
Verify that API endpoints implement CSRF (Cross-Site Request Forgery) protection.

h2. Pre-Conditions
* Focus Server API is running and accessible
* CSRF protection is configured (if applicable)

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Send POST request without CSRF token | No CSRF token | Request rejected (if CSRF enabled) |
| 2 | Send POST request with invalid CSRF token | Invalid CSRF token | Request rejected |
| 3 | Send POST request with valid CSRF token | Valid CSRF token | Request accepted (if CSRF enabled) |

h2. Expected Result
CSRF protection is properly implemented (if applicable to the API design).

h2. Assertions
* CSRF tokens are validated (if CSRF protection is enabled)
* Invalid CSRF tokens are rejected
* API behavior matches security requirements

h2. Automation Status
✅ Automated

*Test Function:* `test_csrf_protection`
*Test File:* `tests/integration/security/test_csrf.py`
*Test Class:* `TestCSRFProtection`

h2. Notes
* CSRF protection may not be required for REST APIs using token authentication
* Verify security requirements for this API
""",
        "priority": "High",
        "labels": ["security", "api", "csrf", "automation"],
        "components": ["focus-server", "api", "security"]
    },
    "SEC-007": {
        "summary": "Security - Rate Limiting",
        "description": """h2. Objective
Verify that API endpoints implement rate limiting to prevent abuse and DoS attacks.

h2. Pre-Conditions
* Focus Server API is running and accessible
* Rate limiting is configured

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Send multiple rapid requests to POST /configure | 100 requests in 1 second | Rate limit enforced |
| 2 | Verify rate limit response | Check response headers | HTTP 429 Too Many Requests |
| 3 | Wait for rate limit window | Wait for rate limit reset | Requests accepted after reset |

h2. Expected Result
Rate limiting is properly enforced to prevent API abuse.

h2. Assertions
* Rate limit is enforced after threshold
* HTTP 429 returned when rate limit exceeded
* Rate limit headers present (X-RateLimit-*)
* Requests accepted after rate limit window resets

h2. Automation Status
✅ Automated

*Test Function:* `test_rate_limiting`
*Test File:* `tests/integration/security/test_rate_limiting.py`
*Test Class:* `TestRateLimiting`

h2. Notes
* Rate limit thresholds may vary by endpoint
* Verify actual rate limit configuration
""",
        "priority": "High",
        "labels": ["security", "api", "rate-limiting", "automation"],
        "components": ["focus-server", "api", "security"]
    },
    "SEC-008": {
        "summary": "Security - Input Sanitization",
        "description": """h2. Objective
Verify that API endpoints properly sanitize and validate all input parameters.

h2. Pre-Conditions
* Focus Server API is running and accessible
* Input validation is configured

h2. Test Data
* Special characters: `<>\"'&{}[]`
* Unicode characters: `\u2028`, `\u2029` (line separators)
* Control characters: `\n`, `\r`, `\t`
* Path traversal: `../../../etc/passwd`

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Send request with special characters in input | Various special chars | Input sanitized or rejected |
| 2 | Send request with Unicode characters | Unicode chars | Input handled correctly |
| 3 | Send request with control characters | Control chars | Input sanitized or rejected |
| 4 | Send request with path traversal attempts | Path traversal | Request rejected |

h2. Expected Result
All input is properly sanitized and validated before processing.

h2. Assertions
* Special characters are handled safely
* Unicode characters are processed correctly
* Control characters are sanitized
* Path traversal attempts are rejected

h2. Automation Status
✅ Automated

*Test Function:* `test_input_sanitization`
*Test File:* `tests/integration/security/test_input_validation.py`
*Test Class:* `TestInputValidation`
""",
        "priority": "High",
        "labels": ["security", "api", "input-validation", "sanitization", "automation"],
        "components": ["focus-server", "api", "security"]
    },
    "SEC-009": {
        "summary": "Security - HTTPS Only",
        "description": """h2. Objective
Verify that API endpoints enforce HTTPS and reject HTTP requests.

h2. Pre-Conditions
* Focus Server API is running and accessible
* HTTPS is configured

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Send HTTP request to POST /configure | HTTP (not HTTPS) | Request rejected or redirected |
| 2 | Send HTTP request to GET /waterfall | HTTP (not HTTPS) | Request rejected or redirected |
| 3 | Verify HTTPS is enforced | Check response | HTTPS required |

h2. Expected Result
All HTTP requests are rejected or redirected to HTTPS.

h2. Assertions
* HTTP requests are rejected or redirected
* HTTPS is enforced for all endpoints
* Security headers present (Strict-Transport-Security)

h2. Automation Status
✅ Automated

*Test Function:* `test_https_only`
*Test File:* `tests/integration/security/test_https.py`
*Test Class:* `TestHTTPSEnforcement`

h2. Notes
* In staging, HTTP may be allowed for testing
* Verify production requirements
""",
        "priority": "High",
        "labels": ["security", "api", "https", "tls", "automation"],
        "components": ["focus-server", "api", "security"]
    },
    "SEC-010": {
        "summary": "Security - Sensitive Data Exposure",
        "description": """h2. Objective
Verify that API responses and error messages do not expose sensitive information.

h2. Pre-Conditions
* Focus Server API is running and accessible
* Error handling is configured

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Send invalid request and check error response | Invalid payload | Error message does not expose sensitive data |
| 2 | Send request causing server error | Trigger 500 error | Error message does not expose stack traces |
| 3 | Verify no credentials in responses | Check all responses | No passwords, tokens, or keys exposed |
| 4 | Verify no database details in errors | Check error messages | No database structure or queries exposed |

h2. Expected Result
No sensitive information is exposed in API responses or error messages.

h2. Assertions
* Error messages are generic and safe
* No stack traces in production responses
* No credentials in responses
* No database details in error messages

h2. Automation Status
✅ Automated

*Test Function:* `test_sensitive_data_exposure`
*Test File:* `tests/integration/security/test_data_exposure.py`
*Test Class:* `TestDataExposure`
""",
        "priority": "High",
        "labels": ["security", "api", "data-exposure", "error-handling", "automation"],
        "components": ["focus-server", "api", "security"]
    }
}


def create_security_test(
    client: JiraClient,
    test_id: str,
    test_data: Dict[str, Any],
    dry_run: bool = False
) -> str:
    """
    Create a security test in Jira Xray.
    
    Args:
        client: JiraClient instance
        test_id: Test identifier (e.g., "SEC-001")
        test_data: Test data dictionary
        dry_run: If True, only preview without creating
        
    Returns:
        Created issue key (e.g., "PZ-14765")
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
        description='Create security tests in Jira Xray'
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
        logger.info(f"{'[DRY RUN] ' if args.dry_run else ''}Creating Security Tests")
        logger.info("=" * 80)
        
        created_tests = []
        failed_tests = []
        
        for test_id, test_data in SECURITY_TESTS.items():
            try:
                issue_key = create_security_test(
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
        print(f"Total tests: {len(SECURITY_TESTS)}")
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

