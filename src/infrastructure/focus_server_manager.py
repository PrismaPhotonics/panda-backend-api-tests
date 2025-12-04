"""
Focus Server Connection Manager
================================

Manages Focus Server connectivity including automatic port-forwarding via SSH.
"""

import time
import logging
import socket
from typing import Optional, Any

try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False

logger = logging.getLogger(__name__)


class FocusServerConnectionManager:
    """
    Automated Focus Server connection manager.
    
    Handles:
    - Service discovery in Kubernetes
    - Automatic port-forwarding via SSH
    - Connection validation
    - Cleanup
    """
    
    def __init__(
        self,
        k8s_host: str,
        ssh_user: str,
        ssh_password: Optional[str] = None,
        ssh_key_file: Optional[str] = None,
        service_name: str = "focus-server",
        namespace: str = "panda",
        local_port: int = 5000,
        remote_port: int = 5000
    ):
        """
        Initialize Focus Server connection manager.
        
        Args:
            k8s_host: Kubernetes cluster host IP
            ssh_user: SSH username for remote host
            ssh_password: SSH password (optional, for automation)
            ssh_key_file: SSH key file path (optional, for key authentication)
            service_name: Focus Server service name in K8s
            namespace: Kubernetes namespace
            local_port: Local port to bind
            remote_port: Remote service port
        """
        self.k8s_host = k8s_host
        self.ssh_user = ssh_user
        self.ssh_password = ssh_password
        self.ssh_key_file = ssh_key_file
        self.service_name = service_name
        self.namespace = namespace
        self.local_port = local_port
        self.remote_port = remote_port
        
        self.ssh_client: Optional[paramiko.SSHClient] = None
        self.port_forward_active = False
        self._ssh_manager_ref: Optional[Any] = None  # Reference to SSHManager if used
        
        logger.info(f"FocusServerConnectionManager initialized for {service_name}")
    
    def _check_port_open(self, host: str, port: int, timeout: int = 2) -> bool:
        """Check if port is open and accepting connections."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.debug(f"Port check failed: {e}")
            return False
    
    def discover_service(self, config_manager=None) -> Optional[str]:
        """
        Discover Focus Server service in Kubernetes.
        
        Args:
            config_manager: Optional ConfigManager instance (for SSHManager support)
        
        Returns:
            Service name if found, None otherwise
        """
        if not PARAMIKO_AVAILABLE:
            logger.warning("Paramiko not available, cannot discover service")
            return None
        
        try:
            # Use SSHManager if config_manager provided (handles jump host automatically)
            if config_manager:
                from src.infrastructure.ssh_manager import SSHManager
                ssh_manager = SSHManager(config_manager)
                if ssh_manager.connect():
                    logger.debug("Using SSHManager for service discovery (with jump host support)")
                    cmd = f"kubectl get svc -n {self.namespace} -o name | grep {self.service_name}"
                    result = ssh_manager.execute_command(cmd, timeout=30)
                    output = result.get("stdout", "").strip()
                    
                    if output and self.service_name in output:
                        service = output.split('/')[-1] if '/' in output else output
                        logger.info(f"Found Focus Server service: {service}")
                        return service
                    else:
                        logger.warning(f"Focus Server service '{self.service_name}' not found in K8s")
                        return None
                else:
                    logger.warning("SSHManager connection failed, falling back to direct connection")
            
            # Fallback: direct connection (legacy)
            if not self.ssh_password and not self.ssh_key_file:
                logger.warning("No SSH authentication method configured for service discovery")
                return None
            
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            logger.debug(f"Connecting to {self.ssh_user}@{self.k8s_host} for service discovery...")
            
            # Connect with key file or password
            if self.ssh_key_file:
                client.connect(
                    hostname=self.k8s_host,
                    username=self.ssh_user,
                    key_filename=self.ssh_key_file,
                    timeout=30,
                    look_for_keys=True,
                    allow_agent=True
                )
            else:
                client.connect(
                    hostname=self.k8s_host,
                    username=self.ssh_user,
                    password=self.ssh_password,
                    timeout=30,
                    look_for_keys=False,
                    allow_agent=False
                )
            
            # List services
            cmd = f"kubectl get svc -n {self.namespace} -o name | grep {self.service_name}"
            stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
            output = stdout.read().decode('utf-8').strip()
            
            client.close()
            
            if output and self.service_name in output:
                # Extract service name (format: service/focus-server)
                service = output.split('/')[-1] if '/' in output else output
                logger.info(f"Found Focus Server service: {service}")
                return service
            else:
                logger.warning(f"Focus Server service '{self.service_name}' not found in K8s")
                return None
                
        except Exception as e:
            logger.error(f"Failed to discover service: {e}")
            return None
    
    def _kill_existing_port_forwards(self):
        """Kill any existing port-forwards on the specified port."""
        if not PARAMIKO_AVAILABLE:
            return

        # Check if we have authentication method
        if not self.ssh_password and not self.ssh_key_file:
            return

        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            logger.debug(f"Checking for existing port-forwards on port {self.local_port}...")
            
            # Connect with key file or password
            if self.ssh_key_file:
                client.connect(
                    hostname=self.k8s_host,
                    username=self.ssh_user,
                    key_filename=self.ssh_key_file,
                    timeout=30,
                    look_for_keys=True,
                    allow_agent=True
                )
            else:
                client.connect(
                    hostname=self.k8s_host,
                    username=self.ssh_user,
                    password=self.ssh_password,
                    timeout=30,
                    look_for_keys=False,
                    allow_agent=False
                )

            # Kill processes listening on the port
            kill_cmd = f"fuser -k {self.local_port}/tcp 2>/dev/null || true"
            stdin, stdout, stderr = client.exec_command(kill_cmd, timeout=10)
            stdout.read()  # Wait for command to complete

            logger.debug(f"Cleaned up any existing port-forwards on port {self.local_port}")
            client.close()

            # Wait a moment for port to be released
            time.sleep(2)

        except Exception as e:
            logger.debug(f"Error cleaning up existing port-forwards: {e}")

    def start_port_forward(self, config_manager=None) -> bool:
        """
        Start kubectl port-forward on remote host via SSH.

        Args:
            config_manager: Optional ConfigManager instance (for SSHManager support)

        Returns:
            True if port-forward started successfully
        """
        logger.info(f"Starting port-forward for {self.service_name}...")

        if not PARAMIKO_AVAILABLE:
            logger.error("Paramiko not available for automation")
            return False

        # Kill any existing port-forwards on this port
        self._kill_existing_port_forwards()

        try:
            import threading

            def run_port_forward():
                try:
                    # Use SSHManager if config_manager provided (handles jump host automatically)
                    if config_manager:
                        from src.infrastructure.ssh_manager import SSHManager
                        ssh_manager = SSHManager(config_manager)
                        if ssh_manager.connect():
                            logger.debug("Using SSHManager for port-forward (with jump host support)")
                            client = ssh_manager.ssh_client
                            # Keep reference to prevent cleanup (stored in self for cleanup later)
                            self._ssh_manager_ref = ssh_manager
                        else:
                            logger.error("Failed to connect via SSHManager")
                            return
                    else:
                        # Fallback: direct connection (legacy)
                        if not self.ssh_password and not self.ssh_key_file:
                            logger.error("No SSH authentication method configured for automation")
                            return
                        
                        client = paramiko.SSHClient()
                        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        
                        logger.info(f"Connecting to {self.ssh_user}@{self.k8s_host} for port-forward...")
                        
                        if self.ssh_key_file:
                            client.connect(
                                hostname=self.k8s_host,
                                username=self.ssh_user,
                                key_filename=self.ssh_key_file,
                                timeout=30,
                                look_for_keys=True,
                                allow_agent=True
                            )
                        else:
                            client.connect(
                                hostname=self.k8s_host,
                                username=self.ssh_user,
                                password=self.ssh_password,
                                timeout=30,
                                look_for_keys=False,
                                allow_agent=False
                            )
                    
                    pf_cmd = (
                        f"kubectl port-forward --address 0.0.0.0 -n {self.namespace} "
                        f"svc/{self.service_name} {self.local_port}:{self.remote_port}"
                    )
                    
                    logger.info(f"Starting kubectl port-forward: {pf_cmd}")
                    self.ssh_client = client
                    stdin, stdout, stderr = client.exec_command(pf_cmd)
                    
                    # Wait for port-forward confirmation
                    port_forward_started = False
                    for line in stdout:
                        line_str = line.strip()
                        logger.debug(f"port-forward: {line_str}")
                        
                        # Check for port-forward confirmation message
                        if "Forwarding from" in line_str or "Forwarding" in line_str:
                            port_forward_started = True
                            logger.info(f"✅ Port-forward confirmed: {line_str}")
                        
                        # Keep reading to keep connection alive
                        if not port_forward_started:
                            time.sleep(0.5)  # Give it a moment to start
                    
                    logger.info("Port-forward stopped")
                    
                except Exception as e:
                    logger.error(f"Port-forward thread error: {e}")
            
            # Start port-forward in background thread
            pf_thread = threading.Thread(target=run_port_forward, daemon=True)
            pf_thread.start()
            
            # Wait for port to become available and verify it's actually working
            logger.info("Waiting for port-forward to start...")
            max_wait = 15
            port_open = False
            
            for i in range(max_wait):
                time.sleep(1)
                if self._check_port_open(self.k8s_host, self.local_port):
                    port_open = True
                    logger.debug(f"Port {self.local_port} is open, verifying Focus Server...")
                    # Verify Focus Server is actually responding
                    if self._verify_focus_server_accessible():
                        logger.info(f"✅ SUCCESS: Port-forward active on {self.k8s_host}:{self.local_port} and Focus Server is responding")
                        self.port_forward_active = True
                        return True
                    else:
                        logger.debug(f"Port is open but Focus Server not responding yet... ({i+1}/{max_wait})")
                else:
                    logger.debug(f"Waiting for port... ({i+1}/{max_wait})")
            
            # Provide detailed error message
            if port_open:
                logger.error(f"Port {self.local_port} is open on {self.k8s_host} but Focus Server not responding after {max_wait}s")
                logger.error("This may indicate:")
                logger.error("  - Focus Server pod is not healthy")
                logger.error("  - Service selector mismatch")
                logger.error("  - Wrong port mapping")
            else:
                logger.error(f"Port-forward did not start in time - port {self.local_port} not accessible on {self.k8s_host} after {max_wait}s")
                logger.error("This may indicate:")
                logger.error("  - kubectl port-forward command failed")
                logger.error("  - Network connectivity issues")
                logger.error("  - Port already in use")
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to start port-forward: {e}")
            return False
    
    def stop_port_forward(self):
        """Stop port-forward and cleanup."""
        if self._ssh_manager_ref:
            try:
                logger.info("Stopping port-forward (via SSHManager)...")
                self._ssh_manager_ref.disconnect()
                self._ssh_manager_ref = None
            except Exception as e:
                logger.debug(f"Error disconnecting SSHManager: {e}")
        
        if self.ssh_client:
            try:
                logger.info("Stopping port-forward...")
                self.ssh_client.close()
                self.ssh_client = None
                self.port_forward_active = False
                logger.info("Port-forward stopped")
            except Exception as e:
                logger.error(f"Error stopping port-forward: {e}")
    
    def _verify_focus_server_accessible(self) -> bool:
        """
        Verify Focus Server is actually responding to HTTP requests.

        Returns:
            True if Focus Server is accessible and responding
        """
        try:
            import requests
            url = f"http://{self.k8s_host}:{self.local_port}/health"
            response = requests.get(url, timeout=5)
            logger.debug(f"Focus Server health check: {response.status_code}")
            return response.status_code in [200, 404]  # 404 is ok if /health doesn't exist
        except Exception as e:
            logger.debug(f"Focus Server verification failed: {e}")
            return False

    def setup(self, config_manager=None) -> bool:
        """
        Full automated setup: discover service and start port-forward.

        Args:
            config_manager: Optional ConfigManager instance (for SSHManager support)

        Returns:
            True if setup successful
        """
        logger.info("=" * 80)
        logger.info("FOCUS SERVER AUTO-SETUP")
        logger.info("=" * 80)

        # Check if already accessible and responding
        if self._check_port_open(self.k8s_host, self.local_port):
            logger.debug(f"Port {self.local_port} is open, verifying Focus Server...")
            if self._verify_focus_server_accessible():
                logger.info(f"✅ Focus Server already accessible at {self.k8s_host}:{self.local_port}")
                self.port_forward_active = True
                return True
            else:
                logger.warning(f"Port {self.local_port} is open but Focus Server not responding, will restart port-forward")

        # Discover service
        logger.info("Step 1: Discovering Focus Server service in Kubernetes...")
        service = self.discover_service(config_manager=config_manager)
        if not service:
            logger.error("Failed to discover Focus Server service")
            return False

        self.service_name = service

        # Start port-forward
        logger.info("Step 2: Starting port-forward...")
        success = self.start_port_forward(config_manager=config_manager)

        if success:
            logger.info("=" * 80)
            logger.info("✅ FOCUS SERVER READY!")
            logger.info(f"   Access at: http://{self.k8s_host}:{self.local_port}")
            logger.info(f"   Service: {self.service_name}")
            logger.info(f"   Namespace: {self.namespace}")
            logger.info("=" * 80)
        else:
            logger.error("❌ Focus Server setup FAILED")

        return success
    
    def cleanup(self):
        """Cleanup all resources."""
        logger.info("Cleaning up Focus Server connection...")
        self.stop_port_forward()
        logger.info("Cleanup complete")
    
    def __enter__(self):
        """Context manager entry."""
        self.setup()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()

