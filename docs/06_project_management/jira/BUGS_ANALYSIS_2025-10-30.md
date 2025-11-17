# 🐛 ניתוח באגים - הרצת אוטומציה 30.10.2025

## 📊 סיכום מהיר:
- **סה"כ טסטים שרצו:** 144 (עם marker xray)
- **עבר:** 100 ✅
- **נכשל:** 37 ❌
- **דילג:** 6 ⏭️
- **שגיאות:** 1 ⚠️

---

## 🔴 באגים קריטיים שצריך לפתוח (CRITICAL - P1)

### 1. **Focus Server: Too Many 500 Errors** 🔥
**חומרה:** CRITICAL  
**מספר כשלונות:** 5 טסטים

**תיאור:**
השרת מחזיר 500 errors רצופים בקריאות ל-`/configure` endpoint.

**טסטים שנכשלו:**
- `test_config_endpoint_p95_latency` (PZ-14092)
- `test_config_endpoint_p99_latency` (PZ-14091)
- `test_job_creation_time` (PZ-14090)
- `test_fft_window_size_validation` (PZ-14072)
- `test_e2e_configure_metadata_grpc_flow` (PZ-13570)

**שגיאה:**
```
HTTPSConnectionPool(host='10.10.100.100', port=443): 
Max retries exceeded with url: /focus-server/configure 
(Caused by ResponseError('too many 500 error responses'))
```

**השפעה:**
- לא ניתן למדוד latency
- לא ניתן למדוד job creation time
- פוגע ב-E2E flows

**Xray IDs מושפעים:**
- PZ-14090 (Job Creation Time)
- PZ-14091 (P99 Latency)
- PZ-14092 (P95 Latency)
- PZ-14072 (FFT Window Validation)
- PZ-13570 (E2E Configure Flow)

---

### 2. **MongoDB: Connection & Manager Issues** 🔥
**חומרה:** CRITICAL  
**מספר כשלונות:** 11 טסטים

**תיאור:**
MongoDBManager לא מאתחל client נכון, ואין method `get_database()`.

**טסטים שנכשלו:**
- `test_mongodb_connection_using_focus_config`
- `test_mongodb_quick_response_time`
- `test_required_mongodb_collections_exist`
- `test_critical_mongodb_indexes_exist`
- `test_recordings_document_schema_validation`
- `test_recordings_metadata_completeness`
- `test_mongodb_recovery_recordings_indexed_after_outage`
- `test_mongodb_data_quality_general`
- `test_recording_collection_schema_validation`
- `test_metadata_collection_schema_validation`
- `test_historical_vs_live_recordings_classification`

**שגיאות:**
```python
# Error 1:
assert None is not None
  where None = <MongoDBManager>.client

# Error 2:
AttributeError: 'MongoDBManager' object has no attribute 'get_database'

# Error 3:
AttributeError: 'NoneType' object has no attribute 'admin'
```

**השפעה:**
- כל טסטי Data Quality נכשלים
- אי אפשר לאמת indexes, schema, או recovery
- בעיית תשתית קריטית

**Xray IDs מושפעים:**
- PZ-13683 (MongoDB Collections Exist)
- PZ-13684 (Schema Validation)
- PZ-13685 (Metadata Completeness)
- PZ-13598 (Data Quality)
- PZ-13604 (Recovery)

**פתרון נדרש:**
תיקון `MongoDBManager` - צריך לוודא:
1. שהclient מאותחל נכון
2. שיש method `get_database()`
3. שהconnection string תקין

---

### 3. **Kubernetes/SSH Connectivity - SSL Certificate Issues** 🔥
**חומרה:** HIGH  
**מספר כשלונות:** 2 טסטים

**תיאור:**
לא ניתן להתחבר ל-Kubernetes API או SSH בגלל בעיות SSL.

**טסטים שנכשלו:**
- `test_kubernetes_connection` (PZ-13773)
- `test_ssh_connection` (PZ-13774)

**שגיאות:**
```
# Kubernetes:
HTTPSConnectionPool(host='10.10.10.151', port=6443): 
Max retries exceeded with url: /version/ 
(Caused by SSLError(SSLCertVerificationError(1, 
'[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: 
self-signed certificate in certificate chain (_ssl.c:1032)')))

# SSH:
Failed to connect via SSH
```

**השפעה:**
- לא ניתן לבצע chaos testing (MongoDB outage)
- לא ניתן לנהל resources ב-K8s

**פתרון נדרש:**
1. הוסף support ל-self-signed certificates
2. תקן SSH configuration

---

## 🟡 באגים ידועים שכבר תועדו (KNOWN BUGS)

### 4. **Live Metadata: Missing Required Fields** (PZ-13985)
**חומרה:** HIGH  
**מספר כשלונות:** 1 טסט

**תיאור:**
Response של `/live-metadata` חסר שדות חובה.

**טסט שנכשל:**
- `test_live_monitoring_get_metadata` (PZ-13985)

**שדות חסרים:**
- `num_samples_per_trace`
- `dtype`

**סטטוס:** ✅ **כבר תועד** (PZ-13985 קיים ב-Xray)

---

### 5. **Future Timestamps Accepted** (PZ-13984)
**חומרה:** MEDIUM  
**מספר כשלונות:** 1 טסט

**תיאור:**
השרת מקבל timestamps עתידיים במקום לדחות אותם.

**טסט שנכשל:**
- `test_time_range_validation_future_timestamps` (PZ-14089)

**סטטוס:** ✅ **כבר תועד** (PZ-13984 קיים ב-Xray)

---

## 🟢 באגים חדשים שצריך לפתוח (NEW BUGS)

### 6. **Calculation Mismatch: Frequency Resolution** ⚠️
**חומרה:** MEDIUM  
**מספר כשלונות:** 1 טסט

**תיאור:**
חישוב frequency resolution לא תואם את הציפייה.

**טסט שנכשל:**
- `test_frequency_resolution_calculation` (PZ-14060)

**הבעיה:**
```
Expected (PRR/NFFT): 1.953 Hz
Actual (from response): 15.595 Hz
```

**סיבה אפשרית:**
- Frequency decimation
- PRR שונה מהצפוי
- התנהגות לא מתועדת

**Xray ID:** PZ-14060

---

### 7. **Calculation Mismatch: Frequency Bins Count** ⚠️
**חומרה:** MEDIUM  
**מספר כשלונות:** 1 טסט

**תיאור:**
מספר frequency bins לא תואם את הציפייה.

**טסט שנכשל:**
- `test_frequency_bins_count_calculation` (PZ-14061)

**הבעיה:**
```
Expected (NFFT/2+1): 129
Actual: 16
Difference: 113
```

**סיבה אפשרית:**
- Frequency decimation based on requested range
- התנהגות לא מתועדת

**Xray ID:** PZ-14061

---

### 8. **Calculation Mismatch: lines_dt Calculation** ⚠️
**חומרה:** MEDIUM  
**מספר כשלונות:** 1 טסט

**תיאור:**
חישוב `lines_dt` לא תואם את הציפייה.

**טסט שנכשל:**
- `test_lines_dt_calculation` (PZ-14066)

**הבעיה:**
```
Expected [(NFFT - Overlap) / PRR]: 0.256000 sec
Actual: 0.039062 sec
Ratio: 6.55x
```

**סיבות אפשריות:**
1. Overlap percentage שונה
2. PRR שונה (~6554 Hz במקום 1000 Hz)
3. Time compression/decimation

**Xray ID:** PZ-14066

---

### 9. **Channel Grouping: Unexpected Behavior** ⚠️
**חומרה:** LOW  
**מספר כשלונות:** 2 טסטים

**תיאור:**
השרת מקבץ channels ל-streams בצורה לא צפויה.

**טסטים שנכשלו:**
- `test_multichannel_mapping_calculation` (PZ-14070)
- `test_stream_amount_calculation` (PZ-14071)

**הבעיה:**
```
Channels: 1-8 (8 channels)
Streams: 3
Mapping: {'1': 0, '2': 0, '3': 0, '4': 1, '5': 1, '6': 1, '7': 2, '8': 2}
```

**השפעה:**
- לא ברור איך השרת מחליט על קיבוץ
- אין תיעוד להתנהגות הזאת

**המלצה:**
זה יכול להיות **תכונה** ולא באג. צריך:
1. לתעד את לוגיקת הקיבוץ
2. לבדוק אם זה אופטימיזציה מכוונת

**Xray IDs:** PZ-14070, PZ-14071

---

### 10. **Live Streaming: Too Many Polling Errors** ⚠️
**חומרה:** MEDIUM  
**מספר כשלונות:** 1 טסט

**תיאור:**
polling נכשל מספר פעמים ברצף ב-live streaming.

**טסט שנכשל:**
- `test_live_streaming_stability` (PZ-13881)

**שגיאה:**
```
Failed: Too many polling errors: 3
```

**השפעה:**
- יציבות streaming נמוכה
- חוויית משתמש לקויה

**Xray ID:** PZ-13881

---

### 11. **SingleChannel Polling: API Unknown Error** ⚠️
**חומרה:** MEDIUM  
**מספר כשלונות:** 1 טסט

**תיאור:**
polling נכשל עם "Unknown error" ב-SingleChannel mode.

**טסט שנכשל:**
- `test_singlechannel_polling_stability` (PZ-13877)

**שגיאה:**
```
Failed: Polling failed: API call failed: Unknown error
```

**Xray ID:** PZ-13877

---

## 🟦 לא באגים - בעיות בקוד הטסטים (TEST CODE ISSUES)

### 12. **Test Code Bug: channels.min = 0** ❌
**חומרה:** TEST BUG (לא באג שרת!)  
**מספר כשלונות:** 10 טסטים

**תיאור:**
הטסטים מנסים לשלוח `channels.min = 0`, אבל Pydantic דורש `>= 1`.

**טסטים שנכשלו:**
- `test_historic_playback_short_duration_1_minute` (PZ-14101)
- `test_historic_playback_very_old_timestamps_no_data` (PZ-13862)
- `test_historic_playback_status_208_completion` (PZ-13863)
- `test_historic_playback_data_integrity` (PZ-13866)
- `test_historic_playback_timestamp_ordering` (PZ-13867)
- `test_historic_playback_complete_e2e_flow` (PZ-13871)
- `test_configuration_with_extreme_values` (PZ-13880)

**שגיאה:**
```python
pydantic_core._pydantic_core.ValidationError: 1 validation error for ConfigureRequest
channels.min
  Input should be greater than or equal to 1 [type=greater_than_equal, input_value=0, input_type=int]
```

**פתרון:**
תיקון קוד הטסטים - **לא לפתוח באג**, לתקן את הטסטים!

---

### 13. **Validation Working as Expected: Waterfall + displayTimeAxisDuration** ✅
**חומרה:** NOT A BUG  
**מספר כשלונות:** 2 טסטים

**תיאור:**
Validation עובד נכון - waterfall view לא יכול לקבל `displayTimeAxisDuration`.

**טסטים שנכשלו:**
- `test_valid_view_types` (PZ-13915)
- `test_waterfall_view_handling` (PZ-13238)

**שגיאה:**
```
Value error, displayTimeAxisDuration not applicable for waterfall view
```

**פתרון:**
תיקון קוד הטסטים - הם צריכים לוודא ש-waterfall נבדק **בלי** displayTimeAxisDuration.

---

### 14. **Validation Working as Expected: Reversed Time Range** ✅
**חומרה:** NOT A BUG  
**מספר כשלונות:** 1 טסט

**תיאור:**
Validation עובד נכון - `end_time` חייב להיות > `start_time`.

**טסט שנכשל:**
- `test_time_range_validation_reversed_range` (PZ-13899)

**שגיאה:**
```
Value error, end_time must be > start_time
```

**פתרון:**
זה **טוב**! הvalidation עובד. הטסט צריך לצפות לשגיאה הזאת.

---

## 📋 סיכום באגים לפתיחה

### 🔴 CRITICAL (P1) - לפתוח מיידית:
1. ✅ **Focus Server 500 Errors** - השרת קורס
2. ✅ **MongoDB Connection Issues** - תשתית לא עובדת
3. ✅ **K8s/SSH SSL Certificate Issues** - connectivity נכשל

### 🟡 HIGH (P2) - לפתוח בקרוב:
4. ✅ **Live Streaming Polling Errors** (PZ-13881)
5. ✅ **SingleChannel Polling Fails** (PZ-13877)

### 🟢 MEDIUM (P3) - לבדיקה נוספת:
6. ✅ **Frequency Resolution Mismatch** (PZ-14060)
7. ✅ **Frequency Bins Count Mismatch** (PZ-14061)
8. ✅ **lines_dt Calculation Mismatch** (PZ-14066)
9. ⚠️ **Channel Grouping** (PZ-14070, PZ-14071) - יכול להיות תכונה

### ❌ לא באגים - תיקוני קוד:
- תיקון 10 טסטים עם `channels.min = 0`
- תיקון 2 טסטים של waterfall view
- עדכון טסט reversed time range לצפות לשגיאה

---

## 🎯 המלצות לפעולה:

### מיידי:
1. **תקן קוד הטסטים** - 13 טסטים נכשלים בגלל בעיות בקוד הטסט
2. **פתח באג Critical** - Focus Server 500 errors
3. **תקן MongoDB Manager** - בעיית תשתית קריטית

### קצר טווח:
4. פתח באגים לpolling issues
5. בדוק calculation mismatches - יכול להיות undocumented behavior

### ארוך טווח:
6. תעד את channel grouping logic
7. הוסף support ל-self-signed SSL certificates

---

**סה"כ באגים חדשים לפתוח: 8**  
**סה"כ תיקוני קוד: 13 טסטים**

