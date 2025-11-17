"""Create detailed breakdowns for work plan"""
import sys
import re
import csv
from pathlib import Path
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("="*80)
print("Creating Detailed Breakdowns for Work Plan")
print("="*80)
print()

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

print()

# 2. Load automation markers
print("="*80)
print("STEP 2: Loading automation markers")
print("="*80)
print()

tests_dir = project_root / "tests"
automation_markers = defaultdict(list)

xray_pattern = re.compile(r'@pytest\.mark\.xray\(["\']([^"\']+)["\']\)')
jira_pattern = re.compile(r'@pytest\.mark\.jira\(["\']([^"\']+)["\']\)')

test_files = list(tests_dir.rglob('test_*.py'))

for test_file in test_files:
    try:
        content = test_file.read_text(encoding='utf-8')
        rel_path = str(test_file.relative_to(project_root))
        
        for line_num, line in enumerate(content.splitlines(), 1):
            xray_matches = xray_pattern.findall(line)
            for match in xray_matches:
                test_ids = [tid.strip() for tid in match.split(',')]
                for test_id in test_ids:
                    if test_id.startswith('PZ-'):
                        automation_markers[test_id].append((rel_path, line_num))
            
            jira_matches = jira_pattern.findall(line)
            for match in jira_matches:
                test_ids = [tid.strip() for tid in match.split(',')]
                for test_id in test_ids:
                    if test_id.startswith('PZ-'):
                        automation_markers[test_id].append((rel_path, line_num))
    except Exception as e:
        print(f"[WARNING] Could not read {test_file}: {e}")

print(f"Found {len(automation_markers)} unique test IDs in automation")
print()

# 3. Find missing tests
print("="*80)
print("STEP 3: Finding missing tests")
print("="*80)
print()

if jira_tests:
    jira_test_ids = set(jira_tests.keys())
    automation_test_ids = set(automation_markers.keys())
    missing_in_automation = jira_test_ids - automation_test_ids
    
    print(f"Tests in Jira: {len(jira_test_ids)}")
    print(f"Tests in automation: {len(automation_test_ids)}")
    print(f"Tests missing in automation: {len(missing_in_automation)}")
    print()
    
    # Categorize missing tests
    missing_by_category = defaultdict(list)
    
    for test_id in missing_in_automation:
        test = jira_tests[test_id]
        summary = test['summary'].lower()
        
        if 'api' in summary or 'endpoint' in summary or '/config' in summary or '/metadata' in summary or '/waterfall' in summary or '/channels' in summary:
            category = 'API'
        elif 'integration' in summary:
            category = 'Integration'
        elif 'infrastructure' in summary or 'pod' in summary or 'mongodb' in summary or 'rabbitmq' in summary:
            category = 'Infrastructure'
        elif 'data quality' in summary or 'schema' in summary or 'metadata' in summary:
            category = 'Data Quality'
        elif 'performance' in summary or 'latency' in summary or 'load' in summary:
            category = 'Performance/Load'
        elif 'security' in summary or 'malformed' in summary:
            category = 'Security'
        elif 'calculation' in summary or 'frequency' in summary or 'nyquist' in summary:
            category = 'Calculations'
        elif 'health' in summary or 'check' in summary:
            category = 'Health Check'
        else:
            category = 'Other'
        
        missing_by_category[category].append((test_id, test))
    
    print("Missing tests by category:")
    for category, tests in sorted(missing_by_category.items()):
        print(f"  {category}: {len(tests)} tests")
    print()
    
    # 4. Generate detailed breakdown
    output_dir = Path("docs/04_testing/xray_mapping")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    breakdown_file = output_dir / "MISSING_TESTS_DETAILED_BREAKDOWN.md"
    
    with open(breakdown_file, 'w', encoding='utf-8') as f:
        f.write("# Missing Tests in Automation - Detailed Breakdown\n\n")
        f.write(f"**Total Missing:** {len(missing_in_automation)} tests\n\n")
        f.write("---\n\n")
        
        for category, tests in sorted(missing_by_category.items()):
            f.write(f"## {category} Tests ({len(tests)} tests)\n\n")
            f.write("| # | Test ID | Summary | Status | Priority | Test Type |\n")
            f.write("|---|---------|---------|--------|----------|-----------|\n")
            
            for i, (test_id, test) in enumerate(tests, 1):
                summary = test['summary'].replace('|', '\\|')[:60]
                status = test['status']
                priority = test.get('priority', 'N/A')
                test_type = test.get('test_type', 'N/A')
                f.write(f"| {i} | {test_id} | {summary} | {status} | {priority} | {test_type} |\n")
            
            f.write("\n")
    
    print(f"Detailed breakdown saved to: {breakdown_file}")
    
    # 5. Generate test functions without markers breakdown
    print()
    print("="*80)
    print("STEP 4: Analyzing test functions without markers")
    print("="*80)
    print()
    
    # Load test functions without markers
    tests_without_markers_by_category = defaultdict(list)
    test_func_pattern = re.compile(r'def\s+(test_\w+)')
    
    for test_file in test_files:
        try:
            content = test_file.read_text(encoding='utf-8')
            rel_path = str(test_file.relative_to(project_root))
            
            # Determine category
            if 'unit' in rel_path.lower():
                category = 'Unit'
            elif 'integration' in rel_path.lower():
                category = 'Integration'
            elif 'infrastructure' in rel_path.lower():
                category = 'Infrastructure'
            elif 'data_quality' in rel_path.lower():
                category = 'Data Quality'
            elif 'security' in rel_path.lower():
                category = 'Security'
            elif 'performance' in rel_path.lower():
                category = 'Performance'
            elif 'load' in rel_path.lower():
                category = 'Load'
            else:
                category = 'Other'
            
            # Find test functions
            test_funcs = test_func_pattern.findall(content)
            
            for test_func in test_funcs:
                # Check if function has markers
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
                        # Check if it's a helper function
                        is_helper = any(keyword in test_func.lower() for keyword in ['summary', 'helper', 'util', 'fixture'])
                        
                        if not is_helper and category != 'Unit':
                            tests_without_markers_by_category[category].append((rel_path, test_func))
        except Exception as e:
            print(f"[WARNING] Could not read {test_file}: {e}")
    
    # Generate breakdown
    functions_breakdown_file = output_dir / "TEST_FUNCTIONS_WITHOUT_MARKERS_BREAKDOWN.md"
    
    with open(functions_breakdown_file, 'w', encoding='utf-8') as f:
        f.write("# Test Functions Without Markers - Detailed Breakdown\n\n")
        f.write("**Note:** Excludes unit tests and helper functions\n\n")
        f.write("---\n\n")
        
        total = 0
        for category, tests in sorted(tests_without_markers_by_category.items()):
            total += len(tests)
            f.write(f"## {category} Tests ({len(tests)} functions)\n\n")
            f.write("| # | File | Test Function |\n")
            f.write("|---|------|---------------|\n")
            
            for i, (file_path, test_func) in enumerate(tests, 1):
                f.write(f"| {i} | `{file_path}` | `{test_func}` |\n")
            
            f.write("\n")
        
        f.write(f"**Total:** {total} test functions need markers\n\n")
    
    print(f"Test functions breakdown saved to: {functions_breakdown_file}")
    print()
    print("Summary by category:")
    for category, tests in sorted(tests_without_markers_by_category.items()):
        print(f"  {category}: {len(tests)} functions")

print()
print("="*80)
print("Breakdowns created successfully!")
print("="*80)

