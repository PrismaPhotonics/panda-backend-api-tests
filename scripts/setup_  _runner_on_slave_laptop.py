#!/usr/bin/env python3
"""
Setup GitHub Actions Runner on Slave Laptop (10.50.0.36)
=========================================================
This script connects to the slave laptop and sets up a self-hosted runner
for the panda-backend-api-tests repository.
"""

import sys
import os
import getpass
from pathlib import Path
from typing import Optional

try:
    import paramiko
except ImportError:
    print("❌ paramiko is required. Install with: pip install paramiko")
    sys.exit(1)


def detect_os(ssh_client: paramiko.SSHClient) -> str:
    """Detect operating system on remote machine."""
    try:
        stdin, stdout, stderr = ssh_client.exec_command("uname -a")
        output = stdout.read().decode().strip()
        if "Linux" in output:
            return "linux"
        elif "Windows" in output or "MINGW" in output or "MSYS" in output:
            return "windows"
        
        # Try PowerShell detection
        stdin, stdout, stderr = ssh_client.exec_command("powershell -Command 'if (Test-Path C:\\Windows) { Write-Output Windows }'")
        output = stdout.read().decode().strip()
        if "Windows" in output:
            return "windows"
        
        return "unknown"
    except Exception as e:
        print(f"⚠️  Could not detect OS: {e}")
        return "unknown"


def execute_command(ssh_client: paramiko.SSHClient, command: str, sudo: bool = False) -> tuple[int, str, str]:
    """Execute command on remote machine."""
    try:
        if sudo:
            command = f"sudo {command}"
        
        stdin, stdout, stderr = ssh_client.exec_command(command, timeout=300)
        exit_code = stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8', errors='ignore')
        errors = stderr.read().decode('utf-8', errors='ignore')
        
        return exit_code, output, errors
    except Exception as e:
        return 1, "", str(e)


def setup_windows_runner(
    ssh_client: paramiko.SSHClient,
    repo_url: str,
    runner_name: str,
    install_path: str,
    token: str
) -> bool:
    """Setup GitHub Actions runner on Windows."""
    print(f"Setting up Windows runner in {install_path}...")
    
    commands = [
        f"New-Item -ItemType Directory -Path '{install_path}' -Force",
        f"Set-Location '{install_path}'",
        f"Invoke-WebRequest -Uri 'https://github.com/actions/runner/releases/latest/download/actions-runner-win-x64-2.311.0.zip' -OutFile 'actions-runner.zip'",
        "Expand-Archive -Path 'actions-runner.zip' -DestinationPath . -Force",
        "Remove-Item 'actions-runner.zip'",
        f".\\config.cmd --url '{repo_url}' --token '{token}' --name '{runner_name}' --labels 'self-hosted,Windows,slave-laptop' --work '_work' --replace",
        ".\\svc.cmd install",
        ".\\svc.cmd start"
    ]
    
    for cmd in commands:
        print(f"  Executing: {cmd}")
        exit_code, output, errors = execute_command(ssh_client, cmd)
        
        if exit_code != 0:
            print(f"❌ Command failed with exit code {exit_code}")
            if errors:
                print(f"Errors: {errors}")
            if output:
                print(f"Output: {output}")
            return False
        
        if output:
            print(f"  {output.strip()}")
    
    return True


def setup_linux_runner(
    ssh_client: paramiko.SSHClient,
    repo_url: str,
    runner_name: str,
    install_path: str,
    token: str
) -> bool:
    """Setup GitHub Actions runner on Linux."""
    print(f"Setting up Linux runner in {install_path}...")
    
    commands = [
        f"sudo mkdir -p {install_path}",
        f"cd {install_path}",
        "curl -L -o actions-runner.tar.gz 'https://github.com/actions/runner/releases/latest/download/actions-runner-linux-x64-2.311.0.tar.gz'",
        "tar xzf actions-runner.tar.gz",
        "rm actions-runner.tar.gz",
        f"sudo ./config.sh --url '{repo_url}' --token '{token}' --name '{runner_name}' --labels 'self-hosted,Linux,slave-laptop' --work '_work' --replace",
        "sudo ./svc.sh install",
        "sudo ./svc.sh start"
    ]
    
    for cmd in commands:
        print(f"  Executing: {cmd}")
        exit_code, output, errors = execute_command(ssh_client, cmd, sudo=cmd.startswith("sudo"))
        
        if exit_code != 0:
            print(f"❌ Command failed with exit code {exit_code}")
            if errors:
                print(f"Errors: {errors}")
            if output:
                print(f"Output: {output}")
            return False
        
        if output:
            print(f"  {output.strip()}")
    
    return True


def main():
    """Main function."""
    print("=" * 60)
    print("GitHub Actions Runner Setup on Slave Laptop")
    print("=" * 60)
    print()
    
    # Configuration
    slave_ip = "10.50.0.36"
    repo_url = "https://github.com/PrismaPhotonics/panda-backend-api-tests"
    runner_name = "slave-laptop-runner"
    
    # Get SSH credentials
    print(f"Connecting to {slave_ip}...")
    ssh_user = input("SSH username: ").strip()
    
    auth_method = input("Authentication method: (1) Password (2) SSH Key [1]: ").strip() or "1"
    
    ssh_password = None
    ssh_key_file = None
    
    if auth_method == "2":
        key_path = input("SSH key file path: ").strip()
        ssh_key_file = Path(key_path).expanduser()
        if not ssh_key_file.exists():
            print(f"❌ Key file not found: {ssh_key_file}")
            sys.exit(1)
    else:
        ssh_password = getpass.getpass("SSH password: ")
    
    # Connect via SSH
    print()
    print("Connecting via SSH...")
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        if ssh_key_file:
            ssh_client.connect(
                hostname=slave_ip,
                username=ssh_user,
                key_filename=str(ssh_key_file),
                timeout=30
            )
        else:
            ssh_client.connect(
                hostname=slave_ip,
                username=ssh_user,
                password=ssh_password,
                timeout=30
            )
        
        print("✅ SSH connection established")
        
        # Detect OS
        print()
        print("Detecting operating system...")
        os_type = detect_os(ssh_client)
        
        if os_type == "unknown":
            print("⚠️  Could not detect OS. Please specify:")
            os_type = input("OS type (windows/linux): ").strip().lower()
        
        print(f"✅ Detected: {os_type}")
        
        # Get installation path
        if os_type == "windows":
            install_path = input(f"Installation path [C:\\actions-runner]: ").strip() or "C:\\actions-runner"
        else:
            install_path = input(f"Installation path [/opt/actions-runner]: ").strip() or "/opt/actions-runner"
        
        # Get registration token
        print()
        print("=" * 60)
        print("Registration Token Required")
        print("=" * 60)
        print()
        print("To get a registration token:")
        print(f"  1. Go to: {repo_url}/settings/actions/runners/new")
        print(f"  2. Select: {'Windows' if os_type == 'windows' else 'Linux'}")
        print("  3. Copy the registration token")
        print()
        
        token = getpass.getpass("Enter registration token: ").strip()
        
        if not token:
            print("❌ Registration token is required")
            sys.exit(1)
        
        # Setup runner
        print()
        print("=" * 60)
        print("Setting up GitHub Actions Runner")
        print("=" * 60)
        print()
        
        success = False
        if os_type == "windows":
            success = setup_windows_runner(ssh_client, repo_url, runner_name, install_path, token)
        else:
            success = setup_linux_runner(ssh_client, repo_url, runner_name, install_path, token)
        
        if success:
            print()
            print("=" * 60)
            print("✅ Runner Setup Complete!")
            print("=" * 60)
            print()
            print(f"Runner Name: {runner_name}")
            print(f"Installation Path: {install_path}")
            print()
            print("To verify the runner is online:")
            print(f"  Visit: {repo_url}/settings/actions/runners")
            print()
            print("To check status on the slave laptop:")
            if os_type == "windows":
                print(f"  ssh {ssh_user}@{slave_ip}")
                print(f"  cd {install_path}")
                print("  .\\svc.cmd status")
            else:
                print(f"  ssh {ssh_user}@{slave_ip}")
                print(f"  cd {install_path}")
                print("  sudo ./svc.sh status")
        else:
            print()
            print("❌ Setup failed. Please check the errors above.")
            sys.exit(1)
        
    except paramiko.AuthenticationException:
        print("❌ SSH authentication failed")
        sys.exit(1)
    except paramiko.SSHException as e:
        print(f"❌ SSH error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        ssh_client.close()


if __name__ == "__main__":
    main()

