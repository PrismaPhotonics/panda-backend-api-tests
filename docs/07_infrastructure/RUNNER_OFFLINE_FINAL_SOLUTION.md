# פתרון סופי: Runner Offline למרות שהוא רץ

**בעיה:** Runner רץ ב-PowerShell, מתחבר ל-GitHub, אבל Offline ב-GitHub  
**סיבה:** לוקח זמן ל-GitHub לעדכן את ה-status, או בעיה ב-heartbeat

---

## 🔍 מה לבדוק

### 1. ודא שה-Runner באמת רץ

ב-PowerShell שבו ה-runner רץ, אתה אמור לראות:
```
√ Connected to GitHub
Listening for Jobs...
```

אם אתה רואה את זה → ה-runner רץ תקין!

---

### 2. המתן 2-3 דקות

לוקח ל-GitHub לפעמים 2-3 דקות לעדכן את ה-status.

**נסה:**
1. המתן 2-3 דקות
2. רענן את הדף ב-GitHub (F5)
3. בדוק שוב

---

### 3. נסה להריץ Workflow

לפעמים ה-runner עובד גם אם הוא Offline ב-GitHub!

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
2. בחר: **Smoke Tests**
3. לחץ: **Run workflow**
4. בחר branch: `chore/add-roy-tests`
5. לחץ: **Run workflow**

**אם ה-workflow מתחיל לרוץ → ה-runner עובד!** (גם אם הוא Offline ב-GitHub)

---

## 🔧 פתרון: Restart ה-Runner

אם אחרי 3 דקות ה-runner עדיין Offline:

1. ב-PowerShell שבו ה-runner רץ, לחץ **Ctrl+C** כדי לעצור
2. המתן 10 שניות
3. הרץ שוב:
   ```powershell
   cd C:\actions-runner
   .\run.cmd
   ```
4. המתן 2-3 דקות
5. רענן את הדף ב-GitHub (F5)
6. בדוק שוב

---

## ⚠️ אם זה עדיין לא עובד

אם אחרי ה-restart ה-runner עדיין Offline:

1. **בדוק את ה-Logs:**
   ```powershell
   cd C:\actions-runner\_diag
   Get-ChildItem -Filter "Runner_*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Get-Content -Tail 50
   ```

2. **בדוק את ה-Firewall:**
   - ודא שה-Firewall לא חוסם את ה-runner
   - נסה לכבות את ה-Firewall זמנית לבדיקה

3. **נסה להריץ Workflow:**
   - לפעמים ה-runner עובד גם אם הוא Offline ב-GitHub
   - אם ה-workflow רץ → הכל תקין!

---

## ✅ מה לעשות עכשיו

1. **המתן 2-3 דקות**
2. **רענן את הדף ב-GitHub** (F5)
3. **נסה להריץ Workflow** - זה יעבוד גם אם הוא Offline!
4. **אם זה לא עובד** → Restart את ה-runner

---

## 💡 טיפ חשוב

**אם ה-workflows מתחילים לרוץ → הכל תקין!**  
לא משנה אם ה-runner Offline ב-GitHub - העיקר שה-workflows רצים.

---

**עודכן לאחרונה:** 2025-11-19

