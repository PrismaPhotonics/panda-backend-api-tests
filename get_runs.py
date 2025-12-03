#!/usr/bin/env python3
"""Script to get runs from Sentinel."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from src.sentinel.main.sentinel_service import SentinelService
    from config.config_manager import ConfigManager
    import yaml
    
    # Load config
    config_path = project_root / "config" / "sentinel_config.yaml"
    config = {}
    if config_path.exists():
        with open(config_path, "r") as f:
            config = yaml.safe_load(f) or {}
    
    # Initialize service
    env = config.get("environment", "staging")
    config_manager = ConfigManager(env=env)
    service = SentinelService(config_manager, config)
    service.start()
    
    # Get active runs
    active_runs = service.get_active_runs()
    
    # Query historical runs
    historical_runs = service.query_runs(limit=10)
    
    print(f"\n{'='*60}")
    print(f"Active Runs: {len(active_runs)}")
    print(f"Historical Runs (last 10): {len(historical_runs)}")
    print(f"{'='*60}\n")
    
    if active_runs:
        print("ACTIVE RUNS:")
        print("-" * 60)
        for run_id, context in active_runs.items():
            print(f"\nRun ID: {run_id}")
            print(f"  Pipeline: {context.pipeline or 'N/A'}")
            print(f"  Environment: {context.environment or 'N/A'}")
            print(f"  Status: {context.status.value}")
            if context.start_time:
                print(f"  Start Time: {context.start_time.isoformat()}")
            print(f"  Tests: {context.total_tests()} total, {context.passed_tests()} passed, {context.failed_tests()} failed")
            if context.anomalies:
                print(f"  Anomalies: {len(context.anomalies)}")
        print()
    
    if historical_runs:
        print("\nHISTORICAL RUNS:")
        print("-" * 60)
        for run in historical_runs[:10]:
            if isinstance(run, dict):
                run_id = run.get("run_id", "unknown")
                pipeline = run.get("pipeline", "N/A")
                status = run.get("status", "N/A")
                print(f"  - {run_id}: {pipeline} ({status})")
            else:
                print(f"  - {str(run)}")
        print()
    
    if not active_runs and not historical_runs:
        print("No runs found.")
        print("\nTo get a specific run, use:")
        print("  python get_runs.py <run_id>")
    
    # If run_id provided as argument
    if len(sys.argv) > 1:
        run_id = sys.argv[1]
        print(f"\n{'='*60}")
        print(f"Details for Run: {run_id}")
        print(f"{'='*60}\n")
        
        # Try active runs first
        context = service.get_run(run_id)
        
        if context:
            print(f"Run ID: {context.run_id}")
            print(f"Pipeline: {context.pipeline or 'N/A'}")
            print(f"Environment: {context.environment or 'N/A'}")
            print(f"Branch: {context.branch or 'N/A'}")
            print(f"Status: {context.status.value}")
            
            if context.start_time:
                print(f"Start Time: {context.start_time.isoformat()}")
            if context.end_time:
                print(f"End Time: {context.end_time.isoformat()}")
                if context.duration_seconds():
                    print(f"Duration: {context.duration_seconds():.1f} seconds")
            
            print(f"\nTests:")
            print(f"  Total: {context.total_tests()}")
            print(f"  Passed: {context.passed_tests()}")
            print(f"  Failed: {context.failed_tests()}")
            print(f"  Skipped: {context.skipped_tests()}")
            
            if context.suites:
                print(f"\nSuites ({len(context.suites)}):")
                for suite_name, suite in context.suites.items():
                    print(f"  - {suite_name}: {suite.total_tests} tests")
            
            if context.anomalies:
                print(f"\nAnomalies ({len(context.anomalies)}):")
                for anomaly in context.anomalies:
                    print(f"  - [{anomaly.severity.value.upper()}] {anomaly.title}")
                    print(f"    {anomaly.description}")
        else:
            print(f"Run '{run_id}' not found.")
    
    service.stop()
    
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)

