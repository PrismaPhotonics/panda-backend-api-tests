"""
Create API Story with Tasks - Example
=====================================

Creates a single Story with detailed Tasks for API Endpoints automation.
This is an example to demonstrate the approach before creating all stories.

Author: QA Automation Architect
Date: 2025-11-04
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraAgent, JiraClient

# Configure UTF-8 for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

# Initialize agent
agent = JiraAgent()
client = JiraClient()

# Epic key
EPIC_KEY = "PZ-14221"
EPIC_LINK_FIELD = "customfield_10014"  # Epic Link field

print("=" * 100)
print("CREATING API STORY WITH TASKS - EXAMPLE")
print("=" * 100)
print()

# Story details
story_data = {
    "summary": "Automation: Focus Server API Endpoints Testing Framework",
    "description": """
h2. Story Overview

This story covers the development of comprehensive automation testing framework for Focus Server API endpoints. The framework includes pre-launch validations, health checks, endpoint coverage, orchestration validation, and additional API scenarios.

h2. Business Value

* Ensures API reliability and correctness
* Enables continuous integration and deployment
* Provides comprehensive test coverage for API endpoints
* Validates error handling and edge cases
* Supports regression testing

h2. Technical Scope

* Pre-launch validation tests (port, data, time-range, config)
* Health check endpoint tests (GET /ack)
* High-priority endpoint tests (GET /channels, etc.)
* Additional endpoint coverage tests
* Orchestration validation tests (K8s integration)

h2. Test Files Implemented

* {{tests/integration/api/test_prelaunch_validations.py}} - Pre-launch validation tests
* {{tests/integration/api/test_health_check.py}} - Health check endpoint tests
* {{tests/integration/api/test_api_endpoints_high_priority.py}} - High-priority endpoint tests
* {{tests/integration/api/test_api_endpoints_additional.py}} - Additional endpoint tests
* {{tests/integration/api/test_orchestration_validation.py}} - Orchestration validation tests
* {{tests/integration/api/test_config_validation_high_priority.py}} - Config validation tests
* {{tests/integration/api/test_config_validation_nfft_frequency.py}} - NFFT frequency validation tests
* {{tests/integration/api/test_view_type_validation.py}} - View type validation tests
* {{tests/integration/api/test_waterfall_view.py}} - Waterfall view tests
* {{tests/integration/api/test_nfft_overlap_edge_case.py}} - NFFT overlap edge cases

h2. Acceptance Criteria

* All API endpoint tests implemented and passing
* Test framework follows best practices (Page Object, DRY, SOLID)
* Comprehensive error handling and logging
* Tests integrated with Xray
* All tests documented with clear descriptions

h2. Related Documentation

* Test Plan: Test plan (TS_Focus_Server_PZ-14024)
* Epic: [PZ-14221|https://prismaphotonics.atlassian.net/browse/PZ-14221]
* Test Repository: https://github.com/PrismaPhotonics/panda-backend-api-tests.git
    """,
    "priority": "High",
    "labels": ["automation", "api", "testing", "backend", "focus-server"],
    "issue_type": "Story"
}

# Tasks details
tasks_data = [
    {
        "summary": "Implement API Pre-launch Validation Framework",
        "description": """
h2. Task Overview

Develop comprehensive test framework for Focus Server API pre-launch validations. This includes validation of port availability, data availability (Live/Historic modes), time-range validation, and configuration validation (channels, frequency, NFFT, view type).

h2. Technical Requirements

* Port Availability Validation:
** Verify port availability checks before job creation
** Test port conflict scenarios
** Validate error messages for port conflicts

* Data Availability Validation:
** Live mode data availability checks
** Historic mode data availability checks
** Time-range validation (future timestamps, reversed ranges)
** Data existence validation

* Configuration Validation:
** Channel range validation (min/max bounds)
** Frequency range validation (Nyquist limit)
** NFFT selection validation
** View type validation (MULTICHANNEL, SINGLECHANNEL, WATERFALL)

* Error Handling:
** Predictable error messages
** Clear error codes
** Proper HTTP status codes

h2. Test Files

* {{tests/integration/api/test_prelaunch_validations.py}}
* {{tests/integration/api/test_config_validation_high_priority.py}}
* {{tests/integration/api/test_config_validation_nfft_frequency.py}}
* {{tests/integration/api/test_view_type_validation.py}}

h2. Xray Tests Covered

* PZ-14089, PZ-14098, PZ-14099, PZ-13909, PZ-13907, PZ-13879, PZ-13878, PZ-13876, PZ-13869, PZ-13547

h2. Acceptance Criteria

* All pre-launch validation scenarios tested
* Error handling validated
* Test framework follows best practices
* Tests integrated with Xray
        """,
        "priority": "High",
        "labels": ["automation", "api", "validation", "pre-launch"]
    },
    {
        "summary": "Implement API Health Check Test Suite",
        "description": """
h2. Task Overview

Develop comprehensive test suite for Focus Server health check endpoint (GET /ack). This includes validation of valid responses, invalid HTTP methods, concurrent requests, various headers, security validation, response structure, SSL/TLS support, and load testing scenarios.

h2. Technical Requirements

* Valid Response Tests:
** Status code validation (200 OK)
** Response time SLA validation (100ms, 200ms, 1000ms)
** JSON response structure validation
** Response content validation

* Invalid HTTP Methods:
** POST, PUT, DELETE, PATCH rejection
** Proper error codes (405 Method Not Allowed)

* Concurrent Requests:
** Multiple simultaneous requests
** Thread safety validation
** Response consistency

* Header Validation:
** Various request headers
** Custom headers handling
** CORS headers (if applicable)

* Security Validation:
** Malformed requests handling
** Injection attack prevention
** Input sanitization

* SSL/TLS Support:
** HTTPS connection validation
** Certificate validation
** SSL/TLS version support

* Load Testing:
** High concurrency scenarios
** Response time under load
** Resource usage validation

h2. Test Files

* {{tests/integration/api/test_health_check.py}}

h2. Xray Tests Covered

* PZ-14026, PZ-14027, PZ-14028, PZ-14029, PZ-14030, PZ-14031, PZ-14032, PZ-14033

h2. Acceptance Criteria

* All health check scenarios tested
* Load testing validated
* Security scenarios covered
* Tests integrated with Xray
        """,
        "priority": "High",
        "labels": ["automation", "api", "health-check", "load-testing"]
    },
    {
        "summary": "Implement API Endpoint High Priority Tests",
        "description": """
h2. Task Overview

Develop high-priority API endpoint tests including GET /channels endpoint validation, channel list retrieval, system channel bounds verification, and additional critical endpoint tests.

h2. Technical Requirements

* GET /channels Endpoint:
** Enabled channels list retrieval
** Channel object structure validation
** System channel bounds (min/max)
** Channel status validation
** Response format validation

* Additional Endpoints:
** Endpoint availability tests
** Response structure validation
** Error handling for invalid requests
** Edge case scenarios

* Integration Scenarios:
** Endpoint interaction tests
** Multi-endpoint workflows
** Error propagation validation

h2. Test Files

* {{tests/integration/api/test_api_endpoints_high_priority.py}}
* {{tests/integration/api/test_api_endpoints_additional.py}}

h2. Xray Tests Covered

* PZ-13895, PZ-13762, PZ-13560, PZ-13896, PZ-13897, PZ-13898, PZ-13899, PZ-13563, PZ-13554, PZ-13555, PZ-13552

h2. Acceptance Criteria

* All high-priority endpoints tested
** Response validation complete
** Error scenarios covered
** Tests integrated with Xray
        """,
        "priority": "High",
        "labels": ["automation", "api", "endpoints", "high-priority"]
    },
    {
        "summary": "Implement API Orchestration Validation Tests",
        "description": """
h2. Task Overview

Develop orchestration validation tests for Kubernetes job lifecycle, resource allocation, port exposure, and observability. This includes validation of K8s integration, job creation, job lifecycle management, and resource cleanup.

h2. Technical Requirements

* Kubernetes Job Lifecycle:
** Job creation validation
** Job status tracking
** Job completion validation
** Job cleanup validation
** Resource allocation validation

* Port Exposure:
** Port allocation validation
** Port conflict handling
** Port cleanup validation
** Service exposure validation

* Resource Management:
** Resource allocation limits
** Resource cleanup on failure
** Resource cleanup on success
** Resource monitoring

* Observability:
** Log collection validation
** Metrics collection validation
** Trace collection validation
** Error reporting

h2. Test Files

* {{tests/integration/api/test_orchestration_validation.py}}
* {{tests/infrastructure/test_k8s_job_lifecycle.py}}

h2. Xray Tests Covered

* PZ-14019, PZ-14018

h2. Acceptance Criteria

* All orchestration scenarios tested
* K8s integration validated
* Resource management validated
* Tests integrated with Xray
        """,
        "priority": "High",
        "labels": ["automation", "api", "orchestration", "kubernetes"]
    },
    {
        "summary": "Implement API Additional Coverage Tests",
        "description": """
h2. Task Overview

Develop additional API endpoint tests for extended coverage including edge cases, error scenarios, waterfall view tests, NFFT overlap edge cases, and additional API validations.

h2. Technical Requirements

* Waterfall View Tests:
** Waterfall view configuration
** Waterfall view data retrieval
** Waterfall view validation
** Edge cases

* NFFT Overlap Edge Cases:
** NFFT overlap calculations
** Edge case scenarios
** Boundary value testing
** Error handling

* Additional Endpoint Validations:
** Extended endpoint coverage
** Error scenario testing
** Edge case validation
** Integration scenarios

h2. Test Files

* {{tests/integration/api/test_waterfall_view.py}}
* {{tests/integration/api/test_nfft_overlap_edge_case.py}}
* {{tests/integration/api/test_api_endpoints_additional.py}}

h2. Xray Tests Covered

* PZ-13557, PZ-13558, PZ-13554, PZ-13555, PZ-13552, PZ-13563

h2. Acceptance Criteria

* All additional scenarios tested
* Edge cases covered
* Error scenarios validated
* Tests integrated with Xray
        """,
        "priority": "Medium",
        "labels": ["automation", "api", "additional-coverage", "edge-cases"]
    }
]

print("Creating Story...")
print()

try:
    # Create Story
    story = agent.create_story(
        summary=story_data["summary"],
        description=story_data["description"],
        priority=story_data["priority"],
        labels=story_data["labels"]
    )
    
    story_key = story["key"]
    print(f"✅ Created Story: {story_key}")
    print(f"   URL: {story['url']}")
    print()
    
    # Link Story to Epic
    try:
        # Get Epic Link field ID dynamically
        fields = client.jira.fields()
        epic_link_field = None
        for field in fields:
            if field['name'] == 'Epic Link' or field['name'] == 'Epic':
                epic_link_field = field['id']
                break
        
        if not epic_link_field:
            # Try common field IDs
            epic_link_field = EPIC_LINK_FIELD
        
        # Update story with Epic Link using fields parameter
        issue = client.jira.issue(story_key)
        issue.update(fields={epic_link_field: EPIC_KEY})
        print(f"✅ Linked Story to Epic: {EPIC_KEY}")
    except Exception as e:
        print(f"⚠️  Failed to link Story to Epic: {e}")
        print(f"   Please link manually: {story['url']}")
    
    print()
    print("Creating Tasks...")
    print()
    
    # Create Tasks
    created_tasks = []
    for i, task_data in enumerate(tasks_data, 1):
        try:
            task = client.create_issue(
                summary=task_data["summary"],
                description=task_data["description"],
                issue_type="Sub-task",
                priority=task_data["priority"],
                labels=task_data["labels"],
                parent_key=story_key
            )
            
            created_tasks.append(task)
            print(f"✅ Task {i}/{len(tasks_data)}: {task['key']} - {task['summary']}")
            print(f"   URL: {task['url']}")
            
        except Exception as e:
            print(f"❌ Failed to create Task {i}: {e}")
            print(f"   Task: {task_data['summary']}")
    
    print()
    print("=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print(f"Story: {story_key} - {story_data['summary']}")
    print(f"Tasks created: {len(created_tasks)}/{len(tasks_data)}")
    print()
    print("Story URL:", story['url'])
    print()
    print("Task URLs:")
    for task in created_tasks:
        print(f"  - {task['key']}: {task['url']}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("✅ Done!")

