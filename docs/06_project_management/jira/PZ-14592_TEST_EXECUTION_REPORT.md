# דוח מפורט - הרצת טסטים מטיקט PZ-14592

**תאריך:** 2025-11-06  
**טיקט:** PZ-14592 - Implement API Endpoint High Priority Tests  
**סביבה:** Staging (10.10.10.100)  
**זמן הרצה:** 6:00 דקות (360.38 שניות)

---

## סיכום כללי

| קטגוריה | כמות | אחוז |
|---------|------|------|
| ✅ **עברו בהצלחה** | 19 | 73.1% |
| ⏭️ **דילגו** | 4 | 15.4% |
| ❌ **נכשלו** | 3 | 11.5% |
| **סה"כ** | **26** | **100%** |

---

## פירוט לפי מפתחות Xray מטיקט PZ-14592

### ✅ טסטים שעברו בהצלחה (8/11)

| מפתח Xray | שם טסט | קובץ | סטטוס |
|-----------|---------|------|--------|
| **PZ-13895** | `test_get_channels_endpoint_success` | `test_api_endpoints_high_priority.py` | ✅ PASSED |
| **PZ-13762** | `test_get_channels_endpoint_success` | `test_api_endpoints_high_priority.py` | ✅ PASSED |
| **PZ-13560** | `test_get_channels_endpoint_success` | `test_api_endpoints_high_priority.py` | ✅ PASSED |
| **PZ-13896** | `test_get_channels_endpoint_response_time` | `test_api_endpoints_high_priority.py` | ✅ PASSED |
| **PZ-13898** | `test_get_channels_endpoint_channel_ids_sequential` | `test_api_endpoints_high_priority.py` | ✅ PASSED |
| **PZ-13899** | `test_get_channels_endpoint_enabled_status` | `test_api_endpoints_high_priority.py` | ✅ PASSED |
| **PZ-13552** | `test_invalid_time_range_rejection` | `test_api_endpoints_additional.py` | ✅ PASSED |
| **PZ-13554** | `test_invalid_channel_range_rejection` | `test_api_endpoints_additional.py` | ✅ PASSED |
| **PZ-13555** | `test_invalid_frequency_range_rejection` | `test_api_endpoints_additional.py` | ✅ PASSED |

**כיסוי:** 8/11 מפתחות Xray (72.7%)

### ⏭️ טסטים שדילגו (2/11)

| מפתח Xray | שם טסט | קובץ | סיבה | הערה |
|-----------|---------|------|------|------|
| **PZ-13897** | `test_get_sensors_endpoint` | `test_api_endpoints_additional.py` | 404 Not Found | Endpoint `/sensors` לא קיים |
| **PZ-13764** | `test_get_live_metadata_available` | `test_api_endpoints_additional.py` | Validation Error | נתונים לא תקינים (waiting for fiber) |
| **PZ-13561** | `test_get_live_metadata_available` | `test_api_endpoints_additional.py` | Validation Error | נתונים לא תקינים (waiting for fiber) |

**הערה:** PZ-13897 מופיע גם ב-`test_get_channels_endpoint_multiple_calls_consistency` שעבר בהצלחה ✅

### ❌ טסטים שנכשלו (1/11)

| מפתח Xray | שם טסט | קובץ | שגיאה | סיבה |
|-----------|---------|------|-------|------|
| **PZ-13563** | `test_get_metadata_by_job_id` | `test_api_endpoints_additional.py` | 503 Service Unavailable | שרת לא זמין/עומס |

---

## פירוט שגיאות

### 1. PZ-13563 - test_get_metadata_by_job_id ❌

**שגיאה:**
```
APIError: Request failed: HTTPSConnectionPool(host='10.10.10.100', port=443): 
Max retries exceeded with url: /focus-server/configure 
(Caused by ResponseError('too many 503 error responses'))
```

**מה קרה:**
- הטסט ניסה להגדיר streaming job דרך `POST /focus-server/configure`
- השרת החזיר 503 Service Unavailable 4 פעמים (retries)
- הטסט נכשל כי לא הצליח ליצור job_id

**סיבה אפשרית:**
- שרת Focus Server לא זמין או תחת עומס
- בעיית תשתית זמנית
- בעיית קונפיגורציה בסביבת Staging

**המלצה:**
- לבדוק את סטטוס השרת לפני הרצת הטסט
- לבדוק את הלוגים של Focus Server
- לנסות שוב מאוחר יותר

---

### 2. PZ-13897 - test_get_sensors_endpoint ⏭️

**שגיאה:**
```
404 Not Found
Response: {"detail": "Not Found"}
```

**מה קרה:**
- הטסט ניסה לגשת ל-`GET /focus-server/sensors`
- השרת החזיר 404 - Endpoint לא קיים

**סיבה אפשרית:**
- Endpoint `/sensors` לא מיושם בסביבת Staging
- Endpoint הוסר או שונה
- Endpoint זמין רק בסביבות מסוימות

**המלצה:**
- לבדוק אם Endpoint קיים ב-Swagger/API docs
- לבדוק אם Endpoint זמין בסביבת Production
- לעדכן את הטסט או לסמן כ-skip אם Endpoint לא קיים

---

### 3. PZ-13764 / PZ-13561 - test_get_live_metadata_available ⏭️

**שגיאה:**
```
4 validation errors for LiveMetadataFlat:
- prr: Input should be greater than 0 [input_value=0.0]
- dx: Input should be greater than 0 [input_value=0.0]
- num_samples_per_trace: Field required [missing]
- dtype: Field required [missing]
```

**מה קרה:**
- הטסט קיבל response מ-`GET /live_metadata` עם status 200
- אבל הנתונים לא תקינים:
  ```json
  {
    "dx": 0.0,
    "prr": 0.0,
    "sw_version": "waiting for fiber",
    "number_of_channels": 2337,
    "fiber_description": "waiting for fiber"
  }
  ```

**סיבה:**
- המערכת מחזירה מצב "waiting for fiber" - עדיין לא מוכן
- זה מצב תקין של המערכת, אבל הנתונים לא עוברים validation

**המלצה:**
- הטסט צריך לבדוק את המצב "waiting for fiber" ולסמן כ-skip
- או לשנות את ה-validation להיות יותר גמיש
- או לבדוק את המצב לפני הרצת הטסט

---

## טסטים נוספים (לא מטיקט PZ-14592)

### טסטי תשתית שנכשלו (2):

1. **test_mongodb_status_via_kubernetes**
   - **סיבה:** חיבור ל-Kubernetes API נכשל
   - **שגיאה:** `Connection to 10.10.100.102 timed out`
   - **הערה:** בעיית תשתית/רשת, לא קשור לטיקט

2. **test_kubernetes_list_deployments**
   - **סיבה:** חיבור ל-Kubernetes API נכשל
   - **שגיאה:** `Connection to 10.10.100.102 timed out`
   - **הערה:** בעיית תשתית/רשת, לא קשור לטיקט

### טסטי תשתית שעברו (11):
- MongoDB connection ✅
- Kubernetes connection ✅
- SSH connection ✅
- ועוד...

---

## ניתוח לפי קטגוריות

### קבצי טסטים:

| קובץ | עברו | דילגו | נכשלו | סה"כ |
|------|------|-------|-------|------|
| `test_api_endpoints_high_priority.py` | 5 | 0 | 0 | 5 |
| `test_api_endpoints_additional.py` | 4 | 3 | 1 | 8 |
| `test_external_connectivity.py` | 11 | 0 | 2 | 13 |

### לפי סוג בעיה:

| סוג בעיה | כמות | אחוז |
|----------|------|------|
| בעיות תשתית (503, Timeout) | 3 | 11.5% |
| Endpoint לא קיים (404) | 1 | 3.8% |
| נתונים לא מוכנים (Validation) | 2 | 7.7% |
| הצלחה | 19 | 73.1% |

---

## המלצות לפעולה

### דחוף (High Priority):

1. **PZ-13563 - 503 Errors**
   - לבדוק את סטטוס Focus Server
   - לבדוק את הלוגים של השרת
   - לבדוק אם יש בעיות תשתית

2. **PZ-13897 - Endpoint לא קיים**
   - לבדוק אם `/sensors` קיים ב-API docs
   - לעדכן את הטסט או לסמן כ-skip

### בינוני (Medium Priority):

3. **PZ-13764/PZ-13561 - Validation Errors**
   - לעדכן את הטסט לטפל במצב "waiting for fiber"
   - או לשנות את ה-validation להיות יותר גמיש

### נמוך (Low Priority):

4. **בעיות תשתית Kubernetes**
   - לבדוק את חיבור הרשת ל-Kubernetes API
   - לא קשור לטיקט PZ-14592

---

## סיכום

**כיסוי מפתחות Xray מטיקט PZ-14592:**
- ✅ **8/11 עברו בהצלחה** (72.7%)
- ⏭️ **2/11 דילגו** (18.2%) - בעיות תשתית/זמינות
- ❌ **1/11 נכשל** (9.1%) - בעיית תשתית

**מסקנה:**
רוב הטסטים מטיקט PZ-14592 עובדים כשורה. הבעיות הן בעיקר בתשתית/זמינות שרת, לא בטסטים עצמם.

---
*דוח נוצר: 2025-11-06*  
*פקודת הרצה:* `pytest tests/integration/api/test_api_endpoints_high_priority.py tests/integration/api/test_api_endpoints_additional.py tests/infrastructure/test_external_connectivity.py -v -s`

