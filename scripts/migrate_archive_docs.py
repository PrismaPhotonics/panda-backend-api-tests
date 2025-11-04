#!/usr/bin/env python3
"""
Archive Documentation Migration Script
=======================================

Intelligently migrates files from archive_docs/ to docs/ structure.
"""

import os
import shutil
from pathlib import Path

def migrate_archive_docs():
    """Migrate archive_docs to organized docs/ structure."""
    project_root = Path(__file__).parent.parent
    archive = project_root / 'archive_docs'
    docs = project_root / 'docs'
    
    # Migration mapping
    migrations = {
        # RabbitMQ guides → Infrastructure
        'rabbitmq': {
            'dest': docs / '07_infrastructure',
            'files': [
                'RABBITMQ_AUTOMATION_GUIDE.md',
                'RABBITMQ_AUTOMATION_QUICK_START.md',
                'RABBITMQ_CONNECTION_GUIDE.md',
                'RABBITMQ_QUICK_REFERENCE.md',
                'BIT_RABBITMQ_PATTERNS.md',
                'COMPLETE_RABBITMQ_JOURNEY.md'
            ]
        },
        
        # MongoDB guides → Infrastructure
        'mongodb': {
            'dest': docs / '07_infrastructure',
            'files': [
                'HOW_TO_DISCOVER_DATABASE_SCHEMA.md',
                'MONGODB_SCHEMA_REAL_FINDINGS.md'
            ]
        },
        
        # Infrastructure setup → Getting Started
        'setup': {
            'dest': docs / '01_getting_started',
            'files': [
                'AUTO_INFRASTRUCTURE_SETUP.md',
                'ENHANCED_LOGGING_GUIDE.md'
            ]
        },
        
        # Test guides → User Guides
        'testing': {
            'dest': docs / '02_user_guides',
            'files': [
                'SINGLECHANNEL_VIEW_TEST_GUIDE.md',
                'COMPLETE_TESTS_DIRECTORY_MAP.md'
            ]
        },
        
        # PZ integration → User Guides
        'pz_integration': {
            'dest': docs / '02_user_guides',
            'files': [
                'PZ_INTEGRATION_GUIDE.md',
                'QUICK_START_PZ.md'
            ]
        },
        
        # Specifications → Architecture
        'specs': {
            'dest': docs / '03_architecture',
            'files': [
                'TECHNICAL_SPECIFICATIONS_CLARIFICATIONS.md',
                'Critical Missing Specifications f.txt'
            ]
        },
        
        # Xray CSV files → Testing/Xray
        'xray_data': {
            'dest': docs / '04_testing' / 'xray_mapping',
            'files': [
                'Tests_xray_21_10_25.csv',
                'xray_tests_21_10_25.csv',
                'Test plan (PZ-13756) by Roy Avrahami (Jira).csv',
                'Test+plan+(PZ-13756)+by+Roy+Avrahami+(Jira).doc'
            ]
        },
        
        # Historical summaries → Archive
        'historical': {
            'dest': docs / '08_archive' / '2025-10',
            'files': [
                'CLEANUP_SUMMARY_20251021.md',
                'FINAL_REORGANIZATION_SUMMARY.md',
                'COMPLETE_PROJECT_STRUCTURE.md',
                'USERSETTINGS_VALIDATION_REPORT_HE.md'
            ]
        },
        
        # Security & configs → Archive
        'security': {
            'dest': docs / '08_archive' / '2025-10',
            'files': [
                'SECURITY_NOTES.md',
                'Update_PandaApp_Config.ps1'
            ]
        },
        
        # PDF documentation → Archive/pdfs
        'pdfs': {
            'dest': docs / '08_archive' / 'pdfs',
            'files': [f for f in os.listdir(archive) if f.endswith('.pdf')]
        },
        
        # Hebrew files → Archive
        'hebrew': {
            'dest': docs / '08_archive' / '2025-10',
            'files': [
                '📌_הוראות_עדכון_קונפיג.txt'
            ]
        }
    }
    
    # Create necessary directories
    pdf_dir = docs / '08_archive' / 'pdfs'
    pdf_dir.mkdir(parents=True, exist_ok=True)
    
    # Track migrations
    migrated = []
    failed = []
    
    print("Starting archive_docs migration...")
    print("=" * 60)
    
    for category, config in migrations.items():
        dest = config['dest']
        files = config['files']
        
        print(f"\n[{category.upper()}] -> {dest.relative_to(project_root)}")
        
        for filename in files:
            src = archive / filename
            if src.exists() and src.is_file():
                try:
                    dst = dest / filename
                    shutil.copy2(str(src), str(dst))
                    migrated.append(f"{filename} -> {dest.name}/")
                    print(f"  [OK] {filename}")
                except Exception as e:
                    failed.append(f"{filename}: {e}")
                    print(f"  [ERROR] {filename}: {e}")
            else:
                print(f"  [SKIP] {filename} (not found)")
    
    # Handle directories
    print(f"\n[DIRECTORIES]")
    dirs_to_copy = ['old_configs', 'session_summaries']
    archive_dest = docs / '08_archive' / '2025-10'
    
    for dirname in dirs_to_copy:
        src_dir = archive / dirname
        if src_dir.exists() and src_dir.is_dir():
            dst_dir = archive_dest / dirname
            try:
                shutil.copytree(str(src_dir), str(dst_dir), dirs_exist_ok=True)
                migrated.append(f"{dirname}/ -> archive/2025-10/")
                print(f"  [OK] {dirname}/ (directory)")
            except Exception as e:
                failed.append(f"{dirname}/: {e}")
                print(f"  [ERROR] {dirname}/: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"[SUMMARY]")
    print(f"  Migrated: {len(migrated)} items")
    print(f"  Failed: {len(failed)} items")
    
    if failed:
        print(f"\n[FAILED ITEMS]")
        for item in failed:
            print(f"  - {item}")
    
    return len(migrated), len(failed)

if __name__ == '__main__':
    migrated, failed = migrate_archive_docs()
    exit(0 if failed == 0 else 1)

