# פתרון סופי: Runner Offline ב-GitHub

**בעיה:** Runner רץ ב-PowerShell אבל Offline ב-GitHub  
**Labels:** נכונים (`self-hosted`, `Windows`, `X64`)  
**סיבה:** ה-runner לא שולח heartbeat ל-GitHub

---

## 🔧 פתרון מהיר

### שלב 1: עצור את ה-Runner

ב-PowerShell שבו ה-runner רץ:
- לחץ **Ctrl+C** כדי לעצור

---

### שלב 2: מחק את קבצי ההגדרה והגדר מחדש

```powershell
cd C:\actions-runner

# מחק את קבצי ההגדרה
Remove-Item .runner -Force -ErrorAction SilentlyContinue
Remove-Item .credentials -Force -ErrorAction SilentlyContinue
Remove-Item .credentials_migrated -Force -ErrorAction SilentlyContinue
Remove-Item .service -Force -ErrorAction SilentlyContinue

# קבל token חדש מ-GitHub:
# לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/new
# בחר Windows ו-x64
# תעתיק את ה-token

# הגדר מחדש (החלף <TOKEN> עם ה-token החדש)
.\config.cmd --url https://github.com/PrismaPhotonics/panda-backend-api-tests --token <TOKEN>
```

כששואלים אותך:
- Enter name for this runner: → לחץ Enter (להשאיר: `PL5012`)
- Enter labels: → לחץ Enter (להשאיר: `self-hosted,Windows,X64`)
- Enter work folder: → לחץ Enter (להשאיר: `_work`)
- Would you like to run the runner as service? → לחץ Enter (N)

---

### שלב 3: הרץ את ה-Runner

```powershell
cd C:\actions-runner
.\run.cmd
```

---

### שלב 4: בדוק ב-GitHub

1. המתן 30-60 שניות
2. רענן את הדף ב-GitHub (F5)
3. בדוק שה-runner Online

---

## ⚠️ אם זה עדיין לא עובד

אם אחרי ההגדרה מחדש ה-runner עדיין Offline:

1. **בדוק את החיבור לאינטרנט:**
   ```powershell
   Test-NetConnection github.com -Port 443
   ```

2. **בדוק את ה-Firewall:**
   - ודא שה-Firewall לא חוסם את ה-runner
   - נסה לכבות את ה-Firewall זמנית לבדיקה

3. **בדוק את ה-Logs:**
   ```powershell
   cd C:\actions-runner\_diag
   Get-ChildItem -Filter "Runner_*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Get-Content -Tail 50
   ```

---

## ✅ Checklist

- [ ] Runner עצור ב-PowerShell
- [ ] קבצי ההגדרה נמחקו
- [ ] Token חדש מ-GitHub
- [ ] Runner מוגדר מחדש
- [ ] Runner רץ (`.\run.cmd`)
- [ ] Runner Online ב-GitHub (אחרי 30-60 שניות)

---

**עודכן לאחרונה:** 2025-11-19

