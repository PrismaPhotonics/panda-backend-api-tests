# JQL Query for API Endpoint Tests
===================================

**Tests:** PZ-14750 to PZ-14764 (15 tests)  
**Purpose:** Find and assign all API endpoint tests to Xray folder

**Note:** For all new tests (Security, Error Handling, Performance, Load, Data Quality), see: `JQL_QUERIES_BY_CATEGORY.md`

---

## 📋 JQL Query (Copy-Paste Ready)

```jql
project = PZ AND key IN (
  PZ-14750, PZ-14751, PZ-14752, PZ-14753, PZ-14754,
  PZ-14755, PZ-14756, PZ-14757, PZ-14758, PZ-14759,
  PZ-14760, PZ-14761, PZ-14762, PZ-14763, PZ-14764
) ORDER BY key ASC
```

---

## 🎯 How to Use

### Step 1: Copy the JQL Query
Copy the query above.

### Step 2: Open Xray Test Repository
Navigate to:
```
https://prismaphotonics.atlassian.net/projects/PZ?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.xpandit.plugins.xray__testing-board#!page=test-repository
```

### Step 3: Paste JQL Query
- Click on "Search" or use the filter/search box
- Paste the JQL query
- Press Enter

### Step 4: Select All Tests
- All 15 tests should appear in the results
- Select all tests (use checkbox or Ctrl+A)

### Step 5: Assign to Folder
- Navigate to folder: `Panda MS3 → BE Tests → Focus Server Tests → API Tests`
- Drag and drop selected tests to the folder
- Or right-click → "Move to folder" → Select `API Tests`

---

## 📊 Test List

| # | Test ID | Test Name |
|---|---------|-----------|
| 1 | PZ-14750 | POST /config/{task_id} - Valid Configuration |
| 2 | PZ-14751 | POST /config/{task_id} - Invalid Task ID |
| 3 | PZ-14752 | POST /config/{task_id} - Missing Required Fields |
| 4 | PZ-14753 | POST /config/{task_id} - Invalid Sensor Range |
| 5 | PZ-14754 | POST /config/{task_id} - Invalid Frequency Range |
| 6 | PZ-14755 | GET /waterfall/{task_id}/{row_count} - Valid Request |
| 7 | PZ-14756 | GET /waterfall/{task_id}/{row_count} - No Data Available |
| 8 | PZ-14757 | GET /waterfall/{task_id}/{row_count} - Invalid Task ID |
| 9 | PZ-14758 | GET /waterfall/{task_id}/{row_count} - Invalid Row Count |
| 10 | PZ-14759 | GET /waterfall/{task_id}/{row_count} - Baby Analyzer Exited |
| 11 | PZ-14760 | GET /metadata/{task_id} - Valid Request |
| 12 | PZ-14761 | GET /metadata/{task_id} - Consumer Not Running |
| 13 | PZ-14762 | GET /metadata/{task_id} - Invalid Task ID |
| 14 | PZ-14763 | GET /metadata/{task_id} - Metadata Consistency |
| 15 | PZ-14764 | GET /metadata/{task_id} - Response Time |

---

## 🔧 Alternative: Use Script

You can also use the script to generate the JQL query:

```bash
python scripts/jira/assign_api_tests_to_xray_folder.py --verify-only
```

This will:
- Verify all 15 tests exist
- Print the JQL query in the correct format

---

**Last Updated:** 2025-11-09

