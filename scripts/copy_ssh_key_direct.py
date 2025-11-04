#!/usr/bin/env python3
"""
Copy SSH Public Key to Target Host via Jump Host
Using paramiko for direct SSH connections
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import paramiko
from paramiko import SSHClient, AutoAddPolicy

# Configuration
JUMP_HOST = "10.10.10.10"
JUMP_USER = "root"
JUMP_PASSWORD = "PASSW0RD"
TARGET_HOST = "10.10.10.150"
TARGET_USER = "prisma"

# SSH key path
SSH_KEY_PATH = Path.home() / ".ssh" / "panda_staging_key.pub"

def main():
    print("\n" + "=" * 80)
    print("Copying SSH Key to Target Host via Jump Host")
    print("=" * 80)
    
    # Step 1: Read public key
    if not SSH_KEY_PATH.exists():
        print(f"[ERROR] Public key not found: {SSH_KEY_PATH}")
        return 1
    
    public_key = SSH_KEY_PATH.read_text().strip()
    
    print(f"\n[INFO] Public key:")
    print(f"  {public_key[:50]}...")
    
    # Step 2: Connect to jump host
    print(f"\n[INFO] Step 1: Connecting to jump host {JUMP_USER}@{JUMP_HOST}...")
    
    jump_client = SSHClient()
    jump_client.set_missing_host_key_policy(AutoAddPolicy())
    
    try:
        jump_client.connect(
            hostname=JUMP_HOST,
            username=JUMP_USER,
            password=JUMP_PASSWORD,
            timeout=10,
            look_for_keys=False,
            allow_agent=False
        )
        print(f"[OK] Connected to jump host")
        
        # Step 3: Save key temporarily on jump host
        temp_key_file = "/tmp/panda_staging_key.pub"
        print(f"[INFO] Step 2: Saving key to jump host: {temp_key_file}")
        
        stdin, stdout, stderr = jump_client.exec_command(
            f"echo '{public_key}' > {temp_key_file} && chmod 600 {temp_key_file}"
        )
        exit_code = stdout.channel.recv_exit_status()
        
        if exit_code != 0:
            error = stderr.read().decode()
            print(f"[ERROR] Failed to save key on jump host: {error}")
            return 1
        
        print(f"[OK] Key saved on jump host")
        
        # Step 4: Copy key from jump host to target host
        print(f"\n[INFO] Step 3: Copying key to target host {TARGET_USER}@{TARGET_HOST}...")
        
        # Create transport channel through jump host to target host
        jump_transport = jump_client.get_transport()
        dest_addr = (TARGET_HOST, 22)
        local_addr = ('127.0.0.1', 0)
        
        print(f"[INFO] Opening SSH tunnel through jump host...")
        channel = jump_transport.open_channel("direct-tcpip", dest_addr, local_addr)
        
        # Step 5: Connect to target host and copy key
        # We'll do this via a command executed on jump host that connects to target
        print(f"[INFO] Executing copy command through jump host...")
        
        # Command to copy key to target host
        copy_command = f"""ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 {TARGET_USER}@{TARGET_HOST} 'mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys' < {temp_key_file}"""
        
        stdin, stdout, stderr = jump_client.exec_command(copy_command, timeout=30)
        exit_code = stdout.channel.recv_exit_status()
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        if exit_code == 0:
            print(f"[OK] Key copied to target host successfully!")
            if output:
                print(f"  Output: {output.strip()}")
        else:
            print(f"[WARNING] Copy command returned exit code {exit_code}")
            if error:
                print(f"  Error: {error.strip()}")
            
            # Try alternative: Direct connection attempt
            print(f"\n[INFO] Trying alternative method...")
            print(f"[INFO] The target host may require the key to be manually added.")
            print(f"[INFO] Please run these commands manually:")
            print(f"\n  1. ssh {JUMP_USER}@{JUMP_HOST}")
            print(f"     Password: {JUMP_PASSWORD}")
            print(f"\n  2. ssh {TARGET_USER}@{TARGET_HOST}")
            print(f"\n  3. On target host, run:")
            print(f"     mkdir -p ~/.ssh")
            print(f"     chmod 700 ~/.ssh")
            print(f"     echo '{public_key}' >> ~/.ssh/authorized_keys")
            print(f"     chmod 600 ~/.ssh/authorized_keys")
            print(f"\n  4. Exit and test:")
            print(f"     ssh -i {SSH_KEY_PATH.parent / 'panda_staging_key'} -o ProxyJump={JUMP_USER}@{JUMP_HOST} {TARGET_USER}@{TARGET_HOST} 'hostname'")
            
            return 1
        
        # Step 6: Cleanup
        print(f"\n[INFO] Cleaning up temporary file...")
        jump_client.exec_command(f"rm -f {temp_key_file}")
        print(f"[OK] Temporary file removed")
        
        # Step 7: Test connection
        print(f"\n[INFO] Step 4: Testing connection...")
        print(f"[INFO] Connection test will be done by test_ssh_connection.py")
        
        print(f"\n" + "=" * 80)
        print("[SUCCESS] SSH key copied successfully!")
        print("=" * 80)
        
        return 0
        
    except paramiko.AuthenticationException as e:
        print(f"[ERROR] Authentication failed: {e}")
        return 1
    except paramiko.SSHException as e:
        print(f"[ERROR] SSH error: {e}")
        return 1
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        jump_client.close()
        print(f"[OK] Disconnected from jump host")

if __name__ == "__main__":
    sys.exit(main())

