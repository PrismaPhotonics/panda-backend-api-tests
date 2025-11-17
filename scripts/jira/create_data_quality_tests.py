#!/usr/bin/env python3
"""
Create Data Quality Tests in Jira Xray
=======================================

Creates 5 data quality test tickets in Jira Xray for Focus Server API.

Tests:
- Waterfall Data Consistency
- Metadata Consistency
- Data Integrity Across Requests
- Timestamp Accuracy
- Data Completeness

Usage:
    python scripts/jira/create_data_quality_tests.py
    python scripts/jira/create_data_quality_tests.py --dry-run
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Dict, Any

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

# Data Quality Tests Definitions
DATA_QUALITY_TESTS = {
    "DQ-001": {
        "summary": "Data Quality - Waterfall Data Consistency",
        "description": """h2. Objective
Verify that waterfall data is consistent across multiple requests for the same job.

h2. Pre-Conditions
* Focus Server API is running and accessible
* Active streaming job exists with data available

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Send GET /waterfall/{job_id}/{row_count} request | job_id, row_count=100 | First request sent |
| 2 | Store response data | Waterfall data | Data stored |
| 3 | Send second GET /waterfall request | Same job_id, row_count=100 | Second request sent |
| 4 | Compare responses | Compare data from both requests | Data compared |
| 5 | Verify consistency | Check for differences | Data is consistent |

h2. Expected Result
Waterfall data is consistent across multiple requests for the same job and row_count.

h2. Assertions
* Data structure is consistent
* Data values match (for same time range)
* No unexpected data loss
* Timestamps are accurate

h2. Automation Status
✅ Automated

*Test Function:* `test_waterfall_data_consistency`
*Test File:* `tests/integration/data_quality/test_waterfall_consistency.py`
*Test Class:* `TestWaterfallConsistency`
""",
        "priority": "Medium",
        "labels": ["data-quality", "api", "waterfall", "consistency", "automation"],
        "components": ["focus-server", "api"]
    },
    "DQ-002": {
        "summary": "Data Quality - Metadata Consistency",
        "description": """h2. Objective
Verify that metadata is consistent with configuration and remains accurate over time.

h2. Pre-Conditions
* Focus Server API is running and accessible
* Active streaming job exists

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Send POST /configure request | Valid configuration | Job created |
| 2 | Store configuration | Configuration parameters | Configuration stored |
| 3 | Send GET /metadata/{job_id} request | job_id | Metadata retrieved |
| 4 | Compare metadata with configuration | Compare values | Values compared |
| 5 | Verify consistency | Check for matches | Metadata matches configuration |
| 6 | Wait and re-check | After 30 seconds | Metadata still consistent |

h2. Expected Result
Metadata is consistent with configuration and remains accurate over time.

h2. Assertions
* Metadata matches configuration parameters
* Metadata remains consistent over time
* No unexpected changes
* Timestamps are accurate

h2. Automation Status
✅ Automated

*Test Function:* `test_metadata_consistency`
*Test File:* `tests/integration/data_quality/test_metadata_consistency.py`
*Test Class:* `TestMetadataConsistency`
""",
        "priority": "Medium",
        "labels": ["data-quality", "api", "metadata", "consistency", "automation"],
        "components": ["focus-server", "api"]
    },
    "DQ-003": {
        "summary": "Data Quality - Data Integrity Across Requests",
        "description": """h2. Objective
Verify that data integrity is maintained across multiple API requests and endpoints.

h2. Pre-Conditions
* Focus Server API is running and accessible
* Active streaming job exists

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Send GET /metadata/{job_id} | job_id | Metadata retrieved |
| 2 | Send GET /waterfall/{job_id}/{row_count} | Same job_id | Waterfall data retrieved |
| 3 | Verify data relationships | Check job_id matches | Relationships verified |
| 4 | Verify data completeness | Check all expected fields | Data is complete |
| 5 | Verify no data corruption | Check data values | No corruption detected |

h2. Expected Result
Data integrity is maintained across multiple API requests and endpoints.

h2. Assertions
* Job IDs match across endpoints
* Data relationships are correct
* No data corruption
* All expected fields present

h2. Automation Status
✅ Automated

*Test Function:* `test_data_integrity_across_requests`
*Test File:* `tests/integration/data_quality/test_data_integrity.py`
*Test Class:* `TestDataIntegrity`
""",
        "priority": "Medium",
        "labels": ["data-quality", "api", "integrity", "automation"],
        "components": ["focus-server", "api"]
    },
    "DQ-004": {
        "summary": "Data Quality - Timestamp Accuracy",
        "description": """h2. Objective
Verify that timestamps in API responses are accurate and consistent.

h2. Pre-Conditions
* Focus Server API is running and accessible
* Active streaming job exists
* System clock is synchronized

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Record current system time | System timestamp | Baseline timestamp recorded |
| 2 | Send GET /metadata/{job_id} | job_id | Metadata retrieved |
| 3 | Extract timestamps from response | Response timestamps | Timestamps extracted |
| 4 | Verify timestamp accuracy | Compare with system time | Timestamps verified |
| 5 | Verify timestamp format | Check format | Format is correct |
| 6 | Verify timestamp consistency | Check across requests | Timestamps consistent |

h2. Expected Result
Timestamps in API responses are accurate, properly formatted, and consistent.

h2. Assertions
* Timestamps are within acceptable range of system time
* Timestamp format is correct (ISO 8601 or similar)
* Timestamps are consistent across requests
* No timezone issues

h2. Automation Status
✅ Automated

*Test Function:* `test_timestamp_accuracy`
*Test File:* `tests/integration/data_quality/test_timestamp_accuracy.py`
*Test Class:* `TestTimestampAccuracy`
""",
        "priority": "Low",
        "labels": ["data-quality", "api", "timestamp", "automation"],
        "components": ["focus-server", "api"]
    },
    "DQ-005": {
        "summary": "Data Quality - Data Completeness",
        "description": """h2. Objective
Verify that API responses contain all required data fields and no data is missing.

h2. Pre-Conditions
* Focus Server API is running and accessible
* Active streaming job exists with data

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | Send GET /metadata/{job_id} | job_id | Metadata retrieved |
| 2 | Verify required fields present | Check field list | All required fields present |
| 3 | Send GET /waterfall/{job_id}/{row_count} | job_id, row_count | Waterfall data retrieved |
| 4 | Verify required fields present | Check field list | All required fields present |
| 5 | Verify no null values in critical fields | Check for nulls | No nulls in critical fields |
| 6 | Verify data ranges | Check value ranges | Values within expected ranges |

h2. Expected Result
API responses contain all required data fields with no missing or null values in critical fields.

h2. Assertions
* All required fields are present
* No null values in critical fields
* Data values are within expected ranges
* Data structure matches schema

h2. Automation Status
✅ Automated

*Test Function:* `test_data_completeness`
*Test File:* `tests/integration/data_quality/test_data_completeness.py`
*Test Class:* `TestDataCompleteness`
""",
        "priority": "Medium",
        "labels": ["data-quality", "api", "completeness", "automation"],
        "components": ["focus-server", "api"]
    }
}


def create_data_quality_test(
    client: JiraClient,
    test_id: str,
    test_data: Dict[str, Any],
    dry_run: bool = False
) -> str:
    """
    Create a data quality test in Jira Xray.
    
    Args:
        client: JiraClient instance
        test_id: Test identifier (e.g., "DQ-001")
        test_data: Test data dictionary
        dry_run: If True, only preview without creating
        
    Returns:
        Created issue key (e.g., "PZ-14807")
    """
    if dry_run:
        logger.info(f"[DRY RUN] Would create test: {test_data['summary']}")
        return f"PZ-DRY-RUN-{test_id}"
    
    try:
        # Create issue using client.create_issue (handles components properly)
        issue = client.create_issue(
            summary=f"Infrastructure - {test_data['summary']}",
            description=test_data['description'],
            issue_type="Test",
            priority=test_data['priority'],
            labels=test_data['labels'],
            components=test_data['components'],
            project_key="PZ"
        )
        
        # Set Test Type to "Automation" after creation
        try:
            issue_obj = client.jira.issue(issue['key'])
            issue_obj.update(fields={"customfield_10951": {"value": "Automation"}})
            logger.info(f"✅ Set Test Type to 'Automation' for {issue['key']}")
        except Exception as e:
            logger.warning(f"⚠️  Could not set Test Type for {issue['key']}: {e}")
        
        logger.info(f"[OK] Created test: {issue['key']} - {test_data['summary']}")
        
        return issue['key']
        
    except Exception as e:
        logger.error(f"[FAIL] Failed to create test {test_id}: {e}")
        raise


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Create data quality tests in Jira Xray'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without creating tests'
    )
    
    args = parser.parse_args()
    
    try:
        client = JiraClient()
        
        logger.info("=" * 80)
        logger.info(f"{'[DRY RUN] ' if args.dry_run else ''}Creating Data Quality Tests")
        logger.info("=" * 80)
        
        created_tests = []
        failed_tests = []
        
        for test_id, test_data in DATA_QUALITY_TESTS.items():
            try:
                issue_key = create_data_quality_test(
                    client,
                    test_id,
                    test_data,
                    dry_run=args.dry_run
                )
                created_tests.append({
                    'test_id': test_id,
                    'issue_key': issue_key,
                    'summary': test_data['summary']
                })
            except Exception as e:
                logger.error(f"Failed to create {test_id}: {e}")
                failed_tests.append(test_id)
        
        # Summary
        print("\n" + "=" * 80)
        print("CREATION SUMMARY")
        print("=" * 80)
        print(f"Total tests: {len(DATA_QUALITY_TESTS)}")
        print(f"[OK] Created: {len(created_tests)}")
        print(f"[FAIL] Failed: {len(failed_tests)}")
        
        if created_tests:
            print("\nCreated Tests:")
            print("-" * 80)
            for test in created_tests:
                print(f"  {test['test_id']}: {test['issue_key']} - {test['summary']}")
        
        if failed_tests:
            print(f"\nFailed Tests: {', '.join(failed_tests)}")
        
        if args.dry_run:
            print("\n[DRY RUN] No tests were actually created")
        
        client.close()
        
        return 0 if len(failed_tests) == 0 else 1
        
    except Exception as e:
        logger.error(f"Failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

