# Test Functions Without Markers - Detailed Breakdown

**Note:** Excludes unit tests and helper functions

---

## Data Quality Tests (11 functions)

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

## Infrastructure Tests (56 functions)

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

## Integration Tests (101 functions)

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

## Load Tests (4 functions)

| # | File | Test Function |
|---|------|---------------|
| 1 | `tests\load\test_job_capacity_limits.py` | `test_single_job_baseline` |
| 2 | `tests\load\test_job_capacity_limits.py` | `test_linear_load_progression` |
| 3 | `tests\load\test_job_capacity_limits.py` | `test_recovery_after_stress` |
| 4 | `tests\load\test_job_capacity_limits.py` | `test_200_concurrent_jobs_target_capacity` |

## Other Tests (3 functions)

| # | File | Test Function |
|---|------|---------------|
| 1 | `tests\stress\test_extreme_configurations.py` | `test_configuration_with_extreme_values` |
| 2 | `tests\ui\generated\test_button_interactions.py` | `test_button_interactions` |
| 3 | `tests\ui\generated\test_form_validation.py` | `test_form_validation` |

## Performance Tests (5 functions)

| # | File | Test Function |
|---|------|---------------|
| 1 | `tests\performance\test_mongodb_outage_resilience.py` | `test_mongodb_scale_down_outage_returns_503_no_orchestration` |
| 2 | `tests\performance\test_mongodb_outage_resilience.py` | `test_mongodb_network_block_outage_returns_503_no_orchestration` |
| 3 | `tests\performance\test_mongodb_outage_resilience.py` | `test_mongodb_outage_no_live_impact` |
| 4 | `tests\performance\test_mongodb_outage_resilience.py` | `test_mongodb_outage_logging_and_metrics` |
| 5 | `tests\performance\test_mongodb_outage_resilience.py` | `test_mongodb_outage_cleanup_and_restore` |

## Security Tests (1 functions)

| # | File | Test Function |
|---|------|---------------|
| 1 | `tests\security\test_malformed_input_handling.py` | `test_robustness_to_malformed_inputs` |

**Total:** 181 test functions need markers

