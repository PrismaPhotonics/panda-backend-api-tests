# הודעה לצוות - תוכנית הבדיקות האוטומטיות

**שלום לכולם! 👋**

מוזמנים לעבור על תוכנית הבדיקות שיצרתי עבור ה-Backend של Focus Server וחבורתו:

🔗 **Jira Test Plan:** [PZ-14024 - Focus Server Test Plan](https://prismaphotonics.atlassian.net/browse/PZ-14024)

---

## 📋 מה יש לנו?

**כל הטסטים שמופיעים ב-Jira Test Plan (PZ-14024) משויכים לטסטים האוטומטיים!**

### סטטיסטיקות:
- ✅ **70+ קבצי בדיקות** אוטומטיות
- ✅ **300+ פונקציות בדיקה**
- ✅ **431 markers** של Xray/Jira משויכים לטסטים
- ✅ **100% כיסוי** - כל הטסטים ב-Jira יש להם טסט אוטומטי מקביל

---

## 🔗 איפה נמצא הקוד?

**GitHub Repository:**  
https://github.com/PrismaPhotonics/panda-backend-api-tests

**Branch:** `chore/add-roy-tests`

**מיקום הטסטים:** `tests/` directory

---

## 🔍 איך הטסטים משויכים ל-Jira?

כל טסט אוטומטי משויך ל-Jira Test Case באמצעות **markers**:

```python
@pytest.mark.xray("PZ-XXXXX")  # משייך ל-Xray Test Case
@pytest.mark.jira("PZ-XXXXX")  # משייך ל-Jira Ticket
```

**דוגמה:**
```python
@pytest.mark.integration
@pytest.mark.api
@pytest.mark.xray("PZ-13986")
def test_job_capacity_200_concurrent():
    """Test that system supports 200 concurrent jobs"""
    ...
```

---

## 📂 מבנה הטסטים

הטסטים מאורגנים לפי קטגוריות:

```
tests/
├── integration/          # בדיקות אינטגרציה (API, E2E)
│   ├── api/             # 20+ קבצי בדיקות API
│   ├── data_quality/    # בדיקות איכות נתונים
│   ├── error_handling/  # בדיקות טיפול בשגיאות
│   ├── load/            # בדיקות עומס
│   ├── performance/     # בדיקות ביצועים
│   └── security/        # בדיקות אבטחה
├── infrastructure/      # בדיקות תשתית
│   └── resilience/      # בדיקות חוסן (pod recovery)
├── data_quality/        # בדיקות MongoDB
├── performance/         # בדיקות ביצועים
├── security/            # בדיקות אבטחה
├── load/                # בדיקות עומס
└── stress/              # בדיקות לחץ
```

**📖 תיעוד מלא:** `tests/README.md`

---

## 🎯 איך למצוא טסט ספציפי?

### 1. לפי Jira Ticket ID:
```bash
# חיפוש בקוד
grep -r "PZ-13986" tests/
```

### 2. לפי קטגוריה:
- **API Tests:** `tests/integration/api/`
- **Infrastructure:** `tests/infrastructure/`
- **Data Quality:** `tests/data_quality/`
- **Performance:** `tests/performance/` + `tests/integration/performance/`
- **Load:** `tests/load/` + `tests/integration/load/`
- **Security:** `tests/security/` + `tests/integration/security/`

### 3. לפי Test Plan ב-Jira:
כל טסט ב-Jira Test Plan (PZ-14024) יש לו טסט אוטומטי מקביל עם אותו ID.

---

## 🚀 איך להריץ את הטסטים?

### הרצת כל הטסטים:
```bash
pytest tests/ -v
```

### הרצה לפי קטגוריה:
```bash
# בדיקות API
pytest tests/integration/api/ -v

# בדיקות תשתית
pytest tests/infrastructure/ -v

# בדיקות עומס
pytest tests/load/ -v
```

### הרצה לפי Jira Ticket:
```bash
# הרצת טסטים של ticket ספציפי
pytest -m xray -k "PZ-13986" -v
```

### הרצה לפי marker:
```bash
pytest -m integration -v
pytest -m api -v
pytest -m critical -v
```

---

## 🔄 איך הטסטים מתעדכנים ב-Jira?

1. **אוטומטי:** כל הרצת טסטים מעדכנת את התוצאות ב-Xray
2. **Markers:** הטסטים משויכים ל-Jira דרך `@pytest.mark.xray()`
3. **תוצאות:** תוצאות ההרצה נשלחות אוטומטית ל-Jira Test Execution

---

## 📊 דוגמאות למיפוי

### בדיקות API:
- **PZ-13986** (200 Jobs Capacity) → `tests/load/test_job_capacity_limits.py`
- **PZ-13985** (Live Metadata) → `tests/integration/api/test_live_monitoring_flow.py`
- **PZ-13984** (Future Timestamps) → `tests/integration/api/test_prelaunch_validations.py`

### בדיקות תשתית:
- **PZ-13640** (MongoDB Outage) → `tests/performance/test_mongodb_outage_resilience.py`
- **PZ-13899** (K8s Job Lifecycle) → `tests/infrastructure/test_k8s_job_lifecycle.py`

### בדיקות Data Quality:
- **PZ-13983** (MongoDB Indexes) → `tests/data_quality/test_mongodb_indexes_and_schema.py`

**📋 מיפוי מלא:** `docs/06_project_management/jira/BUGS_TO_TESTS_MAPPING.md`

---

## 🐛 באגים שנמצאו על ידי הטסטים

**15 באגים** נפתחו ב-Jira על בסיס הטסטים האוטומטיים:
- כל באג יש לו טסט אוטומטי שמזהה אותו
- כל הטסטים מסומנים עם `@pytest.mark.jira("PZ-XXXXX")`
- 100% כיסוי - כל הבאגים יש להם טסטים אוטומטיים

---

## 📚 תיעוד נוסף

- **README ראשי:** `tests/README.md` - תיעוד מלא של כל הטסטים
- **מיפוי באגים:** `docs/06_project_management/jira/BUGS_TO_TESTS_MAPPING.md`
- **מדריכי הרצה:** `docs/02_user_guides/`

---

## ❓ שאלות?

- **איך למצוא טסט ספציפי?** → חפש ב-`tests/` לפי Jira ID
- **איך להריץ טסטים?** → `pytest tests/ -v`
- **איפה התיעוד?** → `tests/README.md`
- **איך הטסטים מתעדכנים ב-Jira?** → אוטומטית דרך Xray integration

---

**מוזמנים לעבור, לבדוק, ולהעיר הערות! 🚀**

**Roy Avrahami**  
QA Automation Architect

