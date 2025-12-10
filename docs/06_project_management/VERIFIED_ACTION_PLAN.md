# 📋 תוכנית עבודה מאומתת - Focus Server Automation
## מבוסס על בדיקת הקוד בפועל

**תאריך:** 2025-12-09  
**מטרה:** לתקן את הטסטים כך שכשהם ירוקים - זה אומר משהו אמיתי

---

## 🎯 סיכום מהיר - מה צריך לתקן?

| עדיפות | משימה | כמות | מאמץ |
|--------|--------|------|------|
| 🔴 CRITICAL | תיקון `assert True` | 6 מופעים | 2 שעות |
| 🔴 CRITICAL | תיקון Security tests שלא מזריקים payloads | 3 טסטים | 3 שעות |
| 🔴 HIGH | שינוי `frequencyRange.max` ל-1000 | ~60 קבצים | 1 שעה (search/replace) |
| 🔴 HIGH | הפיכת VALIDATION GAP ל-pytest.fail | 5 מופעים | 1 שעה |
| 🟡 MEDIUM | טיפול ב-Summary tests | 11 קבצים | 2 שעות |
| 🟡 MEDIUM | יצירת constants.py | קובץ אחד | 1 שעה |

---

## 🔴 Sprint 1: תיקונים קריטיים (3-4 ימים)

### משימה 1.1: תיקון `assert True` (6 מופעים)

**קבצים לתקן:**

#### 1. `be_focus_server_tests/integration/security/test_input_validation.py`

**שורות 116, 197, 288** - הבעיה: `assert True` תמיד עובר

**בעיה נוספת:** ה-payloads (SQL, XSS) **לא נכנסים לשום שדה!**

```python
# הקוד הנוכחי (שורות 82-116):
for sql_payload in sql_injection_payloads:  # "' OR '1'='1" etc.
    test_payload = base_payload.copy()  # ← ה-SQL לא נכנס לכאן!
    config_request = ConfigureRequest(**test_payload)  # ← payload רגיל
    # ...
    except ValidationError as e:
        assert True, "SQL injection attempt caught by validation"  # ← תמיד עובר!
```

**תיקון נדרש:**

```python
def test_sql_injection_prevention(self, focus_server_api: FocusServerAPI):
    """
    NOTE: Focus Server uses MongoDB (not SQL) and Pydantic validation.
    This test verifies that malicious strings don't cause issues.
    
    LIMITATION: ConfigureRequest has no string fields to inject into.
    Testing injection protection at the data layer level.
    """
    sql_injection_payloads = [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
    ]
    
    # Focus Server API doesn't have string input fields
    # The protection is inherent in Pydantic type validation
    # Document this as a design characteristic, not test a non-existent vulnerability
    
    logger.info("Focus Server uses typed fields (int, dict) - SQL injection not applicable")
    logger.info("Pydantic rejects non-numeric values before they reach the database")
    
    # Test that type validation works
    with pytest.raises((ValueError, ValidationError)):
        bad_payload = {
            "nfftSelection": "' OR '1'='1",  # String where int expected
            "channels": {"min": 1, "max": 50},
            # ...
        }
        ConfigureRequest(**bad_payload)
```

**או אלטרנטיבה - להסיר את הטסטים:**

```python
@pytest.mark.skip(reason="Focus Server uses MongoDB + Pydantic typed fields. "
                         "SQL/XSS injection not applicable to this API.")
def test_sql_injection_prevention(self, focus_server_api):
    pass
```

---

#### 2. `be_focus_server_tests/integration/error_handling/test_network_errors.py`

**שורות 125, 221** - `assert True` בטיפול ב-exceptions

```python
# שורה 125 (נוכחי):
if "timeout" in error_str:
    assert True, "Timeout error handled"  # ← תמיד עובר!

# שורה 221 (נוכחי):
if "connection" in error_str or "refused" in error_str:
    assert True, "Connection refused error handled"  # ← תמיד עובר!
```

**תיקון נדרש:**

```python
# במקום assert True - בדיקות משמעותיות:
if "timeout" in error_str:
    # בדיקות אמיתיות:
    assert hasattr(e, '__str__'), "Error should be readable"
    assert len(str(e)) > 10, "Error message should be informative"
    # או אם יש status_code:
    # assert e.status_code in [504, 408], "Should be timeout error code"
```

**או** - להפוך למוק-based tests:

```python
from unittest.mock import patch, MagicMock

def test_network_timeout(self, focus_server_api):
    """Test timeout handling using mock."""
    with patch.object(focus_server_api, 'configure_streaming_job') as mock_configure:
        mock_configure.side_effect = APIError("Connection timed out", status_code=504)
        
        with pytest.raises(APIError) as exc_info:
            focus_server_api.configure_streaming_job(MagicMock())
        
        assert exc_info.value.status_code == 504
        assert "timeout" in str(exc_info.value).lower()
```

---

#### 3. `be_focus_server_tests/integration/api/test_singlechannel_view_mapping.py`

**שורה 1419** - `assert True  # Always pass`

```python
# נוכחי (סוף הקובץ):
    assert True  # Always pass
```

**תיקון:** להסיר את השורה הזו לחלוטין.

---

### משימה 1.2: תיקון VALIDATION GAP → pytest.fail

**5 מופעים שמזהים באגים אבל לא נכשלים:**

| קובץ | שורה | בעיה מזוהה |
|------|------|------------|
| `test_api_endpoints_additional.py` | 476 | Negative timestamps accepted |
| `test_api_endpoints_additional.py` | 529 | Negative channels accepted |
| `test_api_endpoints_additional.py` | 581 | Negative frequency accepted |
| `test_view_type_validation.py` | 163 | Invalid view_type accepted |
| `test_historic_playback_additional.py` | 547 | Future timestamps accepted |

**תיקון נדרש לכל אחד:**

```python
# נוכחי:
logger.warning("⚠️  VALIDATION GAP: Negative timestamps accepted")
logger.info("✅ TEST PASSED")  # ← הטסט עובר למרות שיש באג!

# אחרי תיקון:
pytest.fail("BUG: Server accepted negative timestamps. "
            "Expected: 400 Bad Request. "
            "Actual: Job created with job_id={response.job_id}")
```

---

### משימה 1.3: יישור Constants לפרודקשן

**הבעיה:** הטסטים משתמשים ב-`frequencyRange.max=500` אבל הפרודקשן הוא **1000 Hz**

**172 מופעים ב-60 קבצים!**

**פתרון:**

1. **ליצור קובץ constants:**

```python
# be_focus_server_tests/constants.py
"""
Production constants for Focus Server.
Source: config/usersettings.new_production_client.json
"""

# From Constraints section
FREQUENCY_MAX_HZ = 1000  # NOT 500!
FREQUENCY_MIN_HZ = 0
SENSORS_RANGE = 2222     # NOT 2500!
MAX_WINDOWS = 30

# Default channels (from Defaults section)
DEFAULT_START_CHANNEL = 11
DEFAULT_END_CHANNEL = 109

# NFFT Options (all valid values)
NFFT_OPTIONS = [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]
DEFAULT_NFFT = 1024
```

2. **Search & Replace:**

```bash
# PowerShell command to find all files:
Get-ChildItem -Path "be_focus_server_tests" -Recurse -Filter "*.py" | 
    Select-String '"max": 500' | 
    Select-Object Path, LineNumber -Unique
```

3. **עדכון הטסטים:**

```python
# לפני:
"frequencyRange": {"min": 0, "max": 500}

# אחרי:
from be_focus_server_tests.constants import FREQUENCY_MAX_HZ
"frequencyRange": {"min": 0, "max": FREQUENCY_MAX_HZ}
```

---

## 🟡 Sprint 2: ניקוי וארגון (2-3 ימים)

### משימה 2.1: טיפול ב-Summary Tests

**11 קבצים עם Summary tests שתמיד עוברים:**

```
be_focus_server_tests\stress\test_extreme_configurations.py
be_focus_server_tests\security\test_malformed_input_handling.py
be_focus_server_tests\integration\performance\test_latency_requirements.py
be_focus_server_tests\integration\load\test_live_investigation_grpc_data.py
be_focus_server_tests\integration\e2e\test_configure_metadata_grpc_flow.py
be_focus_server_tests\integration\api\test_health_check.py
be_focus_server_tests\infrastructure\test_rabbitmq_outage_handling.py
be_focus_server_tests\infrastructure\test_rabbitmq_connectivity.py
be_focus_server_tests\infrastructure\resilience\test_mongodb_pod_resilience.py
be_focus_server_tests\data_quality\test_recordings_classification.py
be_focus_server_tests\integration\test_parallel_investigation_monitoring.py
```

**אפשרויות:**

**אופציה א: למחוק (מומלץ)**
```python
# להסיר את הפונקציות לגמרי
```

**אופציה ב: לסמן כ-skip עם הסבר**
```python
@pytest.mark.skip(reason="Documentation only - not a real test")
def test_health_check_summary():
    pass
```

**אופציה ג: להוריד מ-CI**
```python
@pytest.mark.manual  # לא ירוץ ב-CI
def test_health_check_summary():
    ...
```

---

### משימה 2.2: הוספת טסטי NFFT מלאים

**הבעיה:** רוב הטסטים משתמשים רק ב-`nfftSelection=1024`

**הפרודקשן תומך ב-10 ערכים:** `[128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]`

**להוסיף:**

```python
# be_focus_server_tests/integration/api/test_nfft_all_values.py

import pytest
from be_focus_server_tests.constants import NFFT_OPTIONS

@pytest.mark.parametrize("nfft", NFFT_OPTIONS)
def test_valid_nfft_values(focus_server_api, nfft):
    """Test all valid NFFT values are accepted."""
    config = ConfigureRequest(
        nfftSelection=nfft,
        channels={"min": 11, "max": 109},
        frequencyRange={"min": 0, "max": 1000},
        displayTimeAxisDuration=10,
        displayInfo={"height": 1000},
        start_time=None,
        end_time=None,
        view_type=ViewType.MULTICHANNEL
    )
    
    response = focus_server_api.configure_streaming_job(config)
    assert response.job_id is not None, f"NFFT={nfft} should be accepted"
    
    # Cleanup
    focus_server_api.cancel_job(response.job_id)


@pytest.mark.parametrize("invalid_nfft", [100, 500, 1000, 127, 65537, -1, 0])
def test_invalid_nfft_values_rejected(focus_server_api, invalid_nfft):
    """Test invalid NFFT values are rejected."""
    config = ConfigureRequest(
        nfftSelection=invalid_nfft,
        channels={"min": 11, "max": 109},
        frequencyRange={"min": 0, "max": 1000},
        # ...
    )
    
    with pytest.raises((ValidationError, APIError)) as exc:
        focus_server_api.configure_streaming_job(config)
    
    # If no exception - it's a bug!
    pytest.fail(f"Server accepted invalid NFFT={invalid_nfft}")
```

---

## 📋 רשימת פעולות מסודרת

### עכשיו (היום):

- [ ] **תיקון `assert True`** - 6 מופעים (2 שעות)
  - [ ] `test_input_validation.py` - 3 מופעים
  - [ ] `test_network_errors.py` - 2 מופעים  
  - [ ] `test_singlechannel_view_mapping.py` - 1 מופע

### השבוע:

- [ ] **תיקון VALIDATION GAP** - 5 מופעים (1 שעה)
- [ ] **יצירת `constants.py`** (30 דקות)
- [ ] **עדכון frequencyRange מ-500 ל-1000** (2 שעות - batch update)

### שבוע הבא:

- [ ] **טיפול ב-Summary tests** - 11 קבצים
- [ ] **הוספת טסטי NFFT מלאים**
- [ ] **בדיקת pytest.skip patterns** - 44 קבצים

---

## ⚠️ הערות חשובות

### לגבי Security Tests (SQL/XSS):

Focus Server הוא **backend API** שמשתמש ב-:
- **MongoDB** (לא SQL!)
- **Pydantic** עם typed fields (int, dict)
- **gRPC** לתקשורת

**SQL Injection לא רלוונטי** כי:
1. אין SQL - יש MongoDB
2. אין שדות string ב-ConfigureRequest להזריק אליהם
3. Pydantic דוחה כל מה שלא מתאים לטיפוס

**ההמלצה:** להסיר או לשנות את הטסטים האלה ל:
- Type validation tests (Pydantic rejects wrong types)
- או להסיר לחלוטין עם הערה ב-README

### לגבי XSS Tests:

Focus Server הוא **backend API** שמחזיר **JSON/Protobuf** - לא HTML.

**XSS לא רלוונטי** כי:
1. אין HTML rendering
2. אין browser context
3. התשובות הן data structures, לא דפי web

---

## 🚀 פקודות להתחלה

```powershell
# 1. מצא את כל assert True:
grep -rn "assert True" be_focus_server_tests/

# 2. מצא את כל VALIDATION GAP:
grep -rn "VALIDATION GAP" be_focus_server_tests/

# 3. מצא frequencyRange.max=500:
grep -rn '"max": 500' be_focus_server_tests/ | wc -l

# 4. מצא Summary tests:
grep -rn "This test always passes" be_focus_server_tests/
```

---

**אתה רוצה שאתחיל לתקן את הקבצים?**

