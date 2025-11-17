#!/usr/bin/env python3
"""
Create Xray Tests for API Endpoints (Missing Coverage)
======================================================

This script creates 15 new API endpoint tests in Jira Xray Test Repository.

Tests Created:
- POST /config/{task_id} (5 tests)
- GET /waterfall/{task_id}/{row_count} (5 tests)
- GET /metadata/{task_id} (5 tests)

Usage:
    python scripts/jira/create_api_endpoints_tests.py
    python scripts/jira/create_api_endpoints_tests.py --dry-run
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

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

# Test Type Field ID
TEST_TYPE_FIELD_ID = "customfield_10951"

# Test definitions
API_ENDPOINTS_TESTS = {
    # POST /config/{task_id} Tests (5 tests)
    "API-001": {
        "summary": "API - POST /config/{task_id} - Valid Configuration",
        "description": """h2. Objective
Validate that POST /config/{{task_id}} endpoint accepts valid configuration requests and returns 200 OK with proper response structure.

h2. Test Type
Integration Test

h2. Priority
P1 - High

h2. Components/Labels
focus-server, api, config-task, automation

h2. Pre-Conditions
* Focus Server is accessible
* System components are running
* Test environment is configured
* Valid task_id can be generated

h2. Test Data
* task_id: Generated unique task identifier
* displayTimeAxisDuration: 10
* nfftSelection: 1024
* canvasInfo: {{"height": 1000}}
* sensors: {{"min": 1, "max": 50}}
* frequencyRange: {{"min": 0, "max": 500}}
* start_time: null (live mode)
* end_time: null (live mode)

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Generate unique task_id | task_id = "test-task-{timestamp}" | task_id generated successfully |
| 2 | Prepare valid configuration payload | ConfigTaskRequest with all required fields | Payload prepared |
| 3 | Send POST /config/{{task_id}} request | Valid payload | Status code: 200 OK |
| 4 | Verify response structure | Response contains status and task_id fields | Response structure is valid |
| 5 | Verify task_id in response | Response.task_id matches request task_id | task_id matches |

h2. Expected Result
* Request returns 200 OK
* Response contains status field
* Response contains task_id field matching request
* No errors occur

h2. Assertions
* Status code is 200
* Response.status is present
* Response.task_id matches request task_id
* Response is valid JSON

h2. Post-Conditions
* Task is configured and ready for use
* System state is consistent

h2. Automation Status
✅ *Automated* with Pytest

*Test Function:* {{code}}test_config_task_valid_configuration{{code}}
*Test File:* {{code}}tests/integration/api/test_config_task_endpoint.py{{code}}
*Test Class:* {{code}}TestConfigTaskEndpoint{{code}}

*Execution Command:*
{{code}}pytest tests/integration/api/test_config_task_endpoint.py::TestConfigTaskEndpoint::test_config_task_valid_configuration -v{{code}}
""",
        "priority": "High",
        "labels": ["api", "focus-server", "config-task", "automation", "api_test_panda"],
        "components": ["focus-server", "api"]
    },
    
    "API-002": {
        "summary": "API - POST /config/{task_id} - Invalid Task ID",
        "description": """h2. Objective
Validate that POST /config/{{task_id}} endpoint properly rejects invalid task_id formats and returns appropriate error response.

h2. Test Type
Integration Test

h2. Priority
P1 - High

h2. Components/Labels
focus-server, api, config-task, validation, automation

h2. Pre-Conditions
* Focus Server is accessible
* System components are running

h2. Test Data
* Invalid task_id formats: empty string, null, special characters, very long string
* Valid configuration payload (for comparison)

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Prepare invalid task_id (empty string) | task_id = "" | Invalid task_id prepared |
| 2 | Send POST /config/{{task_id}} request | Empty task_id | Status code: 400 Bad Request |
| 3 | Prepare invalid task_id (null) | task_id = null | Invalid task_id prepared |
| 4 | Send POST /config/{{task_id}} request | Null task_id | Status code: 400 Bad Request |
| 5 | Prepare invalid task_id (special chars) | task_id = "test@#$%task" | Invalid task_id prepared |
| 6 | Send POST /config/{{task_id}} request | Special chars task_id | Status code: 400 Bad Request |

h2. Expected Result
* All invalid task_id formats are rejected
* Status code is 400 Bad Request
* Error message indicates invalid task_id

h2. Assertions
* Status code is 400 for all invalid formats
* Error message is present and descriptive
* No task is created

h2. Post-Conditions
* No tasks are created
* System state is unchanged

h2. Automation Status
✅ *Automated* with Pytest

*Test Function:* {{code}}test_config_task_invalid_task_id{{code}}
*Test File:* {{code}}tests/integration/api/test_config_task_endpoint.py{{code}}
*Test Class:* {{code}}TestConfigTaskEndpoint{{code}}
""",
        "priority": "High",
        "labels": ["api", "focus-server", "config-task", "validation", "automation", "api_test_panda"],
        "components": ["focus-server", "api"]
    },
    
    "API-003": {
        "summary": "API - POST /config/{task_id} - Missing Required Fields",
        "description": """h2. Objective
Validate that POST /config/{{task_id}} endpoint properly rejects requests with missing required fields and returns 422 Unprocessable Entity.

h2. Test Type
Integration Test

h2. Priority
P1 - High

h2. Components/Labels
focus-server, api, config-task, validation, automation

h2. Pre-Conditions
* Focus Server is accessible
* System components are running
* Valid task_id can be generated

h2. Test Data
* task_id: Generated unique task identifier
* Test cases: Missing displayTimeAxisDuration, nfftSelection, canvasInfo, sensors, frequencyRange

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Generate unique task_id | task_id = "test-task-{timestamp}" | task_id generated |
| 2 | Prepare payload missing displayTimeAxisDuration | Payload without displayTimeAxisDuration | Payload prepared |
| 3 | Send POST /config/{{task_id}} request | Missing field payload | Status code: 422 Unprocessable Entity |
| 4 | Prepare payload missing nfftSelection | Payload without nfftSelection | Payload prepared |
| 5 | Send POST /config/{{task_id}} request | Missing field payload | Status code: 422 Unprocessable Entity |
| 6 | Prepare payload missing canvasInfo | Payload without canvasInfo | Payload prepared |
| 7 | Send POST /config/{{task_id}} request | Missing field payload | Status code: 422 Unprocessable Entity |
| 8 | Prepare payload missing sensors | Payload without sensors | Payload prepared |
| 9 | Send POST /config/{{task_id}} request | Missing field payload | Status code: 422 Unprocessable Entity |

h2. Expected Result
* All requests with missing required fields are rejected
* Status code is 422 Unprocessable Entity
* Error message indicates which field is missing

h2. Assertions
* Status code is 422 for all missing fields
* Error message is present and descriptive
* No task is created

h2. Post-Conditions
* No tasks are created
* System state is unchanged

h2. Automation Status
✅ *Automated* with Pytest

*Test Function:* {{code}}test_config_task_missing_required_fields{{code}}
*Test File:* {{code}}tests/integration/api/test_config_task_endpoint.py{{code}}
*Test Class:* {{code}}TestConfigTaskEndpoint{{code}}
""",
        "priority": "High",
        "labels": ["api", "focus-server", "config-task", "validation", "automation", "api_test_panda"],
        "components": ["focus-server", "api"]
    },
    
    "API-004": {
        "summary": "API - POST /config/{task_id} - Invalid Sensor Range",
        "description": """h2. Objective
Validate that POST /config/{{task_id}} endpoint properly rejects invalid sensor range configurations and returns 400 Bad Request.

h2. Test Type
Integration Test

h2. Priority
P2 - Medium

h2. Components/Labels
focus-server, api, config-task, validation, automation

h2. Pre-Conditions
* Focus Server is accessible
* System components are running
* Valid task_id can be generated

h2. Test Data
* task_id: Generated unique task identifier
* Invalid sensor ranges: min > max, negative values, out of bounds

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Generate unique task_id | task_id = "test-task-{timestamp}" | task_id generated |
| 2 | Prepare payload with min > max | sensors: {{"min": 50, "max": 1}} | Invalid payload prepared |
| 3 | Send POST /config/{{task_id}} request | Invalid sensor range | Status code: 400 Bad Request |
| 4 | Prepare payload with negative min | sensors: {{"min": -1, "max": 50}} | Invalid payload prepared |
| 5 | Send POST /config/{{task_id}} request | Negative sensor value | Status code: 400 Bad Request |
| 6 | Prepare payload with out of bounds max | sensors: {{"min": 1, "max": 100000}} | Invalid payload prepared |
| 7 | Send POST /config/{{task_id}} request | Out of bounds sensor | Status code: 400 Bad Request |

h2. Expected Result
* All invalid sensor ranges are rejected
* Status code is 400 Bad Request
* Error message indicates invalid sensor range

h2. Assertions
* Status code is 400 for all invalid ranges
* Error message is present and descriptive
* No task is created

h2. Post-Conditions
* No tasks are created
* System state is unchanged

h2. Automation Status
✅ *Automated* with Pytest

*Test Function:* {{code}}test_config_task_invalid_sensor_range{{code}}
*Test File:* {{code}}tests/integration/api/test_config_task_endpoint.py{{code}}
*Test Class:* {{code}}TestConfigTaskEndpoint{{code}}
""",
        "priority": "Medium",
        "labels": ["api", "focus-server", "config-task", "validation", "automation", "api_test_panda"],
        "components": ["focus-server", "api"]
    },
    
    "API-005": {
        "summary": "API - POST /config/{task_id} - Invalid Frequency Range",
        "description": """h2. Objective
Validate that POST /config/{{task_id}} endpoint properly rejects invalid frequency range configurations and returns 400 Bad Request.

h2. Test Type
Integration Test

h2. Priority
P2 - Medium

h2. Components/Labels
focus-server, api, config-task, validation, automation

h2. Pre-Conditions
* Focus Server is accessible
* System components are running
* Valid task_id can be generated

h2. Test Data
* task_id: Generated unique task identifier
* Invalid frequency ranges: min > max, negative values, exceeds Nyquist limit

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Generate unique task_id | task_id = "test-task-{timestamp}" | task_id generated |
| 2 | Prepare payload with min > max | frequencyRange: {{"min": 500, "max": 0}} | Invalid payload prepared |
| 3 | Send POST /config/{{task_id}} request | Invalid frequency range | Status code: 400 Bad Request |
| 4 | Prepare payload with negative min | frequencyRange: {{"min": -1, "max": 500}} | Invalid payload prepared |
| 5 | Send POST /config/{{task_id}} request | Negative frequency value | Status code: 400 Bad Request |
| 6 | Prepare payload exceeding Nyquist | frequencyRange: {{"min": 0, "max": 2000}} (PRR=2000) | Invalid payload prepared |
| 7 | Send POST /config/{{task_id}} request | Exceeds Nyquist limit | Status code: 400 Bad Request |

h2. Expected Result
* All invalid frequency ranges are rejected
* Status code is 400 Bad Request
* Error message indicates invalid frequency range

h2. Assertions
* Status code is 400 for all invalid ranges
* Error message is present and descriptive
* No task is created

h2. Post-Conditions
* No tasks are created
* System state is unchanged

h2. Automation Status
✅ *Automated* with Pytest

*Test Function:* {{code}}test_config_task_invalid_frequency_range{{code}}
*Test File:* {{code}}tests/integration/api/test_config_task_endpoint.py{{code}}
*Test Class:* {{code}}TestConfigTaskEndpoint{{code}}
""",
        "priority": "Medium",
        "labels": ["api", "focus-server", "config-task", "validation", "automation", "api_test_panda"],
        "components": ["focus-server", "api"]
    },
    
    # GET /waterfall/{task_id}/{row_count} Tests (5 tests)
    "API-006": {
        "summary": "API - GET /waterfall/{task_id}/{row_count} - Valid Request",
        "description": """h2. Objective
Validate that GET /waterfall/{{task_id}}/{{row_count}} endpoint returns 201 Created with waterfall data when data is available.

h2. Test Type
Integration Test

h2. Priority
P1 - High

h2. Components/Labels
focus-server, api, waterfall, automation

h2. Pre-Conditions
* Focus Server is accessible
* Task is configured and running
* Waterfall data is available

h2. Test Data
* task_id: Valid configured task identifier
* row_count: 10 (valid positive integer)

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Configure a task | POST /config/{{task_id}} | Task configured successfully |
| 2 | Wait for task to start processing | Wait 5 seconds | Task is processing |
| 3 | Send GET /waterfall/{{task_id}}/{{row_count}} request | row_count = 10 | Status code: 201 Created |
| 4 | Verify response structure | Response contains data array | Response structure is valid |
| 5 | Verify waterfall data structure | Data contains rows, sensors, timestamps | Data structure is valid |

h2. Expected Result
* Request returns 201 Created
* Response contains waterfall data
* Data structure is valid

h2. Assertions
* Status code is 201
* Response.data is present and is a list
* Each row contains required fields (canvasId, sensors, startTimestamp, endTimestamp)
* Timestamps are valid

h2. Post-Conditions
* Task continues running
* System state is consistent

h2. Automation Status
✅ *Automated* with Pytest

*Test Function:* {{code}}test_waterfall_valid_request{{code}}
*Test File:* {{code}}tests/integration/api/test_waterfall_endpoint.py{{code}}
*Test Class:* {{code}}TestWaterfallEndpoint{{code}}
""",
        "priority": "High",
        "labels": ["api", "focus-server", "waterfall", "automation", "api_test_panda"],
        "components": ["focus-server", "api"]
    },
    
    "API-007": {
        "summary": "API - GET /waterfall/{task_id}/{row_count} - No Data Available",
        "description": """h2. Objective
Validate that GET /waterfall/{{task_id}}/{{row_count}} endpoint returns 200 OK with empty response when no data is available yet.

h2. Test Type
Integration Test

h2. Priority
P2 - Medium

h2. Components/Labels
focus-server, api, waterfall, automation

h2. Pre-Conditions
* Focus Server is accessible
* Task is configured but not yet processing

h2. Test Data
* task_id: Valid configured task identifier
* row_count: 10

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Configure a task | POST /config/{{task_id}} | Task configured successfully |
| 2 | Immediately request waterfall data | GET /waterfall/{{task_id}}/10 | Status code: 200 OK |
| 3 | Verify response is empty | Response has no data | Response is empty |

h2. Expected Result
* Request returns 200 OK
* Response indicates no data available
* No errors occur

h2. Assertions
* Status code is 200
* Response.data is None or empty
* No errors occur

h2. Post-Conditions
* Task continues running
* System state is consistent

h2. Automation Status
✅ *Automated* with Pytest

*Test Function:* {{code}}test_waterfall_no_data_available{{code}}
*Test File:* {{code}}tests/integration/api/test_waterfall_endpoint.py{{code}}
*Test Class:* {{code}}TestWaterfallEndpoint{{code}}
""",
        "priority": "Medium",
        "labels": ["api", "focus-server", "waterfall", "automation", "api_test_panda"],
        "components": ["focus-server", "api"]
    },
    
    "API-008": {
        "summary": "API - GET /waterfall/{task_id}/{row_count} - Invalid Task ID",
        "description": """h2. Objective
Validate that GET /waterfall/{{task_id}}/{{row_count}} endpoint returns 404 Not Found for invalid task_id.

h2. Test Type
Integration Test

h2. Priority
P1 - High

h2. Components/Labels
focus-server, api, waterfall, validation, automation

h2. Pre-Conditions
* Focus Server is accessible

h2. Test Data
* Invalid task_id: "nonexistent-task-12345"
* row_count: 10

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Send GET /waterfall/{{task_id}}/{{row_count}} request | Invalid task_id | Status code: 404 Not Found |
| 2 | Verify error response | Response indicates task not found | Error message is present |

h2. Expected Result
* Request returns 404 Not Found
* Error message indicates task not found
* No data is returned

h2. Assertions
* Status code is 404
* Error message is present and descriptive
* No data is returned

h2. Post-Conditions
* System state is unchanged

h2. Automation Status
✅ *Automated* with Pytest

*Test Function:* {{code}}test_waterfall_invalid_task_id{{code}}
*Test File:* {{code}}tests/integration/api/test_waterfall_endpoint.py{{code}}
*Test Class:* {{code}}TestWaterfallEndpoint{{code}}
""",
        "priority": "High",
        "labels": ["api", "focus-server", "waterfall", "validation", "automation", "api_test_panda"],
        "components": ["focus-server", "api"]
    },
    
    "API-009": {
        "summary": "API - GET /waterfall/{task_id}/{row_count} - Invalid Row Count",
        "description": """h2. Objective
Validate that GET /waterfall/{{task_id}}/{{row_count}} endpoint returns 400 Bad Request for invalid row_count values (0 or negative).

h2. Test Type
Integration Test

h2. Priority
P2 - Medium

h2. Components/Labels
focus-server, api, waterfall, validation, automation

h2. Pre-Conditions
* Focus Server is accessible
* Valid task_id exists

h2. Test Data
* task_id: Valid configured task identifier
* Invalid row_count values: 0, -1, -10

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Configure a task | POST /config/{{task_id}} | Task configured successfully |
| 2 | Send GET /waterfall/{{task_id}}/0 request | row_count = 0 | Status code: 400 Bad Request |
| 3 | Send GET /waterfall/{{task_id}}/-1 request | row_count = -1 | Status code: 400 Bad Request |
| 4 | Send GET /waterfall/{{task_id}}/-10 request | row_count = -10 | Status code: 400 Bad Request |

h2. Expected Result
* All invalid row_count values are rejected
* Status code is 400 Bad Request
* Error message indicates invalid row_count

h2. Assertions
* Status code is 400 for all invalid values
* Error message is present and descriptive
* No data is returned

h2. Post-Conditions
* Task continues running
* System state is unchanged

h2. Automation Status
✅ *Automated* with Pytest

*Test Function:* {{code}}test_waterfall_invalid_row_count{{code}}
*Test File:* {{code}}tests/integration/api/test_waterfall_endpoint.py{{code}}
*Test Class:* {{code}}TestWaterfallEndpoint{{code}}
""",
        "priority": "Medium",
        "labels": ["api", "focus-server", "waterfall", "validation", "automation", "api_test_panda"],
        "components": ["focus-server", "api"]
    },
    
    "API-010": {
        "summary": "API - GET /waterfall/{task_id}/{row_count} - Baby Analyzer Exited",
        "description": """h2. Objective
Validate that GET /waterfall/{{task_id}}/{{row_count}} endpoint returns 208 Already Reported when baby analyzer has exited.

h2. Test Type
Integration Test

h2. Priority
P2 - Medium

h2. Components/Labels
focus-server, api, waterfall, automation

h2. Pre-Conditions
* Focus Server is accessible
* Task has completed and baby analyzer has exited

h2. Test Data
* task_id: Valid completed task identifier
* row_count: 10

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Configure a historic playback task | POST /config/{{task_id}} | Task configured successfully |
| 2 | Wait for task to complete | Wait until status 208 | Task completed |
| 3 | Send GET /waterfall/{{task_id}}/{{row_count}} request | row_count = 10 | Status code: 208 Already Reported |
| 4 | Verify response indicates completion | Response indicates analyzer exited | Status is 208 |

h2. Expected Result
* Request returns 208 Already Reported
* Response indicates baby analyzer has exited
* No errors occur

h2. Assertions
* Status code is 208
* Response indicates completion
* No errors occur

h2. Post-Conditions
* Task is completed
* System state is consistent

h2. Automation Status
✅ *Automated* with Pytest

*Test Function:* {{code}}test_waterfall_baby_analyzer_exited{{code}}
*Test File:* {{code}}tests/integration/api/test_waterfall_endpoint.py{{code}}
*Test Class:* {{code}}TestWaterfallEndpoint{{code}}
""",
        "priority": "Medium",
        "labels": ["api", "focus-server", "waterfall", "automation", "api_test_panda"],
        "components": ["focus-server", "api"]
    },
    
    # GET /metadata/{task_id} Tests (5 tests)
    "API-011": {
        "summary": "API - GET /metadata/{task_id} - Valid Request",
        "description": """h2. Objective
Validate that GET /metadata/{{task_id}} endpoint returns 201 Created with metadata when consumer is running.

h2. Test Type
Integration Test

h2. Priority
P1 - High

h2. Components/Labels
focus-server, api, metadata, automation

h2. Pre-Conditions
* Focus Server is accessible
* Task is configured and consumer is running

h2. Test Data
* task_id: Valid configured task identifier

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Configure a task | POST /config/{{task_id}} | Task configured successfully |
| 2 | Wait for consumer to start | Wait 5 seconds | Consumer is running |
| 3 | Send GET /metadata/{{task_id}} request | task_id | Status code: 201 Created |
| 4 | Verify response structure | Response contains metadata | Response structure is valid |
| 5 | Verify metadata fields | Metadata contains prr, dx, number_of_channels | Metadata fields are present |

h2. Expected Result
* Request returns 201 Created
* Response contains metadata
* Metadata structure is valid

h2. Assertions
* Status code is 201
* Response.metadata is present
* Metadata contains required fields (prr, dx, number_of_channels)
* Metadata values are valid

h2. Post-Conditions
* Task continues running
* System state is consistent

h2. Automation Status
✅ *Automated* with Pytest

*Test Function:* {{code}}test_task_metadata_valid_request{{code}}
*Test File:* {{code}}tests/integration/api/test_task_metadata_endpoint.py{{code}}
*Test Class:* {{code}}TestTaskMetadataEndpoint{{code}}
""",
        "priority": "High",
        "labels": ["api", "focus-server", "metadata", "automation", "api_test_panda"],
        "components": ["focus-server", "api"]
    },
    
    "API-012": {
        "summary": "API - GET /metadata/{task_id} - Consumer Not Running",
        "description": """h2. Objective
Validate that GET /metadata/{{task_id}} endpoint returns 200 OK with empty response when consumer is not running.

h2. Test Type
Integration Test

h2. Priority
P2 - Medium

h2. Components/Labels
focus-server, api, metadata, automation

h2. Pre-Conditions
* Focus Server is accessible
* Task is configured but consumer is not running

h2. Test Data
* task_id: Valid configured task identifier

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Configure a task | POST /config/{{task_id}} | Task configured successfully |
| 2 | Immediately request metadata | GET /metadata/{{task_id}} | Status code: 200 OK |
| 3 | Verify response is empty | Response has no metadata | Response is empty |

h2. Expected Result
* Request returns 200 OK
* Response indicates consumer not running
* No errors occur

h2. Assertions
* Status code is 200
* Response.metadata is None or empty
* No errors occur

h2. Post-Conditions
* Task continues running
* System state is consistent

h2. Automation Status
✅ *Automated* with Pytest

*Test Function:* {{code}}test_task_metadata_consumer_not_running{{code}}
*Test File:* {{code}}tests/integration/api/test_task_metadata_endpoint.py{{code}}
*Test Class:* {{code}}TestTaskMetadataEndpoint{{code}}
""",
        "priority": "Medium",
        "labels": ["api", "focus-server", "metadata", "automation", "api_test_panda"],
        "components": ["focus-server", "api"]
    },
    
    "API-013": {
        "summary": "API - GET /metadata/{task_id} - Invalid Task ID",
        "description": """h2. Objective
Validate that GET /metadata/{{task_id}} endpoint returns 404 Not Found for invalid task_id.

h2. Test Type
Integration Test

h2. Priority
P1 - High

h2. Components/Labels
focus-server, api, metadata, validation, automation

h2. Pre-Conditions
* Focus Server is accessible

h2. Test Data
* Invalid task_id: "nonexistent-task-12345"

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Send GET /metadata/{{task_id}} request | Invalid task_id | Status code: 404 Not Found |
| 2 | Verify error response | Response indicates task not found | Error message is present |

h2. Expected Result
* Request returns 404 Not Found
* Error message indicates task not found
* No metadata is returned

h2. Assertions
* Status code is 404
* Error message is present and descriptive
* No metadata is returned

h2. Post-Conditions
* System state is unchanged

h2. Automation Status
✅ *Automated* with Pytest

*Test Function:* {{code}}test_task_metadata_invalid_task_id{{code}}
*Test File:* {{code}}tests/integration/api/test_task_metadata_endpoint.py{{code}}
*Test Class:* {{code}}TestTaskMetadataEndpoint{{code}}
""",
        "priority": "High",
        "labels": ["api", "focus-server", "metadata", "validation", "automation", "api_test_panda"],
        "components": ["focus-server", "api"]
    },
    
    "API-014": {
        "summary": "API - GET /metadata/{task_id} - Metadata Consistency",
        "description": """h2. Objective
Validate that metadata returned by GET /metadata/{{task_id}} is consistent with the task configuration.

h2. Test Type
Integration Test

h2. Priority
P2 - Medium

h2. Components/Labels
focus-server, api, metadata, validation, automation

h2. Pre-Conditions
* Focus Server is accessible
* Task is configured and consumer is running

h2. Test Data
* task_id: Valid configured task identifier
* Configuration parameters: sensors range, frequency range

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Configure a task with specific parameters | POST /config/{{task_id}} | Task configured |
| 2 | Wait for consumer to start | Wait 5 seconds | Consumer is running |
| 3 | Get task metadata | GET /metadata/{{task_id}} | Metadata retrieved |
| 4 | Verify metadata matches configuration | Compare metadata with config | Metadata is consistent |
| 5 | Verify sensor count matches | number_of_channels matches sensors range | Sensor count matches |

h2. Expected Result
* Metadata is consistent with configuration
* Sensor count matches configuration
* No inconsistencies found

h2. Assertions
* Metadata.number_of_channels matches configuration sensors range
* Metadata.prr is valid (> 0)
* Metadata.dx is valid (> 0)
* No inconsistencies

h2. Post-Conditions
* Task continues running
* System state is consistent

h2. Automation Status
✅ *Automated* with Pytest

*Test Function:* {{code}}test_task_metadata_consistency{{code}}
*Test File:* {{code}}tests/integration/api/test_task_metadata_endpoint.py{{code}}
*Test Class:* {{code}}TestTaskMetadataEndpoint{{code}}
""",
        "priority": "Medium",
        "labels": ["api", "focus-server", "metadata", "validation", "automation", "api_test_panda"],
        "components": ["focus-server", "api"]
    },
    
    "API-015": {
        "summary": "API - GET /metadata/{task_id} - Response Time",
        "description": """h2. Objective
Validate that GET /metadata/{{task_id}} endpoint response time is within acceptable limits (< 500ms).

h2. Test Type
Performance Test

h2. Priority
P2 - Medium

h2. Components/Labels
focus-server, api, metadata, performance, automation

h2. Pre-Conditions
* Focus Server is accessible
* Task is configured and consumer is running

h2. Test Data
* task_id: Valid configured task identifier
* Expected response time: < 500ms

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Configure a task | POST /config/{{task_id}} | Task configured successfully |
| 2 | Wait for consumer to start | Wait 5 seconds | Consumer is running |
| 3 | Measure response time | GET /metadata/{{task_id}} | Response time measured |
| 4 | Verify response time < 500ms | Compare with threshold | Response time is acceptable |

h2. Expected Result
* Response time is < 500ms
* Request completes successfully
* No timeouts occur

h2. Assertions
* Response time < 500ms
* Status code is 201
* Response is received

h2. Post-Conditions
* Task continues running
* System state is consistent

h2. Automation Status
✅ *Automated* with Pytest

*Test Function:* {{code}}test_task_metadata_response_time{{code}}
*Test File:* {{code}}tests/integration/api/test_task_metadata_endpoint.py{{code}}
*Test Class:* {{code}}TestTaskMetadataEndpoint{{code}}
""",
        "priority": "Medium",
        "labels": ["api", "focus-server", "metadata", "performance", "automation", "api_test_panda"],
        "components": ["focus-server", "api"]
    },
}


def create_xray_test(
    client: JiraClient,
    test_id: str,
    test_data: Dict[str, Any],
    dry_run: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Create a test in Xray Test Repository.
    
    Args:
        client: JiraClient instance
        test_id: Test ID (e.g., "API-001")
        test_data: Test data dictionary
        dry_run: If True, only print what would be created
        
    Returns:
        Created test issue dictionary or None if dry_run
    """
    logger.info(f"{'[DRY RUN] ' if dry_run else ''}Creating test: {test_id} - {test_data['summary']}")
    
    if dry_run:
        print(f"\n{'='*80}")
        print(f"Test ID: {test_id}")
        print(f"Summary: {test_data['summary']}")
        print(f"Priority: {test_data['priority']}")
        print(f"Labels: {', '.join(test_data['labels'])}")
        print(f"Components: {', '.join(test_data['components'])}")
        print(f"{'='*80}")
        return None
    
    try:
        # Create test issue
        issue = client.create_issue(
            summary=test_data['summary'],
            description=test_data['description'],
            issue_type="Test",
            priority=test_data['priority'],
            labels=test_data['labels'],
            components=test_data['components'],
            project_key="PZ"
        )
        
        # Set Test Type to "Automation"
        try:
            issue_obj = client.jira.issue(issue['key'])
            issue_obj.update(fields={TEST_TYPE_FIELD_ID: {'value': 'Automation'}})
            logger.info(f"✅ Set Test Type to 'Automation' for {issue['key']}")
        except Exception as e:
            logger.warning(f"⚠️  Could not set Test Type for {issue['key']}: {e}")
        
        logger.info(f"✅ Created test: {issue['key']} - {issue['summary']}")
        logger.info(f"   URL: {issue['url']}")
        
        return issue
        
    except Exception as e:
        logger.error(f"❌ Failed to create test {test_id}: {e}")
        raise


def main():
    """Main function for creating API endpoint tests."""
    parser = argparse.ArgumentParser(
        description='Create API endpoint tests in Jira Xray'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview tests without creating them'
    )
    
    parser.add_argument(
        '--test-id',
        help='Create specific test by ID (e.g., API-001)'
    )
    
    args = parser.parse_args()
    
    try:
        client = JiraClient()
        
        # Determine which tests to create
        if args.test_id:
            if args.test_id not in API_ENDPOINTS_TESTS:
                logger.error(f"❌ Test ID {args.test_id} not found")
                return 1
            tests_to_create = {args.test_id: API_ENDPOINTS_TESTS[args.test_id]}
        else:
            tests_to_create = API_ENDPOINTS_TESTS
        
        logger.info(f"\n{'='*80}")
        logger.info(f"{'[DRY RUN] ' if args.dry_run else ''}Creating {len(tests_to_create)} API Endpoint Tests")
        logger.info(f"{'='*80}\n")
        
        created_tests = []
        failed_tests = []
        
        for test_id, test_data in tests_to_create.items():
            try:
                issue = create_xray_test(
                    client=client,
                    test_id=test_id,
                    test_data=test_data,
                    dry_run=args.dry_run
                )
                
                if issue:
                    created_tests.append(issue)
                    
            except Exception as e:
                logger.error(f"Failed to create {test_id}: {e}")
                failed_tests.append(test_id)
        
        logger.info(f"\n{'='*80}")
        logger.info("SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(f"Total: {len(tests_to_create)}")
        if not args.dry_run:
            logger.info(f"Created: {len(created_tests)}")
            logger.info(f"Failed: {len(failed_tests)}")
            
            if created_tests:
                logger.info("\n✅ Created Tests:")
                for issue in created_tests:
                    logger.info(f"   {issue['key']}: {issue['summary']}")
                    logger.info(f"   URL: {issue['url']}")
        logger.info(f"{'='*80}\n")
        
        if args.dry_run:
            logger.info("⚠️  DRY RUN MODE - No tests created")
            logger.info("   Run without --dry-run to create tests")
        
        return 0 if len(failed_tests) == 0 else 1
        
    except Exception as e:
        logger.error(f"Failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        client.close()


if __name__ == '__main__':
    sys.exit(main())

