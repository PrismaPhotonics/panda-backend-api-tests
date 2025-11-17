# סיכום בדיקה T-DATA-002 ל-Xray

**תאריך:** 15 אוקטובר 2025  
**מחבר:** רועי אברהמי  
**סטטוס:** ✅ מוכן לייבוא ל-Xray

---

## 📋 פרטי הבדיקה

**מזהה:** T-DATA-002 (או NEW-006)  
**שם:** Data Lifecycle – Historical vs Live Recordings Classification  
**סוג:** Integration Test  
**עדיפות:** High  
**סטטוס ביצוע:** ✅ PASSED

---

## 🎯 מטרת הבדיקה

הבדיקה מאמתת שהמערכת מבחינה נכון בין:
1. **רשומות היסטוריות** (Historical) - הקלטות שהסתיימו
2. **רשומות חיות** (Live) - הקלטות שעדיין רצות
3. **רשומות שנמחקו** (Deleted) - הקלטות שסומנו למחיקה

---

## 🏗️ הבנה ארכיטקטונית

### תפקיד MongoDB במערכת Focus/Panda

MongoDB משמש כ**אינדקס מטא-נתונים** להקלטות:
- **לא מאחסן** את הנתונים הגולמיים (PRP2/SEGY)
- **משמש** את Focus Server ו-Baby Analyzer
- **מטרה:** למצוא קבצים גולמיים ב-S3/אחסון מקומי לטווחי זמן ספציפיים
- **API:** `POST /recordings_in_time_range` דורש `start_time` ו-`end_time`

### סוגי הקלטות

| סוג | מאפיינים | סטטוס |
|-----|-----------|--------|
| **Historical** | יש `start_time` + `end_time`, `deleted=False` | תקין ✅ |
| **Live** | יש `start_time`, אין `end_time`, `deleted=False` | תקין ✅ |
| **Deleted** | `deleted=True` | ניקוי ⚠️ |
| **Stale** | ישן (>24 שעות), אין `end_time`, `deleted=False` | באג ❌ |

---

## 📊 תוצאות הבדיקה

### סיווג הקלטות (Staging)
```
📊 סיווג הקלטות ב-MongoDB:

├── Historical (היסטוריות): 3,414 (99.3%) ✅
│   └── הקלטות שהסתיימו בהצלחה
│
├── Live (חיות): 1 (0.03%) ✅
│   └── הקלטה פעילה (< 24 שעות)
│
└── Deleted (נמחקו): 24 (0.7%) ⚠️
    └── נמחקו ע"י שירות הניקוי
    └── חסרות end_time (נמחקו תוך כדי הקלטה)
```

### דוגמאות לרשומות היסטוריות

| UUID | משך | סטטוס |
|------|-----|--------|
| 38e432b0-7c87-468c-9b85-fd48462d8901 | 1.97 שעות | ✅ תקין |
| 2b58e51e-50fd-4ad8-a623-46f5d48c9e8b | 0.01 שעות | ✅ תקין |
| 55c582e8-1de4-4a03-b7e2-bd803e03264f | 0.02 שעות | ✅ תקין |

### ניתוח הקלטות שנמחקו

- **עם end_time:** 0 (0%)
- **בלי end_time:** 24 (100%)
- **גיל:** 84 ימים (כולן מ-23.7.2025)
- **דפוס:** ניקוי מרוכז או מדיניות שמירה

---

## ✅ Assertions (תנאי הצלחה)

### קריטיים (הבדיקה נכשלת אם לא מתקיימים)

1. **אין רשומות לא תקינות:**
   ```python
   assert invalid_count == 0  # כל הרשומות חייבות להכיל start_time
   ```

2. **שלמות הסיווג:**
   ```python
   assert (historical + live + deleted) == total
   ```

3. **רוב היסטורי:**
   ```python
   assert (historical / total) > 0.50  # מעל 50% חייבות להיות היסטוריות
   ```

### אזהרות (הבדיקה מצליחה אך מתריעה)

4. **זיהוי הקלטות תקועות:**
   ```python
   if stale_count > 0:
       warning("נמצאו הקלטות תקועות")
   ```

5. **הקלטות שנמחקו ללא end_time:**
   ```python
   if deleted_without_endtime > 0:
       warning("24 הקלטות שנמחקו חסרות end_time")
   ```

---

## 🐛 ממצאים

### ⚠️ בעיה: 24 הקלטות שנמחקו חסרות `end_time`

**התנהגות נוכחית:**
```python
def delete_recording(uuid):
    db.recordings.update_one(
        {"uuid": uuid},
        {"$set": {"deleted": True}}
    )
    # ❌ לא מגדיר end_time!
```

**תיקון מומלץ:**
```python
def delete_recording(uuid):
    """מחיקת הקלטה, כולל הגדרת end_time."""
    db.recordings.update_one(
        {"uuid": uuid},
        {
            "$set": {
                "deleted": True,
                "end_time": end_time or datetime.utcnow(),  # ✅
                "deleted_at": datetime.utcnow(),
                "deletion_reason": "manual"  # או "retention", "cleanup"
            }
        }
    )
```

---

## 💡 המלצות

### 🔴 עדיפות גבוהה: תיקון לוגיקת המחיקה

**בעיה:** הקלטות שנמחקו חסרות `end_time`  
**השפעה:** לא ניתן לחשב משך הקלטה, דוחות לא שלמים  
**פתרון:** לעדכן את פונקציית המחיקה להגדיר `end_time`

### 🟡 עדיפות בינונית: הוספת שדה `status` מפורש

**רציונל:** במקום היוריסטיקות מבוססות זמן, להשתמש בשדה סטטוס ברור:

```python
class RecordingStatus:
    RUNNING = "running"      # הקלטה פעילה
    COMPLETED = "completed"  # הסתיימה בהצלחה
    FAILED = "failed"        # קרסה/כשלה
    DELETED = "deleted"      # נמחקה

# סכימה מומלצת:
{
    "uuid": "abc-123",
    "start_time": datetime,
    "end_time": datetime or None,
    "deleted": bool,
    "status": RecordingStatus.RUNNING  # ← שדה חדש
}
```

**יתרונות:**
- ✅ אין צורך בהיוריסטיקות מבוססות זמן
- ✅ מכונת מצבים ברורה
- ✅ שאילתות פשוטות: `find({status: "running"})`
- ✅ מעקב ואתראות טובות יותר

---

## ❓ שאלות לצוות הפיתוח

### 1. זיהוי שירות הניקוי
**איזה שירות אחראי על הגדרת `deleted=True`?**
- [ ] שירות Sweeper
- [ ] שירות Data Manager
- [ ] שירות Lifeboat
- [ ] קריאות API ידניות
- [ ] אחר: _______________

### 2. טריגר למחיקה
**מה מפעיל את המחיקה/ניקוי ההקלטות?**
- [ ] מדיניות שמירה (מחיקה אוטומטית אחרי X ימים)
- [ ] מחיקה ידנית על ידי משתמש
- [ ] הגעה למכסת אחסון
- [ ] השלמת job של `clean_status_list`
- [ ] אחר: _______________

### 3. התנהגות צפויה
**האם צפוי שלהקלטות שנמחקו יהיה `end_time`?**
- [ ] כן - להגדיר לזמן המחיקה
- [ ] כן - להגדיר לזמן אחרון ידוע
- [ ] לא - להשאיר null
- [ ] תלוי: _______________

### 4. שדה Status
**האם יש תוכנית להוסיף שדה `status` מפורש?**
- [ ] כן - בתהליך
- [ ] אולי - בשיקול
- [ ] לא - לא מתוכנן

---

## 📁 קבצים שנוצרו

### תיעוד Xray
1. **XRAY_T_DATA_002_HISTORICAL_VS_LIVE.md** - מפרט מלא ל-Xray (30 צעדים)
2. **JIRA_XRAY_NEW_TESTS.md** - עודכן עם T-DATA-002

### דוחות ותיעוד טכני
3. **T_DATA_002_HISTORICAL_VS_LIVE_REPORT.md** - דוח ביצוע מלא באנגלית
4. **LIVE_VS_HISTORICAL_RECORDINGS.md** - הסבר טכני מעמיק (313 שורות)
5. **T_DATA_002_XRAY_SUMMARY_HEBREW.md** - סיכום בעברית (קובץ זה)

### קוד
6. **tests/integration/infrastructure/test_mongodb_data_quality.py** - הבדיקה (שורות 960-1165)
7. **pytest.ini** - עודכן עם marker `data_lifecycle`

---

## 🚀 הרצת הבדיקה

```bash
# הרצת T-DATA-002 בלבד
pytest tests/integration/infrastructure/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_historical_vs_live_recordings -v

# הרצת כל בדיקות Data Lifecycle
pytest -m data_lifecycle -v

# הרצת כל בדיקות MongoDB Data Quality
pytest tests/integration/infrastructure/test_mongodb_data_quality.py -v
```

---

## 📊 סטטיסטיקות

- **משך הבדיקה:** ~10 שניות
- **שאילתות DB:** 15 שאילתות
- **רשומות שנסרקו:** 3,439 הקלטות
- **שימוש בזיכרון:** נמוך (streaming queries)

---

## 🎯 ייבוא ל-Xray

### שלב 1: פתיחת Jira
1. עבור ל-Jira → Project PZ → Test Repository
2. לחץ על "Create Test"

### שלב 2: העתקת פרטים
העתק מתוך `XRAY_T_DATA_002_HISTORICAL_VS_LIVE.md`:
- **Summary:** Data Lifecycle – Historical vs Live Recordings Classification
- **Test Type:** Integration Test
- **Priority:** High
- **Components:** `focus-server`, `mongodb`, `data-lifecycle`, `data-quality`
- **Steps:** 27 צעדים (מפורטים בקובץ)

### שלב 3: קישור Requirements
קשר ל:
- **PZ-13598** (Data Quality – Mongo collections)
- **T-DATA-001** (בדיקה קשורה)

### שלב 4: הוספת תוצאות
העתק מתוך החלק "Test Results (Last Run)" את:
- תאריך: 2025-10-15
- סטטוס: PASSED ✅
- תוצאות מפורטות

---

## ✅ Checklist לייבוא

- [x] מזהה בדיקה הוקצה (T-DATA-002)
- [x] תיאור מפורט נכתב
- [x] עדיפות הוגדרה (High)
- [x] רכיבים/Labels נוספו
- [x] Requirements קושרו (PZ-13598)
- [x] צעדים תועדו (27 צעדים)
- [x] תוצאות צפויות הוגדרו
- [x] Assertions רשומים
- [x] סטטוס אוטומציה אושר (Automated ✅)
- [x] הבדיקה הורצה ותוצאות תועדו (PASSED ✅)
- [x] Issues קשורים קושרו
- [x] המלצות ניתנו

---

## 📞 איש קשר

**מחבר הבדיקה:** רועי אברהמי  
**תפקיד:** QA Automation Architect  
**סטטוס בדיקה:** ✅ מוכן לייבוא  
**תאריך:** 15 אוקטובר 2025

---

## 🎉 סיכום

בדיקה T-DATA-002 היא בדיקה קריטית שמאמתת:
1. ✅ סיווג נכון של הקלטות (Historical/Live/Deleted)
2. ✅ שלמות נתונים ב-MongoDB
3. ✅ זיהוי הקלטות תקועות (Stale)
4. ✅ ניתוח שירות הניקוי

**הבדיקה מצאה:**
- ✅ כל הרשומות תקינות
- ✅ אין הקלטות תקועות
- ⚠️ 24 הקלטות שנמחקו חסרות `end_time`

**המלצה:** לתקן את לוגיקת המחיקה ולהוסיף שדה `status` מפורש.

---

**✅ מוכן לייבוא ל-Jira Xray!**

