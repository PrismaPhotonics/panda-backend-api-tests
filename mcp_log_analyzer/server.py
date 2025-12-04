"""
MCP Log Analyzer Server
========================

MCP server for real-time log analysis of test logs.
Works with the project's log structure: test_runs/, errors/, warnings/, pod_logs/
"""

import asyncio
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
except ImportError:
    print("ERROR: mcp package not installed. Run: pip install mcp")
    raise

# Initialize MCP server
server = Server("log-analyzer")

# Project root (adjust if needed)
PROJECT_ROOT = Path(__file__).parent.parent
LOGS_DIR = PROJECT_ROOT / "logs"


def get_latest_log_file(log_type: str) -> Optional[Path]:
    """Get the latest log file of a given type."""
    log_dir = LOGS_DIR / log_type
    if not log_dir.exists():
        return None
    
    log_files = sorted(
        log_dir.glob("*.log"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    return log_files[0] if log_files else None


def read_log_tail(file_path: Path, lines: int = 50) -> str:
    """Read the last N lines from a log file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines_list = content.split('\n')
            return '\n'.join(lines_list[-lines:])
    except Exception as e:
        return f"Error reading log file: {e}"


def search_in_logs(pattern: str, log_type: str = "all", max_results: int = 100) -> List[Dict[str, Any]]:
    """Search for pattern in logs."""
    results = []
    regex = re.compile(pattern, re.IGNORECASE)
    
    # Determine which directories to search
    if log_type == "all":
        search_dirs = ["test_runs", "errors", "warnings", "pod_logs"]
    else:
        search_dirs = [log_type]
    
    for dir_name in search_dirs:
        log_dir = LOGS_DIR / dir_name
        if not log_dir.exists():
            continue
        
        # Search in recent log files (last 24 hours)
        cutoff_time = datetime.now() - timedelta(days=1)
        
        for log_file in log_dir.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_time.timestamp():
                continue
            
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if regex.search(line):
                            results.append({
                                "file": str(log_file.relative_to(PROJECT_ROOT)),
                                "line": line_num,
                                "content": line.strip()
                            })
                            if len(results) >= max_results:
                                return results
            except Exception:
                continue
    
    return results


def analyze_errors(time_range: str = "last hour") -> Dict[str, Any]:
    """Analyze errors in logs."""
    # Parse time range
    if "hour" in time_range.lower():
        hours = 1
    elif "day" in time_range.lower():
        hours = 24
    elif "minute" in time_range.lower():
        minutes = int(re.search(r'\d+', time_range).group() if re.search(r'\d+', time_range) else "10")
        hours = minutes / 60
    else:
        hours = 1
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    errors = []
    
    # Search in errors directory
    errors_dir = LOGS_DIR / "errors"
    if errors_dir.exists():
        for log_file in errors_dir.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_time.timestamp():
                continue
            
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if any(keyword in line.lower() for keyword in ["error", "exception", "failed", "timeout"]):
                            errors.append({
                                "file": log_file.name,
                                "content": line.strip()
                            })
            except Exception:
                continue
    
    return {
        "total_errors": len(errors),
        "time_range": time_range,
        "errors": errors[:50]  # Limit to 50 most recent
    }


@server.list_tools()
async def list_tools():
    """List available tools."""
    return [
        Tool(
            name="tail_logs",
            description="Show the last N lines from a log file (real-time tail)",
            inputSchema={
                "type": "object",
                "properties": {
                    "log_type": {
                        "type": "string",
                        "enum": ["test_runs", "errors", "warnings", "pod_logs"],
                        "description": "Type of log to tail",
                        "default": "test_runs"
                    },
                    "lines": {
                        "type": "integer",
                        "default": 50,
                        "description": "Number of lines to show"
                    }
                },
                "required": ["log_type"]
            }
        ),
        Tool(
            name="search_logs",
            description="Search logs for a pattern (supports regex)",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Search pattern (regex supported)"
                    },
                    "log_type": {
                        "type": "string",
                        "enum": ["test_runs", "errors", "warnings", "pod_logs", "all"],
                        "default": "all",
                        "description": "Type of log to search"
                    },
                    "max_results": {
                        "type": "integer",
                        "default": 100,
                        "description": "Maximum number of results"
                    }
                },
                "required": ["pattern"]
            }
        ),
        Tool(
            name="analyze_errors",
            description="Analyze errors in logs for a time range",
            inputSchema={
                "type": "object",
                "properties": {
                    "time_range": {
                        "type": "string",
                        "default": "last hour",
                        "description": "Time range (e.g., 'last hour', 'last day', 'last 10 minutes')"
                    }
                }
            }
        ),
        Tool(
            name="get_test_logs",
            description="Get logs for a specific test",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_name": {
                        "type": "string",
                        "description": "Test name or pattern to search for"
                    },
                    "log_type": {
                        "type": "string",
                        "enum": ["test_runs", "errors", "warnings", "pod_logs", "all"],
                        "default": "all"
                    }
                },
                "required": ["test_name"]
            }
        ),
        Tool(
            name="list_recent_logs",
            description="List recent log files",
            inputSchema={
                "type": "object",
                "properties": {
                    "log_type": {
                        "type": "string",
                        "enum": ["test_runs", "errors", "warnings", "pod_logs", "all"],
                        "default": "all"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 10,
                        "description": "Maximum number of files to list"
                    }
                }
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Handle tool calls."""
    try:
        if name == "tail_logs":
            log_type = arguments.get("log_type", "test_runs")
            lines = arguments.get("lines", 50)
            
            log_file = get_latest_log_file(log_type)
            if not log_file:
                return [TextContent(
                    type="text",
                    text=f"No log files found in logs/{log_type}/"
                )]
            
            content = read_log_tail(log_file, lines)
            return [TextContent(
                type="text",
                text=f"Last {lines} lines from {log_file.name}:\n\n{content}"
            )]
        
        elif name == "search_logs":
            pattern = arguments.get("pattern")
            log_type = arguments.get("log_type", "all")
            max_results = arguments.get("max_results", 100)
            
            results = search_in_logs(pattern, log_type, max_results)
            
            if not results:
                return [TextContent(
                    type="text",
                    text=f"No matches found for pattern '{pattern}'"
                )]
            
            result_text = f"Found {len(results)} matches for '{pattern}':\n\n"
            for i, result in enumerate(results[:20], 1):  # Show first 20
                result_text += f"{i}. {result['file']}:{result['line']}\n"
                result_text += f"   {result['content']}\n\n"
            
            if len(results) > 20:
                result_text += f"... and {len(results) - 20} more results\n"
            
            return [TextContent(type="text", text=result_text)]
        
        elif name == "analyze_errors":
            time_range = arguments.get("time_range", "last hour")
            analysis = analyze_errors(time_range)
            
            result_text = f"Error Analysis ({time_range}):\n"
            result_text += f"Total errors found: {analysis['total_errors']}\n\n"
            
            if analysis['errors']:
                result_text += "Recent errors:\n"
                for i, error in enumerate(analysis['errors'][:10], 1):
                    result_text += f"{i}. [{error['file']}] {error['content']}\n"
            else:
                result_text += "No errors found in the specified time range.\n"
            
            return [TextContent(type="text", text=result_text)]
        
        elif name == "get_test_logs":
            test_name = arguments.get("test_name")
            log_type = arguments.get("log_type", "all")
            
            # Search for test name in logs
            results = search_in_logs(test_name, log_type, max_results=200)
            
            if not results:
                return [TextContent(
                    type="text",
                    text=f"No logs found for test '{test_name}'"
                )]
            
            result_text = f"Logs for test '{test_name}' ({len(results)} matches):\n\n"
            for result in results[:30]:  # Show first 30
                result_text += f"[{result['file']}:{result['line']}] {result['content']}\n"
            
            if len(results) > 30:
                result_text += f"\n... and {len(results) - 30} more lines\n"
            
            return [TextContent(type="text", text=result_text)]
        
        elif name == "list_recent_logs":
            log_type = arguments.get("log_type", "all")
            limit = arguments.get("limit", 10)
            
            if log_type == "all":
                search_dirs = ["test_runs", "errors", "warnings", "pod_logs"]
            else:
                search_dirs = [log_type]
            
            result_text = "Recent log files:\n\n"
            all_files = []
            
            for dir_name in search_dirs:
                log_dir = LOGS_DIR / dir_name
                if not log_dir.exists():
                    continue
                
                for log_file in log_dir.glob("*.log"):
                    mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                    all_files.append({
                        "path": str(log_file.relative_to(PROJECT_ROOT)),
                        "size": log_file.stat().st_size,
                        "modified": mtime
                    })
            
            # Sort by modification time
            all_files.sort(key=lambda x: x["modified"], reverse=True)
            
            for i, file_info in enumerate(all_files[:limit], 1):
                size_kb = file_info["size"] / 1024
                result_text += f"{i}. {file_info['path']}\n"
                result_text += f"   Modified: {file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}\n"
                result_text += f"   Size: {size_kb:.1f} KB\n\n"
            
            return [TextContent(type="text", text=result_text)]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing tool '{name}': {str(e)}"
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

