# פתרון: Cannot open actions.runner service - בעיית הרשאות

**בעיה:** `Cannot open actions.runner.PrismaPhotonics-panda-backend-api-tests.PL5012 service`  
**סיבה:** צריך הרשאות Administrator כדי לעצור/להפעיל שירותים

---

## ✅ פתרון 1: הרץ PowerShell כ-Administrator

**על המחשב PL5012:**

1. לחץ על **Start** (או Windows key)
2. הקלד: `PowerShell`
3. לחץ ימין על **Windows PowerShell**
4. בחר: **Run as administrator**
5. הרץ את הפקודות:

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

---

## ✅ פתרון 2: בדוק את ה-Logs (ללא הרשאות)

אם ה-service רץ אבל ה-runner Offline, בדוק את ה-logs:

```powershell
# לך לתיקיית ה-runner
cd C:\actions-runner\_diag

# מצא את ה-log האחרון
$latestLog = Get-ChildItem -Filter "Runner_*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

# תצוג את ה-50 שורות האחרונות
Get-Content $latestLog.FullName -Tail 50
```

**חפש:**
- `√ Connected to GitHub` → הכל תקין!
- `Listening for Jobs` → הכל תקין!
- `Error connecting` → בעיית חיבור
- `Authentication failed` → בעיית אימות

---

## ✅ פתרון 3: Restart דרך Services.msc

1. לחץ **Windows + R**
2. הקלד: `services.msc`
3. לחץ **Enter**
4. מצא את השירות: **GitHub Actions Runner (PrismaPhotonics-panda-backend-api-tests.PL5012)**
5. לחץ ימין על השירות
6. בחר: **Restart**

---

## ✅ פתרון 4: בדוק את ה-Status ב-GitHub

אם ה-service רץ אבל ה-runner Offline ב-GitHub:

1. המתן 30-60 שניות
2. רענן את הדף: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/21
3. לפעמים לוקח זמן ל-GitHub לעדכן את ה-status

---

## ✅ פתרון 5: נסה להריץ Workflow

לפעמים ה-runner עובד גם אם הוא Offline ב-GitHub:

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
2. בחר: **Smoke Tests**
3. לחץ: **Run workflow**
4. אם ה-workflow מתחיל לרוץ → ה-runner עובד!

---

## 🔍 מה לבדוק עכשיו

1. **ה-service רץ?** ✅ כן (ראינו ב-`Get-Service`)
2. **ה-runner Offline ב-GitHub?** ⚠️ צריך לבדוק
3. **מה ה-logs אומרים?** → בדוק עם פתרון 2

---

## 💡 המלצה

**אם אתה לא יכול להריץ PowerShell כ-Administrator:**

1. בדוק את ה-logs (פתרון 2)
2. נסה להריץ workflow (פתרון 5)
3. אם ה-workflow עובד → הכל תקין, רק ה-status ב-GitHub לא מעודכן

---

**עודכן לאחרונה:** 2025-01-23

