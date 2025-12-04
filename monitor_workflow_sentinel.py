#!/usr/bin/env python3
"""
Monitor GitHub Actions Workflow Run using Sentinel MCP
======================================================

Uses Sentinel MCP server tools to monitor a GitHub Actions workflow run.
Checks every 2 minutes and provides updates.

Usage:
    python monitor_workflow_sentinel.py <run_id>
    python monitor_workflow_sentinel.py 19866165500
"""

import sys
import time
import asyncio
from datetime import datetime
import os
import io

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Try to use MCP Sentinel if available
try:
    # Import MCP client
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("⚠️ MCP not available. Using direct API calls instead.")


async def monitor_with_sentinel(run_id: str, check_interval: int = 120):
    """
    Monitor workflow run using Sentinel MCP server.
    
    Args:
        run_id: GitHub Actions run ID
        check_interval: Interval between checks in seconds (default: 120 = 2 minutes)
    """
    print(f"Starting Sentinel monitoring for run {run_id}")
    print(f"   Check interval: {check_interval} seconds ({check_interval // 60} minutes)")
    print(f"   Press Ctrl+C to stop\n")
    
    # Use direct API monitoring (more reliable, no K8s dependencies)
    print("Using direct GitHub API monitoring")
    await monitor_direct_api(run_id, check_interval)
    
    # MCP Sentinel integration (disabled for now - requires K8s connection)
    if False and MCP_AVAILABLE:
        # Try to use MCP Sentinel server
        try:
            # Note: Adjust this path to your Sentinel MCP server
            # Use 'py' launcher on Windows, 'python3' on Linux/Mac
            import platform
            python_cmd = "py" if platform.system() == "Windows" else "python3"
            
            server_params = StdioServerParameters(
                command=python_cmd,
                args=["mcp_sentinel/server.py"],
                env=None
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the session
                    await session.initialize()
                    
                    # Monitor loop
                    while True:
                        try:
                            # Use Sentinel's get_workflow_run_details tool
                            result = await session.call_tool(
                                "get_workflow_run_details",
                                {"run_id": run_id}
                            )
                            
                            # Clear screen and print report
                            os.system("cls" if os.name == "nt" else "clear")
                            
                            # Print the result
                            for content in result.content:
                                if hasattr(content, 'text'):
                                    print(content.text)
                                else:
                                    print(str(content))
                            
                            # Check if completed
                            # Parse status from result (you may need to adjust this)
                            if "completed" in str(result).lower():
                                if "success" in str(result).lower():
                                    print("\n✅ Workflow completed successfully!")
                                elif "failure" in str(result).lower():
                                    print("\n❌ Workflow failed!")
                                break
                            
                            # Wait before next check
                            print(f"\n⏳ Waiting {check_interval} seconds until next check...")
                            await asyncio.sleep(check_interval)
                        
                        except KeyboardInterrupt:
                            print("\n\n⚠️ Monitoring stopped by user")
                            break
                        except Exception as e:
                            print(f"\n❌ Error: {e}")
                            await asyncio.sleep(check_interval)
        
        except Exception as e:
            print(f"⚠️ Could not connect to Sentinel MCP server: {e}")
            print("Falling back to direct API monitoring...")
            await monitor_direct_api(run_id, check_interval)
    else:
        # Fallback to direct API
        await monitor_direct_api(run_id, check_interval)


async def monitor_direct_api(run_id: str, check_interval: int):
    """Monitor workflow using direct GitHub API calls."""
    import requests
    
    GITHUB_API_BASE = "https://api.github.com"
    
    def get_repo_info():
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
    
    owner, repo = get_repo_info()
    token = os.getenv("GITHUB_TOKEN")
    
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    
    run_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/runs/{run_id}"
    jobs_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/runs/{run_id}/jobs"
    
    while True:
        try:
            # Get run status
            run_response = requests.get(run_url, headers=headers)
            if run_response.status_code != 200:
                print(f"❌ Failed to get run status: {run_response.status_code}")
                await asyncio.sleep(check_interval)
                continue
            
            run_data = run_response.json()
            
            # Get jobs
            jobs_response = requests.get(jobs_url, headers=headers)
            jobs_data = jobs_response.json().get("jobs", []) if jobs_response.status_code == 200 else []
            
            # Clear screen and print report
            os.system("cls" if os.name == "nt" else "clear")
            
            # Format report
            workflow_name = run_data.get("name", "N/A")
            status = run_data.get("status", "N/A")
            conclusion = run_data.get("conclusion")
            created_at = run_data.get("created_at", "")
            updated_at = run_data.get("updated_at", "")
            
            # Calculate duration
            duration = "N/A"
            if created_at and updated_at:
                try:
                    created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    updated = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                    duration_seconds = (updated - created).total_seconds()
                    minutes = int(duration_seconds // 60)
                    seconds = int(duration_seconds % 60)
                    duration = f"{minutes}m {seconds}s"
                except:
                    pass
            
            # Status emoji (using simple text for Windows compatibility)
            status_emoji = {
                "completed": "[OK]" if conclusion == "success" else "[FAIL]" if conclusion == "failure" else "[WARN]",
                "in_progress": "[RUNNING]",
                "queued": "[QUEUED]",
                "waiting": "[WAITING]"
            }.get(status, "[UNKNOWN]")
            
            print(f"""
{'='*80}
[SENTINEL] Workflow Monitor
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
""")
            
            if jobs_data:
                for job in jobs_data:
                    job_name = job.get("name", "N/A")
                    job_status = job.get("status", "N/A")
                    job_conclusion = job.get("conclusion")
                    
                    job_emoji = {
                        "completed": "[OK]" if job_conclusion == "success" else "[FAIL]" if job_conclusion == "failure" else "[WARN]",
                        "in_progress": "[RUNNING]",
                        "queued": "[QUEUED]"
                    }.get(job_status, "[UNKNOWN]")
                    
                    print(f"  {job_emoji} {job_name}: {job_status}", end="")
                    if job_conclusion:
                        print(f" ({job_conclusion})")
                    else:
                        print()
            else:
                print("  No jobs found")
            
            print(f"\n{'='*80}")
            print(f"Last checked: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*80}\n")
            
            # Check if completed
            if status == "completed":
                if conclusion == "success":
                    print("[SUCCESS] Workflow completed successfully!")
                elif conclusion == "failure":
                    print("[FAILURE] Workflow failed!")
                elif conclusion == "cancelled":
                    print("[CANCELLED] Workflow was cancelled!")
                else:
                    print(f"[WARNING] Workflow completed with conclusion: {conclusion}")
                break
            
            # Wait before next check
            print(f"[WAITING] Waiting {check_interval} seconds until next check...")
            await asyncio.sleep(check_interval)
        
        except KeyboardInterrupt:
            print("\n\n⚠️ Monitoring stopped by user")
            break
        except Exception as e:
            print(f"\n❌ Error during monitoring: {e}")
            import traceback
            traceback.print_exc()
            await asyncio.sleep(check_interval)


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python monitor_workflow_sentinel.py <run_id> [check_interval_seconds]")
        print("\nExample:")
        print("  python monitor_workflow_sentinel.py 19866165500")
        print("  python monitor_workflow_sentinel.py 19866165500 120  # Check every 2 minutes")
        sys.exit(1)
    
    run_id = sys.argv[1]
    check_interval = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    
    asyncio.run(monitor_with_sentinel(run_id, check_interval))


if __name__ == "__main__":
    main()

