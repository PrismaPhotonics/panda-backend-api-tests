"""
Deep Analysis of Epic PZ-14220
================================

Comprehensive analysis of all tickets under Epic PZ-14220
and comparison with Ron's automation project.

Author: QA Automation Architect
Date: 2025-11-04
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
import logging
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Remove scripts directory from path to avoid conflicts
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


class DeepEpicAnalyzer:
    """Deep analysis of epic and all related tickets."""
    
    def __init__(self, epic_key: str, ron_project_path: str):
        """Initialize analyzer."""
        self.epic_key = epic_key
        self.ron_project_path = Path(ron_project_path)
        self.jira_agent = JiraAgent()
        self.jira_client = self.jira_agent.client
        
        # Analyze Ron's project in detail
        self.ron_implementation = self._deep_analyze_ron_project()
    
    def _deep_analyze_ron_project(self) -> Dict[str, Any]:
        """Deep analysis of Ron's project - extract all test details."""
        implementation = {
            'test_files': {},
            'page_objects': {},
            'features': defaultdict(set),
            'test_methods': defaultdict(list),
            'capabilities': set()
        }
        
        # Analyze test files
        tests_dir = self.ron_project_path / "tests" / "panda"
        if tests_dir.exists():
            for test_file in tests_dir.rglob("*.py"):
                if test_file.name.startswith("test") or test_file.name.startswith("Test"):
                    self._analyze_test_file(test_file, implementation)
        
        # Analyze page objects
        blocks_dir = self.ron_project_path / "blocksAndRepo" / "panda"
        if blocks_dir.exists():
            for block_file in blocks_dir.rglob("*.py"):
                if not block_file.name.startswith("__"):
                    self._analyze_page_object(block_file, implementation)
        
        return implementation
    
    def _analyze_test_file(self, test_file: Path, implementation: Dict):
        """Analyze a test file to extract test methods and features."""
        try:
            content = test_file.read_text(encoding='utf-8')
            
            # Extract test methods
            test_methods = re.findall(r'def\s+(test_\w+)', content)
            
            # Extract features from content
            features = self._extract_features_from_content(content)
            
            # Get relative path
            rel_path = test_file.relative_to(self.ron_project_path)
            
            implementation['test_files'][str(rel_path)] = {
                'methods': test_methods,
                'features': features,
                'content_preview': content[:500]
            }
            
            for feature in features:
                implementation['features'][feature].add(str(rel_path))
                implementation['test_methods'][feature].extend(test_methods)
            
            logger.debug(f"Analyzed test file: {rel_path} - {len(test_methods)} tests, features: {features}")
        
        except Exception as e:
            logger.warning(f"Failed to analyze test file {test_file}: {e}")
    
    def _analyze_page_object(self, block_file: Path, implementation: Dict):
        """Analyze a page object file."""
        try:
            content = block_file.read_text(encoding='utf-8')
            
            # Extract class name
            class_match = re.search(r'class\s+(\w+)', content)
            class_name = class_match.group(1) if class_match else None
            
            # Extract methods
            methods = re.findall(r'def\s+(\w+)', content)
            
            # Get relative path
            rel_path = block_file.relative_to(self.ron_project_path)
            
            implementation['page_objects'][str(rel_path)] = {
                'class_name': class_name,
                'methods': methods,
                'content_preview': content[:500]
            }
            
            logger.debug(f"Analyzed page object: {rel_path} - class: {class_name}, {len(methods)} methods")
        
        except Exception as e:
            logger.warning(f"Failed to analyze page object {block_file}: {e}")
    
    def _extract_features_from_content(self, content: str) -> List[str]:
        """Extract features from test file content."""
        content_lower = content.lower()
        features = []
        
        # Map keywords to features
        feature_keywords = {
            'alert': 'alerts',
            'login': 'login',
            'map': 'map',
            'investigation': 'investigations',
            'investigate': 'investigations',
            'filter': 'filters',
            'template': 'analysis_templates',
            'frequency': 'frequency_filter',
            'analyze': 'analyze_alert',
            'live': 'live_mode',
            'historic': 'historic_mode',
            'panel': 'panel',
            'error': 'error_handling',
            'validation': 'validation',
            'recovery': 'error_recovery',
            'server': 'server_errors',
            'ui': 'ui_tests',
            'responsive': 'ui_responsive',
            'e2e': 'e2e',
            'playwright': 'playwright',
            'appium': 'appium'
        }
        
        for keyword, feature in feature_keywords.items():
            if keyword in content_lower:
                features.append(feature)
        
        return list(set(features))
    
    def get_all_tickets_in_epic(self) -> Dict[str, Any]:
        """Get all tickets (stories, tasks, subtasks) in epic."""
        result = {
            'epic': None,
            'stories': [],
            'tasks': [],
            'subtasks': [],
            'all_tickets': []
        }
        
        # Get epic details
        result['epic'] = self.jira_agent.get_issue(self.epic_key)
        logger.info(f"Epic: {result['epic']['summary']}")
        
        # Get all tickets with Epic Link = PZ-14220
        try:
            jql = f'"Epic Link" = {self.epic_key}'
            epic_tickets = self.jira_agent.search(jql=jql, max_results=500)
            logger.info(f"Found {len(epic_tickets)} tickets with Epic Link")
            
            for ticket in epic_tickets:
                issue_type = ticket.get('issue_type', '').lower()
                
                if issue_type == 'story':
                    result['stories'].append(ticket)
                elif issue_type == 'task':
                    result['tasks'].append(ticket)
                elif issue_type == 'sub-task':
                    result['subtasks'].append(ticket)
                
                result['all_tickets'].append(ticket)
        
        except Exception as e:
            logger.error(f"Failed to get epic tickets: {e}")
        
        # Get all subtasks of stories
        for story in result['stories']:
            try:
                subtasks = self.jira_agent.search(jql=f"parent = {story['key']}", max_results=100)
                result['subtasks'].extend(subtasks)
                result['all_tickets'].extend(subtasks)
                logger.info(f"Found {len(subtasks)} subtasks for {story['key']}")
            except Exception as e:
                logger.warning(f"Failed to get subtasks for {story['key']}: {e}")
        
        return result
    
    def match_ticket_with_ron(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """Match ticket requirements with Ron's implementation."""
        summary = ticket.get('summary', '').lower()
        description = ticket.get('description', '').lower()
        ticket_type = ticket.get('issue_type', '').lower()
        
        match_result = {
            'implemented': False,
            'confidence': 'low',
            'matched_features': [],
            'matched_test_files': [],
            'matched_test_methods': [],
            'missing_capabilities': [],
            'notes': []
        }
        
        # Extract requirements from ticket
        all_text = f"{summary} {description}".lower()
        requirements = self._extract_requirements(all_text)
        
        # Match with Ron's implementation
        matched_features = []
        matched_files = set()
        matched_methods = set()
        
        for req_feature in requirements:
            if req_feature in self.ron_implementation['features']:
                matched_features.append(req_feature)
                matched_files.update(self.ron_implementation['features'][req_feature])
                matched_methods.update(self.ron_implementation['test_methods'].get(req_feature, []))
        
        # Check for specific capabilities
        if 'playwright' in all_text or 'e2e' in all_text:
            if 'playwright' in self.ron_implementation['capabilities']:
                match_result['notes'].append("Playwright E2E framework found")
            else:
                match_result['missing_capabilities'].append("Playwright E2E framework")
                match_result['notes'].append("Using Appium instead of Playwright")
        
        if 'appium' in all_text:
            if 'appium' in self.ron_implementation['capabilities']:
                match_result['notes'].append("Appium framework found")
        
        # Determine if implemented
        if matched_features:
            match_result['implemented'] = True
            match_result['confidence'] = 'high' if len(matched_features) >= 2 else 'medium'
            match_result['matched_features'] = matched_features
            match_result['matched_test_files'] = list(matched_files)
            match_result['matched_test_methods'] = list(matched_methods)[:10]  # Limit to 10
        
        return match_result
    
    def _extract_requirements(self, text: str) -> List[str]:
        """Extract requirements/features from text."""
        requirements = []
        
        # Map keywords to requirements
        keyword_map = {
            'alert': 'alerts',
            'login': 'login',
            'map': 'map',
            'investigation': 'investigations',
            'investigate': 'investigations',
            'filter': 'filters',
            'template': 'analysis_templates',
            'frequency': 'frequency_filter',
            'analyze': 'analyze_alert',
            'live mode': 'live_mode',
            'historic mode': 'historic_mode',
            'historic': 'historic_mode',
            'panel': 'panel',
            'error handling': 'error_handling',
            'error recovery': 'error_recovery',
            'validation error': 'validation',
            'server error': 'server_errors',
            'ui test': 'ui_tests',
            'ui/ux': 'ui_tests',
            'responsive': 'ui_responsive',
            'configuration': 'configuration',
            'playback': 'playback',
            'controls': 'controls',
            'streaming': 'streaming',
            'navigation': 'navigation',
            'state management': 'state_management',
            'initialization': 'initialization',
            'reset': 'reset',
            'parameter': 'parameters',
            'form validation': 'form_validation'
        }
        
        for keyword, requirement in keyword_map.items():
            if keyword in text:
                requirements.append(requirement)
        
        return list(set(requirements))
    
    def generate_detailed_report(self, tickets: Dict[str, Any]) -> str:
        """Generate detailed report."""
        report_lines = []
        
        report_lines.append("# דוח ניתוח מעמיק - Epic PZ-14220")
        report_lines.append("## Deep Analysis Report: Epic PZ-14220 vs Ron's Automation")
        report_lines.append("")
        report_lines.append(f"**תאריך:** 2025-11-04")
        report_lines.append(f"**Ron's Repository:** https://github.com/PrismaPhotonics/panda-test-automation.git")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        
        # Epic details
        epic = tickets['epic']
        report_lines.append("## Epic Details")
        report_lines.append("")
        report_lines.append(f"**Key:** {epic['key']}")
        report_lines.append(f"**Summary:** {epic['summary']}")
        report_lines.append(f"**Status:** {epic['status']}")
        report_lines.append(f"**URL:** {epic['url']}")
        report_lines.append("")
        
        # Ron's implementation summary
        report_lines.append("## מה יש בפרויקט של רון")
        report_lines.append("")
        report_lines.append(f"- **Test Files:** {len(self.ron_implementation['test_files'])}")
        report_lines.append(f"- **Page Objects:** {len(self.ron_implementation['page_objects'])}")
        report_lines.append(f"- **Features Implemented:** {len(self.ron_implementation['features'])}")
        report_lines.append("")
        report_lines.append("### Features Implemented:")
        for feature, files in self.ron_implementation['features'].items():
            report_lines.append(f"- **{feature}:** {len(files)} test files")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        
        # Stories analysis
        report_lines.append("## Stories Analysis")
        report_lines.append("")
        
        implemented_stories = []
        not_implemented_stories = []
        
        for story in tickets['stories']:
            match = self.match_ticket_with_ron(story)
            
            if match['implemented']:
                implemented_stories.append((story, match))
            else:
                not_implemented_stories.append((story, match))
        
        report_lines.append(f"### ✅ Implemented Stories ({len(implemented_stories)})")
        report_lines.append("")
        for story, match in implemented_stories:
            report_lines.append(f"#### {story['key']}: {story['summary']}")
            report_lines.append(f"**Status:** {story['status']}")
            report_lines.append(f"**URL:** {story['url']}")
            report_lines.append(f"**Confidence:** {match['confidence']}")
            report_lines.append(f"**Matched Features:** {', '.join(match['matched_features'])}")
            if match['matched_test_files']:
                report_lines.append(f"**Test Files:** {', '.join(match['matched_test_files'][:5])}")
            if match['notes']:
                report_lines.append(f"**Notes:** {'; '.join(match['notes'])}")
            report_lines.append("")
        
        report_lines.append(f"### ❌ Not Implemented Stories ({len(not_implemented_stories)})")
        report_lines.append("")
        for story, match in not_implemented_stories:
            report_lines.append(f"#### {story['key']}: {story['summary']}")
            report_lines.append(f"**Status:** {story['status']}")
            report_lines.append(f"**URL:** {story['url']}")
            if match['missing_capabilities']:
                report_lines.append(f"**Missing:** {', '.join(match['missing_capabilities'])}")
            report_lines.append("")
        
        # Subtasks analysis
        report_lines.append("---")
        report_lines.append("## Subtasks Analysis")
        report_lines.append("")
        
        implemented_subtasks = []
        not_implemented_subtasks = []
        
        for subtask in tickets['subtasks']:
            match = self.match_ticket_with_ron(subtask)
            
            if match['implemented']:
                implemented_subtasks.append((subtask, match))
            else:
                not_implemented_subtasks.append((subtask, match))
        
        report_lines.append(f"### ✅ Implemented Subtasks ({len(implemented_subtasks)})")
        report_lines.append("")
        for subtask, match in implemented_subtasks:
            report_lines.append(f"- **{subtask['key']}:** {subtask['summary']}")
            report_lines.append(f"  - Status: {subtask['status']}")
            report_lines.append(f"  - Features: {', '.join(match['matched_features'])}")
            report_lines.append(f"  - URL: {subtask['url']}")
            report_lines.append("")
        
        report_lines.append(f"### ❌ Not Implemented Subtasks ({len(not_implemented_subtasks)})")
        report_lines.append("")
        for subtask, match in not_implemented_subtasks:
            report_lines.append(f"- **{subtask['key']}:** {subtask['summary']}")
            report_lines.append(f"  - Status: {subtask['status']}")
            if match['missing_capabilities']:
                report_lines.append(f"  - Missing: {', '.join(match['missing_capabilities'])}")
            report_lines.append(f"  - URL: {subtask['url']}")
            report_lines.append("")
        
        # Summary
        report_lines.append("---")
        report_lines.append("## Summary")
        report_lines.append("")
        total = len(tickets['stories']) + len(tickets['subtasks'])
        implemented = len(implemented_stories) + len(implemented_subtasks)
        
        report_lines.append(f"- **Total Stories:** {len(tickets['stories'])}")
        report_lines.append(f"- **Implemented Stories:** {len(implemented_stories)}")
        report_lines.append(f"- **Total Subtasks:** {len(tickets['subtasks'])}")
        report_lines.append(f"- **Implemented Subtasks:** {len(implemented_subtasks)}")
        report_lines.append(f"- **Total Tickets:** {total}")
        report_lines.append(f"- **Total Implemented:** {implemented}")
        report_lines.append(f"- **Completion Rate:** {(implemented / total * 100) if total > 0 else 0:.1f}%")
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
    logger.info("Deep Analysis of Epic PZ-14220")
    logger.info("=" * 80)
    
    analyzer = DeepEpicAnalyzer(epic_key, str(ron_project_path))
    
    # Get all tickets
    tickets = analyzer.get_all_tickets_in_epic()
    
    logger.info(f"Found {len(tickets['stories'])} stories, {len(tickets['subtasks'])} subtasks")
    
    # Generate report
    report = analyzer.generate_detailed_report(tickets)
    
    # Save report
    report_file = project_root / "docs" / "06_project_management" / "jira" / "EPIC_PZ-14220_DEEP_ANALYSIS.md"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    logger.info(f"\nReport saved to: {report_file}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("Deep Analysis Summary")
    print("=" * 80)
    print(report.split("## Summary")[-1])


if __name__ == "__main__":
    main()

