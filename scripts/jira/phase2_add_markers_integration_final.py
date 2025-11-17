"""Phase 2: Add Missing Markers - Integration Tests Final"""
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("="*80)
print("Phase 2: Add Missing Markers - Integration Tests Final")
print("="*80)
print()

# Integration tests that need markers
# Based on actual test files and TEST_PLAN_PZ14024_DETAILED_REPORT.md
INTEGRATION_FINAL_MAPPING = [
    # Integration - API - Dynamic ROI
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_send_roi_change_command", "PZ-13784"),
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_roi_shrinking", "PZ-13788"),
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_roi_with_equal_start_end", "PZ-13790"),
    
    # Integration - API - Health Check
    ("tests/integration/api/test_health_check.py", "test_ack_load_testing", "PZ-14033"),
    
    # Integration - API - Historic Playback Additional
    ("tests/integration/api/test_historic_playback_additional.py", "test_historic_playback_future_timestamps_rejection", "PZ-13870"),
    
    # Integration - API - Historic Playback E2E
    ("tests/integration/api/test_historic_playback_e2e.py", "test_historic_playback_complete_e2e_flow", "PZ-13872"),
    
    # Integration - API - Live Monitoring
    ("tests/integration/api/test_live_monitoring_flow.py", "test_live_monitoring_get_metadata", "PZ-13786"),
    
    # Integration - API - Live Streaming Stability
    ("tests/integration/api/test_live_streaming_stability.py", "test_live_streaming_stability", "PZ-13800"),
    
    # Integration - API - NFFT Overlap Edge Case
    ("tests/integration/api/test_nfft_overlap_edge_case.py", "test_overlap_nfft_escalation_edge_case", "PZ-13558"),
    
    # Integration - API - Orchestration Validation
    ("tests/integration/api/test_orchestration_validation.py", "test_history_with_empty_window_returns_400_no_side_effects", "PZ-14019"),
    
    # Integration - API - Prelaunch Validations
    ("tests/integration/api/test_prelaunch_validations.py", "test_data_availability_live_mode", "PZ-13547"),
    ("tests/integration/api/test_prelaunch_validations.py", "test_config_validation_channels_out_of_range", "PZ-13876"),
    ("tests/integration/api/test_prelaunch_validations.py", "test_config_validation_frequency_exceeds_nyquist", "PZ-13877"),
    ("tests/integration/api/test_prelaunch_validations.py", "test_config_validation_invalid_view_type", "PZ-13878"),
    ("tests/integration/api/test_prelaunch_validations.py", "test_prelaunch_validation_error_messages_clarity", "PZ-13878"),
    
    # Integration - API - SingleChannel View Mapping
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_configure_singlechannel_mapping", "PZ-13862"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_configure_singlechannel_channel_1", "PZ-13814"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_with_zero_channel", "PZ-13824"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_rejects_invalid_nfft_value", "PZ-13822"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_middle_channel", "PZ-13834"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_complete_e2e_flow", "PZ-13862"),
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
print("Adding markers to integration tests")
print("="*80)
print()

added_count = 0
skipped_count = 0
error_count = 0

for file_path_str, function_name, test_id in INTEGRATION_FINAL_MAPPING:
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

