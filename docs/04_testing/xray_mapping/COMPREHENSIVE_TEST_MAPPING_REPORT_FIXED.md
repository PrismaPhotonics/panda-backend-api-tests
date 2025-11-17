# Comprehensive Test Mapping Report - FIXED VERSION

**Generated:** Automated check of automation code vs Jira tests
**Note:** This version checks each test function individually

---

## Executive Summary

| Metric | Count |
|--------|-------|
| Total tests in Jira | 237 |
| Total test IDs in automation | 146 |
| Total test functions | 461 |
| Test functions with markers | 301 |
| Test functions WITHOUT markers | 300 |
| Test functions with multiple markers | 1 |
| Tests in Jira but NOT in automation | 91 |
| Tests in automation but NOT in Jira | 0 |

## 1. Tests Without Xray Markers

**Total: 300 test functions without markers**

| # | File | Test Function |
|---|------|---------------|
| 1 | `tests\data_quality\test_mongodb_data_quality.py` | `test_deleted_recordings_marked_properly` |
| 2 | `tests\data_quality\test_mongodb_data_quality.py` | `test_historical_vs_live_recordings` |
| 3 | `tests\data_quality\test_mongodb_data_quality.py` | `test_mongodb_indexes_exist_and_optimal` |
| 4 | `tests\data_quality\test_mongodb_data_quality.py` | `test_recording_schema_validation` |
| 5 | `tests\data_quality\test_mongodb_data_quality.py` | `test_required_collections_exist` |
| 6 | `tests\data_quality\test_mongodb_indexes_and_schema.py` | `test_critical_mongodb_indexes_exist` |
| 7 | `tests\data_quality\test_mongodb_indexes_and_schema.py` | `test_mongodb_indexes_schema_summary` |
| 8 | `tests\data_quality\test_mongodb_indexes_and_schema.py` | `test_recordings_document_schema_validation` |
| 9 | `tests\data_quality\test_mongodb_indexes_and_schema.py` | `test_recordings_metadata_completeness` |
| 10 | `tests\data_quality\test_mongodb_recovery.py` | `test_mongodb_recovery_recordings_indexed_after_outage` |
| 11 | `tests\data_quality\test_mongodb_recovery.py` | `test_mongodb_recovery_summary` |
| 12 | `tests\data_quality\test_mongodb_schema_validation.py` | `test_metadata_collection_schema_validation` |
| 13 | `tests\data_quality\test_mongodb_schema_validation.py` | `test_mongodb_schema_validation_summary` |
| 14 | `tests\data_quality\test_recordings_classification.py` | `test_historical_vs_live_recordings_classification` |
| 15 | `tests\data_quality\test_recordings_classification.py` | `test_recordings_classification_summary` |
| 16 | `tests\infrastructure\resilience\test_focus_server_pod_resilience.py` | `test_focus_server_pod_resilience_summary` |
| 17 | `tests\infrastructure\resilience\test_focus_server_pod_resilience.py` | `test_focus_server_pod_status_monitoring` |
| 18 | `tests\infrastructure\resilience\test_mongodb_pod_resilience.py` | `test_mongodb_pod_resilience_summary` |
| 19 | `tests\infrastructure\resilience\test_mongodb_pod_resilience.py` | `test_mongodb_pod_status_monitoring` |
| 20 | `tests\infrastructure\resilience\test_multiple_pods_resilience.py` | `test_focus_server_segy_recorder_down_simultaneously` |
| 21 | `tests\infrastructure\resilience\test_multiple_pods_resilience.py` | `test_multiple_pods_resilience_summary` |
| 22 | `tests\infrastructure\resilience\test_pod_recovery_scenarios.py` | `test_pod_recovery_scenarios_summary` |
| 23 | `tests\infrastructure\resilience\test_pod_recovery_scenarios.py` | `test_recovery_time_measurement` |
| 24 | `tests\infrastructure\resilience\test_rabbitmq_pod_resilience.py` | `test_rabbitmq_pod_resilience_summary` |
| 25 | `tests\infrastructure\resilience\test_rabbitmq_pod_resilience.py` | `test_rabbitmq_pod_status_monitoring` |
| 26 | `tests\infrastructure\resilience\test_segy_recorder_pod_resilience.py` | `test_segy_recorder_pod_resilience_summary` |
| 27 | `tests\infrastructure\resilience\test_segy_recorder_pod_resilience.py` | `test_segy_recorder_recovery_after_outage` |
| 28 | `tests\infrastructure\test_basic_connectivity.py` | `test_connectivity_summary` |
| 29 | `tests\infrastructure\test_basic_connectivity.py` | `test_kubernetes_direct_connection` |
| 30 | `tests\infrastructure\test_basic_connectivity.py` | `test_mongodb_direct_connection` |
| 31 | `tests\infrastructure\test_basic_connectivity.py` | `test_ssh_direct_connection` |
| 32 | `tests\infrastructure\test_external_connectivity.py` | `test_all_services_summary` |
| 33 | `tests\infrastructure\test_external_connectivity.py` | `test_kubernetes_connection` |
| 34 | `tests\infrastructure\test_external_connectivity.py` | `test_kubernetes_list_deployments` |
| 35 | `tests\infrastructure\test_external_connectivity.py` | `test_mongodb_connection` |
| 36 | `tests\infrastructure\test_external_connectivity.py` | `test_quick_kubernetes_ping` |
| 37 | `tests\infrastructure\test_external_connectivity.py` | `test_quick_mongodb_ping` |
| 38 | `tests\infrastructure\test_external_connectivity.py` | `test_quick_ssh_ping` |
| 39 | `tests\infrastructure\test_external_connectivity.py` | `test_ssh_connection` |
| 40 | `tests\infrastructure\test_external_connectivity.py` | `test_ssh_network_operations` |
| 41 | `tests\infrastructure\test_k8s_job_lifecycle.py` | `test_job_config` |
| 42 | `tests\infrastructure\test_k8s_job_lifecycle.py` | `test_k8s_job_cancellation_and_cleanup` |
| 43 | `tests\infrastructure\test_k8s_job_lifecycle.py` | `test_k8s_job_creation_triggers_pod_spawn` |
| 44 | `tests\infrastructure\test_k8s_job_lifecycle.py` | `test_k8s_job_observability` |
| 45 | `tests\infrastructure\test_k8s_job_lifecycle.py` | `test_k8s_job_port_exposure` |
| 46 | `tests\infrastructure\test_k8s_job_lifecycle.py` | `test_k8s_job_resource_allocation` |
| 47 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_alert_creation` |
| 48 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_alert_level_values` |
| 49 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_collect_metrics` |
| 50 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_connect_authentication_failure` |
| 51 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_connect_failure_max_retries` |
| 52 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_connect_failure_retry` |
| 53 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_connect_success` |
| 54 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_context_manager` |
| 55 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_count_documents` |
| 56 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_create_alert` |
| 57 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_disconnect` |
| 58 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_ensure_connected_auto_reconnect` |
| 59 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_ensure_connected_success` |
| 60 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_find_documents` |
| 61 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_get_collection_stats` |
| 62 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_get_health_status_healthy` |
| 63 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_get_health_status_unhealthy` |
| 64 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_get_metrics_summary` |
| 65 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_get_recent_alerts` |
| 66 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_init` |
| 67 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_list_collections` |
| 68 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_list_databases` |
| 69 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_list_databases_not_connected` |
| 70 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_monitoring_metrics_defaults` |
| 71 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_register_alert_callback` |
| 72 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_start_monitoring` |
| 73 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_stop_monitoring` |
| 74 | `tests\infrastructure\test_pz_integration.py` | `test_pz_focus_server_access` |
| 75 | `tests\infrastructure\test_pz_integration.py` | `test_pz_import_capability` |
| 76 | `tests\infrastructure\test_pz_integration.py` | `test_pz_integration_summary` |
| 77 | `tests\infrastructure\test_pz_integration.py` | `test_pz_microservices_listing` |
| 78 | `tests\infrastructure\test_pz_integration.py` | `test_pz_repository_available` |
| 79 | `tests\infrastructure\test_pz_integration.py` | `test_pz_version_info` |
| 80 | `tests\infrastructure\test_rabbitmq_connectivity.py` | `test_rabbitmq_connection` |
| 81 | `tests\infrastructure\test_rabbitmq_connectivity.py` | `test_rabbitmq_connectivity_summary` |
| 82 | `tests\infrastructure\test_rabbitmq_outage_handling.py` | `test_rabbitmq_outage_handling` |
| 83 | `tests\infrastructure\test_rabbitmq_outage_handling.py` | `test_rabbitmq_outage_handling_summary` |
| 84 | `tests\infrastructure\test_system_behavior.py` | `test_focus_server_clean_startup` |
| 85 | `tests\infrastructure\test_system_behavior.py` | `test_focus_server_stability_over_time` |
| 86 | `tests\infrastructure\test_system_behavior.py` | `test_predictable_error_no_data_available` |
| 87 | `tests\infrastructure\test_system_behavior.py` | `test_predictable_error_port_in_use` |
| 88 | `tests\infrastructure\test_system_behavior.py` | `test_proper_rollback_on_job_creation_failure` |
| 89 | `tests\integration\api\test_api_endpoints_additional.py` | `test_api_endpoints_additional_summary` |
| 90 | `tests\integration\api\test_api_endpoints_additional.py` | `test_get_live_metadata_available` |
| 91 | `tests\integration\api\test_api_endpoints_additional.py` | `test_get_metadata_by_job_id` |
| 92 | `tests\integration\api\test_api_endpoints_additional.py` | `test_get_sensors_endpoint` |
| 93 | `tests\integration\api\test_api_endpoints_additional.py` | `test_invalid_channel_range_rejection` |
| 94 | `tests\integration\api\test_api_endpoints_additional.py` | `test_invalid_frequency_range_rejection` |
| 95 | `tests\integration\api\test_api_endpoints_additional.py` | `test_invalid_time_range_rejection` |
| 96 | `tests\integration\api\test_api_endpoints_additional.py` | `test_post_recordings_in_time_range` |
| 97 | `tests\integration\api\test_api_endpoints_high_priority.py` | `test_api_endpoints_high_priority_summary` |
| 98 | `tests\integration\api\test_api_endpoints_high_priority.py` | `test_get_channels_endpoint_enabled_status` |
| 99 | `tests\integration\api\test_config_task_endpoint.py` | `test_config_task_endpoint_summary` |
| 100 | `tests\integration\api\test_config_task_endpoint.py` | `test_config_task_invalid_frequency_range` |
| 101 | `tests\integration\api\test_config_validation_high_priority.py` | `test_channel_range_at_maximum` |
| 102 | `tests\integration\api\test_config_validation_high_priority.py` | `test_channel_range_equal_min_max` |
| 103 | `tests\integration\api\test_config_validation_high_priority.py` | `test_channel_range_exceeds_maximum` |
| 104 | `tests\integration\api\test_config_validation_high_priority.py` | `test_config_validation_high_priority_summary` |
| 105 | `tests\integration\api\test_config_validation_high_priority.py` | `test_frequency_range_equal_min_max` |
| 106 | `tests\integration\api\test_config_validation_high_priority.py` | `test_frequency_range_exceeds_nyquist_limit` |
| 107 | `tests\integration\api\test_config_validation_high_priority.py` | `test_historic_mode_valid_configuration` |
| 108 | `tests\integration\api\test_config_validation_high_priority.py` | `test_historic_mode_with_equal_times` |
| 109 | `tests\integration\api\test_config_validation_high_priority.py` | `test_historic_mode_with_negative_time` |
| 110 | `tests\integration\api\test_config_validation_high_priority.py` | `test_invalid_canvas_height_negative` |
| 111 | `tests\integration\api\test_config_validation_high_priority.py` | `test_invalid_canvas_height_zero` |
| 112 | `tests\integration\api\test_config_validation_high_priority.py` | `test_invalid_channel_range_min_greater_than_max` |
| 113 | `tests\integration\api\test_config_validation_high_priority.py` | `test_invalid_frequency_range_min_greater_than_max` |
| 114 | `tests\integration\api\test_config_validation_high_priority.py` | `test_invalid_nfft_exceeds_maximum` |
| 115 | `tests\integration\api\test_config_validation_high_priority.py` | `test_invalid_nfft_not_power_of_2` |
| 116 | `tests\integration\api\test_config_validation_high_priority.py` | `test_live_mode_with_only_end_time` |
| 117 | `tests\integration\api\test_config_validation_high_priority.py` | `test_missing_canvas_height_key` |
| 118 | `tests\integration\api\test_config_validation_high_priority.py` | `test_missing_display_time_axis_duration` |
| 119 | `tests\integration\api\test_config_validation_high_priority.py` | `test_requirement_frequency_must_not_exceed_nyquist` |
| 120 | `tests\integration\api\test_config_validation_high_priority.py` | `test_requirement_negative_height_must_be_rejected` |
| 121 | `tests\integration\api\test_config_validation_high_priority.py` | `test_requirement_nfft_max_2048` |
| 122 | `tests\integration\api\test_config_validation_high_priority.py` | `test_requirement_nfft_must_be_power_of_2` |
| 123 | `tests\integration\api\test_config_validation_high_priority.py` | `test_requirement_reject_only_end_time` |
| 124 | `tests\integration\api\test_config_validation_high_priority.py` | `test_requirement_reject_only_start_time` |
| 125 | `tests\integration\api\test_config_validation_high_priority.py` | `test_requirement_zero_height_must_be_rejected` |
| 126 | `tests\integration\api\test_config_validation_high_priority.py` | `test_valid_configuration_all_parameters` |
| 127 | `tests\integration\api\test_config_validation_high_priority.py` | `test_valid_configuration_multiple_sensors` |
| 128 | `tests\integration\api\test_config_validation_high_priority.py` | `test_valid_configuration_single_sensor` |
| 129 | `tests\integration\api\test_config_validation_high_priority.py` | `test_valid_configuration_various_nfft_values` |
| 130 | `tests\integration\api\test_config_validation_nfft_frequency.py` | `test_frequency_range_variations` |
| 131 | `tests\integration\api\test_config_validation_nfft_frequency.py` | `test_negative_nfft` |
| 132 | `tests\integration\api\test_config_validation_nfft_frequency.py` | `test_valid_nfft_power_of_2` |
| 133 | `tests\integration\api\test_configure_endpoint.py` | `test_configure_endpoint_summary` |
| 134 | `tests\integration\api\test_configure_endpoint.py` | `test_configure_response_time_performance` |
| 135 | `tests\integration\api\test_dynamic_roi_adjustment.py` | `test_roi_shrinking` |
| 136 | `tests\integration\api\test_dynamic_roi_adjustment.py` | `test_roi_with_equal_start_end` |
| 137 | `tests\integration\api\test_dynamic_roi_adjustment.py` | `test_send_roi_change_command` |
| 138 | `tests\integration\api\test_health_check.py` | `test_ack_load_testing` |
| 139 | `tests\integration\api\test_health_check.py` | `test_health_check_summary` |
| 140 | `tests\integration\api\test_historic_playback_additional.py` | `test_historic_playback_additional_summary` |
| 141 | `tests\integration\api\test_historic_playback_additional.py` | `test_historic_playback_future_timestamps_rejection` |
| 142 | `tests\integration\api\test_historic_playback_e2e.py` | `test_historic_playback_complete_e2e_flow` |
| 143 | `tests\integration\api\test_historic_playback_e2e.py` | `test_historic_playback_e2e_summary` |
| 144 | `tests\integration\api\test_live_monitoring_flow.py` | `test_live_monitoring_get_metadata` |
| 145 | `tests\integration\api\test_live_monitoring_flow.py` | `test_live_monitoring_summary` |
| 146 | `tests\integration\api\test_live_streaming_stability.py` | `test_live_streaming_stability` |
| 147 | `tests\integration\api\test_live_streaming_stability.py` | `test_live_streaming_stability_summary` |
| 148 | `tests\integration\api\test_nfft_overlap_edge_case.py` | `test_nfft_overlap_edge_case_summary` |
| 149 | `tests\integration\api\test_nfft_overlap_edge_case.py` | `test_overlap_nfft_escalation_edge_case` |
| 150 | `tests\integration\api\test_orchestration_validation.py` | `test_history_with_empty_window_returns_400_no_side_effects` |
| 151 | `tests\integration\api\test_orchestration_validation.py` | `test_orchestration_validation_summary` |
| 152 | `tests\integration\api\test_prelaunch_validations.py` | `test_config_validation_channels_out_of_range` |
| 153 | `tests\integration\api\test_prelaunch_validations.py` | `test_config_validation_frequency_exceeds_nyquist` |
| 154 | `tests\integration\api\test_prelaunch_validations.py` | `test_config_validation_invalid_view_type` |
| 155 | `tests\integration\api\test_prelaunch_validations.py` | `test_data_availability_live_mode` |
| 156 | `tests\integration\api\test_prelaunch_validations.py` | `test_prelaunch_validation_error_messages_clarity` |
| 157 | `tests\integration\api\test_singlechannel_view_mapping.py` | `test_configure_singlechannel_channel_1` |
| 158 | `tests\integration\api\test_singlechannel_view_mapping.py` | `test_configure_singlechannel_mapping` |
| 159 | `tests\integration\api\test_singlechannel_view_mapping.py` | `test_module_summary` |
| 160 | `tests\integration\api\test_singlechannel_view_mapping.py` | `test_singlechannel_complete_e2e_flow` |
| 161 | `tests\integration\api\test_singlechannel_view_mapping.py` | `test_singlechannel_middle_channel` |
| 162 | `tests\integration\api\test_singlechannel_view_mapping.py` | `test_singlechannel_rejects_invalid_nfft_value` |
| 163 | `tests\integration\api\test_singlechannel_view_mapping.py` | `test_singlechannel_with_zero_channel` |
| 164 | `tests\integration\api\test_task_metadata_endpoint.py` | `test_task_metadata_endpoint_summary` |
| 165 | `tests\integration\api\test_task_metadata_endpoint.py` | `test_task_metadata_response_time` |
| 166 | `tests\integration\api\test_view_type_validation.py` | `test_valid_view_types` |
| 167 | `tests\integration\api\test_view_type_validation.py` | `test_view_type_validation_summary` |
| 168 | `tests\integration\api\test_waterfall_endpoint.py` | `test_waterfall_baby_analyzer_exited` |
| 169 | `tests\integration\api\test_waterfall_endpoint.py` | `test_waterfall_endpoint_summary` |
| 170 | `tests\integration\api\test_waterfall_view.py` | `test_waterfall_view_handling` |
| 171 | `tests\integration\api\test_waterfall_view.py` | `test_waterfall_view_summary` |
| 172 | `tests\integration\calculations\test_system_calculations.py` | `test_spectrogram_dimensions_calculation` |
| 173 | `tests\integration\data_quality\test_data_completeness.py` | `test_data_completeness` |
| 174 | `tests\integration\data_quality\test_data_consistency.py` | `test_metadata_consistency` |
| 175 | `tests\integration\data_quality\test_data_integrity.py` | `test_data_integrity_across_requests` |
| 176 | `tests\integration\e2e\test_configure_metadata_grpc_flow.py` | `test_e2e_configure_metadata_grpc_flow` |
| 177 | `tests\integration\e2e\test_configure_metadata_grpc_flow.py` | `test_e2e_flow_summary` |
| 178 | `tests\integration\error_handling\test_http_error_codes.py` | `test_504_gateway_timeout` |
| 179 | `tests\integration\error_handling\test_invalid_payloads.py` | `test_error_message_format` |
| 180 | `tests\integration\error_handling\test_network_errors.py` | `test_connection_refused` |
| 181 | `tests\integration\load\test_concurrent_load.py` | `test_concurrent_job_creation_load` |
| 182 | `tests\integration\load\test_load_profiles.py` | `test_steady_state_load_profile` |
| 183 | `tests\integration\load\test_peak_load.py` | `test_peak_load_high_rps` |
| 184 | `tests\integration\load\test_recovery_and_exhaustion.py` | `test_resource_exhaustion_under_load` |
| 185 | `tests\integration\load\test_sustained_load.py` | `test_sustained_load_1_hour` |
| 186 | `tests\integration\performance\test_concurrent_performance.py` | `test_concurrent_requests_performance` |
| 187 | `tests\integration\performance\test_database_performance.py` | `test_database_query_performance` |
| 188 | `tests\integration\performance\test_latency_requirements.py` | `test_job_creation_time` |
| 189 | `tests\integration\performance\test_latency_requirements.py` | `test_latency_requirements_summary` |
| 190 | `tests\integration\performance\test_network_latency.py` | `test_end_to_end_latency` |
| 191 | `tests\integration\performance\test_performance_high_priority.py` | `test_concurrent_task_creation` |
| 192 | `tests\integration\performance\test_performance_high_priority.py` | `test_concurrent_task_max_limit` |
| 193 | `tests\integration\performance\test_performance_high_priority.py` | `test_concurrent_task_polling` |
| 194 | `tests\integration\performance\test_performance_high_priority.py` | `test_config_endpoint_latency_p95_p99` |
| 195 | `tests\integration\performance\test_performance_high_priority.py` | `test_performance_high_priority_summary` |
| 196 | `tests\integration\performance\test_resource_usage.py` | `test_cpu_usage_under_load` |
| 197 | `tests\integration\performance\test_response_time.py` | `test_metadata_response_time` |
| 198 | `tests\integration\security\test_api_authentication.py` | `test_expired_authentication_token` |
| 199 | `tests\integration\security\test_csrf_protection.py` | `test_csrf_protection` |
| 200 | `tests\integration\security\test_data_exposure.py` | `test_data_exposure_prevention` |
| ... | ... and 100 more | ... |

## 2. Tests With Multiple Test IDs

**Total: 1 test functions with multiple markers**

These tests check multiple things in one automated test:

| # | File | Test Function | Test IDs |
|---|------|---------------|----------|
| 1 | `tests\integration\api\test_live_monitoring_flow.py` | `test_live_monitoring_sensor_data_availability` | PZ-13786, PZ-13985 |

## 3. Tests in Jira but NOT in Automation

**Total: 91 tests need to be automated**

| # | Test ID | Summary | Status | Test Type |
|---|---------|---------|--------|-----------|
| 1 | PZ-13548 | API – Historical configure (happy path) | TO DO | Automation |
| 2 | PZ-13552 | API – Invalid time range (negative) | TO DO | Automation |
| 3 | PZ-13554 | API – Invalid channels (negative) | TO DO | Automation |
| 4 | PZ-13555 | API – Invalid frequency range (negative) | TO DO | Automation |
| 5 | PZ-13557 | API – Waterfall view handling | TO DO | Automation |
| 6 | PZ-13558 | API - Overlap/NFFT Escalation Edge Case | TO DO | Automation |
| 7 | PZ-13560 | API – GET /channels | TO DO | Automation |
| 8 | PZ-13561 | API – GET /live_metadata present | TO DO | Automation |
| 9 | PZ-13562 | API – GET /live_metadata missing | TO DO | Automation |
| 10 | PZ-13564 | API – POST /recordings_in_time_range | TO DO | Automation |
| 11 | PZ-13570 | E2E – Configure → Metadata → gRPC (mock) | TO DO | Automation |
| 12 | PZ-13572 | Security – Robustness to malformed inputs | TO DO | Automation |
| 13 | PZ-13598 | Data Quality – Mongo collections and schema | TO DO | Automation |
| 14 | PZ-13602 | Integration – RabbitMQ outage on Live configure | TO DO | Automation |
| 15 | PZ-13603 | Integration – Mongo outage on History configure | TO DO | Automation |
| 16 | PZ-13604 | Integration – Orchestrator error triggers rollback | TO DO | Automation |
| 17 | PZ-13684 | Data Quality – node4 Schema Validation | TO DO | Automation |
| 18 | PZ-13685 | Data Quality – Recordings Metadata Completeness | TO DO | Automation |
| 19 | PZ-13687 | MongoDB Recovery – Recordings Indexed After Outage | TO DO | Automation |
| 20 | PZ-13705 | Data Lifecycle – Historical vs Live Recordings Classificatio | TO DO | Automation |
| 21 | PZ-13759 | API – POST /config/{task_id} – Invalid Time Range Rejection | TO DO | Automation |
| 22 | PZ-13760 | API – POST /config/{task_id} – Invalid Channel Range Rejecti | TO DO | Automation |
| 23 | PZ-13761 | API – POST /config/{task_id} – Invalid Frequency Range Rejec | TO DO | Automation |
| 24 | PZ-13762 | API – GET /channels – Returns System Channel Bounds | TO DO | Automation |
| 25 | PZ-13764 |  API – GET /live_metadata – Returns Metadata When Available | TO DO | Automation |
| 26 | PZ-13765 | API – GET /live_metadata – Returns 404 When Unavailable | TO DO | Automation |
| 27 | PZ-13766 |  API – POST /recordings_in_time_range – Returns Recording Wi | TO DO | Automation |
| 28 | PZ-13767 | Integration – MongoDB Outage Handling | TO DO | Automation |
| 29 | PZ-13769 | Security – Malformed Input Handling | TO DO | Automation |
| 30 | PZ-13784 | Integration - Send ROI Change Command via RabbitMQ | TO DO | Automation |
| 31 | PZ-13787 | Integration -  ROI Expansion (Increase Range) | TO DO | Automation |
| 32 | PZ-13792 | Integration - ROI with Negative Start | TO DO | Automation |
| 33 | PZ-13800 | Integration – Safe ROI Change (Within Limits) | TO DO | Automation |
| 34 | PZ-13806 | Infrastructure - Infrastructure – MongoDB Direct TCP Connect | TO DO | Automation |
| 35 | PZ-13811 | Data Quality – Validate Recordings Document Schema | TO DO | Automation |
| 36 | PZ-13812 | Data Quality – Verify Recordings Have Complete Metadata | TO DO | Automation |
| 37 | PZ-13814 | API – SingleChannel View for Channel 1 (First Channel) | TO DO | Automation |
| 38 | PZ-13815 | API – SingleChannel View for Channel 100 (Upper Boundary Tes | TO DO | Automation |
| 39 | PZ-13819 | API – SingleChannel View with Various Frequency Ranges | TO DO | Automation |
| 40 | PZ-13821 | API – SingleChannel Rejects Invalid Display Height | TO DO | Automation |
| 41 | PZ-13823 | API – SingleChannel Rejects When min ≠ max | TO DO | Automation |
| 42 | PZ-13832 | Integration - SingleChannel Edge Case - Minimum Channel (Cha | TO DO | Automation |
| 43 | PZ-13833 | Integration - SingleChannel Edge Case - Maximum Channel (Las | TO DO | Automation |
| 44 | PZ-13835 | Integration - SingleChannel with Invalid Channel (Out of Ran | TO DO | Automation |
| 45 | PZ-13836 | Integration - SingleChannel with Invalid Channel (Negative) | TO DO | Automation |
| 46 | PZ-13837 | Integration - SingleChannel with Invalid Channel (Negative) | TO DO | Automation |
| 47 | PZ-13852 | Integration - SingleChannel with Min > Max (Validation Error | TO DO | Automation |
| 48 | PZ-13854 | Integration - SingleChannel Frequency Range Validation | TO DO | Automation |
| 49 | PZ-13855 | Integration - SingleChannel Canvas Height Validation | TO DO | Automation |
| 50 | PZ-13861 | Integration - SingleChannel Stream Mapping Verification | TO DO | Automation |
| 51 | PZ-13863 | Integration – Historic Playback - Standard 5-Minute Range | TO DO | Automation |
| 52 | PZ-13865 | Integration – Historic Playback - Short Duration (1 Minute) | TO DO | Automation |
| 53 | PZ-13872 | Integration – Historic Playback Complete End-to-End Flow | TO DO | Automation |
| 54 | PZ-13873 | integration - Valid Configuration - All Parameters | TO DO | Automation |
| 55 | PZ-13877 | Integration – Invalid Frequency Range - Min > Max | TO DO | Automation |
| 56 | PZ-13879 | Integration – Missing Required Fields | TO DO | Automation |
| 57 | PZ-13880 | Stress - Configuration with Extreme Values  | TO DO | Automation |
| 58 | PZ-13895 | Integration – GET /channels - Enabled Channels List | TO DO | Automation |
| 59 | PZ-13903 | Integration - Frequency Range Nyquist Limit Enforcement | TO DO | Automation |
| 60 | PZ-14018 | Invalid Configuration Does Not Launch Orchestration | TO DO | Automation |
| 61 | PZ-14026 | API - Health Check Returns Valid Response (200 OK) | TO DO | Automation |
| 62 | PZ-14060 | Integration – Calculation Validation – Frequency Resolution  | TO DO | Automation |
| 63 | PZ-14092 | Performance - Configuration Endpoint P95 Latency | TO DO | Automation |
| 64 | PZ-14094 | Integration - Invalid View Type - String Value | TO DO | Automation |
| 65 | PZ-14099 | Integration - Configuration Missing channels Field | TO DO | Automation |
| 66 | PZ-14101 | Integration - Historic Playback - Short Duration (Rapid Wind | TO DO | Automation |
| 67 | PZ-14733 | Infrastructure - SEGY Recorder Pod Deletion and Recreation | TO DO | Automation |
| 68 | PZ-14750 | API - POST /config/{task_id} - Valid Configuration | TO DO | Automation |
| 69 | PZ-14760 | API - GET /metadata/{task_id} - Valid Request | TO DO | Automation |
| 70 | PZ-14771 | Infrastructure - Security - API Authentication Required | TO DO | Automation |
| 71 | PZ-14774 | Infrastructure - Security - SQL Injection Prevention | TO DO | Automation |
| 72 | PZ-14776 | Infrastructure - Security - CSRF Protection | TO DO | Automation |
| 73 | PZ-14777 | Infrastructure - Security - Rate Limiting | TO DO | Automation |
| 74 | PZ-14778 | Infrastructure - Security - HTTPS Only | TO DO | Automation |
| 75 | PZ-14779 | Infrastructure - Security - Sensitive Data Exposure | TO DO | Automation |
| 76 | PZ-14780 | Infrastructure - Error Handling - 500 Internal Server Error | TO DO | Automation |
| 77 | PZ-14783 | Infrastructure - Error Handling - Network Timeout | TO DO | Automation |
| 78 | PZ-14785 | Infrastructure - Error Handling - Invalid JSON Payload | TO DO | Automation |
| 79 | PZ-14790 | Infrastructure - Performance - POST /configure Response Time | TO DO | Automation |
| 80 | PZ-14793 | Infrastructure - Performance - Concurrent Requests Performan | TO DO | Automation |
| 81 | PZ-14794 | Infrastructure - Performance - Large Payload Handling | TO DO | Automation |
| 82 | PZ-14797 | Infrastructure - Performance - Database Query Performance | TO DO | Automation |
| 83 | PZ-14798 | Infrastructure - Performance - Network Latency Impact | TO DO | Automation |
| 84 | PZ-14800 | Infrastructure - Load - Concurrent Job Creation Load | TO DO | Automation |
| 85 | PZ-14801 | Infrastructure - Load - Sustained Load - 1 Hour | TO DO | Automation |
| 86 | PZ-14802 | Infrastructure - Load - Peak Load - High RPS | TO DO | Automation |
| 87 | PZ-14803 | Infrastructure - Load - Ramp-Up Load Profile | TO DO | Automation |
| 88 | PZ-14806 | Infrastructure - Load - Recovery After Load | TO DO | Automation |
| 89 | PZ-14808 | Infrastructure - Data Quality - Waterfall Data Consistency | TO DO | Automation |
| 90 | PZ-14810 | Infrastructure - Data Quality - Data Integrity Across Reques | TO DO | Automation |
| 91 | PZ-14811 | Infrastructure - Data Quality - Timestamp Accuracy | TO DO | Automation |

## 5. Test Quality Check - Jira Tests

Checking if tests in Jira are written clearly and accurately:

**Total: 1 tests with quality issues**

| # | Test ID | Summary | Issues |
|---|---------|---------|--------|
| 1 | PZ-14093 | Integration - Invalid View Type - Out of Range | Description missing or too short |

