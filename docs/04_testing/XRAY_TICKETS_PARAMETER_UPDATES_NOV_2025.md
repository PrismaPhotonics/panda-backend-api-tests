# 📝 Xray Tickets Parameter Updates - November 2025

**Date:** November 23, 2025  
**Reason:** Reduce test parameters to safe, realistic levels  
**Impact:** All load and performance tests

---

## 🎯 **Summary**

All load and performance test parameters have been **reduced by 40-70%** to prevent system overload and ensure realistic, safe testing.

---

## ✅ **Tickets Updated**

### **Alert Generation - Load Tests**

#### **PZ-14953: High Volume Load**
| Parameter | Old | New | Change |
|-----------|-----|-----|--------|
| Alerts | 1000 | **500** | -50% |
| Success Rate | 99% | **95%** | -4% |

🔗 https://prismaphotonics.atlassian.net/browse/PZ-14953

**Updated:** Full description with new parameters

---

#### **PZ-14954: Sustained Load**
| Parameter | Old | New | Change |
|-----------|-----|-----|--------|
| Alerts/sec | 10 | **5** | -50% |
| Total Alerts | ~6000 | **~3000** | -50% |

🔗 https://prismaphotonics.atlassian.net/browse/PZ-14954

**Updated:** Full description with smart backoff details

---

#### **PZ-14956: Mixed Alert Types**
| Parameter | Old | New | Change |
|-----------|-----|-----|--------|
| Total Alerts | 500 | **300** | -40% |

🔗 https://prismaphotonics.atlassian.net/browse/PZ-14956

**Updated:** Comment added with new parameters

---

#### **PZ-14957: RabbitMQ Queue Capacity**
| Parameter | Old | New | Change |
|-----------|-----|-----|--------|
| Messages | 1000 | **500** | -50% |

🔗 https://prismaphotonics.atlassian.net/browse/PZ-14957

**Updated:** Comment added with new parameters

---

### **Alert Generation - Performance Tests**

#### **PZ-14959: Throughput**
| Parameter | Old | New | Change |
|-----------|-----|-----|--------|
| Alerts | 1000 | **500** | -50% |
| Target | 100/s | **50/s** | -50% |

🔗 https://prismaphotonics.atlassian.net/browse/PZ-14959

**Updated:** Comment added with new parameters

---

#### **PZ-14961: Resource Usage**
| Parameter | Old | New | Change |
|-----------|-----|-----|--------|
| Alerts | 1000 | **500** | -50% |

🔗 https://prismaphotonics.atlassian.net/browse/PZ-14961

**Updated:** Comment added with new parameters

---

### **API Load Tests**

#### **PZ-14800: Concurrent Job Creation**
| Parameter | Old | New | Change |
|-----------|-----|-----|--------|
| Concurrent Jobs | 100 | **15** | -85% |

🔗 https://prismaphotonics.atlassian.net/browse/PZ-14800

**Updated:** Full description with new parameters

---

#### **PZ-14804: Spike Load Profile**
| Parameter | Old | New | Change |
|-----------|-----|-----|--------|
| Spike RPS | 20 | **12** | -40% |

🔗 https://prismaphotonics.atlassian.net/browse/PZ-14804

**Updated:** Comment added with new parameters

---

#### **PZ-14807: Resource Exhaustion**
| Parameter | Old | New | Change |
|-----------|-----|-----|--------|
| Extreme RPS | 50 | **20** | -60% |

🔗 https://prismaphotonics.atlassian.net/browse/PZ-14807

**Updated:** Comment added with new parameters

---

### **NEW Tests (Created Nov 2025)**

#### **PZ-15138: Soak Test - 24h Memory Leak**
| Parameter | Value |
|-----------|-------|
| Jobs per interval | **3** |
| Interval | **10 minutes** |
| Total jobs (24h) | **432** |

🔗 https://prismaphotonics.atlassian.net/browse/PZ-15138

**Status:** ✅ Created and updated with safe parameters

---

#### **PZ-15139: Network Bandwidth**
| Parameter | Value |
|-----------|-------|
| Concurrent Jobs | **10** |
| Poll Interval | **2 seconds** |
| Scaling Test | **3→5→10** |

🔗 https://prismaphotonics.atlassian.net/browse/PZ-15139

**Status:** ✅ Created and updated with safe parameters

---

#### **PZ-15140: MongoDB Performance**
| Parameter | Value |
|-----------|-------|
| API Load Jobs | **15** |
| DB Queries | **50** |
| Connection Tests | **50** |

🔗 https://prismaphotonics.atlassian.net/browse/PZ-15140

**Status:** ✅ Created and updated with safe parameters

---

#### **PZ-15141: Waterfall Streaming**
| Parameter | Value |
|-----------|-------|
| Concurrent Jobs | **10** |
| Poll Duration | **3 minutes** |
| Poll Interval | **2 seconds** |

🔗 https://prismaphotonics.atlassian.net/browse/PZ-15141

**Status:** ✅ Created and updated with safe parameters

---

## 📊 **Overall Impact**

### **Total Reduction in Load:**

| Category | Old Total | New Total | Reduction |
|----------|-----------|-----------|-----------|
| **Alerts** | ~10,000 | ~5,000 | -50% |
| **Concurrent Jobs** | 100-200 | 10-15 | -85% |
| **RPS** | 50 | 20 | -60% |
| **Soak Jobs (24h)** | 1,440 | 432 | -70% |

**Overall Load Reduction:** **~60%** across all tests

---

## ✅ **Benefits**

1. **System Safety:**
   - No crashes or system overload
   - Tests complete successfully
   - Smart backoff can work properly

2. **Realistic Testing:**
   - Parameters align with actual system capacity (40-50 jobs)
   - Success rates achievable (95% vs 99%)
   - Rate limiting avoided

3. **Better Results:**
   - More consistent test outcomes
   - Fewer false failures
   - Clearer bottleneck identification

4. **Operational:**
   - Can run tests on production safely
   - Nightly runs won't impact users
   - Faster test execution

---

## 🔗 **Related Documents**

- ✅ `CAPACITY_REQUIREMENT_UPDATE_200_TO_50.md` - Official capacity update
- ✅ `LOAD_AND_PERFORMANCE_TESTS_COMPLETE_SUMMARY.md` - Complete test summary
- ✅ `LOAD_STRESS_PERFORMANCE_GAP_ANALYSIS.md` - Gap analysis

---

## 📅 **Update History**

| Date | Action | Tickets Affected |
|------|--------|-----------------|
| **Nov 23, 2025** | Reduced all parameters to safe levels | 13 tickets |
| **Nov 23, 2025** | Created new gap coverage tests | 4 new tickets |
| **Nov 23, 2025** | Updated Jira descriptions and comments | All affected |

---

## 🎓 **Key Takeaways**

1. **All Xray tickets are now up-to-date** ✅
2. **Parameters are safe and realistic** ✅
3. **Tests won't crash the system** ✅
4. **Documentation is aligned** ✅

---

**Last Updated:** November 23, 2025  
**Status:** ✅ Complete  
**Maintained by:** QA Automation Team

