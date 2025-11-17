#!/usr/bin/env python3
"""
Get Test Plan Tests from Xray
===============================

Fetches test keys from a Test Plan using Xray GraphQL API.

Usage:
    python scripts/xray/get_test_plan_tests.py --test-plan PZ-14024
    python scripts/xray/get_test_plan_tests.py --test-plan PZ-14024 --output testkeys.txt
    python scripts/xray/get_test_plan_tests.py --test-plan PZ-14024 --pytest-expression
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any

import requests

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class XrayTestPlanFetcher:
    """Fetches test keys from Xray Test Plan."""
    
    def __init__(self):
        """Initialize the fetcher."""
        self.api_url = "https://xray.cloud.getxray.app/api/v2"
        self.client_id = os.getenv("XRAY_CLIENT_ID")
        self.client_secret = os.getenv("XRAY_CLIENT_SECRET")
        
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Missing XRAY_CLIENT_ID or XRAY_CLIENT_SECRET environment variables"
            )
    
    def authenticate(self) -> str:
        """Authenticate and get access token."""
        logger.info("Authenticating with Xray Cloud...")
        
        response = requests.post(
            f"{self.api_url}/authenticate",
            json={
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
        )
        response.raise_for_status()
        
        token = response.text.strip('"')
        logger.info("✅ Authentication successful")
        
        return token
    
    def get_test_plan_tests(self, test_plan_key: str, limit: int = 2000) -> List[str]:
        """
        Get test keys from Test Plan using GraphQL API.
        
        Args:
            test_plan_key: Test Plan key (e.g., "PZ-14024")
            limit: Maximum number of tests to fetch
            
        Returns:
            List of test keys (e.g., ["PZ-12345", "PZ-12346"])
        """
        logger.info(f"Fetching tests from Test Plan: {test_plan_key}")
        
        token = self.authenticate()
        
        # GraphQL query to get tests from Test Plan
        query = """
        query GetTestPlanTests($testPlanKey: String!, $limit: Int!) {
            getTestPlan(issueIdOrKey: $testPlanKey) {
                issueId
                jira(fields: ["key", "summary"])
                tests(limit: $limit) {
                    total
                    results {
                        issueId
                        testType {
                            name
                        }
                        issue {
                            key
                            summary
                        }
                    }
                }
            }
        }
        """
        
        variables = {
            "testPlanKey": test_plan_key,
            "limit": limit
        }
        
        response = requests.post(
            f"{self.api_url}/graphql",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={
                "query": query,
                "variables": variables
            }
        )
        
        response.raise_for_status()
        result = response.json()
        
        # Check for GraphQL errors
        if "errors" in result:
            logger.error(f"GraphQL errors: {result['errors']}")
            raise ValueError(f"GraphQL query failed: {result['errors']}")
        
        # Extract test keys
        test_plan_data = result.get("data", {}).get("getTestPlan")
        if not test_plan_data:
            logger.warning(f"Test Plan {test_plan_key} not found or empty")
            return []
        
        tests = test_plan_data.get("tests", {}).get("results", [])
        test_keys = [test["issue"]["key"] for test in tests if test.get("issue", {}).get("key")]
        
        total = test_plan_data.get("tests", {}).get("total", 0)
        logger.info(f"✅ Found {len(test_keys)} tests (total: {total})")
        
        return test_keys
    
    def generate_pytest_expression(self, test_keys: List[str]) -> str:
        """
        Generate pytest -k expression from test keys.
        
        Args:
            test_keys: List of test keys
            
        Returns:
            pytest -k expression string
        """
        if not test_keys:
            return "True"  # Run all tests if no keys
        
        # For pytest-xray, we can use markers
        # Format: "PZ-12345 or PZ-12346 or ..."
        expression = " or ".join(test_keys)
        
        return expression
    
    def generate_pytest_markers(self, test_keys: List[str]) -> str:
        """
        Generate pytest marker expression from test keys.
        
        Args:
            test_keys: List of test keys
            
        Returns:
            pytest -m expression string (for pytest-xray)
        """
        if not test_keys:
            return ""
        
        # Format: "xray(PZ-12345) or xray(PZ-12346) or ..."
        markers = [f"xray({key})" for key in test_keys]
        expression = " or ".join(markers)
        
        return expression


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Get test keys from Xray Test Plan"
    )
    parser.add_argument(
        "--test-plan",
        type=str,
        required=True,
        help="Test Plan key (e.g., PZ-14024)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file for test keys (one per line)"
    )
    parser.add_argument(
        "--pytest-expression",
        action="store_true",
        help="Generate pytest -k expression"
    )
    parser.add_argument(
        "--pytest-markers",
        action="store_true",
        help="Generate pytest -m expression (for pytest-xray)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=2000,
        help="Maximum number of tests to fetch (default: 2000)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    
    args = parser.parse_args()
    
    try:
        fetcher = XrayTestPlanFetcher()
        test_keys = fetcher.get_test_plan_tests(args.test_plan, limit=args.limit)
        
        if not test_keys:
            logger.warning("No tests found in Test Plan")
            sys.exit(1)
        
        # Output options
        if args.json:
            output = json.dumps({
                "test_plan": args.test_plan,
                "test_keys": test_keys,
                "count": len(test_keys)
            }, indent=2)
            print(output)
        elif args.pytest_expression:
            expression = fetcher.generate_pytest_expression(test_keys)
            print(expression)
        elif args.pytest_markers:
            expression = fetcher.generate_pytest_markers(test_keys)
            print(expression)
        elif args.output:
            # Write to file
            output_path = Path(args.output)
            output_path.write_text("\n".join(test_keys) + "\n")
            logger.info(f"✅ Test keys written to: {output_path}")
        else:
            # Default: print one per line
            for key in test_keys:
                print(key)
        
        logger.info(f"\n✅ Total: {len(test_keys)} tests")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

