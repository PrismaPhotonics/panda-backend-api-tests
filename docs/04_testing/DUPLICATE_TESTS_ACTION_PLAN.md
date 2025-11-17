# תוכנית פעולה - Duplicate Tests ב-Xray

**תאריך:** 27 באוקטובר 2025  
**סטטוס:** הבהרה

---

## ❌ **לא למחוק!**

**אל תמחק** טסטים מ-Xray!

---

## ✅ מה לעשות במקום

### הבעיה:
יש 4 טסטים ב-Xray שהם **כפילויות** - קיים טסט אחר שכבר בודק את אותו הדבר.

### הפתרון:
**סגור אותם ב-Jira כ-"Duplicate"** (לא למחוק!)

---

## 📋 4 הטסטים ה-Duplicate

### 1. PZ-13813: SingleChannel 1:1 Mapping
**למה duplicate:**
- PZ-13861 כבר בודק את אותו הדבר בדיוק
- שני הטסטים: "SingleChannel view returns correct 1:1 mapping"

**פעולה ב-Jira:**
```
Action: Close Issue
Resolution: Duplicate
Comment: Duplicate of PZ-13861 (SingleChannel Stream Mapping Verification)
Link: Add "duplicates" link to PZ-13861
```

---

### 2. PZ-13770: /config Latency P95/P99
**למה duplicate:**
- PZ-13920 + PZ-13921 כבר בודקים P95 ו-P99 latency
- אותה בדיקה בדיוק

**פעולה ב-Jira:**
```
Action: Close Issue
Resolution: Duplicate
Comment: Duplicate of PZ-13920 (P95 latency) and PZ-13921 (P99 latency)
Link: Add "duplicates" links to PZ-13920, PZ-13921
```

---

### 3. PZ-13571: Performance /configure latency p95
**למה duplicate:**
- זהה ל-PZ-13920 (P95 latency test)
- אותה בדיקה

**פעולה ב-Jira:**
```
Action: Close Issue
Resolution: Duplicate
Comment: Duplicate of PZ-13920 (Configuration Endpoint P95 Latency)
Link: Add "duplicates" link to PZ-13920
```

---

### 4. PZ-13556: SingleChannel view mapping
**למה duplicate:**
- PZ-13861 כבר בודק את ה-mapping של SingleChannel
- כפילות

**פעולה ב-Jira:**
```
Action: Close Issue
Resolution: Duplicate
Comment: Duplicate of PZ-13861 (SingleChannel Stream Mapping Verification)
Link: Add "duplicates" link to PZ-13861
```

---

## 🔧 איך לסגור ב-Jira (צעד אחר צעד)

### דרך 1: סגירה בודדת

1. פתח את הטיקט (למשל PZ-13813)
2. לחץ על **"Close"** או **"Resolve"**
3. בחר **Resolution: "Duplicate"**
4. הוסף **Comment** שמסביר מי הטיקט המקורי
5. הוסף **Link** → "duplicates" → בחר את הטיקט המקורי
6. שמור

---

### דרך 2: Bulk Close (מהיר יותר)

1. חפש את כל 4 הטיקטים:
```jql
key in (PZ-13813, PZ-13770, PZ-13571, PZ-13556)
```

2. בחר את כולם
3. **Bulk Change** → **Transition Issues**
4. בחר **"Close"** או **"Done"**
5. **Resolution:** "Duplicate"
6. הוסף **Comment** גלובלי:
```
These tests are duplicates of existing tests already implemented in automation:
- PZ-13813 → PZ-13861
- PZ-13770 → PZ-13920, PZ-13921
- PZ-13571 → PZ-13920
- PZ-13556 → PZ-13861
```

---

## 📊 השפעה על הסטטיסטיקה

### לפני סגירת Duplicates:
- Total: 139 (137 + 2 new)
- Implemented: 107
- Not Implemented: 19
- Coverage: 77.0%

### אחרי סגירת Duplicates:
- **Total (active): 135** (139 - 4 duplicates)
- **Implemented: 107**
- **Not Implemented: 15**
- **Coverage: 79.3%**

### אחרי הוצאת Backlog (8) + Out of Scope (12):
- **Total (active): 115** (135 - 8 - 12)
- **Implemented: 107**
- **Not Implemented: 8**
- **Coverage: 93.0%**

---

## ✅ סיכום

### מה **לא** לעשות:
- ❌ **אל** תמחק טסטים מ-Xray
- ❌ **אל** תמחק מהמערכת

### מה **כן** לעשות:
- ✅ סגור 4 טסטים כ-**"Duplicate"** ב-Jira
- ✅ הוסף קישורים לטסטים המקוריים
- ✅ הוסף comment שמסביר

### למה זה טוב:
- ✅ שומר היסטוריה
- ✅ ניתן לעקוב
- ✅ ניתן לבטל אם טעינו
- ✅ מסודר ומקצועי

---

**לא למחוק - רק לסגור כ-Duplicate!** ✅

