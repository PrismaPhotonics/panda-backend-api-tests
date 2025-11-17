"""Phase 4: Analyze Issues - Multiple Markers and Extra Test IDs"""
import sys
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("="*80)
print("Phase 4: Analyze Issues - Multiple Markers and Extra Test IDs")
print("="*80)
print()

# Patterns
xray_pattern = re.compile(r'@pytest\.mark\.xray\(([^)]+)\)')
jira_pattern = re.compile(r'@pytest\.mark\.jira\(([^)]+)\)')

def find_test_files() -> List[Path]:
    """Find all test files in the project."""
    test_files = []
    tests_dir = project_root / "tests"
    
    if tests_dir.exists():
        test_files.extend(tests_dir.rglob("test_*.py"))
    
    # Also check scripts directory for test files
    scripts_dir = project_root / "scripts"
    if scripts_dir.exists():
        test_files.extend(scripts_dir.rglob("test_*.py"))
    
    return test_files

def scan_for_multiple_markers(test_files: List[Path]) -> Dict[str, List[Tuple[Path, str, List[str]]]]:
    """Scan test files for functions with multiple Xray markers."""
    multiple_markers = {}
    
    for test_file in test_files:
        try:
            content = test_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Find all test functions
            func_pattern = re.compile(r'def\s+(test_\w+)')
            
            for i, line in enumerate(lines):
                # Check if this is a test function
                func_match = func_pattern.search(line)
                if func_match:
                    func_name = func_match.group(1)
                    
                    # Look backwards for markers
                    markers = []
                    j = i - 1
                    while j >= 0 and (lines[j].strip().startswith('@') or lines[j].strip() == ''):
                        if lines[j].strip().startswith('@pytest.mark.xray'):
                            # Extract marker content
                            marker_match = xray_pattern.search(lines[j])
                            if marker_match:
                                marker_content = marker_match.group(1)
                                # Parse multiple test IDs
                                test_ids = [tid.strip().strip('"\'') for tid in marker_content.split(',')]
                                markers.extend(test_ids)
                        j -= 1
                    
                    # Check if function has multiple markers
                    if len(markers) > 1:
                        if func_name not in multiple_markers:
                            multiple_markers[func_name] = []
                        multiple_markers[func_name].append((test_file, func_name, markers))
        
        except Exception as e:
            print(f"[WARNING] Could not read {test_file}: {e}")
    
    return multiple_markers

def scan_for_test_id(test_id: str, test_files: List[Path]) -> List[Tuple[Path, str]]:
    """Scan for a specific test ID."""
    found = []
    
    for test_file in test_files:
        try:
            content = test_file.read_text(encoding='utf-8')
            
            # Find all Xray markers
            for match in xray_pattern.finditer(content):
                marker_content = match.group(1)
                test_ids = [tid.strip().strip('"\'') for tid in marker_content.split(',')]
                
                if test_id in test_ids:
                    # Find function name
                    func_pattern = re.compile(r'def\s+(test_\w+)')
                    lines = content.split('\n')
                    marker_line = content[:match.start()].count('\n')
                    
                    # Find next function after marker
                    for i in range(marker_line, min(marker_line + 20, len(lines))):
                        func_match = func_pattern.search(lines[i])
                        if func_match:
                            found.append((test_file, func_match.group(1)))
                            break
        
        except Exception as e:
            pass
    
    return found

# Find test files
print("="*80)
print("Scanning for multiple markers...")
print("="*80)
print()

test_files = find_test_files()
print(f"Found {len(test_files)} test files")
print()

# Scan for multiple markers
multiple_markers = scan_for_multiple_markers(test_files)

print("="*80)
print("Functions with Multiple Xray Markers")
print("="*80)
print()

if multiple_markers:
    for func_name, occurrences in multiple_markers.items():
        print(f"[MULTIPLE MARKERS] {func_name}:")
        for file_path, func, markers in occurrences:
            print(f"  -> {file_path.relative_to(project_root)}")
            print(f"     Markers: {', '.join(markers)}")
            print(f"     Count: {len(markers)}")
        print()
else:
    print("No functions with multiple markers found (this is expected - multiple markers in one decorator are OK)")
    print()

# Check for PZ-13768
print("="*80)
print("Checking for PZ-13768 (Extra Test ID)")
print("="*80)
print()

pz_13768_found = scan_for_test_id("PZ-13768", test_files)

if pz_13768_found:
    print(f"[FOUND] PZ-13768 found in {len(pz_13768_found)} location(s):")
    for file_path, func_name in pz_13768_found:
        print(f"  -> {file_path.relative_to(project_root)}::{func_name}")
    print()
else:
    print("[NOT FOUND] PZ-13768 not found in automation")
    print()

# Check for PZ-14088 (mentioned in work plan)
print("="*80)
print("Checking for PZ-14088 (Duplicate Marker Case)")
print("="*80)
print()

pz_14088_found = scan_for_test_id("PZ-14088", test_files)

if pz_14088_found:
    print(f"[FOUND] PZ-14088 found in {len(pz_14088_found)} location(s):")
    for file_path, func_name in pz_14088_found:
        print(f"  -> {file_path.relative_to(project_root)}::{func_name}")
    print()
else:
    print("[NOT FOUND] PZ-14088 not found in automation")
    print()

print("="*80)
print("SUMMARY")
print("="*80)
print()
print(f"Functions with multiple markers: {len(multiple_markers)}")
print(f"PZ-13768 found: {len(pz_13768_found)} location(s)")
print(f"PZ-14088 found: {len(pz_14088_found)} location(s)")
print()

