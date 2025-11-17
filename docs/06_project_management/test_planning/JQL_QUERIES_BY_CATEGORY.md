# JQL Queries by Category - All New Tests
==========================================

**Date:** 2025-11-09  
**Purpose:** JQL queries organized by Xray folder/category for easy test assignment

---

## 🔐 Security Tests (10 tests)

**Folder:** `Panda MS3 → BE Tests → Focus Server Tests → Security Tests`  
**Test IDs:** PZ-14771, PZ-14772, PZ-14773, PZ-14774, PZ-14775, PZ-14776, PZ-14777, PZ-14778, PZ-14779, PZ-14788

### JQL Query:
```jql
project = PZ AND key IN (
  PZ-14771, PZ-14772, PZ-14773, PZ-14774, PZ-14775,
  PZ-14776, PZ-14777, PZ-14778, PZ-14779, PZ-14788
) ORDER BY key ASC
```

### Test List:
| # | Test ID | Summary |
|---|---------|---------|
| 1 | PZ-14771 | Security - API Authentication Required |
| 2 | PZ-14772 | Security - Invalid Authentication Token |
| 3 | PZ-14773 | Security - Expired Authentication Token |
| 4 | PZ-14774 | Security - SQL Injection Prevention |
| 5 | PZ-14775 | Security - XSS Prevention |
| 6 | PZ-14776 | Security - CSRF Protection |
| 7 | PZ-14777 | Security - Rate Limiting |
| 8 | PZ-14778 | Security - HTTPS Only |
| 9 | PZ-14779 | Security - Sensitive Data Exposure |
| 10 | PZ-14788 | Security - Input Sanitization |

---

## ⚠️ Error Handling Tests (8 tests)

**Folder:** `Panda MS3 → BE Tests → Focus Server Tests → Error Handling Tests`  
**Test IDs:** PZ-14780, PZ-14781, PZ-14782, PZ-14783, PZ-14784, PZ-14785, PZ-14786, PZ-14787

### JQL Query:
```jql
project = PZ AND key IN (
  PZ-14780, PZ-14781, PZ-14782, PZ-14783,
  PZ-14784, PZ-14785, PZ-14786, PZ-14787
) ORDER BY key ASC
```

### Test List:
| # | Test ID | Summary |
|---|---------|---------|
| 1 | PZ-14780 | Error Handling - 500 Internal Server Error |
| 2 | PZ-14781 | Error Handling - 503 Service Unavailable |
| 3 | PZ-14782 | Error Handling - 504 Gateway Timeout |
| 4 | PZ-14783 | Error Handling - Network Timeout |
| 5 | PZ-14784 | Error Handling - Connection Refused |
| 6 | PZ-14785 | Error Handling - Invalid JSON Payload |
| 7 | PZ-14786 | Error Handling - Malformed Request |
| 8 | PZ-14787 | Error Handling - Error Message Format |

---

## ⚡ Performance Tests (10 tests)

**Folder:** `Panda MS3 → BE Tests → Focus Server Tests → Performance Tests`  
**Test IDs:** PZ-14790, PZ-14791, PZ-14792, PZ-14793, PZ-14794, PZ-14795, PZ-14796, PZ-14797, PZ-14798, PZ-14799

### JQL Query:
```jql
project = PZ AND key IN (
  PZ-14790, PZ-14791, PZ-14792, PZ-14793, PZ-14794,
  PZ-14795, PZ-14796, PZ-14797, PZ-14798, PZ-14799
) ORDER BY key ASC
```

### Test List:
| # | Test ID | Summary |
|---|---------|---------|
| 1 | PZ-14790 | Performance - POST /configure Response Time |
| 2 | PZ-14791 | Performance - GET /waterfall Response Time |
| 3 | PZ-14792 | Performance - GET /metadata Response Time |
| 4 | PZ-14793 | Performance - Concurrent Requests Performance |
| 5 | PZ-14794 | Performance - Large Payload Handling |
| 6 | PZ-14795 | Performance - Memory Usage Under Load |
| 7 | PZ-14796 | Performance - CPU Usage Under Load |
| 8 | PZ-14797 | Performance - Database Query Performance |
| 9 | PZ-14798 | Performance - Network Latency Impact |
| 10 | PZ-14799 | Performance - End-to-End Latency |

---

## 📈 Load Tests (8 tests)

**Folder:** `Panda MS3 → BE Tests → Focus Server Tests → Load Tests`  
**Test IDs:** PZ-14800, PZ-14801, PZ-14802, PZ-14803, PZ-14804, PZ-14805, PZ-14806, PZ-14807

### JQL Query:
```jql
project = PZ AND key IN (
  PZ-14800, PZ-14801, PZ-14802, PZ-14803,
  PZ-14804, PZ-14805, PZ-14806, PZ-14807
) ORDER BY key ASC
```

### Test List:
| # | Test ID | Summary |
|---|---------|---------|
| 1 | PZ-14800 | Load - Concurrent Job Creation Load |
| 2 | PZ-14801 | Load - Sustained Load - 1 Hour |
| 3 | PZ-14802 | Load - Peak Load - High RPS |
| 4 | PZ-14803 | Load - Ramp-Up Load Profile |
| 5 | PZ-14804 | Load - Spike Load Profile |
| 6 | PZ-14805 | Load - Steady-State Load Profile |
| 7 | PZ-14806 | Load - Recovery After Load |
| 8 | PZ-14807 | Load - Resource Exhaustion Under Load |

---

## ✅ Data Quality Tests (5 tests)

**Folder:** `Panda MS3 → BE Tests → Focus Server Tests → Data Quality Tests`  
**Test IDs:** PZ-14808, PZ-14809, PZ-14810, PZ-14811, PZ-14812

### JQL Query:
```jql
project = PZ AND key IN (
  PZ-14808, PZ-14809, PZ-14810, PZ-14811, PZ-14812
) ORDER BY key ASC
```

### Test List:
| # | Test ID | Summary |
|---|---------|---------|
| 1 | PZ-14808 | Data Quality - Waterfall Data Consistency |
| 2 | PZ-14809 | Data Quality - Metadata Consistency |
| 3 | PZ-14810 | Data Quality - Data Integrity Across Requests |
| 4 | PZ-14811 | Data Quality - Timestamp Accuracy |
| 5 | PZ-14812 | Data Quality - Data Completeness |

---

## 📋 Complete JQL Query (All 41 Tests)

If you need to find all tests at once:

```jql
project = PZ AND key IN (
  PZ-14771, PZ-14772, PZ-14773, PZ-14774, PZ-14775,
  PZ-14776, PZ-14777, PZ-14778, PZ-14779, PZ-14780,
  PZ-14781, PZ-14782, PZ-14783, PZ-14784, PZ-14785,
  PZ-14786, PZ-14787, PZ-14788, PZ-14790, PZ-14791,
  PZ-14792, PZ-14793, PZ-14794, PZ-14795, PZ-14796,
  PZ-14797, PZ-14798, PZ-14799, PZ-14800, PZ-14801,
  PZ-14802, PZ-14803, PZ-14804, PZ-14805, PZ-14806,
  PZ-14807, PZ-14808, PZ-14809, PZ-14810, PZ-14811,
  PZ-14812
) ORDER BY key ASC
```

---

## 🎯 How to Use

### Step 1: Open Xray Test Repository
Navigate to:
```
https://prismaphotonics.atlassian.net/projects/PZ?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.xpandit.plugins.xray__testing-board#!page=test-repository
```

### Step 2: Navigate to Target Folder
For each category, navigate to the appropriate folder:
- Security Tests → `Panda MS3 → BE Tests → Focus Server Tests → Security Tests`
- Error Handling Tests → `Panda MS3 → BE Tests → Focus Server Tests → Error Handling Tests`
- Performance Tests → `Panda MS3 → BE Tests → Focus Server Tests → Performance Tests`
- Load Tests → `Panda MS3 → BE Tests → Focus Server Tests → Load Tests`
- Data Quality Tests → `Panda MS3 → BE Tests → Focus Server Tests → Data Quality Tests`

### Step 3: Search for Tests
1. Click "Search" or use the filter/search box
2. Paste the appropriate JQL query for the category
3. Press Enter

### Step 4: Select and Assign
1. Select all tests from search results
2. Drag and drop to the target folder
3. Or right-click → "Move to folder" → Select target folder

---

## 📊 Summary by Category

| Category | Tests | Test IDs Range | Folder Path |
|----------|-------|----------------|-------------|
| **Security** | 10 | PZ-14771 to PZ-14788* | Security Tests |
| **Error Handling** | 8 | PZ-14780 to PZ-14787 | Error Handling Tests |
| **Performance** | 10 | PZ-14790 to PZ-14799 | Performance Tests |
| **Load** | 8 | PZ-14800 to PZ-14807 | Load Tests |
| **Data Quality** | 5 | PZ-14808 to PZ-14812 | Data Quality Tests |
| **TOTAL** | **41** | **PZ-14771 to PZ-14812** | |

*Note: Security tests exclude PZ-14780-PZ-14787 (which are Error Handling tests)

---

**Last Updated:** 2025-11-09

