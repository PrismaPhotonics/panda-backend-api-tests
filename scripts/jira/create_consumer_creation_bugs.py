#!/usr/bin/env python3
"""
Create Jira Bug Tickets for Consumer Creation Issues
====================================================

This script creates bug tickets in Jira for the critical issues found
during consumer creation investigation.

Issues to report:
1. Missing job_id label in K8s Pods
2. Job not saved to MongoDB
3. Consumer Service not identified

Usage:
    python scripts/jira/create_consumer_creation_bugs.py
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira.jira_client import JiraClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_bug_1_missing_job_id_label(client: JiraClient) -> dict:
    """Create bug ticket #1: Missing job_id label in K8s Pods."""
    
    summary = "Missing job_id label in K8s Pods prevents Backend from finding Pods"
    
    description = """During consumer creation investigation, it was discovered that K8s Pods are created without a `job_id` label, preventing the Backend from finding them.

*Environment:*
* Staging
* Kubernetes namespace: panda

*Steps to Reproduce:*
# Send POST /configure request with job configuration
# Backend creates K8s Pods (grpc-job-{job_id}-{suffix}, cleanup-job-{job_id}-{suffix})
# Check Pod labels using: kubectl get pod <pod-name> -o jsonpath='{.metadata.labels}'
# Observe that `job_id` label is missing

*Expected Behavior:*
Pods should have a `job_id` label matching the job ID (e.g., `job_id: 1-3`), allowing Backend to find them using label selectors.

*Actual Behavior:*
Pods are created with only these labels:
* `app: grpc-job-{job_id}`
* `controller-uid: {uuid}`
* `job-name: grpc-job-{job_id}`

The `job_id` label is missing, causing Backend to return "Invalid job_id" when trying to find Pods.

*Impact:*
* Backend cannot find Pods using `job_id` label selector
* `GET /metadata/{job_id}` returns "Invalid job_id"
* Consumer cannot be created
* System is non-functional for job metadata retrieval

*Evidence:*
* Investigation script output shows Pods without `job_id` label
* Backend logs show "Invalid job_id" errors
* Pods exist and are running, but Backend cannot find them

*Root Cause:*
When creating K8s Jobs/Pods in the `/configure` endpoint, the `job_id` label is not added to the Pod metadata.

*Suggested Solution:*
Add `job_id` label when creating K8s Jobs/Pods:

{code:python}
# In Backend code that creates K8s Jobs/Pods
job_metadata = {
    "labels": {
        "app": f"grpc-job-{job_id}",
        "job-name": f"grpc-job-{job_id}",
        "job_id": job_id  # ⬅️ Add this!
    }
}
{code}

*Related Files:*
* Backend: `/configure` endpoint (K8s Job/Pod creation)
* Investigation script: `scripts/investigate_consumer_creation_issue.py`
* Test: `be_focus_server_tests/integration/data_quality/test_consumer_creation_debug.py`
* Documentation: `docs/04_testing/analysis/CONSUMER_CREATION_BUG_REPORT.md`

*Acceptance Criteria:*
* All Pods created for a job have `job_id` label matching the job ID
* Backend can find Pods using `job_id` label selector
* `GET /metadata/{job_id}` works correctly
* Consumer can be created successfully
"""
    
    try:
        issue = client.create_issue(
            summary=summary,
            description=description,
            issue_type="Bug",
            priority="Highest",
            labels=["bug", "critical", "kubernetes", "backend", "consumer-creation"],
            components=["Focus Server", "Backend"],
            custom_fields={
                "customfield_10038": {"value": "QA Cycle"},  # Found by
                "customfield_10179": "Pods should have a `job_id` label matching the job ID, allowing Backend to find them using label selectors.",  # Expected Result
                "customfield_10180": "Pods are created without `job_id` label, causing Backend to return 'Invalid job_id' when trying to find Pods.",  # Actual Results
                "customfield_10123": """1. Send POST /configure request with job configuration
2. Backend creates K8s Pods
3. Check Pod labels using kubectl
4. Observe that `job_id` label is missing"""  # Reproduction Steps
            }
        )
        logger.info(f"✅ Created bug ticket #1: {issue['key']} - {summary}")
        logger.info(f"   URL: {issue.get('url', 'N/A')}")
        return issue
    except Exception as e:
        logger.error(f"❌ Failed to create bug ticket #1: {e}")
        raise


def create_bug_2_job_not_saved_mongodb(client: JiraClient) -> dict:
    """Create bug ticket #2: Job not saved to MongoDB."""
    
    summary = "Job configuration not saved to MongoDB after POST /configure"
    
    description = """During consumer creation investigation, it was discovered that Job configurations are not saved to MongoDB after successful POST /configure requests.

*Environment:*
* Staging
* MongoDB: 10.10.10.108:27017
* Database: prisma

*Steps to Reproduce:*
# Send POST /configure request with job configuration
# Backend responds with 200 OK and job_id
# Check MongoDB for job document
# Query collections: jobs, job, configurations, configs
# Observe that job document is not found

*Expected Behavior:*
After successful POST /configure, the job configuration should be saved to MongoDB in a collection (e.g., `jobs` or `configurations`), allowing Consumer Service to find and process it.

*Actual Behavior:*
Job configuration is not saved to MongoDB. Investigation found only 3 collections in the database:
* `17d07ae1-59b1-40f7-b39b-a44cd8131c3c-unrecognized_recordings`
* `base_paths`
* `17d07ae1-59b1-40f7-b39b-a44cd8131c3c`

No `jobs`, `job`, `configurations`, or `configs` collections exist.

*Impact:*
* Consumer Service cannot find Job in MongoDB
* Consumer cannot be created
* No way to track Job status
* No persistence of Job configuration

*Evidence:*
* Investigation script output shows Job not found in MongoDB
* MongoDB query results show no job-related collections
* Backend logs show successful job creation, but no MongoDB save operation

*Root Cause:*
The `/configure` endpoint creates K8s Pods but does not save the job configuration to MongoDB.

*Suggested Solution:*
Add MongoDB save operation after successful job creation:

{code:python}
# In Backend /configure endpoint
# After creating K8s Jobs/Pods successfully
job_document = {
    "job_id": job_id,
    "config": config_data,
    "status": "created",
    "created_at": datetime.now(),
    "pods": {
        "grpc": grpc_pod_name,
        "cleanup": cleanup_pod_name
    }
}

# Save to MongoDB
db.jobs.insert_one(job_document)  # or db.configurations
{code}

*Related Files:*
* Backend: `/configure` endpoint
* Investigation script: `scripts/investigate_consumer_creation_issue.py`
* Test: `be_focus_server_tests/integration/data_quality/test_consumer_creation_debug.py`
* Documentation: `docs/04_testing/analysis/CONSUMER_CREATION_BUG_REPORT.md`

*Acceptance Criteria:*
* Job configuration is saved to MongoDB after successful POST /configure
* Consumer Service can find Job in MongoDB
* Job document contains all necessary information (job_id, config, status, pods)
* Consumer can be created successfully
"""
    
    try:
        issue = client.create_issue(
            summary=summary,
            description=description,
            issue_type="Bug",
            priority="High",
            labels=["bug", "mongodb", "backend", "consumer-creation", "persistence"],
            components=["Focus Server", "Backend"],
            custom_fields={
                "customfield_10038": {"value": "QA Cycle"},  # Found by
                "customfield_10179": "After successful POST /configure, the job configuration should be saved to MongoDB, allowing Consumer Service to find and process it.",  # Expected Result
                "customfield_10180": "Job configuration is not saved to MongoDB. No job-related collections exist in the database.",  # Actual Results
                "customfield_10123": """1. Send POST /configure request with job configuration
2. Backend responds with 200 OK
3. Check MongoDB for job document
4. Observe that job document is not found"""  # Reproduction Steps
            }
        )
        logger.info(f"✅ Created bug ticket #2: {issue['key']} - {summary}")
        logger.info(f"   URL: {issue.get('url', 'N/A')}")
        return issue
    except Exception as e:
        logger.error(f"❌ Failed to create bug ticket #2: {e}")
        raise


def create_bug_3_consumer_service_not_identified(client: JiraClient) -> dict:
    """Create bug ticket #3: Consumer Service not identified."""
    
    summary = "Consumer Service pods not identified - unclear how Consumer Service finds Pods"
    
    description = """During consumer creation investigation, Consumer Service pods were not identified, and it's unclear how Consumer Service finds and processes Pods.

*Environment:*
* Staging
* Kubernetes namespace: panda

*Steps to Reproduce:*
# Run investigation script: `scripts/investigate_consumer_creation_issue.py`
# Check for Consumer Service pods
# Observe that no Consumer Service pods are found
# Check how Consumer Service is supposed to find Pods

*Expected Behavior:*
Consumer Service should be running and able to find Pods using label selectors or other mechanisms. The investigation should identify Consumer Service pods and their configuration.

*Actual Behavior:*
No Consumer Service pods are found. It's unclear:
* Whether Consumer Service is running
* How Consumer Service finds Pods
* What label selectors Consumer Service uses
* How Consumer Service processes jobs

*Impact:*
* Unclear how Consumer Service works
* Cannot verify Consumer Service functionality
* Cannot debug Consumer creation issues
* System behavior is not fully understood

*Evidence:*
* Investigation script output shows "No Consumer Service pods found"
* No pods matching Consumer Service patterns were identified
* Backend logs don't show Consumer Service activity

*Root Cause:*
Consumer Service may not be running, or it may be named/configured differently than expected. The investigation script may need to be updated to find Consumer Service pods correctly.

*Suggested Solution:*
1. Verify Consumer Service is running
2. Identify Consumer Service pod names/labels
3. Update investigation script to find Consumer Service pods
4. Document how Consumer Service finds and processes Pods

*Related Files:*
* Investigation script: `scripts/investigate_consumer_creation_issue.py`
* Test: `be_focus_server_tests/integration/data_quality/test_consumer_creation_debug.py`
* Documentation: `docs/04_testing/analysis/CONSUMER_CREATION_BUG_REPORT.md`

*Acceptance Criteria:*
* Consumer Service pods are identified
* Consumer Service configuration is documented
* Investigation script can find Consumer Service pods
* Consumer Service functionality is verified
"""
    
    try:
        issue = client.create_issue(
            summary=summary,
            description=description,
            issue_type="Task",
            priority="Medium",
            labels=["investigation", "consumer-service", "documentation"],
            components=["Focus Server", "Backend"],
            custom_fields={
                "customfield_10038": {"value": "QA Cycle"},  # Found by
                "customfield_10179": "Consumer Service should be running and identifiable, with clear documentation on how it finds and processes Pods.",  # Expected Result
                "customfield_10180": "Consumer Service pods are not found, and it's unclear how Consumer Service works.",  # Actual Results
                "customfield_10123": """1. Run investigation script
2. Check for Consumer Service pods
3. Observe that no Consumer Service pods are found"""  # Reproduction Steps
            }
        )
        logger.info(f"✅ Created bug ticket #3: {issue['key']} - {summary}")
        logger.info(f"   URL: {issue.get('url', 'N/A')}")
        return issue
    except Exception as e:
        logger.error(f"❌ Failed to create bug ticket #3: {e}")
        raise


def main():
    """Main function to create all bug tickets."""
    logger.info("=" * 80)
    logger.info("Creating Jira Bug Tickets for Consumer Creation Issues")
    logger.info("=" * 80)
    
    try:
        # Initialize Jira client
        client = JiraClient()
        
        # Create bug tickets
        logger.info("\n1. Creating bug ticket #1: Missing job_id label...")
        bug1 = create_bug_1_missing_job_id_label(client)
        
        logger.info("\n2. Creating bug ticket #2: Job not saved to MongoDB...")
        bug2 = create_bug_2_job_not_saved_mongodb(client)
        
        logger.info("\n3. Creating task ticket #3: Consumer Service not identified...")
        bug3 = create_bug_3_consumer_service_not_identified(client)
        
        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("✅ All tickets created successfully!")
        logger.info("=" * 80)
        logger.info(f"\nBug #1 (Critical): {bug1['key']} - Missing job_id label")
        logger.info(f"Bug #2 (High): {bug2['key']} - Job not saved to MongoDB")
        logger.info(f"Task #3 (Medium): {bug3['key']} - Consumer Service not identified")
        logger.info("\n" + "=" * 80)
        
        # Close client
        client.close()
        
    except Exception as e:
        logger.error(f"❌ Failed to create tickets: {e}")
        raise


if __name__ == "__main__":
    main()

