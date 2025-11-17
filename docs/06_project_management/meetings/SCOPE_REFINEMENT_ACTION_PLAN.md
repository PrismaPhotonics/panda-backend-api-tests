# 🎯 תוכנית פעולה - עדכון Scope הטסטים לאחר פגישת הבהרה

**תאריך:** 27 אוקטובר 2025  
**Jira Reference:** PZ-13756  
**מטרה:** עדכון סוויטת הטסטים בהתאם להנחיות הפגישה  
**אחריות:** QA Automation Architect

---

## 📋 תקציר מנהלים (Executive Summary)

לאחר פגישת הבהרה, זוהו **שינויים קריטיים** ב-scope הטסטים:

### ✅ **IN SCOPE - מה שנשאר:**
1. **K8s/Orchestration** - Job lifecycle, resource allocation, port exposure, observability
2. **Focus Server API** - Pre-launch validations (port, data availability, time-range, config)
3. **System Behavior (infra)** - Clean startup, stability, predictable error handling, rollback/cleanup
4. **Concurrency** - תמיכה ב-200 concurrent Jobs

### ❌ **OUT OF SCOPE - מה שיוצא:**
1. **Internal Job processing ("Baby")** - בדיקות פנימיות של עיבוד ה-Job
2. **Algorithm/data correctness** - תקינות אלגוריתמים ונתונים
3. **Spectrogram/content validation** - אימות תוכן הספקטרוגרמה
4. **Full gRPC stream content checks** - בדיקות מלאות של תוכן stream

### 🔄 **MODIFIED SCOPE - מה שמשתנה:**
- **gRPC:** לשמור רק **transport readiness** (port/handshake), בלי אימות stream content

### 📌 **BACKLOG:**
- Restore/implement `GET /metadata/{job_id}` + create bug ticket

---

## 🔍 ניתוח מצב נוכחי - Current State Analysis

### סטטיסטיקה כללית:

```
📊 מצב קיים:
├── 🟢 Integration Tests:  ~82 טסטים
├── 🟡 Data Quality:        6 טסטים
├── 🟤 Infrastructure:      27 טסטים
├── 🔴 Load/Performance:    10+ טסטים
├── 🔬 Unit Tests:          73 טסטים
└── 🎨 UI Tests:            2 טסטים
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL:                     ~200 טסטים
```

---

## 🎯 תוכנית פעולה מפורטת - Detailed Action Plan

---

## 📁 **PHASE 1: זיהוי וסיווג טסטים קיימים**

### 1.1 טסטים שצריכים **למחיקה מלאה** ❌

#### A. `test_spectrogram_pipeline.py` - **מחיקה חלקית**

**Location:** `tests/integration/api/test_spectrogram_pipeline.py`  
**Status:** ⚠️ **MIXED - חלק למחוק, חלק לשמור**

**טסטים למחיקה:**
```python
# ❌ OUT OF SCOPE - Spectrogram content validation
class TestSpectrogramContentValidation:
    def test_spectrogram_intensity_values()      # ❌ למחוק
    def test_spectrogram_frequency_bins()        # ❌ למחוק
    def test_spectrogram_time_resolution()       # ❌ למחוק
    def test_spectrogram_color_mapping()         # ❌ למחוק (content)
```

**טסטים לשמור:**
```python
# ✅ IN SCOPE - Configuration validation
class TestNFFTConfiguration:
    def test_valid_nfft_power_of_2()             # ✅ לשמור (config validation)
    def test_nfft_variations()                   # ✅ לשמור (config validation)

class TestConfigurationCompatibility:
    def test_high_throughput_configuration()     # ✅ לשמור (config validation)
    def test_low_throughput_configuration()      # ✅ לשמור (config validation)

class TestSpectrogramPipelineErrors:
    def test_zero_nfft()                         # ✅ לשמור (error handling)
    def test_negative_nfft()                     # ✅ לשמור (error handling)
```

**Action Items:**
- [ ] לסקור את הקובץ שורה אחר שורה
- [ ] למחוק טסטים שבודקים spectrogram content
- [ ] לשמור טסטים שבודקים configuration validation
- [ ] לעדכן שם קובץ ל-`test_config_validation_nfft.py`

---

#### B. `test_dynamic_roi_adjustment.py` - **בדיקה נדרשת**

**Location:** `tests/integration/api/test_dynamic_roi_adjustment.py`  
**Status:** ⚠️ **REVIEW REQUIRED**

**שאלות לבדיקה:**
1. האם הטסט בודק **Baby processing** פנימי?
2. האם הטסט בודק **algorithm correctness**?
3. או שהוא בודק רק **API behavior** ו-**RabbitMQ commands**?

**החלטה:**
- אם בודק רק **API + RabbitMQ** → ✅ לשמור
- אם בודק **Baby processing** → ❌ למחוק

**Action Items:**
- [ ] לקרוא את הקובץ
- [ ] לזהות מה בדיוק נבדק
- [ ] להחליט: שמור/מחק/עדכן

---

#### C. טסטים עם `baby` ב-code - **מחיקה/עדכון**

**קבצים שנמצאו:**
```
✗ tests/conftest.py                              # fixtures - לבדוק
✗ tests/integration/api/test_dynamic_roi_adjustment.py  # לבדוק
✗ tests/integration/api/test_spectrogram_pipeline.py    # עדכון חלקי
✗ tests/unit/test_models_validation.py          # unit test - OK
✗ tests/unit/test_validators.py                 # unit test - OK
✗ tests/data_quality/test_mongodb_data_quality.py   # data quality - OK
```

**Action Items:**
- [ ] לסקור כל קובץ עם `baby`
- [ ] לוודא שלא נשארו בדיקות של Baby processing
- [ ] לעדכן fixtures אם צריך

---

### 1.2 טסטים שצריכים **עדכון** 🔄

#### A. gRPC Transport Tests - **עדכון Scope**

**דרישה:** לשמור רק **transport readiness** (port/handshake), **בלי** stream content validation

**טסטים קיימים לבדיקה:**
```bash
# חפש טסטים עם gRPC
grep -r "grpc\|gRPC" tests/ --include="*.py"
```

**Action Items:**
- [ ] למצוא כל טסטי gRPC
- [ ] לוודא שהם בודקים רק:
  - ✅ Port availability
  - ✅ Connection handshake
  - ✅ Transport readiness
- [ ] **למחוק** כל בדיקות של:
  - ❌ Stream content validation
  - ❌ Data correctness in stream
  - ❌ Message parsing

---

### 1.3 טסטים שצריכים **תוספת** ➕

#### A. Concurrent Jobs - **200 Jobs Capacity**

**Status:** ✅ **קיים חלקית** ב-`tests/load/test_job_capacity_limits.py`

**מה קיים:**
```python
BASELINE_JOBS = 1
LIGHT_LOAD_JOBS = 5
MEDIUM_LOAD_JOBS = 10
HEAVY_LOAD_JOBS = 20
EXTREME_LOAD_JOBS = 50
STRESS_LOAD_JOBS = 100    # ⚠️ עד 100 בלבד
```

**מה חסר:**
```python
TARGET_CAPACITY_JOBS = 200  # ❌ חסר!
```

**Action Items:**
- [ ] להוסיף טסט חדש: `test_200_concurrent_jobs_capacity()`
- [ ] לבדוק:
  - ✅ 200 jobs נוצרים בהצלחה
  - ✅ Actual capacity נמדדת
  - ✅ Readiness timings נרשמים
- [ ] אם סביבה לא מצליחה → **Infra Gap Report**
  - Actual capacity achieved
  - Readiness timings
  - Infrastructure recommendations

**דוגמה לטסט חדש:**
```python
@pytest.mark.load
@pytest.mark.capacity
@pytest.mark.critical
def test_200_concurrent_jobs_target_capacity(focus_server_api, config_manager):
    """
    Test: 200 Concurrent Jobs - Target Capacity
    
    Validates that the environment can support 200 concurrent jobs.
    If environment cannot meet target, generates Infra Gap Report.
    
    Success Criteria:
    - DEV/Staging: Must support 200 jobs
    - Other envs: Report actual capacity + gap analysis
    
    Related: Meeting decision - Support 200 concurrent Jobs
    """
    TARGET_CAPACITY = 200
    env = config_manager.environment
    
    logger.info(f"🎯 Testing 200 concurrent jobs on {env} environment...")
    
    # Create 200 jobs
    results = create_concurrent_jobs(
        api=focus_server_api,
        num_jobs=TARGET_CAPACITY,
        config_payload=standard_config_payload(),
        max_workers=50
    )
    
    # Analyze results
    success_count = len([r for r in results if r['success']])
    success_rate = success_count / TARGET_CAPACITY
    
    # Generate report
    if success_rate < 1.0:
        generate_infra_gap_report(
            environment=env,
            target_capacity=TARGET_CAPACITY,
            actual_capacity=success_count,
            readiness_timings=results.readiness_times,
            recommendations=[
                "Scale K8s cluster resources",
                "Optimize Focus Server deployment",
                "Review resource limits"
            ]
        )
    
    # Assertion based on environment
    if env in ["dev", "staging"]:
        assert success_rate >= 0.95, (
            f"Target environment {env} MUST support 200 jobs. "
            f"Achieved: {success_count}/200 ({success_rate*100:.1f}%)"
        )
    else:
        logger.warning(
            f"Environment {env} achieved {success_count}/200 jobs. "
            f"See Infra Gap Report for details."
        )
```

---

#### B. Focus Server Pre-Launch Validations - **טסטים חדשים**

**דרישה:** לבדוק **Pre-launch validations** של Focus Server API:
- Port availability
- Data availability (Live/Historic)
- Time-range checks
- Config validation (channels, frequency, NFFT, view type)

**טסטים חסרים:**

##### 1. Port Availability Validation
```python
# File: tests/integration/api/test_prelaunch_validations.py

@pytest.mark.integration
@pytest.mark.api
@pytest.mark.prelaunch
def test_port_availability_before_job_creation():
    """
    Test: Port Availability Pre-Launch Validation
    
    Validates that Focus Server checks port availability
    BEFORE creating a job.
    
    Expected Behavior:
    - If port in use → Reject with clear error
    - If port free → Proceed with job creation
    
    Related: Meeting decision - Pre-launch validations
    """
    pass  # להוסיף מימוש
```

##### 2. Data Availability Validation (Live/Historic)
```python
@pytest.mark.integration
@pytest.mark.api
@pytest.mark.prelaunch
def test_data_availability_live_mode():
    """
    Test: Data Availability Validation - Live Mode
    
    Validates that Focus Server checks if live data
    is available before accepting job.
    """
    pass  # להוסיף מימוש

@pytest.mark.integration
@pytest.mark.api
@pytest.mark.prelaunch
def test_data_availability_historic_mode():
    """
    Test: Data Availability Validation - Historic Mode
    
    Validates that Focus Server checks if historic data
    exists in requested time range.
    """
    pass  # להוסיף מימוש
```

##### 3. Time-Range Validation
```python
@pytest.mark.integration
@pytest.mark.api
@pytest.mark.prelaunch
def test_time_range_validation_future_timestamps():
    """
    Test: Time-Range Validation - Future Timestamps
    
    Validates rejection of future timestamps in historic mode.
    """
    pass  # להוסיף מימוש

@pytest.mark.integration
@pytest.mark.api
@pytest.mark.prelaunch
def test_time_range_validation_reversed_range():
    """
    Test: Time-Range Validation - Reversed Range
    
    Validates rejection of start_time > end_time.
    """
    pass  # להוסיף מימוש
```

##### 4. Config Validation (channels, frequency, NFFT, view type)
```python
@pytest.mark.integration
@pytest.mark.api
@pytest.mark.prelaunch
def test_config_validation_channels_out_of_range():
    """
    Test: Config Validation - Channels Out of Range
    
    Validates rejection of channel ranges exceeding system limits.
    """
    pass  # להוסיף מימוש

@pytest.mark.integration
@pytest.mark.api
@pytest.mark.prelaunch
def test_config_validation_frequency_exceeds_nyquist():
    """
    Test: Config Validation - Frequency Exceeds Nyquist
    
    Validates rejection of frequency > Nyquist limit.
    """
    pass  # קיים ב-test_config_validation_high_priority.py - לוודא

@pytest.mark.integration
@pytest.mark.api
@pytest.mark.prelaunch
def test_config_validation_invalid_nfft():
    """
    Test: Config Validation - Invalid NFFT
    
    Validates rejection of invalid NFFT values.
    """
    pass  # קיים ב-test_spectrogram_pipeline.py - לוודא

@pytest.mark.integration
@pytest.mark.api
@pytest.mark.prelaunch
def test_config_validation_invalid_view_type():
    """
    Test: Config Validation - Invalid View Type
    
    Validates rejection of unsupported view types.
    """
    pass  # להוסיף מימוש
```

**Action Items:**
- [ ] ליצור קובץ חדש: `tests/integration/api/test_prelaunch_validations.py`
- [ ] לממש את כל הטסטים למעלה
- [ ] לוודא שאין דופליקטים עם טסטים קיימים
- [ ] לקשר ל-Jira tickets

---

#### C. K8s Job Lifecycle - **טסטים חדשים**

**דרישה:** לבדוק **K8s orchestration** של Jobs:
- Job creation
- Job execution (run)
- Job cancellation
- Resource allocation
- Port exposure
- Observability

**טסטים קיימים:**
- `tests/infrastructure/test_external_connectivity.py` - יש K8s connectivity
- `tests/load/test_job_capacity_limits.py` - יש job creation

**טסטים חסרים:**

##### 1. Job Lifecycle Complete Flow
```python
# File: tests/infrastructure/test_k8s_job_lifecycle.py

@pytest.mark.infrastructure
@pytest.mark.kubernetes
@pytest.mark.job_lifecycle
def test_k8s_job_creation_and_pod_spawn():
    """
    Test: K8s Job Creation → Pod Spawn
    
    Validates that creating a Focus Server job
    triggers K8s pod creation with correct labels.
    
    Steps:
    1. Create job via API
    2. Query K8s for corresponding pod
    3. Validate pod labels and annotations
    4. Validate pod status (Running)
    
    Related: Meeting decision - K8s Job lifecycle
    """
    pass  # להוסיף מימוש
```

##### 2. Job Resource Allocation
```python
@pytest.mark.infrastructure
@pytest.mark.kubernetes
@pytest.mark.resources
def test_k8s_job_resource_allocation():
    """
    Test: K8s Job Resource Allocation
    
    Validates that jobs receive allocated resources:
    - CPU requests/limits
    - Memory requests/limits
    - Storage volumes
    
    Related: Meeting decision - Resource allocation
    """
    pass  # להוסיף מימוש
```

##### 3. Job Port Exposure
```python
@pytest.mark.infrastructure
@pytest.mark.kubernetes
@pytest.mark.networking
def test_k8s_job_port_exposure():
    """
    Test: K8s Job Port Exposure
    
    Validates that job ports are properly exposed:
    - gRPC port accessible
    - Port mapping correct
    - Service discovery works
    
    Related: Meeting decision - Port exposure
    """
    pass  # להוסיף מימוש
```

##### 4. Job Cancellation and Cleanup
```python
@pytest.mark.infrastructure
@pytest.mark.kubernetes
@pytest.mark.cleanup
def test_k8s_job_cancellation_and_cleanup():
    """
    Test: K8s Job Cancellation → Pod Cleanup
    
    Validates clean cancellation:
    1. Cancel job via API
    2. Verify pod termination
    3. Verify resource cleanup
    4. Verify no orphaned resources
    
    Related: Meeting decision - Cleanup and rollback
    """
    pass  # להוסיף מימוש
```

##### 5. Job Observability
```python
@pytest.mark.infrastructure
@pytest.mark.kubernetes
@pytest.mark.observability
def test_k8s_job_observability():
    """
    Test: K8s Job Observability
    
    Validates that job state is observable:
    - Pod logs accessible
    - Pod events tracked
    - Metrics exposed
    - Status updates propagated
    
    Related: Meeting decision - Observability
    """
    pass  # להוסיף מימוש
```

**Action Items:**
- [ ] ליצור קובץ חדש: `tests/infrastructure/test_k8s_job_lifecycle.py`
- [ ] לממש את כל הטסטים למעלה
- [ ] להשתמש ב-`KubernetesManager` fixture קיים
- [ ] לקשר ל-Jira tickets

---

#### D. System Behavior (Infra) - **טסטים חדשים**

**דרישה:** לבדוק **System Behavior**:
- Clean startup
- Stability over time
- Predictable error handling (no data, port in use)
- Proper rollback/cleanup

**טסטים קיימים:**
- `tests/performance/test_mongodb_outage_resilience.py` - יש error handling
- `tests/infrastructure/test_basic_connectivity.py` - יש connectivity

**טסטים חסרים:**

##### 1. Clean Startup
```python
# File: tests/infrastructure/test_system_behavior.py

@pytest.mark.infrastructure
@pytest.mark.startup
@pytest.mark.critical
def test_focus_server_clean_startup():
    """
    Test: Focus Server Clean Startup
    
    Validates clean startup sequence:
    1. All dependencies available (MongoDB, K8s)
    2. Configuration loaded correctly
    3. Services initialized in order
    4. Health check passes
    5. Ready to accept requests
    
    Related: Meeting decision - Clean startup
    """
    pass  # להוסיף מימוש
```

##### 2. Stability Over Time
```python
@pytest.mark.infrastructure
@pytest.mark.stability
@pytest.mark.slow
def test_focus_server_stability_over_time():
    """
    Test: Focus Server Stability Over Time
    
    Validates system stability over 1 hour:
    - Create jobs every 5 minutes
    - Monitor memory usage (no leaks)
    - Monitor CPU usage (stable)
    - Monitor error rates (low)
    - Verify no crashes or restarts
    
    Duration: 1 hour
    
    Related: Meeting decision - Stability over time
    """
    pass  # להוסיף מימוש
```

##### 3. Predictable Error Handling - No Data
```python
@pytest.mark.infrastructure
@pytest.mark.error_handling
def test_predictable_error_no_data_available():
    """
    Test: Predictable Error Handling - No Data
    
    Validates clear error when no data available:
    - Historic mode: No recordings in time range
    - Expected: HTTP 404 with clear message
    - No crash, no 500 errors
    
    Related: Meeting decision - Predictable error handling
    """
    pass  # להוסיף מימוש
```

##### 4. Predictable Error Handling - Port in Use
```python
@pytest.mark.infrastructure
@pytest.mark.error_handling
def test_predictable_error_port_in_use():
    """
    Test: Predictable Error Handling - Port in Use
    
    Validates clear error when port unavailable:
    - Create job on port X
    - Try to create another job on same port
    - Expected: HTTP 409 Conflict with clear message
    - No crash, no 500 errors
    
    Related: Meeting decision - Predictable error handling
    """
    pass  # להוסיף מימוש
```

##### 5. Proper Rollback on Failure
```python
@pytest.mark.infrastructure
@pytest.mark.rollback
def test_proper_rollback_on_job_creation_failure():
    """
    Test: Proper Rollback on Failure
    
    Validates rollback when job creation fails:
    1. Trigger failure during job creation
    2. Verify no partial resources left
    3. Verify K8s pod cleaned up
    4. Verify system state unchanged
    
    Related: Meeting decision - Proper rollback/cleanup
    """
    pass  # להוסיף מימוש
```

**Action Items:**
- [ ] ליצור קובץ חדש: `tests/infrastructure/test_system_behavior.py`
- [ ] לממש את כל הטסטים למעלה
- [ ] לקשר ל-Jira tickets

---

### 1.4 טסטים ש**נשארים ללא שינוי** ✅

הטסטים הבאים **תואמים ל-scope החדש** ונשארים כמות שהם:

#### ✅ Infrastructure Tests
- `tests/infrastructure/test_basic_connectivity.py` - ✅ לשמור
- `tests/infrastructure/test_external_connectivity.py` - ✅ לשמור
- `tests/infrastructure/test_pz_integration.py` - ✅ לשמור

#### ✅ Data Quality Tests
- `tests/data_quality/test_mongodb_data_quality.py` - ✅ לשמור
  - Collections validation
  - Schema validation
  - Metadata completeness
  - Indexes validation
  - Historical vs Live classification

#### ✅ Integration Tests (חלק)
- `tests/integration/api/test_config_validation_high_priority.py` - ✅ לשמור
  - Config validation (IN SCOPE)
  - API pre-launch checks (IN SCOPE)

#### ✅ Load Tests
- `tests/load/test_job_capacity_limits.py` - ✅ לשמור (עם תוספות)
  - Capacity testing framework קיים
  - צריך להוסיף טסט ל-200 concurrent jobs

#### ✅ Unit Tests
- `tests/unit/test_validators.py` - ✅ לשמור
- `tests/unit/test_models_validation.py` - ✅ לשמור
- `tests/unit/test_config_loading.py` - ✅ לשמור
- `tests/unit/test_basic_functionality.py` - ✅ לשמור

---

## 📁 **PHASE 2: מימוש השינויים - Implementation**

### 2.1 מחיקת טסטים (Deletion)

**Action Items:**
- [ ] **Step 1:** גיבוי (Backup)
  ```bash
  # Create backup branch
  git checkout -b backup/pre-scope-refinement-$(date +%Y%m%d)
  git push origin backup/pre-scope-refinement-$(date +%Y%m%d)
  
  # Return to main branch
  git checkout develop
  git pull origin develop
  
  # Create feature branch
  git checkout -b feature/scope-refinement-meeting-updates
  ```

- [ ] **Step 2:** מחיקת טסטים OUT OF SCOPE
  ```bash
  # Review and delete spectrogram content validation tests
  # (Manual review required - partial deletion)
  code tests/integration/api/test_spectrogram_pipeline.py
  
  # After manual cleanup, commit
  git add tests/integration/api/test_spectrogram_pipeline.py
  git commit -m "refactor(tests): Remove spectrogram content validation tests - OUT OF SCOPE"
  ```

- [ ] **Step 3:** מחיקת/עדכון טסטים עם Baby processing
  ```bash
  # Review each file with 'baby' references
  grep -r "baby\|Baby" tests/ --include="*.py" -l
  
  # Manual review and cleanup needed
  # Commit each file separately with clear message
  ```

- [ ] **Step 4:** עדכון gRPC טסטים (transport only)
  ```bash
  # Find gRPC tests
  grep -r "grpc\|gRPC" tests/ --include="*.py" -l
  
  # Update to test only transport readiness
  # Remove stream content validation
  ```

---

### 2.2 תוספת טסטים חדשים (Addition)

**Priority Order:**

#### Priority 1 (Critical) 🔴
- [ ] **200 Concurrent Jobs Test**
  - File: `tests/load/test_job_capacity_limits.py`
  - Add: `test_200_concurrent_jobs_target_capacity()`
  - Add: `generate_infra_gap_report()` function
  - Estimated time: 4 hours

- [ ] **K8s Job Lifecycle Tests**
  - File: `tests/infrastructure/test_k8s_job_lifecycle.py` (NEW)
  - Add: All 5 tests (creation, resources, ports, cancellation, observability)
  - Estimated time: 8 hours

#### Priority 2 (High) 🟠
- [ ] **Pre-Launch Validations Tests**
  - File: `tests/integration/api/test_prelaunch_validations.py` (NEW)
  - Add: All 10 tests (port, data, time-range, config validations)
  - Estimated time: 6 hours

- [ ] **System Behavior Tests**
  - File: `tests/infrastructure/test_system_behavior.py` (NEW)
  - Add: All 5 tests (startup, stability, error handling, rollback)
  - Estimated time: 8 hours

#### Priority 3 (Medium) 🟡
- [ ] **GET /metadata/{job_id} Implementation** (Backlog item)
  - Create Jira bug ticket
  - Document expected behavior
  - Create placeholder test (skip until implemented)
  - Estimated time: 2 hours (just documentation + ticket)

---

### 2.3 עדכון תיעוד (Documentation)

**Action Items:**
- [ ] עדכן `tests/README.md` עם scope החדש
- [ ] עדכן `tests/TESTS_LOCATION_GUIDE_HE.md`
- [ ] עדכן `tests/TEST_REORGANIZATION_SUMMARY.md`
- [ ] צור מסמך חדש: `documentation/meetings/SCOPE_REFINEMENT_SUMMARY.md`
- [ ] עדכן כל ה-README.md בתיקיות הטסטים

**Template לעדכון README:**
```markdown
# Test Category Name

**Last Updated:** 27 October 2025  
**Scope Refined:** Following meeting decision (PZ-13756)

## ✅ IN SCOPE (After Meeting)
- K8s Job lifecycle
- Focus Server pre-launch validations
- System behavior (startup, stability, error handling)
- 200 concurrent jobs capacity

## ❌ OUT OF SCOPE (Removed)
- Internal Job processing ("Baby")
- Algorithm/data correctness
- Spectrogram content validation
- Full gRPC stream content checks

## 🔄 MODIFIED SCOPE
- gRPC: Transport readiness only (port/handshake)
```

---

## 📁 **PHASE 3: בדיקה ואימות - Testing & Validation**

### 3.1 הרצת כל הטסטים

**Action Items:**
- [ ] הרץ Unit Tests
  ```bash
  pytest tests/unit/ -v --tb=short
  ```

- [ ] הרץ Infrastructure Tests
  ```bash
  pytest tests/infrastructure/ -v --tb=short
  ```

- [ ] הרץ Integration Tests
  ```bash
  pytest tests/integration/ -v --tb=short
  ```

- [ ] הרץ Data Quality Tests
  ```bash
  pytest tests/data_quality/ -v --tb=short
  ```

- [ ] הרץ Load Tests
  ```bash
  pytest tests/load/ -v --tb=short -m "not slow"
  ```

- [ ] הרץ טסטים חדשים בנפרד
  ```bash
  # K8s Job Lifecycle
  pytest tests/infrastructure/test_k8s_job_lifecycle.py -v -s
  
  # Pre-Launch Validations
  pytest tests/integration/api/test_prelaunch_validations.py -v -s
  
  # System Behavior
  pytest tests/infrastructure/test_system_behavior.py -v -s
  
  # 200 Concurrent Jobs
  pytest tests/load/test_job_capacity_limits.py::test_200_concurrent_jobs -v -s
  ```

---

### 3.2 Code Review

**Action Items:**
- [ ] Self-review:
  - קרא את כל השינויים
  - בדוק שאין דופליקטים
  - בדוק שהסרת כל OUT OF SCOPE

- [ ] Peer review:
  - בקש review מ-team member
  - תעד feedback
  - עדכן לפי הערות

- [ ] Linting & Formatting:
  ```bash
  # Run black
  black tests/ --check
  
  # Run flake8
  flake8 tests/ --max-line-length=120
  
  # Run mypy
  mypy tests/ --ignore-missing-imports
  ```

---

## 📁 **PHASE 4: אינטגרציה ו-CI/CD**

### 4.1 עדכון CI/CD Pipeline

**Action Items:**
- [ ] עדכן `.github/workflows/tests.yml` (אם קיים)
- [ ] הוסף job ייעודי ל-200 concurrent jobs test
- [ ] הוסף job ייעודי ל-K8s lifecycle tests
- [ ] עדכן thresholds לפי scope החדש

**דוגמה:**
```yaml
# .github/workflows/tests.yml

jobs:
  infrastructure-tests:
    name: Infrastructure Tests (IN SCOPE)
    runs-on: ubuntu-latest
    steps:
      - name: Run Infrastructure Tests
        run: |
          pytest tests/infrastructure/ -v \
            -m "not slow" \
            --junitxml=reports/infrastructure.xml

  capacity-tests:
    name: 200 Concurrent Jobs Capacity
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - name: Run Capacity Test
        run: |
          pytest tests/load/test_job_capacity_limits.py::test_200_concurrent_jobs \
            -v -s \
            --junitxml=reports/capacity.xml
      
      - name: Upload Infra Gap Report
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: infra-gap-report
          path: reports/infra_gap_*.json
```

---

### 4.2 Xray Integration

**Action Items:**
- [ ] מפה טסטים חדשים ל-Jira tickets
- [ ] צור Test Executions ב-Xray
- [ ] קשר טסטים ל-Test Plans
- [ ] עדכן Test Coverage reports

---

## 📁 **PHASE 5: Backlog Items**

### 5.1 GET /metadata/{job_id} Restoration

**Action Items:**
- [ ] **Step 1:** Create Jira Bug Ticket
  ```
  Title: Restore GET /metadata/{job_id} endpoint
  
  Description:
  The GET /metadata/{job_id} endpoint is not currently available
  in Focus Server API.
  
  This endpoint is needed for:
  - Querying job status after creation
  - Retrieving job metadata dynamically
  - Monitoring job progress
  
  Expected Behavior:
  GET /metadata/{job_id} should return:
  - job_id
  - status (running/completed/failed)
  - stream_port
  - stream_url
  - view_type
  - metadata (PRR, dx, etc.)
  
  Priority: Medium
  Component: Focus Server API
  ```

- [ ] **Step 2:** Document Current Workaround
  ```markdown
  ## Current Workaround
  
  Since GET /metadata/{job_id} is not available, we:
  1. Store job metadata from POST /configure response
  2. Use stored metadata for subsequent operations
  3. Cannot query dynamic status updates
  
  ## Limitations
  - No way to check if job is still running
  - No way to retrieve metadata if configure response lost
  - Cannot monitor job progress dynamically
  ```

- [ ] **Step 3:** Create Placeholder Test
  ```python
  @pytest.mark.skip(reason="Endpoint not implemented yet - Jira: PZ-XXXXX")
  @pytest.mark.backlog
  def test_get_job_metadata_endpoint():
      """
      Test: GET /metadata/{job_id}
      
      Status: ⏳ PENDING IMPLEMENTATION
      Jira: PZ-XXXXX
      
      This test will be enabled once the endpoint is restored.
      """
      pass
  ```

---

## 📊 סיכום ומעקב - Summary & Tracking

### סטטיסטיקת טסטים - לפני ואחרי

```
┌─────────────────────────────┬──────────┬──────────┬─────────┐
│ Category                    │ Before   │ After    │ Change  │
├─────────────────────────────┼──────────┼──────────┼─────────┤
│ 🟢 Integration              │ ~82      │ ~65      │ -17     │
│ 🟡 Data Quality             │ 6        │ 6        │ 0       │
│ 🟤 Infrastructure           │ 27       │ 42       │ +15     │
│ 🔴 Load/Performance         │ 10       │ 11       │ +1      │
│ 🔬 Unit                     │ 73       │ 73       │ 0       │
│ 🎨 UI                       │ 2        │ 2        │ 0       │
├─────────────────────────────┼──────────┼──────────┼─────────┤
│ TOTAL                       │ ~200     │ ~199     │ -1      │
└─────────────────────────────┴──────────┴──────────┴─────────┘

Changes Breakdown:
- Removed: ~20 tests (spectrogram content, baby processing)
- Added: ~19 tests (K8s lifecycle, pre-launch, system behavior, capacity)
- Net change: -1 test

Quality Improvement: ✅
- Removed out-of-scope tests
- Added critical infrastructure tests
- Better alignment with actual system requirements
```

---

### Timeline & Effort Estimation

```
┌─────────────────────────────┬──────────────┬─────────────┐
│ Phase                       │ Effort       │ Duration    │
├─────────────────────────────┼──────────────┼─────────────┤
│ Phase 1: Analysis           │ 4 hours      │ 0.5 days    │
│ Phase 2: Implementation     │ 28 hours     │ 3.5 days    │
│ Phase 3: Testing            │ 8 hours      │ 1 day       │
│ Phase 4: CI/CD Integration  │ 4 hours      │ 0.5 days    │
│ Phase 5: Backlog Items      │ 2 hours      │ 0.25 days   │
│ Documentation               │ 4 hours      │ 0.5 days    │
├─────────────────────────────┼──────────────┼─────────────┤
│ TOTAL                       │ 50 hours     │ 6.25 days   │
└─────────────────────────────┴──────────────┴─────────────┘

With contingency (20%): ~7.5 days
Target completion: November 5, 2025
```

---

### Checklist - Master Tracking

#### ✅ Phase 1: Analysis
- [ ] קרא את כל הטסטים הקיימים
- [ ] זיהה טסטים OUT OF SCOPE
- [ ] זיהה טסטים IN SCOPE
- [ ] זיהה gaps (טסטים חסרים)
- [ ] צור רשימת Action Items

#### ✅ Phase 2: Implementation
- [ ] מחק טסטים OUT OF SCOPE
- [ ] עדכן טסטים MODIFIED SCOPE (gRPC)
- [ ] הוסף טסט 200 concurrent jobs
- [ ] הוסף K8s job lifecycle tests (5 tests)
- [ ] הוסף Pre-launch validations tests (10 tests)
- [ ] הוסף System behavior tests (5 tests)

#### ✅ Phase 3: Testing
- [ ] הרץ כל הטסטים החדשים
- [ ] הרץ regression על כל הטסטים
- [ ] בצע code review
- [ ] תקן linting errors

#### ✅ Phase 4: CI/CD
- [ ] עדכן CI/CD pipeline
- [ ] אינטגרציה עם Xray
- [ ] עדכן Test Plans

#### ✅ Phase 5: Backlog
- [ ] צור Jira ticket ל-GET /metadata/{job_id}
- [ ] צור placeholder test

#### ✅ Documentation
- [ ] עדכן כל ה-README files
- [ ] צור summary document
- [ ] עדכן Confluence (אם רלוונטי)

---

## 🎓 Lessons Learned & Best Practices

### מה למדנו מהפגישה?

1. **Scope Creep Prevention**
   - חשוב להגדיר בבירור מה IN SCOPE ומה OUT OF SCOPE
   - טסטים צריכים להתמקד ב-infrastructure/API behavior
   - אין לבדוק algorithm correctness ב-automation tests

2. **Testing Strategy**
   - Infrastructure tests > Content validation tests
   - Pre-launch validations קריטיים למניעת כשלים
   - Capacity testing (200 jobs) must have gap analysis

3. **Communication**
   - תיעוד ברור של decisions מפגישות
   - Clear action items with owners
   - Regular updates to stakeholders

---

## 📞 נקודות קשר - Contacts

**Questions & Clarifications:**
- **Scope Questions:** [Product Owner Name]
- **Technical Questions:** [Tech Lead Name]
- **Jira/Xray:** [QA Manager Name]

---

**Created By:** QA Automation Architect  
**Date:** 27 October 2025  
**Version:** 1.0  
**Status:** ✅ READY FOR EXECUTION

---

**הסמכות לביצוע:** מסמך זה מהווה תוכנית עבודה רשמית לעדכון סוויטת הטסטים בהתאם להחלטות הפגישה.

