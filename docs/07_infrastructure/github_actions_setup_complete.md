# הגדרת GitHub Actions - מדריך מלא

**תאריך:** 2025-11-19  
**Repository:** https://github.com/PrismaPhotonics/panda-backend-api-tests

---

## ✅ מה הושלם

### 1. Workflows עם תמיכה ב-Self-Hosted Runners ✅

כל ה-workflows עודכנו לתמוך ב-self-hosted runners:

- ✅ `smoke-tests.yml` - Smoke tests
- ✅ `regression-tests.yml` - Regression tests  
- ✅ `nightly-tests.yml` - Nightly tests
- ✅ `backend-tests.yml` - Backend tests (קיים, עודכן)
- ✅ `load-tests.yml` - Load tests (קיים, עודכן)

### 2. סקריפטים להגדרה ✅

- ✅ `scripts/setup_self_hosted_runner.ps1` - Windows (עם default repository)
- ✅ `scripts/setup_self_hosted_runner.sh` - Linux (עם default repository)
- ✅ `scripts/run_workflow_locally.ps1` - הרצה לוקלית Windows
- ✅ `scripts/run_workflow_locally.sh` - הרצה לוקלית Linux

### 3. תיעוד ✅

- ✅ `docs/07_infrastructure/github_actions_local_and_self_hosted.md` - מדריך מפורט
- ✅ `docs/07_infrastructure/github_actions_integration_guide.md` - מדריך אינטגרציה
- ✅ `README_GITHUB_ACTIONS.md` - Quick Start Guide

---

## 🎯 שימוש מהיר

### הרצת Workflow דרך GitHub

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
2. בחר workflow (למשל: "Smoke Tests")
3. לחץ על "Run workflow"
4. בחר:
   - **Branch:** `main`
   - **Runner:** `self-hosted` (או `github-hosted`)
5. לחץ על "Run workflow"

### הגדרת Self-Hosted Runner במעבדה

#### Windows
```powershell
# פשוט הרץ את הסקריפט (בלי פרמטרים - ישתמש ב-default)
.\scripts\setup_self_hosted_runner.ps1
```

#### Linux
```bash
chmod +x scripts/setup_self_hosted_runner.sh
./scripts/setup_self_hosted_runner.sh
```

---

## 📊 Workflows Overview

| Workflow | מה הוא מריץ | Marker | Runner Options |
|----------|-------------|--------|----------------|
| **smoke-tests.yml** | בדיקות smoke מהירות | `smoke` | `self-hosted` / `ubuntu-latest` |
| **regression-tests.yml** | בדיקות regression | `regression and not slow and not nightly` | `self-hosted` / `ubuntu-latest` |
| **nightly-tests.yml** | כל הבדיקות | `smoke or regression or nightly` | `self-hosted` / `ubuntu-latest` |
| **backend-tests.yml** | בדיקות backend | `not load and not stress` | `self-hosted` / `ubuntu-latest` |
| **load-tests.yml** | בדיקות load/stress | `load or stress` | `self-hosted` / `ubuntu-latest` |
| **contract-tests.yml** | Contract tests | - | `ubuntu-latest` |

---

## 🔧 תצורה

### Secrets ב-GitHub

הוסף ב-GitHub → Settings → Secrets → Actions:

- `FOCUS_BASE_URL` - כתובת Focus Server
- `FOCUS_API_PREFIX` - Prefix ל-API (default: `/focus-server`)
- `VERIFY_SSL` - האם לאמת SSL (default: `false`)

### Environment Variables ל-Self-Hosted Runner

עבור self-hosted runners, הוסף environment variables במחשב במעבדה:

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

## ✅ בדיקות

### 1. בדיקת Workflow לוקלית
```powershell
# Windows
.\scripts\run_workflow_locally.ps1 -WorkflowName smoke-tests
```

### 2. בדיקת Self-Hosted Runner
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

