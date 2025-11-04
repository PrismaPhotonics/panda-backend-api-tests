#!/usr/bin/env python3
"""
Calculation Verification Script
================================

This script sends a real configure request and validates the calculation formulas
by comparing actual response values with expected calculations.

Author: QA Automation Team
Date: 2025-10-29
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.config_manager import ConfigManager
from src.apis.focus_server_api import FocusServerAPI
from src.models.focus_server_models import ConfigureRequest, DisplayInfo, Channels, FrequencyRange, ViewType


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def print_result(name: str, expected: Any, actual: Any, tolerance: float = 0.001) -> bool:
    """Print comparison result and return if it matches."""
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        matches = abs(expected - actual) < tolerance
        symbol = "[OK]" if matches else "[FAIL]"
        print(f"{symbol} {name}:")
        print(f"   Expected: {expected}")
        print(f"   Actual:   {actual}")
        if not matches:
            diff = abs(expected - actual)
            print(f"   Diff:     {diff}")
        return matches
    else:
        matches = expected == actual
        symbol = "[OK]" if matches else "[FAIL]"
        print(f"{symbol} {name}:")
        print(f"   Expected: {expected}")
        print(f"   Actual:   {actual}")
        return matches


def main():
    """Main verification function."""
    
    print_section("CALCULATION VERIFICATION - Real Test")
    
    # Initialize API
    print("Initializing Focus Server API...")
    config_manager = ConfigManager()
    api = FocusServerAPI(config_manager)
    
    print(f"[OK] Connected to: {api.base_url}")
    
    # Test Configuration
    print_section("Test Configuration")
    
    test_config = {
        "nfft": 512,
        "overlap_samples": 256,  # We'll calculate this as NFFT/2
        "channels_min": 1,
        "channels_max": 8,
        "freq_min": 0,
        "freq_max": 500,
        "view_type": ViewType.MULTICHANNEL
    }
    
    # Assumptions (need to verify with system)
    prr = 1000  # Pulse Repetition Rate (samples/second) - NEED TO VERIFY!
    
    print("Test Parameters:")
    print(f"  NFFT:          {test_config['nfft']}")
    print(f"  Overlap:       {test_config['overlap_samples']} samples (50%)")
    print(f"  Channels:      {test_config['channels_min']}-{test_config['channels_max']}")
    print(f"  Frequency:     {test_config['freq_min']}-{test_config['freq_max']} Hz")
    print(f"  PRR (assumed): {prr} Hz")
    print(f"  View Type:     MultiChannel")
    
    # Expected Calculations
    print_section("Expected Calculations (Based on Formulas)")
    
    nfft = test_config['nfft']
    overlap = test_config['overlap_samples']
    min_ch = test_config['channels_min']
    max_ch = test_config['channels_max']
    
    # Calculation 1: Frequency Bins
    expected_freq_bins = nfft // 2 + 1
    print(f"1. Frequency Bins = NFFT / 2 + 1")
    print(f"   = {nfft} / 2 + 1")
    print(f"   = {expected_freq_bins}")
    
    # Calculation 2: lines_dt (Time Resolution)
    expected_lines_dt = (nfft - overlap) / prr
    print(f"\n2. lines_dt = (NFFT - Overlap) / PRR")
    print(f"   = ({nfft} - {overlap}) / {prr}")
    print(f"   = {expected_lines_dt} seconds")
    
    # Calculation 3: Output Rate
    expected_output_rate = prr / (nfft - overlap)
    print(f"\n3. Output Rate = PRR / (NFFT - Overlap)")
    print(f"   = {prr} / ({nfft} - {overlap})")
    print(f"   = {expected_output_rate:.3f} lines/second")
    
    # Calculation 4: Channel Count
    expected_channel_count = max_ch - min_ch + 1
    print(f"\n4. Channel Count = max - min + 1")
    print(f"   = {max_ch} - {min_ch} + 1")
    print(f"   = {expected_channel_count}")
    
    # Calculation 5: Stream Amount (should equal channel count)
    expected_stream_amount = expected_channel_count
    print(f"\n5. Stream Amount = Channel Count")
    print(f"   = {expected_stream_amount}")
    
    # Calculation 6: Frequency Resolution
    expected_freq_resolution = prr / nfft
    print(f"\n6. Frequency Resolution = PRR / NFFT")
    print(f"   = {prr} / {nfft}")
    print(f"   = {expected_freq_resolution:.3f} Hz")
    
    # Send Configure Request
    print_section("Sending Configure Request")
    
    try:
        payload = ConfigureRequest(
            displayTimeAxisDuration=30,
            nfftSelection=test_config['nfft'],
            displayInfo=DisplayInfo(height=768),
            channels=Channels(
                min=test_config['channels_min'],
                max=test_config['channels_max']
            ),
            frequencyRange=FrequencyRange(
                min=test_config['freq_min'],
                max=test_config['freq_max']
            ),
            view_type=test_config['view_type']
        )
        
        print("Payload:")
        print(json.dumps(payload.model_dump(), indent=2))
        
        print("\nSending request...")
        response = api.configure_streaming_job(payload)
        
        print(f"[OK] Success! Job ID: {response.job_id}")
        
        # The ConfigureResponse itself contains the metadata we need!
        print("\n[INFO] ConfigureResponse already contains all metadata")
        metadata = response
        
    except Exception as e:
        print(f"[FAIL] Failed to configure: {e}")
        return 1
    
    # Display Actual Response
    print_section("Actual Response Values from ConfigureResponse")
    
    print(f"job_id:                {metadata.job_id}")
    print(f"lines_dt:              {metadata.lines_dt}")
    print(f"frequencies_amount:    {metadata.frequencies_amount}")
    print(f"channel_amount:        {metadata.channel_amount}")
    print(f"stream_amount:         {metadata.stream_amount}")
    print(f"channel_to_stream_index: {metadata.channel_to_stream_index}")
    print(f"frequencies_list (first 5): {metadata.frequencies_list[:5] if len(metadata.frequencies_list) > 5 else metadata.frequencies_list}")
    
    # Also check if frequency_resolution is returned
    if hasattr(metadata, 'frequency_resolution'):
        print(f"frequency_resolution:  {metadata.frequency_resolution}")
    else:
        print("frequency_resolution:  (not in response)")
    
    # We can derive output_rate from lines_dt
    actual_output_rate = 1 / metadata.lines_dt if metadata.lines_dt > 0 else 0
    print(f"output_rate (derived): {actual_output_rate:.3f} lines/sec")
    
    # Validation
    print_section("Validation Results")
    
    results = []
    
    # Test 1: Frequency Bins
    results.append(print_result(
        "frequencies_amount = NFFT/2 + 1",
        expected_freq_bins,
        metadata.frequencies_amount
    ))
    
    # Test 2: lines_dt
    results.append(print_result(
        "lines_dt = (NFFT - Overlap) / PRR",
        expected_lines_dt,
        metadata.lines_dt,
        tolerance=0.001
    ))
    
    # Test 3: Output Rate
    results.append(print_result(
        "output_rate = 1 / lines_dt",
        expected_output_rate,
        actual_output_rate,
        tolerance=0.01
    ))
    
    # Test 4: Channel Count
    results.append(print_result(
        "channel_amount = max - min + 1",
        expected_channel_count,
        metadata.channel_amount
    ))
    
    # Test 5: Stream Amount
    results.append(print_result(
        "stream_amount = channel_amount",
        expected_stream_amount,
        metadata.stream_amount
    ))
    
    # Test 6: Channel Mapping
    print("\n[CHECK] Channel Mapping Validation:")
    expected_mapping = {str(i): i - min_ch for i in range(min_ch, max_ch + 1)}
    mapping_correct = True
    
    for channel, expected_index in expected_mapping.items():
        actual_index = metadata.channel_to_stream_index.get(channel)
        if actual_index != expected_index:
            print(f"  [FAIL] Channel {channel}: expected index {expected_index}, got {actual_index}")
            mapping_correct = False
    
    if mapping_correct:
        print(f"  [OK] All {len(expected_mapping)} channels mapped correctly")
        print(f"     {metadata.channel_to_stream_index}")
    
    results.append(mapping_correct)
    
    # Summary
    print_section("SUMMARY")
    
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100
    
    print(f"Tests Passed: {passed}/{total} ({percentage:.0f}%)")
    print()
    
    if passed == total:
        print("SUCCESS: ALL FORMULAS VERIFIED!")
        print("\nConclusion:")
        print("  [OK] All calculation formulas are CORRECT")
        print("  [OK] Safe to implement the automated tests")
        return 0
    else:
        print("WARNING: SOME FORMULAS NEED VERIFICATION")
        print("\nNext Steps:")
        print("  1. Check PRR value (is it really 1000 Hz?)")
        print("  2. Check overlap calculation (is it NFFT/2?)")
        print("  3. Consult with Gal/Noga about calculation specs")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Stopped by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

