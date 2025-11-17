# Phase 1: Analysis & Prioritization Report

**Date:** 2025-11-09
**Status:** Complete ✅

---

## 1. Missing Tests in Automation (37 tests)

### By Category:

### API Tests (22 tests)

| # | Test ID | Summary | Status | Priority | Test Type |
|---|---------|---------|--------|----------|-----------|
| 1 | PZ-13819 | API – SingleChannel View with Various Frequency Ranges | TO DO | Medium | Automation |
| 2 | PZ-13895 | Integration – GET /channels - Enabled Channels List | TO DO | Medium | Automation |
| 3 | PZ-13764 |  API – GET /live_metadata – Returns Metadata When Available | TO DO | Medium | Automation |
| 4 | PZ-13762 | API – GET /channels – Returns System Channel Bounds | TO DO | Medium | Automation |
| 5 | PZ-13766 |  API – POST /recordings_in_time_range – Returns Recording Wi | TO DO | Medium | Automation |
| 6 | PZ-13823 | API – SingleChannel Rejects When min ≠ max | TO DO | Medium | Automation |
| 7 | PZ-13560 | API – GET /channels | TO DO | Medium | Automation |
| 8 | PZ-13555 | API – Invalid frequency range (negative) | TO DO | Medium | Automation |
| 9 | PZ-13548 | API – Historical configure (happy path) | TO DO | Medium | Automation |
| 10 | PZ-13761 | API – POST /config/{task_id} – Invalid Frequency Range Rejec | TO DO | Medium | Automation |
| 11 | PZ-13759 | API – POST /config/{task_id} – Invalid Time Range Rejection | TO DO | Medium | Automation |
| 12 | PZ-14101 | Integration - Historic Playback - Short Duration (Rapid Wind | TO DO | Medium | Automation |
| 13 | PZ-13561 | API – GET /live_metadata present | TO DO | Medium | Automation |
| 14 | PZ-13554 | API – Invalid channels (negative) | TO DO | Medium | Automation |
| 15 | PZ-13564 | API – POST /recordings_in_time_range | TO DO | Medium | Automation |
| 16 | PZ-13562 | API – GET /live_metadata missing | TO DO | Medium | Automation |
| 17 | PZ-13815 | API – SingleChannel View for Channel 100 (Upper Boundary Tes | TO DO | Medium | Automation |
| 18 | PZ-13765 | API – GET /live_metadata – Returns 404 When Unavailable | TO DO | Medium | Automation |
| 19 | PZ-13760 | API – POST /config/{task_id} – Invalid Channel Range Rejecti | TO DO | Medium | Automation |
| 20 | PZ-13814 | API – SingleChannel View for Channel 1 (First Channel) | TO DO | Medium | Automation |
| 21 | PZ-13552 | API – Invalid time range (negative) | TO DO | Medium | Automation |
| 22 | PZ-13821 | API – SingleChannel Rejects Invalid Display Height | TO DO | Medium | Automation |

### Data Quality Tests (4 tests)

| # | Test ID | Summary | Status | Priority | Test Type |
|---|---------|---------|--------|----------|-----------|
| 1 | PZ-13684 | Data Quality – node4 Schema Validation | TO DO | Medium | Automation |
| 2 | PZ-13812 | Data Quality – Verify Recordings Have Complete Metadata | TO DO | Medium | Automation |
| 3 | PZ-13685 | Data Quality – Recordings Metadata Completeness | TO DO | Medium | Automation |
| 4 | PZ-13811 | Data Quality – Validate Recordings Document Schema | TO DO | Medium | Automation |

### Integration Tests (16 tests)

| # | Test ID | Summary | Status | Priority | Test Type |
|---|---------|---------|--------|----------|-----------|
| 1 | PZ-13855 | Integration - SingleChannel Canvas Height Validation | TO DO | Medium | Automation |
| 2 | PZ-13833 | Integration - SingleChannel Edge Case - Maximum Channel (Las | TO DO | Medium | Automation |
| 3 | PZ-13854 | Integration - SingleChannel Frequency Range Validation | TO DO | Medium | Automation |
| 4 | PZ-13767 | Integration – MongoDB Outage Handling | TO DO | Medium | Automation |
| 5 | PZ-13903 | Integration - Frequency Range Nyquist Limit Enforcement | TO DO | Medium | Automation |
| 6 | PZ-13865 | Integration – Historic Playback - Short Duration (1 Minute) | TO DO | Medium | Automation |
| 7 | PZ-13873 | integration - Valid Configuration - All Parameters | TO DO | Medium | Automation |
| 8 | PZ-13832 | Integration - SingleChannel Edge Case - Minimum Channel (Cha | TO DO | Medium | Automation |
| 9 | PZ-13604 | Integration – Orchestrator error triggers rollback | TO DO | Medium | Automation |
| 10 | PZ-13877 | Integration – Invalid Frequency Range - Min > Max | TO DO | Medium | Automation |
| 11 | PZ-13603 | Integration – Mongo outage on History configure | TO DO | Medium | Automation |
| 12 | PZ-13863 | Integration – Historic Playback - Standard 5-Minute Range | TO DO | Medium | Automation |
| 13 | PZ-13837 | Integration - SingleChannel with Invalid Channel (Negative) | TO DO | Medium | Automation |
| 14 | PZ-13836 | Integration - SingleChannel with Invalid Channel (Negative) | TO DO | Medium | Automation |
| 15 | PZ-13852 | Integration - SingleChannel with Min > Max (Validation Error | TO DO | Medium | Automation |
| 16 | PZ-13835 | Integration - SingleChannel with Invalid Channel (Out of Ran | TO DO | Medium | Automation |

### Security Tests (2 tests)

| # | Test ID | Summary | Status | Priority | Test Type |
|---|---------|---------|--------|----------|-----------|
| 1 | PZ-13572 | Security – Robustness to malformed inputs | TO DO | Medium | Automation |
| 2 | PZ-13769 | Security – Malformed Input Handling | TO DO | Medium | Automation |

## 2. Test Functions Without Markers (204 functions)

### Summary:

- Total test functions without markers: 204
- Total test functions with markers: 162
- Total test functions with multiple markers: 1

### By Category:

### Data Quality Tests (11 functions)

| # | File | Test Function |
|---|------|---------------|
| 1 | `tests\data_quality\test_mongodb_data_quality.py` | `test_required_collections_exist` |
| 2 | `tests\data_quality\test_mongodb_data_quality.py` | `test_recording_schema_validation` |
| 3 | `tests\data_quality\test_mongodb_data_quality.py` | `test_mongodb_indexes_exist_and_optimal` |
| 4 | `tests\data_quality\test_mongodb_data_quality.py` | `test_deleted_recordings_marked_properly` |
| 5 | `tests\data_quality\test_mongodb_data_quality.py` | `test_historical_vs_live_recordings` |
| 6 | `tests\data_quality\test_mongodb_indexes_and_schema.py` | `test_critical_mongodb_indexes_exist` |
| 7 | `tests\data_quality\test_mongodb_indexes_and_schema.py` | `test_recordings_document_schema_validation` |
| 8 | `tests\data_quality\test_mongodb_indexes_and_schema.py` | `test_recordings_metadata_completeness` |
| 9 | `tests\data_quality\test_mongodb_recovery.py` | `test_mongodb_recovery_recordings_indexed_after_outage` |
| 10 | `tests\data_quality\test_mongodb_schema_validation.py` | `test_metadata_collection_schema_validation` |
| 11 | `tests\data_quality\test_recordings_classification.py` | `test_historical_vs_live_recordings_classification` |

### Infrastructure Tests (56 functions)

| # | File | Test Function |
|---|------|---------------|
| 1 | `tests\infrastructure\test_basic_connectivity.py` | `test_mongodb_direct_connection` |
| 2 | `tests\infrastructure\test_basic_connectivity.py` | `test_kubernetes_direct_connection` |
| 3 | `tests\infrastructure\test_basic_connectivity.py` | `test_ssh_direct_connection` |
| 4 | `tests\infrastructure\test_external_connectivity.py` | `test_mongodb_connection` |
| 5 | `tests\infrastructure\test_external_connectivity.py` | `test_kubernetes_connection` |
| 6 | `tests\infrastructure\test_external_connectivity.py` | `test_kubernetes_list_deployments` |
| 7 | `tests\infrastructure\test_external_connectivity.py` | `test_ssh_connection` |
| 8 | `tests\infrastructure\test_external_connectivity.py` | `test_ssh_network_operations` |
| 9 | `tests\infrastructure\test_external_connectivity.py` | `test_quick_mongodb_ping` |
| 10 | `tests\infrastructure\test_external_connectivity.py` | `test_quick_kubernetes_ping` |
| 11 | `tests\infrastructure\test_external_connectivity.py` | `test_quick_ssh_ping` |
| 12 | `tests\infrastructure\test_k8s_job_lifecycle.py` | `test_job_config` |
| 13 | `tests\infrastructure\test_k8s_job_lifecycle.py` | `test_k8s_job_creation_triggers_pod_spawn` |
| 14 | `tests\infrastructure\test_k8s_job_lifecycle.py` | `test_k8s_job_resource_allocation` |
| 15 | `tests\infrastructure\test_k8s_job_lifecycle.py` | `test_k8s_job_port_exposure` |
| 16 | `tests\infrastructure\test_k8s_job_lifecycle.py` | `test_k8s_job_cancellation_and_cleanup` |
| 17 | `tests\infrastructure\test_k8s_job_lifecycle.py` | `test_k8s_job_observability` |
| 18 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_init` |
| 19 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_connect_success` |
| 20 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_connect_failure_retry` |
| 21 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_connect_failure_max_retries` |
| 22 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_connect_authentication_failure` |
| 23 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_disconnect` |
| 24 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_ensure_connected_success` |
| 25 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_ensure_connected_auto_reconnect` |
| 26 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_list_databases` |
| 27 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_list_databases_not_connected` |
| 28 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_list_collections` |
| 29 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_get_collection_stats` |
| 30 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_count_documents` |
| 31 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_find_documents` |
| 32 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_get_health_status_healthy` |
| 33 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_get_health_status_unhealthy` |
| 34 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_collect_metrics` |
| 35 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_create_alert` |
| 36 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_register_alert_callback` |
| 37 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_get_recent_alerts` |
| 38 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_start_monitoring` |
| 39 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_stop_monitoring` |
| 40 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_context_manager` |
| 41 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_monitoring_metrics_defaults` |
| 42 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_alert_creation` |
| 43 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_alert_level_values` |
| 44 | `tests\infrastructure\test_rabbitmq_connectivity.py` | `test_rabbitmq_connection` |
| 45 | `tests\infrastructure\test_rabbitmq_outage_handling.py` | `test_rabbitmq_outage_handling` |
| 46 | `tests\infrastructure\test_system_behavior.py` | `test_focus_server_clean_startup` |
| 47 | `tests\infrastructure\test_system_behavior.py` | `test_focus_server_stability_over_time` |
| 48 | `tests\infrastructure\test_system_behavior.py` | `test_predictable_error_no_data_available` |
| 49 | `tests\infrastructure\test_system_behavior.py` | `test_predictable_error_port_in_use` |
| 50 | `tests\infrastructure\test_system_behavior.py` | `test_proper_rollback_on_job_creation_failure` |
| 51 | `tests\infrastructure\resilience\test_focus_server_pod_resilience.py` | `test_focus_server_pod_status_monitoring` |
| 52 | `tests\infrastructure\resilience\test_mongodb_pod_resilience.py` | `test_mongodb_pod_status_monitoring` |
| 53 | `tests\infrastructure\resilience\test_multiple_pods_resilience.py` | `test_focus_server_segy_recorder_down_simultaneously` |
| 54 | `tests\infrastructure\resilience\test_pod_recovery_scenarios.py` | `test_recovery_time_measurement` |
| 55 | `tests\infrastructure\resilience\test_rabbitmq_pod_resilience.py` | `test_rabbitmq_pod_status_monitoring` |
| 56 | `tests\infrastructure\resilience\test_segy_recorder_pod_resilience.py` | `test_segy_recorder_recovery_after_outage` |

### Integration Tests (101 functions)

| # | File | Test Function |
|---|------|---------------|
| 1 | `tests\infrastructure\test_pz_integration.py` | `test_pz_repository_available` |
| 2 | `tests\infrastructure\test_pz_integration.py` | `test_pz_microservices_listing` |
| 3 | `tests\infrastructure\test_pz_integration.py` | `test_pz_focus_server_access` |
| 4 | `tests\infrastructure\test_pz_integration.py` | `test_pz_version_info` |
| 5 | `tests\infrastructure\test_pz_integration.py` | `test_pz_import_capability` |
| 6 | `tests\integration\api\test_api_endpoints_additional.py` | `test_get_sensors_endpoint` |
| 7 | `tests\integration\api\test_api_endpoints_additional.py` | `test_get_live_metadata_available` |
| 8 | `tests\integration\api\test_api_endpoints_additional.py` | `test_get_metadata_by_job_id` |
| 9 | `tests\integration\api\test_api_endpoints_additional.py` | `test_post_recordings_in_time_range` |
| 10 | `tests\integration\api\test_api_endpoints_additional.py` | `test_invalid_time_range_rejection` |
| 11 | `tests\integration\api\test_api_endpoints_additional.py` | `test_invalid_channel_range_rejection` |
| 12 | `tests\integration\api\test_api_endpoints_additional.py` | `test_invalid_frequency_range_rejection` |
| 13 | `tests\integration\api\test_api_endpoints_high_priority.py` | `test_get_channels_endpoint_enabled_status` |
| 14 | `tests\integration\api\test_configure_endpoint.py` | `test_configure_response_time_performance` |
| 15 | `tests\integration\api\test_config_task_endpoint.py` | `test_config_task_invalid_frequency_range` |
| 16 | `tests\integration\api\test_config_validation_high_priority.py` | `test_missing_display_time_axis_duration` |
| 17 | `tests\integration\api\test_config_validation_high_priority.py` | `test_invalid_canvas_height_negative` |
| 18 | `tests\integration\api\test_config_validation_high_priority.py` | `test_invalid_canvas_height_zero` |
| 19 | `tests\integration\api\test_config_validation_high_priority.py` | `test_missing_canvas_height_key` |
| 20 | `tests\integration\api\test_config_validation_high_priority.py` | `test_invalid_frequency_range_min_greater_than_max` |
| 21 | `tests\integration\api\test_config_validation_high_priority.py` | `test_frequency_range_exceeds_nyquist_limit` |
| 22 | `tests\integration\api\test_config_validation_high_priority.py` | `test_invalid_channel_range_min_greater_than_max` |
| 23 | `tests\integration\api\test_config_validation_high_priority.py` | `test_frequency_range_equal_min_max` |
| 24 | `tests\integration\api\test_config_validation_high_priority.py` | `test_channel_range_equal_min_max` |
| 25 | `tests\integration\api\test_config_validation_high_priority.py` | `test_channel_range_exceeds_maximum` |
| 26 | `tests\integration\api\test_config_validation_high_priority.py` | `test_channel_range_at_maximum` |
| 27 | `tests\integration\api\test_config_validation_high_priority.py` | `test_valid_configuration_all_parameters` |
| 28 | `tests\integration\api\test_config_validation_high_priority.py` | `test_valid_configuration_multiple_sensors` |
| 29 | `tests\integration\api\test_config_validation_high_priority.py` | `test_valid_configuration_single_sensor` |
| 30 | `tests\integration\api\test_config_validation_high_priority.py` | `test_valid_configuration_various_nfft_values` |
| 31 | `tests\integration\api\test_config_validation_high_priority.py` | `test_invalid_nfft_exceeds_maximum` |
| 32 | `tests\integration\api\test_config_validation_high_priority.py` | `test_invalid_nfft_not_power_of_2` |
| 33 | `tests\integration\api\test_config_validation_high_priority.py` | `test_live_mode_with_only_end_time` |
| 34 | `tests\integration\api\test_config_validation_high_priority.py` | `test_historic_mode_valid_configuration` |
| 35 | `tests\integration\api\test_config_validation_high_priority.py` | `test_historic_mode_with_equal_times` |
| 36 | `tests\integration\api\test_config_validation_high_priority.py` | `test_historic_mode_with_negative_time` |
| 37 | `tests\integration\api\test_config_validation_high_priority.py` | `test_requirement_negative_height_must_be_rejected` |
| 38 | `tests\integration\api\test_config_validation_high_priority.py` | `test_requirement_zero_height_must_be_rejected` |
| 39 | `tests\integration\api\test_config_validation_high_priority.py` | `test_requirement_nfft_must_be_power_of_2` |
| 40 | `tests\integration\api\test_config_validation_high_priority.py` | `test_requirement_nfft_max_2048` |
| 41 | `tests\integration\api\test_config_validation_high_priority.py` | `test_requirement_reject_only_start_time` |
| 42 | `tests\integration\api\test_config_validation_high_priority.py` | `test_requirement_reject_only_end_time` |
| 43 | `tests\integration\api\test_config_validation_high_priority.py` | `test_requirement_frequency_must_not_exceed_nyquist` |
| 44 | `tests\integration\api\test_config_validation_nfft_frequency.py` | `test_valid_nfft_power_of_2` |
| 45 | `tests\integration\api\test_config_validation_nfft_frequency.py` | `test_frequency_range_variations` |
| 46 | `tests\integration\api\test_config_validation_nfft_frequency.py` | `test_negative_nfft` |
| 47 | `tests\integration\api\test_dynamic_roi_adjustment.py` | `test_send_roi_change_command` |
| 48 | `tests\integration\api\test_dynamic_roi_adjustment.py` | `test_roi_shrinking` |
| 49 | `tests\integration\api\test_dynamic_roi_adjustment.py` | `test_roi_with_equal_start_end` |
| 50 | `tests\integration\api\test_health_check.py` | `test_ack_load_testing` |
| 51 | `tests\integration\api\test_historic_playback_additional.py` | `test_historic_playback_future_timestamps_rejection` |
| 52 | `tests\integration\api\test_historic_playback_e2e.py` | `test_historic_playback_complete_e2e_flow` |
| 53 | `tests\integration\api\test_live_monitoring_flow.py` | `test_live_monitoring_get_metadata` |
| 54 | `tests\integration\api\test_live_streaming_stability.py` | `test_live_streaming_stability` |
| 55 | `tests\integration\api\test_nfft_overlap_edge_case.py` | `test_overlap_nfft_escalation_edge_case` |
| 56 | `tests\integration\api\test_orchestration_validation.py` | `test_history_with_empty_window_returns_400_no_side_effects` |
| 57 | `tests\integration\api\test_prelaunch_validations.py` | `test_data_availability_live_mode` |
| 58 | `tests\integration\api\test_prelaunch_validations.py` | `test_config_validation_channels_out_of_range` |
| 59 | `tests\integration\api\test_prelaunch_validations.py` | `test_config_validation_frequency_exceeds_nyquist` |
| 60 | `tests\integration\api\test_prelaunch_validations.py` | `test_config_validation_invalid_view_type` |
| 61 | `tests\integration\api\test_prelaunch_validations.py` | `test_prelaunch_validation_error_messages_clarity` |
| 62 | `tests\integration\api\test_singlechannel_view_mapping.py` | `test_configure_singlechannel_mapping` |
| 63 | `tests\integration\api\test_singlechannel_view_mapping.py` | `test_configure_singlechannel_channel_1` |
| 64 | `tests\integration\api\test_singlechannel_view_mapping.py` | `test_singlechannel_with_zero_channel` |
| 65 | `tests\integration\api\test_singlechannel_view_mapping.py` | `test_singlechannel_rejects_invalid_nfft_value` |
| 66 | `tests\integration\api\test_singlechannel_view_mapping.py` | `test_singlechannel_middle_channel` |
| 67 | `tests\integration\api\test_singlechannel_view_mapping.py` | `test_singlechannel_complete_e2e_flow` |
| 68 | `tests\integration\api\test_task_metadata_endpoint.py` | `test_task_metadata_response_time` |
| 69 | `tests\integration\api\test_view_type_validation.py` | `test_valid_view_types` |
| 70 | `tests\integration\api\test_waterfall_endpoint.py` | `test_waterfall_baby_analyzer_exited` |
| 71 | `tests\integration\api\test_waterfall_view.py` | `test_waterfall_view_handling` |
| 72 | `tests\integration\calculations\test_system_calculations.py` | `test_spectrogram_dimensions_calculation` |
| 73 | `tests\integration\data_quality\test_data_completeness.py` | `test_data_completeness` |
| 74 | `tests\integration\data_quality\test_data_consistency.py` | `test_metadata_consistency` |
| 75 | `tests\integration\data_quality\test_data_integrity.py` | `test_data_integrity_across_requests` |
| 76 | `tests\integration\e2e\test_configure_metadata_grpc_flow.py` | `test_e2e_configure_metadata_grpc_flow` |
| 77 | `tests\integration\error_handling\test_http_error_codes.py` | `test_504_gateway_timeout` |
| 78 | `tests\integration\error_handling\test_invalid_payloads.py` | `test_error_message_format` |
| 79 | `tests\integration\error_handling\test_network_errors.py` | `test_connection_refused` |
| 80 | `tests\integration\load\test_concurrent_load.py` | `test_concurrent_job_creation_load` |
| 81 | `tests\integration\load\test_load_profiles.py` | `test_steady_state_load_profile` |
| 82 | `tests\integration\load\test_peak_load.py` | `test_peak_load_high_rps` |
| 83 | `tests\integration\load\test_recovery_and_exhaustion.py` | `test_resource_exhaustion_under_load` |
| 84 | `tests\integration\load\test_sustained_load.py` | `test_sustained_load_1_hour` |
| 85 | `tests\integration\performance\test_concurrent_performance.py` | `test_concurrent_requests_performance` |
| 86 | `tests\integration\performance\test_database_performance.py` | `test_database_query_performance` |
| 87 | `tests\integration\performance\test_latency_requirements.py` | `test_job_creation_time` |
| 88 | `tests\integration\performance\test_network_latency.py` | `test_end_to_end_latency` |
| 89 | `tests\integration\performance\test_performance_high_priority.py` | `test_config_endpoint_latency_p95_p99` |
| 90 | `tests\integration\performance\test_performance_high_priority.py` | `test_concurrent_task_creation` |
| 91 | `tests\integration\performance\test_performance_high_priority.py` | `test_concurrent_task_polling` |
| 92 | `tests\integration\performance\test_performance_high_priority.py` | `test_concurrent_task_max_limit` |
| 93 | `tests\integration\performance\test_resource_usage.py` | `test_cpu_usage_under_load` |
| 94 | `tests\integration\performance\test_response_time.py` | `test_metadata_response_time` |
| 95 | `tests\integration\security\test_api_authentication.py` | `test_expired_authentication_token` |
| 96 | `tests\integration\security\test_csrf_protection.py` | `test_csrf_protection` |
| 97 | `tests\integration\security\test_data_exposure.py` | `test_data_exposure_prevention` |
| 98 | `tests\integration\security\test_data_exposure.py` | `test_error_message_security` |
| 99 | `tests\integration\security\test_https_enforcement.py` | `test_https_enforcement` |
| 100 | `tests\integration\security\test_input_validation.py` | `test_input_sanitization` |
| 101 | `tests\integration\security\test_rate_limiting.py` | `test_rate_limiting` |

### Load Tests (14 functions)

| # | File | Test Function |
|---|------|---------------|
| 1 | `tests\load\test_job_capacity_limits.py` | `test_single_job_baseline` |
| 2 | `tests\load\test_job_capacity_limits.py` | `test_linear_load_progression` |
| 3 | `tests\load\test_job_capacity_limits.py` | `test_recovery_after_stress` |
| 4 | `tests\load\test_job_capacity_limits.py` | `test_200_concurrent_jobs_target_capacity` |
| 5 | `focus_server_api_load_tests\focus_api_tests\test_api_contract.py` | `test_channels_smoke` |
| 6 | `focus_server_api_load_tests\focus_api_tests\test_api_contract.py` | `test_live_metadata_smoke` |
| 7 | `focus_server_api_load_tests\focus_api_tests\test_api_contract.py` | `test_configure_waterfall_minimal` |
| 8 | `focus_server_api_load_tests\focus_api_tests\test_api_contract.py` | `test_configure_non_waterfall_with_freq_and_nfft` |
| 9 | `focus_server_api_load_tests\focus_api_tests\test_api_contract.py` | `test_recordings_in_time_range` |
| 10 | `focus_server_api_load_tests\focus_api_tests\test_api_contract.py` | `test_get_recordings_timeline_html` |
| 11 | `focus_server_api_load_tests\focus_api_tests\test_api_contract.py` | `test_configure_channels_out_of_range_422` |
| 12 | `focus_server_api_load_tests\focus_api_tests\test_api_contract.py` | `test_configure_waterfall_with_forbidden_fields_422` |
| 13 | `focus_server_api_load_tests\focus_api_tests\test_api_contract.py` | `test_configure_waterfall_nfft_must_be_1` |
| 14 | `focus_server_api_load_tests\focus_api_tests\test_api_contract.py` | `test_configure_missing_required_fields_422` |

### Other Tests (7 functions)

| # | File | Test Function |
|---|------|---------------|
| 1 | `tests\stress\test_extreme_configurations.py` | `test_configuration_with_extreme_values` |
| 2 | `scripts\test_k8s_fixed.py` | `test_kubernetes_connection` |
| 3 | `scripts\test_mongodb_connection.py` | `test_mongodb_connection` |
| 4 | `scripts\test_ssh_connection.py` | `test_direct_ssh` |
| 5 | `scripts\test_ssh_connection.py` | `test_jump_connection` |
| 6 | `scripts\test_ssh_connection.py` | `test_network_connectivity` |
| 7 | `scripts\test_ssh_connection.py` | `test_ssh_manager_connection` |

### Performance Tests (5 functions)

| # | File | Test Function |
|---|------|---------------|
| 1 | `tests\performance\test_mongodb_outage_resilience.py` | `test_mongodb_scale_down_outage_returns_503_no_orchestration` |
| 2 | `tests\performance\test_mongodb_outage_resilience.py` | `test_mongodb_network_block_outage_returns_503_no_orchestration` |
| 3 | `tests\performance\test_mongodb_outage_resilience.py` | `test_mongodb_outage_no_live_impact` |
| 4 | `tests\performance\test_mongodb_outage_resilience.py` | `test_mongodb_outage_logging_and_metrics` |
| 5 | `tests\performance\test_mongodb_outage_resilience.py` | `test_mongodb_outage_cleanup_and_restore` |

### Security Tests (1 functions)

| # | File | Test Function |
|---|------|---------------|
| 1 | `tests\security\test_malformed_input_handling.py` | `test_robustness_to_malformed_inputs` |

### UI Tests (9 functions)

| # | File | Test Function |
|---|------|---------------|
| 1 | `tests\ui\generated\test_button_interactions.py` | `test_button_interactions` |
| 2 | `tests\ui\generated\test_form_validation.py` | `test_form_validation` |
| 3 | `scripts\ui\test_login_page_comprehensive.py` | `test_ssl_certificate_handling` |
| 4 | `scripts\ui\test_login_page_comprehensive.py` | `test_page_load_and_structure` |
| 5 | `scripts\ui\test_login_page_comprehensive.py` | `test_form_validation` |
| 6 | `scripts\ui\test_login_page_comprehensive.py` | `test_successful_login` |
| 7 | `scripts\ui\test_login_page_comprehensive.py` | `test_accessibility` |
| 8 | `scripts\ui\test_login_page_comprehensive.py` | `test_responsive_design` |
| 9 | `scripts\ui\test_login_page_comprehensive.py` | `test_performance_metrics` |

## 3. Test Functions With Multiple Markers

| # | File | Test Function | Test IDs |
|---|------|---------------|----------|
| 1 | `tests\integration\api\test_live_monitoring_flow.py` | `test_live_monitoring_sensor_data_availability` | PZ-13786, PZ-13985 |

## 4. Test IDs in Automation but NOT in Jira

**Total:** 7

- PZ-13238
- PZ-13640
- PZ-13669
- PZ-13768
- PZ-13983
- PZ-13985
- PZ-13986

