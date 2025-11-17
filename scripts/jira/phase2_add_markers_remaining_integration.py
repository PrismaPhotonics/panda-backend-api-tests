"""Phase 2: Add Missing Markers - Remaining Integration Tests"""
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("="*80)
print("Phase 2: Add Missing Markers - Remaining Integration Tests")
print("="*80)
print()

# Remaining integration tests that need markers
# Based on actual test files and TEST_PLAN_PZ14024_DETAILED_REPORT.md
REMAINING_INTEGRATION_MAPPING = [
    # Integration - Data Quality
    ("tests/integration/data_quality/test_data_completeness.py", "test_data_completeness", "PZ-14812"),
    ("tests/integration/data_quality/test_data_consistency.py", "test_metadata_consistency", "PZ-14809"),
    ("tests/integration/data_quality/test_data_integrity.py", "test_data_integrity_across_requests", "PZ-14810"),
    
    # Integration - Error Handling
    ("tests/integration/error_handling/test_http_error_codes.py", "test_504_gateway_timeout", "PZ-14782"),
    ("tests/integration/error_handling/test_invalid_payloads.py", "test_error_message_format", "PZ-14787"),
    ("tests/integration/error_handling/test_network_errors.py", "test_connection_refused", "PZ-14784"),
    
    # Integration - Load
    ("tests/integration/load/test_concurrent_load.py", "test_concurrent_job_creation_load", "PZ-14800"),
    ("tests/integration/load/test_load_profiles.py", "test_steady_state_load_profile", "PZ-14805"),
    ("tests/integration/load/test_peak_load.py", "test_peak_load_high_rps", "PZ-14802"),
    ("tests/integration/load/test_recovery_and_exhaustion.py", "test_resource_exhaustion_under_load", "PZ-14807"),
    ("tests/integration/load/test_sustained_load.py", "test_sustained_load_1_hour", "PZ-14801"),
    
    # Integration - Performance
    ("tests/integration/performance/test_concurrent_performance.py", "test_concurrent_requests_performance", "PZ-14793"),
    ("tests/integration/performance/test_database_performance.py", "test_database_query_performance", "PZ-14797"),
    ("tests/integration/performance/test_latency_requirements.py", "test_job_creation_time", "PZ-14090"),
    ("tests/integration/performance/test_network_latency.py", "test_end_to_end_latency", "PZ-14799"),
    ("tests/integration/performance/test_resource_usage.py", "test_cpu_usage_under_load", "PZ-14796"),
    ("tests/integration/performance/test_response_time.py", "test_metadata_response_time", "PZ-14792"),
    
    # Integration - Security
    ("tests/integration/security/test_api_authentication.py", "test_expired_authentication_token", "PZ-14773"),
    ("tests/integration/security/test_csrf_protection.py", "test_csrf_protection", "PZ-14776"),
    ("tests/integration/security/test_input_validation.py", "test_input_sanitization", "PZ-14788"),
    ("tests/integration/security/test_rate_limiting.py", "test_rate_limiting", "PZ-14777"),
    
    # Load Tests
    ("tests/load/test_job_capacity_limits.py", "test_recovery_after_stress", "PZ-14088"),
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
print("Adding markers to remaining integration tests")
print("="*80)
print()

added_count = 0
skipped_count = 0
error_count = 0

for file_path_str, function_name, test_id in REMAINING_INTEGRATION_MAPPING:
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

