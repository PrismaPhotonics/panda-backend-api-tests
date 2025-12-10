# פקודות הרצה לטסטי Historic Investigation Constraints

## 🌍 הסביבות הזמינות

### 1. **Staging** (10.10.10.100)
- **Backend:** `https://10.10.10.100/focus-server/`
- **MongoDB:** `10.10.10.108:27017`
- **RabbitMQ:** `10.10.10.107`
- **Base Path:** `/prisma/root/recordings`
- **GUID Collections:** Staging environment specific GUIDs

### 2. **Kefar Saba** (10.10.100.100) - Production
- **Backend:** `https://10.10.100.100/focus-server/`
- **MongoDB:** `10.10.100.108:27017`
- **RabbitMQ:** `10.10.100.107`
- **Base Path:** `/prisma/root/recordings/segy`
- **GUID Collections:** Kefar Saba environment specific GUIDs

---

## 🚀 פקודות הרצה

### הרצת כל הטסטים ב-Staging (ברירת מחדל)

```powershell
# הרצה בסיסית
pytest be_focus_server_tests/load/test_historic_investigation_load_constraints.py -v

# או מפורש
pytest be_focus_server_tests/load/test_historic_investigation_load_constraints.py --env=staging -v
```

### הרצת כל הטסטים ב-Kefar Saba (Production)

```powershell
pytest be_focus_server_tests/load/test_historic_investigation_load_constraints.py --env=kefar_saba -v
```

---

## 📋 הרצת טסטים ספציפיים

### טסט 1: אימות מגבלת 30 חלונות

```powershell
# Staging
pytest be_focus_server_tests/load/test_historic_investigation_load_constraints.py::TestHistoricInvestigationConstraints::test_30_window_constraint_validation --env=staging -v

# Kefar Saba
pytest be_focus_server_tests/load/test_historic_investigation_load_constraints.py::TestHistoricInvestigationConstraints::test_30_window_constraint_validation --env=kefar_saba -v
```

### טסט 2: עומס עם חקירות מקבילות רבות

```powershell
# Staging
pytest be_focus_server_tests/load/test_historic_investigation_load_constraints.py::TestHistoricInvestigationConstraints::test_load_with_many_concurrent_investigations --env=staging -v

# Kefar Saba
pytest be_focus_server_tests/load/test_historic_investigation_load_constraints.py::TestHistoricInvestigationConstraints::test_load_with_many_concurrent_investigations --env=kefar_saba -v
```

### טסט 3: חקירות עם משכי זמן ארוכים

```powershell
# Staging
pytest be_focus_server_tests/load/test_historic_investigation_load_constraints.py::TestHistoricInvestigationConstraints::test_long_duration_investigations --env=staging -v

# Kefar Saba
pytest be_focus_server_tests/load/test_historic_investigation_load_constraints.py::TestHistoricInvestigationConstraints::test_long_duration_investigations --env=kefar_saba -v
```

### טסט 4: גדלי חלונות שונים

```powershell
# Staging
pytest be_focus_server_tests/load/test_historic_investigation_load_constraints.py::TestHistoricInvestigationConstraints::test_different_window_sizes --env=staging -v

# Kefar Saba
pytest be_focus_server_tests/load/test_historic_investigation_load_constraints.py::TestHistoricInvestigationConstraints::test_different_window_sizes --env=kefar_saba -v
```

---

## 🎯 הרצה לפי Markers

### הרצת כל טסטי Historic Investigation Constraints

```powershell
# Staging
pytest -m investigation_constraints --env=staging -v

# Kefar Saba
pytest -m investigation_constraints --env=kefar_saba -v
```

### הרצת טסטי Load בלבד

```powershell
# Staging
pytest -m "load and investigation_constraints" --env=staging -v

# Kefar Saba
pytest -m "load and investigation_constraints" --env=kefar_saba -v
```

### הרצת טסטים איטיים (Slow)

```powershell
# Staging
pytest -m "investigation_constraints and slow" --env=staging -v

# Kefar Saba
pytest -m "investigation_constraints and slow" --env=kefar_saba -v
```

---

## 🔍 הרצה עם אפשרויות נוספות

### עם לוגים מפורטים

```powershell
# Staging
pytest be_focus_server_tests/load/test_historic_investigation_load_constraints.py --env=staging -v -s --log-cli-level=DEBUG

# Kefar Saba
pytest be_focus_server_tests/load/test_historic_investigation_load_constraints.py --env=kefar_saba -v -s --log-cli-level=DEBUG
```

### עם דוח HTML

```powershell
# Staging
pytest be_focus_server_tests/load/test_historic_investigation_load_constraints.py --env=staging -v --html=reports/historic_constraints_staging.html --self-contained-html

# Kefar Saba
pytest be_focus_server_tests/load/test_historic_investigation_load_constraints.py --env=kefar_saba -v --html=reports/historic_constraints_kefar_saba.html --self-contained-html
```

### עם דוח JUnit XML

```powershell
# Staging
pytest be_focus_server_tests/load/test_historic_investigation_load_constraints.py --env=staging -v --junitxml=reports/historic_constraints_staging.xml

# Kefar Saba
pytest be_focus_server_tests/load/test_historic_investigation_load_constraints.py --env=kefar_saba -v --junitxml=reports/historic_constraints_kefar_saba.xml
```

---

## 📊 בדיקת Recordings לפני הרצה

### בדיקת Recordings זמינים ב-Staging

```powershell
python scripts/fetch_mongodb_recordings.py --environment staging --weeks-back 4 --limit 10
```

### בדיקת Recordings זמינים ב-Kefar Saba

```powershell
python scripts/fetch_mongodb_recordings.py --environment kefar_saba --weeks-back 4 --limit 10
```

---

## ⚠️ הערות חשובות

### Staging Environment
- ✅ **מותר הכל** - Load tests, Stress tests, כל הטסטים
- ✅ **Recordings:** נשאל מ-`/prisma/root/recordings` (GUIDs של staging)
- ✅ **MongoDB:** `10.10.10.108:27017`

### Kefar Saba Environment (Production)
- ⚠️ **זהירות** - סביבת Production
- ✅ **Recordings:** נשאל מ-`/prisma/root/recordings/segy` (GUIDs של kefar_saba)
- ✅ **MongoDB:** `10.10.100.108:27017`
- ⚠️ **לא להריץ Load Tests כבדים** על Production ללא אישור

---

## 🔄 דוגמאות שימוש מלאות

### דוגמה 1: הרצת כל הטסטים ב-Staging עם לוגים

```powershell
pytest be_focus_server_tests/load/test_historic_investigation_load_constraints.py `
    --env=staging `
    -v `
    -s `
    --log-cli-level=INFO `
    --html=reports/historic_constraints_staging.html `
    --self-contained-html
```

### דוגמה 2: הרצת טסט אחד ספציפי ב-Kefar Saba

```powershell
pytest be_focus_server_tests/load/test_historic_investigation_load_constraints.py::TestHistoricInvestigationConstraints::test_30_window_constraint_validation `
    --env=kefar_saba `
    -v `
    -s `
    --log-cli-level=DEBUG
```

### דוגמה 3: הרצת טסטים איטיים בלבד ב-Staging

```powershell
pytest be_focus_server_tests/load/test_historic_investigation_load_constraints.py `
    --env=staging `
    -m "investigation_constraints and slow" `
    -v `
    -s
```

---

## 📝 סיכום פקודות מהירות

| פעולה | Staging | Kefar Saba |
|------|---------|------------|
| **כל הטסטים** | `pytest be_focus_server_tests/load/test_historic_investigation_load_constraints.py --env=staging -v` | `pytest be_focus_server_tests/load/test_historic_investigation_load_constraints.py --env=kefar_saba -v` |
| **טסט אחד** | `pytest be_focus_server_tests/load/test_historic_investigation_load_constraints.py::TestHistoricInvestigationConstraints::test_30_window_constraint_validation --env=staging -v` | `pytest be_focus_server_tests/load/test_historic_investigation_load_constraints.py::TestHistoricInvestigationConstraints::test_30_window_constraint_validation --env=kefar_saba -v` |
| **לפי Marker** | `pytest -m investigation_constraints --env=staging -v` | `pytest -m investigation_constraints --env=kefar_saba -v` |
| **בדיקת Recordings** | `python scripts/fetch_mongodb_recordings.py --environment staging` | `python scripts/fetch_mongodb_recordings.py --environment kefar_saba` |

---

**תאריך:** 6 בדצמבר 2025  
**גרסה:** 1.0

