#!/usr/bin/env python3
"""
Run Read-Only Tests (Safe for "waiting for fiber" state)
=========================================================
This script runs only read-only tests that don't require configuration.
Safe to run when system is in "waiting for fiber" state.
"""

import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Run read-only tests."""
    print("=" * 80)
    print("Running Read-Only Tests")
    print("Safe for 'waiting for fiber' state")
    print("=" * 80)
    print()
    
    # Test paths to run
    test_paths = [
        "tests/integration/api/test_health_check.py",
        "tests/integration/api/test_api_endpoints_high_priority.py::TestChannelsEndpoint",
        "tests/integration/api/test_api_endpoints_additional.py::TestSensorsEndpoint",
        "tests/integration/api/test_api_endpoints_additional.py::TestLiveMetadataEndpoint",
        "tests/infrastructure/",
        "tests/data_quality/",
        "tests/unit/",
    ]
    
    # Build pytest command
    pytest_args = [
        sys.executable, "-m", "pytest",
        "-v",
        "-s",
        "--tb=short",
        "--skip-health-check",  # Skip health check (has encoding issues)
        "-k", "not configure",  # Exclude configure tests
    ]
    
    # Add test paths
    pytest_args.extend(test_paths)
    
    # Print command
    print("Command:", " ".join(pytest_args))
    print()
    print("=" * 80)
    print()
    
    # Run pytest
    try:
        result = subprocess.run(pytest_args, check=False)
        exit_code = result.returncode
        
        print()
        print("=" * 80)
        if exit_code == 0:
            print("All tests completed successfully!")
        else:
            print(f"Some tests failed (exit code: {exit_code})")
        print("=" * 80)
        
        return exit_code
        
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return 1
    except Exception as e:
        print(f"\nError running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

