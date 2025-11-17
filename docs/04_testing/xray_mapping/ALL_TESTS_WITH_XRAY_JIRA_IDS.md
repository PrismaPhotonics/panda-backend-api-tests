# 📋 רשימה מלאה של טסטים עם Xray/Jira IDs
**תאריך:** 2025-10-30
**סך הכל טסטים:** 143
**Xray IDs:** 152
**Jira IDs:** 7

---

## 📂 tests\data_quality\test_mongodb_data_quality.py

**מספר טסטים:** 1

### ✅ `TestMongoDBDataQuality::test_mongodb_indexes_exist_and_optimal`

**קובץ:** `tests\data_quality\test_mongodb_data_quality.py:690`

**Jira Bugs:** `PZ-13983`

---

## 📂 tests\data_quality\test_mongodb_indexes_and_schema.py

**מספר טסטים:** 7

### ✅ `TestMongoDBConnection::test_mongodb_direct_tcp_connection`

**קובץ:** `tests\data_quality\test_mongodb_indexes_and_schema.py:61`

**Xray IDs:** `PZ-13806`

---

### ✅ `TestMongoDBConnection::test_mongodb_connection_using_focus_config`

**קובץ:** `tests\data_quality\test_mongodb_indexes_and_schema.py:110`

**Xray IDs:** `PZ-13807`

---

### ✅ `TestMongoDBConnection::test_mongodb_quick_response_time`

**קובץ:** `tests\data_quality\test_mongodb_indexes_and_schema.py:142`

**Xray IDs:** `PZ-13808`

---

### ✅ `TestMongoDBCollectionsAndIndexes::test_required_mongodb_collections_exist`

**קובץ:** `tests\data_quality\test_mongodb_indexes_and_schema.py:195`

**Xray IDs:** `PZ-13809`

---

### ✅ `TestMongoDBCollectionsAndIndexes::test_critical_mongodb_indexes_exist`

**קובץ:** `tests\data_quality\test_mongodb_indexes_and_schema.py:232`

**Xray IDs:** `PZ-13810`

---

### ✅ `TestMongoDBSchemaValidation::test_recordings_document_schema_validation`

**קובץ:** `tests\data_quality\test_mongodb_indexes_and_schema.py:300`

**Xray IDs:** `PZ-13684`, `PZ-13811`

---

### ✅ `TestMongoDBSchemaValidation::test_recordings_metadata_completeness`

**קובץ:** `tests\data_quality\test_mongodb_indexes_and_schema.py:345`

**Xray IDs:** `PZ-13685`, `PZ-13812`

---

## 📂 tests\data_quality\test_mongodb_recovery.py

**מספר טסטים:** 1

### ✅ `TestMongoDBRecovery::test_mongodb_recovery_recordings_indexed_after_outage`

**קובץ:** `tests\data_quality\test_mongodb_recovery.py:46`

**Xray IDs:** `PZ-13687`

---

## 📂 tests\data_quality\test_mongodb_schema_validation.py

**מספר טסטים:** 3

### ✅ `TestMongoDBDataQuality::test_mongodb_data_quality_general`

**קובץ:** `tests\data_quality\test_mongodb_schema_validation.py:48`

**Xray IDs:** `PZ-13598`

---

### ✅ `TestMongoDBDataQuality::test_recording_collection_schema_validation`

**קובץ:** `tests\data_quality\test_mongodb_schema_validation.py:103`

**Xray IDs:** `PZ-13683`

---

### ✅ `TestMongoDBDataQuality::test_metadata_collection_schema_validation`

**קובץ:** `tests\data_quality\test_mongodb_schema_validation.py:174`

**Xray IDs:** `PZ-13686`

---

## 📂 tests\data_quality\test_recordings_classification.py

**מספר טסטים:** 1

### ✅ `TestRecordingsClassification::test_historical_vs_live_recordings_classification`

**קובץ:** `tests\data_quality\test_recordings_classification.py:45`

**Xray IDs:** `PZ-13705`

---

## 📂 tests\infrastructure\test_external_connectivity.py

**מספר טסטים:** 3

### ✅ `TestExternalServicesConnectivity::test_mongodb_connection`

**קובץ:** `tests\infrastructure\test_external_connectivity.py:72`

**Xray IDs:** `PZ-13898`

---

### ✅ `TestExternalServicesConnectivity::test_kubernetes_connection`

**קובץ:** `tests\infrastructure\test_external_connectivity.py:177`

**Xray IDs:** `PZ-13899`

---

### ✅ `TestExternalServicesConnectivity::test_ssh_connection`

**קובץ:** `tests\infrastructure\test_external_connectivity.py:310`

**Xray IDs:** `PZ-13900`

---

## 📂 tests\infrastructure\test_rabbitmq_connectivity.py

**מספר טסטים:** 1

### ✅ `TestRabbitMQConnectivity::test_rabbitmq_connection`

**קובץ:** `tests\infrastructure\test_rabbitmq_connectivity.py:50`

**Xray IDs:** `PZ-13602`

---

## 📂 tests\infrastructure\test_rabbitmq_outage_handling.py

**מספר טסטים:** 1

### ✅ `TestRabbitMQOutageHandling::test_rabbitmq_outage_handling`

**קובץ:** `tests\infrastructure\test_rabbitmq_outage_handling.py:54`

**Xray IDs:** `PZ-13768`

---

## 📂 tests\integration\api\test_api_endpoints_additional.py

**מספר טסטים:** 8

### ✅ `TestSensorsEndpoint::test_get_sensors_endpoint`

**קובץ:** `tests\integration\api\test_api_endpoints_additional.py:53`

**Xray IDs:** `PZ-13897`

---

### ✅ `TestLiveMetadataEndpoint::test_get_live_metadata_available`

**קובץ:** `tests\integration\api\test_api_endpoints_additional.py:138`

**Xray IDs:** `PZ-13561`, `PZ-13764`

---

### ✅ `TestLiveMetadataEndpoint::test_get_live_metadata_unavailable_404`

**קובץ:** `tests\integration\api\test_api_endpoints_additional.py:188`

**Xray IDs:** `PZ-13562`, `PZ-13765`

---

### ✅ `TestJobMetadataEndpoint::test_get_metadata_by_job_id`

**קובץ:** `tests\integration\api\test_api_endpoints_additional.py:237`

**Xray IDs:** `PZ-13563`

---

### ✅ `TestRecordingsEndpoint::test_post_recordings_in_time_range`

**קובץ:** `tests\integration\api\test_api_endpoints_additional.py:324`

**Xray IDs:** `PZ-13564`, `PZ-13766`

---

### ✅ `TestInvalidRangeRejection::test_invalid_time_range_rejection`

**קובץ:** `tests\integration\api\test_api_endpoints_additional.py:405`

**Xray IDs:** `PZ-13552`, `PZ-13759`

---

### ✅ `TestInvalidRangeRejection::test_invalid_channel_range_rejection`

**קובץ:** `tests\integration\api\test_api_endpoints_additional.py:458`

**Xray IDs:** `PZ-13554`, `PZ-13760`

---

### ✅ `TestInvalidRangeRejection::test_invalid_frequency_range_rejection`

**קובץ:** `tests\integration\api\test_api_endpoints_additional.py:507`

**Xray IDs:** `PZ-13555`, `PZ-13761`

---

## 📂 tests\integration\api\test_api_endpoints_high_priority.py

**מספר טסטים:** 5

### ✅ `TestChannelsEndpoint::test_get_channels_endpoint_success`

**קובץ:** `tests\integration\api\test_api_endpoints_high_priority.py:41`

**Xray IDs:** `PZ-13560`, `PZ-13762`, `PZ-13895`

---

### ✅ `TestChannelsEndpoint::test_get_channels_endpoint_response_time`

**קובץ:** `tests\integration\api\test_api_endpoints_high_priority.py:126`

**Xray IDs:** `PZ-13896`

---

### ✅ `TestChannelsEndpoint::test_get_channels_endpoint_multiple_calls_consistency`

**קובץ:** `tests\integration\api\test_api_endpoints_high_priority.py:165`

**Xray IDs:** `PZ-13897`

---

### ✅ `TestChannelsEndpoint::test_get_channels_endpoint_channel_ids_sequential`

**קובץ:** `tests\integration\api\test_api_endpoints_high_priority.py:218`

**Xray IDs:** `PZ-13898`

---

### ✅ `TestChannelsEndpoint::test_get_channels_endpoint_enabled_status`

**קובץ:** `tests\integration\api\test_api_endpoints_high_priority.py:289`

**Xray IDs:** `PZ-13899`

---

## 📂 tests\integration\api\test_config_validation_high_priority.py

**מספר טסטים:** 6

### ✅ `TestMissingRequiredFields::test_missing_channels_field`

**קובץ:** `tests\integration\api\test_config_validation_high_priority.py:131`

**Xray IDs:** `PZ-13879`, `PZ-14099`

---

### ✅ `TestMissingRequiredFields::test_missing_frequency_range_field`

**קובץ:** `tests\integration\api\test_config_validation_high_priority.py:179`

**Xray IDs:** `PZ-13879`, `PZ-14098`

---

### ✅ `TestMissingRequiredFields::test_missing_nfft_field`

**קובץ:** `tests\integration\api\test_config_validation_high_priority.py:225`

**Xray IDs:** `PZ-13879`, `PZ-14097`

---

### ✅ `TestMissingRequiredFields::test_missing_display_time_axis_duration`

**קובץ:** `tests\integration\api\test_config_validation_high_priority.py:271`

**Xray IDs:** `PZ-13879`, `PZ-14095`

---

### ✅ `TestLiveModeValidation::test_live_mode_with_only_start_time`

**קובץ:** `tests\integration\api\test_config_validation_high_priority.py:1031`

**Xray IDs:** `PZ-13909`

---

### ✅ `TestLiveModeValidation::test_live_mode_with_only_end_time`

**קובץ:** `tests\integration\api\test_config_validation_high_priority.py:1070`

**Xray IDs:** `PZ-13907`

---

## 📂 tests\integration\api\test_config_validation_nfft_frequency.py

**מספר טסטים:** 7

### ✅ `TestNFFTConfiguration::test_nfft_non_power_of_2`

**קובץ:** `tests\integration\api\test_config_validation_nfft_frequency.py:103`

**Xray IDs:** `PZ-13901`

---

### ✅ `TestFrequencyRangeConfiguration::test_frequency_range_within_nyquist`

**קובץ:** `tests\integration\api\test_config_validation_nfft_frequency.py:143`

**Xray IDs:** `PZ-14100`

---

### ✅ `TestFrequencyRangeConfiguration::test_frequency_range_variations`

**קובץ:** `tests\integration\api\test_config_validation_nfft_frequency.py:182`

**Xray IDs:** `PZ-13904`

---

### ✅ `TestConfigurationCompatibility::test_high_throughput_configuration`

**קובץ:** `tests\integration\api\test_config_validation_nfft_frequency.py:251`

**Xray IDs:** `PZ-13905`

---

### ✅ `TestConfigurationCompatibility::test_low_throughput_configuration`

**קובץ:** `tests\integration\api\test_config_validation_nfft_frequency.py:288`

**Xray IDs:** `PZ-13906`

---

### ✅ `TestSpectrogramPipelineErrors::test_zero_nfft`

**קובץ:** `tests\integration\api\test_config_validation_nfft_frequency.py:332`

**Xray IDs:** `PZ-13874`

---

### ✅ `TestSpectrogramPipelineErrors::test_negative_nfft`

**קובץ:** `tests\integration\api\test_config_validation_nfft_frequency.py:345`

**Xray IDs:** `PZ-13875`

---

## 📂 tests\integration\api\test_dynamic_roi_adjustment.py

**מספר טסטים:** 13

### ✅ `TestDynamicROIHappyPath::test_send_roi_change_command`

**קובץ:** `tests\integration\api\test_dynamic_roi_adjustment.py:148`

**Xray IDs:** `PZ-13787`

---

### ✅ `TestDynamicROIHappyPath::test_multiple_roi_changes_sequence`

**קובץ:** `tests\integration\api\test_dynamic_roi_adjustment.py:224`

**Xray IDs:** `PZ-13788`

---

### ✅ `TestDynamicROIHappyPath::test_roi_expansion`

**קובץ:** `tests\integration\api\test_dynamic_roi_adjustment.py:256`

**Xray IDs:** `PZ-13789`

---

### ✅ `TestDynamicROIHappyPath::test_roi_shrinking`

**קובץ:** `tests\integration\api\test_dynamic_roi_adjustment.py:286`

**Xray IDs:** `PZ-13790`

---

### ✅ `TestDynamicROIHappyPath::test_roi_shift`

**קובץ:** `tests\integration\api\test_dynamic_roi_adjustment.py:347`

**Xray IDs:** `PZ-13791`

---

### ✅ `TestROIEdgeCases::test_roi_with_zero_start`

**קובץ:** `tests\integration\api\test_dynamic_roi_adjustment.py:367`

**Xray IDs:** `PZ-13792`

---

### ✅ `TestROIEdgeCases::test_roi_with_large_range`

**קובץ:** `tests\integration\api\test_dynamic_roi_adjustment.py:386`

**Xray IDs:** `PZ-13793`

---

### ✅ `TestROIEdgeCases::test_roi_with_small_range`

**קובץ:** `tests\integration\api\test_dynamic_roi_adjustment.py:406`

**Xray IDs:** `PZ-13794`

---

### ✅ `TestROIEdgeCases::test_unsafe_roi_change`

**קובץ:** `tests\integration\api\test_dynamic_roi_adjustment.py:423`

**Xray IDs:** `PZ-13795`

---

### ✅ `TestROIErrorHandling::test_roi_with_negative_start`

**קובץ:** `tests\integration\api\test_dynamic_roi_adjustment.py:482`

**Xray IDs:** `PZ-13796`

---

### ✅ `TestROIErrorHandling::test_roi_with_negative_end`

**קובץ:** `tests\integration\api\test_dynamic_roi_adjustment.py:503`

**Xray IDs:** `PZ-13797`

---

### ✅ `TestROIErrorHandling::test_roi_with_reversed_range`

**קובץ:** `tests\integration\api\test_dynamic_roi_adjustment.py:524`

**Xray IDs:** `PZ-13798`

---

### ✅ `TestROIErrorHandling::test_roi_with_equal_start_end`

**קובץ:** `tests\integration\api\test_dynamic_roi_adjustment.py:545`

**Xray IDs:** `PZ-13799`

---

## 📂 tests\integration\api\test_health_check.py

**מספר טסטים:** 8

### ✅ `TestHealthCheckValidResponses::test_ack_health_check_valid_response`

**קובץ:** `tests\integration\api\test_health_check.py:60`

**Xray IDs:** `PZ-14026`

---

### ✅ `TestHealthCheckInvalidMethods::test_ack_rejects_invalid_methods`

**קובץ:** `tests\integration\api\test_health_check.py:135`

**Xray IDs:** `PZ-14027`

---

### ✅ `TestHealthCheckConcurrentRequests::test_ack_concurrent_requests`

**קובץ:** `tests\integration\api\test_health_check.py:210`

**Xray IDs:** `PZ-14028`

---

### ✅ `TestHealthCheckVariousHeaders::test_ack_with_various_headers`

**קובץ:** `tests\integration\api\test_health_check.py:316`

**Xray IDs:** `PZ-14029`

---

### ✅ `TestHealthCheckSecurityHeaders::test_ack_security_headers_validation`

**קובץ:** `tests\integration\api\test_health_check.py:378`

**Xray IDs:** `PZ-14030`

---

### ✅ `TestHealthCheckResponseStructure::test_ack_response_structure_validation`

**קובץ:** `tests\integration\api\test_health_check.py:444`

**Xray IDs:** `PZ-14031`

---

### ✅ `TestHealthCheckSSL::test_ack_with_ssl_tls`

**קובץ:** `tests\integration\api\test_health_check.py:507`

**Xray IDs:** `PZ-14032`

---

### ✅ `TestHealthCheckLoadTesting::test_ack_load_testing`

**קובץ:** `tests\integration\api\test_health_check.py:563`

**Xray IDs:** `PZ-14033`

---

## 📂 tests\integration\api\test_historic_playback_additional.py

**מספר טסטים:** 6

### ✅ `TestHistoricPlaybackEdgeCases::test_historic_playback_short_duration_1_minute`

**קובץ:** `tests\integration\api\test_historic_playback_additional.py:54`

**Xray IDs:** `PZ-13865`, `PZ-14101`

---

### ✅ `TestHistoricPlaybackEdgeCases::test_historic_playback_very_old_timestamps_no_data`

**קובץ:** `tests\integration\api\test_historic_playback_additional.py:129`

**Xray IDs:** `PZ-13866`

---

### ✅ `TestHistoricPlaybackEdgeCases::test_historic_playback_status_208_completion`

**קובץ:** `tests\integration\api\test_historic_playback_additional.py:177`

**Xray IDs:** `PZ-13868`

---

### ✅ `TestHistoricPlaybackDataQuality::test_historic_playback_data_integrity`

**קובץ:** `tests\integration\api\test_historic_playback_additional.py:282`

**Xray IDs:** `PZ-13867`

---

### ✅ `TestHistoricPlaybackDataQuality::test_historic_playback_timestamp_ordering`

**קובץ:** `tests\integration\api\test_historic_playback_additional.py:340`

**Xray IDs:** `PZ-13871`

---

### ✅ `TestHistoricPlaybackDataQuality::test_historic_playback_future_timestamps_rejection`

**קובץ:** `tests\integration\api\test_historic_playback_additional.py:393`

**Xray IDs:** `PZ-13870`

---

## 📂 tests\integration\api\test_historic_playback_e2e.py

**מספר טסטים:** 1

### ✅ `TestHistoricPlaybackCompleteE2E::test_historic_playback_complete_e2e_flow`

**קובץ:** `tests\integration\api\test_historic_playback_e2e.py:51`

**Xray IDs:** `PZ-13872`

---

## 📂 tests\integration\api\test_live_monitoring_flow.py

**מספר טסטים:** 3

### ✅ `TestLiveMonitoringCore::test_live_monitoring_configure_and_poll`

**קובץ:** `tests\integration\api\test_live_monitoring_flow.py:51`

**Xray IDs:** `PZ-13784`

---

### ✅ `TestLiveMonitoringCore::test_live_monitoring_sensor_data_availability`

**קובץ:** `tests\integration\api\test_live_monitoring_flow.py:117`

**Xray IDs:** `PZ-13785`

---

### ✅ `TestLiveMonitoringCore::test_live_monitoring_get_metadata`

**קובץ:** `tests\integration\api\test_live_monitoring_flow.py:175`

**Xray IDs:** `PZ-13786`

**Jira Bugs:** `PZ-13985`

---

## 📂 tests\integration\api\test_live_streaming_stability.py

**מספר טסטים:** 1

### ✅ `TestLiveStreamingStability::test_live_streaming_stability`

**קובץ:** `tests\integration\api\test_live_streaming_stability.py:47`

**Xray IDs:** `PZ-13800`

---

## 📂 tests\integration\api\test_nfft_overlap_edge_case.py

**מספר טסטים:** 1

### ✅ `TestNFFTOverlapEdgeCase::test_overlap_nfft_escalation_edge_case`

**קובץ:** `tests\integration\api\test_nfft_overlap_edge_case.py:44`

**Xray IDs:** `PZ-13558`

---

## 📂 tests\integration\api\test_orchestration_validation.py

**מספר טסטים:** 2

### ✅ `TestOrchestrationValidation::test_invalid_configure_does_not_launch_orchestration`

**קובץ:** `tests\integration\api\test_orchestration_validation.py:52`

**Xray IDs:** `PZ-14018`

---

### ✅ `TestOrchestrationValidation::test_history_with_empty_window_returns_400_no_side_effects`

**קובץ:** `tests\integration\api\test_orchestration_validation.py:151`

**Xray IDs:** `PZ-14019`

---

## 📂 tests\integration\api\test_prelaunch_validations.py

**מספר טסטים:** 8

### ✅ `TestDataAvailabilityValidation::test_data_availability_live_mode`

**קובץ:** `tests\integration\api\test_prelaunch_validations.py:223`

**Xray IDs:** `PZ-13547`, `PZ-13873`

---

### ✅ `TestDataAvailabilityValidation::test_data_availability_historic_mode`

**קובץ:** `tests\integration\api\test_prelaunch_validations.py:275`

**Xray IDs:** `PZ-13547`, `PZ-13548`, `PZ-13863`

---

### ✅ `TestTimeRangeValidation::test_time_range_validation_future_timestamps`

**קובץ:** `tests\integration\api\test_prelaunch_validations.py:359`

**Xray IDs:** `PZ-14089`

---

### ✅ `TestTimeRangeValidation::test_time_range_validation_reversed_range`

**קובץ:** `tests\integration\api\test_prelaunch_validations.py:437`

**Xray IDs:** `PZ-13869`

---

### ✅ `TestConfigurationValidation::test_config_validation_channels_out_of_range`

**קובץ:** `tests\integration\api\test_prelaunch_validations.py:520`

**Xray IDs:** `PZ-13876`

---

### ✅ `TestConfigurationValidation::test_config_validation_frequency_exceeds_nyquist`

**קובץ:** `tests\integration\api\test_prelaunch_validations.py:587`

**Xray IDs:** `PZ-13877`, `PZ-13903`

---

### ✅ `TestConfigurationValidation::test_config_validation_invalid_nfft`

**קובץ:** `tests\integration\api\test_prelaunch_validations.py:659`

**Xray IDs:** `PZ-13874`, `PZ-13875`, `PZ-13901`

---

### ✅ `TestConfigurationValidation::test_config_validation_invalid_view_type`

**קובץ:** `tests\integration\api\test_prelaunch_validations.py:721`

**Xray IDs:** `PZ-13878`

---

## 📂 tests\integration\api\test_singlechannel_view_mapping.py

**מספר טסטים:** 20

### ✅ `TestSingleChannelViewHappyPath::test_configure_singlechannel_mapping`

**קובץ:** `tests\integration\api\test_singlechannel_view_mapping.py:126`

**Xray IDs:** `PZ-13861`

---

### ✅ `TestSingleChannelViewHappyPath::test_configure_singlechannel_channel_1`

**קובץ:** `tests\integration\api\test_singlechannel_view_mapping.py:246`

**Xray IDs:** `PZ-13814`, `PZ-13832`

---

### ✅ `TestSingleChannelViewHappyPath::test_configure_singlechannel_channel_100`

**קובץ:** `tests\integration\api\test_singlechannel_view_mapping.py:284`

**Xray IDs:** `PZ-13815`, `PZ-13833`

---

### ✅ `TestSingleChannelViewHappyPath::test_singlechannel_vs_multichannel_comparison`

**קובץ:** `tests\integration\api\test_singlechannel_view_mapping.py:322`

**Xray IDs:** `PZ-13818`

---

### ✅ `TestSingleChannelViewEdgeCases::test_singlechannel_with_min_not_equal_max_should_fail`

**קובץ:** `tests\integration\api\test_singlechannel_view_mapping.py:421`

**Xray IDs:** `PZ-13823`, `PZ-13852`

**Jira Bugs:** `PZ-13669`

---

### ✅ `TestSingleChannelViewEdgeCases::test_singlechannel_with_zero_channel`

**קובץ:** `tests\integration\api\test_singlechannel_view_mapping.py:481`

**Xray IDs:** `PZ-13824`

---

### ✅ `TestSingleChannelViewEdgeCases::test_singlechannel_with_different_frequency_ranges`

**קובץ:** `tests\integration\api\test_singlechannel_view_mapping.py:530`

**Xray IDs:** `PZ-13819`, `PZ-13854`

---

### ✅ `TestSingleChannelViewErrorHandling::test_singlechannel_with_invalid_nfft`

**קובץ:** `tests\integration\api\test_singlechannel_view_mapping.py:597`

**Xray IDs:** `PZ-13857`

---

### ✅ `TestSingleChannelViewErrorHandling::test_singlechannel_rejects_invalid_nfft_value`

**קובץ:** `tests\integration\api\test_singlechannel_view_mapping.py:634`

**Xray IDs:** `PZ-13822`

---

### ✅ `TestSingleChannelViewErrorHandling::test_singlechannel_with_invalid_height`

**קובץ:** `tests\integration\api\test_singlechannel_view_mapping.py:728`

**Xray IDs:** `PZ-13821`, `PZ-13855`

---

### ✅ `TestSingleChannelViewErrorHandling::test_singlechannel_with_invalid_frequency_range`

**קובץ:** `tests\integration\api\test_singlechannel_view_mapping.py:763`

**Xray IDs:** `PZ-13820`

---

### ✅ `TestSingleChannelBackendConsistency::test_same_channel_multiple_requests_consistent_mapping`

**קובץ:** `tests\integration\api\test_singlechannel_view_mapping.py:814`

**Xray IDs:** `PZ-13817`

---

### ✅ `TestSingleChannelBackendConsistency::test_different_channels_different_mappings`

**קובץ:** `tests\integration\api\test_singlechannel_view_mapping.py:920`

**Xray IDs:** `PZ-13816`

---

### ✅ `TestSingleChannelBackendConsistency::test_singlechannel_middle_channel`

**קובץ:** `tests\integration\api\test_singlechannel_view_mapping.py:994`

**Xray IDs:** `PZ-13834`

---

### ✅ `TestSingleChannelBackendConsistency::test_singlechannel_invalid_channels`

**קובץ:** `tests\integration\api\test_singlechannel_view_mapping.py:1039`

**Xray IDs:** `PZ-13835`, `PZ-13836`, `PZ-13837`

---

### ✅ `TestSingleChannelBackendConsistency::test_singlechannel_data_consistency`

**קובץ:** `tests\integration\api\test_singlechannel_view_mapping.py:1092`

**Xray IDs:** `PZ-13853`

---

### ✅ `TestSingleChannelBackendConsistency::test_singlechannel_rapid_reconfiguration`

**קובץ:** `tests\integration\api\test_singlechannel_view_mapping.py:1139`

**Xray IDs:** `PZ-13858`

---

### ✅ `TestSingleChannelBackendConsistency::test_singlechannel_polling_stability`

**קובץ:** `tests\integration\api\test_singlechannel_view_mapping.py:1183`

**Xray IDs:** `PZ-13859`

---

### ✅ `TestSingleChannelBackendConsistency::test_singlechannel_metadata_consistency`

**קובץ:** `tests\integration\api\test_singlechannel_view_mapping.py:1230`

**Xray IDs:** `PZ-13860`

---

### ✅ `TestSingleChannelBackendConsistency::test_singlechannel_complete_e2e_flow`

**קובץ:** `tests\integration\api\test_singlechannel_view_mapping.py:1271`

**Xray IDs:** `PZ-13862`

---

## 📂 tests\integration\api\test_view_type_validation.py

**מספר טסטים:** 3

### ✅ `TestViewTypeValidation::test_invalid_view_type_string`

**קובץ:** `tests\integration\api\test_view_type_validation.py:49`

**Xray IDs:** `PZ-14094`

---

### ✅ `TestViewTypeValidation::test_invalid_view_type_out_of_range`

**קובץ:** `tests\integration\api\test_view_type_validation.py:105`

**Xray IDs:** `PZ-14093`

---

### ✅ `TestViewTypeValidation::test_valid_view_types`

**קובץ:** `tests\integration\api\test_view_type_validation.py:172`

**Xray IDs:** `PZ-13878`

---

## 📂 tests\integration\api\test_waterfall_view.py

**מספר טסטים:** 1

### ✅ `TestWaterfallView::test_waterfall_view_handling`

**קובץ:** `tests\integration\api\test_waterfall_view.py:45`

**Xray IDs:** `PZ-13557`

**Jira Bugs:** `PZ-13238`

---

## 📂 tests\integration\calculations\test_system_calculations.py

**מספר טסטים:** 15

### ✅ `TestFrequencyCalculations::test_frequency_resolution_calculation`

**קובץ:** `tests\integration\calculations\test_system_calculations.py:33`

**Xray IDs:** `PZ-14060`

---

### ✅ `TestFrequencyCalculations::test_frequency_bins_count_calculation`

**קובץ:** `tests\integration\calculations\test_system_calculations.py:90`

**Xray IDs:** `PZ-14061`

---

### ✅ `TestFrequencyCalculations::test_nyquist_frequency_calculation`

**קובץ:** `tests\integration\calculations\test_system_calculations.py:139`

**Xray IDs:** `PZ-14062`

---

### ✅ `TestTimeCalculations::test_lines_dt_calculation`

**קובץ:** `tests\integration\calculations\test_system_calculations.py:194`

**Xray IDs:** `PZ-14066`

---

### ✅ `TestTimeCalculations::test_output_rate_calculation`

**קובץ:** `tests\integration\calculations\test_system_calculations.py:243`

**Xray IDs:** `PZ-14067`

---

### ✅ `TestTimeCalculations::test_time_window_duration_calculation`

**קובץ:** `tests\integration\calculations\test_system_calculations.py:275`

**Xray IDs:** `PZ-14068`

---

### ✅ `TestChannelCalculations::test_channel_count_calculation`

**קובץ:** `tests\integration\calculations\test_system_calculations.py:316`

**Xray IDs:** `PZ-14069`

---

### ✅ `TestChannelCalculations::test_singlechannel_mapping_calculation`

**קובץ:** `tests\integration\calculations\test_system_calculations.py:351`

**Xray IDs:** `PZ-14069`

---

### ✅ `TestChannelCalculations::test_multichannel_mapping_calculation`

**קובץ:** `tests\integration\calculations\test_system_calculations.py:392`

**Xray IDs:** `PZ-14070`

---

### ✅ `TestChannelCalculations::test_stream_amount_calculation`

**קובץ:** `tests\integration\calculations\test_system_calculations.py:457`

**Xray IDs:** `PZ-14071`

---

### ✅ `TestValidationCalculations::test_fft_window_size_validation`

**קובץ:** `tests\integration\calculations\test_system_calculations.py:497`

**Xray IDs:** `PZ-14072`

---

### ✅ `TestValidationCalculations::test_overlap_percentage_validation`

**קובץ:** `tests\integration\calculations\test_system_calculations.py:537`

**Xray IDs:** `PZ-14073`

---

### ✅ `TestPerformanceCalculations::test_data_rate_calculation`

**קובץ:** `tests\integration\calculations\test_system_calculations.py:575`

**Xray IDs:** `PZ-14078`

---

### ✅ `TestPerformanceCalculations::test_memory_usage_estimation`

**קובץ:** `tests\integration\calculations\test_system_calculations.py:616`

**Xray IDs:** `PZ-14079`

---

### ✅ `TestPerformanceCalculations::test_spectrogram_dimensions_calculation`

**קובץ:** `tests\integration\calculations\test_system_calculations.py:659`

**Xray IDs:** `PZ-14080`

---

## 📂 tests\integration\e2e\test_configure_metadata_grpc_flow.py

**מספר טסטים:** 1

### ✅ `TestConfigureMetadataGRPCFlow::test_e2e_configure_metadata_grpc_flow`

**קובץ:** `tests\integration\e2e\test_configure_metadata_grpc_flow.py:54`

**Xray IDs:** `PZ-13570`

---

## 📂 tests\integration\performance\test_latency_requirements.py

**מספר טסטים:** 3

### ✅ `TestConfigurationEndpointLatency::test_config_endpoint_p95_latency`

**קובץ:** `tests\integration\performance\test_latency_requirements.py:101`

**Xray IDs:** `PZ-14092`

---

### ✅ `TestConfigurationEndpointLatency::test_config_endpoint_p99_latency`

**קובץ:** `tests\integration\performance\test_latency_requirements.py:154`

**Xray IDs:** `PZ-14091`

---

### ✅ `TestConfigurationEndpointLatency::test_job_creation_time`

**קובץ:** `tests\integration\performance\test_latency_requirements.py:206`

**Xray IDs:** `PZ-14090`

---

## 📂 tests\load\test_job_capacity_limits.py

**מספר טסטים:** 6

### ✅ `TestBaselinePerformance::test_single_job_baseline`

**קובץ:** `tests\load\test_job_capacity_limits.py:383`

**Jira Bugs:** `PZ-13268`, `PZ-13986`

---

### ✅ `TestLinearLoad::test_linear_load_progression`

**קובץ:** `tests\load\test_job_capacity_limits.py:432`

**Jira Bugs:** `PZ-13268`, `PZ-13986`

---

### ✅ `TestStressLoad::test_extreme_concurrent_load`

**קובץ:** `tests\load\test_job_capacity_limits.py:527`

**Jira Bugs:** `PZ-13268`, `PZ-13986`

---

### ✅ `TestHeavyConfigurationStress::test_heavy_config_concurrent`

**קובץ:** `tests\load\test_job_capacity_limits.py:585`

**Jira Bugs:** `PZ-13986`

---

### ✅ `TestSystemRecovery::test_recovery_after_stress`

**קובץ:** `tests\load\test_job_capacity_limits.py:635`

**Jira Bugs:** `PZ-13986`

---

### ✅ `Test200ConcurrentJobsCapacity::test_200_concurrent_jobs_target_capacity`

**קובץ:** `tests\load\test_job_capacity_limits.py:805`

**Xray IDs:** `PZ-14088`

---

## 📂 tests\performance\test_mongodb_outage_resilience.py

**מספר טסטים:** 5

### ✅ `TestMongoDBOutageResilience::test_mongodb_scale_down_outage_returns_503_no_orchestration`

**קובץ:** `tests\performance\test_mongodb_outage_resilience.py:159`

**Xray IDs:** `PZ-13603`, `PZ-13604`, `PZ-13767`

**Jira Bugs:** `PZ-13640`

---

### ✅ `TestMongoDBOutageResilience::test_mongodb_network_block_outage_returns_503_no_orchestration`

**קובץ:** `tests\performance\test_mongodb_outage_resilience.py:224`

**Jira Bugs:** `PZ-13640`

---

### ✅ `TestMongoDBOutageResilience::test_mongodb_outage_no_live_impact`

**קובץ:** `tests\performance\test_mongodb_outage_resilience.py:290`

**Jira Bugs:** `PZ-13640`

---

### ✅ `TestMongoDBOutageResilience::test_mongodb_outage_logging_and_metrics`

**קובץ:** `tests\performance\test_mongodb_outage_resilience.py:345`

**Jira Bugs:** `PZ-13640`

---

### ✅ `TestMongoDBOutageResilience::test_mongodb_outage_cleanup_and_restore`

**קובץ:** `tests\performance\test_mongodb_outage_resilience.py:398`

**Jira Bugs:** `PZ-13640`

---

## 📂 tests\security\test_malformed_input_handling.py

**מספר טסטים:** 1

### ✅ `TestMalformedInputHandling::test_robustness_to_malformed_inputs`

**קובץ:** `tests\security\test_malformed_input_handling.py:45`

**Xray IDs:** `PZ-13572`, `PZ-13769`

---

## 📂 tests\stress\test_extreme_configurations.py

**מספר טסטים:** 1

### ✅ `TestExtremeConfigurationValues::test_configuration_with_extreme_values`

**קובץ:** `tests\stress\test_extreme_configurations.py:46`

**Xray IDs:** `PZ-13880`

---

