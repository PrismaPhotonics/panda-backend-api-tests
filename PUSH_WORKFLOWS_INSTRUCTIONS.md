# הוראות דחיפת Workflows ל-GitHub

**תאריך:** 2025-11-19

---

## ✅ מה כבר הוסף ל-Git

כל הקבצים הבאים כבר נוספו ל-Git staging:

### Workflows חדשים:
- ✅ `.github/workflows/smoke-tests.yml`
- ✅ `.github/workflows/regression-tests.yml`
- ✅ `.github/workflows/nightly-tests.yml`

### Workflows שעודכנו:
- ✅ `.github/workflows/backend-tests.yml`
- ✅ `.github/workflows/load-tests.yml`
- ✅ `.github/workflows/README.md`

### סקריפטים:
- ✅ `scripts/run_workflow_locally.ps1`
- ✅ `scripts/run_workflow_locally.sh`
- ✅ `scripts/setup_self_hosted_runner.ps1`
- ✅ `scripts/setup_self_hosted_runner.sh`

### תיעוד:
- ✅ `README_GITHUB_ACTIONS.md`
- ✅ `docs/07_infrastructure/github_actions_*.md`
- ✅ `.gitignore` (עודכן)

---

## 🚀 שלבים לדחיפה

### שלב 1: Commit

```powershell
git commit -m "Add new test suite workflows (smoke, regression, nightly) with self-hosted runner support

- Add smoke-tests.yml workflow for fast critical tests
- Add regression-tests.yml workflow for full integration tests
- Add nightly-tests.yml workflow for complete test suite
- Update backend-tests.yml and load-tests.yml with self-hosted runner support
- Add scripts for local workflow execution and self-hosted runner setup
- Add comprehensive documentation for GitHub Actions integration"
```

### שלב 2: Push ל-GitHub

```powershell
# דחוף ל-branch הנוכחי
git push origin chore/add-roy-tests
```

או אם אתה רוצה לדחוף ישירות ל-main:

```powershell
# עבור ל-main
git checkout main

# Merge את השינויים
git merge chore/add-roy-tests

# דחוף ל-main
git push origin main
```

---

## ✅ אחרי הדחיפה

לאחר הדחיפה, ה-workflows יופיעו ב-GitHub Actions:

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
2. תראה את ה-workflows החדשים:
   - ✅ **Smoke Tests** - חדש!
   - ✅ **Regression Tests** - חדש!
   - ✅ **Nightly Full Suite** - חדש!

3. לחץ על כל workflow כדי לראות את הפרטים
4. לחץ על "Run workflow" כדי להריץ אותו

---

## 🔍 בדיקה

לאחר הדחיפה, בדוק:

1. ✅ ה-workflows מופיעים ב-GitHub Actions
2. ✅ אפשר להריץ אותם דרך "Run workflow"
3. ✅ יש אפשרות לבחור בין `self-hosted` ל-`github-hosted` ב-workflow_dispatch

---

## 📝 הערות

- ה-workflows החדשים יתחילו לרוץ אוטומטית על push/PR (לפי ההגדרות)
- ה-workflows הקיימים (`backend-tests.yml`, `load-tests.yml`) ימשיכו לעבוד כרגיל
- ה-workflows החדשים מוסיפים אפשרות לבחור runner דרך `workflow_dispatch`

---

**עודכן לאחרונה:** 2025-11-19

