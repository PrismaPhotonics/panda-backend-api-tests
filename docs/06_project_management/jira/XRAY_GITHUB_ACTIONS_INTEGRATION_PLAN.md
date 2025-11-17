# תוכנית סנכרון Xray ↔ GitHub Actions - מקצה לקצה
## Complete Xray ↔ GitHub Actions Integration Plan

**תאריך:** 2025-11-09  
**סטטוס:** 📋 תוכנית פעולה

---

## 📊 מצב נוכחי

### ✅ מה כבר קיים:
1. **421 טסטים** עם `@pytest.mark.xray("PZ-XXXXX")` markers
2. **Workflow בסיסי** ב-`.github/workflows/xray_upload.yml`
3. **סקריפט העלאה** `scripts/xray_upload.py` (תומך ב-JUnit + Xray JSON)
4. **קונפיגורציה** ב-`config/xray_config.yaml`
5. **Xray Cloud** מוגדר (לא Server/DC)

### ❌ מה חסר:
1. **סינון לפי Test Plan** - לא מריצים רק את הטסטים מה-Test Plan
2. **קישור ל-Test Plan/Environment/Revision** - לא מועבר ב-upload
3. **Evidence** - לוגים/סקרינשוטים לא מצורפים ל-Test Execution
4. **PR Comments** - לא מעודכן עם קישורים ל-Xray
5. **pytest-xray plugin** - לא מותקן (אופציונלי אבל מועיל)

---

## 🎯 יעדים

1. ✅ **Test Execution** נוצר אוטומטית עם כל ריצה
2. ✅ **קישור ל-Test Plan** (PZ-14024 או אחר)
3. ✅ **קישור ל-Build/Revision** (Git SHA)
4. ✅ **Environment** מסומן (Staging/Production)
5. ✅ **Evidence** מצורף (לוגים/סקרינשוטים)
6. ✅ **PR Comments** עם סיכום וקישורים

---

## 📋 תוכנית פעולה

### שלב 1: עדכון Dependencies ✅
- [ ] הוספת `pytest-xray` ל-`requirements.txt` (אופציונלי)
- [ ] עדכון `pytest-html` לגרסה אחרונה

### שלב 2: סקריפטים תומכים ✅
- [ ] `scripts/xray/get_test_plan_tests.py` - שליפת טסטים מ-Test Plan
- [ ] `scripts/xray/attach_evidence.py` - העלאת evidence ל-Test Execution
- [ ] עדכון `scripts/xray_upload.py` - תמיכה ב-Test Plan/Environment/Revision

### שלב 3: GitHub Actions Workflow ✅
- [ ] יצירת `.github/workflows/xray_full_integration.yml` - workflow מלא
- [ ] עדכון `.github/workflows/xray_upload.yml` - שיפור הקיים

### שלב 4: קונפיגורציה ✅
- [ ] עדכון `config/xray_config.yaml` - הוספת Test Plan default
- [ ] יצירת `.github/workflows/xray_secrets.md` - מדריך הגדרת Secrets

### שלב 5: תיעוד ✅
- [ ] מדריך שימוש מלא
- [ ] דוגמאות
- [ ] פתרון בעיות

---

## 🔧 יישום

### 1. סקריפט לשליפת טסטים מ-Test Plan

```python
# scripts/xray/get_test_plan_tests.py
# משתמש ב-Xray GraphQL API לשליפת טסטים
```

### 2. Workflow מתקדם

```yaml
# .github/workflows/xray_full_integration.yml
# כולל:
# - שליפת טסטים מ-Test Plan
# - הרצת טסטים מסוננים
# - העלאת תוצאות עם Test Plan/Environment/Revision
# - העלאת Evidence
# - PR Comments
```

### 3. עדכון xray_upload.py

```python
# תמיכה ב:
# - testPlanKey
# - testEnvironments
# - revision
# - evidence
```

---

## 📝 הערות חשובות

1. **Xray Cloud** - אנחנו על Cloud, לא Server/DC
2. **Test Plan** - ברירת מחדל: PZ-14024
3. **Environment** - Staging/Production לפי branch
4. **Evidence** - לוגים מ-`logs/`, סקרינשוטים מ-`screenshots/`

---

## 🚀 צעדים הבאים

1. יצירת הסקריפטים
2. יצירת ה-Workflow
3. בדיקה מקומית
4. בדיקה ב-GitHub Actions
5. תיעוד

---

**עודכן:** 2025-11-09

