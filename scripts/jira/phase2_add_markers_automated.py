"""Phase 2: Add Missing Markers - Automated Addition"""
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("="*80)
print("Phase 2: Add Missing Markers - Automated Addition")
print("="*80)
print()

# Matches from intelligent matching (verified manually)
# Format: (file_path, function_name, jira_test_id)
VERIFIED_MATCHES = [
    # Data Quality tests
    ("tests/data_quality/test_mongodb_indexes_and_schema.py", "test_critical_mongodb_indexes_exist", "PZ-13810"),
    ("tests/data_quality/test_mongodb_indexes_and_schema.py", "test_recordings_document_schema_validation", "PZ-13811"),
    ("tests/data_quality/test_mongodb_indexes_and_schema.py", "test_recordings_metadata_completeness", "PZ-13685"),
    ("tests/data_quality/test_mongodb_recovery.py", "test_mongodb_recovery_recordings_indexed_after_outage", "PZ-13810"),
    ("tests/data_quality/test_mongodb_schema_validation.py", "test_metadata_collection_schema_validation", "PZ-14812"),
    ("tests/data_quality/test_recordings_classification.py", "test_historical_vs_live_recordings_classification", "PZ-13705"),
    
    # Infrastructure tests
    ("tests/infrastructure/test_external_connectivity.py", "test_mongodb_connection", "PZ-13807"),
    ("tests/infrastructure/test_rabbitmq_outage_handling.py", "test_rabbitmq_outage_handling", "PZ-13768"),  # Already has xray marker, skip
    
    # Security tests
    ("tests/security/test_malformed_input_handling.py", "test_robustness_to_malformed_inputs", "PZ-13572"),
    
    # Integration tests - API
    ("tests/integration/api/test_api_endpoints_additional.py", "test_get_live_metadata_available", "PZ-13764"),  # Already has marker
    ("tests/integration/api/test_api_endpoints_additional.py", "test_invalid_time_range_rejection", "PZ-13759"),  # Already has marker
    ("tests/integration/api/test_api_endpoints_additional.py", "test_invalid_channel_range_rejection", "PZ-13760"),  # Already has marker
    ("tests/integration/api/test_api_endpoints_additional.py", "test_invalid_frequency_range_rejection", "PZ-13761"),  # Already has marker
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_send_roi_change_command", "PZ-13784"),
    ("tests/integration/api/test_dynamic_roi_adjustment.py", "test_roi_shrinking", "PZ-13788"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_configure_singlechannel_mapping", "PZ-13862"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_configure_singlechannel_channel_1", "PZ-13814"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_with_zero_channel", "PZ-13836"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_rejects_invalid_nfft_value", "PZ-13822"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_middle_channel", "PZ-13819"),
    ("tests/integration/api/test_singlechannel_view_mapping.py", "test_singlechannel_complete_e2e_flow", "PZ-13862"),
    ("tests/integration/api/test_waterfall_view.py", "test_waterfall_view_handling", "PZ-13557"),
    
    # Integration tests - Calculations
    ("tests/integration/calculations/test_system_calculations.py", "test_spectrogram_dimensions_calculation", "PZ-14080"),
    
    # Integration tests - Data Quality
    ("tests/integration/data_quality/test_data_completeness.py", "test_data_completeness", "PZ-14812"),
    ("tests/integration/data_quality/test_data_consistency.py", "test_metadata_consistency", "PZ-14809"),
    ("tests/integration/data_quality/test_data_integrity.py", "test_data_integrity_across_requests", "PZ-14810"),
    
    # Integration tests - Error Handling
    ("tests/integration/error_handling/test_http_error_codes.py", "test_504_gateway_timeout", "PZ-14782"),
    ("tests/integration/error_handling/test_invalid_payloads.py", "test_error_message_format", "PZ-14787"),
    ("tests/integration/error_handling/test_network_errors.py", "test_connection_refused", "PZ-14784"),
    
    # Integration tests - Load
    ("tests/integration/load/test_concurrent_load.py", "test_concurrent_job_creation_load", "PZ-14800"),
    ("tests/integration/load/test_recovery_and_exhaustion.py", "test_resource_exhaustion_under_load", "PZ-14807"),
    
    # Integration tests - Performance
    ("tests/integration/performance/test_concurrent_performance.py", "test_concurrent_requests_performance", "PZ-14793"),
    ("tests/integration/performance/test_database_performance.py", "test_database_query_performance", "PZ-14797"),
    ("tests/integration/performance/test_latency_requirements.py", "test_job_creation_time", "PZ-14090"),
    ("tests/integration/performance/test_resource_usage.py", "test_cpu_usage_under_load", "PZ-14796"),
    ("tests/integration/performance/test_response_time.py", "test_metadata_response_time", "PZ-14792"),
    
    # Integration tests - Security
    ("tests/integration/security/test_api_authentication.py", "test_expired_authentication_token", "PZ-14773"),
    ("tests/integration/security/test_csrf_protection.py", "test_csrf_protection", "PZ-14776"),
    ("tests/integration/security/test_input_validation.py", "test_input_sanitization", "PZ-14788"),
    ("tests/integration/security/test_rate_limiting.py", "test_rate_limiting", "PZ-14777"),
    
    # Infrastructure - Resilience
    ("tests/infrastructure/resilience/test_focus_server_pod_resilience.py", "test_focus_server_pod_status_monitoring", "PZ-14732"),
    ("tests/infrastructure/resilience/test_mongodb_pod_resilience.py", "test_mongodb_pod_status_monitoring", "PZ-14720"),
    ("tests/infrastructure/resilience/test_pod_recovery_scenarios.py", "test_recovery_time_measurement", "PZ-14744"),
    ("tests/infrastructure/resilience/test_rabbitmq_pod_resilience.py", "test_rabbitmq_pod_status_monitoring", "PZ-14726"),
    ("tests/infrastructure/resilience/test_segy_recorder_pod_resilience.py", "test_segy_recorder_recovery_after_outage", "PZ-14737"),
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
        
        # Check previous 10 lines for markers
        for i in range(max(0, func_line_num - 10), func_line_num):
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
print("Adding markers to test functions")
print("="*80)
print()

added_count = 0
skipped_count = 0
error_count = 0

for file_path_str, function_name, test_id in VERIFIED_MATCHES:
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

