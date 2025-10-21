# 🔗 Xray Integration Implementation Guide

**Date:** 2025-10-19  
**Purpose:** Complete integration between pytest automation and Jira Xray

---

## 📋 **Phase 3: Xray Integration Architecture**

### **1. Installation & Setup**

#### **Required Packages:**
```bash
pip install pytest-xray-server
pip install pytest-json-report
pip install requests
pip install python-dateutil
```

#### **Configuration Files:**

##### **pytest.ini additions:**
```ini
[pytest]
# Existing configuration...

# Xray Integration
addopts = 
    --json-report
    --json-report-file=reports/xray/test_results.json
    --json-report-indent=2
    --jira-xray
    
# Xray markers
markers =
    xray: Mark test for Xray reporting
    xray_test_key: Associate test with Xray test key
    xray_test_plan: Associate test with test plan
    xray_test_execution: Associate test with test execution
```

---

### **2. Xray Test Decorator Implementation**

Create `src/utils/xray_integration.py`:

```python
"""
Xray Integration Utilities for Focus Server Automation
"""
import os
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import pytest
from functools import wraps


class XrayClient:
    """Client for Jira Xray API integration"""
    
    def __init__(self):
        self.base_url = os.getenv('XRAY_BASE_URL', 'https://jira.company.com')
        self.username = os.getenv('XRAY_USERNAME')
        self.password = os.getenv('XRAY_PASSWORD')
        self.api_token = os.getenv('XRAY_API_TOKEN')
        self.project_key = 'PZ'
        self.session = requests.Session()
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Jira/Xray"""
        if self.api_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            })
        else:
            self.session.auth = (self.username, self.password)
    
    def create_test_execution(self, summary: str, test_plan_key: Optional[str] = None) -> str:
        """Create a new test execution in Xray"""
        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": f"Automated Test Execution - {summary}",
                "description": f"Automated execution from pytest on {datetime.now()}",
                "issuetype": {"name": "Test Execution"},
                "customfield_10100": test_plan_key if test_plan_key else None  # Test Plan link
            }
        }
        
        response = self.session.post(
            f"{self.base_url}/rest/api/2/issue",
            json=payload
        )
        response.raise_for_status()
        return response.json()['key']
    
    def import_test_results(self, test_execution_key: str, results: Dict[str, Any]):
        """Import test results to Xray"""
        payload = {
            "testExecutionKey": test_execution_key,
            "info": {
                "startDate": results.get('start_time'),
                "finishDate": results.get('end_time'),
                "testEnvironment": os.getenv('TEST_ENV', 'staging')
            },
            "tests": self._format_test_results(results.get('tests', []))
        }
        
        response = self.session.post(
            f"{self.base_url}/rest/raven/2.0/import/execution",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def _format_test_results(self, tests: List[Dict]) -> List[Dict]:
        """Format pytest results for Xray"""
        formatted = []
        for test in tests:
            formatted.append({
                "testKey": test.get('xray_key'),
                "status": self._map_status(test.get('outcome')),
                "start": test.get('start'),
                "finish": test.get('stop'),
                "comment": test.get('message', ''),
                "evidences": self._collect_evidences(test)
            })
        return formatted
    
    def _map_status(self, pytest_status: str) -> str:
        """Map pytest status to Xray status"""
        mapping = {
            'passed': 'PASSED',
            'failed': 'FAILED',
            'skipped': 'SKIPPED',
            'xfailed': 'FAILED',
            'xpassed': 'PASSED'
        }
        return mapping.get(pytest_status, 'TODO')
    
    def _collect_evidences(self, test: Dict) -> List[Dict]:
        """Collect test evidences (screenshots, logs, etc.)"""
        evidences = []
        
        # Add log file if exists
        log_file = test.get('log_file')
        if log_file and os.path.exists(log_file):
            with open(log_file, 'rb') as f:
                evidences.append({
                    "data": f.read().decode('utf-8'),
                    "filename": os.path.basename(log_file),
                    "contentType": "text/plain"
                })
        
        # Add screenshot if exists
        screenshot = test.get('screenshot')
        if screenshot and os.path.exists(screenshot):
            with open(screenshot, 'rb') as f:
                import base64
                evidences.append({
                    "data": base64.b64encode(f.read()).decode('utf-8'),
                    "filename": os.path.basename(screenshot),
                    "contentType": "image/png"
                })
        
        return evidences


def xray_test(test_key: str, test_plan: Optional[str] = None):
    """
    Decorator to mark tests for Xray reporting
    
    Usage:
        @xray_test("PZ-13547")
        def test_live_configure():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Add Xray metadata to test
            func.xray_key = test_key
            func.xray_test_plan = test_plan
            
            # Mark test for pytest
            pytest.mark.xray(func)
            pytest.mark.xray_test_key(test_key)(func)
            if test_plan:
                pytest.mark.xray_test_plan(test_plan)(func)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


class XrayReporter:
    """Custom pytest plugin for Xray reporting"""
    
    def __init__(self):
        self.client = XrayClient()
        self.test_results = []
        self.test_execution_key = None
        self.start_time = None
        self.end_time = None
    
    def pytest_sessionstart(self, session):
        """Called when test session starts"""
        self.start_time = datetime.now().isoformat()
        
        # Create test execution in Jira
        test_plan = session.config.getoption("--test-plan", None)
        execution_summary = session.config.getoption("--execution-summary", 
                                                     f"Pytest Run {datetime.now()}")
        
        self.test_execution_key = self.client.create_test_execution(
            summary=execution_summary,
            test_plan_key=test_plan
        )
        print(f"Created Test Execution: {self.test_execution_key}")
    
    def pytest_runtest_logreport(self, report):
        """Called for each test report"""
        if report.when == 'call':
            test_result = {
                'nodeid': report.nodeid,
                'outcome': report.outcome,
                'duration': report.duration,
                'message': str(report.longrepr) if report.failed else '',
                'xray_key': getattr(report, 'xray_key', None),
                'start': datetime.now().isoformat(),
                'stop': datetime.now().isoformat()
            }
            
            # Capture logs
            if hasattr(report, 'caplog'):
                test_result['logs'] = report.caplog
            
            # Capture stdout
            if hasattr(report, 'capstdout'):
                test_result['stdout'] = report.capstdout
            
            self.test_results.append(test_result)
    
    def pytest_sessionfinish(self, session, exitstatus):
        """Called when test session finishes"""
        self.end_time = datetime.now().isoformat()
        
        # Upload results to Xray
        if self.test_execution_key and self.test_results:
            results = {
                'start_time': self.start_time,
                'end_time': self.end_time,
                'tests': self.test_results
            }
            
            try:
                self.client.import_test_results(self.test_execution_key, results)
                print(f"Results uploaded to Xray: {self.test_execution_key}")
            except Exception as e:
                print(f"Failed to upload results to Xray: {e}")


# Register the plugin
def pytest_configure(config):
    """Register Xray plugin"""
    if config.getoption("--jira-xray", False):
        config.pluginmanager.register(XrayReporter(), 'xray_reporter')


def pytest_addoption(parser):
    """Add Xray command line options"""
    group = parser.getgroup('xray')
    group.addoption(
        '--jira-xray',
        action='store_true',
        default=False,
        help='Enable Jira Xray reporting'
    )
    group.addoption(
        '--test-plan',
        action='store',
        default=None,
        help='Jira test plan key'
    )
    group.addoption(
        '--execution-summary',
        action='store',
        default=None,
        help='Test execution summary'
    )
```

---

### **3. Update Test Files with Xray Markers**

Example test file update:

```python
"""
Test Configure Endpoints with Xray Integration
"""
import pytest
from src.utils.xray_integration import xray_test


class TestConfigureEndpoints:
    
    @xray_test("PZ-13547", test_plan="PZ-PLAN-001")
    def test_configure_live_happy_path(self, focus_server_api):
        """Test live configure with valid payload"""
        payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 1, "max": 3},
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": None,
            "end_time": None,
            "view_type": 0
        }
        
        response = focus_server_api.configure(payload)
        
        assert response.status_code == 200
        assert response.json()['job_id'] is not None
        assert response.json()['stream_port'] > 0
    
    @xray_test("PZ-13548")
    def test_configure_historical_happy_path(self, focus_server_api):
        """Test historical configure with valid time range"""
        # Test implementation...
        pass
    
    @xray_test("PZ-13552")
    @pytest.mark.parametrize("start,end", [
        (1700000600, 1700000000),  # start > end
        (1700000000, 1700000000),  # start == end
    ])
    def test_configure_invalid_time_range(self, focus_server_api, start, end):
        """Test configure with invalid time ranges"""
        # Test implementation...
        pass
```

---

### **4. GitHub Actions Integration**

Create `.github/workflows/xray-test-execution.yml`:

```yaml
name: Xray Test Execution

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:
    inputs:
      test_plan:
        description: 'Jira Test Plan Key'
        required: false
      environment:
        description: 'Test Environment'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production
          - development

jobs:
  test-and-report:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests with Xray reporting
      env:
        XRAY_BASE_URL: ${{ secrets.XRAY_BASE_URL }}
        XRAY_API_TOKEN: ${{ secrets.XRAY_API_TOKEN }}
        TEST_ENV: ${{ github.event.inputs.environment || 'staging' }}
        FOCUS_BASE_URL: ${{ secrets.FOCUS_BASE_URL }}
        MONGODB_URI: ${{ secrets.MONGODB_URI }}
        RABBITMQ_HOST: ${{ secrets.RABBITMQ_HOST }}
      run: |
        pytest \
          --jira-xray \
          --test-plan="${{ github.event.inputs.test_plan }}" \
          --execution-summary="GitHub Actions - ${{ github.run_number }}" \
          --json-report \
          --json-report-file=reports/test_results.json \
          -v
    
    - name: Upload test results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: test-results
        path: reports/
    
    - name: Publish test results to Xray
      if: always()
      run: |
        python scripts/publish_to_xray.py \
          --results reports/test_results.json \
          --execution-key ${{ env.TEST_EXECUTION_KEY }}
```

---

### **5. Local Run Script with Xray**

Create `run_tests_with_xray.ps1`:

```powershell
# Run Tests with Xray Reporting
param(
    [string]$TestPlan = "",
    [string]$Environment = "staging",
    [string]$TestPath = "tests/",
    [string]$Markers = ""
)

Write-Host "=== Running Tests with Xray Reporting ===" -ForegroundColor Cyan
Write-Host ""

# Load environment variables
. .\set_production_env.ps1

# Set Xray credentials
$env:XRAY_BASE_URL = "https://jira.company.com"
$env:XRAY_USERNAME = Read-Host "Enter Jira username"
$env:XRAY_PASSWORD = Read-Host "Enter Jira password" -AsSecureString
$env:TEST_ENV = $Environment

# Build pytest command
$pytestCmd = "pytest"
$pytestArgs = @(
    "--jira-xray",
    "--json-report",
    "--json-report-file=reports/xray/test_results.json",
    "-v",
    "--tb=short"
)

if ($TestPlan) {
    $pytestArgs += "--test-plan=$TestPlan"
}

if ($Markers) {
    $pytestArgs += "-m $Markers"
}

$pytestArgs += $TestPath

# Run tests
Write-Host "Executing: $pytestCmd $($pytestArgs -join ' ')" -ForegroundColor Yellow
& python -m pytest $pytestArgs

# Check results
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ All tests passed!" -ForegroundColor Green
} else {
    Write-Host "`n❌ Some tests failed. Check Xray for details." -ForegroundColor Red
}

Write-Host "`nTest results uploaded to Xray" -ForegroundColor Cyan
```

---

### **6. Xray Results Parser**

Create `scripts/xray_results_parser.py`:

```python
"""
Parse and format test results for Xray
"""
import json
import argparse
from typing import Dict, List
from datetime import datetime


class XrayResultsParser:
    
    def __init__(self, json_report_path: str):
        with open(json_report_path, 'r') as f:
            self.report = json.load(f)
    
    def generate_xray_json(self) -> Dict:
        """Generate Xray-compatible JSON"""
        return {
            "testExecutionKey": self.report.get('test_execution_key'),
            "info": {
                "summary": f"Automated Test Run - {datetime.now()}",
                "startDate": self.report['created'],
                "finishDate": datetime.now().isoformat(),
                "testEnvironment": self.report.get('environment', 'staging')
            },
            "tests": self._parse_tests()
        }
    
    def _parse_tests(self) -> List[Dict]:
        """Parse individual test results"""
        tests = []
        
        for test in self.report.get('tests', []):
            xray_key = self._extract_xray_key(test)
            if xray_key:
                tests.append({
                    "testKey": xray_key,
                    "status": self._map_outcome(test['outcome']),
                    "start": test.get('setup', {}).get('start'),
                    "finish": test.get('teardown', {}).get('stop'),
                    "comment": self._format_comment(test),
                    "evidences": self._collect_evidences(test),
                    "defects": self._extract_defects(test)
                })
        
        return tests
    
    def _extract_xray_key(self, test: Dict) -> str:
        """Extract Xray test key from test metadata"""
        # Look in markers
        for marker in test.get('markers', []):
            if marker.startswith('xray_test_key'):
                return marker.split('(')[1].strip(')')
        
        # Look in test name
        if 'PZ-' in test['nodeid']:
            import re
            match = re.search(r'PZ-\d+', test['nodeid'])
            if match:
                return match.group()
        
        return None
    
    def _map_outcome(self, outcome: str) -> str:
        """Map pytest outcome to Xray status"""
        mapping = {
            'passed': 'PASSED',
            'failed': 'FAILED',
            'skipped': 'BLOCKED',
            'error': 'FAILED'
        }
        return mapping.get(outcome, 'TODO')
    
    def _format_comment(self, test: Dict) -> str:
        """Format test comment with failure details"""
        if test['outcome'] == 'failed':
            return f"Test failed:\n{test.get('call', {}).get('longrepr', 'No details')}"
        return f"Test {test['outcome']}"
    
    def _collect_evidences(self, test: Dict) -> List[Dict]:
        """Collect test evidences"""
        evidences = []
        
        # Add stdout/stderr
        if test.get('call', {}).get('stdout'):
            evidences.append({
                "data": test['call']['stdout'],
                "filename": "stdout.txt",
                "contentType": "text/plain"
            })
        
        return evidences
    
    def _extract_defects(self, test: Dict) -> List[str]:
        """Extract defect links from failed tests"""
        defects = []
        
        if test['outcome'] == 'failed':
            # Look for bug patterns in failure message
            import re
            message = str(test.get('call', {}).get('longrepr', ''))
            bugs = re.findall(r'BUG-\d+', message)
            defects.extend(bugs)
        
        return defects
    
    def generate_html_report(self) -> str:
        """Generate HTML report"""
        html = f"""
        <html>
        <head>
            <title>Test Execution Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .passed {{ color: green; }}
                .failed {{ color: red; }}
                .skipped {{ color: orange; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Test Execution Report</h1>
            <p>Environment: {self.report.get('environment', 'Unknown')}</p>
            <p>Duration: {self.report.get('duration', 0):.2f}s</p>
            
            <h2>Summary</h2>
            <ul>
                <li>Total: {len(self.report['tests'])}</li>
                <li class="passed">Passed: {self._count_by_outcome('passed')}</li>
                <li class="failed">Failed: {self._count_by_outcome('failed')}</li>
                <li class="skipped">Skipped: {self._count_by_outcome('skipped')}</li>
            </ul>
            
            <h2>Test Results</h2>
            <table>
                <tr>
                    <th>Test</th>
                    <th>Status</th>
                    <th>Duration</th>
                    <th>Message</th>
                </tr>
                {self._generate_test_rows()}
            </table>
        </body>
        </html>
        """
        return html
    
    def _count_by_outcome(self, outcome: str) -> int:
        """Count tests by outcome"""
        return len([t for t in self.report['tests'] if t['outcome'] == outcome])
    
    def _generate_test_rows(self) -> str:
        """Generate HTML table rows for tests"""
        rows = []
        for test in self.report['tests']:
            rows.append(f"""
                <tr>
                    <td>{test['nodeid']}</td>
                    <td class="{test['outcome']}">{test['outcome'].upper()}</td>
                    <td>{test.get('duration', 0):.3f}s</td>
                    <td>{test.get('call', {}).get('longrepr', '')}</td>
                </tr>
            """)
        return '\n'.join(rows)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse test results for Xray')
    parser.add_argument('--json-report', required=True, help='Path to JSON report')
    parser.add_argument('--output-format', choices=['xray', 'html'], default='xray')
    parser.add_argument('--output-file', help='Output file path')
    
    args = parser.parse_args()
    
    parser = XrayResultsParser(args.json_report)
    
    if args.output_format == 'xray':
        output = json.dumps(parser.generate_xray_json(), indent=2)
    else:
        output = parser.generate_html_report()
    
    if args.output_file:
        with open(args.output_file, 'w') as f:
            f.write(output)
    else:
        print(output)
```

---

## 📊 **Phase 4: Test Execution Scheduling**

### **1. GitHub Actions Scheduled Runs**

Already included in the workflow above with cron schedule.

### **2. Local Scheduled Runs (Windows Task Scheduler)**

Create `schedule_tests.ps1`:

```powershell
# Create scheduled task for test execution
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-ExecutionPolicy Bypass -File C:\Projects\focus_server_automation\run_tests_with_xray.ps1 -Environment production"

$trigger = @(
    New-ScheduledTaskTrigger -Daily -At 2:00AM
    New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Wednesday,Friday -At 10:00AM
)

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

Register-ScheduledTask `
    -TaskName "FocusServerAutomatedTests" `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Automated test execution for Focus Server with Xray reporting"

Write-Host "Scheduled task created successfully" -ForegroundColor Green
```

### **3. Jenkins Pipeline (Alternative)**

Create `Jenkinsfile`:

```groovy
pipeline {
    agent any
    
    triggers {
        cron('H 2 * * *')  // Daily at 2 AM
        pollSCM('H/15 * * * *')  // Check for changes every 15 min
    }
    
    parameters {
        choice(name: 'ENVIRONMENT', 
               choices: ['staging', 'production', 'development'],
               description: 'Test environment')
        string(name: 'TEST_PLAN',
               defaultValue: '',
               description: 'Jira Test Plan Key')
    }
    
    stages {
        stage('Setup') {
            steps {
                checkout scm
                sh 'python -m pip install -r requirements.txt'
            }
        }
        
        stage('Run Tests') {
            steps {
                withCredentials([
                    string(credentialsId: 'xray-api-token', variable: 'XRAY_API_TOKEN'),
                    string(credentialsId: 'mongodb-uri', variable: 'MONGODB_URI')
                ]) {
                    sh """
                        pytest \
                            --jira-xray \
                            --test-plan=${params.TEST_PLAN} \
                            --execution-summary="Jenkins Build #${BUILD_NUMBER}" \
                            --json-report \
                            -v
                    """
                }
            }
        }
        
        stage('Publish Results') {
            steps {
                junit 'reports/junit.xml'
                archiveArtifacts artifacts: 'reports/**/*'
                
                publishHTML([
                    reportDir: 'reports',
                    reportFiles: 'index.html',
                    reportName: 'Test Report'
                ])
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        failure {
            emailext(
                subject: "Test Execution Failed: ${BUILD_NUMBER}",
                body: "Test execution failed. Check Xray for details.",
                to: 'team@company.com'
            )
        }
    }
}
```

---

## 🎯 **Implementation Checklist**

### **Week 1:**
- [ ] Install required packages
- [ ] Create XrayClient class
- [ ] Implement test decorators
- [ ] Update pytest.ini

### **Week 2:**
- [ ] Add Xray markers to existing tests
- [ ] Create missing test implementations (Critical priority)
- [ ] Test local Xray integration

### **Week 3:**
- [ ] Setup GitHub Actions workflow
- [ ] Configure secrets in GitHub
- [ ] Implement scheduled runs
- [ ] Create Jenkins pipeline (if applicable)

### **Week 4:**
- [ ] Full integration testing
- [ ] Documentation
- [ ] Team training
- [ ] Go-live

---

## 📈 **Expected Benefits**

1. **Real-time test visibility** in Jira
2. **Automated test execution reports**
3. **Traceability** between requirements and tests
4. **Historical test trends**
5. **Defect correlation**
6. **Team dashboards**
7. **Compliance reporting**

---

## 🔧 **Environment Variables Required**

```bash
# Xray Configuration
XRAY_BASE_URL=https://jira.company.com
XRAY_API_TOKEN=your_api_token
XRAY_USERNAME=your_username
XRAY_PASSWORD=your_password

# Test Environment
TEST_ENV=staging
FOCUS_BASE_URL=https://10.10.100.100
MONGODB_URI=mongodb://prisma:prisma@10.10.100.108:27017
RABBITMQ_HOST=10.10.100.107
```

---

## 📊 **Success Metrics**

- 100% test-to-requirement traceability
- < 5 minute test result publication
- 95% automated test coverage
- Daily execution reports
- Zero manual reporting effort
