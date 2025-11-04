# ============================================================================
# Copy vm_150_key Public Key to Server via Jump Host
# ============================================================================
# This script helps you copy the public key to the target server (10.10.10.150)
# through the jump host (10.10.10.10)
# ============================================================================

Write-Host "`n════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Copy vm_150_key Public Key to Server" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan

# Paths
$keyPath = "$env:USERPROFILE\.ssh\vm_150_key"
$pubKeyPath = "$env:USERPROFILE\.ssh\vm_150_key.pub"

# Step 1: Extract public key if needed
Write-Host "`nStep 1: Preparing public key..." -ForegroundColor Yellow

if (-not (Test-Path $pubKeyPath)) {
    Write-Host "Public key file not found, extracting from private key..." -ForegroundColor Cyan
    $pubKey = ssh-keygen -y -f $keyPath 2>&1 | Select-Object -First 1
    if ($LASTEXITCODE -eq 0) {
        $pubKey | Out-File -FilePath $pubKeyPath -Encoding utf8 -NoNewline
        Write-Host "[OK] Public key extracted" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Failed to extract public key" -ForegroundColor Red
        exit 1
    }
}

$pubKey = Get-Content $pubKeyPath -Raw
Write-Host "[OK] Public key ready" -ForegroundColor Green
Write-Host "`nYour public key:" -ForegroundColor Cyan
Write-Host $pubKey.Trim() -ForegroundColor White

# Step 2: Instructions
Write-Host "`n════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Manual Steps Required" -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Since 10.10.10.150 is only accessible via jump host (10.10.10.10)," -ForegroundColor Yellow
Write-Host "you need to copy the public key manually through the jump host." -ForegroundColor Yellow
Write-Host ""
Write-Host "Follow these steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1️⃣  Connect to jump host:" -ForegroundColor Green
Write-Host "    ssh root@10.10.10.10" -ForegroundColor White
Write-Host "    (Password: ask team lead)" -ForegroundColor DarkGray
Write-Host ""
Write-Host "2️⃣  From jump host, connect to target server:" -ForegroundColor Green
Write-Host "    ssh prisma@10.10.10.150" -ForegroundColor White
Write-Host "    (You may need to accept host key)" -ForegroundColor DarkGray
Write-Host ""
Write-Host "3️⃣  On target server, add the public key:" -ForegroundColor Green
Write-Host "    mkdir -p ~/.ssh" -ForegroundColor White
Write-Host "    chmod 700 ~/.ssh" -ForegroundColor White
Write-Host "    echo '$($pubKey.Trim())' >> ~/.ssh/authorized_keys" -ForegroundColor White
Write-Host "    chmod 600 ~/.ssh/authorized_keys" -ForegroundColor White
Write-Host ""
Write-Host "4️⃣  Verify the key was added:" -ForegroundColor Green
Write-Host "    cat ~/.ssh/authorized_keys" -ForegroundColor White
Write-Host "    # You should see your public key" -ForegroundColor DarkGray
Write-Host ""

# Step 3: Alternative - Try automated copy via jump host
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Alternative: Automated Copy (requires password)" -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can try to copy automatically through jump host:" -ForegroundColor Cyan
Write-Host ""

$tryAutomated = Read-Host "Do you want to try automated copy? (y/n)"

if ($tryAutomated -eq 'y' -or $tryAutomated -eq 'Y') {
    Write-Host "`nAttempting automated copy..." -ForegroundColor Cyan
    Write-Host "You will be prompted for passwords:" -ForegroundColor Yellow
    Write-Host "  1. Jump host (root@10.10.10.10)" -ForegroundColor DarkGray
    Write-Host "  2. Target server (prisma@10.10.10.150)" -ForegroundColor DarkGray
    Write-Host ""
    
    # Command to copy key through jump host
    $copyCommand = @"
ssh root@10.10.10.10 "ssh prisma@10.10.10.150 'mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo '$($pubKey.Trim())' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && echo Key added successfully'"
"@
    
    Write-Host "Running command..." -ForegroundColor Cyan
    Invoke-Expression $copyCommand
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Public key copied successfully!" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] Automated copy failed. Use manual method above." -ForegroundColor Yellow
    }
} else {
    Write-Host "Skipping automated copy. Use manual method above." -ForegroundColor DarkGray
}

# Step 4: Test connection after setup
Write-Host "`n════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Next Steps" -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "After adding the key to the server, test the connection:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  .\scripts\connect_k9s_vm150.ps1 -Action test" -ForegroundColor White
Write-Host ""
Write-Host "Or connect directly:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  ssh vm-150" -ForegroundColor White
Write-Host "  k9s" -ForegroundColor White
Write-Host ""

