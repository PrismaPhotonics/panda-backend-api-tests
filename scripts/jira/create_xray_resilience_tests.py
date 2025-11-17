"""
Create Xray Tests for Kubernetes Pod Resilience
================================================

This script creates all 30 Kubernetes Pod Resilience tests in Jira Xray Test Repository.

Usage:
    python scripts/jira/create_xray_resilience_tests.py
    python scripts/jira/create_xray_resilience_tests.py --dry-run
    python scripts/jira/create_xray_resilience_tests.py --folder-id 68d91b9f681e183ea2e83e16
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

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


# Test definitions
RESILIENCE_TESTS = {
    # MongoDB Pod Resilience (6 tests)
    "PZ-TBD-001": {
        "summary": "MongoDB Pod Deletion and Recreation",
        "description": """## Objective
Validate that when MongoDB pod is deleted, Kubernetes automatically recreates it and the system recovers.

## Test Type
Integration Test

## Priority
P0 - Critical

## Components/Labels
mongodb, kubernetes, resilience, infrastructure, pod-lifecycle

## Pre-Conditions
- Kubernetes cluster is accessible
- MongoDB deployment exists in namespace 'panda'
- MongoDB is accessible and functioning

## Test Steps
1. Get current MongoDB pod name
2. Verify MongoDB is accessible
3. Delete MongoDB pod
4. Wait for pod deletion
5. Wait for new pod to be created
6. Wait for new pod to be ready
7. Verify MongoDB connection restored
8. Verify system functionality restored

## Expected Result
- Pod deleted successfully
- New pod created automatically within 60 seconds
- New pod becomes ready within 120 seconds
- MongoDB connection restored
- System functionality restored

## Automation Status
✅ Automated

**Test Function:** `test_mongodb_pod_deletion_recreation`  
**Test File:** `tests/infrastructure/resilience/test_mongodb_pod_resilience.py`  
**Test Class:** `TestMongoDBPodResilience`

## Execution Command
```bash
pytest tests/infrastructure/resilience/test_mongodb_pod_resilience.py::TestMongoDBPodResilience::test_mongodb_pod_deletion_recreation -v
```

## Related Issues
- PZ-13756 (Infrastructure Resilience)
""",
        "priority": "Highest",
        "labels": ["mongodb", "kubernetes", "resilience", "infrastructure", "pod-lifecycle"],
        "components": ["mongodb", "kubernetes", "resilience"]
    },
    "PZ-TBD-002": {
        "summary": "MongoDB Scale Down to 0 Replicas",
        "description": """## Objective
Validate that when MongoDB is scaled down to 0, the system handles the outage gracefully and recovers after scale up.

## Test Type
Integration Test

## Priority
P0 - Critical

## Components/Labels
mongodb, kubernetes, resilience, infrastructure, scaling

## Pre-Conditions
- Kubernetes cluster is accessible
- MongoDB deployment exists in namespace 'panda'
- MongoDB is accessible and functioning

## Test Steps
1. Verify MongoDB is accessible
2. Scale MongoDB deployment to 0
3. Wait for pods to terminate
4. Verify MongoDB is unreachable
5. Attempt job creation (should fail gracefully)
6. Scale MongoDB back to 1
7. Wait for pod to be ready
8. Verify MongoDB connection restored
9. Verify system functionality restored

## Expected Result
- MongoDB scaled down successfully
- MongoDB unreachable after scale down
- Job creation returns 503 or appropriate error
- No system crashes
- MongoDB restored after scale up

## Automation Status
✅ Automated

**Test Function:** `test_mongodb_scale_down_to_zero`  
**Test File:** `tests/infrastructure/resilience/test_mongodb_pod_resilience.py`  
**Test Class:** `TestMongoDBPodResilience`
""",
        "priority": "Highest",
        "labels": ["mongodb", "kubernetes", "resilience", "infrastructure", "scaling"],
        "components": ["mongodb", "kubernetes", "resilience"]
    },
    "PZ-TBD-003": {
        "summary": "MongoDB Pod Restart During Job Creation",
        "description": """## Objective
Validate that when MongoDB pod restarts during job creation, the operation is handled gracefully.

## Test Type
Integration Test

## Priority
P1 - High

## Components/Labels
mongodb, kubernetes, resilience, infrastructure, pod-restart

## Expected Result
- Pod restart handled gracefully
- Job creation either succeeds or fails with clear error
- No crashes or undefined behavior
- System recovers after restart

## Automation Status
✅ Automated

**Test Function:** `test_mongodb_pod_restart_during_job_creation`  
**Test File:** `tests/infrastructure/resilience/test_mongodb_pod_resilience.py`
""",
        "priority": "High",
        "labels": ["mongodb", "kubernetes", "resilience", "pod-restart"],
        "components": ["mongodb", "kubernetes"]
    },
    "PZ-TBD-004": {
        "summary": "MongoDB Outage Graceful Degradation",
        "description": """## Objective
Validate that when MongoDB is down, the system handles outage gracefully with appropriate errors.

## Test Type
Integration Test

## Priority
P0 - Critical

## Components/Labels
mongodb, kubernetes, resilience, graceful-degradation

## Expected Result
- All operations fail gracefully with 503 or appropriate errors
- No crashes or undefined behavior
- Error messages indicate MongoDB unavailability

## Automation Status
✅ Automated

**Test Function:** `test_mongodb_outage_graceful_degradation`  
**Test File:** `tests/infrastructure/resilience/test_mongodb_pod_resilience.py`
""",
        "priority": "Highest",
        "labels": ["mongodb", "kubernetes", "resilience", "graceful-degradation"],
        "components": ["mongodb", "kubernetes"]
    },
    "PZ-TBD-005": {
        "summary": "MongoDB Recovery After Outage",
        "description": """## Objective
Validate that after MongoDB outage, the system recovers automatically.

## Test Type
Integration Test

## Priority
P0 - Critical

## Components/Labels
mongodb, kubernetes, resilience, recovery

## Expected Result
- MongoDB recovers within reasonable time
- Connection restored
- Functionality restored
- No data loss

## Automation Status
✅ Automated

**Test Function:** `test_mongodb_recovery_after_outage`  
**Test File:** `tests/infrastructure/resilience/test_mongodb_pod_resilience.py`
""",
        "priority": "Highest",
        "labels": ["mongodb", "kubernetes", "resilience", "recovery"],
        "components": ["mongodb", "kubernetes"]
    },
    "PZ-TBD-006": {
        "summary": "MongoDB Pod Status Monitoring",
        "description": """## Objective
Validate pod status monitoring capabilities.

## Test Type
Integration Test

## Priority
P2 - Medium

## Components/Labels
mongodb, kubernetes, monitoring

## Automation Status
✅ Automated

**Test Function:** `test_mongodb_pod_status_monitoring`  
**Test File:** `tests/infrastructure/resilience/test_mongodb_pod_resilience.py`
""",
        "priority": "Medium",
        "labels": ["mongodb", "kubernetes", "monitoring"],
        "components": ["mongodb", "kubernetes"]
    },
    # RabbitMQ Pod Resilience (6 tests)
    "PZ-TBD-007": {
        "summary": "RabbitMQ Pod Deletion and Recreation",
        "description": """## Objective
Validate that when RabbitMQ pod is deleted, Kubernetes automatically recreates it (StatefulSet).

## Test Type
Integration Test

## Priority
P0 - Critical

## Components/Labels
rabbitmq, kubernetes, resilience, infrastructure, pod-lifecycle

## Automation Status
✅ Automated

**Test Function:** `test_rabbitmq_pod_deletion_recreation`  
**Test File:** `tests/infrastructure/resilience/test_rabbitmq_pod_resilience.py`
""",
        "priority": "Highest",
        "labels": ["rabbitmq", "kubernetes", "resilience", "infrastructure"],
        "components": ["rabbitmq", "kubernetes"]
    },
    "PZ-TBD-008": {
        "summary": "RabbitMQ Scale Down to 0 Replicas",
        "description": """## Objective
Validate that when RabbitMQ is scaled down to 0, the system handles the outage gracefully.

## Test Type
Integration Test

## Priority
P0 - Critical

## Components/Labels
rabbitmq, kubernetes, resilience, scaling

## Automation Status
✅ Automated

**Test Function:** `test_rabbitmq_scale_down_to_zero`  
**Test File:** `tests/infrastructure/resilience/test_rabbitmq_pod_resilience.py`
""",
        "priority": "Highest",
        "labels": ["rabbitmq", "kubernetes", "resilience", "scaling"],
        "components": ["rabbitmq", "kubernetes"]
    },
    "PZ-TBD-009": {
        "summary": "RabbitMQ Pod Restart During Operations",
        "description": """## Objective
Validate that when RabbitMQ pod restarts during operations, the system handles it gracefully.

## Test Type
Integration Test

## Priority
P1 - High

## Components/Labels
rabbitmq, kubernetes, resilience, pod-restart

## Automation Status
✅ Automated

**Test Function:** `test_rabbitmq_pod_restart_during_operations`  
**Test File:** `tests/infrastructure/resilience/test_rabbitmq_pod_resilience.py`
""",
        "priority": "High",
        "labels": ["rabbitmq", "kubernetes", "resilience"],
        "components": ["rabbitmq", "kubernetes"]
    },
    "PZ-TBD-010": {
        "summary": "RabbitMQ Outage Graceful Degradation",
        "description": """## Objective
Validate that when RabbitMQ is down, the system handles outage gracefully.

## Test Type
Integration Test

## Priority
P0 - Critical

## Components/Labels
rabbitmq, kubernetes, resilience, graceful-degradation

## Automation Status
✅ Automated

**Test Function:** `test_rabbitmq_outage_graceful_degradation`  
**Test File:** `tests/infrastructure/resilience/test_rabbitmq_pod_resilience.py`
""",
        "priority": "Highest",
        "labels": ["rabbitmq", "kubernetes", "resilience"],
        "components": ["rabbitmq", "kubernetes"]
    },
    "PZ-TBD-011": {
        "summary": "RabbitMQ Recovery After Outage",
        "description": """## Objective
Validate that after RabbitMQ outage, the system recovers automatically.

## Test Type
Integration Test

## Priority
P0 - Critical

## Components/Labels
rabbitmq, kubernetes, resilience, recovery

## Automation Status
✅ Automated

**Test Function:** `test_rabbitmq_recovery_after_outage`  
**Test File:** `tests/infrastructure/resilience/test_rabbitmq_pod_resilience.py`
""",
        "priority": "Highest",
        "labels": ["rabbitmq", "kubernetes", "resilience"],
        "components": ["rabbitmq", "kubernetes"]
    },
    "PZ-TBD-012": {
        "summary": "RabbitMQ Pod Status Monitoring",
        "description": """## Objective
Validate pod status monitoring capabilities.

## Test Type
Integration Test

## Priority
P2 - Medium

## Components/Labels
rabbitmq, kubernetes, monitoring

## Automation Status
✅ Automated

**Test Function:** `test_rabbitmq_pod_status_monitoring`  
**Test File:** `tests/infrastructure/resilience/test_rabbitmq_pod_resilience.py`
""",
        "priority": "Medium",
        "labels": ["rabbitmq", "kubernetes", "monitoring"],
        "components": ["rabbitmq", "kubernetes"]
    },
    # Focus Server Pod Resilience (6 tests)
    "PZ-TBD-013": {
        "summary": "Focus Server Pod Deletion and Recreation",
        "description": """## Objective
Validate that when Focus Server pod is deleted, Kubernetes automatically recreates it.

## Test Type
Integration Test

## Priority
P0 - Critical

## Components/Labels
focus-server, kubernetes, resilience, infrastructure, pod-lifecycle

## Automation Status
✅ Automated

**Test Function:** `test_focus_server_pod_deletion_recreation`  
**Test File:** `tests/infrastructure/resilience/test_focus_server_pod_resilience.py`
""",
        "priority": "Highest",
        "labels": ["focus-server", "kubernetes", "resilience", "infrastructure"],
        "components": ["focus-server", "kubernetes"]
    },
    "PZ-TBD-014": {
        "summary": "Focus Server Scale Down to 0 Replicas",
        "description": """## Objective
Validate that when Focus Server is scaled down to 0, the system handles the outage gracefully.

## Test Type
Integration Test

## Priority
P0 - Critical

## Components/Labels
focus-server, kubernetes, resilience, scaling

## Automation Status
✅ Automated

**Test Function:** `test_focus_server_scale_down_to_zero`  
**Test File:** `tests/infrastructure/resilience/test_focus_server_pod_resilience.py`
""",
        "priority": "Highest",
        "labels": ["focus-server", "kubernetes", "resilience"],
        "components": ["focus-server", "kubernetes"]
    },
    "PZ-TBD-015": {
        "summary": "Focus Server Pod Restart During Job Creation",
        "description": """## Objective
Validate that when Focus Server pod restarts during job creation, the operation is handled gracefully.

## Test Type
Integration Test

## Priority
P1 - High

## Components/Labels
focus-server, kubernetes, resilience, pod-restart

## Automation Status
✅ Automated

**Test Function:** `test_focus_server_pod_restart_during_job_creation`  
**Test File:** `tests/infrastructure/resilience/test_focus_server_pod_resilience.py`
""",
        "priority": "High",
        "labels": ["focus-server", "kubernetes", "resilience"],
        "components": ["focus-server", "kubernetes"]
    },
    "PZ-TBD-016": {
        "summary": "Focus Server Outage Graceful Degradation",
        "description": """## Objective
Validate that when Focus Server is down, the system handles outage gracefully.

## Test Type
Integration Test

## Priority
P0 - Critical

## Components/Labels
focus-server, kubernetes, resilience, graceful-degradation

## Automation Status
✅ Automated

**Test Function:** `test_focus_server_outage_graceful_degradation`  
**Test File:** `tests/infrastructure/resilience/test_focus_server_pod_resilience.py`
""",
        "priority": "Highest",
        "labels": ["focus-server", "kubernetes", "resilience"],
        "components": ["focus-server", "kubernetes"]
    },
    "PZ-TBD-017": {
        "summary": "Focus Server Recovery After Outage",
        "description": """## Objective
Validate that after Focus Server outage, the system recovers automatically.

## Test Type
Integration Test

## Priority
P0 - Critical

## Components/Labels
focus-server, kubernetes, resilience, recovery

## Automation Status
✅ Automated

**Test Function:** `test_focus_server_recovery_after_outage`  
**Test File:** `tests/infrastructure/resilience/test_focus_server_pod_resilience.py`
""",
        "priority": "Highest",
        "labels": ["focus-server", "kubernetes", "resilience"],
        "components": ["focus-server", "kubernetes"]
    },
    "PZ-TBD-018": {
        "summary": "Focus Server Pod Status Monitoring",
        "description": """## Objective
Validate pod status monitoring capabilities.

## Test Type
Integration Test

## Priority
P2 - Medium

## Components/Labels
focus-server, kubernetes, monitoring

## Automation Status
✅ Automated

**Test Function:** `test_focus_server_pod_status_monitoring`  
**Test File:** `tests/infrastructure/resilience/test_focus_server_pod_resilience.py`
""",
        "priority": "Medium",
        "labels": ["focus-server", "kubernetes", "monitoring"],
        "components": ["focus-server", "kubernetes"]
    },
    # SEGY Recorder Pod Resilience (5 tests)
    "PZ-TBD-019": {
        "summary": "SEGY Recorder Pod Deletion and Recreation",
        "description": """## Objective
Validate that when SEGY Recorder pod is deleted, Kubernetes automatically recreates it.

## Test Type
Integration Test

## Priority
P1 - High

## Components/Labels
segy-recorder, kubernetes, resilience, infrastructure, pod-lifecycle

## Automation Status
✅ Automated

**Test Function:** `test_segy_recorder_pod_deletion_recreation`  
**Test File:** `tests/infrastructure/resilience/test_segy_recorder_pod_resilience.py`
""",
        "priority": "High",
        "labels": ["segy-recorder", "kubernetes", "resilience"],
        "components": ["segy-recorder", "kubernetes"]
    },
    "PZ-TBD-020": {
        "summary": "SEGY Recorder Scale Down to 0 Replicas",
        "description": """## Objective
Validate that when SEGY Recorder is scaled down to 0, recording stops gracefully.

## Test Type
Integration Test

## Priority
P1 - High

## Components/Labels
segy-recorder, kubernetes, resilience, scaling

## Automation Status
✅ Automated

**Test Function:** `test_segy_recorder_scale_down_to_zero`  
**Test File:** `tests/infrastructure/resilience/test_segy_recorder_pod_resilience.py`
""",
        "priority": "High",
        "labels": ["segy-recorder", "kubernetes", "resilience"],
        "components": ["segy-recorder", "kubernetes"]
    },
    "PZ-TBD-021": {
        "summary": "SEGY Recorder Pod Restart During Recording",
        "description": """## Objective
Validate that when SEGY Recorder pod restarts during recording, the system handles it gracefully.

## Test Type
Integration Test

## Priority
P2 - Medium

## Components/Labels
segy-recorder, kubernetes, resilience, pod-restart

## Automation Status
✅ Automated

**Test Function:** `test_segy_recorder_pod_restart_during_recording`  
**Test File:** `tests/infrastructure/resilience/test_segy_recorder_pod_resilience.py`
""",
        "priority": "Medium",
        "labels": ["segy-recorder", "kubernetes", "resilience"],
        "components": ["segy-recorder", "kubernetes"]
    },
    "PZ-TBD-022": {
        "summary": "SEGY Recorder Outage Behavior",
        "description": """## Objective
Validate that when SEGY Recorder is down, recording stops gracefully.

## Test Type
Integration Test

## Priority
P2 - Medium

## Components/Labels
segy-recorder, kubernetes, resilience

## Automation Status
✅ Automated

**Test Function:** `test_segy_recorder_outage_behavior`  
**Test File:** `tests/infrastructure/resilience/test_segy_recorder_pod_resilience.py`
""",
        "priority": "Medium",
        "labels": ["segy-recorder", "kubernetes", "resilience"],
        "components": ["segy-recorder", "kubernetes"]
    },
    "PZ-TBD-023": {
        "summary": "SEGY Recorder Recovery After Outage",
        "description": """## Objective
Validate that after SEGY Recorder outage, the system recovers automatically.

## Test Type
Integration Test

## Priority
P1 - High

## Components/Labels
segy-recorder, kubernetes, resilience, recovery

## Automation Status
✅ Automated

**Test Function:** `test_segy_recorder_recovery_after_outage`  
**Test File:** `tests/infrastructure/resilience/test_segy_recorder_pod_resilience.py`
""",
        "priority": "High",
        "labels": ["segy-recorder", "kubernetes", "resilience"],
        "components": ["segy-recorder", "kubernetes"]
    },
    # Multiple Pods Resilience (4 tests)
    "PZ-TBD-024": {
        "summary": "MongoDB + RabbitMQ Down Simultaneously",
        "description": """## Objective
Validate that when both MongoDB and RabbitMQ are down, the system handles complete outage gracefully.

## Test Type
Integration Test

## Priority
P1 - High

## Components/Labels
mongodb, rabbitmq, kubernetes, resilience, multiple-pods

## Automation Status
✅ Automated

**Test Function:** `test_mongodb_rabbitmq_down_simultaneously`  
**Test File:** `tests/infrastructure/resilience/test_multiple_pods_resilience.py`
""",
        "priority": "High",
        "labels": ["mongodb", "rabbitmq", "kubernetes", "resilience"],
        "components": ["mongodb", "rabbitmq", "kubernetes"]
    },
    "PZ-TBD-025": {
        "summary": "MongoDB + Focus Server Down Simultaneously",
        "description": """## Objective
Validate that when both MongoDB and Focus Server are down, the system handles complete outage gracefully.

## Test Type
Integration Test

## Priority
P1 - High

## Components/Labels
mongodb, focus-server, kubernetes, resilience, multiple-pods

## Automation Status
✅ Automated

**Test Function:** `test_mongodb_focus_server_down_simultaneously`  
**Test File:** `tests/infrastructure/resilience/test_multiple_pods_resilience.py`
""",
        "priority": "High",
        "labels": ["mongodb", "focus-server", "kubernetes", "resilience"],
        "components": ["mongodb", "focus-server", "kubernetes"]
    },
    "PZ-TBD-026": {
        "summary": "RabbitMQ + Focus Server Down Simultaneously",
        "description": """## Objective
Validate that when both RabbitMQ and Focus Server are down, the system handles complete outage gracefully.

## Test Type
Integration Test

## Priority
P1 - High

## Components/Labels
rabbitmq, focus-server, kubernetes, resilience, multiple-pods

## Automation Status
✅ Automated

**Test Function:** `test_rabbitmq_focus_server_down_simultaneously`  
**Test File:** `tests/infrastructure/resilience/test_multiple_pods_resilience.py`
""",
        "priority": "High",
        "labels": ["rabbitmq", "focus-server", "kubernetes", "resilience"],
        "components": ["rabbitmq", "focus-server", "kubernetes"]
    },
    "PZ-TBD-027": {
        "summary": "Focus Server + SEGY Recorder Down Simultaneously",
        "description": """## Objective
Validate that when both Focus Server and SEGY Recorder are down, jobs fail gracefully and recording stops.

## Test Type
Integration Test

## Priority
P2 - Medium

## Components/Labels
focus-server, segy-recorder, kubernetes, resilience, multiple-pods

## Automation Status
✅ Automated

**Test Function:** `test_focus_server_segy_recorder_down_simultaneously`  
**Test File:** `tests/infrastructure/resilience/test_multiple_pods_resilience.py`
""",
        "priority": "Medium",
        "labels": ["focus-server", "segy-recorder", "kubernetes", "resilience"],
        "components": ["focus-server", "segy-recorder", "kubernetes"]
    },
    # Pod Recovery Scenarios (3 tests)
    "PZ-TBD-028": {
        "summary": "Recovery Order Validation",
        "description": """## Objective
Validate that pods recover in the correct order (MongoDB → RabbitMQ → Focus Server).

## Test Type
Integration Test

## Priority
P1 - High

## Components/Labels
kubernetes, resilience, recovery, recovery-order

## Automation Status
✅ Automated

**Test Function:** `test_recovery_order_validation`  
**Test File:** `tests/infrastructure/resilience/test_pod_recovery_scenarios.py`
""",
        "priority": "High",
        "labels": ["kubernetes", "resilience", "recovery"],
        "components": ["kubernetes", "resilience"]
    },
    "PZ-TBD-029": {
        "summary": "Cascading Recovery Scenarios",
        "description": """## Objective
Validate cascading recovery when multiple pods are restored simultaneously.

## Test Type
Integration Test

## Priority
P2 - Medium

## Components/Labels
kubernetes, resilience, recovery, cascading

## Automation Status
✅ Automated

**Test Function:** `test_cascading_recovery_scenarios`  
**Test File:** `tests/infrastructure/resilience/test_pod_recovery_scenarios.py`
""",
        "priority": "Medium",
        "labels": ["kubernetes", "resilience", "recovery"],
        "components": ["kubernetes", "resilience"]
    },
    "PZ-TBD-030": {
        "summary": "Recovery Time Measurement",
        "description": """## Objective
Measure recovery time for each pod type.

## Test Type
Integration Test

## Priority
P2 - Medium

## Components/Labels
kubernetes, resilience, recovery, performance, metrics

## Automation Status
✅ Automated

**Test Function:** `test_recovery_time_measurement`  
**Test File:** `tests/infrastructure/resilience/test_pod_recovery_scenarios.py`
""",
        "priority": "Medium",
        "labels": ["kubernetes", "resilience", "recovery", "performance"],
        "components": ["kubernetes", "resilience"]
    },
}


def create_xray_test(
    client: JiraClient,
    test_id: str,
    test_data: Dict[str, Any],
    folder_id: Optional[str] = None,
    dry_run: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Create a test in Xray Test Repository.
    
    Args:
        client: JiraClient instance
        test_id: Test ID (e.g., "PZ-TBD-001")
        test_data: Test data dictionary
        folder_id: Optional Xray folder ID
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
        
        logger.info(f"✅ Created test: {issue['key']} - {issue['summary']}")
        logger.info(f"   URL: {issue['url']}")
        
        # Note: Xray folder assignment requires Xray API, not standard Jira API
        # The folder_id would need to be set via Xray REST API if available
        if folder_id:
            logger.info(f"   Note: Folder ID {folder_id} - requires Xray API to assign")
        
        return issue
        
    except Exception as e:
        logger.error(f"❌ Failed to create test {test_id}: {e}")
        raise


def main():
    """Main function for creating Xray tests."""
    parser = argparse.ArgumentParser(
        description='Create Kubernetes Pod Resilience tests in Xray Test Repository',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (preview what would be created)
  python create_xray_resilience_tests.py --dry-run
  
  # Create all tests
  python create_xray_resilience_tests.py
  
  # Create tests in specific folder
  python create_xray_resilience_tests.py --folder-id 68d91b9f681e183ea2e83e16
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview what would be created without actually creating tests'
    )
    
    parser.add_argument(
        '--folder-id',
        help='Xray Test Repository folder ID (requires Xray API for assignment)'
    )
    
    parser.add_argument(
        '--config',
        help='Path to jira_config.yaml (optional)'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize Jira client
        logger.info("Initializing Jira client...")
        client = JiraClient(config_path=args.config)
        
        # Create all tests
        created_tests = []
        failed_tests = []
        
        logger.info(f"\n{'='*80}")
        logger.info(f"Creating {len(RESILIENCE_TESTS)} Kubernetes Pod Resilience Tests")
        logger.info(f"{'='*80}\n")
        
        for test_id, test_data in RESILIENCE_TESTS.items():
            try:
                issue = create_xray_test(
                    client=client,
                    test_id=test_id,
                    test_data=test_data,
                    folder_id=args.folder_id,
                    dry_run=args.dry_run
                )
                
                if issue:
                    created_tests.append(issue)
                
            except Exception as e:
                logger.error(f"Failed to create {test_id}: {e}")
                failed_tests.append((test_id, str(e)))
        
        # Summary
        logger.info(f"\n{'='*80}")
        logger.info("SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(f"Total tests: {len(RESILIENCE_TESTS)}")
        logger.info(f"Created: {len(created_tests)}")
        logger.info(f"Failed: {len(failed_tests)}")
        
        if created_tests:
            logger.info(f"\n✅ Successfully created tests:")
            for issue in created_tests:
                logger.info(f"   - {issue['key']}: {issue['summary']}")
                logger.info(f"     URL: {issue['url']}")
        
        if failed_tests:
            logger.error(f"\n❌ Failed to create tests:")
            for test_id, error in failed_tests:
                logger.error(f"   - {test_id}: {error}")
        
        if args.dry_run:
            logger.info("\n⚠️  DRY RUN MODE - No tests were actually created")
            logger.info("   Run without --dry-run to create tests")
        
        logger.info(f"{'='*80}\n")
        
        return 0 if len(failed_tests) == 0 else 1
        
    except Exception as e:
        logger.error(f"Failed to create tests: {e}")
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

