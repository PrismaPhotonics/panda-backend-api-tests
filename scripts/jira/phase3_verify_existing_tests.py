"""Phase 3: Verify Existing Tests Before Creating New Ones"""
import sys
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("="*80)
print("Phase 3: Verify Existing Tests Before Creating New Ones")
print("="*80)
print()

# Missing tests from MISSING_TESTS_DETAILED_BREAKDOWN.md
MISSING_TESTS = {
    # API Tests (22)
    "PZ-13762": "API – GET /channels – Returns System Channel Bounds",
    "PZ-13552": "API – Invalid time range (negative)",
    "PZ-13561": "API – GET /live_metadata present",
    "PZ-14101": "Integration - Historic Playback - Short Duration (Rapid Window)",
    "PZ-13761": "API – POST /config/{task_id} – Invalid Frequency Range Rejection",
    "PZ-13821": "API – SingleChannel Rejects Invalid Display Height",
    "PZ-13766": "API – POST /recordings_in_time_range – Returns Recording Windows",
    "PZ-13764": "API – GET /live_metadata – Returns Metadata When Available",
    "PZ-13815": "API – SingleChannel View for Channel 100 (Upper Boundary Test)",
    "PZ-13759": "API – POST /config/{task_id} – Invalid Time Range Rejection",
    "PZ-13895": "Integration – GET /channels - Enabled Channels List",
    "PZ-13560": "API – GET /channels",
    "PZ-13823": "API – SingleChannel Rejects When min ≠ max",
    "PZ-13819": "API – SingleChannel View with Various Frequency Ranges",
    "PZ-13548": "API – Historical configure (happy path)",
    "PZ-13765": "API – GET /live_metadata – Returns 404 When Unavailable",
    "PZ-13554": "API – Invalid channels (negative)",
    "PZ-13814": "API – SingleChannel View for Channel 1 (First Channel)",
    "PZ-13562": "API – GET /live_metadata missing",
    "PZ-13555": "API – Invalid frequency range (negative)",
    "PZ-13760": "API – POST /config/{task_id} – Invalid Channel Range Rejection",
    "PZ-13564": "API – POST /recordings_in_time_range",
    
    # Data Quality Tests (4)
    "PZ-13684": "Data Quality – node4 Schema Validation",
    "PZ-13811": "Data Quality – Validate Recordings Document Schema",
    "PZ-13812": "Data Quality – Verify Recordings Have Complete Metadata",
    "PZ-13685": "Data Quality – Recordings Metadata Completeness",
    
    # Integration Tests (16)
    "PZ-13832": "Integration - SingleChannel Edge Case - Minimum Channel (Channel 0)",
    "PZ-13603": "Integration – Mongo outage on History configure",
    "PZ-13863": "Integration – Historic Playback - Standard 5-Minute Range",
    "PZ-13865": "Integration – Historic Playback - Short Duration (1 Minute)",
    "PZ-13767": "Integration – MongoDB Outage Handling",
    "PZ-13877": "Integration – Invalid Frequency Range - Min > Max",
    "PZ-13836": "Integration - SingleChannel with Invalid Channel (Negative)",
    "PZ-13833": "Integration - SingleChannel Edge Case - Maximum Channel (Last Available)",
    "PZ-13854": "Integration - SingleChannel Frequency Range Validation",
    "PZ-13604": "Integration – Orchestrator error triggers rollback",
    "PZ-13852": "Integration - SingleChannel with Min > Max (Validation Error)",
    "PZ-13837": "Integration - SingleChannel with Invalid Channel (Negative)",
    "PZ-13855": "Integration - SingleChannel Canvas Height Validation",
    "PZ-13835": "Integration - SingleChannel with Invalid Channel (Out of Range)",
    "PZ-13873": "integration - Valid Configuration - All Parameters",
    "PZ-13903": "Integration - Frequency Range Nyquist Limit Enforcement",
    
    # Security Tests (2)
    "PZ-13769": "Security – Malformed Input Handling",
    "PZ-13572": "Security – Robustness to malformed inputs",
}

# Patterns
xray_pattern = re.compile(r'@pytest\.mark\.xray\(["\']([^"\']+)["\']\)')
jira_pattern = re.compile(r'@pytest\.mark\.jira\(["\']([^"\']+)["\']\)')

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

def scan_for_test_ids(test_files: List[Path]) -> Dict[str, List[Tuple[Path, str]]]:
    """Scan test files for Xray/Jira markers."""
    found_tests = {}
    
    for test_file in test_files:
        try:
            content = test_file.read_text(encoding='utf-8')
            
            # Find all Xray markers
            for match in xray_pattern.finditer(content):
                test_id = match.group(1)
                # Handle multiple test IDs in one marker
                test_ids = [tid.strip().strip('"\'') for tid in test_id.split(',')]
                for tid in test_ids:
                    if tid not in found_tests:
                        found_tests[tid] = []
                    found_tests[tid].append((test_file, "xray"))
            
            # Find all Jira markers
            for match in jira_pattern.finditer(content):
                test_id = match.group(1)
                # Handle multiple test IDs in one marker
                test_ids = [tid.strip().strip('"\'') for tid in test_id.split(',')]
                for tid in test_ids:
                    if tid not in found_tests:
                        found_tests[tid] = []
                    found_tests[tid].append((test_file, "jira"))
        
        except Exception as e:
            print(f"[WARNING] Could not read {test_file}: {e}")
    
    return found_tests

def find_similar_test_functions(test_id: str, description: str) -> List[Tuple[Path, str]]:
    """Find test functions that might cover this test case."""
    test_files = find_test_files()
    similar = []
    
    # Extract keywords from description
    keywords = []
    if "GET /channels" in description or "channels" in description.lower():
        keywords.extend(["channel", "channels"])
    if "live_metadata" in description.lower() or "live metadata" in description.lower():
        keywords.extend(["live_metadata", "live_metadata", "live metadata"])
    if "recordings_in_time_range" in description.lower() or "recordings in time range" in description.lower():
        keywords.extend(["recordings_in_time_range", "recordings", "time_range"])
    if "singlechannel" in description.lower() or "single channel" in description.lower():
        keywords.extend(["singlechannel", "single_channel"])
    if "historic" in description.lower() or "history" in description.lower():
        keywords.extend(["historic", "history", "playback"])
    if "mongodb" in description.lower() or "mongo" in description.lower():
        keywords.extend(["mongodb", "mongo"])
    if "outage" in description.lower():
        keywords.extend(["outage", "resilience"])
    if "orchestrator" in description.lower() or "orchestration" in description.lower():
        keywords.extend(["orchestrator", "orchestration"])
    if "malformed" in description.lower() or "input" in description.lower():
        keywords.extend(["malformed", "input", "validation"])
    if "schema" in description.lower():
        keywords.extend(["schema", "validation"])
    if "metadata" in description.lower():
        keywords.extend(["metadata"])
    
    for test_file in test_files:
        try:
            content = test_file.read_text(encoding='utf-8')
            
            # Check if file contains keywords
            content_lower = content.lower()
            if any(keyword.lower() in content_lower for keyword in keywords):
                # Find test functions in this file
                func_pattern = re.compile(r'def\s+(test_\w+)', re.MULTILINE)
                for match in func_pattern.finditer(content):
                    func_name = match.group(1)
                    similar.append((test_file, func_name))
        
        except Exception as e:
            pass
    
    return similar

# Scan for existing test IDs
print("="*80)
print("Scanning for existing test IDs...")
print("="*80)
print()

test_files = find_test_files()
print(f"Found {len(test_files)} test files")
print()

found_tests = scan_for_test_ids(test_files)

# Check each missing test
print("="*80)
print("Checking missing tests...")
print("="*80)
print()

found_count = 0
not_found_count = 0
similar_count = 0

for test_id, description in MISSING_TESTS.items():
    # Encode description to avoid Unicode errors
    safe_desc = description.encode('ascii', 'ignore').decode('ascii')
    
    if test_id in found_tests:
        found_count += 1
        print(f"[FOUND] {test_id}: {safe_desc}")
        for file_path, marker_type in found_tests[test_id]:
            print(f"  -> {file_path.relative_to(project_root)} ({marker_type})")
    else:
        # Check for similar test functions
        similar = find_similar_test_functions(test_id, description)
        if similar:
            similar_count += 1
            print(f"[SIMILAR] {test_id}: {safe_desc}")
            for file_path, func_name in similar[:3]:  # Show first 3
                print(f"  -> {file_path.relative_to(project_root)}::{func_name}")
        else:
            not_found_count += 1
            print(f"[NOT FOUND] {test_id}: {safe_desc}")

print()
print("="*80)
print("SUMMARY")
print("="*80)
print()
print(f"Total missing tests: {len(MISSING_TESTS)}")
print(f"Found (with markers): {found_count}")
print(f"Similar functions found: {similar_count}")
print(f"Not found (need to create): {not_found_count}")
print()

