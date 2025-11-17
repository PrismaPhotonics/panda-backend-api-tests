"""
Get Test Plan Tests - Real Direct Access
=========================================

This script reads Test Plan PZ-14024 directly from Jira/Xray and gets ALL linked tests.

Usage:
    python scripts/jira/get_test_plan_tests_real.py --test-plan PZ-14024
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


def get_test_plan_tests_from_xray(client: JiraClient, test_plan_key: str) -> Dict[str, Any]:
    """
    Get test cases from Test Plan using Xray REST API.
    
    Args:
        client: JiraClient instance
        test_plan_key: Test Plan key (e.g., PZ-14024)
        
    Returns:
        Dictionary with test plan info and linked tests
    """
    logger.info(f"Fetching Test Plan from Xray: {test_plan_key}")
    
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
        
        # Try Xray REST API v1
        logger.info("Trying Xray REST API v1...")
        xray_api_urls = [
            f"/rest/raven/1.0/api/testplan/{test_plan_key}/test",
            f"/rest/raven/2.0/api/testplan/{test_plan_key}/test",
            f"/rest/xray/1.0/testplan/{test_plan_key}/test",
            f"/rest/xray/2.0/testplan/{test_plan_key}/test",
        ]
        
        for api_url in xray_api_urls:
            try:
                full_url = f"{client.jira._options['server']}{api_url}"
                logger.info(f"Trying: {full_url}")
                
                response = client.jira._session.get(
                    full_url,
                    headers={'Content-Type': 'application/json'},
                    auth=client.jira._session.auth
                )
                
                logger.info(f"Response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ Success! Got data: {type(data)}")
                    logger.info(f"Data preview: {str(data)[:500]}")
                    
                    # Parse response
                    if isinstance(data, list):
                        tests = data
                    elif isinstance(data, dict):
                        if 'data' in data:
                            tests = data['data']
                        elif 'tests' in data:
                            tests = data['tests']
                        elif 'results' in data:
                            tests = data['results']
                        else:
                            tests = [data]
                    else:
                        tests = []
                    
                    logger.info(f"Found {len(tests)} tests via Xray API")
                    
                    # Get details for each test
                    for test_ref in tests:
                        test_key = None
                        
                        # Try different formats
                        if isinstance(test_ref, str):
                            test_key = test_ref
                        elif isinstance(test_ref, dict):
                            test_key = test_ref.get('key') or test_ref.get('id') or test_ref.get('testKey')
                        
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
                                logger.info(f"  ✅ {test_issue.key}: {test_info['summary'][:60]}")
                                
                            except Exception as e:
                                logger.warning(f"  ⚠️ Could not fetch test {test_key}: {e}")
                    
                    break  # Success, stop trying other URLs
                else:
                    logger.warning(f"  ❌ Status {response.status_code}: {response.text[:200]}")
                    
            except Exception as e:
                logger.warning(f"  ❌ Error with {api_url}: {e}")
                continue
        
        # If Xray API didn't work, try JQL to find tests in Test Plan
        if not test_plan_info['tests']:
            logger.info("Xray API didn't work, trying JQL search...")
            
            # Try to find tests that might be in this Test Plan
            # In Xray, tests can be linked via custom fields
            jql_patterns = [
                f'project = PZ AND issuetype = Test AND "Test Plan" = {test_plan_key}',
                f'project = PZ AND issuetype = Test AND testPlan = {test_plan_key}',
                f'project = PZ AND issuetype = Test AND testplan = {test_plan_key}',
                f'project = PZ AND issuetype = Test AND "Test Plan(s)" = {test_plan_key}',
            ]
            
            for jql in jql_patterns:
                try:
                    logger.info(f"Trying JQL: {jql}")
                    tests = client.jira.search_issues(jql, maxResults=1000)
                    if tests:
                        logger.info(f"✅ Found {len(tests)} tests with JQL!")
                        for test in tests:
                            test_info = {
                                'key': test.key,
                                'summary': test.fields.summary,
                                'description': getattr(test.fields, 'description', None),
                                'status': test.fields.status.name,
                                'test_type': None,
                                'url': f"{client.jira._options['server']}/browse/{test.key}"
                            }
                            test_plan_info['tests'].append(test_info)
                            logger.info(f"  ✅ {test.key}: {test_info['summary'][:60]}")
                        break
                except Exception as e:
                    logger.debug(f"JQL pattern failed: {jql} - {e}")
        
        logger.info(f"Total tests found: {len(test_plan_info['tests'])}")
        return test_plan_info
        
    except Exception as e:
        logger.error(f"Failed to fetch Test Plan: {e}")
        import traceback
        traceback.print_exc()
        raise


def generate_report(test_plan_info: Dict[str, Any], output_file: Optional[Path] = None) -> str:
    """Generate markdown report."""
    report_lines = []
    
    report_lines.append(f"# Test Plan: {test_plan_info['key']}\n\n")
    report_lines.append(f"**Summary:** {test_plan_info['summary']}\n\n")
    report_lines.append(f"**Status:** {test_plan_info['status']}\n\n")
    report_lines.append(f"**URL:** [{test_plan_info['url']}]({test_plan_info['url']})\n\n")
    report_lines.append(f"**Total Tests:** {len(test_plan_info['tests'])}\n\n")
    report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    report_lines.append("---\n\n")
    
    if test_plan_info['tests']:
        report_lines.append("## Test Cases\n\n")
        report_lines.append("| # | Test ID | Summary | Status | Test Type |\n")
        report_lines.append("|---|---------|---------|--------|-----------|\n")
        
        for idx, test in enumerate(test_plan_info['tests'], 1):
            test_id = test['key']
            summary = test['summary'].replace('|', '\\|')[:80]
            status = test['status']
            test_type = test.get('test_type', 'N/A')
            
            report_lines.append(f"| {idx} | [{test_id}]({test['url']}) | {summary} | {status} | {test_type} |\n")
        
        report_lines.append("\n")
    else:
        report_lines.append("**No tests found.**\n\n")
    
    report = ''.join(report_lines)
    
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(report, encoding='utf-8')
        logger.info(f"Report saved to: {output_file}")
    
    return report


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Get test cases directly from Test Plan in Jira/Xray')
    parser.add_argument('--test-plan', type=str, required=True, help='Test Plan key (e.g., PZ-14024)')
    parser.add_argument('--output', type=str, help='Output file path (optional)')
    args = parser.parse_args()
    
    print("="*80)
    print(f"Reading Test Plan DIRECTLY from Jira/Xray: {args.test_plan}")
    print("="*80)
    print()
    
    try:
        client = JiraClient()
        test_plan_info = get_test_plan_tests_from_xray(client, args.test_plan)
        
        output_file = None
        if args.output:
            output_file = Path(args.output)
        
        report = generate_report(test_plan_info, output_file)
        
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Test Plan: {test_plan_info['key']}")
        print(f"Summary: {test_plan_info['summary']}")
        print(f"Status: {test_plan_info['status']}")
        print(f"Total Tests Found: {len(test_plan_info['tests'])}")
        print("="*80)
        
        if test_plan_info['tests']:
            print("\nFirst 10 tests:")
            for test in test_plan_info['tests'][:10]:
                print(f"  - {test['key']}: {test['summary'][:60]}")
            if len(test_plan_info['tests']) > 10:
                print(f"  ... and {len(test_plan_info['tests']) - 10} more")
        else:
            print("\n⚠️ NO TESTS FOUND!")
            print("This means:")
            print("  1. Test Plan might not have tests linked yet")
            print("  2. Xray API might not be accessible")
            print("  3. Tests might be linked via a different mechanism")
        
        client.close()
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

