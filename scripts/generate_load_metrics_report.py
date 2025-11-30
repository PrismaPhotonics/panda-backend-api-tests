#!/usr/bin/env python3
"""
Load Metrics Report Generator for GitHub Actions
=================================================

Generates a clean markdown report from pytest JSON report.
Designed to appear in GitHub Actions Summary with proper formatting.

NOTE: Uses ASCII characters only to avoid Windows/PowerShell encoding issues.

Usage:
    python scripts/generate_load_metrics_report.py reports/quick-load-metrics.json --output reports/load-metrics-summary.md

Author: QA Automation Architect
Date: 2025-11-30
"""

import json
import sys
import argparse
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import re


# ============================================================================
# Environment-based SLA Configuration
# ============================================================================

def get_environment() -> str:
    """Get current environment from env var."""
    return os.getenv("ENVIRONMENT", "staging").lower()


def get_sla_thresholds() -> Dict[str, Dict[str, float]]:
    """
    Get SLA thresholds based on environment.
    
    Production has stricter SLAs, staging is more lenient.
    """
    env = get_environment()
    
    if env == "prod" or env == "production":
        return {
            'channels': {
                'p50': 500,
                'p95': 1000,
                'p99': 1500,
                'error_rate': 1,
            },
            'ack': {
                'p50': 200,
                'p95': 500,
                'p99': 800,
                'error_rate': 0.5,
            },
            'default': {
                'p50': 500,
                'p95': 1000,
                'p99': 1500,
                'error_rate': 1,
            }
        }
    else:
        # Staging - more lenient thresholds
        return {
            'channels': {
                'p50': 3000,
                'p95': 5000,
                'p99': 8000,
                'error_rate': 10,
            },
            'ack': {
                'p50': 1000,
                'p95': 3000,
                'p99': 5000,
                'error_rate': 5,
            },
            'default': {
                'p50': 2000,
                'p95': 4000,
                'p99': 6000,
                'error_rate': 5,
            }
        }


def parse_test_name(nodeid: str) -> str:
    """Extract clean test name from pytest nodeid."""
    match = re.search(r'::(\w+)$', nodeid)
    if match:
        name = match.group(1)
        return name.replace('_', ' ').title()
    return nodeid


def extract_metrics_from_output(output: str) -> Dict[str, Any]:
    """Extract metrics from test output logs."""
    metrics = {}
    
    # Extract latency values
    latency_patterns = {
        'latency_min': r'Min:\s*([\d.]+)',
        'latency_avg': r'Avg:\s*([\d.]+)',
        'latency_p50': r'P50:\s*([\d.]+)',
        'latency_p95': r'P95:\s*([\d.]+)',
        'latency_p99': r'P99:\s*([\d.]+)',
        'latency_max': r'Max:\s*([\d.]+)',
    }
    
    for key, pattern in latency_patterns.items():
        match = re.search(pattern, output)
        if match:
            metrics[key] = float(match.group(1))
    
    # Extract throughput
    throughput_match = re.search(r'THROUGHPUT:\s*([\d.]+)\s*req/s', output)
    if throughput_match:
        metrics['throughput'] = float(throughput_match.group(1))
    
    # Extract request counts
    total_match = re.search(r'Total Requests:\s*(\d+)', output)
    if total_match:
        metrics['total_requests'] = int(total_match.group(1))
    
    success_match = re.search(r'Successful:\s*(\d+)', output)
    if success_match:
        metrics['successful_requests'] = int(success_match.group(1))
    
    failed_match = re.search(r'Failed:\s*(\d+)', output)
    if failed_match:
        metrics['failed_requests'] = int(failed_match.group(1))
    
    # Extract duration
    duration_match = re.search(r'Duration:\s*([\d.]+)s', output)
    if duration_match:
        metrics['duration'] = float(duration_match.group(1))
    
    return metrics


def get_status_icon(outcome: str) -> str:
    """Get ASCII icon for test outcome."""
    return {
        'passed': '[PASS]',
        'failed': '[FAIL]',
        'skipped': '[SKIP]',
        'error': '[ERROR]',
    }.get(outcome, '[?]')


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.0f}s"


def format_latency_with_status(ms: float, threshold: float) -> str:
    """Format latency with pass/fail indicator."""
    status = "OK" if ms < threshold else "HIGH"
    return f"{ms:.0f}ms ({status})"


def generate_progress_bar(value: float, max_value: float, width: int = 20) -> str:
    """Generate a text progress bar using ASCII characters."""
    if max_value <= 0:
        return "-" * width
    
    filled = int(min(value / max_value, 1.0) * width)
    empty = width - filled
    return "#" * filled + "-" * empty


def get_sla_for_test(test_name: str) -> Dict[str, float]:
    """Get appropriate SLA thresholds based on test name."""
    thresholds = get_sla_thresholds()
    test_lower = test_name.lower()
    if 'channels' in test_lower:
        return thresholds['channels']
    elif 'ack' in test_lower:
        return thresholds['ack']
    return thresholds['default']


def generate_markdown_report(data: Dict[str, Any], output_path: Optional[Path] = None) -> str:
    """Generate clean markdown report for GitHub Actions."""
    lines = []
    env = get_environment()
    
    # Header
    lines.append("# Quick Load Tests Report")
    lines.append("")
    
    # Get summary stats
    summary = data.get('summary', {})
    tests = data.get('tests', [])
    
    passed = summary.get('passed', 0)
    failed = summary.get('failed', 0)
    errors = summary.get('error', 0)
    total = summary.get('total', len(tests))
    duration = data.get('duration', 0)
    
    # Status badge
    if failed == 0 and errors == 0:
        status = "PASSED"
        status_indicator = "[+]"
    else:
        status = "FAILED"
        status_indicator = "[!]"
    
    lines.append(f"> **{status_indicator} STATUS: {status}**")
    lines.append(">")
    lines.append(f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append(f">")
    lines.append(f"> Environment: **{env.upper()}**")
    lines.append("")
    
    # Summary Table
    lines.append("## Overview")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total Tests | **{total}** |")
    lines.append(f"| Passed | **{passed}** |")
    lines.append(f"| Failed | **{failed}** |")
    lines.append(f"| Duration | **{format_duration(duration)}** |")
    lines.append("")
    
    # Collect all metrics
    all_metrics = []
    
    # Test Details
    lines.append("## Test Results")
    lines.append("")
    
    for test in tests:
        nodeid = test.get('nodeid', 'Unknown')
        outcome = test.get('outcome', 'unknown')
        test_duration = test.get('call', {}).get('duration', 0) if 'call' in test else 0
        
        test_name = parse_test_name(nodeid)
        icon = get_status_icon(outcome)
        
        # Get test output
        stdout = ""
        if 'call' in test and 'stdout' in test['call']:
            stdout = test['call']['stdout']
        elif 'setup' in test and 'stdout' in test['setup']:
            stdout = test['setup']['stdout']
        
        longrepr = test.get('call', {}).get('longrepr', '')
        if isinstance(longrepr, str):
            stdout += longrepr
        
        metrics = extract_metrics_from_output(stdout)
        
        if metrics:
            all_metrics.append({
                'name': test_name,
                'outcome': outcome,
                **metrics
            })
        
        # Test header - use <details> with open for failures
        open_tag = ' open' if outcome == 'failed' else ''
        lines.append(f"<details{open_tag}>")
        lines.append(f"<summary><strong>{icon} {test_name}</strong> - {format_duration(test_duration)}</summary>")
        lines.append("")
        
        if metrics:
            # Request metrics table
            if 'total_requests' in metrics:
                success_rate = (metrics.get('successful_requests', 0) / metrics['total_requests'] * 100) if metrics['total_requests'] > 0 else 0
                lines.append("| Metric | Value |")
                lines.append("|--------|-------|")
                lines.append(f"| Total Requests | **{metrics['total_requests']}** |")
                lines.append(f"| Successful | {metrics.get('successful_requests', 0)} ({success_rate:.1f}%) |")
                lines.append(f"| Failed | {metrics.get('failed_requests', 0)} |")
                if 'duration' in metrics:
                    lines.append(f"| Duration | {metrics['duration']:.1f}s |")
                if 'throughput' in metrics:
                    lines.append(f"| Throughput | **{metrics['throughput']:.1f} req/s** |")
                lines.append("")
            
            # Latency table
            if 'latency_p50' in metrics:
                sla = get_sla_for_test(test_name)
                lines.append("**Latency Distribution:**")
                lines.append("")
                lines.append("| Percentile | Value | SLA | Status |")
                lines.append("|------------|-------|-----|--------|")
                
                p50 = metrics.get('latency_p50', 0)
                p95 = metrics.get('latency_p95', 0)
                p99 = metrics.get('latency_p99', 0)
                
                p50_ok = p50 < sla['p50']
                p95_ok = p95 < sla['p95']
                p99_ok = p99 < sla['p99']
                
                lines.append(f"| P50 | {p50:.0f}ms | <{sla['p50']}ms | {'PASS' if p50_ok else 'FAIL'} |")
                lines.append(f"| P95 | {p95:.0f}ms | <{sla['p95']}ms | {'PASS' if p95_ok else 'FAIL'} |")
                lines.append(f"| P99 | {p99:.0f}ms | <{sla['p99']}ms | {'PASS' if p99_ok else 'FAIL'} |")
                lines.append(f"| Max | {metrics.get('latency_max', 0):.0f}ms | - | - |")
                lines.append("")
                
                # Visual latency bar (ASCII)
                max_display = max(sla['p99'] * 1.5, metrics.get('latency_max', 0))
                lines.append("```")
                lines.append(f"Min  |{generate_progress_bar(metrics.get('latency_min', 0), max_display)}| {metrics.get('latency_min', 0):.0f}ms")
                lines.append(f"P50  |{generate_progress_bar(p50, max_display)}| {p50:.0f}ms")
                lines.append(f"P95  |{generate_progress_bar(p95, max_display)}| {p95:.0f}ms")
                lines.append(f"P99  |{generate_progress_bar(p99, max_display)}| {p99:.0f}ms")
                lines.append(f"Max  |{generate_progress_bar(metrics.get('latency_max', 0), max_display)}| {metrics.get('latency_max', 0):.0f}ms")
                lines.append("```")
                lines.append("")
        
        # Show failure message if failed
        if outcome == 'failed' and longrepr:
            lines.append("**Failure Details:**")
            lines.append("```")
            if isinstance(longrepr, str):
                # Extract just the assertion error
                assertion_match = re.search(r'(AssertionError:.*?)(?:\n\n|$)', longrepr, re.DOTALL)
                if assertion_match:
                    lines.append(assertion_match.group(1).strip()[:500])
                else:
                    lines.append(longrepr[:500])
            lines.append("```")
            lines.append("")
        
        lines.append("</details>")
        lines.append("")
    
    # Performance Summary
    if all_metrics:
        lines.append("## Performance Summary")
        lines.append("")
        
        # Calculate aggregates
        p50_values = [m['latency_p50'] for m in all_metrics if 'latency_p50' in m]
        p95_values = [m['latency_p95'] for m in all_metrics if 'latency_p95' in m]
        p99_values = [m['latency_p99'] for m in all_metrics if 'latency_p99' in m]
        throughput_values = [m['throughput'] for m in all_metrics if 'throughput' in m]
        total_requests = sum(m.get('total_requests', 0) for m in all_metrics)
        total_failed = sum(m.get('failed_requests', 0) for m in all_metrics)
        
        if p50_values:
            lines.append("| Metric | Average | Min | Max |")
            lines.append("|--------|---------|-----|-----|")
            lines.append(f"| P50 Latency | {sum(p50_values)/len(p50_values):.0f}ms | {min(p50_values):.0f}ms | {max(p50_values):.0f}ms |")
            if p95_values:
                lines.append(f"| P95 Latency | {sum(p95_values)/len(p95_values):.0f}ms | {min(p95_values):.0f}ms | {max(p95_values):.0f}ms |")
            if p99_values:
                lines.append(f"| P99 Latency | {sum(p99_values)/len(p99_values):.0f}ms | {min(p99_values):.0f}ms | {max(p99_values):.0f}ms |")
            if throughput_values:
                lines.append(f"| Throughput | {sum(throughput_values)/len(throughput_values):.1f} req/s | {min(throughput_values):.1f} req/s | {max(throughput_values):.1f} req/s |")
            lines.append("")
        
        if total_requests > 0:
            overall_success_rate = ((total_requests - total_failed) / total_requests) * 100
            lines.append(f"**Total Requests:** {total_requests}")
            lines.append("")
            lines.append(f"**Overall Success Rate:** {overall_success_rate:.1f}%")
            lines.append("")
    
    # SLA Compliance Summary
    lines.append("## SLA Compliance")
    lines.append("")
    lines.append(f"> Environment: **{env.upper()}** (SLA thresholds adjusted accordingly)")
    lines.append("")
    
    if all_metrics:
        all_passed = all(m.get('outcome') == 'passed' for m in all_metrics)
        
        if all_passed:
            lines.append("> [+] **All SLA targets met!** System is performing within acceptable limits.")
        else:
            lines.append("> [!] **Some SLA targets were not met.** Review the failed tests above for details.")
        lines.append("")
        
        lines.append("| Test | P50 Status | P95 Status | Error Rate |")
        lines.append("|------|------------|------------|------------|")
        
        for metric in all_metrics:
            test_name = metric.get('name', 'Unknown')
            sla = get_sla_for_test(test_name)
            
            p50_status = "PASS" if metric.get('latency_p50', 0) < sla['p50'] else "FAIL"
            p95_status = "PASS" if metric.get('latency_p95', 0) < sla['p95'] else "FAIL"
            
            # Calculate error rate from metrics
            total = metric.get('total_requests', 0)
            failed = metric.get('failed_requests', 0)
            error_rate = (failed / total * 100) if total > 0 else 0
            error_status = "PASS" if error_rate < sla['error_rate'] else "FAIL"
            
            lines.append(f"| {test_name[:30]} | {p50_status} | {p95_status} | {error_rate:.1f}% ({error_status}) |")
    else:
        lines.append("> [!] No metrics collected. Check test execution logs.")
    
    lines.append("")
    
    # Footer
    lines.append("---")
    lines.append("")
    lines.append(f"Generated by Quick Load Tests Report Generator | Environment: {env.upper()} | Branch: chore/add-roy-tests")
    lines.append("")
    lines.append("_Job summary generated at run time_")
    
    report = '\n'.join(lines)
    
    if output_path:
        output_path.write_text(report, encoding='utf-8')
        print(f"Report saved to: {output_path}")
    
    return report


def main():
    parser = argparse.ArgumentParser(
        description="Generate load test metrics report from pytest JSON output"
    )
    parser.add_argument(
        "input_file",
        type=Path,
        help="Path to pytest JSON report file"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output file path (default: print to stdout)"
    )
    
    args = parser.parse_args()
    
    if not args.input_file.exists():
        print(f"Error: Input file not found: {args.input_file}", file=sys.stderr)
        # Generate empty report
        empty_report = generate_empty_report()
        if args.output:
            args.output.write_text(empty_report, encoding='utf-8')
            print(f"Empty report saved to: {args.output}")
        else:
            print(empty_report)
        sys.exit(0)
    
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.input_file}: {e}", file=sys.stderr)
        sys.exit(1)
    
    report = generate_markdown_report(data, args.output)
    
    if not args.output:
        print(report)


def generate_empty_report() -> str:
    """Generate a report when no test data is available."""
    env = get_environment()
    lines = [
        "# Quick Load Tests Report",
        "",
        "> [!] **No test results available**",
        ">",
        f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f">",
        f"> Environment: **{env.upper()}**",
        "",
        "## Overview",
        "",
        "No test metrics were collected. This could mean:",
        "",
        "- Tests failed before generating metrics",
        "- Test configuration error",
        "- Report file was not generated",
        "",
        "Please check the test execution logs for details.",
        "",
        "---",
        "",
        "Generated by Quick Load Tests Report Generator"
    ]
    return '\n'.join(lines)


if __name__ == "__main__":
    main()
