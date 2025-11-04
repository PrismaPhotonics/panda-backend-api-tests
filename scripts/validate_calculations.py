#!/usr/bin/env python3
"""
Validation Script - Verify calculation formulas against actual system responses

This script sends real configure requests and validates that the calculations
we derived are correct by comparing them to actual server responses.

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
    """Print formatted section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def validate_frequency_bins_calculation():
    """
    Validate: frequencies_amount = NFFT / 2 + 1
    """
    print_section("TEST 1: Frequency Bins Calculation")
    
    config_manager = ConfigManager()
    api = FocusServerAPI(config_manager)
    
    test_cases = [
        {"nfft": 256, "expected": 129},
        {"nfft": 512, "expected": 257},
        {"nfft": 1024, "expected": 513},
        {"nfft": 2048, "expected": 1025},
    ]
    
    print("Testing formula: frequencies_amount = NFFT / 2 + 1")
    
    results = []
    for case in test_cases:
        nfft = case["nfft"]
        expected = case["expected"]
        
        print(f"Testing NFFT={nfft}...")
        
        try:
            # Create request
            payload = ConfigureRequest(
                displayTimeAxisDuration=30,
                nfftSelection=nfft,
                displayInfo=DisplayInfo(height=768),
                channels=Channels(min=1, max=8),
                frequencyRange=FrequencyRange(min=0, max=500),
                view_type=ViewType.MULTICHANNEL
            )
            
            # Send request
            response = api.configure_streaming_job(payload)
            print(f"  ✓ Job created: {response.job_id}")
            
            # Get metadata
            metadata = api.get_task_metadata(response.job_id)
            actual = metadata.frequencies_amount
            
            # Validate
            match = actual == expected
            status = "[MATCH]" if match else "[MISMATCH]"
            
            print(f"  Expected: {expected}")
            print(f"  Actual:   {actual}")
            print(f"  {status}\n")
            
            results.append({
                "nfft": nfft,
                "expected": expected,
                "actual": actual,
                "match": match,
                "formula": "NFFT / 2 + 1"
            })
            
            # Cleanup
            try:
                api.cancel_job(response.job_id)
                print(f"  ✓ Job cancelled\n")
            except:
                pass
                
        except Exception as e:
            print(f"  ❌ Error: {e}\n")
            results.append({
                "nfft": nfft,
                "error": str(e)
            })
    
    return results


def validate_lines_dt_calculation():
    """
    Validate: lines_dt = (NFFT - Overlap) / PRR
    
    Note: We need to find out what the overlap value is!
    """
    print_section("TEST 2: Time Resolution (lines_dt) Calculation")
    
    config_manager = ConfigManager()
    api = FocusServerAPI(config_manager)
    
    print("Testing formula: lines_dt = (NFFT - Overlap) / PRR")
    print("⚠️  Note: We need to determine Overlap value from response!\n")
    
    test_cases = [
        {"nfft": 512},
        {"nfft": 1024},
    ]
    
    results = []
    for case in test_cases:
        nfft = case["nfft"]
        
        print(f"Testing NFFT={nfft}...")
        
        try:
            # Create request
            payload = ConfigureRequest(
                displayTimeAxisDuration=30,
                nfftSelection=nfft,
                displayInfo=DisplayInfo(height=768),
                channels=Channels(min=1, max=8),
                frequencyRange=FrequencyRange(min=0, max=500),
                view_type=ViewType.MULTICHANNEL
            )
            
            # Send request
            response = api.configure_streaming_job(payload)
            print(f"  [OK] Job created: {response.job_id}")
            
            # Get metadata
            metadata = api.get_task_metadata(response.job_id)
            actual_lines_dt = metadata.lines_dt
            
            print(f"  Actual lines_dt: {actual_lines_dt}")
            
            # Try to reverse-engineer overlap
            # Assuming PRR = 1000 (need to verify!)
            prr = 1000
            
            # From formula: lines_dt = (NFFT - Overlap) / PRR
            # → Overlap = NFFT - (lines_dt * PRR)
            calculated_overlap = nfft - (actual_lines_dt * prr)
            overlap_percentage = (calculated_overlap / nfft) * 100
            
            print(f"  Reverse-engineered Overlap: {calculated_overlap:.0f} samples ({overlap_percentage:.1f}%)")
            
            # Common overlap percentages
            if abs(overlap_percentage - 50) < 5:
                print(f"  → Likely 50% overlap (standard)")
            elif abs(overlap_percentage - 75) < 5:
                print(f"  → Likely 75% overlap")
            elif abs(overlap_percentage - 25) < 5:
                print(f"  → Likely 25% overlap")
            
            print()
            
            results.append({
                "nfft": nfft,
                "lines_dt": actual_lines_dt,
                "calculated_overlap": calculated_overlap,
                "overlap_percentage": overlap_percentage
            })
            
            # Cleanup
            try:
                api.cancel_job(response.job_id)
                print(f"  ✓ Job cancelled\n")
            except:
                pass
                
        except Exception as e:
            print(f"  ❌ Error: {e}\n")
            results.append({
                "nfft": nfft,
                "error": str(e)
            })
    
    return results


def validate_channel_mapping():
    """
    Validate channel mapping calculations.
    """
    print_section("TEST 3: Channel Mapping")
    
    config_manager = ConfigManager()
    api = FocusServerAPI(config_manager)
    
    print("Testing channel mapping calculations:\n")
    
    test_cases = [
        {"min": 7, "max": 7, "name": "SingleChannel"},
        {"min": 1, "max": 8, "name": "MultiChannel (8 channels)"},
        {"min": 5, "max": 10, "name": "MultiChannel (6 channels)"},
    ]
    
    results = []
    for case in test_cases:
        min_ch = case["min"]
        max_ch = case["max"]
        name = case["name"]
        
        expected_amount = max_ch - min_ch + 1
        
        print(f"Testing {name}: channels={{{min_ch}, {max_ch}}}...")
        
        try:
            # Create request
            payload = ConfigureRequest(
                displayTimeAxisDuration=30,
                nfftSelection=512,
                displayInfo=DisplayInfo(height=768),
                channels=Channels(min=min_ch, max=max_ch),
                frequencyRange=FrequencyRange(min=0, max=500),
                view_type=ViewType.SINGLECHANNEL if min_ch == max_ch else ViewType.MULTICHANNEL
            )
            
            # Send request
            response = api.configure_streaming_job(payload)
            print(f"  [OK] Job created: {response.job_id}")
            
            # Get metadata
            metadata = api.get_task_metadata(response.job_id)
            
            print(f"  Expected channel_amount: {expected_amount}")
            print(f"  Actual channel_amount:   {metadata.channel_amount}")
            print(f"  stream_amount:           {metadata.stream_amount}")
            
            # Validate mapping
            print(f"  channel_to_stream_index:")
            for ch, idx in sorted(metadata.channel_to_stream_index.items(), key=lambda x: int(x[0])):
                print(f"    {ch} -> {idx}")
            
            # Check if mapping is sequential
            is_sequential = True
            for i, channel in enumerate(range(min_ch, max_ch + 1)):
                if str(channel) in metadata.channel_to_stream_index:
                    if metadata.channel_to_stream_index[str(channel)] != i:
                        is_sequential = False
                        break
            
            print(f"  Sequential mapping: {'[YES]' if is_sequential else '[NO]'}")
            print()
            
            results.append({
                "name": name,
                "min": min_ch,
                "max": max_ch,
                "expected_amount": expected_amount,
                "actual_amount": metadata.channel_amount,
                "stream_amount": metadata.stream_amount,
                "mapping": dict(metadata.channel_to_stream_index),
                "sequential": is_sequential
            })
            
            # Cleanup
            try:
                api.cancel_job(response.job_id)
                print(f"  [OK] Job cancelled\n")
            except:
                pass
                
        except Exception as e:
            print(f"  [ERROR] {e}\n")
            results.append({
                "name": name,
                "error": str(e)
            })
    
    return results


def main():
    """Run all validation tests."""
    print("\n" + "="*80)
    print("  CALCULATION FORMULAS VALIDATION")
    print("  Verifying formulas against actual system responses")
    print("="*80)
    
    all_results = {}
    
    try:
        # Test 1: Frequency Bins
        freq_bins_results = validate_frequency_bins_calculation()
        all_results["frequency_bins"] = freq_bins_results
        
        # Test 2: lines_dt
        lines_dt_results = validate_lines_dt_calculation()
        all_results["lines_dt"] = lines_dt_results
        
        # Test 3: Channel Mapping
        channel_mapping_results = validate_channel_mapping()
        all_results["channel_mapping"] = channel_mapping_results
        
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Save results
    print_section("SAVING RESULTS")
    
    results_file = project_root / "reports" / "calculation_validation_results.json"
    results_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Results saved to: {results_file}")
    
    # Summary
    print_section("SUMMARY")
    
    print("Frequency Bins Test:")
    freq_matches = sum(1 for r in all_results.get("frequency_bins", []) if r.get("match", False))
    freq_total = len([r for r in all_results.get("frequency_bins", []) if "match" in r])
    print(f"  {freq_matches}/{freq_total} matches")
    
    print("\nlines_dt Test:")
    print(f"  {len(all_results.get('lines_dt', []))} NFFT values tested")
    print(f"  Overlap values calculated from responses")
    
    print("\nChannel Mapping Test:")
    mapping_sequential = sum(1 for r in all_results.get("channel_mapping", []) if r.get("sequential", False))
    mapping_total = len([r for r in all_results.get("channel_mapping", []) if "sequential" in r])
    print(f"  {mapping_sequential}/{mapping_total} sequential mappings")
    
    print(f"\n{'='*80}")
    print(f"View detailed results: {results_file}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()

