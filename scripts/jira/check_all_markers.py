"""
Check All Markers in Automation Code
=====================================

Script to check all Xray/Jira markers in automation code and compare with Jira tests.
"""

import re
import sys
from pathlib import Path
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def find_all_markers():
    """Find all Xray/Jira markers in automation code."""
    markers = defaultdict(list)
    test_files = []
    
    # Find all Python test files
    for test_file in Path('tests').rglob('*.py'):
        if test_file.name.startswith('test_') or 'conftest' in test_file.name:
            test_files.append(test_file)
    
    print(f"Scanning {len(test_files)} test files...\n")
    
    for test_file in test_files:
        try:
            content = test_file.read_text(encoding='utf-8')
            
            # Find all @pytest.mark.xray("PZ-XXXXX") patterns
            xray_matches = re.findall(r'@pytest\.mark\.xray\(["\']([^"\']+)["\']\)', content)
            for match in xray_matches:
                # Handle multiple IDs in one marker: "PZ-1234", "PZ-5678"
                test_ids = [tid.strip() for tid in match.split(',')]
                for test_id in test_ids:
                    if test_id.startswith('PZ-'):
                        markers[test_id].append({
                            'file': str(test_file),
                            'type': 'xray',
                            'line': 'unknown'
                        })
            
            # Find all @pytest.mark.jira("PZ-XXXXX") patterns
            jira_matches = re.findall(r'@pytest\.mark\.jira\(["\']([^"\']+)["\']\)', content)
            for match in jira_matches:
                test_ids = [tid.strip() for tid in match.split(',')]
                for test_id in test_ids:
                    if test_id.startswith('PZ-'):
                        markers[test_id].append({
                            'file': str(test_file),
                            'type': 'jira',
                            'line': 'unknown'
                        })
            
        except Exception as e:
            print(f"Warning: Failed to read {test_file}: {e}")
            continue
    
    return markers


def main():
    """Main function."""
    print("="*80)
    print("Checking All Markers in Automation Code")
    print("="*80)
    print()
    
    markers = find_all_markers()
    
    print(f"Found {len(markers)} unique test IDs with markers\n")
    
    # Group by file
    by_file = defaultdict(list)
    for test_id, occurrences in markers.items():
        for occ in occurrences:
            by_file[occ['file']].append(test_id)
    
    print(f"Markers found in {len(by_file)} files\n")
    
    # Show top files
    print("Top 10 files with most markers:")
    print("-" * 80)
    sorted_files = sorted(by_file.items(), key=lambda x: len(x[1]), reverse=True)
    for file_path, test_ids in sorted_files[:10]:
        file_name = Path(file_path).name
        print(f"{file_name:50} {len(test_ids):3} markers")
    
    print("\n" + "="*80)
    print("All Test IDs with Markers:")
    print("="*80)
    
    for test_id in sorted(markers.keys()):
        occurrences = markers[test_id]
        print(f"{test_id:15} {len(occurrences)} occurrence(s)")
        for occ in occurrences[:3]:  # Show first 3 files
            file_name = Path(occ['file']).name
            print(f"  - {file_name} ({occ['type']})")
        if len(occurrences) > 3:
            print(f"  ... and {len(occurrences) - 3} more")
        print()
    
    print("="*80)
    print(f"Total: {len(markers)} unique test IDs")
    print("="*80)


if __name__ == '__main__':
    main()

