# איפה כל הטסטים? מדריך מלא
**תאריך:** 16 אוקטובר 2025  
**מיקום:** `C:\Projects\focus_server_automation\tests`

---

## 📊 סיכום כללי

✅ **סה"כ קבצי טסטים:** 16 קבצים  
✅ **המבנה מאורגן!** הטסטים מחולקים לפי קטגוריות לוגיות

---

## 📁 מבנה התיקיות - איפה מה נמצא?

### 1️⃣ **Integration Tests** (API & Flows) 🔗
📂 `tests/integration/`

```
tests/integration/
├── configuration/
│   └── test_spectrogram_pipeline.py          ✅ ~40 טסטים (NFFT, Frequency, Config)
├── historic_playback/
│   └── test_historic_playback_flow.py         ✅ ~25 טסטים (Historic playback)
├── live_monitoring/
│   └── test_live_monitoring_flow.py           ✅ ~30 טסטים (Live monitoring)
├── roi_adjustment/
│   └── test_dynamic_roi_adjustment.py         ✅ ~30 טסטים (ROI changes)
└── singlechannel/
    └── test_singlechannel_view_mapping.py     ✅ ~30 טסטים (Single channel view)
```

**סה"כ:** ~155 טסטי אינטגרציה

---

### 2️⃣ **Infrastructure Tests** (K8s, Connectivity) 🏗️
📂 `tests/infrastructure/`

```
tests/infrastructure/
├── test_basic_connectivity.py                ✅ K8s, Focus Server, MongoDB
├── test_external_connectivity.py             ✅ External services
├── test_mongodb_outage_resilience.py         ✅ MongoDB outage scenarios
└── test_pz_integration.py                    ✅ PZ integration
```

**סה"כ:** ~15 טסטי תשתית

---

### 3️⃣ **Data Quality Tests** (MongoDB Schema) 📊
📂 `tests/data_quality/`

```
tests/data_quality/
└── test_mongodb_data_quality.py              ✅ 6 טסטים (Schema, Indexes, Lifecycle)
```

**טסטים:**
- ✅ `test_required_collections_exist`
- ✅ `test_recording_schema_validation`
- ✅ `test_recordings_have_all_required_metadata`
- ✅ `test_mongodb_indexes_exist_and_optimal`
- ✅ `test_deleted_recordings_marked_properly`
- ✅ `test_historical_vs_live_recordings`

---

### 4️⃣ **Unit Tests** (Validations, Models) 🧪
📂 `tests/unit/`

```
tests/unit/
├── test_basic_functionality.py               ✅ Basic functionality
├── test_config_loading.py                    ✅ Configuration loading
├── test_models_validation.py                 ✅ Pydantic models
└── test_validators.py                        ✅ Validators
```

**סה"כ:** ~20 unit tests

---

### 5️⃣ **UI Tests** (Playwright) 🎭
📂 `tests/ui/`

```
tests/ui/
└── generated/
    ├── test_button_interactions.py           ✅ UI button tests
    └── test_form_validation.py               ✅ UI form tests
```

**סה"כ:** ~5 UI tests

---

## 🎯 סיכום לפי קטגוריות

| קטגוריה | תיקייה | קבצים | טסטים משוערים |
|---------|---------|-------|----------------|
| **Integration** | `tests/integration/` | 5 | ~155 |
| **Infrastructure** | `tests/infrastructure/` | 4 | ~15 |
| **Data Quality** | `tests/data_quality/` | 1 | ~6 |
| **Unit Tests** | `tests/unit/` | 4 | ~20 |
| **UI Tests** | `tests/ui/` | 2 | ~5 |
| **סה"כ** | | **16** | **~201** |

---

## 🔍 איך למצוא טסט ספציפי?

### לפי שם הטסט הישן:

| טסט ישן | מיקום חדש |
|---------|-----------|
| `tests/integration/api/test_dynamic_roi_adjustment.py` | ✅ `tests/integration/roi_adjustment/test_dynamic_roi_adjustment.py` |
| `tests/integration/api/test_historic_playback_flow.py` | ✅ `tests/integration/historic_playback/test_historic_playback_flow.py` |
| `tests/integration/api/test_live_monitoring_flow.py` | ✅ `tests/integration/live_monitoring/test_live_monitoring_flow.py` |
| `tests/integration/api/test_spectrogram_pipeline.py` | ✅ `tests/integration/configuration/test_spectrogram_pipeline.py` |
| `tests/integration/api/test_singlechannel_view_mapping.py` | ✅ `tests/integration/singlechannel/test_singlechannel_view_mapping.py` |
| `tests/integration/infrastructure/test_mongodb_data_quality.py` | ✅ `tests/data_quality/test_mongodb_data_quality.py` |

---

## 🚀 פקודות להרצת טסטים

### הרץ הכל:
```powershell
cd C:\Projects\focus_server_automation
pytest tests/ -v
```

### הרץ לפי קטגוריה:

```powershell
# Integration tests בלבד
pytest tests/integration/ -v

# Infrastructure tests בלבד
pytest tests/infrastructure/ -v

# Data Quality tests בלבד
pytest tests/data_quality/ -v

# Unit tests בלבד
pytest tests/unit/ -v

# UI tests בלבד
pytest tests/ui/ -v
```

### הרץ טסט ספציפי:

```powershell
# ROI tests
pytest tests/integration/roi_adjustment/test_dynamic_roi_adjustment.py -v

# Historic playback tests
pytest tests/integration/historic_playback/test_historic_playback_flow.py -v

# Live monitoring tests
pytest tests/integration/live_monitoring/test_live_monitoring_flow.py -v

# MongoDB data quality tests
pytest tests/data_quality/test_mongodb_data_quality.py -v
```

### הרץ קלאס ספציפי:

```powershell
pytest tests/integration/roi_adjustment/test_dynamic_roi_adjustment.py::TestDynamicROIHappyPath -v
```

### הרץ טסט בודד:

```powershell
pytest tests/integration/roi_adjustment/test_dynamic_roi_adjustment.py::TestDynamicROIHappyPath::test_send_roi_change_command -v
```

---

## 📂 למה המבנה החדש טוב יותר?

### לפני (מבנה ישן):
```
tests/
└── integration/
    ├── api/
    │   ├── test_dynamic_roi_adjustment.py
    │   ├── test_historic_playback_flow.py
    │   ├── test_live_monitoring_flow.py
    │   ├── test_spectrogram_pipeline.py
    │   └── test_singlechannel_view_mapping.py
    └── infrastructure/
        └── test_mongodb_data_quality.py
```

❌ **בעיות:**
- הכל בתיקייה אחת (`api/`)
- לא ברור מה שייך למה
- קשה למצוא טסטים ספציפיים

---

### אחרי (מבנה חדש):
```
tests/
├── integration/
│   ├── roi_adjustment/          ← ROI tests
│   ├── historic_playback/       ← Historic tests
│   ├── live_monitoring/         ← Live tests
│   ├── configuration/           ← Config tests
│   └── singlechannel/           ← Single channel tests
├── infrastructure/              ← Infrastructure tests
├── data_quality/                ← MongoDB tests
├── unit/                        ← Unit tests
└── ui/                          ← UI tests
```

✅ **יתרונות:**
- **ארגון לוגי** - כל נושא בתיקייה נפרדת
- **קל למצוא** - יודע בדיוק איפה לחפש
- **סקלביליות** - קל להוסיף טסטים חדשים
- **נקי** - כל תיקייה עם `__init__.py` ו-`README.md`

---

## 🆕 תיקיות חדשות (מוכנות לטסטים)

```
tests/
├── performance/                 📊 Performance & SLA tests (ריק - מחכה!)
├── security/                    🔒 Security tests (ריק - מחכה!)
└── stress/                      💪 Stress tests (ריק - מחכה!)
```

**מה זה אומר?**
- המבנה מוכן לטסטים נוספים!
- יש תיקיות ייעודיות ל-Performance, Security, Stress
- רק צריך להוסיף טסטים!

---

## 🎯 הטסטים החדשים שהמלצתי - איפה לשים?

### מתוך `RECOMMENDED_ADDITIONAL_TESTS.md`:

| טסט חדש | תיקייה מומלצת |
|---------|----------------|
| `test_rabbitmq_baby_analyzer.py` | `tests/integration/messaging/` (חדש) |
| `test_response_time_sla.py` | `tests/performance/` ✅ (קיים!) |
| `test_recording_lifecycle.py` | `tests/data_quality/` |
| `test_partial_results_handling.py` | `tests/integration/historic_playback/` |
| `test_error_handling_comprehensive.py` | `tests/integration/` |
| `test_configuration_constraints.py` | `tests/integration/configuration/` |
| `test_nfft_comprehensive.py` | `tests/integration/configuration/` |
| `test_grpc_retry_logic.py` | `tests/infrastructure/` |

---

## ✅ טסטים שכבר קיימים וצריך לעדכן

### 1. **gRPC Timeout** (180s → 500s)
📁 **אין עדיין!** צריך ליצור ב-`tests/performance/test_response_time_sla.py`

### 2. **Sensor Range** (0-2222)
📁 `tests/integration/roi_adjustment/test_dynamic_roi_adjustment.py`
- ✅ קיים: `test_roi_with_negative_end`
- ❌ חסר: `test_roi_maximum_sensor_2222`

### 3. **NFFT Comprehensive**
📁 `tests/integration/configuration/test_spectrogram_pipeline.py`
- ✅ קיים: `test_nfft_variations` (בודק 128, 256, 512, 1024, 2048)
- ❌ חסר: טסטים ל-4096, 8192, 16384, 32768, 65536

---

## 📋 רשימת בדיקה (Checklist)

### הטסטים שלי קיימים?
- ✅ **Integration Tests** - ROI, Historic, Live, Config, Single Channel
- ✅ **Infrastructure Tests** - Connectivity, MongoDB outage
- ✅ **Data Quality Tests** - MongoDB schema, indexes
- ✅ **Unit Tests** - Config, Models, Validators
- ✅ **UI Tests** - Form, Buttons (Playwright generated)

### מה חסר?
- ⏳ **RabbitMQ Tests** - אין טסטי RabbitMQ!
- ⏳ **Performance Tests** - התיקייה ריקה!
- ⏳ **Security Tests** - התיקייה ריקה!
- ⏳ **Stress Tests** - התיקייה ריקה!

---

## 🚀 צעדים הבאים

### השבוע:
1. ✅ הטסטים שלך קיימים! (רק במקום חדש)
2. ⏳ צריך להוסיף טסטי Performance
3. ⏳ צריך להוסיף טסטי RabbitMQ

### איך להמשיך?
```powershell
# הרץ את כל הטסטים הקיימים
pytest tests/ -v

# הרץ רק Integration
pytest tests/integration/ -v

# הרץ רק Data Quality (MongoDB)
pytest tests/data_quality/ -v
```

---

## 💡 טיפים

### איך לראות כמה טסטים יש?
```powershell
# ספור קבצי טסטים
Get-ChildItem -Path tests -Filter "test_*.py" -Recurse | Measure-Object

# ספור פונקציות טסט
Select-String -Path "tests\**\test_*.py" -Pattern "^\s*def test_" | Measure-Object
```

### איך למצוא טסט לפי שם?
```powershell
# חפש בשמות קבצים
Get-ChildItem -Path tests -Filter "*roi*" -Recurse

# חפש בתוכן
Select-String -Path "tests\**\*.py" -Pattern "test_roi_change"
```

---

**סיכום:** כל הטסטים שלך קיימים! הם רק במבנה מאורגן יותר! 🎉

