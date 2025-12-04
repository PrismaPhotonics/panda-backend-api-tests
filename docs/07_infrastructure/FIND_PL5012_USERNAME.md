# איך למצוא את ה-USERNAME של PL5012
# How to Find PL5012 Username

---

## 🔍 שיטות למציאת ה-USERNAME

### שיטה 1: בדיקה דרך Runner Service (מומלץ)

אם יש לך גישה ל-PL5012 (RDP או ישירות), בדוק את ה-runner service:

```powershell
# בדוק את ה-runner service
Get-Service actions.runner.* | Format-List *

# או בדוק את ה-service configuration
sc qc actions.runner.PL5012*

# או בדוק את ה-process
Get-Process Runner.Listener | Select-Object ProcessName, StartInfo, UserName
```

**התוצאה תציג את המשתמש שרץ את ה-service.**

---

### שיטה 2: בדיקה ישירה על PL5012

אם אתה כבר מחובר ל-PL5012:

```powershell
# בדוק את המשתמש הנוכחי
whoami

# או
$env:USERNAME

# או
[System.Security.Principal.WindowsIdentity]::GetCurrent().Name
```

---

### שיטה 3: נסה Usernames נפוצים

נסה להתחבר עם usernames נפוצים:

```powershell
# נסה את אלה (אחד אחרי השני):
ssh roy@PL5012
ssh roy.avrahami@PL5012
ssh administrator@PL5012
ssh admin@PL5012
ssh prisma@PL5012
ssh PL5012\roy@PL5012
ssh PL5012\roy.avrahami@PL5012
```

**או דרך RDP:**
- נסה: `roy`, `roy.avrahami`, `administrator`, `admin`

---

### שיטה 4: בדיקה דרך GitHub Runners Settings

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
2. לחץ על ה-runner **PL5012**
3. בדוק את ה-labels וה-metadata - לפעמים יש שם מידע על המשתמש

---

### שיטה 5: בדיקה דרך Runner Logs

אם יש לך גישה ל-PL5012:

```powershell
# בדוק את ה-logs של ה-runner
cd C:\actions-runner\_diag
Get-Content Runner_*.log | Select-String -Pattern "user|username|User|Username" | Select-Object -First 10
```

---

### שיטה 6: בדיקה דרך Network Share או RDP

אם אתה מחובר דרך RDP או network share:

1. **פתח File Explorer**
2. **לך ל:** `\\PL5012\C$\Users`
3. **ראה את רשימת המשתמשים** - זה יעזור לך לדעת איזה usernames קיימים

---

## 🎯 לפי התיעוד הקיים

מהתיעוד במערכת, נראה שה-username הוא כנראה:

- **`roy`** או **`roy.avrahami`** (לפי `RUNNER_SETUP_READY.md`)
- **`PL5012\roy.avrahami`** (לפי `CHECK_USER_AND_COMPUTER.md`)

**נסה:**
```powershell
ssh roy@PL5012
# או
ssh roy.avrahami@PL5012
# או
ssh PL5012\roy@PL5012
```

---

## ✅ אחרי שמצאת את ה-USERNAME

לאחר שמצאת את ה-username, התחבר:

```powershell
ssh USERNAME@PL5012
# או אם יש domain:
ssh DOMAIN\USERNAME@PL5012
```

---

## 🔧 אם SSH לא עובד

אם SSH לא מופעל או לא עובד, השתמש ב-RDP:

```powershell
# פתח Remote Desktop
mstsc

# Computer: PL5012
# Username: USERNAME שמצאת
# Password: הסיסמה שלך
```

---

## 📝 Checklist

- [ ] בדקתי את ה-runner service configuration
- [ ] בדקתי את ה-processes שרצים
- [ ] ניסיתי usernames נפוצים
- [ ] בדקתי ב-GitHub runners settings
- [ ] בדקתי את ה-logs
- [ ] בדקתי דרך network share/RDP
- [ ] מצאתי את ה-username ✅

---

**עודכן:** 2025-11-27

