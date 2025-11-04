"""
Real-time Pod Log Monitor for Test Execution
=============================================

Monitors Kubernetes pod logs in real-time during test execution and associates
logs with specific tests.

Features:
- Real-time log streaming from multiple pods
- Automatic association of logs with running tests
- Error detection and highlighting
- Test-specific log files
- Concurrent monitoring of multiple services
"""

import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
from queue import Queue, Empty
import paramiko


class PodLogMonitor:
    """
    Real-time pod log monitor that captures logs during test execution.
    
    Monitors specified pods and associates their logs with the currently
    running test.
    """
    
    def __init__(
        self,
        ssh_host: str,
        ssh_user: str,
        ssh_password: str,
        namespace: str = "panda",
        log_dir: str = "logs/pod_logs"
    ):
        """
        Initialize the pod log monitor.
        
        Args:
            ssh_host: SSH host to connect to (worker node with kubectl)
            ssh_user: SSH username
            ssh_password: SSH password
            namespace: Kubernetes namespace to monitor
            log_dir: Directory to save pod logs
        """
        self.ssh_host = ssh_host
        self.ssh_user = ssh_user
        self.ssh_password = ssh_password
        self.namespace = namespace
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        # SSH connection
        self.ssh_client: Optional[paramiko.SSHClient] = None
        
        # Monitoring state
        self.is_monitoring = False
        self.monitor_threads: Dict[str, threading.Thread] = {}
        self.log_queues: Dict[str, Queue] = {}
        
        # Test association
        self.current_test: Optional[str] = None
        self.test_start_time: Optional[datetime] = None
        self.test_logs: Dict[str, List[str]] = {}  # test_name -> log lines
        
        # Services to monitor
        self.monitored_services: Set[str] = set()
        
        # Error patterns to detect
        self.error_patterns = [
            "error",
            "ERROR",
            "exception",
            "Exception",
            "EXCEPTION",
            "failed",
            "FAILED",
            "timeout",
            "TIMEOUT",
            "panic",
            "PANIC",
            "fatal",
            "FATAL",
            "crash",
            "CRASH",
            "traceback",
            "Traceback",
        ]
    
    def connect(self) -> bool:
        """
        Connect to SSH host.
        
        Returns:
            True if connection successful
        """
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            self.logger.info(f"Connecting to {self.ssh_user}@{self.ssh_host}...")
            self.ssh_client.connect(
                hostname=self.ssh_host,
                username=self.ssh_user,
                password=self.ssh_password,
                timeout=10
            )
            
            self.logger.info("SSH connection established")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect via SSH: {e}")
            return False
    
    def disconnect(self):
        """Close SSH connection and stop all monitoring."""
        self.stop_all_monitoring()
        
        if self.ssh_client:
            try:
                self.ssh_client.close()
                self.logger.info("SSH connection closed")
            except Exception as e:
                self.logger.error(f"Error closing SSH connection: {e}")
    
    def start_monitoring_service(self, service_name: str, pod_selector: Optional[str] = None):
        """
        Start monitoring logs for a specific service.
        
        Args:
            service_name: Name of the service (e.g., "focus-server")
            pod_selector: Kubernetes pod selector (default: app=<service_name>)
        """
        if service_name in self.monitored_services:
            self.logger.debug(f"Already monitoring {service_name}")
            return
        
        if not pod_selector:
            pod_selector = f"app={service_name}"
        
        self.logger.info(f"Starting monitoring for service: {service_name}")
        
        # Create log queue for this service
        self.log_queues[service_name] = Queue()
        
        # Start monitoring thread
        thread = threading.Thread(
            target=self._monitor_pod_logs,
            args=(service_name, pod_selector),
            daemon=True,
            name=f"PodMonitor-{service_name}"
        )
        thread.start()
        
        self.monitor_threads[service_name] = thread
        self.monitored_services.add(service_name)
        
        self.logger.info(f"Monitoring started for {service_name}")
    
    def _monitor_pod_logs(self, service_name: str, pod_selector: str):
        """
        Monitor logs from a specific pod (runs in separate thread).
        
        Args:
            service_name: Name of the service
            pod_selector: Kubernetes pod selector
        """
        self.is_monitoring = True
        
        try:
            # Special handling for grpc-jobs (multiple pods with wildcard selector)
            if service_name == "grpc-jobs":
                self._monitor_grpc_jobs_dynamically(pod_selector)
                return
            
            # Get pod name for single-pod services
            cmd = f"kubectl get pods -n {self.namespace} -l {pod_selector} -o jsonpath='{{.items[0].metadata.name}}'"
            stdin, stdout, stderr = self.ssh_client.exec_command(cmd)
            pod_name = stdout.read().decode().strip()
            
            if not pod_name:
                self.logger.error(f"No pod found for service {service_name} with selector {pod_selector}")
                return
            
            self.logger.info(f"Monitoring pod: {pod_name} for service {service_name}")
            
            # Start streaming logs
            cmd = f"kubectl logs -n {self.namespace} -f {pod_name} --tail=50"
            stdin, stdout, stderr = self.ssh_client.exec_command(cmd, get_pty=True)
            
            # Read logs line by line
            while self.is_monitoring:
                try:
                    line = stdout.readline()
                    if not line:
                        break
                    
                    line = line.strip()
                    if line:
                        self._process_log_line(service_name, line)
                
                except Exception as e:
                    self.logger.error(f"Error reading log line from {service_name}: {e}")
                    break
        
        except Exception as e:
            self.logger.error(f"Error monitoring {service_name}: {e}")
        
        finally:
            self.logger.info(f"Stopped monitoring {service_name}")
    
    def _monitor_grpc_jobs_dynamically(self, pod_selector: str):
        """
        Monitor all gRPC job pods dynamically.
        Detects new jobs and monitors them automatically.
        
        Args:
            pod_selector: Kubernetes pod selector (e.g., "app")
        """
        self.logger.info("Starting dynamic gRPC job monitoring...")
        monitored_pods = set()
        
        while self.is_monitoring:
            try:
                # Get all running gRPC job pods
                cmd = f"kubectl get pods -n {self.namespace} --field-selector=status.phase=Running --no-headers | grep 'grpc-job-'"
                stdin, stdout, stderr = self.ssh_client.exec_command(cmd)
                output = stdout.read().decode().strip()
                
                if output:
                    current_pods = set()
                    for line in output.split('\n'):
                        parts = line.split()
                        if len(parts) > 0:
                            pod_name = parts[0]
                            # Only monitor grpc-job-* pods, not cleanup-job-*
                            if pod_name.startswith("grpc-job-") and not pod_name.startswith("grpc-job-cleanup"):
                                current_pods.add(pod_name)
                    
                    # Start monitoring new pods
                    new_pods = current_pods - monitored_pods
                    for pod_name in new_pods:
                        self.logger.info(f"Detected new gRPC job pod: {pod_name}")
                        # Start monitoring in separate thread
                        thread = threading.Thread(
                            target=self._monitor_single_grpc_pod,
                            args=(pod_name,),
                            daemon=True,
                            name=f"PodMonitor-{pod_name}"
                        )
                        thread.start()
                        monitored_pods.add(pod_name)
                
                # Check for new pods every 5 seconds
                time.sleep(5)
            
            except Exception as e:
                if self.is_monitoring:
                    self.logger.error(f"Error in dynamic gRPC job monitoring: {e}")
                time.sleep(5)
        
        self.logger.info("Stopped dynamic gRPC job monitoring")
    
    def _monitor_single_grpc_pod(self, pod_name: str):
        """
        Monitor logs from a single gRPC job pod.
        
        Args:
            pod_name: Name of the pod
        """
        try:
            self.logger.info(f"Starting log stream for: {pod_name}")
            
            # Start streaming logs from this pod
            cmd = f"kubectl logs -n {self.namespace} -f {pod_name} --tail=20"
            stdin, stdout, stderr = self.ssh_client.exec_command(cmd, get_pty=True)
            
            # Read logs line by line
            while self.is_monitoring:
                try:
                    line = stdout.readline()
                    if not line:
                        # Pod probably completed or failed
                        break
                    
                    line = line.strip()
                    if line:
                        # Log under "grpc-jobs" service name
                        enriched_line = f"[{pod_name}] {line}"
                        self._process_log_line("grpc-jobs", enriched_line)
                
                except Exception as e:
                    if self.is_monitoring:
                        self.logger.debug(f"Error reading from {pod_name}: {e}")
                    break
        
        except Exception as e:
            self.logger.error(f"Error monitoring pod {pod_name}: {e}")
        
        finally:
            self.logger.info(f"Stopped monitoring pod: {pod_name}")
    
    def _process_log_line(self, service_name: str, line: str):
        """
        Process a log line from a pod.
        
        Args:
            service_name: Name of the service that generated the log
            line: Log line content
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        # Create enriched log entry
        log_entry = {
            "timestamp": timestamp,
            "service": service_name,
            "test": self.current_test or "NO_TEST",
            "line": line,
            "is_error": self._is_error_line(line)
        }
        
        # Add to queue
        self.log_queues[service_name].put(log_entry)
        
        # Associate with current test
        if self.current_test:
            if self.current_test not in self.test_logs:
                self.test_logs[self.current_test] = []
            
            formatted_line = f"[{timestamp}] [{service_name}] {line}"
            self.test_logs[self.current_test].append(formatted_line)
            
            # If error, log it prominently
            if log_entry["is_error"]:
                self.logger.warning(
                    f"ERROR detected in {service_name} during test {self.current_test}: {line}"
                )
        
        # Also log to main pod log file
        self._write_to_pod_log_file(service_name, timestamp, line, log_entry["is_error"])
    
    def _is_error_line(self, line: str) -> bool:
        """
        Check if a log line contains an error.
        
        Args:
            line: Log line to check
            
        Returns:
            True if line contains error indicators
        """
        line_lower = line.lower()
        return any(pattern.lower() in line_lower for pattern in self.error_patterns)
    
    def _write_to_pod_log_file(self, service_name: str, timestamp: str, line: str, is_error: bool):
        """
        Write log line to service-specific log file.
        
        Args:
            service_name: Name of the service
            timestamp: Timestamp of the log
            line: Log line content
            is_error: Whether this is an error line
        """
        try:
            # Main log file
            log_file = self.log_dir / f"{service_name}_realtime.log"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {line}\n")
            
            # Error-only log file
            if is_error:
                error_log_file = self.log_dir / f"{service_name}_errors.log"
                with open(error_log_file, "a", encoding="utf-8") as f:
                    test_info = f"[TEST: {self.current_test}] " if self.current_test else ""
                    f.write(f"[{timestamp}] {test_info}{line}\n")
        
        except Exception as e:
            self.logger.error(f"Error writing to log file: {e}")
    
    def set_current_test(self, test_name: str):
        """
        Set the currently running test.
        
        Args:
            test_name: Name of the test
        """
        self.current_test = test_name
        self.test_start_time = datetime.now()
        
        self.logger.info(f"=" * 80)
        self.logger.info(f"TEST STARTED: {test_name}")
        self.logger.info(f"=" * 80)
        
        # Initialize test log storage
        if test_name not in self.test_logs:
            self.test_logs[test_name] = []
    
    def clear_current_test(self):
        """Clear the current test context."""
        if self.current_test:
            self.logger.info(f"=" * 80)
            self.logger.info(f"TEST FINISHED: {self.current_test}")
            self.logger.info(f"=" * 80)
            
            # Save test-specific logs
            self._save_test_logs(self.current_test)
        
        self.current_test = None
        self.test_start_time = None
    
    def _save_test_logs(self, test_name: str):
        """
        Save logs for a specific test.
        
        Args:
            test_name: Name of the test
        """
        if test_name not in self.test_logs or not self.test_logs[test_name]:
            return
        
        try:
            # Create test logs directory
            test_logs_dir = self.log_dir / "test_logs"
            test_logs_dir.mkdir(parents=True, exist_ok=True)
            
            # Sanitize test name for filename
            safe_test_name = test_name.replace("/", "_").replace("\\", "_").replace(":", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save all logs for this test
            log_file = test_logs_dir / f"{safe_test_name}_{timestamp}.log"
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(f"Test: {test_name}\n")
                f.write(f"Started: {self.test_start_time}\n")
                f.write(f"Finished: {datetime.now()}\n")
                f.write("=" * 80 + "\n\n")
                
                for log_line in self.test_logs[test_name]:
                    f.write(log_line + "\n")
            
            # Check for errors in test logs
            error_lines = [line for line in self.test_logs[test_name] if self._is_error_line(line)]
            
            if error_lines:
                self.logger.warning(
                    f"Test {test_name} had {len(error_lines)} error(s) in pod logs"
                )
                
                # Save error summary
                error_file = test_logs_dir / f"{safe_test_name}_{timestamp}_ERRORS.log"
                with open(error_file, "w", encoding="utf-8") as f:
                    f.write(f"Test: {test_name}\n")
                    f.write(f"Error Count: {len(error_lines)}\n")
                    f.write("=" * 80 + "\n\n")
                    
                    for error_line in error_lines:
                        f.write(error_line + "\n")
            
            self.logger.info(f"Saved logs for test: {test_name} -> {log_file}")
        
        except Exception as e:
            self.logger.error(f"Error saving test logs: {e}")
    
    def get_test_logs(self, test_name: str) -> List[str]:
        """
        Get logs for a specific test.
        
        Args:
            test_name: Name of the test
            
        Returns:
            List of log lines for the test
        """
        return self.test_logs.get(test_name, [])
    
    def get_test_errors(self, test_name: str) -> List[str]:
        """
        Get error logs for a specific test.
        
        Args:
            test_name: Name of the test
            
        Returns:
            List of error log lines for the test
        """
        all_logs = self.get_test_logs(test_name)
        return [line for line in all_logs if self._is_error_line(line)]
    
    def stop_monitoring_service(self, service_name: str):
        """
        Stop monitoring a specific service.
        
        Args:
            service_name: Name of the service
        """
        if service_name not in self.monitored_services:
            return
        
        self.logger.info(f"Stopping monitoring for {service_name}")
        
        self.monitored_services.remove(service_name)
        
        # Thread will stop when is_monitoring is False
        if service_name in self.monitor_threads:
            thread = self.monitor_threads[service_name]
            # Give thread time to finish
            thread.join(timeout=2)
            del self.monitor_threads[service_name]
        
        # Clear queue
        if service_name in self.log_queues:
            del self.log_queues[service_name]
    
    def stop_all_monitoring(self):
        """Stop monitoring all services."""
        self.logger.info("Stopping all pod monitoring...")
        self.is_monitoring = False
        
        # Stop all monitoring threads
        for service_name in list(self.monitored_services):
            self.stop_monitoring_service(service_name)
        
        self.logger.info("All monitoring stopped")
    
    def get_monitoring_summary(self) -> Dict:
        """
        Get summary of monitoring activity.
        
        Returns:
            Dictionary with monitoring statistics
        """
        total_tests = len(self.test_logs)
        total_errors = sum(len(self.get_test_errors(test)) for test in self.test_logs)
        
        return {
            "monitored_services": list(self.monitored_services),
            "total_tests_monitored": total_tests,
            "total_errors_detected": total_errors,
            "tests_with_errors": [
                test for test in self.test_logs if self.get_test_errors(test)
            ]
        }

