#!/usr/bin/env python3
"""
Test individual health checks with timeout.

Usage:
    python scripts/test_health_check_individual.py [--check=all|mongodb|rabbitmq]
"""

import sys
import os
import time
import argparse

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from scripts.pre_test_health_check import PreTestHealthChecker

def test_check(checker, check_name, check_func, timeout=60):
    """Test a single health check with timeout."""
    print(f"\n{'='*80}")
    print(f"Testing: {check_name}")
    print(f"{'='*80}")
    print(f"Timeout: {timeout} seconds")
    print()
    
    start_time = time.time()
    
    try:
        result = check_func()
        elapsed = time.time() - start_time
        
        print(f"✅ Check completed in {elapsed:.2f}s")
        print(f"Status: {'PASSED' if result.status else 'FAILED'}")
        
        if result.details:
            print("\nDetails:")
            for key, value in result.details.items():
                print(f"  - {key}: {value}")
        
        if result.error:
            print(f"\n❌ Error: {result.error}")
        
        return result.status, elapsed
        
    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        print(f"\n⚠️ Check interrupted after {elapsed:.2f}s")
        return False, elapsed
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ Check failed after {elapsed:.2f}s: {e}")
        import traceback
        traceback.print_exc()
        return False, elapsed

def main():
    parser = argparse.ArgumentParser(description="Test individual health checks")
    parser.add_argument(
        "--check",
        choices=["all", "mongodb", "rabbitmq", "kubernetes", "ssh", "focus"],
        default="all",
        help="Which check to run (default: all)"
    )
    parser.add_argument(
        "--env",
        default="staging",
        help="Environment name (default: staging)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Timeout in seconds (default: 60)"
    )
    
    args = parser.parse_args()
    
    print("="*80)
    print("Individual Health Check Tester")
    print("="*80)
    print(f"Environment: {args.env}")
    print(f"Timeout: {args.timeout}s")
    print()
    
    checker = PreTestHealthChecker(environment=args.env)
    
    checks = {
        "focus": ("Focus Server API", checker.check_focus_server),
        "ssh": ("SSH", checker.check_ssh),
        "kubernetes": ("Kubernetes", checker.check_kubernetes),
        "mongodb": ("MongoDB", checker.check_mongodb),
        "rabbitmq": ("RabbitMQ", checker.check_rabbitmq),
    }
    
    if args.check == "all":
        results = {}
        for check_key, (check_name, check_func) in checks.items():
            status, elapsed = test_check(checker, check_name, check_func, args.timeout)
            results[check_key] = (status, elapsed)
            
            # If check took too long, warn
            if elapsed > args.timeout * 0.8:
                print(f"\n⚠️ WARNING: Check took {elapsed:.2f}s (close to timeout {args.timeout}s)")
        
        # Summary
        print("\n" + "="*80)
        print("Summary")
        print("="*80)
        for check_key, (status, elapsed) in results.items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {checks[check_key][0]}: {elapsed:.2f}s")
        
        all_passed = all(status for status, _ in results.values())
        return 0 if all_passed else 1
    else:
        if args.check not in checks:
            print(f"❌ Unknown check: {args.check}")
            return 1
        
        check_name, check_func = checks[args.check]
        status, elapsed = test_check(checker, check_name, check_func, args.timeout)
        
        return 0 if status else 1

if __name__ == "__main__":
    sys.exit(main())

