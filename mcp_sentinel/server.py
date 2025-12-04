"""
MCP Sentinel Server
===================

MCP server for Automation Run Sentinel - Monitoring service for automation runs.
Provides tools to query runs, anomalies, and monitor automation executions.
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
except ImportError:
    print("ERROR: mcp package not installed. Run: pip install mcp")
    raise

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from config.config_manager import ConfigManager
    from src.sentinel.main.sentinel_service import SentinelService
    from src.sentinel.core.models import RunContext, AnomalySeverity
except ImportError as e:
    print(f"WARNING: Could not import Sentinel modules: {e}")
    print("Sentinel service will run in limited mode")

# Initialize MCP server
server = Server("sentinel")

# Global service instance (will be initialized on first use)
_sentinel_service: Optional[SentinelService] = None
_config_manager: Optional[ConfigManager] = None

# GitHub configuration
GITHUB_API_BASE = "https://api.github.com"


def get_github_token() -> Optional[str]:
    """Get GitHub token from environment or config."""
    # Try environment variable first
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    
    # Try reading from mcp.json if available
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


def get_repo_info() -> tuple[str, str]:
    """Get repository owner and name from git config or default."""
    try:
        import subprocess
        # Try to get from git remote
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        if result.returncode == 0:
            url = result.stdout.strip()
            # Parse git URL (supports both https and ssh)
            if "github.com" in url:
                parts = url.replace(".git", "").split("/")
                if len(parts) >= 2:
                    owner = parts[-2].replace(":", "").split("@")[-1]
                    repo = parts[-1]
                    return owner, repo
    except Exception:
        pass
    
    # Default fallback (you can update this)
    return "your-username", "focus_server_automation"


def get_sentinel_service() -> Optional[SentinelService]:
    """Get or create Sentinel service instance."""
    global _sentinel_service, _config_manager
    
    if _sentinel_service is None:
        try:
            # Try to load config
            config_path = PROJECT_ROOT / "config" / "sentinel_config.yaml"
            config = {}
            
            if config_path.exists():
                import yaml
                with open(config_path, "r") as f:
                    config = yaml.safe_load(f) or {}
            
            # Initialize ConfigManager
            env = config.get("environment", "staging")
            _config_manager = ConfigManager(env=env)
            
            # Create Sentinel service
            _sentinel_service = SentinelService(_config_manager, config)
            _sentinel_service.start()
            
        except Exception as e:
            print(f"WARNING: Could not initialize Sentinel service: {e}")
            return None
    
    return _sentinel_service


def format_run_context(context: RunContext) -> str:
    """Format RunContext for display."""
    lines = [
        f"Run ID: {context.run_id}",
        f"Pipeline: {context.pipeline or 'N/A'}",
        f"Environment: {context.environment or 'N/A'}",
        f"Branch: {context.branch or 'N/A'}",
        f"Status: {context.status.value}",
    ]
    
    if context.start_time:
        lines.append(f"Start Time: {context.start_time.isoformat()}")
    if context.end_time:
        lines.append(f"End Time: {context.end_time.isoformat()}")
        if context.duration_seconds():
            lines.append(f"Duration: {context.duration_seconds():.1f} seconds")
    
    lines.append(f"Total Tests: {context.total_tests()}")
    lines.append(f"Passed: {context.passed_tests()}")
    lines.append(f"Failed: {context.failed_tests()}")
    
    if context.suites:
        lines.append(f"\nSuites ({len(context.suites)}):")
        for suite_name, suite in context.suites.items():
            lines.append(f"  - {suite_name}: {suite.total_tests} tests")
    
    if context.anomalies:
        lines.append(f"\nAnomalies ({len(context.anomalies)}):")
        for anomaly in context.anomalies[:5]:  # Show first 5
            lines.append(f"  - [{anomaly.severity.value}] {anomaly.title}")
    
    return "\n".join(lines)


@server.list_tools()
async def list_tools():
    """List available tools."""
    return [
        Tool(
            name="get_active_runs",
            description="Get all currently active automation runs",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_run",
            description="Get details of a specific run by run_id",
            inputSchema={
                "type": "object",
                "properties": {
                    "run_id": {
                        "type": "string",
                        "description": "The run ID to query"
                    }
                },
                "required": ["run_id"]
            }
        ),
        Tool(
            name="query_runs",
            description="Query historical runs with filters (pipeline, environment, status, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "pipeline": {
                        "type": "string",
                        "description": "Filter by pipeline name"
                    },
                    "environment": {
                        "type": "string",
                        "description": "Filter by environment"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["running", "completed", "failed", "cancelled"],
                        "description": "Filter by status"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 10,
                        "description": "Maximum number of results"
                    }
                }
            }
        ),
        Tool(
            name="get_run_anomalies",
            description="Get all anomalies detected for a specific run",
            inputSchema={
                "type": "object",
                "properties": {
                    "run_id": {
                        "type": "string",
                        "description": "The run ID to query"
                    }
                },
                "required": ["run_id"]
            }
        ),
        Tool(
            name="get_recent_anomalies",
            description="Get recent anomalies across all runs",
            inputSchema={
                "type": "object",
                "properties": {
                    "severity": {
                        "type": "string",
                        "enum": ["critical", "warning", "info"],
                        "description": "Filter by severity level"
                    },
                    "hours": {
                        "type": "integer",
                        "default": 24,
                        "description": "Number of hours to look back"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 20,
                        "description": "Maximum number of results"
                    }
                }
            }
        ),
        Tool(
            name="get_run_stats",
            description="Get statistics about runs (total, active, failed, etc.)",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="monitor_run",
            description="Monitor a specific run in real-time (returns current status)",
            inputSchema={
                "type": "object",
                "properties": {
                    "run_id": {
                        "type": "string",
                        "description": "The run ID to monitor"
                    }
                },
                "required": ["run_id"]
            }
        ),
        Tool(
            name="trigger_github_workflow",
            description="Trigger a GitHub Actions workflow manually",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_file": {
                        "type": "string",
                        "description": "Workflow file name (e.g., 'build-sentinel.yml') or workflow ID"
                    },
                    "ref": {
                        "type": "string",
                        "default": "main",
                        "description": "Branch, tag, or commit SHA to run the workflow on"
                    },
                    "inputs": {
                        "type": "object",
                        "description": "Input parameters for the workflow (if workflow_dispatch)"
                    },
                    "repository": {
                        "type": "string",
                        "description": "Repository in format 'owner/repo' (defaults to current repo if not specified)"
                    }
                },
                "required": ["workflow_file"]
            }
        ),
        Tool(
            name="list_github_workflows",
            description="List available GitHub Actions workflows in the repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository": {
                        "type": "string",
                        "description": "Repository in format 'owner/repo' (defaults to current repo if not specified)"
                    }
                }
            }
        ),
        Tool(
            name="get_workflow_yaml",
            description="Get the YAML content of a GitHub Actions workflow file",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_file": {
                        "type": "string",
                        "description": "Workflow file name (e.g., 'smoke-tests.yml')"
                    },
                    "repository": {
                        "type": "string",
                        "description": "Repository in format 'owner/repo' (defaults to current repo if not specified)"
                    }
                },
                "required": ["workflow_file"]
            }
        ),
        Tool(
            name="update_workflow_schedule",
            description="Add or update schedule (cron) for a GitHub Actions workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_file": {
                        "type": "string",
                        "description": "Workflow file name (e.g., 'smoke-tests.yml')"
                    },
                    "schedule": {
                        "type": "string",
                        "description": "Cron expression (e.g., '0 8 * * *' for daily at 8 AM)"
                    },
                    "timezone": {
                        "type": "string",
                        "default": "UTC",
                        "description": "Timezone for the schedule (e.g., 'Asia/Jerusalem', 'UTC')"
                    },
                    "repository": {
                        "type": "string",
                        "description": "Repository in format 'owner/repo' (defaults to current repo if not specified)"
                    }
                },
                "required": ["workflow_file", "schedule"]
            }
        ),
        Tool(
            name="remove_workflow_schedule",
            description="Remove schedule from a GitHub Actions workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_file": {
                        "type": "string",
                        "description": "Workflow file name (e.g., 'smoke-tests.yml')"
                    },
                    "repository": {
                        "type": "string",
                        "description": "Repository in format 'owner/repo' (defaults to current repo if not specified)"
                    }
                },
                "required": ["workflow_file"]
            }
        ),
        Tool(
            name="update_workflow_yaml",
            description="Update GitHub Actions workflow YAML file (add schedule, change triggers, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_file": {
                        "type": "string",
                        "description": "Workflow file name (e.g., 'smoke-tests.yml')"
                    },
                    "yaml_content": {
                        "type": "string",
                        "description": "Full YAML content to write (will replace entire file)"
                    },
                    "repository": {
                        "type": "string",
                        "description": "Repository in format 'owner/repo' (defaults to current repo if not specified)"
                    }
                },
                "required": ["workflow_file", "yaml_content"]
            }
        ),
        Tool(
            name="list_workflow_schedules",
            description="List all scheduled workflows and their schedules",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository": {
                        "type": "string",
                        "description": "Repository in format 'owner/repo' (defaults to current repo if not specified)"
                    }
                }
            }
        ),
        Tool(
            name="get_workflow_run_details",
            description="Get detailed information about a GitHub Actions workflow run (jobs, steps, logs, errors, timing)",
            inputSchema={
                "type": "object",
                "properties": {
                    "run_id": {
                        "type": "string",
                        "description": "GitHub Actions workflow run ID"
                    },
                    "repository": {
                        "type": "string",
                        "description": "Repository in format 'owner/repo' (defaults to current repo if not specified)"
                    },
                    "include_logs": {
                        "type": "boolean",
                        "default": False,
                        "description": "Include log content for failed steps"
                    }
                },
                "required": ["run_id"]
            }
        ),
        Tool(
            name="monitor_workflow_run_detailed",
            description="Monitor a GitHub Actions workflow run with detailed progress (jobs, steps, failures, timing)",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_file": {
                        "type": "string",
                        "description": "Workflow file name (e.g., 'smoke-tests.yml')"
                    },
                    "run_id": {
                        "type": "string",
                        "description": "Optional: specific run ID to monitor (if not provided, monitors latest run)"
                    },
                    "repository": {
                        "type": "string",
                        "description": "Repository in format 'owner/repo' (defaults to current repo if not specified)"
                    },
                    "poll_interval": {
                        "type": "integer",
                        "default": 10,
                        "description": "Polling interval in seconds"
                    }
                },
                "required": ["workflow_file"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Handle tool calls."""
    try:
        service = get_sentinel_service()
        
        if service is None:
            return [TextContent(
                type="text",
                text="ERROR: Sentinel service is not available. Please check configuration."
            )]
        
        if name == "get_active_runs":
            active_runs = service.get_active_runs()
            
            if not active_runs:
                return [TextContent(
                    type="text",
                    text="No active runs found."
                )]
            
            result = f"Active Runs ({len(active_runs)}):\n\n"
            for run_id, context in active_runs.items():
                result += f"{'='*60}\n"
                result += format_run_context(context)
                result += "\n\n"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "get_run":
            run_id = arguments.get("run_id")
            if not run_id:
                return [TextContent(
                    type="text",
                    text="ERROR: run_id is required"
                )]
            
            context = service.get_run(run_id)
            if not context:
                return [TextContent(
                    type="text",
                    text=f"Run '{run_id}' not found."
                )]
            
            return [TextContent(
                type="text",
                text=format_run_context(context)
            )]
        
        elif name == "query_runs":
            filters = {
                k: v for k, v in arguments.items()
                if k in ["pipeline", "environment", "status"] and v
            }
            limit = arguments.get("limit", 10)
            
            runs = service.query_runs(**filters, limit=limit)
            
            if not runs:
                filter_str = ", ".join([f"{k}={v}" for k, v in filters.items()])
                return [TextContent(
                    type="text",
                    text=f"No runs found matching filters: {filter_str}"
                )]
            
            result = f"Found {len(runs)} runs:\n\n"
            for run in runs[:limit]:
                if isinstance(run, dict):
                    run_id = run.get("run_id", "unknown")
                    pipeline = run.get("pipeline", "N/A")
                    status = run.get("status", "N/A")
                    result += f"- {run_id}: {pipeline} ({status})\n"
                else:
                    result += f"- {str(run)}\n"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "get_run_anomalies":
            run_id = arguments.get("run_id")
            if not run_id:
                return [TextContent(
                    type="text",
                    text="ERROR: run_id is required"
                )]
            
            context = service.get_run(run_id)
            if not context:
                return [TextContent(
                    type="text",
                    text=f"Run '{run_id}' not found."
                )]
            
            anomalies = context.anomalies
            if not anomalies:
                return [TextContent(
                    type="text",
                    text=f"No anomalies found for run '{run_id}'."
                )]
            
            result = f"Anomalies for Run '{run_id}' ({len(anomalies)}):\n\n"
            for anomaly in anomalies:
                result += f"[{anomaly.severity.value.upper()}] {anomaly.title}\n"
                result += f"  Category: {anomaly.category.value}\n"
                result += f"  Description: {anomaly.description}\n"
                if anomaly.affected_component:
                    result += f"  Component: {anomaly.affected_component}\n"
                result += f"  Time: {anomaly.timestamp.isoformat()}\n\n"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "get_recent_anomalies":
            severity_filter = arguments.get("severity")
            hours = arguments.get("hours", 24)
            limit = arguments.get("limit", 20)
            
            # Query runs from the last N hours
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Get all active runs and query recent runs
            active_runs = service.get_active_runs()
            all_anomalies = []
            
            for run_id, context in active_runs.items():
                if context.start_time and context.start_time >= cutoff_time:
                    for anomaly in context.anomalies:
                        if not severity_filter or anomaly.severity.value == severity_filter:
                            all_anomalies.append((run_id, anomaly))
            
            # Sort by timestamp
            all_anomalies.sort(key=lambda x: x[1].timestamp, reverse=True)
            
            if not all_anomalies:
                return [TextContent(
                    type="text",
                    text=f"No anomalies found in the last {hours} hours."
                )]
            
            result = f"Recent Anomalies (last {hours} hours, showing {min(limit, len(all_anomalies))}):\n\n"
            for run_id, anomaly in all_anomalies[:limit]:
                result += f"Run: {run_id}\n"
                result += f"[{anomaly.severity.value.upper()}] {anomaly.title}\n"
                result += f"  {anomaly.description}\n"
                result += f"  Time: {anomaly.timestamp.isoformat()}\n\n"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "get_run_stats":
            active_runs = service.get_active_runs()
            
            stats = {
                "active_runs": len(active_runs),
                "total_tests": sum(ctx.total_tests() for ctx in active_runs.values()),
                "passed_tests": sum(ctx.passed_tests() for ctx in active_runs.values()),
                "failed_tests": sum(ctx.failed_tests() for ctx in active_runs.values()),
                "total_anomalies": sum(len(ctx.anomalies) for ctx in active_runs.values()),
            }
            
            result = "Run Statistics:\n\n"
            result += f"Active Runs: {stats['active_runs']}\n"
            result += f"Total Tests: {stats['total_tests']}\n"
            result += f"Passed: {stats['passed_tests']}\n"
            result += f"Failed: {stats['failed_tests']}\n"
            result += f"Total Anomalies: {stats['total_anomalies']}\n"
            
            if stats['total_tests'] > 0:
                pass_rate = (stats['passed_tests'] / stats['total_tests']) * 100
                result += f"Pass Rate: {pass_rate:.1f}%\n"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "monitor_run":
            run_id = arguments.get("run_id")
            if not run_id:
                return [TextContent(
                    type="text",
                    text="ERROR: run_id is required"
                )]
            
            context = service.get_run(run_id)
            if not context:
                return [TextContent(
                    type="text",
                    text=f"Run '{run_id}' not found. It may have completed or not started yet."
                )]
            
            result = f"Monitoring Run: {run_id}\n\n"
            result += format_run_context(context)
            
            # Add real-time status
            if context.status.value == "running":
                result += "\n\n⚠️ Run is currently active"
            elif context.status.value == "failed":
                result += "\n\n❌ Run has failed"
            elif context.status.value == "completed":
                result += "\n\n✅ Run completed successfully"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "trigger_github_workflow":
            if not REQUESTS_AVAILABLE:
                return [TextContent(
                    type="text",
                    text="ERROR: requests package is required. Install it with: pip install requests"
                )]
            
            workflow_file = arguments.get("workflow_file")
            ref = arguments.get("ref", "main")
            inputs = arguments.get("inputs", {})
            repository = arguments.get("repository")
            
            if not workflow_file:
                return [TextContent(
                    type="text",
                    text="ERROR: workflow_file is required"
                )]
            
            # Get GitHub token
            token = get_github_token()
            if not token:
                return [TextContent(
                    type="text",
                    text="ERROR: GitHub token not found. Set GITHUB_TOKEN environment variable or configure in mcp.json"
                )]
            
            # Get repository info
            if repository:
                owner, repo = repository.split("/", 1)
            else:
                owner, repo = get_repo_info()
            
            # Trigger workflow
            try:
                url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/workflows/{workflow_file}/dispatches"
                headers = {
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                payload = {
                    "ref": ref
                }
                if inputs:
                    payload["inputs"] = inputs
                
                response = requests.post(url, json=payload, headers=headers)
                
                if response.status_code == 204:
                    result = f"✅ Successfully triggered workflow '{workflow_file}'\n\n"
                    result += f"Repository: {owner}/{repo}\n"
                    result += f"Branch: {ref}\n"
                    if inputs:
                        result += f"Inputs: {json.dumps(inputs, indent=2)}\n"
                    result += f"\nCheck the workflow run at: https://github.com/{owner}/{repo}/actions"
                    return [TextContent(type="text", text=result)]
                else:
                    error_msg = response.json().get("message", "Unknown error")
                    return [TextContent(
                        type="text",
                        text=f"ERROR: Failed to trigger workflow. Status: {response.status_code}\nMessage: {error_msg}"
                    )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"ERROR: Failed to trigger workflow: {str(e)}"
                )]
        
        elif name == "list_github_workflows":
            if not REQUESTS_AVAILABLE:
                return [TextContent(
                    type="text",
                    text="ERROR: requests package is required. Install it with: pip install requests"
                )]
            
            repository = arguments.get("repository")
            
            # Get GitHub token
            token = get_github_token()
            if not token:
                return [TextContent(
                    type="text",
                    text="ERROR: GitHub token not found. Set GITHUB_TOKEN environment variable or configure in mcp.json"
                )]
            
            # Get repository info
            if repository:
                owner, repo = repository.split("/", 1)
            else:
                owner, repo = get_repo_info()
            
            # List workflows
            try:
                url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/workflows"
                headers = {
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    workflows = response.json().get("workflows", [])
                    
                    if not workflows:
                        return [TextContent(
                            type="text",
                            text=f"No workflows found in {owner}/{repo}"
                        )]
                    
                    result = f"Available Workflows in {owner}/{repo}:\n\n"
                    for workflow in workflows:
                        result += f"📋 {workflow['name']}\n"
                        result += f"   File: {workflow['path']}\n"
                        result += f"   State: {workflow['state']}\n"
                        result += f"   ID: {workflow['id']}\n"
                        result += f"   URL: {workflow['html_url']}\n\n"
                    
                    return [TextContent(type="text", text=result)]
                else:
                    error_msg = response.json().get("message", "Unknown error")
                    return [TextContent(
                        type="text",
                        text=f"ERROR: Failed to list workflows. Status: {response.status_code}\nMessage: {error_msg}"
                    )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"ERROR: Failed to list workflows: {str(e)}"
                )]
        
        elif name == "get_workflow_yaml":
            if not REQUESTS_AVAILABLE:
                return [TextContent(
                    type="text",
                    text="ERROR: requests package is required. Install it with: pip install requests"
                )]
            
            workflow_file = arguments.get("workflow_file")
            repository = arguments.get("repository")
            
            if not workflow_file:
                return [TextContent(
                    type="text",
                    text="ERROR: workflow_file is required"
                )]
            
            token = get_github_token()
            if not token:
                return [TextContent(
                    type="text",
                    text="ERROR: GitHub token not found"
                )]
            
            if repository:
                owner, repo = repository.split("/", 1)
            else:
                owner, repo = get_repo_info()
            
            try:
                # Get workflow file content from repository
                url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/.github/workflows/{workflow_file}"
                headers = {
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    import base64
                    content = base64.b64decode(response.json()["content"]).decode("utf-8")
                    return [TextContent(
                        type="text",
                        text=f"Workflow YAML for {workflow_file}:\n\n{content}"
                    )]
                else:
                    error_msg = response.json().get("message", "Unknown error")
                    return [TextContent(
                        type="text",
                        text=f"ERROR: Failed to get workflow YAML. Status: {response.status_code}\nMessage: {error_msg}"
                    )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"ERROR: Failed to get workflow YAML: {str(e)}"
                )]
        
        elif name == "update_workflow_schedule":
            if not REQUESTS_AVAILABLE:
                return [TextContent(
                    type="text",
                    text="ERROR: requests package is required. Install it with: pip install requests"
                )]
            
            workflow_file = arguments.get("workflow_file")
            schedule = arguments.get("schedule")
            timezone = arguments.get("timezone", "UTC")
            repository = arguments.get("repository")
            
            if not workflow_file or not schedule:
                return [TextContent(
                    type="text",
                    text="ERROR: workflow_file and schedule are required"
                )]
            
            token = get_github_token()
            if not token:
                return [TextContent(
                    type="text",
                    text="ERROR: GitHub token not found"
                )]
            
            if repository:
                owner, repo = repository.split("/", 1)
            else:
                owner, repo = get_repo_info()
            
            try:
                import yaml
                import base64
                
                # Get current workflow content
                url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/.github/workflows/{workflow_file}"
                headers = {
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                
                response = requests.get(url, headers=headers)
                if response.status_code != 200:
                    return [TextContent(
                        type="text",
                        text=f"ERROR: Failed to get workflow file. Status: {response.status_code}"
                    )]
                
                file_data = response.json()
                current_content = base64.b64decode(file_data["content"]).decode("utf-8")
                
                # Parse YAML
                workflow_yaml = yaml.safe_load(current_content)
                
                # Add or update schedule
                if "on" not in workflow_yaml:
                    workflow_yaml["on"] = {}
                
                if "schedule" not in workflow_yaml["on"]:
                    workflow_yaml["on"]["schedule"] = []
                
                # Check if schedule already exists
                schedule_exists = False
                for idx, existing_schedule in enumerate(workflow_yaml["on"]["schedule"]):
                    if existing_schedule.get("cron") == schedule:
                        workflow_yaml["on"]["schedule"][idx] = {
                            "cron": schedule,
                            "timezone": timezone
                        }
                        schedule_exists = True
                        break
                
                if not schedule_exists:
                    workflow_yaml["on"]["schedule"].append({
                        "cron": schedule,
                        "timezone": timezone
                    })
                
                # Convert back to YAML
                updated_yaml = yaml.dump(workflow_yaml, default_flow_style=False, sort_keys=False)
                
                # Update file
                update_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/.github/workflows/{workflow_file}"
                update_payload = {
                    "message": f"Update schedule for {workflow_file}: {schedule} ({timezone})",
                    "content": base64.b64encode(updated_yaml.encode("utf-8")).decode("utf-8"),
                    "sha": file_data["sha"]
                }
                
                update_response = requests.put(update_url, json=update_payload, headers=headers)
                
                if update_response.status_code == 200:
                    result = f"✅ Successfully updated schedule for '{workflow_file}'\n\n"
                    result += f"Schedule: {schedule} ({timezone})\n"
                    result += f"Repository: {owner}/{repo}\n"
                    result += f"View at: https://github.com/{owner}/{repo}/blob/main/.github/workflows/{workflow_file}"
                    return [TextContent(type="text", text=result)]
                else:
                    error_msg = update_response.json().get("message", "Unknown error")
                    return [TextContent(
                        type="text",
                        text=f"ERROR: Failed to update workflow. Status: {update_response.status_code}\nMessage: {error_msg}"
                    )]
            except Exception as e:
                import traceback
                return [TextContent(
                    type="text",
                    text=f"ERROR: Failed to update schedule: {str(e)}\n\n{traceback.format_exc()}"
                )]
        
        elif name == "remove_workflow_schedule":
            if not REQUESTS_AVAILABLE:
                return [TextContent(
                    type="text",
                    text="ERROR: requests package is required. Install it with: pip install requests"
                )]
            
            workflow_file = arguments.get("workflow_file")
            repository = arguments.get("repository")
            
            if not workflow_file:
                return [TextContent(
                    type="text",
                    text="ERROR: workflow_file is required"
                )]
            
            token = get_github_token()
            if not token:
                return [TextContent(
                    type="text",
                    text="ERROR: GitHub token not found"
                )]
            
            if repository:
                owner, repo = repository.split("/", 1)
            else:
                owner, repo = get_repo_info()
            
            try:
                import yaml
                import base64
                
                # Get current workflow content
                url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/.github/workflows/{workflow_file}"
                headers = {
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                
                response = requests.get(url, headers=headers)
                if response.status_code != 200:
                    return [TextContent(
                        type="text",
                        text=f"ERROR: Failed to get workflow file. Status: {response.status_code}"
                    )]
                
                file_data = response.json()
                current_content = base64.b64decode(file_data["content"]).decode("utf-8")
                
                # Parse YAML
                workflow_yaml = yaml.safe_load(current_content)
                
                # Remove schedule
                if "on" in workflow_yaml and "schedule" in workflow_yaml["on"]:
                    del workflow_yaml["on"]["schedule"]
                    if not workflow_yaml["on"]:
                        del workflow_yaml["on"]
                    
                    # Convert back to YAML
                    updated_yaml = yaml.dump(workflow_yaml, default_flow_style=False, sort_keys=False)
                    
                    # Update file
                    update_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/.github/workflows/{workflow_file}"
                    update_payload = {
                        "message": f"Remove schedule from {workflow_file}",
                        "content": base64.b64encode(updated_yaml.encode("utf-8")).decode("utf-8"),
                        "sha": file_data["sha"]
                    }
                    
                    update_response = requests.put(update_url, json=update_payload, headers=headers)
                    
                    if update_response.status_code == 200:
                        return [TextContent(
                            type="text",
                            text=f"✅ Successfully removed schedule from '{workflow_file}'"
                        )]
                    else:
                        error_msg = update_response.json().get("message", "Unknown error")
                        return [TextContent(
                            type="text",
                            text=f"ERROR: Failed to update workflow. Status: {update_response.status_code}\nMessage: {error_msg}"
                        )]
                else:
                    return [TextContent(
                        type="text",
                        text=f"No schedule found in '{workflow_file}'"
                    )]
            except Exception as e:
                import traceback
                return [TextContent(
                    type="text",
                    text=f"ERROR: Failed to remove schedule: {str(e)}\n\n{traceback.format_exc()}"
                )]
        
        elif name == "update_workflow_yaml":
            if not REQUESTS_AVAILABLE:
                return [TextContent(
                    type="text",
                    text="ERROR: requests package is required. Install it with: pip install requests"
                )]
            
            workflow_file = arguments.get("workflow_file")
            yaml_content = arguments.get("yaml_content")
            repository = arguments.get("repository")
            
            if not workflow_file or not yaml_content:
                return [TextContent(
                    type="text",
                    text="ERROR: workflow_file and yaml_content are required"
                )]
            
            token = get_github_token()
            if not token:
                return [TextContent(
                    type="text",
                    text="ERROR: GitHub token not found"
                )]
            
            if repository:
                owner, repo = repository.split("/", 1)
            else:
                owner, repo = get_repo_info()
            
            try:
                import base64
                
                # Get current file SHA
                url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/.github/workflows/{workflow_file}"
                headers = {
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                
                response = requests.get(url, headers=headers)
                file_sha = None
                if response.status_code == 200:
                    file_sha = response.json()["sha"]
                
                # Update file
                update_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/.github/workflows/{workflow_file}"
                update_payload = {
                    "message": f"Update workflow {workflow_file}",
                    "content": base64.b64encode(yaml_content.encode("utf-8")).decode("utf-8")
                }
                if file_sha:
                    update_payload["sha"] = file_sha
                
                update_response = requests.put(update_url, json=update_payload, headers=headers)
                
                if update_response.status_code == 200:
                    result = f"✅ Successfully updated workflow '{workflow_file}'\n\n"
                    result += f"Repository: {owner}/{repo}\n"
                    result += f"View at: https://github.com/{owner}/{repo}/blob/main/.github/workflows/{workflow_file}"
                    return [TextContent(type="text", text=result)]
                else:
                    error_msg = update_response.json().get("message", "Unknown error")
                    return [TextContent(
                        type="text",
                        text=f"ERROR: Failed to update workflow. Status: {update_response.status_code}\nMessage: {error_msg}"
                    )]
            except Exception as e:
                import traceback
                return [TextContent(
                    type="text",
                    text=f"ERROR: Failed to update workflow YAML: {str(e)}\n\n{traceback.format_exc()}"
                )]
        
        elif name == "list_workflow_schedules":
            if not REQUESTS_AVAILABLE:
                return [TextContent(
                    type="text",
                    text="ERROR: requests package is required. Install it with: pip install requests"
                )]
            
            repository = arguments.get("repository")
            
            token = get_github_token()
            if not token:
                return [TextContent(
                    type="text",
                    text="ERROR: GitHub token not found"
                )]
            
            if repository:
                owner, repo = repository.split("/", 1)
            else:
                owner, repo = get_repo_info()
            
            try:
                import yaml
                import base64
                
                # List all workflows
                workflows_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/workflows"
                headers = {
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                
                response = requests.get(workflows_url, headers=headers)
                if response.status_code != 200:
                    return [TextContent(
                        type="text",
                        text=f"ERROR: Failed to list workflows. Status: {response.status_code}"
                    )]
                
                workflows = response.json().get("workflows", [])
                
                result = f"Scheduled Workflows in {owner}/{repo}:\n\n"
                scheduled_count = 0
                
                for workflow in workflows:
                    workflow_path = workflow.get("path", "")
                    workflow_file = workflow_path.replace(".github/workflows/", "")
                    
                    # Get workflow content
                    content_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{workflow_path}"
                    content_response = requests.get(content_url, headers=headers)
                    
                    if content_response.status_code == 200:
                        content_data = content_response.json()
                        workflow_content = base64.b64decode(content_data["content"]).decode("utf-8")
                        workflow_yaml = yaml.safe_load(workflow_content)
                        
                        if "on" in workflow_yaml and "schedule" in workflow_yaml["on"]:
                            schedules = workflow_yaml["on"]["schedule"]
                            if schedules:
                                scheduled_count += 1
                                result += f"📅 {workflow['name']} ({workflow_file})\n"
                                for schedule in schedules:
                                    cron = schedule.get("cron", "N/A")
                                    tz = schedule.get("timezone", "UTC")
                                    result += f"   Schedule: {cron} ({tz})\n"
                                result += "\n"
                
                if scheduled_count == 0:
                    result += "No scheduled workflows found."
                
                return [TextContent(type="text", text=result)]
            except Exception as e:
                import traceback
                return [TextContent(
                    type="text",
                    text=f"ERROR: Failed to list schedules: {str(e)}\n\n{traceback.format_exc()}"
                )]
        
        elif name == "get_workflow_run_details":
            if not REQUESTS_AVAILABLE:
                return [TextContent(
                    type="text",
                    text="ERROR: requests package is required. Install it with: pip install requests"
                )]
            
            run_id = arguments.get("run_id")
            repository = arguments.get("repository")
            include_logs = arguments.get("include_logs", False)
            
            if not run_id:
                return [TextContent(
                    type="text",
                    text="ERROR: run_id is required"
                )]
            
            token = get_github_token()
            if not token:
                return [TextContent(
                    type="text",
                    text="ERROR: GitHub token not found"
                )]
            
            if repository:
                owner, repo = repository.split("/", 1)
            else:
                owner, repo = get_repo_info()
            
            try:
                # Get run details
                run_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/runs/{run_id}"
                headers = {
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                
                run_response = requests.get(run_url, headers=headers)
                if run_response.status_code != 200:
                    return [TextContent(
                        type="text",
                        text=f"ERROR: Failed to get run details. Status: {run_response.status_code}"
                    )]
                
                run_data = run_response.json()
                
                # Get jobs for this run
                jobs_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/runs/{run_id}/jobs"
                jobs_response = requests.get(jobs_url, headers=headers)
                jobs_data = jobs_response.json().get("jobs", []) if jobs_response.status_code == 200 else []
                
                # Build detailed report
                result = f"{'='*70}\n"
                result += f"Workflow Run Details: {run_id}\n"
                result += f"{'='*70}\n\n"
                
                # Run summary
                result += f"📋 Run Summary:\n"
                result += f"   Workflow: {run_data.get('name', 'N/A')}\n"
                result += f"   Status: {run_data.get('status', 'N/A')}\n"
                result += f"   Conclusion: {run_data.get('conclusion', 'N/A')}\n"
                result += f"   Started: {run_data.get('created_at', 'N/A')}\n"
                if run_data.get('updated_at'):
                    result += f"   Updated: {run_data.get('updated_at')}\n"
                if run_data.get('run_duration_ms'):
                    duration_sec = run_data.get('run_duration_ms', 0) / 1000
                    result += f"   Duration: {duration_sec:.1f} seconds ({duration_sec/60:.1f} minutes)\n"
                result += f"   URL: {run_data.get('html_url', 'N/A')}\n"
                result += f"   Branch: {run_data.get('head_branch', 'N/A')}\n"
                result += f"   Commit: {run_data.get('head_sha', 'N/A')[:8]}\n\n"
                
                # Jobs details
                if jobs_data:
                    result += f"{'='*70}\n"
                    result += f"Jobs ({len(jobs_data)}):\n"
                    result += f"{'='*70}\n\n"
                    
                    for job in jobs_data:
                        job_name = job.get('name', 'N/A')
                        job_status = job.get('status', 'N/A')
                        job_conclusion = job.get('conclusion', 'N/A')
                        job_started = job.get('started_at', 'N/A')
                        job_completed = job.get('completed_at', 'N/A')
                        
                        # Calculate duration
                        duration_str = "N/A"
                        if job_started != 'N/A' and job_completed != 'N/A':
                            try:
                                from datetime import datetime as dt
                                start = dt.fromisoformat(job_started.replace('Z', '+00:00'))
                                end = dt.fromisoformat(job_completed.replace('Z', '+00:00'))
                                duration = (end - start).total_seconds()
                                duration_str = f"{duration:.1f}s ({duration/60:.1f}m)"
                            except:
                                pass
                        
                        # Status icon
                        if job_conclusion == 'success':
                            icon = "✅"
                        elif job_conclusion == 'failure':
                            icon = "❌"
                        elif job_conclusion == 'cancelled':
                            icon = "⚠️"
                        else:
                            icon = "⏳"
                        
                        result += f"{icon} Job: {job_name}\n"
                        result += f"   Status: {job_status} | Conclusion: {job_conclusion}\n"
                        result += f"   Started: {job_started}\n"
                        result += f"   Completed: {job_completed}\n"
                        result += f"   Duration: {duration_str}\n"
                        result += f"   URL: {job.get('html_url', 'N/A')}\n\n"
                        
                        # Steps details
                        steps = job.get('steps', [])
                        if steps:
                            result += f"   Steps ({len(steps)}):\n"
                            for step in steps:
                                step_name = step.get('name', 'N/A')
                                step_status = step.get('status', 'N/A')
                                step_conclusion = step.get('conclusion', 'N/A')
                                step_number = step.get('number', 'N/A')
                                
                                # Step icon
                                if step_conclusion == 'success':
                                    step_icon = "  ✓"
                                elif step_conclusion == 'failure':
                                    step_icon = "  ✗"
                                elif step_conclusion == 'cancelled':
                                    step_icon = "  ⊘"
                                else:
                                    step_icon = "  ○"
                                
                                result += f"{step_icon} Step {step_number}: {step_name}\n"
                                result += f"      Status: {step_status} | Conclusion: {step_conclusion}\n"
                                
                                # Calculate step duration
                                if step.get('started_at') and step.get('completed_at'):
                                    try:
                                        from datetime import datetime as dt
                                        step_start = dt.fromisoformat(step['started_at'].replace('Z', '+00:00'))
                                        step_end = dt.fromisoformat(step['completed_at'].replace('Z', '+00:00'))
                                        step_duration = (step_end - step_start).total_seconds()
                                        result += f"      Duration: {step_duration:.1f}s\n"
                                    except Exception:
                                        pass
                                
                                # Get logs for failed steps
                                if include_logs and step_conclusion == 'failure':
                                    try:
                                        logs_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/jobs/{job.get('id')}/logs"
                                        logs_response = requests.get(logs_url, headers=headers)
                                        if logs_response.status_code == 200:
                                            # Logs are usually gzipped, but GitHub API returns them as text
                                            logs_content = logs_response.text
                                            # Extract relevant error lines (last 50 lines)
                                            log_lines = logs_content.split('\n')
                                            error_lines = [line for line in log_lines if any(keyword in line.lower() for keyword in ['error', 'failed', 'exception', 'traceback', 'fatal', 'critical'])]
                                            if error_lines:
                                                result += f"      ❌ Recent Errors ({len(error_lines)} found):\n"
                                                for error_line in error_lines[-15:]:  # Last 15 error lines
                                                    # Truncate long lines
                                                    display_line = error_line[:150] + "..." if len(error_line) > 150 else error_line
                                                    result += f"        {display_line}\n"
                                            else:
                                                # If no error keywords, show last 20 lines
                                                result += f"      📋 Last Log Lines:\n"
                                                for log_line in log_lines[-20:]:
                                                    display_line = log_line[:150] + "..." if len(log_line) > 150 else log_line
                                                    result += f"        {display_line}\n"
                                    except Exception as e:
                                        result += f"      (Could not fetch logs: {str(e)})\n"
                                
                                result += "\n"
                        
                        result += "\n"
                
                # Summary statistics
                total_jobs = len(jobs_data)
                successful_jobs = len([j for j in jobs_data if j.get('conclusion') == 'success'])
                failed_jobs = len([j for j in jobs_data if j.get('conclusion') == 'failure'])
                cancelled_jobs = len([j for j in jobs_data if j.get('conclusion') == 'cancelled'])
                
                # Count steps
                total_steps = 0
                successful_steps = 0
                failed_steps = 0
                for job in jobs_data:
                    steps = job.get('steps', [])
                    total_steps += len(steps)
                    successful_steps += len([s for s in steps if s.get('conclusion') == 'success'])
                    failed_steps += len([s for s in steps if s.get('conclusion') == 'failure'])
                
                result += f"{'='*70}\n"
                result += f"📊 Summary:\n"
                result += f"{'='*70}\n"
                result += f"Total Jobs: {total_jobs}\n"
                result += f"  ✅ Successful: {successful_jobs}\n"
                result += f"  ❌ Failed: {failed_jobs}\n"
                if cancelled_jobs > 0:
                    result += f"  ⚠️ Cancelled: {cancelled_jobs}\n"
                result += f"\nTotal Steps: {total_steps}\n"
                result += f"  ✅ Successful: {successful_steps}\n"
                result += f"  ❌ Failed: {failed_steps}\n"
                
                # Overall conclusion with failed details
                if run_data.get('conclusion') == 'success':
                    result += f"\n🎉 Overall: SUCCESS\n"
                elif run_data.get('conclusion') == 'failure':
                    result += f"\n💥 Overall: FAILURE\n"
                    if failed_jobs > 0:
                        result += f"\n❌ Failed Jobs Details:\n"
                        for job in jobs_data:
                            if job.get('conclusion') == 'failure':
                                result += f"  • {job.get('name', 'N/A')}\n"
                                failed_steps_in_job = [s for s in job.get('steps', []) if s.get('conclusion') == 'failure']
                                if failed_steps_in_job:
                                    result += f"    Failed Steps:\n"
                                    for step in failed_steps_in_job:
                                        result += f"      - {step.get('name', 'N/A')}\n"
                elif run_data.get('conclusion') == 'cancelled':
                    result += f"\n⚠️ Overall: CANCELLED\n"
                
                return [TextContent(type="text", text=result)]
            except Exception as e:
                import traceback
                return [TextContent(
                    type="text",
                    text=f"ERROR: Failed to get run details: {str(e)}\n\n{traceback.format_exc()}"
                )]
        
        elif name == "monitor_workflow_run_detailed":
            if not REQUESTS_AVAILABLE:
                return [TextContent(
                    type="text",
                    text="ERROR: requests package is required. Install it with: pip install requests"
                )]
            
            workflow_file = arguments.get("workflow_file")
            run_id = arguments.get("run_id")
            repository = arguments.get("repository")
            poll_interval = arguments.get("poll_interval", 10)
            
            if not workflow_file:
                return [TextContent(
                    type="text",
                    text="ERROR: workflow_file is required"
                )]
            
            token = get_github_token()
            if not token:
                return [TextContent(
                    type="text",
                    text="ERROR: GitHub token not found"
                )]
            
            if repository:
                owner, repo = repository.split("/", 1)
            else:
                owner, repo = get_repo_info()
            
            try:
                headers = {
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                
                # If run_id not provided, get latest run
                if not run_id:
                    workflows_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/workflows"
                    workflows_response = requests.get(workflows_url, headers=headers)
                    if workflows_response.status_code != 200:
                        return [TextContent(
                            type="text",
                            text=f"ERROR: Failed to get workflows. Status: {workflows_response.status_code}"
                        )]
                    
                    workflows = workflows_response.json().get("workflows", [])
                    workflow_id = None
                    for workflow in workflows:
                        if workflow_file in workflow.get("path", ""):
                            workflow_id = workflow["id"]
                            break
                    
                    if not workflow_id:
                        return [TextContent(
                            type="text",
                            text=f"ERROR: Workflow '{workflow_file}' not found"
                        )]
                    
                    runs_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
                    runs_response = requests.get(runs_url, headers=headers, params={"per_page": 1})
                    if runs_response.status_code == 200:
                        runs = runs_response.json().get("workflow_runs", [])
                        if runs:
                            run_id = str(runs[0]["id"])
                        else:
                            return [TextContent(
                                type="text",
                                text=f"No runs found for workflow '{workflow_file}'"
                            )]
                    else:
                        return [TextContent(
                            type="text",
                            text=f"ERROR: Failed to get latest run. Status: {runs_response.status_code}"
                        )]
                
                # Get run details (reuse logic from get_workflow_run_details)
                run_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/runs/{run_id}"
                run_response = requests.get(run_url, headers=headers)
                if run_response.status_code != 200:
                    return [TextContent(
                        type="text",
                        text=f"ERROR: Failed to get run details. Status: {run_response.status_code}"
                    )]
                
                run_data = run_response.json()
                
                # Get jobs
                jobs_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/runs/{run_id}/jobs"
                jobs_response = requests.get(jobs_url, headers=headers)
                jobs_data = jobs_response.json().get("jobs", []) if jobs_response.status_code == 200 else []
                
                # Build monitoring report
                result = f"📊 Monitoring Workflow Run: {run_id}\n"
                result += f"   Workflow: {workflow_file}\n"
                result += f"   Repository: {owner}/{repo}\n"
                result += f"   Status: {run_data.get('status', 'N/A')} | Conclusion: {run_data.get('conclusion', 'N/A')}\n"
                result += f"   URL: https://github.com/{owner}/{repo}/actions/runs/{run_id}\n\n"
                
                # Show current status
                if run_data.get('status') == 'completed':
                    result += f"{'='*70}\n"
                    result += f"Run Completed!\n"
                    result += f"{'='*70}\n\n"
                elif run_data.get('status') == 'in_progress':
                    result += f"{'='*70}\n"
                    result += f"Run In Progress...\n"
                    result += f"{'='*70}\n\n"
                
                # Show jobs progress
                if jobs_data:
                    result += f"Jobs Progress:\n"
                    for job in jobs_data:
                        job_name = job.get('name', 'N/A')
                        job_status = job.get('status', 'N/A')
                        job_conclusion = job.get('conclusion', 'N/A')
                        
                        if job_conclusion == 'success':
                            icon = "✅"
                        elif job_conclusion == 'failure':
                            icon = "❌"
                        elif job_conclusion == 'cancelled':
                            icon = "⚠️"
                        else:
                            icon = "⏳"
                        
                        result += f"{icon} {job_name}: {job_status}"
                        if job_conclusion != 'N/A':
                            result += f" ({job_conclusion})"
                        result += "\n"
                        
                        # Show failed steps
                        steps = job.get('steps', [])
                        failed_steps = [s for s in steps if s.get('conclusion') == 'failure']
                        if failed_steps:
                            result += f"   Failed Steps:\n"
                            for step in failed_steps:
                                result += f"     ✗ {step.get('name', 'N/A')}\n"
                
                result += f"\n💡 Use 'get_workflow_run_details' with run_id={run_id} for full details including logs and timing."
                
                return [TextContent(type="text", text=result)]
            except Exception as e:
                import traceback
                return [TextContent(
                    type="text",
                    text=f"ERROR: Failed to monitor run: {str(e)}\n\n{traceback.format_exc()}"
                )]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        import traceback
        return [TextContent(
            type="text",
            text=f"Error executing tool '{name}': {str(e)}\n\n{traceback.format_exc()}"
        )]


async def main():
    """Run the MCP server."""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())


