# Runner לא כותב Logs חדשים אחרי Restart

**תאריך:** 2025-01-23  
**בעיה:** ה-log עודכן ב-11:08:30 אבל התוכן עדיין ישן (מ-09:05-09:08)

---

## 🚨 מה זה אומר?

ה-runner לא כותב logs חדשים אחרי ה-restart. זה יכול להיות:
1. ה-runner לא מתחיל נכון
2. ה-runner תקוע ולא מתחבר
3. בעיית configuration

---

## ✅ פתרונות

### פתרון 1: בדוק אם ה-Runner Service באמת רץ

```powershell
# בדוק את ה-status
Get-Service actions.runner.*

# בדוק את ה-process
Get-Process | Where-Object {$_.ProcessName -like "*runner*"}
```

**אם אין process:**
- ה-service לא רץ נכון
- צריך לבדוק למה

---

### פתרון 2: הרץ Runner ישירות (לא כשירות)

זה יעזור לראות מה קורה בזמן אמת:

```powershell
cd C:\actions-runner

# עצור את ה-service
Stop-Service actions.runner.*

# המתן 5 שניות
Start-Sleep -Seconds 5

# הרץ ישירות (תראה את ה-output בזמן אמת)
.\run.cmd
```

**חפש ב-console:**
- `√ Connected to GitHub` → הכל תקין!
- `Listening for Jobs` → הכל תקין!
- שגיאות → יש בעיה

**⚠️ חשוב:** זה ירוץ רק כל עוד ה-PowerShell פתוח. זה טוב לבדיקה.

---

### פתרון 3: בדוק את ה-Configuration

```powershell
cd C:\actions-runner

# בדוק את ה-config
Get-Content .runner

# בדוק אם יש בעיות
Test-Path .runner
Test-Path .credentials
```

**חפש:**
- האם ה-URL נכון: `https://github.com/PrismaPhotonics/panda-backend-api-tests`
- האם יש token תקין

---

### פתרון 4: נסה להריץ Workflow לבדיקה

לפעמים ה-runner עובד למרות שאין logs חדשים:

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
2. בחר: **Smoke Tests**
3. לחץ: **Run workflow**
4. בחר branch: `chore/add-roy-tests` (או `main`)
5. לחץ: **Run workflow**

**אם ה-workflow מתחיל לרוץ תוך כמה שניות → ה-runner עובד!** ✅

**אם ה-workflow תקוע ב-"Waiting for a runner..." → ה-runner לא עובד**

---

### פתרון 5: Reconfigure את ה-Runner

אם כלום לא עובד, אולי צריך להגדיר מחדש:

```powershell
cd C:\actions-runner

# עצור את ה-service
Stop-Service actions.runner.*

# הסר את ה-config הישן (אבל שמור backup!)
Copy-Item .runner .runner.backup
Copy-Item .credentials .credentials.backup

# הגדר מחדש (תצטרך token חדש מ-GitHub)
.\config.cmd --url https://github.com/PrismaPhotonics/panda-backend-api-tests --token YOUR_TOKEN
```

**איך לקבל token חדש:**
1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
2. לחץ על **"New self-hosted runner"**
3. העתק את ה-token

---

## 💡 המלצה

**התחל עם:**
1. ✅ בדוק אם ה-service רץ (פתרון 1)
2. ✅ הרץ ישירות כדי לראות מה קורה (פתרון 2)
3. ✅ נסה להריץ workflow (פתרון 4)

**אם כלום לא עובד:**
- נסה reconfigure (פתרון 5)

---

## 🔗 קישורים שימושיים

- **Actions:** https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
- **Runners:** https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
- **New Runner Token:** https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/new

---

**עודכן לאחרונה:** 2025-01-23

