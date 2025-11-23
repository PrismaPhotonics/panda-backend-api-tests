# פתרון: PL5012 Runner Offline

**תאריך:** 2025-01-23  
**Runner:** PL5012 (Windows, self-hosted, X64)  
**Status:** Offline ❌  
**URL:** https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/21

---

## 🚨 הבעיה

ה-runner **PL5012** הוא **Offline**, וכל ה-workflows שלנו תלויים בו:
- ✅ Smoke Tests
- ✅ Regression Tests  
- ✅ Load and Performance Tests

**כל ה-workflows משתמשים ב:** `runs-on: [self-hosted, Windows]`

---

## ✅ פתרון מהיר

### שלב 1: בדוק אם ה-Runner Service רץ

על המחשב PL5012, פתח PowerShell ובדוק:

```powershell
Get-Service actions.runner.*
```

**אם אתה רואה שירות רץ:**
- Status: `Running` → ה-service רץ, אבל ה-runner לא מתחבר ל-GitHub
- המשך לשלב 2

**אם אין שירות:**
- המשך לשלב 3

---

### שלב 2: Restart ה-Runner Service

אם ה-service רץ אבל ה-runner Offline:

```powershell
# עצור את ה-service
Stop-Service actions.runner.*

# המתן כמה שניות
Start-Sleep -Seconds 5

# התחל שוב
Start-Service actions.runner.*

# בדוק שה-service רץ
Get-Service actions.runner.*
```

**המתן 30-60 שניות** ואז רענן את הדף ב-GitHub:
https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/21

---

### שלב 3: התחל את ה-Runner Service

אם אין שירות רץ:

```powershell
# לך לתיקיית ה-runner
cd C:\actions-runner

# התחל את ה-service
.\svc\start.cmd

# או אם אין תיקיית svc, הרץ ישירות:
.\run.cmd
```

**⚠️ חשוב:**
- אם אתה מריץ `.\run.cmd` → ה-runner ירוץ רק כל עוד ה-PowerShell פתוח
- אם אתה רוצה שה-runner ירוץ תמיד → השתמש ב-`.\svc\start.cmd`

---

### שלב 4: בדוק את ה-Logs

אם ה-runner עדיין Offline אחרי 2-3 דקות:

```powershell
cd C:\actions-runner\_diag

# מצא את ה-log האחרון
$latestLog = Get-ChildItem -Filter "Runner_*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

# תצוג את ה-50 שורות האחרונות
Get-Content $latestLog.FullName -Tail 50
```

**חפש שגיאות כמו:**
- `Error connecting to GitHub`
- `Authentication failed`
- `Network error`

---

## 🔍 בדיקה: האם ה-Runner עובד?

### דרך 1: בדוק ב-GitHub

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/21
2. רענן את הדף (F5)
3. בדוק את ה-Status:
   - ✅ **Online** (ירוק) = הכל תקין!
   - ⚠️ **Offline** (אדום) = צריך לבדוק עוד

### דרך 2: הרץ Workflow לבדיקה

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
2. בחר: **Smoke Tests**
3. לחץ: **Run workflow**
4. בחר branch: `chore/add-roy-tests` (או `main`)
5. לחץ: **Run workflow**
6. ה-workflow צריך להתחיל לרוץ תוך כמה שניות

**אם ה-workflow תקוע ב-"Waiting for a runner...":**
- ה-runner עדיין Offline או לא מזהה את ה-job
- בדוק את ה-labels (צריך להיות: `self-hosted`, `Windows`)

---

## 📝 Checklist

- [ ] בדקתי שה-runner service רץ: `Get-Service actions.runner.*`
- [ ] הפעלתי/עשיתי restart ל-runner service
- [ ] המתנתי 30-60 שניות
- [ ] רעננתי את הדף ב-GitHub
- [ ] ה-runner Online ב-GitHub ✅
- [ ] בדקתי workflow לבדיקה

---

## 💡 טיפים

1. **אם אתה עובד מהבית:** ודא שה-runner service רץ כל הזמן
2. **אם המחשב נכבה:** ה-runner יעצור, אבל יתחיל שוב כשתדליק את המחשב (אם הותקן כשירות)
3. **לבדיקה מהירה:** הרץ `Get-Service actions.runner.*` כדי לראות אם ה-runner רץ

---

## 🔗 קישורים שימושיים

- **Runner Settings:** https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/21
- **Actions:** https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
- **All Runners:** https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners

---

**עודכן לאחרונה:** 2025-01-23

