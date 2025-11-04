# 🚨 דרושים עדכונים דחופים ב-Jira

**תאריך:** 21 אוקטובר 2025  
**נושא:** node2 ו-node4 - שמות לא תקינים של MongoDB collections  
**דחיפות:** 🔴 **גבוהה**  
**מטופל על ידי:** QA Automation Team

---

## 📋 מה צריך לעשות?

### 6 טסטים ב-Jira דורשים עדכון מיידי:

| # | Jira ID | שם הטסט | מה לשנות |
|---|---------|---------|----------|
| 1 | **PZ-13598** | MongoDB Collections Exist | החלף `node2, node4` ← `{GUID} (dynamic)` |
| 2 | **PZ-13684** | node4 Schema Validation | שנה `node4` ← `recording collection (GUID-based)` |
| 3 | **PZ-13685** | Recordings Metadata Completeness | עדכן כל ההתייחסויות ל-`node4` |
| 4 | **PZ-13686** | MongoDB Indexes Validation | עדכן כל ההתייחסויות ל-`node4` |
| 5 | **PZ-13687** | MongoDB Recovery | עדכן כל ההתייחסויות ל-`node4` |
| 6 | **PZ-13705** | Historical vs Live | עדכן כל ההתייחסויות ל-`node4` |

---

## 🎯 הבעיה בקצרה

### ❌ מה כתוב ב-Jira (לא נכון):
```
MongoDB Collections: base_paths, node2, node4
```

### ✅ מה קורה במציאות:
```
MongoDB Collections:
  1. base_paths (שם קבוע)
  2. {GUID} - שם דינמי, מתגלה מתוך base_paths
     דוגמה: "77e49b5d-e06a-4aae-a33e-17117418151c"
  3. {GUID}-unrecognized_recordings (אופציונלי)
```

---

## 📝 דוגמה לעדכון - PZ-13598

### לפני (לא נכון):

```markdown
Test Data:
- Database: prisma
- Required collections: base_paths, node2, node4

Steps:
1. Connect to MongoDB
2. List all collections
3. Verify 'base_paths' exists
4. Verify 'node2' exists  ❌ שם לא קיים!
5. Verify 'node4' exists  ❌ שם לא קיים!
```

### אחרי (נכון):

```markdown
Test Data:
- Database: prisma
- Required collections:
  * base_paths (fixed name)
  * {GUID} (discovered dynamically from base_paths.guid field)

Steps:
1. Connect to MongoDB
2. List all collections
3. Verify 'base_paths' exists
4. Read 'guid' field from base_paths collection
5. Verify collection with name={guid} exists
6. (Optional) Verify '{guid}-unrecognized_recordings' exists
```

---

## 💻 הקוד שלנו (נכון!)

```python
def _get_recording_collection_name(self):
    """
    Discover the recording collection name dynamically.
    Recording collections are named by GUID from base_paths.
    """
    base_paths = self._get_collection("base_paths")
    base_path_doc = base_paths.find_one()
    guid = base_path_doc.get("guid")  # ← זה שם האוסף!
    return guid

# Usage:
collection_name = self._get_recording_collection_name()
# Returns: "77e49b5d-e06a-4aae-a33e-17117418151c" (not "node4"!)
```

---

## 🔍 למה זה חשוב?

1. **דיוק תיעוד:** Jira צריך לשקף את המציאות
2. **הבנת המערכת:** QA team צריך להבין את הארכיטקטורה האמיתית
3. **אוטומציה עתידית:** טסטים חדשים יכתבו נכון מההתחלה
4. **מניעת בלבול:** מפתחים חדשים לא יטעו

---

## 📚 מסמכים נוספים

| מסמך | תיאור |
|------|--------|
| `MONGODB_COLLECTIONS_CLARIFICATION.md` | מסמך טכני מפורט (200+ שורות) |
| `MONGODB_NODE2_NODE4_ISSUE_SUMMARY.md` | סיכום מנהלים (1 עמוד) |
| `README.md` (שורות 221-245) | הערה ב-README הראשי |
| `דוח_השוואה_JIRA_מול_אוטומציה.md` | עדכון בדוח ההשוואה |

---

## ✅ פעולות שכבר בוצעו

- [x] תיעוד הבעיה במסמך מפורט
- [x] עדכון README עם אזהרה
- [x] עדכון דוח ההשוואה Jira vs Code
- [x] יצירת סיכום מנהלים
- [x] זיהוי כל הטסטים המושפעים

---

## 📋 פעולות נדרשות (TODO)

### דחוף (השבוע):
- [ ] לעדכן PZ-13598 ב-Jira
- [ ] לעדכן PZ-13684 ב-Jira
- [ ] לעדכן PZ-13685 ב-Jira
- [ ] לברר מהיכן הגיעו השמות המקוריים node2/node4

### קצר טווח (שבועיים):
- [ ] לעדכן PZ-13686, PZ-13687, PZ-13705
- [ ] לחפש התייחסויות נוספות ב-Jira
- [ ] לעדכן כל התיעוד הפנימי

### ארוך טווח (חודש):
- [ ] ליצור תהליך אימות בין Jira לקוד
- [ ] להוסיף בדיקות אוטומטיות לזיהוי אי-התאמות

---

## 👥 מי צריך לראות את זה?

- ✅ **QA Team Lead** - לאישור העדכונים
- ✅ **Jira Admin** - לביצוע העדכונים
- ✅ **Tech Lead** - להסבר על הארכיטקטורה
- ✅ **Dev Team** - להבנת המבנה האמיתי

---

## 💬 שאלות ותשובות

**ש: למה לא פשוט לשנות את הקוד להתאים ל-Jira?**  
ת: כי הקוד נכון! הוא משקף את המערכת האמיתית. Jira צריך להתאים למציאות, לא להיפך.

**ש: האם יש סיכון שהמערכת תשתמש ב-node2/node4 בעתיד?**  
ת: לא סביר. GUID-based naming הוא עיקרון אדריכלי שמאפשר multiple base paths.

**ש: האם זה משפיע על הטסטים הקיימים?**  
ת: לא! הטסטים האוטומטיים שלנו עובדים נכון. רק התיעוד ב-Jira צריך עדכון.

**ש: איך נוכל למנוע בעיות דומות בעתיד?**  
ת: באמצעות תהליך אימות אוטומטי ו-CI/CD integration בין קוד ל-Jira.

---

## 📞 צור קשר

יש שאלות? פנה ל:
- **QA Automation Team**
- **Email:** qa@prismaphotonics.com
- **Slack:** #qa-automation

---

**תאריך עדכון אחרון:** 21 אוקטובר 2025  
**סטטוס:** ✅ מתועד - ממתין לעדכוני Jira  
**נוצר על ידי:** QA Automation Team

