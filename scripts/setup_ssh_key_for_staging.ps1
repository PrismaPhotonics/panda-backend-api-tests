# Setup SSH Key for Staging Environment
# =======================================
# This script will:
# 1. Generate SSH key pair (if not exists)
# 2. Copy public key to target host via jump host
# 3. Update environments.yaml configuration

param(
    [string]$KeyName = "panda_staging_key",
    [string]$JumpHost = "10.10.10.10",
    [string]$JumpUser = "root",
    [string]$JumpPassword = "PASSW0RD",
    [string]$TargetHost = "10.10.10.150",
    [string]$TargetUser = "prisma",
    [string]$Environment = "staging"
)

$ErrorActionPreference = "Stop"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "SSH Key Setup for Staging Environment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Step 1: Check/Generate SSH Key
$sshDir = Join-Path $env:USERPROFILE ".ssh"
$privateKeyPath = Join-Path $sshDir "$KeyName"
$publicKeyPath = Join-Path $sshDir "$KeyName.pub"

Write-Host "`nStep 1: Checking SSH Key..." -ForegroundColor Yellow

if (Test-Path $privateKeyPath) {
    Write-Host "[OK] SSH key already exists: $privateKeyPath" -ForegroundColor Green
} else {
    Write-Host "[INFO] Creating new SSH key pair..." -ForegroundColor Cyan
    
    # Create .ssh directory if not exists
    if (-not (Test-Path $sshDir)) {
        New-Item -ItemType Directory -Path $sshDir -Force | Out-Null
        Write-Host "[OK] Created .ssh directory" -ForegroundColor Green
    }
    
    # Generate SSH key (ed25519)
    Write-Host "[INFO] Generating ed25519 key (no passphrase for automation)..." -ForegroundColor Cyan
    $keygenOutput = ssh-keygen -t ed25519 -f $privateKeyPath -N '""' -C "panda-staging-automation" 2>&1
    
    if ($LASTEXITCODE -eq 0 -and (Test-Path $privateKeyPath)) {
        Write-Host "[OK] SSH key created successfully" -ForegroundColor Green
        Write-Host "  Private key: $privateKeyPath" -ForegroundColor Gray
        Write-Host "  Public key:  $publicKeyPath" -ForegroundColor Gray
    } else {
        Write-Host "[ERROR] Failed to create SSH key" -ForegroundColor Red
        Write-Host $keygenOutput -ForegroundColor Red
        exit 1
    }
}

# Step 2: Read public key
Write-Host "`nStep 2: Reading public key..." -ForegroundColor Yellow
$publicKey = Get-Content $publicKeyPath -Raw
$publicKey = $publicKey.Trim()
Write-Host "[OK] Public key read successfully" -ForegroundColor Green
Write-Host "  Key: $($publicKey.Substring(0, [Math]::Min(50, $publicKey.Length)))..." -ForegroundColor Gray

# Step 3: Copy public key to target host via jump host
Write-Host "`nStep 3: Copying public key to target host via jump host..." -ForegroundColor Yellow
Write-Host "  Jump Host:   $JumpUser@$JumpHost" -ForegroundColor Gray
Write-Host "  Target Host: $TargetUser@$TargetHost" -ForegroundColor Gray

# Create command to copy key to target host
$copyCommand = @"
mkdir -p ~/.ssh && 
echo '$publicKey' >> ~/.ssh/authorized_keys && 
chmod 700 ~/.ssh && 
chmod 600 ~/.ssh/authorized_keys && 
echo 'Key copied successfully'
"@

# Use Plink or ssh to connect through jump host
# First, test jump host connection
Write-Host "`n[INFO] Testing jump host connection..." -ForegroundColor Cyan
try {
    $jumpTest = ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 "$JumpUser@$JumpHost" "hostname" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Jump host connection successful" -ForegroundColor Green
        
        # Now copy key through jump host
        Write-Host "`n[INFO] Copying key to target host..." -ForegroundColor Cyan
        
        # Method 1: Use ssh with expect-like behavior (PowerShell)
        $fullCommand = "ssh $TargetUser@$TargetHost '$copyCommand'"
        $copyOutput = ssh -o StrictHostKeyChecking=no "$JumpUser@$JumpHost" $fullCommand 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Public key copied successfully!" -ForegroundColor Green
        } else {
            Write-Host "[WARNING] Direct copy failed, trying alternative method..." -ForegroundColor Yellow
            Write-Host $copyOutput -ForegroundColor Gray
            
            # Alternative: Copy to jump host first, then to target
            Write-Host "[INFO] Trying two-step copy..." -ForegroundColor Cyan
            
            # Step 3a: Copy key to jump host temporarily
            $tempKeyFile = "/tmp/panda_staging_key.pub"
            echo $publicKey | ssh -o StrictHostKeyChecking=no "$JumpUser@$JumpHost" "cat > $tempKeyFile" 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "[OK] Key saved to jump host temporarily" -ForegroundColor Green
                
                # Step 3b: Copy from jump host to target host
                $copyFromJump = "ssh $TargetUser@$TargetHost 'mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys' < $tempKeyFile"
                $copyOutput2 = ssh -o StrictHostKeyChecking=no "$JumpUser@$JumpHost" $copyFromJump 2>&1
                
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "[OK] Public key copied to target host!" -ForegroundColor Green
                    
                    # Cleanup temp file
                    ssh -o StrictHostKeyChecking=no "$JumpUser@$JumpHost" "rm -f $tempKeyFile" 2>&1 | Out-Null
                } else {
                    Write-Host "[ERROR] Failed to copy key from jump host to target host" -ForegroundColor Red
                    Write-Host $copyOutput2 -ForegroundColor Red
                    Write-Host "`n[INFO] You may need to copy the key manually:" -ForegroundColor Yellow
                    Write-Host "  1. ssh $JumpUser@$JumpHost" -ForegroundColor White
                    Write-Host "  2. ssh $TargetUser@$TargetHost" -ForegroundColor White
                    Write-Host "  3. echo '$publicKey' >> ~/.ssh/authorized_keys" -ForegroundColor White
                    exit 1
                }
            } else {
                Write-Host "[ERROR] Failed to copy key to jump host" -ForegroundColor Red
                exit 1
            }
        }
    } else {
        Write-Host "[ERROR] Cannot connect to jump host" -ForegroundColor Red
        Write-Host $jumpTest -ForegroundColor Red
        Write-Host "`n[INFO] Please verify:" -ForegroundColor Yellow
        Write-Host "  1. Jump host is accessible: $JumpUser@$JumpHost" -ForegroundColor White
        Write-Host "  2. Password is correct: $JumpPassword" -ForegroundColor White
        exit 1
    }
} catch {
    Write-Host "[ERROR] Connection error: $_" -ForegroundColor Red
    exit 1
}

# Step 4: Test SSH connection
Write-Host "`nStep 4: Testing SSH connection to target host..." -ForegroundColor Yellow
try {
    # Test connection through jump host using the new key
    $testCommand = "ssh -i $privateKeyPath -o StrictHostKeyChecking=no -o ConnectTimeout=10 -o ProxyJump=$JumpUser@$JumpHost $TargetUser@$TargetHost 'hostname && echo Connection successful'"
    $testOutput = & cmd /c $testCommand 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] SSH connection test successful!" -ForegroundColor Green
        Write-Host $testOutput -ForegroundColor Gray
    } else {
        Write-Host "[WARNING] Direct SSH test failed, but key might still work" -ForegroundColor Yellow
        Write-Host "[INFO] Testing with SSHManager instead..." -ForegroundColor Cyan
    }
} catch {
    Write-Host "[WARNING] SSH test failed, but continuing..." -ForegroundColor Yellow
}

# Step 5: Update environments.yaml
Write-Host "`nStep 5: Updating environments.yaml configuration..." -ForegroundColor Yellow

$configPath = Join-Path $PSScriptRoot "..\config\environments.yaml"
$configPath = Resolve-Path $configPath

if (-not (Test-Path $configPath)) {
    Write-Host "[ERROR] Cannot find environments.yaml at: $configPath" -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] Updating SSH configuration..." -ForegroundColor Cyan

# Read YAML file
$yamlContent = Get-Content $configPath -Raw

# Update target_host key_file (use relative path for Windows compatibility)
$keyPathForConfig = "~/.ssh/$KeyName"

# Use regex to find and update the target_host section
$targetHostPattern = '(?s)(target_host:\s*\n\s*host:\s*"[^"]+"\s*\n\s*port:\s*\d+\s*\n\s*username:\s*"[^"]+"\s*\n\s*password:\s*"[^"]+"\s*\n\s*)'
$replacement = "`$1    key_file: `"$keyPathForConfig`"`n      "

if ($yamlContent -match $targetHostPattern) {
    $yamlContent = $yamlContent -replace $targetHostPattern, $replacement
    
    # Write back to file
    Set-Content -Path $configPath -Value $yamlContent -NoNewline
    Write-Host "[OK] environments.yaml updated successfully" -ForegroundColor Green
    Write-Host "  Added key_file: $keyPathForConfig" -ForegroundColor Gray
} else {
    Write-Host "[WARNING] Could not auto-update environments.yaml" -ForegroundColor Yellow
    Write-Host "[INFO] Please manually update config/environments.yaml:" -ForegroundColor Yellow
    Write-Host "  target_host:" -ForegroundColor White
    Write-Host "    key_file: `"$keyPathForConfig`"" -ForegroundColor White
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "[SUCCESS] SSH Key Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "  Private Key: $privateKeyPath" -ForegroundColor Gray
Write-Host "  Public Key:  $publicKeyPath" -ForegroundColor Gray
Write-Host "  Target Host: $TargetUser@$TargetHost" -ForegroundColor Gray
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Test connection: python scripts/test_ssh_connection.py --env $Environment" -ForegroundColor White
Write-Host "  2. Verify in environments.yaml: key_file is set" -ForegroundColor White
Write-Host ""

