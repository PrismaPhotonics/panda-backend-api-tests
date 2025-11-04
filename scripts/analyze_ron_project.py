"""
Analyze Ron's Panda Test Automation Project
===========================================

This script analyzes Ron's project and compares it with Jira tickets
to update ticket status based on what has been implemented.

Author: QA Automation Architect
Date: 2025-11-04
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Set
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Remove scripts directory from path to avoid conflicts with jira package
scripts_dir = str(project_root / "scripts")
if scripts_dir in sys.path:
    sys.path.remove(scripts_dir)

# Import JiraAgent directly
from external.jira.jira_agent import JiraAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RonProjectAnalyzer:
    """Analyze Ron's Panda test automation project."""
    
    def __init__(self, ron_project_path: str):
        """
        Initialize analyzer.
        
        Args:
            ron_project_path: Path to Ron's project directory
        """
        self.ron_project_path = Path(ron_project_path)
        self.jira_agent = JiraAgent()
        
        # Get current user from Jira
        try:
            # Get current user account ID or email
            # Access the underlying jira client
            jira_client_instance = self.jira_agent.client
            current_user_info = jira_client_instance.jira.current_user()
            self.current_user_account_id = current_user_info.accountId
            self.current_user_email = getattr(current_user_info, 'emailAddress', None)
            self.current_user_display_name = current_user_info.displayName
            logger.info(f"Current Jira user: {self.current_user_display_name} ({self.current_user_account_id})")
        except Exception as e:
            logger.warning(f"Could not get current user: {e}")
            self.current_user_account_id = None
            self.current_user_email = None
            self.current_user_display_name = None
        
        # Track what has been implemented
        self.implemented_features = {
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
        
    def analyze_project(self) -> Dict[str, any]:
        """
        Analyze Ron's project and extract implemented features.
        
        Returns:
            Dict with analysis results
        """
        logger.info(f"Analyzing Ron's project: {self.ron_project_path}")
        
        # Analyze test files
        self._analyze_tests()
        
        # Analyze page objects/blocks
        self._analyze_blocks()
        
        # Create summary
        summary = self._create_summary()
        
        return summary
    
    def _analyze_tests(self):
        """Analyze test files to identify implemented features."""
        tests_dir = self.ron_project_path / "tests" / "panda"
        
        if not tests_dir.exists():
            logger.warning(f"Tests directory not found: {tests_dir}")
            return
        
        # Sanity tests
        sanity_dir = tests_dir / "sanity"
        if sanity_dir.exists():
            # Alerts tests
            alerts_tests = list(sanity_dir.glob("alerts/*.py"))
            if alerts_tests:
                self.implemented_features['alerts'].add('sanity_tests')
                logger.info(f"Found {len(alerts_tests)} alert sanity tests")
            
            # Login tests
            login_tests = list(sanity_dir.glob("login/*.py"))
            if login_tests:
                self.implemented_features['login'].add('sanity_tests')
                logger.info(f"Found {len(login_tests)} login sanity tests")
            
            # Map tests
            map_tests = list(sanity_dir.glob("map/*.py"))
            if map_tests:
                self.implemented_features['map'].add('sanity_tests')
                logger.info(f"Found {len(map_tests)} map sanity tests")
            
            # Investigations tests
            inv_tests = list(sanity_dir.glob("investigations/*.py"))
            if inv_tests:
                self.implemented_features['investigations'].add('sanity_tests')
                logger.info(f"Found {len(inv_tests)} investigation sanity tests")
            
            # Filter tests
            filter_tests = list(sanity_dir.glob("alerts/*Filter*.py"))
            if filter_tests:
                self.implemented_features['filters'].add('sanity_tests')
                logger.info(f"Found {len(filter_tests)} filter sanity tests")
            
            # Analysis templates tests
            template_tests = list(sanity_dir.glob("preDefinedAnalysisTemplates/*.py"))
            if template_tests:
                self.implemented_features['analysis_templates'].add('sanity_tests')
                logger.info(f"Found {len(template_tests)} analysis template tests")
            
            # Frequency filter tests
            freq_tests = list(sanity_dir.glob("frequencyFilter/*.py"))
            if freq_tests:
                self.implemented_features['frequency_filter'].add('sanity_tests')
                logger.info(f"Found {len(freq_tests)} frequency filter tests")
            
            # Analyze alert tests
            analyze_tests = list(sanity_dir.glob("analyze_alert/*.py"))
            if analyze_tests:
                self.implemented_features['alerts'].add('analyze_alert_tests')
                logger.info(f"Found {len(analyze_tests)} analyze alert tests")
        
        # Smoke tests
        smoke_dir = tests_dir / "smoke"
        if smoke_dir.exists():
            smoke_tests = list(smoke_dir.glob("*.py"))
            if smoke_tests:
                self.implemented_features['smoke_tests'].add('smoke_tests')
                logger.info(f"Found {len(smoke_tests)} smoke tests")
        
        # Regression tests
        regression_dir = tests_dir / "regression"
        if regression_dir.exists():
            regression_tests = list(regression_dir.glob("**/*.py"))
            if regression_tests:
                self.implemented_features['regression_tests'].add('regression_tests')
                logger.info(f"Found {len(regression_tests)} regression tests")
    
    def _analyze_blocks(self):
        """Analyze page objects/blocks to identify implemented features."""
        blocks_dir = self.ron_project_path / "blocksAndRepo" / "panda"
        
        if not blocks_dir.exists():
            logger.warning(f"Blocks directory not found: {blocks_dir}")
            return
        
        # Check for alert blocks
        if (blocks_dir / "alerts").exists():
            self.implemented_features['alerts'].add('page_objects')
            logger.info("Found alert page objects")
        
        # Check for login blocks
        if (blocks_dir / "login").exists():
            self.implemented_features['login'].add('page_objects')
            logger.info("Found login page objects")
        
        # Check for map blocks
        if (blocks_dir / "map").exists():
            self.implemented_features['map'].add('page_objects')
            logger.info("Found map page objects")
        
        # Check for investigator blocks
        if (blocks_dir / "investigator").exists():
            self.implemented_features['investigations'].add('page_objects')
            logger.info("Found investigator page objects")
    
    def _create_summary(self) -> Dict[str, any]:
        """Create summary of implemented features."""
        summary = {
            'total_features': len([f for f in self.implemented_features.values() if f]),
            'implemented_features': {},
            'test_coverage': {}
        }
        
        for feature, implementations in self.implemented_features.items():
            if implementations:
                summary['implemented_features'][feature] = list(implementations)
                summary['test_coverage'][feature] = len(implementations)
        
        return summary
    
    def search_jira_tickets(self, jql: str = None) -> List[Dict]:
        """
        Search for Jira tickets related to Panda automation.
        
        Args:
            jql: Custom JQL query (optional)
        
        Returns:
            List of issue dicts
        """
        if not jql:
            # Default JQL for Panda automation tickets
            jql = (
                "project = PZ AND "
                "(summary ~ 'Panda' OR summary ~ 'panda' OR "
                "summary ~ 'E2E' OR summary ~ 'e2e' OR "
                "summary ~ 'Frontend' OR summary ~ 'frontend' OR "
                "labels in (panda, frontend, e2e)) AND "
                "status != Done"
            )
        
        logger.info(f"Searching Jira with JQL: {jql}")
        issues = self.jira_agent.search(jql=jql, max_results=100)
        logger.info(f"Found {len(issues)} Jira tickets")
        
        return issues
    
    def compare_with_jira(self, issues: List[Dict]) -> Dict[str, any]:
        """
        Compare implemented features with Jira tickets.
        
        Args:
            issues: List of Jira issue dicts
        
        Returns:
            Dict with comparison results
        """
        comparison = {
            'completed': [],
            'in_progress': [],
            'not_started': [],
            'needs_update': []
        }
        
        for issue in issues:
            key = issue['key']
            summary = issue['summary'].lower()
            status = issue['status']
            issue_type = issue.get('issue_type', '').lower()
            
            # Skip bugs - DO NOT update bug tickets
            if issue_type == 'bug':
                logger.debug(f"Skipping bug ticket: {key} - {issue['summary']}")
                continue
            
            # Check if feature is implemented
            is_implemented = False
            feature_type = None
            
            if 'alert' in summary:
                is_implemented = 'alerts' in self.implemented_features and self.implemented_features['alerts']
                feature_type = 'alerts'
            elif 'login' in summary:
                is_implemented = 'login' in self.implemented_features and self.implemented_features['login']
                feature_type = 'login'
            elif 'map' in summary:
                is_implemented = 'map' in self.implemented_features and self.implemented_features['map']
                feature_type = 'map'
            elif 'investigation' in summary or 'investigate' in summary:
                is_implemented = 'investigations' in self.implemented_features and self.implemented_features['investigations']
                feature_type = 'investigations'
            elif 'filter' in summary:
                is_implemented = 'filters' in self.implemented_features and self.implemented_features['filters']
                feature_type = 'filters'
            elif 'template' in summary or 'analysis' in summary:
                is_implemented = 'analysis_templates' in self.implemented_features and self.implemented_features['analysis_templates']
                feature_type = 'analysis_templates'
            
            # Determine status
            if is_implemented and status != 'Done':
                comparison['needs_update'].append({
                    'key': key,
                    'summary': issue['summary'],
                    'current_status': status,
                    'should_be': 'Done',
                    'feature_type': feature_type
                })
            elif not is_implemented and status == 'Done':
                comparison['needs_update'].append({
                    'key': key,
                    'summary': issue['summary'],
                    'current_status': status,
                    'should_be': 'To Do',
                    'feature_type': feature_type
                })
            elif is_implemented:
                comparison['completed'].append({
                    'key': key,
                    'summary': issue['summary'],
                    'status': status
                })
            elif status == 'In Progress':
                comparison['in_progress'].append({
                    'key': key,
                    'summary': issue['summary'],
                    'status': status
                })
            else:
                comparison['not_started'].append({
                    'key': key,
                    'summary': issue['summary'],
                    'status': status
                })
        
        return comparison
    
    def update_jira_tickets(self, comparison: Dict[str, any]) -> Dict[str, any]:
        """
        Update Jira tickets based on comparison.
        
        Args:
            comparison: Comparison results from compare_with_jira
        
        Returns:
            Dict with update results
        """
        update_results = {
            'updated': [],
            'failed': [],
            'skipped': []
        }
        
        for ticket in comparison['needs_update']:
            key = ticket['key']
            current_status = ticket['current_status']
            should_be = ticket['should_be']
            
            # Get issue details to check issue type and reporter
            try:
                issue_details = self.jira_agent.get_issue(key)
                issue_type = issue_details.get('issue_type', '').lower()
                reporter = issue_details.get('reporter', '')
                
                # DO NOT update bug tickets
                if issue_type == 'bug':
                    logger.warning(f"Skipping bug ticket: {key} - {issue_details.get('summary', 'N/A')}")
                    update_results['skipped'].append({
                        'key': key,
                        'reason': 'Bug ticket - not updating'
                    })
                    continue
                
                # DO NOT update tickets that were not created by current user
                # Check if reporter matches current user
                if reporter and self.current_user_account_id:
                    # Need to get full issue to check reporter account ID
                    full_issue = self.jira_agent.client.jira.issue(key)
                    reporter_account_id = getattr(full_issue.fields.reporter, 'accountId', None)
                    
                    if reporter_account_id and reporter_account_id != self.current_user_account_id:
                        logger.warning(
                            f"Skipping ticket not created by current user: {key} - "
                            f"Reporter: {reporter}, Current user: {self.current_user_account_id}"
                        )
                        update_results['skipped'].append({
                            'key': key,
                            'reason': f'Ticket not created by current user (reporter: {reporter})'
                        })
                        continue
                elif reporter and not self.current_user_account_id:
                    # If we can't get current user account ID, skip all tickets
                    logger.warning(f"Could not verify current user - skipping {key}")
                    update_results['skipped'].append({
                        'key': key,
                        'reason': 'Could not verify current user'
                    })
                    continue
                    
            except Exception as e:
                logger.warning(f"Could not get issue details for {key}: {e}")
                # Skip this ticket if we can't verify it
                update_results['skipped'].append({
                    'key': key,
                    'reason': f'Could not get issue details: {e}'
                })
                continue
            
            try:
                if should_be == 'Done':
                    # Try different status transitions based on workflow
                    # For most tickets, use "CLOSED" or "QA Testing" as final status
                    target_status = None
                    try:
                        # Try CLOSED first (most common)
                        self.jira_agent.update_status(key, "CLOSED")
                        target_status = "CLOSED"
                    except:
                        try:
                            # Try QA Testing
                            self.jira_agent.update_status(key, "QA Testing")
                            target_status = "QA Testing"
                        except:
                            # Try Internal Testing
                            try:
                                self.jira_agent.update_status(key, "Internal Testing")
                                target_status = "Internal Testing"
                            except:
                                logger.warning(f"Could not transition {key} to any completion status")
                                update_results['skipped'].append({
                                    'key': key,
                                    'reason': 'No valid transition to completion status'
                                })
                                continue
                    
                    # Add comment
                    comment = (
                        f"✅ Feature implemented in Ron's Panda Test Automation project.\n"
                        f"Repository: https://github.com/PrismaPhotonics/panda-test-automation.git\n"
                        f"Feature type: {ticket.get('feature_type', 'N/A')}\n"
                        f"Status updated from '{current_status}' to '{target_status}'.\n"
                        f"Implemented features: {', '.join(self.implemented_features.get(ticket.get('feature_type', ''), []))}"
                    )
                    self.jira_agent.add_comment(key, comment)
                    
                    update_results['updated'].append({
                        'key': key,
                        'from': current_status,
                        'to': target_status
                    })
                    logger.info(f"Updated {key} from {current_status} to {target_status}")
                
                elif should_be == 'To Do':
                    # Update to To Do
                    self.jira_agent.update_status(key, "To Do")
                    
                    # Add comment
                    comment = (
                        f"⚠️ Feature not yet implemented in Ron's Panda Test Automation project.\n"
                        f"Status updated from '{current_status}' to 'To Do'.\n"
                        f"Please verify implementation status."
                    )
                    self.jira_agent.add_comment(key, comment)
                    
                    update_results['updated'].append({
                        'key': key,
                        'from': current_status,
                        'to': should_be
                    })
                    logger.info(f"Updated {key} from {current_status} to {should_be}")
                
            except Exception as e:
                logger.error(f"Failed to update {key}: {e}")
                update_results['failed'].append({
                    'key': key,
                    'error': str(e)
                })
        
        return update_results


def main():
    """Main execution function."""
    # Path to Ron's project
    ron_project_path = project_root / "ron_project"
    
    if not ron_project_path.exists():
        logger.error(f"Ron's project not found at: {ron_project_path}")
        logger.info("Please clone the project first:")
        logger.info("git clone https://github.com/PrismaPhotonics/panda-test-automation.git ron_project")
        return
    
    # Initialize analyzer
    analyzer = RonProjectAnalyzer(str(ron_project_path))
    
    # Analyze project
    logger.info("=" * 80)
    logger.info("Analyzing Ron's Panda Test Automation Project")
    logger.info("=" * 80)
    
    summary = analyzer.analyze_project()
    
    logger.info("\n" + "=" * 80)
    logger.info("Analysis Summary")
    logger.info("=" * 80)
    logger.info(f"Total features implemented: {summary['total_features']}")
    logger.info(f"Implemented features: {list(summary['implemented_features'].keys())}")
    
    # Search Jira tickets
    logger.info("\n" + "=" * 80)
    logger.info("Searching Jira Tickets")
    logger.info("=" * 80)
    
    issues = analyzer.search_jira_tickets()
    
    logger.info(f"Found {len(issues)} relevant Jira tickets")
    for issue in issues:
        logger.info(f"  - {issue['key']}: {issue['summary']} ({issue['status']})")
    
    # Compare with Jira
    logger.info("\n" + "=" * 80)
    logger.info("Comparing with Jira Tickets")
    logger.info("=" * 80)
    
    comparison = analyzer.compare_with_jira(issues)
    
    logger.info(f"Completed: {len(comparison['completed'])}")
    logger.info(f"In Progress: {len(comparison['in_progress'])}")
    logger.info(f"Not Started: {len(comparison['not_started'])}")
    logger.info(f"Needs Update: {len(comparison['needs_update'])}")
    
    if comparison['needs_update']:
        logger.info("\nTickets that need status update:")
        for ticket in comparison['needs_update']:
            logger.info(f"  - {ticket['key']}: {ticket['summary']}")
            logger.info(f"    Current: {ticket['current_status']} → Should be: {ticket['should_be']}")
    
    # Update Jira tickets
    if comparison['needs_update']:
        logger.info("\n" + "=" * 80)
        logger.info("Updating Jira Tickets")
        logger.info("=" * 80)
        
        update_results = analyzer.update_jira_tickets(comparison)
        
        logger.info(f"Updated: {len(update_results['updated'])}")
        logger.info(f"Failed: {len(update_results['failed'])}")
        
        if update_results['updated']:
            logger.info("\nSuccessfully updated tickets:")
            for result in update_results['updated']:
                logger.info(f"  - {result['key']}: {result['from']} → {result['to']}")
        
        if update_results['failed']:
            logger.error("\nFailed to update tickets:")
            for result in update_results['failed']:
                logger.error(f"  - {result['key']}: {result['error']}")
    
    logger.info("\n" + "=" * 80)
    logger.info("Analysis Complete")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()

