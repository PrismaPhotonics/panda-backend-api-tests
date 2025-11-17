# ניתוח כישלונות בדיקות - 2 בנובמבר 2025

## סיכום כללי
- **סה"כ בדיקות שרצו:** 142 (39 נכשלו, 97 עברו, 6 דילוגים)
- **זמן ריצה:** 189.63 שניות
- **סביבה:** Production (10.10.100.100)

## סיווג הכישלונות

### 1. באגים אמיתיים במערכת (BUGS) - 12 כישלונות

#### 1.1 באג קריטי - שרת מחזיר 500 errors
**כישלונות:** 8 בדיקות
```
- test_fft_window_size_validation
- test_overlap_percentage_validation  
- test_memory_usage_estimation
- test_e2e_configure_metadata_grpc_flow
- test_config_endpoint_p95_latency
- test_config_endpoint_p99_latency
- test_job_creation_time
- test_live_streaming_stability (חלקי)
```
**תיאור:** השרת מחזיר "too many 500 error responses" - זה באג קריטי בשרת
**חומרה:** קריטי
**המלצה:** לפתוח באג דחוף ב-Jira

#### 1.2 באג - Future timestamps מתקבלים במערכת
**כישלון:** `test_time_range_validation_future_timestamps`
**תיאור:** המערכת מקבלת timestamps עתידיים במקום לדחות אותם
**חומרה:** גבוהה
**המלצה:** לפתוח באג ב-Jira (PZ-13984 כבר קיים)

#### 1.3 באג - חוסר בשדות Metadata
**כישלון:** `test_live_monitoring_get_metadata`
**שדות חסרים:**
- `num_samples_per_trace`
- `dtype`
**חומרה:** גבוהה
**המלצה:** לפתוח באג ב-Jira (PZ-13985 כבר קיים)

#### 1.4 באג - בעיית חישוב Frequency Resolution
**כישלונות:** 3 בדיקות
```
- test_frequency_resolution_calculation (Expected: 1.953 Hz, Actual: 15.595 Hz)
- test_frequency_bins_count_calculation (Expected: 129, Actual: 16)
- test_lines_dt_calculation (Expected: 0.256 sec, Actual: 0.039 sec)
```
**תיאור:** חישובי תדר לא מדויקים - הבדלים משמעותיים
**חומרה:** בינונית
**המלצה:** לפתוח באג ב-Jira

### 2. בעיות קונפיגורציה (CONFIGURATION) - 15 כישלונות

#### 2.1 בעיית חיבור MongoDB
**כישלונות:** 11 בדיקות
```
- כל בדיקות ה-MongoDB (test_mongodb_*)
```
**בעיה:** חיבור ל-MongoDB נכשל - כנראה בעיית קונפיגורציה
**פתרון:** לבדוק את הגדרות החיבור ל-MongoDB

#### 2.2 בעיית חיבור Kubernetes
**כישלונות:** 2 בדיקות
```
- test_kubernetes_connection
- test_mongodb_scale_down_outage_returns_503_no_orchestration
```
**בעיה:** SSL certificate verification failed עבור 10.10.10.151:6443
**פתרון:** לעדכן את כתובת Kubernetes API ל-10.10.100.102:6443

#### 2.3 בעיית חיבור SSH
**כישלון:** `test_ssh_connection`
**בעיה:** החיבור SSH נכשל
**פתרון:** להשתמש בנתוני החיבור הנכונים (10.10.100.3 -> 10.10.100.113)

### 3. בעיות Validation בטסטים (TEST ISSUES) - 12 כישלונות

#### 3.1 בעיית Pydantic Validation - channels.min
**כישלונות:** 7 בדיקות
```
- test_configuration_with_extreme_values
- test_historic_playback_* (5 בדיקות)
```
**בעיה:** `channels.min` מקבל 0 במקום ערך >= 1
**פתרון:** לתקן את הטסטים להעביר ערכי channels תקינים

#### 3.2 בעיית Validation - Waterfall View
**כישלונות:** 2 בדיקות
```
- test_valid_view_types
- test_waterfall_view_handling
```
**בעיה:** `displayTimeAxisDuration` לא רלוונטי ל-Waterfall view
**פתרון:** להסיר את הפרמטר כשמשתמשים ב-Waterfall

#### 3.3 בעיות Validation אחרות
**כישלונות:** 3 בדיקות
```
- test_time_range_validation_reversed_range (end_time < start_time)
- test_singlechannel_polling_stability (API error)
- test_multichannel_mapping_calculation (channel grouping)
- test_stream_amount_calculation (streams != channels)
```

## סיכום וטבלת סיווג

| קטגוריה | מספר כישלונות | אחוז | פעולה נדרשת |
|---------|-------------|------|-------------|
| באגים אמיתיים | 12 | 31% | לפתוח ב-Jira |
| בעיות קונפיגורציה | 15 | 38% | לתקן הגדרות |
| בעיות בטסטים | 12 | 31% | לתקן קוד טסט |

## באגים לפתיחה ב-Jira (רק האמיתיים)

### באגים חדשים לפתוח:
1. **500 Server Errors** - קריטי
   - השרת מחזיר שגיאות 500 באופן קבוע
   - משפיע על 8+ בדיקות
   
2. **Frequency Calculations Mismatch** - בינוני
   - חישובי תדר לא מדויקים
   - הבדלים של פי 8 בחישובים

### באגים קיימים שכבר מכוסים:
- PZ-13984: Future Timestamps Accepted
- PZ-13985: Live Metadata Missing Fields

## תיקונים דחופים נדרשים

### קונפיגורציה:
1. עדכון כתובת Kubernetes API מ-10.10.10.151 ל-10.10.100.102
2. בדיקת חיבור MongoDB
3. תיקון הגדרות SSH

### טסטים:
1. תיקון ערכי channels.min בכל הטסטים (>= 1)
2. הסרת displayTimeAxisDuration מטסטי Waterfall
3. תיקון reversed time ranges בטסטים
