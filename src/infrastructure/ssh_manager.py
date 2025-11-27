"""
SSH Manager
===========

SSH infrastructure manager for remote operations and node access.
"""

import logging
import time
import os
import sys
from pathlib import Path
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
    
    @staticmethod
    def _expand_path(path: str) -> str:
        """
        Expand tilde (~) in path to actual home directory.
        Works on both Windows and Unix-like systems.
        
        On Windows, when running as a service, Path.home() may return the system profile.
        This method uses USERPROFILE environment variable on Windows to get the correct user profile.
        If USERPROFILE is not set or points to system profile, uses USERNAME to build the path.
        
        Args:
            path: Path string that may contain ~
        
        Returns:
            Expanded path string
        """
        if path and path.startswith('~'):
            # On Windows, prefer USERPROFILE env var (works correctly for services)
            # On Unix-like systems, use Path.home()
            if sys.platform == 'win32':
                userprofile = os.environ.get('USERPROFILE')
                # Check if USERPROFILE is system profile (indicates service context)
                if userprofile and 'system32\\config\\systemprofile' not in userprofile.lower():
                    home = userprofile
                else:
                    # Fallback: use USERNAME to build path
                    username = os.environ.get('USERNAME')
                    if username:
                        home = f"C:\\Users\\{username}"
                    else:
                        # Last resort: use Path.home()
                        home = str(Path.home())
            else:
                home = str(Path.home())
            path = path.replace('~', home, 1)
        return path
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize SSH manager.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.ssh_config = config_manager.get_ssh_config()
        self.logger = logging.getLogger(__name__)
        
        # SSH clients (for jump host support)
        self.ssh_client: Optional[SSHClient] = None
        self.jump_ssh_client: Optional[SSHClient] = None  # For jump host connection
        self.connected = False
        self.use_jump_host = False
        
        self.logger.info("SSH manager initialized")
    
    def connect(self) -> bool:
        """
        Connect to the SSH server.
        
        Supports both direct connection and jump host connection.
        If jump_host is configured, connects through jump host to target host.
        
        Returns:
            True if connection successful
        """
        try:
            self.logger.debug("Connecting to SSH server...")
            
            # Check if jump host is configured
            jump_host_config = self.ssh_config.get("jump_host")
            target_host_config = self.ssh_config.get("target_host")
            
            if jump_host_config and target_host_config:
                # Use jump host connection
                return self._connect_via_jump_host(jump_host_config, target_host_config)
            elif "host" in self.ssh_config:
                # Direct connection (legacy format)
                return self._connect_direct()
            elif target_host_config:
                # Target host only (no jump host)
                return self._connect_direct(target_host_config)
            else:
                raise InfrastructureError("No valid SSH configuration found (host or target_host required)")
            
        except paramiko.AuthenticationException as e:
            self.logger.error(f"SSH authentication failed: {e}")
            return False
        except paramiko.SSHException as e:
            self.logger.error(f"SSH connection failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during SSH connection: {e}")
            return False
    
    def _connect_direct(self, host_config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Connect directly to SSH server (without jump host).
        
        Args:
            host_config: Optional host configuration dict. If None, uses self.ssh_config.
        
        Returns:
            True if connection successful
        """
        config = host_config or self.ssh_config
        
        # Create SSH client
        self.ssh_client = SSHClient()
        self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        
        # Connection parameters
        hostname = config["host"]
        port = config.get("port", 22)
        username = config["username"]
        password = config.get("password")
        key_file = config.get("key_file")
        
        # Expand tilde in key_file path
        if key_file:
            key_file = self._expand_path(key_file)
        
        # Connect
        if key_file:
            # Use SSH key authentication
            self.ssh_client.connect(
                hostname=hostname,
                port=port,
                username=username,
                key_filename=key_file,
                timeout=10,
                allow_agent=False,  # Don't try agent when we have key file
                look_for_keys=False  # Don't look for other keys
            )
        elif password:
            # Use password authentication
            self.ssh_client.connect(
                hostname=hostname,
                port=port,
                username=username,
                password=password,
                timeout=10,
                allow_agent=False,  # Don't try agent with password
                look_for_keys=False  # Don't look for keys with password
            )
        else:
            raise InfrastructureError("No authentication method configured (password or key_file)")
        
        self.connected = True
        self.use_jump_host = False
        self.logger.info(f"Successfully connected to SSH server {hostname}:{port}")
        return True
    
    def _connect_via_jump_host(self, jump_host_config: Dict[str, Any], target_host_config: Dict[str, Any]) -> bool:
        """
        Connect to target host through jump host.
        
        Args:
            jump_host_config: Jump host configuration dictionary
            target_host_config: Target host configuration dictionary
        
        Returns:
            True if connection successful
        """
        self.logger.debug("Connecting via jump host...")
        
        # Step 1: Connect to jump host
        jump_hostname = jump_host_config["host"]
        jump_port = jump_host_config.get("port", 22)
        jump_username = jump_host_config["username"]
        jump_password = jump_host_config.get("password")
        jump_key_file = jump_host_config.get("key_file")
        
        self.logger.debug(f"Connecting to jump host {jump_username}@{jump_hostname}:{jump_port}...")
        
        self.jump_ssh_client = SSHClient()
        self.jump_ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        
        if jump_key_file:
            # Expand tilde in key_file path
            jump_key_file = self._expand_path(jump_key_file)
            self.jump_ssh_client.connect(
                hostname=jump_hostname,
                port=jump_port,
                username=jump_username,
                key_filename=jump_key_file,
                timeout=10,
                allow_agent=False,  # Don't try agent when we have key file
                look_for_keys=False  # Don't look for other keys
            )
        elif jump_password:
            self.jump_ssh_client.connect(
                hostname=jump_hostname,
                port=jump_port,
                username=jump_username,
                password=jump_password,
                timeout=10,
                allow_agent=False,  # Don't try agent with password
                look_for_keys=False  # Don't look for keys with password
            )
        else:
            raise InfrastructureError("No authentication method configured for jump host")
        
        self.logger.info(f"Connected to jump host {jump_hostname}:{jump_port}")
        
        # Step 2: Create transport channel through jump host to target host
        target_hostname = target_host_config["host"]
        target_port = target_host_config.get("port", 22)
        target_username = target_host_config["username"]
        target_password = target_host_config.get("password")
        target_key_file = target_host_config.get("key_file")
        
        self.logger.debug(f"Creating SSH tunnel to target host {target_username}@{target_hostname}:{target_port}...")
        
        # Create transport channel through jump host
        jump_transport = self.jump_ssh_client.get_transport()
        dest_addr = (target_hostname, target_port)
        local_addr = ('127.0.0.1', 0)
        channel = jump_transport.open_channel("direct-tcpip", dest_addr, local_addr)
        
        # Step 3: Connect to target host through the channel
        self.ssh_client = SSHClient()
        self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        
        # Try authentication methods in order of preference
        # 1. SSH key file (if configured) - try this first without agent/look_for_keys
        if target_key_file:
            try:
                # Expand tilde in key_file path
                target_key_file = self._expand_path(target_key_file)
                self.ssh_client.connect(
                    hostname=target_hostname,
                    username=target_username,
                    key_filename=target_key_file,
                    sock=channel,
                    timeout=10,
                    allow_agent=False,  # Don't try agent when we have key file
                    look_for_keys=False  # Don't look for other keys
                )
                self.logger.debug("Connected to target host using SSH key file")
                self.connected = True
                self.use_jump_host = True
                self.logger.info(f"Successfully connected to target host {target_hostname}:{target_port} via jump host {jump_hostname}")
                return True
            except paramiko.AuthenticationException:
                self.logger.debug("SSH key file authentication failed, trying SSH agent...")
                # Create new client for next attempt
                self.ssh_client.close()
                self.ssh_client = SSHClient()
                self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        
        # 2. SSH Agent (forwarded from jump host or local) - only if no key_file or key_file failed
        try:
            self.ssh_client.connect(
                hostname=target_hostname,
                username=target_username,
                sock=channel,
                timeout=10,
                allow_agent=True,  # Use SSH agent
                look_for_keys=True  # Look for keys in default locations
            )
            self.logger.debug("Connected to target host using SSH agent/key")
            self.connected = True
            self.use_jump_host = True
            self.logger.info(f"Successfully connected to target host {target_hostname}:{target_port} via jump host {jump_hostname} using SSH key")
            return True
        except paramiko.AuthenticationException:
            self.logger.debug("SSH agent/key authentication failed, trying password...")
            # Create new client for next attempt
            self.ssh_client.close()
            self.ssh_client = SSHClient()
            self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        
        # 3. Password authentication (last resort, if allowed by server)
        if target_password:
            try:
                self.ssh_client.connect(
                    hostname=target_hostname,
                    username=target_username,
                    password=target_password,
                    sock=channel,
                    timeout=10,
                    allow_agent=False,
                    look_for_keys=False
                )
                self.logger.debug("Connected to target host using password")
                self.connected = True
                self.use_jump_host = True
                self.logger.info(f"Successfully connected to target host {target_hostname}:{target_port} via jump host {jump_hostname} using password")
                return True
            except paramiko.AuthenticationException as e:
                self.logger.error(f"Password authentication also failed: {e}")
                raise InfrastructureError(f"Failed to authenticate to target host {target_hostname}. "
                                       f"Server requires SSH key authentication. Please configure key_file "
                                       f"or set up SSH agent with appropriate key.")
        
        # If we get here, all authentication methods failed
        raise InfrastructureError(f"No authentication method succeeded for target host {target_hostname}. "
                               f"Server requires SSH key authentication. Please configure key_file "
                               f"or set up SSH agent with appropriate key.")
    
    def disconnect(self):
        """Disconnect from SSH server."""
        if self.ssh_client and self.connected:
            self.ssh_client.close()
            self.ssh_client = None
            
        if self.jump_ssh_client:
            self.jump_ssh_client.close()
            self.jump_ssh_client = None
        
        if self.connected:
            self.connected = False
            self.use_jump_host = False
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
