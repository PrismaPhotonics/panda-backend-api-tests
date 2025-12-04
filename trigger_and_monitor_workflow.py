#!/usr/bin/env python3
"""Script to trigger GitHub workflow and monitor the run."""

import json
import os
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: requests package required. Install with: pip install requests")
    sys.exit(1)

# GitHub API configuration
GITHUB_API_BASE = "https://api.github.com"

def get_github_token():
    """Get GitHub token from environment or mcp.json."""
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    
    if not token:
        try:
            mcp_config_path = Path.home() / ".cursor" / "mcp.json"
            if mcp_config_path.exists():
                with open(mcp_config_path, "r") as f:
                    mcp_config = json.load(f)
                    github_config = mcp_config.get("mcpServers", {}).get("github", {})
                    token = github_config.get("env", {}).get("GITHUB_PERSONAL_ACCESS_TOKEN")
        except Exception:
            pass
    
    return token

def get_repo_info():
    """Get repository owner and name from git config."""
    try:
        import subprocess
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            url = result.stdout.strip()
            if "github.com" in url:
                parts = url.replace(".git", "").split("/")
                if len(parts) >= 2:
                    owner = parts[-2].replace(":", "").split("@")[-1]
                    repo = parts[-1]
                    return owner, repo
    except Exception:
        pass
    
    return "PrismaPhotonics", "panda-backend-api-tests"

def trigger_workflow(workflow_file, ref="main", inputs=None, token=None, owner=None, repo=None):
    """Trigger a GitHub Actions workflow."""
    if not token:
        token = get_github_token()
    
    if not token:
        print("ERROR: GitHub token not found. Set GITHUB_TOKEN environment variable.")
        return None
    
    if not owner or not repo:
        owner, repo = get_repo_info()
    
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/workflows/{workflow_file}/dispatches"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {"ref": ref}
    if inputs:
        payload["inputs"] = inputs
    
    print(f"🚀 Triggering workflow '{workflow_file}' on {owner}/{repo} (branch: {ref})...")
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 204:
        print(f"✅ Workflow triggered successfully!")
        print(f"   View at: https://github.com/{owner}/{repo}/actions")
        return True
    else:
        error_msg = response.json().get("message", "Unknown error")
        print(f"❌ Failed to trigger workflow. Status: {response.status_code}")
        print(f"   Error: {error_msg}")
        return False

def get_latest_workflow_run(workflow_file, token=None, owner=None, repo=None):
    """Get the latest workflow run."""
    if not token:
        token = get_github_token()
    
    if not owner or not repo:
        owner, repo = get_repo_info()
    
    # First get workflow ID
    workflows_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/workflows"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(workflows_url, headers=headers)
    if response.status_code != 200:
        return None
    
    workflows = response.json().get("workflows", [])
    workflow_id = None
    for workflow in workflows:
        if workflow_file in workflow.get("path", ""):
            workflow_id = workflow["id"]
            break
    
    if not workflow_id:
        return None
    
    # Get latest run
    runs_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
    response = requests.get(runs_url, headers=headers, params={"per_page": 1})
    
    if response.status_code == 200:
        runs = response.json().get("workflow_runs", [])
        return runs[0] if runs else None
    
    return None

def monitor_workflow_run(run_id, token=None, owner=None, repo=None):
    """Monitor a workflow run until completion."""
    if not token:
        token = get_github_token()
    
    if not owner or not repo:
        owner, repo = get_repo_info()
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/runs/{run_id}"
    
    print(f"\n📊 Monitoring workflow run {run_id}...")
    print(f"   View at: https://github.com/{owner}/{repo}/actions/runs/{run_id}\n")
    
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed to get run status: {response.status_code}")
            break
        
        run = response.json()
        status = run.get("status")
        conclusion = run.get("conclusion")
        
        # Status indicators
        if status == "completed":
            if conclusion == "success":
                print(f"✅ Workflow completed successfully!")
            elif conclusion == "failure":
                print(f"❌ Workflow failed!")
            elif conclusion == "cancelled":
                print(f"⚠️ Workflow was cancelled!")
            else:
                print(f"⚠️ Workflow completed with status: {conclusion}")
            break
        elif status == "in_progress":
            print(f"⏳ Workflow is running... (checking again in 10 seconds)")
        elif status == "queued":
            print(f"⏳ Workflow is queued... (checking again in 10 seconds)")
        else:
            print(f"📋 Status: {status}")
        
        time.sleep(10)
    
    return run

def main():
    """Main function."""
    workflow_file = "smoke-tests.yml"
    branch = "main"
    
    # Check for arguments: workflow_file [branch]
    if len(sys.argv) > 1:
        workflow_file = sys.argv[1]
    if len(sys.argv) > 2:
        branch = sys.argv[2]
    
    token = get_github_token()
    owner, repo = get_repo_info()
    
    print(f"{'='*60}")
    print(f"Triggering and Monitoring GitHub Workflow")
    print(f"{'='*60}")
    print(f"Repository: {owner}/{repo}")
    print(f"Workflow: {workflow_file}")
    print(f"Branch: {branch}")
    print(f"{'='*60}\n")
    
    # Trigger workflow
    success = trigger_workflow(workflow_file, ref=branch, token=token, owner=owner, repo=repo)
    
    if not success:
        sys.exit(1)
    
    # Wait a bit for the run to start
    print("\n⏳ Waiting for workflow run to start...")
    time.sleep(5)
    
    # Get latest run
    latest_run = get_latest_workflow_run(workflow_file, token=token, owner=owner, repo=repo)
    
    if latest_run:
        run_id = latest_run["id"]
        print(f"\n📋 Found workflow run: {run_id}")
        print(f"   Started at: {latest_run.get('created_at', 'N/A')}")
        
        # Monitor the run
        final_run = monitor_workflow_run(run_id, token=token, owner=owner, repo=repo)
        
        if final_run:
            print(f"\n{'='*60}")
            print(f"Final Status:")
            print(f"{'='*60}")
            print(f"Status: {final_run.get('status')}")
            print(f"Conclusion: {final_run.get('conclusion', 'N/A')}")
            print(f"Duration: {final_run.get('run_duration_ms', 0) / 1000:.1f} seconds")
            print(f"URL: {final_run.get('html_url', 'N/A')}")
    else:
        print("\n⚠️ Could not find workflow run. It may take a few moments to appear.")
        print(f"   Check manually at: https://github.com/{owner}/{repo}/actions")

if __name__ == "__main__":
    main()

