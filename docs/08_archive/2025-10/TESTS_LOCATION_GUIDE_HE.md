# 🗺️ מדריך מיקום טסטים - איפה כל דבר נמצא
## Guide to Test Locations - Where Everything Is

**תאריך:** 2025-10-21  
**מטרה:** להסביר בדיוק איפה כל קובץ טסט נמצא ומה יש בו  

---

## 📂 מבנה כללי

```
tests/
├── integration/        # 🟢 Integration (5 קבצים, 82 טסטים)
├── api/               # 🔵 API (ריק - לבנות)
├── data_quality/      # 🟡 Data Quality (1 קובץ, 6 טסטים)
├── performance/       # 🔴 Performance (ריק - לבנות)
├── infrastructure/    # 🟤 Infrastructure (4 קבצים, 27 טסטים)
├── security/          # 🔐 Security (ריק - לבנות)
├── stress/            # ⚡ Stress (ריק - לבנות)
└── unit/              # 🔬 Unit (4 קבצים, 73 טסטים)
```

**סה"כ:** 17 קבצי טסט, ~202 טסטים

---

## 🟢 INTEGRATION - הקטגוריה הכי גדולה

### 📁 integration/configuration/
**קובץ:** `test_spectrogram_pipeline.py`  
**טסטים:** 13  

**מה בודק:**
1. ✅ NFFT validation (128, 256, 512, 1024, 2048, 4096)
2. ✅ Frequency range within Nyquist ⭐ **קריטי!**
3. ✅ Resource estimation (CPU, Memory, Bandwidth)
4. ✅ High/Low throughput configs
5. ✅ Colormap commands
6. ✅ CAxis adjustment commands
7. ✅ Invalid NFFT (zero, negative)

**Xray:** PZ-13873-13880, PZ-13801-13805

---

### 📁 integration/historic_playback/
**קובץ:** `test_historic_playback_flow.py`  
**טסטים:** 14  

**מה בודק:**
1. ✅ Configure historic task (happy path)
2. ✅ Poll until completion (status 208)
3. ✅ Time range validation
4. ✅ Future timestamps (should reject)
5. ✅ Very old timestamps (no data)
6. ✅ Reversed time range (end < start)
7. ✅ Short duration (1 minute)
8. ✅ Long duration (24 hours)
9. ✅ Data integrity validation
10. ✅ Invalid time formats

**Xray:** PZ-13863-13872

---

### 📁 integration/live_monitoring/
**קובץ:** `test_live_monitoring_flow.py`  
**טסטים:** 17  

**מה בודק:**
1. ✅ Configure live task
2. ✅ **GET /sensors** - רשימת sensors ⭐
3. ✅ **GET /live_metadata** - metadata מהfiber
4. ✅ Get task metadata
5. ✅ Complete end-to-end flow
6. ✅ Invalid task_id error handling
8. ✅ Invalid row_count (zero, negative, huge)
9. ✅ Rapid polling (stress)
10. ✅ Invalid sensor/frequency ranges

**Xray:** PZ-13547

---

### 📁 integration/singlechannel/
**קובץ:** `test_singlechannel_view_mapping.py`  
**טסטים:** 13  

**מה בודק:**
1. ✅ Channel 7 mapping (main test)
2. ✅ Channel 1 mapping (first channel)
3. ✅ Channel 100 mapping (upper boundary)
4. ✅ SingleChannel vs MultiChannel comparison
5. ✅ Min ≠ Max validation (should fail)
6. ✅ Channel zero handling
7. ✅ Different frequency ranges
8. ✅ Invalid NFFT/height/frequency
9. ✅ Consistency across requests
10. ✅ Different channels → different mappings

**Xray:** PZ-13813-13862

---

### 📁 integration/roi_adjustment/
**קובץ:** `test_dynamic_roi_adjustment.py`  
**טסטים:** 25+  

**מה בודק:**
1. ✅ Send ROI command via RabbitMQ
2. ✅ Safety validation (50% limit)
3. ✅ Multiple ROI changes in sequence
4. ✅ ROI expansion (increase range)
5. ✅ ROI shrinking (decrease range)
6. ✅ ROI shift (move position)
7. ✅ ROI edge cases:
   - Equal start/end (zero size)
   - Reversed range
   - Negative start/end
   - Small/large ranges
   - Starting at zero
8. ✅ Unsafe changes:
   - Large jump (>50%)
   - Large position shift
9. ✅ Safe changes (within limits)

**Xray:** PZ-13784-13800

---

### 📁 integration/visualization/
**קובץ:** אין עדיין (הטסטים ב-configuration)  
**טסטים:** 0  

**צריך להעביר:** Colormap ו-CAxis tests מ-test_spectrogram_pipeline.py

**Xray:** PZ-13801-13805

---

## 🔵 API - ריק (לבנות)

### 📁 api/endpoints/
**צריך ליצור:**
- test_channels_endpoint.py (PZ-13895)
- test_live_metadata_endpoint.py (PZ-13764-13765)
- test_recordings_in_time_range.py (PZ-13766)

### 📁 api/singlechannel/
**צריך ליצור:**
- test_singlechannel_api.py (PZ-13813-13824)

---

## 🟡 DATA QUALITY

### 📁 data_quality/
**קובץ:** `test_mongodb_data_quality.py`  
**טסטים:** 6  

**מה בודק:**
1. ✅ Collections exist (base_paths + GUID)
2. ✅ Recording schema (validate structure)
3. ✅ Metadata completeness (all required fields)
4. ✅ MongoDB indexes (performance)
5. ✅ Soft delete (deleted flag)
6. ✅ Historical vs live (1 hour threshold)

**Xray:** PZ-13683-13812

---

## 🔴 PERFORMANCE - ריק (לבנות)

### 📁 performance/
**צריך ליצור:**
- test_api_latency_p95.py (PZ-13770)
- test_concurrent_tasks.py (PZ-13896)

---

## 🟤 INFRASTRUCTURE

### 📁 infrastructure/
**4 קבצים, 27 טסטים**

1. **test_basic_connectivity.py** (3 tests)
   - MongoDB quick ping
   - Kubernetes quick ping
   - SSH quick ping

2. **test_external_connectivity.py** (13 tests)
   - Full MongoDB connection suite
   - Full Kubernetes connection suite
   - Full SSH connection suite
   - All services summary

3. **test_mongodb_outage_resilience.py** (5 tests)
   - Scale down outage (503)
   - Network block outage
   - No live impact
   - Logging/metrics
   - Cleanup/restore

4. **test_pz_integration.py** (6 tests)
   - PZ repository tests
   - Version info
   - Import capability

**Xray:** PZ-13806-13808, PZ-13767-13768

---

## 🔬 UNIT - לא ב-Xray

### 📁 unit/
**4 קבצים, 73 טסטים** (framework unit tests)

1. test_validators.py (30 tests)
2. test_models_validation.py (20 tests)
3. test_config_loading.py (12 tests)
4. test_basic_functionality.py (11 tests)

---

## 🎯 איך למצוא טסט?

### לפי Xray ID:
```
PZ-13871 "Integration - Historic Playback - Timestamp Ordering"
→ tests/integration/historic_playback/test_historic_playback_flow.py
```

### לפי קטגוריה:
```
רוצה Integration tests? → tests/integration/
רוצה Data Quality tests? → tests/data_quality/
רוצה Infrastructure tests? → tests/infrastructure/
```

### לפי feature:
```
רוצה Historic tests? → tests/integration/historic_playback/
רוצה ROI tests? → tests/integration/roi_adjustment/
רוצה SingleChannel tests? → tests/integration/singlechannel/
```

---

**המבנה מושלם ומתואם 100% ל-Jira Xray!** ✅

