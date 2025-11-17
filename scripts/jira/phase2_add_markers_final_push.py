"""Phase 2: Add Missing Markers - Final Push to 99% Coverage"""
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("="*80)
print("Phase 2: Add Missing Markers - Final Push to 99% Coverage")
print("="*80)
print()

# Final comprehensive mapping - targeting remaining 132 test functions
# Format: (file_path, function_name, jira_test_id)
FINAL_MAPPING = [
    # Data Quality - MongoDB Data Quality (remaining)
    ("tests/data_quality/test_mongodb_data_quality.py", "test_mongodb_collections_exist", "PZ-13683"),
    ("tests/data_quality/test_mongodb_data_quality.py", "test_node4_schema_validation", "PZ-13684"),
    ("tests/data_quality/test_mongodb_data_quality.py", "test_mongodb_indexes_validation", "PZ-13686"),
    ("tests/data_quality/test_mongodb_recovery.py", "test_recordings_indexed_after_outage", "PZ-13687"),
    
    # Infrastructure - Resilience (remaining)
    ("tests/infrastructure/resilience/test_focus_server_pod_resilience.py", "test_focus_server_pod_deletion_recreation", "PZ-14727"),
    ("tests/infrastructure/resilience/test_focus_server_pod_resilience.py", "test_focus_server_scale_down_to_zero", "PZ-14728"),
    ("tests/infrastructure/resilience/test_focus_server_pod_resilience.py", "test_focus_server_pod_restart_during_job_creation", "PZ-14729"),
    ("tests/infrastructure/resilience/test_focus_server_pod_resilience.py", "test_focus_server_outage_graceful_degradation", "PZ-14730"),
    ("tests/infrastructure/resilience/test_focus_server_pod_resilience.py", "test_focus_server_recovery_after_outage", "PZ-14731"),
    
    ("tests/infrastructure/resilience/test_mongodb_pod_resilience.py", "test_mongodb_pod_deletion_recreation", "PZ-14715"),
    ("tests/infrastructure/resilience/test_mongodb_pod_resilience.py", "test_mongodb_scale_down_to_zero", "PZ-14716"),
    ("tests/infrastructure/resilience/test_mongodb_pod_resilience.py", "test_mongodb_pod_restart_during_job_creation", "PZ-14717"),
    ("tests/infrastructure/resilience/test_mongodb_pod_resilience.py", "test_mongodb_outage_graceful_degradation", "PZ-14718"),
    ("tests/infrastructure/resilience/test_mongodb_pod_resilience.py", "test_mongodb_recovery_after_outage", "PZ-14719"),
    
    ("tests/infrastructure/resilience/test_rabbitmq_pod_resilience.py", "test_rabbitmq_pod_deletion_recreation", "PZ-14721"),
    ("tests/infrastructure/resilience/test_rabbitmq_pod_resilience.py", "test_rabbitmq_scale_down_to_zero", "PZ-14722"),
    ("tests/infrastructure/resilience/test_rabbitmq_pod_resilience.py", "test_rabbitmq_pod_restart_during_operations", "PZ-14723"),
    ("tests/infrastructure/resilience/test_rabbitmq_pod_resilience.py", "test_rabbitmq_outage_graceful_degradation", "PZ-14724"),
    ("tests/infrastructure/resilience/test_rabbitmq_pod_resilience.py", "test_rabbitmq_recovery_after_outage", "PZ-14725"),
    
    ("tests/infrastructure/resilience/test_segy_recorder_pod_resilience.py", "test_segy_recorder_pod_deletion_recreation", "PZ-14733"),
    ("tests/infrastructure/resilience/test_segy_recorder_pod_resilience.py", "test_segy_recorder_scale_down_to_zero", "PZ-14734"),
    ("tests/infrastructure/resilience/test_segy_recorder_pod_resilience.py", "test_segy_recorder_pod_restart_during_recording", "PZ-14735"),
    ("tests/infrastructure/resilience/test_segy_recorder_pod_resilience.py", "test_segy_recorder_outage_behavior", "PZ-14736"),
    
    ("tests/infrastructure/resilience/test_pod_recovery_scenarios.py", "test_recovery_order_validation", "PZ-14742"),
    ("tests/infrastructure/resilience/test_pod_recovery_scenarios.py", "test_cascading_recovery_scenarios", "PZ-14743"),
    
    # Infrastructure - Other
    ("tests/infrastructure/test_system_behavior.py", "test_system_behavior", "PZ-13873"),
    ("tests/infrastructure/test_pz_integration.py", "test_pz_integration", "PZ-13873"),
    
    # Integration - Calculations (all already have markers - skip)
    # Integration - E2E
    ("tests/integration/e2e/test_configure_metadata_grpc_flow.py", "test_e2e_configure_metadata_grpc_flow", "PZ-13570"),
    
    # Integration - API - Historic Playback Additional (remaining)
    ("tests/integration/api/test_historic_playback_additional.py", "test_historic_playback_short_duration_1_minute", "PZ-14101"),
    ("tests/integration/api/test_historic_playback_additional.py", "test_historic_playback_very_old_timestamps_no_data", "PZ-13866"),
    ("tests/integration/api/test_historic_playback_additional.py", "test_historic_playback_status_208_completion", "PZ-13868"),
    ("tests/integration/api/test_historic_playback_additional.py", "test_historic_playback_data_integrity", "PZ-13867"),
    ("tests/integration/api/test_historic_playback_additional.py", "test_historic_playback_timestamp_ordering", "PZ-13871"),
    
    # Integration - API - Dynamic ROI (remaining)
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_roi_change_with_validation", "PZ-13785"),
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_multiple_roi_changes_sequence", "PZ-13786"),
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_roi_with_zero_start", "PZ-13796"),
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_roi_with_large_range", "PZ-13795"),
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_roi_with_small_range", "PZ-13794"),
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_roi_with_negative_start", "PZ-13792"),
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_roi_with_negative_end", "PZ-13793"),
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_roi_with_reversed_range", "PZ-13791"),
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_roi_with_equal_start_end", "PZ-13790"),
    
    # Integration - API - Live Monitoring (remaining)
    ("tests/integration/api/test_live_monitoring_flow.py", "test_live_monitoring_sensor_data_availability", "PZ-13785"),
    ("tests/integration/api/test_live_monitoring_flow.py", "test_live_monitoring_metadata_consistency", "PZ-13985"),
    ("tests/integration/api/test_live_monitoring_flow.py", "test_live_monitoring_stream_stability", "PZ-13570"),
    ("tests/integration/api/test_live_monitoring_flow.py", "test_live_monitoring_error_handling", "PZ-14787"),
    
    # Integration - API - Live Streaming Stability (remaining)
    ("tests/integration/api/test_live_streaming_stability.py", "test_live_streaming_long_duration", "PZ-13570"),
    ("tests/integration/api/test_live_streaming_stability.py", "test_live_streaming_reconnection", "PZ-13570"),
    ("tests/integration/api/test_live_streaming_stability.py", "test_live_streaming_data_quality", "PZ-14810"),
    
    # Integration - API - SingleChannel (remaining - already have most)
    # Integration - API - Health Check (all already have markers - skip)
    # Integration - API - Configure/Config Task/Waterfall/Task Metadata (all already have markers - skip)
    
    # Load Tests (remaining)
    ("tests/load/test_job_capacity_limits.py", "test_recovery_after_stress", "PZ-14088"),
    
    # Performance Tests (all already have markers - skip)
    # Security Tests (all already have markers - skip)
]

# Patterns
xray_pattern = re.compile(r'@pytest\.mark\.xray\(["\']([^"\']+)["\']\)')
jira_pattern = re.compile(r'@pytest\.mark\.jira\(["\']([^"\']+)["\']\)')

def add_marker_to_function(file_path: Path, function_name: str, test_id: str) -> bool:
    """Add Xray marker to a test function."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Find the function - handle both class methods and module-level functions
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
print("Adding markers to remaining test functions")
print("="*80)
print()

added_count = 0
skipped_count = 0
error_count = 0

for file_path_str, function_name, test_id in FINAL_MAPPING:
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

