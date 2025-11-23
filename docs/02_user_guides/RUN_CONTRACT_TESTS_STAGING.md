# הרצת Contract Tests על Staging Environment

## 🎯 סביבת Staging

- **Backend URL:** `https://10.10.10.100/focus-server/`
- **IP Address:** `10.10.10.100`
- **API Prefix:** `/focus-server`
- **SSL Verification:** Disabled (self-signed cert)

---

## 🚀 שיטות להרצת הבדיקות

### שיטה 1: הרצה ישירה (ברירת מחדל = staging)

הבדיקות כבר מוגדרות להשתמש ב-staging כברירת מחדל:

```powershell
# הרצת כל הבדיקות
cd focus_server_api_load_tests/focus_api_tests
pytest test_api_contract.py -v

# או מהשורש של הפרויקט:
pytest focus_server_api_load_tests/focus_api_tests/test_api_contract.py -v
```

### שיטה 2: הגדרת משתני סביבה ידנית

```powershell
# הגדר משתני סביבה
$env:FOCUS_ENV = "staging"
$env:FOCUS_SERVER_HOST = "10.10.10.100"
$env:FOCUS_API_PREFIX = "/focus-server"
$env:VERIFY_SSL = "false"

# הרץ את הבדיקות
pytest focus_server_api_load_tests/focus_api_tests/test_api_contract.py -v
```

### שיטה 3: שימוש ב-ConfigManager (אוטומטי)

הקוד כבר משתמש ב-`ConfigManager` שמזהה את staging אוטומטית:

```powershell
# פשוט הרץ - הקוד יטען את staging אוטומטית
pytest focus_server_api_load_tests/focus_api_tests/test_api_contract.py -v
```

---

## 📋 דוגמאות שימוש

### הרצת בדיקה ספציפית:

```powershell
# בדיקת health check
pytest focus_server_api_load_tests/focus_api_tests/test_api_contract.py::test_health_check -v

# בדיקת channels endpoint
pytest focus_server_api_load_tests/focus_api_tests/test_api_contract.py::test_get_channels -v

# בדיקת metadata
pytest focus_server_api_load_tests/focus_api_tests/test_api_contract.py::test_live_metadata_smoke -v
```

### הרצה עם דוחות:

```powershell
# עם HTML report
pytest focus_server_api_load_tests/focus_api_tests/test_api_contract.py \
  --html=reports/contract-report.html \
  --self-contained-html \
  -v

# עם JUnit XML report
pytest focus_server_api_load_tests/focus_api_tests/test_api_contract.py \
  --junitxml=reports/junit-contract.xml \
  -v

# עם JSON report
pytest focus_server_api_load_tests/focus_api_tests/test_api_contract.py \
  --json-report \
  --json-report-file=reports/contract-report.json \
  -v
```

### הרצה עם פילטרים:

```powershell
# רק smoke tests
pytest focus_server_api_load_tests/focus_api_tests/test_api_contract.py -k "smoke" -v

# רק negative tests
pytest focus_server_api_load_tests/focus_api_tests/test_api_contract.py -k "negative" -v

# דילוג על בדיקות מסוימות
pytest focus_server_api_load_tests/focus_api_tests/test_api_contract.py -k "not test_configure" -v
```

---

## 🔧 הגדרות מתקדמות

### הגדרת timeout:

```powershell
pytest focus_server_api_load_tests/focus_api_tests/test_api_contract.py \
  --timeout=300 \
  -v
```

### הרצה מקבילית:

```powershell
pytest focus_server_api_load_tests/focus_api_tests/test_api_contract.py \
  -n auto \
  -v
```

### הרצה עם debug output:

```powershell
pytest focus_server_api_load_tests/focus_api_tests/test_api_contract.py \
  -v -s \
  --log-cli-level=DEBUG
```

---

## ✅ בדיקת חיבור לפני הרצה

לפני הרצת הבדיקות, אפשר לבדוק שהשרת נגיש:

```powershell
# בדיקת חיבור בסיסית
curl -k https://10.10.10.100/focus-server/channels

# או עם PowerShell
Invoke-WebRequest -Uri "https://10.10.10.100/focus-server/channels" -SkipCertificateCheck
```

---

## 🐛 פתרון בעיות

### שגיאת חיבור (Connection Error):

1. **בדוק שהשרת נגיש:**
   ```powershell
   ping 10.10.10.100
   ```

2. **בדוק שהפורט פתוח:**
   ```powershell
   Test-NetConnection -ComputerName 10.10.10.100 -Port 443
   ```

3. **ודא שמשתני הסביבה נכונים:**
   ```powershell
   echo $env:FOCUS_SERVER_HOST
   echo $env:FOCUS_API_PREFIX
   ```

### שגיאת SSL:

אם יש שגיאת SSL, ודא ש-`VERIFY_SSL=false`:
```powershell
$env:VERIFY_SSL = "false"
```

### הבדיקות מנסות להתחבר ל-localhost:

זה אומר שהקוד לא מזהה את משתני הסביבה. ודא ש:
1. משתני הסביבה מוגדרים נכון
2. או שהקוד משתמש ב-ConfigManager עם `FOCUS_ENV=staging`

---

## 📝 סיכום - הפקודה הפשוטה ביותר

```powershell
# מהשורש של הפרויקט:
pytest focus_server_api_load_tests/focus_api_tests/test_api_contract.py -v
```

**זה הכל!** הקוד כבר מוגדר להשתמש ב-staging כברירת מחדל.

---

**תאריך:** נובמבר 2025  
**גרסה:** 1.0

