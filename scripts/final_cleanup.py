#!/usr/bin/env python3
"""
Final Root Cleanup Script
=========================

Moves remaining MD files from project root to appropriate docs/ locations.
"""

import shutil
from pathlib import Path

def final_cleanup():
    """Move remaining MD files to docs structure."""
    project_root = Path(__file__).parent.parent
    docs = project_root / 'docs'
    
    # Files to keep in root
    keep_in_root = {'README.md'}
    
    # Get all MD files in root
    md_files = [f for f in project_root.glob('*.md') if f.name not in keep_in_root]
    
    # Categorize and move
    categories = {
        'xray': {
            'dest': docs / '04_testing' / 'xray_mapping',
            'patterns': ['XRAY', 'xray']
        },
        'coverage': {
            'dest': docs / '04_testing',
            'patterns': ['COVERAGE', 'COMPLETE', 'FINAL', 'COMPARISON']
        },
        'implementation': {
            'dest': docs / '06_project_management' / 'progress_reports',
            'patterns': ['IMPLEMENTATION', 'SUMMARY', 'STATUS', 'UPDATE']
        },
        'missing_tests': {
            'dest': docs / '04_testing',
            'patterns': ['MISSING', 'REMAINING', 'NOT_IMPLEMENTED', 'BACKLOG']
        },
        'csv_analysis': {
            'dest': docs / '04_testing',
            'patterns': ['CSV']
        },
        'duplicates': {
            'dest': docs / '04_testing',
            'patterns': ['DUPLICATE']
        },
        'how_to': {
            'dest': docs / '01_getting_started',
            'patterns': ['HOW_TO']
        },
        'visualization': {
            'dest': docs / '04_testing',
            'patterns': ['VISUALIZATION']
        }
    }
    
    moved = []
    
    for md_file in md_files:
        # Find matching category
        for cat_name, cat_config in categories.items():
            if any(pattern in md_file.name for pattern in cat_config['patterns']):
                dest = cat_config['dest'] / md_file.name
                try:
                    shutil.move(str(md_file), str(dest))
                    moved.append(f"{md_file.name} -> {cat_config['dest'].name}/")
                    print(f"[OK] {md_file.name} -> {cat_config['dest'].relative_to(project_root)}")
                    break
                except Exception as e:
                    print(f"[ERROR] {md_file.name}: {e}")
    
    print(f"\n[SUMMARY] Moved {len(moved)} files")
    return len(moved)

if __name__ == '__main__':
    moved = final_cleanup()
    exit(0)

