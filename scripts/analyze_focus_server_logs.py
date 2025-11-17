#!/usr/bin/env python3
"""
Script to analyze Focus Server logs to find the exact source of the validation error.

This script:
1. Gets Focus Server logs via SSH/kubectl
2. Analyzes the error messages to find patterns
3. Looks for stack traces or error context
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


def analyze_logs_for_error_source(logs: str) -> Dict[str, Any]:
    """
    Analyze logs to find the source of the validation error.
    
    Args:
        logs: Log content as string
        
    Returns:
        Dictionary with findings
    """
    findings = {
        "error_count": 0,
        "error_lines": [],
        "stack_traces": [],
        "error_context": []
    }
    
    lines = logs.split('\n')
    
    # Pattern for the error
    error_pattern = re.compile(
        r'Cannot configure job.*validation failed.*Cannot proceed.*Missing required.*prr',
        re.IGNORECASE
    )
    
    # Pattern for stack traces
    stack_trace_pattern = re.compile(r'Traceback|File ".*", line \d+|at .*\(.*\)')
    
    for i, line in enumerate(lines):
        if error_pattern.search(line):
            findings["error_count"] += 1
            findings["error_lines"].append({
                "line_number": i + 1,
                "content": line,
                "timestamp": extract_timestamp(line)
            })
            
            # Look for context (lines before and after)
            context_start = max(0, i - 10)
            context_end = min(len(lines), i + 10)
            context = '\n'.join(lines[context_start:context_end])
            
            findings["error_context"].append({
                "line_number": i + 1,
                "context": context
            })
            
            # Look for stack trace nearby
            for j in range(max(0, i - 50), min(len(lines), i + 50)):
                if stack_trace_pattern.search(lines[j]):
                    stack_trace = extract_stack_trace(lines, j)
                    if stack_trace:
                        findings["stack_traces"].append({
                            "error_line": i + 1,
                            "stack_trace": stack_trace
                        })
                        break
    
    return findings


def extract_timestamp(line: str) -> Optional[str]:
    """Extract timestamp from log line."""
    # Common timestamp formats
    patterns = [
        r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[\+\-]\d{4})',
        r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, line)
        if match:
            return match.group(1)
    
    return None


def extract_stack_trace(lines: List[str], start_line: int) -> Optional[str]:
    """Extract stack trace starting from start_line."""
    stack_trace_lines = []
    
    for i in range(start_line, min(len(lines), start_line + 30)):
        line = lines[i]
        stack_trace_lines.append(line)
        
        # Stop if we hit an empty line after stack trace
        if i > start_line and not line.strip() and len(stack_trace_lines) > 3:
            break
    
    if len(stack_trace_lines) > 3:
        return '\n'.join(stack_trace_lines)
    
    return None


def main():
    """Main analysis function."""
    logger.info("=" * 80)
    logger.info("Analyzing Focus Server logs for validation error source")
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
    pods = k8s_manager.get_pods(namespace="panda")
    focus_pods = [p for p in pods if "focus-server" in p.get("name", "").lower()]
    
    if not focus_pods:
        logger.warning("No Focus Server pods found")
        return
    
    logger.info(f"Found {len(focus_pods)} Focus Server pod(s)")
    
    # Analyze logs from each pod
    all_findings = {}
    
    for pod in focus_pods:
        pod_name = pod.get("name")
        logger.info(f"Analyzing logs from pod: {pod_name}")
        
        try:
            # Get more logs (last 2000 lines to catch stack traces)
            logs = k8s_manager.get_pod_logs(pod_name, namespace="panda", tail_lines=2000)
            
            # Analyze logs
            findings = analyze_logs_for_error_source(logs)
            all_findings[pod_name] = findings
            
            logger.info(f"Found {findings['error_count']} error occurrences")
            logger.info(f"Found {len(findings['stack_traces'])} stack traces")
            
            # Print first error with context
            if findings["error_context"]:
                logger.info("\n" + "=" * 80)
                logger.info("FIRST ERROR WITH CONTEXT:")
                logger.info("=" * 80)
                first_error = findings["error_context"][0]
                logger.info(f"\nLine {first_error['line_number']}:")
                logger.info(first_error["context"])
            
            # Print stack traces
            if findings["stack_traces"]:
                logger.info("\n" + "=" * 80)
                logger.info("STACK TRACES FOUND:")
                logger.info("=" * 80)
                for i, st in enumerate(findings["stack_traces"][:3]):  # First 3
                    logger.info(f"\nStack Trace #{i+1} (near error line {st['error_line']}):")
                    logger.info(st["stack_trace"])
        
        except Exception as e:
            logger.error(f"Error analyzing logs from pod {pod_name}: {e}")
    
    # Save results
    output_file = project_root / "docs" / "04_testing" / "analysis" / f"FOCUS_SERVER_LOGS_ANALYSIS_{Path(__file__).stem}.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Focus Server Logs Analysis - Validation Error Source\n\n")
        f.write("## Summary\n\n")
        
        for pod_name, findings in all_findings.items():
            f.write(f"### {pod_name}\n\n")
            f.write(f"- Error count: {findings['error_count']}\n")
            f.write(f"- Stack traces found: {len(findings['stack_traces'])}\n\n")
            
            if findings["error_context"]:
                f.write("### First Error Context\n\n")
                f.write(f"```\n{findings['error_context'][0]['context']}\n```\n\n")
            
            if findings["stack_traces"]:
                f.write("### Stack Traces\n\n")
                for i, st in enumerate(findings["stack_traces"][:3]):
                    f.write(f"#### Stack Trace #{i+1}\n\n")
                    f.write(f"```\n{st['stack_trace']}\n```\n\n")
    
    logger.info(f"\nResults saved to: {output_file}")
    logger.info("Analysis complete!")


if __name__ == "__main__":
    main()

