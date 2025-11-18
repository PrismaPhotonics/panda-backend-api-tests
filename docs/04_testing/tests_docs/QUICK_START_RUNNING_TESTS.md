# 🚀 מדריך מהיר להרצת טסטים

**תאריך:** 2025-01-27

---

## ⚡ הרצה מהירה (3 שלבים)

### שלב 1: חזרה לתיקיית השורש

```powershell
cd C:\Projects\focus_server_automation
```

### שלב 2: הפעלת Virtual Environment

```powershell
# אם יש .venv
.\.venv\Scripts\Activate.ps1

# או אם יש venv
.\venv\Scripts\Activate.ps1
```

### שלב 3: הרצת הטסטים

```powershell
# כל הטסטים
pytest be_focus_server_tests/ -v

# או דרך הסקריפט (מפעיל את ה-venv אוטומטית)
.\scripts\run_all_tests.ps1
```

---

## 🔴 פתרון בעיות נפוצות

### בעיה 1: "pytest: command not found"

**סיבה:** Virtual environment לא מופעל

**פתרון:**
```powershell
# הפעל את ה-venv
.\.venv\Scripts\Activate.ps1

# או השתמש בסקריפט
.\scripts\run_all_tests.ps1
```

### בעיה 2: "file or directory not found: be_focus_server_tests/"

**סיבה:** אתה לא בתיקיית השורש

**פתרון:**
```powershell
# חזור לתיקיית השורש
cd C:\Projects\focus_server_automation

# הרץ שוב
pytest be_focus_server_tests/ -v
```

### בעיה 3: "Activate.ps1 cannot be loaded"

**סיבה:** מדיניות PowerShell

**פתרון:**
```powershell
# הפעל PowerShell כמנהל והרץ:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# או השתמש בסקריפט
.\scripts\run_all_tests.ps1
```

---

## 📋 פקודות מוכנות

### הרצה בסיסית

```powershell
# מתוך שורש הפרויקט
cd C:\Projects\focus_server_automation
.\.venv\Scripts\Activate.ps1
pytest be_focus_server_tests/ -v
```

### הרצה דרך סקריפט (מומלץ)

```powershell
# מתוך שורש הפרויקט
cd C:\Projects\focus_server_automation
.\scripts\run_all_tests.ps1
```

### הרצה לפי קטגוריה

```powershell
cd C:\Projects\focus_server_automation
.\.venv\Scripts\Activate.ps1

# רק Integration
pytest be_focus_server_tests/integration/ -v

# רק API
pytest be_focus_server_tests/integration/api/ -v

# רק Unit
pytest be_focus_server_tests/unit/ -v
```

---

## ✅ אימות שהכל תקין

```powershell
# 1. בדוק שאתה בתיקיית השורש
Get-Location
# צריך לראות: C:\Projects\focus_server_automation

# 2. בדוק שהתיקייה קיימת
Test-Path be_focus_server_tests
# צריך לראות: True

# 3. בדוק שה-venv מופעל
python --version
# צריך לראות: Python 3.x.x

# 4. בדוק ש-pytest מותקן
pytest --version
# צריך לראות: pytest x.x.x
```

---

## 🎯 סיכום

| שלב | פקודה | תוצאה צפויה |
|-----|-------|-------------|
| 1 | `cd C:\Projects\focus_server_automation` | חזרה לשורש |
| 2 | `.\.venv\Scripts\Activate.ps1` | הפעלת venv |
| 3 | `pytest be_focus_server_tests/ -v` | הרצת טסטים |

**או פשוט:**
```powershell
cd C:\Projects\focus_server_automation
.\scripts\run_all_tests.ps1
```

---

**תאריך:** 2025-01-27  
**גרסה:** 1.0

