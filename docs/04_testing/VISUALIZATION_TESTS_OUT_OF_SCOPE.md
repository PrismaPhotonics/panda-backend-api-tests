# 🚫 Visualization Tests - Out of Scope

**תאריך:** 27 באוקטובר 2025  
**סטטוס:** מסומנים למחיקה/סגירה

---

## החלטה

לפי החלטת הפגישה (PZ-13756), טסטי Visualization הם **OUT OF SCOPE**.

---

## רשימת טסטים למחיקה (12 טסטים)

| # | Xray ID | Summary | סיבת הסגירה |
|---|---------|---------|-------------|
| 1 | PZ-13801 | Visualization - Colormap Change | Out of Scope |
| 2 | PZ-13802 | Visualization - CAxis Adjustment | Out of Scope |
| 3 | PZ-13803 | Visualization - Invalid Colormap | Out of Scope |
| 4 | PZ-13804 | Visualization - CAxis Invalid Range | Out of Scope |
| 5 | PZ-13805 | Visualization - Multiple Commands Sequence | Out of Scope |
| 6 | PZ-13806 | Visualization - Colormap Persistence | Out of Scope |
| 7 | PZ-13807 | Visualization - CAxis Reset | Out of Scope |
| 8 | PZ-13808 | Visualization - Colormap Options List | Out of Scope |
| 9 | PZ-13809 | Visualization - CAxis Auto Range | Out of Scope |
| 10 | PZ-13810 | Visualization - Colormap Validation | Out of Scope |
| 11 | PZ-13811 | Visualization - CAxis Manual Range | Out of Scope |
| 12 | PZ-13812 | Visualization - Commands E2E Flow | Out of Scope |

---

## הנמקה

### למה Out of Scope?

1. **החלטת פגישה (PZ-13756):**
   - Visualization commands (Colormap, CAxis) לא בתחום הבדיקות
   - התמקדות ב-Kubernetes, API Validation, System Behavior

2. **עדיפויות:**
   - Infrastructure > Configuration > API > Visualization
   - Visualization = Low Priority / Out of Scope

3. **משאבים:**
   - 12 טסטים = ~2-3 ימי עבודה
   - עדיף להשקיע ב-SingleChannel, Historic, Live Monitoring

---

## פעולות נדרשות ב-Jira

### אופציה 1: סגירה כ-"Won't Do"
```
Resolution: Won't Do
Reason: Out of scope per meeting decision (PZ-13756)
Comment: Visualization commands (Colormap, CAxis) are not in test scope.
          Focus is on K8s orchestration, API validation, and system behavior.
```

### אופציה 2: העברה ל-Backlog
```
Status: Backlog
Priority: Low
Label: visualization, out-of-scope-current-epic
Comment: Deferred to future epic. Not included in current test plan.
```

### אופציה 3: קישור ל-Epic חדש
```
Create new Epic: "Visualization Commands Testing (Future)"
Link: PZ-13801 to PZ-13812 → New Epic
Status: To Do (in future epic)
```

---

## המלצה

**אופציה 1 מומלצת:**
- סגור כ-**"Won't Do"**
- סיבה: **Out of Scope (PZ-13756)**
- הוסף comment שמסביר החלטה

---

## קישורי Jira (לעדכון)

### Bulk Update Command:
```
project = PZ AND key in (PZ-13801, PZ-13802, PZ-13803, PZ-13804, PZ-13805, PZ-13806, PZ-13807, PZ-13808, PZ-13809, PZ-13810, PZ-13811, PZ-13812)
```

### פעולות:
1. Select all 12 issues
2. Bulk Change → Transition Issues
3. Choose "Won't Do" or "Cancelled"
4. Add comment: "Out of scope per test plan refinement (PZ-13756)"

---

## השפעה על הסטטיסטיקה

### לפני סגירה:
- טסטים ב-Xray: 113
- ממומשים: 51
- לא ממומשים: 62
- כיסוי: 45.1%

### אחרי סגירה (הוצאת 12 Visualization):
- **טסטים ב-Xray (רלוונטיים): 101**
- **ממומשים: 51**
- **לא ממומשים: 50**
- **כיסוי: 50.5%** ← שיפור ניכר!

---

## סיכום

**החלטה:** סגור 12 טסטי Visualization כ-Out of Scope  
**פעולה:** Bulk close ב-Jira עם נימוק  
**תוצאה:** כיסוי עולה ל-50.5% ללא עבודה נוספת

---

**קובץ זה מוכן לשליחה למנהל/לצוות!**

