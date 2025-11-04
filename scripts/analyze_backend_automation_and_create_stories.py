"""
Analyze Backend Automation Project and Create Stories
======================================================

This script:
1. Analyzes the backend automation project structure
2. Creates organized Stories based on the test content
3. Creates Tasks under each Story for what's done and what needs to be done
4. Updates statuses appropriately
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Set
import logging
import re

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


class BackendAutomationAnalyzer:
    """Analyze backend automation and create Jira stories."""
    
    def __init__(self, epic_key: str, tests_dir: Path):
        """Initialize analyzer."""
        self.epic_key = epic_key
        self.tests_dir = Path(tests_dir)
        self.jira_agent = JiraAgent()
        
        # Structure to hold analysis
        self.test_structure = {
            'api_tests': [],
            'kubernetes_tests': [],
            'grpc_tests': [],
            'data_validation_tests': [],
            'performance_tests': [],
            'infrastructure_tests': [],
            'other_tests': []
        }
    
    def analyze_project_structure(self) -> Dict[str, Any]:
        """Analyze the test project structure."""
        logger.info("Analyzing project structure...")
        
        if not self.tests_dir.exists():
            logger.error(f"Tests directory not found: {self.tests_dir}")
            return self.test_structure
        
        # Walk through test files
        for test_file in self.tests_dir.rglob("*.py"):
            if test_file.name.startswith("__"):
                continue
            
            relative_path = test_file.relative_to(self.tests_dir)
            
            # Categorize based on path and content
            category = self._categorize_test_file(test_file, relative_path)
            
            # Read file to understand what it does
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                test_info = {
                    'file': str(relative_path),
                    'full_path': str(test_file),
                    'category': category,
                    'has_tests': self._has_test_functions(content),
                    'test_count': self._count_test_functions(content),
                    'description': self._extract_description(content)
                }
                
                self.test_structure[category].append(test_info)
                
            except Exception as e:
                logger.warning(f"Could not read {test_file}: {e}")
        
        # Log summary
        for category, tests in self.test_structure.items():
            if tests:
                logger.info(f"{category}: {len(tests)} test files")
        
        return self.test_structure
    
    def _categorize_test_file(self, file_path: Path, relative_path: Path) -> str:
        """Categorize test file based on path and name."""
        path_str = str(relative_path).lower()
        name_lower = file_path.name.lower()
        
        # Kubernetes tests
        if 'k8s' in path_str or 'kubernetes' in path_str or 'k8s' in name_lower:
            return 'kubernetes_tests'
        
        # gRPC tests
        if 'grpc' in path_str or 'grpc' in name_lower or 'stream' in path_str:
            return 'grpc_tests'
        
        # API tests
        if 'api' in path_str or 'endpoint' in path_str or 'rest' in path_str:
            return 'api_tests'
        
        # Performance tests
        if 'performance' in path_str or 'load' in path_str or 'stress' in path_str:
            return 'performance_tests'
        
        # Data validation tests
        if 'validation' in path_str or 'data' in path_str or 'schema' in path_str:
            return 'data_validation_tests'
        
        # Infrastructure tests
        if 'infra' in path_str or 'infrastructure' in path_str or 'setup' in path_str:
            return 'infrastructure_tests'
        
        return 'other_tests'
    
    def _has_test_functions(self, content: str) -> bool:
        """Check if file has test functions."""
        test_patterns = [
            r'def test_\w+',
            r'class Test\w+',
            r'def \w+_test',
            r'@pytest\.mark'
        ]
        
        for pattern in test_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def _count_test_functions(self, content: str) -> int:
        """Count test functions in file."""
        test_pattern = r'def (test_\w+|\w+_test)'
        matches = re.findall(test_pattern, content, re.IGNORECASE)
        return len(matches)
    
    def _extract_description(self, content: str) -> str:
        """Extract description from docstring."""
        docstring_pattern = r'"""([^"]+)"""'
        match = re.search(docstring_pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()[:200]
        return ""
    
    def get_existing_stories(self) -> List[Dict[str, Any]]:
        """Get existing stories in epic."""
        try:
            jql = f'"Epic Link" = {self.epic_key} AND issuetype = Story'
            stories = self.jira_agent.search(jql=jql, max_results=500)
            logger.info(f"Found {len(stories)} existing stories in Epic {self.epic_key}")
            return stories
        except Exception as e:
            logger.error(f"Failed to get existing stories: {e}")
            return []
    
    def create_story_plan(self) -> List[Dict[str, Any]]:
        """Create plan for stories based on analysis."""
        stories_plan = []
        
        # API Tests Story
        if self.test_structure['api_tests']:
            stories_plan.append({
                'summary': 'API Endpoint Tests - Focus Server',
                'description': self._create_api_story_description(),
                'category': 'api_tests',
                'tests': self.test_structure['api_tests']
            })
        
        # Kubernetes Tests Story
        if self.test_structure['kubernetes_tests']:
            stories_plan.append({
                'summary': 'Kubernetes Orchestration Tests',
                'description': self._create_k8s_story_description(),
                'category': 'kubernetes_tests',
                'tests': self.test_structure['kubernetes_tests']
            })
        
        # gRPC Tests Story
        if self.test_structure['grpc_tests']:
            stories_plan.append({
                'summary': 'gRPC Stream Validation Tests',
                'description': self._create_grpc_story_description(),
                'category': 'grpc_tests',
                'tests': self.test_structure['grpc_tests']
            })
        
        # Data Validation Tests Story
        if self.test_structure['data_validation_tests']:
            stories_plan.append({
                'summary': 'Data Validation and Schema Tests',
                'description': self._create_data_validation_story_description(),
                'category': 'data_validation_tests',
                'tests': self.test_structure['data_validation_tests']
            })
        
        # Performance Tests Story
        if self.test_structure['performance_tests']:
            stories_plan.append({
                'summary': 'Performance and Load Tests',
                'description': self._create_performance_story_description(),
                'category': 'performance_tests',
                'tests': self.test_structure['performance_tests']
            })
        
        # Infrastructure Tests Story
        if self.test_structure['infrastructure_tests']:
            stories_plan.append({
                'summary': 'Infrastructure and Setup Tests',
                'description': self._create_infrastructure_story_description(),
                'category': 'infrastructure_tests',
                'tests': self.test_structure['infrastructure_tests']
            })
        
        return stories_plan
    
    def _create_api_story_description(self) -> str:
        """Create description for API tests story."""
        tests = self.test_structure['api_tests']
        total_tests = sum(t['test_count'] for t in tests)
        
        return f"""## 🎯 Goal
Comprehensive API endpoint testing for Focus Server backend.

## 📋 Scope
- API endpoint coverage and validation
- HTTP method testing (GET, POST, PUT, DELETE)
- Request/Response validation
- Error handling and status codes
- Authentication and authorization

## 📊 Test Coverage
- **Test Files:** {len(tests)}
- **Test Functions:** {total_tests}

## ✅ Acceptance Criteria
- [ ] All API endpoints have test coverage
- [ ] All HTTP methods are tested
- [ ] Error scenarios are covered
- [ ] Response validation is implemented
- [ ] Tests are integrated with CI/CD

## 📁 Test Files
{chr(10).join(f"- `{t['file']}` ({t['test_count']} tests)" for t in tests[:10])}
"""
    
    def _create_k8s_story_description(self) -> str:
        """Create description for Kubernetes tests story."""
        tests = self.test_structure['kubernetes_tests']
        total_tests = sum(t['test_count'] for t in tests)
        
        return f"""## 🎯 Goal
Kubernetes orchestration and resource management testing for Focus Server.

## 📋 Scope
- Pod health and monitoring
- Resource management (CPU, Memory)
- Deployment and scaling
- Service discovery
- ConfigMap and Secret management

## 📊 Test Coverage
- **Test Files:** {len(tests)}
- **Test Functions:** {total_tests}

## ✅ Acceptance Criteria
- [ ] Pod health monitoring tests implemented
- [ ] Resource management tests complete
- [ ] Deployment and scaling tests working
- [ ] Service discovery tests validated
- [ ] ConfigMap/Secret tests implemented

## 📁 Test Files
{chr(10).join(f"- `{t['file']}` ({t['test_count']} tests)" for t in tests[:10])}
"""
    
    def _create_grpc_story_description(self) -> str:
        """Create description for gRPC tests story."""
        tests = self.test_structure['grpc_tests']
        total_tests = sum(t['test_count'] for t in tests)
        
        return f"""## 🎯 Goal
gRPC stream validation and communication testing.

## 📋 Scope
- gRPC stream validation
- Message serialization/deserialization
- Stream handling and error recovery
- Connection management
- Performance of gRPC streams

## 📊 Test Coverage
- **Test Files:** {len(tests)}
- **Test Functions:** {total_tests}

## ✅ Acceptance Criteria
- [ ] gRPC stream validation framework implemented
- [ ] Stream handling tests complete
- [ ] Error recovery tests implemented
- [ ] Connection management tests working
- [ ] Performance tests validated

## 📁 Test Files
{chr(10).join(f"- `{t['file']}` ({t['test_count']} tests)" for t in tests[:10])}
"""
    
    def _create_data_validation_story_description(self) -> str:
        """Create description for data validation tests story."""
        tests = self.test_structure['data_validation_tests']
        total_tests = sum(t['test_count'] for t in tests)
        
        return f"""## 🎯 Goal
Data validation and schema testing for Focus Server.

## 📋 Scope
- Data schema validation
- Input validation
- Output validation
- Data integrity tests
- Schema compliance

## 📊 Test Coverage
- **Test Files:** {len(tests)}
- **Test Functions:** {total_tests}

## ✅ Acceptance Criteria
- [ ] Data schema validation implemented
- [ ] Input validation tests complete
- [ ] Output validation tests working
- [ ] Data integrity tests validated
- [ ] Schema compliance tests implemented

## 📁 Test Files
{chr(10).join(f"- `{t['file']}` ({t['test_count']} tests)" for t in tests[:10])}
"""
    
    def _create_performance_story_description(self) -> str:
        """Create description for performance tests story."""
        tests = self.test_structure['performance_tests']
        total_tests = sum(t['test_count'] for t in tests)
        
        return f"""## 🎯 Goal
Performance and load testing for Focus Server.

## 📋 Scope
- Load testing
- Stress testing
- Performance benchmarking
- Resource utilization
- Response time validation

## 📊 Test Coverage
- **Test Files:** {len(tests)}
- **Test Functions:** {total_tests}

## ✅ Acceptance Criteria
- [ ] Load testing framework implemented
- [ ] Stress tests complete
- [ ] Performance benchmarks established
- [ ] Resource utilization tests working
- [ ] Response time validation implemented

## 📁 Test Files
{chr(10).join(f"- `{t['file']}` ({t['test_count']} tests)" for t in tests[:10])}
"""
    
    def _create_infrastructure_story_description(self) -> str:
        """Create description for infrastructure tests story."""
        tests = self.test_structure['infrastructure_tests']
        total_tests = sum(t['test_count'] for t in tests)
        
        return f"""## 🎯 Goal
Infrastructure and setup testing.

## 📋 Scope
- Environment setup
- Infrastructure validation
- Configuration testing
- Deployment verification
- System health checks

## 📊 Test Coverage
- **Test Files:** {len(tests)}
- **Test Functions:** {total_tests}

## ✅ Acceptance Criteria
- [ ] Environment setup tests implemented
- [ ] Infrastructure validation complete
- [ ] Configuration tests working
- [ ] Deployment verification tests validated
- [ ] System health checks implemented

## 📁 Test Files
{chr(10).join(f"- `{t['file']}` ({t['test_count']} tests)" for t in tests[:10])}
"""
    
    def create_tasks_for_story(self, story: Dict[str, Any], tests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create tasks for a story based on test files."""
        tasks = []
        
        # Group tests by implementation status
        implemented_tests = [t for t in tests if t['has_tests'] and t['test_count'] > 0]
        pending_tests = [t for t in tests if not t['has_tests'] or t['test_count'] == 0]
        
        # Tasks for implemented tests
        if implemented_tests:
            for test in implemented_tests:
                tasks.append({
                    'summary': f"Test: {test['file']}",
                    'description': f"""Test file: `{test['file']}`

**Status:** ✅ Implemented

**Test Count:** {test['test_count']}

**Description:**
{test['description'] or 'No description available'}

**Full Path:** `{test['full_path']}`
""",
                    'status': 'Done',
                    'implemented': True
                })
        
        # Tasks for pending tests
        if pending_tests:
            for test in pending_tests:
                tasks.append({
                    'summary': f"Implement: {test['file']}",
                    'description': f"""Test file: `{test['file']}`

**Status:** ⏳ Pending Implementation

**Current State:** Test file exists but no tests implemented yet

**Full Path:** `{test['full_path']}`

**Next Steps:**
1. Analyze requirements for this test file
2. Implement test cases
3. Add test data and fixtures
4. Validate and execute tests
""",
                    'status': 'To Do',
                    'implemented': False
                })
        
        return tasks
    
    def process(self):
        """Main processing function."""
        logger.info("=" * 80)
        logger.info("Backend Automation Analysis and Story Creation")
        logger.info("=" * 80)
        
        # Analyze project
        self.analyze_project_structure()
        
        # Get existing stories
        existing_stories = self.get_existing_stories()
        existing_summaries = {s.get('summary', '').lower() for s in existing_stories}
        
        # Create story plan
        stories_plan = self.create_story_plan()
        
        logger.info(f"\nPlanned {len(stories_plan)} stories to create/update")
        
        # Process each story
        for story_plan in stories_plan:
            story_summary = story_plan['summary']
            
            # Check if story already exists
            existing_story = None
            for story in existing_stories:
                if story.get('summary', '').lower() == story_summary.lower():
                    existing_story = story
                    break
            
            if existing_story:
                logger.info(f"\nStory already exists: {existing_story['key']} - {story_summary}")
                story_key = existing_story['key']
            else:
                # Create new story
                logger.info(f"\nCreating new story: {story_summary}")
                try:
                    story = self.jira_agent.create_story(
                        summary=story_summary,
                        description=story_plan['description'],
                        priority="High",
                        labels=["backend", "automation", "focus-server"]
                    )
                    
                    # Link to epic
                    epic_link_field = 'customfield_10014'
                    try:
                        self.jira_agent.client.update_issue(
                            issue_key=story['key'],
                            **{epic_link_field: self.epic_key}
                        )
                    except:
                        pass
                    
                    story_key = story['key']
                    logger.info(f"Created story: {story_key}")
                except Exception as e:
                    logger.error(f"Failed to create story: {e}")
                    continue
            
            # Create tasks for this story
            tasks = self.create_tasks_for_story(
                existing_story or {'key': story_key},
                story_plan['tests']
            )
            
            # Get existing subtasks
            existing_subtasks = self.jira_agent.search(
                jql=f"parent = {story_key}",
                max_results=100
            )
            existing_task_summaries = {t.get('summary', '').lower() for t in existing_subtasks}
            
            # Create/update tasks
            for task in tasks:
                task_summary = task['summary']
                
                # Check if task exists
                existing_task = None
                for subtask in existing_subtasks:
                    if subtask.get('summary', '').lower() == task_summary.lower():
                        existing_task = subtask
                        break
                
                if existing_task:
                    # Update existing task status if needed
                    existing_status = existing_task.get('status', '').upper()
                    if task['status'] == 'Done' and existing_status != 'CLOSED' and existing_status != 'DONE':
                        try:
                            self.jira_agent.update_status(existing_task['key'], 'CLOSED')
                            logger.info(f"  Updated task {existing_task['key']} to CLOSED")
                        except:
                            try:
                                self.jira_agent.update_status(existing_task['key'], 'Done')
                                logger.info(f"  Updated task {existing_task['key']} to Done")
                            except Exception as e:
                                logger.warning(f"  Could not update task {existing_task['key']}: {e}")
                else:
                    # Create new task
                    try:
                        created_task = self.jira_agent.client.create_issue(
                            summary=task['summary'],
                            description=task['description'],
                            issue_type="Sub-task",
                            priority="Medium",
                            parent_key=story_key
                        )
                        
                        # Set initial status
                        if task['status'] == 'Done':
                            try:
                                self.jira_agent.update_status(created_task['key'], 'CLOSED')
                            except:
                                try:
                                    self.jira_agent.update_status(created_task['key'], 'Done')
                                except:
                                    pass
                        
                        logger.info(f"  Created task {created_task['key']}: {task_summary}")
                    except Exception as e:
                        logger.error(f"  Failed to create task {task_summary}: {e}")
            
            # Update story status based on tasks
            if existing_story:
                # Check if all tasks are done
                all_tasks = self.jira_agent.search(
                    jql=f"parent = {story_key}",
                    max_results=100
                )
                
                all_done = True
                for t in all_tasks:
                    status = t.get('status', '').upper()
                    if status not in ['CLOSED', 'DONE', 'RESOLVED']:
                        all_done = False
                        break
                
                if all_done and len(all_tasks) > 0:
                    story_status = existing_story.get('status', '').upper()
                    if story_status not in ['CLOSED', 'DONE']:
                        try:
                            self.jira_agent.update_status(story_key, 'CLOSED')
                            logger.info(f"  Updated story {story_key} to CLOSED (all tasks done)")
                        except:
                            try:
                                self.jira_agent.update_status(story_key, 'Done')
                                logger.info(f"  Updated story {story_key} to Done (all tasks done)")
                            except Exception as e:
                                logger.warning(f"  Could not update story status: {e}")


def main():
    """Main execution function."""
    epic_key = "PZ-14221"
    tests_dir = Path(r"C:\Projects\focus_server_automation\tests")
    
    analyzer = BackendAutomationAnalyzer(epic_key, tests_dir)
    analyzer.process()
    
    logger.info("\n" + "=" * 80)
    logger.info("Analysis complete!")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()

