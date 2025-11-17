"""Phase 2: Add Missing Markers - Intelligent Matching"""
import sys
import re
import csv
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Set, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("="*80)
print("Phase 2: Add Missing Markers - Intelligent Matching")
print("="*80)
print()

# Patterns
xray_pattern = re.compile(r'@pytest\.mark\.xray\(["\']([^"\']+)["\']\)')
jira_pattern = re.compile(r'@pytest\.mark\.jira\(["\']([^"\']+)["\']\)')
test_func_pattern = re.compile(r'def\s+(test_\w+)')

# 1. Load Jira tests
print("="*80)
print("STEP 1: Loading Jira tests")
print("="*80)
print()

jira_tests = {}
csv_file = Path(r"c:\Users\roy.avrahami\Downloads\Jira (28).csv")

if csv_file.exists():
    try:
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                test_key = row.get('Issue key', '')
                if test_key and row.get('Issue Type', '') == 'Test':
                    jira_tests[test_key] = {
                        'key': test_key,
                        'summary': row.get('Summary', ''),
                        'status': row.get('Status', ''),
                        'test_plan': row.get('Custom field (Test plan', ''),
                        'test_type': row.get('Custom field (Test Type)', ''),
                        'description': row.get('Description', ''),
                        'priority': row.get('Priority', ''),
                    }
        print(f"Loaded {len(jira_tests)} tests from Jira CSV")
    except Exception as e:
        print(f"[ERROR] Failed to load CSV: {e}")
        jira_tests = {}
else:
    print(f"[WARNING] CSV file not found: {csv_file}")
    jira_tests = {}

print()

# 2. Find test functions without markers
print("="*80)
print("STEP 2: Finding test functions without markers")
print("="*80)
print()

tests_without_markers = []

# Scan tests/ directory
tests_dir = project_root / "tests"
test_files = list(tests_dir.rglob('test_*.py'))

for test_file in test_files:
    try:
        content = test_file.read_text(encoding='utf-8')
        rel_path = str(test_file.relative_to(project_root))
        
        test_funcs = test_func_pattern.findall(content)
        
        for test_func in test_funcs:
            func_pattern = re.compile(
                rf'def\s+{re.escape(test_func)}.*?(?=def\s+test_|\Z)',
                re.DOTALL
            )
            match = func_pattern.search(content)
            
            if match:
                func_content = match.group(0)
                has_xray = xray_pattern.search(func_content)
                has_jira = jira_pattern.search(func_content)
                
                if not has_xray and not has_jira:
                    # Check if it's a helper function or unit test
                    is_helper = any(keyword in test_func.lower() for keyword in ['summary', 'helper', 'util', 'fixture'])
                    is_unit = 'unit' in rel_path.lower()
                    
                    if not is_helper and not is_unit:
                        # Extract function docstring for matching
                        docstring_match = re.search(r'"""(.*?)"""', func_content, re.DOTALL)
                        docstring = docstring_match.group(1) if docstring_match else ""
                        
                        tests_without_markers.append({
                            'file': rel_path,
                            'function': test_func,
                            'docstring': docstring,
                            'content': func_content
                        })
    except Exception as e:
        print(f"[WARNING] Could not read {test_file}: {e}")

print(f"Found {len(tests_without_markers)} test functions without markers")
print()

# 3. Intelligent matching
print("="*80)
print("STEP 3: Intelligent matching with Jira tests")
print("="*80)
print()

def find_matching_jira_test(test_func_name: str, docstring: str, file_path: str) -> Optional[str]:
    """
    Find matching Jira test ID based on test function name and docstring.
    
    Returns:
        Test ID if match found, None otherwise
    """
    # Create search text
    search_text = f"{test_func_name} {docstring}".lower()
    
    # Keywords mapping
    keywords_map = {
        'required_collections_exist': ['schema', 'collection', 'node4'],
        'recording_schema_validation': ['schema', 'document', 'recordings'],
        'mongodb_indexes_exist': ['index', 'indexes'],
        'recordings_metadata_completeness': ['metadata', 'completeness'],
        'channels': ['channels', 'get /channels'],
        'live_metadata': ['live_metadata', 'live metadata', 'get /live_metadata'],
        'recordings_in_time_range': ['recordings_in_time_range', 'recordings in time range'],
        'singlechannel': ['singlechannel', 'single channel'],
        'historic_playback': ['historic playback', 'historic'],
        'mongodb_outage': ['mongodb outage', 'mongo outage'],
        'rabbitmq_outage': ['rabbitmq outage', 'rabbitmq'],
        'kubernetes': ['kubernetes', 'k8s'],
        'ssh': ['ssh'],
    }
    
    # Try to find matching Jira test
    best_match = None
    best_score = 0
    
    for test_id, test_info in jira_tests.items():
        summary = test_info['summary'].lower()
        description = test_info.get('description', '').lower()
        test_text = f"{summary} {description}"
        
        # Calculate match score
        score = 0
        
        # Check for exact keywords
        for keyword, related_terms in keywords_map.items():
            if keyword in search_text:
                for term in related_terms:
                    if term in test_text:
                        score += 10
                        break
        
        # Check for function name keywords in summary
        func_keywords = test_func_name.replace('test_', '').replace('_', ' ')
        if func_keywords in summary:
            score += 20
        
        # Check for common patterns
        if 'schema' in search_text and 'schema' in test_text:
            score += 15
        if 'metadata' in search_text and 'metadata' in test_text:
            score += 15
        if 'index' in search_text and 'index' in test_text:
            score += 15
        if 'collection' in search_text and 'collection' in test_text:
            score += 15
        
        if score > best_score:
            best_score = score
            best_match = test_id
    
    # Only return if score is high enough
    if best_score >= 20:
        return best_match
    
    return None

# Find matches
matches_found = []
for test_info in tests_without_markers:
    match = find_matching_jira_test(
        test_info['function'],
        test_info['docstring'],
        test_info['file']
    )
    if match:
        matches_found.append({
            'file': test_info['file'],
            'function': test_info['function'],
            'jira_test': match,
            'summary': jira_tests[match]['summary']
        })

print(f"Found {len(matches_found)} potential matches")
print()

# 4. Display matches
print("="*80)
print("STEP 4: Potential Matches")
print("="*80)
print()

print("| # | File | Test Function | Jira Test | Summary |")
print("|---|------|---------------|-----------|---------|")
for i, match in enumerate(matches_found[:50], 1):  # Show first 50
    file_short = match['file'].split('/')[-1] if '/' in match['file'] else match['file']
    summary_short = match['summary'][:50]
    print(f"| {i} | `{file_short}` | `{match['function']}` | {match['jira_test']} | {summary_short} |")

if len(matches_found) > 50:
    print(f"\n... and {len(matches_found) - 50} more matches")
print()

# 5. Generate report
output_dir = Path("docs/04_testing/xray_mapping")
output_dir.mkdir(parents=True, exist_ok=True)
report_file = output_dir / "PHASE2_MARKER_MATCHES.md"

with open(report_file, 'w', encoding='utf-8') as f:
    f.write("# Phase 2: Marker Matches - Intelligent Matching\n\n")
    f.write(f"**Date:** 2025-11-09\n")
    f.write(f"**Total Matches Found:** {len(matches_found)}\n\n")
    f.write("---\n\n")
    
    f.write("## Potential Matches\n\n")
    f.write("| # | File | Test Function | Jira Test | Summary |\n")
    f.write("|---|------|---------------|-----------|---------|\n")
    for i, match in enumerate(matches_found, 1):
        summary_short = match['summary'].replace('|', '\\|')[:60]
        f.write(f"| {i} | `{match['file']}` | `{match['function']}` | {match['jira_test']} | {summary_short} |\n")
    f.write("\n")
    
    f.write("## Next Steps\n\n")
    f.write("1. Review matches manually\n")
    f.write("2. Add markers to confirmed matches\n")
    f.write("3. Create Jira tests for unmatched functions\n")

print(f"Report saved to: {report_file}")
print()

print("="*80)
print("PHASE 2 SUMMARY")
print("="*80)
print()
print(f"Test functions without markers: {len(tests_without_markers)}")
print(f"Potential matches found: {len(matches_found)}")
print(f"Match rate: {len(matches_found) / len(tests_without_markers) * 100:.1f}%")
print()

