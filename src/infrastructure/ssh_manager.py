"""
SSH Manager
===========

SSH infrastructure manager for remote operations and node access.
"""

import logging
import time
from typing import Optional, Dict, Any, List

import paramiko
from paramiko import SSHClient, AutoAddPolicy

from src.core.exceptions import InfrastructureError, NetworkError
from config.config_manager import ConfigManager


class SSHManager:
    """
    SSH infrastructure manager for remote operations.
    
    Provides methods for:
    - SSH connection management
    - Remote command execution
    - File operations
    - Network configuration (iptables)
    - System monitoring
    """
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize SSH manager.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.ssh_config = config_manager.get_ssh_config()
        self.logger = logging.getLogger(__name__)
        
        # SSH client
        self.ssh_client: Optional[SSHClient] = None
        self.connected = False
        
        self.logger.info("SSH manager initialized")
    
    def connect(self) -> bool:
        """
        Connect to the SSH server.
        
        Returns:
            True if connection successful
        """
        try:
            self.logger.debug("Connecting to SSH server...")
            
            # Create SSH client
            self.ssh_client = SSHClient()
            self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())
            
            # Connection parameters
            hostname = self.ssh_config["host"]
            port = self.ssh_config.get("port", 22)
            username = self.ssh_config["username"]
            password = self.ssh_config.get("password")
            key_file = self.ssh_config.get("key_file")
            
            # Connect
            if key_file:
                # Use SSH key authentication
                self.ssh_client.connect(
                    hostname=hostname,
                    port=port,
                    username=username,
                    key_filename=key_file,
                    timeout=10
                )
            elif password:
                # Use password authentication
                self.ssh_client.connect(
                    hostname=hostname,
                    port=port,
                    username=username,
                    password=password,
                    timeout=10
                )
            else:
                raise InfrastructureError("No authentication method configured (password or key_file)")
            
            self.connected = True
            self.logger.info(f"Successfully connected to SSH server {hostname}:{port}")
            return True
            
        except paramiko.AuthenticationException as e:
            self.logger.error(f"SSH authentication failed: {e}")
            return False
        except paramiko.SSHException as e:
            self.logger.error(f"SSH connection failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during SSH connection: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from SSH server."""
        if self.ssh_client and self.connected:
            self.ssh_client.close()
            self.connected = False
            self.logger.info("Disconnected from SSH server")
    
    def execute_command(self, command: str, timeout: int = 60) -> Dict[str, Any]:
        """
        Execute a command on the remote server.
        
        Args:
            command: Command to execute
            timeout: Command timeout in seconds
            
        Returns:
            Dictionary containing command results
            
        Raises:
            InfrastructureError: If command execution fails
        """
        if not self.connected:
            raise InfrastructureError("SSH not connected")
        
        try:
            self.logger.debug(f"Executing command: {command}")
            
            # Execute command
            stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=timeout)
            
            # Wait for command to complete
            exit_code = stdout.channel.recv_exit_status()
            
            # Get output
            stdout_data = stdout.read().decode('utf-8')
            stderr_data = stderr.read().decode('utf-8')
            
            result = {
                "command": command,
                "exit_code": exit_code,
                "stdout": stdout_data,
                "stderr": stderr_data,
                "success": exit_code == 0
            }
            
            if exit_code == 0:
                self.logger.debug(f"Command executed successfully: {command}")
            else:
                self.logger.warning(f"Command failed with exit code {exit_code}: {command}")
                self.logger.warning(f"Stderr: {stderr_data}")
            
            return result
            
        except paramiko.SSHException as e:
            raise InfrastructureError(f"SSH command execution failed: {e}") from e
        except Exception as e:
            raise InfrastructureError(f"Unexpected error during command execution: {e}") from e
    
    def execute_sudo_command(self, command: str, timeout: int = 60) -> Dict[str, Any]:
        """
        Execute a sudo command on the remote server.
        
        Args:
            command: Sudo command to execute
            timeout: Command timeout in seconds
            
        Returns:
            Dictionary containing command results
        """
        sudo_command = f"sudo {command}"
        return self.execute_command(sudo_command, timeout)
    
    def block_port_with_iptables(self, port: int, protocol: str = "tcp") -> bool:
        """
        Block a port using iptables.
        
        Args:
            port: Port number to block
            protocol: Protocol (tcp, udp)
            
        Returns:
            True if blocking was successful
        """
        try:
            self.logger.info(f"Blocking port {port}/{protocol} using iptables...")
            
            command = f"iptables -A INPUT -p {protocol} --dport {port} -j DROP"
            result = self.execute_sudo_command(command)
            
            if result["success"]:
                self.logger.info(f"Successfully blocked port {port}/{protocol}")
                return True
            else:
                self.logger.error(f"Failed to block port {port}/{protocol}: {result['stderr']}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error blocking port {port}/{protocol}: {e}")
            return False
    
    def unblock_port_with_iptables(self, port: int, protocol: str = "tcp") -> bool:
        """
        Unblock a port using iptables.
        
        Args:
            port: Port number to unblock
            protocol: Protocol (tcp, udp)
            
        Returns:
            True if unblocking was successful
        """
        try:
            self.logger.info(f"Unblocking port {port}/{protocol} using iptables...")
            
            command = f"iptables -D INPUT -p {protocol} --dport {port} -j DROP"
            result = self.execute_sudo_command(command)
            
            if result["success"]:
                self.logger.info(f"Successfully unblocked port {port}/{protocol}")
                return True
            else:
                self.logger.error(f"Failed to unblock port {port}/{protocol}: {result['stderr']}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error unblocking port {port}/{protocol}: {e}")
            return False
    
    def get_iptables_rules(self) -> List[str]:
        """
        Get current iptables rules.
        
        Returns:
            List of iptables rules
        """
        try:
            self.logger.debug("Getting iptables rules...")
            
            result = self.execute_sudo_command("iptables -L -n")
            
            if result["success"]:
                rules = result["stdout"].strip().split('\n')
                self.logger.debug(f"Retrieved {len(rules)} iptables rules")
                return rules
            else:
                self.logger.error(f"Failed to get iptables rules: {result['stderr']}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting iptables rules: {e}")
            return []
    
    def check_port_status(self, port: int, protocol: str = "tcp") -> bool:
        """
        Check if a port is open/listening.
        
        Args:
            port: Port number to check
            protocol: Protocol (tcp, udp)
            
        Returns:
            True if port is open
        """
        try:
            self.logger.debug(f"Checking if port {port}/{protocol} is open...")
            
            # Use netstat to check port status
            command = f"netstat -tuln | grep ':{port} '"
            result = self.execute_command(command)
            
            if result["success"] and result["stdout"]:
                self.logger.debug(f"Port {port}/{protocol} is open")
                return True
            else:
                self.logger.debug(f"Port {port}/{protocol} is not open")
                return False
                
        except Exception as e:
            self.logger.error(f"Error checking port {port}/{protocol}: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information from the remote server.
        
        Returns:
            Dictionary containing system information
        """
        try:
            self.logger.debug("Getting system information...")
            
            system_info = {}
            
            # Get OS information
            result = self.execute_command("uname -a")
            if result["success"]:
                system_info["os"] = result["stdout"].strip()
            
            # Get memory information
            result = self.execute_command("free -h")
            if result["success"]:
                system_info["memory"] = result["stdout"].strip()
            
            # Get disk information
            result = self.execute_command("df -h")
            if result["success"]:
                system_info["disk"] = result["stdout"].strip()
            
            # Get CPU information
            result = self.execute_command("cat /proc/cpuinfo | grep 'model name' | head -1")
            if result["success"]:
                system_info["cpu"] = result["stdout"].strip()
            
            # Get load average
            result = self.execute_command("uptime")
            if result["success"]:
                system_info["uptime"] = result["stdout"].strip()
            
            self.logger.debug("System information retrieved successfully")
            return system_info
            
        except Exception as e:
            self.logger.error(f"Error getting system information: {e}")
            return {}
    
    def get_network_interfaces(self) -> List[Dict[str, str]]:
        """
        Get network interface information.
        
        Returns:
            List of network interface dictionaries
        """
        try:
            self.logger.debug("Getting network interface information...")
            
            result = self.execute_command("ip addr show")
            
            if result["success"]:
                interfaces = []
                lines = result["stdout"].split('\n')
                
                current_interface = None
                for line in lines:
                    if line.startswith(' '):
                        # Interface details
                        if 'inet ' in line:
                            parts = line.strip().split()
                            if len(parts) >= 2:
                                ip_address = parts[1].split('/')[0]
                                if current_interface:
                                    current_interface["ip"] = ip_address
                    else:
                        # New interface
                        if current_interface:
                            interfaces.append(current_interface)
                        
                        parts = line.split(':')
                        if len(parts) >= 2:
                            current_interface = {
                                "name": parts[1].strip(),
                                "index": parts[0].strip(),
                                "ip": None
                            }
                
                # Add the last interface
                if current_interface:
                    interfaces.append(current_interface)
                
                self.logger.debug(f"Retrieved {len(interfaces)} network interfaces")
                return interfaces
            else:
                self.logger.error(f"Failed to get network interfaces: {result['stderr']}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting network interfaces: {e}")
            return []
    
    def test_connectivity(self, host: str, port: int, timeout: int = 5) -> bool:
        """
        Test network connectivity to a host and port.
        
        Args:
            host: Target host
            port: Target port
            timeout: Connection timeout in seconds
            
        Returns:
            True if connectivity test successful
        """
        try:
            self.logger.debug(f"Testing connectivity to {host}:{port}...")
            
            command = f"timeout {timeout} bash -c '</dev/tcp/{host}/{port}'"
            result = self.execute_command(command)
            
            if result["success"]:
                self.logger.debug(f"Connectivity test to {host}:{port} successful")
                return True
            else:
                self.logger.debug(f"Connectivity test to {host}:{port} failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Error testing connectivity to {host}:{port}: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
