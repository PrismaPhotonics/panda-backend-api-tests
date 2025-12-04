# Comprehensive Test Report Generator

## Overview

The `generate_comprehensive_test_report.py` script generates professional, detailed test reports from JUnit XML files with:

- ✅ Full test statistics and metrics
- 📊 Performance analysis (min/max/avg/median execution times)
- 🔄 Test flow breakdown
- 💡 Key insights and recommendations
- 📦 Suite-level and class-level metrics
- ❌ Detailed failure analysis
- 📎 Artifact listing

## Usage

### Basic Usage

```bash
# Generate markdown report (outputs to GitHub Actions summary or stdout)
python scripts/generate_comprehensive_test_report.py test-results/junit-smoke.xml
```

### With Custom Environment

```bash
python scripts/generate_comprehensive_test_report.py test-results/junit-smoke.xml \
  --environment production \
  --target https://10.10.10.100/focus-server
```

### Save to File

```bash
python scripts/generate_comprehensive_test_report.py test-results/junit-smoke.xml \
  --output reports/test-report.md
```

### Generate Both Markdown and JSON

```bash
python scripts/generate_comprehensive_test_report.py test-results/junit-smoke.xml \
  --output reports/test-report.md \
  --json reports/test-report.json
```

## Report Sections

The generated report includes:

1. **Test Details** - Environment, target, timestamp
2. **Overall Statistics** - Total tests, passed/failed/errors/skipped, duration, success rate
3. **Test Flow** - Step-by-step breakdown of the test lifecycle
4. **Key Insights** - Summary of test results with recommendations
5. **Performance Metrics** - Execution time statistics
6. **Test Suites Breakdown** - Per-suite metrics and sample test cases
7. **Failed Tests Details** - Detailed error messages and stack traces
8. **Class-Level Metrics** - Performance breakdown by test class
9. **Artifacts** - List of generated files

## Integration with GitHub Actions

The script automatically detects `GITHUB_STEP_SUMMARY` environment variable and writes to it if available. Otherwise, it outputs to stdout.

### Example Workflow Step

```yaml
- name: Generate Comprehensive Test Report
  if: always()
  shell: powershell
  env:
    ENVIRONMENT: ${{ secrets.ENVIRONMENT || 'staging' }}
    FOCUS_SERVER_HOST: ${{ secrets.FOCUS_SERVER_HOST }}
  run: |
    $target = "https://$env:FOCUS_SERVER_HOST/focus-server"
    py scripts/generate_comprehensive_test_report.py test-results/junit-smoke.xml `
      --environment $env:ENVIRONMENT `
      --target $target
```

## Output Examples

### Markdown Report

The markdown report is optimized for GitHub Actions summary display and includes:

- Professional formatting with emojis
- Tables for easy reading
- Code blocks for error messages
- Links to artifacts

### JSON Report

The JSON report provides programmatic access to all metrics:

```json
{
  "metadata": {
    "environment": "staging",
    "target": "https://10.10.10.100/focus-server",
    "generated_at": "2025-12-02T17:01:27",
    "xml_file": "test-results/junit-smoke.xml"
  },
  "summary": {
    "total": 42,
    "passed": 40,
    "failed": 1,
    "errors": 1,
    "skipped": 0,
    "duration": 112.5,
    "success_rate": 95.2
  },
  "performance": {
    "min_time": 0.123,
    "max_time": 5.678,
    "avg_time": 2.345,
    "median_time": 2.100,
    "total_time": 98.5,
    "std_dev": 1.234
  }
}
```

## Requirements

- Python 3.7+
- Standard library only (no external dependencies)

## Exit Codes

- `0` - All tests passed
- `1` - Tests failed or errors occurred

