"""Phase 2: Add Missing Markers - Comprehensive Final Push"""
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("="*80)
print("Phase 2: Add Missing Markers - Comprehensive Final Push")
print("="*80)
print()

# Comprehensive mapping based on PHASE1_ANALYSIS_REPORT.md and TEST_PLAN_PZ14024_DETAILED_REPORT.md
# Format: (file_path, function_name, jira_test_id)
COMPREHENSIVE_MAPPING = [
    # Integration - API - Live Monitoring
    ("tests/integration/api/test_live_monitoring_flow.py", "test_live_monitoring_sensor_data_availability", "PZ-13786"),
    ("tests/integration/api/test_live_monitoring_flow.py", "test_live_monitoring_metadata_consistency", "PZ-13985"),
    ("tests/integration/api/test_live_monitoring_flow.py", "test_live_monitoring_stream_stability", "PZ-13570"),
    ("tests/integration/api/test_live_monitoring_flow.py", "test_live_monitoring_error_handling", "PZ-14787"),
    
    # Integration - API - Live Streaming Stability
    ("tests/integration/api/test_live_streaming_stability.py", "test_live_streaming_long_duration", "PZ-13570"),
    ("tests/integration/api/test_live_streaming_stability.py", "test_live_streaming_reconnection", "PZ-13570"),
    ("tests/integration/api/test_live_streaming_stability.py", "test_live_streaming_data_quality", "PZ-14810"),
    
    # Integration - API - Historic Playback Additional
    ("tests/integration/api/test_historic_playback_additional.py", "test_historic_playback_short_duration", "PZ-14101"),
    ("tests/integration/api/test_historic_playback_additional.py", "test_historic_playback_long_duration", "PZ-13863"),
    ("tests/integration/api/test_historic_playback_additional.py", "test_historic_playback_old_timestamps", "PZ-13866"),
    ("tests/integration/api/test_historic_playback_additional.py", "test_historic_playback_data_integrity", "PZ-13867"),
    ("tests/integration/api/test_historic_playback_additional.py", "test_historic_playback_polling", "PZ-13868"),
    
    # Integration - API - Historic Playback E2E
    ("tests/integration/api/test_historic_playback_e2e.py", "test_historic_playback_complete_flow", "PZ-13872"),
    ("tests/integration/api/test_historic_playback_e2e.py", "test_historic_playback_timestamp_ordering", "PZ-13871"),
    ("tests/integration/api/test_historic_playback_e2e.py", "test_historic_playback_status_208", "PZ-13868"),
    
    # Integration - API - Dynamic ROI Adjustment
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_roi_expansion", "PZ-13787"),
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_roi_shift", "PZ-13789"),
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_roi_reversed_range", "PZ-13791"),
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_roi_negative_start", "PZ-13792"),
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_roi_negative_end", "PZ-13793"),
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_roi_small_range", "PZ-13794"),
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_roi_large_range", "PZ-13795"),
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_roi_starting_at_zero", "PZ-13796"),
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_unsafe_roi_change", "PZ-13797"),
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_unsafe_roi_range_change", "PZ-13798"),
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_unsafe_roi_shift", "PZ-13799"),
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_safe_roi_change", "PZ-13800"),
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_roi_change_with_safety_validation", "PZ-13785"),
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_multiple_roi_changes_in_sequence", "PZ-13786"),
    
    # Integration - API - SingleChannel (additional tests)
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_channel_100", "PZ-13815"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_different_channels", "PZ-13816"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_consistent_mapping", "PZ-13817"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_vs_multichannel", "PZ-13818"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_invalid_frequency_range", "PZ-13820"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_invalid_display_height", "PZ-13821"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_rejects_min_not_equal_max", "PZ-13823"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_rejects_channel_zero", "PZ-13824"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_minimum_channel", "PZ-13832"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_maximum_channel", "PZ-13833"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_invalid_channel_high", "PZ-13835"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_invalid_channel_negative", "PZ-13836"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_min_greater_than_max", "PZ-13852"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_data_consistency", "PZ-13853"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_frequency_range_validation", "PZ-13854"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_canvas_height_validation", "PZ-13855"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_nfft_validation", "PZ-13857"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_rapid_reconfiguration", "PZ-13858"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_polling_stability", "PZ-13859"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_metadata_consistency", "PZ-13860"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_stream_mapping_verification", "PZ-13861"),
    
    # Integration - API - Health Check (additional tests)
    ("tests/integration/api/test_health_check.py", "test_ack_rejects_invalid_http_methods", "PZ-14027"),
    ("tests/integration/api/test_health_check.py", "test_ack_handles_concurrent_requests", "PZ-14028"),
    ("tests/integration/api/test_health_check.py", "test_ack_with_various_headers", "PZ-14029"),
    ("tests/integration/api/test_health_check.py", "test_ack_security_headers_validation", "PZ-14030"),
    ("tests/integration/api/test_health_check.py", "test_ack_response_structure_validation", "PZ-14031"),
    ("tests/integration/api/test_health_check.py", "test_ack_with_ssl_tls", "PZ-14032"),
    
    # Integration - API - Configure Endpoint (additional tests)
    ("tests/integration/api/test_configure_endpoint.py", "test_configure_valid_configuration", "PZ-13547"),
    ("tests/integration/api/test_configure_endpoint.py", "test_configure_response_time_performance", "PZ-14790"),
    
    # Integration - API - Config Task Endpoint (additional tests)
    ("tests/integration/api/test_config_task_endpoint.py", "test_config_task_valid_configuration", "PZ-13547"),
    ("tests/integration/api/test_config_task_endpoint.py", "test_config_task_missing_required_fields", "PZ-13879"),
    ("tests/integration/api/test_config_task_endpoint.py", "test_config_task_invalid_sensor_range", "PZ-14753"),
    ("tests/integration/api/test_config_task_endpoint.py", "test_config_task_invalid_frequency_range", "PZ-14754"),
    
    # Integration - API - API Endpoints High Priority (additional tests)
    ("tests/integration/api/test_api_endpoints_high_priority.py", "test_get_channels_endpoint_response_time", "PZ-14790"),
    ("tests/integration/api/test_api_endpoints_high_priority.py", "test_get_channels_endpoint_multiple_calls_consistency", "PZ-14809"),
    ("tests/integration/api/test_api_endpoints_high_priority.py", "test_get_channels_endpoint_channel_ids_sequential", "PZ-13762"),
    ("tests/integration/api/test_api_endpoints_high_priority.py", "test_get_channels_endpoint_enabled_status", "PZ-13895"),
    
    # Integration - API - Waterfall Endpoint (additional tests)
    ("tests/integration/api/test_waterfall_endpoint.py", "test_waterfall_valid_request", "PZ-14755"),
    ("tests/integration/api/test_waterfall_endpoint.py", "test_waterfall_no_data_available", "PZ-14756"),
    ("tests/integration/api/test_waterfall_endpoint.py", "test_waterfall_invalid_row_count", "PZ-14758"),
    
    # Integration - API - Task Metadata Endpoint (additional tests)
    ("tests/integration/api/test_task_metadata_endpoint.py", "test_task_metadata_valid_request", "PZ-14760"),
    ("tests/integration/api/test_task_metadata_endpoint.py", "test_task_metadata_consumer_not_running", "PZ-14761"),
    ("tests/integration/api/test_task_metadata_endpoint.py", "test_task_metadata_invalid_task_id", "PZ-14762"),
    
    # Integration - API - View Type Validation (additional tests)
    ("tests/integration/api/test_view_type_validation.py", "test_invalid_view_type_string", "PZ-14094"),
    ("tests/integration/api/test_view_type_validation.py", "test_invalid_view_type_out_of_range", "PZ-14093"),
    
    # Integration - Calculations
    ("tests/integration/calculations/test_system_calculations.py", "test_frequency_resolution_calculation", "PZ-14060"),
    ("tests/integration/calculations/test_system_calculations.py", "test_frequency_bins_count_calculation", "PZ-14061"),
    ("tests/integration/calculations/test_system_calculations.py", "test_nyquist_frequency_limit_validation", "PZ-14062"),
    ("tests/integration/calculations/test_system_calculations.py", "test_time_resolution_calculation", "PZ-14066"),
    ("tests/integration/calculations/test_system_calculations.py", "test_output_rate_calculation", "PZ-14067"),
    ("tests/integration/calculations/test_system_calculations.py", "test_time_window_duration_calculation", "PZ-14068"),
    ("tests/integration/calculations/test_system_calculations.py", "test_channel_count_calculation", "PZ-14069"),
    ("tests/integration/calculations/test_system_calculations.py", "test_multichannel_mapping_validation", "PZ-14070"),
    ("tests/integration/calculations/test_system_calculations.py", "test_stream_amount_calculation", "PZ-14071"),
    ("tests/integration/calculations/test_system_calculations.py", "test_fft_window_size_validation", "PZ-14072"),
    ("tests/integration/calculations/test_system_calculations.py", "test_overlap_percentage_validation", "PZ-14073"),
    ("tests/integration/calculations/test_system_calculations.py", "test_data_rate_calculation", "PZ-14078"),
    ("tests/integration/calculations/test_system_calculations.py", "test_memory_usage_estimation", "PZ-14079"),
    
    # Integration - E2E
    ("tests/integration/e2e/test_configure_metadata_grpc_flow.py", "test_e2e_configure_metadata_grpc_flow", "PZ-13570"),
    
    # Infrastructure - Resilience
    ("tests/infrastructure/resilience/test_focus_server_pod_resilience.py", "test_focus_server_pod_deletion_and_recreation", "PZ-14727"),
    ("tests/infrastructure/resilience/test_focus_server_pod_resilience.py", "test_focus_server_scale_down_to_zero", "PZ-14728"),
    ("tests/infrastructure/resilience/test_focus_server_pod_resilience.py", "test_focus_server_pod_restart_during_job_creation", "PZ-14729"),
    ("tests/infrastructure/resilience/test_focus_server_pod_resilience.py", "test_focus_server_outage_graceful_degradation", "PZ-14730"),
    ("tests/infrastructure/resilience/test_focus_server_pod_resilience.py", "test_focus_server_recovery_after_outage", "PZ-14731"),
    
    ("tests/infrastructure/resilience/test_mongodb_pod_resilience.py", "test_mongodb_pod_deletion_and_recreation", "PZ-14715"),
    ("tests/infrastructure/resilience/test_mongodb_pod_resilience.py", "test_mongodb_scale_down_to_zero", "PZ-14716"),
    ("tests/infrastructure/resilience/test_mongodb_pod_resilience.py", "test_mongodb_pod_restart_during_job_creation", "PZ-14717"),
    ("tests/infrastructure/resilience/test_mongodb_pod_resilience.py", "test_mongodb_outage_graceful_degradation", "PZ-14718"),
    ("tests/infrastructure/resilience/test_mongodb_pod_resilience.py", "test_mongodb_recovery_after_outage", "PZ-14719"),
    
    ("tests/infrastructure/resilience/test_rabbitmq_pod_resilience.py", "test_rabbitmq_pod_deletion_and_recreation", "PZ-14721"),
    ("tests/infrastructure/resilience/test_rabbitmq_pod_resilience.py", "test_rabbitmq_scale_down_to_zero", "PZ-14722"),
    ("tests/infrastructure/resilience/test_rabbitmq_pod_resilience.py", "test_rabbitmq_pod_restart_during_operations", "PZ-14723"),
    ("tests/infrastructure/resilience/test_rabbitmq_pod_resilience.py", "test_rabbitmq_outage_graceful_degradation", "PZ-14724"),
    ("tests/infrastructure/resilience/test_rabbitmq_pod_resilience.py", "test_rabbitmq_recovery_after_outage", "PZ-14725"),
    
    ("tests/infrastructure/resilience/test_segy_recorder_pod_resilience.py", "test_segy_recorder_pod_deletion_and_recreation", "PZ-14733"),
    ("tests/infrastructure/resilience/test_segy_recorder_pod_resilience.py", "test_segy_recorder_scale_down_to_zero", "PZ-14734"),
    ("tests/infrastructure/resilience/test_segy_recorder_pod_resilience.py", "test_segy_recorder_pod_restart_during_recording", "PZ-14735"),
    ("tests/infrastructure/resilience/test_segy_recorder_pod_resilience.py", "test_segy_recorder_outage_behavior", "PZ-14736"),
    
    ("tests/infrastructure/resilience/test_pod_recovery_scenarios.py", "test_recovery_order_validation", "PZ-14742"),
    ("tests/infrastructure/resilience/test_pod_recovery_scenarios.py", "test_cascading_recovery_scenarios", "PZ-14743"),
    
    ("tests/infrastructure/resilience/test_multiple_pods_resilience.py", "test_mongodb_rabbitmq_down_simultaneously", "PZ-14738"),
    ("tests/infrastructure/resilience/test_multiple_pods_resilience.py", "test_mongodb_focus_server_down_simultaneously", "PZ-14739"),
    ("tests/infrastructure/resilience/test_multiple_pods_resilience.py", "test_rabbitmq_focus_server_down_simultaneously", "PZ-14740"),
    ("tests/infrastructure/resilience/test_multiple_pods_resilience.py", "test_focus_server_segy_recorder_down_simultaneously", "PZ-14741"),
    
    # Infrastructure - Other
    ("tests/infrastructure/test_system_behavior.py", "test_system_behavior", "PZ-13873"),
    ("tests/infrastructure/test_pz_integration.py", "test_pz_integration", "PZ-13873"),
    
    # Data Quality
    ("tests/data_quality/test_mongodb_data_quality.py", "test_mongodb_collections_exist", "PZ-13683"),
    ("tests/data_quality/test_mongodb_data_quality.py", "test_node4_schema_validation", "PZ-13684"),
    ("tests/data_quality/test_mongodb_data_quality.py", "test_mongodb_indexes_validation", "PZ-13686"),
    ("tests/data_quality/test_mongodb_recovery.py", "test_recordings_indexed_after_outage", "PZ-13687"),
    
    # Load
    ("tests/load/test_job_capacity_limits.py", "test_single_job_baseline", "PZ-14088"),
    ("tests/load/test_job_capacity_limits.py", "test_linear_load_progression", "PZ-14088"),
    ("tests/load/test_job_capacity_limits.py", "test_recovery_after_stress", "PZ-14088"),
    
    # Performance
    ("tests/performance/test_mongodb_outage_resilience.py", "test_mongodb_scale_down_outage_returns_503_no_orchestration", "PZ-13603"),
    ("tests/performance/test_mongodb_outage_resilience.py", "test_mongodb_network_block_outage_returns_503_no_orchestration", "PZ-13603"),
    ("tests/performance/test_mongodb_outage_resilience.py", "test_mongodb_outage_no_live_impact", "PZ-13603"),
    ("tests/performance/test_mongodb_outage_resilience.py", "test_mongodb_outage_logging_and_metrics", "PZ-13603"),
    ("tests/performance/test_mongodb_outage_resilience.py", "test_mongodb_outage_cleanup_and_restore", "PZ-13603"),
]

# Patterns
xray_pattern = re.compile(r'@pytest\.mark\.xray\(["\']([^"\']+)["\']\)')
jira_pattern = re.compile(r'@pytest\.mark\.jira\(["\']([^"\']+)["\']\)')

def add_marker_to_function(file_path: Path, function_name: str, test_id: str) -> bool:
    """Add Xray marker to a test function."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Find the function
        func_pattern = re.compile(
            rf'(def\s+{re.escape(function_name)}\s*\([^)]*\):)',
            re.MULTILINE
        )
        match = func_pattern.search(content)
        
        if not match:
            return False
        
        func_start = match.start()
        
        # Check if function already has marker
        lines = content[:func_start].split('\n')
        func_line_num = len(lines) - 1
        
        # Check previous 20 lines for markers
        for i in range(max(0, func_line_num - 20), func_line_num):
            line = lines[i]
            if xray_pattern.search(line) or jira_pattern.search(line):
                if test_id in line:
                    return False
        
        # Find where to insert marker
        insert_pos = func_start
        decorator_pattern = re.compile(r'^\s*@', re.MULTILINE)
        decorator_matches = list(decorator_pattern.finditer(content[:func_start]))
        
        if decorator_matches:
            last_decorator = decorator_matches[-1]
            line_end = content.find('\n', last_decorator.end())
            if line_end == -1:
                line_end = len(content)
            insert_pos = line_end + 1
        else:
            insert_pos = func_start
        
        # Get indentation
        func_line = lines[-1] if lines else ""
        indent = len(func_line) - len(func_line.lstrip())
        indent_str = ' ' * indent
        
        # Create marker line
        marker_line = f"{indent_str}@pytest.mark.xray(\"{test_id}\")\n"
        
        # Insert marker
        new_content = content[:insert_pos] + marker_line + content[insert_pos:]
        
        # Write back
        file_path.write_text(new_content, encoding='utf-8')
        print(f"[OK] Added marker {test_id} to {function_name} in {file_path.name}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to add marker to {function_name} in {file_path}: {e}")
        return False

# Process matches
print("="*80)
print("Adding markers to all remaining test functions")
print("="*80)
print()

added_count = 0
skipped_count = 0
error_count = 0

for file_path_str, function_name, test_id in COMPREHENSIVE_MAPPING:
    file_path = project_root / file_path_str
    
    if not file_path.exists():
        print(f"[WARNING] File not found: {file_path_str}")
        error_count += 1
        continue
    
    if add_marker_to_function(file_path, function_name, test_id):
        added_count += 1
    else:
        skipped_count += 1

print()
print("="*80)
print("SUMMARY")
print("="*80)
print()
print(f"Markers added: {added_count}")
print(f"Markers skipped (already exist or not found): {skipped_count}")
print(f"Errors: {error_count}")
print()

