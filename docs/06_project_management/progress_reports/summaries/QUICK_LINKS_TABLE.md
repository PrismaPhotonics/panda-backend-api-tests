# 🔗 Quick Links Table - Code & Tests

## Copy-Paste Ready for Presentation

---

## **All 9 Examples - Full Links**

### **[P0] #1: ROI change limit - hardcoded 50%**
- **Code:** `vscode://file/C:/Projects/focus_server_automation/src/utils/validators.py:395`
- **Test:** `vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_dynamic_roi_adjustment.py:475`

### **[P0] #2: Performance assertions disabled (P95/P99)**
- **Code:** `vscode://file/C:/Projects/focus_server_automation/tests/integration/performance/test_performance_high_priority.py:67`
- **Test:** Same file (this IS the test with disabled assertions)

### **[P1] #3: NFFT validation too permissive**
- **Code:** `vscode://file/C:/Projects/focus_server_automation/src/utils/validators.py:194`
- **Test:** `vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_spectrogram_pipeline.py:98`

### **[P1] #4: Frequency range - no absolute max/min**
- **Code:** `vscode://file/C:/Projects/focus_server_automation/src/models/focus_server_models.py:46`
- **Test:** `vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_spectrogram_pipeline.py:159`

### **[P2] #5: Sensor range - no min/max ROI size**
- **Code:** `vscode://file/C:/Projects/focus_server_automation/src/utils/validators.py:116`
- **Test:** `vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_config_validation_high_priority.py:416`

### **[P2] #6: Polling helper - hardcoded timeouts**
- **Code:** `vscode://file/C:/Projects/focus_server_automation/src/utils/helpers.py:474`
- **Test:** `vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_live_monitoring_flow.py:184`

### **[P2] #7: Default payloads mismatch config**
- **Code:** `vscode://file/C:/Projects/focus_server_automation/src/utils/helpers.py:507`
- **Test:** Used by ALL config tests
- **Config:** `vscode://file/C:/Projects/focus_server_automation/config/environments.yaml:24`

### **[P3] #8: Config validation tests with TODO/no assertions**
- **Code:** `vscode://file/C:/Projects/focus_server_automation/tests/integration/api/test_config_validation_high_priority.py:475`
- **Test:** Same file (this IS the test with TODO)

### **[P3] #9: MongoDB outage resilience (behavior unclear)**
- **Code:** `vscode://file/C:/Projects/focus_server_automation/tests/performance/test_mongodb_outage_resilience.py:157`
- **Test:** Same file (this IS the test with unclear SLA)

---

## 📋 **Compact Format - For Quick Copy**

```
1. ROI 50%
   Code: validators.py:395
   Test: test_dynamic_roi_adjustment.py:475

2. Performance disabled
   Code: test_performance_high_priority.py:67
   Test: (same)

3. NFFT permissive
   Code: validators.py:194
   Test: test_spectrogram_pipeline.py:98

4. Frequency no max
   Code: focus_server_models.py:46
   Test: test_spectrogram_pipeline.py:159

5. Sensor no limits
   Code: validators.py:116
   Test: test_config_validation_high_priority.py:416

6. Polling hardcoded
   Code: helpers.py:474
   Test: test_live_monitoring_flow.py:184

7. Defaults mismatch
   Code: helpers.py:507
   Test: (all tests)

8. No assertions
   Code: test_config_validation_high_priority.py:475
   Test: (same)

9. MongoDB unclear
   Code: test_mongodb_outage_resilience.py:157
   Test: (same)
```

---

## ✅ **Ready to Use!**

