# 📋 API Migration Summary - 23 אוקטובר 2025

**מועד:** 23 אוקטובר 2025, 17:30+  
**סטטוס:** 🟡 **בביצוע**  
**מטרה:** להעביר כל הטסטים מAPI חדש (`POST /config/{task_id}`) לAPI ישן (`POST /configure`)

---

## 🎯 **סיבה למיגרציה**

השרת הנוכחי (`pzlinux:10.7.122`) תומך רק ב-API ישן:
- ✅ `POST /configure` - זמין
- ❌ `POST /config/{task_id}` - **לא זמין!**

**החלטת רועי:** השרת יישאר כמו שהוא, אז הטסטים צריכים להתאים.

---

## 🔄 **שינויים נדרשים**

### **1. Imports:**
```python
# ❌ לפני:
from src.models.focus_server_models import ConfigTaskRequest, ConfigTaskResponse
from src.utils.helpers import generate_task_id, generate_config_payload

# ✅ אחרי:
from src.models.focus_server_models import ConfigureRequest, ConfigureResponse, ViewType
```

### **2. Payload Structure:**
```python
# ❌ לפני (canvasInfo/sensors):
{
    "canvasInfo": {"height": 1000},
    "sensors": {"min": 1, "max": 50},
    ...
}

# ✅ אחרי (displayInfo/channels):
{
    "displayInfo": {"height": 1000},
    "channels": {"min": 1, "max": 50},
    "view_type": ViewType.MULTICHANNEL,
    ...
}
```

### **3. API Calls:**
```python
# ❌ לפני:
task_id = generate_task_id("test")
config_request = ConfigTaskRequest(**payload)
response = focus_server_api.config_task(task_id, config_request)

# ✅ אחרי:
config_request = ConfigureRequest(**payload)
response = focus_server_api.configure_streaming_job(config_request)
job_id = response.job_id
```

### **4. Response Handling:**
```python
# ❌ לפני:
if response.status == "Config received successfully":
    ...

# ✅ אחרי:
if hasattr(response, 'job_id') and response.job_id:
    ...
```

### **5. Task/Job ID Usage:**
```python
# ❌ לפני:
task_id = generate_task_id("test")
waterfall = api.get_waterfall(task_id, ...)

# ✅ אחרי:
job_id = response.job_id  # מהתגובה של configure
waterfall = api.get_waterfall(job_id, ...)
```

---

## 📊 **Progress**

| File | Status | Notes |
|------|--------|-------|
| `test_performance_high_priority.py` | ✅ **Done** | 595 שורות, 12 תיקונים |
| `test_dynamic_roi_adjustment.py` | 🟡 **In Progress** | - |
| `test_spectrogram_pipeline.py` | ⏳ **Pending** | - |
| `test_live_monitoring_flow.py` | ⏳ **Pending** | - |
| `test_historic_playback_flow.py` | ⏳ **Pending** | - |
| **Total** | **20%** | **1/5 קבצים** |

---

## ⚠️  **בעיות ידועות**

### **1. Helper Functions:**

הפונקציה `generate_config_payload()` מחזירה payload בפורמט הישן.

**פתרון:**
- צור payload ידנית בכל טסט
- או עדכן את `src/utils/helpers.py`

### **2. Waterfall API:**

יש להניח שגם Waterfall API השתנה, אבל לא בדקנו את זה עדיין.

**TODO:** בדוק:
```python
# האם זה עובד?
response = api.get_waterfall(job_id, row_count=100)
```

---

## 🎯 **עדיפויות**

### **HIGH:**
1. ✅ `test_performance_high_priority.py` - מקיף ביותר
2. 🟡 `test_dynamic_roi_adjustment.py` - RabbitMQ + ROI
3. 🟡 `test_historic_playback_flow.py` - Historic mode

### **MEDIUM:**
4. ⏳ `test_live_monitoring_flow.py` - Live mode
5. ⏳ `test_spectrogram_pipeline.py` - Spectrogram

---

## 🧪 **טסטים נוספים צריכים עדכון?**

כן! יש קבצים נוספים שעשויים להשתמש ב-API ישן:

```bash
# מצא את כל השימושים:
grep -r "config_task\|ConfigTaskRequest" tests/ --include="*.py"
```

**קבצים אפשריים:**
- `tests/api/test_metadata.py`
- `tests/integration/test_task_lifecycle.py`
- `tests/integration/test_waterfall.py`
- `tests/integration/test_sensors.py`

---

## 📚 **מסמכים קשורים**

- [`FOCUS_SERVER_API_ENDPOINTS.md`](./FOCUS_SERVER_API_ENDPOINTS.md) - כל ה-endpoints הזמינים
- [`PERFORMANCE_TESTS_STATUS.md`](../integration/performance/PERFORMANCE_TESTS_STATUS.md) - למה לא עובד API חדש

---

## 🚀 **זמן משוער**

| קובץ | שורות | זמן |
|------|-------|-----|
| ✅ test_performance_high_priority.py | 595 | 30 דק |
| test_dynamic_roi_adjustment.py | 622 | 30 דק |
| test_spectrogram_pipeline.py | 379 | 20 דק |
| test_live_monitoring_flow.py | 627 | 30 דק |
| test_historic_playback_flow.py | 591 | 30 דק |
| **Total** | **2,814** | **~2.5 שעות** |

---

**נוצר:** 23 אוקטובר 2025, 17:40  
**עודכן:** 23 אוקטובר 2025, 17:40  
**סטטוס:** 🟡 **בביצוע - 20% הושלם**

