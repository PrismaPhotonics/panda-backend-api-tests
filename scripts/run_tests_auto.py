"""
Automated Test Runner with Infrastructure Setup
================================================

Runs pytest with automatic infrastructure setup (port-forwards, etc.)
"""

import sys
import subprocess
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    """Run tests with automatic infrastructure setup."""
    parser = argparse.ArgumentParser(
        description="Run automated tests with infrastructure setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests (auto-setup enabled)
  python scripts/run_tests_auto.py

  # Run only unit tests (no infrastructure needed)
  python scripts/run_tests_auto.py --unit

  # Run only integration tests
  python scripts/run_tests_auto.py --integration

  # Run with specific environment
  python scripts/run_tests_auto.py --env=staging

  # Run specific test file
  python scripts/run_tests_auto.py --file=tests/integration/api/test_live_monitoring_flow.py

  # Run with verbose output
  python scripts/run_tests_auto.py -v

  # Skip infrastructure setup (for local testing)
  python scripts/run_tests_auto.py --env=local
        """
    )
    
    parser.add_argument(
        "--env",
        default="staging",
        help="Environment to test against (default: staging)"
    )
    parser.add_argument(
        "--unit",
        action="store_true",
        help="Run only unit tests (no infrastructure setup)"
    )
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run only integration tests"
    )
    parser.add_argument(
        "--file",
        help="Run specific test file"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "-s", "--show-output",
        action="store_true",
        help="Show print statements (disable capture)"
    )
    parser.add_argument(
        "--markers",
        help="Run tests matching markers (e.g., -m rabbitmq)"
    )
    parser.add_argument(
        "--tb",
        default="short",
        choices=["short", "long", "line", "native", "no"],
        help="Traceback style (default: short)"
    )
    
    args = parser.parse_args()
    
    # Build pytest command
    cmd = ["py", "-m", "pytest"]
    
    # Add environment
    cmd.extend(["--env", args.env])
    
    # Add test path
    if args.file:
        cmd.append(args.file)
    elif args.unit:
        cmd.append("tests/unit/")
    elif args.integration:
        cmd.append("tests/integration/")
    else:
        cmd.append("tests/")
    
    # Add verbose flag
    if args.verbose:
        cmd.append("-v")
    
    # Add show output flag
    if args.show_output:
        cmd.append("-s")
    
    # Add markers
    if args.markers:
        cmd.extend(["-m", args.markers])
    
    # Add traceback style
    cmd.extend(["--tb", args.tb])
    
    # Print command
    print("=" * 80)
    print("AUTOMATED TEST RUNNER")
    print("=" * 80)
    print(f"Environment: {args.env}")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 80)
    print()
    
    # Run pytest
    result = subprocess.run(cmd, cwd=project_root)
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())

