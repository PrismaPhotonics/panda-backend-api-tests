# פתרון בעיות Runner - Workflows ב-Queued

**בעיה:** Workflows ב-Queued ולא מתחילים לרוץ  
**Runner:** PL5012 (המחשב מהבית)  
**Runner ID:** 21 (ב-GitHub) / Agent ID: 22 (מקומי)

---

## 🔍 בדיקה מהירה

### 1. בדוק ב-GitHub אם ה-Runner Online

לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/21

**אם Status = Offline:**
- ה-runner service רץ, אבל ה-runner לא מתחבר ל-GitHub
- צריך לבדוק את החיבור לאינטרנט
- צריך לבדוק את ה-logs

**אם Status = Online:**
- ה-runner Online, אבל לא מזהה jobs
- צריך לבדוק את ה-labels

---

## 🔧 פתרונות

### פתרון 1: Restart ה-Runner Service

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

### פתרון 2: בדוק את ה-Labels

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/21
2. לחץ על **Edit**
3. ודא שה-labels הם:
   - `self-hosted`
   - `Windows`
   - `X64`
4. לחץ **Save**

### פתרון 3: בדוק את ה-Workflow Labels

ה-workflow משתמש ב:
```yaml
runs-on: [self-hosted, Windows, X64]
```

ה-runner צריך להיות עם כל ה-labels האלה.

### פתרון 4: בדוק את ה-Logs

```powershell
cd C:\actions-runner\_diag
# מצא את ה-log האחרון
$latestLog = Get-ChildItem -Filter "Runner_*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
# תצוג את ה-50 שורות האחרונות
Get-Content $latestLog.FullName -Tail 50
```

חפש שגיאות כמו:
- `Error connecting to GitHub`
- `Authentication failed`
- `Job not found`

---

## ⚠️ בעיות נפוצות

### בעיה: Runner Service רץ אבל Runner Offline ב-GitHub

**פתרונות:**
1. בדוק את החיבור לאינטרנט
2. Restart את ה-service (ראה פתרון 1)
3. בדוק את ה-logs (ראה פתרון 4)

### בעיה: Runner Online אבל לא מזהה Jobs

**פתרונות:**
1. בדוק את ה-labels (ראה פתרון 2)
2. ודא שה-workflow משתמש ב-labels הנכונים
3. Restart את ה-service

### בעיה: חוסר התאמה בין Runner ID ב-GitHub ל-Agent ID מקומי

**פתרון:**
- זה לא בעיה - ה-Agent ID מקומי יכול להיות שונה מה-Runner ID ב-GitHub
- העיקר שה-runner Online ב-GitHub

---

## ✅ Checklist

- [ ] Runner Online ב-GitHub (ירוק)
- [ ] Runner service רץ על המחשב (`Get-Service actions.runner.*`)
- [ ] Labels נכונים: `self-hosted`, `Windows`, `X64`
- [ ] Workflow משתמש ב-labels הנכונים: `runs-on: [self-hosted, Windows, X64]`
- [ ] אין שגיאות ב-logs

---

**עודכן לאחרונה:** 2025-11-19

