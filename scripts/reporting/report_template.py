"""
Report Template Generator - HTML templates for test reports

This module generates beautiful HTML reports and dashboards for test results.

Author: QA Automation Team
Date: 2025-10-29
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


class ReportTemplate:
    """
    Generate HTML templates for test reports and dashboards.
    
    Features:
    - Modern, responsive design
    - Interactive charts and graphs
    - Color-coded status indicators
    - Historical trend visualization
    """
    
    def generate_report_html(self, results: Dict[str, Any], project_name: str = "Test Automation") -> str:
        """
        Generate HTML report for a single test run.
        
        Args:
            results: Dictionary with test execution results
            project_name: Name of the project
            
        Returns:
            Complete HTML document as string
        """
        run_id = results.get("run_id", "unknown")
        timestamp = results.get("start_time", datetime.now().isoformat())
        passed = results.get("passed", 0)
        failed = results.get("failed", 0)
        skipped = results.get("skipped", 0)
        total = results.get("total", 0)
        pass_rate = results.get("pass_rate", 0)
        duration = results.get("duration_seconds", results.get("duration", 0))
        
        # Format timestamp
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            formatted_time = timestamp
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name} - Test Report - {run_id}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .header h1 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        
        .header .meta {{
            opacity: 0.9;
            font-size: 0.9em;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
        
        .stat-card h3 {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}
        
        .stat-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        
        .stat-card.passed .value {{ color: #28a745; }}
        .stat-card.failed .value {{ color: #dc3545; }}
        .stat-card.skipped .value {{ color: #ffc107; }}
        .stat-card.total .value {{ color: #007bff; }}
        .stat-card.rate .value {{ color: #17a2b8; }}
        .stat-card.duration .value {{ color: #6f42c1; }}
        
        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #e9ecef;
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            transition: width 0.3s ease;
        }}
        
        .section {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .section h2 {{
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        
        .test-list {{
            list-style: none;
        }}
        
        .test-item {{
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 4px solid #ddd;
        }}
        
        .test-item.passed {{
            background: #d4edda;
            border-left-color: #28a745;
        }}
        
        .test-item.failed {{
            background: #f8d7da;
            border-left-color: #dc3545;
        }}
        
        .test-item.skipped {{
            background: #fff3cd;
            border-left-color: #ffc107;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            margin-top: 40px;
        }}
        
        @media (max-width: 768px) {{
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{project_name}</h1>
            <p class="meta">Test Execution Report - {run_id}</p>
            <p class="meta">Executed: {formatted_time}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card total">
                <h3>Total Tests</h3>
                <div class="value">{total}</div>
            </div>
            <div class="stat-card passed">
                <h3>Passed</h3>
                <div class="value">{passed}</div>
            </div>
            <div class="stat-card failed">
                <h3>Failed</h3>
                <div class="value">{failed}</div>
            </div>
            <div class="stat-card skipped">
                <h3>Skipped</h3>
                <div class="value">{skipped}</div>
            </div>
            <div class="stat-card rate">
                <h3>Pass Rate</h3>
                <div class="value">{pass_rate:.1f}%</div>
            </div>
            <div class="stat-card duration">
                <h3>Duration</h3>
                <div class="value">{duration:.1f}s</div>
            </div>
        </div>
        
        <div class="section">
            <h2>Execution Summary</h2>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {pass_rate}%">
                    {pass_rate:.1f}%
                </div>
            </div>
        </div>
        
        {self._generate_failures_section(results)}
        {self._generate_test_details_section(results)}
        
        <div class="footer">
            <p>Generated by Focus Server Automation Framework</p>
            <p>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def _generate_failures_section(self, results: Dict[str, Any]) -> str:
        """Generate HTML section for failed tests."""
        failed_tests = results.get("failed_tests", [])
        
        if not failed_tests:
            return '<div class="section"><h2>Test Results</h2><p style="color: #28a745;">✓ All tests passed!</p></div>'
        
        html = '<div class="section"><h2>Failed Tests</h2><ul class="test-list">'
        for test in failed_tests[:20]:  # Limit to 20 for performance
            nodeid = test.get("nodeid", "Unknown")
            html += f'<li class="test-item failed">{nodeid}</li>'
        html += '</ul></div>'
        
        return html
    
    def _generate_test_details_section(self, results: Dict[str, Any]) -> str:
        """Generate HTML section with detailed test information."""
        tests = results.get("tests", [])
        
        if not tests:
            return ""
        
        html = '<div class="section"><h2>Test Details</h2><ul class="test-list">'
        for test in tests[:50]:  # Limit to 50
            status = test.get("status", "unknown")
            nodeid = test.get("nodeid", "Unknown")
            duration = test.get("duration", 0)
            
            html += f'''<li class="test-item {status}">
                <strong>{nodeid}</strong>
                <span style="float: right; color: #666;">{duration:.2f}s</span>
            </li>'''
        html += '</ul></div>'
        
        return html
    
    def generate_dashboard_html(
        self,
        history: List[Dict[str, Any]],
        project_name: str = "Test Automation",
        latest_run: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate dashboard HTML with historical data and trends.
        
        Args:
            history: List of historical test runs
            project_name: Name of the project
            latest_run: Optional latest run details
            
        Returns:
            Complete HTML dashboard document
        """
        # Calculate statistics
        total_runs = len(history)
        latest_run_data = latest_run or (history[0] if history else {})
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name} - Test Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .header h1 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .dashboard-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .dashboard-card h3 {{
            color: #666;
            margin-bottom: 15px;
            font-size: 0.9em;
            text-transform: uppercase;
        }}
        
        .dashboard-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .runs-table {{
            width: 100%;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .runs-table table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .runs-table th,
        .runs-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        
        .runs-table th {{
            background: #667eea;
            color: white;
            font-weight: 600;
        }}
        
        .runs-table tr:hover {{
            background: #f8f9fa;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        
        .status-badge.passed {{
            background: #d4edda;
            color: #155724;
        }}
        
        .status-badge.failed {{
            background: #f8d7da;
            color: #721c24;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{project_name} - Test Dashboard</h1>
            <p>Comprehensive test execution overview and historical analysis</p>
        </div>
        
        <div class="dashboard-grid">
            <div class="dashboard-card">
                <h3>Total Test Runs</h3>
                <div class="value">{total_runs}</div>
            </div>
            <div class="dashboard-card">
                <h3>Latest Pass Rate</h3>
                <div class="value">{latest_run_data.get('pass_rate', 0):.1f}%</div>
            </div>
            <div class="dashboard-card">
                <h3>Latest Duration</h3>
                <div class="value">{latest_run_data.get('duration_seconds', latest_run_data.get('duration', 0)):.1f}s</div>
            </div>
        </div>
        
        <div class="dashboard-card" style="margin-top: 20px;">
            <h3>Recent Test Runs</h3>
            <div class="runs-table">
                <table>
                    <thead>
                        <tr>
                            <th>Run ID</th>
                            <th>Timestamp</th>
                            <th>Total</th>
                            <th>Passed</th>
                            <th>Failed</th>
                            <th>Pass Rate</th>
                            <th>Duration</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # Add table rows for recent runs
        for run in history[:20]:  # Show last 20 runs
            run_id = run.get("run_id", "unknown")
            timestamp = run.get("timestamp", "")
            total = run.get("total", 0)
            passed = run.get("passed", 0)
            failed = run.get("failed", 0)
            pass_rate = run.get("pass_rate", 0)
            duration = run.get("duration", 0)
            
            # Format timestamp
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                formatted_time = dt.strftime("%Y-%m-%d %H:%M")
            except:
                formatted_time = timestamp[:16] if len(timestamp) > 16 else timestamp
            
            status_class = "passed" if failed == 0 else "failed"
            
            html += f"""
                        <tr>
                            <td><a href="runs/{run.get('run_dir', '')}/index.html">{run_id}</a></td>
                            <td>{formatted_time}</td>
                            <td>{total}</td>
                            <td>{passed}</td>
                            <td>{failed}</td>
                            <td><span class="status-badge {status_class}">{pass_rate:.1f}%</span></td>
                            <td>{duration:.1f}s</td>
                        </tr>
            """
        
        html += """
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="footer" style="text-align: center; padding: 20px; color: #666; margin-top: 40px;">
            <p>Generated by Focus Server Automation Framework</p>
            <p>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
    </div>
</body>
</html>"""
        
        return html

