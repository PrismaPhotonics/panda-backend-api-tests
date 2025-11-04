#!/usr/bin/env python3
"""
Documentation Organizer Script
==============================

Moves remaining root-level documentation files to appropriate directories.
"""

import os
import shutil
from pathlib import Path

def organize_documents():
    """Organize remaining documentation files."""
    project_root = Path(__file__).parent.parent
    
    # Files to keep in root
    keep_in_root = {
        'README.md',
        'QUICK_START.md',
        'CHANGELOG.md',
        'PROJECT_REORGANIZATION_PLAN.md',
        'LICENSE',
        'requirements.txt',
        'setup.py',
        'pytest.ini'
    }
    
    # Get all .md files in root
    md_files = list(project_root.glob('*.md'))
    
    moved_files = []
    kept_files = []
    
    for md_file in md_files:
        if md_file.name in keep_in_root:
            kept_files.append(md_file.name)
            continue
        
        # Move to archive
        dest = project_root / 'docs' / '08_archive' / '2025-10' / md_file.name
        try:
            shutil.move(str(md_file), str(dest))
            moved_files.append(md_file.name)
            # Handle encoding issues with emoji/special chars
            try:
                print(f"[OK] Moved: {md_file.name}")
            except UnicodeEncodeError:
                print(f"[OK] Moved: {md_file.name.encode('ascii', 'ignore').decode()}")
        except Exception as e:
            try:
                print(f"[ERROR] Failed to move {md_file.name}: {e}")
            except UnicodeEncodeError:
                print(f"[ERROR] Failed to move file (encoding issue)")
    
    print(f"\n[SUMMARY]")
    print(f"   Moved: {len(moved_files)} files")
    print(f"   Kept in root: {len(kept_files)} files")
    print(f"\n[FILES KEPT IN ROOT]")
    for f in kept_files:
        print(f"   - {f}")

if __name__ == '__main__':
    organize_documents()

