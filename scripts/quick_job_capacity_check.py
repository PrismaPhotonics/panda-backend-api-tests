#!/usr/bin/env python3
"""
Quick Job Capacity Check Script
=================================

סקריפט מהיר לבדיקת קיבולת המערכת ללא צורך ב-pytest.
ניתן להריץ ישירות מהטרמינל.

Usage:
    python scripts/quick_job_capacity_check.py --help
    python scripts/quick_job_capacity_check.py --environment production --max-jobs 50
    python scripts/quick_job_capacity_check.py --environment staging --quick

Author: QA Automation Team
Date: October 26, 2025
"""

import sys
import os
import time
import argparse
import logging
import json
import statistics
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Tuple
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config_manager import ConfigManager
from src.apis.focus_server_api import FocusServerAPI
from src.models.focus_server_models import ConfigureRequest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'logs/quick_capacity_check_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)


# ===================================================================
# Configuration
# ===================================================================

QUICK_TEST_JOBS = [1, 5, 10]
STANDARD_TEST_JOBS = [1, 5, 10, 20, 30]
COMPREHENSIVE_TEST_JOBS = [1, 5, 10, 20, 30, 50, 75, 100]

DEFAULT_CONFIG = {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {"height": 1000},
    "channels": {"min": 1, "max": 50},
    "frequencyRange": {"min": 0, "max": 500},
    "start_time": None,
    "end_time": None,
    "view_type": 0
}


# ===================================================================
# Helper Functions
# ===================================================================

def print_banner(text: str, char: str = "="):
    """הדפס כותרת מעוצבת."""
    width = 80
    print()
    print(char * width)
    print(text.center(width))
    print(char * width)
    print()


def print_success(message: str):
    """הדפס הודעת הצלחה."""
    try:
        print(f"✅ {message}", flush=True)
    except UnicodeEncodeError:
        print(f"[OK] {message}", flush=True)


def print_warning(message: str):
    """הדפס הודעת אזהרה."""
    try:
        print(f"⚠️ {message}", flush=True)
    except UnicodeEncodeError:
        print(f"[WARNING] {message}", flush=True)


def print_error(message: str):
    """הדפס הודעת שגיאה."""
    try:
        print(f"❌ {message}", flush=True)
    except UnicodeEncodeError:
        print(f"[ERROR] {message}", flush=True)


def print_progress_bar(iteration: int, total: int, prefix: str = '', 
                       suffix: str = '', length: int = 50, fill: str = '█'):
    """הדפס progress bar."""
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='')
    if iteration == total:
        print()


def create_single_job(api: FocusServerAPI, config: Dict[str, Any], 
                     job_num: int) -> Dict[str, Any]:
    """צור job בודד."""
    result = {
        'job_num': job_num,
        'success': False,
        'latency_ms': 0,
        'job_id': None,
        'error': None
    }
    
    try:
        start_time = time.time()
        config_request = ConfigureRequest(**config)
        response = api.configure_streaming_job(config_request)
        latency_ms = (time.time() - start_time) * 1000
        
        result['success'] = True
        result['latency_ms'] = latency_ms
        result['job_id'] = response.job_id if hasattr(response, 'job_id') else None
        
    except Exception as e:
        result['error'] = str(e)
    
    return result


def test_concurrent_jobs(api: FocusServerAPI, config: Dict[str, Any],
                        num_jobs: int) -> Dict[str, Any]:
    """בדוק יצירת jobs concurrent."""
    logger.info(f"Testing {num_jobs} concurrent jobs...")
    
    start_time = time.time()
    results = []
    
    with ThreadPoolExecutor(max_workers=min(num_jobs, 20)) as executor:
        futures = [
            executor.submit(create_single_job, api, config, i)
            for i in range(num_jobs)
        ]
        
        for i, future in enumerate(as_completed(futures)):
            results.append(future.result())
            print_progress_bar(i + 1, num_jobs, prefix='Progress:', suffix='Complete')
    
    end_time = time.time()
    
    # Calculate metrics
    successes = [r for r in results if r['success']]
    failures = [r for r in results if not r['success']]
    
    success_rate = len(successes) / len(results) if results else 0
    
    latencies = [r['latency_ms'] for r in successes]
    latency_stats = {}
    if latencies:
        sorted_latencies = sorted(latencies)
        latency_stats = {
            'mean': statistics.mean(latencies),
            'median': statistics.median(latencies),
            'p95': sorted_latencies[int(len(sorted_latencies) * 0.95)],
            'p99': sorted_latencies[int(len(sorted_latencies) * 0.99)],
            'min': min(latencies),
            'max': max(latencies)
        }
    
    return {
        'num_jobs': num_jobs,
        'total_time': end_time - start_time,
        'success_count': len(successes),
        'failure_count': len(failures),
        'success_rate': success_rate,
        'latency_stats': latency_stats,
        'job_ids': [r['job_id'] for r in successes if r['job_id']],
        'errors': [r['error'] for r in failures if r['error']]
    }


def print_test_result(result: Dict[str, Any]):
    """הדפס תוצאות בדיקה."""
    print(f"\n[*] Results for {result['num_jobs']} jobs:")
    print(f"   [+] Success Rate: {result['success_rate']:.1%}")
    print(f"   [+] Successful: {result['success_count']}/{result['num_jobs']}")
    print(f"   [-] Failed: {result['failure_count']}/{result['num_jobs']}")
    print(f"   [T] Total Time: {result['total_time']:.2f}s")
    
    if result['latency_stats']:
        stats = result['latency_stats']
        print(f"   [L] Latency:")
        print(f"      Mean: {stats['mean']:.0f}ms")
        print(f"      Median: {stats['median']:.0f}ms")
        print(f"      P95: {stats['p95']:.0f}ms")
        print(f"      P99: {stats['p99']:.0f}ms")
    
    # Print verdict
    if result['success_rate'] >= 0.95:
        verdict = "EXCELLENT"
        symbol = "[OK]"
    elif result['success_rate'] >= 0.90:
        verdict = "GOOD"
        symbol = "[OK]"
    elif result['success_rate'] >= 0.80:
        verdict = "ACCEPTABLE"
        symbol = "[WARN]"
    elif result['success_rate'] >= 0.50:
        verdict = "POOR"
        symbol = "[ERR]"
    else:
        verdict = "FAILING"
        symbol = "[ERR]"
    
    print(f"   {symbol} {verdict}")


def print_summary_table(all_results: List[Dict[str, Any]]):
    """הדפס טבלת סיכום."""
    print_banner("SUMMARY REPORT", "=")
    
    print(f"{'Jobs':<10} {'Success Rate':<15} {'Latency P95 (ms)':<20} {'Total Time (s)':<15} {'Verdict':<15}")
    print("-" * 80)
    
    for result in all_results:
        latency_p95 = result['latency_stats'].get('p95', 0) if result['latency_stats'] else 0
        
        if result['success_rate'] >= 0.90:
            verdict = "[PASS]"
        elif result['success_rate'] >= 0.80:
            verdict = "[MARGINAL]"
        else:
            verdict = "[FAIL]"
        
        print(f"{result['num_jobs']:<10} "
              f"{result['success_rate']:<15.1%} "
              f"{latency_p95:<20.0f} "
              f"{result['total_time']:<15.2f} "
              f"{verdict:<15}")
    
    print("-" * 80)
    
    # Find maximum capacity
    max_capacity = 0
    for result in all_results:
        if result['success_rate'] >= 0.90:
            max_capacity = result['num_jobs']
    
    print(f"\n[*] Maximum Capacity (90%+ success): {max_capacity} concurrent jobs")
    
    # Find breaking point
    breaking_point = None
    for i, result in enumerate(all_results):
        if result['success_rate'] < 0.80:
            breaking_point = result['num_jobs']
            break
    
    if breaking_point:
        print(f"[!] Breaking Point (< 80% success): {breaking_point} concurrent jobs")
    else:
        print(f"[OK] No breaking point found in tested range")


def save_results(all_results: List[Dict[str, Any]], output_file: str):
    """שמור תוצאות לקובץ."""
    report = {
        'test_date': datetime.now().isoformat(),
        'test_results': all_results,
        'summary': {
            'total_tests': len(all_results),
            'max_capacity': max([r['num_jobs'] for r in all_results if r['success_rate'] >= 0.90], default=0)
        }
    }
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Results saved to: {output_file}")


# ===================================================================
# Main Functions
# ===================================================================

def run_quick_check(api: FocusServerAPI, config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """הרץ בדיקה מהירה (1, 5, 10 jobs)."""
    print_banner("QUICK CAPACITY CHECK")
    print("Testing: 1, 5, 10 concurrent jobs")
    print("Estimated time: ~30 seconds")
    
    results = []
    for num_jobs in QUICK_TEST_JOBS:
        result = test_concurrent_jobs(api, config, num_jobs)
        results.append(result)
        print_test_result(result)
        time.sleep(2)  # Brief pause between tests
    
    return results


def run_standard_check(api: FocusServerAPI, config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """הרץ בדיקה סטנדרטית (1, 5, 10, 20, 30 jobs)."""
    print_banner("STANDARD CAPACITY CHECK")
    print("Testing: 1, 5, 10, 20, 30 concurrent jobs")
    print("Estimated time: ~2 minutes")
    
    results = []
    for num_jobs in STANDARD_TEST_JOBS:
        result = test_concurrent_jobs(api, config, num_jobs)
        results.append(result)
        print_test_result(result)
        
        # Stop if success rate drops below 80%
        if result['success_rate'] < 0.80:
            logger.warning(f"⚠️ Success rate dropped below 80% at {num_jobs} jobs. Stopping test.")
            break
        
        time.sleep(5)  # Longer pause for system recovery
    
    return results


def run_comprehensive_check(api: FocusServerAPI, config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """הרץ בדיקה מקיפה (1, 5, 10, 20, 30, 50, 75, 100 jobs)."""
    print_banner("COMPREHENSIVE CAPACITY CHECK")
    print("Testing: 1, 5, 10, 20, 30, 50, 75, 100 concurrent jobs")
    print("Estimated time: ~5-10 minutes")
    print("⚠️ This may stress the system significantly!")
    
    results = []
    for num_jobs in COMPREHENSIVE_TEST_JOBS:
        result = test_concurrent_jobs(api, config, num_jobs)
        results.append(result)
        print_test_result(result)
        
        # Stop if success rate drops below 50%
        if result['success_rate'] < 0.50:
            logger.warning(f"❌ Success rate dropped below 50% at {num_jobs} jobs. System breaking point reached!")
            break
        
        time.sleep(10)  # Longer pause for system recovery
    
    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Quick Job Capacity Check for Focus Server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick check (1, 5, 10 jobs)
  python scripts/quick_job_capacity_check.py --environment staging --quick

  # Standard check (1, 5, 10, 20, 30 jobs)
  python scripts/quick_job_capacity_check.py --environment production

  # Comprehensive check (up to 100 jobs)
  python scripts/quick_job_capacity_check.py --environment staging --comprehensive

  # Custom max jobs
  python scripts/quick_job_capacity_check.py --environment production --max-jobs 50
        """
    )
    
    parser.add_argument(
        '--environment', '-e',
        choices=['development', 'staging', 'production', 'new_production'],
        default='new_production',
        help='Environment to test (default: new_production)'
    )
    
    parser.add_argument(
        '--quick', '-q',
        action='store_true',
        help='Quick check (1, 5, 10 jobs)'
    )
    
    parser.add_argument(
        '--comprehensive', '-c',
        action='store_true',
        help='Comprehensive check (up to 100 jobs)'
    )
    
    parser.add_argument(
        '--max-jobs', '-m',
        type=int,
        help='Custom maximum number of jobs to test'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='capacity_check_results.json',
        help='Output file for results (default: capacity_check_results.json)'
    )
    
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save results to file'
    )
    
    args = parser.parse_args()
    
    # Print header
    print_banner(f"FOCUS SERVER CAPACITY CHECK", "#")
    print(f"Environment: {args.environment}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Initialize API
        logger.info(f"Initializing Focus Server API for environment: {args.environment}")
        config_manager = ConfigManager(env=args.environment)
        api = FocusServerAPI(config_manager)
        
        # Validate connection
        logger.info("Validating connection...")
        if not api.validate_connection():
            logger.error("Failed to connect to Focus Server!")
            sys.exit(1)
        
        logger.info("Connection validated successfully")
        
        # Run appropriate check
        if args.quick:
            results = run_quick_check(api, DEFAULT_CONFIG)
        elif args.comprehensive:
            results = run_comprehensive_check(api, DEFAULT_CONFIG)
        elif args.max_jobs:
            # Custom range
            test_jobs = [1, 5, 10, 20, 30]
            if args.max_jobs > 30:
                test_jobs.extend([50, 75, 100])
            test_jobs = [j for j in test_jobs if j <= args.max_jobs]
            
            print_banner(f"CUSTOM CAPACITY CHECK (up to {args.max_jobs})")
            results = []
            for num_jobs in test_jobs:
                result = test_concurrent_jobs(api, DEFAULT_CONFIG, num_jobs)
                results.append(result)
                print_test_result(result)
                if result['success_rate'] < 0.80:
                    break
                time.sleep(5)
        else:
            results = run_standard_check(api, DEFAULT_CONFIG)
        
        # Print summary
        print_summary_table(results)
        
        # Save results
        if not args.no_save:
            save_results(results, args.output)
        
        print_banner("CAPACITY CHECK COMPLETED", "=")
        
    except KeyboardInterrupt:
        print("\n\n[!] Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

