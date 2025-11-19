# הגדרת Runner מהבית - מדריך מהיר

**Runner:** PL5012 (המחשב שלך מהבית)  
**Runner ID:** 21  
**URL:** https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/21

---

## ✅ בדיקה מהירה: האם ה-Runner Online?

### דרך 1: בדוק ב-GitHub
1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/21
2. בדוק את ה-Status:
   - ✅ **Online** (ירוק) = הכל תקין, ה-workflows יכולים לרוץ
   - ⚠️ **Offline** (אדום) = צריך להתחיל את ה-runner service

---

## 🔧 פתרון: התחל את ה-Runner Service

### שלב 1: בדוק אם ה-Service רץ

פתח **PowerShell** (או **PowerShell כ-Administrator** אם צריך) והרץ:

```powershell
# בדוק אם ה-runner service רץ
Get-Service actions.runner.*
```

**תוצאות אפשריות:**
- ✅ אם אתה רואה שירות עם Status = `Running` → הכל תקין!
- ❌ אם אתה רואה שירות עם Status = `Stopped` → צריך להתחיל אותו
- ❌ אם אין שירות בכלל → צריך להתקין אותו

---

### שלב 2: התחל את ה-Runner Service

אם ה-service לא רץ, הרץ את הפקודות הבאות:

```powershell
# לך לתיקיית ה-runner
cd C:\actions-runner

# בדוק אם יש תיקיית svc
Test-Path .\svc

# אם יש תיקיית svc, התחל את השירות:
.\svc\start.cmd

# אם אין תיקיית svc, הרץ את ה-runner ישירות:
.\run.cmd
```

---

### שלב 3: הרצה ידנית (אם אין service)

אם אין service מותקן, אתה יכול להריץ את ה-runner ישירות:

```powershell
cd C:\actions-runner
.\run.cmd
```

**⚠️ חשוב:** כשאתה מריץ את `run.cmd`, ה-runner רץ רק כל עוד ה-PowerShell פתוח. אם תסגור את החלון, ה-runner יעצור.

---

## 🚀 התקנת Runner כשירות (מומלץ)

אם אתה רוצה שה-runner ירוץ תמיד (גם אחרי הפעלה מחדש של המחשב):

```powershell
# פתח PowerShell כ-Administrator
cd C:\actions-runner

# התקן כשירות
.\svc\install.cmd

# התחל את השירות
.\svc\start.cmd

# בדוק שהשירות רץ
Get-Service actions.runner.*
```

**אם אין תיקיית `svc`:**
- זה אומר שה-runner לא הותקן כשירות
- אתה יכול להריץ אותו ידנית עם `.\run.cmd` (אבל זה יעצור כשתסגור את ה-PowerShell)

---

## 🔍 בדיקה: האם ה-Runner עובד?

### דרך 1: בדוק ב-GitHub
1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/21
2. אחרי כמה שניות, ה-Status צריך להשתנות ל-**Online** (ירוק)

### דרך 2: הרץ Workflow לבדיקה
1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
2. בחר: **Smoke Tests**
3. לחץ: **Run workflow**
4. בחר branch: `chore/add-roy-tests`
5. לחץ: **Run workflow**
6. ה-workflow צריך להתחיל לרוץ תוך כמה שניות

---

## ⚠️ בעיות נפוצות

### בעיה: "Waiting for a runner to pick up this job..."

**פתרונות:**
1. ✅ ודא שה-runner Online ב-GitHub
2. ✅ ודא שה-runner service רץ על המחשב שלך
3. ✅ ודא שה-labels תואמים:
   - Workflow משתמש ב: `runs-on: [self-hosted, Windows, X64]`
   - Runner צריך להיות עם: `self-hosted`, `Windows`, `X64`

### בעיה: Runner לא מתחבר ל-GitHub

**פתרונות:**
1. בדוק את החיבור לאינטרנט
2. בדוק את ה-logs:
   ```powershell
   cd C:\actions-runner\_diag
   Get-Content Runner_*.log -Tail 50
   ```

### בעיה: Runner עוצר אחרי הפעלה מחדש

**פתרון:** התקן את ה-runner כשירות:
```powershell
cd C:\actions-runner
.\svc\install.cmd
.\svc\start.cmd
```

---

## 📝 Checklist מהיר

- [ ] Runner Online ב-GitHub (ירוק)
- [ ] Runner service רץ על המחשב (`Get-Service actions.runner.*`)
- [ ] Labels נכונים: `self-hosted`, `Windows`, `X64`
- [ ] Workflow נדחף ל-GitHub
- [ ] בדיקה ידנית של workflow דרך GitHub UI

---

## 💡 טיפים

1. **אם אתה עובד מהבית:** ודא שה-runner service רץ כל הזמן כדי שה-workflows יוכלו לרוץ
2. **אם אתה סוגר את המחשב:** ה-runner יעצור, אבל יתחיל שוב כשתדליק את המחשב (אם הותקן כשירות)
3. **לבדיקה מהירה:** הרץ `Get-Service actions.runner.*` כדי לראות אם ה-runner רץ

---

**עודכן לאחרונה:** 2025-11-19

