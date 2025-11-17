# 📁 Xray Tests Folder Assignment - Manual Instructions
========================================================

**Date:** 2025-11-08  
**Status:** ⚠️ **MANUAL ACTION REQUIRED**  
**Tests:** PZ-14715 to PZ-14744 (30 tests)  
**Target Folder:** `Panda MS3 > BE Tests > Focus Server Tests > infrastructure Tests`

---

## 🎯 Objective

Assign all 30 Infrastructure Resilience tests to the **"infrastructure Tests"** folder in the Xray Test Repository.

---

## 📋 Test List

### MongoDB Pod Resilience (6 tests)
- PZ-14715: MongoDB Pod Deletion and Recreation
- PZ-14716: MongoDB Scale Down to 0 Replicas
- PZ-14717: MongoDB Pod Restart During Job Creation
- PZ-14718: MongoDB Outage Graceful Degradation
- PZ-14719: MongoDB Recovery After Outage
- PZ-14720: MongoDB Pod Status Monitoring

### RabbitMQ Pod Resilience (6 tests)
- PZ-14721: RabbitMQ Pod Deletion and Recreation
- PZ-14722: RabbitMQ Scale Down to 0 Replicas
- PZ-14723: RabbitMQ Pod Restart During Job Creation
- PZ-14724: RabbitMQ Outage Graceful Degradation
- PZ-14725: RabbitMQ Recovery After Outage
- PZ-14726: RabbitMQ Pod Status Monitoring

### Focus Server Pod Resilience (6 tests)
- PZ-14727: Focus Server Pod Deletion and Recreation
- PZ-14728: Focus Server Scale Down to 0 Replicas
- PZ-14729: Focus Server Pod Restart During Job Creation
- PZ-14730: Focus Server Outage Graceful Degradation
- PZ-14731: Focus Server Recovery After Outage
- PZ-14732: Focus Server Pod Status Monitoring

### SEGY Recorder Pod Resilience (5 tests)
- PZ-14733: SEGY Recorder Pod Deletion and Recreation
- PZ-14734: SEGY Recorder Scale Down to 0 Replicas
- PZ-14735: SEGY Recorder Pod Restart During Recording
- PZ-14736: SEGY Recorder Outage Behavior
- PZ-14737: SEGY Recorder Recovery After Outage

### Multiple Pods Resilience (4 tests)
- PZ-14738: MongoDB + RabbitMQ Down Simultaneously
- PZ-14739: MongoDB + Focus Server Down Simultaneously
- PZ-14740: RabbitMQ + Focus Server Down Simultaneously
- PZ-14741: Focus Server + SEGY Recorder Down Simultaneously

### Pod Recovery Scenarios (3 tests)
- PZ-14742: Recovery Order Validation
- PZ-14743: Cascading Recovery Scenarios
- PZ-14744: Recovery Time Measurement

---

## 📍 Target Folder Path

**Full Path:** `Panda MS3 > BE Tests > Focus Server Tests > infrastructure Tests`

**Current Location in Test Repository:**
```
Panda MS3 (165 tests)
  └── BE Tests (151 tests)
      └── Focus Server Tests (151 tests)
          └── infrastructure Tests (6 tests) ← TARGET FOLDER
```

---

## 🔧 Manual Assignment Steps

### Method 1: Drag and Drop (Recommended)

1. **Open Xray Test Repository:**
   - Go to: https://prismaphotonics.atlassian.net/projects/PZ?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.xpandit.plugins.xray__testing-board#!page=test-repository

2. **Navigate to Target Folder:**
   - Expand: `Panda MS3`
   - Expand: `BE Tests`
   - Expand: `Focus Server Tests`
   - Click on: `infrastructure Tests` (should show 6 tests currently)

3. **Search for All Tests:**
   - Use the search bar at the top
   - Search for: `PZ-14715 OR PZ-14716 OR PZ-14717 OR ... OR PZ-14744`
   - Or search for: `project = PZ AND key IN (PZ-14715, PZ-14716, ..., PZ-14744)`

4. **Select All Tests:**
   - Select all 30 tests (use checkbox or Ctrl+A)
   - Or select them one by one

5. **Drag and Drop:**
   - Drag the selected tests
   - Drop them into the `infrastructure Tests` folder
   - Confirm the move if prompted

---

### Method 2: Bulk Move via Search

1. **Open Xray Test Repository:**
   - Go to: https://prismaphotonics.atlassian.net/projects/PZ?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.xpandit.plugins.xray__testing-board#!page=test-repository

2. **Use Advanced Search:**
   - Click on "Advanced Search" or use JQL
   - Enter: `project = PZ AND key IN (PZ-14715, PZ-14716, PZ-14717, PZ-14718, PZ-14719, PZ-14720, PZ-14721, PZ-14722, PZ-14723, PZ-14724, PZ-14725, PZ-14726, PZ-14727, PZ-14728, PZ-14729, PZ-14730, PZ-14731, PZ-14732, PZ-14733, PZ-14734, PZ-14735, PZ-14736, PZ-14737, PZ-14738, PZ-14739, PZ-14740, PZ-14741, PZ-14742, PZ-14743, PZ-14744)`

3. **Select All Results:**
   - Select all 30 tests from the search results

4. **Move to Folder:**
   - Right-click on selected tests
   - Choose "Move to Folder" or "Assign to Folder"
   - Navigate to: `Panda MS3 > BE Tests > Focus Server Tests > infrastructure Tests`
   - Confirm

---

### Method 3: Individual Assignment

If bulk move doesn't work, assign each test individually:

1. **Open each test** (PZ-14715 to PZ-14744)
2. **Click "Edit"** or "More" → "Edit"
3. **Find "Test Repository"** or "Folder" field
4. **Select:** `Panda MS3 > BE Tests > Focus Server Tests > infrastructure Tests`
5. **Save**

---

## ✅ Verification

After assignment, verify:

1. **Go to Test Repository:**
   - Navigate to: `Panda MS3 > BE Tests > Focus Server Tests > infrastructure Tests`

2. **Check Test Count:**
   - Should show: **36 tests** (6 existing + 30 new = 36 total)

3. **Verify All Tests Present:**
   - All 30 tests (PZ-14715 to PZ-14744) should be visible in the folder

---

## 🔍 Quick Test Search JQL

Use this JQL query to find all tests at once:

```jql
project = PZ AND key IN (
  PZ-14715, PZ-14716, PZ-14717, PZ-14718, PZ-14719, PZ-14720,
  PZ-14721, PZ-14722, PZ-14723, PZ-14724, PZ-14725, PZ-14726,
  PZ-14727, PZ-14728, PZ-14729, PZ-14730, PZ-14731, PZ-14732,
  PZ-14733, PZ-14734, PZ-14735, PZ-14736, PZ-14737, PZ-14738,
  PZ-14739, PZ-14740, PZ-14741, PZ-14742, PZ-14743, PZ-14744
) ORDER BY key ASC
```

---

## 📝 Notes

- **Xray API Required:** Folder assignment requires Xray API, not standard Jira API
- **Manual Action:** Currently, manual assignment via UI is the most reliable method
- **Folder Structure:** The folder structure is: `Panda MS3 > BE Tests > Focus Server Tests > infrastructure Tests`
- **Test Count:** After assignment, the folder should contain 36 tests (6 existing + 30 new)

---

## 🚀 Alternative: Xray API (If Available)

If Xray API credentials are available, you can use:

```bash
# For each test
PUT /rest/raven/1.0/api/testrepository/PZ/folders/{folder_id}/tests/{test_key}
```

**Note:** This requires:
- Xray API credentials
- Folder ID (needs to be retrieved from Xray API)
- Proper authentication

---

**Created:** 2025-11-08  
**Priority:** ⚠️ **MANUAL ACTION REQUIRED**  
**Estimated Time:** 5-10 minutes

