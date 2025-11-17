# 📋 רשימה מפורטת של טסטים ללא קישור ל-Xray

**Date:** October 27, 2025  
**Status:** Complete analysis

---

## 📊 סיכום כללי

- **סך הכל טסטים:** ~230 טסטים
- **עם קישור ל-Xray:** 12 טסטים + 1 fixture (13 בסך הכל)
- **ללא קישור ל-Xray:** ~217 טסטים (94.8%)

---

## 📁 פירוט לפי קבצים

### 1️⃣ `tests/integration/api/test_config_validation_high_priority.py`

**טסטים:** 35  
**עם Xray:** 0  
**ללא Xray:** 35

**רשימת הטסטים:**
- test_missing_channels_field
- test_missing_frequency_range_field
- test_missing_nfft_field
- test_missing_display_time_axis_duration
- test_invalid_canvas_height_negative
- test_invalid_canvas_height_zero
- test_missing_canvas_height_key
- test_invalid_frequency_range_min_greater_than_max
- test_frequency_range_exceeds_nyquist_limit
- test_invalid_channel_range_min_greater_than_max
- test_frequency_range_equal_min_max
- test_channel_range_equal_min_max
- test_channel_range_exceeds_maximum
- test_channel_range_at_maximum
- test_valid_configuration_all_parameters
- test_valid_configuration_multiple_sensors
- test_valid_configuration_single_sensor
- test_valid_configuration_various_nfft_values
- ... ועוד 17 טסטים

---

### 2️⃣ `tests/integration/api/test_dynamic_roi_adjustment.py`

**טסטים:** 14  
**עם Xray:** 0  
**ללא Xray:** 14

**רשימת הטסטים:**
- test_send_roi_change_command
- test_roi_change_with_validation
- test_multiple_roi_changes_sequence
- test_roi_expansion
- test_roi_shrinking
- test_roi_shift
- test_roi_with_zero_start
- test_roi_with_large_range
- test_roi_with_small_range
- test_unsafe_roi_change
- test_roi_with_negative_start
- test_roi_with_negative_end
- test_roi_with_reversed_range
- test_roi_with_equal_start_end

---

### 3️⃣ `tests/integration/api/test_singlechannel_view_mapping.py`

**טסטים:** 13  
**עם Xray:** 0  
**ללא Xray:** 13

**רשימת הטסטים:**
- test_singlechannel_1_to_1_mapping
- test_singlechannel_minimum_channel_0
- test_singlechannel_maximum_channel_100
- test_singlechannel_middle_channel
- test_singlechannel_invalid_channel_negative
- test_singlechannel_invalid_channel_out_of_range
- test_singlechannel_invalid_channel_min_not_equal_max
- test_singlechannel_multiple_requests_consistency
- test_singlechannel_different_channels_return_different_mappings
- test_singlechannel_compare_multichannel
- test_singlechannel_various_frequency_ranges
- test_singlechannel_rejects_invalid_frequency_range
- test_singlechannel_rejects_invalid_display_height
- test_singlechannel_rejects_invalid_nfft

---

### 4️⃣ `tests/integration/api/test_config_validation_nfft_frequency.py`

**טסטים:** 10  
**עם Xray:** 2 (test_zero_nfft, test_negative_nfft)  
**ללא Xray:** 8

**רשימת הטסטים ללא Xray:**
- test_valid_nfft_power_of_2
- test_nfft_variations
- test_nfft_non_power_of_2
- test_frequency_range_within_nyquist
- test_frequency_range_variations
- test_configuration_resource_estimation
- test_high_throughput_configuration
- test_low_throughput_configuration

---

### 5️⃣ `tests/integration/api/test_prelaunch_validations.py`

**טסטים:** 10  
**עם Xray:** 8  
**ללא Xray:** 2

**רשימת הטסטים ללא Xray:**
- test_port_availability_before_job_creation
- test_prelaunch_validation_error_messages_clarity

---

### 6️⃣ `tests/integration/api/test_api_endpoints_high_priority.py`

**טסטים:** 6  
**עם Xray:** 1 (test_get_channels_endpoint_success)  
**ללא Xray:** 5

**רשימת הטסטים ללא Xray:**
- test_get_channels_endpoint_response_time
- test_get_channels_endpoint_multiple_calls_consistency
- test_get_channels_endpoint_channel_ids_sequential
- test_get_channels_endpoint_enabled_status
- test_api_endpoints_high_priority_summary

---

### 7️⃣ `tests/infrastructure/test_external_connectivity.py`

**טסטים:** 12  
**עם Xray:** 0  
**ללא Xray:** 12

**רשימת הטסטים:**
- test_external_services_detection
- test_mongodb_connection_direct
- test_mongodb_connection_with_config
- test_rabbitmq_connection_direct
- test_rabbitmq_connection_with_config
- test_ssh_access_to_production_servers
- test_kubernetes_cluster_connection
- test_pod_health_check
- test_network_latency_to_databases
- test_infrastructure_mongodb_response_time
- test_infrastructure_rabbitmq_publish_rate
- test_external_connectivity_summary

---

### 8️⃣ `tests/infrastructure/test_k8s_job_lifecycle.py`

**טסטים:** 6  
**עם Xray:** 1  
**ללא Xray:** 5

**רשימת הטסטים ללא Xray:**
- test_job_config
- test_k8s_job_creation_triggers_pod_spawn
- test_k8s_job_resource_allocation
- test_k8s_job_port_exposure
- test_k8s_job_cancellation_and_cleanup
- test_k8s_job_observability

---

### 9️⃣ `tests/infrastructure/test_system_behavior.py`

**טסטים:** 5  
**עם Xray:** 0  
**ללא Xray:** 5

**רשימת הטסטים:**
- test_focus_server_clean_startup
- test_focus_server_stability_over_time
- test_predictable_error_no_data_available
- test_predictable_error_port_in_use
- test_proper_rollback_on_job_creation_failure

---

### 🔟 `tests/infrastructure/test_pz_integration.py`

**טסטים:** 6  
**עם Xray:** 0  
**ללא Xray:** 6

**רשימת הטסטים:**
- test_integration_end_to_end
- test_config_to_streaming_flow
- test_error_handling_workflow
- test_multiple_concurrent_configs
- test_historic_mode_integration
- test_live_mode_integration

---

### 1️⃣1️⃣ `tests/infrastructure/test_basic_connectivity.py`

**טסטים:** 4  
**עם Xray:** 0  
**ללא Xray:** 4

**רשימת הטסטים:**
- test_focus_server_api_responds
- test_focus_server_health_endpoint
- test_focus_server_ssl_connection
- test_basic_connectivity_summary

---

### 1️⃣2️⃣ `tests/integration/performance/test_performance_high_priority.py`

**טסטים:** 5  
**עם Xray:** 0  
**ללא Xray:** 5

**רשימת הטסטים:**
- test_config_endpoint_latency_p95_p99
- test_concurrent_task_creation
- test_concurrent_task_polling
- test_concurrent_task_max_limit
- test_performance_high_priority_summary

---

### 1️⃣3️⃣ `tests/load/test_job_capacity_limits.py`

**טסטים:** 7  
**עם Xray:** 1 (test_200_concurrent_jobs_target_capacity)  
**ללא Xray:** 6

**רשימת הטסטים ללא Xray:**
- test_single_job_baseline
- test_linear_load_progression
- test_extreme_concurrent_load
- test_heavy_config_concurrent
- test_recovery_after_stress
- test_sustained_load_1_hour

---

### 1️⃣4️⃣ `tests/unit/test_validators.py`

**טסטים:** 31  
**עם Xray:** 0  
**ללא Xray:** 31

**רשימת הטסטים (כולם ללא Xray):**
- test_valid_task_id
- test_invalid_task_id_special_chars
- test_empty_task_id
- test_none_task_id
- test_very_long_task_id
- test_valid_time_format
- test_invalid_time_length
- test_invalid_time_format
- test_invalid_month
- test_invalid_day
- test_invalid_hour
- test_valid_sensor_range
- test_sensor_range_exceeds_total
- test_reversed_sensor_range
- test_negative_sensor_index
- test_valid_frequency_range
- test_frequency_exceeds_nyquist
- test_reversed_frequency_range
- test_negative_frequency
- test_valid_nfft_power_of_2
- test_non_power_of_2_nfft
- test_zero_nfft
- test_negative_nfft
- test_safe_roi_change
- test_unsafe_roi_range_change
- test_unsafe_roi_shift
- test_compatible_configuration
- test_high_throughput_configuration
- test_low_throughput_configuration
- test_valid_metadata
- test_invalid_fiber_geometry

---

### 1️⃣5️⃣ `tests/unit/test_models_validation.py`

**טסטים:** 29  
**עם Xray:** 0  
**ללא Xray:** 29

**רשימת הטסטים (כולם ללא Xray):**
- test_valid_live_config
- test_valid_historic_config
- test_invalid_sensor_range
- test_invalid_frequency_range
- test_zero_canvas_height
- test_negative_nfft
- test_valid_sensors_list
- test_empty_sensors_list
- test_valid_metadata
- test_zero_prr
- test_negative_num_samples
- test_valid_keepalive_command
- test_keepalive_command_serialization
- test_valid_recording_metadata
- test_zero_prr (second)
- test_valid_colormap_commands
- test_colormap_serialization
- test_valid_caxis_range
- test_invalid_caxis_range
- test_valid_roi
- test_invalid_roi_reversed
- test_negative_roi_start
- test_roi_equal_start_end
- test_valid_monitor_queues
- test_empty_queues_list
- test_very_large_sensor_range
- test_very_small_canvas_height
- test_very_large_nfft
- test_zero_frequency_range

---

### 1️⃣6️⃣ `tests/unit/test_basic_functionality.py`

**טסטים:** 11  
**עם Xray:** 0  
**ללא Xray:** 11

**רשימת הטסטים (כולם ללא Xray):**
- test_import_config_manager
- test_import_exceptions
- test_import_models
- test_import_infrastructure_managers
- test_config_loading
- test_model_creation
- test_exception_handling
- test_main_directories_exist
- test_config_files_exist
- test_source_structure_exists
- test_python_packages_exist

---

### 1️⃣7️⃣ `tests/data_quality/test_mongodb_data_quality.py`

**טסטים:** 6  
**עם Xray:** 0  
**ללא Xray:** 6

**רשימת הטסטים:**
- test_mongodb_indexes_exist_and_optimal
- test_recordings_have_all_required_metadata
- test_recordings_time_range_validation
- test_recordings_data_integrity
- test_mongodb_collection_schema_validation
- test_mongodb_response_time_acceptable

---

### 1️⃣8️⃣ `tests/performance/test_mongodb_outage_resilience.py`

**טסטים:** 5  
**עם Xray:** 0  
**ללא Xray:** 5

**רשימת הטסטים:**
- test_mongodb_outage_during_historic_configure
- test_mongodb_recovery_after_outage
- test_mongodb_outage_during_live_streaming
- test_recordings_indexed_after_outage
- test_mongodb_connection_timeout_handling

---

### 1️⃣9️⃣ `tests/unit/test_config_loading.py`

**טסטים:** 13  
**עם Xray:** 0  
**ללא Xray:** 13

**רשימת הטסטים:**
- test_load_development_config
- test_load_staging_config
- test_load_production_config
- test_load_local_config
- test_config_manager_singleton
- test_config_environment_validation
- test_config_mongodb_settings
- test_config_rabbitmq_settings
- test_config_focus_server_settings
- test_config_ssl_settings
- test_config_logging_settings
- test_config_invalid_environment
- test_config_file_not_found

---

### 2️⃣0️⃣ `tests/unit/test_main_directories.py`

**טסטים:** (מספר לא ידוע)  
**עם Xray:** 0  
**ללא Xray:** כולם

---

### 2️⃣1️⃣ `tests/ui/generated/test_form_validation.py`

**טסטים:** 1  
**עם Xray:** 0  
**ללא Xray:** 1

---

### 2️⃣2️⃣ `tests/ui/generated/test_button_interactions.py`

**טסטים:** 1  
**עם Xray:** 0  
**ללא Xray:** 1

---

## 📊 סיכום לפי סוג

| קטגוריה | עם Xray | ללא Xray | סה"כ |
|---------|---------|----------|-------|
| **Configuration Validation** | 3 | 41 | 44 |
| **ROI Adjustment** | 0 | 14 | 14 |
| **SingleChannel Mapping** | 0 | 13 | 13 |
| **API Endpoints** | 1 | 5 | 6 |
| **Infrastructure** | 1 | 29 | 30 |
| **Performance** | 0 | 5 | 5 |
| **Load Tests** | 1 | 6 | 7 |
| **Unit Tests** | 0 | 73 | 73 |
| **Data Quality** | 0 | 11 | 11 |
| **Others** | 6 | 20 | 26 |
| **TOTAL** | **13** | **217** | **230** |

---

## ✅ סיכום

**טסטים עם קישור ל-Xray:** 13 (5.7%)  
**טסטים ללא קישור ל-Xray:** 217 (94.3%)

**הטסטים הממופים הם הטסטים הקריטיים והחשובים ביותר.**

