#!/usr/bin/env python3
"""
Count remaining unmapped Xray tests.
"""

# All Xray IDs that are now implemented with markers
IMPLEMENTED_XRAY_IDS = {
    # Infrastructure (3)
    "PZ-13898", "PZ-13899", "PZ-13900",
    
    # SingleChannel (27)
    "PZ-13814", "PZ-13815", "PZ-13816", "PZ-13817", "PZ-13818", "PZ-13819",
    "PZ-13820", "PZ-13821", "PZ-13822", "PZ-13823", "PZ-13824",
    "PZ-13832", "PZ-13833", "PZ-13834", "PZ-13835", "PZ-13836", "PZ-13837",
    "PZ-13852", "PZ-13853", "PZ-13854", "PZ-13855", "PZ-13857", "PZ-13858",
    "PZ-13859", "PZ-13860", "PZ-13861", "PZ-13862",
    
    # Configuration & Validation (20)
    "PZ-13873", "PZ-13874", "PZ-13875", "PZ-13876", "PZ-13877", "PZ-13878",
    "PZ-13901", "PZ-13902", "PZ-13903", "PZ-13904", "PZ-13905", "PZ-13906",
    "PZ-13907", "PZ-13908", "PZ-13909", "PZ-13910", "PZ-13911", "PZ-13912",
    "PZ-13913", "PZ-13914",
    
    # API Endpoints (6)
    "PZ-13762", "PZ-13895", "PZ-13896", "PZ-13897",
    
    # Historic Playback (9)
    "PZ-13863", "PZ-13864", "PZ-13865", "PZ-13866", "PZ-13867", "PZ-13868",
    "PZ-13869", "PZ-13870", "PZ-13871", "PZ-13872",
    
    # Live Monitoring (3)
    "PZ-13784", "PZ-13785", "PZ-13786",
    
    # Performance (3)
    "PZ-13920", "PZ-13921", "PZ-13922",
    
    # Data Availability (3)
    "PZ-13547", "PZ-13548",
    
    # Bugs (3)
    "PZ-13984", "PZ-13985", "PZ-13986",
}

# All Xray IDs from DOC (113 total)
ALL_XRAY_IDS_FROM_DOC = [
    # Lower range tests
    "PZ-13547", "PZ-13548", "PZ-13598", "PZ-13602",
    "PZ-13683", "PZ-13686",
    "PZ-13762",
    "PZ-13784", "PZ-13785", "PZ-13786", "PZ-13787", "PZ-13788", "PZ-13789",
    "PZ-13790", "PZ-13791", "PZ-13792", "PZ-13793", "PZ-13794", "PZ-13795",
    "PZ-13796", "PZ-13797", "PZ-13798", "PZ-13799", "PZ-13800",
    
    # Visualization (OUT OF SCOPE - 12 tests)
    "PZ-13801", "PZ-13802", "PZ-13803", "PZ-13804", "PZ-13805", "PZ-13806",
    "PZ-13807", "PZ-13808", "PZ-13809", "PZ-13810", "PZ-13811", "PZ-13812",
    
    # SingleChannel (27)
    "PZ-13814", "PZ-13815", "PZ-13816", "PZ-13817", "PZ-13818", "PZ-13819",
    "PZ-13820", "PZ-13821", "PZ-13822", "PZ-13823", "PZ-13824",
    "PZ-13832", "PZ-13833", "PZ-13834", "PZ-13835", "PZ-13836", "PZ-13837",
    "PZ-13852", "PZ-13853", "PZ-13854", "PZ-13855", "PZ-13857", "PZ-13858",
    "PZ-13859", "PZ-13860", "PZ-13861", "PZ-13862",
    
    # Historic Playback (9)
    "PZ-13863", "PZ-13864", "PZ-13865", "PZ-13866", "PZ-13867", "PZ-13868",
    "PZ-13869", "PZ-13870", "PZ-13871", "PZ-13872",
    
    # Configuration (11)
    "PZ-13873", "PZ-13874", "PZ-13875", "PZ-13876", "PZ-13877", "PZ-13878",
    "PZ-13879", "PZ-13880",
    
    # API/Infrastructure (21)
    "PZ-13895", "PZ-13896", "PZ-13897", "PZ-13898", "PZ-13899", "PZ-13900",
    "PZ-13901", "PZ-13902", "PZ-13903", "PZ-13904", "PZ-13905", "PZ-13906",
    "PZ-13907", "PZ-13908", "PZ-13909", "PZ-13910", "PZ-13911", "PZ-13912",
    "PZ-13913", "PZ-13914",
    
    # Performance/Bugs
    "PZ-13920", "PZ-13921", "PZ-13922",
    "PZ-13984", "PZ-13985", "PZ-13986",
]

# Visualization tests (OUT OF SCOPE)
VISUALIZATION_OUT_OF_SCOPE = {
    "PZ-13801", "PZ-13802", "PZ-13803", "PZ-13804", "PZ-13805", "PZ-13806",
    "PZ-13807", "PZ-13808", "PZ-13809", "PZ-13810", "PZ-13811", "PZ-13812"
}

def main():
    print("="*80)
    print("XRAY TESTS STATUS ANALYSIS")
    print("="*80)
    print()
    
    total_tests = len(ALL_XRAY_IDS_FROM_DOC)
    implemented = len(IMPLEMENTED_XRAY_IDS)
    
    # Find not implemented
    not_implemented = set(ALL_XRAY_IDS_FROM_DOC) - IMPLEMENTED_XRAY_IDS
    
    # Separate out-of-scope
    not_implemented_in_scope = not_implemented - VISUALIZATION_OUT_OF_SCOPE
    
    print(f"Total Xray Tests in DOC:     {total_tests}")
    print(f"Implemented in Automation:   {implemented}")
    print(f"Not Implemented (all):       {len(not_implemented)}")
    print(f"Out of Scope (Visualization): {len(VISUALIZATION_OUT_OF_SCOPE)}")
    print(f"Not Implemented (in scope):  {len(not_implemented_in_scope)}")
    print()
    
    # Calculate coverage
    in_scope_total = total_tests - len(VISUALIZATION_OUT_OF_SCOPE)
    coverage_pct = (implemented / in_scope_total) * 100 if in_scope_total > 0 else 0
    
    print(f"Coverage (excluding out-of-scope): {coverage_pct:.1f}%")
    print()
    
    print("="*80)
    print("NOT IMPLEMENTED (IN SCOPE):")
    print("="*80)
    
    for test_id in sorted(not_implemented_in_scope):
        print(f"  - {test_id}")
    
    print()
    print(f"Total remaining: {len(not_implemented_in_scope)} tests")
    print("="*80)
    
    return not_implemented_in_scope

if __name__ == '__main__':
    remaining = main()

