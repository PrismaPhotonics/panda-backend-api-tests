#!/usr/bin/env python3
"""
Create Live & Historic Job Tests in Jira Xray
==============================================

Creates Test Cases for Live and Historic Job Load Tests.

Tests Created:
- 7 Live Job Tests (PZ-LOAD-200 to PZ-LOAD-220)
- 9 Historic Job Tests (PZ-LOAD-300 to PZ-LOAD-331)
- 7 Live Job Load Tests (PZ-LOAD-100 to PZ-LOAD-120)
- 7 Quick Load Metrics Tests (PZ-LOAD-000 to PZ-LOAD-011)

Total: 30 Test Cases

Usage:
    python scripts/jira/create_live_historic_job_tests.py
    python scripts/jira/create_live_historic_job_tests.py --dry-run
    python scripts/jira/create_live_historic_job_tests.py --category live
    python scripts/jira/create_live_historic_job_tests.py --category historic

Author: QA Automation Architect
Date: 2025-11-30
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
# LIVE JOB TESTS (test_live_load.py)
# =============================================================================

LIVE_JOB_TESTS = {
    "LOAD-200": {
        "summary": "Load - Live - Single Live Job Complete Flow",
        "description": """h2. Objective
Verify that a single Live streaming job completes successfully through all phases.

h2. Pre-Conditions
* Focus Server API is running and accessible
* gRPC services are available
* DAS fiber is streaming data

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Send POST /configure request | Live job config (no start_time/end_time) | Job created successfully |
| 2 | Wait for gRPC pod to become ready | Retry up to 5 times | Pod becomes ready |
| 3 | Connect to gRPC stream | Using stream_url and stream_port | Connection established |
| 4 | Receive spectrogram frames | At least 5 frames | Frames received |
| 5 | Disconnect from gRPC | Close connection | Disconnected cleanly |

h2. Expected Result
Single Live job completes all phases: Configure → Wait → Connect → Stream → Disconnect

h2. Assertions
* Job creation returns 200 OK
* gRPC connection established within timeout
* At least 1 frame received
* No errors during disconnection

h2. Automation Status
✅ Automated

*Test Function:* `test_single_live_job`
*Test File:* `be_focus_server_tests/load/test_live_load.py`
*Test Class:* `TestLiveJobLoad`
*Xray Marker:* `PZ-LOAD-200`
""",
        "priority": "High",
        "labels": ["load", "live", "job", "grpc", "automation", "job_load"],
        "components": ["focus-server", "grpc"]
    },
    "LOAD-201": {
        "summary": "Load - Live - Job Timing Meets SLA",
        "description": """h2. Objective
Verify that Live job timing meets SLA requirements for the environment.

h2. Pre-Conditions
* Focus Server API is running
* SLA thresholds configured per environment

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Run 5 Live jobs | 2 concurrent | Jobs complete |
| 2 | Measure configure phase timing | P95 threshold | Within SLA |
| 3 | Measure gRPC connect timing | P95 threshold | Within SLA |
| 4 | Measure total job timing | P95/P99 threshold | Within SLA |

h2. Expected Result
All timing metrics meet SLA:
* Staging: P95 < 45s, P99 < 90s
* Production: P95 < 20s, P99 < 45s

h2. Automation Status
✅ Automated

*Test Function:* `test_live_job_timing`
*Test File:* `be_focus_server_tests/load/test_live_load.py`
*Test Class:* `TestLiveJobLoad`
*Xray Marker:* `PZ-LOAD-201`
""",
        "priority": "High",
        "labels": ["load", "live", "sla", "timing", "automation", "job_load"],
        "components": ["focus-server", "grpc"]
    },
    "LOAD-202": {
        "summary": "Load - Live - Multiple Concurrent Jobs",
        "description": """h2. Objective
Verify that system handles multiple concurrent Live jobs efficiently.

h2. Pre-Conditions
* Focus Server can handle concurrent jobs
* Sufficient resources available

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Create 6 Live jobs | 3 concurrent at a time | Jobs created |
| 2 | Monitor job success rate | Track failures | Success rate measured |
| 3 | Verify all gRPC connections | Check connection status | All connected |
| 4 | Verify frame reception | Check frames received | Frames received |

h2. Expected Result
Success rate >= 80% (staging) or >= 95% (production) for concurrent jobs.

h2. Automation Status
✅ Automated

*Test Function:* `test_concurrent_live_jobs`
*Test File:* `be_focus_server_tests/load/test_live_load.py`
*Test Class:* `TestLiveJobLoad`
*Xray Marker:* `PZ-LOAD-202`
""",
        "priority": "High",
        "labels": ["load", "live", "concurrent", "automation", "job_load"],
        "components": ["focus-server", "grpc"]
    },
    "LOAD-203": {
        "summary": "Load - Live - Retry Behavior (gRPC Connection)",
        "description": """h2. Objective
Verify that Live jobs handle gRPC connection delays with proper retry behavior.

h2. Background
Based on Yonatan's feedback: "There might be a slight delay between step 4 and 5, 
it might be necessary to try more than once" - referring to the delay between 
pod creation and gRPC server readiness.

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Create Live jobs | With retry mechanism | Jobs created |
| 2 | Monitor gRPC connection attempts | Track retries | Retries recorded |
| 3 | Verify retry logic works | Check success after retries | Jobs succeed |
| 4 | Measure average retries | Per job | Within SLA |

h2. Expected Result
* Jobs succeed even when retries are needed
* Average retries per job <= 3.0 (staging) or <= 2.0 (production)

h2. Automation Status
✅ Automated

*Test Function:* `test_live_retry_behavior`
*Test File:* `be_focus_server_tests/load/test_live_load.py`
*Test Class:* `TestLiveJobLoad`
*Xray Marker:* `PZ-LOAD-203`
""",
        "priority": "High",
        "labels": ["load", "live", "retry", "grpc", "automation", "job_load"],
        "components": ["focus-server", "grpc"]
    },
    "LOAD-210": {
        "summary": "Load - Live - Heavy Channel Load (500 Channels)",
        "description": """h2. Objective
Verify that Live jobs handle heavy channel configurations (500 channels).

h2. Pre-Conditions
* System can handle high channel count
* Sufficient bandwidth available

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Create Live job | channels: 1-500, NFFT: 2048 | Job created |
| 2 | Connect to gRPC | Heavy data stream | Connected |
| 3 | Receive frames | Large spectrogram data | Frames received |
| 4 | Verify data integrity | Check frame format | Data valid |

h2. Expected Result
Heavy channel jobs complete with success rate >= 70% (staging) or >= 85% (production).

h2. Automation Status
✅ Automated

*Test Function:* `test_heavy_channel_live`
*Test File:* `be_focus_server_tests/load/test_live_load.py`
*Test Class:* `TestLiveHeavyLoad`
*Xray Marker:* `PZ-LOAD-210`
""",
        "priority": "Medium",
        "labels": ["load", "live", "heavy", "channels", "automation", "job_load"],
        "components": ["focus-server", "grpc"]
    },
    "LOAD-211": {
        "summary": "Load - Live - Sustained Load Test",
        "description": """h2. Objective
Verify that system maintains performance under sustained Live job load.

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Run 10 Live jobs | 2 concurrent at a time | Jobs created |
| 2 | Monitor system stability | Throughout test | System stable |
| 3 | Measure success rate | Track failures | Rate measured |
| 4 | Verify no performance degradation | Compare first vs last jobs | No degradation |

h2. Expected Result
Sustained load maintains success rate >= 80% (staging) or >= 95% (production).

h2. Automation Status
✅ Automated

*Test Function:* `test_sustained_live_load`
*Test File:* `be_focus_server_tests/load/test_live_load.py`
*Test Class:* `TestLiveHeavyLoad`
*Xray Marker:* `PZ-LOAD-211`
""",
        "priority": "Medium",
        "labels": ["load", "live", "sustained", "automation", "job_load"],
        "components": ["focus-server", "grpc"]
    },
    "LOAD-220": {
        "summary": "Load - Live - Maximum Concurrent Jobs Stress",
        "description": """h2. Objective
Verify system behavior under maximum concurrent Live job stress.

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Create 5 Live jobs simultaneously | All at once | Jobs created |
| 2 | Monitor system under stress | Track errors | Behavior recorded |
| 3 | Verify graceful handling | Check error handling | Graceful degradation |
| 4 | Measure success rate | Under stress | Rate measured |

h2. Expected Result
Under maximum stress, success rate >= 65% (staging) or >= 80% (production).

h2. Automation Status
✅ Automated

*Test Function:* `test_max_concurrent_live`
*Test File:* `be_focus_server_tests/load/test_live_load.py`
*Test Class:* `TestLiveStress`
*Xray Marker:* `PZ-LOAD-220`
""",
        "priority": "Medium",
        "labels": ["load", "live", "stress", "concurrent", "automation", "job_load"],
        "components": ["focus-server", "grpc"]
    },
}


# =============================================================================
# HISTORIC JOB TESTS (test_historic_load.py)
# =============================================================================

HISTORIC_JOB_TESTS = {
    "LOAD-300": {
        "summary": "Load - Historic - Single Historic Job Complete Flow",
        "description": """h2. Objective
Verify that a single Historic playback job completes successfully.

h2. Pre-Conditions
* Recordings available in the system
* Focus Server API is running

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Query available recordings | /recordings_in_time_range | Recordings found |
| 2 | Send POST /configure | With start_time and end_time | Job created |
| 3 | Connect to gRPC stream | Using returned URL/port | Connected |
| 4 | Receive playback frames | From recording | Frames received |
| 5 | Disconnect | Clean disconnection | Disconnected |

h2. Expected Result
Historic job plays back recorded data successfully.

h2. Automation Status
✅ Automated

*Test Function:* `test_single_historic_job`
*Test File:* `be_focus_server_tests/load/test_historic_load.py`
*Test Class:* `TestHistoricJobLoad`
*Xray Marker:* `PZ-LOAD-300`
""",
        "priority": "High",
        "labels": ["load", "historic", "job", "playback", "automation", "job_load"],
        "components": ["focus-server", "grpc"]
    },
    "LOAD-301": {
        "summary": "Load - Historic - Job Timing Meets SLA",
        "description": """h2. Objective
Verify that Historic job timing meets SLA requirements.

h2. Expected Result
Historic jobs meet timing SLA:
* Staging: P95 < 60s, P99 < 120s
* Production: P95 < 30s, P99 < 60s

h2. Automation Status
✅ Automated

*Test Function:* `test_historic_job_timing`
*Test File:* `be_focus_server_tests/load/test_historic_load.py`
*Test Class:* `TestHistoricJobLoad`
*Xray Marker:* `PZ-LOAD-301`
""",
        "priority": "High",
        "labels": ["load", "historic", "sla", "timing", "automation", "job_load"],
        "components": ["focus-server", "grpc"]
    },
    "LOAD-302": {
        "summary": "Load - Historic - Multiple Concurrent Jobs",
        "description": """h2. Objective
Verify that system handles multiple concurrent Historic playback jobs.

h2. Expected Result
Success rate >= 75% (staging) or >= 90% (production) for concurrent Historic jobs.

h2. Automation Status
✅ Automated

*Test Function:* `test_concurrent_historic_jobs`
*Test File:* `be_focus_server_tests/load/test_historic_load.py`
*Test Class:* `TestHistoricJobLoad`
*Xray Marker:* `PZ-LOAD-302`
""",
        "priority": "High",
        "labels": ["load", "historic", "concurrent", "automation", "job_load"],
        "components": ["focus-server", "grpc"]
    },
    "LOAD-303": {
        "summary": "Load - Historic - Retry Behavior",
        "description": """h2. Objective
Verify that Historic jobs handle gRPC connection delays with proper retry behavior.

h2. Expected Result
Jobs succeed with retries, average retries <= 4.0 (staging) or <= 2.5 (production).

h2. Automation Status
✅ Automated

*Test Function:* `test_historic_retry_behavior`
*Test File:* `be_focus_server_tests/load/test_historic_load.py`
*Test Class:* `TestHistoricJobLoad`
*Xray Marker:* `PZ-LOAD-303`
""",
        "priority": "Medium",
        "labels": ["load", "historic", "retry", "automation", "job_load"],
        "components": ["focus-server", "grpc"]
    },
    "LOAD-310": {
        "summary": "Load - Historic - Heavy Channel Load (500 Channels)",
        "description": """h2. Objective
Verify that Historic jobs handle heavy channel configurations (500 channels).

h2. Expected Result
Heavy Historic jobs complete with success rate >= 65% (staging) or >= 80% (production).

h2. Automation Status
✅ Automated

*Test Function:* `test_heavy_channel_historic`
*Test File:* `be_focus_server_tests/load/test_historic_load.py`
*Test Class:* `TestHistoricHeavyLoad`
*Xray Marker:* `PZ-LOAD-310`
""",
        "priority": "Medium",
        "labels": ["load", "historic", "heavy", "channels", "automation", "job_load"],
        "components": ["focus-server", "grpc"]
    },
    "LOAD-311": {
        "summary": "Load - Historic - Sustained Load Test",
        "description": """h2. Objective
Verify that system maintains performance under sustained Historic job load.

h2. Expected Result
Sustained load maintains success rate >= 75% (staging) or >= 90% (production).

h2. Automation Status
✅ Automated

*Test Function:* `test_sustained_historic_load`
*Test File:* `be_focus_server_tests/load/test_historic_load.py`
*Test Class:* `TestHistoricHeavyLoad`
*Xray Marker:* `PZ-LOAD-311`
""",
        "priority": "Medium",
        "labels": ["load", "historic", "sustained", "automation", "job_load"],
        "components": ["focus-server", "grpc"]
    },
    "LOAD-320": {
        "summary": "Load - Historic - Maximum Concurrent Jobs Stress",
        "description": """h2. Objective
Verify system behavior under maximum concurrent Historic job stress.

h2. Expected Result
Under maximum stress, success rate >= 60% (staging) or >= 75% (production).

h2. Automation Status
✅ Automated

*Test Function:* `test_max_concurrent_historic`
*Test File:* `be_focus_server_tests/load/test_historic_load.py`
*Test Class:* `TestHistoricStress`
*Xray Marker:* `PZ-LOAD-320`
""",
        "priority": "Medium",
        "labels": ["load", "historic", "stress", "concurrent", "automation", "job_load"],
        "components": ["focus-server", "grpc"]
    },
    "LOAD-330": {
        "summary": "Load - Historic - Recording Availability Check",
        "description": """h2. Objective
Verify that recordings are available before running Historic tests.

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Query recordings API | Last 24 hours | Recordings found |
| 2 | Verify recording format | start_time, end_time | Format valid |
| 3 | List available recordings | Top 5 | Recordings listed |

h2. Expected Result
At least one recording is available for Historic playback tests.

h2. Automation Status
✅ Automated

*Test Function:* `test_recording_availability`
*Test File:* `be_focus_server_tests/load/test_historic_load.py`
*Test Class:* `TestHistoricSpecific`
*Xray Marker:* `PZ-LOAD-330`
""",
        "priority": "High",
        "labels": ["load", "historic", "recording", "validation", "automation", "job_load"],
        "components": ["focus-server"]
    },
    "LOAD-331": {
        "summary": "Load - Historic - Playback Runs to Completion",
        "description": """h2. Objective
Verify that Historic playback runs to completion and receives all expected frames.

h2. Expected Result
Historic playback completes with frames received from recording.

h2. Automation Status
✅ Automated

*Test Function:* `test_historic_playback_complete`
*Test File:* `be_focus_server_tests/load/test_historic_load.py`
*Test Class:* `TestHistoricSpecific`
*Xray Marker:* `PZ-LOAD-331`
""",
        "priority": "Medium",
        "labels": ["load", "historic", "playback", "completion", "automation", "job_load"],
        "components": ["focus-server", "grpc"]
    },
}


# =============================================================================
# QUICK LOAD METRICS TESTS (test_quick_load_metrics.py)
# =============================================================================

QUICK_LOAD_TESTS = {
    "LOAD-000": {
        "summary": "Load - Quick - API Response Time Baseline",
        "description": """h2. Objective
Establish baseline API response times for load comparison.

h2. Automation Status
✅ Automated

*Test Function:* `test_api_response_time_baseline`
*Test File:* `be_focus_server_tests/load/test_quick_load_metrics.py`
*Xray Marker:* `PZ-LOAD-000`
""",
        "priority": "Medium",
        "labels": ["load", "quick", "baseline", "api", "automation"],
        "components": ["focus-server"]
    },
    "LOAD-001": {
        "summary": "Load - Quick - Configure Endpoint Performance",
        "description": """h2. Objective
Measure /configure endpoint performance under light load.

h2. Automation Status
✅ Automated

*Test Function:* `test_configure_endpoint_performance`
*Test File:* `be_focus_server_tests/load/test_quick_load_metrics.py`
*Xray Marker:* `PZ-LOAD-001`
""",
        "priority": "Medium",
        "labels": ["load", "quick", "configure", "performance", "automation"],
        "components": ["focus-server"]
    },
    "LOAD-002": {
        "summary": "Load - Quick - Concurrent Request Handling",
        "description": """h2. Objective
Verify system handles concurrent requests efficiently.

h2. Automation Status
✅ Automated

*Test Function:* `test_concurrent_request_handling`
*Test File:* `be_focus_server_tests/load/test_quick_load_metrics.py`
*Xray Marker:* `PZ-LOAD-002`
""",
        "priority": "Medium",
        "labels": ["load", "quick", "concurrent", "automation"],
        "components": ["focus-server"]
    },
    "LOAD-003": {
        "summary": "Load - Quick - Error Rate Under Load",
        "description": """h2. Objective
Measure error rate under light load conditions.

h2. Automation Status
✅ Automated

*Test Function:* `test_error_rate_under_load`
*Test File:* `be_focus_server_tests/load/test_quick_load_metrics.py`
*Xray Marker:* `PZ-LOAD-003`
""",
        "priority": "Medium",
        "labels": ["load", "quick", "error-rate", "automation"],
        "components": ["focus-server"]
    },
    "LOAD-004": {
        "summary": "Load - Quick - Throughput Measurement",
        "description": """h2. Objective
Measure system throughput (requests per second).

h2. Automation Status
✅ Automated

*Test Function:* `test_throughput_measurement`
*Test File:* `be_focus_server_tests/load/test_quick_load_metrics.py`
*Xray Marker:* `PZ-LOAD-004`
""",
        "priority": "Medium",
        "labels": ["load", "quick", "throughput", "automation"],
        "components": ["focus-server"]
    },
    "LOAD-010": {
        "summary": "Load - Quick - P50/P95/P99 Latency Metrics",
        "description": """h2. Objective
Measure percentile latency metrics (P50, P95, P99).

h2. Automation Status
✅ Automated

*Test Function:* `test_latency_percentiles`
*Test File:* `be_focus_server_tests/load/test_quick_load_metrics.py`
*Xray Marker:* `PZ-LOAD-010`
""",
        "priority": "Medium",
        "labels": ["load", "quick", "latency", "percentiles", "automation"],
        "components": ["focus-server"]
    },
    "LOAD-011": {
        "summary": "Load - Quick - Resource Usage Under Load",
        "description": """h2. Objective
Monitor resource usage during load testing.

h2. Automation Status
✅ Automated

*Test Function:* `test_resource_usage_under_load`
*Test File:* `be_focus_server_tests/load/test_quick_load_metrics.py`
*Xray Marker:* `PZ-LOAD-011`
""",
        "priority": "Medium",
        "labels": ["load", "quick", "resources", "monitoring", "automation"],
        "components": ["focus-server"]
    },
}


# =============================================================================
# LIVE JOB LOAD TESTS (test_live_job_load.py)
# =============================================================================

LIVE_JOB_LOAD_TESTS = {
    "LOAD-100": {
        "summary": "Load - Live Job - Single Job Full Flow",
        "description": """h2. Objective
Test single Live job through complete flow with detailed metrics.

h2. Automation Status
✅ Automated

*Test Function:* `test_single_live_job_full_flow`
*Test File:* `be_focus_server_tests/load/test_live_job_load.py`
*Xray Marker:* `PZ-LOAD-100`
""",
        "priority": "High",
        "labels": ["load", "live", "job", "full-flow", "automation", "job_load"],
        "components": ["focus-server", "grpc"]
    },
    "LOAD-101": {
        "summary": "Load - Live Job - Sequential Jobs",
        "description": """h2. Objective
Test sequential Live job creation and execution.

h2. Automation Status
✅ Automated

*Test Function:* `test_sequential_live_jobs`
*Test File:* `be_focus_server_tests/load/test_live_job_load.py`
*Xray Marker:* `PZ-LOAD-101`
""",
        "priority": "High",
        "labels": ["load", "live", "sequential", "automation", "job_load"],
        "components": ["focus-server", "grpc"]
    },
    "LOAD-102": {
        "summary": "Load - Live Job - Parallel Jobs",
        "description": """h2. Objective
Test parallel Live job creation and execution.

h2. Automation Status
✅ Automated

*Test Function:* `test_parallel_live_jobs`
*Test File:* `be_focus_server_tests/load/test_live_job_load.py`
*Xray Marker:* `PZ-LOAD-102`
""",
        "priority": "High",
        "labels": ["load", "live", "parallel", "automation", "job_load"],
        "components": ["focus-server", "grpc"]
    },
    "LOAD-103": {
        "summary": "Load - Live Job - Channel Range Variations",
        "description": """h2. Objective
Test Live jobs with different channel range configurations.

h2. Automation Status
✅ Automated

*Test Function:* `test_channel_range_variations`
*Test File:* `be_focus_server_tests/load/test_live_job_load.py`
*Xray Marker:* `PZ-LOAD-103`
""",
        "priority": "Medium",
        "labels": ["load", "live", "channels", "variations", "automation", "job_load"],
        "components": ["focus-server", "grpc"]
    },
    "LOAD-110": {
        "summary": "Load - Live Job - High Channel Count",
        "description": """h2. Objective
Test Live jobs with high channel count (500+).

h2. Automation Status
✅ Automated

*Test Function:* `test_high_channel_count`
*Test File:* `be_focus_server_tests/load/test_live_job_load.py`
*Xray Marker:* `PZ-LOAD-110`
""",
        "priority": "Medium",
        "labels": ["load", "live", "high-channels", "automation", "job_load"],
        "components": ["focus-server", "grpc"]
    },
    "LOAD-111": {
        "summary": "Load - Live Job - Extended Streaming",
        "description": """h2. Objective
Test Live jobs with extended streaming duration.

h2. Automation Status
✅ Automated

*Test Function:* `test_extended_streaming`
*Test File:* `be_focus_server_tests/load/test_live_job_load.py`
*Xray Marker:* `PZ-LOAD-111`
""",
        "priority": "Medium",
        "labels": ["load", "live", "extended", "streaming", "automation", "job_load"],
        "components": ["focus-server", "grpc"]
    },
    "LOAD-120": {
        "summary": "Load - Live Job - Stress Test Maximum Capacity",
        "description": """h2. Objective
Stress test Live jobs at maximum system capacity.

h2. Automation Status
✅ Automated

*Test Function:* `test_stress_maximum_capacity`
*Test File:* `be_focus_server_tests/load/test_live_job_load.py`
*Xray Marker:* `PZ-LOAD-120`
""",
        "priority": "Medium",
        "labels": ["load", "live", "stress", "capacity", "automation", "job_load"],
        "components": ["focus-server", "grpc"]
    },
}


# =============================================================================
# ALL TESTS COMBINED
# =============================================================================

ALL_TESTS = {
    "live": LIVE_JOB_TESTS,
    "historic": HISTORIC_JOB_TESTS,
    "quick": QUICK_LOAD_TESTS,
    "live_job": LIVE_JOB_LOAD_TESTS,
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
        test_id: Test identifier (e.g., "LOAD-200")
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
        return issue_key
        
    except Exception as e:
        logger.error(f"❌ Failed to create {test_id}: {e}")
        return None


def create_tests_by_category(
    client: JiraClient,
    category: str,
    tests: Dict[str, Dict],
    dry_run: bool = False
) -> Dict[str, List]:
    """Create tests for a specific category."""
    results = {"created": [], "failed": []}
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Creating {category.upper()} tests ({len(tests)} tests)")
    logger.info(f"{'='*60}")
    
    for test_id, test_data in tests.items():
        issue_key = create_test_case(client, test_id, test_data, dry_run)
        
        if issue_key:
            results["created"].append({
                "local_id": test_id,
                "jira_key": issue_key,
                "summary": test_data['summary']
            })
        else:
            results["failed"].append(test_id)
    
    return results


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Create Live & Historic Job Tests in Jira Xray'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without creating tests'
    )
    
    parser.add_argument(
        '--category',
        choices=['live', 'historic', 'quick', 'live_job', 'all'],
        default='all',
        help='Category of tests to create (default: all)'
    )
    
    args = parser.parse_args()
    
    try:
        client = JiraClient()
        
        print("\n" + "=" * 80)
        print(f"{'[DRY RUN] ' if args.dry_run else ''}Creating Load & Job Tests in Jira Xray")
        print("=" * 80)
        
        all_results = {"created": [], "failed": []}
        
        # Determine which categories to process
        if args.category == 'all':
            categories = ALL_TESTS.keys()
        else:
            categories = [args.category]
        
        # Process each category
        for category in categories:
            if category in ALL_TESTS:
                results = create_tests_by_category(
                    client,
                    category,
                    ALL_TESTS[category],
                    args.dry_run
                )
                all_results["created"].extend(results["created"])
                all_results["failed"].extend(results["failed"])
        
        # Print summary
        print("\n" + "=" * 80)
        print("CREATION SUMMARY")
        print("=" * 80)
        
        total_tests = sum(len(tests) for cat, tests in ALL_TESTS.items() 
                         if args.category == 'all' or cat == args.category)
        
        print(f"Total tests: {total_tests}")
        print(f"✅ Created: {len(all_results['created'])}")
        print(f"❌ Failed: {len(all_results['failed'])}")
        
        if all_results["created"]:
            print("\n📋 Created Tests:")
            print("-" * 80)
            for test in all_results["created"]:
                print(f"  {test['local_id']} → {test['jira_key']}: {test['summary'][:50]}...")
        
        if all_results["failed"]:
            print(f"\n❌ Failed Tests: {', '.join(all_results['failed'])}")
        
        if args.dry_run:
            print("\n⚠️  [DRY RUN] No tests were actually created")
        else:
            # Generate mapping file
            print("\n📝 Generating marker mapping...")
            mapping_lines = []
            for test in all_results["created"]:
                mapping_lines.append(f"# {test['local_id']} → {test['jira_key']}")
            
            if mapping_lines:
                print("\n" + "-" * 40)
                print("Update your test markers with:")
                print("-" * 40)
                for test in all_results["created"]:
                    print(f'@pytest.mark.xray("{test["jira_key"]}")  # Was: PZ-{test["local_id"]}')
        
        client.close()
        
        return 0 if len(all_results["failed"]) == 0 else 1
        
    except Exception as e:
        logger.error(f"Failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

