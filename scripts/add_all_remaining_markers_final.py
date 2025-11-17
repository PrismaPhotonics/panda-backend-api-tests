"""
Final comprehensive script to add ALL remaining missing Xray markers.
This script will scan all test files and add markers based on function names,
file locations, and existing patterns.
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional

# Base directory
BASE_DIR = Path(__file__).parent.parent
TESTS_DIR = BASE_DIR / "tests"

# Comprehensive mapping based on existing patterns
TEST_ID_MAPPINGS = {
    # Integration API Tests
    "test_health_check": {
        "valid_response": "PZ-14026",
        "invalid_methods": "PZ-14027",
        "concurrent": "PZ-14028",
        "headers": "PZ-14029",
        "security": "PZ-14030",
        "structure": "PZ-14031",
        "ssl": "PZ-14032",
        "load": "PZ-14033",
    },
    "test_waterfall": {
        "waterfall": "PZ-13557",
        "view": "PZ-13238",
    },
    "test_orchestration": {
        "invalid": "PZ-14018",
        "empty": "PZ-14019",
    },
    "test_nfft_overlap": {
        "overlap": "PZ-13558",
        "nfft": "PZ-13873",
    },
    "test_view_type": {
        "invalid_string": "PZ-14094",
        "invalid_range": "PZ-14093",
        "valid": "PZ-13878",
    },
    "test_live_streaming": {
        "stability": "PZ-13800",
    },
    "test_historic_playback_e2e": {
        "e2e": "PZ-13872",
    },
    "test_load": {
        "sustained": "PZ-14801",
        "peak": "PZ-14802",
        "concurrent": "PZ-14800",
        "ramp": "PZ-14803",
        "spike": "PZ-14804",
        "steady": "PZ-14805",
        "recovery": "PZ-14806",
        "exhaustion": "PZ-14807",
    },
    "test_performance": {
        "performance": "PZ-14790",
        "latency": "PZ-14790",
        "response_time": "PZ-14790",
    },
    "test_security": {
        "security": "PZ-13572",
        "authentication": "PZ-13572",
        "csrf": "PZ-13572",
        "rate_limiting": "PZ-13572",
    },
    "test_error": {
        "error": "PZ-13807",
        "network": "PZ-13807",
        "http": "PZ-13807",
    },
    "test_data_quality": {
        "completeness": "PZ-13812",
        "integrity": "PZ-13812",
        "consistency": "PZ-13812",
    },
    "test_infrastructure": {
        "resilience": "PZ-13810",
        "pod": "PZ-13810",
        "recovery": "PZ-13810",
    },
}


def find_test_functions(file_path: Path) -> List[Tuple[int, str]]:
    """Find all test functions in a file."""
    test_functions = []
    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        match = re.match(r'^\s*def\s+(test_\w+)', line)
        if match:
            func_name = match.group(1)
            test_functions.append((i, func_name))
    
    return test_functions


def has_xray_marker(file_path: Path, line_number: int) -> bool:
    """Check if a test function already has an Xray marker."""
    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    for i in range(max(0, line_number - 5), line_number):
        if i < len(lines) and '@pytest.mark.xray' in lines[i]:
            return True
    
    return False


def get_marker_for_test(file_path: Path, func_name: str) -> Optional[str]:
    """Determine the appropriate Jira Test ID for a test function."""
    file_name = file_path.stem
    file_path_str = str(file_path.relative_to(BASE_DIR))
    
    # Try file name patterns
    for pattern, mappings in TEST_ID_MAPPINGS.items():
        if pattern in file_name:
            for func_pattern, test_id in mappings.items():
                if func_pattern in func_name:
                    return test_id
    
    # Try directory-based defaults
    if "integration" in file_path_str:
        if "load" in file_path_str:
            return "PZ-14800"
        elif "performance" in file_path_str:
            return "PZ-14790"
        elif "security" in file_path_str:
            return "PZ-13572"
        elif "error_handling" in file_path_str:
            return "PZ-13807"
        elif "data_quality" in file_path_str:
            return "PZ-13812"
        else:
            return "PZ-13547"
    elif "infrastructure" in file_path_str:
        if "resilience" in file_path_str:
            return "PZ-13810"
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
    
    return None


def add_marker_to_test(file_path: Path, line_number: int, test_id: str) -> bool:
    """Add Xray marker to a test function."""
    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    if has_xray_marker(file_path, line_number):
        return False
    
    func_line_idx = line_number - 1
    insert_idx = func_line_idx
    
    # Find existing decorators
    for i in range(func_line_idx - 1, max(-1, func_line_idx - 10), -1):
        if i >= 0 and lines[i].strip().startswith('@'):
            insert_idx = i + 1
            break
    
    # Get indent
    indent = ''
    if insert_idx < func_line_idx:
        if insert_idx > 0:
            indent = re.match(r'^(\s*)', lines[insert_idx - 1]).group(1) if lines[insert_idx - 1].strip().startswith('@') else ''
    else:
        indent = re.match(r'^(\s*)', lines[func_line_idx]).group(1)
    
    marker_line = f"{indent}@pytest.mark.xray(\"{test_id}\")"
    lines.insert(insert_idx, marker_line)
    
    file_path.write_text('\n'.join(lines), encoding='utf-8')
    return True


def main():
    """Main entry point."""
    print("=" * 80)
    print("Final Comprehensive Missing Markers Addition")
    print("=" * 80)
    print()
    
    test_files = list(TESTS_DIR.rglob("test_*.py"))
    test_files = [f for f in test_files if not f.name.endswith('.backup')]
    
    print(f"Found {len(test_files)} test files")
    print()
    
    total_added = 0
    total_skipped = 0
    total_errors = 0
    
    for test_file in sorted(test_files):
        test_functions = find_test_functions(test_file)
        
        if not test_functions:
            continue
        
        file_added = 0
        file_skipped = 0
        
        for line_num, func_name in test_functions:
            try:
                if has_xray_marker(test_file, line_num):
                    file_skipped += 1
                    continue
                
                test_id = get_marker_for_test(test_file, func_name)
                if test_id:
                    if add_marker_to_test(test_file, line_num, test_id):
                        file_added += 1
                        print(f"  ✅ {test_file.relative_to(BASE_DIR)}:{line_num} - Added {test_id} to {func_name}")
                    else:
                        file_skipped += 1
                else:
                    file_skipped += 1
            except Exception as e:
                total_errors += 1
                print(f"  ❌ Error processing {func_name} in {test_file}: {e}")
        
        if file_added > 0:
            total_added += file_added
            total_skipped += file_skipped
            print(f"  {test_file.relative_to(BASE_DIR)}: Added {file_added}, Skipped {file_skipped}")
    
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

