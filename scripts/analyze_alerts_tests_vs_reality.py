"""
Script to analyze alerts tests vs actual system implementation.

This script:
1. Analyzes all alert test files
2. Checks what they actually test vs what they claim to test
3. Identifies unimplemented tests (skeletons)
4. Checks against actual system architecture
5. Generates comprehensive report

Run with:
    python scripts/analyze_alerts_tests_vs_reality.py
"""

import sys
import os
import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logger = None  # Will be initialized

def analyze_test_file(file_path: Path) -> Dict:
    """Analyze a single test file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    analysis = {
        'file': str(file_path.relative_to(project_root)),
        'total_tests': 0,
        'implemented_tests': [],
        'skeleton_tests': [],
        'uses_api': False,
        'uses_rabbitmq': False,
        'uses_mongodb': False,
        'api_endpoint': None,
        'issues': []
    }
    
    # Count test functions
    tree = ast.parse(content)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
            analysis['total_tests'] += 1
            
            # Check if test is implemented or skeleton
            test_code = ast.get_source_segment(content, node)
            if test_code:
                # Check for skeleton indicators
                has_implementation = False
                has_pass_only = False
                has_implementation_comment = False
                
                for child in ast.walk(node):
                    if isinstance(child, ast.Pass):
                        has_pass_only = True
                    if isinstance(child, ast.Expr) and isinstance(child.value, ast.Constant):
                        if isinstance(child.value.value, str) and 'Implementation' in child.value.value:
                            has_implementation_comment = True
                    if isinstance(child, (ast.Call, ast.Assign, ast.Return, ast.Raise)):
                        if not isinstance(child, ast.Pass):
                            has_implementation = True
                
                # Check for actual API calls
                if 'session.post' in test_code or 'requests.post' in test_code:
                    analysis['uses_api'] = True
                    # Extract API endpoint
                    match = re.search(r'["\']([^"\']*push-to-rabbit[^"\']*)["\']', test_code)
                    if match:
                        analysis['api_endpoint'] = match.group(1)
                
                if 'pika' in test_code or 'RabbitMQ' in test_code:
                    analysis['uses_rabbitmq'] = True
                
                if 'MongoDB' in test_code or 'mongodb' in test_code.lower():
                    analysis['uses_mongodb'] = True
                
                # Determine if skeleton
                if has_implementation_comment or (has_pass_only and not has_implementation):
                    analysis['skeleton_tests'].append(node.name)
                else:
                    analysis['implemented_tests'].append(node.name)
    
    return analysis

def main():
    print("=" * 80)
    print("Alerts Tests vs Reality Analysis")
    print("=" * 80)
    print()
    
    # Find all alert test files
    alerts_dir = project_root / "be_focus_server_tests" / "integration" / "alerts"
    test_files = list(alerts_dir.glob("test_*.py"))
    
    print(f"Found {len(test_files)} test files:")
    for f in test_files:
        print(f"  - {f.name}")
    print()
    
    # Analyze each file
    all_analyses = []
    for test_file in test_files:
        print(f"Analyzing {test_file.name}...")
        analysis = analyze_test_file(test_file)
        all_analyses.append(analysis)
    
    # Generate report
    print("\n" + "=" * 80)
    print("ANALYSIS REPORT")
    print("=" * 80)
    print()
    
    total_tests = 0
    total_implemented = 0
    total_skeletons = 0
    
    for analysis in all_analyses:
        print(f"\n[FILE] {analysis['file']}")
        print(f"   Total tests: {analysis['total_tests']}")
        print(f"   [OK] Implemented: {len(analysis['implemented_tests'])}")
        print(f"   [WARN] Skeletons: {len(analysis['skeleton_tests'])}")
        
        if analysis['skeleton_tests']:
            print(f"   Skeleton tests:")
            for test in analysis['skeleton_tests']:
                print(f"     - {test}")
        
        if analysis['uses_api']:
            print(f"   [API] Uses API: Yes")
            if analysis['api_endpoint']:
                print(f"      Endpoint: {analysis['api_endpoint']}")
        else:
            print(f"   [API] Uses API: No")
        
        if analysis['uses_rabbitmq']:
            print(f"   [RABBITMQ] Uses RabbitMQ: Yes")
        else:
            print(f"   [RABBITMQ] Uses RabbitMQ: No")
        
        if analysis['uses_mongodb']:
            print(f"   [MONGODB] Uses MongoDB: Yes")
        else:
            print(f"   [MONGODB] Uses MongoDB: No")
        
        total_tests += analysis['total_tests']
        total_implemented += len(analysis['implemented_tests'])
        total_skeletons += len(analysis['skeleton_tests'])
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total tests: {total_tests}")
    print(f"[OK] Implemented: {total_implemented}")
    print(f"[WARN] Skeletons: {total_skeletons}")
    print(f"[STATS] Implementation rate: {total_implemented/total_tests*100:.1f}%")
    
    # Check API endpoint consistency
    print("\n" + "=" * 80)
    print("API ENDPOINT ANALYSIS")
    print("=" * 80)
    
    endpoints_found = set()
    for analysis in all_analyses:
        if analysis['api_endpoint']:
            endpoints_found.add(analysis['api_endpoint'])
    
    if endpoints_found:
        print("Endpoints found in tests:")
        for endpoint in sorted(endpoints_found):
            print(f"  - {endpoint}")
    else:
        print("[WARN] No API endpoints found in test code!")
    
    # Check architecture alignment
    print("\n" + "=" * 80)
    print("ARCHITECTURE ALIGNMENT")
    print("=" * 80)
    
    print("\nExpected API endpoint: POST /prisma-210-1000/api/push-to-rabbit")
    print("Expected API base: https://10.10.10.100/prisma/api/")
    print("Expected system: Prisma Web App API (NOT Focus Server API)")
    
    # MongoDB usage
    mongodb_usage = sum(1 for a in all_analyses if a['uses_mongodb'])
    print(f"\n[WARN] Files using MongoDB: {mongodb_usage}")
    print("   Note: Alerts are NOT stored in MongoDB!")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print()
    print("1. Complete skeleton tests or mark them as skipped")
    print("2. Remove MongoDB-related code (alerts not stored in MongoDB)")
    print("3. Verify API endpoint matches Prisma Web App API")
    print("4. Ensure tests use correct authentication (cookie-based)")
    print("5. Verify RabbitMQ exchange and routing keys match reality")
    
    # Save detailed report
    report_file = project_root / "docs" / "04_testing" / "analysis" / "ALERTS_TESTS_VS_REALITY_ANALYSIS.md"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 🔍 Alerts Tests vs Reality - Complete Analysis\n\n")
        f.write(f"**Date:** {Path(__file__).stat().st_mtime}\n\n")
        f.write("## Summary\n\n")
        f.write(f"- Total tests: {total_tests}\n")
        f.write(f"- Implemented: {total_implemented}\n")
        f.write(f"- Skeletons: {total_skeletons}\n")
        f.write(f"- Implementation rate: {total_implemented/total_tests*100:.1f}%\n\n")
        f.write("## Detailed Analysis\n\n")
        for analysis in all_analyses:
            f.write(f"### {analysis['file']}\n\n")
            f.write(f"- Total: {analysis['total_tests']}\n")
            f.write(f"- Implemented: {len(analysis['implemented_tests'])}\n")
            f.write(f"- Skeletons: {len(analysis['skeleton_tests'])}\n")
            if analysis['skeleton_tests']:
                f.write(f"\nSkeleton tests:\n")
                for test in analysis['skeleton_tests']:
                    f.write(f"  - `{test}`\n")
            f.write("\n")
    
    print(f"\n[OK] Detailed report saved to: {report_file}")

if __name__ == "__main__":
    main()

