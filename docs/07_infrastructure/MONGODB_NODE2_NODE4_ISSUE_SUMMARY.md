# 🚨 סיכום בעיה: node2 ו-node4 ב-MongoDB

**תאריך גילוי:** 21 אוקטובר 2025  
**חומרה:** 🔴 קריטי  
**השפעה:** 6+ טסטים ב-Jira

---

## 🎯 מה הבעיה?

### ב-Jira כתוב (לא נכון):
```
MongoDB Collections: base_paths, node2, node4
```

### במציאות (נכון):
```
MongoDB Collections: 
  - base_paths (קבוע)
  - {GUID} (דינמי, דוגמה: "77e49b5d-e06a-4aae-a33e-17117418151c")
  - {GUID}-unrecognized_recordings (דינמי)
```

---

## 📍 איפה מצאנו את זה?

### 1. בקובץ CSV של Jira (שורה 8393):
```
docs/xray_tests_21_10_25.csv:
"Objective: Verify that base_paths, node2, and node4 collections exist"
```

### 2. בקוד שלנו (שורה 228):
```python
tests/integration/infrastructure/test_mongodb_data_quality.py:
"""
NOTE: Recording collections are named dynamically by GUID 
(e.g., "77e49b5d-e06a-4aae-a33e-17117418151c"), not hardcoded
like "node4". The GUID is stored in base_paths collection.
"""
```

---

## 🔍 איך הקוד שלנו עובד (נכון)?

```python
def _get_recording_collection_name(self):
    """גילוי דינמי של שם אוסף ההקלטות"""
    base_paths = self._get_collection("base_paths")
    base_path_doc = base_paths.find_one()
    guid = base_path_doc.get("guid")  # ← זה שם האוסף!
    return guid
```

**✅ הקוד מגלה את שם האוסף באופן דינמי - זה נכון!**

---

## 📋 טסטים ב-Jira שצריכים עדכון

| Jira ID | שם | מה לתקן |
|---------|-----|---------|
| PZ-13598 | MongoDB Collections Exist | החלף node2, node4 ← GUID דינמי |
| PZ-13684 | node4 Schema Validation | שנה node4 ← recording collection |
| PZ-13685 | Recordings Metadata | עדכן התייחסויות |
| PZ-13686 | MongoDB Indexes | עדכן התייחסויות |
| PZ-13687 | MongoDB Recovery | עדכן התייחסויות |
| PZ-13705 | Historical vs Live | עדכן התייחסויות |

---

## 📖 למידה

**מה למדנו:**
1. ✅ תמיד לבדוק את הקוד האמיתי, לא רק תיעוד
2. ✅ MongoDB collections יכולים להיות דינמיים
3. ✅ GUID-based naming הוא שיטה נפוצה במערכות distributed
4. ⚠️ תיעוד ישן יכול להטעות - תמיד לאמת

---

## 🔗 קישורים

- **הבהרה מפורטת:** `MONGODB_COLLECTIONS_CLARIFICATION.md` (מסמך מלא 200+ שורות)
- **עדכון בדוח:** `דוח_השוואה_JIRA_מול_אוטומציה.md` (שורות 76-86, 64-69)
- **עדכון בטסטים החסרים:** `TESTS_IN_CODE_MISSING_IN_XRAY.md` (שורות 10-18)
- **הקוד הנכון:** `tests/integration/infrastructure/test_mongodb_data_quality.py`

---

**🎯 Bottom Line:**  
אין node2 או node4 במערכת! יש GUID דינמי. הקוד שלנו נכון, Jira צריך תיקון.

