"""
Create Sanity Tests Stories and Tasks
=====================================

Creates comprehensive Stories and Tasks for Sanity Tests based on:
- PZ-9300: Sanity Tests - Panda MS2
- PZ-11734: Sanity tests
- Existing test structure in the codebase
- Test tree structure from Tomer

All Stories linked to Client Automation Epic (PZ-14220)
"""

import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraAgent

agent = JiraAgent()
client_epic_key = "PZ-14220"

print("\n" + "="*100)
print("Creating Sanity Tests Stories and Tasks")
print("="*100 + "\n")

# ============================================================================
# Define Stories based on test categories and existing test structure
# ============================================================================

stories = [
    {
        "summary": "Panel Configuration Tests - Sanity",
        "description": """
## 🎯 Goal
Implement E2E sanity tests for Panel configuration functionality in Panda App.

## 📋 Test Coverage
- Panel configuration form validation
- Panel parameter settings
- Panel state management
- Panel initialization and reset

## 📝 Test Structure
Based on test tree structure created by Tomer.
All tests should be in `tests/e2e/panel/` directory.

## ✅ Acceptance Criteria
- [ ] All Panel configuration tests implemented
- [ ] Tests pass consistently
- [ ] Tests properly cleanup after execution
- [ ] Page Objects created for Panel components

## 📎 Related Files
- `tests/e2e/panel/test_panel_configuration.py`
- `tests/e2e/page_objects/panel.py`
- `tests/e2e/page_objects/configuration_panel.py`

## 🔗 Parent Epic
{epic_key}

## 📌 Related Sanity Test
- PZ-9300: Sanity Tests - Panda MS2
- PZ-11734: Sanity tests
        """.format(epic_key=client_epic_key),
        "labels": ["automation", "e2e", "frontend", "sanity", "panel", "configuration"],
        "tasks": [
            {
                "summary": "Test Panel Configuration Form Validation",
                "description": """
## 🎯 Goal
Test that Panel configuration form validates inputs correctly.

## 📝 Test Steps
1. Navigate to Panda App
2. Open Panel configuration
3. Test invalid inputs:
   - Invalid channel ranges
   - Invalid frequency ranges
   - Invalid NFFT values
   - Missing required fields
4. Verify error messages displayed
5. Verify form doesn't submit with invalid data

## ✅ Acceptance Criteria
- [ ] Invalid inputs are rejected
- [ ] Clear error messages displayed
- [ ] Form validation works for all fields
- [ ] Test passes consistently

## 📎 Related Files
- `tests/e2e/panel/test_panel_configuration.py::TestPanelConfigurationValidation`
                """,
                "labels": ["automation", "e2e", "panel", "validation"],
                "priority": "High"
            },
            {
                "summary": "Test Panel Parameter Settings",
                "description": """
## 🎯 Goal
Test that Panel parameters can be set and saved correctly.

## 📝 Test Steps
1. Navigate to Panda App
2. Open Panel configuration
3. Set valid parameters:
   - Channel range
   - Frequency range
   - NFFT value
   - Other Panel-specific parameters
4. Save configuration
5. Verify parameters are saved
6. Reload page and verify parameters persist

## ✅ Acceptance Criteria
- [ ] Parameters can be set successfully
- [ ] Parameters are saved correctly
- [ ] Parameters persist after page reload
- [ ] Test passes consistently

## 📎 Related Files
- `tests/e2e/panel/test_panel_configuration.py::TestPanelParameterSettings`
                """,
                "labels": ["automation", "e2e", "panel", "parameters"],
                "priority": "High"
            },
            {
                "summary": "Test Panel State Management",
                "description": """
## 🎯 Goal
Test that Panel state is managed correctly during operations.

## 📝 Test Steps
1. Navigate to Panda App
2. Open Panel
3. Test state transitions:
   - Initial state
   - Configuration state
   - Running state
   - Stopped state
4. Verify state is updated correctly
5. Verify UI reflects state changes

## ✅ Acceptance Criteria
- [ ] State transitions work correctly
- [ ] UI reflects state changes
- [ ] State persists during operations
- [ ] Test passes consistently

## 📎 Related Files
- `tests/e2e/panel/test_panel_state.py`
                """,
                "labels": ["automation", "e2e", "panel", "state-management"],
                "priority": "Medium"
            },
            {
                "summary": "Test Panel Initialization and Reset",
                "description": """
## 🎯 Goal
Test that Panel initializes correctly and can be reset.

## 📝 Test Steps
1. Navigate to Panda App
2. Open Panel
3. Verify Panel initializes with default values
4. Change Panel configuration
5. Reset Panel to defaults
6. Verify Panel returns to initial state

## ✅ Acceptance Criteria
- [ ] Panel initializes correctly
- [ ] Default values are applied
- [ ] Reset functionality works
- [ ] Test passes consistently

## 📎 Related Files
- `tests/e2e/panel/test_panel_initialization.py`
                """,
                "labels": ["automation", "e2e", "panel", "initialization"],
                "priority": "Medium"
            }
        ]
    },
    {
        "summary": "Panel Live Mode Tests - Sanity",
        "description": """
## 🎯 Goal
Implement E2E sanity tests for Panel Live Mode functionality.

## 📋 Test Coverage
- Panel Live Mode configuration
- Panel Live Mode streaming
- Panel Live Mode controls
- Panel Live Mode data display

## 📝 Test Structure
Based on test tree structure created by Tomer.
All tests should be in `tests/e2e/panel/` directory.

## ✅ Acceptance Criteria
- [ ] All Panel Live Mode tests implemented
- [ ] Tests pass consistently
- [ ] Tests properly cleanup after execution

## 📎 Related Files
- `tests/e2e/panel/test_panel_live_mode.py`
- `tests/e2e/page_objects/panel_live_mode.py`

## 🔗 Parent Epic
{epic_key}

## 📌 Related Sanity Test
- PZ-9300: Sanity Tests - Panda MS2
        """.format(epic_key=client_epic_key),
        "labels": ["automation", "e2e", "frontend", "sanity", "panel", "live-mode"],
        "tasks": [
            {
                "summary": "Test Panel Live Mode Configuration",
                "description": """
## 🎯 Goal
Test that Panel Live Mode can be configured correctly.

## 📝 Test Steps
1. Navigate to Panda App
2. Open Panel
3. Configure Live Mode:
   - Set channel range
   - Set frequency range
   - Set NFFT
   - Configure other Live Mode parameters
4. Start Live Mode streaming
5. Verify configuration is applied

## ✅ Acceptance Criteria
- [ ] Live Mode configuration works
- [ ] Configuration is applied correctly
- [ ] Streaming starts successfully
- [ ] Test passes consistently

## 📎 Related Files
- `tests/e2e/panel/test_panel_live_mode.py::TestPanelLiveModeConfiguration`
                """,
                "labels": ["automation", "e2e", "panel", "live-mode", "configuration"],
                "priority": "High"
            },
            {
                "summary": "Test Panel Live Mode Streaming",
                "description": """
## 🎯 Goal
Test that Panel Live Mode streams data correctly.

## 📝 Test Steps
1. Configure and start Panel Live Mode
2. Verify data is streaming
3. Verify data is displayed correctly
4. Verify data updates in real-time
5. Monitor streaming for stability

## ✅ Acceptance Criteria
- [ ] Data streams correctly
- [ ] Data is displayed correctly
- [ ] Data updates in real-time
- [ ] Streaming is stable
- [ ] Test passes consistently

## 📎 Related Files
- `tests/e2e/panel/test_panel_live_mode.py::TestPanelLiveModeStreaming`
                """,
                "labels": ["automation", "e2e", "panel", "live-mode", "streaming"],
                "priority": "High"
            },
            {
                "summary": "Test Panel Live Mode Controls",
                "description": """
## 🎯 Goal
Test that Panel Live Mode controls work correctly.

## 📝 Test Steps
1. Start Panel Live Mode
2. Test controls:
   - Stop button
   - Pause/Resume button
   - Settings button
   - Other Live Mode controls
3. Verify controls work correctly
4. Verify state changes accordingly

## ✅ Acceptance Criteria
- [ ] All controls work correctly
- [ ] State changes correctly
- [ ] UI reflects control actions
- [ ] Test passes consistently

## 📎 Related Files
- `tests/e2e/panel/test_panel_live_mode.py::TestPanelLiveModeControls`
                """,
                "labels": ["automation", "e2e", "panel", "live-mode", "controls"],
                "priority": "Medium"
            }
        ]
    },
    {
        "summary": "Panel Historic Mode Tests - Sanity",
        "description": """
## 🎯 Goal
Implement E2E sanity tests for Panel Historic Mode functionality.

## 📋 Test Coverage
- Panel Historic Mode configuration
- Panel Historic Mode playback
- Panel Historic Mode navigation
- Panel Historic Mode data display

## 📝 Test Structure
Based on test tree structure created by Tomer.
All tests should be in `tests/e2e/panel/` directory.

## ✅ Acceptance Criteria
- [ ] All Panel Historic Mode tests implemented
- [ ] Tests pass consistently
- [ ] Tests properly cleanup after execution

## 📎 Related Files
- `tests/e2e/panel/test_panel_historic_mode.py`
- `tests/e2e/page_objects/panel_historic_mode.py`

## 🔗 Parent Epic
{epic_key}

## 📌 Related Sanity Test
- PZ-9300: Sanity Tests - Panda MS2
        """.format(epic_key=client_epic_key),
        "labels": ["automation", "e2e", "frontend", "sanity", "panel", "historic-mode"],
        "tasks": [
            {
                "summary": "Test Panel Historic Mode Configuration",
                "description": """
## 🎯 Goal
Test that Panel Historic Mode can be configured correctly.

## 📝 Test Steps
1. Navigate to Panda App
2. Open Panel
3. Configure Historic Mode:
   - Set time range
   - Set channel range
   - Set frequency range
   - Configure other Historic Mode parameters
4. Start Historic Mode playback
5. Verify configuration is applied

## ✅ Acceptance Criteria
- [ ] Historic Mode configuration works
- [ ] Configuration is applied correctly
- [ ] Playback starts successfully
- [ ] Test passes consistently

## 📎 Related Files
- `tests/e2e/panel/test_panel_historic_mode.py::TestPanelHistoricModeConfiguration`
                """,
                "labels": ["automation", "e2e", "panel", "historic-mode", "configuration"],
                "priority": "High"
            },
            {
                "summary": "Test Panel Historic Mode Playback",
                "description": """
## 🎯 Goal
Test that Panel Historic Mode playback works correctly.

## 📝 Test Steps
1. Configure and start Panel Historic Mode
2. Verify playback starts
3. Verify data is displayed correctly
4. Verify playback controls work (play, pause, seek)
5. Monitor playback for stability

## ✅ Acceptance Criteria
- [ ] Playback works correctly
- [ ] Data is displayed correctly
- [ ] Playback controls work
- [ ] Playback is stable
- [ ] Test passes consistently

## 📎 Related Files
- `tests/e2e/panel/test_panel_historic_mode.py::TestPanelHistoricModePlayback`
                """,
                "labels": ["automation", "e2e", "panel", "historic-mode", "playback"],
                "priority": "High"
            },
            {
                "summary": "Test Panel Historic Mode Navigation",
                "description": """
## 🎯 Goal
Test that Panel Historic Mode navigation works correctly.

## 📝 Test Steps
1. Start Panel Historic Mode playback
2. Test navigation:
   - Seek forward
   - Seek backward
   - Jump to specific time
   - Navigate through time range
3. Verify navigation works correctly
4. Verify data updates accordingly

## ✅ Acceptance Criteria
- [ ] Navigation works correctly
- [ ] Data updates correctly
- [ ] Time position is accurate
- [ ] Test passes consistently

## 📎 Related Files
- `tests/e2e/panel/test_panel_historic_mode.py::TestPanelHistoricModeNavigation`
                """,
                "labels": ["automation", "e2e", "panel", "historic-mode", "navigation"],
                "priority": "Medium"
            }
        ]
    },
    {
        "summary": "Panel Error Handling Tests - Sanity",
        "description": """
## 🎯 Goal
Implement E2E sanity tests for Panel error handling.

## 📋 Test Coverage
- Panel error messages
- Panel error recovery
- Panel error state management
- Panel error validation

## 📝 Test Structure
Based on test tree structure created by Tomer.
All tests should be in `tests/e2e/panel/` directory.

## ✅ Acceptance Criteria
- [ ] All Panel error handling tests implemented
- [ ] Tests pass consistently
- [ ] Tests properly cleanup after execution

## 📎 Related Files
- `tests/e2e/panel/test_panel_error_handling.py`
- `tests/e2e/page_objects/panel_error_handling.py`

## 🔗 Parent Epic
{epic_key}

## 📌 Related Sanity Test
- PZ-9300: Sanity Tests - Panda MS2
        """.format(epic_key=client_epic_key),
        "labels": ["automation", "e2e", "frontend", "sanity", "panel", "error-handling"],
        "tasks": [
            {
                "summary": "Test Panel Error Messages",
                "description": """
## 🎯 Goal
Test that Panel displays error messages correctly.

## 📝 Test Steps
1. Navigate to Panda App
2. Open Panel
3. Trigger various errors:
   - Invalid configuration
   - Server errors
   - Network errors
   - Timeout errors
4. Verify error messages are displayed
5. Verify error messages are clear and actionable

## ✅ Acceptance Criteria
- [ ] Error messages are displayed correctly
- [ ] Error messages are clear
- [ ] Error messages are actionable
- [ ] Test passes consistently

## 📎 Related Files
- `tests/e2e/panel/test_panel_error_handling.py::TestPanelErrorMessages`
                """,
                "labels": ["automation", "e2e", "panel", "error-handling", "messages"],
                "priority": "High"
            },
            {
                "summary": "Test Panel Error Recovery",
                "description": """
## 🎯 Goal
Test that Panel can recover from errors correctly.

## 📝 Test Steps
1. Trigger an error in Panel
2. Verify error is displayed
3. Attempt to recover:
   - Fix invalid input
   - Retry failed operation
   - Reset Panel state
4. Verify recovery works correctly
5. Verify Panel returns to normal operation

## ✅ Acceptance Criteria
- [ ] Error recovery works correctly
- [ ] Panel returns to normal operation
- [ ] No lingering error state
- [ ] Test passes consistently

## 📎 Related Files
- `tests/e2e/panel/test_panel_error_handling.py::TestPanelErrorRecovery`
                """,
                "labels": ["automation", "e2e", "panel", "error-handling", "recovery"],
                "priority": "Medium"
            }
        ]
    },
    {
        "summary": "Panel UI/UX Tests - Sanity",
        "description": """
## 🎯 Goal
Implement E2E sanity tests for Panel UI/UX functionality.

## 📋 Test Coverage
- Panel UI elements
- Panel user interactions
- Panel visual validation
- Panel accessibility

## 📝 Test Structure
Based on test tree structure created by Tomer.
All tests should be in `tests/e2e/panel/` directory.

## ✅ Acceptance Criteria
- [ ] All Panel UI/UX tests implemented
- [ ] Tests pass consistently
- [ ] Tests properly cleanup after execution

## 📎 Related Files
- `tests/e2e/panel/test_panel_ui_ux.py`
- `tests/e2e/page_objects/panel_ui.py`

## 🔗 Parent Epic
{epic_key}

## 📌 Related Sanity Test
- PZ-9300: Sanity Tests - Panda MS2
        """.format(epic_key=client_epic_key),
        "labels": ["automation", "e2e", "frontend", "sanity", "panel", "ui", "ux"],
        "tasks": [
            {
                "summary": "Test Panel UI Elements",
                "description": """
## 🎯 Goal
Test that Panel UI elements are displayed correctly.

## 📝 Test Steps
1. Navigate to Panda App
2. Open Panel
3. Verify UI elements:
   - Buttons are visible
   - Forms are displayed
   - Labels are correct
   - Icons are displayed
4. Verify UI elements are functional

## ✅ Acceptance Criteria
- [ ] All UI elements are displayed
- [ ] UI elements are functional
- [ ] UI elements are correctly positioned
- [ ] Test passes consistently

## 📎 Related Files
- `tests/e2e/panel/test_panel_ui_ux.py::TestPanelUIElements`
                """,
                "labels": ["automation", "e2e", "panel", "ui", "elements"],
                "priority": "Medium"
            },
            {
                "summary": "Test Panel User Interactions",
                "description": """
## 🎯 Goal
Test that Panel user interactions work correctly.

## 📝 Test Steps
1. Navigate to Panda App
2. Open Panel
3. Test interactions:
   - Click buttons
   - Fill forms
   - Select options
   - Drag and drop (if applicable)
4. Verify interactions work correctly
5. Verify UI responds appropriately

## ✅ Acceptance Criteria
- [ ] All interactions work correctly
- [ ] UI responds appropriately
- [ ] No unexpected behavior
- [ ] Test passes consistently

## 📎 Related Files
- `tests/e2e/panel/test_panel_ui_ux.py::TestPanelUserInteractions`
                """,
                "labels": ["automation", "e2e", "panel", "ui", "interactions"],
                "priority": "Medium"
            }
        ]
    }
]

# ============================================================================
# Create Stories and Tasks
# ============================================================================

created_stories = []
epic_link_field = "customfield_10014"  # Epic Link field

print(f"Creating {len(stories)} Stories with Tasks...\n")

for story_idx, story_data in enumerate(stories, 1):
    print(f"{'='*100}")
    print(f"Story {story_idx}/{len(stories)}: {story_data['summary']}")
    print(f"{'='*100}\n")
    
    # Create Story
    try:
        story = agent.create_story(
            summary=story_data["summary"],
            description=story_data["description"],
            priority="Medium",
            labels=story_data["labels"]
        )
        
        # Link Story to Epic
        try:
            agent.client.update_issue(story["key"], **{epic_link_field: client_epic_key})
            print(f"✅ Created and linked Story: {story['key']}")
            print(f"   URL: {story['url']}\n")
        except Exception as e:
            print(f"⚠️  Created Story but failed to link: {story['key']}")
            print(f"   Error: {e}\n")
        
        created_stories.append({
            "story": story,
            "tasks": []
        })
        
        # Create Tasks under Story
        print(f"   Creating {len(story_data['tasks'])} Tasks...\n")
        
        for task_idx, task_data in enumerate(story_data["tasks"], 1):
            try:
                task = agent.client.create_issue(
                    summary=task_data["summary"],
                    description=task_data["description"],
                    issue_type="Sub-task",
                    priority=task_data["priority"],
                    labels=task_data["labels"],
                    parent_key=story["key"]
                )
                
                created_stories[-1]["tasks"].append(task)
                print(f"   ✅ Task {task_idx}/{len(story_data['tasks'])}: {task['key']} - {task['summary']}")
                
            except Exception as e:
                print(f"   ❌ Failed to create Task {task_idx}: {e}")
        
        print()
        
    except Exception as e:
        print(f"❌ Failed to create Story {story_idx}: {e}\n")

# ============================================================================
# Summary
# ============================================================================

print("\n" + "="*100)
print("Summary")
print("="*100)

print(f"\n✅ Created {len(created_stories)} Stories:")
total_tasks = 0
for story_info in created_stories:
    story = story_info["story"]
    tasks = story_info["tasks"]
    total_tasks += len(tasks)
    print(f"\n   {story['key']}: {story['summary']}")
    print(f"   URL: {story['url']}")
    print(f"   Tasks: {len(tasks)}")
    for task in tasks:
        print(f"      - {task['key']}: {task['summary']}")

print(f"\n✅ Total:")
print(f"   Stories: {len(created_stories)}")
print(f"   Tasks: {total_tasks}")
print(f"\n✅ All Stories linked to Epic: {client_epic_key}")
print(f"   Epic URL: https://prismaphotonics.atlassian.net/browse/{client_epic_key}")

print("\n" + "="*100)
print("Next Steps:")
print("1. Review all Stories and Tasks in Jira")
print("2. Assign Tasks to team members (Ron David)")
print("3. Set Story Points and estimates")
print("4. Link to PZ-9300 (Sanity Tests - Panda MS2)")
print("5. Link to PZ-11734 (Sanity tests)")
print("="*100 + "\n")

