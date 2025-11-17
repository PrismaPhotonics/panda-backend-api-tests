"""
Comprehensive script to add missing Xray markers to all test functions.
This script will scan all test files and add markers based on test function names,
file locations, and existing patterns.
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional

# Base directory
BASE_DIR = Path(__file__).parent.parent
TESTS_DIR = BASE_DIR / "tests"

# Mapping of test function patterns to Jira Test IDs
# This is based on existing patterns and file locations
TEST_ID_MAPPINGS = {
    # Integration API Tests
    "test_config_validation": {
        "missing_channels": "PZ-14099",
        "missing_frequency": "PZ-14098",
        "missing_nfft": "PZ-14097",
        "missing_display": "PZ-14095",
        "invalid_canvas": "PZ-13878",
        "invalid_frequency_range": "PZ-13877",
        "invalid_channel_range": "PZ-13876",
        "valid_configuration": "PZ-13873",
        "live_mode": "PZ-13548",
        "historic_mode": "PZ-13548",
        "nfft": "PZ-13873",
        "frequency": "PZ-13877",
        "channel": "PZ-13876",
    },
    "test_prelaunch": {
        "port_availability": "PZ-14018",
        "data_availability": "PZ-13547",
        "time_range": "PZ-13552",
        "channels_out_of_range": "PZ-13876",
        "frequency_exceeds": "PZ-13877",
        "invalid_nfft": "PZ-13873",
        "invalid_view_type": "PZ-13878",
        "error_messages": "PZ-13878",
    },
    "test_api_endpoints": {
        "get_channels": "PZ-13762",
        "get_live_metadata": "PZ-13764",
        "post_recordings": "PZ-13766",
        "invalid_time_range": "PZ-13759",
        "invalid_channel_range": "PZ-13760",
        "invalid_frequency_range": "PZ-13761",
    },
    "test_configure": {
        "valid_configuration": "PZ-13547",
        "missing_required": "PZ-13879",
        "response_time": "PZ-14790",
    },
    "test_config_task": {
        "valid_configuration": "PZ-13547",
        "invalid_task_id": "PZ-13879",
        "missing_required": "PZ-13879",
    },
    "test_task_metadata": {
        "get_task_metadata": "PZ-13561",
        "task_not_found": "PZ-13562",
    },
    "test_waterfall": {
        "waterfall": "PZ-13238",
    },
    "test_dynamic_roi": {
        "roi": "PZ-13556",
    },
    "test_historic_playback": {
        "historic": "PZ-13548",
        "time_range": "PZ-13552",
    },
    "test_live_monitoring": {
        "live": "PZ-13548",
        "sensors": "PZ-13560",
        "metadata": "PZ-13561",
    },
    "test_singlechannel": {
        "singlechannel": "PZ-13669",
    },
    "test_nfft": {
        "nfft": "PZ-13873",
        "frequency": "PZ-13877",
    },
    "test_view_type": {
        "view_type": "PZ-13878",
    },
    "test_orchestration": {
        "orchestration": "PZ-14018",
    },
    "test_health_check": {
        "health": "PZ-13807",
    },
    
    # Infrastructure Tests
    "test_basic_connectivity": {
        "connectivity": "PZ-13807",
        "kubernetes": "PZ-13807",
        "focus_server": "PZ-13807",
    },
    "test_external_connectivity": {
        "mongodb": "PZ-13807",
        "rabbitmq": "PZ-13768",
        "external": "PZ-13807",
    },
    "test_mongodb": {
        "mongodb": "PZ-13807",
        "connection": "PZ-13807",
        "recovery": "PZ-13810",
        "outage": "PZ-13603",
    },
    "test_rabbitmq": {
        "rabbitmq": "PZ-13768",
        "connection": "PZ-13768",
    },
    "test_pz_integration": {
        "pz": "PZ-13807",
        "integration": "PZ-13807",
    },
    "test_system_behavior": {
        "clean_startup": "PZ-13807",
        "stability": "PZ-13807",
        "error": "PZ-13807",
        "rollback": "PZ-14018",
    },
    "test_k8s": {
        "k8s": "PZ-13807",
        "job": "PZ-14018",
        "lifecycle": "PZ-14018",
    },
    "test_mongodb_monitoring": {
        "monitoring": "PZ-13810",
        "agent": "PZ-13810",
    },
    
    # Data Quality Tests
    "test_mongodb_data_quality": {
        "required_collections": "PZ-13811",
        "recording_schema": "PZ-13811",
        "recordings_have": "PZ-13812",
        "indexes": "PZ-13811",
        "deleted": "PZ-13811",
    },
    "test_mongodb_indexes": {
        "indexes": "PZ-13811",
        "schema": "PZ-13811",
    },
    "test_mongodb_schema": {
        "schema": "PZ-13811",
    },
    "test_mongodb_recovery": {
        "recovery": "PZ-13810",
    },
    
    # Performance Tests
    "test_mongodb_outage": {
        "outage": "PZ-13603",
        "resilience": "PZ-13603",
    },
    "test_performance": {
        "performance": "PZ-14790",
        "response_time": "PZ-14790",
        "latency": "PZ-14790",
    },
    
    # Load Tests
    "test_job_capacity": {
        "capacity": "PZ-13986",
        "concurrent": "PZ-13986",
    },
    "test_load": {
        "load": "PZ-13986",
        "peak": "PZ-13986",
        "sustained": "PZ-13986",
    },
    
    # Security Tests
    "test_malformed_input": {
        "malformed": "PZ-13572",
        "input": "PZ-13572",
    },
    "test_security": {
        "security": "PZ-13572",
        "authentication": "PZ-13572",
        "csrf": "PZ-13572",
        "rate_limiting": "PZ-13572",
    },
    
    # Error Handling Tests
    "test_error": {
        "error": "PZ-13807",
        "network": "PZ-13807",
        "http": "PZ-13807",
    },
    
    # E2E Tests
    "test_e2e": {
        "e2e": "PZ-13547",
        "flow": "PZ-13547",
    },
}

# Default markers for categories
DEFAULT_MARKERS = {
    "integration": "PZ-13547",
    "infrastructure": "PZ-13807",
    "data_quality": "PZ-13811",
    "performance": "PZ-14790",
    "load": "PZ-13986",
    "security": "PZ-13572",
    "error_handling": "PZ-13807",
}


def find_test_functions(file_path: Path) -> List[Tuple[int, str, str]]:
    """
    Find all test functions in a file.
    Returns list of (line_number, function_name, function_signature)
    """
    test_functions = []
    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Match test function definitions
        match = re.match(r'^\s*def\s+(test_\w+)', line)
        if match:
            func_name = match.group(1)
            # Get full signature (may span multiple lines)
            signature = line.strip()
            if i < len(lines):
                # Check if signature continues on next line
                j = i
                while j < len(lines) and lines[j].strip().endswith('\\'):
                    j += 1
                    if j < len(lines):
                        signature += ' ' + lines[j].strip()
            test_functions.append((i, func_name, signature))
    
    return test_functions


def has_xray_marker(file_path: Path, line_number: int) -> bool:
    """
    Check if a test function already has an Xray marker.
    """
    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    # Check lines before the function definition
    for i in range(max(0, line_number - 5), line_number):
        if i < len(lines):
            line = lines[i]
            if '@pytest.mark.xray' in line:
                return True
    
    return False


def get_marker_for_test(file_path: Path, func_name: str) -> Optional[str]:
    """
    Determine the appropriate Jira Test ID for a test function.
    """
    file_name = file_path.stem
    file_path_str = str(file_path.relative_to(BASE_DIR))
    
    # Try to match file name patterns
    for pattern, mappings in TEST_ID_MAPPINGS.items():
        if pattern in file_name:
            # Try to match function name patterns
            for func_pattern, test_id in mappings.items():
                if func_pattern in func_name:
                    return test_id
    
    # Try to match based on directory
    if "integration" in file_path_str:
        if "api" in file_path_str:
            if "config" in file_name:
                return "PZ-13873"
            elif "prelaunch" in file_name:
                return "PZ-14018"
            elif "historic" in file_name:
                return "PZ-13548"
            elif "live" in file_name:
                return "PZ-13548"
            else:
                return "PZ-13547"
        else:
            return "PZ-13547"
    elif "infrastructure" in file_path_str:
        if "mongodb" in file_name:
            return "PZ-13807"
        elif "rabbitmq" in file_name:
            return "PZ-13768"
        elif "k8s" in file_name:
            return "PZ-13807"
        else:
            return "PZ-13807"
    elif "data_quality" in file_path_str:
        return "PZ-13811"
    elif "performance" in file_path_str:
        return "PZ-14790"
    elif "load" in file_path_str:
        return "PZ-13986"
    elif "security" in file_path_str:
        return "PZ-13572"
    elif "error_handling" in file_path_str:
        return "PZ-13807"
    
    # Default fallback
    return None


def add_marker_to_test(file_path: Path, line_number: int, test_id: str) -> bool:
    """
    Add Xray marker to a test function.
    Returns True if marker was added, False if already exists.
    """
    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    # Check if marker already exists
    if has_xray_marker(file_path, line_number):
        return False
    
    # Find the function definition line
    func_line_idx = line_number - 1
    
    # Find where to insert the marker (before decorators or function definition)
    insert_idx = func_line_idx
    
    # Look for existing decorators
    for i in range(func_line_idx - 1, max(-1, func_line_idx - 10), -1):
        if i >= 0 and lines[i].strip().startswith('@'):
            insert_idx = i + 1
            break
    
    # Insert the marker
    indent = ''
    if insert_idx < func_line_idx:
        # Use same indent as existing decorators
        if insert_idx > 0:
            indent = re.match(r'^(\s*)', lines[insert_idx - 1]).group(1) if lines[insert_idx - 1].strip().startswith('@') else ''
    else:
        # Use indent from function definition
        indent = re.match(r'^(\s*)', lines[func_line_idx]).group(1)
    
    marker_line = f"{indent}@pytest.mark.xray(\"{test_id}\")"
    lines.insert(insert_idx, marker_line)
    
    # Write back to file
    file_path.write_text('\n'.join(lines), encoding='utf-8')
    return True


def process_test_file(file_path: Path) -> Tuple[int, int, int]:
    """
    Process a single test file and add missing markers.
    Returns (added, skipped, errors)
    """
    added = 0
    skipped = 0
    errors = 0
    
    try:
        test_functions = find_test_functions(file_path)
        
        for line_num, func_name, signature in test_functions:
            try:
                # Skip helper functions and fixtures
                if func_name.startswith('test_') and 'fixture' not in signature.lower():
                    if has_xray_marker(file_path, line_num):
                        skipped += 1
                    else:
                        test_id = get_marker_for_test(file_path, func_name)
                        if test_id:
                            if add_marker_to_test(file_path, line_num, test_id):
                                added += 1
                                print(f"  ✅ Added marker {test_id} to {func_name}")
                            else:
                                skipped += 1
                        else:
                            # No marker found, but still count as processed
                            skipped += 1
            except Exception as e:
                errors += 1
                print(f"  ❌ Error processing {func_name}: {e}")
    
    except Exception as e:
        errors += 1
        print(f"  ❌ Error processing file {file_path}: {e}")
    
    return added, skipped, errors


def main():
    """Main entry point."""
    print("=" * 80)
    print("Comprehensive Missing Markers Addition Script")
    print("=" * 80)
    print()
    
    # Find all test files
    test_files = list(TESTS_DIR.rglob("test_*.py"))
    
    print(f"Found {len(test_files)} test files")
    print()
    
    total_added = 0
    total_skipped = 0
    total_errors = 0
    
    for test_file in sorted(test_files):
        # Skip backup files
        if test_file.name.endswith('.backup'):
            continue
        
        print(f"Processing: {test_file.relative_to(BASE_DIR)}")
        added, skipped, errors = process_test_file(test_file)
        
        total_added += added
        total_skipped += skipped
        total_errors += errors
        
        if added > 0 or skipped > 0 or errors > 0:
            print(f"  Added: {added}, Skipped: {skipped}, Errors: {errors}")
        print()
    
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Markers added: {total_added}")
    print(f"Markers skipped (already exist): {total_skipped}")
    print(f"Errors: {total_errors}")
    print()


if __name__ == '__main__':
    main()

