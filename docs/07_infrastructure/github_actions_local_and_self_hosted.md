# הרצת GitHub Actions לוקלית ו-Self-Hosted Runners

**תאריך:** 2025-11-19  
**מטרה:** להריץ GitHub Actions מהלוקלי ולהגדיר self-hosted runner במעבדה

---

## 📋 תוכן עניינים

1. [הרצה לוקלית עם Act](#הרצה-לוקלית-עם-act)
2. [הגדרת Self-Hosted Runner](#הגדרת-self-hosted-runner)
3. [שימוש ב-Self-Hosted Runner](#שימוש-ב-self-hosted-runner)
4. [פתרון בעיות](#פתרון-בעיות)

---

## 🚀 הרצה לוקלית עם Act

### התקנת Act

#### Windows (Chocolatey)
```powershell
choco install act-cli
```

#### Windows (Manual)
1. הורד מ: https://github.com/nektos/act/releases
2. חלץ את `act.exe` לתיקיית PATH

#### macOS
```bash
brew install act
```

#### Linux
```bash
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

---

### הגדרת Secrets לוקלית

צור קובץ `.secrets` בשורש הפרויקט:

```bash
# GitHub Secrets for local testing
FOCUS_BASE_URL=https://your-focus-server-url
FOCUS_API_PREFIX=/focus-server
VERIFY_SSL=false
```

**⚠️ חשוב:** הוסף את `.secrets` ל-`.gitignore`!

---

### הרצת Workflow לוקלית

#### Windows (PowerShell)
```powershell
# הרצת smoke tests
.\scripts\run_workflow_locally.ps1 -WorkflowName smoke-tests

# הרצת regression tests
.\scripts\run_workflow_locally.ps1 -WorkflowName regression-tests

# הרצת nightly tests
.\scripts\run_workflow_locally.ps1 -WorkflowName nightly-tests
```

#### Linux/macOS (Bash)
```bash
# הרצת smoke tests
chmod +x scripts/run_workflow_locally.sh
./scripts/run_workflow_locally.sh smoke-tests

# הרצת regression tests
./scripts/run_workflow_locally.sh regression-tests

# הרצת nightly tests
./scripts/run_workflow_locally.sh nightly-tests
```

#### שימוש ישיר ב-Act
```bash
# הרצת workflow ספציפי
act workflow_dispatch \
    --workflows .github/workflows/smoke-tests.yml \
    --secret-file .secrets \
    --env FOCUS_ENV=local

# הרצת workflow עם inputs
act workflow_dispatch \
    --workflows .github/workflows/smoke-tests.yml \
    --secret-file .secrets \
    --input runner=self-hosted
```

---

## 🖥️ הגדרת Self-Hosted Runner

### שלב 1: הורדת Runner

1. לך ל-GitHub Repository → Settings → Actions → Runners
2. לחץ על "New self-hosted runner"
3. בחר את מערכת ההפעלה (Windows/Linux/macOS)
4. הורד את ה-runner

#### Windows
```powershell
# הורד את actions-runner-win-x64-*.zip
# חלץ לתיקייה (למשל: C:\actions-runner)
```

#### Linux
```bash
# הורד את actions-runner-linux-x64-*.tar.gz
mkdir actions-runner && cd actions-runner
tar xzf ../actions-runner-linux-x64-*.tar.gz
```

---

### שלב 2: הגדרת Runner

#### Windows
```powershell
cd C:\actions-runner

# הגדר את ה-runner
.\config.cmd --url https://github.com/YOUR_ORG/YOUR_REPO --token YOUR_TOKEN

# אפשרויות:
# - Runner name: lab-windows-runner-01
# - Labels: self-hosted, windows, lab
# - Work folder: C:\actions-runner\_work
```

#### Linux
```bash
cd actions-runner

# הגדר את ה-runner
./config.sh --url https://github.com/YOUR_ORG/YOUR_REPO --token YOUR_TOKEN

# אפשרויות:
# - Runner name: lab-linux-runner-01
# - Labels: self-hosted, linux, lab
# - Work folder: ./_work
```

---

### שלב 3: התקנת Runner כשירות

#### Windows (כשירות)
```powershell
cd C:\actions-runner

# התקן כשירות
.\svc.cmd install

# התחל את השירות
.\svc.cmd start

# בדוק סטטוס
.\svc.cmd status
```

#### Linux (systemd)
```bash
cd actions-runner

# התקן כשירות
sudo ./svc.sh install

# התחל את השירות
sudo ./svc.sh start

# בדוק סטטוס
sudo ./svc.sh status
```

---

### שלב 4: הגדרת Runner Labels

לאחר ההתקנה, עדכן את ה-labels ב-GitHub:

1. לך ל-Settings → Actions → Runners
2. לחץ על ה-runner
3. לחץ על "Edit"
4. הוסף labels:
   - `self-hosted`
   - `windows` (או `linux`)
   - `lab`
   - `lab-windows-01` (שם ייחודי)

---

## 🎯 שימוש ב-Self-Hosted Runner

### עדכון Workflows

ה-workflows כבר תומכים ב-self-hosted runners! פשוט בחר ב-runner בעת ההרצה:

#### דרך GitHub UI
1. לך ל-Actions → Workflow
2. לחץ על "Run workflow"
3. בחר ב-"Use workflow from" → Branch
4. בחר ב-"Runner" → `self-hosted`
5. לחץ על "Run workflow"

#### דרך API
```bash
curl -X POST \
  -H "Authorization: token YOUR_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/YOUR_ORG/YOUR_REPO/actions/workflows/smoke-tests.yml/dispatches \
  -d '{
    "ref": "main",
    "inputs": {
      "runner": "self-hosted"
    }
  }'
```

---

## 🔧 פתרון בעיות

### בעיה: Runner לא מתחבר ל-GitHub

**פתרון:**
1. בדוק חיבור לאינטרנט
2. בדוק firewall/proxy
3. בדוק שה-token תקף
4. הרץ מחדש את `config.sh`/`config.cmd`

---

### בעיה: Runner לא מזהה Jobs

**פתרון:**
1. בדוק שה-runner online ב-GitHub
2. בדוק שה-labels נכונים
3. בדוק שה-workflow משתמש ב-`runs-on: self-hosted`

---

### בעיה: Secrets לא זמינים

**פתרון:**
1. בדוק שה-secrets מוגדרים ב-GitHub
2. עבור self-hosted runners, הוסף את ה-secrets כ-environment variables:
   ```bash
   # Linux
   export FOCUS_BASE_URL="https://your-server"
   
   # Windows
   $env:FOCUS_BASE_URL="https://your-server"
   ```

---

### בעיה: Docker לא עובד ב-Act

**פתרון:**
1. התקן Docker Desktop
2. הרץ Act עם `--container-architecture linux/amd64`
3. או השתמש ב-`--no-container` (לא מומלץ)

---

## 📝 Best Practices

1. **Security:**
   - אל תעלה את `.secrets` ל-Git
   - השתמש ב-GitHub Secrets עבור self-hosted runners
   - הגבל גישה ל-runner רק למשתמשים מורשים

2. **Performance:**
   - השתמש ב-self-hosted runners רק כשיש צורך בגישה לרשת פנימית
   - השתמש ב-GitHub-hosted runners לבדיקות רגילות

3. **Maintenance:**
   - עדכן את ה-runner באופן קבוע
   - בדוק את ה-logs באופן קבוע
   - הגדר monitoring ל-runner

---

## 🔗 קישורים שימושיים

- [Act Documentation](https://github.com/nektos/act)
- [GitHub Self-Hosted Runners](https://docs.github.com/en/actions/hosting-your-own-runners)
- [GitHub Actions Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

---

**עודכן לאחרונה:** 2025-11-19

