# איך להפעיל את ה-Workflow
## How to Run the Workflow

**תאריך:** 2025-11-09  
**Repository:** https://github.com/PrismaPhotonics/panda-backend-api-tests

---

## 🎯 מה לעשות עכשיו

### שלב 1: ודא שה-Workflow קיים

1. **לך ל-GitHub:**
   ```
   https://github.com/PrismaPhotonics/panda-backend-api-tests
   ```

2. **בדוק שה-workflow קיים:**
   - לחץ על **Actions** (בתפריט העליון)
   - חפש **"Tests - Simple (No Xray API)"**
   - אם אתה רואה אותו - מעולה! ✅
   - אם לא - צריך לדחוף את הקוד (ראה שלב 2)

---

### שלב 2: דחוף את ה-Workflow (אם צריך)

אם ה-workflow לא קיים ב-GitHub:

```bash
# ודא שאתה ב-branch הנכון
git checkout main  # או develop

# הוסף את ה-workflow
git add .github/workflows/tests_simple.yml

# Commit
git commit -m "Add simple test workflow"

# Push
git push origin main  # או develop
```

---

### שלב 3: הפעל את ה-Workflow

**אפשרות A - אוטומטי (מומלץ):**

1. **דחוף קוד ל-GitHub:**
   ```bash
   git add .
   git commit -m "Trigger workflow"
   git push
   ```

2. **ה-workflow ירוץ אוטומטית:**
   - עם push ל-`main` או `develop`
   - עם Pull Request

**אפשרות B - ידני:**

1. **לך ל-GitHub Actions:**
   ```
   https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
   ```

2. **בחר "Tests - Simple (No Xray API)"**

3. **לחץ "Run workflow"** (כפתור בצד ימין)

4. **בחר branch** (main/develop)

5. **לחץ "Run workflow"**

---

## 📊 מה תראה

### ב-GitHub Actions:

1. **תוצאות הריצה:**
   - ✅ כמה טסטים עברו
   - ❌ כמה נכשלו
   - 📊 סה"כ טסטים
   - ⏱️ זמן ריצה

2. **Artifacts:**
   - `test-results-XXX` - כל הקבצים
   - `reports/junit.xml` - תוצאות JUnit
   - `reports/report.html` - דוח HTML
   - `logs/` - לוגים
   - `screenshots/` - סקרינשוטים

### ב-PR (אם יש Pull Request):

הערה אוטומטית עם:
- ✅ כמה טסטים עברו
- ❌ כמה נכשלו
- 📊 סה"כ
- 📎 קישור להורדת Artifacts

---

## ✅ Checklist

לפני הרצה:

- [ ] ה-workflow קיים ב-GitHub (Actions → "Tests - Simple")
- [ ] יש טסטים בתיקייה `tests/`
- [ ] יש `requirements.txt` עם כל ה-dependencies
- [ ] יש `pytest.ini` מוגדר (אופציונלי)

---

## 🐛 פתרון בעיות

### בעיה: "Workflow not found"

**פתרון:**
1. ודא שה-workflow קיים: `.github/workflows/tests_simple.yml`
2. ודא שהוא ב-branch הנכון (main/develop)
3. דחוף את הקוד: `git push`

### בעיה: "No tests found"

**פתרון:**
1. בדוק שהתיקייה `tests/` קיימת
2. בדוק שיש קבצי טסט (`test_*.py`)
3. בדוק שה-`pytest.ini` מוגדר נכון

### בעיה: "Tests failed"

**פתרון:**
1. בדוק את הלוגים ב-GitHub Actions
2. הורד את ה-Artifacts
3. פתח את `reports/report.html` לראות פרטים

---

## 🎉 סיכום

**מה לעשות עכשיו:**

1. ✅ **לך ל-GitHub Actions** → בדוק שה-workflow קיים
2. ✅ **דחוף קוד** → ה-workflow ירוץ אוטומטית
3. ✅ **ראה תוצאות** → ב-Actions → Artifacts

**זה הכל!** 🚀

---

**עודכן:** 2025-11-09

