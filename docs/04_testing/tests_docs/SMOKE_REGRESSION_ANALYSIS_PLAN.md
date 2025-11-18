# 📋 תכנית ניתוח Smoke ו-Regression Tests

**תאריך:** 2025-01-27  
**מטרה:** לזהות ולהוסיף markers לכל הטסטים

---

## 🎯 קריטריונים לזיהוי Smoke Tests

### Smoke Tests - טסטים מהירים וקריטיים שצריכים לרוץ לפני כל דבר:

1. **Health Check Tests**
   - `test_health_check.py` - GET /ack endpoint
   - בדיקות בסיסיות של זמינות המערכת

2. **Basic Connectivity Tests**
   - `test_basic_connectivity.py` - MongoDB, K8s, SSH
   - בדיקות חיבור בסיסיות

3. **Critical API Endpoints**
   - `test_api_endpoints_high_priority.py` - GET /channels
   - `test_configure_endpoint.py` - POST /configure (בסיסי)
   - `test_prelaunch_validations.py` - Port availability

4. **Infrastructure Basic Tests**
   - `test_external_connectivity.py` - חיבורים בסיסיים
   - `test_rabbitmq_connectivity.py` - חיבור RabbitMQ

---

## 📊 קריטריונים לזיהוי Regression Tests

### Regression Tests - כל הטסטים (חוץ מ-unit tests):
- כל הטסטים ב-integration/
- כל הטסטים ב-infrastructure/
- כל הטסטים ב-data_quality/
- כל הטסטים ב-performance/
- כל הטסטים ב-load/
- כל הטסטים ב-stress/
- כל הטסטים ב-security/
- כל הטסטים ב-ui/

**לא regression:**
- Unit tests (unit/) - לא צריכים regression marker

---

## 🔍 קטגוריות לזיהוי

### Smoke Tests (מהירים וקריטיים):
- ✅ Health checks
- ✅ Basic connectivity
- ✅ Critical API endpoints
- ✅ Basic configuration validation
- ✅ Infrastructure connectivity

### Regression Tests (כל הטסטים):
- ✅ כל הטסטים חוץ מ-unit tests

---

## 📝 תכנית פעולה

1. **שלב 1:** לזהות טסטים קריטיים ל-smoke
2. **שלב 2:** להוסיף `@pytest.mark.smoke` לטסטים הקריטיים
3. **שלב 3:** להוסיף `@pytest.mark.regression` לכל הטסטים (חוץ מ-unit)
4. **שלב 4:** לוודא שה-markers נוספו נכון

---

**תאריך:** 2025-01-27  
**גרסה:** 1.0

