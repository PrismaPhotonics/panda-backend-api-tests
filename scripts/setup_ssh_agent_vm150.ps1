# ============================================================================
# Setup SSH Agent with vm_150_key for Automatic Authentication
# ============================================================================
# This script configures Windows OpenSSH agent to automatically use vm_150_key
# for connecting to 10.10.10.150 (k9s access)
# ============================================================================

Write-Host "`n════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  SSH Agent Setup - vm_150_key" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan

# Path to SSH key
$keyPath = "$env:USERPROFILE\.ssh\vm_150_key"

# Step 1: Verify key exists
Write-Host "`nStep 1: Verifying SSH key exists..." -ForegroundColor Yellow
if (-not (Test-Path $keyPath)) {
    Write-Host "[ERROR] SSH key not found at: $keyPath" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] SSH key found: $keyPath" -ForegroundColor Green

# Step 2: Start SSH Agent service
Write-Host "`nStep 2: Starting SSH Agent service..." -ForegroundColor Yellow
try {
    $service = Get-Service ssh-agent -ErrorAction Stop
    if ($service.StartType -ne 'Automatic') {
        Set-Service ssh-agent -StartupType Automatic
        Write-Host "[OK] SSH Agent service set to auto-start" -ForegroundColor Green
    } else {
        Write-Host "[OK] SSH Agent service already set to auto-start" -ForegroundColor Green
    }
    
    if ($service.Status -ne 'Running') {
        Start-Service ssh-agent
        Write-Host "[OK] SSH Agent service started" -ForegroundColor Green
    } else {
        Write-Host "[OK] SSH Agent service already running" -ForegroundColor Green
    }
} catch {
    Write-Host "[ERROR] Failed to configure SSH Agent service: $_" -ForegroundColor Red
    exit 1
}

# Step 3: Check current keys
Write-Host "`nStep 3: Checking current SSH keys..." -ForegroundColor Yellow
$currentKeys = ssh-add -l 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "Currently loaded keys:" -ForegroundColor Cyan
    ssh-add -l
} else {
    Write-Host "No keys currently loaded" -ForegroundColor DarkGray
}

# Step 4: Remove key if already loaded (to avoid duplicates)
Write-Host "`nStep 4: Removing existing vm_150_key (if loaded)..." -ForegroundColor Yellow
$keyFingerprint = ssh-keygen -lf $keyPath 2>&1 | Select-String -Pattern "SHA256:"
if ($keyFingerprint) {
    $fingerprint = ($keyFingerprint -split " ")[1]
    ssh-add -d $fingerprint 2>&1 | Out-Null
    # Also try removing by path
    ssh-add -d $keyPath 2>&1 | Out-Null
}
# Ignore errors if key wasn't loaded

# Step 5: Add vm_150_key to agent
Write-Host "`nStep 5: Adding vm_150_key to SSH agent..." -ForegroundColor Yellow
try {
    $addResult = ssh-add $keyPath 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] vm_150_key added successfully to SSH agent" -ForegroundColor Green
        
        # Show fingerprint
        Write-Host "`nKey fingerprint:" -ForegroundColor Cyan
        ssh-add -l | Select-String "vm_150_key" | ForEach-Object { Write-Host $_.Line -ForegroundColor White }
    } else {
        Write-Host "[ERROR] Failed to add key to agent: $addResult" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] Failed to add key to agent: $_" -ForegroundColor Red
    exit 1
}

# Step 6: Verify key is loaded
Write-Host "`nStep 6: Verifying key is loaded..." -ForegroundColor Yellow
$verifyKeys = ssh-add -l 2>&1
if ($LASTEXITCODE -eq 0 -and $verifyKeys -match "vm_150_key|RSA") {
    Write-Host "[OK] Key verified and ready to use" -ForegroundColor Green
    Write-Host "`nLoaded keys:" -ForegroundColor Cyan
    ssh-add -l
} else {
    Write-Host "[WARNING] Key might not be loaded correctly" -ForegroundColor Yellow
}

# Step 7: Test connection (optional)
Write-Host "`nStep 7: Test connection to 10.10.10.150 (optional)..." -ForegroundColor Yellow
Write-Host "NOTE: 10.10.10.150 requires jump host (10.10.10.10)" -ForegroundColor DarkGray
Write-Host "Make sure the public key is added to the server first!" -ForegroundColor Yellow
Write-Host ""
Write-Host "To copy the public key, run:" -ForegroundColor Cyan
Write-Host "  .\scripts\copy_vm150_key_to_server.ps1" -ForegroundColor White
Write-Host ""
$testConnection = Read-Host "Do you want to test the connection now? (y/n)"
if ($testConnection -eq 'y' -or $testConnection -eq 'Y') {
    Write-Host "`nTesting SSH connection via jump host..." -ForegroundColor Cyan
    Write-Host "This should work WITHOUT password prompt" -ForegroundColor DarkGray
    ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no vm-150 "echo 'Connection successful!'; hostname"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Connection test successful!" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] Connection test failed." -ForegroundColor Yellow
        Write-Host "Possible reasons:" -ForegroundColor Yellow
        Write-Host "  1. Public key not added to server (run copy_vm150_key_to_server.ps1)" -ForegroundColor White
        Write-Host "  2. Jump host not accessible (10.10.10.10)" -ForegroundColor White
        Write-Host "  3. Target server not accessible from jump host" -ForegroundColor White
    }
}

# Summary
Write-Host "`n════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now connect to 10.10.10.150 without entering password:" -ForegroundColor Yellow
Write-Host "  ssh vm-150           # Using SSH config alias" -ForegroundColor White
Write-Host "  ssh prisma@10.10.10.150   # Direct connection" -ForegroundColor White
Write-Host ""
Write-Host "To connect to k9s:" -ForegroundColor Yellow
Write-Host "  ssh vm-150" -ForegroundColor White
Write-Host "  k9s" -ForegroundColor White
Write-Host ""
Write-Host "Note: The key will persist until you restart the SSH agent or reboot." -ForegroundColor DarkGray
Write-Host "To automatically add the key on login, run this script at startup." -ForegroundColor DarkGray
Write-Host ""

