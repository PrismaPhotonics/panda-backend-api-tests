"""Phase 2: Add Missing Markers - Load, Performance, Security Tests"""
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("="*80)
print("Phase 2: Add Missing Markers - Load, Performance, Security Tests")
print("="*80)
print()

# Load, Performance, Security tests that need markers
# Based on actual test files and TEST_PLAN_PZ14024_DETAILED_REPORT.md
LOAD_PERFORMANCE_SECURITY_MAPPING = [
    # Load Tests
    ("tests/load/test_job_capacity_limits.py", "test_single_job_baseline", "PZ-14088"),
    ("tests/load/test_job_capacity_limits.py", "test_linear_load_progression", "PZ-14088"),
    ("tests/load/test_job_capacity_limits.py", "test_200_concurrent_jobs_target_capacity", "PZ-14088"),
    
    # Performance Tests
    ("tests/performance/test_mongodb_outage_resilience.py", "test_mongodb_scale_down_outage_returns_503_no_orchestration", "PZ-13603"),
    ("tests/performance/test_mongodb_outage_resilience.py", "test_mongodb_network_block_outage_returns_503_no_orchestration", "PZ-13603"),
    ("tests/performance/test_mongodb_outage_resilience.py", "test_mongodb_outage_no_live_impact", "PZ-13603"),
    ("tests/performance/test_mongodb_outage_resilience.py", "test_mongodb_outage_logging_and_metrics", "PZ-13603"),
    ("tests/performance/test_mongodb_outage_resilience.py", "test_mongodb_outage_cleanup_and_restore", "PZ-13603"),
    
    # Security Tests
    ("tests/security/test_malformed_input_handling.py", "test_robustness_to_malformed_inputs", "PZ-13572"),
    
    # Stress Tests
    ("tests/stress/test_extreme_configurations.py", "test_configuration_with_extreme_values", "PZ-13880"),
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
print("Adding markers to load, performance, security tests")
print("="*80)
print()

added_count = 0
skipped_count = 0
error_count = 0

for file_path_str, function_name, test_id in LOAD_PERFORMANCE_SECURITY_MAPPING:
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

