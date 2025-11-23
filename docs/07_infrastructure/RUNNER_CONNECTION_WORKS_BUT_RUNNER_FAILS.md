# פתרון: חיבור תקין אבל Runner לא מתחבר

**תאריך:** 2025-01-23  
**Runner:** PL5012  
**מצב:**
- ✅ חיבור לאינטרנט תקין
- ✅ DNS עובד
- ✅ חיבור ל-GitHub עובד
- ❌ Runner לא מתחבר ל-GitHub

---

## 🔍 מה הבעיה?

ה-runner מנסה להתחבר ל-`broker.actions.githubusercontent.com` אבל נכשל, למרות שהחיבור הכללי תקין.

**סיבות אפשריות:**
1. ה-runner service רץ אבל לא מתחבר נכון
2. בעיה עם ה-credentials או ה-configuration
3. ה-runner צריך restart מלא

---

## ✅ פתרונות

### פתרון 1: Restart מלא של ה-Runner Service

```powershell
# עצור את ה-service
Stop-Service actions.runner.*

# המתן 10 שניות
Start-Sleep -Seconds 10

# התחל שוב
Start-Service actions.runner.*

# המתן 30-60 שניות
Start-Sleep -Seconds 60

# בדוק את ה-logs שוב
cd C:\actions-runner\_diag
$latestLog = Get-ChildItem -Filter "Runner_*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Get-Content $latestLog.FullName -Tail 30
```

---

### פתרון 2: בדוק את ה-Configuration

```powershell
cd C:\actions-runner

# בדוק את ה-config
Get-Content .runner

# בדוק את ה-credentials
Get-Content .credentials
```

**חפש:**
- האם ה-URL נכון: `https://github.com/PrismaPhotonics/panda-backend-api-tests`
- האם יש token תקין

---

### פתרון 3: נסה להריץ Runner ישירות (לא כשירות)

לפעמים זה עוזר לזהות בעיות:

```powershell
cd C:\actions-runner

# עצור את ה-service
Stop-Service actions.runner.*

# המתן 5 שניות
Start-Sleep -Seconds 5

# הרץ ישירות
.\run.cmd
```

**חפש ב-console:**
- `√ Connected to GitHub` → הכל תקין!
- `Listening for Jobs` → הכל תקין!
- שגיאות → יש בעיה

**⚠️ חשוב:** זה ירוץ רק כל עוד ה-PowerShell פתוח. זה טוב לבדיקה.

---

### פתרון 4: בדוק אם יש Proxy או Firewall ספציפי

```powershell
# בדוק אם יש proxy מוגדר
[System.Net.WebRequest]::GetSystemWebProxy().GetProxy("https://broker.actions.githubusercontent.com")

# בדוק firewall rules
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*GitHub*" -or $_.DisplayName -like "*Actions*"}
```

---

### פתרון 5: נסה להריץ Workflow לבדיקה

לפעמים ה-runner עובד למרות השגיאות ב-logs:

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
2. בחר: **Smoke Tests**
3. לחץ: **Run workflow**
4. אם ה-workflow מתחיל לרוץ → ה-runner עובד!

---

## 💡 המלצה

**התחל עם:**
1. ✅ Restart מלא (פתרון 1)
2. ✅ המתן 60 שניות
3. ✅ בדוק את ה-logs שוב
4. ✅ נסה להריץ workflow (פתרון 5)

**אם זה לא עובד:**
- נסה להריץ ישירות (פתרון 3) כדי לראות שגיאות בזמן אמת

---

## 🔗 קישורים שימושיים

- **Runner Settings:** https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/21
- **Actions:** https://github.com/PrismaPhotonics/panda-backend-api-tests/actions

---

**עודכן לאחרונה:** 2025-01-23

