# הגדרת GitHub Actions Runner על Slave Laptop (10.50.0.36)
# Setup GitHub Actions Runner on Slave Laptop (10.50.0.36)

**תאריך:** 2025-01-XX  
**מטרה:** הגדרת self-hosted runner על ה-slave laptop במעבדה להרצת GitHub Actions

---

## 📋 סקירה כללית

ה-slave laptop (IP: 10.50.0.36) יושב ליד המערכות ומחובר בכבל רשת, מה שמאפשר לו גישה ישירה לרשת הפנימית (10.10.10.x) ללא צורך ב-VPN.

**יתרונות:**
- ✅ גישה ישירה לרשת הפנימית
- ✅ יכול להריץ בדיקות שדורשות גישה ל-K8s, MongoDB, RabbitMQ
- ✅ לא תלוי ב-VPN
- ✅ זמין 24/7

---

## 🚀 שלב 1: קבלת Registration Token מ-GitHub

1. **לך ל-GitHub Repository:**
   ```
   https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/new
   ```

2. **בחר את מערכת ההפעלה:**
   - אם ה-slave laptop הוא **Windows** → בחר **Windows**
   - אם ה-slave laptop הוא **Linux** → בחר **Linux**

3. **העתק את ה-Registration Token:**
   - GitHub יציג לך token (נראה כמו: `AXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`)
   - **חשוב:** ה-token תקף ל-1 שעה בלבד!

---

## 🖥️ שלב 2: זיהוי מערכת ההפעלה

### בדיקה ידנית:
```powershell
# התחבר ל-slave laptop
ssh user@10.50.0.36

# בדוק מערכת הפעלה
# Windows:
dir C:\Windows

# Linux:
uname -a
```

---

## 🔧 שלב 3: הגדרת Runner

יש לך שתי אפשרויות:

### אפשרות 1: Python Script (מומלץ)

```powershell
# הרץ את הסקריפט
python scripts/setup_runner_on_slave_laptop.py
```

הסקריפט יבקש ממך:
1. SSH username
2. Authentication method (Password או SSH Key)
3. Registration token מ-GitHub
4. Installation path (default: `C:\actions-runner` עבור Windows או `/opt/actions-runner` עבור Linux)

### אפשרות 2: PowerShell Script

```powershell
.\scripts\setup_runner_on_slave_laptop.ps1 `
    -SlaveIP "10.50.0.36" `
    -SSHUser "your_username" `
    -RegistrationToken "YOUR_TOKEN_FROM_GITHUB"
```

---

## 📝 שלב 4: הגדרה ידנית (אם הסקריפטים לא עובדים)

### Windows:

```powershell
# התחבר ל-slave laptop
ssh user@10.50.0.36

# צור תיקייה
mkdir C:\actions-runner
cd C:\actions-runner

# הורד runner
Invoke-WebRequest -Uri https://github.com/actions/runner/releases/latest/download/actions-runner-win-x64-2.311.0.zip -OutFile actions-runner.zip

# חלץ
Expand-Archive -Path actions-runner.zip -DestinationPath . -Force
Remove-Item actions-runner.zip

# הגדר runner
.\config.cmd --url https://github.com/PrismaPhotonics/panda-backend-api-tests --token YOUR_TOKEN --name slave-laptop-runner --labels "self-hosted,Windows,slave-laptop" --work "_work" --replace

# התקן כשירות
.\svc.cmd install
.\svc.cmd start

# בדוק סטטוס
.\svc.cmd status
```

### Linux:

```bash
# התחבר ל-slave laptop
ssh user@10.50.0.36

# צור תיקייה
sudo mkdir -p /opt/actions-runner
cd /opt/actions-runner

# הורד runner
curl -L -o actions-runner.tar.gz https://github.com/actions/runner/releases/latest/download/actions-runner-linux-x64-2.311.0.tar.gz

# חלץ
tar xzf actions-runner.tar.gz
rm actions-runner.tar.gz

# הגדר runner
sudo ./config.sh --url https://github.com/PrismaPhotonics/panda-backend-api-tests --token YOUR_TOKEN --name slave-laptop-runner --labels "self-hosted,Linux,slave-laptop" --work "_work" --replace

# התקן כשירות
sudo ./svc.sh install
sudo ./svc.sh start

# בדוק סטטוס
sudo ./svc.sh status
```

---

## ✅ שלב 5: וידוא שה-Runner פעיל

1. **בדוק ב-GitHub:**
   ```
   https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
   ```
   
   אתה אמור לראות את ה-runner עם סטטוס **"Online"** (ירוק)

2. **בדוק על המכונה:**
   ```powershell
   # Windows
   ssh user@10.50.0.36
   cd C:\actions-runner
   .\svc.cmd status
   
   # Linux
   ssh user@10.50.0.36
   cd /opt/actions-runner
   sudo ./svc.sh status
   ```

---

## 🔍 פתרון בעיות

### Runner לא מופיע ב-GitHub:

1. **בדוק שה-token תקף:**
   - ה-token תקף ל-1 שעה בלבד
   - קבל token חדש מ-GitHub

2. **בדוק חיבור לאינטרנט:**
   ```powershell
   # על ה-slave laptop
   Test-NetConnection github.com -Port 443
   ```

3. **בדוק לוגים:**
   ```powershell
   # Windows
   cd C:\actions-runner
   Get-Content _diag\Runner_*.log -Tail 50
   
   # Linux
   cd /opt/actions-runner
   tail -50 _diag/Runner_*.log
   ```

### Runner לא מתחבר:

1. **בדוק firewall:**
   - ודא שה-slave laptop יכול לגשת ל-`github.com:443`
   - ודא שה-slave laptop יכול לגשת ל-`api.github.com:443`

2. **בדוק proxy settings:**
   - אם יש proxy, הגדר אותו ב-runner config

### Runner לא מריץ jobs:

1. **בדוק labels:**
   - ודא שה-workflow משתמש ב-label הנכון (`self-hosted` או `slave-laptop`)

2. **בדוק permissions:**
   - ודא שה-runner יש לו הרשאות להריץ את ה-workflow

---

## 📊 שימוש ב-Runner ב-Workflows

כדי להשתמש ב-runner הזה ב-workflow, הוסף:

```yaml
jobs:
  test:
    runs-on: self-hosted  # או slave-laptop אם הגדרת label ספציפי
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: pytest
```

או עם label ספציפי:

```yaml
jobs:
  test:
    runs-on: [self-hosted, slave-laptop]
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: pytest
```

---

## 🔄 עדכון Runner

כדי לעדכן את ה-runner לגרסה חדשה:

```powershell
# Windows
cd C:\actions-runner
.\svc.cmd stop
.\svc.cmd uninstall
# הורד גרסה חדשה והתקן מחדש

# Linux
cd /opt/actions-runner
sudo ./svc.sh stop
sudo ./svc.sh uninstall
# הורד גרסה חדשה והתקן מחדש
```

---

## 📞 תמיכה

אם יש בעיות:
1. בדוק את הלוגים (ראה "פתרון בעיות")
2. ודא שה-slave laptop מחובר לרשת
3. ודא שה-runner יכול לגשת ל-GitHub

---

## 📚 קישורים שימושיים

- [GitHub Actions Runner Documentation](https://docs.github.com/en/actions/hosting-your-own-runners)
- [Self-Hosted Runner Setup Guide](https://docs.github.com/en/actions/hosting-your-own-runners/adding-self-hosted-runners)
- [Runner Configuration Options](https://docs.github.com/en/actions/hosting-your-own-runners/configuring-the-self-hosted-runner-application-as-a-service)

