#!/usr/bin/env python3
"""
Analyze Xray CSV and Create Mapping to Automation Tests
======================================================

This script analyzes the Jira Xray CSV export and creates a mapping
between Xray tests and automation test files.
"""

import csv
import json
from pathlib import Path
from typing import List, Dict, Any
import re

# Test file patterns in the automation suite
AUTOMATION_TEST_PATTERNS = {
    "integration": {
        "path": "tests/integration/api/",
        "files": [
            "test_prelaunch_validations.py",
            "test_config_validation_nfft_frequency.py",
            "test_api_endpoints_high_priority.py",
        ]
    },
    "data_quality": {
        "path": "tests/data_quality/",
        "files": [
            "test_mongodb_data_quality.py",
        ]
    },
    "load": {
        "path": "tests/load/",
        "files": [
            "test_job_capacity_limits.py",
        ]
    },
    "infrastructure": {
        "path": "tests/infrastructure/",
        "files": [
            "test_basic_connectivity.py",
            "test_external_connectivity.py",
            "test_k8s_job_lifecycle.py",
            "test_system_behavior.py",
        ]
    }
}


def extract_test_info(row: Dict[str, str]) -> Dict[str, Any]:
    """Extract relevant information from a test row."""
    return {
        "issue_key": row.get("Issue key", ""),
        "summary": row.get("Summary", ""),
        "status": row.get("Status", ""),
        "priority": row.get("Priority", ""),
        "labels": row.get("Labels", ""),
        "description": row.get("Description", ""),
        "issue_type": row.get("Issue Type", ""),
    }


def categorize_test(test_info: Dict[str, Any]) -> str:
    """Categorize test based on summary and labels."""
    summary = test_info["summary"].lower()
    labels = test_info["labels"].lower()
    
    if "integration" in labels or "integration" in summary:
        return "integration"
    elif "data_quality" in labels or "data quality" in summary or "mongodb" in summary:
        return "data_quality"
    elif "performance" in labels or "performance" in summary or "throughput" in summary:
        return "performance"
    elif "infrastructure" in labels or "infrastructure" in summary or "connectivity" in summary:
        return "infrastructure"
    elif "security" in labels or "security" in summary or "malformed" in summary:
        return "security"
    elif "stress" in labels or "stress" in summary or "extreme" in summary:
        return "stress"
    elif "capacity" in summary or "200" in summary or "concurrent" in summary:
        return "load"
    elif "api" in labels or "endpoint" in summary:
        return "api"
    else:
        return "other"


def find_automation_match(test_info: Dict[str, Any], category: str) -> Dict[str, Any]:
    """Find potential automation test match for Xray test."""
    summary = test_info["summary"].lower()
    issue_key = test_info["issue_key"]
    
    matches = {
        "suggested_file": None,
        "suggested_test_name": None,
        "confidence": "low"
    }
    
    # Known mappings
    known_mappings = {
        "PZ-13984": {
            "file": "tests/integration/api/test_prelaunch_validations.py",
            "test": "test_time_range_validation_future_timestamps",
            "confidence": "high"
        },
        "PZ-13985": {
            "file": "tests/conftest.py",
            "test": "live_metadata",
            "confidence": "high"
        },
        "PZ-13986": {
            "file": "tests/load/test_job_capacity_limits.py",
            "test": "test_200_concurrent_jobs_target_capacity",
            "confidence": "high"
        }
    }
    
    if issue_key in known_mappings:
        return known_mappings[issue_key]
    
    # Try to match based on keywords
    if "future timestamp" in summary or "timestamp" in summary:
        matches["suggested_file"] = "tests/integration/api/test_prelaunch_validations.py"
        matches["confidence"] = "medium"
    elif "metadata" in summary or "live metadata" in summary:
        matches["suggested_file"] = "tests/conftest.py"
        matches["confidence"] = "medium"
    elif "200" in summary or "capacity" in summary or "concurrent" in summary:
        matches["suggested_file"] = "tests/load/test_job_capacity_limits.py"
        matches["confidence"] = "medium"
    elif "mongodb" in summary or "data quality" in summary:
        matches["suggested_file"] = "tests/data_quality/test_mongodb_data_quality.py"
        matches["confidence"] = "medium"
    
    return matches


def analyze_csv(file_path: str):
    """Analyze the CSV file and create mapping."""
    
    print("=" * 80)
    print("XRAY CSV ANALYSIS - FULL MAPPING")
    print("=" * 80)
    print()
    
    tests = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            if row.get('Issue Type') == 'Test':
                test_info = extract_test_info(row)
                category = categorize_test(test_info)
                automation_match = find_automation_match(test_info, category)
                
                test_info["category"] = category
                test_info["automation_match"] = automation_match
                tests.append(test_info)
    
    print(f"✅ Total tests found: {len(tests)}")
    print()
    
    # Summary by category
    categories = {}
    for test in tests:
        cat = test["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    print("Tests by Category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat:20} {count:3} tests")
    print()
    
    # Tests by status
    statuses = {}
    for test in tests:
        status = test["status"]
        statuses[status] = statuses.get(status, 0) + 1
    
    print("Tests by Status:")
    for status, count in sorted(statuses.items()):
        print(f"  {status:15} {count:3} tests")
    print()
    
    # Show tests with high confidence automation matches
    print("=" * 80)
    print("TESTS WITH AUTOMATION MAPPING (HIGH CONFIDENCE)")
    print("=" * 80)
    print()
    
    mapped_tests = [t for t in tests if t["automation_match"]["confidence"] == "high"]
    
    for test in mapped_tests:
        print(f"✅ {test['issue_key']}: {test['summary'][:60]}")
        print(f"   Automation: {test['automation_match']['file']}")
        print(f"   Test: {test['automation_match']['test']}")
        print()
    
    # Show all tests that need mapping
    print("=" * 80)
    print("ALL TESTS (First 20)")
    print("=" * 80)
    print()
    
    for i, test in enumerate(tests[:20], 1):
        match = test["automation_match"]
        conf_icon = "✅" if match["confidence"] == "high" else "⚠️" if match["confidence"] == "medium" else "❓"
        
        print(f"{conf_icon} {test['issue_key']}: {test['summary'][:50]}")
        if match["suggested_file"]:
            print(f"   → {match['suggested_file']}")
        print()
    
    # Create JSON mapping
    mapping = {
        "total_tests": len(tests),
        "tests_mapped": len(mapped_tests),
        "tests_needing_mapping": len(tests) - len(mapped_tests),
        "mapping": {}
    }
    
    for test in tests:
        if test["automation_match"]["suggested_file"]:
            mapping["mapping"][test["issue_key"]] = {
                "summary": test["summary"],
                "category": test["category"],
                "automation_file": test["automation_match"]["suggested_file"],
                "confidence": test["automation_match"]["confidence"]
            }
    
    # Write mapping JSON
    output_file = "XRAY_AUTOMATION_MAPPING.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    
    print("=" * 80)
    print(f"✅ Mapping saved to: {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    file_path = r"c:\Users\roy.avrahami\Downloads\Test plan (PZ-13756) by Roy Avrahami (Jira).csv"
    
    if not Path(file_path).exists():
        print(f"❌ Error: File not found: {file_path}")
        exit(1)
    
    analyze_csv(file_path)

