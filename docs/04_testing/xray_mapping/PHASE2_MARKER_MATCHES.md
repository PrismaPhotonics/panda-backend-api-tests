# Phase 2: Marker Matches - Intelligent Matching

**Date:** 2025-11-09
**Total Matches Found:** 52

---

## Potential Matches

| # | File | Test Function | Jira Test | Summary |
|---|------|---------------|-----------|---------|
| 1 | `tests\data_quality\test_mongodb_data_quality.py` | `test_required_collections_exist` | PZ-13898 | Infrastructure - MongoDB Direct Connection and Health Check |
| 2 | `tests\data_quality\test_mongodb_data_quality.py` | `test_recording_schema_validation` | PZ-14812 | Infrastructure - Data Quality - Data Completeness |
| 3 | `tests\data_quality\test_mongodb_data_quality.py` | `test_mongodb_indexes_exist_and_optimal` | PZ-13810 | Data Quality – Verify Critical MongoDB Indexes Exist |
| 4 | `tests\data_quality\test_mongodb_data_quality.py` | `test_historical_vs_live_recordings` | PZ-13705 | Data Lifecycle – Historical vs Live Recordings Classificatio |
| 5 | `tests\data_quality\test_mongodb_indexes_and_schema.py` | `test_critical_mongodb_indexes_exist` | PZ-13810 | Data Quality – Verify Critical MongoDB Indexes Exist |
| 6 | `tests\data_quality\test_mongodb_indexes_and_schema.py` | `test_recordings_document_schema_validation` | PZ-13811 | Data Quality – Validate Recordings Document Schema |
| 7 | `tests\data_quality\test_mongodb_indexes_and_schema.py` | `test_recordings_metadata_completeness` | PZ-13685 | Data Quality – Recordings Metadata Completeness |
| 8 | `tests\data_quality\test_mongodb_recovery.py` | `test_mongodb_recovery_recordings_indexed_after_outage` | PZ-13810 | Data Quality – Verify Critical MongoDB Indexes Exist |
| 9 | `tests\data_quality\test_mongodb_schema_validation.py` | `test_metadata_collection_schema_validation` | PZ-14812 | Infrastructure - Data Quality - Data Completeness |
| 10 | `tests\data_quality\test_recordings_classification.py` | `test_historical_vs_live_recordings_classification` | PZ-13705 | Data Lifecycle – Historical vs Live Recordings Classificatio |
| 11 | `tests\infrastructure\test_basic_connectivity.py` | `test_mongodb_direct_connection` | PZ-13898 | Infrastructure - MongoDB Direct Connection and Health Check |
| 12 | `tests\infrastructure\test_external_connectivity.py` | `test_mongodb_connection` | PZ-13807 | Infrastructure - Infrastructure – MongoDB Connection Using F |
| 13 | `tests\infrastructure\test_rabbitmq_outage_handling.py` | `test_rabbitmq_outage_handling` | PZ-13879 | Integration – Missing Required Fields |
| 14 | `tests\security\test_malformed_input_handling.py` | `test_robustness_to_malformed_inputs` | PZ-13572 | Security – Robustness to malformed inputs |
| 15 | `tests\stress\test_extreme_configurations.py` | `test_configuration_with_extreme_values` | PZ-13880 | Stress - Configuration with Extreme Values  |
| 16 | `tests\integration\api\test_api_endpoints_additional.py` | `test_get_live_metadata_available` | PZ-14100 | Integration - Frequency Range Within Nyquist Limit |
| 17 | `tests\integration\api\test_api_endpoints_additional.py` | `test_invalid_time_range_rejection` | PZ-13759 | API – POST /config/{task_id} – Invalid Time Range Rejection |
| 18 | `tests\integration\api\test_api_endpoints_additional.py` | `test_invalid_channel_range_rejection` | PZ-13760 | API – POST /config/{task_id} – Invalid Channel Range Rejecti |
| 19 | `tests\integration\api\test_api_endpoints_additional.py` | `test_invalid_frequency_range_rejection` | PZ-13761 | API – POST /config/{task_id} – Invalid Frequency Range Rejec |
| 20 | `tests\integration\api\test_config_validation_high_priority.py` | `test_channel_range_equal_min_max` | PZ-13878 | Integration – Invalid View Type - Out of Range |
| 21 | `tests\integration\api\test_dynamic_roi_adjustment.py` | `test_send_roi_change_command` | PZ-13784 | Integration - Send ROI Change Command via RabbitMQ |
| 22 | `tests\integration\api\test_dynamic_roi_adjustment.py` | `test_roi_shrinking` | PZ-13788 | Integration - ROI Shrinking (Decrease Range) |
| 23 | `tests\integration\api\test_singlechannel_view_mapping.py` | `test_configure_singlechannel_mapping` | PZ-13862 | Integration - SingleChannel Complete Flow End-to-End |
| 24 | `tests\integration\api\test_singlechannel_view_mapping.py` | `test_configure_singlechannel_channel_1` | PZ-13862 | Integration - SingleChannel Complete Flow End-to-End |
| 25 | `tests\integration\api\test_singlechannel_view_mapping.py` | `test_singlechannel_with_zero_channel` | PZ-13878 | Integration – Invalid View Type - Out of Range |
| 26 | `tests\integration\api\test_singlechannel_view_mapping.py` | `test_singlechannel_rejects_invalid_nfft_value` | PZ-13822 | API – SingleChannel Rejects Invalid NFFT Value |
| 27 | `tests\integration\api\test_singlechannel_view_mapping.py` | `test_singlechannel_middle_channel` | PZ-13862 | Integration - SingleChannel Complete Flow End-to-End |
| 28 | `tests\integration\api\test_singlechannel_view_mapping.py` | `test_singlechannel_complete_e2e_flow` | PZ-13873 | integration - Valid Configuration - All Parameters |
| 29 | `tests\integration\api\test_waterfall_view.py` | `test_waterfall_view_handling` | PZ-13557 | API – Waterfall view handling |
| 30 | `tests\integration\calculations\test_system_calculations.py` | `test_spectrogram_dimensions_calculation` | PZ-14080 | Historic – Spectrogram Dimensions Calculation |
| 31 | `tests\integration\data_quality\test_data_completeness.py` | `test_data_completeness` | PZ-14812 | Infrastructure - Data Quality - Data Completeness |
| 32 | `tests\integration\data_quality\test_data_consistency.py` | `test_metadata_consistency` | PZ-14809 | Infrastructure - Data Quality - Metadata Consistency |
| 33 | `tests\integration\data_quality\test_data_integrity.py` | `test_data_integrity_across_requests` | PZ-14810 | Infrastructure - Data Quality - Data Integrity Across Reques |
| 34 | `tests\integration\error_handling\test_http_error_codes.py` | `test_504_gateway_timeout` | PZ-14782 | Infrastructure - Error Handling - 504 Gateway Timeout |
| 35 | `tests\integration\error_handling\test_invalid_payloads.py` | `test_error_message_format` | PZ-14787 | Infrastructure - Error Handling - Error Message Format |
| 36 | `tests\integration\error_handling\test_network_errors.py` | `test_connection_refused` | PZ-14784 | Infrastructure - Error Handling - Connection Refused |
| 37 | `tests\integration\load\test_concurrent_load.py` | `test_concurrent_job_creation_load` | PZ-14800 | Infrastructure - Load - Concurrent Job Creation Load |
| 38 | `tests\integration\load\test_recovery_and_exhaustion.py` | `test_resource_exhaustion_under_load` | PZ-14807 | Infrastructure - Load - Resource Exhaustion Under Load |
| 39 | `tests\integration\performance\test_concurrent_performance.py` | `test_concurrent_requests_performance` | PZ-14793 | Infrastructure - Performance - Concurrent Requests Performan |
| 40 | `tests\integration\performance\test_database_performance.py` | `test_database_query_performance` | PZ-14797 | Infrastructure - Performance - Database Query Performance |
| 41 | `tests\integration\performance\test_latency_requirements.py` | `test_job_creation_time` | PZ-14090 | Performance - Job Creation Time < 2 Seconds |
| 42 | `tests\integration\performance\test_resource_usage.py` | `test_cpu_usage_under_load` | PZ-14796 | Infrastructure - Performance - CPU Usage Under Load |
| 43 | `tests\integration\performance\test_response_time.py` | `test_metadata_response_time` | PZ-14792 | Infrastructure - Performance - GET /metadata Response Time |
| 44 | `tests\integration\security\test_api_authentication.py` | `test_expired_authentication_token` | PZ-14773 | Infrastructure - Security - Expired Authentication Token |
| 45 | `tests\integration\security\test_csrf_protection.py` | `test_csrf_protection` | PZ-14776 | Infrastructure - Security - CSRF Protection |
| 46 | `tests\integration\security\test_input_validation.py` | `test_input_sanitization` | PZ-14788 | Infrastructure - Security - Input Sanitization |
| 47 | `tests\integration\security\test_rate_limiting.py` | `test_rate_limiting` | PZ-14777 | Infrastructure - Security - Rate Limiting |
| 48 | `tests\infrastructure\resilience\test_focus_server_pod_resilience.py` | `test_focus_server_pod_status_monitoring` | PZ-14732 | Infrastructure - Focus Server Pod Status Monitoring |
| 49 | `tests\infrastructure\resilience\test_mongodb_pod_resilience.py` | `test_mongodb_pod_status_monitoring` | PZ-14720 | Infrastructure - MongoDB Pod Status Monitoring |
| 50 | `tests\infrastructure\resilience\test_pod_recovery_scenarios.py` | `test_recovery_time_measurement` | PZ-14744 | Infrastructure - Recovery Time Measurement |
| 51 | `tests\infrastructure\resilience\test_rabbitmq_pod_resilience.py` | `test_rabbitmq_pod_status_monitoring` | PZ-14726 | Infrastructure - RabbitMQ Pod Status Monitoring |
| 52 | `tests\infrastructure\resilience\test_segy_recorder_pod_resilience.py` | `test_segy_recorder_recovery_after_outage` | PZ-14737 | Infrastructure - SEGY Recorder Recovery After Outage |

## Next Steps

1. Review matches manually
2. Add markers to confirmed matches
3. Create Jira tests for unmatched functions
