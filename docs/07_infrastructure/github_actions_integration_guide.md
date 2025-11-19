# מדריך אינטגרציה - GitHub Actions עם be_focus_server_tests

**תאריך:** 2025-11-19  
**Repository:** https://github.com/PrismaPhotonics/panda-backend-api-tests

---

## 🎯 מטרה

לחבר את הבדיקות המקומיות (`be_focus_server_tests`) ל-GitHub Actions של ה-repository הקיים.

---

## 📋 מבנה הפרויקט

```
focus_server_automation/                    # פרויקט מקומי
├── be_focus_server_tests/                # הבדיקות המקומיות
│   ├── integration/
│   ├── infrastructure/
│   ├── load/
│   └── ...
└── .github/
    └── workflows/                         # GitHub Actions workflows
        ├── smoke-tests.yml                # ✅ חדש - Smoke tests
        ├── regression-tests.yml           # ✅ חדש - Regression tests
        ├── nightly-tests.yml              # ✅ חדש - Nightly tests
        ├── backend-tests.yml             # קיים - Backend tests
        ├── contract-tests.yml            # קיים - Contract tests
        └── load-tests.yml                # קיים - Load tests
```

---

## ✅ מה כבר קיים

### Workflows קיימים
1. **backend-tests.yml** - מריץ `be_focus_server_tests/` ✅
2. **contract-tests.yml** - מריץ contract tests
3. **load-tests.yml** - מריץ load tests

### Workflows חדשים שנוספו
1. **smoke-tests.yml** - Smoke tests עם תמיכה ב-self-hosted runners ✅
2. **regression-tests.yml** - Regression tests עם תמיכה ב-self-hosted runners ✅
3. **nightly-tests.yml** - Nightly tests עם תמיכה ב-self-hosted runners ✅

---

## 🚀 שימוש

### דרך GitHub UI

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
2. בחר workflow (למשל: "Smoke Tests")
3. לחץ על "Run workflow"
4. בחר:
   - **Branch:** `main` (או branch אחר)
   - **Runner:** `self-hosted` (או `github-hosted`)
5. לחץ על "Run workflow"

### דרך API

```bash
curl -X POST \
  -H "Authorization: token YOUR_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/PrismaPhotonics/panda-backend-api-tests/actions/workflows/smoke-tests.yml/dispatches \
  -d '{
    "ref": "main",
    "inputs": {
      "runner": "self-hosted"
    }
  }'
```

---

## 🖥️ הגדרת Self-Hosted Runner במעבדה

### Windows

```powershell
# 1. הורד והתקן runner
.\scripts\setup_self_hosted_runner.ps1 -RepoUrl "https://github.com/PrismaPhotonics/panda-backend-api-tests"

# 2. בדוק סטטוס
cd C:\actions-runner
.\svc.cmd status
```

### Linux

```bash
# 1. הורד והתקן runner
chmod +x scripts/setup_self_hosted_runner.sh
./scripts/setup_self_hosted_runner.sh https://github.com/PrismaPhotonics/panda-backend-api-tests

# 2. בדוק סטטוס
cd actions-runner
sudo ./svc.sh status
```

---

## 📊 Workflows Overview

| Workflow | Marker | Runner | Timeout | Max Failures |
|----------|--------|--------|---------|--------------|
| **smoke-tests.yml** | `smoke` | `self-hosted` / `ubuntu-latest` | 10 min | 5 |
| **regression-tests.yml** | `regression and not slow and not nightly` | `self-hosted` / `ubuntu-latest` | 60 min | 10 |
| **nightly-tests.yml** | `smoke or regression or nightly` | `self-hosted` / `ubuntu-latest` | 120 min | 20 |
| **backend-tests.yml** | `not load and not stress` | `ubuntu-latest` | 60 min | 10 |
| **contract-tests.yml** | Contract tests | `ubuntu-latest` | 30 min | - |
| **load-tests.yml** | `load or stress` | `ubuntu-latest` | 120 min | 5 |

---

## 🔧 תצורה

### Secrets ב-GitHub

הוסף את ה-secrets הבאים ב-GitHub Repository → Settings → Secrets → Actions:

- `FOCUS_BASE_URL` - כתובת Focus Server
- `FOCUS_API_PREFIX` - Prefix ל-API (default: `/focus-server`)
- `VERIFY_SSL` - האם לאמת SSL (default: `false`)

### Environment Variables ל-Self-Hosted Runner

עבור self-hosted runners, הוסף environment variables:

#### Windows
```powershell
[System.Environment]::SetEnvironmentVariable("FOCUS_BASE_URL", "https://your-server", "Machine")
[System.Environment]::SetEnvironmentVariable("FOCUS_API_PREFIX", "/focus-server", "Machine")
[System.Environment]::SetEnvironmentVariable("VERIFY_SSL", "false", "Machine")
```

#### Linux
```bash
sudo tee -a /etc/environment << EOF
FOCUS_BASE_URL=https://your-server
FOCUS_API_PREFIX=/focus-server
VERIFY_SSL=false
EOF
```

---

## 📝 בדיקות

### בדיקת Workflow לוקלית

```powershell
# Windows
.\scripts\run_workflow_locally.ps1 -WorkflowName smoke-tests

# Linux
./scripts/run_workflow_locally.sh smoke-tests
```

### בדיקת Self-Hosted Runner

1. ודא שה-runner online ב-GitHub
2. הרץ workflow עם `runner: self-hosted`
3. בדוק את ה-logs ב-GitHub Actions

---

## 🔗 קישורים

- **Repository:** https://github.com/PrismaPhotonics/panda-backend-api-tests
- **Actions:** https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
- **Runners:** https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners

---

**עודכן לאחרונה:** 2025-11-19

