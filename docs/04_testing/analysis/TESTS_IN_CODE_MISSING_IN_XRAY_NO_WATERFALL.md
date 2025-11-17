# 📊 Tests in Automation Code - Missing in Xray (NO WATERFALL)
## טסטים שכתבת בקוד אבל לא מתועדים ב-Jira Xray - ללא waterfall

**תאריך:** 2025-10-21  
**מקור קוד:** `tests/` directory (מסונן - ללא waterfall tests)  
**מקור Xray:** `docs/Tests_xray_21_10_25.csv` (257 tests)  

---

## 📈 סיכום מנהלים (ללא waterfall)

| מטריקה | ערך |
|--------|-----|
| **סה"כ test functions בקוד** | 234 |
| **טסטים הקשורים ל-waterfall** | ~65 |
| **טסטים ללא waterfall** | ~169 |
| **טסטים ב-Xray (non-waterfall)** | ~180 |
| **טסטים בקוד שחסרים ב-Xray** | ~11 (קריטיים בלבד) |

---

## ✅ 11 טסטים קריטיים לתעוד ב-Xray (ללא waterfall)

### 🔴 CRITICAL - Infrastructure & Smoke (6 tests)

#### 1. test_get_sensors_list
- **קטגוריה:** API Smoke Test
- **מה בודק:** GET /sensors endpoint
- **למה חשוב:** Prerequisite לכל sensor configuration
- **חסר ב-Xray:** ✅ צריך תיעוד

#### 2. test_mongodb_connection
- **קטגוריה:** Infrastructure
- **מה בודק:** חיבור ישיר ל-MongoDB (10.10.100.108:27017)
- **למה חשוב:** Diagnostic test - מבודד MongoDB issues
- **חסר ב-Xray:** ✅ צריך תיעוד

#### 3. test_kubernetes_connection  
- **קטגוריה:** Infrastructure
- **מה בודק:** K8s cluster health, pod status
- **למה חשוב:** Orchestration validation
- **חסר ב-Xray:** ✅ צריך תיעוד

#### 4. test_ssh_connection
- **קטגוריה:** Infrastructure
- **מה בודק:** SSH access (10.10.100.3 → 10.10.100.113)
- **למה חשוב:** Access לtroubleshooting
- **חסר ב-Xray:** ✅ צריך תיעוד

#### 5. test_nfft_variations
- **קטגוריה:** Validation
- **מה בודק:** כל ערכי NFFT (128-4096) עובדים
- **למה חשוב:** Functional coverage
- **חסר ב-Xray:** ✅ צריך תיעוד

#### 6. test_frequency_range_within_nyquist ⭐ **הכי קריטי!**
- **קטגוריה:** Data Quality
- **מה בודק:** אכיפת חוק Nyquist (max_freq ≤ PRR/2)
- **למה חשוב:** **מונע data corruption (aliasing)**
- **חסר ב-Xray:** ✅ **חובה לתעד** - זה המסוכן ביותר!

---

### 🟡 HIGH - Validation & Performance (5 tests)

#### 7. test_config_with_missing_start_time
- **קטגוריה:** Validation (Negative)
- **מה בודק:** Historic config ללא start_time
- **סטטוס:** ❌ חסר בקוד - צריך ליצור!
- **חסר ב-Xray:** ✅ צריך תיעוד

#### 8. test_config_with_missing_end_time
- **קטגוריה:** Validation (Negative)
- **מה בודק:** Historic config ללא end_time
- **סטטוס:** ❌ חסר בקוד - צריך ליצור!
- **חסר ב-Xray:** ✅ צריך תיעוד

#### 9. test_configuration_resource_estimation
- **קטגוריה:** Performance Planning
- **מה בודק:** Resource usage estimation (CPU, Memory, Bandwidth)
- **למה חשוב:** Capacity planning
- **חסר ב-Xray:** ✅ צריך תיעוד

#### 10. test_high_throughput_configuration
- **קטגוריה:** Performance (Stress)
- **מה בודק:** Config עם throughput > 50 Mbps
- **למה חשוב:** Max capacity validation
- **חסר ב-Xray:** ✅ צריך תיעוד

#### 11. test_low_throughput_configuration
- **קטגוריה:** Edge Case
- **מה בודק:** Config עם throughput < 1 Mbps
- **למה חשוב:** Min viable config
- **חסר ב-Xray:** ✅ צריך תיעוד

---

## 🗑️ מה מחקתי (waterfall related)

**הטסטים הבאים הוסרו מהרשימה כי קשורים ל-waterfall:**

1. ❌ `test_complete_live_monitoring_flow` - כולל waterfall polling
2. ❌ `test_waterfall_with_invalid_task_id` - waterfall endpoint
3. ❌ `test_rapid_waterfall_polling` - waterfall stress
4. ❌ `test_waterfall_with_zero_row_count` - waterfall validation
5. ❌ `test_waterfall_with_negative_row_count` - waterfall validation
6. ❌ `test_waterfall_with_very_large_row_count` - waterfall validation
7. ❌ `test_poll_waterfall_data_live_task` - waterfall polling
8. ❌ `test_poll_historic_playback_until_completion` - waterfall polling
9. ❌ כל טסט עם "waterfall" בשם

**סה"כ הוסרו:** ~65 טסטים שקשורים ל-waterfall

---

## 📝 פעולות נדרשות

### 1. תעד ב-Xray (9 טסטים קיימים):
```
✅ test_get_sensors_list
✅ test_mongodb_connection
✅ test_kubernetes_connection
✅ test_ssh_connection
✅ test_nfft_variations
✅ test_frequency_range_within_nyquist ⭐ קריטי!
✅ test_configuration_resource_estimation
✅ test_high_throughput_configuration
✅ test_low_throughput_configuration
```

### 2. צור בקוד + תעד בXray (2 טסטים):
```
❌ test_config_with_missing_start_time
❌ test_config_with_missing_end_time
```

### 3. Optional - ROI tests (אם ROI רלוונטי):
```
⚪ test_roi_verification_after_change
⚪ test_roi_concurrent_changes
⚪ test_roi_rollback_on_error
⚪ test_config_with_start_equals_end
⚪ test_historic_timeout_behavior
```

---

## 🏆 הטסט הכי קריטי

**🥇 test_frequency_range_within_nyquist**

**למה?**
- זה **היחיד** שאם לא בודקים, מקבלים **נתונים שגויים פיזיקלית**
- Aliasing = תדרים מזויפים = החלטות שגויות
- זה לא bug תוכנה - זה **חוק פיזיקלי** (Shannon-Nyquist)

כל השאר:
- Errors → יודעים שיש בעיה
- Crashes → רואים שזה לא עובד  
- Slow → מרגישים שזה איטי

אבל **Nyquist violation** → המערכת עובדת, נותנת נתונים, אבל הנתונים **שגויים**!

---

**Document Created:** 2025-10-21  
**Filtered:** ללא כל טסט waterfall  
**Ready For:** Xray documentation
