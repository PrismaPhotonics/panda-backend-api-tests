#!/usr/bin/env python3
"""
Load Metrics Report Generator for GitHub Actions
=================================================

Generates a beautiful markdown report from pytest JSON report.
Designed to appear in GitHub Actions Summary with proper formatting.

Usage:
    python scripts/generate_load_metrics_report.py reports/quick-load-metrics.json --output reports/load-metrics-summary.md

Author: QA Automation Architect
Date: 2025-11-30
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import re


# ============================================================================
# SLA THRESHOLDS (must match test_quick_load_metrics.py)
# ============================================================================

SLA_THRESHOLDS = {
    'channels': {
        'p50': 1000,   # ms
        'p95': 1500,   # ms
        'p99': 2000,   # ms
        'error_rate': 5,  # %
    },
    'ack': {
        'p50': 800,    # ms
        'p95': 1200,   # ms
        'p99': 1500,   # ms
        'error_rate': 1,  # %
    },
    'default': {
        'p50': 1000,
        'p95': 1500,
        'p99': 2000,
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


def get_status_emoji(outcome: str) -> str:
    """Get emoji for test outcome."""
    return {
        'passed': '✅',
        'failed': '❌',
        'skipped': '⏭️',
        'error': '💥',
    }.get(outcome, '❓')


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


def format_latency(ms: float) -> str:
    """Format latency with color indicator."""
    if ms < 200:
        return f"🟢 {ms:.0f}ms"
    elif ms < 500:
        return f"🟡 {ms:.0f}ms"
    elif ms < 1000:
        return f"🟠 {ms:.0f}ms"
    else:
        return f"🔴 {ms:.0f}ms"


def generate_progress_bar(value: float, max_value: float, width: int = 15) -> str:
    """Generate a text progress bar."""
    if max_value <= 0:
        return "░" * width
    
    filled = int(min(value / max_value, 1.0) * width)
    empty = width - filled
    return "█" * filled + "░" * empty


def get_sla_for_test(test_name: str) -> Dict[str, float]:
    """Get appropriate SLA thresholds based on test name."""
    test_lower = test_name.lower()
    if 'channels' in test_lower:
        return SLA_THRESHOLDS['channels']
    elif 'ack' in test_lower:
        return SLA_THRESHOLDS['ack']
    return SLA_THRESHOLDS['default']


def generate_markdown_report(data: Dict[str, Any], output_path: Optional[Path] = None) -> str:
    """Generate beautiful markdown report for GitHub Actions."""
    lines = []
    
    # Header with badge-style summary
    lines.append("# 🚀 Quick Load Tests Report")
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
        status_badge = "![Status](https://img.shields.io/badge/Status-PASSED-success?style=for-the-badge)"
    else:
        status_badge = "![Status](https://img.shields.io/badge/Status-FAILED-critical?style=for-the-badge)"
    
    lines.append(f"> {status_badge}")
    lines.append(">")
    lines.append(f"> **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append("")
    
    # Quick Summary Cards
    lines.append("## 📊 Overview")
    lines.append("")
    lines.append("<table>")
    lines.append("<tr>")
    lines.append(f"<td align='center'><h3>🧪 {total}</h3><br/>Total Tests</td>")
    lines.append(f"<td align='center'><h3>✅ {passed}</h3><br/>Passed</td>")
    lines.append(f"<td align='center'><h3>❌ {failed}</h3><br/>Failed</td>")
    lines.append(f"<td align='center'><h3>⏱️ {format_duration(duration)}</h3><br/>Duration</td>")
    lines.append("</tr>")
    lines.append("</table>")
    lines.append("")
    
    # Collect all metrics
    all_metrics = []
    
    # Test Details
    lines.append("## 🔬 Test Results")
    lines.append("")
    
    for test in tests:
        nodeid = test.get('nodeid', 'Unknown')
        outcome = test.get('outcome', 'unknown')
        test_duration = test.get('call', {}).get('duration', 0) if 'call' in test else 0
        
        test_name = parse_test_name(nodeid)
        emoji = get_status_emoji(outcome)
        
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
        
        # Test header
        lines.append(f"<details {'open' if outcome == 'failed' else ''}>")
        lines.append(f"<summary><strong>{emoji} {test_name}</strong> - {format_duration(test_duration)}</summary>")
        lines.append("")
        
        if metrics:
            # Metrics table
            if 'total_requests' in metrics:
                success_rate = (metrics.get('successful_requests', 0) / metrics['total_requests'] * 100) if metrics['total_requests'] > 0 else 0
                lines.append("| Metric | Value |")
                lines.append("|--------|-------|")
                lines.append(f"| 📬 Total Requests | **{metrics['total_requests']}** |")
                lines.append(f"| ✅ Successful | {metrics.get('successful_requests', 0)} ({success_rate:.1f}%) |")
                lines.append(f"| ❌ Failed | {metrics.get('failed_requests', 0)} |")
                if 'duration' in metrics:
                    lines.append(f"| ⏱️ Duration | {metrics['duration']:.1f}s |")
                if 'throughput' in metrics:
                    lines.append(f"| 🚀 Throughput | **{metrics['throughput']:.1f} req/s** |")
                lines.append("")
            
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
                
                lines.append(f"| P50 | {format_latency(p50)} | <{sla['p50']}ms | {'✅' if p50_ok else '❌'} |")
                lines.append(f"| P95 | {format_latency(p95)} | <{sla['p95']}ms | {'✅' if p95_ok else '❌'} |")
                lines.append(f"| P99 | {format_latency(p99)} | <{sla['p99']}ms | {'✅' if p99_ok else '❌'} |")
                lines.append(f"| Max | {format_latency(metrics.get('latency_max', 0))} | - | - |")
                lines.append("")
                
                # Visual latency bar
                lines.append("```")
                lines.append(f"Min  {generate_progress_bar(metrics.get('latency_min', 0), 2000)} {metrics.get('latency_min', 0):.0f}ms")
                lines.append(f"P50  {generate_progress_bar(p50, 2000)} {p50:.0f}ms")
                lines.append(f"P95  {generate_progress_bar(p95, 2000)} {p95:.0f}ms")
                lines.append(f"P99  {generate_progress_bar(p99, 2000)} {p99:.0f}ms")
                lines.append(f"Max  {generate_progress_bar(metrics.get('latency_max', 0), 2000)} {metrics.get('latency_max', 0):.0f}ms")
                lines.append("```")
                lines.append("")
        
        # Show failure message if failed
        if outcome == 'failed' and longrepr:
            lines.append("**❌ Failure Details:**")
            lines.append("```")
            if isinstance(longrepr, str):
                # Extract just the assertion error
                assertion_match = re.search(r'(AssertionError:.*?)(?:\n\n|$)', longrepr, re.DOTALL)
                if assertion_match:
                    lines.append(assertion_match.group(1).strip()[:300])
                else:
                    lines.append(longrepr[:300])
            lines.append("```")
            lines.append("")
        
        lines.append("</details>")
        lines.append("")
    
    # Aggregate Summary
    if all_metrics:
        lines.append("## 📈 Performance Summary")
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
            lines.append(f"| **P50 Latency** | {sum(p50_values)/len(p50_values):.0f}ms | {min(p50_values):.0f}ms | {max(p50_values):.0f}ms |")
            if p95_values:
                lines.append(f"| **P95 Latency** | {sum(p95_values)/len(p95_values):.0f}ms | {min(p95_values):.0f}ms | {max(p95_values):.0f}ms |")
            if p99_values:
                lines.append(f"| **P99 Latency** | {sum(p99_values)/len(p99_values):.0f}ms | {min(p99_values):.0f}ms | {max(p99_values):.0f}ms |")
            if throughput_values:
                lines.append(f"| **Throughput** | {sum(throughput_values)/len(throughput_values):.1f} req/s | {min(throughput_values):.1f} req/s | {max(throughput_values):.1f} req/s |")
            lines.append("")
        
        if total_requests > 0:
            overall_success_rate = ((total_requests - total_failed) / total_requests) * 100
            lines.append(f"**📬 Total Requests:** {total_requests}")
            lines.append("")
            lines.append(f"**✅ Overall Success Rate:** {overall_success_rate:.1f}%")
            lines.append("")
    
    # SLA Compliance Summary
    lines.append("## 🎯 SLA Compliance")
    lines.append("")
    
    if all_metrics:
        all_passed = all(m.get('outcome') == 'passed' for m in all_metrics)
        
        if all_passed:
            lines.append("> ✅ **All SLA targets met!** The system is performing within acceptable limits.")
        else:
            lines.append("> ⚠️ **Some SLA targets were not met.** Review the failed tests above for details.")
        lines.append("")
        
        lines.append("| SLA Target | Threshold | Status |")
        lines.append("|------------|-----------|--------|")
        
        for metric in all_metrics:
            test_name = metric.get('name', 'Unknown')
            sla = get_sla_for_test(test_name)
            
            if 'latency_p50' in metric:
                p50_ok = metric['latency_p50'] < sla['p50']
                lines.append(f"| {test_name} - P50 | <{sla['p50']}ms | {'✅ PASS' if p50_ok else '❌ FAIL'} |")
    else:
        lines.append("> ⚠️ No metrics collected. Check test execution logs.")
    
    lines.append("")
    
    # Footer
    lines.append("---")
    lines.append("")
    lines.append("<sub>🤖 Generated by Quick Load Tests Report Generator | ")
    lines.append(f"Environment: **Staging** | ")
    lines.append(f"Branch: **chore/add-roy-tests**</sub>")
    
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
    lines = [
        "# 🚀 Quick Load Tests Report",
        "",
        "> ⚠️ **No test results available**",
        ">",
        f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        "## 📊 Overview",
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
        "<sub>🤖 Generated by Quick Load Tests Report Generator</sub>"
    ]
    return '\n'.join(lines)


if __name__ == "__main__":
    main()
