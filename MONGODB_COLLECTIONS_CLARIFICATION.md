# 🔍 MongoDB Collections - הבהרה חשובה: node2 ו-node4

**תאריך:** 21 אוקטובר 2025  
**נושא:** אי-התאמה בין תיעוד Jira לבין המימוש בפועל  
**חשיבות:** 🔴 **קריטי** - משפיע על כל הטסטים הקשורים ל-MongoDB

---

## 🎯 תקציר מנהלים

**בעיה שהתגלתה:**
- הטסטים ב-Jira (כולל PZ-13598, PZ-13684, וכו') מתייחסים לאוספים (collections) בשמות **קבועים**: `node2` ו-`node4`
- המימוש האמיתי במערכת משתמש באוספים בשמות **דינמיים** (GUID)
- הקוד האוטומציה שכתבנו **נכון** ומשקף את המציאות, אבל התיעוד ב-Jira **לא מעודכן**

**פעולה נדרשת:**
- ✅ הקוד תקין - אין צורך לשנות
- ❌ התיעוד ב-Jira דורש עדכון להתאים למציאות

---

## 📊 השוואה: Jira vs. מציאות

### ❌ **מה שכתוב ב-Jira (לא נכון):**

**טסט PZ-13598 - "MongoDB Collections Exist":**
```
Required collections: base_paths, node2, node4
```

**צעדי הטסט ב-Jira:**
1. Connect to MongoDB ✅
2. List all collections ✅
3. Verify `base_paths` collection exists ✅
4. Verify `node2` collection exists ❌ **שם לא קיים במציאות!**
5. Verify `node4` collection exists ❌ **שם לא קיים במציאות!**

---

### ✅ **מה שקורה במציאות (נכון):**

**במערכת האמיתית:**
```python
# MongoDB Collections Structure:
1. base_paths                              # ✅ אוסף קבוע
2. {GUID}                                  # 🔄 אוסף דינמי - שם משתנה!
   דוגמה: "77e49b5d-e06a-4aae-a33e-17117418151c"
3. {GUID}-unrecognized_recordings          # 🔄 אוסף דינמי משני
```

**איך זה עובד:**
1. האוסף `base_paths` מכיל מסמך עם השדה `guid`
2. ה-`guid` הזה הוא **שם האוסף** של ההקלטות (recordings)
3. אין שום דבר בשם `node2` או `node4` - אלו כנראה שמות ישנים שלא רלוונטיים יותר

---

## 💻 מה הקוד שלנו עושה (נכון!)

### הקוד ב-`test_mongodb_data_quality.py`:

```python
def _get_recording_collection_name(self):
    """
    Discover the recording collection name dynamically from base_paths.
    
    The recording collection is named by GUID, which is stored in the
    base_paths collection. This method:
    1. Reads base_paths collection
    2. Extracts the GUID
    3. Returns the GUID as the collection name
    
    Returns:
        Recording collection name (GUID)
    """
    # Use cached value if available
    if self._recording_collection_name:
        return self._recording_collection_name
    
    try:
        # Get base_paths collection
        base_paths = self._get_collection(self.BASE_COLLECTION)
        
        # Get first document (should only be one)
        base_path_doc = base_paths.find_one()
        
        if not base_path_doc:
            raise DatabaseError(
                f"Collection '{self.BASE_COLLECTION}' is empty - "
                f"cannot discover recording collection"
            )
        
        # Extract GUID - THIS IS THE COLLECTION NAME!
        guid = base_path_doc.get("guid")
        if not guid:
            raise DatabaseError(
                f"Document in '{self.BASE_COLLECTION}' has no 'guid' field"
            )
        
        # Cache for future use
        self._recording_collection_name = guid
        
        return guid
        
    except Exception as e:
        raise DatabaseError(
            f"Failed to discover recording collection name: {e}"
        ) from e
```

### ההערה בקוד (שורות 226-228):

```python
NOTE: Recording collections are named dynamically by GUID 
(e.g., "77e49b5d-e06a-4aae-a33e-17117418151c"), not hardcoded
like "node4". The GUID is stored in base_paths collection.
```

**✅ הקוד שלנו נכון! הוא מגלה את שם האוסף באופן דינמי.**

---

## 🔴 איזה טסטים ב-Jira מושפעים?

### טסטים שצריכים עדכון:

| Jira ID | שם הטסט | מה צריך לתקן |
|---------|---------|-------------|
| **PZ-13598** | MongoDB Collections Exist | להחליף `node2, node4` ב-`{GUID} (discovered dynamically)` |
| **PZ-13684** | node4 Schema Validation | לשנות את כל ההתייחסויות מ-`node4` ל-`recordings collection (GUID-based)` |
| **PZ-13685** | Recordings Metadata Completeness | לעדכן התייחסויות ל-`node4` |
| **PZ-13686** | MongoDB Indexes Validation | לעדכן התייחסויות ל-`node4` |
| **PZ-13687** | MongoDB Recovery | לעדכן התייחסויות ל-`node4` |
| **PZ-13705** | Historical vs Live | לעדכן התייחסויות ל-`node4` |

---

## 📝 עדכונים נדרשים ב-Jira

### PZ-13598 - עדכון מומלץ:

**Before (לא נכון):**
```
Test Data:
Database: prisma (staging) or focus_db (local).
Required collections: base_paths, node2, node4.

Steps:
3. Verify 'base_paths' collection exists
4. Verify 'node2' collection exists  ❌
5. Verify 'node4' collection exists  ❌
```

**After (נכון):**
```
Test Data:
Database: prisma (staging) or focus_db (local).
Required collections: 
  - base_paths (fixed name)
  - {GUID} (discovered dynamically from base_paths)
  - {GUID}-unrecognized_recordings (optional)

Steps:
3. Verify 'base_paths' collection exists
4. Read 'guid' field from base_paths document
5. Verify collection with name={guid} exists
6. (Optional) Verify '{guid}-unrecognized_recordings' exists
```

---

## 🎓 מידע ארכיטקטוני

### למה זה עובד ככה?

**עיצוב המערכת:**
1. כל קובץ PRP2/SEGY מאוחסן ב-S3 או בדיסק מקומי
2. MongoDB **לא** מאחסן את הנתונים הגולמיים - רק **מטא-דאטה** (אינדקס)
3. ה-GUID מייצג **base path** ספציפי במערכת הקבצים
4. כל base path יכול להיות בעל אוסף הקלטות משלו
5. שם האוסף = GUID של ה-base path (ייחודי למערכת)

**דוגמה מהמציאות:**
```
base_paths collection:
{
  "_id": ObjectId("..."),
  "guid": "77e49b5d-e06a-4aae-a33e-17117418151c",  ← שם האוסף!
  "path": "/mnt/storage/recordings/fiber1",
  "created_at": "2024-01-15T10:00:00Z"
}

Recording collections:
- "77e49b5d-e06a-4aae-a33e-17117418151c"           ← אוסף ההקלטות
- "77e49b5d-e06a-4aae-a33e-17117418151c-unrecognized_recordings"  ← הקלטות לא מזוהות
```

---

## ❓ מאיפה הגיעו השמות node2 ו-node4?

**תיאוריות אפשריות:**

1. **גרסאות ישנות:** אולי בגרסאות קדומות של המערכת השתמשו בשמות קבועים
2. **סביבת פיתוח:** אולי בסביבת dev/test השתמשו בשמות כאלו לפשטות
3. **תיעוד לא מעודכן:** מישהו כתב את הספסיפיקציה לפני שהמערכת השתנתה לGUID
4. **טעות בתיעוד:** מישהו ניחש שמות מבלי לבדוק את הקוד האמיתי

**המסקנה:**
כיום (אוקטובר 2025), במערכת הפרודקשן והסטייג'ינג, **אין** שום דבר בשם `node2` או `node4`.

---

## ✅ מה עשינו נכון?

1. ✅ **חקרנו את הקוד האמיתי** במקום להניח הנחות
2. ✅ **כתבנו טסט שמגלה את שם האוסף באופן דינמי** (כמו שהמערכת עובדת)
3. ✅ **תיעדנו את ההבדל בין Jira למציאות** (המסמך הזה)
4. ✅ **הבנו את הארכיטקטורה** (GUID-based collections)

---

## 📋 פעולות המשך

### מיידי:
- [ ] לעדכן את PZ-13598 ב-Jira עם השמות הנכונים
- [ ] לעדכן את PZ-13684 (Schema Validation) 
- [ ] לעדכן את PZ-13685, PZ-13686, PZ-13687, PZ-13705
- [ ] לברר עם הצוות למה היו שמות `node2`, `node4` במקור

### קצר טווח:
- [ ] לעבור על כל התיעוד ולהחליף התייחסויות ל-node2/node4
- [ ] לוודא שכל הטסטים החדשים משתמשים בגילוי דינמי
- [ ] לעדכן את הדוקומנטציה הפנימית

### ארוך טווח:
- [ ] ליצור תהליך סנכרון בין קוד לתיעוד למנוע בעיות דומות
- [ ] להוסיף בדיקות אוטומטיות שמזהות אי-התאמות

---

## 📚 קבצים רלוונטיים

**קוד:**
- `tests/integration/infrastructure/test_mongodb_data_quality.py` - הטסטים הנכונים שלנו
- `src/infrastructure/mongodb_manager.py` - מנהל החיבור ל-MongoDB

**תיעוד שצריך עדכון:**
- `COMPLETE_XRAY_TEST_DOCUMENTATION_PART3_INFRASTRUCTURE.md` - יש התייחסויות ל-node4
- `documentation/jira/JIRA_XRAY_NEW_TESTS.md` - יש התייחסויות רבות
- כל הקבצים שמופיעים ב-grep למעלה

---

## 🎯 סיכום

| מה | סטטוס | הערות |
|----|-------|-------|
| **הקוד שלנו** | ✅ **נכון** | משתמש בגילוי דינמי של GUID |
| **התיעוד ב-Jira** | ❌ **לא מעודכן** | מתייחס ל-node2, node4 שלא קיימים |
| **ההבנה שלנו** | ✅ **מלאה** | מבינים את הארכיטקטורה |
| **הפעולה הנדרשת** | 🔄 **עדכון תיעוד** | לא לשנות קוד, רק לעדכן Jira |

---

**✨ Bottom Line:**  
הקוד שלנו מתקדם יותר מהתיעוד ב-Jira. במקום לתקן את הקוד כדי להתאים ל-Jira המיושן, 
צריך לעדכן את Jira כדי להתאים למציאות!

---

**נוצר ב:** 2025-10-21  
**עודכן לאחרונה:** 2025-10-21  
**מחבר:** QA Automation Team  
**סטטוס:** ✅ Final - מוכן לשיתוף עם הצוות

