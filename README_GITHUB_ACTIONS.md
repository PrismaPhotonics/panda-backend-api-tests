# GitHub Actions - Quick Start Guide

**Repository:** https://github.com/PrismaPhotonics/panda-backend-api-tests  
**Actions:** https://github.com/PrismaPhotonics/panda-backend-api-tests/actions

---

## 🚀 הרצה לוקלית

### Windows
```powershell
# התקן Act
choco install act-cli

# הרץ smoke tests
.\scripts\run_workflow_locally.ps1 -WorkflowName smoke-tests
```

### Linux/macOS
```bash
# התקן Act
brew install act  # macOS
# או
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash  # Linux

# הרץ smoke tests
chmod +x scripts/run_workflow_locally.sh
./scripts/run_workflow_locally.sh smoke-tests
```

---

## 🖥️ הגדרת Self-Hosted Runner במעבדה

### Windows
```powershell
# עם URL מפורש
.\scripts\setup_self_hosted_runner.ps1 -RepoUrl "https://github.com/PrismaPhotonics/panda-backend-api-tests"

# או ללא URL (ישתמש ב-default)
.\scripts\setup_self_hosted_runner.ps1
```

### Linux
```bash
chmod +x scripts/setup_self_hosted_runner.sh

# עם URL מפורש
./scripts/setup_self_hosted_runner.sh https://github.com/PrismaPhotonics/panda-backend-api-tests

# או ללא URL (ישתמש ב-default)
./scripts/setup_self_hosted_runner.sh
```

---

## 📚 תיעוד מלא

ראה: [`docs/07_infrastructure/github_actions_local_and_self_hosted.md`](docs/07_infrastructure/github_actions_local_and_self_hosted.md)

