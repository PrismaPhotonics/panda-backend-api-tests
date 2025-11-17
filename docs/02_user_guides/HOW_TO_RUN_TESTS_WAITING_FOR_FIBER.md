# 🚀 איך להריץ את האוטומציה עכשיו - מצב "waiting for fiber"

**תאריך:** 2025-11-08  
**סטטוס:** ⚠️ **המערכת במצב "waiting for fiber"**  
**השפעה:** חלק מהטסטים לא יכולים לרוץ

---

## 📋 סיכום המצב

המערכת במצב **"waiting for fiber"** - אין fiber פיזי מחובר, ולכן:
- ❌ כל הטסטים שמנסים להגדיר jobs יכשלו
- ✅ טסטי read-only יכולים לרוץ
- ⚠️ יש retry logic פעיל שיוצר עומס מיותר על השרת

---

## ⚠️ אזהרה: אל תריץ טסטים שמנסים להגדיר jobs!

**טסטים שצריך להימנע מהם עכשיו:**
- כל טסטי `test_configure_*`
- כל טסטי `test_live_monitoring_*`
- כל טסטי `test_singlechannel_*`
- כל טסטי `test_waterfall_*`
- כל טסטי performance/load שמנסים להגדיר jobs
- כל ה-load tests (Locust)

**למה?**
- הם יכשלו עם `503 Service Unavailable`
- הם יוצרים עומס מיותר על השרת (retry logic)
- הם לא מוסיפים ערך במצב הנוכחי

---

## ✅ טסטים שיכולים לרוץ עכשיו

### 1. טסטי Read-Only (API Endpoints)

**טסטים שיכולים לרוץ:**
- `test_get_live_metadata` - בדיקת metadata (יחזיר 0.0, אבל יעבוד)
- `test_get_channels` - רשימת channels (יחזיר 2337 channels)
- `test_get_sensors` - רשימת sensors
- `test_health_check` - בדיקת health
- כל טסטי read-only שלא דורשים configuration

**איך להריץ:**
```bash
# רק טסטי API read-only
pytest tests/integration/api/test_api_endpoints_high_priority.py::TestHealthCheck -v
pytest tests/integration/api/test_api_endpoints_high_priority.py::TestChannelsEndpoint -v
pytest tests/integration/api/test_api_endpoints_high_priority.py::TestSensorsEndpoint -v
pytest tests/integration/api/test_api_endpoints_high_priority.py::TestLiveMetadataEndpoint -v
```

---

### 2. טסטי Infrastructure

**טסטים שיכולים לרוץ:**
- `test_mongodb_connection` - בדיקת חיבור ל-MongoDB
- `test_rabbitmq_connection` - בדיקת חיבור ל-RabbitMQ
- `test_kubernetes_connectivity` - בדיקת חיבור ל-Kubernetes
- כל טסטי infrastructure שלא דורשים configuration

**איך להריץ:**
```bash
# טסטי infrastructure
pytest tests/infrastructure/ -v -k "not configure"
```

---

### 3. טסטי Data Quality (Read-Only)

**טסטים שיכולים לרוץ:**
- `test_mongodb_indexes` - בדיקת indexes
- `test_mongodb_collections` - בדיקת collections
- `test_mongodb_schema` - בדיקת schema
- כל טסטי data quality שלא דורשים configuration

**איך להריץ:**
```bash
# טסטי data quality
pytest tests/data_quality/ -v -k "not configure"
```

---

### 4. טסטי Unit Tests

**טסטים שיכולים לרוץ:**
- כל טסטי unit שלא דורשים חיבור לשרת
- טסטי validation
- טסטי calculations

**איך להריץ:**
```bash
# כל טסטי unit
pytest tests/unit/ -v
```

---

## 🚫 טסטים שלא יכולים לרוץ עכשיו

### טסטים שצריך לדלג עליהם:

```bash
# אל תריץ את הטסטים האלה עכשיו:
# - tests/integration/api/test_configure_*.py
# - tests/integration/api/test_live_monitoring_*.py
# - tests/integration/api/test_singlechannel_*.py
# - tests/integration/api/test_waterfall_*.py
# - tests/integration/performance/test_performance_*.py (אם מנסים להגדיר jobs)
# - tests/load/test_job_capacity_limits.py
# - focus_server_api_load_tests/load_tests/locust_focus_server.py
```

---

## 🎯 איך להריץ את הטסטים

### אפשרות 1: הרצה ידנית (מומלץ עכשיו)

```bash
# רק טסטי read-only
pytest tests/integration/api/test_api_endpoints_high_priority.py::TestHealthCheck -v
pytest tests/integration/api/test_api_endpoints_high_priority.py::TestChannelsEndpoint -v
pytest tests/integration/api/test_api_endpoints_high_priority.py::TestSensorsEndpoint -v
pytest tests/integration/api/test_api_endpoints_high_priority.py::TestLiveMetadataEndpoint -v

# טסטי infrastructure
pytest tests/infrastructure/ -v -k "not configure"

# טסטי data quality
pytest tests/data_quality/ -v -k "not configure"

# טסטי unit
pytest tests/unit/ -v
```

---

### אפשרות 2: הרצה עם markers (מומלץ)

```bash
# רק טסטי health check
pytest -m health_check -v

# רק טסטי infrastructure (ללא configure)
pytest -m infrastructure -v -k "not configure"

# רק טסטי data quality (ללא configure)
pytest -m data_quality -v -k "not configure"

# רק טסטי unit
pytest -m unit -v
```

---

### אפשרות 3: הרצה עם script (אם יש)

```bash
# אם יש script שמסנן טסטי configure
python scripts/run_tests.py --test-type integration --exclude-markers configure
```

---

## 🔧 פתרון זמני: הוסף Health Check לפני הטסטים

**קובץ:** `tests/conftest.py`

```python
@pytest.fixture(scope="session", autouse=True)
def check_metadata_ready(focus_server_api):
    """Skip all configure tests if system is waiting for fiber."""
    import pytest
    
    try:
        metadata = focus_server_api.get_live_metadata_flat()
        if metadata.prr <= 0 or metadata.sw_version == "waiting for fiber":
            pytest.skip("System is waiting for fiber - stopping all configure tests")
    except Exception as e:
        pytest.skip(f"Cannot check metadata - stopping all configure tests: {e}")
```

**יתרונות:**
- הטסטים ידלגו אוטומטית אם המערכת לא מוכנה
- לא יוצר עומס מיותר על השרת
- חוסך זמן

---

## 📊 סיכום - מה להריץ עכשיו

### ✅ טסטים שיכולים לרוץ:

| קטגוריה | טסטים | פקודה |
|---------|-------|-------|
| Health Check | `test_health_check` | `pytest tests/integration/api/test_api_endpoints_high_priority.py::TestHealthCheck -v` |
| Channels | `test_get_channels` | `pytest tests/integration/api/test_api_endpoints_high_priority.py::TestChannelsEndpoint -v` |
| Sensors | `test_get_sensors` | `pytest tests/integration/api/test_api_endpoints_high_priority.py::TestSensorsEndpoint -v` |
| Live Metadata | `test_get_live_metadata` | `pytest tests/integration/api/test_api_endpoints_high_priority.py::TestLiveMetadataEndpoint -v` |
| Infrastructure | כל טסטי infrastructure (ללא configure) | `pytest tests/infrastructure/ -v -k "not configure"` |
| Data Quality | כל טסטי data quality (ללא configure) | `pytest tests/data_quality/ -v -k "not configure"` |
| Unit Tests | כל טסטי unit | `pytest tests/unit/ -v` |

### ❌ טסטים שלא יכולים לרוץ:

| קטגוריה | טסטים | למה |
|---------|-------|-----|
| Configure | כל טסטי `test_configure_*` | דורשים PRR > 0 |
| Live Monitoring | כל טסטי `test_live_monitoring_*` | דורשים PRR > 0 |
| SingleChannel | כל טסטי `test_singlechannel_*` | דורשים PRR > 0 |
| Waterfall | כל טסטי `test_waterfall_*` | דורשים PRR > 0 |
| Performance | טסטי performance שמנסים להגדיר jobs | דורשים PRR > 0 |
| Load Tests | כל ה-load tests | דורשים PRR > 0 |

---

## 🔍 איך לבדוק אם המערכת מוכנה

### בדיקה ידנית:

```bash
# בדוק metadata
curl -k https://10.10.10.100/focus-server/live_metadata | jq

# אם prr > 0 ו-sw_version != "waiting for fiber", המערכת מוכנה
```

### בדיקה דרך Python:

```python
from src.apis.focus_server_api import FocusServerAPI
from src.core.config_manager import ConfigManager

config = ConfigManager()
api = FocusServerAPI(config)

metadata = api.get_live_metadata_flat()
if metadata.prr > 0 and metadata.sw_version != "waiting for fiber":
    print("✅ System is ready!")
else:
    print("❌ System is waiting for fiber")
```

---

## 📝 המלצות

### לטווח הקצר (עכשיו):

1. ✅ **הרץ רק טסטי read-only** - אלה יעבדו גם במצב "waiting for fiber"
2. ⛔ **אל תריץ טסטי configure** - הם יכשלו ויוצרים עומס מיותר
3. 🔍 **בדוק את מצב המערכת** - לפני הרצת טסטים, בדוק אם המערכת מוכנה

### לטווח הארוך (לאחר שהמערכת תהיה מוכנה):

1. 🔧 **הוסף Health Check** - לפני כל טסט configure, בדוק אם המערכת מוכנה
2. 🔧 **עדכן את ה-Retry Logic** - אל תנסה retry על 503 אם המערכת במצב "waiting for fiber"
3. 📝 **תיעד את המצבים השונים** - תיעד איך לטפל ב-"waiting for fiber"

---

## ✅ Checklist לפני הרצת טסטים

- [ ] בדוק את מצב המערכת (`GET /live_metadata`)
- [ ] אם המערכת במצב "waiting for fiber" - הרץ רק טסטי read-only
- [ ] אם המערכת מוכנה (`prr > 0`) - אפשר להריץ את כל הטסטים
- [ ] ודא שאין טסטים אחרים שרצים (retry logic)
- [ ] הרץ את הטסטים לפי הקטגוריות למעלה

---

**עודכן לאחרונה:** 2025-11-08  
**סטטוס:** ⚠️ המערכת במצב "waiting for fiber" - הרץ רק טסטי read-only

