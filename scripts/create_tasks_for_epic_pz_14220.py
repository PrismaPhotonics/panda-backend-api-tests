"""
Create Tasks for Epic PZ-14220 Stories
=======================================

Go through all Stories in Epic PZ-14220 and create Tasks based on their definitions.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Remove scripts directory from path to avoid conflicts
scripts_dir = str(project_root / "scripts")
if scripts_dir in sys.path:
    sys.path.remove(scripts_dir)

from external.jira.jira_agent import JiraAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EpicTasksCreator:
    """Create tasks for Epic PZ-14220 stories."""
    
    def __init__(self, epic_key: str):
        """Initialize creator."""
        self.epic_key = epic_key
        self.jira_agent = JiraAgent()
    
    def get_all_stories(self) -> List[Dict[str, Any]]:
        """Get all stories linked to the epic."""
        try:
            jql = f'"Epic Link" = {self.epic_key} AND issuetype = Story'
            stories = self.jira_agent.search(jql=jql, max_results=500)
            logger.info(f"Found {len(stories)} stories in Epic {self.epic_key}")
            return stories
        except Exception as e:
            logger.error(f"Failed to get stories: {e}")
            return []
    
    def get_existing_subtasks(self, story_key: str) -> List[Dict[str, Any]]:
        """Get existing subtasks for a story."""
        try:
            jql = f"parent = {story_key}"
            subtasks = self.jira_agent.search(jql=jql, max_results=100)
            return subtasks
        except Exception as e:
            logger.warning(f"Failed to get subtasks for {story_key}: {e}")
            return []
    
    def parse_story_description(self, story: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Parse story description to extract tasks.
        
        Looks for:
        - Task lists (checkbox format)
        - Numbered lists
        - Acceptance criteria
        - Implementation steps
        """
        description = story.get('description', '')
        summary = story.get('summary', '')
        
        tasks = []
        
        if not description:
            logger.warning(f"No description for {story.get('key')}")
            return tasks
        
        # Split by lines
        lines = description.split('\n')
        
        current_section = None
        task_items = []
        
        for line in lines:
            line = line.strip()
            
            # Check for task markers
            if line.startswith('- [ ]') or line.startswith('* [ ]') or line.startswith('1. [ ]'):
                # Task item
                task_text = line.replace('- [ ]', '').replace('* [ ]', '').replace('1. [ ]', '').strip()
                if task_text:
                    task_items.append(task_text)
            
            elif line.startswith('- ') or line.startswith('* ') or (line.startswith('1. ') and not line.startswith('1. [')):
                # Regular list item that might be a task
                task_text = line.replace('- ', '').replace('* ', '').strip()
                if task_text and len(task_text) > 10:  # Filter out very short items
                    task_items.append(task_text)
            
            elif line.startswith('##') or line.startswith('###'):
                # Section header - save previous tasks if any
                if task_items:
                    tasks.extend([{'summary': item, 'section': current_section} for item in task_items])
                    task_items = []
                current_section = line.replace('#', '').strip()
            
            elif line.upper().startswith('ACCEPTANCE CRITERIA') or 'acceptance criteria' in line.lower():
                current_section = 'Acceptance Criteria'
        
        # Add remaining task items
        if task_items:
            tasks.extend([{'summary': item, 'section': current_section} for item in task_items])
        
        # If no tasks found, create default tasks based on story summary
        if not tasks:
            logger.info(f"No tasks found in description for {story.get('key')}, creating default tasks")
            # Create basic tasks based on story type
            if 'E2E' in summary or 'E2E' in summary.upper():
                tasks = [
                    {'summary': f'Setup test environment for {summary}', 'section': 'Setup'},
                    {'summary': f'Implement test cases for {summary}', 'section': 'Implementation'},
                    {'summary': f'Add test data and fixtures', 'section': 'Test Data'},
                    {'summary': f'Execute and validate tests', 'section': 'Validation'}
                ]
            elif 'Error Handling' in summary:
                tasks = [
                    {'summary': f'Identify error scenarios', 'section': 'Analysis'},
                    {'summary': f'Implement error handling tests', 'section': 'Implementation'},
                    {'summary': f'Validate error messages and recovery', 'section': 'Validation'}
                ]
            elif 'Live Mode' in summary:
                tasks = [
                    {'summary': f'Setup live mode test environment', 'section': 'Setup'},
                    {'summary': f'Implement live mode test cases', 'section': 'Implementation'},
                    {'summary': f'Validate live streaming', 'section': 'Validation'}
                ]
            elif 'Historic Mode' in summary:
                tasks = [
                    {'summary': f'Setup historic mode test environment', 'section': 'Setup'},
                    {'summary': f'Implement historic mode test cases', 'section': 'Implementation'},
                    {'summary': f'Validate historic data playback', 'section': 'Validation'}
                ]
            elif 'UI' in summary or 'UX' in summary:
                tasks = [
                    {'summary': f'Identify UI components to test', 'section': 'Analysis'},
                    {'summary': f'Implement UI test cases', 'section': 'Implementation'},
                    {'summary': f'Validate UI responsiveness', 'section': 'Validation'}
                ]
            else:
                # Generic tasks
                tasks = [
                    {'summary': f'Analyze requirements for {summary}', 'section': 'Analysis'},
                    {'summary': f'Implement test cases', 'section': 'Implementation'},
                    {'summary': f'Validate and test', 'section': 'Validation'}
                ]
        
        return tasks
    
    def create_task(self, story_key: str, task_summary: str, task_description: str = None, section: str = None) -> Dict[str, Any]:
        """Create a task under a story."""
        try:
            task = self.jira_agent.client.create_issue(
                summary=task_summary,
                description=task_description or f"Task for Story {story_key}\n\nSection: {section or 'General'}",
                issue_type="Sub-task",
                priority="Medium",
                parent_key=story_key
            )
            return task
        except Exception as e:
            logger.error(f"Failed to create task '{task_summary}' for {story_key}: {e}")
            return None
    
    def process_story(self, story: Dict[str, Any]) -> Dict[str, Any]:
        """Process a story and create tasks."""
        story_key = story.get('key')
        story_summary = story.get('summary', '')
        
        logger.info(f"\n{'=' * 80}")
        logger.info(f"Processing Story: {story_key} - {story_summary}")
        logger.info(f"{'=' * 80}")
        
        # Get existing subtasks
        existing_subtasks = self.get_existing_subtasks(story_key)
        existing_summaries = [st.get('summary', '').lower() for st in existing_subtasks]
        
        logger.info(f"Existing subtasks: {len(existing_subtasks)}")
        
        # Parse story description to get tasks
        tasks = self.parse_story_description(story)
        
        logger.info(f"Found {len(tasks)} tasks in description")
        
        # Create tasks
        created_tasks = []
        skipped_tasks = []
        
        for task_data in tasks:
            task_summary = task_data.get('summary', '').strip()
            section = task_data.get('section', '')
            
            if not task_summary:
                continue
            
            # Check if task already exists
            if task_summary.lower() in existing_summaries:
                logger.info(f"  [SKIP] Task already exists: {task_summary}")
                skipped_tasks.append(task_summary)
                continue
            
            # Create task
            task_description = f"Task extracted from Story {story_key} description.\n\n"
            if section:
                task_description += f"Section: {section}\n\n"
            task_description += f"Parent Story: [{story_key}|{story.get('url', '')}]"
            
            task = self.create_task(
                story_key=story_key,
                task_summary=task_summary,
                task_description=task_description,
                section=section
            )
            
            if task:
                created_tasks.append(task)
                logger.info(f"  [CREATED] {task.get('key')} - {task_summary}")
            else:
                logger.error(f"  [FAILED] Could not create task: {task_summary}")
        
        return {
            'story_key': story_key,
            'created': created_tasks,
            'skipped': skipped_tasks,
            'total_tasks': len(tasks)
        }
    
    def process_all_stories(self) -> Dict[str, Any]:
        """Process all stories in the epic."""
        results = {
            'stories_processed': 0,
            'total_tasks_created': 0,
            'total_tasks_skipped': 0,
            'story_results': []
        }
        
        # Get all stories
        stories = self.get_all_stories()
        
        if not stories:
            logger.warning(f"No stories found in Epic {self.epic_key}")
            return results
        
        # Process each story
        for story in stories:
            story_result = self.process_story(story)
            results['story_results'].append(story_result)
            results['stories_processed'] += 1
            results['total_tasks_created'] += len(story_result['created'])
            results['total_tasks_skipped'] += len(story_result['skipped'])
        
        return results


def main():
    """Main execution function."""
    epic_key = "PZ-14220"
    
    logger.info("=" * 80)
    logger.info(f"Create Tasks for Epic {epic_key} Stories")
    logger.info("=" * 80)
    
    creator = EpicTasksCreator(epic_key)
    
    # Process all stories
    results = creator.process_all_stories()
    
    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("Summary")
    logger.info("=" * 80)
    logger.info(f"Stories processed: {results['stories_processed']}")
    logger.info(f"Tasks created: {results['total_tasks_created']}")
    logger.info(f"Tasks skipped (already exist): {results['total_tasks_skipped']}")
    
    if results['story_results']:
        logger.info("\nPer-story breakdown:")
        for story_result in results['story_results']:
            logger.info(f"\n  Story: {story_result['story_key']}")
            logger.info(f"    Tasks created: {len(story_result['created'])}")
            logger.info(f"    Tasks skipped: {len(story_result['skipped'])}")
            if story_result['created']:
                logger.info("    Created tasks:")
                for task in story_result['created']:
                    logger.info(f"      - {task.get('key')}: {task.get('summary', 'N/A')}")


if __name__ == "__main__":
    main()

