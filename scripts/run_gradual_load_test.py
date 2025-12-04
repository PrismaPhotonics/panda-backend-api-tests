#!/usr/bin/env python3
"""
Gradual Live Job Load Test Runner
==================================

Standalone script to run the gradual Live Job load test.

This test gradually increases the number of concurrent Live Jobs:
- Starts with 5 jobs
- Adds 5 jobs every 10 seconds
- Continues until reaching 50 jobs
- Verifies system health at each step
- Cleans up all jobs at the end

Usage:
    # Run with default settings (5 → 50 jobs, +5 every 10s)
    python scripts/run_gradual_load_test.py
    
    # Run with custom settings
    python scripts/run_gradual_load_test.py --max-jobs 30 --step 3 --interval 5
    
    # Run on production environment
    python scripts/run_gradual_load_test.py --env production
    
    # Quick test (smaller scale)
    python scripts/run_gradual_load_test.py --quick

Examples:
    # Full load test (staging)
    python scripts/run_gradual_load_test.py --env staging
    
    # Quick CI test
    python scripts/run_gradual_load_test.py --quick --env staging
    
    # Custom configuration
    python scripts/run_gradual_load_test.py --initial 3 --step 3 --max-jobs 30 --interval 5

Author: QA Automation Architect
Date: 2025-11-30
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.config_manager import ConfigManager

# Configure logging
def setup_logging(log_level: str = "INFO", log_file: bool = True):
    """Setup logging configuration."""
    
    # Create logs directory if needed
    logs_dir = PROJECT_ROOT / "logs" / "load_tests"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Handlers
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level))
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    ))
    handlers.append(console_handler)
    
    # File handler
    if log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_path = logs_dir / f"gradual_load_{timestamp}.log"
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        handlers.append(file_handler)
        print(f"📝 Log file: {log_path}")
    
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=handlers,
        force=True
    )
    
    return logging.getLogger(__name__)


def print_banner():
    """Print test banner."""
    print()
    print("=" * 70)
    print("  📈 GRADUAL LIVE JOB LOAD TEST")
    print("=" * 70)
    print("  Tests system stability as load increases step by step")
    print("=" * 70)
    print()


def print_config(args):
    """Print configuration summary."""
    print("📋 Configuration:")
    print(f"   • Environment: {args.env}")
    print(f"   • Initial Jobs: {args.initial}")
    print(f"   • Step Increment: +{args.step} jobs")
    print(f"   • Step Interval: {args.interval} seconds")
    print(f"   • Maximum Jobs: {args.max_jobs}")
    print()
    
    # Calculate expected duration
    num_steps = (args.max_jobs - args.initial) // args.step + 1
    estimated_minutes = (num_steps * args.interval) / 60 + 2  # +2 for cleanup
    print(f"   ⏱️  Estimated Duration: ~{estimated_minutes:.1f} minutes")
    print(f"   📊 Expected Steps: {num_steps}")
    print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Gradual Live Job Load Test",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_gradual_load_test.py
  python scripts/run_gradual_load_test.py --env staging --max-jobs 30
  python scripts/run_gradual_load_test.py --quick
        """
    )
    
    # Environment
    parser.add_argument(
        "--env", "-e",
        default="staging",
        help="Environment to test (staging/production)"
    )
    
    # Load configuration
    parser.add_argument(
        "--initial", "-i",
        type=int,
        default=5,
        help="Initial number of jobs (default: 5)"
    )
    parser.add_argument(
        "--step", "-s",
        type=int,
        default=5,
        help="Jobs to add per step (default: 5)"
    )
    parser.add_argument(
        "--max-jobs", "-m",
        type=int,
        default=50,
        help="Maximum number of jobs (default: 50)"
    )
    parser.add_argument(
        "--interval", "-t",
        type=int,
        default=10,
        help="Seconds between steps (default: 10)"
    )
    
    # Quick mode
    parser.add_argument(
        "--quick", "-q",
        action="store_true",
        help="Quick test mode (2→10 jobs, +2 every 5s)"
    )
    
    # Logging
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Log level (default: INFO)"
    )
    parser.add_argument(
        "--no-log-file",
        action="store_true",
        help="Don't create log file"
    )
    
    args = parser.parse_args()
    
    # Quick mode overrides
    if args.quick:
        args.initial = 2
        args.step = 2
        args.max_jobs = 10
        args.interval = 5
    
    # Setup logging
    logger = setup_logging(args.log_level, not args.no_log_file)
    
    # Print banner and config
    print_banner()
    print_config(args)
    
    # Import after path setup
    from be_focus_server_tests.load.test_gradual_live_job_load import (
        GradualLiveJobLoadTester, 
        GradualLoadConfig,
        HealthCheckResult
    )
    
    try:
        # Create configuration
        config = ConfigManager(env=args.env)
        
        # Create custom load config
        load_config = GradualLoadConfig()
        load_config.INITIAL_JOBS = args.initial
        load_config.STEP_INCREMENT = args.step
        load_config.MAX_JOBS = args.max_jobs
        load_config.STEP_INTERVAL_SECONDS = args.interval
        
        # Create tester
        tester = GradualLiveJobLoadTester(config, load_config)
        
        # Run test
        test_name = f"Gradual Load Test ({args.env.upper()})"
        if args.quick:
            test_name += " - Quick Mode"
        
        result = tester.run_gradual_load_test(test_name=test_name)
        
        # Print final summary
        print()
        print("=" * 70)
        
        if result.final_health_status == HealthCheckResult.HEALTHY:
            print("✅ TEST PASSED - System remained healthy throughout")
            exit_code = 0
        elif result.final_health_status == HealthCheckResult.DEGRADED:
            print("⚠️  TEST PASSED (with warnings) - System was degraded")
            exit_code = 0
        else:
            print("❌ TEST FAILED - System became unhealthy")
            exit_code = 1
        
        print("=" * 70)
        print()
        
        # Summary stats
        print("📊 Summary:")
        print(f"   • Max Jobs Reached: {result.max_jobs_reached}")
        print(f"   • Total Created: {result.total_jobs_created}")
        print(f"   • Total Failed: {result.total_jobs_failed}")
        print(f"   • Duration: {result.duration_seconds:.1f}s")
        print()
        
        # Health stats
        print("🏥 Health Status per Step:")
        for step in result.step_metrics:
            icon = "✅" if step.health_status == HealthCheckResult.HEALTHY else (
                "⚠️" if step.health_status == HealthCheckResult.DEGRADED else "❌"
            )
            print(
                f"   Step {step.step_number:2d}: {step.actual_jobs:2d} jobs | "
                f"{step.success_rate:.0f}% success | {icon}"
            )
        print()
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

