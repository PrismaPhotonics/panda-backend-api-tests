"""
Create Automation Epics Script
===============================

Creates two Epics:
1. Client/Frontend Automation Epic
2. Backend Automation Epic

Then creates Stories for Client Automation based on test tree structure.
"""

import sys
import io
from pathlib import Path

# Set UTF-8 encoding for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraAgent

# Initialize agent
agent = JiraAgent()

print("\n" + "="*100)
print("Creating Automation Epics and Stories")
print("="*100 + "\n")

# ============================================================================
# Create Epics
# ============================================================================

print("1. Creating Client/Frontend Automation Epic...")
client_epic = agent.client.create_issue(
    summary="Client/Frontend Automation - Panda App E2E Tests",
    description="""
## 🎯 Goal
Create comprehensive E2E automation tests for the Panda App client/frontend.

## 📋 Scope
- UI automation tests using Playwright
- E2E tests for Live Mode, Historic Mode, and Error Handling
- Panel tests based on test tree structure
- User interaction validation
- Visual regression testing

## 🔗 Related
- Epic parent: PZ-14203 (Focus Server & Panda Automation Project)
- Team: QA Automation Team (Ron David)
    """,
    issue_type="Epic",
    labels=["automation", "e2e", "frontend", "client", "panda-app"]
)

print(f"   ✅ Created Epic: {client_epic['key']}")
print(f"   URL: {client_epic['url']}\n")

print("2. Creating Backend Automation Epic...")
backend_epic = agent.client.create_issue(
    summary="Backend Automation - Focus Server API Tests",
    description="""
## 🎯 Goal
Create comprehensive automation tests for the Focus Server backend API.

## 📋 Scope
- API endpoint tests
- Integration tests
- Performance tests
- Infrastructure tests (MongoDB, RabbitMQ, K8s)
- Data quality tests
- Security tests

## 🔗 Related
- Epic parent: PZ-14203 (Focus Server & Panda Automation Project)
- Team: QA Automation Team
    """,
    issue_type="Epic",
    labels=["automation", "api", "backend", "focus-server"]
)

print(f"   ✅ Created Epic: {backend_epic['key']}")
print(f"   URL: {backend_epic['url']}\n")

# ============================================================================
# Create Stories for Client Automation
# ============================================================================

print("3. Creating Stories for Client Automation...\n")

# Define Stories based on test tree structure
client_stories = [
    {
        "summary": "Live Mode E2E Tests - Client Automation",
        "description": """
## 🎯 Goal
Implement E2E tests for Live Mode functionality in Panda App.

## 📋 Test Coverage
- Live Mode configuration
- Live streaming controls
- Canvas display and updates
- Frequency and channel axis validation
- Stop/pause/resume functionality

## 📎 Related Files
- `tests/e2e/test_live_mode.py`
- `tests/e2e/page_objects/panda_app_page.py`
- `tests/e2e/page_objects/configuration_panel.py`

## 🔗 Parent Epic
{epic_key}
        """.format(epic_key=client_epic['key']),
        "labels": ["automation", "e2e", "frontend", "live-mode"]
    },
    {
        "summary": "Historic Mode E2E Tests - Client Automation",
        "description": """
## 🎯 Goal
Implement E2E tests for Historic Mode functionality in Panda App.

## 📋 Test Coverage
- Historic Mode configuration
- Time range selection
- Playback controls
- Data visualization
- Navigation through historic data

## 📎 Related Files
- `tests/e2e/test_historic_mode.py`
- `tests/e2e/page_objects/panda_app_page.py`
- `tests/e2e/page_objects/historic_panel.py`

## 🔗 Parent Epic
{epic_key}
        """.format(epic_key=client_epic['key']),
        "labels": ["automation", "e2e", "frontend", "historic-mode"]
    },
    {
        "summary": "Error Handling E2E Tests - Client Automation",
        "description": """
## 🎯 Goal
Implement E2E tests for error handling in Panda App UI.

## 📋 Test Coverage
- Validation errors
- Server errors
- Error recovery
- User-friendly error messages
- Error state management

## 📎 Related Files
- `tests/e2e/test_error_handling.py`
- `tests/e2e/page_objects/panda_app_page.py`
- `tests/e2e/helpers/error_helpers.py`

## 🔗 Parent Epic
{epic_key}
        """.format(epic_key=client_epic['key']),
        "labels": ["automation", "e2e", "frontend", "error-handling"]
    },
    {
        "summary": "Panel Tests - Client Automation",
        "description": """
## 🎯 Goal
Implement E2E tests for Panel functionality based on test tree structure.

## 📋 Test Coverage
- Panel configuration
- Panel interactions
- Panel state management
- Panel validation

## 📎 Related Files
- `tests/e2e/test_panel.py`
- `tests/e2e/page_objects/panel.py`

## 🔗 Parent Epic
{epic_key}

## 📝 Note
This story is based on the test tree structure created by Tomer.
        """.format(epic_key=client_epic['key']),
        "labels": ["automation", "e2e", "frontend", "panel"]
    },
    {
        "summary": "Playwright E2E Framework Setup - Client Automation",
        "description": """
## 🎯 Goal
Set up Playwright E2E framework infrastructure for Panda App automation.

## 📋 Scope
- Playwright installation and configuration
- Page Object Model implementation
- Helper functions and utilities
- Test fixtures and setup
- CI/CD integration

## 📎 Related Files
- `tests/e2e/page_objects/`
- `tests/e2e/helpers/`
- `tests/e2e/conftest.py`

## 🔗 Parent Epic
{epic_key}
        """.format(epic_key=client_epic['key']),
        "labels": ["automation", "e2e", "frontend", "framework", "playwright"]
    }
]

created_stories = []
for i, story_data in enumerate(client_stories, 1):
    print(f"   Creating Story {i}/{len(client_stories)}: {story_data['summary']}...")
    
    story = agent.create_story(
        summary=story_data["summary"],
        description=story_data["description"],
        priority="Medium",
        labels=story_data["labels"]
    )
    
    # Link to Epic using custom field (if available)
    # For now, we'll add it to description
    created_stories.append(story)
    
    print(f"      ✅ Created: {story['key']}")
    print(f"      URL: {story['url']}\n")

print("\n" + "="*100)
print("Summary")
print("="*100)
print(f"\n✅ Created 2 Epics:")
print(f"   1. Client/Frontend Automation: {client_epic['key']}")
print(f"   2. Backend Automation: {backend_epic['key']}")

print(f"\n✅ Created {len(created_stories)} Stories for Client Automation:")
for story in created_stories:
    print(f"   - {story['key']}: {story['summary']}")

print("\n" + "="*100)
print("Next Steps:")
print("1. Link Stories to Epic using Jira UI (Epic Link field)")
print("2. Create Tasks and Sub-tasks under each Story")
print("3. Assign Stories to team members")
print("="*100 + "\n")

