"""Phase 2: Add Missing Markers - Batch 3"""
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("="*80)
print("Phase 2: Add Missing Markers - Batch 3")
print("="*80)
print()

# Additional verified matches for Integration API tests
# Format: (file_path, function_name, jira_test_id)
BATCH3_MATCHES = [
    # Integration - API - Configure Endpoint
    ("tests/integration/api/test_configure_endpoint.py", "test_configure_valid_request", "PZ-13547"),
    ("tests/integration/api/test_configure_endpoint.py", "test_configure_invalid_request", "PZ-13879"),
    ("tests/integration/api/test_configure_endpoint.py", "test_configure_missing_required_fields", "PZ-13879"),
    ("tests/integration/api/test_configure_endpoint.py", "test_configure_invalid_parameters", "PZ-13878"),
    ("tests/integration/api/test_configure_endpoint.py", "test_configure_response_structure", "PZ-13873"),
    ("tests/integration/api/test_configure_endpoint.py", "test_configure_concurrent_requests", "PZ-14800"),
    ("tests/integration/api/test_configure_endpoint.py", "test_configure_error_handling", "PZ-14787"),
    
    # Integration - API - Config Task Endpoint
    ("tests/integration/api/test_config_task_endpoint.py", "test_config_task_valid_request", "PZ-13547"),
    ("tests/integration/api/test_config_task_endpoint.py", "test_config_task_invalid_task_id", "PZ-13879"),
    ("tests/integration/api/test_config_task_endpoint.py", "test_config_task_missing_fields", "PZ-13879"),
    ("tests/integration/api/test_config_task_endpoint.py", "test_config_task_response_time", "PZ-14090"),
    
    # Integration - API - High Priority Endpoints
    ("tests/integration/api/test_api_endpoints_high_priority.py", "test_get_channels_endpoint", "PZ-13560"),
    ("tests/integration/api/test_api_endpoints_high_priority.py", "test_get_channels_response_structure", "PZ-13762"),
    ("tests/integration/api/test_api_endpoints_high_priority.py", "test_get_channels_enabled_list", "PZ-13895"),
    ("tests/integration/api/test_api_endpoints_high_priority.py", "test_get_channels_error_handling", "PZ-14787"),
    
    # Integration - API - Waterfall Endpoint
    ("tests/integration/api/test_waterfall_endpoint.py", "test_waterfall_valid_request", "PZ-13557"),
    ("tests/integration/api/test_waterfall_endpoint.py", "test_waterfall_invalid_task_id", "PZ-13557"),
    ("tests/integration/api/test_waterfall_endpoint.py", "test_waterfall_invalid_row_count", "PZ-13557"),
    ("tests/integration/api/test_waterfall_endpoint.py", "test_waterfall_no_data_available", "PZ-13557"),
    ("tests/integration/api/test_waterfall_endpoint.py", "test_waterfall_response_structure", "PZ-13557"),
    ("tests/integration/api/test_waterfall_endpoint.py", "test_waterfall_response_time", "PZ-14791"),
    
    # Integration - API - Task Metadata Endpoint
    ("tests/integration/api/test_task_metadata_endpoint.py", "test_task_metadata_valid_request", "PZ-13563"),
    ("tests/integration/api/test_task_metadata_endpoint.py", "test_task_metadata_invalid_task_id", "PZ-13563"),
    ("tests/integration/api/test_task_metadata_endpoint.py", "test_task_metadata_response_structure", "PZ-13563"),
    ("tests/integration/api/test_task_metadata_endpoint.py", "test_task_metadata_consistency", "PZ-14763"),
    
    # Integration - API - View Type Validation
    ("tests/integration/api/test_view_type_validation.py", "test_invalid_view_type_rejection", "PZ-13878"),
    ("tests/integration/api/test_view_type_validation.py", "test_view_type_string_value", "PZ-14094"),
    
    # Integration - API - NFFT Overlap Edge Case
    ("tests/integration/api/test_nfft_overlap_edge_case.py", "test_nfft_overlap_edge_case", "PZ-13558"),
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
        lines = content[:func_start].split('\n')
        func_line_num = len(lines) - 1
        
        # Check previous 20 lines for markers
        for i in range(max(0, func_line_num - 20), func_line_num):
            line = lines[i]
            if xray_pattern.search(line) or jira_pattern.search(line):
                if test_id in line:
                    print(f"[SKIP] {function_name} already has marker {test_id}")
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
print("Adding markers to test functions (Batch 3)")
print("="*80)
print()

added_count = 0
skipped_count = 0
error_count = 0

for file_path_str, function_name, test_id in BATCH3_MATCHES:
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

