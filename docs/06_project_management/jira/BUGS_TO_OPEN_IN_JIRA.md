# 🐛 רשימת באגים לפתיחה ב-Jira

תאריך: 30.10.2025  
מקור: הרצת אוטומציה (144 טסטים, 37 נכשלו)

---

## 🔴 קריטי (P1) - לטיפול מיידי

### באג #1: Focus Server - Too Many 500 Internal Server Errors
**Priority:** Critical (P1)  
**Component:** Focus Server API  
**Affected Endpoint:** `/configure`

**תיאור:**
השרת מחזיר שגיאות 500 רצופות בקריאות ל-`/configure` endpoint, מה שגורם לכשלון של 5 טסטים ופגיעה ביכולת למדוד performance.

**שגיאה:**
```
HTTPSConnectionPool(host='10.10.100.100', port=443): 
Max retries exceeded with url: /focus-server/configure 
(Caused by ResponseError('too many 500 error responses'))
```

**טסטים מושפעים:**
- PZ-14092: Configuration Endpoint P95 Latency
- PZ-14091: Configuration Endpoint P99 Latency  
- PZ-14090: Job Creation Time < 2 Seconds
- PZ-14072: FFT Window Size Validation
- PZ-13570: E2E Configure → Metadata → gRPC Flow

**השפעה:**
- לא ניתן למדוד latency וperformance
- E2E flows נכשלים
- חוויית משתמש קריטית פגועה

**צעדים לשחזור:**
1. שלח מספר קריאות POST ל-`/configure` ברצף
2. השרת מתחיל להחזיר 500 errors
3. הבעיה מתמשכת גם עם retry logic

**קבצים רלוונטיים:**
- `tests/integration/performance/test_latency_requirements.py`
- `tests/integration/calculations/test_system_calculations.py`

---

### באג #2: MongoDB Manager - Client Initialization Failure
**Priority:** Critical (P1)  
**Component:** Infrastructure - MongoDB  
**Affected Class:** `MongoDBManager`

**תיאור:**
`MongoDBManager` לא מאתחל את ה-`client` נכון (נשאר `None`), ואין לו method `get_database()`, מה שגורם לכשלון של כל 11 טסטי Data Quality.

**שגיאות:**
```python
# שגיאה 1:
assert None is not None
  where None = <MongoDBManager>.client

# שגיאה 2:
AttributeError: 'MongoDBManager' object has no attribute 'get_database'

# שגיאה 3:
AttributeError: 'NoneType' object has no attribute 'admin'
```

**טסטים מושפעים:**
- PZ-13683: MongoDB Collections Exist
- PZ-13684: Schema Validation
- PZ-13685: Metadata Completeness  
- PZ-13598: Data Quality General
- PZ-13604: MongoDB Recovery
- ועוד 6 טסטים נוספים

**השפעה:**
- **אי אפשר לאמת data quality**
- אי אפשר לבדוק indexes ו-schema
- אי אפשר לבדוק recovery scenarios
- תשתית קריטית לא עובדת

**צעדים לשחזור:**
1. נסה ליצור instance של `MongoDBManager`
2. בדוק אם `client` מאותחל
3. נסה לקרוא ל-`get_database()`

**פתרון מוצע:**
1. וודא ש-`__init__()` מאתחל את `self.client`
2. הוסף method `get_database(db_name: str)`
3. בדוק את connection string

**קבצים רלוונטיים:**
- `src/infrastructure/mongodb_manager.py`
- `tests/data_quality/test_mongodb_*.py`

---

### באג #3: Kubernetes/SSH Connectivity - SSL Certificate Verification Failed
**Priority:** High (P2)  
**Component:** Infrastructure - K8s & SSH  

**תיאור:**
לא ניתן להתחבר ל-Kubernetes API Server או SSH בגלל self-signed certificates שלא נתמכים.

**שגיאות:**
```
# Kubernetes:
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: 
self-signed certificate in certificate chain

# SSH:
Failed to connect via SSH
```

**טסטים מושפעים:**
- PZ-13773: Kubernetes Connection Test
- PZ-13774: SSH Connection Test

**השפעה:**
- לא ניתן לבצע chaos testing (MongoDB/RabbitMQ outage)
- לא ניתן לנהל K8s resources מהטסטים
- פוגע ביכולת לבדוק resilience

**פתרון מוצע:**
1. הוסף support ל-`verify=False` או custom CA bundle
2. תקן SSH configuration (keys, host verification)
3. הוסף אפשרות להגדרת trust store

**קבצים רלוונטיים:**
- `src/infrastructure/kubernetes_manager.py`
- `src/infrastructure/ssh_manager.py`
- `tests/infrastructure/test_external_connectivity.py`

---

## 🟡 גבוה (P2) - לטיפול בקרוב

### באג #4: Live Streaming - Too Many Polling Errors
**Priority:** High (P2)  
**Component:** Live Streaming  
**Xray ID:** PZ-13881

**תיאור:**
polling נכשל מספר פעמים ברצף במהלך live streaming, מה שפוגע ביציבות.

**שגיאה:**
```
Failed: Too many polling errors: 3
```

**טסט מושפע:**
- PZ-13881: Live Streaming Stability

**השפעה:**
- יציבות streaming נמוכה
- חוויית משתמש לקויה
- הפרעות בזרימת נתונים

**צעדים לשחזור:**
1. התחל live streaming job
2. בצע polling רציף לdata
3. צפה למספר כשלונות ברצף

**קובץ רלוונטי:**
- `tests/integration/api/test_live_streaming_stability.py`

---

### באג #5: SingleChannel Polling - Unknown API Error
**Priority:** High (P2)  
**Component:** SingleChannel View  
**Xray ID:** PZ-13877

**תיאור:**
polling נכשל עם "Unknown error" כאשר עובדים ב-SingleChannel mode.

**שגיאה:**
```
Failed: Polling failed: API call failed: Unknown error
```

**טסט מושפע:**
- PZ-13877: SingleChannel Polling Stability

**השפעה:**
- SingleChannel view לא יציב
- לא ניתן לקבל data באופן רציף

**צעדים לשחזור:**
1. הגדר configuration ב-SingleChannel mode
2. התחל streaming job
3. בצע polling
4. תתקל ב-"Unknown error"

**קובץ רלוונטי:**
- `tests/integration/api/test_singlechannel_view_mapping.py`

---

## 🟢 בינוני (P3) - לבדיקה ותיעוד

### באג #6: Calculation Mismatch - Frequency Resolution
**Priority:** Medium (P3)  
**Component:** Calculations & Metadata  
**Xray ID:** PZ-14060

**תיאור:**
חישוב frequency resolution לא תואם את הציפייה לפי הנוסחה `PRR/NFFT`.

**ערכים:**
```
Expected (PRR/NFFT): 1.953 Hz
Actual (from response): 15.595 Hz
Ratio: ~8x difference
```

**השערה:**
- ייתכן frequency decimation
- ייתכן PRR שונה מהמוגדר
- ייתכן התנהגות לא מתועדת

**טסט מושפע:**
- PZ-14060: Frequency Resolution Calculation

**פעולה נדרשת:**
1. בדוק האם זה bug או feature לא מתועדת
2. אם feature - תעד את הלוגיקה
3. אם bug - תקן את החישוב

**קובץ רלוונטי:**
- `tests/integration/calculations/test_system_calculations.py`

---

### באג #7: Calculation Mismatch - Frequency Bins Count
**Priority:** Medium (P3)  
**Component:** Calculations & Metadata  
**Xray ID:** PZ-14061

**תיאור:**
מספר frequency bins לא תואם את הציפייה לפי הנוסחה `NFFT/2+1`.

**ערכים:**
```
Expected (NFFT/2+1): 129
Actual: 16
Difference: 113 bins
```

**השערה:**
- ייתכן decimation על בסיס frequency range המבוקש
- ייתכן אופטימיזציה לא מתועדת

**טסט מושפע:**
- PZ-14061: Frequency Bins Count Calculation

**פעולה נדרשת:**
בדיקה והבהרה מול הפיתוח

**קובץ רלוונטי:**
- `tests/integration/calculations/test_system_calculations.py`

---

### באג #8: Calculation Mismatch - lines_dt Value
**Priority:** Medium (P3)  
**Component:** Calculations & Metadata  
**Xray ID:** PZ-14066

**תיאור:**
ערך `lines_dt` לא תואם את הציפייה לפי הנוסחה `(NFFT - Overlap) / PRR`.

**ערכים:**
```
Expected: 0.256000 sec
Actual: 0.039062 sec
Ratio: 6.55x faster
```

**סיבות אפשריות:**
1. Overlap percentage שונה מהצפוי
2. PRR שונה (~6554 Hz במקום 1000 Hz)
3. Time compression/decimation

**טסט מושפע:**
- PZ-14066: Time Resolution (lines_dt) Calculation

**פעולה נדרשת:**
הבהרה של הפרמטרים האמיתיים

**קובץ רלוונטי:**
- `tests/integration/calculations/test_system_calculations.py`

---

### באג #9: Channel Grouping - Undocumented Behavior (?)
**Priority:** Low (P4) - **ייתכן שזו תכונה**  
**Component:** Channel Mapping  
**Xray IDs:** PZ-14070, PZ-14071

**תיאור:**
השרת מקבץ channels ל-streams בצורה לא צפויה.

**דוגמה:**
```
Input: 8 channels (1-8)
Output: 3 streams
Mapping: 
  Stream 0: channels 1,2,3
  Stream 1: channels 4,5,6
  Stream 2: channels 7,8
```

**טסטים מושפעים:**
- PZ-14070: MultiChannel Mapping Calculation
- PZ-14071: Stream Amount Calculation

**פעולה נדרשת:**
**לא בטוח שזה באג!**
1. בדוק אם זו אופטימיזציה מכוונת
2. **אם כן - תעד את הלוגיקה**
3. אם לא - תקן את ההתנהגות

**קובץ רלוונטי:**
- `tests/integration/calculations/test_system_calculations.py`

---

## ❌ לא באגים - תיקוני קוד טסטים

### 🛠️ תיקון נדרש: channels.min = 0
**רכיב:** Test Code  
**כמות טסטים:** 10

**הבעיה:**
הטסטים מנסים לשלוח `channels.min = 0`, אבל Pydantic דורש `>= 1`.

**טסטים לתקן:**
- PZ-14101: Historic Playback Short Duration
- PZ-13862: Historic Playback Old Timestamps
- PZ-13863: Historic Playback Status 208
- PZ-13866: Historic Playback Data Integrity
- PZ-13867: Historic Playback Timestamp Ordering
- PZ-13871: Historic Playback E2E
- PZ-13880: Extreme Configuration Values
- ועוד 3 טסטים

**פתרון:**
שנה את כל המקומות שמגדירים `channels.min = 0` ל-`channels.min = 1`.

**קבצים לתקן:**
- `tests/integration/api/test_historic_playback_*.py`
- `tests/stress/test_extreme_configurations.py`

---

### 🛠️ תיקון נדרש: Waterfall View Tests
**רכיב:** Test Code  
**כמות טסטים:** 2

**הבעיה:**
הטסטים שולחים `displayTimeAxisDuration` עם waterfall view, אבל זה לא תקף.

**טסטים לתקן:**
- PZ-13915: Valid View Types
- PZ-13238: Waterfall View Handling

**פתרון:**
הסר `displayTimeAxisDuration` מתצורות waterfall view, או אל תשלח אותו בכלל.

**קבצים לתקן:**
- `tests/integration/api/test_view_type_validation.py`
- `tests/integration/api/test_waterfall_view.py`

---

### ✅ עובד כצפוי: Reversed Time Range Validation
**רכיב:** Validation  
**טסט:** PZ-13899

**מצב:**
הvalidation **עובד נכון** - השרת דוחה `end_time < start_time`.

**פתרון:**
עדכן את הטסט לצפות לשגיאה זו (assert raises ValidationError).

**קובץ:**
- `tests/integration/api/test_prelaunch_validations.py`

---

## 📊 סיכום סופי

### באגים חדשים לפתוח ב-Jira:
- **Critical (P1):** 3 באגים
- **High (P2):** 2 באגים  
- **Medium (P3):** 4 באגים (מתוכם אחד צריך בדיקה אם זו תכונה)

**סה"כ: 9 באגים חדשים**

### תיקוני קוד טסטים:
- **13 טסטים** דורשים תיקון בקוד הטסט (לא באגי שרת)

---

## 🎯 סדר עדיפויות לפתיחה:

1. **מיידי (היום):**
   - באג #1: Focus Server 500 Errors
   - באג #2: MongoDB Manager Issues

2. **השבוע:**
   - באג #3: K8s/SSH Connectivity
   - באג #4: Live Streaming Polling
   - באג #5: SingleChannel Polling

3. **השבועיים הקרובים:**
   - באגים #6-8: Calculation Mismatches (צריך בדיקה)
   - באג #9: Channel Grouping (אם זה באג)

4. **תיקוני קוד:**
   - תחילה: תקן את 13 הטסטים
   - זה ישפר את תמונת הכשלונות הכוללת

---

**הכן לפתיחה? כל הפרטים כאן! 🚀**

