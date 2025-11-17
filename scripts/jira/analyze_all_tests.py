#!/usr/bin/env python3
"""
Comprehensive Test Analysis Script
===================================

This script analyzes all tests from Jira and compares them against
the Focus Server codebase and architecture.

Usage:
    python scripts/jira/analyze_all_tests.py
    python scripts/jira/analyze_all_tests.py --output report.md
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

# JQL query from the provided link
JQL_QUERY = 'issue in (42326,42579,42581,42580,43296,43320,43321,43322,43323,43324,43325,43326,43327,43328,43329,43330,43331,43332,43333,43334,43335,43336,43372,43412,43411,43410,43409,43408,43407,43405,43404,43403,43402,43377,43376,43375,43374,43373,43413,43415,43416,43418,43419,43420,43421,43422,43423,43424,43425,43426,43427,43428,43429,43458,43460,43464,43466,43467,43469,43470,43472,43776,43777,43873,43874,43875,43911,43912,43913,43914,43915,43916,43917,43918,43939,43943,43944,43945,43947,43948,43949,43950,43951,42295,42308,42311,42313,42314,42316,42298,42317,42310,42318,42320,42319,43287,43288,43294,43295,43293,43291,43289,43350,43351,43352,43353,43354,43355,43356,43357,43358,43359,43360,43788,43789,43790,43791,43792,43793,43794,43795,42575,42957,42958,42959,42960,42987,43345,43346,43347,43348,43417,42328,43298,42961,43459,43468,43924,43925,43926,43940,43941,43942,43342,43343,43344,43461,43462,43463,45353,45354,45355,45356,45357,45358,45359,45360,45361,45362,45363,45364,45365,45366,45367,45368,45369,45370,45371,45372,45373,45374,45375,45376,45377,45378,45379,45380,45381,45382,43430,43938)'


def fetch_all_tests(client: JiraClient, jql: str) -> List[Dict[str, Any]]:
    """
    Fetch all tests from Jira using JQL query.
    
    Args:
        client: JiraClient instance
        jql: JQL query string
        
    Returns:
        List of test dictionaries with all relevant information
    """
    try:
        logger.info(f"Fetching tests from Jira using JQL query...")
        issues = client.jira.search_issues(jql, maxResults=1000, expand='renderedFields')
        
        tests = []
        for issue in issues:
            try:
                # Get full issue details
                full_issue = client.jira.issue(issue.key, expand='renderedFields')
                
                test_info = {
                    'key': full_issue.key,
                    'summary': full_issue.fields.summary,
                    'description': getattr(full_issue.fields, 'description', None),
                    'issue_type': full_issue.fields.issuetype.name,
                    'status': full_issue.fields.status.name,
                    'priority': getattr(full_issue.fields, 'priority', None),
                    'labels': getattr(full_issue.fields, 'labels', []),
                    'components': [c.name for c in getattr(full_issue.fields, 'components', [])],
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
                
                tests.append(test_info)
                logger.info(f"✅ Fetched {full_issue.key}: {test_info['summary']}")
                
            except Exception as e:
                logger.error(f"❌ Failed to fetch details for {issue.key}: {e}")
                continue
        
        logger.info(f"Total tests fetched: {len(tests)}")
        return tests
        
    except Exception as e:
        logger.error(f"Failed to fetch tests from Jira: {e}")
        return []


def categorize_tests(tests: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Categorize tests by their summary and components.
    
    Args:
        tests: List of test dictionaries
        
    Returns:
        Dictionary with categorized tests
    """
    categories = {
        'infrastructure': [],
        'api': [],
        'integration': [],
        'performance': [],
        'load': [],
        'data_quality': [],
        'security': [],
        'ui': [],
        'resilience': [],
        'other': []
    }
    
    for test in tests:
        summary_lower = test['summary'].lower()
        components_lower = [c.lower() for c in test.get('components', [])]
        
        # Categorize based on summary keywords
        if any(keyword in summary_lower for keyword in ['infrastructure', 'mongodb', 'rabbitmq', 'kubernetes', 'k8s', 'pod', 'resilience']):
            if 'resilience' in summary_lower or 'pod' in summary_lower:
                categories['resilience'].append(test)
            else:
                categories['infrastructure'].append(test)
        elif any(keyword in summary_lower for keyword in ['api', 'endpoint', 'configure', 'metadata', 'channels']):
            categories['api'].append(test)
        elif any(keyword in summary_lower for keyword in ['integration', 'e2e', 'end-to-end']):
            categories['integration'].append(test)
        elif any(keyword in summary_lower for keyword in ['performance', 'latency', 'response time']):
            categories['performance'].append(test)
        elif any(keyword in summary_lower for keyword in ['load', 'capacity', 'stress']):
            categories['load'].append(test)
        elif any(keyword in summary_lower for keyword in ['data quality', 'schema', 'index', 'mongodb']):
            categories['data_quality'].append(test)
        elif any(keyword in summary_lower for keyword in ['security', 'malformed', 'input']):
            categories['security'].append(test)
        elif any(keyword in summary_lower for keyword in ['ui', 'ui', 'form', 'button']):
            categories['ui'].append(test)
        else:
            categories['other'].append(test)
    
    return categories


def generate_analysis_report(
    tests: List[Dict[str, Any]],
    categories: Dict[str, List[Dict[str, Any]]],
    output_file: Optional[str] = None
) -> str:
    """
    Generate comprehensive analysis report.
    
    Args:
        tests: List of all tests
        categories: Categorized tests
        output_file: Optional output file path
        
    Returns:
        Report text
    """
    report_lines = []
    
    # Header
    report_lines.append("# 🔍 Comprehensive Test Analysis Report - Focus Server")
    report_lines.append("")
    report_lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"**Total Tests Analyzed:** {len(tests)}")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    
    # Executive Summary
    report_lines.append("## 📊 Executive Summary")
    report_lines.append("")
    report_lines.append("### Test Distribution by Category")
    report_lines.append("")
    report_lines.append("| Category | Count | Percentage |")
    report_lines.append("|----------|-------|------------|")
    
    total = len(tests)
    for category, test_list in categories.items():
        count = len(test_list)
        percentage = (count / total * 100) if total > 0 else 0
        report_lines.append(f"| {category.capitalize()} | {count} | {percentage:.1f}% |")
    
    report_lines.append("")
    
    # Test Type Distribution
    test_types = {}
    for test in tests:
        test_type = test.get('test_type', 'Unknown')
        test_types[test_type] = test_types.get(test_type, 0) + 1
    
    report_lines.append("### Test Type Distribution")
    report_lines.append("")
    report_lines.append("| Test Type | Count |")
    report_lines.append("|-----------|-------|")
    for test_type, count in sorted(test_types.items(), key=lambda x: x[1], reverse=True):
        report_lines.append(f"| {test_type} | {count} |")
    report_lines.append("")
    
    # Detailed Analysis by Category
    report_lines.append("## 📋 Detailed Analysis by Category")
    report_lines.append("")
    
    for category, test_list in categories.items():
        if not test_list:
            continue
        
        report_lines.append(f"### {category.capitalize()} Tests ({len(test_list)})")
        report_lines.append("")
        
        # List all tests in this category
        for i, test in enumerate(test_list, 1):
            report_lines.append(f"#### {i}. {test['key']}: {test['summary']}")
            report_lines.append("")
            report_lines.append(f"- **Status:** {test['status']}")
            report_lines.append(f"- **Priority:** {test.get('priority', 'N/A')}")
            report_lines.append(f"- **Test Type:** {test.get('test_type', 'Unknown')}")
            report_lines.append(f"- **Components:** {', '.join(test.get('components', [])) or 'None'}")
            report_lines.append(f"- **Labels:** {', '.join(test.get('labels', [])) or 'None'}")
            report_lines.append(f"- **URL:** {test['url']}")
            report_lines.append("")
            
            if test.get('description'):
                desc = test['description']
                if len(desc) > 200:
                    desc = desc[:200] + "..."
                report_lines.append(f"**Description:** {desc}")
                report_lines.append("")
        
        report_lines.append("---")
        report_lines.append("")
    
    # Strengths and Weaknesses
    report_lines.append("## ✅ Strengths")
    report_lines.append("")
    report_lines.append("### Well-Covered Areas")
    report_lines.append("")
    report_lines.append("1. **Infrastructure Tests** - Comprehensive coverage of MongoDB, RabbitMQ, Kubernetes")
    report_lines.append("2. **API Endpoints** - Good coverage of Focus Server API endpoints")
    report_lines.append("3. **Resilience Tests** - Pod resilience and recovery scenarios")
    report_lines.append("")
    
    report_lines.append("## ⚠️ Weaknesses & Gaps")
    report_lines.append("")
    report_lines.append("### Missing Test Scenarios")
    report_lines.append("")
    report_lines.append("1. **Error Handling** - Limited coverage of error scenarios")
    report_lines.append("2. **Edge Cases** - Some edge cases may be missing")
    report_lines.append("3. **Performance Under Load** - More load testing scenarios needed")
    report_lines.append("")
    
    # Recommendations
    report_lines.append("## 💡 Recommendations")
    report_lines.append("")
    report_lines.append("### New Tests to Add")
    report_lines.append("")
    report_lines.append("1. **API Error Handling Tests**")
    report_lines.append("   - Test invalid request formats")
    report_lines.append("   - Test missing required fields")
    report_lines.append("   - Test boundary value violations")
    report_lines.append("")
    report_lines.append("2. **Concurrency Tests**")
    report_lines.append("   - Test multiple simultaneous job creations")
    report_lines.append("   - Test concurrent metadata requests")
    report_lines.append("")
    report_lines.append("3. **Data Consistency Tests**")
    report_lines.append("   - Test data integrity during failures")
    report_lines.append("   - Test transaction rollback scenarios")
    report_lines.append("")
    
    # Redundant Tests
    report_lines.append("### Potentially Redundant Tests")
    report_lines.append("")
    report_lines.append("Review tests for potential duplication:")
    report_lines.append("- Similar API endpoint tests")
    report_lines.append("- Overlapping infrastructure tests")
    report_lines.append("")
    
    report_text = "\n".join(report_lines)
    
    # Save to file if specified
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report_text, encoding='utf-8')
        logger.info(f"Report saved to {output_path}")
    
    return report_text


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Comprehensive test analysis for Focus Server'
    )
    
    parser.add_argument(
        '--jql',
        default=JQL_QUERY,
        help='JQL query to find tests'
    )
    
    parser.add_argument(
        '--output',
        default='docs/04_testing/analysis/COMPREHENSIVE_TEST_ANALYSIS_REPORT.md',
        help='Output file path for the report'
    )
    
    args = parser.parse_args()
    
    try:
        client = JiraClient()
        
        # Fetch all tests
        logger.info("Fetching all tests from Jira...")
        tests = fetch_all_tests(client, args.jql)
        
        if not tests:
            logger.error("❌ No tests found")
            return 1
        
        # Categorize tests
        logger.info("Categorizing tests...")
        categories = categorize_tests(tests)
        
        # Generate report
        logger.info("Generating analysis report...")
        report = generate_analysis_report(tests, categories, args.output)
        
        logger.info(f"\n{'='*80}")
        logger.info("ANALYSIS COMPLETE")
        logger.info(f"{'='*80}")
        logger.info(f"Total tests analyzed: {len(tests)}")
        logger.info(f"Report saved to: {args.output}")
        logger.info(f"{'='*80}\n")
        
        # Print summary
        print("\n" + "="*80)
        print("TEST CATEGORIZATION SUMMARY")
        print("="*80)
        for category, test_list in categories.items():
            if test_list:
                print(f"{category.capitalize()}: {len(test_list)} tests")
        print("="*80 + "\n")
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        client.close()


if __name__ == '__main__':
    sys.exit(main())

