# מדריך סנכרון Xray ↔ GitHub Actions - מקצה לקצה
## Complete Xray ↔ GitHub Actions Integration Guide

**תאריך:** 2025-11-09  
**סטטוס:** ✅ מוכן לשימוש

---

## 🎯 מה המערכת עושה

1. ✅ **מריצה טסטים** לפי Test Plan ב-Xray
2. ✅ **יוצרת Test Execution** אוטומטית עם כל ריצה
3. ✅ **מקשרת ל-Test Plan** (PZ-14024 או אחר)
4. ✅ **מסמנת Environment** (Staging/Production)
5. ✅ **מוסיפה Revision** (Git SHA)
6. ✅ **מצרפת Evidence** (לוגים/סקרינשוטים)
7. ✅ **מעדכנת PR** עם סיכום וקישורים

---

## 📋 הגדרה חד-פעמית

### 1. GitHub Secrets

הוסף ב-GitHub → Settings → Secrets → Actions:

```
XRAY_CLIENT_ID=your_client_id
XRAY_CLIENT_SECRET=your_client_secret
```

**איך להשיג:**
1. היכנס ל-Xray Cloud Portal: https://xray.cloud.getxray.app/
2. נווט ל-Settings → API Keys
3. לחץ "Create API Key" או "Generate"
4. העתק את ה-Client ID ו-Client Secret
5. הוסף ל-GitHub Secrets (ראה מדריך מפורט: `HOW_TO_GET_XRAY_SECRETS.md`)

### 2. Test Plan ב-Xray

ודא שיש Test Plan ב-Xray (למשל: PZ-14024) עם טסטים מקושרים.

**ברירת מחדל:** `PZ-14024` (ניתן לשנות ב-workflow)

---

## 🚀 שימוש

### הרצה אוטומטית

המערכת רצה אוטומטית ב:
- ✅ **Push ל-main/develop** - ריצה אוטומטית
- ✅ **Pull Request** - ריצה אוטומטית + הערה ב-PR
- ✅ **לילה (2:00 AM)** - ריצה יומית
- ✅ **Manual trigger** - דרך GitHub Actions UI

### הרצה ידנית

1. היכנס ל-GitHub → Actions
2. בחר "Xray Full Integration - Test Execution"
3. לחץ "Run workflow"
4. בחר:
   - **Test Plan:** PZ-14024 (או אחר)
   - **Environment:** Staging/Production
   - **Run all tests:** false (להריץ רק מה-Test Plan)

---

## 📊 מה קורה בכל ריצה

### שלב 1: אימות Xray
```
✅ Authenticating with Xray Cloud...
✅ Authentication successful
```

### שלב 2: שליפת טסטים מ-Test Plan
```
Fetching tests from Test Plan: PZ-14024
Found 47 tests in Test Plan
```

### שלב 3: הרצת טסטים
```
Running tests from Test Plan: PZ-12345 or PZ-12346 or ...
pytest tests/ -v --junitxml=reports/junit.xml
```

### שלב 4: העלאת תוצאות ל-Xray
```
Uploading JUnit XML: reports/junit.xml
Linking to Test Plan: PZ-14024
Environments: Staging
Revision: abc1234
✅ Upload successful!
   Test Execution: PZ-EXE-123
```

### שלב 5: צירוף Evidence
```
Attaching evidence to PZ-EXE-123...
✅ Successfully attached error.log
✅ Successfully attached screenshot.png
✅ Evidence attachment complete
```

### שלב 6: עדכון PR (אם רלוונטי)
```
## 🧪 Test Execution Results
✅ Passed: 45
❌ Failed: 2
📊 Total: 47
[View Test Execution in Xray](...)
```

---

## 🔧 קונפיגורציה

### Environment Variables

ב-`.github/workflows/xray_full_integration.yml`:

```yaml
env:
  TEST_PLAN: PZ-14024  # ברירת מחדל
  TEST_ENV: Staging     # או Production לפי branch
  PROJECT_KEY: PZ
```

### Test Plan Filtering

המערכת מריצה רק טסטים מה-Test Plan. כדי להריץ הכל:

```yaml
RUN_ALL_TESTS: true
```

---

## 📁 קבצים שנוצרים

### בפרויקט:
- `reports/junit.xml` - תוצאות JUnit
- `reports/report.html` - דוח HTML
- `logs/` - לוגים
- `screenshots/` - סקרינשוטים

### ב-Xray:
- **Test Execution** חדש (PZ-EXE-XXX)
- **קישור ל-Test Plan**
- **Evidence** מצורף

---

## 🔍 פתרון בעיות

### בעיה: "No tests found in Test Plan"

**פתרון:**
1. בדוק שהת Plan קיים: `https://prismaphotonics.atlassian.net/browse/PZ-14024`
2. ודא שיש טסטים מקושרים ל-Test Plan
3. בדוק שה-Test Plan לא ריק

### בעיה: "Authentication failed"

**פתרון:**
1. בדוק שה-Secrets מוגדרים נכון ב-GitHub
2. ודא שה-Client ID/Secret תקינים ב-Xray
3. נסה ליצור מחדש API keys

### בעיה: "Test Execution not created"

**פתרון:**
1. בדוק את הלוגים ב-GitHub Actions
2. ודא שה-JUnit XML נוצר (`reports/junit.xml`)
3. בדוק שה-Test Plan key נכון

### בעיה: "Evidence not attached"

**פתרון:**
1. ודא שהתיקיות `logs/` ו-`screenshots/` קיימות
2. בדוק שגודל הקבצים < 10MB
3. בדוק שהת Test Execution נוצר לפני ניסיון הצירוף

---

## 📝 דוגמאות שימוש

### הרצה מקומית (ללא CI)

```bash
# 1. שליפת טסטים מ-Test Plan
export XRAY_CLIENT_ID=your_id
export XRAY_CLIENT_SECRET=your_secret
python scripts/xray/get_test_plan_tests.py --test-plan PZ-14024 --output testkeys.txt

# 2. הרצת טסטים
pytest tests/ -v --junitxml=reports/junit.xml

# 3. העלאת תוצאות
python scripts/xray_upload.py \
  --format junit \
  --test-plan PZ-14024 \
  --environment Staging \
  --revision $(git rev-parse HEAD)

# 4. צירוף Evidence
python scripts/xray/attach_evidence.py \
  --test-exec PZ-EXE-123 \
  --evidence logs/ \
  --evidence screenshots/
```

### עדכון Test Plan

```bash
# שנה את ה-Test Plan ב-workflow:
# env:
#   TEST_PLAN: PZ-XXXXX  # Test Plan החדש
```

---

## 🎨 Customization

### הוספת Environments נוספים

עדכן ב-workflow:

```yaml
environment:
  type: choice
  options:
    - Staging
    - Production
    - QA
    - Development
```

### שינוי Schedule

עדכן ב-workflow:

```yaml
schedule:
  - cron: '0 2 * * *'  # 2 AM Israel time
```

### הוספת Notifications

הוסף step ב-workflow:

```yaml
- name: Send Slack notification
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "Test Execution completed: ${{ steps.xray-upload.outputs.test_exec_key }}"
      }
```

---

## 📊 דוחות ותוצאות

### ב-Xray:
1. היכנס ל-Jira → Xray → Test Executions
2. מצא את ה-Test Execution שנוצר
3. ראה:
   - ✅ סטטוס כל טסט
   - 📋 קישור ל-Test Plan
   - 🔗 קישור ל-Build (GitHub Actions)
   - 📎 Evidence מצורף

### ב-GitHub:
1. היכנס ל-Actions → Workflow runs
2. ראה את התוצאות
3. הורד artifacts (לוגים/דוחות)

### ב-PR:
- הערה אוטומטית עם סיכום
- קישורים ל-Xray ול-Build

---

## 🔗 קישורים שימושיים

- **Xray Cloud API:** https://xray.cloud.getxray.app/api/v2
- **GraphQL API:** https://xray.cloud.getxray.app/api/v2/graphql
- **Jira Base URL:** https://prismaphotonics.atlassian.net
- **Test Plan Example:** https://prismaphotonics.atlassian.net/browse/PZ-14024

---

## ✅ Checklist לפני שימוש

- [ ] GitHub Secrets מוגדרים (XRAY_CLIENT_ID, XRAY_CLIENT_SECRET)
- [ ] Test Plan קיים ב-Xray (PZ-14024 או אחר)
- [ ] טסטים מקושרים ל-Test Plan
- [ ] כל הטסטים מסומנים עם `@pytest.mark.xray("PZ-XXXXX")`
- [ ] Workflow מופעל (push/PR/schedule)

---

## 🎉 סיכום

המערכת מוכנה לשימוש! כל ריצה:
1. ✅ מריצה טסטים מה-Test Plan
2. ✅ יוצרת Test Execution ב-Xray
3. ✅ מקשרת ל-Test Plan, Environment, Revision
4. ✅ מצרפת Evidence
5. ✅ מעדכנת PR

**הכל אוטומטי!** 🚀

---

**עודכן:** 2025-11-09  
**מחבר:** QA Automation Team

