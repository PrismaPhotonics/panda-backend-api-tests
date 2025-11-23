# פתרון: Runner Offline ב-GitHub למרות שהוא רץ

**בעיה:** Runner רץ ב-PowerShell אבל Offline ב-GitHub  
**סיבה:** לוקח זמן ל-GitHub לעדכן את ה-status, או runner חדש

---

## 🔍 בדיקה מהירה

### 1. ודא שה-Runner רץ

ב-PowerShell שבו ה-runner רץ, אתה אמור לראות:
```
√ Connected to GitHub
Listening for Jobs...
```

אם אתה רואה את זה → ה-runner רץ תקין!

---

### 2. המתן כמה שניות

לוקח ל-GitHub 10-30 שניות לעדכן את ה-status.

**נסה:**
1. רענן את הדף ב-GitHub (F5)
2. המתן 30 שניות
3. בדוק שוב

---

### 3. בדוק ב-GitHub

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
2. רענן את הדף (F5)
3. בדוק אם ה-runner מופיע שם

**אם ה-runner לא מופיע:**
- זה אומר שה-runner לא נרשם ב-GitHub
- צריך להגדיר מחדש

**אם ה-runner מופיע אבל Offline:**
- המתן עוד 30 שניות
- רענן את הדף
- בדוק את ה-logs

---

## 🔧 פתרונות

### פתרון 1: המתן ורענן

1. המתן 30-60 שניות
2. רענן את הדף ב-GitHub (F5)
3. בדוק שוב

### פתרון 2: בדוק את ה-Logs

ב-PowerShell שבו ה-runner רץ, בדוק אם יש שגיאות.

אם אתה רואה:
- `√ Connected to GitHub` → הכל תקין!
- `Listening for Jobs` → הכל תקין!

אם אתה רואה שגיאות:
- שלח את השגיאה

### פתרון 3: Restart ה-Runner

1. ב-PowerShell שבו ה-runner רץ, לחץ **Ctrl+C** כדי לעצור
2. הרץ שוב:
   ```powershell
   cd C:\actions-runner
   .\run.cmd
   ```
3. המתן 30 שניות
4. בדוק ב-GitHub שוב

---

## ✅ מה לעשות עכשיו

1. **ודא שה-runner רץ** - אתה רואה `Listening for Jobs`?
2. **המתן 30-60 שניות**
3. **רענן את הדף ב-GitHub** (F5)
4. **בדוק שוב** - האם ה-runner Online?

---

## 💡 טיפ

אם ה-runner עדיין Offline אחרי 2-3 דקות:
- בדוק את ה-logs (ראה פתרון 2)
- נסה להריץ workflow - לפעמים ה-runner עובד גם אם הוא Offline ב-GitHub

---

**עודכן לאחרונה:** 2025-11-19

