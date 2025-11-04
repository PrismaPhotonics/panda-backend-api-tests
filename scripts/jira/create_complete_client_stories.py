"""
Create Complete Client Automation Stories
==========================================

Creates comprehensive Stories with Sub-tasks for Client Automation based on:
- Existing E2E task documents (LIVE_MODE_E2E_TASKS.md, ERROR_HANDLING_E2E_TASKS.md)
- PZ-9300: Sanity Tests - Panda MS2
- PZ-11734: Sanity tests
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
epic_link_field = "customfield_10014"

print("\n" + "="*100)
print("Creating Complete Client Automation Stories with Sub-tasks")
print("="*100 + "\n")

# ============================================================================
# Define Stories based on existing documents and test structure
# ============================================================================

stories = [
    {
        "summary": "Live Mode E2E Tests - Complete Implementation",
        "description": """
## 🎯 Goal
Complete E2E tests implementation for Live Mode functionality in Panda App based on existing test specifications.

## 📋 Test Coverage
Based on `docs/06_project_management/jira/LIVE_MODE_E2E_TASKS.md`:
- Live Mode configuration
- Live Mode controls (stop, pause/resume)
- View type switching
- Channel management
- Canvas display and updates

## 📝 Test Structure
All tests should be in `tests/e2e/` directory:
- `tests/e2e/test_live_mode.py`
- `tests/e2e/page_objects/panda_app_page.py`
- `tests/e2e/page_objects/configuration_panel.py`
- `tests/e2e/page_objects/spectrogram_canvas.py`

## ✅ Acceptance Criteria
- [ ] All Live Mode E2E tests implemented and passing
- [ ] Page Objects created for all components
- [ ] Tests pass consistently
- [ ] Tests properly cleanup after execution

## 🔗 Parent Epic
{epic_key}

## 📌 Related Tickets
- PZ-13951: Live Mode E2E Tests (original task)
- PZ-9300: Sanity Tests - Panda MS2
- PZ-11734: Sanity tests
        """.format(epic_key=client_epic_key),
        "labels": ["automation", "e2e", "frontend", "live-mode", "sanity"],
        "priority": "Medium",
        "sub_tasks": [
            {
                "summary": "Test Live Mode Configuration",
                "description": """
## 🎯 Goal
Implement E2E test for live mode configuration and spectrogram display.

## 📝 Test Steps
1. Implement `test_user_configures_and_sees_live_spectrogram`:
   - Navigate to Panda App
   - Fill configuration form:
     * Channels: 1-99
     * Frequency: 0-1000Hz
     * NFFT: 1024
   - Click "Start Streaming"
   - Verify canvas displays
   - Verify frequency axis labels (0-1000 Hz)
   - Verify channel axis labels (1-99)
   - Verify data is streaming (canvas updates)

## ✅ Acceptance Criteria
- [ ] Test successfully configures live streaming
- [ ] All UI elements verified
- [ ] Canvas streaming validation working
- [ ] Test passes consistently

## 📎 Related Files
- `tests/e2e/test_live_mode.py::test_user_configures_and_sees_live_spectrogram`
- `tests/e2e/page_objects/panda_app_page.py`
- `tests/e2e/page_objects/configuration_panel.py`

## ⏱️ Estimate
3 hours
                """,
                "labels": ["automation", "e2e", "live-mode", "configuration"],
                "priority": "High"
            },
            {
                "summary": "Test Live Mode Controls",
                "description": """
## 🎯 Goal
Implement tests for live mode controls (stop, pause/resume).

## 📝 Test Steps
1. Implement `test_user_can_stop_live_streaming`:
   - Start live streaming
   - Click "Stop Streaming" button
   - Verify streaming stops
   - Verify canvas stops updating
   - Verify UI state returns to configuration mode

2. Implement `test_user_can_pause_resume_streaming`:
   - Start live streaming
   - Click "Pause" button
   - Verify streaming pauses (canvas stops updating)
   - Click "Resume" button
   - Verify streaming resumes (canvas continues updating)

## ✅ Acceptance Criteria
- [ ] Stop streaming test working
- [ ] Pause/resume test working
- [ ] Tests pass consistently

## 📎 Related Files
- `tests/e2e/test_live_mode.py::test_user_can_stop_live_streaming`
- `tests/e2e/test_live_mode.py::test_user_can_pause_resume_streaming`

## ⏱️ Estimate
2 hours
                """,
                "labels": ["automation", "e2e", "live-mode", "controls"],
                "priority": "Medium"
            },
            {
                "summary": "Test View Type Switching",
                "description": """
## 🎯 Goal
Implement test for switching between different view types during live streaming.

## 📝 Test Steps
1. Implement `test_user_switches_between_view_types`:
   - Start streaming with MultiChannel view
   - Verify MultiChannel view displays correctly
   - Switch to SingleChannel view
   - Verify SingleChannel view displays correctly
   - Switch to Waterfall view
   - Verify Waterfall view displays correctly
   - Verify data continues streaming during switches
   - Verify no data loss during transitions

## ✅ Acceptance Criteria
- [ ] Can switch between all view types
- [ ] Each view displays correctly
- [ ] No data loss during transitions
- [ ] Test passes consistently

## 📎 Related Files
- `tests/e2e/test_live_mode.py::test_user_switches_between_view_types`

## ⏱️ Estimate
3 hours
                """,
                "labels": ["automation", "e2e", "live-mode", "view-types"],
                "priority": "Medium"
            },
            {
                "summary": "Test Channel Management",
                "description": """
## 🎯 Goal
Implement tests for channel management during live streaming.

## 📝 Test Steps
1. Implement `test_user_switches_channels_during_streaming`:
   - Start streaming with channels 1-50
   - Switch to channels 51-100
   - Verify channel switch works correctly
   - Verify canvas updates with new channels
   - Verify no streaming interruption

2. Implement `test_user_configures_maximum_channels`:
   - Configure with 2222 channels (maximum)
   - Start streaming
   - Verify configuration accepted
   - Verify UI performance acceptable with max channels
   - Verify canvas displays correctly

## ✅ Acceptance Criteria
- [ ] Channel switching works during streaming
- [ ] Maximum channels configuration accepted
- [ ] Test passes consistently

## 📎 Related Files
- `tests/e2e/test_live_mode.py::test_user_switches_channels_during_streaming`
- `tests/e2e/test_live_mode.py::test_user_configures_maximum_channels`

## ⏱️ Estimate
2 hours
                """,
                "labels": ["automation", "e2e", "live-mode", "channels"],
                "priority": "Medium"
            }
        ]
    },
    {
        "summary": "Historic Mode E2E Tests - Complete Implementation",
        "description": """
## 🎯 Goal
Complete E2E tests implementation for Historic Mode functionality in Panda App.

## 📋 Test Coverage
- Historic Mode configuration
- Time range selection and validation
- Playback controls
- Data visualization
- Navigation through historic data

## 📝 Test Structure
All tests should be in `tests/e2e/` directory:
- `tests/e2e/test_historic_mode.py`
- `tests/e2e/page_objects/panda_app_page.py`
- `tests/e2e/page_objects/historic_panel.py`

## ✅ Acceptance Criteria
- [ ] All Historic Mode E2E tests implemented and passing
- [ ] Page Objects created for Historic Mode components
- [ ] Tests pass consistently

## 🔗 Parent Epic
{epic_key}

## 📌 Related Tickets
- PZ-13952: Historic Mode E2E Tests (original task)
- PZ-9300: Sanity Tests - Panda MS2
        """.format(epic_key=client_epic_key),
        "labels": ["automation", "e2e", "frontend", "historic-mode", "sanity"],
        "priority": "Medium",
        "sub_tasks": [
            {
                "summary": "Test Historic Mode Configuration",
                "description": """
## 🎯 Goal
Implement E2E test for historic mode configuration.

## 📝 Test Steps
1. Implement `test_user_configures_historic_mode`:
   - Navigate to Panda App
   - Select Historic Mode
   - Fill configuration form:
     * Time range (start and end times)
     * Channels: 1-99
     * Frequency: 0-1000Hz
     * NFFT: 1024
   - Click "Start Playback"
   - Verify configuration is applied
   - Verify historic data loads

## ✅ Acceptance Criteria
- [ ] Historic mode configuration works
- [ ] Time range selection works
- [ ] Configuration is applied correctly
- [ ] Test passes consistently

## 📎 Related Files
- `tests/e2e/test_historic_mode.py::test_user_configures_historic_mode`

## ⏱️ Estimate
3 hours
                """,
                "labels": ["automation", "e2e", "historic-mode", "configuration"],
                "priority": "High"
            },
            {
                "summary": "Test Historic Mode Playback",
                "description": """
## 🎯 Goal
Implement tests for historic mode playback functionality.

## 📝 Test Steps
1. Implement `test_user_controls_historic_playback`:
   - Configure and start historic mode playback
   - Test playback controls:
     * Play button
     * Pause button
     * Stop button
     * Seek forward/backward
   - Verify playback works correctly
   - Verify data is displayed correctly

## ✅ Acceptance Criteria
- [ ] Playback controls work correctly
- [ ] Data is displayed correctly
- [ ] Playback is stable
- [ ] Test passes consistently

## 📎 Related Files
- `tests/e2e/test_historic_mode.py::test_user_controls_historic_playback`

## ⏱️ Estimate
3 hours
                """,
                "labels": ["automation", "e2e", "historic-mode", "playback"],
                "priority": "High"
            },
            {
                "summary": "Test Historic Mode Time Range Validation",
                "description": """
## 🎯 Goal
Implement tests for historic mode time range validation.

## 📝 Test Steps
1. Implement `test_user_sees_error_for_invalid_time_range`:
   - Try to configure with reversed time range (end < start)
   - Verify error message displayed
   - Try to configure with future timestamps
   - Verify error message displayed
   - Try to configure with very old timestamps
   - Verify appropriate handling

## ✅ Acceptance Criteria
- [ ] Invalid time ranges are rejected
- [ ] Clear error messages displayed
- [ ] Future timestamps are rejected
- [ ] Test passes consistently

## 📎 Related Files
- `tests/e2e/test_historic_mode.py::test_user_sees_error_for_invalid_time_range`

## ⏱️ Estimate
2 hours
                """,
                "labels": ["automation", "e2e", "historic-mode", "validation"],
                "priority": "Medium"
            }
        ]
    },
    {
        "summary": "Error Handling E2E Tests - Complete Implementation",
        "description": """
## 🎯 Goal
Complete E2E tests implementation for error handling in Panda App UI.

## 📋 Test Coverage
Based on `docs/06_project_management/jira/ERROR_HANDLING_E2E_TASKS.md`:
- Validation errors
- Server errors
- Error recovery
- User-friendly error messages
- Error state management

## 📝 Test Structure
All tests should be in `tests/e2e/` directory:
- `tests/e2e/test_error_handling.py`
- `tests/e2e/page_objects/panda_app_page.py`
- `tests/e2e/page_objects/configuration_panel.py`
- `tests/e2e/helpers/error_helpers.py`

## ✅ Acceptance Criteria
- [ ] All Error Handling E2E tests implemented and passing
- [ ] Error messages are user-friendly
- [ ] Error state management working correctly
- [ ] Tests pass consistently

## 🔗 Parent Epic
{epic_key}

## 📌 Related Tickets
- PZ-13953: Error Handling E2E Tests (original task)
- PZ-9300: Sanity Tests - Panda MS2
        """.format(epic_key=client_epic_key),
        "labels": ["automation", "e2e", "frontend", "error-handling", "sanity"],
        "priority": "Medium",
        "sub_tasks": [
            {
                "summary": "Test Validation Errors",
                "description": """
## 🎯 Goal
Implement E2E tests for validation errors in Panda UI.

## 📝 Test Steps
1. Implement `test_user_sees_clear_error_for_invalid_nfft`:
   - Navigate to Panda App
   - Fill configuration form with NFFT value that is not a power of 2 (e.g., 1000)
   - Click "Start Streaming"
   - Verify clear error message is displayed
   - Verify error message is specific and actionable
   - Verify input field is highlighted appropriately

2. Implement `test_user_sees_error_for_frequency_exceeds_limit`:
   - Fill configuration form with frequency > 1000 Hz (e.g., 1500 Hz)
   - Click "Start Streaming"
   - Verify error message displayed
   - Verify error message indicates the limit (1000 Hz)
   - Verify input field is highlighted

3. Implement `test_user_sees_error_for_invalid_channels`:
   - Fill configuration form with invalid channel range (e.g., channels 100-50, or negative channels)
   - Click "Start Streaming"
   - Verify error message displayed
   - Verify error message indicates valid channel range
   - Verify input field is highlighted

## ✅ Acceptance Criteria
- [ ] All validation error tests implemented and passing
- [ ] Error messages are clear and specific
- [ ] Input fields highlighted appropriately
- [ ] Test passes consistently

## 📎 Related Files
- `tests/e2e/test_error_handling.py::test_user_sees_clear_error_for_invalid_nfft`
- `tests/e2e/test_error_handling.py::test_user_sees_error_for_frequency_exceeds_limit`
- `tests/e2e/test_error_handling.py::test_user_sees_error_for_invalid_channels`

## ⏱️ Estimate
3 hours
                """,
                "labels": ["automation", "e2e", "error-handling", "validation"],
                "priority": "High"
            },
            {
                "summary": "Test Server Errors",
                "description": """
## 🎯 Goal
Implement E2E tests for server error scenarios.

## 📝 Test Steps
1. Implement `test_user_sees_error_when_server_unavailable`:
   - Stop Focus Server backend (or simulate server down)
   - Navigate to Panda App
   - Fill configuration form with valid values
   - Click "Start Streaming"
   - Verify user-friendly error message is displayed
   - Verify error message indicates server is unavailable
   - Verify error message is not technical (no stack traces)
   - Verify no silent failures (UI doesn't just hang)

2. Implement `test_user_sees_error_for_timeout`:
   - Simulate request timeout scenario (or use network throttling)
   - Fill configuration form with valid values
   - Click "Start Streaming"
   - Verify timeout error message is displayed
   - Verify error message indicates timeout occurred
   - Verify user is informed about retry option
   - Verify no silent failures

## ✅ Acceptance Criteria
- [ ] Server error scenarios tested
- [ ] User-friendly error messages shown
- [ ] No silent failures
- [ ] Test passes consistently

## 📎 Related Files
- `tests/e2e/test_error_handling.py::test_user_sees_error_when_server_unavailable`
- `tests/e2e/test_error_handling.py::test_user_sees_error_for_timeout`

## ⏱️ Estimate
2 hours
                """,
                "labels": ["automation", "e2e", "error-handling", "server-errors"],
                "priority": "High"
            },
            {
                "summary": "Test Error Recovery",
                "description": """
## 🎯 Goal
Implement E2E tests for error recovery scenarios.

## 📝 Test Steps
1. Implement error recovery test for validation errors:
   - Trigger validation error (e.g., invalid NFFT)
   - Verify error message is displayed
   - Correct the invalid input (change to valid NFFT)
   - Click "Start Streaming" again
   - Verify error message is cleared
   - Verify operation succeeds
   - Verify no lingering error messages

2. Implement error recovery test for server errors:
   - Trigger server error (server unavailable)
   - Verify error message is displayed
   - Start server (or simulate server recovery)
   - Click "Retry" button (if available) or "Start Streaming" again
   - Verify error message is cleared
   - Verify operation succeeds
   - Verify error state is properly cleaned up

## ✅ Acceptance Criteria
- [ ] User can correct errors and retry
- [ ] Error state cleanup working
- [ ] No lingering error messages
- [ ] Test passes consistently

## 📎 Related Files
- `tests/e2e/test_error_handling.py::test_user_can_correct_validation_error`
- `tests/e2e/test_error_handling.py::test_user_can_retry_after_server_error`

## ⏱️ Estimate
2 hours
                """,
                "labels": ["automation", "e2e", "error-handling", "recovery"],
                "priority": "Medium"
            }
        ]
    },
    {
        "summary": "Playwright E2E Framework Setup - Infrastructure",
        "description": """
## 🎯 Goal
Set up Playwright E2E framework infrastructure for Panda App automation.

## 📋 Scope
Based on `docs/06_project_management/jira/PLAYWRIGHT_E2E_SETUP_TASKS.md`:
- Playwright installation and configuration
- Page Object Model implementation
- Helper functions and utilities
- Test fixtures and setup
- CI/CD integration

## 📝 Test Structure
All infrastructure should be in:
- `tests/e2e/page_objects/`
- `tests/e2e/helpers/`
- `tests/e2e/conftest.py`

## ✅ Acceptance Criteria
- [ ] Playwright framework set up and working
- [ ] Page Objects created for all components
- [ ] Helper functions available
- [ ] Test fixtures working
- [ ] CI/CD integration complete

## 🔗 Parent Epic
{epic_key}

## 📌 Related Tickets
- PZ-9300: Sanity Tests - Panda MS2
        """.format(epic_key=client_epic_key),
        "labels": ["automation", "e2e", "frontend", "framework", "playwright", "infrastructure"],
        "priority": "High",
        "sub_tasks": [
            {
                "summary": "Install and Configure Playwright",
                "description": """
## 🎯 Goal
Install and configure Playwright for end-to-end testing framework.

## 📝 Test Steps
1. Add Playwright dependencies to `requirements.txt`:
   - `playwright==1.40.0`
   - `pytest-playwright==0.4.3`
2. Run `playwright install chromium` to install Chromium browser
3. Configure pytest-playwright in `pytest.ini`
4. Test basic browser launch with sample script

## ✅ Acceptance Criteria
- [ ] Playwright installed successfully
- [ ] Chromium browser installed
- [ ] Can launch browser and navigate to a page
- [ ] `requirements.txt` updated with Playwright packages
- [ ] `pytest.ini` configured for pytest-playwright
- [ ] Basic browser launch test passes

## 📎 Related Files
- `requirements.txt`
- `pytest.ini`

## ⏱️ Estimate
1 hour
                """,
                "labels": ["automation", "e2e", "playwright", "setup"],
                "priority": "High"
            },
            {
                "summary": "Create E2E Directory Structure",
                "description": """
## 🎯 Goal
Create directory structure for E2E tests with proper fixtures.

## 📝 Test Steps
1. Create `tests/e2e/` directory
2. Create subdirectories:
   - `tests/e2e/page_objects/`
   - `tests/e2e/helpers/`
3. Create `tests/e2e/conftest.py` with browser fixtures
4. Implement browser lifecycle management in fixtures
5. Add page fixture for test isolation

## ✅ Acceptance Criteria
- [ ] Directory structure created
- [ ] `conftest.py` has browser and page fixtures
- [ ] Browser lifecycle managed correctly
- [ ] Test isolation working

## 📎 Related Files
- `tests/e2e/conftest.py`
- `tests/e2e/page_objects/`
- `tests/e2e/helpers/`

## ⏱️ Estimate
1 hour
                """,
                "labels": ["automation", "e2e", "playwright", "setup"],
                "priority": "High"
            },
            {
                "summary": "Create Page Object Models",
                "description": """
## 🎯 Goal
Create Page Object Models for Panda App components.

## 📝 Test Steps
1. Create `panda_app_page.py`:
   - Main page object for Panda App
   - Navigation methods
   - Common UI interactions

2. Create `configuration_panel.py`:
   - Configuration form page object
   - Form filling methods
   - Validation methods

3. Create `spectrogram_canvas.py`:
   - Canvas page object
   - Canvas interaction methods
   - Canvas validation methods

## ✅ Acceptance Criteria
- [ ] Page Objects created for all components
- [ ] Page Objects follow Page Object Pattern
- [ ] Methods are reusable and maintainable
- [ ] Page Objects tested

## 📎 Related Files
- `tests/e2e/page_objects/panda_app_page.py`
- `tests/e2e/page_objects/configuration_panel.py`
- `tests/e2e/page_objects/spectrogram_canvas.py`

## ⏱️ Estimate
4 hours
                """,
                "labels": ["automation", "e2e", "playwright", "page-objects"],
                "priority": "High"
            },
            {
                "summary": "Create Helper Functions and Utilities",
                "description": """
## 🎯 Goal
Create helper functions and utilities for E2E tests.

## 📝 Test Steps
1. Create `browser_helpers.py`:
   - Browser interaction helpers
   - Wait utilities
   - Screenshot utilities

2. Create `assertion_helpers.py`:
   - Custom assertion methods
   - Validation helpers
   - Error message helpers

3. Create `test_data_helpers.py`:
   - Test data generation
   - Configuration builders
   - Data validation helpers

## ✅ Acceptance Criteria
- [ ] Helper functions created
- [ ] Helper functions are reusable
- [ ] Helper functions are well-documented
- [ ] Helper functions tested

## 📎 Related Files
- `tests/e2e/helpers/browser_helpers.py`
- `tests/e2e/helpers/assertion_helpers.py`
- `tests/e2e/helpers/test_data_helpers.py`

## ⏱️ Estimate
3 hours
                """,
                "labels": ["automation", "e2e", "playwright", "helpers"],
                "priority": "Medium"
            }
        ]
    }
]

# ============================================================================
# Create Stories and Sub-tasks
# ============================================================================

created_stories = []

print(f"Creating {len(stories)} Stories with Sub-tasks...\n")

for story_idx, story_data in enumerate(stories, 1):
    print(f"{'='*100}")
    print(f"Story {story_idx}/{len(stories)}: {story_data['summary']}")
    print(f"{'='*100}\n")
    
    # Create Story
    try:
        story = agent.create_story(
            summary=story_data["summary"],
            description=story_data["description"],
            priority=story_data.get("priority", "Medium"),
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
            "sub_tasks": []
        })
        
        # Create Sub-tasks under Story
        sub_tasks = story_data.get("sub_tasks", [])
        print(f"   Creating {len(sub_tasks)} Sub-tasks...\n")
        
        for task_idx, task_data in enumerate(sub_tasks, 1):
            try:
                sub_task = agent.client.create_issue(
                    summary=task_data["summary"],
                    description=task_data["description"],
                    issue_type="Sub-task",
                    priority=task_data["priority"],
                    labels=task_data["labels"],
                    parent_key=story["key"]
                )
                
                created_stories[-1]["sub_tasks"].append(sub_task)
                print(f"   ✅ Sub-task {task_idx}/{len(sub_tasks)}: {sub_task['key']} - {sub_task['summary']}")
                
            except Exception as e:
                print(f"   ❌ Failed to create Sub-task {task_idx}: {e}")
        
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
print(f"\n✅ All Stories linked to Epic: {client_epic_key}")
print(f"   Epic URL: https://prismaphotonics.atlassian.net/browse/{client_epic_key}")

print("\n" + "="*100)
print("Next Steps:")
print("1. Review all Stories and Sub-tasks in Jira")
print("2. Assign Sub-tasks to team members (Ron David)")
print("3. Set Story Points and estimates")
print("4. Link to PZ-9300 (Sanity Tests - Panda MS2)")
print("5. Link to PZ-11734 (Sanity tests)")
print("="*100 + "\n")

