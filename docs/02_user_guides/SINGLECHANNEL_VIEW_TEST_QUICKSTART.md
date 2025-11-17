# SingleChannel View Test - Quick Start Guide 🚀

## מהיר ולעניין - הרצת הטסט ב-5 דקות

### 📋 סקירה כללית
טסט אוטומטי מקיף לבדיקת **SingleChannel view** של Focus Server.

**מה הטסט בודק?**
- ✅ `stream_amount = 1` (בדיוק סטרים אחד)
- ✅ מיפוי 1:1 נכון של הערוץ
- ✅ אין ערוצים מיותרים
- ✅ עקביות backend (כפי שהמפתח המליץ)

---

## 🎯 הרצה מהירה

### 1️⃣ הרצת הטסט הראשי
```bash
pytest tests/integration/api/test_singlechannel_view_mapping.py::TestSingleChannelViewHappyPath::test_configure_singlechannel_mapping -v -s
```

### 2️⃣ הרצת כל הטסטים (Happy Path)
```bash
pytest tests/integration/api/test_singlechannel_view_mapping.py::TestSingleChannelViewHappyPath -v
```

### 3️⃣ הרצת כל הטסטים בקובץ
```bash
pytest tests/integration/api/test_singlechannel_view_mapping.py -v
```

---

## 📊 מבנה הטסטים

### Happy Path (4 טסטים)
1. **test_configure_singlechannel_mapping** - הטסט הראשי לערוץ 7
2. **test_configure_singlechannel_channel_1** - גבול תחתון (ערוץ 1)
3. **test_configure_singlechannel_channel_100** - ערוץ גבוה
4. **test_singlechannel_vs_multichannel_comparison** - השוואה לMULTICHANNEL

### Edge Cases (3 טסטים)
1. **test_singlechannel_with_min_not_equal_max_should_fail** - min != max
2. **test_singlechannel_with_zero_channel** - ערוץ 0
3. **test_singlechannel_with_different_frequency_ranges** - טווחי תדרים שונים

### Error Handling (3 טסטים)
1. **test_singlechannel_with_invalid_nfft** - NFFT לא תקין
2. **test_singlechannel_with_invalid_height** - גובה לא תקין
3. **test_singlechannel_with_invalid_frequency_range** - טווח תדרים לא תקין

### Backend Consistency (2 טסטים) ⭐
**כפי שהמפתח המליץ: "check in the BE if it's the same channel process"**
1. **test_same_channel_multiple_requests_consistent_mapping** - עקביות אותו ערוץ
2. **test_different_channels_different_mappings** - עצמאות בין ערוצים

---

## 🎨 דוגמת Request/Response

### Request Payload (ערוץ 7)
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": { "height": 1000 },
  "channels": { "min": 7, "max": 7 },
  "frequencyRange": { "min": 0, "max": 500 },
  "start_time": null,
  "end_time": null,
  "view_type": 1
}
```

### Expected Response
```json
{
  "status": "success",
  "stream_amount": 1,           ← חייב להיות 1
  "channel_to_stream_index": {   ← חייבת להיות רשומה אחת בדיוק
    "7": 0                       ← מיפוי 1:1
  },
  "channel_amount": 1,           ← חייב להיות 1
  "job_id": "...",
  "view_type": 1
}
```

---

## ✅ קריטריוני הצלחה

הטסט עובר כאשר:

```python
# 1. בדיוק סטרים אחד
assert response.stream_amount == 1

# 2. רשומת מיפוי אחת בדיוק
assert len(response.channel_to_stream_index) == 1

# 3. הערוץ המבוקש קיים במיפוי
assert "7" in response.channel_to_stream_index

# 4. מיפוי לסטרים 0
assert response.channel_to_stream_index["7"] == 0

# 5. כמות ערוצים = 1
assert response.channel_amount == 1
```

---

## 🔧 פתרון בעיות נפוצות

### ❌ שגיאה: "Expected stream_amount=1, got 2"
**פתרון**: בדוק שה-view_type נשלח נכון (1 = SINGLECHANNEL)

### ❌ שגיאה: "Channel '7' not in mapping"
**פתרון**: בדוק את לוגיקת בחירת הערוצים ב-backend

### ❌ שגיאה: "Expected stream index 0, got 1"
**פתרון**: ייתכן שה-backend משתמש באינדקס מבוסס-1 במקום 0

---

## 📈 תוצאות מצופות

| מטריקה | ערך מצופה |
|--------|-----------|
| Happy Path Tests | 4/4 עוברים |
| Edge Cases Tests | 3/3 עוברים |
| Error Handling Tests | 3/3 עוברים |
| Backend Consistency | 2/2 עוברים |
| **סה"כ** | **12/12 עוברים** |
| זמן ריצה | < 30 שניות |

---

## 📝 דוגמת פלט מוצלח

```
tests/integration/api/test_singlechannel_view_mapping.py::TestSingleChannelViewHappyPath::test_configure_singlechannel_mapping 
================================================================================
TEST: SingleChannel View Mapping - Channel 7
================================================================================
Step 1: Creating ConfigureRequest with view_type=SINGLECHANNEL
✅ ConfigureRequest validated
Step 2: Sending POST /configure
Step 3: Validating response structure
✅ Response status: success
Step 4: Validating stream_amount
✅ stream_amount = 1
Step 5: Validating channel_to_stream_index
✅ channel_to_stream_index has 1 entry
Step 6: Validating 1:1 channel mapping
✅ Channel mapping verified: {'7': 0}
Additional validation: Checking channel_amount
✅ channel_amount = 1
================================================================================
RESPONSE SUMMARY:
================================================================================
Job ID: test_job_20251012143045_a1b2c3d4
Status: success
View Type: 1
Stream Amount: 1
Channel Amount: 1
Channel Mapping: {'7': 0}
================================================================================
✅ TEST PASSED: SingleChannel mapping validated successfully
PASSED
```

---

## 🐛 יצירת Bug Ticket

אם הטסט נכשל, צור ticket לפי התבנית הזו:

```markdown
### [FOCUS-XXX] SingleChannel view - stream_amount != 1

**Environment**: Staging

**Test**: test_configure_singlechannel_mapping

**Expected**: stream_amount = 1
**Actual**: stream_amount = 2

**Payload**:
```json
{
  "channels": { "min": 7, "max": 7 },
  "view_type": 1
}
```

**Impact**: Medium - API contract violation

**Automated Test**: 
`tests/integration/api/test_singlechannel_view_mapping.py::test_configure_singlechannel_mapping`
```

---

## 📚 תיעוד נוסף

- 📖 [מדריך מלא](docs/SINGLECHANNEL_VIEW_TEST_GUIDE.md) - תיעוד מפורט
- 🔗 [Focus Server API](docs/API_HEALING_GUIDE.md)
- 🎯 [דרישות טכניות](docs/TECHNICAL_SPECIFICATIONS_CLARIFICATIONS.md)

---

## 👨‍💻 פקודות מתקדמות

### הרצה עם לוגים מלאים
```bash
pytest tests/integration/api/test_singlechannel_view_mapping.py -v -s --log-cli-level=DEBUG
```

### הרצה עם Allure reporting
```bash
pytest tests/integration/api/test_singlechannel_view_mapping.py --alluredir=reports/allure-results
allure serve reports/allure-results
```

### הרצה עם coverage
```bash
pytest tests/integration/api/test_singlechannel_view_mapping.py --cov=src.apis.focus_server_api --cov-report=html
```

### הרצה במקביל (parallel)
```bash
pytest tests/integration/api/test_singlechannel_view_mapping.py -n auto
```

### הרצה רק של טסטי consistency (המלצת המפתח)
```bash
pytest tests/integration/api/test_singlechannel_view_mapping.py::TestSingleChannelBackendConsistency -v -s
```

---

## 🎓 הסבר קצר למפתחים

### למה זה חשוב?
SingleChannel view חייב להחזיר **בדיוק סטרים אחד** עם מיפוי 1:1 נכון. 
זה קריטי להבטחת התנהגות עקבית ב-UI וב-backend.

### מה המפתח צריך לבדוק?
> **"check in the BE if it's the same channel process"**

הטסטים `TestSingleChannelBackendConsistency` בודקים בדיוק את זה:
- אותו ערוץ במספר בקשות = אותו process
- ערוצים שונים = processes עצמאיים
- מיפוי עקבי לאורך זמן

---

## ✨ סיכום

**זמן התקנה**: 0 דקות (הכל מוכן!)  
**זמן הרצה**: < 30 שניות  
**כיסוי**: 12 טסטים מקיפים  
**איכות**: Production-grade, documented, maintainable  

**הרצה עכשיו**:
```bash
pytest tests/integration/api/test_singlechannel_view_mapping.py -v
```

---

**נוצר על ידי**: QA Automation Architect  
**תאריך**: 2025-10-12  
**גרסה**: 1.0  
**סטטוס**: ✅ מוכן לשימוש

