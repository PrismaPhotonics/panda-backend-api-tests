"""
Analyze Xray Test Repository Folders
=====================================

Command-line script for analyzing tests in specific Xray Test Repository folders.

This script connects to Jira, retrieves all tests, and attempts to identify
which tests belong to specific folders based on test metadata.

Usage:
    python scripts/jira/analyze_xray_folders.py --folder-ids 674c55ccbaf7e0b87d2be730,67d7d7a878a0a2d1bfe6b650
    python scripts/jira/analyze_xray_folders.py --folder-ids 674c55ccbaf7e0b87d2be730 --output reports/folder1_analysis.md
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


def get_all_tests(client: JiraClient, project_key: str = "PZ") -> List[Dict[str, Any]]:
    """
    Get all tests from project.
    
    Args:
        client: JiraClient instance
        project_key: Project key (default: PZ)
        
    Returns:
        List of test issue dictionaries
    """
    logger.info(f"Fetching all tests from project {project_key}")
    
    jql = f'project = {project_key} AND issuetype = Test'
    
    try:
        tests = client.search_issues(
            jql=jql,
            max_results=None
        )
        
        logger.info(f"Found {len(tests)} tests in project")
        return tests
        
    except Exception as e:
        logger.error(f"Failed to fetch tests: {e}")
        raise


def get_test_details(client: JiraClient, test_key: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific test.
    
    Args:
        client: JiraClient instance
        test_key: Test issue key (e.g., "PZ-12345")
        
    Returns:
        Detailed test information dictionary
    """
    try:
        issue = client.jira.issue(test_key, expand='renderedFields')
        
        return {
            'key': issue.key,
            'summary': issue.fields.summary,
            'description': getattr(issue.fields, 'description', ''),
            'status': issue.fields.status.name,
            'priority': issue.fields.priority.name if issue.fields.priority else None,
            'labels': issue.fields.labels,
            'components': [c.name for c in issue.fields.components] if issue.fields.components else [],
            'assignee': issue.fields.assignee.displayName if issue.fields.assignee else None,
            'reporter': issue.fields.reporter.displayName if issue.fields.reporter else None,
            'created': issue.fields.created,
            'updated': issue.fields.updated,
            'url': f"{client.base_url}/browse/{issue.key}",
            'custom_fields': _extract_custom_fields(issue)
        }
    except Exception as e:
        logger.error(f"Failed to get test details for {test_key}: {e}")
        return None


def _extract_custom_fields(issue) -> Dict[str, Any]:
    """Extract custom fields from issue."""
    custom_fields = {}
    
    # Try to get Xray custom fields
    for field_name, field_value in issue.raw['fields'].items():
        if field_name.startswith('customfield_'):
            # Try to get field name
            field_info = issue.fields.__dict__.get(field_name, None)
            if field_info:
                custom_fields[field_name] = str(field_value)
    
    return custom_fields


def analyze_folder_tests(
    all_tests: List[Dict[str, Any]],
    folder_id: str,
    folder_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze tests that might belong to a specific folder.
    
    Note: Since Xray folder information is not directly available via Jira API,
    this function analyzes all tests and provides detailed information.
    For folder-specific analysis, manual verification or Xray API access is needed.
    
    Args:
        all_tests: List of all test dictionaries
        folder_id: Folder ID to analyze
        folder_name: Optional folder name
        
    Returns:
        Analysis results dictionary
    """
    logger.info(f"Analyzing tests for folder: {folder_id} ({folder_name or 'Unknown'})")
    
    # Since we can't directly filter by folder via Jira API,
    # we'll analyze all tests and provide detailed breakdown
    # The user can manually identify which tests belong to which folder
    
    analysis = {
        'folder_id': folder_id,
        'folder_name': folder_name or 'Unknown',
        'total_tests_analyzed': len(all_tests),
        'tests': [],
        'by_status': defaultdict(int),
        'by_priority': defaultdict(int),
        'by_category': defaultdict(int),
        'by_assignee': defaultdict(int),
        'by_label': defaultdict(int),
        'automation_status': {
            'automated': 0,
            'manual': 0,
            'unknown': 0
        }
    }
    
    for test in all_tests:
        # Add test to analysis
        analysis['tests'].append({
            'key': test['key'],
            'summary': test['summary'],
            'status': test.get('status', 'Unknown'),
            'priority': test.get('priority', 'Unknown'),
            'labels': test.get('labels', []),
            'components': test.get('components', []),
            'assignee': test.get('assignee'),
            'url': test.get('url', '')
        })
        
        # Count by status
        status = test.get('status', 'Unknown')
        analysis['by_status'][status] += 1
        
        # Count by priority
        priority = test.get('priority', 'Unknown')
        analysis['by_priority'][priority] += 1
        
        # Count by assignee
        assignee = test.get('assignee') or 'Unassigned'
        analysis['by_assignee'][assignee] += 1
        
        # Count by labels
        labels = test.get('labels', [])
        for label in labels:
            analysis['by_label'][label] += 1
        
        # Categorize by summary
        summary = test.get('summary', '')
        category = _categorize_test(summary, labels)
        analysis['by_category'][category] += 1
        
        # Automation status
        is_automated = _is_automated_test(labels)
        if is_automated:
            analysis['automation_status']['automated'] += 1
        elif 'manual' in str(labels).lower():
            analysis['automation_status']['manual'] += 1
        else:
            analysis['automation_status']['unknown'] += 1
    
    return analysis


def _categorize_test(summary: str, labels: List[str]) -> str:
    """Categorize test based on summary and labels."""
    summary_lower = summary.lower()
    labels_lower = ' '.join(labels).lower()
    
    if 'integration' in summary_lower or 'integration' in labels_lower:
        return 'Integration'
    elif 'api' in summary_lower or 'api' in labels_lower:
        return 'API'
    elif 'performance' in summary_lower or 'performance' in labels_lower:
        return 'Performance'
    elif 'data quality' in summary_lower or 'data_quality' in labels_lower:
        return 'Data Quality'
    elif 'infrastructure' in summary_lower or 'infrastructure' in labels_lower:
        return 'Infrastructure'
    elif 'security' in summary_lower or 'security' in labels_lower:
        return 'Security'
    elif 'load' in summary_lower or 'load' in labels_lower:
        return 'Load'
    elif 'stress' in summary_lower or 'stress' in labels_lower:
        return 'Stress'
    elif 'calculation' in summary_lower:
        return 'Calculation'
    elif 'historic' in summary_lower or 'historic' in labels_lower:
        return 'Historic Playback'
    elif 'singlechannel' in summary_lower:
        return 'SingleChannel'
    elif 'configuration' in summary_lower or 'validation' in summary_lower:
        return 'Configuration/Validation'
    else:
        return 'Other'


def _is_automated_test(labels: List[str]) -> bool:
    """Determine if test is automated based on labels."""
    automation_labels = ['automation', 'automated', 'automated-test', 'e2e-automation']
    labels_lower = ' '.join(labels).lower()
    return any(label in labels_lower for label in automation_labels)


def generate_folder_report(
    folder_analyses: List[Dict[str, Any]],
    output_path: Optional[Path] = None
) -> str:
    """
    Generate comprehensive markdown report for folder analyses.
    
    Args:
        folder_analyses: List of folder analysis dictionaries
        output_path: Optional path to save report
        
    Returns:
        Markdown report string
    """
    report_lines = []
    
    # Header
    report_lines.append("# Xray Test Repository - Folder Analysis")
    report_lines.append("")
    report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"**Folders Analyzed:** {len(folder_analyses)}")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    
    # Note about folder filtering
    report_lines.append("## ⚠️ Note on Folder Analysis")
    report_lines.append("")
    report_lines.append("Xray folder information is not directly available via Jira REST API.")
    report_lines.append("This analysis includes all tests from the project.")
    report_lines.append("To identify which tests belong to specific folders, manual verification")
    report_lines.append("in the Xray Test Repository UI or Xray REST API access is required.")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    
    # Analyze each folder
    for idx, analysis in enumerate(folder_analyses, 1):
        folder_id = analysis['folder_id']
        folder_name = analysis['folder_name']
        
        report_lines.append(f"## Folder {idx}: {folder_name}")
        report_lines.append("")
        report_lines.append(f"**Folder ID:** `{folder_id}`")
        report_lines.append(f"**Total Tests Analyzed:** {analysis['total_tests_analyzed']}")
        report_lines.append("")
        
        # Summary statistics
        report_lines.append("### 📊 Summary Statistics")
        report_lines.append("")
        report_lines.append(f"- **Total Tests:** {analysis['total_tests_analyzed']}")
        report_lines.append(f"- **Automated:** {analysis['automation_status']['automated']} ({analysis['automation_status']['automated']/max(analysis['total_tests_analyzed'],1)*100:.1f}%)")
        report_lines.append(f"- **Manual:** {analysis['automation_status']['manual']} ({analysis['automation_status']['manual']/max(analysis['total_tests_analyzed'],1)*100:.1f}%)")
        report_lines.append(f"- **Unknown:** {analysis['automation_status']['unknown']} ({analysis['automation_status']['unknown']/max(analysis['total_tests_analyzed'],1)*100:.1f}%)")
        report_lines.append("")
        
        # Tests by Status
        report_lines.append("### 📈 Tests by Status")
        report_lines.append("")
        report_lines.append("| Status | Count | Percentage |")
        report_lines.append("|--------|-------|------------|")
        total = analysis['total_tests_analyzed']
        for status, count in sorted(analysis['by_status'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            report_lines.append(f"| {status} | {count} | {percentage:.1f}% |")
        report_lines.append("")
        
        # Tests by Priority
        report_lines.append("### 🎯 Tests by Priority")
        report_lines.append("")
        report_lines.append("| Priority | Count | Percentage |")
        report_lines.append("|----------|-------|------------|")
        for priority, count in sorted(analysis['by_priority'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            report_lines.append(f"| {priority} | {count} | {percentage:.1f}% |")
        report_lines.append("")
        
        # Tests by Category
        if analysis['by_category']:
            report_lines.append("### 📂 Tests by Category")
            report_lines.append("")
            report_lines.append("| Category | Count | Percentage |")
            report_lines.append("|----------|-------|------------|")
            for category, count in sorted(analysis['by_category'].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total * 100) if total > 0 else 0
                report_lines.append(f"| {category} | {count} | {percentage:.1f}% |")
            report_lines.append("")
        
        # Tests by Assignee
        if analysis['by_assignee']:
            report_lines.append("### 👤 Tests by Assignee")
            report_lines.append("")
            report_lines.append("| Assignee | Count | Percentage |")
            report_lines.append("|----------|-------|------------|")
            for assignee, count in sorted(analysis['by_assignee'].items(), key=lambda x: x[1], reverse=True)[:10]:
                percentage = (count / total * 100) if total > 0 else 0
                report_lines.append(f"| {assignee} | {count} | {percentage:.1f}% |")
            report_lines.append("")
        
        # Top Labels
        if analysis['by_label']:
            report_lines.append("### 🏷️ Top Labels")
            report_lines.append("")
            report_lines.append("| Label | Count | Percentage |")
            report_lines.append("|-------|-------|------------|")
            for label, count in sorted(analysis['by_label'].items(), key=lambda x: x[1], reverse=True)[:15]:
                percentage = (count / total * 100) if total > 0 else 0
                report_lines.append(f"| {label} | {count} | {percentage:.1f}% |")
            report_lines.append("")
        
        # All Tests
        report_lines.append("### 📋 All Tests")
        report_lines.append("")
        report_lines.append("| Test Key | Summary | Status | Priority | Category |")
        report_lines.append("|----------|---------|--------|----------|----------|")
        
        for test in sorted(analysis['tests'], key=lambda x: x['key']):
            summary = test['summary'][:50] + '...' if len(test['summary']) > 50 else test['summary']
            category = _categorize_test(test['summary'], test.get('labels', []))
            report_lines.append(f"| {test['key']} | {summary} | {test['status']} | {test['priority']} | {category} |")
        
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
    
    # Comparison section
    if len(folder_analyses) > 1:
        report_lines.append("## 📊 Comparison Between Folders")
        report_lines.append("")
        report_lines.append("| Metric | " + " | ".join([f"Folder {i+1}" for i in range(len(folder_analyses))]) + " |")
        report_lines.append("|--------|" + "|".join(["---" for _ in folder_analyses]) + "|")
        
        report_lines.append(f"| Total Tests | " + " | ".join([str(a['total_tests_analyzed']) for a in folder_analyses]) + " |")
        report_lines.append(f"| Automated | " + " | ".join([str(a['automation_status']['automated']) for a in folder_analyses]) + " |")
        report_lines.append(f"| Manual | " + " | ".join([str(a['automation_status']['manual']) for a in folder_analyses]) + " |")
        report_lines.append(f"| Unknown | " + " | ".join([str(a['automation_status']['unknown']) for a in folder_analyses]) + " |")
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
    """Main function for analyzing Xray folders."""
    parser = argparse.ArgumentParser(
        description='Analyze Xray Test Repository folders',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze specific folders
  python analyze_xray_folders.py --folder-ids 674c55ccbaf7e0b87d2be730,67d7d7a878a0a2d1bfe6b650
  
  # Analyze with folder names
  python analyze_xray_folders.py --folder-ids 674c55ccbaf7e0b87d2be730 --folder-names "Folder 1"
  
  # Save report to file
  python analyze_xray_folders.py --folder-ids 674c55ccbaf7e0b87d2be730 --output reports/folder_analysis.md
        """
    )
    
    parser.add_argument(
        '--folder-ids',
        required=True,
        help='Comma-separated list of folder IDs to analyze'
    )
    
    parser.add_argument(
        '--folder-names',
        help='Comma-separated list of folder names (optional, same order as folder-ids)'
    )
    
    parser.add_argument(
        '--project',
        '--project-key',
        dest='project_key',
        default='PZ',
        help='Project key (default: PZ)'
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
        # Parse folder IDs
        folder_ids = [fid.strip() for fid in args.folder_ids.split(',')]
        
        # Parse folder names if provided
        folder_names = None
        if args.folder_names:
            folder_names = [name.strip() for name in args.folder_names.split(',')]
            if len(folder_names) != len(folder_ids):
                logger.warning("Number of folder names doesn't match number of folder IDs. Using folder IDs as names.")
                folder_names = None
        
        # Initialize Jira client
        logger.info("Connecting to Jira...")
        client = JiraClient(config_path=args.config)
        
        # Get all tests
        all_tests = get_all_tests(client, project_key=args.project_key)
        
        if not all_tests:
            logger.warning("No tests found in project")
            print("\n⚠️ No tests found in project")
            return 1
        
        # Analyze each folder
        folder_analyses = []
        for idx, folder_id in enumerate(folder_ids):
            folder_name = folder_names[idx] if folder_names and idx < len(folder_names) else f"Folder {idx+1}"
            
            logger.info(f"Analyzing folder {idx+1}/{len(folder_ids)}: {folder_id} ({folder_name})")
            
            # Note: Since we can't filter by folder via Jira API,
            # we analyze all tests and provide detailed breakdown
            analysis = analyze_folder_tests(all_tests, folder_id, folder_name)
            folder_analyses.append(analysis)
        
        # Generate report
        output_path = Path(args.output_file) if args.output_file else None
        report = generate_folder_report(folder_analyses, output_path)
        
        # Print summary
        print("\n" + "="*80)
        print("Xray Folder Analysis Summary")
        print("="*80)
        for idx, analysis in enumerate(folder_analyses, 1):
            print(f"\nFolder {idx}: {analysis['folder_name']} (ID: {analysis['folder_id']})")
            print(f"  Total Tests: {analysis['total_tests_analyzed']}")
            print(f"  Automated: {analysis['automation_status']['automated']} ({analysis['automation_status']['automated']/max(analysis['total_tests_analyzed'],1)*100:.1f}%)")
            print(f"  Manual: {analysis['automation_status']['manual']} ({analysis['automation_status']['manual']/max(analysis['total_tests_analyzed'],1)*100:.1f}%)")
            print(f"  Unknown: {analysis['automation_status']['unknown']} ({analysis['automation_status']['unknown']/max(analysis['total_tests_analyzed'],1)*100:.1f}%)")
        print("\n" + "="*80)
        
        # Save JSON if requested
        if args.json_output:
            json_path = Path(args.json_output)
            json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(folder_analyses, f, indent=2, default=str)
            logger.info(f"JSON analysis saved to: {json_path}")
        
        if output_path:
            print(f"\nFull report saved to: {output_path}")
        else:
            print("\nFull report:")
            print(report)
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed to analyze folders: {e}", exc_info=True)
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1
    finally:
        try:
            client.close()
        except:
            pass


if __name__ == '__main__':
    sys.exit(main())

