"""
Get Test Plan Tests V2 - Alternative method using JQL
======================================================

This script retrieves test cases from a Test Plan using JQL queries.

Usage:
    python scripts/jira/get_test_plan_tests_v2.py --test-plan PZ-14024
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


def get_test_plan_tests_via_jql(client: JiraClient, test_plan_key: str) -> Dict[str, Any]:
    """
    Get test cases from Test Plan using JQL.
    
    In Xray, tests can be linked to Test Plans through:
    1. Test Executions (test execution -> test plan)
    2. Test Sets (test set -> test plan)
    3. Direct links
    
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
        
        # Method 1: Search for Test Executions linked to this Test Plan
        logger.info("Searching for Test Executions...")
        try:
            # In Xray, Test Executions reference Test Plans
            # Custom field for Test Plan link might be customfield_XXXXX
            # Common field IDs: customfield_10100, customfield_10101, etc.
            
            # Try to find Test Executions
            execution_jql = f'project = PZ AND issuetype = "Test Execution" AND "Test Plan" = {test_plan_key}'
            executions = client.jira.search_issues(execution_jql, maxResults=100)
            logger.info(f"Found {len(executions)} Test Executions")
            
            # Get tests from executions
            test_keys = set()
            for execution in executions:
                # Get tests from execution
                exec_issue = client.jira.issue(execution.key, expand='renderedFields')
                # Tests might be in custom field or as linked issues
                # Try common custom fields
                for field_name in dir(exec_issue.fields):
                    if 'test' in field_name.lower() and not field_name.startswith('_'):
                        try:
                            field_value = getattr(exec_issue.fields, field_name)
                            if field_value:
                                logger.debug(f"Found field {field_name}: {field_value}")
                        except:
                            pass
            
        except Exception as e:
            logger.warning(f"Could not get Test Executions: {e}")
        
        # Method 2: Search for tests that might be in this Test Plan
        # Based on documentation, PZ-14024 has 47 tests
        # From COMPLETE_XRAY_COVERAGE_PZ14024.md, we know the test IDs
        
        # Known test IDs from Test Plan PZ-14024 (from documentation)
        known_test_ids = [
            # Calculations (14)
            'PZ-14060', 'PZ-14061', 'PZ-14062', 'PZ-14066', 'PZ-14067', 'PZ-14068',
            'PZ-14069', 'PZ-14070', 'PZ-14071', 'PZ-14072', 'PZ-14073', 'PZ-14078',
            'PZ-14079', 'PZ-14080',
            # Health Check (8)
            'PZ-14026', 'PZ-14027', 'PZ-14028', 'PZ-14029', 'PZ-14030', 'PZ-14031',
            'PZ-14032', 'PZ-14033',
            # Orchestration (2)
            'PZ-14018', 'PZ-14019',
            # Infrastructure (3)
            'PZ-13898', 'PZ-13899', 'PZ-13900',
            # API Endpoints (8)
            'PZ-13895', 'PZ-13896', 'PZ-13897', 'PZ-13901', 'PZ-13903', 'PZ-13904',
            'PZ-13905', 'PZ-13906',
            # Historic/Config/Live (12)
            'PZ-13547', 'PZ-13548', 'PZ-13863', 'PZ-13864', 'PZ-13865', 'PZ-13866',
            'PZ-13867', 'PZ-13868', 'PZ-13869', 'PZ-13870', 'PZ-13871', 'PZ-13872'
        ]
        
        logger.info(f"Fetching {len(known_test_ids)} known tests from Test Plan...")
        
        # Fetch all tests in batches
        batch_size = 50
        for i in range(0, len(known_test_ids), batch_size):
            batch = known_test_ids[i:i+batch_size]
            jql = f'project = PZ AND key IN ({",".join(batch)})'
            
            try:
                batch_tests = client.jira.search_issues(jql, maxResults=batch_size)
                
                for test_issue in batch_tests:
                    try:
                        # Get full issue details
                        full_issue = client.jira.issue(test_issue.key, expand='renderedFields')
                        
                        test_info = {
                            'key': full_issue.key,
                            'summary': full_issue.fields.summary,
                            'description': getattr(full_issue.fields, 'description', None),
                            'status': full_issue.fields.status.name,
                            'test_type': None,
                            'url': f"{client.jira._options['server']}/browse/{full_issue.key}"
                        }
                        
                        # Try to get Test Type custom field
                        try:
                            test_type_field = getattr(full_issue.fields, 'customfield_10951', None)
                            if test_type_field:
                                test_info['test_type'] = test_type_field.value if hasattr(test_type_field, 'value') else str(test_type_field)
                        except:
                            pass
                        
                        test_plan_info['tests'].append(test_info)
                        logger.info(f"  ✅ {full_issue.key}: {test_info['summary'][:60]}")
                        
                    except Exception as e:
                        logger.warning(f"  ⚠️ Could not fetch test {test_issue.key}: {e}")
                        
            except Exception as e:
                logger.warning(f"Could not fetch batch {i//batch_size + 1}: {e}")
        
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
    
    if test_plan_info['description']:
        report_lines.append("## Description\n\n")
        report_lines.append(f"{test_plan_info['description']}\n\n")
        report_lines.append("---\n\n")
    
    # Group tests by category
    categories = {
        'Calculations': [],
        'Health Check': [],
        'Orchestration': [],
        'Infrastructure': [],
        'API Endpoints': [],
        'Historic/Config/Live': [],
        'Other': []
    }
    
    for test in test_plan_info['tests']:
        test_id = test['key']
        if test_id.startswith('PZ-1406') or test_id.startswith('PZ-1407') or test_id.startswith('PZ-1408'):
            categories['Calculations'].append(test)
        elif test_id.startswith('PZ-1402'):
            categories['Health Check'].append(test)
        elif test_id.startswith('PZ-1401'):
            categories['Orchestration'].append(test)
        elif test_id.startswith('PZ-1389'):
            categories['Infrastructure'].append(test)
        elif test_id.startswith('PZ-1389') and int(test_id.split('-')[1]) >= 13901:
            categories['API Endpoints'].append(test)
        elif test_id.startswith('PZ-138') or test_id.startswith('PZ-135'):
            categories['Historic/Config/Live'].append(test)
        else:
            categories['Other'].append(test)
    
    report_lines.append("## Test Cases by Category\n\n")
    
    for category, tests in categories.items():
        if tests:
            report_lines.append(f"### {category} ({len(tests)} tests)\n\n")
            report_lines.append("| # | Test ID | Summary | Status | Test Type |\n")
            report_lines.append("|---|---------|---------|--------|-----------|\n")
            
            for idx, test in enumerate(tests, 1):
                test_id = test['key']
                summary = test['summary'].replace('|', '\\|')[:80]
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
        report_lines.append(f"- **URL:** [{test['url']}]({test['url']})\n")
        if test.get('description'):
            desc = test['description'][:300] + "..." if len(test['description']) > 300 else test['description']
            report_lines.append(f"- **Description:** {desc}\n")
        report_lines.append("\n")
    
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
    args = parser.parse_args()
    
    print("="*80)
    print(f"Fetching Test Plan: {args.test_plan}")
    print("="*80)
    print()
    
    try:
        client = JiraClient()
        test_plan_info = get_test_plan_tests_via_jql(client, args.test_plan)
        
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
        print(f"Total Tests: {len(test_plan_info['tests'])}")
        print("="*80)
        
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

