# 🧪 מדריך בדיקות Alerts מה-Backend

**תאריך:** 13 בנובמבר 2025  
**מטרה:** מדריך מקיף לבדיקות אוטומטיות של תהליכי alerts מה-Backend

---

## 📋 תוכן עניינים

1. [סקירה כללית](#סקירה-כללית)
2. [קטגוריות בדיקות](#קטגוריות-בדיקות)
3. [הרצת בדיקות](#הרצת-בדיקות)
4. [תרחישים חיוביים](#תרחישים-חיוביים)
5. [תרחישים שליליים](#תרחישים-שליליים)
6. [Edge Cases](#edge-cases)
7. [תרחישי עומסים](#תרחישי-עומסים)
8. [תרחישי Performance](#תרחישי-performance)
9. [דוגמאות שימוש](#דוגמאות-שימוש)

---

## 🎯 סקירה כללית

### מטרת הבדיקות:

בדיקות מקיפות של תהליכי alerts מה-Backend, כולל:
- יצירת alerts
- עיבוד דרך RabbitMQ
- אחסון ב-MongoDB
- ביצועים ותקינות

### מיקום הקבצים:

```
be_focus_server_tests/integration/alerts/
├── __init__.py
├── test_alert_generation_positive.py      # תרחישים חיוביים
├── test_alert_generation_negative.py      # תרחישים שליליים
├── test_alert_generation_edge_cases.py    # Edge cases
├── test_alert_generation_load.py          # תרחישי עומסים
├── test_alert_generation_performance.py   # תרחישי performance
└── README.md
```

---

## 📊 קטגוריות בדיקות

### 1. תרחישים חיוביים ✅

**קובץ:** `test_alert_generation_positive.py`

**בדיקות:**
- ✅ PZ-15000: יצירת SD Alert מוצלחת
- ✅ PZ-15001: יצירת SC Alert מוצלחת
- ✅ PZ-15002: יצירת מספר Alerts
- ✅ PZ-15003: רמות חומרה שונות
- ✅ PZ-15004: עיבוד דרך RabbitMQ
- ✅ PZ-15005: אחסון ב-MongoDB

**דוגמה:**
```python
@pytest.mark.xray("PZ-15000")
def test_successful_sd_alert_generation(self, config_manager):
    """
    בדיקה ש-SD Alert נוצר בהצלחה
    """
    alert_payload = {
        "alertsAmount": 1,
        "dofM": 4163,
        "classId": 104,  # SD
        "severity": 3,
        "alertIds": ["test-sd-123"]
    }
    # Publish alert...
```

---

### 2. תרחישים שליליים ❌

**קובץ:** `test_alert_generation_negative.py`

**בדיקות:**
- ❌ PZ-15010: Class ID לא תקין
- ❌ PZ-15011: Severity לא תקין
- ❌ PZ-15012: טווח DOF לא תקין
- ❌ PZ-15013: שדות חובה חסרים
- ❌ PZ-15014: כשל חיבור RabbitMQ
- ❌ PZ-15015: כשל חיבור MongoDB
- ❌ PZ-15016: פורמט Alert ID לא תקין
- ❌ PZ-15017: Alert IDs כפולים

**דוגמה:**
```python
@pytest.mark.xray("PZ-15010")
def test_invalid_class_id(self, config_manager):
    """
    בדיקה ש-Class ID לא תקין נדחה
    """
    invalid_class_ids = [0, 1, 100, 105, 999, -1]
    
    for invalid_class_id in invalid_class_ids:
        alert_payload = {
            "classId": invalid_class_id,  # לא תקין
            # ...
        }
        # Should raise exception
        with pytest.raises((ValueError, APIError)):
            # Publish alert...
```

---

### 3. Edge Cases 🔍

**קובץ:** `test_alert_generation_edge_cases.py`

**בדיקות:**
- 🔍 PZ-15020: ערכי DOF גבוליים (0, 1, 2221, 2222)
- 🔍 PZ-15021: Severity מינימום/מקסימום (1, 3)
- 🔍 PZ-15022: alertsAmount = 0
- 🔍 PZ-15023: Alert ID מאוד ארוך
- 🔍 PZ-15024: Alerts מקבילים עם אותו DOF
- 🔍 PZ-15025: Alerts רצופים מהירים
- 🔍 PZ-15026: Alert עם כל השדות במקסימום
- 🔍 PZ-15027: Alert עם שדות מינימום בלבד

**דוגמה:**
```python
@pytest.mark.xray("PZ-15020")
def test_boundary_dof_values(self, config_manager):
    """
    בדיקת ערכי DOF גבוליים
    """
    boundary_dofs = [0, 1, 2221, 2222]
    
    for dof in boundary_dofs:
        alert_payload = {
            "dofM": dof,  # ערך גבולי
            # ...
        }
```

---

### 4. תרחישי עומסים 📈

**קובץ:** `test_alert_generation_load.py`

**בדיקות:**
- 📈 PZ-15030: עומס נפח גבוה (1000+ alerts)
- 📈 PZ-15031: עומס מתמשך (10+ דקות)
- 📈 PZ-15032: עומס התפרצות (500 alerts בו-זמנית)
- 📈 PZ-15033: עומס סוגי alerts מעורבים
- 📈 PZ-15034: קיבולת Queue של RabbitMQ
- 📈 PZ-15035: עומס כתיבה ל-MongoDB

**דוגמה:**
```python
@pytest.mark.xray("PZ-15030")
def test_high_volume_load(self, config_manager):
    """
    בדיקת עומס נפח גבוה
    """
    num_alerts = 1000
    min_success_rate = 0.99  # 99%
    
    for i in range(num_alerts):
        # Publish alert...
        success_count += 1
    
    success_rate = success_count / num_alerts
    assert success_rate >= min_success_rate
```

---

### 5. תרחישי Performance ⚡

**קובץ:** `test_alert_generation_performance.py`

**בדיקות:**
- ⚡ PZ-15040: Response Time (Mean < 100ms, P95 < 200ms)
- ⚡ PZ-15041: Throughput (>= 100 alerts/sec)
- ⚡ PZ-15042: Latency (Mean < 50ms, P95 < 100ms)
- ⚡ PZ-15043: Resource Usage (CPU < 80%, Memory < 500MB)
- ⚡ PZ-15044: End-to-End Performance (Mean < 200ms)
- ⚡ PZ-15045: RabbitMQ Performance (Publish < 10ms)
- ⚡ PZ-15046: MongoDB Performance (Write < 20ms, Read < 10ms)

**דוגמה:**
```python
@pytest.mark.xray("PZ-15040")
def test_alert_response_time(self, config_manager):
    """
    בדיקת Response Time
    """
    response_times = []
    
    for i in range(100):
        start_time = time.time()
        # Publish alert...
        response_time = (time.time() - start_time) * 1000
        response_times.append(response_time)
    
    mean_time = mean(response_times)
    assert mean_time < 100, f"Mean {mean_time:.2f}ms exceeds 100ms"
```

---

## 🚀 הרצת בדיקות

### הרצת כל הבדיקות:
```bash
pytest be_focus_server_tests/integration/alerts/ -v
```

### הרצת קטגוריה ספציפית:
```bash
# תרחישים חיוביים
pytest be_focus_server_tests/integration/alerts/test_alert_generation_positive.py -v

# תרחישים שליליים
pytest be_focus_server_tests/integration/alerts/test_alert_generation_negative.py -v

# Edge cases
pytest be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py -v

# עומסים
pytest be_focus_server_tests/integration/alerts/test_alert_generation_load.py -v

# Performance
pytest be_focus_server_tests/integration/alerts/test_alert_generation_performance.py -v
```

### הרצה עם Markers:
```bash
# רק בדיקות חיוביות
pytest be_focus_server_tests/integration/alerts/ -m positive -v

# רק בדיקות שליליות
pytest be_focus_server_tests/integration/alerts/ -m negative -v

# רק edge cases
pytest be_focus_server_tests/integration/alerts/ -m edge_cases -v

# רק בדיקות עומס
pytest be_focus_server_tests/integration/alerts/ -m load -v

# רק בדיקות performance
pytest be_focus_server_tests/integration/alerts/ -m performance -v
```

### הרצה עם Xray Marker:
```bash
# בדיקה ספציפית לפי Xray ID
pytest be_focus_server_tests/integration/alerts/ -k "PZ-15000" -v
```

---

## 📝 דרישות

### Dependencies:
```bash
pip install pika pymongo psutil
```

### Configuration:
הבדיקות משתמשות ב-`config/environments.yaml`:
- RabbitMQ connection settings
- MongoDB connection settings
- Site ID (`prisma-210-1000`)

---

## 🔧 דוגמאות שימוש

### דוגמה 1: בדיקת Alert חיובי

```python
def test_successful_alert():
    alert_payload = {
        "alertsAmount": 1,
        "dofM": 4163,
        "classId": 104,
        "severity": 3,
        "alertIds": ["test-123"]
    }
    
    # Publish to RabbitMQ
    # Verify in MongoDB
    # Verify processing
```

### דוגמה 2: בדיקת עומס

```python
def test_load():
    num_alerts = 1000
    
    for i in range(num_alerts):
        # Publish alert
        pass
    
    # Verify success rate >= 99%
```

### דוגמה 3: בדיקת Performance

```python
def test_performance():
    response_times = []
    
    for i in range(100):
        start = time.time()
        # Publish alert
        response_times.append((time.time() - start) * 1000)
    
    assert mean(response_times) < 100  # ms
```

---

## 📊 סיכום

### כיסוי בדיקות:

- ✅ **תרחישים חיוביים:** 6 בדיקות
- ❌ **תרחישים שליליים:** 8 בדיקות
- 🔍 **Edge Cases:** 8 בדיקות
- 📈 **עומסים:** 6 בדיקות
- ⚡ **Performance:** 7 בדיקות

**סה"כ:** 35 בדיקות מקיפות

### Xray Coverage:

- PZ-15000 - PZ-15005: Positive
- PZ-15010 - PZ-15017: Negative
- PZ-15020 - PZ-15027: Edge Cases
- PZ-15030 - PZ-15035: Load
- PZ-15040 - PZ-15046: Performance

---

**תאריך עדכון:** 13 בנובמבר 2025  
**גרסה:** 1.0.0

