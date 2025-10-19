"""
Pod Logs Collector
==================

Utility for collecting and monitoring logs from Kubernetes pods in real-time.
Useful for debugging tests by seeing what happens inside the services being tested.
"""

import paramiko
import logging
import threading
import time
from typing import Optional, List, Callable
from queue import Queue, Empty


class PodLogsCollector:
    """
    Collects logs from Kubernetes pods via SSH connection.
    
    Features:
    - Real-time log streaming
    - Background log collection
    - Filtering and searching
    - Multiple pod monitoring
    """
    
    def __init__(
        self,
        ssh_host: str,
        ssh_user: str,
        ssh_password: str,
        namespace: str = "default"
    ):
        """
        Initialize the logs collector.
        
        Args:
            ssh_host: SSH host for kubectl access
            ssh_user: SSH username
            ssh_password: SSH password
            namespace: Kubernetes namespace
        """
        self.ssh_host = ssh_host
        self.ssh_user = ssh_user
        self.ssh_password = ssh_password
        self.namespace = namespace
        
        self.logger = logging.getLogger(__name__)
        self.ssh_client: Optional[paramiko.SSHClient] = None
        self.log_threads: List[threading.Thread] = []
        self.stop_flag = threading.Event()
        
    def connect(self):
        """Establish SSH connection."""
        self.logger.info(f"Connecting to {self.ssh_user}@{self.ssh_host} for log collection...")
        
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            self.ssh_client.connect(
                hostname=self.ssh_host,
                username=self.ssh_user,
                password=self.ssh_password,
                timeout=10
            )
            self.logger.info("✅ SSH connection established for log collection")
        except Exception as e:
            self.logger.error(f"Failed to connect for log collection: {e}")
            raise
    
    def get_pod_name(self, service_name: str) -> Optional[str]:
        """
        Get pod name for a service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Pod name or None if not found
        """
        if not self.ssh_client:
            raise RuntimeError("SSH client not connected. Call connect() first.")
        
        command = f"kubectl get pods -n {self.namespace} -l app={service_name} -o jsonpath='{{.items[0].metadata.name}}'"
        
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            pod_name = stdout.read().decode().strip()
            
            if pod_name:
                self.logger.info(f"Found pod: {pod_name} for service: {service_name}")
                return pod_name
            else:
                # Try alternative label
                command = f"kubectl get pods -n {self.namespace} | grep {service_name} | head -1 | awk '{{print $1}}'"
                stdin, stdout, stderr = self.ssh_client.exec_command(command)
                pod_name = stdout.read().decode().strip()
                
                if pod_name:
                    self.logger.info(f"Found pod: {pod_name} for service: {service_name}")
                    return pod_name
                
                self.logger.warning(f"No pod found for service: {service_name}")
                return None
        except Exception as e:
            self.logger.error(f"Error finding pod for {service_name}: {e}")
            return None
    
    def tail_logs(
        self,
        pod_name: str,
        lines: int = 100,
        follow: bool = False,
        container: Optional[str] = None
    ) -> str:
        """
        Get logs from a pod.
        
        Args:
            pod_name: Name of the pod
            lines: Number of lines to retrieve
            follow: Whether to follow logs (stream)
            container: Specific container name (optional)
            
        Returns:
            Log output as string
        """
        if not self.ssh_client:
            raise RuntimeError("SSH client not connected. Call connect() first.")
        
        command = f"kubectl logs -n {self.namespace} {pod_name} --tail={lines}"
        
        if container:
            command += f" -c {container}"
        
        if follow:
            command += " -f"
        
        self.logger.info(f"Collecting logs from pod: {pod_name}")
        
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=5)
            logs = stdout.read().decode()
            
            if logs:
                self.logger.debug(f"Collected {len(logs)} bytes of logs from {pod_name}")
                return logs
            else:
                error = stderr.read().decode()
                if error:
                    self.logger.warning(f"Error getting logs from {pod_name}: {error}")
                return ""
        except Exception as e:
            self.logger.error(f"Failed to get logs from {pod_name}: {e}")
            return ""
    
    def stream_logs_to_logger(
        self,
        pod_name: str,
        log_prefix: str = "",
        lines: int = 50,
        container: Optional[str] = None,
        filter_func: Optional[Callable[[str], bool]] = None
    ):
        """
        Stream logs from pod to Python logger in background thread.
        
        Args:
            pod_name: Name of the pod
            log_prefix: Prefix for log lines
            lines: Number of initial lines to retrieve
            container: Specific container name (optional)
            filter_func: Optional function to filter log lines
        """
        def _stream_worker():
            if not self.ssh_client:
                self.logger.error("SSH client not connected")
                return
            
            command = f"kubectl logs -n {self.namespace} {pod_name} --tail={lines} -f"
            if container:
                command += f" -c {container}"
            
            self.logger.info(f"Starting log stream from {pod_name}...")
            
            try:
                # Open SSH channel for streaming
                transport = self.ssh_client.get_transport()
                channel = transport.open_session()
                channel.exec_command(command)
                
                # Read logs line by line
                while not self.stop_flag.is_set():
                    if channel.recv_ready():
                        line = channel.recv(4096).decode()
                        
                        for log_line in line.strip().split('\n'):
                            if log_line and not self.stop_flag.is_set():
                                # Apply filter if provided
                                if filter_func and not filter_func(log_line):
                                    continue
                                
                                # Log to Python logger
                                if log_prefix:
                                    self.logger.info(f"[{log_prefix}] {log_line}")
                                else:
                                    self.logger.info(log_line)
                    
                    if channel.exit_status_ready():
                        break
                    
                    time.sleep(0.1)
                
                channel.close()
                self.logger.info(f"Log stream from {pod_name} stopped")
                
            except Exception as e:
                if not self.stop_flag.is_set():
                    self.logger.error(f"Error streaming logs from {pod_name}: {e}")
        
        # Start background thread
        thread = threading.Thread(target=_stream_worker, daemon=True)
        thread.start()
        self.log_threads.append(thread)
        
        self.logger.info(f"✅ Started background log streaming from {pod_name}")
    
    def collect_logs_for_service(
        self,
        service_name: str,
        lines: int = 100,
        stream: bool = False,
        container: Optional[str] = None
    ) -> Optional[str]:
        """
        Collect logs for a service (finds pod automatically).
        
        Args:
            service_name: Name of the service
            lines: Number of lines to retrieve
            stream: Whether to stream logs in background
            container: Specific container name (optional)
            
        Returns:
            Log output as string (if not streaming), None if streaming
        """
        pod_name = self.get_pod_name(service_name)
        
        if not pod_name:
            self.logger.warning(f"Cannot collect logs: pod not found for {service_name}")
            return None
        
        if stream:
            self.stream_logs_to_logger(
                pod_name=pod_name,
                log_prefix=service_name,
                lines=lines,
                container=container
            )
            return None
        else:
            return self.tail_logs(
                pod_name=pod_name,
                lines=lines,
                container=container
            )
    
    def save_logs_to_file(
        self,
        service_name: str,
        output_file: str,
        lines: int = 1000,
        container: Optional[str] = None
    ):
        """
        Save logs from a service to a file.
        
        Args:
            service_name: Name of the service
            output_file: Path to output file
            lines: Number of lines to retrieve
            container: Specific container name (optional)
        """
        logs = self.collect_logs_for_service(
            service_name=service_name,
            lines=lines,
            stream=False,
            container=container
        )
        
        if logs:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"=== Logs from {service_name} ===\n")
                f.write(f"Retrieved: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*80}\n\n")
                f.write(logs)
            
            self.logger.info(f"✅ Saved logs to {output_file}")
        else:
            self.logger.warning(f"No logs collected for {service_name}")
    
    def stop_streaming(self):
        """Stop all background log streaming threads."""
        self.logger.info("Stopping log streams...")
        self.stop_flag.set()
        
        # Wait for threads to finish
        for thread in self.log_threads:
            thread.join(timeout=2)
        
        self.log_threads.clear()
        self.stop_flag.clear()
        
        self.logger.info("All log streams stopped")
    
    def disconnect(self):
        """Close SSH connection."""
        self.stop_streaming()
        
        if self.ssh_client:
            self.ssh_client.close()
            self.logger.info("SSH connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


# Utility functions for common use cases

def collect_focus_server_logs(
    ssh_host: str,
    ssh_user: str,
    ssh_password: str,
    lines: int = 200,
    output_file: Optional[str] = None
) -> str:
    """
    Collect logs from Focus Server pod.
    
    Args:
        ssh_host: SSH host
        ssh_user: SSH username
        ssh_password: SSH password
        lines: Number of lines to retrieve
        output_file: Optional file to save logs
        
    Returns:
        Log output as string
    """
    collector = PodLogsCollector(ssh_host, ssh_user, ssh_password)
    
    try:
        collector.connect()
        logs = collector.collect_logs_for_service("focus-server", lines=lines)
        
        if output_file and logs:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(logs)
        
        return logs or ""
    finally:
        collector.disconnect()


def stream_service_logs_during_test(
    ssh_host: str,
    ssh_user: str,
    ssh_password: str,
    services: List[str],
    lines: int = 50
) -> PodLogsCollector:
    """
    Start streaming logs from multiple services during a test.
    Returns collector object - caller must call disconnect() when done.
    
    Args:
        ssh_host: SSH host
        ssh_user: SSH username
        ssh_password: SSH password
        services: List of service names to monitor
        lines: Number of initial lines to retrieve
        
    Returns:
        PodLogsCollector instance (caller must disconnect when done)
    """
    collector = PodLogsCollector(ssh_host, ssh_user, ssh_password)
    collector.connect()
    
    for service in services:
        collector.collect_logs_for_service(
            service_name=service,
            lines=lines,
            stream=True
        )
    
    return collector

