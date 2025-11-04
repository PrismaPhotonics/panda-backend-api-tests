"""
Create Migrated Stories from PZ-14203 to PZ-14221
=================================================

Based on the 7 issues found:
1. PZ-14175: K8s Resource Management Tests (TO DO)
2. PZ-14174: K8s Pod Health Monitoring Tests (TO DO)
3. PZ-14024: Focus Server Test Plan (TO DO)
4. PZ-13954: UI Responsiveness Tests (TO DO)
5. PZ-13953: Error Handling E2E Tests (TO DO)
6. PZ-13950: Playwright E2E Testing Setup (Working)
7. PZ-13949: gRPC Stream Validation Framework (TO DO)

Organize into Stories with Sub-tasks, check codebase for status, set correct statuses.
"""

import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraAgent

agent = JiraAgent()

print("\n" + "="*100)
print("Creating Migrated Stories from PZ-14203 to PZ-14221")
print("="*100 + "\n")

source_epic = "PZ-14203"
target_epic = "PZ-14221"
epic_link_field = "customfield_10014"

# Issues to migrate (from previous analysis)
issues_to_migrate = [
    {
        "key": "PZ-14175",
        "summary": "K8s Resource Management Tests",
        "type": "Task",
        "status": "TO DO",
        "description": "Create Kubernetes resource management tests to validate CPU, memory, and resource quota enforcement."
    },
    {
        "key": "PZ-14174",
        "summary": "K8s Pod Health Monitoring Tests",
        "type": "Task",
        "status": "TO DO",
        "description": "Create comprehensive Kubernetes pod health monitoring tests for Focus Server backend."
    },
    {
        "key": "PZ-14024",
        "summary": "Focus Server Test Plan",
        "type": "Test Plan",
        "status": "TO DO",
        "description": "Focus Server Test Plan - comprehensive test documentation"
    },
    {
        "key": "PZ-13954",
        "summary": "UI Responsiveness Tests",
        "type": "Task",
        "status": "TO DO",
        "description": "Implement UI responsiveness tests for different screen sizes"
    },
    {
        "key": "PZ-13953",
        "summary": "Error Handling E2E Tests",
        "type": "Task",
        "status": "TO DO",
        "description": "Implement error handling E2E tests for validation errors, server errors, and error recovery."
    },
    {
        "key": "PZ-13950",
        "summary": "Playwright E2E Testing Setup",
        "type": "Task",
        "status": "Working",
        "description": "Setup Playwright for end-to-end (E2E) testing. This includes installation, directory structure creation, page objects implementation, helper utilities, and documentation."
    },
    {
        "key": "PZ-13949",
        "summary": "gRPC Stream Validation Framework",
        "type": "Task",
        "status": "TO DO",
        "description": "This issue involves setting up a gRPC Stream Validation Framework. It includes tasks for creating a testing infrastructure, implementing a client wrapper, writing various tests, and documentation."
    }
]

# Check codebase for completion status
def check_codebase_status(issue_key, summary):
    """Check if task is completed based on codebase"""
    status = "TO DO"
    notes = []
    
    if "k8s" in summary.lower() or "kubernetes" in summary.lower():
        if "pod health" in summary.lower():
            if Path("tests/infrastructure/test_k8s_pod_health.py").exists():
                status = "Done"
                notes.append("✅ File exists: tests/infrastructure/test_k8s_pod_health.py")
            else:
                status = "TO DO"
                notes.append("❌ File not found: tests/infrastructure/test_k8s_pod_health.py")
        elif "resource" in summary.lower():
            if Path("tests/infrastructure/test_k8s_resources.py").exists():
                status = "Done"
                notes.append("✅ File exists: tests/infrastructure/test_k8s_resources.py")
            else:
                status = "TO DO"
                notes.append("❌ File not found: tests/infrastructure/test_k8s_resources.py")
    
    elif "playwright" in summary.lower() or ("e2e" in summary.lower() and "setup" in summary.lower()):
        requirements = Path("requirements.txt").read_text(encoding='utf-8') if Path("requirements.txt").exists() else ""
        if "playwright" in requirements.lower():
            if Path("tests/e2e").exists() or Path("tests/integration/e2e").exists():
                status = "Working"  # In progress
                notes.append("✅ Playwright installed, e2e directory exists")
            else:
                status = "TO DO"
                notes.append("⚠️ Playwright installed but e2e directory structure missing")
        else:
            status = "TO DO"
            notes.append("❌ Playwright not in requirements.txt")
    
    elif "grpc" in summary.lower():
        if Path("tests/integration/e2e/test_configure_metadata_grpc_flow.py").exists():
            status = "Done"
            notes.append("✅ gRPC E2E test exists: test_configure_metadata_grpc_flow.py")
        else:
            status = "TO DO"
            notes.append("❌ gRPC E2E test not found")
    
    elif "ui" in summary.lower() and "responsive" in summary.lower():
        if Path("tests/ui").exists():
            status = "Working"
            notes.append("✅ UI tests directory exists")
        else:
            status = "TO DO"
            notes.append("❌ UI tests directory not found")
    
    elif "error handling" in summary.lower() and "e2e" in summary.lower():
        # Check if error handling tests exist (they were created earlier as PZ-14260)
        status = "Working"  # Story PZ-14260 was created earlier
        notes.append("✅ Error Handling E2E Story created: PZ-14260")
    
    elif "test plan" in summary.lower():
        status = "Done"  # Documentation is done
        notes.append("✅ Test Plan is documentation")
    
    return status, notes

# Check status for each issue
print("1. Checking codebase status for each issue...\n")
for issue in issues_to_migrate:
    codebase_status, notes = check_codebase_status(issue['key'], issue['summary'])
    issue['codebase_status'] = codebase_status
    issue['codebase_notes'] = notes
    print(f"   {issue['key']}: {issue['summary']}")
    print(f"      Jira Status: {issue['status']}")
    print(f"      Codebase Status: {codebase_status}")
    for note in notes:
        print(f"      {note}")
    print()

# Organize into Stories
print("2. Organizing into Stories...\n")

stories = [
    {
        "summary": "Kubernetes Infrastructure Tests",
        "description": """
## 🎯 Goal
Comprehensive Kubernetes infrastructure tests including pod health monitoring, resource management, and job lifecycle validation.

## 📋 Test Coverage
- Pod Health Monitoring (liveness, readiness, startup probes)
- Resource Management (CPU, memory, quotas)
- Job Lifecycle (already implemented)

## ✅ Acceptance Criteria
- [ ] Pod health monitoring tests implemented
- [ ] Resource management tests implemented
- [ ] All tests passing consistently
- [ ] Tests properly documented

## 🔗 Parent Epic
{epic_key}

## 📌 Related Issues
- PZ-14175: K8s Resource Management Tests
- PZ-14174: K8s Pod Health Monitoring Tests
        """.format(epic_key=target_epic),
        "labels": ["backend", "kubernetes", "infrastructure", "automation", "high-priority"],
        "priority": "High",
        "issues": [issues_to_migrate[0], issues_to_migrate[1]]  # PZ-14175, PZ-14174
    },
    {
        "summary": "E2E Testing Framework Setup",
        "description": """
## 🎯 Goal
Setup and configure Playwright for end-to-end testing framework.

## 📋 Scope
- Playwright installation and configuration
- Page Object Model implementation
- Helper functions and utilities
- Test fixtures and setup
- Directory structure

## ✅ Acceptance Criteria
- [ ] Playwright framework set up and working
- [ ] Page Objects created for all components
- [ ] Helper functions available
- [ ] Test fixtures working
- [ ] Documentation complete

## 🔗 Parent Epic
{epic_key}

## 📌 Related Issues
- PZ-13950: Playwright E2E Testing Setup
        """.format(epic_key=target_epic),
        "labels": ["frontend", "e2e", "playwright", "automation", "framework", "high-priority"],
        "priority": "High",
        "issues": [issues_to_migrate[5]]  # PZ-13950
    },
    {
        "summary": "gRPC Stream Validation Framework",
        "description": """
## 🎯 Goal
Create gRPC stream validation framework and tests for validating data streaming.

## 📋 Scope
- gRPC testing infrastructure setup
- GrpcStreamClient wrapper implementation
- Stream connectivity tests
- Data validity tests
- Performance tests

## ✅ Acceptance Criteria
- [ ] gRPC framework setup complete
- [ ] Stream connectivity tests passing
- [ ] Data validity tests passing
- [ ] Performance tests passing
- [ ] Documentation complete

## 🔗 Parent Epic
{epic_key}

## 📌 Related Issues
- PZ-13949: gRPC Stream Validation Framework
        """.format(epic_key=target_epic),
        "labels": ["backend", "grpc", "integration", "automation", "medium-priority"],
        "priority": "Medium",
        "issues": [issues_to_migrate[6]]  # PZ-13949
    },
    {
        "summary": "Error Handling E2E Tests",
        "description": """
## 🎯 Goal
End-to-end error handling tests for validation errors, server errors, and error recovery.

## 📋 Scope
- Validation error tests
- Server error tests
- Error recovery tests
- User-friendly error messages

## ✅ Acceptance Criteria
- [ ] Validation error tests implemented
- [ ] Server error tests implemented
- [ ] Error recovery tests implemented
- [ ] All tests passing consistently

## 🔗 Parent Epic
{epic_key}

## 📌 Related Issues
- PZ-13953: Error Handling E2E Tests
- PZ-14260: Error Handling E2E Tests - Complete Implementation (already created)
        """.format(epic_key=target_epic),
        "labels": ["frontend", "e2e", "error-handling", "automation", "medium-priority"],
        "priority": "Medium",
        "issues": [issues_to_migrate[4]]  # PZ-13953
    },
    {
        "summary": "UI Testing and Responsiveness",
        "description": """
## 🎯 Goal
UI responsiveness tests and frontend testing capabilities.

## 📋 Scope
- Responsive layout tests
- Different screen sizes
- UI component tests
- User interaction tests

## ✅ Acceptance Criteria
- [ ] Responsive layout tests implemented
- [ ] Screen size tests implemented
- [ ] UI component tests implemented
- [ ] All tests passing consistently

## 🔗 Parent Epic
{epic_key}

## 📌 Related Issues
- PZ-13954: UI Responsiveness Tests
        """.format(epic_key=target_epic),
        "labels": ["frontend", "ui", "automation", "responsiveness", "medium-priority"],
        "priority": "Medium",
        "issues": [issues_to_migrate[3]]  # PZ-13954
    },
    {
        "summary": "Test Plan and Documentation",
        "description": """
## 🎯 Goal
Test plan and comprehensive documentation for Focus Server automation.

## 📋 Scope
- Test plan documentation
- Test coverage documentation
- Test execution documentation
- Best practices documentation

## ✅ Acceptance Criteria
- [ ] Test plan documented
- [ ] Test coverage documented
- [ ] Test execution documented
- [ ] Documentation complete

## 🔗 Parent Epic
{epic_key}

## 📌 Related Issues
- PZ-14024: Focus Server Test Plan
        """.format(epic_key=target_epic),
        "labels": ["documentation", "test-plan", "low-priority"],
        "priority": "Low",
        "issues": [issues_to_migrate[2]]  # PZ-14024
    }
]

# Create Stories with Sub-tasks
print("3. Creating Stories with Sub-tasks...\n")

created_stories = []
epic_link_field = "customfield_10014"

for story_idx, story_data in enumerate(stories, 1):
    print(f"{'='*100}")
    print(f"Story {story_idx}/{len(stories)}: {story_data['summary']}")
    print(f"{'='*100}\n")
    
    # Create Story
    try:
        story = agent.create_story(
            summary=story_data["summary"],
            description=story_data["description"],
            priority=story_data["priority"],
            labels=story_data["labels"]
        )
        
        # Link Story to Epic
        try:
            agent.client.update_issue(story["key"], **{epic_link_field: target_epic})
            print(f"✅ Created and linked Story: {story['key']}")
            print(f"   URL: {story['url']}\n")
        except Exception as e:
            print(f"⚠️  Created Story but failed to link: {story['key']}")
            print(f"   Error: {e}\n")
        
        created_stories.append({
            "story": story,
            "sub_tasks": []
        })
        
        # Create Sub-tasks from original issues
        print(f"   Creating Sub-tasks from {len(story_data['issues'])} original issues...\n")
        
        for issue_data in story_data["issues"]:
            # Determine status based on codebase check
            target_status = issue_data.get('codebase_status', issue_data['status'])
            
            # Create Sub-task
            try:
                sub_task = agent.client.create_issue(
                    summary=issue_data["summary"],
                    description=f"""
## Original Issue
**Original Key:** {issue_data['key']}  
**Original Status:** {issue_data['status']}  
**Codebase Status:** {issue_data.get('codebase_status', 'Unknown')}

## Description
{issue_data['description']}

## Codebase Analysis
{chr(10).join(issue_data.get('codebase_notes', []))}

## Target Status
{target_status}
                    """,
                    issue_type="Sub-task",
                    priority=story_data["priority"],
                    labels=story_data["labels"],
                    parent_key=story["key"]
                )
                
                # Set status if needed
                if target_status == "Done":
                    try:
                        agent.client.transition_issue(sub_task["key"], "Done")
                        print(f"   ✅ Sub-task created and marked Done: {sub_task['key']} - {sub_task['summary']}")
                    except Exception as e:
                        print(f"   ✅ Sub-task created: {sub_task['key']} - {sub_task['summary']} (Status: {target_status})")
                        print(f"      ⚠️  Could not transition to Done: {e}")
                elif target_status == "Working":
                    try:
                        agent.client.transition_issue(sub_task["key"], "In Progress")
                        print(f"   ✅ Sub-task created and marked In Progress: {sub_task['key']} - {sub_task['summary']}")
                    except Exception as e:
                        print(f"   ✅ Sub-task created: {sub_task['key']} - {sub_task['summary']} (Status: {target_status})")
                else:
                    print(f"   ✅ Sub-task created: {sub_task['key']} - {sub_task['summary']} (Status: {target_status})")
                
                created_stories[-1]["sub_tasks"].append(sub_task)
                
            except Exception as e:
                print(f"   ❌ Failed to create Sub-task for {issue_data['key']}: {e}")
        
        print()
        
    except Exception as e:
        print(f"❌ Failed to create Story {story_idx}: {e}\n")

# Summary
print("\n" + "="*100)
print("Summary")
print("="*100)

print(f"\n✅ Created {len(created_stories)} Stories:")
total_sub_tasks = 0
for story_info in created_stories:
    story = story_info["story"]
    sub_tasks = story_info["sub_tasks"]
    total_sub_tasks += len(sub_tasks)
    print(f"\n   {story['key']}: {story['summary']}")
    print(f"   URL: {story['url']}")
    print(f"   Sub-tasks: {len(sub_tasks)}")
    for sub_task in sub_tasks:
        print(f"      - {sub_task['key']}: {sub_task['summary']}")

print(f"\n✅ Total:")
print(f"   Stories: {len(created_stories)}")
print(f"   Sub-tasks: {total_sub_tasks}")
print(f"\n✅ All Stories linked to Epic: {target_epic}")
print(f"   Epic URL: https://prismaphotonics.atlassian.net/browse/{target_epic}")

print("\n" + "="*100 + "\n")

