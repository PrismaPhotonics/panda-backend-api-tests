# Copy SSH Public Key to Target Host via Jump Host
# =================================================

param(
    [string]$PublicKeyPath = "$env:USERPROFILE\.ssh\panda_staging_key.pub",
    [string]$JumpHost = "10.10.10.10",
    [string]$JumpUser = "root",
    [string]$JumpPassword = "PASSW0RD",
    [string]$TargetHost = "10.10.10.150",
    [string]$TargetUser = "prisma"
)

$ErrorActionPreference = "Stop"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Copying SSH Key to Target Host" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Step 1: Read public key
if (-not (Test-Path $PublicKeyPath)) {
    Write-Host "[ERROR] Public key not found: $PublicKeyPath" -ForegroundColor Red
    exit 1
}

$publicKey = Get-Content $PublicKeyPath -Raw
$publicKey = $publicKey.Trim()

Write-Host "`n[INFO] Public key:" -ForegroundColor Cyan
Write-Host $publicKey -ForegroundColor Gray

# Step 2: Copy key to target host via jump host using Python
Write-Host "`n[INFO] Copying key to target host via jump host..." -ForegroundColor Cyan
Write-Host "  Jump Host:   $JumpUser@$JumpHost" -ForegroundColor Gray
Write-Host "  Target Host: $TargetUser@$TargetHost" -ForegroundColor Gray

# Create Python script to do the copy using paramiko
$pythonScript = @"
import paramiko
import sys

# Configuration
jump_host = "$JumpHost"
jump_user = "$JumpUser"
jump_password = "$JumpPassword"
target_host = "$TargetHost"
target_user = "$TargetUser"
public_key = """$publicKey"""

try:
    # Step 1: Connect to jump host
    print(f"[INFO] Connecting to jump host {jump_user}@{jump_host}...")
    jump_client = paramiko.SSHClient()
    jump_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    jump_client.connect(
        hostname=jump_host,
        username=jump_user,
        password=jump_password,
        timeout=10,
        look_for_keys=False,
        allow_agent=False
    )
    print(f"[OK] Connected to jump host")

    # Step 2: Save public key temporarily on jump host
    temp_key_file = "/tmp/panda_staging_key.pub"
    print(f"[INFO] Saving key to jump host: {temp_key_file}")
    stdin, stdout, stderr = jump_client.exec_command(f"echo '{public_key}' > {temp_key_file}")
    exit_code = stdout.channel.recv_exit_status()
    if exit_code != 0:
        error = stderr.read().decode()
        print(f"[ERROR] Failed to save key on jump host: {error}")
        sys.exit(1)
    print(f"[OK] Key saved on jump host")

    # Step 3: Copy key from jump host to target host
    print(f"[INFO] Copying key to target host {target_user}@{target_host}...")
    
    # Create transport channel through jump host
    jump_transport = jump_client.get_transport()
    dest_addr = (target_host, 22)
    local_addr = ('127.0.0.1', 0)
    channel = jump_transport.open_channel("direct-tcpip", dest_addr, local_addr)
    
    # Connect to target host
    target_client = paramiko.SSHClient()
    target_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # Try to connect - target host might need key auth, so we'll copy via jump host command
    try:
        # Read the key from temp file on jump host and append to target host
        copy_command = f'''ssh -o StrictHostKeyChecking=no {target_user}@{target_host} "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys" < {temp_key_file}'''
        
        stdin, stdout, stderr = jump_client.exec_command(copy_command)
        exit_code = stdout.channel.recv_exit_status()
        
        if exit_code == 0:
            print(f"[OK] Key copied to target host successfully!")
            
            # Cleanup
            jump_client.exec_command(f"rm -f {temp_key_file}")
            print(f"[OK] Temporary file cleaned up")
        else:
            error = stderr.read().decode()
            print(f"[WARNING] Direct copy failed: {error}")
            print(f"[INFO] Trying alternative method...")
            
            # Alternative: Manual copy instruction
            print(f"\n[INFO] You may need to copy manually:")
            print(f"  1. ssh {jump_user}@{jump_host}")
            print(f"  2. ssh {target_user}@{target_host}")
            print(f"  3. echo '{public_key}' >> ~/.ssh/authorized_keys")
            print(f"  4. chmod 600 ~/.ssh/authorized_keys")
            
            sys.exit(1)
            
    except Exception as e:
        print(f"[ERROR] Failed to copy key: {e}")
        sys.exit(1)
    
    # Close connections
    jump_client.close()
    print(f"[SUCCESS] SSH key setup complete!")
    sys.exit(0)
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"@

# Save Python script temporarily
$tempPythonScript = Join-Path $env:TEMP "copy_ssh_key.py"
$pythonScript | Out-File -FilePath $tempPythonScript -Encoding UTF8

try {
    # Run Python script
    $output = python $tempPythonScript 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] SSH key copied successfully!" -ForegroundColor Green
        Write-Host $output -ForegroundColor Gray
    } else {
        Write-Host "[ERROR] Failed to copy SSH key" -ForegroundColor Red
        Write-Host $output -ForegroundColor Red
        
        Write-Host "`n[INFO] Manual copy instructions:" -ForegroundColor Yellow
        Write-Host "  1. ssh $JumpUser@$JumpHost" -ForegroundColor White
        Write-Host "  2. ssh $TargetUser@$TargetHost" -ForegroundColor White
        Write-Host "  3. mkdir -p ~/.ssh" -ForegroundColor White
        Write-Host "  4. echo '$publicKey' >> ~/.ssh/authorized_keys" -ForegroundColor White
        Write-Host "  5. chmod 700 ~/.ssh" -ForegroundColor White
        Write-Host "  6. chmod 600 ~/.ssh/authorized_keys" -ForegroundColor White
        
        Remove-Item $tempPythonScript -ErrorAction SilentlyContinue
        exit 1
    }
} catch {
    Write-Host "[ERROR] Failed to execute Python script: $_" -ForegroundColor Red
    Remove-Item $tempPythonScript -ErrorAction SilentlyContinue
    exit 1
} finally {
    Remove-Item $tempPythonScript -ErrorAction SilentlyContinue
}

Write-Host "`n[OK] Done!" -ForegroundColor Green

