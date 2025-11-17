# 🔴 Xray Tests - Complete Fix Required
========================================

**Date:** 2025-11-08  
**Status:** 🔴 **URGENT - Tests Created But Need Proper Structure**  
**Tests:** PZ-14715 to PZ-14744 (30 tests)

---

## ❌ Problems Identified

1. **Test Type Field Not Set** - `customfield_10951` is null for all tests
2. **Description Format Wrong** - Not in proper Jira markup format
3. **Missing Test Steps Table** - No structured test steps
4. **Not in Folder** - Tests not assigned to folder `68d91b9f681e183ea2e83e16`
5. **Missing Required Sections** - Pre-Conditions, Test Data, Assertions, Post-Conditions not properly formatted

---

## ✅ Solution: Manual Update Required

### Step 1: Find Valid Test Type Values

**Action Required:** Check what values are valid for Test Type field.

**Method:**
1. Open any existing test in Jira that has Test Type set
2. Click Edit → Test Type field
3. See what options are available
4. Or check Xray documentation

**Possible Values (need verification):**
- Manual Test
- Automated Test  
- Integration Test
- Performance Test
- (Other values?)

---

### Step 2: Update Test Type Field

For each test (PZ-14715 to PZ-14744):

**Via Jira UI:**
1. Open test in Jira
2. Click **Edit**
3. Find field **"Test Type"**
4. Select correct value (verify what's available)
5. Save

**Via API (when we know the correct value):**
```python
# Example (need to verify correct value format)
issue.update(fields={'customfield_10951': {'value': 'Integration Test'}})
```

---

### Step 3: Update Description Format

Each test needs description in **Jira markup format**:

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

### Step 4: Add Test Steps via Xray UI

For each test:

1. Open test in Jira
2. Go to **Test Steps** section
3. Click **Add Step** or **Edit Steps**
4. Add each step with:
   - **Action:** What to do
   - **Data:** Input/data needed
   - **Expected Result:** What should happen

**Example for PZ-14715:**
- Step 1: Action: "Get current MongoDB pod name", Data: "namespace: panda, label: app=mongodb", Expected: "Pod name retrieved"
- Step 2: Action: "Verify MongoDB is accessible", Data: "MongoDB connection test", Expected: "MongoDB connection successful"
- ... (8 steps total)

---

### Step 5: Assign Tests to Folder

**Folder ID:** `68d91b9f681e183ea2e83e16`

**Method 1: Manual (Recommended)**
1. Go to Xray Test Repository
2. Navigate to folder
3. Select all tests (PZ-14715 to PZ-14744)
4. Drag and drop into folder

**Method 2: Xray API (Requires credentials)**
```bash
# For each test
PUT /rest/raven/1.0/api/testrepository/PZ/folders/68d91b9f681e183ea2e83e16/tests/{testKey}
```

---

## 📋 Test Details for Each Test

### PZ-14715: MongoDB Pod Deletion and Recreation

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

## 🚀 Next Steps

1. **Verify Test Type Values** - Check what values are valid
2. **Update All 30 Tests** - Set Test Type, update description, add test steps
3. **Assign to Folder** - Move all tests to folder `68d91b9f681e183ea2e83e16`
4. **Link to Requirement** - Link all tests to PZ-13756

---

## 📊 Progress Tracking

- [ ] Test Type values verified
- [ ] Test Type field updated (30 tests)
- [ ] Descriptions updated (30 tests)
- [ ] Test Steps added (30 tests)
- [ ] Tests assigned to folder (30 tests)
- [ ] Tests linked to requirement (30 tests)
- [ ] All tests verified

---

**Created:** 2025-11-08  
**Priority:** 🔴 **URGENT**  
**Action Required:** Manual update in Jira UI

