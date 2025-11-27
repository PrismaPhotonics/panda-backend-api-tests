# הגדרת SSH Key על PL5012 Runner
# Setup SSH Key on PL5012 Runner

**Runner:** PL5012  
**URL:** https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners

---

## 🎯 מטרה

להגדיר את ה-SSH key `panda_staging_key` על ה-runner PL5012 כדי שה-health checks יעברו.

---

## 🔍 שלב 1: גישה ל-PL5012

יש לך כמה אפשרויות לגשת ל-PL5012:

### אפשרות A: RDP (Remote Desktop) - מומלץ

1. **פתח Remote Desktop Connection:**
   ```powershell
   mstsc
   ```

2. **התחבר ל-PL5012:**
   - Computer: `PL5012` או ה-IP של המחשב
   - Username: המשתמש שלך (כנראה `PL5012$` או משתמש אחר)
   - Password: הסיסמה שלך

### אפשרות B: SSH (אם SSH מופעל)

```powershell
ssh USERNAME@PL5012
# או
ssh USERNAME@<IP_OF_PL5012>
```

### אפשרות C: ישירות על המחשב

אם אתה במעבדה, התחבר ישירות למחשב PL5012.

---

## 📁 שלב 2: זיהוי הנתיב הנכון

לאחר התחברות ל-PL5012, בדוק מה ה-username וה-USERPROFILE:

```powershell
# בדוק את ה-username הנוכחי
$env:USERNAME

# בדוק את ה-USERPROFILE
$env:USERPROFILE

# בדוק את ה-COMPUTERNAME
$env:COMPUTERNAME
```

**תוצאה צפויה:**
- `USERNAME`: `PL5012$` או משתמש אחר
- `USERPROFILE`: `C:\Users\PL5012$` או `C:\Windows\system32\config\systemprofile` (אם רץ כ-service)

---

## 🔑 שלב 3: העתקת ה-SSH Key

### שלב 3.1: בדוק אם יש לך את ה-key כבר

```powershell
# בדוק אם ה-key קיים במיקומים שונים
Test-Path "C:\Users\$env:USERNAME\.ssh\panda_staging_key"
Test-Path "C:\actions-runner\.ssh\panda_staging_key"
Test-Path "$env:USERPROFILE\.ssh\panda_staging_key"
```

### שלב 3.2: העתק את ה-key

**אם יש לך את ה-key על המחשב שלך:**

```powershell
# מהמחשב שלך (לא על PL5012)
# העתק את ה-key ל-PL5012 דרך RDP או network share
```

**או דרך PowerShell (אם יש network share):**

```powershell
# על PL5012
# צור את התיקייה
New-Item -ItemType Directory -Force -Path "C:\Users\$env:USERNAME\.ssh"
New-Item -ItemType Directory -Force -Path "C:\actions-runner\.ssh"

# העתק את ה-key (החלף את הנתיב למקום שבו ה-key נמצא)
Copy-Item "\\YOUR_COMPUTER\share\panda_staging_key" -Destination "C:\Users\$env:USERNAME\.ssh\panda_staging_key"
Copy-Item "\\YOUR_COMPUTER\share\panda_staging_key" -Destination "C:\actions-runner\.ssh\panda_staging_key"
```

**או דרך USB/Network:**

1. העתק את `panda_staging_key` ל-USB או network share
2. על PL5012, העתק את הקובץ למיקום הנכון

### שלב 3.3: הגדר הרשאות

```powershell
# הגדר הרשאות לקובץ (רק הבעלים יכול לקרוא)
icacls "C:\Users\$env:USERNAME\.ssh\panda_staging_key" /inheritance:r /grant:r "$env:USERNAME`:R"

# או אם זה ב-actions-runner
icacls "C:\actions-runner\.ssh\panda_staging_key" /inheritance:r /grant:r "$env:USERNAME`:R"
```

---

## 🔧 שלב 4: בדיקה

לאחר העתקת ה-key, הרץ את הסקריפט לבדיקה:

```powershell
# על PL5012
cd C:\Projects\focus_server_automation  # או הנתיב של הפרויקט
.\scripts\check_runner_infrastructure.ps1
```

או בדוק ידנית:

```powershell
# בדוק שהקובץ קיים
Test-Path "C:\Users\$env:USERNAME\.ssh\panda_staging_key"

# בדוק את הגודל (אמור להיות כמה KB)
(Get-Item "C:\Users\$env:USERNAME\.ssh\panda_staging_key").Length
```

---

## 🚀 שלב 5: הפעלה מחדש של ה-Runner

לאחר העתקת ה-key, הפעל מחדש את ה-runner service:

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

## ✅ שלב 6: בדיקה ב-GitHub Actions

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
2. הרץ את ה-workflow "Smoke Tests"
3. בדוק שה-health checks עוברים

---

## 🔍 פתרון בעיות

### הבעיה: ה-key לא נמצא

**פתרון:**
- ודא שהקובץ קיים בנתיב הנכון
- בדוק את הרשאות הקובץ
- ודא שה-runner service רץ תחת אותו משתמש שיש לו גישה לקובץ

### הבעיה: ה-runner עדיין מחפש ב-system profile

**פתרון:**
- ה-runner רץ כ-service תחת SYSTEM account
- העתק את ה-key גם ל-`C:\actions-runner\.ssh\panda_staging_key`
- או שנה את ה-runner service לרוץ תחת משתמש ספציפי

### הבעיה: אין גישה ל-PL5012

**פתרון:**
- שאל את מנהל המערכת לגישה
- בדוק אם יש RDP או SSH מופעל
- בדוק אם המחשב במעבדה נגיש

---

## 📝 Checklist

- [ ] התחברתי ל-PL5012 (RDP/SSH/ישירות)
- [ ] בדקתי את ה-USERNAME וה-USERPROFILE
- [ ] העתקתי את `panda_staging_key` למיקום הנכון
- [ ] הגדרתי הרשאות לקובץ
- [ ] בדקתי שהקובץ קיים
- [ ] הפעלתי מחדש את ה-runner service
- [ ] בדקתי ב-GitHub Actions שה-health checks עוברים

---

## 🔗 קישורים שימושיים

- **Runner Settings:** https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
- **Actions:** https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
- **Runner Troubleshooting:** `docs/07_infrastructure/RUNNER_TROUBLESHOOTING.md`

---

**עודכן לאחרונה:** 2025-11-27

