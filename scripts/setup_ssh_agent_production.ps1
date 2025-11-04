# ============================================================================
# Setup SSH Agent with panda_production_key for Production (כפר סבא)
# ============================================================================
# This script configures Windows OpenSSH agent to automatically use 
# panda_production_key for connecting to production environment
# ============================================================================

Write-Host "`n════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  SSH Agent Setup - Production (כפר סבא)" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan

# Path to SSH key
$keyPath = "$env:USERPROFILE\.ssh\panda_production_key"

# Step 1: Verify key exists
Write-Host "`nStep 1: Verifying SSH key exists..." -ForegroundColor Yellow
if (-not (Test-Path $keyPath)) {
    Write-Host "[ERROR] SSH key not found at: $keyPath" -ForegroundColor Red
    Write-Host "Please generate the key first:" -ForegroundColor Yellow
    Write-Host "  ssh-keygen -t ed25519 -f `"$keyPath`" -N '`"`"`" -C `"roy.avrahami@prismaphotonics.com`"" -ForegroundColor White
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
Write-Host "`nStep 4: Removing existing production key (if loaded)..." -ForegroundColor Yellow
$keyFingerprint = ssh-keygen -lf $keyPath 2>&1 | Select-String -Pattern "SHA256:"
if ($keyFingerprint) {
    $fingerprint = ($keyFingerprint -split " ")[1]
    ssh-add -d $fingerprint 2>&1 | Out-Null
    ssh-add -d $keyPath 2>&1 | Out-Null
}
# Ignore errors if key wasn't loaded

# Step 5: Add production key to agent
Write-Host "`nStep 5: Adding production key to SSH agent..." -ForegroundColor Yellow
try {
    $addResult = ssh-add $keyPath 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Production key added successfully to SSH agent" -ForegroundColor Green
        
        # Show fingerprint
        Write-Host "`nKey fingerprint:" -ForegroundColor Cyan
        ssh-add -l | Select-String "panda_production_key" | ForEach-Object { Write-Host $_.Line -ForegroundColor White }
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
if ($LASTEXITCODE -eq 0 -and $verifyKeys -match "panda_production_key") {
    Write-Host "[OK] Key verified and ready to use" -ForegroundColor Green
    Write-Host "`nLoaded keys:" -ForegroundColor Cyan
    ssh-add -l
} else {
    Write-Host "[WARNING] Key might not be loaded correctly" -ForegroundColor Yellow
}

# Step 7: Instructions
Write-Host "`n════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔗 Production Environment (כפר סבא):" -ForegroundColor Yellow
Write-Host ""
Write-Host "Jump Host: 10.10.100.3 (panda2worker)" -ForegroundColor Cyan
Write-Host "Target:     10.10.100.113 (worker node)" -ForegroundColor Cyan
Write-Host ""
Write-Host "To connect to k9s:" -ForegroundColor Yellow
Write-Host "  1. ssh root@10.10.100.3" -ForegroundColor White
Write-Host "  2. ssh prisma@10.10.100.113" -ForegroundColor White
Write-Host "  3. k9s -n panda" -ForegroundColor White
Write-Host ""
Write-Host "Or use the script:" -ForegroundColor Yellow
Write-Host "  .\scripts\utilities\connect_k9s.ps1 -Mode connect" -ForegroundColor White
Write-Host ""
Write-Host "Note: The key will persist until you restart the SSH agent or reboot." -ForegroundColor DarkGray
Write-Host "To automatically add the key on login, run this script at startup." -ForegroundColor DarkGray
Write-Host ""

