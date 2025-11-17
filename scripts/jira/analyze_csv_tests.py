"""
Analyze CSV Test Files
=======================

Script to analyze Jira test CSV files and generate comprehensive analysis report.

Usage:
    python scripts/jira/analyze_csv_tests.py --files "file1.csv,file2.csv,file3.csv" --output report.md
"""

import argparse
import sys
import csv
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def read_csv_file(file_path: Path) -> List[Dict[str, Any]]:
    """
    Read CSV file and return list of test dictionaries.
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        List of test dictionaries
    """
    logger.info(f"Reading CSV file: {file_path}")
    
    tests = []
    
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Issue key'):  # Only process rows with issue keys
                    tests.append(row)
        
        logger.info(f"Found {len(tests)} tests in {file_path.name}")
        return tests
        
    except Exception as e:
        logger.error(f"Failed to read CSV file {file_path}: {e}")
        raise


def analyze_tests(tests: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Perform comprehensive analysis on test list.
    
    Args:
        tests: List of test dictionaries
        
    Returns:
        Analysis results dictionary
    """
    logger.info(f"Analyzing {len(tests)} tests...")
    
    analysis = {
        'total_tests': len(tests),
        'by_status': defaultdict(int),
        'by_priority': defaultdict(int),
        'by_assignee': defaultdict(int),
        'by_reporter': defaultdict(int),
        'by_creator': defaultdict(int),
        'by_category': defaultdict(int),
        'by_label': defaultdict(int),
        'tests_without_assignee': [],
        'tests_without_labels': [],
        'recent_tests': [],
        'oldest_tests': [],
        'test_keys': [],
        'test_summaries': []
    }
    
    for test in tests:
        # Status
        status = test.get('Status', 'Unknown')
        analysis['by_status'][status] += 1
        
        # Priority
        priority = test.get('Priority', 'Unassigned')
        analysis['by_priority'][priority] += 1
        
        # Assignee
        assignee = test.get('Assignee', '')
        if assignee:
            analysis['by_assignee'][assignee] += 1
        else:
            analysis['tests_without_assignee'].append(test.get('Issue key', 'Unknown'))
        
        # Reporter
        reporter = test.get('Reporter', 'Unknown')
        analysis['by_reporter'][reporter] += 1
        
        # Creator
        creator = test.get('Creator', 'Unknown')
        analysis['by_creator'][creator] += 1
        
        # Labels
        labels_str = test.get('Labels', '')
        if labels_str:
            labels = [label.strip() for label in labels_str.split(',') if label.strip()]
            for label in labels:
                analysis['by_label'][label] += 1
        else:
            key = test.get('Issue key', 'Unknown')
            if key not in analysis['tests_without_labels']:
                analysis['tests_without_labels'].append(key)
        
        # Categorize test
        summary = test.get('Summary', '')
        category = categorize_test(summary, labels_str)
        analysis['by_category'][category] += 1
        
        # Collect test keys and summaries
        key = test.get('Issue key', '')
        if key:
            analysis['test_keys'].append(key)
            analysis['test_summaries'].append({
                'key': key,
                'summary': summary,
                'status': status,
                'priority': priority,
                'assignee': assignee or 'Unassigned',
                'reporter': reporter,
                'creator': creator,
                'labels': labels_str,
                'created': test.get('Created', ''),
                'updated': test.get('Updated', '')
            })
            
            # Track creation date for recent/oldest analysis
            created = test.get('Created', '')
            if created:
                analysis['recent_tests'].append({
                    'key': key,
                    'summary': summary,
                    'created': created
                })
                analysis['oldest_tests'].append({
                    'key': key,
                    'summary': summary,
                    'created': created
                })
    
    # Sort recent and oldest
    analysis['recent_tests'].sort(key=lambda x: x['created'], reverse=True)
    analysis['oldest_tests'].sort(key=lambda x: x['created'])
    
    # Limit to top 20
    analysis['recent_tests'] = analysis['recent_tests'][:20]
    analysis['oldest_tests'] = analysis['oldest_tests'][:20]
    
    return analysis


def categorize_test(summary: str, labels: str) -> str:
    """Categorize test based on summary and labels."""
    summary_lower = summary.lower()
    labels_lower = labels.lower()
    
    if 'rl' in summary_lower or 'report' in summary_lower:
        return 'Report Lines (RLs)'
    elif 'alert' in summary_lower:
        return 'Alerts'
    elif 'investigation' in summary_lower or 'investigat' in summary_lower:
        return 'Investigation'
    elif 'analyze' in summary_lower or 'analyze' in summary_lower:
        return 'Analyze'
    elif 'template' in summary_lower:
        return 'Templates'
    elif 'filter' in summary_lower:
        return 'Filter'
    elif 'sort' in summary_lower or 'sorting' in summary_lower:
        return 'Sorting'
    elif 'map' in summary_lower:
        return 'Map'
    elif 'note' in summary_lower or 'notes' in summary_lower:
        return 'Notes'
    elif 'date' in summary_lower or 'time' in summary_lower or 'dst' in summary_lower:
        return 'Date/Time'
    elif 'live view' in summary_lower or 'live' in summary_lower:
        return 'Live View'
    elif 'history' in summary_lower or 'historic' in summary_lower:
        return 'History'
    elif 'bell' in summary_lower or 'notification' in summary_lower:
        return 'Notifications'
    elif 'status' in summary_lower:
        return 'Status'
    else:
        return 'Other'


def generate_markdown_report(analysis: Dict[str, Any], output_path: Optional[Path] = None) -> str:
    """Generate comprehensive markdown report from analysis."""
    report_lines = []
    
    # Header
    report_lines.append("# Jira Test CSV Analysis Report")
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
    report_lines.append(f"- **Tests Without Assignee:** {len(analysis['tests_without_assignee'])}")
    report_lines.append(f"- **Tests Without Labels:** {len(analysis['tests_without_labels'])}")
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
    
    # Tests by Category
    if analysis['by_category']:
        report_lines.append("## 📂 Tests by Category")
        report_lines.append("")
        report_lines.append("| Category | Count | Percentage |")
        report_lines.append("|----------|-------|------------|")
        for category, count in sorted(analysis['by_category'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            report_lines.append(f"| {category} | {count} | {percentage:.1f}% |")
        report_lines.append("")
    
    # Tests by Assignee
    if analysis['by_assignee']:
        report_lines.append("## 👤 Tests by Assignee")
        report_lines.append("")
        report_lines.append("| Assignee | Count | Percentage |")
        report_lines.append("|----------|-------|------------|")
        for assignee, count in sorted(analysis['by_assignee'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            report_lines.append(f"| {assignee} | {count} | {percentage:.1f}% |")
        report_lines.append("")
    
    # Tests by Reporter
    if analysis['by_reporter']:
        report_lines.append("## 📝 Tests by Reporter")
        report_lines.append("")
        report_lines.append("| Reporter | Count | Percentage |")
        report_lines.append("|----------|-------|------------|")
        for reporter, count in sorted(analysis['by_reporter'].items(), key=lambda x: x[1], reverse=True)[:10]:
            percentage = (count / total * 100) if total > 0 else 0
            report_lines.append(f"| {reporter} | {count} | {percentage:.1f}% |")
        report_lines.append("")
    
    # Tests by Creator
    if analysis['by_creator']:
        report_lines.append("## ✍️ Tests by Creator")
        report_lines.append("")
        report_lines.append("| Creator | Count | Percentage |")
        report_lines.append("|---------|-------|------------|")
        for creator, count in sorted(analysis['by_creator'].items(), key=lambda x: x[1], reverse=True)[:10]:
            percentage = (count / total * 100) if total > 0 else 0
            report_lines.append(f"| {creator} | {count} | {percentage:.1f}% |")
        report_lines.append("")
    
    # Top Labels
    if analysis['by_label']:
        report_lines.append("## 🏷️ Top Labels")
        report_lines.append("")
        report_lines.append("| Label | Count | Percentage |")
        report_lines.append("|-------|-------|------------|")
        for label, count in sorted(analysis['by_label'].items(), key=lambda x: x[1], reverse=True)[:20]:
            percentage = (count / total * 100) if total > 0 else 0
            report_lines.append(f"| {label} | {count} | {percentage:.1f}% |")
        report_lines.append("")
    
    # Issues
    if analysis['tests_without_assignee']:
        report_lines.append("## ⚠️ Tests Without Assignee")
        report_lines.append("")
        report_lines.append(f"**Count:** {len(analysis['tests_without_assignee'])}")
        report_lines.append("")
        report_lines.append("| Test Key |")
        report_lines.append("|----------|")
        for key in analysis['tests_without_assignee'][:30]:
            report_lines.append(f"| {key} |")
        if len(analysis['tests_without_assignee']) > 30:
            report_lines.append(f"| ... and {len(analysis['tests_without_assignee']) - 30} more |")
        report_lines.append("")
    
    # Recent Tests
    if analysis['recent_tests']:
        report_lines.append("## 🆕 Recent Tests (Top 20)")
        report_lines.append("")
        report_lines.append("| Test Key | Summary | Created |")
        report_lines.append("|----------|---------|--------|")
        for test in analysis['recent_tests']:
            summary = test['summary'][:50] + '...' if len(test['summary']) > 50 else test['summary']
            created = test['created'][:10] if test['created'] else 'Unknown'
            report_lines.append(f"| {test['key']} | {summary} | {created} |")
        report_lines.append("")
    
    # All Tests
    report_lines.append("## 📋 All Tests")
    report_lines.append("")
    report_lines.append("| Test Key | Summary | Status | Priority | Assignee | Category |")
    report_lines.append("|----------|---------|--------|----------|----------|----------|")
    for test in sorted(analysis['test_summaries'], key=lambda x: x['key']):
        summary = test['summary'][:60] + '...' if len(test['summary']) > 60 else test['summary']
        category = categorize_test(test['summary'], test.get('labels', ''))
        report_lines.append(f"| {test['key']} | {summary} | {test['status']} | {test['priority']} | {test['assignee']} | {category} |")
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
    """Main function for analyzing CSV test files."""
    parser = argparse.ArgumentParser(
        description='Analyze Jira test CSV files',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--files',
        required=True,
        help='Comma-separated list of CSV file paths'
    )
    
    parser.add_argument(
        '--output',
        '--output-file',
        dest='output_file',
        help='Output file path for markdown report'
    )
    
    args = parser.parse_args()
    
    try:
        # Parse file paths
        file_paths = [Path(f.strip()) for f in args.files.split(',')]
        
        # Read all CSV files
        all_tests = []
        for file_path in file_paths:
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                continue
            
            tests = read_csv_file(file_path)
            all_tests.extend(tests)
        
        if not all_tests:
            logger.warning("No tests found in CSV files")
            print("\n⚠️ No tests found in CSV files")
            return 1
        
        # Remove duplicates based on Issue key
        seen_keys = set()
        unique_tests = []
        for test in all_tests:
            key = test.get('Issue key', '')
            if key and key not in seen_keys:
                seen_keys.add(key)
                unique_tests.append(test)
        
        logger.info(f"Found {len(unique_tests)} unique tests (removed {len(all_tests) - len(unique_tests)} duplicates)")
        
        # Perform analysis
        logger.info("Performing analysis...")
        analysis = analyze_tests(unique_tests)
        
        # Generate report
        output_path = Path(args.output_file) if args.output_file else None
        report = generate_markdown_report(analysis, output_path)
        
        # Print summary
        print("\n" + "="*80)
        print("CSV Test Analysis Summary")
        print("="*80)
        print(f"\nTotal Tests: {analysis['total_tests']}")
        print(f"Tests Without Assignee: {len(analysis['tests_without_assignee'])}")
        print(f"Tests Without Labels: {len(analysis['tests_without_labels'])}")
        
        print("\nTop Categories:")
        for category, count in sorted(analysis['by_category'].items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {category}: {count}")
        
        print("\nTop Assignees:")
        for assignee, count in sorted(analysis['by_assignee'].items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {assignee}: {count}")
        
        print("\n" + "="*80)
        
        if output_path:
            print(f"\nFull report saved to: {output_path}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed to analyze CSV files: {e}", exc_info=True)
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

