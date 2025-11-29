#!/usr/bin/env python3
"""
Load Metrics Report Generator
=============================

Generates a beautiful markdown report from pytest JSON report.
Shows key performance metrics: TPS, latency percentiles, error rates.

Usage:
    python scripts/generate_load_metrics_report.py reports/quick-load-metrics.json --output reports/load-metrics-summary.md

Author: QA Automation Architect
Date: 2025-11-29
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import re


def parse_test_name(nodeid: str) -> str:
    """Extract clean test name from pytest nodeid."""
    # Example: be_focus_server_tests/load/test_quick_load_metrics.py::TestQuickLoadMetrics::test_api_latency
    match = re.search(r'::(\w+)$', nodeid)
    if match:
        name = match.group(1)
        # Convert snake_case to Title Case
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
    
    # Extract error rate
    error_rate_match = re.search(r'(\d+\.?\d*)\s*%\s*\)', output)
    if error_rate_match:
        metrics['error_rate'] = float(error_rate_match.group(1))
    
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


def generate_latency_bar(value: float, max_value: float = 1000) -> str:
    """Generate ASCII bar for latency visualization."""
    if max_value <= 0:
        return ""
    
    bar_length = 20
    filled = int(min(value / max_value, 1.0) * bar_length)
    empty = bar_length - filled
    
    # Color based on value
    if value < 100:
        color = "🟢"
    elif value < 300:
        color = "🟡"
    elif value < 500:
        color = "🟠"
    else:
        color = "🔴"
    
    return f"{color} {'█' * filled}{'░' * empty} {value:.0f}ms"


def generate_markdown_report(data: Dict[str, Any], output_path: Optional[Path] = None) -> str:
    """Generate markdown report from pytest JSON report."""
    lines = []
    
    # Header
    lines.append("# 📊 Load Test Metrics Report")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    # Summary stats
    summary = data.get('summary', {})
    tests = data.get('tests', [])
    
    passed = summary.get('passed', 0)
    failed = summary.get('failed', 0)
    total = summary.get('total', len(tests))
    duration = data.get('duration', 0)
    
    lines.append("## 📋 Summary")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total Tests | {total} |")
    lines.append(f"| Passed | {passed} ✅ |")
    lines.append(f"| Failed | {failed} ❌ |")
    lines.append(f"| Duration | {format_duration(duration)} |")
    lines.append("")
    
    # Collect all metrics
    all_metrics = []
    
    lines.append("## 🧪 Test Results")
    lines.append("")
    
    for test in tests:
        nodeid = test.get('nodeid', 'Unknown')
        outcome = test.get('outcome', 'unknown')
        test_duration = test.get('call', {}).get('duration', 0) if 'call' in test else 0
        
        test_name = parse_test_name(nodeid)
        emoji = get_status_emoji(outcome)
        
        lines.append(f"### {emoji} {test_name}")
        lines.append("")
        lines.append(f"- **Status:** {outcome.upper()}")
        lines.append(f"- **Duration:** {format_duration(test_duration)}")
        
        # Extract metrics from output
        stdout = ""
        if 'call' in test and 'stdout' in test['call']:
            stdout = test['call']['stdout']
        elif 'setup' in test and 'stdout' in test['setup']:
            stdout = test['setup']['stdout']
        
        # Also check longrepr for output
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
            
            lines.append("")
            lines.append("**Metrics:**")
            lines.append("")
            
            if 'total_requests' in metrics:
                lines.append(f"| Requests | {metrics['total_requests']} |")
                lines.append("|----------|------|")
                lines.append(f"| Successful | {metrics.get('successful_requests', 0)} |")
                lines.append(f"| Failed | {metrics.get('failed_requests', 0)} |")
                if 'error_rate' in metrics:
                    lines.append(f"| Error Rate | {metrics['error_rate']:.1f}% |")
                lines.append("")
            
            if 'latency_p50' in metrics:
                lines.append("**Latency Distribution:**")
                lines.append("```")
                lines.append(f"P50:  {generate_latency_bar(metrics.get('latency_p50', 0))}")
                lines.append(f"P95:  {generate_latency_bar(metrics.get('latency_p95', 0))}")
                lines.append(f"P99:  {generate_latency_bar(metrics.get('latency_p99', 0))}")
                lines.append(f"Max:  {generate_latency_bar(metrics.get('latency_max', 0))}")
                lines.append("```")
                lines.append("")
            
            if 'throughput' in metrics:
                lines.append(f"**Throughput:** {metrics['throughput']:.1f} req/s")
                lines.append("")
        
        # Show failure message if failed
        if outcome == 'failed':
            longrepr = test.get('call', {}).get('longrepr', '')
            if longrepr:
                lines.append("")
                lines.append("**Failure:**")
                lines.append("```")
                if isinstance(longrepr, str):
                    lines.append(longrepr[:500])  # Truncate long errors
                lines.append("```")
                lines.append("")
        
        lines.append("---")
        lines.append("")
    
    # Aggregate metrics summary
    if all_metrics:
        lines.append("## 📈 Aggregate Metrics")
        lines.append("")
        
        # Calculate averages
        p50_values = [m['latency_p50'] for m in all_metrics if 'latency_p50' in m]
        p95_values = [m['latency_p95'] for m in all_metrics if 'latency_p95' in m]
        p99_values = [m['latency_p99'] for m in all_metrics if 'latency_p99' in m]
        throughput_values = [m['throughput'] for m in all_metrics if 'throughput' in m]
        error_rates = [m['error_rate'] for m in all_metrics if 'error_rate' in m]
        
        if p50_values:
            lines.append("### Latency Summary")
            lines.append("")
            lines.append("| Percentile | Avg | Min | Max |")
            lines.append("|------------|-----|-----|-----|")
            lines.append(f"| P50 | {sum(p50_values)/len(p50_values):.0f}ms | {min(p50_values):.0f}ms | {max(p50_values):.0f}ms |")
            if p95_values:
                lines.append(f"| P95 | {sum(p95_values)/len(p95_values):.0f}ms | {min(p95_values):.0f}ms | {max(p95_values):.0f}ms |")
            if p99_values:
                lines.append(f"| P99 | {sum(p99_values)/len(p99_values):.0f}ms | {min(p99_values):.0f}ms | {max(p99_values):.0f}ms |")
            lines.append("")
        
        if throughput_values:
            lines.append("### Throughput Summary")
            lines.append("")
            lines.append(f"- **Average:** {sum(throughput_values)/len(throughput_values):.1f} req/s")
            lines.append(f"- **Min:** {min(throughput_values):.1f} req/s")
            lines.append(f"- **Max:** {max(throughput_values):.1f} req/s")
            lines.append("")
        
        if error_rates:
            avg_error = sum(error_rates) / len(error_rates)
            lines.append("### Error Rate Summary")
            lines.append("")
            lines.append(f"- **Average Error Rate:** {avg_error:.2f}%")
            lines.append(f"- **Max Error Rate:** {max(error_rates):.2f}%")
            lines.append("")
    
    # SLA compliance
    lines.append("## 🎯 SLA Compliance")
    lines.append("")
    lines.append("| SLA Target | Status |")
    lines.append("|------------|--------|")
    
    # Check SLAs based on collected metrics
    if all_metrics:
        p50_ok = all(m.get('latency_p50', 0) < 200 for m in all_metrics if 'latency_p50' in m)
        p95_ok = all(m.get('latency_p95', 0) < 500 for m in all_metrics if 'latency_p95' in m)
        p99_ok = all(m.get('latency_p99', 0) < 1000 for m in all_metrics if 'latency_p99' in m)
        error_ok = all(m.get('error_rate', 100) < 5 for m in all_metrics if 'error_rate' in m)
        
        lines.append(f"| P50 < 200ms | {'✅ PASS' if p50_ok else '❌ FAIL'} |")
        lines.append(f"| P95 < 500ms | {'✅ PASS' if p95_ok else '❌ FAIL'} |")
        lines.append(f"| P99 < 1000ms | {'✅ PASS' if p99_ok else '❌ FAIL'} |")
        lines.append(f"| Error Rate < 5% | {'✅ PASS' if error_ok else '❌ FAIL'} |")
    else:
        lines.append("| No metrics available | ⚠️ |")
    
    lines.append("")
    lines.append("---")
    lines.append(f"*Report generated by Load Metrics Report Generator*")
    
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
        sys.exit(1)
    
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.input_file}: {e}", file=sys.stderr)
        sys.exit(1)
    
    report = generate_markdown_report(data, args.output)
    
    if not args.output:
        print(report)


if __name__ == "__main__":
    main()

