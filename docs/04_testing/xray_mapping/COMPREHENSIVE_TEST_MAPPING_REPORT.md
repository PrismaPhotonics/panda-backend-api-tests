# Comprehensive Test Mapping Report

**Generated:** Automated check of automation code vs Jira tests

---

## 📊 Executive Summary

| Metric | Count |
|--------|-------|
| Total tests in Jira | 237 |
| Total test IDs in automation | 194 |
| Tests with markers | 194 |
| Tests without markers | 138 |
| Tests with multiple markers | 1 |
| Tests in Jira but NOT in automation | 44 |
| Tests in automation but NOT in Jira | 1 |

## 1. ⚠️ Tests Without Xray Markers

**Total: 138 test functions without markers**

| # | File | Test Function |
|---|------|---------------|
| 1 | `tests\infrastructure\test_basic_connectivity.py` | `test_mongodb_direct_connection` |
| 2 | `tests\infrastructure\test_basic_connectivity.py` | `test_kubernetes_direct_connection` |
| 3 | `tests\infrastructure\test_basic_connectivity.py` | `test_ssh_direct_connection` |
| 4 | `tests\infrastructure\test_basic_connectivity.py` | `test_connectivity_summary` |
| 5 | `tests\infrastructure\test_k8s_job_lifecycle.py` | `test_job_config` |
| 6 | `tests\infrastructure\test_k8s_job_lifecycle.py` | `test_k8s_job_creation_triggers_pod_spawn` |
| 7 | `tests\infrastructure\test_k8s_job_lifecycle.py` | `test_k8s_job_resource_allocation` |
| 8 | `tests\infrastructure\test_k8s_job_lifecycle.py` | `test_k8s_job_port_exposure` |
| 9 | `tests\infrastructure\test_k8s_job_lifecycle.py` | `test_k8s_job_cancellation_and_cleanup` |
| 10 | `tests\infrastructure\test_k8s_job_lifecycle.py` | `test_k8s_job_observability` |
| 11 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_init` |
| 12 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_connect_success` |
| 13 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_connect_failure_retry` |
| 14 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_connect_failure_max_retries` |
| 15 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_connect_authentication_failure` |
| 16 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_disconnect` |
| 17 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_ensure_connected_success` |
| 18 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_ensure_connected_auto_reconnect` |
| 19 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_list_databases` |
| 20 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_list_databases_not_connected` |
| 21 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_list_collections` |
| 22 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_get_collection_stats` |
| 23 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_count_documents` |
| 24 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_find_documents` |
| 25 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_get_health_status_healthy` |
| 26 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_get_health_status_unhealthy` |
| 27 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_collect_metrics` |
| 28 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_get_metrics_summary` |
| 29 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_create_alert` |
| 30 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_register_alert_callback` |
| 31 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_get_recent_alerts` |
| 32 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_start_monitoring` |
| 33 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_stop_monitoring` |
| 34 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_context_manager` |
| 35 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_monitoring_metrics_defaults` |
| 36 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_alert_creation` |
| 37 | `tests\infrastructure\test_mongodb_monitoring_agent.py` | `test_alert_level_values` |
| 38 | `tests\infrastructure\test_pz_integration.py` | `test_pz_repository_available` |
| 39 | `tests\infrastructure\test_pz_integration.py` | `test_pz_microservices_listing` |
| 40 | `tests\infrastructure\test_pz_integration.py` | `test_pz_focus_server_access` |
| 41 | `tests\infrastructure\test_pz_integration.py` | `test_pz_version_info` |
| 42 | `tests\infrastructure\test_pz_integration.py` | `test_pz_import_capability` |
| 43 | `tests\infrastructure\test_pz_integration.py` | `test_pz_integration_summary` |
| 44 | `tests\infrastructure\test_system_behavior.py` | `test_focus_server_clean_startup` |
| 45 | `tests\infrastructure\test_system_behavior.py` | `test_focus_server_stability_over_time` |
| 46 | `tests\infrastructure\test_system_behavior.py` | `test_predictable_error_no_data_available` |
| 47 | `tests\infrastructure\test_system_behavior.py` | `test_predictable_error_port_in_use` |
| 48 | `tests\infrastructure\test_system_behavior.py` | `test_proper_rollback_on_job_creation_failure` |
| 49 | `tests\security\test_malformed_input_handling.py` | `test_robustness_to_malformed_inputs` |
| 50 | `tests\security\test_malformed_input_handling.py` | `test_malformed_input_handling_summary` |
| 51 | `tests\unit\test_basic_functionality.py` | `test_import_config_manager` |
| 52 | `tests\unit\test_basic_functionality.py` | `test_import_exceptions` |
| 53 | `tests\unit\test_basic_functionality.py` | `test_import_models` |
| 54 | `tests\unit\test_basic_functionality.py` | `test_import_infrastructure_managers` |
| 55 | `tests\unit\test_basic_functionality.py` | `test_config_loading` |
| 56 | `tests\unit\test_basic_functionality.py` | `test_model_creation` |
| 57 | `tests\unit\test_basic_functionality.py` | `test_exception_handling` |
| 58 | `tests\unit\test_basic_functionality.py` | `test_main_directories_exist` |
| 59 | `tests\unit\test_basic_functionality.py` | `test_config_files_exist` |
| 60 | `tests\unit\test_basic_functionality.py` | `test_source_structure_exists` |
| 61 | `tests\unit\test_basic_functionality.py` | `test_python_packages_exist` |
| 62 | `tests\unit\test_config_loading.py` | `test_load_staging_config` |
| 63 | `tests\unit\test_config_loading.py` | `test_load_local_config` |
| 64 | `tests\unit\test_config_loading.py` | `test_invalid_environment` |
| 65 | `tests\unit\test_config_loading.py` | `test_get_nested_config` |
| 66 | `tests\unit\test_config_loading.py` | `test_get_with_default` |
| 67 | `tests\unit\test_config_loading.py` | `test_environment_validation` |
| 68 | `tests\unit\test_config_loading.py` | `test_import_core_exceptions` |
| 69 | `tests\unit\test_config_loading.py` | `test_import_api_client` |
| 70 | `tests\unit\test_config_loading.py` | `test_import_models` |
| 71 | `tests\unit\test_config_loading.py` | `test_import_infrastructure_managers` |
| 72 | `tests\unit\test_config_loading.py` | `test_project_structure` |
| 73 | `tests\unit\test_config_loading.py` | `test_python_package_structure` |
| 74 | `tests\unit\test_models_validation.py` | `test_valid_live_config` |
| 75 | `tests\unit\test_models_validation.py` | `test_valid_historic_config` |
| 76 | `tests\unit\test_models_validation.py` | `test_invalid_sensor_range` |
| 77 | `tests\unit\test_models_validation.py` | `test_invalid_frequency_range` |
| 78 | `tests\unit\test_models_validation.py` | `test_zero_canvas_height` |
| 79 | `tests\unit\test_models_validation.py` | `test_negative_nfft` |
| 80 | `tests\unit\test_models_validation.py` | `test_valid_sensors_list` |
| 81 | `tests\unit\test_models_validation.py` | `test_empty_sensors_list` |
| 82 | `tests\unit\test_models_validation.py` | `test_valid_metadata` |
| 83 | `tests\unit\test_models_validation.py` | `test_zero_prr` |
| 84 | `tests\unit\test_models_validation.py` | `test_negative_num_samples` |
| 85 | `tests\unit\test_models_validation.py` | `test_valid_keepalive_command` |
| 86 | `tests\unit\test_models_validation.py` | `test_keepalive_command_serialization` |
| 87 | `tests\unit\test_models_validation.py` | `test_valid_recording_metadata` |
| 88 | `tests\unit\test_models_validation.py` | `test_zero_prr` |
| 89 | `tests\unit\test_models_validation.py` | `test_valid_colormap_commands` |
| 90 | `tests\unit\test_models_validation.py` | `test_colormap_serialization` |
| 91 | `tests\unit\test_models_validation.py` | `test_valid_caxis_range` |
| 92 | `tests\unit\test_models_validation.py` | `test_invalid_caxis_range` |
| 93 | `tests\unit\test_models_validation.py` | `test_valid_roi` |
| 94 | `tests\unit\test_models_validation.py` | `test_invalid_roi_reversed` |
| 95 | `tests\unit\test_models_validation.py` | `test_negative_roi_start` |
| 96 | `tests\unit\test_models_validation.py` | `test_roi_equal_start_end` |
| 97 | `tests\unit\test_models_validation.py` | `test_valid_monitor_queues` |
| 98 | `tests\unit\test_models_validation.py` | `test_empty_queues_list` |
| 99 | `tests\unit\test_models_validation.py` | `test_very_large_sensor_range` |
| 100 | `tests\unit\test_models_validation.py` | `test_very_small_canvas_height` |
| ... | ... and 38 more | ... |

## 2. 🔄 Tests With Multiple Test IDs

**Total: 1 test functions with multiple markers**

These tests check multiple things in one automated test:

| # | File | Test Function | Test IDs |
|---|------|---------------|----------|
| 1 | `tests\load\test_job_capacity_limits.py` | `test_sustained_load_1_hour` | PZ-14088, PZ-14088 |

## 3. ❌ Tests in Jira but NOT in Automation

**Total: 44 tests need to be automated**

| # | Test ID | Summary | Status | Test Type |
|---|---------|---------|--------|-----------|
| 1 | PZ-13548 | API – Historical configure (happy path) | TO DO | Automation |
| 2 | PZ-13552 | API – Invalid time range (negative) | TO DO | Automation |
| 3 | PZ-13554 | API – Invalid channels (negative) | TO DO | Automation |
| 4 | PZ-13555 | API – Invalid frequency range (negative) | TO DO | Automation |
| 5 | PZ-13560 | API – GET /channels | TO DO | Automation |
| 6 | PZ-13561 | API – GET /live_metadata present | TO DO | Automation |
| 7 | PZ-13562 | API – GET /live_metadata missing | TO DO | Automation |
| 8 | PZ-13564 | API – POST /recordings_in_time_range | TO DO | Automation |
| 9 | PZ-13572 | Security – Robustness to malformed inputs | TO DO | Automation |
| 10 | PZ-13603 | Integration – Mongo outage on History configure | TO DO | Automation |
| 11 | PZ-13604 | Integration – Orchestrator error triggers rollback | TO DO | Automation |
| 12 | PZ-13684 | Data Quality – node4 Schema Validation | TO DO | Automation |
| 13 | PZ-13685 | Data Quality – Recordings Metadata Completeness | TO DO | Automation |
| 14 | PZ-13759 | API – POST /config/{task_id} – Invalid Time Range Rejection | TO DO | Automation |
| 15 | PZ-13760 | API – POST /config/{task_id} – Invalid Channel Range Rejecti | TO DO | Automation |
| 16 | PZ-13761 | API – POST /config/{task_id} – Invalid Frequency Range Rejec | TO DO | Automation |
| 17 | PZ-13762 | API – GET /channels – Returns System Channel Bounds | TO DO | Automation |
| 18 | PZ-13764 |  API – GET /live_metadata – Returns Metadata When Available | TO DO | Automation |
| 19 | PZ-13765 | API – GET /live_metadata – Returns 404 When Unavailable | TO DO | Automation |
| 20 | PZ-13766 |  API – POST /recordings_in_time_range – Returns Recording Wi | TO DO | Automation |
| 21 | PZ-13767 | Integration – MongoDB Outage Handling | TO DO | Automation |
| 22 | PZ-13769 | Security – Malformed Input Handling | TO DO | Automation |
| 23 | PZ-13811 | Data Quality – Validate Recordings Document Schema | TO DO | Automation |
| 24 | PZ-13812 | Data Quality – Verify Recordings Have Complete Metadata | TO DO | Automation |
| 25 | PZ-13814 | API – SingleChannel View for Channel 1 (First Channel) | TO DO | Automation |
| 26 | PZ-13815 | API – SingleChannel View for Channel 100 (Upper Boundary Tes | TO DO | Automation |
| 27 | PZ-13819 | API – SingleChannel View with Various Frequency Ranges | TO DO | Automation |
| 28 | PZ-13821 | API – SingleChannel Rejects Invalid Display Height | TO DO | Automation |
| 29 | PZ-13823 | API – SingleChannel Rejects When min ≠ max | TO DO | Automation |
| 30 | PZ-13832 | Integration - SingleChannel Edge Case - Minimum Channel (Cha | TO DO | Automation |
| 31 | PZ-13833 | Integration - SingleChannel Edge Case - Maximum Channel (Las | TO DO | Automation |
| 32 | PZ-13835 | Integration - SingleChannel with Invalid Channel (Out of Ran | TO DO | Automation |
| 33 | PZ-13836 | Integration - SingleChannel with Invalid Channel (Negative) | TO DO | Automation |
| 34 | PZ-13837 | Integration - SingleChannel with Invalid Channel (Negative) | TO DO | Automation |
| 35 | PZ-13852 | Integration - SingleChannel with Min > Max (Validation Error | TO DO | Automation |
| 36 | PZ-13854 | Integration - SingleChannel Frequency Range Validation | TO DO | Automation |
| 37 | PZ-13855 | Integration - SingleChannel Canvas Height Validation | TO DO | Automation |
| 38 | PZ-13863 | Integration – Historic Playback - Standard 5-Minute Range | TO DO | Automation |
| 39 | PZ-13865 | Integration – Historic Playback - Short Duration (1 Minute) | TO DO | Automation |
| 40 | PZ-13873 | integration - Valid Configuration - All Parameters | TO DO | Automation |
| 41 | PZ-13877 | Integration – Invalid Frequency Range - Min > Max | TO DO | Automation |
| 42 | PZ-13895 | Integration – GET /channels - Enabled Channels List | TO DO | Automation |
| 43 | PZ-13903 | Integration - Frequency Range Nyquist Limit Enforcement | TO DO | Automation |
| 44 | PZ-14101 | Integration - Historic Playback - Short Duration (Rapid Wind | TO DO | Automation |

## 4. ⚠️ Tests in Automation but NOT in Jira

**Total: 1 test IDs in automation not found in Jira**

| # | Test ID | Files |
|---|---------|-------|
| 1 | PZ-13768 | `tests\infrastructure\test_rabbitmq_outage_handling.py` |

## 5. 📝 Test Quality Check - Jira Tests

Checking if tests in Jira are written clearly and accurately:

**Total: 1 tests with quality issues**

| # | Test ID | Summary | Issues |
|---|---------|---------|--------|
| 1 | PZ-14093 | Integration - Invalid View Type - Out of Range | Description missing or too short |

## 6. ✅ All Automation Markers

**Total: 194 unique test IDs in automation**

| # | Test ID | Files |
|---|---------|-------|
| 1 | PZ-13547 | `tests\integration\api\test_prelaunch_validations.py:209` |
| 2 | PZ-13557 | `tests\integration\api\test_waterfall_view.py:43` |
| 3 | PZ-13558 | `tests\integration\api\test_nfft_overlap_edge_case.py:43` |
| 4 | PZ-13563 | `tests\integration\api\test_api_endpoints_additional.py:236` |
| 5 | PZ-13570 | `tests\integration\e2e\test_configure_metadata_grpc_flow.py:53` |
| 6 | PZ-13598 | `tests\data_quality\test_mongodb_schema_validation.py:47` |
| 7 | PZ-13602 | `tests\infrastructure\test_rabbitmq_connectivity.py:49` |
| 8 | PZ-13683 | `tests\data_quality\test_mongodb_schema_validation.py:102` |
| 9 | PZ-13686 | `tests\data_quality\test_mongodb_schema_validation.py:173` |
| 10 | PZ-13687 | `tests\data_quality\test_mongodb_recovery.py:45` |
| 11 | PZ-13705 | `tests\data_quality\test_recordings_classification.py:44` |
| 12 | PZ-13768 | `tests\infrastructure\test_rabbitmq_outage_handling.py:53` |
| 13 | PZ-13784 | `tests\integration\api\test_live_monitoring_flow.py:50` |
| 14 | PZ-13785 | `tests\integration\api\test_live_monitoring_flow.py:116` |
| 15 | PZ-13786 | `tests\integration\api\test_live_monitoring_flow.py:173` |
| 16 | PZ-13787 | `tests\integration\api\test_dynamic_roi_adjustment.py:147` |
| 17 | PZ-13788 | `tests\integration\api\test_dynamic_roi_adjustment.py:223` |
| 18 | PZ-13789 | `tests\integration\api\test_dynamic_roi_adjustment.py:255` |
| 19 | PZ-13790 | `tests\integration\api\test_dynamic_roi_adjustment.py:285` |
| 20 | PZ-13791 | `tests\integration\api\test_dynamic_roi_adjustment.py:346` |
| 21 | PZ-13792 | `tests\integration\api\test_dynamic_roi_adjustment.py:366` |
| 22 | PZ-13793 | `tests\integration\api\test_dynamic_roi_adjustment.py:385` |
| 23 | PZ-13794 | `tests\integration\api\test_dynamic_roi_adjustment.py:405` |
| 24 | PZ-13795 | `tests\integration\api\test_dynamic_roi_adjustment.py:422` |
| 25 | PZ-13796 | `tests\integration\api\test_dynamic_roi_adjustment.py:481` |
| 26 | PZ-13797 | `tests\integration\api\test_dynamic_roi_adjustment.py:502` |
| 27 | PZ-13798 | `tests\integration\api\test_dynamic_roi_adjustment.py:523` |
| 28 | PZ-13799 | `tests\integration\api\test_dynamic_roi_adjustment.py:544` |
| 29 | PZ-13800 | `tests\integration\api\test_live_streaming_stability.py:46` |
| 30 | PZ-13806 | `tests\data_quality\test_mongodb_indexes_and_schema.py:60` |
| 31 | PZ-13807 | `tests\data_quality\test_mongodb_indexes_and_schema.py:109` |
| 32 | PZ-13808 | `tests\data_quality\test_mongodb_indexes_and_schema.py:145` |
| 33 | PZ-13809 | `tests\data_quality\test_mongodb_indexes_and_schema.py:198` |
| 34 | PZ-13810 | `tests\data_quality\test_mongodb_indexes_and_schema.py:235` |
| 35 | PZ-13816 | `tests\integration\api\test_singlechannel_view_mapping.py:919` |
| 36 | PZ-13817 | `tests\integration\api\test_singlechannel_view_mapping.py:813` |
| 37 | PZ-13818 | `tests\integration\api\test_singlechannel_view_mapping.py:321` |
| 38 | PZ-13820 | `tests\integration\api\test_singlechannel_view_mapping.py:762` |
| 39 | PZ-13822 | `tests\integration\api\test_singlechannel_view_mapping.py:633` |
| 40 | PZ-13824 | `tests\integration\api\test_singlechannel_view_mapping.py:480` |
| 41 | PZ-13834 | `tests\integration\api\test_singlechannel_view_mapping.py:993` |
| 42 | PZ-13853 | `tests\integration\api\test_singlechannel_view_mapping.py:1091` |
| 43 | PZ-13857 | `tests\integration\api\test_singlechannel_view_mapping.py:596` |
| 44 | PZ-13858 | `tests\integration\api\test_singlechannel_view_mapping.py:1138` |
| 45 | PZ-13859 | `tests\integration\api\test_singlechannel_view_mapping.py:1181` |
| 46 | PZ-13860 | `tests\integration\api\test_singlechannel_view_mapping.py:1229` |
| 47 | PZ-13861 | `tests\integration\api\test_singlechannel_view_mapping.py:125` |
| 48 | PZ-13862 | `tests\integration\api\test_singlechannel_view_mapping.py:1268` |
| 49 | PZ-13866 | `tests\integration\api\test_historic_playback_additional.py:128` |
| 50 | PZ-13867 | `tests\integration\api\test_historic_playback_additional.py:280` |
| 51 | PZ-13868 | `tests\integration\api\test_historic_playback_additional.py:175` |
| 52 | PZ-13869 | `tests\integration\api\test_prelaunch_validations.py:436` |
| 53 | PZ-13870 | `tests\integration\api\test_historic_playback_additional.py:392` |
| 54 | PZ-13871 | `tests\integration\api\test_historic_playback_additional.py:338` |
| 55 | PZ-13872 | `tests\integration\api\test_historic_playback_e2e.py:49` |
| 56 | PZ-13874 | `tests\integration\api\test_config_validation_nfft_frequency.py:331` |
| 57 | PZ-13875 | `tests\integration\api\test_config_validation_nfft_frequency.py:344` |
| 58 | PZ-13876 | `tests\integration\api\test_prelaunch_validations.py:519` |
| 59 | PZ-13878 | `tests\integration\api\test_prelaunch_validations.py:720`, `tests\integration\api\test_view_type_validation.py:171` |
| 60 | PZ-13879 | `tests\integration\api\test_config_validation_high_priority.py:113` |
| 61 | PZ-13880 | `tests\stress\test_extreme_configurations.py:44` |
| 62 | PZ-13896 | `tests\integration\api\test_api_endpoints_high_priority.py:125` |
| 63 | PZ-13897 | `tests\integration\api\test_api_endpoints_additional.py:52`, `tests\integration\api\test_api_endpoints_high_priority.py:164` |
| 64 | PZ-13898 | `tests\infrastructure\test_external_connectivity.py:68`, `tests\integration\api\test_api_endpoints_high_priority.py:217` |
| 65 | PZ-13899 | `tests\infrastructure\test_external_connectivity.py:173`, `tests\integration\api\test_api_endpoints_high_priority.py:288` |
| 66 | PZ-13900 | `tests\infrastructure\test_external_connectivity.py:306` |
| 67 | PZ-13901 | `tests\integration\api\test_config_validation_nfft_frequency.py:102` |
| 68 | PZ-13904 | `tests\integration\api\test_config_validation_nfft_frequency.py:181` |
| 69 | PZ-13905 | `tests\integration\api\test_config_validation_nfft_frequency.py:250` |
| 70 | PZ-13906 | `tests\integration\api\test_config_validation_nfft_frequency.py:287` |
| 71 | PZ-13907 | `tests\integration\api\test_config_validation_high_priority.py:1069` |
| 72 | PZ-13909 | `tests\integration\api\test_config_validation_high_priority.py:1030` |
| 73 | PZ-14018 | `tests\integration\api\test_orchestration_validation.py:51` |
| 74 | PZ-14019 | `tests\integration\api\test_orchestration_validation.py:150` |
| 75 | PZ-14026 | `tests\integration\api\test_health_check.py:54` |
| 76 | PZ-14027 | `tests\integration\api\test_health_check.py:133` |
| 77 | PZ-14028 | `tests\integration\api\test_health_check.py:204` |
| 78 | PZ-14029 | `tests\integration\api\test_health_check.py:310` |
| 79 | PZ-14030 | `tests\integration\api\test_health_check.py:372` |
| 80 | PZ-14031 | `tests\integration\api\test_health_check.py:443` |
| 81 | PZ-14032 | `tests\integration\api\test_health_check.py:506` |
| 82 | PZ-14033 | `tests\integration\api\test_health_check.py:562` |
| 83 | PZ-14060 | `tests\integration\calculations\test_system_calculations.py:32` |
| 84 | PZ-14061 | `tests\integration\calculations\test_system_calculations.py:89` |
| 85 | PZ-14062 | `tests\integration\calculations\test_system_calculations.py:138` |
| 86 | PZ-14066 | `tests\integration\calculations\test_system_calculations.py:193` |
| 87 | PZ-14067 | `tests\integration\calculations\test_system_calculations.py:242` |
| 88 | PZ-14068 | `tests\integration\calculations\test_system_calculations.py:274` |
| 89 | PZ-14069 | `tests\integration\calculations\test_system_calculations.py:315`, `tests\integration\calculations\test_system_calculations.py:350` |
| 90 | PZ-14070 | `tests\integration\calculations\test_system_calculations.py:391` |
| 91 | PZ-14071 | `tests\integration\calculations\test_system_calculations.py:456` |
| 92 | PZ-14072 | `tests\integration\calculations\test_system_calculations.py:496` |
| 93 | PZ-14073 | `tests\integration\calculations\test_system_calculations.py:536` |
| 94 | PZ-14078 | `tests\integration\calculations\test_system_calculations.py:574` |
| 95 | PZ-14079 | `tests\integration\calculations\test_system_calculations.py:615` |
| 96 | PZ-14080 | `tests\integration\calculations\test_system_calculations.py:658` |
| 97 | PZ-14088 | `tests\load\test_job_capacity_limits.py:810`, `tests\load\test_job_capacity_limits.py:825` |
| 98 | PZ-14089 | `tests\integration\api\test_prelaunch_validations.py:358` |
| 99 | PZ-14090 | `tests\integration\performance\test_latency_requirements.py:205` |
| 100 | PZ-14091 | `tests\integration\performance\test_latency_requirements.py:153` |
| ... | ... and 94 more | ... |

