# מדריך בחירת סביבה - Environment Selection Guide

## 🎯 שתי הסביבות המוגדרות:

### 1. **Staging** (10.10.10.100)
- **Backend:** `https://10.10.10.100/focus-server/`
- **Frontend:** `https://10.10.10.100/liveView`
- **Load Tests:** ✅ ENABLED (200 jobs)
- **Destructive Tests:** ✅ ENABLED

### 2. **Production** (10.10.100.100)
- **Backend:** `https://10.10.100.100/focus-server/`
- **Frontend:** `https://10.10.100.100/liveView`
- **Load Tests:** ❌ DISABLED (safety)
- **Destructive Tests:** ❌ DISABLED

---

## 🚀 איך לבחור סביבה לפני ריצת טסטים:

### שיטה 1: סקריפט PowerShell (הכי נוח)

```powershell
# הצג את כל הסביבות
.\scripts\select_environment.ps1 -Action show

# בחר staging
.\scripts\select_environment.ps1 -Action staging

# בחר production
.\scripts\select_environment.ps1 -Action production

# בחר local
.\scripts\select_environment.ps1 -Action local
```

### שיטה 2: דרך pytest command line (מומלץ)

```powershell
# הרץ טסטים על staging (ברירת מחדל)
pytest tests/ -v

# הרץ טסטים על production
pytest tests/ --env=production -v

# הרץ טסטים על staging (מפורש)
pytest tests/ --env=staging -v

# הרץ טסטים על local
pytest tests/ --env=local -v
```

### שיטה 3: עדכון ידני בקובץ קונפיגורציה

ערוך את `config/environments.yaml`:

```yaml
# Default environment
default_environment: "staging"  # או "production"
```

---

## 📋 דוגמאות שימוש:

### הרצת טסט אחד על staging:
```powershell
pytest tests/load/test_job_capacity_limits.py::Test200ConcurrentJobsCapacity --env=staging -v
```

### הרצת טסט אחד על production:
```powershell
pytest tests/integration/api/test_health_check.py --env=production -v
```

### הרצת כל הטסטים על staging (ברירת מחדל):
```powershell
pytest tests/ -v
```

### הרצת כל הטסטים על production:
```powershell
pytest tests/ --env=production -v
```

### הרצת רק טסטים שלא הורסים על production:
```powershell
# הטסטים האלה יעברו אוטומטית על production (destructive tests יישמטו)
pytest tests/integration/api/test_health_check.py --env=production -v
pytest tests/integration/api/test_live_monitoring_flow.py --env=production -v
```

---

## ⚠️ אזהרות חשובות:

### Production Environment:
- ❌ **אין להריץ Load Tests** על production
- ❌ **אין להריץ Destructive Tests** (MongoDB Outage, RabbitMQ Outage)
- ✅ **רק טסטים בטוחים** - Health checks, Read-only operations

### Staging Environment:
- ✅ **מותר הכל** - Load tests, Stress tests, Outage tests

---

## 🔍 בדיקת הסביבה הנוכחית:

```powershell
# בדוק איזו סביבה מוגדרת כברירת מחדל
.\scripts\select_environment.ps1 -Action show
```

או:

```python
# בקוד Python
from config.config_manager import ConfigManager
config = ConfigManager()
print(f"Current environment: {config.environment}")
print(f"Backend URL: {config.get_api_config()['base_url']}")
```

---

## 📝 סיכום:

| שיטה | מתי להשתמש | דוגמה |
|------|------------|-------|
| **סקריפט PowerShell** | בחירת סביבה חד-פעמית | `.\scripts\select_environment.ps1 -Action staging` |
| **pytest --env** | בחירת סביבה לכל ריצה | `pytest tests/ --env=production -v` |
| **עדכון ידני** | שינוי קבוע | עדכן `default_environment` בקובץ |

---

**המלצה:** השתמש ב-`pytest --env=...` לכל ריצה - זה הכי גמיש ונוח!

---

**תאריך:** 2 בנובמבר 2025
**גרסה:** 1.0
