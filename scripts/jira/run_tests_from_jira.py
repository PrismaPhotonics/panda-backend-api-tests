#!/usr/bin/env python3
"""
Run Tests from Jira Configuration
==================================

This script reads the Jira test configuration and runs the corresponding
automation tests.

Usage:
    # Run all mapped tests
    python scripts/jira/run_tests_from_jira.py
    
    # Run specific test plan
    python scripts/jira/run_tests_from_jira.py --test-plan PZ-14024
    
    # Run specific test
    python scripts/jira/run_tests_from_jira.py --test-id PZ-12345
    
    # Run with pytest options
    python scripts/jira/run_tests_from_jira.py --pytest-args "-v --tb=short"
"""

import argparse
import sys
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JiraTestRunner:
    """Runs automation tests based on Jira test configuration."""
    
    def __init__(self, config_file: str = "jira_test_config.json"):
        """Initialize the test runner."""
        self.config_file = project_root / config_file
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration file."""
        if not self.config_file.exists():
            logger.warning(f"Configuration file not found: {self.config_file}")
            logger.info("Run map_manual_tests_to_automation.py first to generate config")
            self.config = {"mappings": []}
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            logger.info(f"Loaded configuration from {self.config_file}")
            logger.info(f"Found {len(self.config.get('mappings', []))} test mappings")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self.config = {"mappings": []}
    
    def get_test_command(
        self, 
        automation_test: Dict[str, Any],
        pytest_args: List[str] = None
    ) -> List[str]:
        """
        Build pytest command for automation test.
        
        Args:
            automation_test: Automation test information
            pytest_args: Additional pytest arguments
            
        Returns:
            Command as list of strings
        """
        file_path = automation_test.get("file", "")
        test_function = automation_test.get("test_function", "")
        
        if not file_path:
            logger.warning("No file path in automation test")
            return []
        
        # Build command
        cmd = ["pytest"]
        
        # Add file path
        if test_function:
            cmd.append(f"{file_path}::{test_function}")
        else:
            cmd.append(file_path)
        
        # Add default flags
        default_flags = self.config.get("test_execution", {}).get("default_flags", ["-v"])
        cmd.extend(default_flags)
        
        # Add custom pytest args
        if pytest_args:
            cmd.extend(pytest_args)
        
        return cmd
    
    def run_test(self, test_id: str, pytest_args: List[str] = None) -> bool:
        """
        Run specific test by Jira test ID.
        
        Args:
            test_id: Jira test ID (e.g., "PZ-12345")
            pytest_args: Additional pytest arguments
            
        Returns:
            True if test passed
        """
        logger.info("=" * 80)
        logger.info(f"Running Test: {test_id}")
        logger.info("=" * 80)
        
        # Find mapping
        mapping = self.find_mapping(test_id)
        if not mapping:
            logger.error(f"No mapping found for {test_id}")
            return False
        
        automation_test = mapping.get("automation_test")
        if not automation_test:
            logger.error(f"No automation test found for {test_id}")
            return False
        
        # Build command
        cmd = self.get_test_command(automation_test, pytest_args)
        
        logger.info(f"Command: {' '.join(cmd)}")
        logger.info("")
        
        # Run test
        try:
            result = subprocess.run(
                cmd,
                cwd=project_root,
                capture_output=True,
                text=True
            )
            
            # Print output
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            
            # Return success
            success = result.returncode == 0
            
            if success:
                logger.info(f"✅ Test {test_id} PASSED")
            else:
                logger.error(f"❌ Test {test_id} FAILED")
            
            return success
            
        except Exception as e:
            logger.error(f"Error running test: {e}")
            return False
    
    def run_test_plan(self, test_plan_id: str, pytest_args: List[str] = None) -> Dict[str, Any]:
        """
        Run all tests in a test plan.
        
        Args:
            test_plan_id: Test plan ID (e.g., "PZ-14024")
            pytest_args: Additional pytest arguments
            
        Returns:
            Results summary
        """
        logger.info("=" * 80)
        logger.info(f"Running Test Plan: {test_plan_id}")
        logger.info("=" * 80)
        
        # Find all tests in test plan
        # Note: This requires querying Jira for test plan tests
        # For now, we'll use Xray markers to find tests
        
        from external.jira import JiraClient
        client = JiraClient()
        
        # Query for tests with Xray markers matching test plan
        # This is a simplified approach - you may need to adjust based on your setup
        jql = f'project = PZ AND issuetype = Test AND text ~ "{test_plan_id}"'
        
        try:
            issues = client.search_issues(jql, max_results=500)
            logger.info(f"Found {len(issues)} tests in test plan")
            
            results = {
                "test_plan": test_plan_id,
                "total": len(issues),
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "results": []
            }
            
            for issue in issues:
                test_id = issue.key
                logger.info(f"\nRunning: {test_id}")
                
                success = self.run_test(test_id, pytest_args)
                
                if success:
                    results["passed"] += 1
                    status = "PASSED"
                else:
                    results["failed"] += 1
                    status = "FAILED"
                
                results["results"].append({
                    "test_id": test_id,
                    "status": status
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error running test plan: {e}")
            return {"error": str(e)}
    
    def run_all_mapped_tests(self, pytest_args: List[str] = None) -> Dict[str, Any]:
        """
        Run all mapped tests from configuration.
        
        Args:
            pytest_args: Additional pytest arguments
            
        Returns:
            Results summary
        """
        logger.info("=" * 80)
        logger.info("Running All Mapped Tests")
        logger.info("=" * 80)
        
        mappings = self.config.get("mappings", [])
        
        if not mappings:
            logger.warning("No test mappings found in configuration")
            return {"error": "No mappings found"}
        
        results = {
            "total": len(mappings),
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "no_automation": 0,
            "results": []
        }
        
        for mapping in mappings:
            manual_test = mapping.get("manual_test", {})
            automation_test = mapping.get("automation_test")
            test_id = manual_test.get("key", "UNKNOWN")
            
            if not automation_test:
                logger.warning(f"Skipping {test_id} - no automation test")
                results["no_automation"] += 1
                results["results"].append({
                    "test_id": test_id,
                    "status": "SKIPPED",
                    "reason": "No automation test"
                })
                continue
            
            logger.info(f"\nRunning: {test_id}")
            
            success = self.run_test(test_id, pytest_args)
            
            if success:
                results["passed"] += 1
                status = "PASSED"
            else:
                results["failed"] += 1
                status = "FAILED"
            
            results["results"].append({
                "test_id": test_id,
                "status": status
            })
        
        return results
    
    def find_mapping(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Find mapping for test ID."""
        for mapping in self.config.get("mappings", []):
            manual_test = mapping.get("manual_test", {})
            if manual_test.get("key") == test_id:
                return mapping
        return None
    
    def print_summary(self, results: Dict[str, Any]):
        """Print results summary."""
        logger.info("\n" + "=" * 80)
        logger.info("RESULTS SUMMARY")
        logger.info("=" * 80)
        
        if "error" in results:
            logger.error(f"Error: {results['error']}")
            return
        
        logger.info(f"Total Tests: {results.get('total', 0)}")
        logger.info(f"Passed: {results.get('passed', 0)}")
        logger.info(f"Failed: {results.get('failed', 0)}")
        logger.info(f"Skipped: {results.get('skipped', 0)}")
        
        if results.get('no_automation', 0) > 0:
            logger.info(f"No Automation: {results.get('no_automation', 0)}")
        
        logger.info("=" * 80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run automation tests from Jira configuration"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="jira_test_config.json",
        help="Configuration file path"
    )
    parser.add_argument(
        "--test-id",
        type=str,
        help="Run specific test by Jira test ID"
    )
    parser.add_argument(
        "--test-plan",
        type=str,
        help="Run all tests in test plan"
    )
    parser.add_argument(
        "--pytest-args",
        type=str,
        help="Additional pytest arguments (e.g., '-v --tb=short')"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all mapped tests"
    )
    
    args = parser.parse_args()
    
    # Parse pytest args
    pytest_args = []
    if args.pytest_args:
        pytest_args = args.pytest_args.split()
    
    # Initialize runner
    runner = JiraTestRunner(config_file=args.config)
    
    # Run tests
    if args.test_id:
        success = runner.run_test(args.test_id, pytest_args)
        sys.exit(0 if success else 1)
    elif args.test_plan:
        results = runner.run_test_plan(args.test_plan, pytest_args)
        runner.print_summary(results)
        sys.exit(0 if results.get("failed", 0) == 0 else 1)
    elif args.all:
        results = runner.run_all_mapped_tests(pytest_args)
        runner.print_summary(results)
        sys.exit(0 if results.get("failed", 0) == 0 else 1)
    else:
        logger.error("Please specify --test-id, --test-plan, or --all")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

