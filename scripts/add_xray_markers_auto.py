#!/usr/bin/env python3
"""
Automatically Add Xray Markers Based on Keywords
================================================

This script adds @pytest.mark.xray("KEY") markers to test functions
based on keyword matching between CSV summary and test names.
"""

import re
from pathlib import Path
from typing import Dict, List

# Mapping based on keywords
KEYWORD_MAPPINGS = {
    # Historic / Time validation tests
    "historic.*end_time|missing end_time": ("PZ-13909", "test_prelaunch_validations.py"),
    "historic.*start_time|missing start_time": ("PZ-13907", "test_prelaunch_validations.py"),
    "future timestamp": ("PZ-13870", "test_prelaunch_validations.py"),
    "reversed range|end.*start": ("PZ-13869", "test_prelaunch_validations.py"),
    "invalid time range": ("PZ-13869", "test_prelaunch_validations.py"),
    
    # NFFT tests
    "nfft.*negative": ("PZ-13875", "test_config_validation_nfft_frequency.py"),
    "nfft.*zero": ("PZ-13874", "test_config_validation_nfft_frequency.py"),
    "nfft.*validation|all.*nfft": ("PZ-13901", "test_config_validation_nfft_frequency.py"),
    
    # Frequency tests
    "frequency.*nyquist": ("PZ-13903", "test_config_validation_nfft_frequency.py"),
    "invalid frequency.*min.*max": ("PZ-13877", "test_config_validation_nfft_frequency.py"),
    
    # Channel tests
    "channels.*enabled|get.*channels": ("PZ-13895", "test_api_endpoints_high_priority.py"),
    "invalid channel.*min.*max": ("PZ-13876", "test_prelaunch_validations.py"),
    
    # View type tests
    "invalid view type": ("PZ-13878", "test_prelaunch_validations.py"),
    
    # Performance tests
    "high throughput|performance.*stress": ("PZ-13905", "test_job_capacity_limits.py"),
    "concurrent.*limit|capacity": ("PZ-13896", "test_job_capacity_limits.py"),
    "200.*concurrent|target capacity": ("PZ-13986", "test_job_capacity_limits.py"),
    
    # Infrastructure tests
    "ssh.*production": ("PZ-13900", "test_external_connectivity.py"),
    "kubernetes.*cluster": ("PZ-13899", "test_k8s_job_lifecycle.py"),
    "mongodb.*connection": ("PZ-13898", "test_mongodb_data_quality.py"),
    "mongodb.*index": ("PZ-13810", "test_mongodb_data_quality.py"),
    
    # Data quality
    "data integrity|complete metadata": ("PZ-13812", "test_mongodb_data_quality.py"),
    "required.*fields": ("PZ-13879", "test_prelaunch_validations.py"),
    
    # ROI tests
    "roi.*change|dynamic.*roi": ("PZ-13784", "test_dynamic_roi_adjustment.py"),
}

print("=" * 80)
print("XRAY MARKER AUTO-MAPPING")
print("=" * 80)
print()

# Read test list
test_file = Path("xray_tests_list.txt")
if not test_file.exists():
    print("❌ xray_tests_list.txt not found")
    exit(1)

tests_to_map = []
with open(test_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if ',' in line:
            key, summary = line.split(',', 1)
            tests_to_map.append({'key': key, 'summary': summary})

print(f"Found {len(tests_to_map)} tests to map")
print()

# Find matches
matches = []
for test in tests_to_map:
    summary_lower = test['summary'].lower()
    
    for pattern, (key, file) in KEYWORD_MAPPINGS.items():
        if re.search(pattern, summary_lower):
            matches.append({
                'test_key': key,
                'xray_key': test['key'],
                'summary': test['summary'],
                'file': file
            })
            break

print(f"Found {len(matches)} potential matches")
print()

# Show matches
print("Matching Tests:")
for match in matches[:20]:
    print(f"✅ {match['xray_key']}: {match['summary'][:50]}")
    print(f"   → {match['file']}")
    print()

print("=" * 80)
print("Now I'll add the markers to the actual test files...")
print("=" * 80)

