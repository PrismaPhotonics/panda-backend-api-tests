"""
RabbitMQ Connection Manager with Auto Port-Forward
===================================================

Automates RabbitMQ connection setup including:
- K8s service discovery
- Credential extraction from secrets
- Auto port-forward with cleanup
- SSH tunnel management
- Fully automated (no password prompts!)

Author: QA Automation Architect
Date: 2025-10-08
"""

import subprocess
import time
import logging
import socket
import base64
import threading
import os
import sys
from typing import Optional, Dict, Tuple
from contextlib import contextmanager
from dataclasses import dataclass

try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False
    logging.warning("paramiko not installed - SSH automation will be limited")

logger = logging.getLogger(__name__)


@dataclass
class RabbitMQCredentials:
    """RabbitMQ credentials."""
    username: str
    password: str
    host: str
    port: int
    management_port: int
    service_name: str


class RabbitMQConnectionManager:
    """
    Manages RabbitMQ connections with automatic setup and teardown.
    
    Features:
    - Auto-discovers RabbitMQ services in K8s
    - Extracts credentials from K8s secrets
    - Sets up kubectl port-forward automatically
    - Cleans up resources on exit
    
    Usage:
        with RabbitMQConnectionManager(k8s_host='10.10.10.150') as conn_info:
            # Use conn_info to connect to RabbitMQ
            client = BabyAnalyzerMQClient(**conn_info)
    """
    
    def __init__(
        self,
        k8s_host: str,
        ssh_user: str = "prisma",
        ssh_password: Optional[str] = None,
        ssh_key_file: Optional[str] = None,
        namespace: str = "panda",
        preferred_service: str = "rabbitmq-panda",
        local_port: int = 5672,
        local_mgmt_port: int = 15672
    ):
        """
        Initialize RabbitMQ Connection Manager.
        
        Args:
            k8s_host: Kubernetes cluster host IP
            ssh_user: SSH username for K8s host
            ssh_password: SSH password (optional, uses SSH keys if None)
            ssh_key_file: SSH key file path (optional, for key authentication)
            namespace: K8s namespace
            preferred_service: Preferred RabbitMQ service name
            local_port: Local port for AMQP
            local_mgmt_port: Local port for Management UI
        """
        self.k8s_host = k8s_host
        self.ssh_user = ssh_user
        self.ssh_password = ssh_password
        self.ssh_key_file = ssh_key_file
        self.namespace = namespace
        self.preferred_service = preferred_service
        self.local_port = local_port
        self.local_mgmt_port = local_mgmt_port
        
        self.port_forward_process: Optional[subprocess.Popen] = None
        self.credentials: Optional[RabbitMQCredentials] = None
    
    def discover_rabbitmq_services(self) -> Dict[str, str]:
        """
        Discover RabbitMQ services in K8s cluster.
        
        Returns:
            Dict mapping service names to their LoadBalancer IPs
        """
        logger.info(f"Discovering RabbitMQ services in namespace {self.namespace}...")
        
        try:
            # Get services via kubectl (assumes kubectl is configured)
            result = subprocess.run(
                ["kubectl", "get", "svc", "-n", self.namespace, "-o", "json"],
                capture_output=True,
                text=True,
                timeout=30  # Increased from 10 to 30 seconds (matching SSH timeout)
            )
            
            if result.returncode != 0:
                logger.warning("kubectl not available locally or failed, will use SSH")
                return self._discover_via_ssh()
            
            import json
            services = json.loads(result.stdout)
            
            rabbitmq_services = {}
            for item in services.get("items", []):
                name = item["metadata"]["name"]
                if "rabbitmq" in name.lower() and "headless" not in name.lower():
                    rabbitmq_services[name] = item
            
            logger.info(f"Found RabbitMQ services: {list(rabbitmq_services.keys())}")
            return rabbitmq_services
            
        except subprocess.TimeoutExpired:
            # kubectl timed out - fallback to SSH
            logger.warning("kubectl command timed out, falling back to SSH discovery")
            return self._discover_via_ssh()
        except FileNotFoundError:
            # kubectl not installed - fallback to SSH
            logger.warning("kubectl not found, falling back to SSH discovery")
            return self._discover_via_ssh()
        except Exception as e:
            # Any other error - try SSH as fallback
            logger.warning(f"kubectl discovery failed ({e}), falling back to SSH")
            return self._discover_via_ssh()
    
    def _discover_via_ssh(self) -> Dict[str, str]:
        """Discover services via SSH when kubectl is not available locally."""
        logger.info("Discovering services via SSH...")
        
        cmd = f"kubectl get svc -n {self.namespace} --output=json"
        result = self._run_ssh_command(cmd)
        
        if result:
            import json
            services = json.loads(result)
            rabbitmq_services = {}
            for item in services.get("items", []):
                name = item["metadata"]["name"]
                if "rabbitmq" in name.lower() and "headless" not in name.lower():
                    rabbitmq_services[name] = item
            return rabbitmq_services
        
        return {}
    
    def extract_credentials(self, service_name: str) -> Optional[RabbitMQCredentials]:
        """
        Extract RabbitMQ credentials from K8s secret.
        
        Args:
            service_name: RabbitMQ service name
            
        Returns:
            RabbitMQCredentials or None if extraction fails
        """
        logger.info(f"Extracting credentials for service: {service_name}")
        
        try:
            # Try to get secret with same name as service
            secret_name = service_name
            
            # Get username
            username_cmd = (
                f"kubectl get secret {secret_name} -n {self.namespace} "
                f"-o jsonpath='{{.data.rabbitmq-username}}' | base64 -d"
            )
            username = self._run_ssh_command(username_cmd)
            
            # Get password
            password_cmd = (
                f"kubectl get secret {secret_name} -n {self.namespace} "
                f"-o jsonpath='{{.data.rabbitmq-password}}' | base64 -d"
            )
            password = self._run_ssh_command(password_cmd)
            
            # If username is empty, try default RabbitMQ username
            if not username or username.strip() == "":
                username = "user"  # Default for Helm charts
            
            if not password:
                logger.error(f"Failed to extract password for {service_name}")
                return None
            
            logger.info(f"Successfully extracted credentials (username: {username})")
            
            return RabbitMQCredentials(
                username=username.strip(),
                password=password.strip(),
                host=self.k8s_host,
                port=self.local_port,
                management_port=self.local_mgmt_port,
                service_name=service_name
            )
            
        except Exception as e:
            logger.error(f"Failed to extract credentials: {e}")
            return None
    
    def _run_ssh_command(self, command: str) -> Optional[str]:
        """
        Run command on K8s host via SSH (fully automated with paramiko).
        
        Args:
            command: Command to run
        
        Returns:
            Command output or None if failed
        """
        if not PARAMIKO_AVAILABLE:
            # Fallback to subprocess (will prompt for password)
            logger.warning("Using fallback SSH (may prompt for password)")
            return self._run_ssh_command_fallback(command)
        
        # Check if we have authentication method
        if not self.ssh_password and not self.ssh_key_file:
            logger.warning("No SSH authentication method configured")
            return None
        
        try:
            # Create SSH client with paramiko (no password prompt!)
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            logger.debug(f"Connecting to {self.ssh_user}@{self.k8s_host}...")
            
            # Expand tilde in key_file path if needed
            key_file = None
            if self.ssh_key_file:
                from pathlib import Path
                if self.ssh_key_file.startswith('~'):
                    # On Windows, prefer USERPROFILE env var (works correctly for services)
                    if sys.platform == 'win32':
                        home = os.environ.get('USERPROFILE') or str(Path.home())
                    else:
                        home = str(Path.home())
                    key_file = self.ssh_key_file.replace('~', home, 1)
                else:
                    key_file = self.ssh_key_file
            
            # Connect with key file (preferred) or password
            if key_file:
                client.connect(
                    hostname=self.k8s_host,
                    username=self.ssh_user,
                    key_filename=key_file,
                    timeout=30,
                    allow_agent=False,  # Don't try agent when we have key file
                    look_for_keys=False  # Don't look for other keys
                )
            elif self.ssh_password:
                client.connect(
                    hostname=self.k8s_host,
                    username=self.ssh_user,
                    password=self.ssh_password,
                    timeout=30,
                    look_for_keys=False,  # Don't use SSH keys
                    allow_agent=False     # Don't use SSH agent
                )
            
            # Execute command
            logger.debug(f"Executing: {command}")
            stdin, stdout, stderr = client.exec_command(command, timeout=30)
            
            # Get output
            exit_code = stdout.channel.recv_exit_status()
            output = stdout.read().decode('utf-8').strip()
            error = stderr.read().decode('utf-8').strip()
            
            client.close()
            
            if exit_code == 0:
                return output
            else:
                logger.error(f"SSH command failed (exit {exit_code}): {error}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to run SSH command via paramiko: {e}")
            return None
    
    def _run_ssh_command_fallback(self, command: str) -> Optional[str]:
        """
        Fallback SSH method using subprocess (may prompt for password).
        
        Args:
            command: Command to run
            
        Returns:
            Command output or None if failed
        """
        ssh_cmd = [
            "ssh",
            f"{self.ssh_user}@{self.k8s_host}",
            command
        ]
        
        try:
            result = subprocess.run(
                ssh_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.error(f"SSH command failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to run SSH command: {e}")
            return None
    
    def start_port_forward(self, service_name: str) -> bool:
        """
        Start kubectl port-forward on remote host (fully automated).
        
        Args:
            service_name: RabbitMQ service name
            
        Returns:
            True if successful
        """
        logger.info(f"Starting port-forward for {service_name}...")
        
        if not PARAMIKO_AVAILABLE:
            logger.error("Paramiko not available for automation")
            return False
        
        # Check if we have authentication method
        if not self.ssh_password and not self.ssh_key_file:
            logger.error("No SSH authentication method configured (password or key_file)")
            return False
        
        try:
            # Start port-forward via paramiko in background thread
            def run_port_forward():
                """Run port-forward in background."""
                try:
                    # Create SSH client
                    client = paramiko.SSHClient()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    
                    logger.info(f"Connecting to {self.ssh_user}@{self.k8s_host} for port-forward...")
                    
                    # Try key file first (preferred), then password
                    if self.ssh_key_file:
                        # Expand tilde in key_file path
                        from pathlib import Path
                        if self.ssh_key_file.startswith('~'):
                            # On Windows, prefer USERPROFILE env var (works correctly for services)
                            if sys.platform == 'win32':
                                home = os.environ.get('USERPROFILE') or str(Path.home())
                            else:
                                home = str(Path.home())
                            key_file = self.ssh_key_file.replace('~', home, 1)
                        else:
                            key_file = self.ssh_key_file
                        
                        client.connect(
                            hostname=self.k8s_host,
                            username=self.ssh_user,
                            key_filename=key_file,
                            timeout=30,
                            allow_agent=False,  # Don't try agent when we have key file
                            look_for_keys=False  # Don't look for other keys
                        )
                    elif self.ssh_password:
                        client.connect(
                            hostname=self.k8s_host,
                            username=self.ssh_user,
                            password=self.ssh_password,
                            timeout=30,
                            look_for_keys=False,
                            allow_agent=False
                        )
                    
                    # Start port-forward (this will keep running)
                    pf_cmd = (
                        f"kubectl port-forward --address 0.0.0.0 -n {self.namespace} "
                        f"svc/{service_name} {self.local_port}:5672 {self.local_mgmt_port}:15672"
                    )
                    
                    logger.info(f"Starting kubectl port-forward on remote host...")
                    stdin, stdout, stderr = client.exec_command(pf_cmd)
                    
                    # Keep thread alive and log output
                    for line in stdout:
                        logger.debug(f"port-forward: {line.strip()}")
                    
                    # If we get here, port-forward stopped
                    logger.info("Port-forward stopped")
                    client.close()
                    
                except Exception as e:
                    logger.error(f"Port-forward thread error: {e}")
            
            # Start in background thread
            pf_thread = threading.Thread(target=run_port_forward, daemon=True)
            pf_thread.start()
            
            # Wait for port-forward to be ready
            logger.info("Waiting for port-forward to start...")
            max_wait = 15
            for i in range(max_wait):
                time.sleep(1)
                if self._check_port_open(self.k8s_host, self.local_port):
                    logger.info(f"✅ Port-forward active on {self.k8s_host}:{self.local_port}")
                    return True
                logger.debug(f"Waiting for port... ({i+1}/{max_wait})")
            
            logger.error("Port-forward did not start in time")
            return False
                
        except Exception as e:
            logger.error(f"Failed to start port-forward: {e}")
            return False
    
    def _check_port_open(self, host: str, port: int, timeout: int = 5) -> bool:
        """
        Check if a port is open.
        
        Args:
            host: Host to check
            port: Port to check
            timeout: Timeout in seconds
            
        Returns:
            True if port is open
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        try:
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def stop_port_forward(self):
        """Stop port-forward process."""
        if self.port_forward_process:
            logger.info("Stopping port-forward...")
            try:
                self.port_forward_process.terminate()
                self.port_forward_process.wait(timeout=5)
                logger.info("✅ Port-forward stopped")
            except Exception as e:
                logger.error(f"Failed to stop port-forward: {e}")
                try:
                    self.port_forward_process.kill()
                except:
                    pass
    
    def setup(self) -> Dict[str, any]:
        """
        Complete setup: discover, extract credentials, start port-forward.
        
        Returns:
            Dict with connection info
        """
        logger.info("=" * 70)
        logger.info("Setting up RabbitMQ connection...")
        logger.info("=" * 70)
        
        # 1. Discover services
        services = self.discover_rabbitmq_services()
        
        if not services:
            raise RuntimeError("No RabbitMQ services found")
        
        # 2. Choose service (prefer specified, fallback to first available)
        service_name = self.preferred_service
        if service_name not in services:
            service_name = list(services.keys())[0]
            logger.warning(
                f"Preferred service '{self.preferred_service}' not found, "
                f"using '{service_name}'"
            )
        
        # 3. Extract credentials
        self.credentials = self.extract_credentials(service_name)
        
        if not self.credentials:
            raise RuntimeError(f"Failed to extract credentials for {service_name}")
        
        # 4. Start port-forward
        if not self.start_port_forward(service_name):
            raise RuntimeError("Failed to start port-forward")
        
        logger.info("=" * 70)
        logger.info("✅ RabbitMQ connection ready!")
        logger.info(f"   Service: {service_name}")
        logger.info(f"   Host: {self.k8s_host}:{self.local_port}")
        logger.info(f"   Username: {self.credentials.username}")
        logger.info(f"   Management UI: http://{self.k8s_host}:{self.local_mgmt_port}")
        logger.info("=" * 70)
        
        return {
            "host": self.k8s_host,  # Connect to server, not localhost
            "port": self.local_port,
            "username": self.credentials.username,
            "password": self.credentials.password,
            "virtual_host": "/",
            "management_port": self.local_mgmt_port
        }
    
    def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up RabbitMQ connection...")
        self.stop_port_forward()
    
    def __enter__(self):
        """Context manager entry."""
        return self.setup()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
        return False


@contextmanager
def rabbitmq_connection(
    k8s_host: str = "10.10.10.150",
    service: str = "rabbitmq-panda",
    namespace: str = "default"
):
    """
    Context manager for RabbitMQ connection with auto-setup and cleanup.
    
    Usage:
        with rabbitmq_connection() as conn_info:
            client = BabyAnalyzerMQClient(**conn_info)
            client.send_keepalive()
    
    Args:
        k8s_host: Kubernetes host
        service: RabbitMQ service name
        namespace: K8s namespace
        
    Yields:
        Dict with connection info (host, port, username, password)
    """
    manager = RabbitMQConnectionManager(
        k8s_host=k8s_host,
        preferred_service=service,
        namespace=namespace
    )
    
    try:
        conn_info = manager.setup()
        yield conn_info
    finally:
        manager.cleanup()

