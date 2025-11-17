# Error Handling E2E Tests - Sub-tasks
## Ready-to-Import Jira Sub-tasks

**Created:** 2025-11-04  
**Parent Ticket:** PZ-13953 - Error Handling E2E Tests  
**Status:** TO DO (from Sprint 70)  
**Story Points:** 2  
**Priority:** Medium  
**Ready for Jira Import**

---

## 📋 How to Use

1. Copy each sub-task section below
2. Create new Jira sub-task under PZ-13953
3. Paste content into description
4. Set fields as indicated
5. Link sub-tasks as dependencies if needed

---

## 🎯 Sub-tasks

### Task 5.1: Test Validation Errors

**Type:** Sub-task  
**Parent:** PZ-13953  
**Story Points:** 1  
**Priority:** Medium  
**Labels:** `frontend`, `e2e`, `automation`, `ui`, `error-handling`, `validation`, `medium-priority`  
**Assignee:** [Ron - Frontend & UI Automation]  
**Estimate:** 3 hours

**Title:** Test Validation Errors

**Description:**
```
## 🎯 Goal
Implement E2E tests for validation errors in Panda UI. Ensure users receive clear feedback when input validation fails.

## 📝 Steps
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
- [ ] All validation error tests implemented:
  - [ ] `test_user_sees_clear_error_for_invalid_nfft` passing
  - [ ] `test_user_sees_error_for_frequency_exceeds_limit` passing
  - [ ] `test_user_sees_error_for_invalid_channels` passing
- [ ] Error messages are clear and specific:
  - [ ] Error messages explain what is wrong
  - [ ] Error messages suggest how to fix the issue
  - [ ] Error messages are user-friendly (not technical jargon)
- [ ] Input fields highlighted appropriately:
  - [ ] Invalid fields are visually highlighted
  - [ ] Error indicators are clear and visible
  - [ ] Multiple errors are all clearly indicated
- [ ] Tests pass consistently
- [ ] Tests properly cleanup after execution

## 🔗 Dependencies
None (requires Page Objects from Playwright setup)

## 📎 Related Files
- `tests/e2e/test_error_handling.py`
- `tests/e2e/page_objects/panda_app_page.py`
- `tests/e2e/page_objects/configuration_panel.py`

## ⏱️ Estimate
3 hours
```

---

### Task 5.2: Test Server Errors

**Type:** Sub-task  
**Parent:** PZ-13953  
**Story Points:** 1  
**Priority:** Medium  
**Labels:** `frontend`, `e2e`, `automation`, `ui`, `error-handling`, `server-errors`, `medium-priority`  
**Assignee:** [Ron - Frontend & UI Automation]  
**Estimate:** 2 hours

**Title:** Test Server Errors

**Description:**
```
## 🎯 Goal
Implement E2E tests for server error scenarios. Ensure users receive user-friendly error messages when server errors occur.

## 📝 Steps
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
- [ ] Server error scenarios tested:
  - [ ] `test_user_sees_error_when_server_unavailable` passing
  - [ ] `test_user_sees_error_for_timeout` passing
- [ ] User-friendly error messages shown:
  - [ ] Error messages are clear and understandable
  - [ ] Error messages don't show technical details (no stack traces)
  - [ ] Error messages provide actionable information
  - [ ] Error messages suggest recovery actions
- [ ] No silent failures:
  - [ ] UI doesn't hang or freeze
  - [ ] Error state is clearly visible
  - [ ] User is always informed of errors
  - [ ] Loading states are properly cleared on error
- [ ] Tests pass consistently
- [ ] Tests properly cleanup after execution

## 🔗 Dependencies
- Task 5.1 (Test Validation Errors)

## 📎 Related Files
- `tests/e2e/test_error_handling.py`
- `tests/e2e/page_objects/panda_app_page.py`
- `tests/e2e/helpers/error_helpers.py` (if needed)

## ⏱️ Estimate
2 hours
```

---

### Task 5.3: Test Error Recovery

**Type:** Sub-task  
**Parent:** PZ-13953  
**Story Points:** 1  
**Priority:** Medium  
**Labels:** `frontend`, `e2e`, `automation`, `ui`, `error-handling`, `error-recovery`, `medium-priority`  
**Assignee:** [Ron - Frontend & UI Automation]  
**Estimate:** 2 hours

**Title:** Test Error Recovery

**Description:**
```
## 🎯 Goal
Implement E2E tests for error recovery scenarios. Ensure users can correct errors and retry operations successfully.

## 📝 Steps
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
3. Implement error recovery test for timeout:
   - Trigger timeout error
   - Verify error message is displayed
   - Resolve timeout issue (or wait for retry)
   - Click "Retry" button or "Start Streaming" again
   - Verify error message is cleared
   - Verify operation succeeds

## ✅ Acceptance Criteria
- [ ] User can correct errors and retry:
  - [ ] Validation errors can be corrected
  - [ ] Server errors can be retried after server recovery
  - [ ] Timeout errors can be retried
  - [ ] Retry functionality works correctly
- [ ] Error state cleanup working:
  - [ ] Error messages are cleared when error is resolved
  - [ ] Error indicators are removed
  - [ ] UI returns to normal state
  - [ ] No error state persists after successful operation
- [ ] No lingering error messages:
  - [ ] Error messages don't persist after correction
  - [ ] Error indicators don't remain visible
  - [ ] UI state is properly reset
  - [ ] Previous errors don't affect new operations
- [ ] Tests pass consistently
- [ ] Tests properly cleanup after execution

## 🔗 Dependencies
- Task 5.2 (Test Server Errors)

## 📎 Related Files
- `tests/e2e/test_error_handling.py`
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
| **5.1** | Test Validation Errors | 1 | 3 hours | Medium |
| **5.2** | Test Server Errors | 1 | 2 hours | Medium |
| **5.3** | Test Error Recovery | 1 | 2 hours | Medium |
| **Total** | | **2** | **7 hours** | |

### Dependency Chain

```
Task 5.1 (Test Validation Errors)
    ↓
Task 5.2 (Test Server Errors)
    ↓
Task 5.3 (Test Error Recovery)
```

---

## 📁 Expected Test Files

After completion, the following test files should exist:

```
tests/e2e/test_error_handling.py
├── test_user_sees_clear_error_for_invalid_nfft
├── test_user_sees_error_for_frequency_exceeds_limit
├── test_user_sees_error_for_invalid_channels
├── test_user_sees_error_when_server_unavailable
├── test_user_sees_error_for_timeout
├── test_user_can_correct_validation_error
├── test_user_can_retry_after_server_error
└── test_user_can_retry_after_timeout
```

---

## 🎯 Test Scenarios Coverage

### Validation Error Tests
1. **Invalid NFFT** - NFFT not power of 2
2. **Frequency Exceeds Limit** - Frequency > 1000 Hz
3. **Invalid Channels** - Invalid channel range

### Server Error Tests
1. **Server Unavailable** - Server down scenario
2. **Request Timeout** - Request timeout scenario

### Error Recovery Tests
1. **Correct Invalid Input** - User can fix validation errors
2. **Retry After Server Error** - User can retry after server recovery
3. **Retry After Timeout** - User can retry after timeout

---

## ✅ Overall Acceptance Criteria

- [ ] All 3 sub-tasks completed
- [ ] All 8 E2E tests implemented and passing
- [ ] Validation error tests working correctly
- [ ] Server error tests working correctly
- [ ] Error recovery tests working correctly
- [ ] All tests pass consistently
- [ ] Tests properly cleanup after execution
- [ ] Error messages are user-friendly
- [ ] Error state management working correctly

---

## 🔗 Related Dependencies

**Requires:**
- Playwright E2E Setup (PZ-XXXX) - Page Objects and Helpers must be ready
- Page Objects: `panda_app_page.py`, `configuration_panel.py`
- Helpers: `browser_helpers.py`, `assertion_helpers.py`

**Related Tickets:**
- PZ-13951: Live Mode E2E Tests (similar E2E patterns)
- PZ-13952: Historic Mode E2E Tests (similar E2E patterns)
- PZ-XXXX: Playwright E2E Framework Setup (required infrastructure)

---

## 📝 Test Implementation Notes

### Error Message Requirements
- **Clear and Specific:** Error messages should explain what is wrong
- **User-Friendly:** Avoid technical jargon, use plain language
- **Actionable:** Error messages should suggest how to fix the issue
- **Visual Indicators:** Invalid fields should be visually highlighted

### Error State Management
- **Error Display:** Errors should be clearly visible to users
- **Error Cleanup:** Errors should be cleared when resolved
- **State Reset:** UI should return to normal state after error resolution
- **No Persistence:** Previous errors should not affect new operations

### Test Data Requirements
- **Invalid NFFT Values:** 1000, 500, 1500 (not powers of 2)
- **Invalid Frequency Values:** 1500 Hz, 2000 Hz (> 1000 Hz limit)
- **Invalid Channel Ranges:** 100-50 (reversed), -1-10 (negative), 2223-2224 (exceeds max)
- **Server Error Simulation:** Stop server or use network throttling
- **Timeout Simulation:** Use network throttling or timeout configuration

---

**Last Updated:** 2025-11-04  
**Created by:** QA Team Lead  
**Status:** Ready for Jira Import

