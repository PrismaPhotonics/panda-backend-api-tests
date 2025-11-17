"""
Get Test Plan Tests - Direct from Jira
========================================

This script reads Test Plan PZ-14024 directly from Jira and gets all linked tests.

Usage:
    python scripts/jira/get_test_plan_tests_direct.py --test-plan PZ-14024
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
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


def get_test_plan_tests_direct(client: JiraClient, test_plan_key: str) -> Dict[str, Any]:
    """
    Get test cases directly from Test Plan in Jira.
    
    Args:
        client: JiraClient instance
        test_plan_key: Test Plan key (e.g., PZ-14024)
        
    Returns:
        Dictionary with test plan info and linked tests
    """
    logger.info(f"Fetching Test Plan directly from Jira: {test_plan_key}")
    
    try:
        # Get Test Plan issue
        test_plan_issue = client.jira.issue(test_plan_key, expand='renderedFields')
        
        test_plan_info = {
            'key': test_plan_issue.key,
            'summary': test_plan_issue.fields.summary,
            'description': getattr(test_plan_issue.fields, 'description', None),
            'status': test_plan_issue.fields.status.name,
            'url': f"{client.jira._options['server']}/browse/{test_plan_issue.key}",
            'tests': []
        }
        
        logger.info(f"Test Plan: {test_plan_info['summary']}")
        logger.info(f"Status: {test_plan_info['status']}")
        
        # Method 1: Check issue links
        logger.info("Checking issue links...")
        if hasattr(test_plan_issue.fields, 'issuelinks'):
            linked_issues = []
            for link in test_plan_issue.fields.issuelinks:
                if hasattr(link, 'outwardIssue'):
                    linked_issues.append(link.outwardIssue)
                if hasattr(link, 'inwardIssue'):
                    linked_issues.append(link.inwardIssue)
            
            logger.info(f"Found {len(linked_issues)} linked issues")
            for link in linked_issues[:10]:  # Show first 10
                logger.info(f"  - {link.key}: {link.fields.summary[:50]}")
        
        # Method 2: Check all custom fields for test references
        logger.info("Checking custom fields...")
        custom_fields_found = []
        for field_name in dir(test_plan_issue.fields):
            if not field_name.startswith('_') and 'custom' in field_name.lower():
                try:
                    field_value = getattr(test_plan_issue.fields, field_name)
                    if field_value:
                        logger.info(f"  Found custom field: {field_name} = {field_value}")
                        custom_fields_found.append((field_name, field_value))
                except:
                    pass
        
        # Method 3: Try Xray GraphQL API (if available)
        logger.info("Trying Xray GraphQL API...")
        try:
            graphql_query = """
            {
              getTestPlan(jira: {id: "%s"}) {
                tests {
                  jira(fields: ["key", "summary", "status"])
                }
              }
            }
            """ % test_plan_key
            
            # Try GraphQL endpoint
            graphql_url = f"{client.jira._options['server']}/rest/api/2/graphql"
            response = client.jira._session.post(
                graphql_url,
                json={'query': graphql_query},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"GraphQL response: {data}")
            else:
                logger.warning(f"GraphQL returned {response.status_code}")
        except Exception as e:
            logger.warning(f"GraphQL not available: {e}")
        
        # Method 4: Search for Test Executions that reference this Test Plan
        logger.info("Searching for Test Executions...")
        try:
            # Try different JQL patterns
            jql_patterns = [
                f'project = PZ AND issuetype = "Test Execution" AND "Test Plan" = {test_plan_key}',
                f'project = PZ AND issuetype = "Test Execution" AND testPlan = {test_plan_key}',
                f'project = PZ AND issuetype = "Test Execution" AND testplan = {test_plan_key}',
            ]
            
            for jql in jql_patterns:
                try:
                    executions = client.jira.search_issues(jql, maxResults=100)
                    if executions:
                        logger.info(f"Found {len(executions)} Test Executions with JQL: {jql}")
                        for exec in executions[:5]:
                            logger.info(f"  - {exec.key}: {exec.fields.summary[:50]}")
                        break
                except Exception as e:
                    logger.debug(f"JQL pattern failed: {jql} - {e}")
        except Exception as e:
            logger.warning(f"Could not search Test Executions: {e}")
        
        # Method 5: Get all fields and print them to see what's available
        logger.info("Analyzing all Test Plan fields...")
        logger.info("="*80)
        logger.info("ALL FIELDS IN TEST PLAN:")
        logger.info("="*80)
        
        for field_name in sorted(dir(test_plan_issue.fields)):
            if not field_name.startswith('_'):
                try:
                    field_value = getattr(test_plan_issue.fields, field_name)
                    if field_value and not callable(field_value):
                        # Truncate long values
                        value_str = str(field_value)
                        if len(value_str) > 100:
                            value_str = value_str[:100] + "..."
                        logger.info(f"  {field_name}: {value_str}")
                except Exception as e:
                    pass
        
        logger.info("="*80)
        
        # For now, return what we have
        logger.info(f"Total tests found via direct methods: {len(test_plan_info['tests'])}")
        return test_plan_info
        
    except Exception as e:
        logger.error(f"Failed to fetch Test Plan: {e}")
        import traceback
        traceback.print_exc()
        raise


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Get test cases directly from Test Plan in Jira')
    parser.add_argument('--test-plan', type=str, required=True, help='Test Plan key (e.g., PZ-14024)')
    args = parser.parse_args()
    
    print("="*80)
    print(f"Reading Test Plan DIRECTLY from Jira: {args.test_plan}")
    print("="*80)
    print()
    
    try:
        client = JiraClient()
        test_plan_info = get_test_plan_tests_direct(client, args.test_plan)
        
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Test Plan: {test_plan_info['key']}")
        print(f"Summary: {test_plan_info['summary']}")
        print(f"Status: {test_plan_info['status']}")
        print(f"Total Tests Found: {len(test_plan_info['tests'])}")
        print("="*80)
        
        client.close()
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

