#!/usr/bin/env python3
"""
Parse HTML DOC file to extract all Xray test IDs and summaries.
"""
import re
from pathlib import Path
from bs4 import BeautifulSoup

def extract_tests_from_html_doc(doc_path):
    """Extract all Xray tests from HTML DOC."""
    with open(doc_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Parse HTML
    soup = BeautifulSoup(content, 'html.parser')
    
    # Find all test entries
    tests = []
    
    # Pattern: [PZ-XXXXX] followed by summary
    pattern = r'\[PZ-(\d+)\].*?>(.*?)</a>'
    matches = re.findall(pattern, content)
    
    for pz_number, summary in matches:
        pz_id = f"PZ-{pz_number}"
        # Clean HTML from summary
        clean_summary = re.sub(r'<[^>]+>', '', summary)
        clean_summary = clean_summary.replace('&gt;', '>').replace('&lt;', '<').replace('&nbsp;', ' ')
        
        tests.append({
            'id': pz_id,
            'summary': clean_summary.strip()
        })
    
    return tests

def main():
    doc_path = Path("c:/Projects/focus_server_automation/archive_docs/Test+plan+(PZ-13756)+by+Roy+Avrahami+(Jira).doc")
    
    print("Extracting tests from HTML DOC...")
    tests = extract_tests_from_html_doc(doc_path)
    
    print(f"Found {len(tests)} tests in DOC")
    print("\n" + "="*80)
    print("ALL TESTS IN DOC:")
    print("="*80)
    
    for test in tests:
        print(f"{test['id']}: {test['summary']}")
    
    # Save to file
    output = Path('output/xray_tests_from_doc.txt')
    output.parent.mkdir(exist_ok=True)
    
    with open(output, 'w', encoding='utf-8') as f:
        for test in tests:
            f.write(f"{test['id']}: {test['summary']}\n")
    
    print(f"\nSaved to: {output}")
    
    return tests

if __name__ == '__main__':
    tests = main()

