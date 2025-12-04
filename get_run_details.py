#!/usr/bin/env python3
"""Get detailed information about a GitHub Actions workflow run."""

import json
import os
import sys
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

def get_workflow_run_details(run_id, include_logs=True):
    """Get detailed information about a workflow run."""
    token = get_github_token()
    if not token:
        print("ERROR: GitHub token not found. Set GITHUB_TOKEN environment variable.")
        return None
    
    owner, repo = get_repo_info()
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Get run details
    run_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/runs/{run_id}"
    response = requests.get(run_url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get run details: {response.status_code}")
        print(f"   Error: {response.json().get('message', 'Unknown error')}")
        return None
    
    run_data = response.json()
    
    # Get jobs for this run
    jobs_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/runs/{run_id}/jobs"
    response = requests.get(jobs_url, headers=headers)
    
    if response.status_code != 200:
        print(f"⚠️ Failed to get jobs: {response.status_code}")
        jobs_data = []
    else:
        jobs_data = response.json().get("jobs", [])
    
    # Format output
    result = []
    
    # Run summary
    workflow_name = run_data.get("workflow_id") and f"workflow-{run_data['workflow_id']}" or "N/A"
    status = run_data.get("status", "unknown")
    conclusion = run_data.get("conclusion", "N/A")
    
    # Calculate duration
    created_at = run_data.get("created_at")
    updated_at = run_data.get("updated_at")
    duration_sec = 0
    if created_at and updated_at:
        from datetime import datetime
        start = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        end = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        duration_sec = (end - start).total_seconds()
    
    duration_min = duration_sec / 60
    
    summary = f"""📊 Workflow Run Details
{'='*60}
Workflow: {workflow_name}
Run ID: {run_id}
Status: {status}
Conclusion: {conclusion}
Duration: {duration_sec:.1f} seconds ({duration_min:.1f} minutes)
Branch: {run_data.get('head_branch', 'N/A')}
Commit: {run_data.get('head_sha', 'N/A')[:8]}
URL: {run_data.get('html_url', 'N/A')}
"""
    result.append(summary)
    
    # Jobs details
    if jobs_data:
        result.append(f"\n📋 Jobs ({len(jobs_data)} total):\n")
        
        for job in jobs_data:
            job_name = job.get("name", "N/A")
            job_status = job.get("status", "unknown")
            job_conclusion = job.get("conclusion", "N/A")
            
            # Calculate job duration
            job_start = job.get("started_at")
            job_end = job.get("completed_at")
            job_duration = "N/A"
            if job_start and job_end:
                from datetime import datetime
                start = datetime.fromisoformat(job_start.replace("Z", "+00:00"))
                end = datetime.fromisoformat(job_end.replace("Z", "+00:00"))
                job_duration_sec = (end - start).total_seconds()
                job_duration = f"{job_duration_sec:.1f}s ({job_duration_sec/60:.1f}m)"
            
            # Status icon
            if job_conclusion == "success":
                icon = "✅"
            elif job_conclusion == "failure":
                icon = "❌"
            elif job_conclusion == "cancelled":
                icon = "⚠️"
            else:
                icon = "⏳"
            
            result.append(f"{icon} Job: {job_name}")
            result.append(f"   Status: {job_status} | Conclusion: {job_conclusion}")
            result.append(f"   Duration: {job_duration}")
            result.append(f"   URL: {job.get('html_url', 'N/A')}")
            
            # Steps
            steps = job.get("steps", [])
            if steps:
                result.append(f"   Steps ({len(steps)}):")
                for step in steps:
                    step_name = step.get("name", "N/A")
                    step_status = step.get("status", "unknown")
                    step_conclusion = step.get("conclusion", "N/A")
                    
                    # Calculate step duration
                    step_start = step.get("started_at")
                    step_end = step.get("completed_at")
                    step_duration = "N/A"
                    if step_start and step_end:
                        from datetime import datetime
                        start = datetime.fromisoformat(step_start.replace("Z", "+00:00"))
                        end = datetime.fromisoformat(step_end.replace("Z", "+00:00"))
                        step_duration_sec = (end - start).total_seconds()
                        step_duration = f"{step_duration_sec:.1f}s"
                    
                    # Step icon
                    if step_conclusion == "success":
                        step_icon = "  ✅"
                    elif step_conclusion == "failure":
                        step_icon = "  ❌"
                    elif step_conclusion == "cancelled":
                        step_icon = "  ⚠️"
                    else:
                        step_icon = "  ⏳"
                    
                    result.append(f"{step_icon} {step_name}")
                    result.append(f"      Status: {step_status} | Conclusion: {step_conclusion} | Duration: {step_duration}")
                    
                    # Get logs for failed steps
                    if include_logs and step_conclusion == "failure":
                        log_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/jobs/{job.get('id')}/logs"
                        log_response = requests.get(log_url, headers=headers)
                        if log_response.status_code == 200:
                            log_lines = log_response.text.split("\n")
                            error_lines = [line for line in log_lines if any(keyword in line.lower() for keyword in ['error', 'failed', 'exception', 'traceback', 'fatal', 'critical'])]
                            if error_lines:
                                result.append(f"      ❌ Recent Errors ({len(error_lines)} found):")
                                for error_line in error_lines[-15:]:
                                    display_line = error_line[:150] + "..." if len(error_line) > 150 else error_line
                                    result.append(f"        {display_line}")
                            else:
                                result.append(f"      📋 Last Log Lines:")
                                for log_line in log_lines[-20:]:
                                    display_line = log_line[:150] + "..." if len(log_line) > 150 else log_line
                                    result.append(f"        {display_line}")
            
            result.append("")
    
    # Summary statistics
    total_jobs = len(jobs_data)
    successful_jobs = len([j for j in jobs_data if j.get("conclusion") == "success"])
    failed_jobs = len([j for j in jobs_data if j.get("conclusion") == "failure"])
    cancelled_jobs = len([j for j in jobs_data if j.get("conclusion") == "cancelled"])
    
    total_steps = sum(len(j.get("steps", [])) for j in jobs_data)
    successful_steps = sum(len([s for s in j.get("steps", []) if s.get("conclusion") == "success"]) for j in jobs_data)
    failed_steps = sum(len([s for s in j.get("steps", []) if s.get("conclusion") == "failure"]) for j in jobs_data)
    
    result.append(f"\n📊 Summary Statistics:")
    result.append(f"Total Jobs: {total_jobs}")
    result.append(f"  ✅ Successful: {successful_jobs}")
    result.append(f"  ❌ Failed: {failed_jobs}")
    if cancelled_jobs > 0:
        result.append(f"  ⚠️ Cancelled: {cancelled_jobs}")
    result.append(f"\nTotal Steps: {total_steps}")
    result.append(f"  ✅ Successful: {successful_steps}")
    result.append(f"  ❌ Failed: {failed_steps}")
    
    # Overall conclusion
    if conclusion == "success":
        result.append(f"\n🎉 Overall: SUCCESS\n")
    elif conclusion == "failure":
        result.append(f"\n💥 Overall: FAILURE\n")
        if failed_jobs > 0:
            result.append(f"\n❌ Failed Jobs Details:\n")
            for job in jobs_data:
                if job.get("conclusion") == "failure":
                    result.append(f"  • {job.get('name', 'N/A')}\n")
                    failed_steps_in_job = [s for s in job.get("steps", []) if s.get("conclusion") == "failure"]
                    if failed_steps_in_job:
                        result.append(f"    Failed Steps:\n")
                        for step in failed_steps_in_job:
                            result.append(f"      - {step.get('name', 'N/A')}\n")
    
    return "\n".join(result)

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: get_run_details.py <run_id> [--no-logs]")
        print("Example: get_run_details.py 19862437272")
        sys.exit(1)
    
    run_id = sys.argv[1]
    include_logs = "--no-logs" not in sys.argv
    
    details = get_workflow_run_details(run_id, include_logs=include_logs)
    if details:
        print(details)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()

