# GitHub Actions Workflows

סקירה כללית של ה-workflows הזמינים בפרויקט.

## 📋 Workflows זמינים

### 1. Smoke Tests (`smoke-tests.yml`)
**מטרה:** בדיקות מהירות וקריטיות  
**Runner:** Self-hosted Windows  
**זמן ריצה:** ~5-15 דקות  
**תדירות:** כל push/PR  
**מרקרים:** `smoke`

**Triggers:**
- Push ל-`main`, `develop`, `master`, `chore/add-roy-tests`
- Pull requests ל-`main`
- Manual (`workflow_dispatch`)

**מה זה מריץ:**
```bash
pytest be_focus_server_tests/ -m "smoke" -v --maxfail=10
```

---

### 2. Regression Tests (`regression-tests.yml`)
**מטרה:** בדיקות אינטגרציה מלאות  
**Runner:** Self-hosted Windows  
**זמן ריצה:** ~30-60 דקות  
**תדירות:** לפני merge ל-main, כל לילה  
**מרקרים:** `regression` (ללא `slow` ו-`nightly`)

**Triggers:**
- Push ל-`main`, `develop`, `master`
- Pull requests ל-`main`
- Scheduled: כל לילה ב-23:00 UTC
- Manual (`workflow_dispatch`)

**מה זה מריץ:**
```bash
pytest be_focus_server_tests/ -m "regression and not slow and not nightly" -v
```

---

### 3. Load and Performance Tests (`load-performance-tests.yml`)
**מטרה:** בדיקות עומס וביצועים בלבד  
**Runner:** Self-hosted Windows  
**זמן ריצה:** ~60-120 דקות  
**תדירות:** כל לילה, ידנית  
**מרקרים:** `load` או `performance`

**Triggers:**
- Scheduled: כל לילה ב-02:00 UTC
- Manual (`workflow_dispatch`)

**מה זה מריץ:**
```bash
pytest be_focus_server_tests/ -m "load or performance" --monitor-pods -v
```

---

## 🗑️ Workflows שנמחקו

העבודה הבאים נמחקו כחלק מהניקוי:
- `focus-backend-tests.yml` - הוחלף ב-3 workflows נפרדים
- `backend-tests.yml` - legacy
- `backend-tests-github.yml` - legacy
- `backend-tests-lab.yml` - legacy
- `nightly-tests.yml` - הוחלף ב-`regression-tests.yml` ו-`load-performance-tests.yml`

---

## 🚀 הרצת Workflows

### דרך GitHub UI
1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
2. בחר את ה-workflow הרצוי
3. לחץ על **Run workflow**
4. בחר branch ולחץ **Run workflow**

### דרך Git Push
```bash
# Smoke tests ירוצו אוטומטית על כל push
git push origin feature/my-feature

# Regression tests ירוצו אוטומטית על push ל-main
git push origin main
```

---

## 📊 Test Suites

### Smoke Tests
- **מספר בדיקות:** ~30-50 בדיקות
- **זמן ריצה:** < 15 דקות
- **תדירות:** כל commit/PR
- **מטרה:** וידוא שהמערכת עובדת

### Regression Tests
- **מספר בדיקות:** ~150-200 בדיקות
- **זמן ריצה:** ~30-60 דקות
- **תדירות:** לפני merge, כל לילה
- **מטרה:** וידוא שלא נשבר דבר

### Load and Performance Tests
- **מספר בדיקות:** ~20-30 בדיקות
- **זמן ריצה:** ~60-120 דקות
- **תדירות:** כל לילה, ידנית
- **מטרה:** בדיקות עומס וביצועים

---

## 🔧 תצורה

כל ה-workflows משתמשים ב:
- **Python:** 3.12
- **Runner:** Self-hosted Windows (`self-hosted`, `Windows`)
- **Environment:** `new_production`
- **Dependencies:** `requirements.txt` עם `--use-deprecated=legacy-resolver`

---

## 📝 Artifacts

כל workflow מייצר JUnit XML reports שנשמרים כ-artifacts:
- **Smoke Tests:** `smoke-test-reports` (שמירה: 7 ימים)
- **Regression Tests:** `regression-test-reports` (שמירה: 7 ימים)
- **Load/Performance Tests:** `load-performance-test-reports` (שמירה: 7 ימים)

---

## 🐛 Troubleshooting

### Workflow לא רץ
- ודא שה-runner פעיל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
- בדוק שה-runner יש לו את ה-labels הנכונים: `self-hosted`, `Windows`

### Tests נכשלים
- בדוק את ה-logs ב-GitHub Actions
- הורד את ה-artifacts לניתוח מפורט
- ודא שה-Focus Server זמין ופועל

### Dependency installation נכשל
- ה-workflow משתמש ב-`--use-deprecated=legacy-resolver` כדי למנוע `resolution-too-deep` errors
- אם עדיין יש בעיות, בדוק את `requirements.txt`

---

## 📚 קישורים שימושיים

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pytest Documentation](https://docs.pytest.org/)
- [Test Suites Guide](../../be_focus_server_tests/TEST_SUITES.md)
