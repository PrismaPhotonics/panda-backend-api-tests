#!/usr/bin/env python3
"""
Analyze Test Failures from GitHub Actions Run
============================================

Downloads and analyzes test failures from a GitHub Actions run.
"""

import sys
import requests
import os
from typing import Dict, List, Any
import json

GITHUB_API_BASE = "https://api.github.com"


def get_github_token() -> str:
    """Get GitHub token from environment."""
    return os.getenv("GITHUB_TOKEN", "")


def get_repo_info() -> tuple[str, str]:
    """Get repository owner and name."""
    import subprocess
    try:
        remote_url = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        if "github.com" in remote_url:
            if remote_url.startswith("https://"):
                parts = remote_url.replace("https://github.com/", "").replace(".git", "").split("/")
            elif remote_url.startswith("git@"):
                parts = remote_url.replace("git@github.com:", "").replace(".git", "").split("/")
            else:
                parts = remote_url.split("/")
            
            if len(parts) >= 2:
                return parts[0], parts[1]
    except:
        pass
    
    return "PrismaPhotonics", "panda-backend-api-tests"


def get_workflow_run_details(run_id: str) -> Dict[str, Any]:
    """Get workflow run details including jobs and steps."""
    token = get_github_token()
    owner, repo = get_repo_info()
    
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    
    # Get run details
    run_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/runs/{run_id}"
    run_response = requests.get(run_url, headers=headers)
    
    if run_response.status_code != 200:
        return {"error": f"Failed to get run: {run_response.status_code}"}
    
    run_data = run_response.json()
    
    # Get jobs
    jobs_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/runs/{run_id}/jobs"
    jobs_response = requests.get(jobs_url, headers=headers)
    jobs_data = jobs_response.json().get("jobs", []) if jobs_response.status_code == 200 else []
    
    return {
        "run": run_data,
        "jobs": jobs_data,
        "owner": owner,
        "repo": repo
    }


def analyze_failures(data: Dict[str, Any]) -> None:
    """Analyze and print failure details."""
    run = data.get("run", {})
    jobs = data.get("jobs", [])
    owner = data.get("owner", "")
    repo = data.get("repo", "")
    run_id = run.get("id", "N/A")
    
    print("="*80)
    print("TEST FAILURE ANALYSIS")
    print("="*80)
    print(f"Run ID: {run_id}")
    print(f"Workflow: {run.get('name', 'N/A')}")
    print(f"Status: {run.get('status', 'N/A')}")
    print(f"Conclusion: {run.get('conclusion', 'N/A')}")
    print(f"URL: {run.get('html_url', 'N/A')}")
    print("="*80)
    print()
    
    # Analyze jobs
    for job in jobs:
        job_name = job.get("name", "N/A")
        job_id = job.get("id", "N/A")
        job_status = job.get("status", "N/A")
        job_conclusion = job.get("conclusion", "N/A")
        
        print(f"Job: {job_name} (ID: {job_id})")
        print(f"  Status: {job_status}")
        print(f"  Conclusion: {job_conclusion}")
        print(f"  URL: https://github.com/{owner}/{repo}/actions/runs/{run_id}/job/{job_id}")
        print()
        
        # Analyze steps
        steps = job.get("steps", [])
        failed_steps = [s for s in steps if s.get("conclusion") == "failure"]
        
        if failed_steps:
            print(f"  Failed Steps: {len(failed_steps)}")
            for step in failed_steps:
                step_name = step.get("name", "N/A")
                step_number = step.get("number", "N/A")
                print(f"    [{step_number}] {step_name}")
                
                # Try to get step logs URL
                step_url = f"https://github.com/{owner}/{repo}/actions/runs/{run_id}/job/{job_id}#step:{step_number}:1"
                print(f"      Logs: {step_url}")
        else:
            print("  No failed steps")
        
        # Show all steps for context
        print()
        print("  All Steps:")
        for step in steps:
            step_name = step.get("name", "N/A")
            step_conclusion = step.get("conclusion", "N/A")
            step_status = step.get("status", "N/A")
            icon = "[OK]" if step_conclusion == "success" else "[FAIL]" if step_conclusion == "failure" else "[SKIP]" if step_conclusion == "skipped" else "[RUNNING]"
            print(f"    {icon} {step_name}: {step_status} ({step_conclusion})")
        
        print()
    
    # Summary
    total_failed_steps = sum(len([s for s in j.get("steps", []) if s.get("conclusion") == "failure"]) for j in jobs)
    print("="*80)
    print(f"SUMMARY: {total_failed_steps} failed step(s) across {len(jobs)} job(s)")
    print("="*80)
    print()
    print("Next steps:")
    print("1. Check the failed step logs using the URLs above")
    print("2. Look for pytest output showing which tests failed")
    print("3. Check the JUnit XML file in artifacts for detailed failure messages")
    print("4. Review common failure patterns:")
    print("   - MongoDB connection issues")
    print("   - Kubernetes connectivity problems")
    print("   - Timeout errors")
    print("   - Infrastructure availability")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python analyze_test_failures.py <run_id>")
        print("\nExample:")
        print("  python analyze_test_failures.py 19866607156")
        sys.exit(1)
    
    run_id = sys.argv[1]
    
    print(f"Analyzing workflow run {run_id}...")
    print()
    
    data = get_workflow_run_details(run_id)
    
    if "error" in data:
        print(f"Error: {data['error']}")
        sys.exit(1)
    
    analyze_failures(data)


if __name__ == "__main__":
    main()

