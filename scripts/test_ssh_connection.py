#!/usr/bin/env python3
"""Test SSH connection to jump host and target host."""

import paramiko
import socket
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager

def test_direct_ssh(host: str, port: int, username: str, password: str) -> bool:
    """Test direct SSH connection."""
    print(f"\n[TEST] Direct SSH to {username}@{host}:{port}")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            timeout=10,
            allow_agent=False,
            look_for_keys=False
        )
        
        # Execute test command
        stdin, stdout, stderr = ssh.exec_command("hostname")
        hostname = stdout.read().decode().strip()
        
        print(f"[OK] Connected successfully! Hostname: {hostname}")
        
        # Get system info
        stdin, stdout, stderr = ssh.exec_command("uname -a")
        system_info = stdout.read().decode().strip()
        print(f"System: {system_info}")
        
        ssh.close()
        return True
        
    except paramiko.AuthenticationException as e:
        print(f"[ERROR] Authentication failed: {e}")
        return False
    except paramiko.SSHException as e:
        print(f"[ERROR] SSH error: {e}")
        return False
    except socket.timeout:
        print(f"[ERROR] Connection timeout")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

def test_jump_connection(env: str = "staging") -> bool:
    """Test SSH connection through jump host using ConfigManager."""
    print("\n" + "=" * 80)
    print(f"Testing SSH Jump Host Connection (Environment: {env})")
    print("=" * 80)
    
    # Load configuration
    config_manager = ConfigManager(env=env)
    ssh_config = config_manager.get_ssh_config()
    
    # Extract jump host and target host configs
    jump_host_config = ssh_config.get("jump_host", {})
    target_host_config = ssh_config.get("target_host", {})
    
    if not jump_host_config or not target_host_config:
        print("[ERROR] Jump host or target host not configured in environments.yaml")
        print(f"SSH Config: {ssh_config}")
        return False
    
    # Jump host configuration
    jump_host = {
        "host": jump_host_config["host"],
        "port": jump_host_config.get("port", 22),
        "username": jump_host_config["username"],
        "password": jump_host_config.get("password", "PASSW0RD")
    }
    
    # Target host configuration
    target_host = {
        "host": target_host_config["host"],
        "port": target_host_config.get("port", 22),
        "username": target_host_config["username"],
        "password": target_host_config.get("password", "PASSW0RD")
    }
    
    print(f"\nJump Host: {jump_host['username']}@{jump_host['host']}:{jump_host['port']}")
    print(f"Target Host: {target_host['username']}@{target_host['host']}:{target_host['port']}")
    
    # Test jump host connection
    print("\nStep 1: Testing jump host connection")
    if not test_direct_ssh(**jump_host):
        return False
    
    print("\nStep 2: Testing connection through jump host to target")
    try:
        # Connect to jump host
        jump_ssh = paramiko.SSHClient()
        jump_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        jump_ssh.connect(
            hostname=jump_host["host"],
            port=jump_host["port"],
            username=jump_host["username"],
            password=jump_host["password"],
            timeout=10,
            allow_agent=False,
            look_for_keys=False
        )
        
        print(f"[OK] Connected to jump host {jump_host['host']}")
        
        # Create transport channel through jump host
        jump_transport = jump_ssh.get_transport()
        dest_addr = (target_host["host"], target_host["port"])
        local_addr = ('127.0.0.1', 0)
        channel = jump_transport.open_channel("direct-tcpip", dest_addr, local_addr)
        
        # Connect to target host through the channel
        target_ssh = paramiko.SSHClient()
        target_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Try SSH key first, then password
        target_key_file = target_host_config.get("key_file")
        
        try:
            if target_key_file:
                # Expand tilde in path
                if target_key_file.startswith('~'):
                    from pathlib import Path
                    home = str(Path.home())
                    target_key_file = target_key_file.replace('~', home, 1)
                
                target_ssh.connect(
                    hostname=target_host["host"],
                    username=target_host["username"],
                    key_filename=target_key_file,
                    sock=channel,
                    timeout=10,
                    allow_agent=True,
                    look_for_keys=True
                )
            else:
                # Try password as fallback
                target_ssh.connect(
                    hostname=target_host["host"],
                    username=target_host["username"],
                    password=target_host["password"],
                    sock=channel,
                    timeout=10,
                    allow_agent=True,
                    look_for_keys=True
                )
        except paramiko.AuthenticationException as e:
            if target_key_file:
                print(f"[ERROR] SSH key authentication failed: {e}")
                print(f"[INFO] Key file: {target_key_file}")
                print(f"[INFO] Trying password authentication...")
                # Try password as fallback
                try:
                    target_ssh.connect(
                        hostname=target_host["host"],
                        username=target_host["username"],
                        password=target_host["password"],
                        sock=channel,
                        timeout=10,
                        allow_agent=False,
                        look_for_keys=False
                    )
                except paramiko.AuthenticationException as e2:
                    raise paramiko.AuthenticationException(f"Both key and password authentication failed. Key: {e}, Password: {e2}")
            else:
                raise
        
        print(f"[OK] Connected to target host {target_host['host']} through jump host")
        
        # Execute test command on target
        stdin, stdout, stderr = target_ssh.exec_command("hostname")
        hostname = stdout.read().decode().strip()
        print(f"Target hostname: {hostname}")
        
        # Check for k9s
        stdin, stdout, stderr = target_ssh.exec_command("which k9s")
        k9s_path = stdout.read().decode().strip()
        if k9s_path:
            print(f"[OK] k9s found at: {k9s_path}")
        else:
            print("[WARNING] k9s not found on target host")
        
        # Check for kubectl
        stdin, stdout, stderr = target_ssh.exec_command("which kubectl")
        kubectl_path = stdout.read().decode().strip()
        if kubectl_path:
            print(f"[OK] kubectl found at: {kubectl_path}")
        else:
            print("[WARNING] kubectl not found on target host")
        
        # Close connections
        target_ssh.close()
        jump_ssh.close()
        
        print("\n[SUCCESS] SSH jump connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to connect through jump host: {e}")
        return False

def test_network_connectivity(env: str = "staging"):
    """Test basic network connectivity to SSH hosts."""
    print("\n" + "=" * 80)
    print(f"Testing Network Connectivity (Environment: {env})")
    print("=" * 80)
    
    # Load configuration
    config_manager = ConfigManager(env=env)
    ssh_config = config_manager.get_ssh_config()
    
    jump_host_config = ssh_config.get("jump_host", {})
    target_host_config = ssh_config.get("target_host", {})
    
    hosts = []
    if jump_host_config:
        hosts.append((jump_host_config["host"], jump_host_config.get("port", 22), "Jump host"))
    if target_host_config:
        hosts.append((target_host_config["host"], target_host_config.get("port", 22), "Target host"))
    
    for host, port, name in hosts:
        print(f"\nTesting {name} ({host}:{port})")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        
        try:
            result = sock.connect_ex((host, port))
            if result == 0:
                print(f"[OK] Port {port} is open on {host}")
            else:
                print(f"[ERROR] Cannot connect to {host}:{port} - Error code: {result}")
        except socket.error as e:
            print(f"[ERROR] Socket error: {e}")
        finally:
            sock.close()

def test_ssh_manager_connection(env: str = "staging") -> bool:
    """Test SSH connection using SSHManager class."""
    print("\n" + "=" * 80)
    print(f"Testing SSHManager Jump Host Connection (Environment: {env})")
    print("=" * 80)
    
    try:
        # Load configuration
        config_manager = ConfigManager(env=env)
        ssh_manager = SSHManager(config_manager)
        
        # Connect
        print("\nConnecting via SSHManager...")
        if ssh_manager.connect():
            print("[OK] SSHManager connected successfully!")
            
            # Test command execution
            print("\nTesting command execution...")
            result = ssh_manager.execute_command("hostname")
            if result["success"]:
                hostname = result["stdout"].strip()
                print(f"[OK] Command executed successfully! Hostname: {hostname}")
                
                # Check for k9s
                result = ssh_manager.execute_command("which k9s")
                if result["success"] and result["stdout"].strip():
                    k9s_path = result["stdout"].strip()
                    print(f"[OK] k9s found at: {k9s_path}")
                else:
                    print("[WARNING] k9s not found on target host")
                
                # Check for kubectl
                result = ssh_manager.execute_command("which kubectl")
                if result["success"] and result["stdout"].strip():
                    kubectl_path = result["stdout"].strip()
                    print(f"[OK] kubectl found at: {kubectl_path}")
                else:
                    print("[WARNING] kubectl not found on target host")
                
                # Disconnect
                ssh_manager.disconnect()
                print("\n[SUCCESS] SSHManager test completed successfully!")
                return True
            else:
                print(f"[ERROR] Command execution failed: {result['stderr']}")
                return False
        else:
            print("[ERROR] SSHManager connection failed")
            return False
            
    except Exception as e:
        print(f"[ERROR] SSHManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test SSH connection via jump host")
    parser.add_argument("--env", default="staging", choices=["staging", "production", "local"],
                        help="Environment to test (default: staging)")
    args = parser.parse_args()
    
    # Test network connectivity first
    print("\n" + "=" * 80)
    print("Step 1: Network Connectivity Test")
    print("=" * 80)
    test_network_connectivity()
    
    # Test SSH connections using paramiko directly
    print("\n" + "=" * 80)
    print("Step 2: Direct SSH Connection Test (paramiko)")
    print("=" * 80)
    success1 = test_jump_connection(env=args.env)
    
    # Test SSH connections using SSHManager
    print("\n" + "=" * 80)
    print("Step 3: SSHManager Connection Test")
    print("=" * 80)
    success2 = test_ssh_manager_connection(env=args.env)
    
    if success1 and success2:
        print("\n" + "=" * 80)
        print("[SUCCESS] All SSH tests passed!")
        print("=" * 80)
        sys.exit(0)
    else:
        print("\n" + "=" * 80)
        print("[FAILURE] Some SSH tests failed!")
        print("=" * 80)
        sys.exit(1)
