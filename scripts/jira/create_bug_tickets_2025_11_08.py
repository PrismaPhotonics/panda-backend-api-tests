#!/usr/bin/env python3
"""
Script to create 3 bug tickets in Jira for Focus Server issues discovered on 2025-11-08.

Tickets to create:
1. MongoDB Connection Failure גורם ל-Pod Restarts
2. Error Handling לא ברור ב-/configure Endpoint
3. חוסר Validation של Metadata לפני Configure
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


def create_bug_1_mongodb_connection(client: JiraClient) -> dict:
    """Create bug ticket #1: MongoDB Connection Failure."""
    
    summary = "Focus Server pod restarts due to MongoDB connection failure during initialization"
    
    description = """Focus Server pod fails during startup due to MongoDB connection failure, causing repeated restarts until connection is restored.

*Environment:*
* Kubernetes namespace: panda
* Pod: panda-panda-focus-server-78dbcfd9d9-kjj77
* MongoDB service: mongodb.panda:27017

*Steps to Reproduce:*
# Deploy Focus Server pod
# MongoDB service is not ready or DNS is not available
# Pod tries to initialize FocusManager
# FocusManager tries to connect to MongoDB (line 61 in focus_manager.py)
# Connection fails with DNS resolution error
# Pod crashes and restarts

*Expected Behavior:*
Pod should wait for MongoDB to be available or retry connection with backoff instead of crashing.

*Actual Behavior:*
Pod crashes and restarts repeatedly until MongoDB connection is restored.

*Error Message:*
{code}
pymongo.errors.ServerSelectionTimeoutError: mongodb:27017: [Errno -3] Temporary failure in name resolution
(configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms), 
Timeout: 30s, Topology Description: <TopologyDescription id: 690dacafa411911c09db4a57, 
topology_type: Unknown, servers: [<ServerDescription ('mongodb', 27017) server_type: Unknown, 
rtt: None, error=AutoReconnect('mongodb:27017: [Errno -3] Temporary failure in name resolution 
(configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms)')>]>
{code}

*Impact:*
* Service downtime during pod restarts
* Repeated pod restarts (observed: 4 restarts in 28 hours)
* Increased load on Kubernetes
* Poor reliability

*Evidence:*
* Pod logs show the error clearly
* Pod status: 4 restarts in 28 hours
* Pod is now running for 46 hours (after connection was restored)

*Root Cause:*
FocusManager.__init__() tries to create RecordingMongoMapper immediately without checking if MongoDB is available. If DNS resolution fails or MongoDB service is not ready, the pod crashes.

*Suggested Solutions:*

*Solution 1: Add Init Container* (Recommended)
{code:yaml}
initContainers:
- name: wait-for-mongodb
  image: busybox
  command: ['sh', '-c', 'until nslookup mongodb.panda; do echo waiting for mongodb; sleep 2; done']
{code}

*Solution 2: Add Retry Logic in Code*
{code:python}
# pz/microservices/focus_server/focus_manager.py
import time
from pymongo.errors import ServerSelectionTimeoutError

max_retries = 5
retry_delay = 5
for attempt in range(max_retries):
    try:
        self.mongo_mapper = RecordingMongoMapper(self.storage_path)
        break
    except ServerSelectionTimeoutError as e:
        if attempt < max_retries - 1:
            logger.warning(f"MongoDB connection failed (attempt {{attempt + 1}}/{{max_retries}}): {{e}}")
            time.sleep(retry_delay)
        else:
            logger.error(f"MongoDB connection failed after {{max_retries}} attempts: {{e}}")
            raise
{code}

*Solution 3: Add Readiness Probe* - Pod won't receive traffic until it's ready

*Related Files:*
* {{pz/microservices/focus_server/focus_manager.py:61}}
* {{docs/04_testing/analysis/MONGODB_CONNECTION_RESTARTS_ANALYSIS.md}}

*Acceptance Criteria:*
* Pod doesn't crash when MongoDB is temporarily unavailable
* Pod waits for MongoDB or retries connection with backoff
* No repeated restarts due to MongoDB connection issues
* Readiness probe or init container implemented
"""
    
    try:
        # Extract required fields from description
        # Expected Result
        expected_result = """Pod should wait for MongoDB to be available or retry connection with backoff instead of crashing."""
        
        # Actual Results
        actual_result = """Pod crashes and restarts repeatedly until MongoDB connection is restored."""
        
        # Reproduction Steps
        reproduction_steps = """1. Deploy Focus Server pod
2. MongoDB service is not ready or DNS is not available
3. Pod tries to initialize FocusManager
4. FocusManager tries to connect to MongoDB (line 61 in focus_manager.py)
5. Connection fails with DNS resolution error
6. Pod crashes and restarts"""
        
        issue = client.create_issue(
            summary=summary,
            description=description,
            issue_type="Bug",
            priority="High",
            labels=["infrastructure", "mongodb", "kubernetes", "reliability"],
            components=["Focus Server", "Infrastructure"],
            custom_fields={
                "customfield_10038": {"value": "QA Cycle"},  # Found by (must be dict with value)
                "customfield_10179": expected_result,  # Expected Result
                "customfield_10180": actual_result,  # Actual Results
                "customfield_10123": reproduction_steps  # Reproduction Steps
            }
        )
        logger.info(f"✅ Created bug ticket #1: {issue['key']} - {summary}")
        return issue
    except Exception as e:
        logger.error(f"❌ Failed to create bug ticket #1: {e}")
        raise


def create_bug_2_error_handling(client: JiraClient) -> dict:
    """Create bug ticket #2: Error Handling לא ברור."""
    
    summary = "/configure endpoint returns unclear error when system is waiting for fiber"
    
    description = """When system is in "waiting for fiber" state, /configure endpoint returns 503 Service Unavailable without clear error message, making it difficult for users to understand what went wrong.

*Environment:*
* Endpoint: POST /configure
* System state: "waiting for fiber" (prr=0.0, sw_version="waiting for fiber")

*Steps to Reproduce:*
# System is in "waiting for fiber" state (check via GET /live_metadata)
# Send POST request to /configure endpoint
# Receive 503 Service Unavailable response
# Error message is not clear or user-friendly

*Expected Behavior:*
Return 400 Bad Request with structured error response explaining:
* What went wrong (missing PRR metadata)
* Why it happened (system waiting for fiber)
* What the user should do (wait for fiber connection)

*Actual Behavior:*
Returns 503 Service Unavailable with minimal error information:
{code}
ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr
INFO: "POST /configure HTTP/1.1" 503 Service Unavailable
{code}

*Current Response:*
* Status Code: 503 (Service Unavailable)
* No structured error body
* Error only in logs, not in response

*Desired Response:*
{code:json}
{{
  "error": "Cannot configure job",
  "reason": "Missing required fiber metadata fields: prr",
  "status": "waiting_for_fiber",
  "message": "System is waiting for fiber connection. Please ensure fiber is connected and metadata is available.",
  "details": {{
    "prr": 0.0,
    "sw_version": "waiting for fiber",
    "fiber_description": "waiting for fiber"
  }}
}}
{code}
Status Code: 400 (Bad Request) instead of 503

*Impact:*
* Poor user experience - users don't understand what went wrong
* Difficult to diagnose issues programmatically
* Difficult to handle errors in client applications
* 503 suggests server issue, but it's actually a client/state issue

*Suggested Solution:*
{code:python}
# pz/microservices/focus_server/focus_server.py
@app.post('/configure')
def configure(configuration: Dict):
    # Check metadata before attempting to configure
    if focus_manager.fiber_metadata.prr <= 0 or focus_manager.fiber_metadata.sw_version == "waiting for fiber":
        return ORJSONResponse(
            content={{
                "error": "Cannot configure job",
                "reason": "Missing required fiber metadata fields: prr",
                "status": "waiting_for_fiber",
                "message": "System is waiting for fiber connection. Please ensure fiber is connected and metadata is available.",
                "details": {{
                    "prr": focus_manager.fiber_metadata.prr,
                    "sw_version": focus_manager.fiber_metadata.sw_version,
                    "fiber_description": focus_manager.fiber_metadata.fiber_description
                }}
            }},
            status_code=400  # Bad Request instead of 503
        )
    
    # Continue with normal configuration...
{code}

*Related Files:*
* {{pz/microservices/focus_server/focus_server.py}}
* {{docs/04_testing/analysis/PRR_ERROR_CURRENT_STATUS_2025-11-08.md}}

*Acceptance Criteria:*
* Returns 400 Bad Request (not 503) when metadata is missing
* Returns structured JSON error response
* Error message is clear and actionable
* Error includes relevant metadata details
* Client applications can handle the error programmatically
"""
    
    try:
        # Extract required fields from description
        # Expected Result
        expected_result = """Return 400 Bad Request with structured error response explaining:
* What went wrong (missing PRR metadata)
* Why it happened (system waiting for fiber)
* What the user should do (wait for fiber connection)"""
        
        # Actual Results
        actual_result = """Returns 503 Service Unavailable with minimal error information:
ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr
INFO: "POST /configure HTTP/1.1" 503 Service Unavailable"""
        
        # Reproduction Steps
        reproduction_steps = """1. System is in "waiting for fiber" state (check via GET /live_metadata)
2. Send POST request to /configure endpoint
3. Receive 503 Service Unavailable response
4. Error message is not clear or user-friendly"""
        
        issue = client.create_issue(
            summary=summary,
            description=description,
            issue_type="Bug",
            priority="Medium",
            labels=["api", "error-handling", "ux", "configure-endpoint"],
            components=["Focus Server", "API"],
            custom_fields={
                "customfield_10038": {"value": "QA Cycle"},  # Found by (must be dict with value)
                "customfield_10179": expected_result,  # Expected Result
                "customfield_10180": actual_result,  # Actual Results
                "customfield_10123": reproduction_steps  # Reproduction Steps
            }
        )
        logger.info(f"✅ Created bug ticket #2: {issue['key']} - {summary}")
        return issue
    except Exception as e:
        logger.error(f"❌ Failed to create bug ticket #2: {e}")
        raise


def create_bug_3_validation(client: JiraClient) -> dict:
    """Create bug ticket #3: חוסר Validation של Metadata."""
    
    summary = "/configure endpoint doesn't validate metadata availability before attempting configuration"
    
    description = """/configure endpoint doesn't check if metadata is available before attempting to configure job, causing unnecessary errors and increased server load.

*Environment:*
* Endpoint: POST /configure
* System state: "waiting for fiber" or metadata not initialized

*Steps to Reproduce:*
# System is in "waiting for fiber" state (prr=0.0)
# Send POST request to /configure endpoint
# Server attempts to configure job
# Only then discovers metadata is not available
# Returns error after wasting processing time

*Expected Behavior:*
Check metadata availability before attempting configuration and return clear error immediately if metadata is not available.

*Actual Behavior:*
Attempts configuration first, then returns error after discovering metadata is not available during processing.

*Impact:*
* Unnecessary errors and processing
* Increased server load
* Slower response time
* Poor user experience

*Current Flow:*
# Request received
# Start processing configuration
# Try to use metadata (e.g., focus_manager.prr)
# Discover metadata is missing/invalid
# Return error

*Desired Flow:*
# Request received
# Validate metadata availability immediately
# If metadata not available, return error immediately
# If metadata available, continue with configuration

*Suggested Solution:*
{code:python}
# pz/microservices/focus_server/focus_server.py
@app.post('/configure')
def configure(configuration: Dict):
    # Validate metadata before attempting to configure
    if not hasattr(focus_manager, 'fiber_metadata') or focus_manager.fiber_metadata is None:
        return ORJSONResponse(
            content={{
                "error": "Cannot configure job",
                "reason": "Fiber metadata not available",
                "status": "metadata_unavailable",
                "message": "Fiber metadata is not available. Please wait for the system to initialize."
            }},
            status_code=503  # Service Unavailable - system not ready
        )
    
    if focus_manager.fiber_metadata.prr <= 0:
        return ORJSONResponse(
            content={{
                "error": "Cannot configure job",
                "reason": "Missing required fiber metadata fields: prr",
                "status": "waiting_for_fiber",
                "message": "System is waiting for fiber connection. Please ensure fiber is connected and metadata is available.",
                "details": {{
                    "prr": focus_manager.fiber_metadata.prr,
                    "sw_version": focus_manager.fiber_metadata.sw_version
                }}
            }},
            status_code=400  # Bad Request - invalid state
        )
    
    # Continue with normal configuration...
    # Now we know metadata is available
{code}

*Benefits:*
* Faster error response (fail fast)
* Reduced server load
* Better error messages
* Clearer separation between "system not ready" (503) and "invalid request" (400)

*Related Files:*
* {{pz/microservices/focus_server/focus_server.py}}
* {{pz/microservices/focus_server/focus_manager.py}}
* {{docs/04_testing/analysis/PRR_ERROR_CURRENT_STATUS_2025-11-08.md}}

*Acceptance Criteria:*
* Metadata is validated before attempting configuration
* Error is returned immediately if metadata is not available
* Appropriate HTTP status codes are used (503 for system not ready, 400 for invalid state)
* Error messages are clear and actionable
* Reduced processing time for invalid requests
"""
    
    try:
        # Extract required fields from description
        # Expected Result
        expected_result = """Check metadata availability before attempting configuration and return clear error immediately if metadata is not available."""
        
        # Actual Results
        actual_result = """Attempts configuration first, then returns error after discovering metadata is not available during processing."""
        
        # Reproduction Steps
        reproduction_steps = """1. System is in "waiting for fiber" state (prr=0.0)
2. Send POST request to /configure endpoint
3. Server attempts to configure job
4. Only then discovers metadata is not available
5. Returns error after wasting processing time"""
        
        issue = client.create_issue(
            summary=summary,
            description=description,
            issue_type="Bug",
            priority="Medium",
            labels=["api", "validation", "metadata", "configure-endpoint"],
            components=["Focus Server", "API"],
            custom_fields={
                "customfield_10038": {"value": "QA Cycle"},  # Found by (must be dict with value)
                "customfield_10179": expected_result,  # Expected Result
                "customfield_10180": actual_result,  # Actual Results
                "customfield_10123": reproduction_steps  # Reproduction Steps
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
    logger.info("Creating 3 bug tickets in Jira for Focus Server issues")
    logger.info("Date: 2025-11-08")
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
        logger.info("Creating Bug Ticket #1: MongoDB Connection Failure")
        logger.info("=" * 80)
        issue1 = create_bug_1_mongodb_connection(client)
        issues.append(issue1)
        
        logger.info("\n" + "=" * 80)
        logger.info("Creating Bug Ticket #2: Error Handling לא ברור")
        logger.info("=" * 80)
        issue2 = create_bug_2_error_handling(client)
        issues.append(issue2)
        
        logger.info("\n" + "=" * 80)
        logger.info("Creating Bug Ticket #3: חוסר Validation של Metadata")
        logger.info("=" * 80)
        issue3 = create_bug_3_validation(client)
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

