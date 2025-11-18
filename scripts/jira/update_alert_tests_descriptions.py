"""
Script to update Alert Generation Xray test cases descriptions in Jira
using Atlassian API directly.

Tests: PZ-14933 to PZ-14963 (31 tests)
"""

import os
import sys
import re
from typing import Dict, List, Any
from pathlib import Path

# Test descriptions in Jira markup format
TEST_DESCRIPTIONS = {
    'PZ-14933': """h2. Objective
Verify that SD (Spatial Distribution) alerts can be successfully generated and processed through the backend system.

h2. Test Details
* *Test ID:* PZ-14933
* *Test Type:* Integration Test
* *Category:* Positive
* *File:* be_focus_server_tests/integration/alerts/test_alert_generation_positive.py
* *Function:* {code}test_successful_sd_alert_generation{code}

h2. Prerequisites
* Focus Server API is available and healthy
* Backend system is running and accessible
* Valid configuration manager with API credentials

h2. Test Data
* *Alert Type:* SD (Spatial Distribution)
* *Class ID:* 104
* *DOF (Distance on Fiber):* 4163 meters
* *Severity:* 3 (High)
* *Alert ID Format:* test-sd-{timestamp}

h2. Test Steps

|| # || Action || Data || Expected Result ||
| 1 | Create SD alert payload | classId=104, dofM=4163, severity=3 | Payload created successfully |
| 2 | Send alert via HTTP API | push-to-rabbit endpoint | HTTP status 200/201 |
| 3 | Verify response status | Check status code | Status code is 200 or 201 |
| 4 | Log response details | Response text and status | Details logged for verification |

h2. Expected Result
Alert is successfully generated and sent via HTTP API with status code 200 or 201. The alert payload is correctly formatted and processed by the backend system.

h2. Post-Conditions
* Alert is sent to RabbitMQ queue
* System remains stable and operational

h2. Automation Status
✅ *Automated* with Pytest

*Test Function:* {code}test_successful_sd_alert_generation{code}
*Test File:* {code}be_focus_server_tests/integration/alerts/test_alert_generation_positive.py{code}""",

    'PZ-14934': """h2. Objective
Verify that SC (Single Channel) alerts can be successfully generated and processed through the backend system.

h2. Test Details
* *Test ID:* PZ-14934
* *Test Type:* Integration Test
* *Category:* Positive
* *File:* be_focus_server_tests/integration/alerts/test_alert_generation_positive.py
* *Function:* {code}test_successful_sc_alert_generation{code}

h2. Prerequisites
* Focus Server API is available and healthy
* Backend system is running and accessible
* Valid configuration manager with API credentials

h2. Test Data
* *Alert Type:* SC (Single Channel)
* *Class ID:* 103
* *DOF (Distance on Fiber):* 5682 meters
* *Severity:* 2 (Medium)
* *Alert ID Format:* test-sc-{timestamp}

h2. Test Steps

|| # || Action || Data || Expected Result ||
| 1 | Create SC alert payload | classId=103, dofM=5682, severity=2 | Payload created successfully |
| 2 | Send alert via HTTP API | push-to-rabbit endpoint | HTTP status 200/201 |
| 3 | Verify response status | Check status code | Status code is 200 or 201 |
| 4 | Log response details | Response text and status | Details logged for verification |

h2. Expected Result
Alert is successfully generated and sent via HTTP API with status code 200 or 201. The alert payload is correctly formatted and processed by the backend system.

h2. Post-Conditions
* Alert is sent to RabbitMQ queue
* System remains stable and operational

h2. Automation Status
✅ *Automated* with Pytest

*Test Function:* {code}test_successful_sc_alert_generation{code}
*Test File:* {code}be_focus_server_tests/integration/alerts/test_alert_generation_positive.py{code}""",

    'PZ-14938': """h2. Objective
Verify that alerts with invalid class IDs are rejected by the system with appropriate error handling.

h2. Test Details
* *Test ID:* PZ-14938
* *Test Type:* Integration Test
* *Category:* Negative
* *File:* be_focus_server_tests/integration/alerts/test_alert_generation_negative.py
* *Function:* {code}test_invalid_class_id{code}

h2. Prerequisites
* Focus Server API is available and healthy
* Backend system is running and accessible
* Valid configuration manager with API credentials

h2. Test Data
* *Invalid Class IDs:* 0, 1, 100, 105, 999, -1
* *Valid Class IDs:* 103 (SC), 104 (SD)
* *DOF:* 5000 meters
* *Severity:* 3 (High)

h2. Test Steps

|| # || Action || Data || Expected Result ||
| 1 | Iterate through invalid class IDs | [0, 1, 100, 105, 999, -1] | All IDs processed |
| 2 | Create alert payload with invalid class ID | classId=<invalid>, dofM=5000, severity=3 | Payload created |
| 3 | Attempt to send alert via HTTP API | push-to-rabbit endpoint | Request sent |
| 4 | Verify rejection | Check status code | Status code >= 400 |
| 5 | Log rejection details | Status code and response | Details logged |
| 6 | Verify at least some rejections | Count rejected alerts | At least one rejection |

h2. Expected Result
Alerts with invalid class IDs are rejected with appropriate error message. HTTP status code should be 400 (Bad Request) or 422 (Unprocessable Entity). At least some invalid class IDs must be rejected to pass the test.

h2. Post-Conditions
* No invalid alerts are processed by the system
* System remains stable and operational

h2. Automation Status
✅ *Automated* with Pytest

*Test Function:* {code}test_invalid_class_id{code}
*Test File:* {code}be_focus_server_tests/integration/alerts/test_alert_generation_negative.py{code}"""
}

# Continue with remaining tests...
# For brevity, I'll create a function to generate descriptions dynamically

