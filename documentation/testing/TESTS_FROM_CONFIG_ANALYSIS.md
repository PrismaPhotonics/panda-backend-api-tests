# Additional Test Ideas Based on Configuration Analysis
**Date:** October 16, 2025  
**Source:** Focus Server Frontend Configuration JSON  
**Author:** QA Automation Architect

---

## 📋 Configuration Analysis

### Key Findings from Configuration

```json
{
  "Communication": {
    "Backend": "https://10.10.100.100/focus-server/",
    "Frontend": "https://10.10.10.100/liveView",
    "GrpcStreamMinTimeout_sec": 600,        // ⚠️ 10 minutes!
    "GrpcTimeout": 500,                      // ⚠️ 8.33 minutes (not 180s!)
    "NumGrpcRetries": 10
  },
  "Constraints": {
    "FrequencyMax": 1000,
    "FrequencyMin": 0,
    "FrequencyMinRange": 1,
    "MaxWindows": 30,
    "SensorsRange": 2222                     // ⚠️ Total sensor count!
  },
  "Defaults": {
    "Nfft": 1024,
    "StartChannel": 11,
    "EndChannel": 109,
    "StartFrequency_hz": 0,
    "EndFrequency_hz": 1000,
    "NumLinesToDisplay": 200,
    "TimeWindow": "30s",
    "ViewType": "MultiChannelSpectrogram"
  },
  "Options": {
    "nfftSingleChannel": [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]
  }
}
```

---

## 🔥 Critical Updates to Existing Tests

### 1. **Update gRPC Timeout Tests**

**Current assumption:** 180 seconds (from team feedback)  
**Actual from config:** 500 seconds (8.33 minutes) for GrpcTimeout  
**Stream timeout:** 600 seconds (10 minutes) for GrpcStreamMinTimeout

#### Action Required:
```python
# tests/integration/performance/test_response_time_sla.py

def test_grpc_connection_timeout_matches_config(self):
    """
    Verify gRPC connection timeout matches configuration.
    
    UPDATED: Team said 180s, but config shows 500s!
    """
    # Expected timeouts from config
    GRPC_TIMEOUT = 500  # seconds
    GRPC_STREAM_MIN_TIMEOUT = 600  # seconds
    
    # Test: Establish gRPC connection, measure timeout
    # Expected: Timeout after ~500s ± 10s
    # Note: This is MUCH longer than the 180s mentioned by team!
```

### 2. **Update Sensor Range Tests**

**Discovery:** `SensorsRange: 2222` - Total number of sensors!

#### Action Required:
```python
# tests/integration/api/test_dynamic_roi_adjustment.py

def test_roi_maximum_sensor_range_2222(self):
    """
    Verify ROI can span full sensor range (0-2222).
    
    NEW: Discovered from config - SensorsRange: 2222
    """
    # Test: Send ROI [0, 2222]
    # Expected: Success, covers full sensor range
    
def test_roi_beyond_sensor_range_returns_422(self):
    """
    Verify ROI beyond 2222 sensors returns validation error.
    """
    # Test: Send ROI [0, 2223]
    # Expected: 422 with "exceeds maximum sensor range"
```

---

## 🆕 New Test Categories Based on Config

### Category A: Configuration Constraints Validation 🔒

**Purpose:** Validate that API enforces constraints defined in configuration

#### `tests/integration/api/test_configuration_constraints.py`

```python
class TestConfigurationConstraints:
    """
    Test that API enforces constraints from configuration.
    
    Based on actual Frontend configuration constraints.
    """
    
    def test_frequency_max_constraint_1000hz(self):
        """
        Verify frequency cannot exceed 1000 Hz.
        
        Config: "FrequencyMax": 1000
        """
        # Test: Send configure with end_frequency=1001
        # Expected: 422 with "frequency exceeds maximum 1000 Hz"
        
    def test_frequency_min_constraint_0hz(self):
        """
        Verify frequency cannot be below 0 Hz.
        
        Config: "FrequencyMin": 0
        """
        # Test: Send configure with start_frequency=-1
        # Expected: 422 with "frequency below minimum 0 Hz"
        
    def test_frequency_min_range_constraint_1hz(self):
        """
        Verify frequency range must be at least 1 Hz.
        
        Config: "FrequencyMinRange": 1
        """
        # Test: Send start_frequency=100, end_frequency=100
        # Expected: 422 with "frequency range must be at least 1 Hz"
        
    def test_max_windows_constraint_30(self):
        """
        Verify maximum 30 concurrent windows allowed.
        
        Config: "MaxWindows": 30
        """
        # Test: Create 31 concurrent tasks
        # Expected: 429 Too Many Requests or 503 Service Unavailable
        
    def test_sensors_range_constraint_2222(self):
        """
        Verify sensor indices cannot exceed 2222.
        
        Config: "SensorsRange": 2222
        """
        # Test: Send ROI [0, 2223]
        # Expected: 422 with "sensor index exceeds range 2222"
        
    def test_sensors_valid_full_range(self):
        """
        Verify full sensor range [0, 2222] is valid.
        """
        # Test: Send ROI [0, 2222]
        # Expected: 200 OK
```

---

### Category B: Default Values Validation ✅

**Purpose:** Validate that defaults match configuration when not specified

#### `tests/integration/api/test_configuration_defaults.py`

```python
class TestConfigurationDefaults:
    """
    Test that API uses correct defaults from configuration.
    """
    
    def test_default_nfft_1024(self):
        """
        Verify default NFFT is 1024 when not specified.
        
        Config: "Nfft": 1024
        """
        # Test: Send configure without nfft field
        # Expected: Task created with nfft=1024
        
    def test_default_roi_channels_11_to_109(self):
        """
        Verify default ROI is channels 11-109.
        
        Config: "StartChannel": 11, "EndChannel": 109
        """
        # Test: Send configure without start/end channel
        # Expected: ROI set to [11, 109]
        
    def test_default_frequency_range_0_to_1000(self):
        """
        Verify default frequency range is 0-1000 Hz.
        
        Config: "StartFrequency_hz": 0, "EndFrequency_hz": 1000
        """
        # Test: Send configure without frequency range
        # Expected: Frequency range [0, 1000] Hz
        
    def test_default_num_lines_to_display_200(self):
        """
        Verify default waterfall lines is 200.
        
        Config: "NumLinesToDisplay": 200
        """
        # Test: GET /waterfall without row_count parameter
        # Expected: Returns 200 rows (or less if not available)
        
    def test_default_time_window_30_seconds(self):
        """
        Verify default time window is 30 seconds for live view.
        
        Config: "TimeWindow": "30s"
        """
        # Test: Request live data without time window
        # Expected: Returns last 30 seconds of data
```

---

### Category C: NFFT Options Validation 🔢

**Purpose:** Validate allowed NFFT values match configuration

#### `tests/integration/api/test_nfft_options_validation.py`

```python
class TestNFFTOptionsValidation:
    """
    Test NFFT validation based on configuration options.
    
    Config: "nfftSingleChannel": [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]
    """
    
    VALID_NFFT_VALUES = [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]
    
    @pytest.mark.parametrize("nfft", VALID_NFFT_VALUES)
    def test_all_valid_nfft_values_accepted(self, nfft, focus_server_api):
        """
        Verify all NFFT values from config are accepted.
        
        Tests: 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536
        """
        # Test: Send configure with each valid nfft
        # Expected: 200 OK for all values
        
    def test_nfft_64_rejected(self):
        """
        Verify NFFT=64 is rejected (not in config options).
        """
        # Test: Send configure with nfft=64
        # Expected: 422 with "NFFT must be one of: [128, 256, ...]"
        
    def test_nfft_131072_rejected(self):
        """
        Verify NFFT=131072 is rejected (exceeds max 65536).
        """
        # Test: Send configure with nfft=131072
        # Expected: 422 with "NFFT exceeds maximum 65536"
        
    def test_nfft_boundary_min_128(self):
        """
        Verify minimum NFFT is 128.
        """
        # Test: Send configure with nfft=128
        # Expected: 200 OK (boundary test)
        
    def test_nfft_boundary_max_65536(self):
        """
        Verify maximum NFFT is 65536.
        """
        # Test: Send configure with nfft=65536
        # Expected: 200 OK (boundary test)
        
    def test_nfft_1000_not_power_of_2_rejected(self):
        """
        Verify NFFT=1000 (not power of 2) is rejected.
        """
        # Test: Send configure with nfft=1000
        # Expected: 422 with "NFFT must be power of 2"
```

---

### Category D: Multi-Window & Concurrency Tests 🪟

**Purpose:** Test concurrent operations and max windows constraint

#### `tests/integration/api/test_multi_window_concurrency.py`

```python
class TestMultiWindowConcurrency:
    """
    Test concurrent operations and max windows constraint.
    
    Config: "MaxWindows": 30, "NumLiveScreens": 30, "NumTabs": 10
    """
    
    def test_max_30_concurrent_windows(self):
        """
        Verify system supports up to 30 concurrent windows.
        
        Config: "MaxWindows": 30
        """
        # Test: Create 30 concurrent tasks
        # Expected: All tasks created successfully
        
    def test_31st_window_rejected_or_queued(self):
        """
        Verify 31st window is rejected or queued.
        """
        # Test: Create 31 concurrent tasks
        # Expected: 31st request returns 429 or queues
        
    def test_concurrent_roi_changes_across_windows(self):
        """
        Verify ROI changes work across multiple windows.
        """
        # Test: Create 5 windows, send different ROI to each
        # Expected: Each window maintains separate ROI state
        
    def test_concurrent_waterfall_polling_multiple_tasks(self):
        """
        Verify concurrent waterfall polling for multiple tasks.
        """
        # Test: Poll /waterfall for 10 tasks simultaneously
        # Expected: All polls succeed, no interference
        
    def test_10_tabs_navigation_performance(self):
        """
        Verify switching between 10 tabs maintains performance.
        
        Config: "NumTabs": 10
        """
        # Test: Create 10 tasks, poll each sequentially
        # Expected: Each response < 3s, no degradation
```

---

### Category E: gRPC Retry Logic Tests 🔄

**Purpose:** Test gRPC retry mechanism

#### `tests/integration/grpc/test_grpc_retry_logic.py`

```python
class TestGrpcRetryLogic:
    """
    Test gRPC retry mechanism.
    
    Config: "NumGrpcRetries": 10
    """
    
    def test_grpc_retries_up_to_10_times(self):
        """
        Verify gRPC retries up to 10 times on failure.
        
        Config: "NumGrpcRetries": 10
        """
        # Test: Simulate transient gRPC failure
        # Expected: Up to 10 retry attempts before failing
        
    def test_grpc_retry_exponential_backoff(self):
        """
        Verify gRPC retries use exponential backoff.
        """
        # Test: Monitor retry intervals
        # Expected: 1s, 2s, 4s, 8s, 16s, ... pattern
        
    def test_grpc_success_on_3rd_retry(self):
        """
        Verify gRPC succeeds when server recovers on 3rd retry.
        """
        # Test: Fail first 2 attempts, succeed on 3rd
        # Expected: Request succeeds, total 3 attempts logged
        
    def test_grpc_all_10_retries_exhausted_returns_error(self):
        """
        Verify error after all 10 retries exhausted.
        """
        # Test: Fail all 10 retry attempts
        # Expected: 503 Service Unavailable after 10 attempts
        
    def test_grpc_stream_min_timeout_600_seconds(self):
        """
        Verify gRPC stream minimum timeout is 600 seconds.
        
        Config: "GrpcStreamMinTimeout_sec": 600
        """
        # Test: Establish gRPC stream, measure timeout
        # Expected: Stream stays open for at least 600s
```

---

### Category F: View Type & Display Tests 📺

**Purpose:** Test different view types and display configurations

#### `tests/integration/api/test_view_types_and_display.py`

```python
class TestViewTypesAndDisplay:
    """
    Test different view types and display configurations.
    
    Config: "ViewType": "MultiChannelSpectrogram"
    """
    
    def test_multichannel_spectrogram_view(self):
        """
        Verify MultiChannelSpectrogram view returns expected data format.
        
        Config: "ViewType": "MultiChannelSpectrogram"
        """
        # Test: Request waterfall data for multichannel view
        # Expected: Data includes multiple channels (11-109)
        
    def test_display_time_axis_duration_30_seconds(self):
        """
        Verify display time axis duration is 30 seconds.
        
        Config: "DisplayTimeAxisDuration": 30
        """
        # Test: Request live data
        # Expected: Time range covers 30 seconds
        
    def test_refresh_rate_20_updates_per_second(self):
        """
        Verify refresh rate supports 20 updates per second.
        
        Config: "RefreshRate": 20
        """
        # Test: Poll waterfall data 20 times in 1 second
        # Expected: All requests succeed, data updates
        
    def test_split_screen_mode_supported(self):
        """
        Verify split screen mode is supported.
        
        Config: "SplitScreen": true
        """
        # Test: Create 2 tasks, request data simultaneously
        # Expected: Both tasks return data without interference
```

---

### Category G: Reconnection & Resilience Tests 🔌

**Purpose:** Test reconnection logic and resilience

#### `tests/integration/resilience/test_reconnection_logic.py`

```python
class TestReconnectionLogic:
    """
    Test automatic reconnection logic.
    
    Config: "EnableReconnection": true
    """
    
    def test_automatic_reconnection_enabled(self):
        """
        Verify automatic reconnection is enabled by default.
        
        Config: "EnableReconnection": true
        """
        # Test: Disconnect backend, wait for reconnection
        # Expected: Client automatically reconnects within 30s
        
    def test_reconnection_after_backend_restart(self):
        """
        Verify reconnection works after backend restart.
        """
        # Test: Restart Focus Server pod, monitor reconnection
        # Expected: Client reconnects and resumes operation
        
    def test_reconnection_preserves_task_state(self):
        """
        Verify reconnection preserves active task state.
        """
        # Test: Create task, disconnect, reconnect
        # Expected: Task still accessible after reconnection
        
    def test_reconnection_retries_with_backoff(self):
        """
        Verify reconnection retries with exponential backoff.
        """
        # Test: Keep backend down, monitor retry intervals
        # Expected: Retry attempts with increasing intervals
```

---

### Category H: Frontend API Integration Tests 🌐

**Purpose:** Test Frontend API endpoint

#### `tests/integration/api/test_frontend_api_integration.py`

```python
class TestFrontendAPIIntegration:
    """
    Test Frontend API integration.
    
    Config: "FrontendApi": "https://10.10.10.150:30443/prisma/api/internal/sites/prisma-210-1000"
    """
    
    def test_frontend_api_site_endpoint_accessible(self):
        """
        Verify Frontend API site endpoint is accessible.
        """
        # Test: GET https://10.10.10.150:30443/prisma/api/internal/sites/prisma-210-1000
        # Expected: 200 OK with site information
        
    def test_frontend_api_returns_site_id_prisma_210_1000(self):
        """
        Verify Frontend API returns correct site ID.
        
        Config: "SiteId": "prisma-210-1000"
        """
        # Test: Query Frontend API
        # Expected: Response includes "siteId": "prisma-210-1000"
        
    def test_backend_frontend_communication_integration(self):
        """
        Verify Backend and Frontend communicate correctly.
        """
        # Test: Create task via Backend, verify via Frontend API
        # Expected: Task visible in Frontend API
```

---

## 📊 Summary of New Tests

| Category | Tests | Priority | Effort |
|----------|-------|----------|--------|
| **A: Configuration Constraints** | 5 | 🔥 High | 2 days |
| **B: Default Values** | 5 | ⚠️ Medium | 2 days |
| **C: NFFT Options** | 7 | 🔥 High | 1 day |
| **D: Multi-Window Concurrency** | 5 | ⚠️ Medium | 3 days |
| **E: gRPC Retry Logic** | 5 | 🔥 High | 2 days |
| **F: View Types & Display** | 4 | 📅 Low | 2 days |
| **G: Reconnection Logic** | 4 | ⚠️ Medium | 2 days |
| **H: Frontend API Integration** | 3 | 📅 Low | 1 day |
| **Total** | **38 tests** | | **~15 days** |

---

## 🎯 Critical Updates Required

### 1. **Update gRPC Timeout in Performance Tests**

❌ **Wrong (from team):** 180 seconds  
✅ **Correct (from config):** 500 seconds (GrpcTimeout), 600 seconds (GrpcStreamMinTimeout)

**Action:**
```python
# tests/integration/performance/test_response_time_sla.py

# UPDATE THIS:
def test_grpc_connection_timeout_180s(self):  # ❌ WRONG!
    # Expected: Timeout after 180s

# TO THIS:
def test_grpc_connection_timeout_500s(self):  # ✅ CORRECT!
    """
    Verify gRPC connection timeout is 500 seconds.
    
    Config: "GrpcTimeout": 500
    Team said: 180s (INCORRECT!)
    """
    # Expected: Timeout after 500s ± 10s
```

### 2. **Add Sensor Range Boundary Tests**

**Discovery:** Maximum sensor index is **2222**, not unlimited!

**Action:**
```python
# tests/integration/api/test_dynamic_roi_adjustment.py

def test_roi_at_maximum_sensor_2222(self):
    """Verify ROI at maximum sensor (2222) is valid"""
    
def test_roi_exceeds_maximum_sensor_2223_rejected(self):
    """Verify ROI beyond 2222 is rejected"""
```

### 3. **Comprehensive NFFT Validation**

**Discovery:** Exact list of valid NFFT values: `[128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]`

**Action:**
- Parametrize test for all 10 valid values
- Test boundary values (128, 65536)
- Test invalid values (64, 131072)

---

## 🔄 Comparison with Previous Recommendations

### From `RECOMMENDED_ADDITIONAL_TESTS.md`:
- RabbitMQ Tests (8 tests) - ✅ **Still Critical!**
- Performance/SLA Tests (6 tests) - ⚠️ **UPDATE gRPC timeout!**
- Recording Lifecycle (5 tests) - ✅ **Still Important**
- Error Handling (11 tests) - ✅ **Still Important**

### New from Configuration Analysis:
- **Configuration Constraints (5 tests)** - 🔥 **NEW! High Priority**
- **NFFT Options Validation (7 tests)** - 🔥 **NEW! High Priority**
- **gRPC Retry Logic (5 tests)** - 🔥 **NEW! High Priority**
- **Multi-Window Concurrency (5 tests)** - ⚠️ **NEW! Medium Priority**

---

## 📅 Updated Implementation Plan

### Phase 1 (Week 1) - **Critical Updates & New High Priority** 🔥

1. ✅ **UPDATE:** `test_response_time_sla.py` - Fix gRPC timeout (180s → 500s)
2. ✅ **NEW:** `test_configuration_constraints.py` - 5 tests
3. ✅ **NEW:** `test_nfft_options_validation.py` - 7 tests
4. ✅ **NEW:** `test_grpc_retry_logic.py` - 5 tests
5. ✅ **EXISTING:** `test_rabbitmq_baby_analyzer.py` - 8 tests (from previous recommendation)

**Total Phase 1:** ~26 tests (including updates)

### Phase 2 (Week 2-3) - **Medium Priority** ⚠️

6. `test_configuration_defaults.py` - 5 tests
7. `test_multi_window_concurrency.py` - 5 tests
8. `test_reconnection_logic.py` - 4 tests
9. `test_recording_lifecycle.py` - 5 tests (from previous recommendation)
10. `test_partial_results_handling.py` - 4 tests (from previous recommendation)

**Total Phase 2:** ~23 tests

### Phase 3 (Future) - **Low Priority / Nice-to-Have** 📅

11. `test_view_types_and_display.py` - 4 tests
12. `test_frontend_api_integration.py` - 3 tests
13. UI/API Healing tests (from previous recommendation)

**Total Phase 3:** ~7+ tests

---

## 🎓 Key Learnings from Configuration

### 1. **Team Information Can Be Incorrect**
- Team said gRPC timeout is **180s**
- Config shows it's actually **500s** (almost 3x longer!)
- **Lesson:** Always verify against actual configuration

### 2. **Hidden Constraints Discovered**
- **SensorsRange: 2222** - We didn't know this limit!
- **MaxWindows: 30** - Concurrency limit discovered
- **FrequencyMinRange: 1** - Minimum frequency range

### 3. **Complete NFFT List Revealed**
- Previously tested: [128, 256, 512, 1024, 2048]
- Actually valid: [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]
- **Missing tests for:** 4096, 8192, 16384, 32768, 65536

### 4. **Default Values for Better Tests**
- Default ROI: channels 11-109 (not 0-100!)
- Default NFFT: 1024
- Default frequency: 0-1000 Hz
- Default waterfall lines: 200

---

## 💡 Recommendations

### Immediate Actions (This Week):

1. ✅ **Fix gRPC Timeout Test** - Change 180s → 500s
2. ✅ **Add Sensor Range Tests** - Test 0-2222 range
3. ✅ **Add Complete NFFT Tests** - Test all 10 valid values
4. ✅ **Add Constraint Validation** - Test frequency, window limits
5. ✅ **Add gRPC Retry Tests** - Test 10-retry mechanism

### Next Steps:

6. **Request actual configuration files** from team for all environments (dev, staging, prod)
7. **Compare configurations** - Identify differences between environments
8. **Create configuration validation tests** - Ensure deployed config matches expected values
9. **Document discovered limits** - Update technical specifications

---

**Total New Tests from Config:** ~38 tests  
**Critical Updates Required:** 3 tests  
**Total Combined:** ~86 new/updated tests (including previous recommendations)

**Expected Timeline:** 4-5 weeks for complete implementation  
**Priority Focus:** Phase 1 (26 tests) in Week 1

---

**Status:** 📋 Ready for Implementation  
**Next Step:** Update gRPC timeout test immediately!

