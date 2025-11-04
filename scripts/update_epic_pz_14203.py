"""
Update Epic PZ-14203 to contain only BE and FE Epics
====================================================

This script updates Epic PZ-14203 to contain only Backend (BE) and Frontend (FE) epics.

Author: QA Automation Architect
Date: 2025-11-04
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

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


class EpicPZ14203Updater:
    """Update Epic PZ-14203 to contain only BE and FE epics."""
    
    def __init__(self, epic_key: str):
        """Initialize updater."""
        self.epic_key = epic_key
        self.jira_agent = JiraAgent()
        self.jira_client = self.jira_agent.client
    
    def get_epic_details(self) -> Dict[str, Any]:
        """Get epic details."""
        epic = self.jira_agent.get_issue(self.epic_key)
        return epic
    
    def get_all_epics(self) -> List[Dict[str, Any]]:
        """Get all epics in the project."""
        try:
            # Search for all epics
            jql = "project = PZ AND issuetype = Epic"
            epics = self.jira_agent.search(jql=jql, max_results=500)
            logger.info(f"Found {len(epics)} epics in project")
            return epics
        except Exception as e:
            logger.error(f"Failed to get epics: {e}")
            return []
    
    def identify_be_fe_epics(self, epics: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Identify BE and FE automation epics.
        
        Only includes:
        - BE Epic: PZ-14221 - Backend Automation - Focus Server API Tests
        - FE Epic: PZ-14220 - Client/Frontend Automation - Panda App E2E Tests
        
        Returns:
            Dict with 'be_epics' and 'fe_epics' lists
        """
        be_epics = []
        fe_epics = []
        
        # Only the two automation epics
        target_be_epic = 'PZ-14221'
        target_fe_epic = 'PZ-14220'
        
        for epic in epics:
            epic_key = epic.get('key', '')
            summary = epic.get('summary', '').lower()
            
            # Check if it's the Backend Automation epic
            if epic_key == target_be_epic or \
               (target_be_epic in summary or 'backend automation' in summary):
                be_epics.append(epic)
                logger.info(f"BE Epic: {epic['key']} - {epic['summary']}")
            
            # Check if it's the Frontend Automation epic
            elif epic_key == target_fe_epic or \
                 (target_fe_epic in summary or ('client/frontend automation' in summary or 'frontend automation' in summary)):
                fe_epics.append(epic)
                logger.info(f"FE Epic: {epic['key']} - {epic['summary']}")
        
        return {
            'be_epics': be_epics,
            'fe_epics': fe_epics
        }
    
    def get_current_epic_links(self, epic_key: str) -> List[str]:
        """Get current epic links (sub-epics) of the main epic."""
        try:
            # Get all issues with Epic Link = PZ-14203
            jql = f'"Epic Link" = {epic_key}'
            linked_issues = self.jira_agent.search(jql=jql, max_results=500)
            
            # Filter only epics
            epic_keys = []
            for issue in linked_issues:
                if issue.get('issue_type', '').lower() == 'epic':
                    epic_keys.append(issue['key'])
            
            logger.info(f"Found {len(epic_keys)} epics currently linked to {epic_key}")
            return epic_keys
        
        except Exception as e:
            logger.error(f"Failed to get current epic links: {e}")
            return []
    
    def find_epic_link_field(self) -> Optional[str]:
        """Find Epic Link custom field ID."""
        try:
            fields = self.jira_client.jira.fields()
            for field in fields:
                if field['name'].lower() == 'epic link' or field['name'].lower() == 'epic':
                    logger.info(f"Found Epic Link field: {field['id']} ({field['name']})")
                    return field['id']
            
            # Try common field IDs
            common_fields = ['customfield_10014', 'customfield_10011']
            for field_id in common_fields:
                try:
                    # Test if field exists by trying to read it
                    test_issue = self.jira_client.jira.search_issues('project = PZ AND issuetype = Epic', maxResults=1)
                    if test_issue:
                        # Try to access the field
                        test = test_issue[0]
                        if hasattr(test.fields, field_id.replace('customfield_', '')):
                            logger.info(f"Found Epic Link field: {field_id}")
                            return field_id
                except:
                    continue
            
            logger.warning("Could not find Epic Link field automatically")
            return None
        
        except Exception as e:
            logger.error(f"Failed to find Epic Link field: {e}")
            return None
    
    def link_epic_to_parent(self, child_epic_key: str, parent_epic_key: str) -> bool:
        """
        Link child epic to parent epic using Epic Link custom field.
        
        Args:
            child_epic_key: Child epic key
            parent_epic_key: Parent epic key
        
        Returns:
            True if successful
        """
        try:
            # Find Epic Link field
            epic_link_field = self.find_epic_link_field()
            if not epic_link_field:
                # Try common IDs
                epic_link_field = 'customfield_10014'
            
            # Update Epic Link using JiraClient
            self.jira_client.update_issue(
                issue_key=child_epic_key,
                **{epic_link_field: parent_epic_key}
            )
            
            logger.info(f"Linked {child_epic_key} to {parent_epic_key}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to link {child_epic_key} to {parent_epic_key}: {e}")
            # Try alternative method
            try:
                issue = self.jira_client.jira.issue(child_epic_key)
                for field_id in ['customfield_10014', 'customfield_10011']:
                    try:
                        issue.update(fields={field_id: parent_epic_key})
                        logger.info(f"Linked {child_epic_key} to {parent_epic_key} using {field_id}")
                        return True
                    except:
                        continue
            except:
                pass
            return False
    
    def unlink_epic_from_parent(self, child_epic_key: str, parent_epic_key: str) -> bool:
        """Unlink epic from parent."""
        try:
            # Find Epic Link field
            epic_link_field = self.find_epic_link_field()
            if not epic_link_field:
                epic_link_field = 'customfield_10014'
            
            # Update Epic Link to None
            try:
                self.jira_client.update_issue(
                    issue_key=child_epic_key,
                    **{epic_link_field: None}
                )
            except:
                # Try direct update
                issue = self.jira_client.jira.issue(child_epic_key)
                for field_id in ['customfield_10014', 'customfield_10011']:
                    try:
                        issue.update(fields={field_id: None})
                        logger.info(f"Unlinked {child_epic_key} from {parent_epic_key}")
                        return True
                    except:
                        continue
            
            logger.info(f"Unlinked {child_epic_key} from {parent_epic_key}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to unlink {child_epic_key}: {e}")
            return False
    
    def update_epic_structure(self) -> Dict[str, Any]:
        """Update Epic PZ-14203 to contain only BE and FE epics."""
        results = {
            'be_epics_linked': [],
            'fe_epics_linked': [],
            'unlinked': [],
            'failed': []
        }
        
        # Get current epic
        epic = self.get_epic_details()
        logger.info(f"Epic: {epic['key']} - {epic['summary']}")
        
        # Get all epics
        all_epics = self.get_all_epics()
        
        # Identify BE and FE epics
        be_fe_epics = self.identify_be_fe_epics(all_epics)
        be_epics = be_fe_epics['be_epics']
        fe_epics = be_fe_epics['fe_epics']
        
        logger.info(f"Found {len(be_epics)} BE epics and {len(fe_epics)} FE epics")
        
        # Get current epic links
        current_links = self.get_current_epic_links(self.epic_key)
        
        # Link BE epics
        for be_epic in be_epics:
            be_key = be_epic['key']
            if be_key != self.epic_key:  # Don't link to itself
                if be_key not in current_links:
                    if self.link_epic_to_parent(be_key, self.epic_key):
                        results['be_epics_linked'].append(be_key)
                    else:
                        results['failed'].append(be_key)
        
        # Link FE epics
        for fe_epic in fe_epics:
            fe_key = fe_epic['key']
            if fe_key != self.epic_key:  # Don't link to itself
                if fe_key not in current_links:
                    if self.link_epic_to_parent(fe_key, self.epic_key):
                        results['fe_epics_linked'].append(fe_key)
                    else:
                        results['failed'].append(fe_key)
        
        # Unlink epics that are not BE or FE
        for linked_key in current_links:
            is_be = any(epic['key'] == linked_key for epic in be_epics)
            is_fe = any(epic['key'] == linked_key for epic in fe_epics)
            
            if not is_be and not is_fe:
                if self.unlink_epic_from_parent(linked_key, self.epic_key):
                    results['unlinked'].append(linked_key)
                else:
                    results['failed'].append(linked_key)
        
        return results


def main():
    """Main execution function."""
    epic_key = "PZ-14203"
    
    logger.info("=" * 80)
    logger.info(f"Update Epic {epic_key} to contain only BE and FE epics")
    logger.info("=" * 80)
    
    updater = EpicPZ14203Updater(epic_key)
    
    # Update epic structure
    results = updater.update_epic_structure()
    
    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("Summary")
    logger.info("=" * 80)
    logger.info(f"BE Epics linked: {len(results['be_epics_linked'])}")
    logger.info(f"FE Epics linked: {len(results['fe_epics_linked'])}")
    logger.info(f"Unlinked: {len(results['unlinked'])}")
    logger.info(f"Failed: {len(results['failed'])}")
    
    if results['be_epics_linked']:
        logger.info("\nBE Epics linked:")
        for key in results['be_epics_linked']:
            logger.info(f"  - {key}")
    
    if results['fe_epics_linked']:
        logger.info("\nFE Epics linked:")
        for key in results['fe_epics_linked']:
            logger.info(f"  - {key}")
    
    if results['unlinked']:
        logger.info("\nUnlinked epics:")
        for key in results['unlinked']:
            logger.info(f"  - {key}")


if __name__ == "__main__":
    main()

