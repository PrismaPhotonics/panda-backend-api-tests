# Live Mode E2E Tests - Sub-tasks
## Ready-to-Import Jira Sub-tasks

**Created:** 2025-11-04  
**Parent Ticket:** PZ-13951 - Live Mode E2E Tests  
**Status:** Working (from Sprint 70)  
**Ready for Jira Import**

---

## 📋 How to Use

1. Copy each sub-task section below
2. Create new Jira sub-task under PZ-13951
3. Paste content into description
4. Set fields as indicated
5. Link sub-tasks as dependencies if needed

---

## 🎯 Sub-tasks

### Task 3.1: Test Live Mode Configuration

**Type:** Sub-task  
**Parent:** PZ-13951  
**Story Points:** 2  
**Priority:** Medium  
**Labels:** `frontend`, `e2e`, `automation`, `ui`, `live-mode`, `medium-priority`  
**Assignee:** [Ron - Frontend & UI Automation]  
**Estimate:** 3 hours

**Title:** Test Live Mode Configuration

**Description:**
```
## 🎯 Goal
Implement E2E test for live mode configuration and spectrogram display.

## 📝 Steps
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
- [ ] All UI elements verified:
  - [ ] Configuration form filled correctly
  - [ ] Start Streaming button works
  - [ ] Canvas displays after start
- [ ] Canvas streaming validation working:
  - [ ] Frequency axis labels correct (0-1000 Hz)
  - [ ] Channel axis labels correct (1-99)
  - [ ] Canvas updates (data streaming)
- [ ] Test passes consistently
- [ ] Test properly cleans up after execution

## 🔗 Dependencies
None (requires Page Objects from Playwright setup)

## 📎 Related Files
- `tests/e2e/test_live_mode.py`
- `tests/e2e/page_objects/panda_app_page.py`
- `tests/e2e/page_objects/configuration_panel.py`
- `tests/e2e/page_objects/spectrogram_canvas.py`

## ⏱️ Estimate
3 hours
```

---

### Task 3.2: Test Live Mode Controls

**Type:** Sub-task  
**Parent:** PZ-13951  
**Story Points:** 1  
**Priority:** Medium  
**Labels:** `frontend`, `e2e`, `automation`, `ui`, `live-mode`, `medium-priority`  
**Assignee:** [Ron - Frontend & UI Automation]  
**Estimate:** 2 hours

**Title:** Test Live Mode Controls

**Description:**
```
## 🎯 Goal
Implement tests for live mode controls (stop, pause/resume).

## 📝 Steps
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
- [ ] Stop streaming test working:
  - [ ] Stop button works correctly
  - [ ] Streaming stops when clicked
  - [ ] Canvas stops updating
  - [ ] UI returns to configuration state
- [ ] Pause/resume test working:
  - [ ] Pause button works correctly
  - [ ] Resume button works correctly
  - [ ] Canvas state verified correctly during pause/resume
  - [ ] No data loss during pause/resume
- [ ] Tests pass consistently
- [ ] Tests properly cleanup after execution

## 🔗 Dependencies
- Task 3.1 (Test Live Mode Configuration)

## 📎 Related Files
- `tests/e2e/test_live_mode.py`
- `tests/e2e/page_objects/panda_app_page.py`

## ⏱️ Estimate
2 hours
```

---

### Task 3.3: Test View Type Switching

**Type:** Sub-task  
**Parent:** PZ-13951  
**Story Points:** 2  
**Priority:** Medium  
**Labels:** `frontend`, `e2e`, `automation`, `ui`, `live-mode`, `view-types`, `medium-priority`  
**Assignee:** [Ron - Frontend & UI Automation]  
**Estimate:** 3 hours

**Title:** Test View Type Switching

**Description:**
```
## 🎯 Goal
Implement test for switching between different view types during live streaming.

## 📝 Steps
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
- [ ] Can switch between all view types:
  - [ ] MultiChannel → SingleChannel
  - [ ] SingleChannel → Waterfall
  - [ ] Waterfall → MultiChannel
- [ ] Each view displays correctly:
  - [ ] MultiChannel view renders properly
  - [ ] SingleChannel view renders properly
  - [ ] Waterfall view renders properly
- [ ] No data loss during transitions:
  - [ ] Streaming continues during switches
  - [ ] Canvas updates continue
  - [ ] No errors during view switching
- [ ] Tests pass consistently
- [ ] Tests properly cleanup after execution

## 🔗 Dependencies
- Task 3.1 (Test Live Mode Configuration)

## 📎 Related Files
- `tests/e2e/test_live_mode.py`
- `tests/e2e/page_objects/panda_app_page.py`
- `tests/e2e/page_objects/spectrogram_canvas.py`

## ⏱️ Estimate
3 hours
```

---

### Task 3.4: Test Channel Management

**Type:** Sub-task  
**Parent:** PZ-13951  
**Story Points:** 1  
**Priority:** Medium  
**Labels:** `frontend`, `e2e`, `automation`, `ui`, `live-mode`, `channels`, `medium-priority`  
**Assignee:** [Ron - Frontend & UI Automation]  
**Estimate:** 2 hours

**Title:** Test Channel Management

**Description:**
```
## 🎯 Goal
Implement tests for channel management during live streaming.

## 📝 Steps
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
- [ ] Channel switching works during streaming:
  - [ ] Can switch channels while streaming
  - [ ] Canvas updates with new channels
  - [ ] No streaming interruption
  - [ ] No data loss during switch
- [ ] Maximum channels configuration accepted:
  - [ ] 2222 channels configuration accepted
  - [ ] UI performance acceptable with max channels
  - [ ] Canvas displays correctly with max channels
  - [ ] No errors or crashes with max channels
- [ ] Tests pass consistently
- [ ] Tests properly cleanup after execution

## 🔗 Dependencies
- Task 3.1 (Test Live Mode Configuration)

## 📎 Related Files
- `tests/e2e/test_live_mode.py`
- `tests/e2e/page_objects/panda_app_page.py`
- `tests/e2e/page_objects/configuration_panel.py`

## ⏱️ Estimate
2 hours
```

---

## 📊 Summary

### Task Breakdown

| Task | Title | Story Points | Estimate | Priority |
|------|-------|--------------|----------|----------|
| **3.1** | Test Live Mode Configuration | 2 | 3 hours | Medium |
| **3.2** | Test Live Mode Controls | 1 | 2 hours | Medium |
| **3.3** | Test View Type Switching | 2 | 3 hours | Medium |
| **3.4** | Test Channel Management | 1 | 2 hours | Medium |
| **Total** | | **6** | **10 hours** | |

### Dependency Chain

```
Task 3.1 (Test Live Mode Configuration)
    ↓
Task 3.2 (Test Live Mode Controls)
    ↓
Task 3.3 (Test View Type Switching)
    ↓
Task 3.4 (Test Channel Management)
```

**Note:** Tasks 3.2, 3.3, and 3.4 all depend on Task 3.1, but can be worked on in parallel after 3.1 is complete.

---

## 📁 Expected Test Files

After completion, the following test files should exist:

```
tests/e2e/
├── test_live_mode.py
│   ├── test_user_configures_and_sees_live_spectrogram
│   ├── test_user_can_stop_live_streaming
│   ├── test_user_can_pause_resume_streaming
│   ├── test_user_switches_between_view_types
│   ├── test_user_switches_channels_during_streaming
│   └── test_user_configures_maximum_channels
```

---

## ✅ Overall Acceptance Criteria

- [ ] All 4 sub-tasks completed
- [ ] All 6 E2E tests implemented and passing
- [ ] Live mode configuration works correctly
- [ ] Live mode controls (stop, pause/resume) work correctly
- [ ] View type switching works correctly
- [ ] Channel management works correctly
- [ ] All tests pass consistently
- [ ] Tests properly cleanup after execution

---

## 🔗 Related Dependencies

**Requires:**
- Playwright E2E Setup (PZ-XXXX) - Page Objects and Helpers must be ready
- Page Objects: `panda_app_page.py`, `configuration_panel.py`, `spectrogram_canvas.py`
- Helpers: `browser_helpers.py`, `assertion_helpers.py`

---

**Last Updated:** 2025-11-04  
**Created by:** QA Team Lead  
**Status:** Ready for Jira Import

