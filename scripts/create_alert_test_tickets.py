"""
Script to create Jira tickets for all alert test cases.

This script creates Jira test cases for all 33 alert tests documented in the automation project.

Usage:
    python scripts/create_alert_test_tickets.py

Requirements:
    - Jira API token configured in config/jira_config.yaml
    - Project PZ access
    - Test issue type available in project
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent

# IMPORTANT: Add project root AFTER removing scripts/jira to avoid import conflict
# Remove scripts/jira from path if it exists to prevent importing scripts/jira/__init__.py instead of jira package
scripts_jira_dir = project_root / "scripts" / "jira"
scripts_dir = project_root / "scripts"

# Temporarily rename scripts/jira/__init__.py to avoid import conflict
import shutil
scripts_jira_init = scripts_jira_dir / "__init__.py"
scripts_jira_init_backup = scripts_jira_dir / "__init__.py.backup"
backup_created = False

if scripts_jira_init.exists():
    try:
        shutil.move(str(scripts_jira_init), str(scripts_jira_init_backup))
        backup_created = True
    except Exception as e:
        pass  # If we can't rename, continue anyway

try:
    sys.path.insert(0, str(project_root))
    
    from external.jira import JiraClient
finally:
    # Restore __init__.py if we backed it up
    if backup_created and scripts_jira_init_backup.exists():
        try:
            shutil.move(str(scripts_jira_init_backup), str(scripts_jira_init))
        except Exception:
            pass
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test cases data - all 33 backend integration tests
TEST_CASES = [
    {
        "test_id": "PZ-15000",
        "summary": "Alert Generation - Successful SD Alert",
        "description": """Verify that SD (Spatial Distribution) alerts can be successfully generated and processed through the backend system.

h3. Test Details
* Test ID: PZ-15000
* Test Type: Integration Test
* Category: Positive
* File: be_focus_server_tests/integration/alerts/test_alert_generation_positive.py

h3. Test Steps
# Create SD alert payload (classId=104)
# Send alert via HTTP API (push-to-rabbit endpoint)
# Verify alert is sent successfully

h3. Expected Result
Alert is successfully generated and sent via HTTP API.""",
        "category": "Positive"
    },
    {
        "test_id": "PZ-15001",
        "summary": "Alert Generation - Successful SC Alert",
        "description": """Verify that SC (Single Channel) alerts can be successfully generated and processed through the backend system.

h3. Test Details
* Test ID: PZ-15001
* Test Type: Integration Test
* Category: Positive
* File: be_focus_server_tests/integration/alerts/test_alert_generation_positive.py

h3. Test Steps
# Create SC alert payload (classId=103)
# Send alert via HTTP API
# Verify alert is sent successfully

h3. Expected Result
Alert is successfully generated and processed.""",
        "category": "Positive"
    },
    {
        "test_id": "PZ-15002",
        "summary": "Alert Generation - Multiple Alerts",
        "description": """Verify that multiple alerts can be generated and processed simultaneously without conflicts.

h3. Test Details
* Test ID: PZ-15002
* Test Type: Integration Test
* Category: Positive
* File: be_focus_server_tests/integration/alerts/test_alert_generation_positive.py

h3. Expected Result
All alerts are successfully generated and processed. No conflicts or data loss.""",
        "category": "Positive"
    },
    {
        "test_id": "PZ-15003",
        "summary": "Alert Generation - Different Severity Levels",
        "description": """Verify that alerts with different severity levels (1, 2, 3) are correctly generated and processed.

h3. Test Details
* Test ID: PZ-15003
* Test Type: Integration Test
* Category: Positive
* File: be_focus_server_tests/integration/alerts/test_alert_generation_positive.py

h3. Expected Result
All severity levels are processed correctly.""",
        "category": "Positive"
    },
    {
        "test_id": "PZ-15004",
        "summary": "Alert Generation - Alert Processing via RabbitMQ",
        "description": """Verify that alerts are correctly processed through RabbitMQ message queue system.

h3. Test Details
* Test ID: PZ-15004
* Test Type: Integration Test
* Category: Positive
* File: be_focus_server_tests/integration/alerts/test_alert_generation_positive.py

h3. Expected Result
Alert is correctly processed via RabbitMQ.""",
        "category": "Positive"
    },
    {
        "test_id": "PZ-15010",
        "summary": "Alert Generation - Invalid Class ID",
        "description": """Verify that alerts with invalid class IDs are rejected.

h3. Test Details
* Test ID: PZ-15010
* Test Type: Integration Test
* Category: Negative
* File: be_focus_server_tests/integration/alerts/test_alert_generation_negative.py

h3. Expected Result
Alert is rejected with appropriate error message (400/422 status code).""",
        "category": "Negative"
    },
    {
        "test_id": "PZ-15011",
        "summary": "Alert Generation - Invalid Severity",
        "description": """Verify that alerts with invalid severity levels are rejected.

h3. Test Details
* Test ID: PZ-15011
* Test Type: Integration Test
* Category: Negative
* File: be_focus_server_tests/integration/alerts/test_alert_generation_negative.py

h3. Expected Result
Alert is rejected with appropriate error message (400/422 status code).""",
        "category": "Negative"
    },
    {
        "test_id": "PZ-15012",
        "summary": "Alert Generation - Invalid DOF Range",
        "description": """Verify that alerts with invalid DOF (Distance on Fiber) values are rejected or handled appropriately.

h3. Test Details
* Test ID: PZ-15012
* Test Type: Integration Test
* Category: Negative
* File: be_focus_server_tests/integration/alerts/test_alert_generation_negative.py

h3. Expected Result
Invalid DOF values are rejected or handled appropriately (400/422 status code).""",
        "category": "Negative"
    },
    {
        "test_id": "PZ-15013",
        "summary": "Alert Generation - Missing Required Fields",
        "description": """Verify that alerts with missing required fields are rejected.

h3. Test Details
* Test ID: PZ-15013
* Test Type: Integration Test
* Category: Negative
* File: be_focus_server_tests/integration/alerts/test_alert_generation_negative.py

h3. Expected Result
Alerts with missing required fields are rejected (400 Bad Request).""",
        "category": "Negative"
    },
    {
        "test_id": "PZ-15014",
        "summary": "Alert Generation - RabbitMQ Connection Failure",
        "description": """Verify that system handles RabbitMQ connection failures gracefully.

h3. Test Details
* Test ID: PZ-15014
* Test Type: Integration Test
* Category: Negative
* File: be_focus_server_tests/integration/alerts/test_alert_generation_negative.py

h3. Expected Result
Connection failure is handled gracefully. Appropriate error message is returned.""",
        "category": "Negative"
    },
    {
        "test_id": "PZ-15015",
        "summary": "Alert Generation - MongoDB Connection Failure",
        "description": """SKIPPED: Alerts are NOT stored in MongoDB - this test is invalid.

h3. Test Details
* Test ID: PZ-15015
* Test Type: Integration Test
* Category: Negative
* File: be_focus_server_tests/integration/alerts/test_alert_generation_negative.py
* Status: SKIPPED

h3. Note
*This test is currently SKIPPED because alerts are NOT stored in MongoDB.*""",
        "category": "Negative",
        "skip": True
    },
    {
        "test_id": "PZ-15016",
        "summary": "Alert Generation - Invalid Alert ID Format",
        "description": """Verify that alerts with invalid alert ID formats are rejected or handled appropriately.

h3. Test Details
* Test ID: PZ-15016
* Test Type: Integration Test
* Category: Negative
* File: be_focus_server_tests/integration/alerts/test_alert_generation_negative.py

h3. Expected Result
Invalid alert ID formats are rejected or handled appropriately (400/422 status code).""",
        "category": "Negative"
    },
    {
        "test_id": "PZ-15017",
        "summary": "Alert Generation - Duplicate Alert IDs",
        "description": """Verify that duplicate alert IDs are handled appropriately.

h3. Test Details
* Test ID: PZ-15017
* Test Type: Integration Test
* Category: Negative
* File: be_focus_server_tests/integration/alerts/test_alert_generation_negative.py

h3. Expected Result
Duplicate alert IDs are handled appropriately. Note: The system may accept duplicate IDs as separate alert events.""",
        "category": "Negative"
    },
    {
        "test_id": "PZ-15020",
        "summary": "Alert Generation - Boundary DOF Values",
        "description": """Verify that alerts with boundary DOF values (min, max, edge cases) are handled correctly.

h3. Test Details
* Test ID: PZ-15020
* Test Type: Integration Test
* Category: Edge Case
* File: be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py

h3. Expected Result
All boundary DOF values are processed correctly.""",
        "category": "Edge Case"
    },
    {
        "test_id": "PZ-15021",
        "summary": "Alert Generation - Minimum/Maximum Severity",
        "description": """Verify that alerts with minimum (1) and maximum (3) severity are handled correctly.

h3. Test Details
* Test ID: PZ-15021
* Test Type: Integration Test
* Category: Edge Case
* File: be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py

h3. Expected Result
Both minimum and maximum severity values are processed correctly.""",
        "category": "Edge Case"
    },
    {
        "test_id": "PZ-15022",
        "summary": "Alert Generation - Zero Alerts Amount",
        "description": """Verify that alerts with alertsAmount = 0 are handled appropriately.

h3. Test Details
* Test ID: PZ-15022
* Test Type: Integration Test
* Category: Edge Case
* File: be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py

h3. Expected Result
Zero alerts amount is handled appropriately.""",
        "category": "Edge Case"
    },
    {
        "test_id": "PZ-15023",
        "summary": "Alert Generation - Very Large Alert ID",
        "description": """Verify that alerts with very long alert IDs (1000+ characters) are handled correctly.

h3. Test Details
* Test ID: PZ-15023
* Test Type: Integration Test
* Category: Edge Case
* File: be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py

h3. Expected Result
Very large alert IDs are handled appropriately.""",
        "category": "Edge Case"
    },
    {
        "test_id": "PZ-15024",
        "summary": "Alert Generation - Concurrent Alerts with Same DOF",
        "description": """Verify that multiple alerts with the same DOF can be processed concurrently without conflicts.

h3. Test Details
* Test ID: PZ-15024
* Test Type: Integration Test
* Category: Edge Case
* File: be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py

h3. Expected Result
All concurrent alerts with same DOF are processed correctly.""",
        "category": "Edge Case"
    },
    {
        "test_id": "PZ-15025",
        "summary": "Alert Generation - Rapid Sequential Alerts",
        "description": """Verify that rapid sequential alerts are processed correctly without loss or corruption.

h3. Test Details
* Test ID: PZ-15025
* Test Type: Integration Test
* Category: Edge Case
* File: be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py

h3. Expected Result
All rapid sequential alerts are processed correctly.""",
        "category": "Edge Case"
    },
    {
        "test_id": "PZ-15026",
        "summary": "Alert Generation - Alert with Maximum Fields",
        "description": """Verify that alerts with all possible fields set to maximum values are processed correctly.

h3. Test Details
* Test ID: PZ-15026
* Test Type: Integration Test
* Category: Edge Case
* File: be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py

h3. Expected Result
Alert with maximum fields is processed correctly.""",
        "category": "Edge Case"
    },
    {
        "test_id": "PZ-15027",
        "summary": "Alert Generation - Alert with Minimum Fields",
        "description": """Verify that alerts with only required fields (minimum) are processed correctly.

h3. Test Details
* Test ID: PZ-15027
* Test Type: Integration Test
* Category: Edge Case
* File: be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py

h3. Expected Result
Alert with minimum fields is processed correctly.""",
        "category": "Edge Case"
    },
    {
        "test_id": "PZ-15030",
        "summary": "Alert Generation - High Volume Load",
        "description": """Verify that system can handle high volume of alerts (1000+) without degradation or failures.

h3. Test Details
* Test ID: PZ-15030
* Test Type: Integration Test
* Category: Load
* File: be_focus_server_tests/integration/alerts/test_alert_generation_load.py

h3. Expected Result
System handles high volume load successfully. Success rate >= 99%. No system degradation.""",
        "category": "Load"
    },
    {
        "test_id": "PZ-15031",
        "summary": "Alert Generation - Sustained Load",
        "description": """Verify that system can handle sustained load over extended period (10+ minutes) without degradation.

h3. Test Details
* Test ID: PZ-15031
* Test Type: Integration Test
* Category: Load
* File: be_focus_server_tests/integration/alerts/test_alert_generation_load.py

h3. Expected Result
System maintains performance under sustained load. No memory leaks or performance degradation.""",
        "category": "Load"
    },
    {
        "test_id": "PZ-15032",
        "summary": "Alert Generation - Burst Load",
        "description": """Verify that system can handle sudden burst of alerts (500 simultaneous) without failures or degradation.

h3. Test Details
* Test ID: PZ-15032
* Test Type: Integration Test
* Category: Load
* File: be_focus_server_tests/integration/alerts/test_alert_generation_load.py

h3. Expected Result
System handles burst load successfully. All alerts are processed.""",
        "category": "Load"
    },
    {
        "test_id": "PZ-15033",
        "summary": "Alert Generation - Mixed Alert Types Load",
        "description": """Verify that system can handle mixed alert types (SD, SC, different severities) under load without issues.

h3. Test Details
* Test ID: PZ-15033
* Test Type: Integration Test
* Category: Load
* File: be_focus_server_tests/integration/alerts/test_alert_generation_load.py

h3. Expected Result
All alert types are processed correctly under load.""",
        "category": "Load"
    },
    {
        "test_id": "PZ-15034",
        "summary": "Alert Generation - RabbitMQ Queue Capacity",
        "description": """Verify that RabbitMQ queues can handle high volume of alerts without overflow or message loss.

h3. Test Details
* Test ID: PZ-15034
* Test Type: Integration Test
* Category: Load
* File: be_focus_server_tests/integration/alerts/test_alert_generation_load.py

h3. Expected Result
Queue handles capacity correctly. No message loss.""",
        "category": "Load"
    },
    {
        "test_id": "PZ-15035",
        "summary": "Alert Generation - MongoDB Write Load",
        "description": """SKIPPED: Alerts are NOT stored in MongoDB - this test is invalid.

h3. Test Details
* Test ID: PZ-15035
* Test Type: Integration Test
* Category: Load
* File: be_focus_server_tests/integration/alerts/test_alert_generation_load.py
* Status: SKIPPED

h3. Note
*This test is currently SKIPPED because alerts are NOT stored in MongoDB.*""",
        "category": "Load",
        "skip": True
    },
    {
        "test_id": "PZ-15040",
        "summary": "Alert Generation - Response Time",
        "description": """Verify that alert generation response time meets requirements.

h3. Test Details
* Test ID: PZ-15040
* Test Type: Integration Test
* Category: Performance
* File: be_focus_server_tests/integration/alerts/test_alert_generation_performance.py

h3. Requirements
* Mean < 100ms
* P95 < 200ms
* P99 < 500ms

h3. Expected Result
Response time meets requirements.""",
        "category": "Performance"
    },
    {
        "test_id": "PZ-15041",
        "summary": "Alert Generation - Throughput",
        "description": """Verify that alert generation throughput meets requirements.

h3. Test Details
* Test ID: PZ-15041
* Test Type: Integration Test
* Category: Performance
* File: be_focus_server_tests/integration/alerts/test_alert_generation_performance.py

h3. Requirements
* >= 100 alerts/second

h3. Expected Result
Throughput meets requirements.""",
        "category": "Performance"
    },
    {
        "test_id": "PZ-15042",
        "summary": "Alert Generation - Latency",
        "description": """Verify that alert generation latency (time from creation to processing) meets requirements.

h3. Test Details
* Test ID: PZ-15042
* Test Type: Integration Test
* Category: Performance
* File: be_focus_server_tests/integration/alerts/test_alert_generation_performance.py

h3. Requirements
* Mean < 50ms
* P95 < 100ms

h3. Expected Result
Latency meets requirements.""",
        "category": "Performance"
    },
    {
        "test_id": "PZ-15043",
        "summary": "Alert Generation - Resource Usage",
        "description": """Verify that alert generation does not cause excessive resource usage.

h3. Test Details
* Test ID: PZ-15043
* Test Type: Integration Test
* Category: Performance
* File: be_focus_server_tests/integration/alerts/test_alert_generation_performance.py

h3. Requirements
* CPU usage < 80%
* Memory usage increase < 500MB

h3. Expected Result
Resource usage is acceptable.""",
        "category": "Performance"
    },
    {
        "test_id": "PZ-15044",
        "summary": "Alert Generation - End-to-End Performance",
        "description": """Verify end-to-end performance from alert creation to storage.

h3. Test Details
* Test ID: PZ-15044
* Test Type: Integration Test
* Category: Performance
* File: be_focus_server_tests/integration/alerts/test_alert_generation_performance.py

h3. Requirements
* Mean < 200ms
* P95 < 500ms

h3. Expected Result
End-to-end time meets requirements.""",
        "category": "Performance"
    },
    {
        "test_id": "PZ-15045",
        "summary": "Alert Generation - RabbitMQ Performance",
        "description": """Verify RabbitMQ performance in alert processing.

h3. Test Details
* Test ID: PZ-15045
* Test Type: Integration Test
* Category: Performance
* File: be_focus_server_tests/integration/alerts/test_alert_generation_performance.py

h3. Requirements
* Publish time < 10ms
* Consume time < 50ms

h3. Expected Result
RabbitMQ performance meets requirements.""",
        "category": "Performance"
    },
    {
        "test_id": "PZ-15046",
        "summary": "Alert Generation - MongoDB Performance",
        "description": """SKIPPED: Alerts are NOT stored in MongoDB - this test is invalid.

h3. Test Details
* Test ID: PZ-15046
* Test Type: Integration Test
* Category: Performance
* File: be_focus_server_tests/integration/alerts/test_alert_generation_performance.py
* Status: SKIPPED

h3. Note
*This test is currently SKIPPED because alerts are NOT stored in MongoDB.*""",
        "category": "Performance",
        "skip": True
    },
    {
        "test_id": "PZ-15051",
        "summary": "Deep Alert Logs Investigation",
        "description": """Comprehensive investigation of alert logs across all components: Focus Server, Prisma Web App API, RabbitMQ, gRPC Jobs, MongoDB, RabbitMQ Management API.

h3. Test Details
* Test ID: PZ-15051
* Test Type: Integration Test
* Category: Investigation
* File: be_focus_server_tests/integration/alerts/test_deep_alert_logs_investigation.py

h3. Objective
To comprehensively investigate where alert-related logs appear across all components in the Kubernetes environment.""",
        "category": "Investigation"
    }
]


def create_test_tickets():
    """Create Jira tickets for all alert test cases."""
    logger.info("=" * 80)
    logger.info("Creating Jira tickets for Alert Test Cases")
    logger.info("=" * 80)
    
    # Initialize Jira client
    try:
        client = JiraClient()
        logger.info(f"Connected to Jira: {client.base_url}")
        logger.info(f"Project: {client.project_key}")
    except Exception as e:
        logger.error(f"Failed to initialize Jira client: {e}")
        return
    
    # Try different issue types for Test cases
    issue_types_to_try = ["Test", "Test Case", "Task"]
    issue_type = None
    
    # Check which issue type is available
    try:
        project = client.jira.project(client.project_key)
        available_types = [it.name for it in client.jira.issue_types()]
        logger.info(f"Available issue types: {available_types}")
        
        for it in issue_types_to_try:
            if it in available_types:
                issue_type = it
                logger.info(f"Using issue type: {issue_type}")
                break
        
        if not issue_type:
            logger.warning(f"None of {issue_types_to_try} found. Using first available: {available_types[0] if available_types else 'Task'}")
            issue_type = available_types[0] if available_types else "Task"
    except Exception as e:
        logger.warning(f"Could not check issue types: {e}. Using default: Task")
        issue_type = "Task"
    
    created_count = 0
    skipped_count = 0
    failed_count = 0
    created_tickets = []
    
    for test_case in TEST_CASES:
        test_id = test_case["test_id"]
        summary = test_case["summary"]
        description = test_case["description"]
        category = test_case["category"]
        
        # Skip if marked as skip
        if test_case.get("skip"):
            logger.info(f"⏭️  SKIPPING {test_id}: {summary} (test is invalid)")
            skipped_count += 1
            continue
        
        # Check if ticket already exists
        try:
            existing = client.search_issues(f'project = {client.project_key} AND summary ~ "{test_id}"', max_results=1)
            if existing:
                logger.info(f"⏭️  SKIPPING {test_id}: Ticket already exists - {existing[0]['key']}")
                skipped_count += 1
                continue
        except Exception as e:
            logger.warning(f"Could not check for existing ticket {test_id}: {e}")
        
        # Create ticket
        try:
            labels = ["alert", "integration-test", category.lower().replace(" ", "-")]
            if category == "Performance":
                labels.append("performance")
            elif category == "Load":
                labels.append("load-test")
            
            issue = client.create_issue(
                summary=f"{test_id}: {summary}",
                description=description,
                issue_type=issue_type,
                labels=labels,
                priority="Medium"
            )
            
            created_tickets.append({
                "test_id": test_id,
                "key": issue["key"],
                "url": issue["url"]
            })
            
            logger.info(f"✅ CREATED {test_id}: {issue['key']} - {summary}")
            logger.info(f"   URL: {issue['url']}")
            created_count += 1
            
        except Exception as e:
            logger.error(f"❌ FAILED {test_id}: {e}")
            failed_count += 1
    
    # Summary
    logger.info("=" * 80)
    logger.info("SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total test cases: {len(TEST_CASES)}")
    logger.info(f"✅ Created: {created_count}")
    logger.info(f"⏭️  Skipped: {skipped_count}")
    logger.info(f"❌ Failed: {failed_count}")
    
    if created_tickets:
        logger.info("\nCreated tickets:")
        for ticket in created_tickets:
            logger.info(f"  {ticket['test_id']}: {ticket['key']} - {ticket['url']}")
    
    # Close client
    client.close()
    
    logger.info("=" * 80)
    logger.info("Done!")
    logger.info("=" * 80)


if __name__ == "__main__":
    create_test_tickets()

