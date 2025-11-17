# 📍 Complete Tests Directory Map
## מפה מפורטת של כל קבצי הטסטים - איפה כל דבר נמצא

**Date:** 2025-10-21  
**Location:** `C:\Projects\focus_server_automation\tests\`  
**Total Test Files:** 20 files  

---

## 🗺️ Full Directory Tree with Files

```
tests/
│
├── conftest.py                              # Main pytest configuration & fixtures
├── README.md                                # Tests structure guide
│
├── 🟢 integration/                          # INTEGRATION Tests (Xray category)
│   ├── __init__.py
│   │
│   ├── configuration/                       # Configuration & Validation
│   │   ├── __init__.py
│   │   └── test_spectrogram_pipeline.py    # ⭐ 13 tests
│   │       - NFFT validation (128-4096)
│   │       - Frequency range (Nyquist!)
│   │       - Resource estimation
│   │       - Colormap commands
│   │       - CAxis commands
│   │
│   ├── historic_playback/                   # Historic Playback
│   │   ├── __init__.py
│   │   └── test_historic_playback_flow.py   # ⭐ 14 tests
│   │       - Configure historic task
│   │       - Time range validation
│   │       - Future/old timestamps
│   │       - Reversed time range
│   │       - Data integrity
│   │       - Short/long durations
│   │
│   ├── live_monitoring/                     # Live Monitoring
│   │   ├── __init__.py
│   │   └── test_live_monitoring_flow.py     # ⭐ 17 tests
│   │       - Configure live task
│   │       - Get sensors list
│   │       - Get live metadata
│   │       - Poll data
│   │       - Get task metadata
│   │       - Complete flow
│   │       - Error handling
│   │
│   ├── singlechannel/                       # SingleChannel View
│   │   ├── __init__.py
│   │   └── test_singlechannel_view_mapping.py  # ⭐ 13 tests
│   │       - Channel 1, 7, 100 mapping
│   │       - vs MultiChannel comparison
│   │       - Min/max validation
│   │       - Zero channel
│   │       - Frequency ranges
│   │       - Invalid NFFT/height
│   │       - Consistency checks
│   │
│   ├── roi_adjustment/                      # ROI Dynamic Adjustment
│   │   ├── __init__.py
│   │   └── test_dynamic_roi_adjustment.py   # ⭐ 25+ tests
│   │       - Send ROI command via RabbitMQ
│   │       - Safety validation (50% limit)
│   │       - Expansion, shrinking, shift
│   │       - Unsafe changes
│   │       - Negative values
│   │       - Reversed range
│   │       - Edge cases
│   │
│   └── visualization/                       # Colormap & CAxis
│       └── __init__.py
│           (Tests currently in configuration/test_spectrogram_pipeline.py)
│
├── 🔵 api/                                  # API Tests (Xray category)
│   ├── __init__.py
│   ├── endpoints/                           # API Endpoints
│   │   └── __init__.py
│   │       ⚠️ No test files yet - to be created:
│   │       - test_channels_endpoint.py (PZ-13895)
│   │       - test_live_metadata_endpoint.py (PZ-13764-13765)
│   │       - test_metadata_endpoint.py (PZ-13563)
│   │       - test_recordings_in_time_range.py (PZ-13766)
│   │
│   └── singlechannel/                       # API SingleChannel
│       └── __init__.py
│           ⚠️ No test files yet - to be created:
│           - test_singlechannel_api.py (PZ-13813-13824)
│
├── 🟡 data_quality/                         # DATA QUALITY Tests (Xray)
│   ├── __init__.py
│   └── test_mongodb_data_quality.py         # ⭐ 6 tests
│       - Required collections exist (PZ-13683, PZ-13809)
│       - Recording schema validation (PZ-13684, PZ-13811)
│       - Metadata completeness (PZ-13685, PZ-13812)
│       - MongoDB indexes (PZ-13686, PZ-13810)
│       - Deleted recordings (soft delete)
│       - Historical vs live classification (PZ-13705)
│
├── 🔴 performance/                          # PERFORMANCE Tests (Xray)
│   └── __init__.py
│       ⚠️ No test files yet - to be created:
│       - test_api_latency_p95.py (PZ-13770, PZ-13571)
│       - test_concurrent_tasks.py (PZ-13896)
│       - test_throughput.py
│
├── 🟤 infrastructure/                       # INFRASTRUCTURE Tests (Xray)
│   ├── __init__.py
│   ├── test_basic_connectivity.py           # ⭐ 3 tests
│   │   - MongoDB direct connection
│   │   - Kubernetes direct connection
│   │   - SSH direct connection
│   │
│   ├── test_external_connectivity.py        # ⭐ 13 tests
│   │   - MongoDB connection & operations
│   │   - MongoDB status via K8s
│   │   - Kubernetes connection
│   │   - K8s list deployments
│   │   - K8s list pods
│   │   - SSH connection (jump host)
│   │   - SSH network operations
│   │   - All services summary
│   │   - Quick ping tests
│   │
│   ├── test_mongodb_outage_resilience.py    # ⭐ 5 tests
│   │   - Scale down outage (503)
│   │   - Network block outage
│   │   - No live impact during outage
│   │   - Logging and metrics
│   │   - Cleanup and restore
│   │
│   └── test_pz_integration.py               # ⭐ 6 tests
│       - PZ repository available
│       - Microservices listing
│       - Focus server access
│       - Version info
│       - Import capability
│       - Integration summary
│
├── 🔐 security/                             # SECURITY Tests (Xray)
│   └── __init__.py
│       ⚠️ No test files yet - to be created:
│       - test_malformed_input.py (PZ-13769)
│       - test_input_validation.py (PZ-13572)
│
├── ⚡ stress/                               # STRESS Tests (Xray)
│   └── __init__.py
│       ⚠️ No test files yet - to be created:
│       - test_extreme_values.py (PZ-13880)
│       - test_resource_limits.py
│
├── 🔬 unit/                                 # UNIT Tests (NOT in Xray)
│   ├── test_validators.py                   # ⭐ 30+ tests
│   │   - Task ID validation
│   │   - Time format validation
│   │   - Sensor range validation
│   │   - Frequency range validation
│   │   - NFFT validation
│   │   - ROI change validation
│   │   - Configuration compatibility
│   │   - Metadata validation
│   │
│   ├── test_models_validation.py            # ⭐ 20+ tests
│   │   - ConfigureRequest validation
│   │   - SensorsListResponse validation
│   │   - Metadata validation
│   │   - WaterfallResponse validation
│   │   - BabyAnalyzerCommands validation
│   │   - RecordingMetadata validation
│   │
│   ├── test_config_loading.py               # ⭐ 12 tests
│   │   - Load environments (production, staging, local)
│   │   - Invalid environment handling
│   │   - Nested config access
│   │   - Default values
│   │   - Import tests
│   │   - Package structure tests
│   │
│   └── test_basic_functionality.py          # ⭐ 11 tests
│       - Framework imports
│       - Exception handling
│       - Project structure validation
│       - Config file existence
│       - Source structure validation
│
├── 🎭 ui/                                   # UI Tests (Placeholder)
│   ├── __init__.py
│   └── generated/
│       ├── test_form_validation.py          # 1 test (Playwright)
│       └── test_button_interactions.py      # 1 test (Playwright)
│
├── fixtures/                                # Shared Fixtures (Empty - for future)
│   └── __init__.py
│
└── helpers/                                 # Test Helpers (Empty - for future)
    └── __init__.py
```

---

## 📊 Test Count by Category

| Category | Subdirectory | Test Files | Test Count | Xray IDs |
|----------|--------------|------------|-----------|----------|
| **🟢 Integration** | | **5 files** | **~82 tests** | PZ-13784-13880 |
| ↳ Configuration | `integration/configuration/` | 1 | 13 | PZ-13873-13880 |
| ↳ Historic | `integration/historic_playback/` | 1 | 14 | PZ-13863-13872 |
| ↳ Live | `integration/live_monitoring/` | 1 | 17 | PZ-13547 |
| ↳ SingleChannel | `integration/singlechannel/` | 1 | 13 | PZ-13813-13862 |
| ↳ ROI | `integration/roi_adjustment/` | 1 | 25 | PZ-13784-13800 |
| ↳ Visualization | `integration/visualization/` | 0 | (in config) | PZ-13801-13805 |
| **🔵 API** | | **0 files** | **0 tests** | PZ-13560-13766 |
| **🟡 Data Quality** | `data_quality/` | 1 | 6 | PZ-13683-13812 |
| **🔴 Performance** | `performance/` | 0 | 0 | PZ-13770, PZ-13896 |
| **🟤 Infrastructure** | `infrastructure/` | 4 | 27 | PZ-13806-13808 |
| **🔐 Security** | `security/` | 0 | 0 | PZ-13769, PZ-13572 |
| **⚡ Stress** | `stress/` | 0 | 0 | PZ-13880 |
| **🔬 Unit** | `unit/` | 4 | 73 | N/A |
| **🎭 UI** | `ui/generated/` | 2 | 2 | N/A |
| **Total** | | **17 files** | **~202 tests** | ~100 IDs |

---

## 📁 Detailed Breakdown

### 🟢 integration/ (82 tests in 5 files)

#### 1. integration/configuration/test_spectrogram_pipeline.py
**מה יש בקובץ:** (13 tests)
```python
TestNFFTConfiguration:
  - test_valid_nfft_power_of_2
  - test_nfft_variations (128, 256, 512, 1024, 2048, 4096)
  - test_nfft_non_power_of_2

TestFrequencyConfiguration:
  - test_frequency_range_within_nyquist ⭐ CRITICAL
  - test_frequency_range_variations

TestVisualizationCommands:
  - test_colormap_commands
  - test_caxis_adjustment
  - test_caxis_with_invalid_range

TestResourceEstimation:
  - test_configuration_resource_estimation
  - test_high_throughput_configuration
  - test_low_throughput_configuration

TestInvalidConfigs:
  - test_zero_nfft
  - test_negative_nfft
```

**Xray IDs:** PZ-13873-13880, PZ-13801-13805

---

#### 2. integration/historic_playback/test_historic_playback_flow.py
**מה יש בקובץ:** (14 tests)
```python
TestHistoricPlaybackHappyPath:
  - test_configure_historic_task_success
  - test_poll_historic_playback_until_completion

TestHistoricPlaybackValidation:
  - test_historic_playback_with_short_duration
  - test_historic_playback_data_integrity
  - test_historic_with_very_old_timestamps
  - test_historic_with_future_timestamps
  - test_historic_with_reversed_time_range
  - test_historic_with_very_long_duration

TestHistoricPlaybackEdgeCases:
  - test_config_with_non_numeric_time
  - test_config_with_invalid_time_format
  - (more edge cases)
```

**Xray IDs:** PZ-13863-13872

---

#### 3. integration/live_monitoring/test_live_monitoring_flow.py
**מה יש בקובץ:** (17 tests)
```python
TestLiveMonitoringHappyPath:
  - test_configure_live_task_success
  - test_get_sensors_list ⭐ Important!
  - test_get_live_metadata
  - test_poll_waterfall_data_live_task
  - test_get_task_metadata
  - test_complete_live_monitoring_flow

TestLiveMonitoringErrorHandling:
  - test_waterfall_with_invalid_task_id
  - test_waterfall_with_zero_row_count
  - test_waterfall_with_negative_row_count
  - test_waterfall_with_very_large_row_count
  - test_metadata_for_invalid_task_id

TestLiveMonitoringStress:
  - test_rapid_waterfall_polling

TestLiveMonitoringValidation:
  - test_config_with_invalid_sensor_range
  - test_config_with_invalid_frequency_range
  - test_config_with_zero_canvas_height
  - test_config_with_non_numeric_time
  - test_config_with_invalid_time_format
```

**Xray IDs:** PZ-13547

---

#### 4. integration/singlechannel/test_singlechannel_view_mapping.py
**מה יש בקובץ:** (13 tests)
```python
TestSingleChannelMapping:
  - test_configure_singlechannel_mapping (channel 7)
  - test_configure_singlechannel_channel_1
  - test_configure_singlechannel_channel_100
  - test_singlechannel_vs_multichannel_comparison

TestSingleChannelValidation:
  - test_singlechannel_with_min_not_equal_max_should_fail
  - test_singlechannel_with_zero_channel
  - test_singlechannel_with_different_frequency_ranges
  - test_singlechannel_with_invalid_nfft
  - test_singlechannel_with_invalid_height
  - test_singlechannel_with_invalid_frequency_range

TestSingleChannelConsistency:
  - test_same_channel_multiple_requests_consistent_mapping
  - test_different_channels_different_mappings

Summary:
  - test_module_summary
```

**Xray IDs:** PZ-13813-13862

---

#### 5. integration/roi_adjustment/test_dynamic_roi_adjustment.py
**מה יש בקובץ:** (25+ tests)
```python
TestROICommandsViaRabbitMQ:
  - test_send_roi_change_command_via_rabbitmq
  - test_roi_change_with_safety_validation
  - test_multiple_roi_changes_in_sequence

TestROIExpansionAndShrinking:
  - test_roi_expansion_increase_range
  - test_roi_shrinking_decrease_range
  - test_roi_shift_move_range

TestROIEdgeCases:
  - test_roi_with_equal_start_and_end
  - test_roi_with_reversed_range
  - test_roi_with_negative_start
  - test_roi_reject_negative_end
  - test_roi_with_small_range
  - test_roi_with_large_range
  - test_roi_starting_at_zero

TestROIUnsafeChanges:
  - test_unsafe_roi_change_large_jump
  - test_unsafe_roi_range_change_over_50_percent
  - test_unsafe_roi_shift_large_position
  - test_safe_roi_change_within_limits

(+ more ROI validation tests)
```

**Xray IDs:** PZ-13784-13800

---

### 🔵 api/ (0 tests - TO BE CREATED)

**Empty placeholder directories:**
- `api/endpoints/` - ⚠️ צריך ליצור test files
- `api/singlechannel/` - ⚠️ צריך ליצור test files

**Tests to create:**
- test_channels_endpoint.py
- test_live_metadata_endpoint.py
- test_recordings_in_time_range.py
- test_singlechannel_api.py

---

### 🟡 data_quality/ (1 file, 6 tests)

#### test_mongodb_data_quality.py
**מה יש בקובץ:** (6 tests)
```python
TestMongoDBDataQuality:
  - test_required_collections_exist
    → Checks: base_paths, GUID collections exist
    
  - test_recording_schema_validation
    → Validates recording document structure
    
  - test_recordings_have_all_required_metadata
    → Checks: prr, num_samples_per_trace, timestamps
    
  - test_mongodb_indexes_exist_and_optimal
    → Validates indexes on recordings collection
    
  - test_deleted_recordings_marked_properly
    → Soft delete validation
    
  - test_historical_vs_live_recordings
    → Classification based on age (1 hour threshold)
```

**Xray IDs:** PZ-13683-13812

---

### 🔴 performance/ (0 tests - TO BE CREATED)

**Empty - Need to create:**
- test_api_latency_p95.py (P95/P99 latency measurement)
- test_concurrent_tasks.py (concurrent load test)
- test_throughput.py (data throughput validation)

---

### 🟤 infrastructure/ (4 files, 27 tests)

#### 1. test_basic_connectivity.py (3 tests)
```python
- test_mongodb_direct_connection
  → Quick MongoDB TCP ping
  
- test_kubernetes_direct_connection
  → Quick K8s API ping
  
- test_ssh_direct_connection
  → Quick SSH connection test
```

#### 2. test_external_connectivity.py (13 tests)
```python
TestExternalServicesConnectivity:
  - test_mongodb_connection (full connection suite)
  - test_mongodb_status_via_kubernetes
  - test_kubernetes_connection
  - test_kubernetes_list_deployments
  - test_kubernetes_list_pods
  - test_ssh_connection (jump + target host)
  - test_ssh_network_operations
  - test_all_services_summary

Module-level:
  - test_quick_mongodb_ping
  - test_quick_kubernetes_ping
  - test_quick_ssh_ping
```

#### 3. test_mongodb_outage_resilience.py (5 tests)
```python
TestMongoDBOutageResilience:
  - test_mongodb_scale_down_outage_returns_503_no_orchestration
  - test_mongodb_network_block_outage_returns_503_no_orchestration
  - test_mongodb_outage_no_live_impact
  - test_mongodb_outage_logging_and_metrics
  - test_mongodb_outage_cleanup_and_restore
```

#### 4. test_pz_integration.py (6 tests)
```python
- test_pz_repository_available
- test_pz_microservices_listing
- test_pz_focus_server_access
- test_pz_version_info
- test_pz_import_capability
- test_pz_integration_summary
```

**Xray IDs:** PZ-13806-13808, PZ-13767-13768

---

### 🔐 security/ (0 tests - TO BE CREATED)

**Empty - Need to create:**
- test_malformed_input.py
- test_input_validation.py

---

### ⚡ stress/ (0 tests - TO BE CREATED)

**Empty - Need to create:**
- test_extreme_values.py
- test_resource_limits.py

---

### 🔬 unit/ (4 files, 73 tests)

#### 1. test_validators.py (30+ tests)
**Unit tests for validation functions in `src/utils/validators.py`**

#### 2. test_models_validation.py (20+ tests)
**Unit tests for Pydantic models in `src/models/`**

#### 3. test_config_loading.py (12 tests)
**Unit tests for ConfigManager in `config/config_manager.py`**

#### 4. test_basic_functionality.py (11 tests)
**Basic framework functionality tests**

---

### 🎭 ui/ (2 files, 2 tests)

**Placeholder UI tests - not active**

---

## 🎯 Summary

### קבצים קיימים (17 test files):
1. ✅ integration/configuration/test_spectrogram_pipeline.py
2. ✅ integration/historic_playback/test_historic_playback_flow.py
3. ✅ integration/live_monitoring/test_live_monitoring_flow.py
4. ✅ integration/singlechannel/test_singlechannel_view_mapping.py
5. ✅ integration/roi_adjustment/test_dynamic_roi_adjustment.py
6. ✅ data_quality/test_mongodb_data_quality.py
7-10. ✅ infrastructure/* (4 files)
11-14. ✅ unit/* (4 files)
15-16. ✅ ui/generated/* (2 files)

### תיקיות ריקות (צריך ליצור tests):
17. ⚠️ integration/visualization/ (empty)
18. ⚠️ api/endpoints/ (empty)
19. ⚠️ api/singlechannel/ (empty)
20. ⚠️ performance/ (empty)
21. ⚠️ security/ (empty)
22. ⚠️ stress/ (empty)

---

**Total Test Files:** 17 existing + 6 empty categories  
**Total Tests:** ~202 tests  
**Structure:** ✅ 100% Xray-aligned  
**Organization:** ✅ Perfect

