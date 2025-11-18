# ⚠️ פתרון בעיה: הרצת טסטים מתוך תיקיית scripts/

**תאריך:** 2025-01-27  
**בעיה:** pytest לא מוצא את `be_focus_server_tests/` כשהפקודה רצה מתוך `scripts/`

---

## 🔴 הבעיה

כשמרצים את הפקודה מתוך תיקיית `scripts/`:

```powershell
# ❌ שגוי - מתוך scripts/
PS C:\Projects\focus_server_automation\scripts> pytest be_focus_server_tests/ -v
ERROR: file or directory not found: be_focus_server_tests/
```

**סיבה:** pytest מחפש את התיקייה יחסית לתיקייה הנוכחית (`scripts/`), ולא מוצא אותה.

---

## ✅ פתרונות

### פתרון 1: חזרה לתיקיית השורש (מומלץ)

```powershell
# חזרה לתיקיית השורש
cd C:\Projects\focus_server_automation

# הרצת הטסטים
pytest be_focus_server_tests/ -v
```

### פתרון 2: שימוש בנתיב יחסי

```powershell
# מתוך scripts/ - שימוש בנתיב יחסי
PS C:\Projects\focus_server_automation\scripts> pytest ../be_focus_server_tests/ -v
```

### פתרון 3: שימוש בנתיב מלא

```powershell
# מתוך scripts/ - שימוש בנתיב מלא
PS C:\Projects\focus_server_automation\scripts> pytest C:\Projects\focus_server_automation\be_focus_server_tests/ -v
```

### פתרון 4: שימוש בסקריפט המוכן

```powershell
# מתוך scripts/ - חזרה לשורש והרצה
PS C:\Projects\focus_server_automation\scripts> cd ..; pytest be_focus_server_tests/ -v

# או שימוש בסקריפט המוכן
PS C:\Projects\focus_server_automation\scripts> cd ..; .\scripts\run_all_tests.ps1
```

---

## 📝 הערות חשובות

### GitHub Actions Workflow

ה-GitHub Actions workflow (`tests_simple.yml`) רץ נכון כי הוא רץ מתוך שורש הפרויקט:

```yaml
- name: Run tests
  run: |
    mkdir -p reports logs screenshots
    pytest be_focus_server_tests/ -v \
      --junitxml=reports/junit.xml \
      ...
```

**זה תקין** - ב-GitHub Actions, ה-working directory הוא תמיד שורש הפרויקט.

---

## 🎯 המלצות

### להרצה מקומית

**תמיד להריץ מתוך שורש הפרויקט:**

```powershell
# ודא שאתה בתיקיית השורש
cd C:\Projects\focus_server_automation

# הרץ את הטסטים
pytest be_focus_server_tests/ -v
```

### או שימוש בסקריפטים המוכנים

```powershell
# מתוך שורש הפרויקט
.\scripts\run_all_tests.ps1

# או עם פרמטרים
.\scripts\run_all_tests.ps1 -TestSuite integration
.\scripts\run_all_tests.ps1 -TestSuite api
.\scripts\run_all_tests.ps1 -TestSuite quick
```

---

## 🔍 אימות נתיב

לבדוק שאתה בתיקייה הנכונה:

```powershell
# בדיקת תיקייה נוכחית
Get-Location

# בדיקת קיום התיקייה
Test-Path be_focus_server_tests

# רשימת תיקיות ברמה הראשית
Get-ChildItem -Directory | Select-Object Name
```

**צריך לראות:**
- `be_focus_server_tests/` קיימת
- `scripts/` קיימת
- `config/` קיימת
- `docs/` קיימת

---

## ✅ סיכום

| מיקום | פקודה | תוצאה |
|-------|-------|--------|
| ❌ `scripts/` | `pytest be_focus_server_tests/ -v` | ❌ שגיאה |
| ✅ שורש | `pytest be_focus_server_tests/ -v` | ✅ עובד |
| ✅ `scripts/` | `pytest ../be_focus_server_tests/ -v` | ✅ עובד |
| ✅ שורש | `.\scripts\run_all_tests.ps1` | ✅ עובד |

---

**תאריך:** 2025-01-27  
**גרסה:** 1.0

