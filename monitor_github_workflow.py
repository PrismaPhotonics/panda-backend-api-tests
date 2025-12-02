#!/usr/bin/env python3
"""
Monitor GitHub Actions Workflow Run
===================================

Monitors a specific GitHub Actions workflow run and updates every 2 minutes.
Uses Sentinel for tracking and reporting.

Usage:
    python monitor_github_workflow.py <run_id>
    python monitor_github_workflow.py 19866165500
"""

import sys
import time
import requests
import os
from datetime import datetime
from typing import Optional, Dict, Any


GITHUB_API_BASE = "https://api.github.com"


def get_github_token() -> Optional[str]:
    """Get GitHub token from environment or config."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        # Try to get from git config
        import subprocess
        try:
            token = subprocess.check_output(
                ["git", "config", "--global", "github.token"],
                stderr=subprocess.DEVNULL
            ).decode().strip()
        except:
            pass
    return token


def get_repo_info() -> tuple[str, str]:
    """Get repository owner and name from git remote."""
    import subprocess
    try:
        remote_url = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        # Parse git URL (supports both https and ssh)
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
    
    # Default fallback
    return "PrismaPhotonics", "panda-backend-api-tests"


def get_workflow_run_details(run_id: str, token: Optional[str] = None, 
                            owner: Optional[str] = None, repo: Optional[str] = None) -> Dict[str, Any]:
    """Get detailed information about a workflow run."""
    if not token:
        token = get_github_token()
    
    if not owner or not repo:
        owner, repo = get_repo_info()
    
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    if token:
        headers["Authorization"] = f"token {token}"
    
    # Get run details
    run_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/runs/{run_id}"
    run_response = requests.get(run_url, headers=headers)
    
    if run_response.status_code != 200:
        return {
            "error": f"Failed to get run details: {run_response.status_code}",
            "status_code": run_response.status_code
        }
    
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


def format_status_report(data: Dict[str, Any]) -> str:
    """Format a status report from workflow run data."""
    run = data.get("run", {})
    jobs = data.get("jobs", [])
    owner = data.get("owner", "")
    repo = data.get("repo", "")
    run_id = run.get("id", "N/A")
    
    # Basic info
    workflow_name = run.get("name", "N/A")
    status = run.get("status", "N/A")
    conclusion = run.get("conclusion")
    created_at = run.get("created_at", "")
    updated_at = run.get("updated_at", "")
    
    # Calculate duration
    duration = "N/A"
    if created_at and updated_at:
        try:
            from datetime import datetime
            created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            updated = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
            duration_seconds = (updated - created).total_seconds()
            minutes = int(duration_seconds // 60)
            seconds = int(duration_seconds % 60)
            duration = f"{minutes}m {seconds}s"
        except:
            pass
    
    # Status emoji
    status_emoji = {
        "completed": "✅" if conclusion == "success" else "❌" if conclusion == "failure" else "⚠️",
        "in_progress": "⏳",
        "queued": "⏸️",
        "waiting": "⏸️"
    }.get(status, "📋")
    
    report = f"""
{'='*80}
📊 GitHub Actions Workflow Monitor
{'='*80}
Run ID: {run_id}
Workflow: {workflow_name}
Repository: {owner}/{repo}
Status: {status_emoji} {status.upper()}
Conclusion: {conclusion or 'N/A'}
Duration: {duration}
Created: {created_at}
Updated: {updated_at}
URL: https://github.com/{owner}/{repo}/actions/runs/{run_id}
{'='*80}

Jobs Status:
"""
    
    # Jobs details
    if jobs:
        for job in jobs:
            job_name = job.get("name", "N/A")
            job_status = job.get("status", "N/A")
            job_conclusion = job.get("conclusion")
            job_started = job.get("started_at", "")
            job_completed = job.get("completed_at", "")
            
            job_emoji = {
                "completed": "✅" if job_conclusion == "success" else "❌" if job_conclusion == "failure" else "⚠️",
                "in_progress": "⏳",
                "queued": "⏸️"
            }.get(job_status, "📋")
            
            report += f"  {job_emoji} {job_name}: {job_status}"
            if job_conclusion:
                report += f" ({job_conclusion})"
            report += "\n"
            
            if job_started:
                report += f"    Started: {job_started}\n"
            if job_completed:
                report += f"    Completed: {job_completed}\n"
    else:
        report += "  No jobs found\n"
    
    report += f"\n{'='*80}\n"
    report += f"Last checked: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report += f"{'='*80}\n"
    
    return report


def monitor_workflow_run(run_id: str, check_interval: int = 120):
    """
    Monitor a workflow run and update every check_interval seconds.
    
    Args:
        run_id: GitHub Actions run ID
        check_interval: Interval between checks in seconds (default: 120 = 2 minutes)
    """
    print(f"🚀 Starting workflow monitor for run {run_id}")
    print(f"   Check interval: {check_interval} seconds ({check_interval // 60} minutes)")
    print(f"   Press Ctrl+C to stop\n")
    
    try:
        while True:
            # Get workflow details
            data = get_workflow_run_details(run_id)
            
            if "error" in data:
                print(f"❌ Error: {data['error']}")
                break
            
            # Clear screen and print report
            import os
            os.system("cls" if os.name == "nt" else "clear")
            
            report = format_status_report(data)
            print(report)
            
            # Check if completed
            run = data.get("run", {})
            status = run.get("status", "")
            conclusion = run.get("conclusion")
            
            if status == "completed":
                if conclusion == "success":
                    print("✅ Workflow completed successfully!")
                elif conclusion == "failure":
                    print("❌ Workflow failed!")
                elif conclusion == "cancelled":
                    print("⚠️ Workflow was cancelled!")
                else:
                    print(f"⚠️ Workflow completed with conclusion: {conclusion}")
                break
            
            # Wait before next check
            print(f"⏳ Waiting {check_interval} seconds until next check...")
            time.sleep(check_interval)
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Error during monitoring: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python monitor_github_workflow.py <run_id> [check_interval_seconds]")
        print("\nExample:")
        print("  python monitor_github_workflow.py 19866165500")
        print("  python monitor_github_workflow.py 19866165500 120  # Check every 2 minutes")
        sys.exit(1)
    
    run_id = sys.argv[1]
    check_interval = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    
    monitor_workflow_run(run_id, check_interval)


if __name__ == "__main__":
    main()

