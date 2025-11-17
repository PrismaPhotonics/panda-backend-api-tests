# ⚠️ Xray Tests Need Proper Structure - Fix Required
====================================================

**Date:** 2025-11-08  
**Status:** 🔴 **URGENT FIX REQUIRED**  
**Issue:** Tests created but missing proper Xray structure

---

## 🔴 Problems Identified

1. **Missing Test Type Field** - Tests don't have Test Type custom field set
2. **Poor Description Format** - Description is not in proper Xray format
3. **Missing Test Steps Table** - No structured test steps table
4. **Not Assigned to Folder** - Tests not in folder `68d91b9f681e183ea2e83e16`
5. **Missing Required Sections** - Pre-Conditions, Test Data, Assertions, Post-Conditions not properly formatted

---

## ✅ Solution: Manual Update Required

### Step 1: Update Test Type Field

For each test (PZ-14715 to PZ-14744):

1. Open test in Jira
2. Click **Edit**
3. Find field **"Test Type"** (Custom Field ID: `customfield_10951`)
4. Set value to: **"Integration Test"**
5. Save

**Or via API:**
```python
issue.update(fields={'customfield_10951': {'value': 'Integration Test'}})
```

---

### Step 2: Update Description Format

Each test needs description in this format:

```
h2. Objective
[Objective text with business impact]

h2. Pre-Conditions
* [Pre-condition 1]
* [Pre-condition 2]
* [Pre-condition 3]

h2. Test Data
* [Test data item 1]
* [Test data item 2]

h2. Test Steps
|| # || Action || Data || Expected Result ||
| 1 | [Action] | [Data] | [Expected] |
| 2 | [Action] | [Data] | [Expected] |

h2. Expected Result
[Overall expected result]

h2. Assertions
* [Assertion 1]
* [Assertion 2]

h2. Post-Conditions
* [Post-condition 1]
* [Post-condition 2]

h2. Automation Status
✅ *Automated* with Pytest

*Test Function:* {code}test_function_name{code}
*Test File:* {code}tests/infrastructure/resilience/test_file.py{code}
*Test Class:* {code}TestClassName{code}

*Execution Command:*
{code}pytest tests/infrastructure/resilience/test_file.py::TestClassName::test_function_name -v{code}
```

---

### Step 3: Assign Tests to Folder

**Folder ID:** `68d91b9f681e183ea2e83e16`

**Method 1: Manual (Recommended)**
1. Go to Xray Test Repository
2. Navigate to folder
3. Drag and drop tests into folder

**Method 2: Xray API (Requires credentials)**
```bash
PUT /rest/raven/1.0/api/testrepository/PZ/folders/{folderId}/tests/{testKey}
```

---

## 📋 Test Details Template

For each test, extract from test code:

### Example: PZ-14715 (MongoDB Pod Deletion and Recreation)

**Objective:**
```
Validate that when MongoDB pod is deleted, Kubernetes automatically recreates it 
and the system recovers. This ensures high availability and resilience of the 
database layer, preventing data loss and service interruptions.
```

**Pre-Conditions:**
- Kubernetes cluster is accessible
- MongoDB deployment exists in namespace 'panda'
- MongoDB is accessible and functioning

**Test Data:**
- Namespace: panda
- Deployment: mongodb
- Label selector: app=mongodb

**Test Steps:**
| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Get current MongoDB pod name | namespace: panda, label: app=mongodb | Pod name retrieved |
| 2 | Verify MongoDB is accessible | MongoDB connection test | MongoDB connection successful |
| 3 | Delete MongoDB pod | kubectl delete pod <pod_name> | Pod deletion initiated |
| 4 | Wait for pod deletion | Timeout: 30 seconds | Pod deleted successfully |
| 5 | Wait for new pod to be created | Timeout: 60 seconds | New pod created automatically |
| 6 | Wait for new pod to be ready | Timeout: 120 seconds | Pod status: Running, Ready: True |
| 7 | Verify MongoDB connection restored | MongoDB connection test | MongoDB connection successful |
| 8 | Verify system functionality restored | Create test job via API | Job created successfully |

**Expected Result:**
- Pod deleted successfully
- New pod created automatically within 60 seconds
- New pod becomes ready within 120 seconds
- MongoDB connection restored
- System functionality restored

**Assertions:**
- Pod deleted successfully
- New pod created automatically within 60 seconds
- New pod becomes ready within 120 seconds
- MongoDB connection restored
- System functionality restored

**Post-Conditions:**
- MongoDB pod is running
- MongoDB connection is restored
- System functionality is verified

**Automation Info:**
- Test Function: `test_mongodb_pod_deletion_recreation`
- Test File: `tests/infrastructure/resilience/test_mongodb_pod_resilience.py`
- Test Class: `TestMongoDBPodResilience`
- Execution Command: `pytest tests/infrastructure/resilience/test_mongodb_pod_resilience.py::TestMongoDBPodResilience::test_mongodb_pod_deletion_recreation -v`

---

## 🚀 Quick Fix Script

A script `scripts/jira/fix_xray_tests_structure.py` will be created to:
1. Update Test Type field for all tests
2. Update descriptions with proper format
3. Generate test steps data for Xray API
4. Provide instructions for folder assignment

---

## 📊 Progress Tracking

- [ ] Test Type field updated (30 tests)
- [ ] Descriptions updated (30 tests)
- [ ] Test Steps added (30 tests)
- [ ] Tests assigned to folder (30 tests)
- [ ] All tests verified

---

**Next Steps:**
1. Run fix script (when ready)
2. Manually verify each test
3. Assign tests to folder
4. Link tests to requirement PZ-13756

---

**Created:** 2025-11-08  
**Priority:** 🔴 **URGENT**

