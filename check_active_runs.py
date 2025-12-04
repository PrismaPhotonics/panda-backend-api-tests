#!/usr/bin/env python3
"""Quick script to check active runs in Sentinel."""

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
    
    print(f"\n{'='*60}")
    print(f"Active Automation Runs: {len(active_runs)}")
    print(f"{'='*60}\n")
    
    if not active_runs:
        print("No active runs found.")
    else:
        for run_id, context in active_runs.items():
            print(f"Run ID: {run_id}")
            print(f"  Pipeline: {context.pipeline or 'N/A'}")
            print(f"  Environment: {context.environment or 'N/A'}")
            print(f"  Status: {context.status.value}")
            if context.start_time:
                print(f"  Start Time: {context.start_time.isoformat()}")
            print(f"  Total Tests: {context.total_tests()}")
            print(f"  Passed: {context.passed_tests()}")
            print(f"  Failed: {context.failed_tests()}")
            if context.anomalies:
                print(f"  Anomalies: {len(context.anomalies)}")
            print()
    
    service.stop()
    
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)

