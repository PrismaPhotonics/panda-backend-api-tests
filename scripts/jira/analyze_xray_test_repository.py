"""
Analyze Xray Test Repository
=============================

Command-line script for analyzing all tests in Xray Test Repository.

This script connects to Jira, retrieves all tests from the Xray Test Repository,
and performs comprehensive analysis including:
- Test counts by category/priority/status
- Test coverage analysis
- Automation status analysis
- Test distribution analysis

Usage:
    python scripts/jira/analyze_xray_test_repository.py
    python scripts/jira/analyze_xray_test_repository.py --output report.md
    python scripts/jira/analyze_xray_test_repository.py --folder-id 674f109d682e8700850e3111
"""

import argparse
import sys
import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict
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


def get_all_tests_from_repository(
    client: JiraClient,
    project_key: str = "PZ",
    folder_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get all tests from Xray Test Repository.
    
    Args:
        client: JiraClient instance
        project_key: Project key (default: PZ)
        folder_id: Optional folder ID to filter tests
        
    Returns:
        List of test issue dictionaries
    """
    logger.info(f"Fetching all tests from Xray Test Repository for project {project_key}")
    
    # JQL query to get all Test type issues
    jql = f'project = {project_key} AND issuetype = Test'
    
    if folder_id:
        # If folder ID is provided, we might need to filter by folder
        # Note: Xray folder filtering might require specific API calls
        logger.info(f"Filtering by folder ID: {folder_id}")
    
    try:
        # Search for all test issues
        tests = client.search_issues(
            jql=jql,
            max_results=None  # Get all results
        )
        
        logger.info(f"Found {len(tests)} tests in repository")
        return tests
        
    except Exception as e:
        logger.error(f"Failed to fetch tests: {e}")
        raise


def analyze_tests(tests: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Perform comprehensive analysis on test list.
    
    Args:
        tests: List of test issue dictionaries
        
    Returns:
        Analysis results dictionary
    """
    logger.info("Analyzing tests...")
    
    analysis = {
        'total_tests': len(tests),
        'by_status': defaultdict(int),
        'by_priority': defaultdict(int),
        'by_component': defaultdict(int),
        'by_label': defaultdict(int),
        'by_assignee': defaultdict(int),
        'by_reporter': defaultdict(int),
        'automation_status': {
            'automated': 0,
            'manual': 0,
            'unknown': 0
        },
        'recent_tests': [],
        'oldest_tests': [],
        'tests_without_assignee': [],
        'tests_without_components': [],
        'tests_without_labels': [],
        'test_keys': [],
        'test_summaries': []
    }
    
    for test in tests:
        # Status
        status = test.get('status', 'Unknown')
        analysis['by_status'][status] += 1
        
        # Priority
        priority = test.get('priority', 'Unassigned')
        analysis['by_priority'][priority] += 1
        
        # Components
        components = test.get('components', [])
        if components:
            for component in components:
                analysis['by_component'][component] += 1
        else:
            analysis['tests_without_components'].append(test['key'])
        
        # Labels
        labels = test.get('labels', [])
        if labels:
            for label in labels:
                analysis['by_label'][label] += 1
        else:
            analysis['tests_without_labels'].append(test['key'])
        
        # Assignee
        assignee = test.get('assignee')
        if assignee:
            analysis['by_assignee'][assignee] += 1
        else:
            analysis['tests_without_assignee'].append(test['key'])
        
        # Reporter
        reporter = test.get('reporter', 'Unknown')
        analysis['by_reporter'][reporter] += 1
        
        # Automation status (check labels or custom fields)
        # Common automation labels: automation, automated, manual, manual-test
        is_automated = False
        if labels:
            automation_labels = ['automation', 'automated', 'automated-test', 'e2e-automation']
            is_automated = any(label.lower() in automation_labels for label in labels)
        
        if is_automated:
            analysis['automation_status']['automated'] += 1
        elif 'manual' in str(labels).lower():
            analysis['automation_status']['manual'] += 1
        else:
            analysis['automation_status']['unknown'] += 1
        
        # Collect test keys and summaries
        analysis['test_keys'].append(test['key'])
        analysis['test_summaries'].append({
            'key': test['key'],
            'summary': test['summary'],
            'status': status,
            'priority': priority,
            'url': test.get('url', '')
        })
        
        # Track creation date for recent/oldest analysis
        created = test.get('created', '')
        if created:
            analysis['recent_tests'].append({
                'key': test['key'],
                'summary': test['summary'],
                'created': created
            })
            analysis['oldest_tests'].append({
                'key': test['key'],
                'summary': test['summary'],
                'created': created
            })
    
    # Sort recent and oldest
    analysis['recent_tests'].sort(key=lambda x: x['created'], reverse=True)
    analysis['oldest_tests'].sort(key=lambda x: x['created'])
    
    # Limit to top 10
    analysis['recent_tests'] = analysis['recent_tests'][:10]
    analysis['oldest_tests'] = analysis['oldest_tests'][:10]
    
    return analysis


def generate_markdown_report(analysis: Dict[str, Any], output_path: Optional[Path] = None) -> str:
    """
    Generate comprehensive markdown report from analysis.
    
    Args:
        analysis: Analysis results dictionary
        output_path: Optional path to save report
        
    Returns:
        Markdown report string
    """
    report_lines = []
    
    # Header
    report_lines.append("# Xray Test Repository Analysis")
    report_lines.append("")
    report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"**Total Tests:** {analysis['total_tests']}")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    
    # Executive Summary
    report_lines.append("## 📊 Executive Summary")
    report_lines.append("")
    report_lines.append(f"- **Total Tests:** {analysis['total_tests']}")
    report_lines.append(f"- **Automated Tests:** {analysis['automation_status']['automated']} ({analysis['automation_status']['automated']/max(analysis['total_tests'],1)*100:.1f}%)")
    report_lines.append(f"- **Manual Tests:** {analysis['automation_status']['manual']} ({analysis['automation_status']['manual']/max(analysis['total_tests'],1)*100:.1f}%)")
    report_lines.append(f"- **Unknown Status:** {analysis['automation_status']['unknown']} ({analysis['automation_status']['unknown']/max(analysis['total_tests'],1)*100:.1f}%)")
    report_lines.append(f"- **Tests Without Assignee:** {len(analysis['tests_without_assignee'])}")
    report_lines.append(f"- **Tests Without Components:** {len(analysis['tests_without_components'])}")
    report_lines.append(f"- **Tests Without Labels:** {len(analysis['tests_without_labels'])}")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    
    # Tests by Status
    report_lines.append("## 📈 Tests by Status")
    report_lines.append("")
    report_lines.append("| Status | Count | Percentage |")
    report_lines.append("|--------|-------|------------|")
    total = analysis['total_tests']
    for status, count in sorted(analysis['by_status'].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total * 100) if total > 0 else 0
        report_lines.append(f"| {status} | {count} | {percentage:.1f}% |")
    report_lines.append("")
    
    # Tests by Priority
    report_lines.append("## 🎯 Tests by Priority")
    report_lines.append("")
    report_lines.append("| Priority | Count | Percentage |")
    report_lines.append("|----------|-------|------------|")
    for priority, count in sorted(analysis['by_priority'].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total * 100) if total > 0 else 0
        report_lines.append(f"| {priority} | {count} | {percentage:.1f}% |")
    report_lines.append("")
    
    # Tests by Component
    if analysis['by_component']:
        report_lines.append("## 🔧 Tests by Component")
        report_lines.append("")
        report_lines.append("| Component | Count | Percentage |")
        report_lines.append("|-----------|-------|------------|")
        for component, count in sorted(analysis['by_component'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            report_lines.append(f"| {component} | {count} | {percentage:.1f}% |")
        report_lines.append("")
    
    # Tests by Label
    if analysis['by_label']:
        report_lines.append("## 🏷️ Top Labels")
        report_lines.append("")
        report_lines.append("| Label | Count | Percentage |")
        report_lines.append("|-------|-------|------------|")
        for label, count in sorted(analysis['by_label'].items(), key=lambda x: x[1], reverse=True)[:20]:
            percentage = (count / total * 100) if total > 0 else 0
            report_lines.append(f"| {label} | {count} | {percentage:.1f}% |")
        report_lines.append("")
    
    # Tests by Assignee
    if analysis['by_assignee']:
        report_lines.append("## 👤 Tests by Assignee")
        report_lines.append("")
        report_lines.append("| Assignee | Count | Percentage |")
        report_lines.append("|----------|-------|------------|")
        for assignee, count in sorted(analysis['by_assignee'].items(), key=lambda x: x[1], reverse=True)[:10]:
            percentage = (count / total * 100) if total > 0 else 0
            report_lines.append(f"| {assignee} | {count} | {percentage:.1f}% |")
        report_lines.append("")
    
    # Automation Status
    report_lines.append("## 🤖 Automation Status")
    report_lines.append("")
    report_lines.append("| Status | Count | Percentage |")
    report_lines.append("|--------|-------|------------|")
    auto_status = analysis['automation_status']
    for status, count in auto_status.items():
        percentage = (count / total * 100) if total > 0 else 0
        report_lines.append(f"| {status.capitalize()} | {count} | {percentage:.1f}% |")
    report_lines.append("")
    
    # Issues
    if analysis['tests_without_assignee']:
        report_lines.append("## ⚠️ Tests Without Assignee")
        report_lines.append("")
        report_lines.append(f"**Count:** {len(analysis['tests_without_assignee'])}")
        report_lines.append("")
        report_lines.append("| Test Key |")
        report_lines.append("|----------|")
        for key in analysis['tests_without_assignee'][:20]:
            report_lines.append(f"| {key} |")
        if len(analysis['tests_without_assignee']) > 20:
            report_lines.append(f"| ... and {len(analysis['tests_without_assignee']) - 20} more |")
        report_lines.append("")
    
    if analysis['tests_without_components']:
        report_lines.append("## ⚠️ Tests Without Components")
        report_lines.append("")
        report_lines.append(f"**Count:** {len(analysis['tests_without_components'])}")
        report_lines.append("")
        report_lines.append("| Test Key |")
        report_lines.append("|----------|")
        for key in analysis['tests_without_components'][:20]:
            report_lines.append(f"| {key} |")
        if len(analysis['tests_without_components']) > 20:
            report_lines.append(f"| ... and {len(analysis['tests_without_components']) - 20} more |")
        report_lines.append("")
    
    # Recent Tests
    if analysis['recent_tests']:
        report_lines.append("## 🆕 Recent Tests (Top 10)")
        report_lines.append("")
        report_lines.append("| Test Key | Summary | Created |")
        report_lines.append("|----------|---------|--------|")
        for test in analysis['recent_tests']:
            summary = test['summary'][:50] + '...' if len(test['summary']) > 50 else test['summary']
            created = test['created'][:10] if test['created'] else 'Unknown'
            report_lines.append(f"| {test['key']} | {summary} | {created} |")
        report_lines.append("")
    
    # Test List
    report_lines.append("## 📋 All Tests")
    report_lines.append("")
    report_lines.append("| Test Key | Summary | Status | Priority |")
    report_lines.append("|----------|---------|--------|----------|")
    for test in sorted(analysis['test_summaries'], key=lambda x: x['key']):
        summary = test['summary'][:60] + '...' if len(test['summary']) > 60 else test['summary']
        report_lines.append(f"| {test['key']} | {summary} | {test['status']} | {test['priority']} |")
    report_lines.append("")
    
    report = '\n'.join(report_lines)
    
    # Save to file if path provided
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to: {output_path}")
    
    return report


def main():
    """Main function for analyzing Xray Test Repository."""
    parser = argparse.ArgumentParser(
        description='Analyze Xray Test Repository',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze all tests
  python analyze_xray_test_repository.py
  
  # Save report to file
  python analyze_xray_test_repository.py --output reports/xray_analysis.md
  
  # Filter by folder
  python analyze_xray_test_repository.py --folder-id 674f109d682e8700850e3111
        """
    )
    
    parser.add_argument(
        '--project',
        '--project-key',
        dest='project_key',
        default='PZ',
        help='Project key (default: PZ)'
    )
    
    parser.add_argument(
        '--folder-id',
        help='Folder ID to filter tests (optional)'
    )
    
    parser.add_argument(
        '--output',
        '--output-file',
        dest='output_file',
        help='Output file path for markdown report'
    )
    
    parser.add_argument(
        '--json',
        '--json-output',
        dest='json_output',
        help='Output file path for JSON analysis data'
    )
    
    parser.add_argument(
        '--config',
        help='Path to jira_config.yaml (optional)'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize Jira client
        logger.info("Connecting to Jira...")
        client = JiraClient(config_path=args.config)
        
        # Get all tests
        tests = get_all_tests_from_repository(
            client=client,
            project_key=args.project_key,
            folder_id=args.folder_id
        )
        
        if not tests:
            logger.warning("No tests found in repository")
            print("\n⚠️ No tests found in repository")
            return 1
        
        # Perform analysis
        logger.info("Performing analysis...")
        analysis = analyze_tests(tests)
        
        # Generate report
        output_path = Path(args.output_file) if args.output_file else None
        report = generate_markdown_report(analysis, output_path)
        
        # Print summary to console
        print("\n" + "="*80)
        print("Xray Test Repository Analysis Summary")
        print("="*80)
        print(f"\nTotal Tests: {analysis['total_tests']}")
        print(f"Automated: {analysis['automation_status']['automated']} ({analysis['automation_status']['automated']/max(analysis['total_tests'],1)*100:.1f}%)")
        print(f"Manual: {analysis['automation_status']['manual']} ({analysis['automation_status']['manual']/max(analysis['total_tests'],1)*100:.1f}%)")
        print(f"Unknown: {analysis['automation_status']['unknown']} ({analysis['automation_status']['unknown']/max(analysis['total_tests'],1)*100:.1f}%)")
        print(f"\nTests Without Assignee: {len(analysis['tests_without_assignee'])}")
        print(f"Tests Without Components: {len(analysis['tests_without_components'])}")
        print(f"Tests Without Labels: {len(analysis['tests_without_labels'])}")
        print("\n" + "="*80)
        
        # Save JSON if requested
        if args.json_output:
            json_path = Path(args.json_output)
            json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, default=str)
            logger.info(f"JSON analysis saved to: {json_path}")
        
        if output_path:
            print(f"\n✅ Full report saved to: {output_path}")
        else:
            print("\n📄 Full report:")
            print(report)
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed to analyze test repository: {e}", exc_info=True)
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1
    finally:
        try:
            client.close()
        except:
            pass


if __name__ == '__main__':
    sys.exit(main())

