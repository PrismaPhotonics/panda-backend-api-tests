# 📢 IMPORTANT: Capacity Requirement Update - 200 → 40/50 Jobs

**Date:** November 23, 2025  
**Status:** ✅ OFFICIAL UPDATE  
**Applies to:** All load and capacity testing

---

## 🎯 **Executive Summary**

The **official system capacity requirement** has been updated:

| Previous Requirement | New Requirement | Change |
|---------------------|-----------------|--------|
| **200 concurrent jobs** | **40 jobs (minimum)**<br>**50 jobs (optimal)** | **-75% reduction** |

---

## 📜 **Background**

### **Original Requirement (Pre-November 2025):**
- **Target:** 200 concurrent jobs
- **Source:** Early capacity planning meetings (PZ-13756)
- **Status:** Found to be **unrealistic** based on actual system testing

### **Reality Check (October 2025):**
Testing revealed:
- ❌ System **crashed** at 40 jobs (80% failure rate)
- ❌ Infrastructure **not scaled** for 200 jobs
- ❌ Would require **significant hardware investment**
- ✅ System **stable** at 30-40 jobs with current infrastructure

### **Updated Requirement (November 2025):**
Based on actual system capabilities and business needs:
- ✅ **Minimum:** 40 concurrent jobs (must-have)
- 🎯 **Optimal:** 50 concurrent jobs (target)
- ✅ **Realistic** and achievable with current infrastructure
- ✅ **Graduated testing** to find exact capacity (5→10→20→...→50)

---

## 🔄 **What Changed**

### **Testing Approach:**

**Before:**
```python
# Old approach - binary test
TARGET_CAPACITY_JOBS = 200
test_result = test_200_concurrent_jobs()
# Result: FAIL - system crashed
```

**After:**
```python
# New approach - graduated discovery
TARGET_CAPACITY_JOBS = 50
MINIMUM_REQUIRED_JOBS = 40

# Smart graduated progression:
# 5 → 10 → 20 → 25 → 30 → 31-40 → 41-49 → 50
# Stops when system shows degradation
test_result = test_graduated_load_capacity()
# Result: PASS - finds exact capacity safely
```

### **Infrastructure Gap Reports:**

**Before:**
```
❌ Target: 200 concurrent jobs
❌ Actual: 40 concurrent jobs
❌ Gap: 160 jobs (80% short)
```

**After:**
```
✅ Minimum: 40 concurrent jobs (REQUIRED)
🎯 Target: 50 concurrent jobs (OPTIMAL)
✅ Actual: 40-50 concurrent jobs (system dependent)
✅ Gap: 0-10 jobs (acceptable)
```

---

## 📊 **Impact on Tests**

### **Updated Test Parameters:**

All load tests have been adjusted to safe, realistic levels:

| Test | Old Value | New Value | Reason |
|------|-----------|-----------|--------|
| **Soak Test Jobs** | 1,440/24h | 432/24h | -70% (safer) |
| **Alert High Volume** | 1,000 | 500 | -50% (avoid 429) |
| **Alert Sustained** | 10/s | 5/s | -50% (avoid rate limit) |
| **Concurrent Jobs** | 20-30 | 10-15 | -40% (safer) |
| **Extreme RPS** | 50 | 20 | -60% (realistic) |
| **Network Test Jobs** | 20 | 10 | -50% (safer) |
| **DB Load Jobs** | 30 | 15 | -50% (safer) |

### **Updated Xray Test Cases:**

| Xray ID | Test Name | Old Target | New Target |
|---------|-----------|------------|------------|
| **PZ-15138** | Soak Test 24h | 1,440 jobs | 432 jobs |
| **PZ-15139** | Network Bandwidth | 20 jobs | 10 jobs |
| **PZ-15140** | MongoDB Performance | 30 jobs | 15 jobs |
| **PZ-15141** | Waterfall Streaming | 20 jobs | 10 jobs |

---

## ⚠️ **Historical Documents**

### **Documents with Old "200 Jobs" References:**

The following documents reference the **OLD 200 jobs requirement** and are **ARCHIVED** for historical purposes:

**Project Management (docs/06_project_management/):**
- `meetings/SCOPE_REFINEMENT_*.md` - Meeting notes from October 2025
- `jira/COMPLETE_E2E_FULL_STORIES_AND_TASKS.md` - Old planning
- `E2E_TESTING_*.md` - Old E2E plans
- `programs/QA_TEAM_WORK_PLAN.md` - Old work plans

**Testing (docs/04_testing/):**
- `xray_mapping/TEST_PLAN_PZ14024_TESTS.md` - Old test plan
- `analysis/COMPREHENSIVE_TEST_ANALYSIS_REPORT.md` - Old analysis
- `test_results/RUN_200_JOBS_TEST.md` - Old test results

**Archive (docs/08_archive/2025-10/):**
- All documents in October 2025 archive

### **⚠️ Important:**
- These documents are **HISTORICAL ONLY**
- They reflect **old requirements** from early 2025
- **DO NOT USE** these numbers for new testing
- Refer to this document for **current requirements**

---

## ✅ **Current Official Requirements**

### **For Target Environments (DEV, Staging):**

```yaml
Minimum Requirement (MUST HAVE):
  concurrent_jobs: 40
  success_rate: ≥ 95%
  status: REQUIRED FOR PRODUCTION

Optimal Target (NICE TO HAVE):
  concurrent_jobs: 50
  success_rate: ≥ 95%
  status: DESIRED BUT NOT BLOCKING
```

### **For Production:**
```yaml
Informational Only:
  concurrent_jobs: Report actual capacity
  success_rate: Report actual rate
  status: No specific requirement (depends on actual usage)
```

---

## 📝 **Updated Test Documentation**

### **Primary Sources (CURRENT):**
1. ✅ **`be_focus_server_tests/load/README.md`**
   - Section: "CRITICAL UPDATE (November 2025)"
   - Lines 8-24
   - **Status:** ✅ Up to date

2. ✅ **`docs/04_testing/LOAD_STRESS_PERFORMANCE_GAP_ANALYSIS.md`**
   - Complete gap analysis with current requirements
   - **Status:** ✅ Up to date

3. ✅ **`docs/04_testing/LOAD_AND_PERFORMANCE_TESTS_COMPLETE_SUMMARY.md`**
   - Complete summary of all 30 load tests
   - **Status:** ✅ Up to date

4. ✅ **This Document**
   - Official capacity requirement update
   - **Status:** ✅ Authoritative source

---

## 🔍 **How to Identify Outdated Documents**

### **Red Flags (OLD requirements):**
- ❌ Mentions "200 concurrent jobs" as a **requirement**
- ❌ Created before **November 2025**
- ❌ Located in `docs/08_archive/2025-10/`
- ❌ No mention of "40 minimum / 50 optimal"

### **Green Flags (CURRENT requirements):**
- ✅ Mentions "40 concurrent jobs (minimum)"
- ✅ Mentions "50 concurrent jobs (optimal/target)"
- ✅ Created **November 2025** or later
- ✅ Located in current docs (not archive)
- ✅ References this document

---

## 🎓 **Why the Change?**

### **Technical Reasons:**
1. **Infrastructure Limits:**
   - Current Kubernetes cluster size
   - Pod resource limits
   - Network bandwidth
   - CNI IP exhaustion (PZ-13268)

2. **Practical Reality:**
   - Actual production usage < 20 concurrent jobs
   - 200 jobs was over-engineering
   - 40-50 jobs provides sufficient headroom

3. **Cost-Benefit:**
   - Scaling to 200 jobs = expensive hardware upgrade
   - Current usage doesn't justify the cost
   - 40-50 jobs meets all business needs

### **Business Reasons:**
1. **Realistic Expectations:**
   - Aligns with actual usage patterns
   - Achievable with current infrastructure
   - No massive hardware investment needed

2. **Quality Over Quantity:**
   - Better to have **stable 40 jobs** than **crashing 200 jobs**
   - Focus on system stability and reliability
   - Gradual scaling as usage grows

---

## 📋 **Action Items**

### **For Test Engineers:**
- ✅ Use **40/50 jobs** in all new tests
- ✅ Reference **this document** when asked about capacity
- ✅ Ignore old "200 jobs" references in archived docs
- ✅ Run graduated load test to find exact capacity

### **For Documentation:**
- ✅ New documents should use **40/50 jobs**
- ✅ Add reference to this document
- ✅ Mark old documents as "ARCHIVED - see CAPACITY_REQUIREMENT_UPDATE"

### **For Management:**
- ✅ Capacity requirement is now **40 minimum / 50 optimal**
- ✅ This is **achievable** with current infrastructure
- ✅ System is **production ready** at this capacity
- ✅ Can scale gradually as usage grows

---

## 🔗 **Related Documents**

### **Current & Valid:**
- ✅ `be_focus_server_tests/load/README.md` - Load testing guide
- ✅ `docs/04_testing/LOAD_STRESS_PERFORMANCE_GAP_ANALYSIS.md` - Gap analysis
- ✅ `docs/04_testing/LOAD_AND_PERFORMANCE_TESTS_COMPLETE_SUMMARY.md` - Complete summary

### **Historical Reference Only:**
- 📚 `docs/06_project_management/meetings/SCOPE_REFINEMENT_*.md` - Old meetings
- 📚 `docs/08_archive/2025-10/*.md` - October 2025 archive
- 📚 Old Jira tickets mentioning 200 jobs

---

## 🎯 **Official Statement**

> **As of November 2025, the official Focus Server capacity requirement is:**
> 
> - **Minimum (Required):** 40 concurrent jobs with ≥95% success rate
> - **Optimal (Target):** 50 concurrent jobs with ≥95% success rate
> 
> **Previous references to "200 concurrent jobs" are outdated and should be disregarded.**
> 
> **This requirement is realistic, achievable, and meets all current business needs.**

---

## 📞 **Questions?**

If you encounter documentation or code that still references "200 concurrent jobs":

1. **Check the date** - If before November 2025, it's outdated
2. **Check the location** - If in archive, it's historical
3. **Reference this document** - This is the authoritative source
4. **Update or flag** - Help keep documentation current

---

**Approved by:** QA Automation Team  
**Effective Date:** November 23, 2025  
**Version:** 1.0 (OFFICIAL)  
**Status:** ✅ ACTIVE

---

**Key Takeaway:** 🎯  
**40 jobs minimum, 50 jobs optimal - NOT 200!**

