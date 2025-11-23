# שלבים הבאים - GitHub Actions

**תאריך:** 2025-11-19  
**סטטוס:** ✅ Workflows נדחפו ל-GitHub

---

## ✅ מה כבר בוצע

1. ✅ Workflows חדשים נוצרו:
   - `smoke-tests.yml`
   - `regression-tests.yml`
   - `nightly-tests.yml`

2. ✅ Workflows קיימים עודכנו:
   - `backend-tests.yml` - תמיכה ב-self-hosted runners
   - `load-tests.yml` - תמיכה ב-self-hosted runners

3. ✅ כל הקבצים נדחפו ל-GitHub:
   - Commit: `0db4788`
   - Branch: `chore/add-roy-tests`

---

## 🎯 מה לעשות עכשיו

### שלב 1: בדוק ב-GitHub Actions

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
2. בדוק שה-workflows החדשים מופיעים:
   - ✅ **Smoke Tests**
   - ✅ **Regression Tests**
   - ✅ **Nightly Full Suite**

### שלב 2: הרץ Workflow לבדיקה

1. לחץ על "Smoke Tests"
2. לחץ על "Run workflow" (מימין למעלה)
3. בחר:
   - **Use workflow from:** `chore/add-roy-tests` (או `main`)
   - **Runner:** `github-hosted` (לבדיקה ראשונית)
4. לחץ על "Run workflow"

### שלב 3: בדוק שהכל עובד

1. לחץ על ה-run שיצרת
2. בדוק שה-workflow רץ בהצלחה
3. בדוק שה-tests רצים

---

## 🖥️ הגדרת Self-Hosted Runner (לאחר בדיקה)

לאחר שבדקת שהכל עובד עם `github-hosted`, תוכל להגדיר self-hosted runner:

### במעבדה (Windows):

```powershell
# הרץ את הסקריפט (בלי פרמטרים - ישתמש ב-default repository)
.\scripts\setup_self_hosted_runner.ps1
```

### במעבדה (Linux):

```bash
chmod +x scripts/setup_self_hosted_runner.sh
./scripts/setup_self_hosted_runner.sh
```

---

## 📝 הערות חשובות

1. **Branch:** ה-workflows נדחפו ל-`chore/add-roy-tests`
   - כדי שירוצו על `main`, צריך לעשות merge ל-`main`
   - או להריץ אותם ידנית דרך `workflow_dispatch`

2. **Self-Hosted Runner:**
   - צריך להיות במעבדה עם גישה לרשת הפנימית
   - צריך גישה ל-GitHub (אינטרנט)
   - לא צריך VPN כי ה-runner רץ במעבדה

3. **Secrets:**
   - עבור `github-hosted` runners: הוסף secrets ב-GitHub
   - עבור `self-hosted` runners: הוסף environment variables במחשב

---

## 🔗 קישורים

- **Repository:** https://github.com/PrismaPhotonics/panda-backend-api-tests
- **Actions:** https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
- **Runners:** https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners

---

**עודכן לאחרונה:** 2025-11-19

