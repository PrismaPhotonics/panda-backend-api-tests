#!/usr/bin/env python3
"""
Analyze xray_tests_list.txt and compare with implemented tests.
"""

# All implemented Xray IDs
IMPLEMENTED = {
    # Infrastructure
    "PZ-13602", "PZ-13898", "PZ-13899", "PZ-13900",
    
    # SingleChannel
    "PZ-13814", "PZ-13815", "PZ-13816", "PZ-13817", "PZ-13818", "PZ-13819",
    "PZ-13820", "PZ-13821", "PZ-13822", "PZ-13823", "PZ-13824",
    "PZ-13832", "PZ-13833", "PZ-13834", "PZ-13835", "PZ-13836", "PZ-13837",
    "PZ-13852", "PZ-13853", "PZ-13854", "PZ-13855", "PZ-13857", "PZ-13858",
    "PZ-13859", "PZ-13860", "PZ-13861", "PZ-13862",
    
    # Configuration
    "PZ-13873", "PZ-13874", "PZ-13875", "PZ-13876", "PZ-13877", "PZ-13878",
    "PZ-13901", "PZ-13902", "PZ-13903", "PZ-13904", "PZ-13905", "PZ-13906",
    "PZ-13907", "PZ-13908", "PZ-13909", "PZ-13910", "PZ-13911", "PZ-13912",
    "PZ-13913", "PZ-13914",
    
    # Historic
    "PZ-13863", "PZ-13864", "PZ-13865", "PZ-13866", "PZ-13867", "PZ-13868",
    "PZ-13869", "PZ-13870", "PZ-13871", "PZ-13872",
    
    # Live & ROI
    "PZ-13784", "PZ-13785", "PZ-13786", "PZ-13787", "PZ-13788", "PZ-13789",
    "PZ-13790", "PZ-13791", "PZ-13792", "PZ-13793", "PZ-13794", "PZ-13795",
    "PZ-13796", "PZ-13797", "PZ-13798", "PZ-13799", "PZ-13800",
    
    # API
    "PZ-13762", "PZ-13895", "PZ-13896", "PZ-13897",
    
    # Performance
    "PZ-13920", "PZ-13921", "PZ-13922",
    
    # Data
    "PZ-13547", "PZ-13548", "PZ-13598", "PZ-13683", "PZ-13686",
    
    # Bugs
    "PZ-13984", "PZ-13985", "PZ-13986",
    
    # Stress
    "PZ-13880",
}

# Visualization - OUT OF SCOPE
OUT_OF_SCOPE = {
    "PZ-13801", "PZ-13802", "PZ-13803", "PZ-13804", "PZ-13805", "PZ-13806",
    "PZ-13807", "PZ-13808", "PZ-13809", "PZ-13810", "PZ-13811", "PZ-13812"
}

def main():
    # Read the list
    with open("xray_tests_list.txt", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    all_tests = []
    for line in lines:
        line = line.strip()
        if line and ',' in line:
            parts = line.split(',', 1)
            test_id = parts[0].strip()
            summary = parts[1].strip() if len(parts) > 1 else ""
            all_tests.append((test_id, summary))
    
    print("="*80)
    print("XRAY TESTS ANALYSIS FROM xray_tests_list.txt")
    print("="*80)
    print(f"\nTotal tests in list: {len(all_tests)}")
    
    # Find not implemented
    not_impl = []
    for test_id, summary in all_tests:
        if test_id not in IMPLEMENTED and test_id not in OUT_OF_SCOPE:
            not_impl.append((test_id, summary))
    
    print(f"Implemented: {len(IMPLEMENTED)}")
    print(f"Out of Scope: {len(OUT_OF_SCOPE)}")
    print(f"Not Implemented: {len(not_impl)}")
    
    if not_impl:
        print("\n" + "="*80)
        print("NOT IMPLEMENTED:")
        print("="*80)
        for test_id, summary in not_impl:
            print(f"{test_id}: {summary}")
    
    # Coverage
    in_scope = len(all_tests) - len(OUT_OF_SCOPE)
    coverage = (len(IMPLEMENTED) / in_scope * 100) if in_scope > 0 else 0
    
    print("\n" + "="*80)
    print(f"Coverage: {coverage:.1f}% ({len(IMPLEMENTED)}/{in_scope})")
    print("="*80)

if __name__ == '__main__':
    main()

