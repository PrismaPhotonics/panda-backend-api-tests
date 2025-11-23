# דחיפת Workflows ל-GitHub

**תאריך:** 2025-11-19

---

## 🎯 מטרה

להוסיף את ה-workflows החדשים ל-GitHub כדי שיופיעו ב-GitHub Actions.

---

## ✅ מה צריך לדחוף

### Workflows חדשים:
- ✅ `.github/workflows/smoke-tests.yml`
- ✅ `.github/workflows/regression-tests.yml`
- ✅ `.github/workflows/nightly-tests.yml`

### Workflows שעודכנו:
- ✅ `.github/workflows/backend-tests.yml`
- ✅ `.github/workflows/load-tests.yml`

### קבצים נוספים:
- ✅ `.github/workflows/README.md`
- ✅ `scripts/run_workflow_locally.ps1`
- ✅ `scripts/run_workflow_locally.sh`
- ✅ `scripts/setup_self_hosted_runner.ps1`
- ✅ `scripts/setup_self_hosted_runner.sh`
- ✅ `README_GITHUB_ACTIONS.md`
- ✅ `.gitignore` (עודכן עם `.secrets`)

---

## 🚀 הוראות דחיפה

### שלב 1: הוסף את הקבצים ל-Git

```powershell
# הוסף את כל ה-workflows החדשים
git add .github/workflows/smoke-tests.yml
git add .github/workflows/regression-tests.yml
git add .github/workflows/nightly-tests.yml

# הוסף את ה-workflows שעודכנו
git add .github/workflows/backend-tests.yml
git add .github/workflows/load-tests.yml
git add .github/workflows/README.md

# הוסף את הסקריפטים
git add scripts/run_workflow_locally.ps1
git add scripts/run_workflow_locally.sh
git add scripts/setup_self_hosted_runner.ps1
git add scripts/setup_self_hosted_runner.sh

# הוסף את התיעוד
git add README_GITHUB_ACTIONS.md
git add docs/07_infrastructure/github_actions_*.md

# הוסף את השינויים ב-.gitignore
git add .gitignore
```

### שלב 2: Commit

```powershell
git commit -m "Add new test suite workflows (smoke, regression, nightly) with self-hosted runner support"
```

### שלב 3: Push ל-GitHub

```powershell
git push origin chore/add-roy-tests
```

או אם אתה רוצה לדחוף ל-main:

```powershell
git checkout main
git merge chore/add-roy-tests
git push origin main
```

---

## ✅ אחרי הדחיפה

לאחר הדחיפה, ה-workflows יופיעו ב-GitHub Actions:

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
2. תראה את ה-workflows החדשים:
   - ✅ Smoke Tests
   - ✅ Regression Tests
   - ✅ Nightly Full Suite

---

## 🔍 בדיקה

לאחר הדחיפה, בדוק:

1. ✅ ה-workflows מופיעים ב-GitHub Actions
2. ✅ אפשר להריץ אותם דרך "Run workflow"
3. ✅ יש אפשרות לבחור בין `self-hosted` ל-`github-hosted`

---

**עודכן לאחרונה:** 2025-11-19

