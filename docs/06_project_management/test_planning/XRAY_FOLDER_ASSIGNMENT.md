# Xray Folder Assignment - API Endpoints Tests
==============================================

**Date:** 2025-11-09  
**Tests:** PZ-14750 to PZ-14764 (15 tests)  
**Target Folder:** `Panda MS3` → `BE Tests` → `Focus Server Tests` → `API Tests`

---

## 🔍 JQL Query to Find Tests

### Single JQL Query (All 15 Tests)

```jql
project = PZ AND key IN (
  PZ-14750, PZ-14751, PZ-14752, PZ-14753, PZ-14754,
  PZ-14755, PZ-14756, PZ-14757, PZ-14758, PZ-14759,
  PZ-14760, PZ-14761, PZ-14762, PZ-14763, PZ-14764
) ORDER BY key ASC
```

### Alternative JQL Query (By Range)

```jql
project = PZ AND key >= PZ-14750 AND key <= PZ-14764 ORDER BY key ASC
```

### JQL Query with Labels Filter

```jql
project = PZ AND labels in (api_test_panda) AND type = Test AND issuekey >= PZ-14750 AND issuekey <= PZ-14764
```

---

## 📁 Target Folder Structure

**Full Path:**
```
Panda MS3
  └── BE Tests
      └── Focus Server Tests
          └── API Tests  ← Target folder
```

**Folder ID:** (Need to verify in Xray UI)

---

## 🎯 Steps to Assign Tests to Folder

### Method 1: Via Xray Test Repository UI (Recommended)

1. **Navigate to Xray Test Repository:**
   ```
   https://prismaphotonics.atlassian.net/projects/PZ?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.xpandit.plugins.xray__testing-board#!page=test-repository
   ```

2. **Navigate to Target Folder:**
   - Expand: `Panda MS3` → `BE Tests` → `Focus Server Tests`
   - Click on: `API Tests` folder (or create it if doesn't exist)

3. **Search for Tests:**
   - Use JQL query in search:
   ```jql
   project = PZ AND key IN (
     PZ-14750, PZ-14751, PZ-14752, PZ-14753, PZ-14754,
     PZ-14755, PZ-14756, PZ-14757, PZ-14758, PZ-14759,
     PZ-14760, PZ-14761, PZ-14762, PZ-14763, PZ-14764
   ) ORDER BY key ASC
   ```

4. **Select All Tests:**
   - Select all 15 tests from search results
   - Use bulk selection if available

5. **Drag and Drop:**
   - Drag selected tests to `API Tests` folder
   - Or use "Move to folder" option if available

---

### Method 2: Via Xray REST API (If Available)

**Note:** Requires Xray API credentials and folder ID

```python
import requests

# Xray API endpoint
xray_api_url = "https://prismaphotonics.atlassian.net/rest/raven/1.0/api/test"

# Folder ID (need to get from Xray UI)
folder_id = "YOUR_FOLDER_ID_HERE"

# Test keys
test_keys = [
    "PZ-14750", "PZ-14751", "PZ-14752", "PZ-14753", "PZ-14754",
    "PZ-14755", "PZ-14756", "PZ-14757", "PZ-14758", "PZ-14759",
    "PZ-14760", "PZ-14761", "PZ-14762", "PZ-14763", "PZ-14764"
]

# Assign each test to folder
for test_key in test_keys:
    # Xray API call to assign test to folder
    # (Exact endpoint depends on Xray version)
    pass
```

---

## 📋 Test List for Manual Assignment

### POST /config/{task_id} Tests (5 tests)
- PZ-14750
- PZ-14751
- PZ-14752
- PZ-14753
- PZ-14754

### GET /waterfall/{task_id}/{row_count} Tests (5 tests)
- PZ-14755
- PZ-14756
- PZ-14757
- PZ-14758
- PZ-14759

### GET /metadata/{task_id} Tests (5 tests)
- PZ-14760
- PZ-14761
- PZ-14762
- PZ-14763
- PZ-14764

---

## 🔗 Direct Links to Tests

### POST /config/{task_id} Tests
- [PZ-14750](https://prismaphotonics.atlassian.net/browse/PZ-14750)
- [PZ-14751](https://prismaphotonics.atlassian.net/browse/PZ-14751)
- [PZ-14752](https://prismaphotonics.atlassian.net/browse/PZ-14752)
- [PZ-14753](https://prismaphotonics.atlassian.net/browse/PZ-14753)
- [PZ-14754](https://prismaphotonics.atlassian.net/browse/PZ-14754)

### GET /waterfall/{task_id}/{row_count} Tests
- [PZ-14755](https://prismaphotonics.atlassian.net/browse/PZ-14755)
- [PZ-14756](https://prismaphotonics.atlassian.net/browse/PZ-14756)
- [PZ-14757](https://prismaphotonics.atlassian.net/browse/PZ-14757)
- [PZ-14758](https://prismaphotonics.atlassian.net/browse/PZ-14758)
- [PZ-14759](https://prismaphotonics.atlassian.net/browse/PZ-14759)

### GET /metadata/{task_id} Tests
- [PZ-14760](https://prismaphotonics.atlassian.net/browse/PZ-14760)
- [PZ-14761](https://prismaphotonics.atlassian.net/browse/PZ-14761)
- [PZ-14762](https://prismaphotonics.atlassian.net/browse/PZ-14762)
- [PZ-14763](https://prismaphotonics.atlassian.net/browse/PZ-14763)
- [PZ-14764](https://prismaphotonics.atlassian.net/browse/PZ-14764)

---

## 📝 Quick Copy-Paste JQL

**Copy this JQL query:**

```jql
project = PZ AND key IN (
  PZ-14750, PZ-14751, PZ-14752, PZ-14753, PZ-14754,
  PZ-14755, PZ-14756, PZ-14757, PZ-14758, PZ-14759,
  PZ-14760, PZ-14761, PZ-14762, PZ-14763, PZ-14764
) ORDER BY key ASC
```

**Or shorter version:**

```jql
project = PZ AND key >= PZ-14750 AND key <= PZ-14764 ORDER BY key ASC
```

---

## 🎯 Instructions for Manual Assignment

1. **Open Xray Test Repository:**
   - Go to: https://prismaphotonics.atlassian.net/projects/PZ?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.xpandit.plugins.xray__testing-board#!page=test-repository

2. **Navigate to Folder:**
   - Expand: `Panda MS3` → `BE Tests` → `Focus Server Tests`
   - Open or create: `API Tests` folder

3. **Search Tests:**
   - Click "Search" or use filter
   - Paste JQL query:
   ```jql
   project = PZ AND key IN (
     PZ-14750, PZ-14751, PZ-14752, PZ-14753, PZ-14754,
     PZ-14755, PZ-14756, PZ-14757, PZ-14758, PZ-14759,
     PZ-14760, PZ-14761, PZ-14762, PZ-14763, PZ-14764
   ) ORDER BY key ASC
   ```

4. **Select All:**
   - Select all 15 tests from results
   - Use checkbox to select all

5. **Move to Folder:**
   - Right-click → "Move to folder" → Select `API Tests`
   - Or drag and drop to folder

---

## ✅ Verification

After assignment, verify by:
1. Navigate to `API Tests` folder
2. Verify all 15 tests are visible
3. Check test count matches: 15 tests

---

**Last Updated:** 2025-11-09

