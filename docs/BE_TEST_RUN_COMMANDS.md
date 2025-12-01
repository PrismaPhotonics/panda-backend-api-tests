# פקודות הרצה - Backend Automation Tests
# ===========================================

## תוכן עניינים
1. [התקנת Dependencies](#התקנת-dependencies)
2. [הרצה בסיסית](#הרצה-בסיסית)
3. [הרצה לפי קטגוריות](#הרצה-לפי-קטגוריות)
4. [הרצה לפי Markers](#הרצה-לפי-markers)
5. [הרצה מקבילית](#הרצה-מקבילית)
6. [הרצה עם דוחות](#הרצה-עם-דוחות)
7. [הרצה לפי סביבה](#הרצה-לפי-סביבה)
8. [שימוש בסקריפטים](#שימוש-בסקריפטים)

---

## התקנת Dependencies

### ⚠️ חשוב: בגלל בעיית resolution-too-deep, התקן חבילות ישירות:

```bash
# התקנת חבילות בסיסיות
pip install pytest pytest-asyncio pytest-timeout pytest-mock pytest-html pytest-cov pytest-json-report pytest-xdist

# התקנת חבילות HTTP ו-Data Processing
pip install requests httpx beautifulsoup4 pydantic pydantic-settings orjson pyyaml

# התקנת חבילות Infrastructure
pip install kubernetes pymongo paramiko pika structlog colorlog python-dateutil pytz psutil python-dotenv netaddr

# התקנת חבילות אופציונליות
pip install allure-pytest jinja2 asyncio-mqtt aiofiles
pip install playwright pytest-playwright
pip install jira pytest-xray
pip install black flake8 mypy isort cryptography bandit sphinx sphinx-rtd-theme
```

---

## הרצה בסיסית

### הרצת כל הטסטים:
```bash
pytest be_focus_server_tests/
```

### הרצה עם פלט מפורט:
```bash
pytest be_focus_server_tests/ -v
```

### הרצה עם פלט מלא (ללא capture):
```bash
pytest be_focus_server_tests/ -v -s
```

### הרצה של קובץ ספציפי:
```bash
pytest be_focus_server_tests/integration/api/test_health_check.py
```

### הרצה של טסט ספציפי:
```bash
pytest be_focus_server_tests/integration/api/test_health_check.py::test_health_check_endpoint
```

---

## הרצה לפי קטגוריות

### Unit Tests בלבד:
```bash
pytest be_focus_server_tests/unit/
```

### Integration Tests:
```bash
pytest be_focus_server_tests/integration/
```

### API Tests:
```bash
pytest be_focus_server_tests/integration/api/
```

### Infrastructure Tests:
```bash
pytest be_focus_server_tests/infrastructure/
```

### Load Tests:
```bash
pytest be_focus_server_tests/load/
```

### Stress Tests:
```bash
pytest be_focus_server_tests/stress/
```

### Security Tests:
```bash
pytest be_focus_server_tests/security/
```

### Data Quality Tests:
```bash
pytest be_focus_server_tests/data_quality/
```

### Performance Tests:
```bash
pytest be_focus_server_tests/performance/
```

---

## הרצה לפי Markers

### הרצת טסטים עם marker ספציפי:
```bash
# Smoke tests
pytest -m smoke

# Critical tests
pytest -m critical

# Integration tests
pytest -m integration

# API tests
pytest -m api

# Unit tests
pytest -m unit

# Load tests
pytest -m load

# Stress tests
pytest -m stress

# Performance tests
pytest -m performance

# Security tests
pytest -m security

# MongoDB tests
pytest -m mongodb

# RabbitMQ tests
pytest -m rabbitmq

# Kubernetes tests
pytest -m kubernetes

# E2E tests
pytest -m e2e

# Health check tests
pytest -m health_check

# Alert tests
pytest -m alerts
```

### הרצת מספר markers:
```bash
# OR - טסטים עם אחד מהמרקרים
pytest -m "smoke or critical"

# AND - טסטים עם שני המרקרים
pytest -m "integration and api"

# NOT - טסטים ללא marker מסוים
pytest -m "not load"
pytest -m "not load and not stress"
```

### הרצה ללא Load/Stress:
```bash
pytest -m "not load and not stress and not grpc"
```

---

## הרצה מקבילית

### הרצה מקבילית עם מספר workers:
```bash
# 4 workers (ברירת מחדל)
pytest be_focus_server_tests/ -n 4

# 8 workers
pytest be_focus_server_tests/ -n 8

# Auto - לפי מספר cores
pytest be_focus_server_tests/ -n auto
```

### הרצה מקבילית לפי קטגוריה:
```bash
pytest be_focus_server_tests/integration/ -n 4
```

---

## הרצה עם דוחות

### דוח HTML:
```bash
pytest be_focus_server_tests/ --html=reports/report.html --self-contained-html
```

### דוח JUnit XML:
```bash
pytest be_focus_server_tests/ --junitxml=reports/junit.xml
```

### דוח Coverage:
```bash
pytest be_focus_server_tests/ --cov=src --cov-report=html --cov-report=term
```

### דוח JSON:
```bash
pytest be_focus_server_tests/ --json-report --json-report-file=reports/report.json
```

### Allure Report:
```bash
# הרצה עם Allure
pytest be_focus_server_tests/ --alluredir=reports/allure-results

# פתיחת דוח Allure
allure serve reports/allure-results
```

### כל הדוחות יחד:
```bash
pytest be_focus_server_tests/ \
  --html=reports/report.html \
  --self-contained-html \
  --junitxml=reports/junit.xml \
  --cov=src \
  --cov-report=html \
  --json-report \
  --json-report-file=reports/report.json \
  --alluredir=reports/allure-results
```

---

## הרצה לפי סביבה

### הרצה עם סביבה ספציפית:
```bash
# סביבת staging (ברירת מחדל)
pytest be_focus_server_tests/ --env=staging

# סביבת local
pytest be_focus_server_tests/ --env=local

# סביבת production
pytest be_focus_server_tests/ --env=production
```

### הרצה עם משתני סביבה:
```bash
# הגדרת FOCUS_BASE_URL
export FOCUS_BASE_URL=https://focus-server.example.com
pytest be_focus_server_tests/

# הגדרת מספר משתנים
export FOCUS_BASE_URL=https://focus-server.example.com
export FOCUS_API_PREFIX=/focus-server
export VERIFY_SSL=false
pytest be_focus_server_tests/
```

---

## הרצה עם אופציות נוספות

### עצירה אחרי מספר כשלים:
```bash
# עצירה אחרי 5 כשלים
pytest be_focus_server_tests/ --maxfail=5

# עצירה אחרי כשל ראשון
pytest be_focus_server_tests/ --maxfail=1
```

### הרצה עם timeout:
```bash
# timeout של 300 שניות לכל טסט
pytest be_focus_server_tests/ --timeout=300
```

### הרצה עם retry:
```bash
# 3 ניסיונות לכל טסט שנכשל
pytest be_focus_server_tests/ --reruns=3
```

### הרצה עם verbose mode:
```bash
# פלט מפורט מאוד
pytest be_focus_server_tests/ -vv

# פלט מפורט ביותר
pytest be_focus_server_tests/ -vvv
```

### הרצה עם traceback:
```bash
# traceback קצר (ברירת מחדל)
pytest be_focus_server_tests/ --tb=short

# traceback ארוך
pytest be_focus_server_tests/ --tb=long

# traceback מלא
pytest be_focus_server_tests/ --tb=longest

# ללא traceback
pytest be_focus_server_tests/ --tb=no
```

---

## שימוש בסקריפטים

### הרצה עם הסקריפט המקצועי:
```bash
# הרצה בסיסית
python scripts/run_tests.py

# הרצה עם סביבה ספציפית
python scripts/run_tests.py --env local

# הרצה מקבילית
python scripts/run_tests.py --parallel

# הרצה עם סוג טסטים ספציפי
python scripts/run_tests.py --test-type integration

# הרצה עם דוחות
python scripts/run_tests.py --generate-reports
```

### הרצה עם אופציות נוספות:
```bash
# עזרה
python scripts/run_tests.py --help

# Dry run (ללא הרצה בפועל)
python scripts/run_tests.py --dry-run

# הרצה עם monitoring
python scripts/run_tests.py --monitor-pods

# הרצה עם איסוף logs
python scripts/run_tests.py --collect-pod-logs
```

---

## דוגמאות שימוש נפוצות

### 1. הרצה מהירה של Unit Tests:
```bash
pytest be_focus_server_tests/unit/ -v
```

### 2. הרצה של Integration Tests עם דוחות:
```bash
pytest be_focus_server_tests/integration/ \
  -v \
  --html=reports/integration_report.html \
  --self-contained-html \
  --junitxml=reports/integration_junit.xml
```

### 3. הרצה של API Tests בלבד (ללא Load):
```bash
pytest be_focus_server_tests/integration/api/ \
  -m "not load and not stress" \
  -v \
  --env=local
```

### 4. הרצה מקבילית של כל הטסטים (ללא Load/Stress):
```bash
pytest be_focus_server_tests/ \
  -m "not load and not stress and not grpc" \
  -n auto \
  -v \
  --html=reports/full_report.html \
  --self-contained-html
```

### 5. הרצה של Smoke Tests בלבד:
```bash
pytest -m smoke -v --env=local
```

### 6. הרצה עם Coverage:
```bash
pytest be_focus_server_tests/unit/ \
  --cov=src \
  --cov-report=html \
  --cov-report=term-missing
```

### 7. הרצה של טסט ספציפי עם debug:
```bash
pytest be_focus_server_tests/integration/api/test_health_check.py::test_health_check_endpoint \
  -v -s \
  --tb=long
```

### 8. הרצה עם Allure:
```bash
pytest be_focus_server_tests/integration/ \
  --alluredir=reports/allure-results \
  -v

# פתיחת דוח
allure serve reports/allure-results
```

---

## טיפים וטריקים

### 1. הרצה מהירה לבדיקה:
```bash
# רק Unit Tests
pytest be_focus_server_tests/unit/ -v --tb=short
```

### 2. הרצה עם פילטר לפי שם:
```bash
# טסטים שמכילים "health" בשם
pytest be_focus_server_tests/ -k "health" -v

# טסטים שמכילים "api" או "integration"
pytest be_focus_server_tests/ -k "api or integration" -v
```

### 3. הרצה עם איסוף מידע בלבד (ללא הרצה):
```bash
# איסוף טסטים בלבד
pytest be_focus_server_tests/ --collect-only

# איסוף עם פירוט
pytest be_focus_server_tests/ --collect-only -v
```

### 4. הרצה עם cache:
```bash
# ניקוי cache
pytest --cache-clear

# הרצה עם cache
pytest be_focus_server_tests/ --cache-show
```

### 5. הרצה עם markers מותאמים אישית:
```bash
# טסטים עם marker ספציפי
pytest -m xray -v

# טסטים עם Jira marker
pytest -m jira -v
```

---

## פתרון בעיות נפוצות

### בעיית resolution-too-deep:
```bash
# אל תשתמש ב-requirements.txt ישירות
# התקן חבילות ישירות (ראה סעיף "התקנת Dependencies")
```

### בעיית import:
```bash
# ודא שאתה בתיקיית הפרויקט
cd C:\Projects\focus_server_automation

# ודא ש-PYTHONPATH מוגדר נכון
export PYTHONPATH=.
```

### בעיית סביבה:
```bash
# ודא שהסביבה מוגדרת נכון
pytest be_focus_server_tests/ --env=local -v
```

---

## Gradual Load Tests (טסטי עומס הדרגתיים)

טסטים אלה בודקים את יציבות המערכת תחת עומס עולה הדרגתית של Live Jobs.

### הרצה עם סקריפט ייעודי:
```bash
# הרצה מלאה (5 → 50 jobs, +5 כל 10 שניות)
python scripts/run_gradual_load_test.py --env staging

# הרצה מהירה לבדיקת CI (2 → 10 jobs)
python scripts/run_gradual_load_test.py --quick --env staging

# הרצה עם הגדרות מותאמות אישית
python scripts/run_gradual_load_test.py --initial 5 --step 5 --max-jobs 30 --interval 5
```

### הרצה עם pytest:
```bash
# טסט מלא (הדרגתי ל-50 jobs)
pytest be_focus_server_tests/load/test_gradual_live_job_load.py -m gradual_load -v

# טסט מהיר (לבדיקות CI)
pytest be_focus_server_tests/load/test_gradual_live_job_load.py::TestGradualLiveJobLoad::test_quick_gradual_load -v

# כל טסטי ה-gradual load
pytest -m gradual_load -v --env staging

# עם דוח HTML
pytest -m gradual_load -v --html=reports/gradual_load_report.html --self-contained-html
```

### פרמטרים של הסקריפט:
| פרמטר | ברירת מחדל | תיאור |
|-------|-------------|--------|
| `--env` | staging | סביבה (staging/production) |
| `--initial` | 5 | מספר jobs התחלתי |
| `--step` | 5 | כמות jobs להוספה בכל שלב |
| `--max-jobs` | 50 | מקסימום jobs |
| `--interval` | 10 | שניות בין שלבים |
| `--quick` | - | מצב מהיר (2→10 jobs) |

### דוגמאות שימוש:
```bash
# בדיקת יציבות עד 30 jobs
python scripts/run_gradual_load_test.py --max-jobs 30 --env staging

# בדיקה מהירה יותר (5 שניות בין שלבים)
python scripts/run_gradual_load_test.py --interval 5 --env staging

# הרצה על production עם הגדרות שמרניות
python scripts/run_gradual_load_test.py --max-jobs 20 --step 2 --interval 15 --env production
```

---

## סיכום - פקודות מהירות

```bash
# הרצה בסיסית
pytest be_focus_server_tests/ -v

# Unit Tests בלבד
pytest be_focus_server_tests/unit/ -v

# Integration Tests (ללא Load/Stress)
pytest be_focus_server_tests/integration/ -m "not load and not stress" -v

# API Tests
pytest be_focus_server_tests/integration/api/ -v

# עם דוח HTML
pytest be_focus_server_tests/ --html=reports/report.html --self-contained-html -v

# מקבילית
pytest be_focus_server_tests/ -n auto -v

# Smoke Tests
pytest -m smoke -v
```

