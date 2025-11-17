# ⚡ Quick Start - איך להריץ את האוטומציה עכשיו

**תאריך:** 2025-11-08  
**מצב:** ⚠️ המערכת במצב "waiting for fiber"

---

## 🎯 פקודות מהירות

### ✅ טסטים שיכולים לרוץ עכשיו:

```bash
# 1. Health Check
pytest tests/integration/api/test_api_endpoints_high_priority.py::TestHealthCheck -v

# 2. Channels Endpoint
pytest tests/integration/api/test_api_endpoints_high_priority.py::TestChannelsEndpoint -v

# 3. Sensors Endpoint
pytest tests/integration/api/test_api_endpoints_high_priority.py::TestSensorsEndpoint -v

# 4. Live Metadata Endpoint
pytest tests/integration/api/test_api_endpoints_high_priority.py::TestLiveMetadataEndpoint -v

# 5. כל טסטי Infrastructure (ללא configure)
pytest tests/infrastructure/ -v -k "not configure"

# 6. כל טסטי Data Quality (ללא configure)
pytest tests/data_quality/ -v -k "not configure"

# 7. כל טסטי Unit
pytest tests/unit/ -v
```

---

## ❌ טסטים שלא יכולים לרוץ עכשיו:

```bash
# אל תריץ את הטסטים האלה - הם יכשלו:
# - כל טסטי configure
# - כל טסטי live_monitoring
# - כל טסטי singlechannel
# - כל טסטי waterfall
# - כל טסטי performance שמנסים להגדיר jobs
# - כל ה-load tests
```

---

## 🔍 בדיקה מהירה - האם המערכת מוכנה?

```bash
# בדוק metadata
curl -k https://10.10.10.100/focus-server/live_metadata | jq

# אם prr > 0 ו-sw_version != "waiting for fiber" - המערכת מוכנה!
# אם prr = 0.0 ו-sw_version = "waiting for fiber" - המערכת לא מוכנה
```

---

## 📋 סיכום מהיר

| מצב | מה להריץ | מה לא להריץ |
|-----|----------|-------------|
| **"waiting for fiber"** (עכשיו) | ✅ Read-only tests<br>✅ Infrastructure tests<br>✅ Data quality tests<br>✅ Unit tests | ❌ Configure tests<br>❌ Live monitoring tests<br>❌ SingleChannel tests<br>❌ Waterfall tests<br>❌ Performance tests<br>❌ Load tests |
| **מוכן** (`prr > 0`) | ✅ כל הטסטים | - |

---

## 🚀 הרצה מהירה (מומלץ עכשיו)

```bash
# הרץ רק טסטי read-only
pytest tests/integration/api/test_api_endpoints_high_priority.py::TestHealthCheck tests/integration/api/test_api_endpoints_high_priority.py::TestChannelsEndpoint tests/integration/api/test_api_endpoints_high_priority.py::TestSensorsEndpoint -v

# או עם markers
pytest -m "health_check or api" -v -k "not configure"
```

---

**ראה מדריך מפורט:** `docs/02_user_guides/HOW_TO_RUN_TESTS_WAITING_FOR_FIBER.md`

