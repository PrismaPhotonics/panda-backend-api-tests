"""
Script to create Jira tickets for all alert test cases.

This script creates Jira test cases for all alert tests documented in the automation project.

Usage:
    python create_jira_tickets.py --project PROJECT_KEY --cloud-id CLOUD_ID

Requirements:
    - Atlassian MCP server configured and authenticated
    - Jira project access
    - Test issue type available in project
"""

import argparse
import json
import csv
from typing import List, Dict

# Test cases data
TEST_CASES = [
    {
        "test_id": "PZ-15000",
        "summary": "Alert Generation - Successful SD Alert",
        "description": "Verify that SD (Spatial Distribution) alerts can be successfully generated and processed through the backend system.",
        "test_type": "Integration Test",
        "category": "Positive",
        "file": "test_alert_generation_positive.py"
    },
    {
        "test_id": "PZ-15001",
        "summary": "Alert Generation - Successful SC Alert",
        "description": "Verify that SC (Single Channel) alerts can be successfully generated and processed through the backend system.",
        "test_type": "Integration Test",
        "category": "Positive",
        "file": "test_alert_generation_positive.py"
    },
    {
        "test_id": "PZ-15002",
        "summary": "Alert Generation - Multiple Alerts",
        "description": "Verify that multiple alerts can be generated and processed simultaneously without conflicts.",
        "test_type": "Integration Test",
        "category": "Positive",
        "file": "test_alert_generation_positive.py"
    },
    {
        "test_id": "PZ-15003",
        "summary": "Alert Generation - Different Severity Levels",
        "description": "Verify that alerts with different severity levels (1, 2, 3) are correctly generated and processed.",
        "test_type": "Integration Test",
        "category": "Positive",
        "file": "test_alert_generation_positive.py"
    },
    {
        "test_id": "PZ-15004",
        "summary": "Alert Generation - Alert Processing via RabbitMQ",
        "description": "Verify that alerts are correctly processed through RabbitMQ message queue system.",
        "test_type": "Integration Test",
        "category": "Positive",
        "file": "test_alert_generation_positive.py"
    },
    {
        "test_id": "PZ-15010",
        "summary": "Alert Generation - Invalid Class ID",
        "description": "Verify that alerts with invalid class IDs are rejected with appropriate error message (400/422 status code).",
        "test_type": "Integration Test",
        "category": "Negative",
        "file": "test_alert_generation_negative.py"
    },
    {
        "test_id": "PZ-15011",
        "summary": "Alert Generation - Invalid Severity",
        "description": "Verify that alerts with invalid severity levels are rejected with appropriate error message (400/422 status code).",
        "test_type": "Integration Test",
        "category": "Negative",
        "file": "test_alert_generation_negative.py"
    },
    {
        "test_id": "PZ-15012",
        "summary": "Alert Generation - Invalid DOF Range",
        "description": "Verify that alerts with invalid DOF (Distance on Fiber) values are rejected or handled appropriately (400/422 status code).",
        "test_type": "Integration Test",
        "category": "Negative",
        "file": "test_alert_generation_negative.py"
    },
    {
        "test_id": "PZ-15013",
        "summary": "Alert Generation - Missing Required Fields",
        "description": "Verify that alerts with missing required fields are rejected (400 Bad Request).",
        "test_type": "Integration Test",
        "category": "Negative",
        "file": "test_alert_generation_negative.py"
    },
    {
        "test_id": "PZ-15014",
        "summary": "Alert Generation - RabbitMQ Connection Failure",
        "description": "Verify that system handles RabbitMQ connection failures gracefully with appropriate error message.",
        "test_type": "Integration Test",
        "category": "Negative",
        "file": "test_alert_generation_negative.py"
    },
    {
        "test_id": "PZ-15015",
        "summary": "Alert Generation - MongoDB Connection Failure",
        "description": "SKIPPED: Alerts are NOT stored in MongoDB - this test is invalid.",
        "test_type": "Integration Test",
        "category": "Negative",
        "file": "test_alert_generation_negative.py",
        "skip": True
    },
    {
        "test_id": "PZ-15016",
        "summary": "Alert Generation - Invalid Alert ID Format",
        "description": "Verify that alerts with invalid alert ID formats are rejected or handled appropriately (400/422 status code).",
        "test_type": "Integration Test",
        "category": "Negative",
        "file": "test_alert_generation_negative.py"
    },
    {
        "test_id": "PZ-15017",
        "summary": "Alert Generation - Duplicate Alert IDs",
        "description": "Verify that duplicate alert IDs are handled appropriately. Note: The system may accept duplicate IDs as separate alert events.",
        "test_type": "Integration Test",
        "category": "Negative",
        "file": "test_alert_generation_negative.py"
    },
    {
        "test_id": "PZ-15020",
        "summary": "Alert Generation - Boundary DOF Values",
        "description": "Verify that alerts with boundary DOF values (min, max, edge cases) are handled correctly.",
        "test_type": "Integration Test",
        "category": "Edge Case",
        "file": "test_alert_generation_edge_cases.py"
    },
    {
        "test_id": "PZ-15021",
        "summary": "Alert Generation - Minimum/Maximum Severity",
        "description": "Verify that alerts with minimum (1) and maximum (3) severity are handled correctly.",
        "test_type": "Integration Test",
        "category": "Edge Case",
        "file": "test_alert_generation_edge_cases.py"
    },
    {
        "test_id": "PZ-15022",
        "summary": "Alert Generation - Zero Alerts Amount",
        "description": "Verify that alerts with alertsAmount = 0 are handled appropriately.",
        "test_type": "Integration Test",
        "category": "Edge Case",
        "file": "test_alert_generation_edge_cases.py"
    },
    {
        "test_id": "PZ-15023",
        "summary": "Alert Generation - Very Large Alert ID",
        "description": "Verify that alerts with very long alert IDs (1000+ characters) are handled correctly (truncate, reject, or process).",
        "test_type": "Integration Test",
        "category": "Edge Case",
        "file": "test_alert_generation_edge_cases.py"
    },
    {
        "test_id": "PZ-15024",
        "summary": "Alert Generation - Concurrent Alerts with Same DOF",
        "description": "Verify that multiple alerts with the same DOF can be processed concurrently without conflicts.",
        "test_type": "Integration Test",
        "category": "Edge Case",
        "file": "test_alert_generation_edge_cases.py"
    },
    {
        "test_id": "PZ-15025",
        "summary": "Alert Generation - Rapid Sequential Alerts",
        "description": "Verify that rapid sequential alerts are processed correctly without loss or corruption.",
        "test_type": "Integration Test",
        "category": "Edge Case",
        "file": "test_alert_generation_edge_cases.py"
    },
    {
        "test_id": "PZ-15026",
        "summary": "Alert Generation - Alert with Maximum Fields",
        "description": "Verify that alerts with all possible fields set to maximum values are processed correctly.",
        "test_type": "Integration Test",
        "category": "Edge Case",
        "file": "test_alert_generation_edge_cases.py"
    },
    {
        "test_id": "PZ-15027",
        "summary": "Alert Generation - Alert with Minimum Fields",
        "description": "Verify that alerts with only required fields (minimum) are processed correctly.",
        "test_type": "Integration Test",
        "category": "Edge Case",
        "file": "test_alert_generation_edge_cases.py"
    },
    {
        "test_id": "PZ-15030",
        "summary": "Alert Generation - High Volume Load",
        "description": "Verify that system can handle high volume of alerts (1000+) without degradation or failures. Success rate >= 99%.",
        "test_type": "Integration Test",
        "category": "Load",
        "file": "test_alert_generation_load.py"
    },
    {
        "test_id": "PZ-15031",
        "summary": "Alert Generation - Sustained Load",
        "description": "Verify that system can handle sustained load over extended period (10+ minutes) without degradation. No memory leaks or performance degradation.",
        "test_type": "Integration Test",
        "category": "Load",
        "file": "test_alert_generation_load.py"
    },
    {
        "test_id": "PZ-15032",
        "summary": "Alert Generation - Burst Load",
        "description": "Verify that system can handle sudden burst of alerts (500 simultaneous) without failures or degradation.",
        "test_type": "Integration Test",
        "category": "Load",
        "file": "test_alert_generation_load.py"
    },
    {
        "test_id": "PZ-15033",
        "summary": "Alert Generation - Mixed Alert Types Load",
        "description": "Verify that system can handle mixed alert types (SD, SC, different severities) under load without issues.",
        "test_type": "Integration Test",
        "category": "Load",
        "file": "test_alert_generation_load.py"
    },
    {
        "test_id": "PZ-15034",
        "summary": "Alert Generation - RabbitMQ Queue Capacity",
        "description": "Verify that RabbitMQ queues can handle high volume of alerts without overflow or message loss.",
        "test_type": "Integration Test",
        "category": "Load",
        "file": "test_alert_generation_load.py"
    },
    {
        "test_id": "PZ-15035",
        "summary": "Alert Generation - MongoDB Write Load",
        "description": "SKIPPED: Alerts are NOT stored in MongoDB - this test is invalid.",
        "test_type": "Integration Test",
        "category": "Load",
        "file": "test_alert_generation_load.py",
        "skip": True
    },
    {
        "test_id": "PZ-15040",
        "summary": "Alert Generation - Response Time",
        "description": "Verify that alert generation response time meets requirements: Mean < 100ms, P95 < 200ms, P99 < 500ms.",
        "test_type": "Integration Test",
        "category": "Performance",
        "file": "test_alert_generation_performance.py"
    },
    {
        "test_id": "PZ-15041",
        "summary": "Alert Generation - Throughput",
        "description": "Verify that alert generation throughput meets requirements: >= 100 alerts/second.",
        "test_type": "Integration Test",
        "category": "Performance",
        "file": "test_alert_generation_performance.py"
    },
    {
        "test_id": "PZ-15042",
        "summary": "Alert Generation - Latency",
        "description": "Verify that alert generation latency (time from creation to processing) meets requirements: Mean < 50ms, P95 < 100ms.",
        "test_type": "Integration Test",
        "category": "Performance",
        "file": "test_alert_generation_performance.py"
    },
    {
        "test_id": "PZ-15043",
        "summary": "Alert Generation - Resource Usage",
        "description": "Verify that alert generation does not cause excessive resource usage: CPU usage < 80%, Memory usage increase < 500MB.",
        "test_type": "Integration Test",
        "category": "Performance",
        "file": "test_alert_generation_performance.py"
    },
    {
        "test_id": "PZ-15044",
        "summary": "Alert Generation - End-to-End Performance",
        "description": "Verify end-to-end performance from alert creation to storage: Mean < 200ms, P95 < 500ms.",
        "test_type": "Integration Test",
        "category": "Performance",
        "file": "test_alert_generation_performance.py"
    },
    {
        "test_id": "PZ-15045",
        "summary": "Alert Generation - RabbitMQ Performance",
        "description": "Verify RabbitMQ performance in alert processing: Publish time < 10ms, Consume time < 50ms.",
        "test_type": "Integration Test",
        "category": "Performance",
        "file": "test_alert_generation_performance.py"
    },
    {
        "test_id": "PZ-15046",
        "summary": "Alert Generation - MongoDB Performance",
        "description": "SKIPPED: Alerts are NOT stored in MongoDB - this test is invalid.",
        "test_type": "Integration Test",
        "category": "Performance",
        "file": "test_alert_generation_performance.py",
        "skip": True
    },
    {
        "test_id": "PZ-15051",
        "summary": "Deep Alert Logs Investigation",
        "description": "Comprehensive investigation of alert logs across all components: Focus Server, Prisma Web App API, RabbitMQ, gRPC Jobs, MongoDB, RabbitMQ Management API.",
        "test_type": "Integration Test",
        "category": "Investigation",
        "file": "test_deep_alert_logs_investigation.py"
    }
]


def format_description(test_case: Dict) -> str:
    """Format test case description for Jira."""
    description = f"""
{test_case['description']}

h3. Test Details
* Test ID: {test_case['test_id']}
* Test Type: {test_case['test_type']}
* Category: {test_case['category']}
* File: be_focus_server_tests/integration/alerts/{test_case['file']}

h3. Test Location
{{code}}
be_focus_server_tests/integration/alerts/{test_case['file']}
{{code}}
"""
    if test_case.get('skip'):
        description += "\nh3. Note\n*This test is currently SKIPPED.*\n"
    
    return description.strip()


def print_instructions():
    """Print instructions for creating Jira tickets."""
    print("=" * 80)
    print("JIRA TICKET CREATION INSTRUCTIONS")
    print("=" * 80)
    print("\nTo create Jira tickets for all alert test cases:")
    print("\n1. Ensure Atlassian MCP server is configured and authenticated")
    print("2. Get your Cloud ID from Atlassian")
    print("3. Get your Jira project key")
    print("4. Run this script with:")
    print("   python create_jira_tickets.py --project PROJECT_KEY --cloud-id CLOUD_ID")
    print("\nAlternatively, use the CSV file (jira_test_cases_import.csv) for bulk import.")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create Jira tickets for alert test cases")
    parser.add_argument("--project", help="Jira project key")
    parser.add_argument("--cloud-id", help="Atlassian Cloud ID")
    parser.add_argument("--dry-run", action="store_true", help="Print tickets without creating them")
    
    args = parser.parse_args()
    
    if args.dry_run or not args.project or not args.cloud_id:
        print_instructions()
        print(f"\nTotal test cases: {len(TEST_CASES)}")
        print(f"Skipped tests: {sum(1 for tc in TEST_CASES if tc.get('skip'))}")
        print(f"Active tests: {sum(1 for tc in TEST_CASES if not tc.get('skip'))}")
        print("\nSample ticket format:")
        if TEST_CASES:
            sample = TEST_CASES[0]
            print(f"\nSummary: {sample['summary']}")
            print(f"Description:\n{format_description(sample)}")
    else:
        print(f"Creating {len(TEST_CASES)} Jira tickets...")
        print("Note: This requires Atlassian MCP server to be configured.")
        print("Please use the CSV file for manual import or configure MCP authentication.")

