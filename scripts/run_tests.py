"""
Professional Test Runner
========================

Professional test runner for the Focus Server automation framework.
Provides comprehensive test execution with environment management, reporting, and CI/CD integration.
"""

import argparse
import subprocess
import os
import sys
import time
import logging
import requests
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from config.config_manager import ConfigManager
from src.core.exceptions import InfrastructureError, ConfigurationError


class TestRunner:
    """
    Professional test runner for the Focus Server automation framework.
    
    Provides comprehensive test execution capabilities including:
    - Environment validation and setup
    - Port forwarding for local access
    - Parallel test execution
    - Comprehensive reporting
    - CI/CD integration
    """
    
    def __init__(self, environment: str = "staging"):
        """
        Initialize the test runner.
        
        Args:
            environment: Target environment (staging, production, local)
        """
        self.environment = environment
        self.config_manager = ConfigManager(environment)
        self.logger = self._setup_logging()
        self.port_forward_process = None
        
        # Test execution settings
        self.parallel_workers = self.config_manager.get("focus_server.parallel_workers", 4)
        self.max_failures = self.config_manager.get("focus_server.max_failures", 5)
        self.retry_count = self.config_manager.get("focus_server.retry_count", 3)
        self.retry_delay = self.config_manager.get("focus_server.retry_delay", 5)
        
        # Timeout settings
        self.api_timeout = self.config_manager.get("focus_server.api_timeout", 60)
        self.infrastructure_timeout = self.config_manager.get("focus_server.infrastructure_timeout", 300)
        self.test_timeout = self.config_manager.get("focus_server.test_timeout", 1800)
        
        # Reporting settings
        self.generate_html_report = self.config_manager.get("focus_server.generate_html_report", True)
        self.generate_allure_report = self.config_manager.get("focus_server.generate_allure_report", True)
        self.generate_junit_report = self.config_manager.get("focus_server.generate_junit_report", True)
        
        self.logger.info(f"Test runner initialized for environment: {environment}")
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging for the test runner."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Create logs directory
        logs_dir = Path("reports/logs")
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Add file handler
        file_handler = logging.FileHandler(logs_dir / f"test_runner_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)8s] %(name)s: %(message)s'
        ))
        
        logger = logging.getLogger("test_runner")
        logger.addHandler(file_handler)
        
        return logger
    
    def _run_command(self, command: List[str], check_output: bool = False, 
                    suppress_errors: bool = False) -> Any:
        """
        Run a command and handle errors appropriately.
        
        Args:
            command: Command to execute
            check_output: Whether to capture output
            suppress_errors: Whether to suppress error output
            
        Returns:
            Command output or True if successful
            
        Raises:
            InfrastructureError: If command execution fails
        """
        self.logger.debug(f"Running command: {' '.join(command)}")
        
        try:
            if check_output:
                return subprocess.check_output(command, text=True, stderr=subprocess.PIPE).strip()
            else:
                subprocess.check_call(command, stderr=subprocess.PIPE)
                return True
                
        except subprocess.CalledProcessError as e:
            if not suppress_errors:
                self.logger.error(f"Command failed: {' '.join(command)}")
                self.logger.error(f"Exit code: {e.returncode}")
                self.logger.error(f"Stdout: {e.stdout}")
                self.logger.error(f"Stderr: {e.stderr}")
                raise InfrastructureError(f"Command failed: {e.cmd}") from e
            return False
            
        except FileNotFoundError:
            if not suppress_errors:
                self.logger.error(f"Command not found: {command[0]}")
                self.logger.error("Please ensure the required tools are installed and in your PATH")
                raise InfrastructureError(f"Executable not found: {command[0]}")
            return False
    
    def _check_prerequisites(self) -> bool:
        """
        Check that all prerequisites are available.
        
        Returns:
            True if all prerequisites are available
            
        Raises:
            InfrastructureError: If prerequisites are missing
        """
        self.logger.info("Checking prerequisites...")
        
        prerequisites = [
            ("kubectl", ["kubectl", "version", "--client"]),
            ("python", ["python", "--version"]),
            ("pip", ["pip", "--version"]),
        ]
        
        # Add SSH check if not production
        if not self.config_manager.is_production():
            prerequisites.append(("ssh", ["ssh", "-V"]))
        
        for name, command in prerequisites:
            try:
                self._run_command(command, suppress_errors=False)
                self.logger.info(f"✓ {name} is available")
            except InfrastructureError:
                self.logger.error(f"✗ {name} is not available")
                raise InfrastructureError(f"Prerequisite missing: {name}")
        
        self.logger.info("All prerequisites are available")
        return True
    
    def _install_dependencies(self) -> bool:
        """
        Install required dependencies.
        
        Returns:
            True if dependencies were installed successfully
        """
        self.logger.info("Installing dependencies...")
        
        try:
            # Install main requirements
            self._run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            self.logger.info("✓ Dependencies installed successfully")
            return True
            
        except InfrastructureError as e:
            self.logger.error(f"Failed to install dependencies: {e}")
            return False
    
    def _start_port_forward(self) -> Optional[subprocess.Popen]:
        """
        Start kubectl port-forward for local access to services.
        
        Returns:
            Port-forward process or None if not needed
        """
        if self.config_manager.is_production():
            self.logger.info("Skipping port-forward for production environment")
            return None
        
        k8s_config = self.config_manager.get_kubernetes_config()
        focus_server_config = self.config_manager.get_api_config()
        
        service_name = focus_server_config.get("port_forward", {}).get("service")
        namespace = k8s_config.get("namespace", "default")
        local_port = focus_server_config.get("port_forward", {}).get("local_port", 8500)
        remote_port = focus_server_config.get("port_forward", {}).get("remote_port", 5000)
        
        if not service_name:
            self.logger.warning("Port-forward service not configured, skipping")
            return None
        
        command = [
            "kubectl", "-n", namespace, "port-forward",
            f"svc/{service_name}", f"{local_port}:{remote_port}"
        ]
        
        self.logger.info(f"Starting port-forward for {service_name} to localhost:{local_port}...")
        
        try:
            # Start port-forward in background
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            # Wait a moment for port-forward to start
            time.sleep(5)
            
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                self.logger.error(f"Port-forward failed to start")
                self.logger.error(f"Stdout: {stdout.decode()}")
                self.logger.error(f"Stderr: {stderr.decode()}")
                raise InfrastructureError("Failed to start kubectl port-forward")
            
            # Verify API is reachable
            api_url = self.config_manager.get("focus_server.base_url")
            if self._verify_api_access(api_url):
                self.logger.info(f"✓ Port-forward started successfully (PID: {process.pid})")
                return process
            else:
                self.logger.error("API not reachable after port-forward")
                self._stop_port_forward(process)
                raise InfrastructureError("API not reachable after port-forward")
                
        except Exception as e:
            self.logger.error(f"Failed to start port-forward: {e}")
            raise InfrastructureError(f"Failed to start port-forward: {e}")
    
    def _verify_api_access(self, api_url: str, max_retries: int = 5) -> bool:
        """
        Verify that the API is accessible.
        
        Args:
            api_url: API URL to test
            max_retries: Maximum number of retry attempts
            
        Returns:
            True if API is accessible
        """
        self.logger.debug(f"Verifying API access: {api_url}")
        
        for attempt in range(max_retries):
            try:
                response = requests.get(f"{api_url}/channels", timeout=5)
                if response.status_code == 200:
                    self.logger.info(f"✓ API is accessible at {api_url}")
                    return True
                    
            except requests.exceptions.RequestException as e:
                self.logger.debug(f"API access attempt {attempt + 1} failed: {e}")
                
            time.sleep(2)
        
        self.logger.error(f"✗ API not accessible at {api_url} after {max_retries} attempts")
        return False
    
    def _stop_port_forward(self, process: Optional[subprocess.Popen]):
        """
        Stop the port-forward process.
        
        Args:
            process: Port-forward process to stop
        """
        if not process:
            return
        
        self.logger.info(f"Stopping port-forward process (PID: {process.pid})...")
        
        try:
            if os.name == 'nt':
                # Windows
                process.terminate()
            else:
                # Unix-like systems
                os.killpg(os.getpgid(process.pid), subprocess.signal.SIGTERM)
            
            process.wait(timeout=10)
            self.logger.info("✓ Port-forward stopped successfully")
            
        except subprocess.TimeoutExpired:
            self.logger.warning("Port-forward did not stop gracefully, forcing termination")
            try:
                if os.name == 'nt':
                    process.kill()
                else:
                    os.killpg(os.getpgid(process.pid), subprocess.signal.SIGKILL)
                process.wait(timeout=5)
                self.logger.info("✓ Port-forward killed successfully")
            except Exception as e:
                self.logger.error(f"Failed to kill port-forward process: {e}")
                
        except Exception as e:
            self.logger.error(f"Failed to stop port-forward process: {e}")
    
    def _build_pytest_command(self, test_paths: List[str], markers: List[str], 
                             parallel: bool = False, verbose: bool = False) -> List[str]:
        """
        Build the pytest command with all required options.
        
        Args:
            test_paths: List of test paths to run
            markers: List of pytest markers
            parallel: Whether to run tests in parallel
            verbose: Whether to enable verbose output
            
        Returns:
            List of command arguments
        """
        command = [sys.executable, "-m", "pytest"]
        
        # Add environment variable
        command.extend([f"--env={self.environment}"])
        
        # Add test paths
        if test_paths:
            command.extend(test_paths)
        
        # Add markers
        if markers:
            command.extend(["-m", " and ".join(markers)])
        
        # Add parallel execution
        if parallel:
            command.extend(["-n", str(self.parallel_workers)])
        
        # Add verbose output
        if verbose:
            command.append("-v")
        
        # Add timeout
        command.extend(["--timeout", str(self.test_timeout)])
        
        # Add retry options
        command.extend(["--maxfail", str(self.max_failures)])
        
        # Add reporting options
        if self.generate_html_report:
            html_dir = Path("reports/html-reports")
            html_dir.mkdir(parents=True, exist_ok=True)
            command.extend([
                "--html", str(html_dir / "test_report.html"),
                "--self-contained-html"
            ])
        
        if self.generate_junit_report:
            reports_dir = Path("reports")
            reports_dir.mkdir(parents=True, exist_ok=True)
            command.extend(["--junitxml", str(reports_dir / "junit-results.xml")])
        
        if self.generate_allure_report:
            allure_dir = Path("reports/allure-results")
            allure_dir.mkdir(parents=True, exist_ok=True)
            command.extend([
                "--alluredir", str(allure_dir),
                "--clean-alluredir"
            ])
        
        # Add logging options
        command.extend([
            "--log-cli-level=INFO",
            "--log-cli-format=%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
            "--log-cli-date-format=%Y-%m-%d %H:%M:%S"
        ])
        
        return command
    
    def _generate_allure_report(self) -> bool:
        """
        Generate Allure report from test results.
        
        Returns:
            True if report was generated successfully
        """
        if not self.generate_allure_report:
            return True
        
        self.logger.info("Generating Allure report...")
        
        try:
            allure_results_dir = Path("reports/allure-results")
            allure_report_dir = Path("reports/allure-html")
            
            if not allure_results_dir.exists():
                self.logger.warning("No Allure results found, skipping report generation")
                return True
            
            command = [
                "allure", "generate",
                str(allure_results_dir),
                "-o", str(allure_report_dir),
                "--clean"
            ]
            
            self._run_command(command)
            self.logger.info(f"✓ Allure report generated: {allure_report_dir}")
            return True
            
        except InfrastructureError as e:
            self.logger.error(f"Failed to generate Allure report: {e}")
            return False
    
    def run_tests(self, test_paths: List[str], markers: List[str], 
                  parallel: bool = False, verbose: bool = False, 
                  dry_run: bool = False) -> bool:
        """
        Run the test suite.
        
        Args:
            test_paths: List of test paths to run
            markers: List of pytest markers
            parallel: Whether to run tests in parallel
            verbose: Whether to enable verbose output
            dry_run: Whether to perform a dry run
            
        Returns:
            True if all tests passed
        """
        self.logger.info("=" * 80)
        self.logger.info("FOCUS SERVER AUTOMATION FRAMEWORK - TEST EXECUTION")
        self.logger.info("=" * 80)
        self.logger.info(f"Environment: {self.environment}")
        self.logger.info(f"Test paths: {test_paths or ['all']}")
        self.logger.info(f"Markers: {markers or ['all']}")
        self.logger.info(f"Parallel: {parallel}")
        self.logger.info(f"Verbose: {verbose}")
        self.logger.info(f"Dry run: {dry_run}")
        self.logger.info("=" * 80)
        
        try:
            # Step 1: Check prerequisites
            self._check_prerequisites()
            
            # Step 2: Install dependencies
            self._install_dependencies()
            
            # Step 3: Start port-forward (if needed)
            if not dry_run:
                self.port_forward_process = self._start_port_forward()
            
            # Step 4: Build and run pytest command
            pytest_command = self._build_pytest_command(test_paths, markers, parallel, verbose)
            
            if dry_run:
                self.logger.info("DRY RUN - Would execute:")
                self.logger.info(f"Command: {' '.join(pytest_command)}")
                return True
            
            self.logger.info(f"Executing: {' '.join(pytest_command)}")
            self._run_command(pytest_command)
            
            # Step 5: Generate Allure report
            self._generate_allure_report()
            
            self.logger.info("✓ All tests completed successfully")
            return True
            
        except InfrastructureError as e:
            self.logger.error(f"Test execution failed: {e}")
            return False
            
        except Exception as e:
            self.logger.error(f"Unexpected error during test execution: {e}")
            return False
            
        finally:
            # Cleanup
            if self.port_forward_process:
                self._stop_port_forward(self.port_forward_process)
            
            self.logger.info("Test execution finished")


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="Focus Server Automation Framework - Professional Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all integration tests on staging
  python scripts/run_tests.py --test-type integration --env staging
  
  # Run MongoDB outage tests with parallel execution
  python scripts/run_tests.py --test-type infrastructure --markers "mongodb_outage and resilience" --parallel
  
  # Run specific test file with verbose output
  python scripts/run_tests.py --test-paths tests/integration/infrastructure/test_mongodb_outage_resilience.py --verbose
  
  # Dry run to validate setup
  python scripts/run_tests.py --test-type integration --dry-run
        """
    )
    
    # Environment options
    parser.add_argument(
        "--env", "--environment",
        default="staging",
        choices=["staging", "production", "local"],
        help="Target environment (default: staging)"
    )
    
    # Test selection options
    parser.add_argument(
        "--test-type",
        default="all",
        choices=["all", "unit", "integration", "infrastructure", "api", "end_to_end"],
        help="Type of tests to run (default: all)"
    )
    
    parser.add_argument(
        "--test-paths",
        nargs="+",
        help="Specific test files or directories to run"
    )
    
    parser.add_argument(
        "--markers",
        nargs="+",
        help="Pytest markers to filter tests"
    )
    
    # Execution options
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without executing tests"
    )
    
    # Reporting options
    parser.add_argument(
        "--no-html-report",
        action="store_true",
        help="Disable HTML report generation"
    )
    
    parser.add_argument(
        "--no-allure-report",
        action="store_true",
        help="Disable Allure report generation"
    )
    
    parser.add_argument(
        "--no-junit-report",
        action="store_true",
        help="Disable JUnit report generation"
    )
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = TestRunner(environment=args.env)
    
    # Override reporting settings if requested
    if args.no_html_report:
        runner.generate_html_report = False
    if args.no_allure_report:
        runner.generate_allure_report = False
    if args.no_junit_report:
        runner.generate_junit_report = False
    
    # Determine test paths
    test_paths = args.test_paths
    if not test_paths:
        if args.test_type == "all":
            test_paths = ["tests/"]
        else:
            test_paths = [f"tests/{args.test_type}/"]
    
    # Determine markers
    markers = args.markers
    if not markers and args.test_type != "all":
        markers = [args.test_type]
    
    # Run tests
    success = runner.run_tests(
        test_paths=test_paths,
        markers=markers,
        parallel=args.parallel,
        verbose=args.verbose,
        dry_run=args.dry_run
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()