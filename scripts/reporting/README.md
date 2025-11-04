# 📊 Test Reporting System

Comprehensive reporting system for Focus Server Automation Framework.

## 🎯 Features

- **HTML Report Generation** - Beautiful, self-contained HTML reports
- **Dashboard** - Centralized dashboard with historical analysis
- **Historical Tracking** - All test runs are stored and accessible
- **Statistics** - Pass rates, trends, and performance metrics
- **JSON Data Persistence** - Machine-readable data for integration

## 📁 Directory Structure

```
reports/
├── runs/                    # Individual test run directories
│   └── run_YYYYMMDD_HHMMSS/
│       ├── index.html      # Enhanced HTML report
│       ├── pytest_report.html  # Original pytest HTML
│       ├── pytest_results.json # JSON results
│       ├── junit_results.xml   # JUnit XML
│       └── run_metadata.json   # Run metadata
├── dashboard/
│   ├── index.html          # Main dashboard
│   └── dashboard_data.json # Dashboard data
└── json/                   # Historical JSON files
    └── run_*.json          # One JSON per run
```

## 🚀 Usage

### Basic Usage

Generate report from running pytest:

```bash
# Run tests with comprehensive reporting
python scripts/reporting/generate_report.py tests/

# With specific markers
python scripts/reporting/generate_report.py tests/ -m integration

# Parallel execution
python scripts/reporting/generate_report.py tests/ --parallel

# Custom output directory
python scripts/reporting/generate_report.py tests/ --output-dir custom_reports/
```

### From Existing Results

Generate report from existing pytest JSON output:

```bash
python scripts/reporting/generate_report.py \
    --from-json path/to/pytest_results.json \
    --from-html path/to/pytest_report.html
```

### Python API

```python
from scripts.reporting.generate_report import TestReportGenerator

# Initialize generator
generator = TestReportGenerator()

# Run pytest and generate reports
results = generator.run_pytest_with_reporting(
    test_paths=["tests/"],
    markers=["integration"],
    parallel=True
)

# Generate from existing files
results = generator.generate_report_from_files(
    json_file=Path("pytest_results.json"),
    html_file=Path("pytest_report.html")
)
```

## 📊 Dashboard

Access the dashboard at:
```
reports/dashboard/index.html
```

The dashboard shows:
- Total test runs
- Latest pass rate and duration
- Recent test runs table
- Links to individual run reports

## 📈 Report Features

### Individual Run Report

Each test run generates a comprehensive report with:
- **Summary Statistics** - Total, passed, failed, skipped, pass rate
- **Execution Details** - Duration, timestamp, command used
- **Failed Tests** - List of failed tests with details
- **Test Details** - Complete test list with status and duration

### Dashboard

The central dashboard provides:
- **Historical Overview** - All test runs in one place
- **Trend Analysis** - Pass rate trends over time
- **Quick Navigation** - Links to all individual reports
- **Statistics** - Aggregated metrics across all runs

## 🔧 Configuration

### pytest.ini Integration

The reporting system works seamlessly with pytest. Ensure you have:

```ini
[pytest]
addopts = 
    --html=reports/html-reports/test_report.html
    --self-contained-html
```

Or use the reporting system which handles this automatically.

## 📋 Requirements

Required packages (already in `requirements.txt`):
- `pytest-html>=4.1.1`
- `pytest-json-report>=1.5.0` (optional, for enhanced JSON reports)
- `jinja2>=3.1.2` (for template rendering)

Install with:
```bash
pip install -r requirements.txt
```

## 🎨 Customization

### Custom Report Template

Modify `report_template.py` to customize the HTML output:

```python
from scripts.reporting.report_template import ReportTemplate

template = ReportTemplate()
# Customize as needed
```

### Report Processing

Extend `report_processor.py` for custom data processing:

```python
from scripts.reporting.report_processor import ReportProcessor

processor = ReportProcessor(Path("reports/"))
# Add custom processing logic
```

## 🔗 Integration

### CI/CD Integration

The reporting system can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Tests with Reporting
  run: |
    python scripts/reporting/generate_report.py tests/
    # Upload reports as artifacts
```

### Xray Integration

Reports can be used alongside Xray test management:

```python
# Generate report and upload to Xray
generator = TestReportGenerator()
results = generator.run_pytest_with_reporting(["tests/"])
# Upload results to Xray via xray_upload.py
```

## 📝 Examples

### Daily Test Run

```bash
# Run all tests daily
python scripts/reporting/generate_report.py tests/ -m "not slow"
```

### Integration Tests Only

```bash
# Run integration tests with reporting
python scripts/reporting/generate_report.py tests/integration/ -m integration
```

### Performance Tests

```bash
# Run performance tests
python scripts/reporting/generate_report.py tests/performance/ --parallel
```

## 🐛 Troubleshooting

### Report Not Generated

- Ensure pytest-html is installed: `pip install pytest-html`
- Check that test execution completed successfully
- Verify output directory has write permissions

### Dashboard Not Showing Runs

- Ensure runs are stored in `reports/runs/`
- Check that `reports/json/` contains JSON files
- Verify JSON files have valid format

### Missing JSON Reports

If `pytest-json-report` is not installed, JSON reports won't be generated.
Install it: `pip install pytest-json-report`

The system will work without it but with reduced functionality.

## 📞 Support

For issues or questions:
- Check existing reports in `reports/`
- Review logs in `logs/test_runs/`
- Consult project documentation

---

**Author:** QA Automation Team  
**Version:** 1.0.0  
**Date:** 2025-10-29

