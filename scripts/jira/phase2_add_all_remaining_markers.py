"""Phase 2: Add All Remaining Markers - Comprehensive"""
import sys
import re
import csv
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("="*80)
print("Phase 2: Add All Remaining Markers - Comprehensive")
print("="*80)
print()

# Load Jira tests from CSV
jira_tests = {}
csv_file = Path(r"c:\Users\roy.avrahami\Downloads\Jira (28).csv")

if csv_file.exists():
    try:
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                test_key = row.get('Issue key', '')
                if test_key and row.get('Issue Type', '') == 'Test':
                    summary = row.get('Summary', '').lower()
                    jira_tests[test_key] = {
                        'key': test_key,
                        'summary': summary,
                        'description': row.get('Description', '').lower(),
                        'status': row.get('Status', ''),
                        'test_type': row.get('Custom field (Test Type)', ''),
                    }
        print(f"Loaded {len(jira_tests)} tests from Jira CSV")
    except Exception as e:
        print(f"[ERROR] Failed to load CSV: {e}")
        jira_tests = {}
else:
    print(f"[WARNING] CSV file not found: {csv_file}")
    jira_tests = {}

print()

# Patterns
xray_pattern = re.compile(r'@pytest\.mark\.xray\(["\']([^"\']+)["\']\)')
jira_pattern = re.compile(r'@pytest\.mark\.jira\(["\']([^"\']+)["\']\)')
test_func_pattern = re.compile(r'def\s+(test_\w+)')

# Comprehensive mapping based on PHASE1_ANALYSIS_REPORT.md and PHASE2_MARKER_MATCHES.md
COMPREHENSIVE_MAPPING = [
    # Integration - API - Additional endpoints
    ("tests/integration/api/test_api_endpoints_additional.py", "test_get_sensors_endpoint", "PZ-13897"),
    ("tests/integration/api/test_api_endpoints_additional.py", "test_get_live_metadata_unavailable_404", "PZ-13765"),
    ("tests/integration/api/test_api_endpoints_additional.py", "test_post_recordings_in_time_range", "PZ-13564"),
    
    # Integration - API - Performance
    ("tests/integration/performance/test_network_latency.py", "test_end_to_end_latency", "PZ-14090"),
    ("tests/integration/performance/test_performance_high_priority.py", "test_config_endpoint_latency_p95_p99", "PZ-14090"),
    ("tests/integration/performance/test_performance_high_priority.py", "test_concurrent_task_creation", "PZ-14800"),
    ("tests/integration/performance/test_performance_high_priority.py", "test_concurrent_task_polling", "PZ-14800"),
    ("tests/integration/performance/test_performance_high_priority.py", "test_concurrent_task_max_limit", "PZ-14800"),
    
    # Integration - Load
    ("tests/integration/load/test_sustained_load.py", "test_sustained_load_1_hour", "PZ-14800"),
    
    # Integration - Security
    ("tests/integration/security/test_data_exposure.py", "test_data_exposure_prevention", "PZ-13572"),
    ("tests/integration/security/test_data_exposure.py", "test_error_message_security", "PZ-13572"),
    ("tests/integration/security/test_https_enforcement.py", "test_https_enforcement", "PZ-13572"),
    
    # Load tests
    ("tests/load/test_job_capacity_limits.py", "test_single_job_baseline", "PZ-13986"),
    ("tests/load/test_job_capacity_limits.py", "test_linear_load_progression", "PZ-13986"),
    ("tests/load/test_job_capacity_limits.py", "test_recovery_after_stress", "PZ-13986"),
    ("tests/load/test_job_capacity_limits.py", "test_200_concurrent_jobs_target_capacity", "PZ-13986"),
    
    # Performance tests
    ("tests/performance/test_mongodb_outage_resilience.py", "test_mongodb_scale_down_outage_returns_503_no_orchestration", "PZ-13687"),
    ("tests/performance/test_mongodb_outage_resilience.py", "test_mongodb_network_block_outage_returns_503_no_orchestration", "PZ-13687"),
    ("tests/performance/test_mongodb_outage_resilience.py", "test_mongodb_outage_no_live_impact", "PZ-13687"),
    ("tests/performance/test_mongodb_outage_resilience.py", "test_mongodb_outage_logging_and_metrics", "PZ-13687"),
    ("tests/performance/test_mongodb_outage_resilience.py", "test_mongodb_outage_cleanup_and_restore", "PZ-13687"),
    
    # Stress tests
    ("tests/stress/test_extreme_configurations.py", "test_configuration_with_extreme_values", "PZ-13880"),
    
    # Infrastructure tests - K8s
    ("tests/infrastructure/test_k8s_job_lifecycle.py", "test_job_config", "PZ-13899"),
    ("tests/infrastructure/test_k8s_job_lifecycle.py", "test_k8s_job_creation_triggers_pod_spawn", "PZ-13899"),
    ("tests/infrastructure/test_k8s_job_lifecycle.py", "test_k8s_job_resource_allocation", "PZ-13899"),
    ("tests/infrastructure/test_k8s_job_lifecycle.py", "test_k8s_job_port_exposure", "PZ-13899"),
    ("tests/infrastructure/test_k8s_job_lifecycle.py", "test_k8s_job_cancellation_and_cleanup", "PZ-13899"),
    ("tests/infrastructure/test_k8s_job_lifecycle.py", "test_k8s_job_observability", "PZ-13899"),
    
    # Infrastructure tests - MongoDB Monitoring
    ("tests/infrastructure/test_mongodb_monitoring_agent.py", "test_init", "PZ-13898"),
    ("tests/infrastructure/test_mongodb_monitoring_agent.py", "test_connect_success", "PZ-13807"),
    ("tests/infrastructure/test_mongodb_monitoring_agent.py", "test_connect_failure_retry", "PZ-13807"),
    ("tests/infrastructure/test_mongodb_monitoring_agent.py", "test_connect_failure_max_retries", "PZ-13807"),
    ("tests/infrastructure/test_mongodb_monitoring_agent.py", "test_connect_authentication_failure", "PZ-13807"),
    ("tests/infrastructure/test_mongodb_monitoring_agent.py", "test_disconnect", "PZ-13807"),
    ("tests/infrastructure/test_mongodb_monitoring_agent.py", "test_ensure_connected_success", "PZ-13807"),
    ("tests/infrastructure/test_mongodb_monitoring_agent.py", "test_ensure_connected_auto_reconnect", "PZ-13807"),
    ("tests/infrastructure/test_mongodb_monitoring_agent.py", "test_list_databases", "PZ-13809"),
    ("tests/infrastructure/test_mongodb_monitoring_agent.py", "test_list_databases_not_connected", "PZ-13807"),
    ("tests/infrastructure/test_mongodb_monitoring_agent.py", "test_list_collections", "PZ-13809"),
    ("tests/infrastructure/test_mongodb_monitoring_agent.py", "test_get_collection_stats", "PZ-13810"),
    ("tests/infrastructure/test_mongodb_monitoring_agent.py", "test_count_documents", "PZ-13810"),
    ("tests/infrastructure/test_mongodb_monitoring_agent.py", "test_find_documents", "PZ-13810"),
    ("tests/infrastructure/test_mongodb_monitoring_agent.py", "test_get_health_status_healthy", "PZ-13898"),
    ("tests/infrastructure/test_mongodb_monitoring_agent.py", "test_get_health_status_unhealthy", "PZ-13898"),
    ("tests/infrastructure/test_mongodb_monitoring_agent.py", "test_collect_metrics", "PZ-13810"),
    ("tests/infrastructure/test_mongodb_monitoring_agent.py", "test_create_alert", "PZ-13810"),
    ("tests/infrastructure/test_mongodb_monitoring_agent.py", "test_register_alert_callback", "PZ-13810"),
    ("tests/infrastructure/test_mongodb_monitoring_agent.py", "test_get_recent_alerts", "PZ-13810"),
    ("tests/infrastructure/test_mongodb_monitoring_agent.py", "test_start_monitoring", "PZ-13810"),
    ("tests/infrastructure/test_mongodb_monitoring_agent.py", "test_stop_monitoring", "PZ-13810"),
    ("tests/infrastructure/test_mongodb_monitoring_agent.py", "test_context_manager", "PZ-13807"),
    ("tests/infrastructure/test_mongodb_monitoring_agent.py", "test_monitoring_metrics_defaults", "PZ-13810"),
    ("tests/infrastructure/test_mongodb_monitoring_agent.py", "test_alert_creation", "PZ-13810"),
    ("tests/infrastructure/test_mongodb_monitoring_agent.py", "test_alert_level_values", "PZ-13810"),
    
    # Infrastructure tests - RabbitMQ
    ("tests/infrastructure/test_rabbitmq_connectivity.py", "test_rabbitmq_connection", "PZ-13602"),
    
    # Infrastructure tests - External connectivity
    ("tests/infrastructure/test_external_connectivity.py", "test_mongodb_status_via_kubernetes", "PZ-13899"),
    ("tests/infrastructure/test_external_connectivity.py", "test_kubernetes_list_pods", "PZ-13899"),
    ("tests/infrastructure/test_external_connectivity.py", "test_all_services_summary", "PZ-13898"),
    
    # Data Quality tests
    ("tests/data_quality/test_mongodb_data_quality.py", "test_deleted_recordings_marked_properly", "PZ-13812"),
    
    # Scripts - Infrastructure
    ("scripts/test_k8s_fixed.py", "test_kubernetes_connection", "PZ-13899"),
    ("scripts/test_mongodb_connection.py", "test_mongodb_connection", "PZ-13898"),
    ("scripts/test_ssh_connection.py", "test_direct_ssh", "PZ-13900"),
    ("scripts/test_ssh_connection.py", "test_jump_connection", "PZ-13900"),
    ("scripts/test_ssh_connection.py", "test_network_connectivity", "PZ-13900"),
    ("scripts/test_ssh_connection.py", "test_ssh_manager_connection", "PZ-13900"),
    
    # UI tests
    ("scripts/ui/test_login_page_comprehensive.py", "test_ssl_certificate_handling", "PZ-13572"),
    ("scripts/ui/test_login_page_comprehensive.py", "test_page_load_and_structure", "PZ-13572"),
    ("scripts/ui/test_login_page_comprehensive.py", "test_form_validation", "PZ-13572"),
    ("scripts/ui/test_login_page_comprehensive.py", "test_successful_login", "PZ-13572"),
    ("scripts/ui/test_login_page_comprehensive.py", "test_accessibility", "PZ-13572"),
    ("scripts/ui/test_login_page_comprehensive.py", "test_responsive_design", "PZ-13572"),
    ("scripts/ui/test_login_page_comprehensive.py", "test_performance_metrics", "PZ-14090"),
    
    # API Load tests
    ("focus_server_api_load_tests/focus_api_tests/test_api_contract.py", "test_channels_smoke", "PZ-13560"),
    ("focus_server_api_load_tests/focus_api_tests/test_api_contract.py", "test_live_metadata_smoke", "PZ-13561"),
    ("focus_server_api_load_tests/focus_api_tests/test_api_contract.py", "test_configure_waterfall_minimal", "PZ-13557"),
    ("focus_server_api_load_tests/focus_api_tests/test_api_contract.py", "test_configure_non_waterfall_with_freq_and_nfft", "PZ-13873"),
    ("focus_server_api_load_tests/focus_api_tests/test_api_contract.py", "test_recordings_in_time_range", "PZ-13564"),
    ("focus_server_api_load_tests/focus_api_tests/test_api_contract.py", "test_get_recordings_timeline_html", "PZ-13564"),
    ("focus_server_api_load_tests/focus_api_tests/test_api_contract.py", "test_configure_channels_out_of_range_422", "PZ-13554"),
    ("focus_server_api_load_tests/focus_api_tests/test_api_contract.py", "test_configure_waterfall_with_forbidden_fields_422", "PZ-13557"),
    ("focus_server_api_load_tests/focus_api_tests/test_api_contract.py", "test_configure_waterfall_nfft_must_be_1", "PZ-13557"),
    ("focus_server_api_load_tests/focus_api_tests/test_api_contract.py", "test_configure_missing_required_fields_422", "PZ-13878"),
]

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

# Process all matches
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
print(f"Markers skipped (already exist): {skipped_count}")
print(f"Errors: {error_count}")
print()

