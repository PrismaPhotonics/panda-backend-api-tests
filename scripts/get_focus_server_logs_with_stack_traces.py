#!/usr/bin/env python3
"""
Script to get Focus Server logs with stack traces to find the exact source of the validation error.

This script:
1. Gets Focus Server logs via kubectl/SSH
2. Searches for the error message and stack traces
3. Analyzes the stack traces to find the exact source
"""

import sys
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.config_manager import ConfigManager
from src.infrastructure.kubernetes_manager import KubernetesManager

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


def extract_stack_traces(logs: str) -> List[Dict[str, Any]]:
    """
    Extract stack traces from logs.
    
    Args:
        logs: Log content as string
        
    Returns:
        List of stack traces with context
    """
    stack_traces = []
    lines = logs.split('\n')
    
    # Pattern for stack trace start
    traceback_pattern = re.compile(r'Traceback.*\(most recent call last\)', re.IGNORECASE)
    file_line_pattern = re.compile(r'File\s+"([^"]+)",\s+line\s+(\d+)', re.IGNORECASE)
    error_pattern = re.compile(r'(?:Error|Exception|ValueError|InvalidArgument|ValidationError):\s*(.+)', re.IGNORECASE)
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if this is the start of a stack trace
        if traceback_pattern.search(line):
            stack_trace = {
                "start_line": i + 1,
                "lines": [],
                "files": [],
                "error_message": None
            }
            
            # Collect stack trace lines
            j = i
            while j < len(lines) and j < i + 50:  # Limit to 50 lines per stack trace
                trace_line = lines[j]
                stack_trace["lines"].append(trace_line)
                
                # Extract file and line number
                file_match = file_line_pattern.search(trace_line)
                if file_match:
                    file_path = file_match.group(1)
                    line_num = file_match.group(2)
                    stack_trace["files"].append({
                        "file": file_path,
                        "line": int(line_num),
                        "content": trace_line
                    })
                
                # Extract error message
                error_match = error_pattern.search(trace_line)
                if error_match and not stack_trace["error_message"]:
                    stack_trace["error_message"] = error_match.group(1)
                
                # Check if this is the end of the stack trace (empty line or new traceback)
                if j > i and (not trace_line.strip() or traceback_pattern.search(trace_line)):
                    break
                
                j += 1
            
            if stack_trace["files"] or stack_trace["error_message"]:
                # Get context before the stack trace (10 lines)
                context_start = max(0, i - 10)
                stack_trace["context_before"] = '\n'.join(lines[context_start:i])
                stack_traces.append(stack_trace)
            
            i = j
        else:
            i += 1
    
    return stack_traces


def find_error_with_stack_traces(logs: str, error_pattern: str) -> List[Dict[str, Any]]:
    """
    Find error messages with their associated stack traces.
    
    Args:
        logs: Log content as string
        error_pattern: Pattern to search for in error messages
        
    Returns:
        List of errors with stack traces
    """
    errors_with_traces = []
    lines = logs.split('\n')
    
    # Compile error pattern
    pattern = re.compile(error_pattern, re.IGNORECASE)
    
    # Find all error lines
    error_lines = []
    for i, line in enumerate(lines):
        if pattern.search(line):
            error_lines.append({
                "line_number": i + 1,
                "content": line
            })
    
    # Extract stack traces
    stack_traces = extract_stack_traces(logs)
    
    # Match errors with stack traces
    for error_line in error_lines:
        error_info = {
            "error_line": error_line,
            "stack_traces": []
        }
        
        # Find stack traces that appear after this error (within 100 lines)
        for stack_trace in stack_traces:
            if (stack_trace["start_line"] > error_line["line_number"] and 
                stack_trace["start_line"] < error_line["line_number"] + 100):
                error_info["stack_traces"].append(stack_trace)
        
        if error_info["stack_traces"]:
            errors_with_traces.append(error_info)
    
    return errors_with_traces


def main():
    """Main analysis function."""
    logger.info("=" * 80)
    logger.info("Getting Focus Server logs with stack traces")
    logger.info("=" * 80)
    
    # Initialize config manager
    try:
        config_manager = ConfigManager(env="staging")
    except Exception as e:
        logger.error(f"Failed to initialize config manager: {e}")
        return
    
    # Initialize Kubernetes manager
    try:
        k8s_manager = KubernetesManager(config_manager)
    except Exception as e:
        logger.error(f"Failed to initialize Kubernetes manager: {e}")
        return
    
    # Get Focus Server pods
    try:
        pods = k8s_manager.get_pods(namespace="panda")
        focus_pods = [p for p in pods if "focus-server" in p.get("name", "").lower()]
        
        if not focus_pods:
            logger.warning("No Focus Server pods found")
            return
        
        logger.info(f"Found {len(focus_pods)} Focus Server pod(s)")
    except Exception as e:
        logger.error(f"Error getting pods: {e}")
        return
    
    # Analyze logs from each pod
    all_findings = {}
    
    for pod in focus_pods:
        pod_name = pod.get("name")
        logger.info(f"Analyzing logs from pod: {pod_name}")
        
        try:
            # Get more logs (last 5000 lines to catch stack traces)
            logs = k8s_manager.get_pod_logs(pod_name, namespace="panda", tail_lines=5000)
            
            # Find errors with stack traces
            error_pattern = r"Cannot proceed.*Missing required.*prr|Cannot configure job.*validation failed"
            errors_with_traces = find_error_with_stack_traces(logs, error_pattern)
            
            all_findings[pod_name] = {
                "errors_found": len(errors_with_traces),
                "errors_with_traces": errors_with_traces
            }
            
            logger.info(f"Found {len(errors_with_traces)} errors with stack traces")
            
            # Print first error with stack trace
            if errors_with_traces:
                logger.info("\n" + "=" * 80)
                logger.info("FIRST ERROR WITH STACK TRACE:")
                logger.info("=" * 80)
                first_error = errors_with_traces[0]
                logger.info(f"\nError Line {first_error['error_line']['line_number']}:")
                logger.info(first_error['error_line']['content'])
                
                if first_error['stack_traces']:
                    logger.info("\nStack Trace:")
                    for st in first_error['stack_traces']:
                        logger.info(f"\nStack Trace (starting at line {st['start_line']}):")
                        logger.info('\n'.join(st['lines'][:30]))  # First 30 lines
                        
                        if st['files']:
                            logger.info("\nFiles in stack trace:")
                            for file_info in st['files'][:10]:  # First 10 files
                                logger.info(f"  {file_info['file']}:{file_info['line']}")
                        
                        if st['error_message']:
                            logger.info(f"\nError message: {st['error_message']}")
        
        except Exception as e:
            logger.error(f"Error analyzing logs from pod {pod_name}: {e}")
    
    # Save results
    output_file = project_root / "docs" / "04_testing" / "analysis" / f"FOCUS_SERVER_LOGS_STACK_TRACES_{Path(__file__).stem}.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Focus Server Logs with Stack Traces\n\n")
        f.write("## Summary\n\n")
        
        for pod_name, findings in all_findings.items():
            f.write(f"### {pod_name}\n\n")
            f.write(f"- Errors found: {findings['errors_found']}\n\n")
            
            if findings['errors_with_traces']:
                f.write("## Errors with Stack Traces\n\n")
                for i, error_info in enumerate(findings['errors_with_traces'][:5]):  # First 5
                    f.write(f"### Error #{i+1}\n\n")
                    f.write(f"**Line {error_info['error_line']['line_number']}:**\n")
                    f.write(f"```\n{error_info['error_line']['content']}\n```\n\n")
                    
                    if error_info['stack_traces']:
                        for st in error_info['stack_traces']:
                            f.write(f"**Stack Trace (starting at line {st['start_line']}):**\n\n")
                            f.write("```\n")
                            f.write('\n'.join(st['lines'][:50]))  # First 50 lines
                            f.write("\n```\n\n")
                            
                            if st['files']:
                                f.write("**Files in stack trace:**\n\n")
                                for file_info in st['files'][:15]:  # First 15 files
                                    f.write(f"- `{file_info['file']}:{file_info['line']}`\n")
                                f.write("\n")
                            
                            if st['error_message']:
                                f.write(f"**Error message:** `{st['error_message']}`\n\n")
    
    logger.info(f"\nResults saved to: {output_file}")
    logger.info("Analysis complete!")


if __name__ == "__main__":
    main()

