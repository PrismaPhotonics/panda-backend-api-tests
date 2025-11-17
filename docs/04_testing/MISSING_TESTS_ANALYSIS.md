# 📊 ניתוח מפורט: טסטים חסרים באוטומציה

## סיכום ראשוני
- **סה"כ טסטים ב-xray_tests_list.txt**: 126
- **טסטים מכוסים באוטומציה**: 98
- **טסטים חסרים**: 28

---

## ✅ טסטים שכן מופיעים באוטומציה (בטסטים משולבים)

הטסטים הבאים **כן קיימים** באוטומציה אבל מופיעים עם מספר markers:

### 1. PZ-13762 - API – GET /channels
- **מיקום**: `test_api_endpoints_high_priority.py` שורה 40
- **Marker**: `@pytest.mark.xray("PZ-13895", "PZ-13762")`
- ✅ **מכוסה**

### 2. PZ-13766 - POST /recordings_in_time_range
- **מיקום**: `test_api_endpoints_additional.py` שורה 323
- **Marker**: `@pytest.mark.xray("PZ-13564", "PZ-13766")`
- ✅ **מכוסה**

### 3. PZ-13769 - Security – Malformed Input Handling
- **מיקום**: `test_malformed_input_handling.py` שורה 44
- **Marker**: `@pytest.mark.xray("PZ-13572", "PZ-13769")`
- ✅ **מכוסה**

### 4. PZ-13863 - Historic Playback Standard 5-Minute
- **מיקום**: `test_prelaunch_validations.py` שורה 274
- **Marker**: `@pytest.mark.xray("PZ-13548", "PZ-13863")`
- ✅ **מכוסה**

### 5. PZ-13873 - Valid Configuration All Parameters
- **מיקום**: `test_prelaunch_validations.py` שורה 222
- **Marker**: `@pytest.mark.xray("PZ-13547", "PZ-13873")`
- ✅ **מכוסה**

### 6. PZ-13903 - Frequency Range Nyquist Limit
- **מיקום**: `test_prelaunch_validations.py` שורה 586
- **Marker**: `@pytest.mark.xray("PZ-13877", "PZ-13903")`
- ✅ **מכוסה**

### 7. PZ-13684 - node4 Schema Validation
- **מיקום**: `test_mongodb_indexes_and_schema.py` שורה 299
- **Marker**: `@pytest.mark.xray("PZ-13811", "PZ-13684")`
- ✅ **מכוסה**

### 8. PZ-13685 - Recordings Metadata Completeness
- **מיקום**: `test_mongodb_indexes_and_schema.py` שורה 344
- **Marker**: `@pytest.mark.xray("PZ-13812", "PZ-13685")`
- ✅ **מכוסה**

### 9. SingleChannel Tests משפחה
כל הטסטים הבאים מופיעים ב-`test_singlechannel_view_mapping.py`:
- **PZ-13832**: שורה 245 - `@pytest.mark.xray("PZ-13814", "PZ-13832")`
- **PZ-13833**: שורה 283 - `@pytest.mark.xray("PZ-13815", "PZ-13833")`
- **PZ-13854**: שורה 528 - `@pytest.mark.xray("PZ-13819", "PZ-13854")`
- **PZ-13855**: שורה 626 - `@pytest.mark.xray("PZ-13821", "PZ-13855")`
- **PZ-13836**: שורה 937 - `@pytest.mark.xray("PZ-13835", "PZ-13836", "PZ-13837")`
- **PZ-13837**: שורה 937 - `@pytest.mark.xray("PZ-13835", "PZ-13836", "PZ-13837")`

### 10. Historic Playback Tests
- **PZ-13865**: `test_historic_playback_additional.py` שורה 53
- **Marker**: `@pytest.mark.xray("PZ-13864", "PZ-13865")`
- ✅ **מכוסה**

### 11. Validation Tests
כל הטסטים הבאים מופיעים ב-`test_api_endpoints_additional.py`:
- **PZ-13552**: שורה 404 - `@pytest.mark.xray("PZ-13759", "PZ-13552")`
- **PZ-13554**: שורה 457 - `@pytest.mark.xray("PZ-13760", "PZ-13554")`
- **PZ-13555**: שורה 506 - `@pytest.mark.xray("PZ-13761", "PZ-13555")`
- **PZ-13561**: שורה 137 - `@pytest.mark.xray("PZ-13764", "PZ-13561")`
- **PZ-13562**: שורה 187 - `@pytest.mark.xray("PZ-13765", "PZ-13562")`

### 12. Mongo Outage Tests
- **PZ-13603, PZ-13604**: `test_mongodb_outage_resilience.py` שורה 152
- **Marker**: `@pytest.mark.xray("PZ-13767", "PZ-13603", "PZ-13604")`
- ✅ **מכוסים**

---

## ❌ טסטים שלא מכוסים - רק אלו באמת חסרים

### SingleChannel NFFT Validation
- **PZ-13857**: Integration - SingleChannel NFFT Validation
- **PZ-13855**: Integration - SingleChannel Canvas Height Validation (אבל ✅ PZ-13855 כן מופיע ב-shared marker)

### SingleChannel Edge Cases
- **PZ-13822**: API – SingleChannel Rejects Invalid NFFT Value

### Orchestration Tests
- **PZ-13600**: Integration – Invalid configure does not launch orchestration
- **PZ-13601**: Integration – History with empty window returns 400 and no side effects

### API Tests
- **PZ-13560**: API – GET /channels
- **PZ-13766**: API – POST /recordings_in_time_range – Returns Recording Windows (אבל ✅ PZ-13766 מופיע עם PZ-13564)

### Historic Playback
- **PZ-13863**: Integration – Historic Playback - Standard 5-Minute Range (אבל ✅ PZ-13863 מופיע עם PZ-13548)
- **PZ-13865**: Integration – Historic Playback - Short Duration (אבל ✅ PZ-13865 מופיע עם PZ-13864)

---

## 📝 מסקנה

מתוך 28 הטסטים שהוגדרו כ"חסרים", **18+ טסטים כן מכוסים** אבל מופיעים עם מספר markers.

**הטסטים שבאמת חסרים הם רק:**
1. PZ-13857 - SingleChannel NFFT Validation
2. PZ-13822 - SingleChannel Rejects Invalid NFFT
3. PZ-13600 - Invalid configure doesn't launch
4. PZ-13601 - History with empty window
5. PZ-13560 - API GET /channels (פשוט)

**סה"כ באמת חסרים: ~5 טסטים**

