#!/usr/bin/env python3
"""
Script to create 3 bug tickets in Jira for Alert Validation issues discovered on 2025-11-16.

Tickets to create:
1. Missing Validation on Class ID
2. Missing Validation on DOF Range
3. Missing Validation on Required Fields
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_bug_1_class_id_validation(client: JiraClient) -> dict:
    """Create bug ticket #1: Missing Validation on Class ID."""
    
    summary = "Alert API accepts invalid Class ID values without validation"
    
    description = """The `/prisma-210-1000/api/push-to-rabbit` endpoint accepts any Class ID value without validation, allowing invalid alerts to be processed and sent to RabbitMQ.

*Environment:*
* Endpoint: POST /prisma-210-1000/api/push-to-rabbit
* Environment: Staging
* Test: PZ-15010 (test_invalid_class_id)

*Steps to Reproduce:*
# Send POST request to /prisma-210-1000/api/push-to-rabbit with invalid classId
# Use any of the following invalid values: 0, 1, 100, 105, 999, -1
# Observe that the API returns 201 Created status
# Check RabbitMQ - invalid alerts are sent to the queue

*Example Invalid Payload:*
{code:json}
{{
  "alertsAmount": 1,
  "dofM": 5000,
  "classId": 999,
  "severity": 3,
  "alertIds": ["test-invalid-class-999-1763289559"]
}}
{code}

*Expected Behavior:*
The API should reject any classId that is not 103 (SC - Single Channel) or 104 (SD - Spatial Distribution) with status code 400 Bad Request or 422 Unprocessable Entity.

*Actual Behavior:*
The API accepts all classId values (including 0, 1, 100, 105, 999, -1) and returns 201 Created status, allowing invalid alerts to be processed.

*Test Evidence:*
{code}
2025-11-16 12:39:19 [ WARNING] ⚠️  Class ID 0 was accepted (status 201)
2025-11-16 12:39:19 [ WARNING] ⚠️  Class ID 1 was accepted (status 201)
2025-11-16 12:39:19 [ WARNING] ⚠️  Class ID 100 was accepted (status 201)
2025-11-16 12:39:19 [ WARNING] ⚠️  Class ID 105 was accepted (status 201)
2025-11-16 12:39:19 [ WARNING] ⚠️  Class ID 999 was accepted (status 201)
2025-11-16 12:39:20 [ WARNING] ⚠️  Class ID -1 was accepted (status 201)
{code}

*Impact:*
* Invalid alerts enter the system and are processed
* Data quality issues - alerts with invalid types can cause processing errors downstream
* Potential security risk - no input validation allows malicious or malformed data
* Poor user experience - users may not realize their alerts are invalid until later stages
* Resource waste - invalid alerts consume processing resources unnecessarily

*Root Cause:*
The API endpoint lacks validation logic to check if classId is one of the valid values (103 or 104) before accepting and processing the alert.

*Suggested Solution:*
Add validation layer to check classId before processing:

{code:python}
# Validation rule that should be implemented:
if classId not in [103, 104]:
    return 400, {{
        "error": "Invalid classId",
        "message": "classId must be 103 (SC - Single Channel) or 104 (SD - Spatial Distribution)",
        "received": classId,
        "valid_values": [103, 104]
    }}
{code}

*Recommended Implementation:*
Use Pydantic or JSON Schema for validation:

{code:python}
from pydantic import BaseModel, Field, validator

class AlertPayload(BaseModel):
    alertsAmount: int = Field(ge=1, description="Number of alerts")
    dofM: int = Field(ge=0, le=2222, description="Distance on fiber in meters")
    classId: int = Field(description="Alert type")
    severity: int = Field(description="Severity level")
    alertIds: List[str] = Field(min_items=1, description="List of alert IDs")
    
    @validator('classId')
    def validate_class_id(cls, v):
        if v not in [103, 104]:
            raise ValueError('classId must be 103 (SC) or 104 (SD)')
        return v
{code}

*Related Files:*
* {{be_focus_server_tests/integration/alerts/test_alert_generation_negative.py:test_invalid_class_id}}
* {{docs/04_testing/analysis/ALERTS_VALIDATION_BUGS_ANALYSIS.md}}

*Acceptance Criteria:*
* API rejects classId values other than 103 or 104 with status 400
* Error response includes clear message explaining valid values
* Invalid alerts are not sent to RabbitMQ
* Test PZ-15010 passes (currently fails)
* All invalid classId values tested are rejected
"""
    
    try:
        expected_result = """The API should reject any classId that is not 103 (SC - Single Channel) or 104 (SD - Spatial Distribution) with status code 400 Bad Request or 422 Unprocessable Entity."""
        
        actual_result = """The API accepts all classId values (including 0, 1, 100, 105, 999, -1) and returns 201 Created status, allowing invalid alerts to be processed."""
        
        reproduction_steps = """1. Send POST request to /prisma-210-1000/api/push-to-rabbit with invalid classId
2. Use any of the following invalid values: 0, 1, 100, 105, 999, -1
3. Observe that the API returns 201 Created status
4. Check RabbitMQ - invalid alerts are sent to the queue"""
        
        issue = client.create_issue(
            summary=summary,
            description=description,
            issue_type="Bug",
            priority="High",
            labels=["api", "validation", "alerts", "critical", "security"],
            components=["Focus Server", "API"],
            custom_fields={
                "customfield_10038": {"value": "QA Cycle"},
                "customfield_10179": expected_result,
                "customfield_10180": actual_result,
                "customfield_10123": reproduction_steps
            }
        )
        logger.info(f"✅ Created bug ticket #1: {issue['key']} - {summary}")
        return issue
    except Exception as e:
        logger.error(f"❌ Failed to create bug ticket #1: {e}")
        raise


def create_bug_2_dof_validation(client: JiraClient) -> dict:
    """Create bug ticket #2: Missing Validation on DOF Range."""
    
    summary = "Alert API accepts negative DOF (Distance on Fiber) values without validation"
    
    description = """The `/prisma-210-1000/api/push-to-rabbit` endpoint accepts negative DOF (Distance on Fiber) values without validation, allowing alerts with invalid locations to be processed.

*Environment:*
* Endpoint: POST /prisma-210-1000/api/push-to-rabbit
* Environment: Staging
* Test: PZ-15012 (test_invalid_dof_range)
* Valid DOF Range: 0-2222 meters (per production client configuration)

*Steps to Reproduce:*
# Send POST request to /prisma-210-1000/api/push-to-rabbit with negative dofM value
# Use any negative value: -1, -100, -5000
# Observe that the API returns 201 Created status
# Check RabbitMQ - alerts with invalid DOF are sent to the queue

*Example Invalid Payload:*
{code:json}
{{
  "alertsAmount": 1,
  "dofM": -100,
  "classId": 104,
  "severity": 3,
  "alertIds": ["test-invalid-dof--100-1763289560"]
}}
{code}

*Expected Behavior:*
The API should reject any dofM value that is:
* Negative (< 0)
* Greater than the maximum allowed (2222 meters)

With status code 400 Bad Request and a clear error message.

*Actual Behavior:*
The API accepts negative dofM values (e.g., -1, -100) and returns 201 Created status, allowing alerts with invalid locations to be processed.

*Test Evidence:*
{code}
2025-11-16 12:39:20 [ WARNING] ⚠️  DOF -1 was accepted (status 201)
2025-11-16 12:39:20 [ WARNING] ⚠️  DOF -100 was accepted (status 201)
{code}

*Impact:*
* Invalid alert locations enter the system
* Alerts with negative DOF cannot be displayed correctly on maps
* Data integrity issues - alerts may appear in wrong locations or fail to display
* Potential downstream processing errors when systems try to process invalid locations
* Poor user experience - users may see alerts in impossible locations

*Root Cause:*
The API endpoint lacks validation logic to check if dofM is within the valid range (0-2222 meters) before accepting and processing the alert.

*Configuration Reference:*
According to production client configuration:
* SensorsRange (Max Channels): 2222
* Valid DOF Range: 0-2222 meters

*Suggested Solution:*
Add validation layer to check dofM range before processing:

{code:python}
# Validation rule that should be implemented:
if dofM < 0 or dofM > 2222:
    return 400, {{
        "error": "Invalid dofM",
        "message": "dofM must be between 0 and 2222 meters",
        "received": dofM,
        "valid_range": {{"min": 0, "max": 2222}}
    }}
{code}

*Recommended Implementation:*
Use Pydantic for validation:

{code:python}
from pydantic import BaseModel, Field

class AlertPayload(BaseModel):
    alertsAmount: int = Field(ge=1, description="Number of alerts")
    dofM: int = Field(ge=0, le=2222, description="Distance on fiber in meters")
    classId: int = Field(description="Alert type")
    severity: int = Field(description="Severity level")
    alertIds: List[str] = Field(min_items=1, description="List of alert IDs")
{code}

*Related Files:*
* {{be_focus_server_tests/integration/alerts/test_alert_generation_negative.py:test_invalid_dof_range}}
* {{docs/04_testing/analysis/ALERTS_VALIDATION_BUGS_ANALYSIS.md}}
* {{config/usersettings.new_production_client.json}}

*Acceptance Criteria:*
* API rejects dofM values < 0 with status 400
* API rejects dofM values > 2222 with status 400
* Error response includes clear message explaining valid range
* Invalid alerts are not sent to RabbitMQ
* Test PZ-15012 passes (currently fails)
* All invalid dofM values tested are rejected
"""
    
    try:
        expected_result = """The API should reject any dofM value that is negative (< 0) or greater than the maximum allowed (2222 meters) with status code 400 Bad Request and a clear error message."""
        
        actual_result = """The API accepts negative dofM values (e.g., -1, -100) and returns 201 Created status, allowing alerts with invalid locations to be processed."""
        
        reproduction_steps = """1. Send POST request to /prisma-210-1000/api/push-to-rabbit with negative dofM value
2. Use any negative value: -1, -100, -5000
3. Observe that the API returns 201 Created status
4. Check RabbitMQ - alerts with invalid DOF are sent to the queue"""
        
        issue = client.create_issue(
            summary=summary,
            description=description,
            issue_type="Bug",
            priority="High",
            labels=["api", "validation", "alerts", "critical", "data-integrity"],
            components=["Focus Server", "API"],
            custom_fields={
                "customfield_10038": {"value": "QA Cycle"},
                "customfield_10179": expected_result,
                "customfield_10180": actual_result,
                "customfield_10123": reproduction_steps
            }
        )
        logger.info(f"✅ Created bug ticket #2: {issue['key']} - {summary}")
        return issue
    except Exception as e:
        logger.error(f"❌ Failed to create bug ticket #2: {e}")
        raise


def create_bug_3_required_fields_validation(client: JiraClient) -> dict:
    """Create bug ticket #3: Missing Validation on Required Fields."""
    
    summary = "Alert API accepts requests with missing required fields without validation"
    
    description = """The `/prisma-210-1000/api/push-to-rabbit` endpoint accepts requests with missing required fields without validation, allowing incomplete alerts to be processed.

*Environment:*
* Endpoint: POST /prisma-210-1000/api/push-to-rabbit
* Environment: Staging
* Test: PZ-15013 (test_missing_required_fields)
* Required Fields: alertsAmount, dofM, classId, severity, alertIds

*Steps to Reproduce:*
# Send POST request to /prisma-210-1000/api/push-to-rabbit with missing required field
# Remove one of the required fields: alertsAmount, dofM, classId, severity, or alertIds
# Observe that the API returns 201 Created status
# Check RabbitMQ - incomplete alerts are sent to the queue

*Example Invalid Payloads:*
{code:json}
// Missing alertsAmount
{{
  "dofM": 5000,
  "classId": 104,
  "severity": 3,
  "alertIds": ["test-no-amount-1763289560"]
}}

// Missing dofM
{{
  "alertsAmount": 1,
  "classId": 104,
  "severity": 3,
  "alertIds": ["test-no-dof-1763289560"]
}}

// Missing classId
{{
  "alertsAmount": 1,
  "dofM": 5000,
  "severity": 3,
  "alertIds": ["test-no-class-1763289560"]
}}

// Missing severity
{{
  "alertsAmount": 1,
  "dofM": 5000,
  "classId": 104,
  "alertIds": ["test-no-severity-1763289560"]
}}

// Missing alertIds
{{
  "alertsAmount": 1,
  "dofM": 5000,
  "classId": 104,
  "severity": 3
}}
{code}

*Expected Behavior:*
The API should reject any request missing required fields with status code 400 Bad Request and a clear error message indicating which field(s) are missing.

*Actual Behavior:*
The API accepts requests with missing required fields and returns 201 Created status, allowing incomplete alerts to be processed.

*Test Evidence:*
{code}
2025-11-16 12:39:21 [ WARNING] ⚠️  Missing alertsAmount was accepted (status 201)
2025-11-16 12:39:21 [ WARNING] ⚠️  Missing dofM was accepted (status 201)
2025-11-16 12:39:21 [ WARNING] ⚠️  Missing classId was accepted (status 201)
2025-11-16 12:39:21 [ WARNING] ⚠️  Missing severity was accepted (status 201)
2025-11-16 12:39:21 [ WARNING] ⚠️  Missing alertIds was accepted (status 201)
{code}

*Impact:*
* Incomplete alerts enter the system and may cause processing errors
* Data integrity issues - alerts missing critical information cannot be properly processed
* Potential null pointer exceptions or errors in downstream systems
* Poor user experience - alerts may fail to display or process correctly
* Resource waste - incomplete alerts consume processing resources unnecessarily
* Difficult to debug - errors may occur later in the pipeline, making it hard to trace back to the source

*Root Cause:*
The API endpoint lacks validation logic to check if all required fields are present before accepting and processing the alert.

*Required Fields:*
* alertsAmount (int) - Number of alerts
* dofM (int) - Distance on fiber in meters
* classId (int) - Alert type (103 for SC, 104 for SD)
* severity (int) - Severity level (1, 2, or 3)
* alertIds (array) - List of alert IDs

*Suggested Solution:*
Add validation layer to check required fields before processing:

{code:python}
# Validation rule that should be implemented:
required_fields = ["alertsAmount", "dofM", "classId", "severity", "alertIds"]
missing_fields = [field for field in required_fields if field not in payload]

if missing_fields:
    return 400, {{
        "error": "Missing required fields",
        "message": f"The following required fields are missing: {', '.join(missing_fields)}",
        "missing_fields": missing_fields,
        "required_fields": required_fields
    }}

# Also check if alertIds is empty array
if not payload.get("alertIds") or len(payload["alertIds"]) == 0:
    return 400, {{
        "error": "Invalid alertIds",
        "message": "alertIds must contain at least one ID"
    }}
{code}

*Recommended Implementation:*
Use Pydantic for automatic validation:

{code:python}
from pydantic import BaseModel, Field

class AlertPayload(BaseModel):
    alertsAmount: int = Field(..., ge=1, description="Number of alerts")
    dofM: int = Field(..., ge=0, le=2222, description="Distance on fiber in meters")
    classId: int = Field(..., description="Alert type")
    severity: int = Field(..., description="Severity level")
    alertIds: List[str] = Field(..., min_items=1, description="List of alert IDs")
    
    # Field(...) means the field is required
{code}

*Related Files:*
* {{be_focus_server_tests/integration/alerts/test_alert_generation_negative.py:test_missing_required_fields}}
* {{docs/04_testing/analysis/ALERTS_VALIDATION_BUGS_ANALYSIS.md}}

*Acceptance Criteria:*
* API rejects requests missing any required field with status 400
* Error response includes clear message listing missing fields
* Invalid alerts are not sent to RabbitMQ
* Test PZ-15013 passes (currently fails)
* All missing field scenarios tested are rejected
* Empty alertIds array is also rejected
"""
    
    try:
        expected_result = """The API should reject any request missing required fields with status code 400 Bad Request and a clear error message indicating which field(s) are missing."""
        
        actual_result = """The API accepts requests with missing required fields and returns 201 Created status, allowing incomplete alerts to be processed."""
        
        reproduction_steps = """1. Send POST request to /prisma-210-1000/api/push-to-rabbit with missing required field
2. Remove one of the required fields: alertsAmount, dofM, classId, severity, or alertIds
3. Observe that the API returns 201 Created status
4. Check RabbitMQ - incomplete alerts are sent to the queue"""
        
        issue = client.create_issue(
            summary=summary,
            description=description,
            issue_type="Bug",
            priority="High",
            labels=["api", "validation", "alerts", "critical", "data-integrity"],
            components=["Focus Server", "API"],
            custom_fields={
                "customfield_10038": {"value": "QA Cycle"},
                "customfield_10179": expected_result,
                "customfield_10180": actual_result,
                "customfield_10123": reproduction_steps
            }
        )
        logger.info(f"✅ Created bug ticket #3: {issue['key']} - {summary}")
        return issue
    except Exception as e:
        logger.error(f"❌ Failed to create bug ticket #3: {e}")
        raise


def main():
    """Main function to create all 3 bug tickets."""
    
    logger.info("=" * 80)
    logger.info("Creating 3 bug tickets in Jira for Alert Validation issues")
    logger.info("Date: 2025-11-16")
    logger.info("=" * 80)
    
    try:
        # Initialize Jira client
        logger.info("Initializing Jira client...")
        client = JiraClient()
        logger.info(f"✅ Connected to Jira: {client.base_url}")
        logger.info(f"✅ Project: {client.project_key}")
        
        # Create all 3 bug tickets
        issues = []
        
        logger.info("\n" + "=" * 80)
        logger.info("Creating Bug Ticket #1: Missing Validation on Class ID")
        logger.info("=" * 80)
        issue1 = create_bug_1_class_id_validation(client)
        issues.append(issue1)
        
        logger.info("\n" + "=" * 80)
        logger.info("Creating Bug Ticket #2: Missing Validation on DOF Range")
        logger.info("=" * 80)
        issue2 = create_bug_2_dof_validation(client)
        issues.append(issue2)
        
        logger.info("\n" + "=" * 80)
        logger.info("Creating Bug Ticket #3: Missing Validation on Required Fields")
        logger.info("=" * 80)
        issue3 = create_bug_3_required_fields_validation(client)
        issues.append(issue3)
        
        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("✅ SUCCESS: All 3 bug tickets created successfully!")
        logger.info("=" * 80)
        logger.info("\nCreated tickets:")
        for i, issue in enumerate(issues, 1):
            logger.info(f"  {i}. {issue['key']}: {issue['summary']}")
            logger.info(f"     URL: {issue['url']}")
        
        logger.info("\n" + "=" * 80)
        logger.info("Summary:")
        logger.info(f"  Total tickets created: {len(issues)}")
        logger.info(f"  Project: {client.project_key}")
        logger.info(f"  Board: https://prismaphotonics.atlassian.net/jira/software/c/projects/PZ/boards/21")
        logger.info("=" * 80)
        
        return issues
        
    except Exception as e:
        logger.error(f"\n❌ FAILED: Error creating bug tickets: {e}")
        logger.exception(e)
        sys.exit(1)
    finally:
        # Close client connection
        try:
            client.close()
            logger.info("Closed Jira client connection")
        except:
            pass


if __name__ == "__main__":
    main()

