"""
Create All Stories with Tasks - Complete Automation Framework
=============================================================

Creates comprehensive Stories with detailed Tasks for all implemented tests.
Groups tests by category and creates Stories with Tasks at mission level.

Author: QA Automation Architect
Date: 2025-11-04
"""

import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Set

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


def find_test_files_for_xray_test(xray_test_key: str, tests_dir: Path) -> List[str]:
    """Find test files with Xray marker for test key."""
    test_files = []
    
    for test_file in tests_dir.rglob('test_*.py'):
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Check for Xray marker - handle both single and multiple test keys
                pattern = rf'@pytest\.mark\.xray\([^)]*["\']?{re.escape(xray_test_key)}["\']?[^)]*\)'
                if re.search(pattern, content):
                    rel_path = str(test_file.relative_to(tests_dir.parent))
                    test_files.append(rel_path)
        except:
            pass
    
    return test_files


def get_epic_link_field():
    """Get Epic Link field ID dynamically."""
    try:
        fields = client.jira.fields()
        for field in fields:
            if field['name'] == 'Epic Link' or field['name'] == 'Epic':
                return field['id']
        # Fallback to common field ID
        return 'customfield_10014'
    except:
        return 'customfield_10014'


def link_story_to_epic(story_key: str, epic_key: str):
    """Link Story to Epic."""
    try:
        epic_link_field = get_epic_link_field()
        issue = client.jira.issue(story_key)
        issue.update(fields={epic_link_field: epic_key})
        return True
    except Exception as e:
        print(f"   ⚠️  Failed to link Story to Epic: {e}")
        return False


# All Stories with Tasks
stories_data = [
    {
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

h2. Related Documentation

* Test Plan: Test plan (TS_Focus_Server_PZ-14024)
* Epic: [PZ-14221|https://prismaphotonics.atlassian.net/browse/PZ-14221]
* Test Repository: https://github.com/PrismaPhotonics/panda-backend-api-tests.git
        """,
        "priority": "High",
        "labels": ["automation", "api", "testing", "backend", "focus-server"],
        "tasks": [
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

* Security Validation:
** Malformed requests handling
** Injection attack prevention
** Input sanitization

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

h2. Test Files

* {{tests/integration/api/test_api_endpoints_high_priority.py}}
* {{tests/integration/api/test_api_endpoints_additional.py}}

h2. Xray Tests Covered

* PZ-13895, PZ-13762, PZ-13560, PZ-13896, PZ-13897, PZ-13898, PZ-13899, PZ-13563, PZ-13554, PZ-13555, PZ-13552

h2. Acceptance Criteria

* All high-priority endpoints tested
* Response validation complete
* Error scenarios covered
* Tests integrated with Xray
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

h2. Test Files

* {{tests/integration/api/test_waterfall_view.py}}
* {{tests/integration/api/test_nfft_overlap_edge_case.py}}

h2. Xray Tests Covered

* PZ-13557, PZ-13558

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
    },
    {
        "summary": "Automation: Focus Server Integration Tests - Historic Playback",
        "description": """
h2. Story Overview

This story covers the development of comprehensive automation testing framework for Focus Server Historic Playback functionality. The framework includes E2E historic playback flows, short duration playback, long duration playback, and edge case scenarios.

h2. Business Value

* Ensures historic playback reliability and correctness
* Validates time-range handling and data retrieval
* Tests various playback durations and configurations
* Validates error handling and edge cases

h2. Technical Scope

* Historic playback E2E flow tests
* Short duration playback tests (1 minute, 5 minutes)
* Long duration playback tests
* Additional historic playback scenarios
* Edge case validation

h2. Test Files Implemented

* {{tests/integration/api/test_historic_playback_e2e.py}} - E2E historic playback tests
* {{tests/integration/api/test_historic_playback_additional.py}} - Additional historic playback tests

h2. Related Documentation

* Test Plan: Test plan (TS_Focus_Server_PZ-14024)
* Epic: [PZ-14221|https://prismaphotonics.atlassian.net/browse/PZ-14221]
* Test Repository: https://github.com/PrismaPhotonics/panda-backend-api-tests.git
        """,
        "priority": "High",
        "labels": ["automation", "integration", "historic-playback", "testing", "backend"],
        "tasks": [
            {
                "summary": "Implement Historic Playback E2E Test Framework",
                "description": """
h2. Task Overview

Develop comprehensive E2E test framework for historic playback functionality. This includes validation of complete historic playback flow, time-range handling, data retrieval, and job lifecycle management.

h2. Technical Requirements

* E2E Flow Validation:
** Complete historic playback flow
** Time-range validation
** Data retrieval validation
** Job lifecycle management
** Status tracking

* Configuration Validation:
** Time-range configuration
** Channel selection
** Frequency range
** View type configuration

h2. Test Files

* {{tests/integration/api/test_historic_playback_e2e.py}}

h2. Xray Tests Covered

* PZ-13872

h2. Acceptance Criteria

* E2E flow tested
* Time-range handling validated
* Job lifecycle validated
* Tests integrated with Xray
                """,
                "priority": "High",
                "labels": ["automation", "integration", "historic-playback", "e2e"]
            },
            {
                "summary": "Implement Historic Playback Additional Scenarios",
                "description": """
h2. Task Overview

Develop additional historic playback test scenarios including short duration playback, long duration playback, edge cases, and various configurations.

h2. Technical Requirements

* Short Duration Playback:
** 1-minute playback tests
** 5-minute playback tests
** Rapid window scenarios
** Data availability validation

* Long Duration Playback:
** Extended time-range tests
** Large data retrieval
** Performance validation
** Resource usage validation

* Edge Cases:
** Boundary time ranges
** Invalid configurations
** Error scenarios
** Recovery scenarios

h2. Test Files

* {{tests/integration/api/test_historic_playback_additional.py}}

h2. Xray Tests Covered

* PZ-14101, PZ-13865, PZ-13871, PZ-13870, PZ-13868, PZ-13867, PZ-13866

h2. Acceptance Criteria

* All playback scenarios tested
* Edge cases covered
* Performance validated
* Tests integrated with Xray
                """,
                "priority": "High",
                "labels": ["automation", "integration", "historic-playback", "scenarios"]
            }
        ]
    },
    {
        "summary": "Automation: Focus Server Integration Tests - Live Monitoring",
        "description": """
h2. Story Overview

This story covers the development of comprehensive automation testing framework for Focus Server Live Monitoring functionality. The framework includes live monitoring flow tests, live streaming stability tests, and metadata validation.

h2. Business Value

* Ensures live monitoring reliability and correctness
* Validates real-time data streaming
* Tests streaming stability and performance
* Validates metadata handling

h2. Technical Scope

* Live monitoring flow tests
* Live streaming stability tests
* Metadata validation
* Performance validation

h2. Test Files Implemented

* {{tests/integration/api/test_live_monitoring_flow.py}} - Live monitoring flow tests
* {{tests/integration/api/test_live_streaming_stability.py}} - Live streaming stability tests

h2. Related Documentation

* Test Plan: Test plan (TS_Focus_Server_PZ-14024)
* Epic: [PZ-14221|https://prismaphotonics.atlassian.net/browse/PZ-14221]
* Test Repository: https://github.com/PrismaPhotonics/panda-backend-api-tests.git
        """,
        "priority": "High",
        "labels": ["automation", "integration", "live-monitoring", "testing", "backend"],
        "tasks": [
            {
                "summary": "Implement Live Monitoring Flow Test Framework",
                "description": """
h2. Task Overview

Develop comprehensive test framework for live monitoring flow. This includes validation of live data streaming, metadata handling, configuration management, and real-time data processing.

h2. Technical Requirements

* Live Monitoring Flow:
** Live data streaming validation
** Metadata handling
** Configuration management
** Real-time data processing
** Status tracking

* Metadata Validation:
** Metadata structure validation
** Metadata field validation
** Metadata updates
** Metadata consistency

h2. Test Files

* {{tests/integration/api/test_live_monitoring_flow.py}}

h2. Xray Tests Covered

* PZ-13786, PZ-13785, PZ-13784

h2. Acceptance Criteria

* Live monitoring flow tested
* Metadata handling validated
* Real-time processing validated
* Tests integrated with Xray
                """,
                "priority": "High",
                "labels": ["automation", "integration", "live-monitoring", "flow"]
            },
            {
                "summary": "Implement Live Streaming Stability Tests",
                "description": """
h2. Task Overview

Develop comprehensive test suite for live streaming stability. This includes validation of streaming continuity, performance under load, error handling, and recovery scenarios.

h2. Technical Requirements

* Streaming Stability:
** Streaming continuity validation
** Performance under load
** Error handling
** Recovery scenarios
** Resource usage validation

* Performance Validation:
** Latency validation
** Throughput validation
** Resource consumption
** Scalability testing

h2. Test Files

* {{tests/integration/api/test_live_streaming_stability.py}}

h2. Xray Tests Covered

* PZ-13800

h2. Acceptance Criteria

* Streaming stability tested
* Performance validated
* Error handling validated
* Tests integrated with Xray
                """,
                "priority": "High",
                "labels": ["automation", "integration", "live-monitoring", "stability"]
            }
        ]
    },
    {
        "summary": "Automation: Focus Server Integration Tests - SingleChannel View",
        "description": """
h2. Story Overview

This story covers the development of comprehensive automation testing framework for Focus Server SingleChannel View functionality. The framework includes single channel view mapping tests, channel selection validation, and view configuration tests.

h2. Business Value

* Ensures single channel view reliability and correctness
* Validates channel mapping and selection
* Tests view configuration and rendering
* Validates edge cases and error handling

h2. Technical Scope

* Single channel view mapping tests
* Channel selection validation
* View configuration tests
* Edge case validation

h2. Test Files Implemented

* {{tests/integration/api/test_singlechannel_view_mapping.py}} - SingleChannel view mapping tests

h2. Related Documentation

* Test Plan: Test plan (TS_Focus_Server_PZ-14024)
* Epic: [PZ-14221|https://prismaphotonics.atlassian.net/browse/PZ-14221]
* Test Repository: https://github.com/PrismaPhotonics/panda-backend-api-tests.git
        """,
        "priority": "High",
        "labels": ["automation", "integration", "singlechannel", "testing", "backend"],
        "tasks": [
            {
                "summary": "Implement SingleChannel View Mapping Test Framework",
                "description": """
h2. Task Overview

Develop comprehensive test framework for single channel view mapping. This includes validation of channel mapping, channel selection, view configuration, and rendering.

h2. Technical Requirements

* Channel Mapping:
** Channel mapping validation
** Channel selection validation
** Channel bounds validation
** Channel status validation

* View Configuration:
** View type configuration
** View parameters validation
** View rendering validation
** Edge cases

h2. Test Files

* {{tests/integration/api/test_singlechannel_view_mapping.py}}

h2. Xray Tests Covered

* PZ-13862, PZ-13861, PZ-13860, PZ-13859, PZ-13858, PZ-13857, PZ-13853, PZ-13834, PZ-13824, PZ-13822, PZ-13820, PZ-13818, PZ-13817, PZ-13816

h2. Acceptance Criteria

* Channel mapping tested
* View configuration validated
* Edge cases covered
* Tests integrated with Xray
                """,
                "priority": "High",
                "labels": ["automation", "integration", "singlechannel", "mapping"]
            }
        ]
    },
    {
        "summary": "Automation: Focus Server Integration Tests - Dynamic ROI Adjustment",
        "description": """
h2. Story Overview

This story covers the development of comprehensive automation testing framework for Focus Server Dynamic ROI Adjustment functionality. The framework includes dynamic ROI adjustment tests, ROI configuration validation, and real-time ROI updates.

h2. Business Value

* Ensures dynamic ROI adjustment reliability and correctness
* Validates ROI configuration and updates
* Tests real-time ROI adjustments
* Validates error handling and edge cases

h2. Technical Scope

* Dynamic ROI adjustment tests
* ROI configuration validation
* Real-time ROI updates
* Edge case validation

h2. Test Files Implemented

* {{tests/integration/api/test_dynamic_roi_adjustment.py}} - Dynamic ROI adjustment tests

h2. Related Documentation

* Test Plan: Test plan (TS_Focus_Server_PZ-14024)
* Epic: [PZ-14221|https://prismaphotonics.atlassian.net/browse/PZ-14221]
* Test Repository: https://github.com/PrismaPhotonics/panda-backend-api-tests.git
        """,
        "priority": "High",
        "labels": ["automation", "integration", "roi", "testing", "backend"],
        "tasks": [
            {
                "summary": "Implement Dynamic ROI Adjustment Test Framework",
                "description": """
h2. Task Overview

Develop comprehensive test framework for dynamic ROI adjustment. This includes validation of ROI configuration, real-time ROI updates, ROI bounds validation, and error handling.

h2. Technical Requirements

* ROI Configuration:
** ROI configuration validation
** ROI bounds validation
** ROI parameter validation
** ROI update validation

* Real-time Updates:
** Real-time ROI adjustments
** Update propagation
** Consistency validation
** Performance validation

h2. Test Files

* {{tests/integration/api/test_dynamic_roi_adjustment.py}}

h2. Xray Tests Covered

* PZ-13799, PZ-13798, PZ-13797, PZ-13796, PZ-13795, PZ-13794, PZ-13793, PZ-13792, PZ-13791, PZ-13790, PZ-13789, PZ-13788, PZ-13787

h2. Acceptance Criteria

* ROI adjustment tested
* Real-time updates validated
* Error handling validated
* Tests integrated with Xray
                """,
                "priority": "High",
                "labels": ["automation", "integration", "roi", "dynamic-adjustment"]
            }
        ]
    },
    {
        "summary": "Automation: Focus Server Data Quality Tests",
        "description": """
h2. Story Overview

This story covers the development of comprehensive automation testing framework for Focus Server Data Quality validation. The framework includes MongoDB schema validation, data quality checks, index validation, and recovery tests.

h2. Business Value

* Ensures data quality and consistency
* Validates MongoDB schema and indexes
* Tests data recovery scenarios
* Validates data integrity

h2. Technical Scope

* MongoDB schema validation tests
* Data quality validation tests
* MongoDB index validation tests
* Data recovery tests
* Recordings classification tests

h2. Test Files Implemented

* {{tests/data_quality/test_mongodb_schema_validation.py}} - MongoDB schema validation
* {{tests/data_quality/test_mongodb_data_quality.py}} - Data quality validation
* {{tests/data_quality/test_mongodb_indexes_and_schema.py}} - Index and schema validation
* {{tests/data_quality/test_mongodb_recovery.py}} - Data recovery tests
* {{tests/data_quality/test_recordings_classification.py}} - Recordings classification tests

h2. Related Documentation

* Test Plan: Test plan (TS_Focus_Server_PZ-14024)
* Epic: [PZ-14221|https://prismaphotonics.atlassian.net/browse/PZ-14221]
* Test Repository: https://github.com/PrismaPhotonics/panda-backend-api-tests.git
        """,
        "priority": "High",
        "labels": ["automation", "data-quality", "mongodb", "testing", "backend"],
        "tasks": [
            {
                "summary": "Implement MongoDB Schema Validation Framework",
                "description": """
h2. Task Overview

Develop comprehensive test framework for MongoDB schema validation. This includes validation of schema structure, field types, required fields, and schema consistency.

h2. Technical Requirements

* Schema Validation:
** Schema structure validation
** Field type validation
** Required field validation
** Schema consistency validation
** Index validation

* Data Quality Checks:
** Data integrity validation
** Data consistency validation
** Data completeness validation
** Data accuracy validation

h2. Test Files

* {{tests/data_quality/test_mongodb_schema_validation.py}}
* {{tests/data_quality/test_mongodb_indexes_and_schema.py}}

h2. Xray Tests Covered

* PZ-13686, PZ-13683, PZ-13598, PZ-13810, PZ-13809, PZ-13808, PZ-13807, PZ-13806

h2. Acceptance Criteria

* Schema validation tested
* Data quality validated
* Index validation complete
* Tests integrated with Xray
                """,
                "priority": "High",
                "labels": ["automation", "data-quality", "mongodb", "schema"]
            },
            {
                "summary": "Implement Data Quality Validation Framework",
                "description": """
h2. Task Overview

Develop comprehensive test framework for data quality validation. This includes validation of data completeness, data accuracy, data consistency, and data integrity.

h2. Technical Requirements

* Data Completeness:
** Required data validation
** Missing data detection
** Data completeness metrics
** Data coverage validation

* Data Accuracy:
** Data accuracy validation
** Data correctness checks
** Data validation rules
** Data quality metrics

h2. Test Files

* {{tests/data_quality/test_mongodb_data_quality.py}}

h2. Xray Tests Covered

* PZ-13683 (additional coverage)

h2. Acceptance Criteria

* Data quality validated
* Data completeness checked
* Data accuracy validated
* Tests integrated with Xray
                """,
                "priority": "High",
                "labels": ["automation", "data-quality", "validation"]
            },
            {
                "summary": "Implement MongoDB Recovery Tests",
                "description": """
h2. Task Overview

Develop comprehensive test framework for MongoDB recovery scenarios. This includes validation of data recovery, recovery procedures, and recovery validation.

h2. Technical Requirements

* Recovery Scenarios:
** Data recovery validation
** Recovery procedure validation
** Recovery validation
** Recovery performance

h2. Test Files

* {{tests/data_quality/test_mongodb_recovery.py}}

h2. Xray Tests Covered

* PZ-13687

h2. Acceptance Criteria

* Recovery scenarios tested
* Recovery procedures validated
* Recovery performance validated
* Tests integrated with Xray
                """,
                "priority": "Medium",
                "labels": ["automation", "data-quality", "mongodb", "recovery"]
            },
            {
                "summary": "Implement Recordings Classification Tests",
                "description": """
h2. Task Overview

Develop comprehensive test framework for recordings classification. This includes validation of classification logic, classification accuracy, and classification performance.

h2. Technical Requirements

* Classification Logic:
** Classification algorithm validation
** Classification accuracy validation
** Classification performance validation
** Edge cases

h2. Test Files

* {{tests/data_quality/test_recordings_classification.py}}

h2. Xray Tests Covered

* PZ-13705

h2. Acceptance Criteria

* Classification logic tested
* Classification accuracy validated
* Performance validated
* Tests integrated with Xray
                """,
                "priority": "Medium",
                "labels": ["automation", "data-quality", "classification"]
            }
        ]
    },
    {
        "summary": "Automation: Focus Server Performance and Load Tests",
        "description": """
h2. Story Overview

This story covers the development of comprehensive automation testing framework for Focus Server Performance and Load Testing. The framework includes latency requirements tests, job capacity limits tests, MongoDB outage resilience tests, and performance validation.

h2. Business Value

* Ensures system performance under load
* Validates latency requirements
* Tests system capacity limits
* Validates outage resilience

h2. Technical Scope

* Latency requirements tests
* Job capacity limits tests
* MongoDB outage resilience tests
* Performance validation tests

h2. Test Files Implemented

* {{tests/integration/performance/test_latency_requirements.py}} - Latency requirements tests
* {{tests/load/test_job_capacity_limits.py}} - Job capacity limits tests
* {{tests/performance/test_mongodb_outage_resilience.py}} - MongoDB outage resilience tests
* {{tests/integration/performance/test_performance_high_priority.py}} - High-priority performance tests

h2. Related Documentation

* Test Plan: Test plan (TS_Focus_Server_PZ-14024)
* Epic: [PZ-14221|https://prismaphotonics.atlassian.net/browse/PZ-14221]
* Test Repository: https://github.com/PrismaPhotonics/panda-backend-api-tests.git
        """,
        "priority": "High",
        "labels": ["automation", "performance", "load-testing", "testing", "backend"],
        "tasks": [
            {
                "summary": "Implement Latency Requirements Test Framework",
                "description": """
h2. Task Overview

Develop comprehensive test framework for latency requirements validation. This includes validation of P95 latency, response time SLA, and performance under various load conditions.

h2. Technical Requirements

* Latency Validation:
** P95 latency validation
** Response time SLA validation
** Latency under load
** Performance metrics

* Load Testing:
** Various load scenarios
** Performance under load
** Resource usage validation
** Scalability testing

h2. Test Files

* {{tests/integration/performance/test_latency_requirements.py}}

h2. Xray Tests Covered

* PZ-14092, PZ-14091, PZ-14090

h2. Acceptance Criteria

* Latency requirements validated
* Performance under load tested
* SLA validation complete
* Tests integrated with Xray
                """,
                "priority": "High",
                "labels": ["automation", "performance", "latency"]
            },
            {
                "summary": "Implement Job Capacity Limits Test Framework",
                "description": """
h2. Task Overview

Develop comprehensive test framework for job capacity limits validation. This includes validation of maximum concurrent jobs, resource allocation, and capacity management.

h2. Technical Requirements

* Capacity Limits:
** Maximum concurrent jobs validation
** Resource allocation validation
** Capacity management validation
** Resource exhaustion scenarios

* Load Testing:
** High concurrency scenarios
** Resource usage validation
** Performance under load
** Scalability testing

h2. Test Files

* {{tests/load/test_job_capacity_limits.py}}

h2. Xray Tests Covered

* PZ-14088

h2. Acceptance Criteria

* Capacity limits validated
* High concurrency tested
* Resource management validated
* Tests integrated with Xray
                """,
                "priority": "High",
                "labels": ["automation", "performance", "load-testing", "capacity"]
            },
            {
                "summary": "Implement MongoDB Outage Resilience Tests",
                "description": """
h2. Task Overview

Develop comprehensive test framework for MongoDB outage resilience validation. This includes validation of outage handling, recovery procedures, and system resilience.

h2. Technical Requirements

* Outage Handling:
** MongoDB outage detection
** Outage handling validation
** Recovery procedure validation
** System resilience validation

* Recovery Scenarios:
** Recovery time validation
** Data consistency validation
** Service continuity validation
** Error handling validation

h2. Test Files

* {{tests/performance/test_mongodb_outage_resilience.py}}

h2. Xray Tests Covered

* PZ-13640 (outage resilience)

h2. Acceptance Criteria

* Outage handling validated
* Recovery procedures tested
* System resilience validated
* Tests integrated with Xray
                """,
                "priority": "High",
                "labels": ["automation", "performance", "mongodb", "outage-resilience"]
            }
        ]
    },
    {
        "summary": "Automation: Focus Server Infrastructure Tests",
        "description": """
h2. Story Overview

This story covers the development of comprehensive automation testing framework for Focus Server Infrastructure validation. The framework includes connectivity tests, system behavior tests, K8s integration tests, and RabbitMQ connectivity tests.

h2. Business Value

* Ensures infrastructure reliability and correctness
* Validates connectivity and system behavior
* Tests K8s integration and resource management
* Validates external service connectivity

h2. Technical Scope

* Basic connectivity tests
* External connectivity tests
* System behavior tests
* K8s job lifecycle tests
* RabbitMQ connectivity tests
* PZ integration tests

h2. Test Files Implemented

* {{tests/infrastructure/test_basic_connectivity.py}} - Basic connectivity tests
* {{tests/infrastructure/test_external_connectivity.py}} - External connectivity tests
* {{tests/infrastructure/test_system_behavior.py}} - System behavior tests
* {{tests/infrastructure/test_k8s_job_lifecycle.py}} - K8s job lifecycle tests
* {{tests/infrastructure/test_rabbitmq_connectivity.py}} - RabbitMQ connectivity tests
* {{tests/infrastructure/test_pz_integration.py}} - PZ integration tests

h2. Related Documentation

* Test Plan: Test plan (TS_Focus_Server_PZ-14024)
* Epic: [PZ-14221|https://prismaphotonics.atlassian.net/browse/PZ-14221]
* Test Repository: https://github.com/PrismaPhotonics/panda-backend-api-tests.git
        """,
        "priority": "High",
        "labels": ["automation", "infrastructure", "testing", "backend"],
        "tasks": [
            {
                "summary": "Implement Infrastructure Connectivity Test Framework",
                "description": """
h2. Task Overview

Develop comprehensive test framework for infrastructure connectivity validation. This includes validation of basic connectivity, external connectivity, and service availability.

h2. Technical Requirements

* Basic Connectivity:
** Basic connectivity validation
** Service availability validation
** Network connectivity validation
** Port accessibility validation

* External Connectivity:
** External service connectivity
** Service integration validation
** API connectivity validation
** Error handling validation

h2. Test Files

* {{tests/infrastructure/test_basic_connectivity.py}}
* {{tests/infrastructure/test_external_connectivity.py}}

h2. Xray Tests Covered

* PZ-13900, PZ-13899, PZ-13898

h2. Acceptance Criteria

* Connectivity validated
* Service availability tested
* External connectivity validated
* Tests integrated with Xray
                """,
                "priority": "High",
                "labels": ["automation", "infrastructure", "connectivity"]
            },
            {
                "summary": "Implement System Behavior Test Framework",
                "description": """
h2. Task Overview

Develop comprehensive test framework for system behavior validation. This includes validation of system startup, system stability, error handling, and resource management.

h2. Technical Requirements

* System Startup:
** Clean startup validation
** Startup sequence validation
** Resource initialization validation
** Service initialization validation

* System Stability:
** System stability validation
** Predictable error handling
** Resource management validation
** Error recovery validation

h2. Test Files

* {{tests/infrastructure/test_system_behavior.py}}

h2. Xray Tests Covered

* PZ-13602 (system behavior)

h2. Acceptance Criteria

* System behavior validated
* Startup sequence tested
* Stability validated
* Tests integrated with Xray
                """,
                "priority": "High",
                "labels": ["automation", "infrastructure", "system-behavior"]
            },
            {
                "summary": "Implement K8s Job Lifecycle Test Framework",
                "description": """
h2. Task Overview

Develop comprehensive test framework for K8s job lifecycle validation. This includes validation of job creation, job lifecycle management, resource allocation, and cleanup procedures.

h2. Technical Requirements

* Job Lifecycle:
** Job creation validation
** Job status tracking
** Job completion validation
** Job cleanup validation

* Resource Management:
** Resource allocation validation
** Resource cleanup validation
** Resource limits validation
** Resource monitoring

h2. Test Files

* {{tests/infrastructure/test_k8s_job_lifecycle.py}}

h2. Xray Tests Covered

* PZ-14019, PZ-14018 (K8s orchestration)

h2. Acceptance Criteria

* Job lifecycle validated
* Resource management tested
* Cleanup procedures validated
* Tests integrated with Xray
                """,
                "priority": "High",
                "labels": ["automation", "infrastructure", "kubernetes", "job-lifecycle"]
            },
            {
                "summary": "Implement RabbitMQ Connectivity Test Framework",
                "description": """
h2. Task Overview

Develop comprehensive test framework for RabbitMQ connectivity validation. This includes validation of RabbitMQ connection, message queue handling, and integration validation.

h2. Technical Requirements

* RabbitMQ Connectivity:
** Connection validation
** Queue creation validation
** Message handling validation
** Integration validation

* Message Queue:
** Message queue validation
** Message processing validation
** Error handling validation
** Performance validation

h2. Test Files

* {{tests/infrastructure/test_rabbitmq_connectivity.py}}

h2. Xray Tests Covered

* PZ-13602 (RabbitMQ connectivity)

h2. Acceptance Criteria

* RabbitMQ connectivity validated
* Message queue tested
* Integration validated
* Tests integrated with Xray
                """,
                "priority": "High",
                "labels": ["automation", "infrastructure", "rabbitmq", "connectivity"]
            }
        ]
    },
    {
        "summary": "Automation: Focus Server Integration Tests - Calculations and E2E",
        "description": """
h2. Story Overview

This story covers the development of comprehensive automation testing framework for Focus Server Calculations and E2E flows. The framework includes system calculations tests, gRPC metadata flow tests, and E2E integration scenarios.

h2. Business Value

* Ensures calculations accuracy and correctness
* Validates E2E flows and integration
* Tests gRPC metadata handling
* Validates system calculations

h2. Technical Scope

* System calculations tests
* gRPC metadata flow tests
* E2E integration tests

h2. Test Files Implemented

* {{tests/integration/calculations/test_system_calculations.py}} - System calculations tests
* {{tests/integration/e2e/test_configure_metadata_grpc_flow.py}} - gRPC metadata flow tests

h2. Related Documentation

* Test Plan: Test plan (TS_Focus_Server_PZ-14024)
* Epic: [PZ-14221|https://prismaphotonics.atlassian.net/browse/PZ-14221]
* Test Repository: https://github.com/PrismaPhotonics/panda-backend-api-tests.git
        """,
        "priority": "High",
        "labels": ["automation", "integration", "calculations", "e2e", "testing"],
        "tasks": [
            {
                "summary": "Implement System Calculations Test Framework",
                "description": """
h2. Task Overview

Develop comprehensive test framework for system calculations validation. This includes validation of calculation algorithms, calculation accuracy, and calculation performance.

h2. Technical Requirements

* Calculation Algorithms:
** Algorithm validation
** Calculation accuracy validation
** Calculation performance validation
** Edge cases

* Calculation Scenarios:
** Various calculation scenarios
** Boundary value testing
** Error handling validation
** Performance validation

h2. Test Files

* {{tests/integration/calculations/test_system_calculations.py}}

h2. Xray Tests Covered

* PZ-14080, PZ-14079, PZ-14078, PZ-14073, PZ-14072, PZ-14071, PZ-14070, PZ-14069, PZ-14068, PZ-14067, PZ-14066, PZ-14062, PZ-14061, PZ-14060

h2. Acceptance Criteria

* Calculations validated
* Algorithm accuracy tested
* Performance validated
* Tests integrated with Xray
                """,
                "priority": "High",
                "labels": ["automation", "integration", "calculations"]
            },
            {
                "summary": "Implement gRPC Metadata Flow E2E Test Framework",
                "description": """
h2. Task Overview

Develop comprehensive E2E test framework for gRPC metadata flow. This includes validation of metadata configuration, metadata flow, and gRPC integration.

h2. Technical Requirements

* gRPC Metadata Flow:
** Metadata configuration validation
** Metadata flow validation
** gRPC integration validation
** Metadata handling validation

* E2E Integration:
** Complete flow validation
** Integration validation
** Error handling validation
** Performance validation

h2. Test Files

* {{tests/integration/e2e/test_configure_metadata_grpc_flow.py}}

h2. Xray Tests Covered

* PZ-13570

h2. Acceptance Criteria

* gRPC metadata flow tested
* E2E integration validated
* Metadata handling validated
* Tests integrated with Xray
                """,
                "priority": "High",
                "labels": ["automation", "integration", "e2e", "grpc"]
            }
        ]
    },
    {
        "summary": "Automation: Focus Server Stress and Edge Case Tests",
        "description": """
h2. Story Overview

This story covers the development of comprehensive automation testing framework for Focus Server Stress and Edge Case testing. The framework includes extreme configurations tests and stress testing scenarios.

h2. Business Value

* Ensures system stability under extreme conditions
* Validates edge cases and boundary conditions
* Tests system limits and constraints
* Validates error handling under stress

h2. Technical Scope

* Extreme configurations tests
* Stress testing scenarios
* Edge case validation

h2. Test Files Implemented

* {{tests/stress/test_extreme_configurations.py}} - Extreme configurations tests

h2. Related Documentation

* Test Plan: Test plan (TS_Focus_Server_PZ-14024)
* Epic: [PZ-14221|https://prismaphotonics.atlassian.net/browse/PZ-14221]
* Test Repository: https://github.com/PrismaPhotonics/panda-backend-api-tests.git
        """,
        "priority": "Medium",
        "labels": ["automation", "stress", "edge-cases", "testing"],
        "tasks": [
            {
                "summary": "Implement Extreme Configurations Test Framework",
                "description": """
h2. Task Overview

Develop comprehensive test framework for extreme configurations validation. This includes validation of boundary conditions, extreme values, and system limits.

h2. Technical Requirements

* Extreme Configurations:
** Boundary value testing
** Extreme value testing
** System limits validation
** Error handling validation

* Stress Testing:
** High load scenarios
** Resource exhaustion scenarios
** Performance under stress
** System stability validation

h2. Test Files

* {{tests/stress/test_extreme_configurations.py}}

h2. Xray Tests Covered

* PZ-13880

h2. Acceptance Criteria

* Extreme configurations tested
* Boundary conditions validated
* Stress scenarios tested
* Tests integrated with Xray
                """,
                "priority": "Medium",
                "labels": ["automation", "stress", "extreme-configurations"]
            }
        ]
    }
]


def main():
    """Main execution."""
    print("=" * 100)
    print("CREATING ALL STORIES WITH TASKS - COMPLETE AUTOMATION FRAMEWORK")
    print("=" * 100)
    print()
    
    created_stories = []
    
    for story_idx, story_data in enumerate(stories_data, 1):
        print(f"{'='*100}")
        print(f"Story {story_idx}/{len(stories_data)}: {story_data['summary']}")
        print(f"{'='*100}\n")
        
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
            print(f"   URL: {story['url']}\n")
            
            # Link Story to Epic
            if link_story_to_epic(story_key, EPIC_KEY):
                print(f"✅ Linked Story to Epic: {EPIC_KEY}\n")
            
            # Create Tasks
            created_tasks = []
            tasks = story_data.get("tasks", [])
            
            if tasks:
                print(f"Creating {len(tasks)} Tasks...\n")
                
                for task_idx, task_data in enumerate(tasks, 1):
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
                        print(f"✅ Task {task_idx}/{len(tasks)}: {task['key']} - {task['summary']}")
                        print(f"   URL: {task['url']}\n")
                        
                    except Exception as e:
                        print(f"❌ Failed to create Task {task_idx}: {e}")
                        print(f"   Task: {task_data['summary']}\n")
            
            created_stories.append({
                "story": story,
                "tasks": created_tasks
            })
            
            print()
            
        except Exception as e:
            print(f"❌ Failed to create Story {story_idx}: {e}")
            print(f"   Story: {story_data['summary']}\n")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print(f"\nTotal Stories Created: {len(created_stories)}/{len(stories_data)}")
    
    total_tasks = sum(len(s["tasks"]) for s in created_stories)
    expected_tasks = sum(len(s.get("tasks", [])) for s in stories_data)
    print(f"Total Tasks Created: {total_tasks}/{expected_tasks}\n")
    
    print("Created Stories:")
    for i, story_info in enumerate(created_stories, 1):
        story = story_info["story"]
        tasks = story_info["tasks"]
        print(f"\n{i}. {story['key']}: {story['summary']}")
        print(f"   URL: {story['url']}")
        print(f"   Tasks: {len(tasks)}")
        for task in tasks:
            print(f"      - {task['key']}: {task['summary']}")
    
    print("\n✅ Done!")


if __name__ == '__main__':
    main()


