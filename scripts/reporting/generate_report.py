"""
Test Report Generator - Comprehensive reporting system for Focus Server Automation

This script generates detailed HTML reports from pytest execution results,
including statistics, historical tracking, and a centralized dashboard.

Author: QA Automation Team
Date: 2025-10-29
"""

import json
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.reporting.report_processor import ReportProcessor
from scripts.reporting.report_template import ReportTemplate
from scripts.reporting.environment_cleanup import EnvironmentCleanup


class TestReportGenerator:
    """
    Professional test report generator with comprehensive features.
    
    Features:
    - HTML report generation with rich formatting
    - JSON data persistence for historical tracking
    - Dashboard creation with statistics
    - Integration with pytest execution
    - Xray test mapping integration
    """
    
    def __init__(
        self,
        output_dir: Optional[Path] = None,
        project_name: str = "Focus Server Automation"
    ):
        """
        Initialize the report generator.
        
        Args:
            output_dir: Directory to store reports (default: reports/)
            project_name: Name of the project for report headers
        """
        self.project_root = project_root
        self.project_name = project_name
        
        # Set up directories
        if output_dir is None:
            output_dir = project_root / "reports"
        
        self.reports_dir = Path(output_dir)
        self.runs_dir = self.reports_dir / "runs"
        self.dashboard_dir = self.reports_dir / "dashboard"
        self.json_dir = self.reports_dir / "json"
        
        # Create directories
        for directory in [self.reports_dir, self.runs_dir, self.dashboard_dir, self.json_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.processor = ReportProcessor(self.reports_dir)
        self.template = ReportTemplate()
        
        # Initialize cleanup (lazy - will use config from pytest run)
        self.cleanup = None
        
        # Current run metadata
        self.current_run_id = None
        self.current_run_dir = None
        
    def create_run_directory(self, run_name: Optional[str] = None) -> Path:
        """
        Create a timestamped directory for the current test run.
        
        Args:
            run_name: Optional name for the run (default: timestamp)
            
        Returns:
            Path to the run directory
        """
        if run_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            run_name = f"run_{timestamp}"
        
        run_dir = self.runs_dir / run_name
        run_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_run_id = run_name
        self.current_run_dir = run_dir
        
        return run_dir
    
    def run_pytest_with_reporting(
        self,
        test_paths: List[str],
        markers: Optional[List[str]] = None,
        parallel: bool = False,
        verbose: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run pytest and generate comprehensive reports.
        
        Args:
            test_paths: List of test paths to execute
            markers: Optional list of pytest markers
            parallel: Whether to run tests in parallel
            verbose: Enable verbose output
            **kwargs: Additional pytest options
            
        Returns:
            Dictionary with execution results and metadata
        """
        # Create run directory
        run_dir = self.create_run_directory()
        
        # Build pytest command
        pytest_cmd = self._build_pytest_command(
            test_paths=test_paths,
            markers=markers,
            parallel=parallel,
            verbose=verbose,
            run_dir=run_dir,
            **kwargs
        )
        
        # Execute pytest
        start_time = datetime.now()
        print(f"\n{'='*80}")
        print(f"Running pytest with comprehensive reporting...")
        print(f"Run ID: {self.current_run_id}")
        print(f"Output Directory: {run_dir}")
        print(f"{'='*80}\n")
        
        try:
            # Run pytest with real-time output streaming
            # Use Popen to stream output in real-time while still capturing it
            process = subprocess.Popen(
                pytest_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Merge stderr into stdout
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True,
                cwd=str(self.project_root)
            )
            
            # Stream output in real-time while collecting it
            stdout_lines = []
            print()  # Blank line before pytest output
            
            # Read and display output line by line
            for line in process.stdout:
                line = line.rstrip()
                if line:  # Only print non-empty lines
                    print(line)
                    stdout_lines.append(line)
            
            # Wait for process to complete
            process.wait()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Combine all output for parsing
            stdout_text = "\n".join(stdout_lines)
            
            # Extract results from pytest output
            results = self._parse_pytest_output(stdout_text, "")
            results.update({
                "run_id": self.current_run_id,
                "run_dir": str(run_dir),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "exit_code": process.returncode,
                "pytest_command": " ".join([sys.executable, "-m", "pytest"] + pytest_cmd[2:]),
                "stdout": stdout_text
            })
            
            # Generate reports
            self._generate_reports(results, run_dir)
            
            # Cleanup environment after tests
            self._cleanup_environment()
            
            return results
            
        except Exception as e:
            print(f"Error running pytest: {e}", file=sys.stderr)
            # Still try to cleanup even if tests failed
            try:
                self._cleanup_environment()
            except:
                pass
            raise
    
    def _build_pytest_command(
        self,
        test_paths: List[str],
        markers: Optional[List[str]],
        parallel: bool,
        verbose: bool,
        run_dir: Path,
        **kwargs
    ) -> List[str]:
        """Build pytest command with reporting options."""
        cmd = [sys.executable, "-m", "pytest"]
        
        # Add test paths
        cmd.extend(test_paths)
        
        # Add markers
        if markers:
            cmd.extend(["-m", " and ".join(markers)])
        
        # Parallel execution
        if parallel:
            cmd.extend(["-n", "auto"])
        
        # Verbose output
        if verbose:
            cmd.append("-v")
        
        # Enable real-time logging (shows logs during execution)
        cmd.extend([
            "-s",  # Show print statements
            "--log-cli-level=INFO",  # Show INFO level logs in console
            "--log-cli-format=%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
            "--log-cli-date-format=%Y-%m-%d %H:%M:%S"
        ])
        
        # Reporting options
        cmd.extend([
            "--html", str(run_dir / "pytest_report.html"),
            "--self-contained-html",
            "--junitxml", str(run_dir / "junit_results.xml"),
        ])
        
        # Add JSON report if pytest-json-report is available
        try:
            import pytest_jsonreport
            cmd.extend([
                "--json-report",
                "--json-report-file", str(run_dir / "pytest_results.json"),
            ])
        except ImportError:
            pass  # pytest-json-report not installed, skip
        
        # Additional options from kwargs
        for key, value in kwargs.items():
            if key.startswith("--"):
                cmd.append(key)
                if value is not None and value is not True:
                    cmd.append(str(value))
            elif value:
                cmd.append(f"--{key.replace('_', '-')}")
        
        return cmd
    
    def _parse_pytest_output(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """Parse pytest output to extract test results."""
        results = {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "total": 0,
            "warnings": [],
            "failures": []
        }
        
        lines = stdout.split("\n")
        for line in lines:
            # Parse summary line: "X passed, Y failed, Z skipped in N.NNs"
            if "passed" in line or "failed" in line:
                if "passed" in line:
                    try:
                        results["passed"] = int(line.split()[0])
                    except (ValueError, IndexError):
                        pass
                if "failed" in line:
                    try:
                        idx = line.split().index("failed")
                        results["failed"] = int(line.split()[idx - 1])
                    except (ValueError, IndexError):
                        pass
                if "skipped" in line:
                    try:
                        idx = line.split().index("skipped")
                        results["skipped"] = int(line.split()[idx - 1])
                    except (ValueError, IndexError):
                        pass
        
        results["total"] = results["passed"] + results["failed"] + results["skipped"] + results["errors"]
        results["pass_rate"] = (results["passed"] / results["total"] * 100) if results["total"] > 0 else 0
        
        return results
    
    def _generate_reports(self, results: Dict[str, Any], run_dir: Path):
        """Generate all report files for the current run."""
        print(f"\nGenerating reports for run {self.current_run_id}...")
        
        # Load JSON report if available
        json_report_path = run_dir / "pytest_results.json"
        if json_report_path.exists():
            with open(json_report_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            results["detailed_results"] = json_data
        
        # Generate enhanced HTML report
        html_content = self.template.generate_report_html(results, self.project_name)
        html_path = run_dir / "index.html"
        html_path.write_text(html_content, encoding="utf-8")
        print(f"  ✓ HTML report: {html_path}")
        
        # Save full stdout output to file for debugging
        stdout_path = run_dir / "test_output.log"
        stdout_path.write_text(results.get("stdout", ""), encoding="utf-8")
        print(f"  ✓ Test output log: {stdout_path}")
        
        # Save JSON metadata
        json_path = run_dir / "run_metadata.json"
        # Remove stdout from JSON (too large) but keep it in the log file
        json_results = {k: v for k, v in results.items() if k != "stdout"}
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_results, f, indent=2, ensure_ascii=False)
        print(f"  ✓ JSON metadata: {json_path}")
        
        # Save for historical tracking
        history_path = self.json_dir / f"{self.current_run_id}.json"
        shutil.copy(json_path, history_path)
        
        # Update dashboard
        self._update_dashboard(results)
        
        print(f"\nReport generation complete!")
        print(f"View report at: {html_path}")
    
    def _cleanup_environment(self):
        """Clean up environment after test execution."""
        print(f"\n{'='*80}")
        print(f"Starting environment cleanup...")
        print(f"{'='*80}\n")
        
        try:
            # Initialize cleanup if not already done
            if self.cleanup is None:
                from config.config_manager import ConfigManager
                config_manager = ConfigManager()
                self.cleanup = EnvironmentCleanup(config_manager)
            
            stats = self.cleanup.cleanup_all()
            
            print(f"\n{'='*80}")
            print(f"Environment cleanup completed")
            print(f"Jobs cancelled: {stats['jobs_cancelled']}")
            print(f"Jobs deleted: {stats['jobs_deleted']}")
            print(f"Services deleted: {stats['services_deleted']}")
            print(f"Pods deleted: {stats['pods_deleted']}")
            if stats['errors'] > 0:
                print(f"Errors: {stats['errors']} (some cleanup operations failed)")
            print(f"{'='*80}\n")
            
        except Exception as e:
            print(f"Warning: Environment cleanup failed: {e}", file=sys.stderr)
            print("You may need to manually clean up resources.\n")
    
    def _update_dashboard(self, results: Dict[str, Any]):
        """Update the central dashboard with latest run results."""
        # Load historical data
        history = self.processor.load_all_runs()
        
        # Add current run
        history.append({
            "run_id": self.current_run_id,
            "timestamp": results.get("start_time", datetime.now().isoformat()),
            "duration": results.get("duration_seconds", 0),
            "passed": results.get("passed", 0),
            "failed": results.get("failed", 0),
            "skipped": results.get("skipped", 0),
            "total": results.get("total", 0),
            "pass_rate": results.get("pass_rate", 0),
            "run_dir": str(self.current_run_dir.relative_to(self.reports_dir))
        })
        
        # Generate dashboard
        dashboard_html = self.template.generate_dashboard_html(
            history, 
            self.project_name,
            latest_run=results
        )
        
        dashboard_path = self.dashboard_dir / "index.html"
        dashboard_path.write_text(dashboard_html, encoding="utf-8")
        
        # Save dashboard data
        dashboard_data_path = self.dashboard_dir / "dashboard_data.json"
        with open(dashboard_data_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        
        print(f"  ✓ Dashboard updated: {dashboard_path}")
    
    def generate_report_from_files(
        self,
        json_file: Path,
        html_file: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Generate report from existing pytest JSON output.
        
        Useful for generating reports after pytest execution.
        
        Args:
            json_file: Path to pytest JSON results file
            html_file: Optional path to pytest HTML report
            
        Returns:
            Dictionary with processed results
        """
        json_file = Path(json_file)
        if not json_file.exists():
            raise FileNotFoundError(f"JSON file not found: {json_file}")
        
        # Create run directory
        run_dir = self.create_run_directory()
        
        # Copy files to run directory
        shutil.copy(json_file, run_dir / "pytest_results.json")
        if html_file and Path(html_file).exists():
            shutil.copy(html_file, run_dir / "pytest_report.html")
        
        # Load and process JSON
        with open(json_file, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        
        # Process results
        results = self.processor.process_json_report(json_data)
        results.update({
            "run_id": self.current_run_id,
            "run_dir": str(run_dir),
            "timestamp": datetime.now().isoformat()
        })
        
        # Generate reports
        self._generate_reports(results, run_dir)
        
        return results


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Generate comprehensive test reports for Focus Server Automation"
    )
    
    parser.add_argument(
        "test_paths",
        nargs="*",
        default=["tests/"],
        help="Test paths to execute (default: tests/)"
    )
    
    parser.add_argument(
        "--markers",
        "-m",
        nargs="+",
        help="Pytest markers to filter tests"
    )
    
    parser.add_argument(
        "--parallel",
        "-p",
        action="store_true",
        help="Run tests in parallel"
    )
    
    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        help="Output directory for reports (default: reports/)"
    )
    
    parser.add_argument(
        "--from-json",
        type=Path,
        help="Generate report from existing JSON file"
    )
    
    parser.add_argument(
        "--from-html",
        type=Path,
        help="Optional HTML report to include (used with --from-json)"
    )
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = TestReportGenerator(output_dir=args.output_dir)
    
    # Generate report
    if args.from_json:
        # Generate from existing files
        results = generator.generate_report_from_files(
            args.from_json,
            args.from_html
        )
    else:
        # Run pytest and generate
        results = generator.run_pytest_with_reporting(
            test_paths=args.test_paths,
            markers=args.markers,
            parallel=args.parallel
        )
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"Report Generation Summary")
    print(f"{'='*80}")
    print(f"Run ID: {results['run_id']}")
    print(f"Total Tests: {results.get('total', 0)}")
    print(f"Passed: {results.get('passed', 0)}")
    print(f"Failed: {results.get('failed', 0)}")
    print(f"Skipped: {results.get('skipped', 0)}")
    print(f"Pass Rate: {results.get('pass_rate', 0):.2f}%")
    print(f"Duration: {results.get('duration_seconds', 0):.2f} seconds")
    print(f"{'='*80}\n")
    
    # Exit with appropriate code
    sys.exit(0 if results.get("failed", 0) == 0 else 1)


if __name__ == "__main__":
    main()

