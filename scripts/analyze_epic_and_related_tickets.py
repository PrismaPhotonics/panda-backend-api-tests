"""
Analyze Epic and Related Tickets
=================================

This script analyzes an epic ticket (PZ-14220) and all its related tickets,
stories, and tasks, then compares them with Ron's automation project.

Author: QA Automation Architect
Date: 2025-11-04
"""

import sys
from pathlib import Path
from typing import Dict, List, Set, Any
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Remove scripts directory from path to avoid conflicts with jira package
scripts_dir = str(project_root / "scripts")
if scripts_dir in sys.path:
    sys.path.remove(scripts_dir)

from external.jira.jira_agent import JiraAgent
from external.jira.jira_client import JiraClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EpicAnalyzer:
    """Analyze epic and all related tickets."""
    
    def __init__(self, epic_key: str, ron_project_path: str):
        """
        Initialize analyzer.
        
        Args:
            epic_key: Epic issue key (e.g., PZ-14220)
            ron_project_path: Path to Ron's project directory
        """
        self.epic_key = epic_key
        self.ron_project_path = Path(ron_project_path)
        self.jira_agent = JiraAgent()
        self.jira_client = self.jira_agent.client
        
        # Get current user
        try:
            current_user_info = self.jira_client.jira.current_user()
            self.current_user_account_id = current_user_info.accountId
            self.current_user_display_name = current_user_info.displayName
            logger.info(f"Current Jira user: {self.current_user_display_name} ({self.current_user_account_id})")
        except Exception as e:
            logger.warning(f"Could not get current user: {e}")
            self.current_user_account_id = None
            self.current_user_display_name = None
        
        # Track what Ron has implemented
        self.ron_features = self._analyze_ron_project()
    
    def _analyze_ron_project(self) -> Dict[str, Set[str]]:
        """Analyze Ron's project to identify implemented features."""
        features = {
            'alerts': set(),
            'login': set(),
            'map': set(),
            'investigations': set(),
            'filters': set(),
            'analysis_templates': set(),
            'frequency_filter': set(),
            'smoke_tests': set(),
            'regression_tests': set()
        }
        
        tests_dir = self.ron_project_path / "tests" / "panda"
        
        if not tests_dir.exists():
            logger.warning(f"Tests directory not found: {tests_dir}")
            return features
        
        # Sanity tests
        sanity_dir = tests_dir / "sanity"
        if sanity_dir.exists():
            if list(sanity_dir.glob("alerts/*.py")):
                features['alerts'].add('sanity_tests')
            if list(sanity_dir.glob("login/*.py")):
                features['login'].add('sanity_tests')
            if list(sanity_dir.glob("map/*.py")):
                features['map'].add('sanity_tests')
            if list(sanity_dir.glob("investigations/*.py")):
                features['investigations'].add('sanity_tests')
            if list(sanity_dir.glob("alerts/*Filter*.py")):
                features['filters'].add('sanity_tests')
            if list(sanity_dir.glob("preDefinedAnalysisTemplates/*.py")):
                features['analysis_templates'].add('sanity_tests')
            if list(sanity_dir.glob("frequencyFilter/*.py")):
                features['frequency_filter'].add('sanity_tests')
            if list(sanity_dir.glob("analyze_alert/*.py")):
                features['alerts'].add('analyze_alert_tests')
        
        # Page objects
        blocks_dir = self.ron_project_path / "blocksAndRepo" / "panda"
        if blocks_dir.exists():
            if (blocks_dir / "alerts").exists():
                features['alerts'].add('page_objects')
            if (blocks_dir / "login").exists():
                features['login'].add('page_objects')
            if (blocks_dir / "map").exists():
                features['map'].add('page_objects')
            if (blocks_dir / "investigator").exists():
                features['investigations'].add('page_objects')
        
        return features
    
    def get_epic_details(self) -> Dict[str, Any]:
        """Get epic ticket details."""
        logger.info(f"Getting epic details: {self.epic_key}")
        epic = self.jira_agent.get_issue(self.epic_key)
        return epic
    
    def get_linked_issues(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get all linked issues."""
        try:
            issue = self.jira_client.jira.issue(issue_key, expand='changelog')
            linked_issues = []
            
            # Get issue links
            if hasattr(issue.fields, 'issuelinks'):
                for link in issue.fields.issuelinks:
                    if hasattr(link, 'outwardIssue'):
                        linked_issues.append({
                            'key': link.outwardIssue.key,
                            'type': link.type.outward,
                            'direction': 'outward'
                        })
                    if hasattr(link, 'inwardIssue'):
                        linked_issues.append({
                            'key': link.inwardIssue.key,
                            'type': link.type.inward,
                            'direction': 'inward'
                        })
            
            return linked_issues
        except Exception as e:
            logger.error(f"Failed to get linked issues for {issue_key}: {e}")
            return []
    
    def get_subtasks(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get all subtasks of an issue."""
        try:
            jql = f"parent = {issue_key}"
            subtasks = self.jira_agent.search(jql=jql, max_results=100)
            return subtasks
        except Exception as e:
            logger.error(f"Failed to get subtasks for {issue_key}: {e}")
            return []
    
    def get_stories_in_epic(self, epic_key: str) -> List[Dict[str, Any]]:
        """Get all stories in an epic."""
        try:
            # Try to get epic link custom field
            jql = f'"Epic Link" = {epic_key} OR parent = {epic_key}'
            stories = self.jira_agent.search(jql=jql, max_results=200)
            return stories
        except Exception as e:
            logger.error(f"Failed to get stories in epic {epic_key}: {e}")
            return []
    
    def get_all_related_tickets(self) -> Dict[str, Any]:
        """Get epic and all related tickets."""
        result = {
            'epic': None,
            'linked_issues': [],
            'stories': [],
            'all_tasks': [],
            'all_subtasks': []
        }
        
        # Get epic details
        result['epic'] = self.get_epic_details()
        logger.info(f"Epic: {result['epic']['summary']} ({result['epic']['status']})")
        
        # Get linked issues
        result['linked_issues'] = self.get_linked_issues(self.epic_key)
        logger.info(f"Found {len(result['linked_issues'])} linked issues")
        
        # Get stories in epic
        result['stories'] = self.get_stories_in_epic(self.epic_key)
        logger.info(f"Found {len(result['stories'])} stories in epic")
        
        # Get all tasks and subtasks
        all_issue_keys = [self.epic_key]
        all_issue_keys.extend([link['key'] for link in result['linked_issues']])
        all_issue_keys.extend([story['key'] for story in result['stories']])
        
        for issue_key in all_issue_keys:
            subtasks = self.get_subtasks(issue_key)
            result['all_subtasks'].extend(subtasks)
            logger.info(f"Found {len(subtasks)} subtasks for {issue_key}")
        
        # Get all tasks (issues with type = Task)
        try:
            jql = f"(parent in ({','.join(all_issue_keys)}) OR issue in ({','.join(all_issue_keys)})) AND issuetype = Task"
            tasks = self.jira_agent.search(jql=jql, max_results=200)
            result['all_tasks'] = tasks
            logger.info(f"Found {len(tasks)} tasks")
        except Exception as e:
            logger.error(f"Failed to get tasks: {e}")
        
        return result
    
    def match_with_ron_features(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """
        Match ticket with Ron's implemented features.
        
        Returns:
            Dict with match results
        """
        summary = ticket.get('summary', '').lower()
        description = ticket.get('description', '').lower()
        issue_type = ticket.get('issue_type', '').lower()
        
        match_result = {
            'implemented': False,
            'matched_features': [],
            'confidence': 'low'
        }
        
        # Check for different features
        if 'alert' in summary or 'alert' in description:
            if self.ron_features['alerts']:
                match_result['implemented'] = True
                match_result['matched_features'].append('alerts')
                match_result['confidence'] = 'high'
        
        if 'login' in summary or 'login' in description:
            if self.ron_features['login']:
                match_result['implemented'] = True
                match_result['matched_features'].append('login')
                match_result['confidence'] = 'high'
        
        if 'map' in summary or 'map' in description:
            if self.ron_features['map']:
                match_result['implemented'] = True
                match_result['matched_features'].append('map')
                match_result['confidence'] = 'high'
        
        if 'investigation' in summary or 'investigate' in summary or 'investigation' in description:
            if self.ron_features['investigations']:
                match_result['implemented'] = True
                match_result['matched_features'].append('investigations')
                match_result['confidence'] = 'high'
        
        if 'filter' in summary or 'filter' in description:
            if self.ron_features['filters'] or self.ron_features['frequency_filter']:
                match_result['implemented'] = True
                match_result['matched_features'].extend(['filters', 'frequency_filter'])
                match_result['confidence'] = 'high'
        
        if 'template' in summary or 'analysis' in summary or 'template' in description:
            if self.ron_features['analysis_templates']:
                match_result['implemented'] = True
                match_result['matched_features'].append('analysis_templates')
                match_result['confidence'] = 'high'
        
        return match_result
    
    def generate_report(self, related_tickets: Dict[str, Any]) -> str:
        """Generate comprehensive report."""
        report_lines = []
        
        report_lines.append("# דוח ניתוח Epic PZ-14220 והשוואה עם אוטומציה של רון")
        report_lines.append("## Analysis Report: Epic PZ-14220 vs Ron's Automation")
        report_lines.append("")
        report_lines.append(f"**תאריך:** 2025-11-04")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        
        # Epic details
        epic = related_tickets['epic']
        report_lines.append("## Epic Details")
        report_lines.append("")
        report_lines.append(f"**Key:** {epic['key']}")
        report_lines.append(f"**Summary:** {epic['summary']}")
        report_lines.append(f"**Status:** {epic['status']}")
        report_lines.append(f"**Type:** {epic['issue_type']}")
        report_lines.append(f"**URL:** {epic['url']}")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        
        # Stories
        report_lines.append("## Stories in Epic")
        report_lines.append("")
        if related_tickets['stories']:
            for story in related_tickets['stories']:
                match = self.match_with_ron_features(story)
                status_icon = "✅" if match['implemented'] else "❌"
                
                report_lines.append(f"### {status_icon} {story['key']}: {story['summary']}")
                report_lines.append(f"**Status:** {story['status']}")
                report_lines.append(f"**Type:** {story['issue_type']}")
                report_lines.append(f"**URL:** {story['url']}")
                
                if match['implemented']:
                    report_lines.append(f"**✅ Implemented by Ron:** Yes")
                    report_lines.append(f"**Matched Features:** {', '.join(match['matched_features'])}")
                    report_lines.append(f"**Confidence:** {match['confidence']}")
                else:
                    report_lines.append(f"**❌ Not Implemented by Ron:** No matching features found")
                
                report_lines.append("")
                
                # Get subtasks for this story
                story_subtasks = self.get_subtasks(story['key'])
                if story_subtasks:
                    report_lines.append(f"**Subtasks ({len(story_subtasks)}):**")
                    for subtask in story_subtasks:
                        subtask_match = self.match_with_ron_features(subtask)
                        subtask_status_icon = "✅" if subtask_match['implemented'] else "❌"
                        report_lines.append(f"- {subtask_status_icon} {subtask['key']}: {subtask['summary']} ({subtask['status']})")
                        if subtask_match['implemented']:
                            report_lines.append(f"  - Implemented: {', '.join(subtask_match['matched_features'])}")
                    report_lines.append("")
        else:
            report_lines.append("No stories found in epic.")
        report_lines.append("")
        
        # Tasks
        report_lines.append("## Tasks")
        report_lines.append("")
        if related_tickets['all_tasks']:
            implemented_tasks = []
            not_implemented_tasks = []
            
            for task in related_tickets['all_tasks']:
                match = self.match_with_ron_features(task)
                if match['implemented']:
                    implemented_tasks.append((task, match))
                else:
                    not_implemented_tasks.append((task, match))
            
            report_lines.append(f"### ✅ Implemented Tasks ({len(implemented_tasks)})")
            report_lines.append("")
            for task, match in implemented_tasks:
                report_lines.append(f"- **{task['key']}:** {task['summary']}")
                report_lines.append(f"  - Status: {task['status']}")
                report_lines.append(f"  - Matched Features: {', '.join(match['matched_features'])}")
                report_lines.append(f"  - URL: {task['url']}")
                report_lines.append("")
            
            report_lines.append(f"### ❌ Not Implemented Tasks ({len(not_implemented_tasks)})")
            report_lines.append("")
            for task, match in not_implemented_tasks:
                report_lines.append(f"- **{task['key']}:** {task['summary']}")
                report_lines.append(f"  - Status: {task['status']}")
                report_lines.append(f"  - URL: {task['url']}")
                report_lines.append("")
        else:
            report_lines.append("No tasks found.")
        report_lines.append("")
        
        # Subtasks
        report_lines.append("## Subtasks")
        report_lines.append("")
        if related_tickets['all_subtasks']:
            implemented_subtasks = []
            not_implemented_subtasks = []
            
            for subtask in related_tickets['all_subtasks']:
                match = self.match_with_ron_features(subtask)
                if match['implemented']:
                    implemented_subtasks.append((subtask, match))
                else:
                    not_implemented_subtasks.append((subtask, match))
            
            report_lines.append(f"### ✅ Implemented Subtasks ({len(implemented_subtasks)})")
            report_lines.append("")
            for subtask, match in implemented_subtasks:
                report_lines.append(f"- **{subtask['key']}:** {subtask['summary']}")
                report_lines.append(f"  - Status: {subtask['status']}")
                report_lines.append(f"  - Matched Features: {', '.join(match['matched_features'])}")
                report_lines.append(f"  - URL: {subtask['url']}")
                report_lines.append("")
            
            report_lines.append(f"### ❌ Not Implemented Subtasks ({len(not_implemented_subtasks)})")
            report_lines.append("")
            for subtask, match in not_implemented_subtasks:
                report_lines.append(f"- **{subtask['key']}:** {subtask['summary']}")
                report_lines.append(f"  - Status: {subtask['status']}")
                report_lines.append(f"  - URL: {subtask['url']}")
                report_lines.append("")
        else:
            report_lines.append("No subtasks found.")
        report_lines.append("")
        
        # Summary
        report_lines.append("## Summary")
        report_lines.append("")
        total_tickets = len(related_tickets['stories']) + len(related_tickets['all_tasks']) + len(related_tickets['all_subtasks'])
        implemented_count = sum([
            len([s for s in related_tickets['stories'] if self.match_with_ron_features(s)['implemented']]),
            len([t for t in related_tickets['all_tasks'] if self.match_with_ron_features(t)['implemented']]),
            len([st for st in related_tickets['all_subtasks'] if self.match_with_ron_features(st)['implemented']])
        ])
        
        report_lines.append(f"- **Total Tickets:** {total_tickets}")
        report_lines.append(f"- **Implemented by Ron:** {implemented_count}")
        report_lines.append(f"- **Not Implemented:** {total_tickets - implemented_count}")
        report_lines.append(f"- **Completion Rate:** {(implemented_count / total_tickets * 100) if total_tickets > 0 else 0:.1f}%")
        report_lines.append("")
        
        return "\n".join(report_lines)


def main():
    """Main execution function."""
    epic_key = "PZ-14220"
    ron_project_path = project_root / "ron_project"
    
    if not ron_project_path.exists():
        logger.error(f"Ron's project not found at: {ron_project_path}")
        return
    
    logger.info("=" * 80)
    logger.info("Analyzing Epic PZ-14220 and Related Tickets")
    logger.info("=" * 80)
    
    analyzer = EpicAnalyzer(epic_key, str(ron_project_path))
    
    # Get all related tickets
    related_tickets = analyzer.get_all_related_tickets()
    
    # Generate report
    report = analyzer.generate_report(related_tickets)
    
    # Save report
    report_file = project_root / "docs" / "06_project_management" / "jira" / f"EPIC_PZ-14220_ANALYSIS_{Path(__file__).stem}.md"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    logger.info(f"\nReport saved to: {report_file}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("Analysis Summary")
    print("=" * 80)
    print(report.split("## Summary")[-1])


if __name__ == "__main__":
    main()

