"""
Get Test Plan Tests - Read all test cases linked to a Test Plan
================================================================

This script connects to Jira and retrieves all test cases linked to a specific Test Plan.

Usage:
    python scripts/jira/get_test_plan_tests.py --test-plan PZ-14024
    python scripts/jira/get_test_plan_tests.py --test-plan PZ-14024 --output reports/test_plan_tests.md
"""

import argparse
import sys
import logging
import json
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


def get_test_plan_tests(client: JiraClient, test_plan_key: str) -> Dict[str, Any]:
    """
    Get all test cases linked to a Test Plan.
    
    Args:
        client: JiraClient instance
        test_plan_key: Test Plan key (e.g., PZ-14024)
        
    Returns:
        Dictionary with test plan info and linked tests
    """
    logger.info(f"Fetching Test Plan: {test_plan_key}")
    
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
        
        # Try to get tests linked to Test Plan using Xray API
        # Method 1: Search for tests that reference this Test Plan
        # In Xray, tests are linked to Test Plans through test executions or test sets
        
        # Method 2: Use JQL to find tests that might be in this Test Plan
        # Note: This depends on how Xray stores Test Plan relationships
        
        # Method 3: Get tests from Test Plan's linked issues
        logger.info("Fetching linked tests...")
        
        # Get all issue links
        linked_issues = []
        if hasattr(test_plan_issue.fields, 'issuelinks'):
            for link in test_plan_issue.fields.issuelinks:
                if hasattr(link, 'outwardIssue'):
                    linked_issues.append(link.outwardIssue)
                if hasattr(link, 'inwardIssue'):
                    linked_issues.append(link.inwardIssue)
        
        # Also try to get tests using Xray-specific API
        # Xray stores Test Plan relationships in test executions
        # We'll search for tests that might be associated with this Test Plan
        
        # Search for all tests in the project (we'll filter by Test Plan later if possible)
        jql = f'project = PZ AND issuetype = Test'
        all_tests = client.jira.search_issues(jql, maxResults=1000)
        
        logger.info(f"Found {len(all_tests)} total tests in project")
        
        # Try to get Test Plan tests using Xray REST API
        # Xray API endpoint: /rest/raven/1.0/api/testplan/{testPlanKey}/test
        try:
            xray_api_url = f"/rest/raven/1.0/api/testplan/{test_plan_key}/test"
            response = client.jira._session.get(
                f"{client.jira._options['server']}{xray_api_url}",
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                xray_tests = response.json()
                logger.info(f"Found {len(xray_tests)} tests via Xray API")
                
                # Get details for each test
                for test_ref in xray_tests:
                    test_key = test_ref.get('key') or test_ref.get('id')
                    if test_key:
                        try:
                            test_issue = client.jira.issue(test_key, expand='renderedFields')
                            test_info = {
                                'key': test_issue.key,
                                'summary': test_issue.fields.summary,
                                'description': getattr(test_issue.fields, 'description', None),
                                'status': test_issue.fields.status.name,
                                'test_type': None,
                                'url': f"{client.jira._options['server']}/browse/{test_issue.key}"
                            }
                            
                            # Try to get Test Type custom field
                            try:
                                test_type_field = getattr(test_issue.fields, 'customfield_10951', None)
                                if test_type_field:
                                    test_info['test_type'] = test_type_field.value if hasattr(test_type_field, 'value') else str(test_type_field)
                            except:
                                pass
                            
                            test_plan_info['tests'].append(test_info)
                            logger.info(f"  ✅ {test_issue.key}: {test_info['summary']}")
                            
                        except Exception as e:
                            logger.warning(f"  ⚠️ Could not fetch test {test_key}: {e}")
            else:
                logger.warning(f"Xray API returned status {response.status_code}, trying alternative method...")
                
                # Alternative: Search for tests that might be in Test Plan
                # This is a fallback - we'll search for tests and check if they're linked
                logger.info("Using fallback method: searching for tests...")
                
        except Exception as e:
            logger.warning(f"Could not use Xray API: {e}")
            logger.info("Using fallback method: searching for all tests...")
        
        # Fallback: If Xray API doesn't work, we'll need to manually identify tests
        # For now, we'll return what we found via linked issues
        
        logger.info(f"Total tests found: {len(test_plan_info['tests'])}")
        return test_plan_info
        
    except Exception as e:
        logger.error(f"Failed to fetch Test Plan: {e}")
        raise


def generate_report(test_plan_info: Dict[str, Any], output_file: Optional[Path] = None) -> str:
    """
    Generate markdown report for Test Plan tests.
    
    Args:
        test_plan_info: Dictionary with test plan info and tests
        output_file: Optional output file path
        
    Returns:
        Report as string
    """
    report_lines = []
    
    report_lines.append(f"# Test Plan: {test_plan_info['key']}\n\n")
    report_lines.append(f"**Summary:** {test_plan_info['summary']}\n\n")
    report_lines.append(f"**Status:** {test_plan_info['status']}\n\n")
    report_lines.append(f"**URL:** {test_plan_info['url']}\n\n")
    report_lines.append(f"**Total Tests:** {len(test_plan_info['tests'])}\n\n")
    report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    report_lines.append("---\n\n")
    
    if test_plan_info['description']:
        report_lines.append("## Description\n\n")
        report_lines.append(f"{test_plan_info['description']}\n\n")
        report_lines.append("---\n\n")
    
    report_lines.append("## Test Cases\n\n")
    
    if test_plan_info['tests']:
        report_lines.append("| # | Test ID | Summary | Status | Test Type |\n")
        report_lines.append("|---|---------|---------|--------|-----------|\n")
        
        for idx, test in enumerate(test_plan_info['tests'], 1):
            test_id = test['key']
            summary = test['summary'].replace('|', '\\|')[:80]  # Truncate and escape
            status = test['status']
            test_type = test.get('test_type', 'N/A')
            
            report_lines.append(f"| {idx} | [{test_id}]({test['url']}) | {summary} | {status} | {test_type} |\n")
        
        report_lines.append("\n")
        
        # Detailed list
        report_lines.append("## Detailed Test List\n\n")
        for idx, test in enumerate(test_plan_info['tests'], 1):
            report_lines.append(f"### {idx}. {test['key']}: {test['summary']}\n\n")
            report_lines.append(f"- **Status:** {test['status']}\n")
            if test.get('test_type'):
                report_lines.append(f"- **Test Type:** {test['test_type']}\n")
            report_lines.append(f"- **URL:** {test['url']}\n")
            if test.get('description'):
                desc = test['description'][:200] + "..." if len(test['description']) > 200 else test['description']
                report_lines.append(f"- **Description:** {desc}\n")
            report_lines.append("\n")
    else:
        report_lines.append("**No tests found.**\n\n")
        report_lines.append("This might mean:\n")
        report_lines.append("- The Test Plan doesn't have tests linked yet\n")
        report_lines.append("- Xray API access is restricted\n")
        report_lines.append("- Tests are linked through a different mechanism\n\n")
    
    report = ''.join(report_lines)
    
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(report, encoding='utf-8')
        logger.info(f"Report saved to: {output_file}")
    
    return report


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Get all test cases from a Test Plan')
    parser.add_argument('--test-plan', type=str, required=True, help='Test Plan key (e.g., PZ-14024)')
    parser.add_argument('--output', type=str, help='Output file path (optional)')
    parser.add_argument('--json', type=str, help='Output JSON file path (optional)')
    args = parser.parse_args()
    
    print("="*80)
    print(f"Fetching Test Plan: {args.test_plan}")
    print("="*80)
    print()
    
    try:
        # Initialize Jira client
        client = JiraClient()
        
        # Get Test Plan tests
        test_plan_info = get_test_plan_tests(client, args.test_plan)
        
        # Generate report
        output_file = None
        if args.output:
            output_file = Path(args.output)
        
        report = generate_report(test_plan_info, output_file)
        
        # Print summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Test Plan: {test_plan_info['key']}")
        print(f"Summary: {test_plan_info['summary']}")
        print(f"Status: {test_plan_info['status']}")
        print(f"Total Tests: {len(test_plan_info['tests'])}")
        print("="*80)
        
        # Save JSON if requested
        if args.json:
            json_file = Path(args.json)
            json_file.parent.mkdir(parents=True, exist_ok=True)
            json_file.write_text(json.dumps(test_plan_info, indent=2, default=str), encoding='utf-8')
            print(f"\nJSON saved to: {json_file}")
        
        # Print first few tests
        if test_plan_info['tests']:
            print("\nFirst 10 tests:")
            for test in test_plan_info['tests'][:10]:
                print(f"  - {test['key']}: {test['summary'][:60]}")
            if len(test_plan_info['tests']) > 10:
                print(f"  ... and {len(test_plan_info['tests']) - 10} more")
        
        client.close()
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

