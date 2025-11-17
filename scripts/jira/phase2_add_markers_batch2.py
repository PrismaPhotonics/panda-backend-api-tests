"""Phase 2: Add Missing Markers - Batch 2"""
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("="*80)
print("Phase 2: Add Missing Markers - Batch 2")
print("="*80)
print()

# Additional verified matches from PHASE2_MARKER_MATCHES.md
# Format: (file_path, function_name, jira_test_id)
ADDITIONAL_MATCHES = [
    # Integration - API tests
    ("tests/integration/api/test_config_validation_high_priority.py", "test_requirement_negative_height_must_be_rejected", "PZ-13878"),
    ("tests/integration/api/test_config_validation_high_priority.py", "test_requirement_zero_height_must_be_rejected", "PZ-13878"),
    ("tests/integration/api/test_config_validation_high_priority.py", "test_requirement_nfft_must_be_power_of_2", "PZ-13873"),
    ("tests/integration/api/test_config_validation_high_priority.py", "test_requirement_nfft_max_2048", "PZ-13873"),
    ("tests/integration/api/test_config_validation_high_priority.py", "test_requirement_reject_only_start_time", "PZ-13552"),
    ("tests/integration/api/test_config_validation_high_priority.py", "test_requirement_reject_only_end_time", "PZ-13552"),
    ("tests/integration/api/test_config_validation_high_priority.py", "test_requirement_frequency_must_not_exceed_nyquist", "PZ-13555"),
    
    # Integration - API - NFFT/Frequency
    ("tests/integration/api/test_config_validation_nfft_frequency.py", "test_negative_nfft", "PZ-13555"),
    
    # Integration - API - ROI
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_roi_with_equal_start_end", "PZ-13799"),
    
    # Integration - API - Historic Playback
    ("tests/integration/api/test_historic_playback_additional.py", "test_historic_playback_future_timestamps_rejection", "PZ-13984"),
    ("tests/integration/api/test_historic_playback_e2e.py", "test_historic_playback_complete_e2e_flow", "PZ-14101"),
    
    # Integration - API - Live Monitoring
    ("tests/integration/api/test_live_monitoring_flow.py", "test_live_monitoring_get_metadata", "PZ-13561"),
    ("tests/integration/api/test_live_streaming_stability.py", "test_live_streaming_stability", "PZ-13570"),
    
    # Integration - API - Prelaunch
    ("tests/integration/api/test_prelaunch_validations.py", "test_data_availability_live_mode", "PZ-13561"),
    ("tests/integration/api/test_prelaunch_validations.py", "test_config_validation_channels_out_of_range", "PZ-13554"),
    ("tests/integration/api/test_prelaunch_validations.py", "test_config_validation_frequency_exceeds_nyquist", "PZ-13555"),
    ("tests/integration/api/test_prelaunch_validations.py", "test_config_validation_invalid_view_type", "PZ-13878"),
    ("tests/integration/api/test_prelaunch_validations.py", "test_prelaunch_validation_error_messages_clarity", "PZ-13878"),
    
    # Integration - API - SingleChannel
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_complete_e2e_flow", "PZ-13873"),
    
    # Integration - API - Task Metadata
    ("tests/integration/api/test_task_metadata_endpoint.py", "test_task_metadata_response_time", "PZ-14090"),
    
    # Integration - API - View Type
    ("tests/integration/api/test_view_type_validation.py", "test_valid_view_types", "PZ-13873"),
    
    # Integration - API - Waterfall
    ("tests/integration/api/test_waterfall_endpoint.py", "test_waterfall_baby_analyzer_exited", "PZ-13557"),
    
    # Integration - API - NFFT Overlap
    ("tests/integration/api/test_nfft_overlap_edge_case.py", "test_overlap_nfft_escalation_edge_case", "PZ-13873"),
    
    # Integration - API - Orchestration
    ("tests/integration/api/test_orchestration_validation.py", "test_history_with_empty_window_returns_400_no_side_effects", "PZ-13552"),
    
    # Integration - Load
    ("tests/integration/load/test_load_profiles.py", "test_steady_state_load_profile", "PZ-14800"),
    ("tests/integration/load/test_peak_load.py", "test_peak_load_high_rps", "PZ-14800"),
    
    # Integration - E2E
    ("tests/integration/e2e/test_configure_metadata_grpc_flow.py", "test_e2e_configure_metadata_grpc_flow", "PZ-13873"),
]

# Patterns
xray_pattern = re.compile(r'@pytest\.mark\.xray\(["\']([^"\']+)["\']\)')
jira_pattern = re.compile(r'@pytest\.mark\.jira\(["\']([^"\']+)["\']\)')
test_func_pattern = re.compile(r'def\s+(test_\w+)')

def add_marker_to_function(file_path: Path, function_name: str, test_id: str) -> bool:
    """
    Add Xray marker to a test function.
    
    Returns:
        True if marker was added, False if function already has marker or not found
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Find the function
        func_pattern = re.compile(
            rf'(def\s+{re.escape(function_name)}\s*\([^)]*\):)',
            re.MULTILINE
        )
        match = func_pattern.search(content)
        
        if not match:
            print(f"[WARNING] Function {function_name} not found in {file_path}")
            return False
        
        func_start = match.start()
        
        # Check if function already has marker
        # Look backwards from function definition for decorators
        lines = content[:func_start].split('\n')
        func_line_num = len(lines) - 1
        
        # Check previous 15 lines for markers
        for i in range(max(0, func_line_num - 15), func_line_num):
            line = lines[i]
            if xray_pattern.search(line) or jira_pattern.search(line):
                # Check if this marker is for our test_id
                if test_id in line:
                    print(f"[SKIP] {function_name} already has marker {test_id}")
                    return False
        
        # Find where to insert marker (before function definition)
        # Look for existing decorators
        insert_pos = func_start
        
        # Find the start of decorators (go backwards to find @pytest.mark or @pytest.fixture)
        decorator_pattern = re.compile(r'^\s*@', re.MULTILINE)
        decorator_matches = list(decorator_pattern.finditer(content[:func_start]))
        
        if decorator_matches:
            # Insert after last decorator
            last_decorator = decorator_matches[-1]
            # Find the end of that line
            line_end = content.find('\n', last_decorator.end())
            if line_end == -1:
                line_end = len(content)
            insert_pos = line_end + 1
        else:
            # Insert right before function definition
            insert_pos = func_start
        
        # Get indentation from function definition
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
print("Adding markers to test functions (Batch 2)")
print("="*80)
print()

added_count = 0
skipped_count = 0
error_count = 0

for file_path_str, function_name, test_id in ADDITIONAL_MATCHES:
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
print(f"Markers skipped (already exist): {skipped_count}")
print(f"Errors: {error_count}")
print()

