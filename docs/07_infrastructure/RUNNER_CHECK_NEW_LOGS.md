# בדיקת Logs חדשים אחרי Restart

**תאריך:** 2025-01-23  
**בעיה:** ה-logs שמוצגים הם ישנים (מ-09:05-09:08) לפני ה-restart

---

## 🔍 מה הבעיה?

ה-logs שמוצגים הם מהישנים, לא מה-הרצה החדשה אחרי ה-restart.

**התאריכים ב-logs:**
- `[2025-11-23 09:05:43Z]` - לפני ה-restart
- `[2025-11-23 09:08:30Z]` - לפני ה-restart

---

## ✅ מה לעשות

### שלב 1: בדוק את כל ה-Logs לפי תאריך

```powershell
# בדוק את כל ה-logs לפי תאריך
Get-ChildItem -Filter "Runner_*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 5 | Format-Table Name, LastWriteTime
```

זה יראה לך את כל ה-logs החדשים ביותר.

---

### שלב 2: בדוק את ה-Log החדש ביותר

```powershell
# מצא את ה-log החדש ביותר
$latestLog = Get-ChildItem -Filter "Runner_*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

# תצוג את התאריך
Write-Host "Log: $($latestLog.Name) - Last Write: $($latestLog.LastWriteTime)"

# תצוג את ה-50 שורות האחרונות
Get-Content $latestLog.FullName -Tail 50
```

**חפש:**
- תאריך חדש (אחרי ה-restart)
- `√ Connected to GitHub` → הכל תקין!
- `Listening for Jobs` → הכל תקין!

---

### שלב 3: בדוק את ה-Logs בזמן אמת

אם אין logs חדשים, נסה להריץ את ה-runner ישירות כדי לראות מה קורה:

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

### שלב 4: נסה להריץ Workflow לבדיקה

לפעמים ה-runner עובד למרות השגיאות ב-logs הישנים:

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
2. בחר: **Smoke Tests**
3. לחץ: **Run workflow**
4. בחר branch: `chore/add-roy-tests` (או `main`)
5. לחץ: **Run workflow**

**אם ה-workflow מתחיל לרוץ תוך כמה שניות → ה-runner עובד!** ✅

---

## 💡 המלצה

**התחל עם:**
1. ✅ בדוק את כל ה-logs לפי תאריך (שלב 1)
2. ✅ בדוק את ה-log החדש ביותר (שלב 2)
3. ✅ אם אין logs חדשים → נסה להריץ ישירות (שלב 3)
4. ✅ נסה להריץ workflow (שלב 4)

---

## 🔗 קישורים שימושיים

- **Actions:** https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
- **Smoke Tests:** https://github.com/PrismaPhotonics/panda-backend-api-tests/actions/workflows/smoke-tests.yml

---

**עודכן לאחרונה:** 2025-01-23

