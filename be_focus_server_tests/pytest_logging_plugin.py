"""
Pytest Logging Plugin
=====================

Automatically saves test logs to timestamped files in the logs directory.

Features:
- Timestamped log files (YYYY-MM-DD_HH-MM-SS)
- Test type/marker in filename
- Separate error and warning log files
- Automatic archiving of old logs
- Separate logs per test session
"""

import pytest
import logging
import os
from datetime import datetime
from pathlib import Path


class TestLoggerPlugin:
    """Plugin to manage test logging to files."""
    
    def __init__(self, config):
        self.config = config
        self.log_dir = Path("logs/test_runs")
        self.errors_dir = Path("logs/errors")
        self.warnings_dir = Path("logs/warnings")
        self.archive_dir = Path("logs/archive")
        
        # Log files
        self.log_file = None
        self.error_log_file = None
        self.warning_log_file = None
        
        # Handlers
        self.file_handler = None
        self.error_handler = None
        self.warning_handler = None
        
        # Ensure directories exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.errors_dir.mkdir(parents=True, exist_ok=True)
        self.warnings_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    @pytest.hookimpl(tryfirst=True)
    def pytest_configure(self, config):
        """Configure logging at the start of test session."""
        # Get test markers/types from command line
        test_type = self._get_test_type(config)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Generate log filenames
        log_filename = f"{timestamp}_{test_type}.log"
        error_filename = f"{timestamp}_{test_type}_ERRORS.log"
        warning_filename = f"{timestamp}_{test_type}_WARNINGS.log"
        
        self.log_file = self.log_dir / log_filename
        self.error_log_file = self.errors_dir / error_filename
        self.warning_log_file = self.warnings_dir / warning_filename
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 1. Main log file handler (all levels)
        self.file_handler = logging.FileHandler(
            self.log_file,
            mode='w',
            encoding='utf-8'
        )
        self.file_handler.setFormatter(formatter)
        self.file_handler.setLevel(logging.DEBUG)
        
        # 2. Error log file handler (ERROR and CRITICAL only)
        self.error_handler = logging.FileHandler(
            self.error_log_file,
            mode='w',
            encoding='utf-8'
        )
        self.error_handler.setFormatter(formatter)
        self.error_handler.setLevel(logging.ERROR)
        
        # 3. Warning log file handler (WARNING and above)
        self.warning_handler = logging.FileHandler(
            self.warning_log_file,
            mode='w',
            encoding='utf-8'
        )
        self.warning_handler.setFormatter(formatter)
        self.warning_handler.setLevel(logging.WARNING)
        
        # Add all handlers to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(self.file_handler)
        root_logger.addHandler(self.error_handler)
        root_logger.addHandler(self.warning_handler)
        
        # Log session start
        logging.info("=" * 80)
        logging.info(f"TEST SESSION STARTED: {test_type}")
        logging.info(f"Main log file: {self.log_file}")
        logging.info(f"Error log file: {self.error_log_file}")
        logging.info(f"Warning log file: {self.warning_log_file}")
        logging.info(f"Environment: {config.getoption('--env', 'staging')}")
        logging.info("=" * 80)
    
    @pytest.hookimpl(trylast=True)
    def pytest_unconfigure(self, config):
        """Clean up logging at the end of test session."""
        if self.file_handler:
            # Log session end
            logging.info("=" * 80)
            logging.info("TEST SESSION COMPLETED")
            logging.info(f"Main log: {self.log_file}")
            logging.info(f"Error log: {self.error_log_file}")
            logging.info(f"Warning log: {self.warning_log_file}")
            logging.info("=" * 80)
            
            # Remove all handlers
            root_logger = logging.getLogger()
            
            if self.file_handler:
                root_logger.removeHandler(self.file_handler)
                self.file_handler.close()
            
            if self.error_handler:
                root_logger.removeHandler(self.error_handler)
                self.error_handler.close()
            
            if self.warning_handler:
                root_logger.removeHandler(self.warning_handler)
                self.warning_handler.close()
            
            # Print log locations to console (ASCII-safe for Windows)
            try:
                print(f"\n✅ Test logs saved:")
                print(f"   📝 All logs: {self.log_file}")
                print(f"   ⚠️  Warnings: {self.warning_log_file}")
                print(f"   ❌ Errors: {self.error_log_file}")
            except UnicodeEncodeError:
                print(f"\n[OK] Test logs saved:")
                print(f"   [ALL] {self.log_file}")
                print(f"   [WARN] {self.warning_log_file}")
                print(f"   [ERROR] {self.error_log_file}")
    
    def _get_test_type(self, config):
        """Determine test type from command line options."""
        # Check for markers
        markers = config.getoption("-m", None)
        if markers:
            return f"marker_{markers.replace(' ', '_')}"
        
        # Check for specific test file/directory
        args = config.args
        if args:
            # Extract test type from path
            for arg in args:
                if "integration" in arg:
                    return "integration_tests"
                elif "unit" in arg:
                    return "unit_tests"
                elif "infrastructure" in arg:
                    return "infrastructure_tests"
                elif "api" in arg:
                    return "api_tests"
                elif "performance" in arg:
                    return "performance_tests"
        
        # Default
        return "all_tests"
    
    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_logreport(self, report):
        """Log test results."""
        if report.when == "call":
            # Log test result with outcome marker
            outcome_marker = {
                "passed": "[PASS]",
                "failed": "[FAIL]",
                "skipped": "[SKIP]"
            }
            marker = outcome_marker.get(report.outcome, "[????]")
            
            logging.info(
                f"{marker} {report.nodeid} - {report.outcome.upper()}"
            )


def pytest_configure(config):
    """Register the plugin."""
    if not config.getoption("--dry-run", False):
        plugin = TestLoggerPlugin(config)
        config.pluginmanager.register(plugin, "test_logger_plugin")

