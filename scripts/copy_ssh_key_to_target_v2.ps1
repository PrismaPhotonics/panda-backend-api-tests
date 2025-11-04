# Copy SSH Public Key to Target Host via Jump Host
# =================================================
# Uses SSH directly through jump host

param(
    [string]$PublicKeyPath = "$env:USERPROFILE\.ssh\panda_staging_key.pub",
    [string]$JumpHost = "10.10.10.10",
    [string]$JumpUser = "root",
    [string]$JumpPassword = "PASSW0RD",
    [string]$TargetHost = "10.10.10.150",
    [string]$TargetUser = "prisma"
)

$ErrorActionPreference = "Continue"

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

# Step 2: Save key to temporary file for transfer
$tempKeyFile = Join-Path $env:TEMP "panda_staging_key.pub"
$publicKey | Out-File -FilePath $tempKeyFile -Encoding ASCII -NoNewline

Write-Host "`n[INFO] Copying key to target host via jump host..." -ForegroundColor Cyan
Write-Host "  Jump Host:   $JumpUser@$JumpHost" -ForegroundColor Gray
Write-Host "  Target Host: $TargetUser@$TargetHost" -ForegroundColor Gray

# Step 3: Copy key through jump host using SSH
Write-Host "`n[INFO] Step 1: Copying key to jump host temporarily..." -ForegroundColor Yellow

# Use sshpass or echo password (if sshpass available)
# Otherwise, we'll use a simpler approach
$copyToJumpHost = @"
cat > /tmp/panda_staging_key.pub << 'EOFKEY'
$publicKey
EOFKEY
chmod 600 /tmp/panda_staging_key.pub
echo 'Key saved to jump host'
"@

# Try to connect and copy
try {
    Write-Host "[INFO] Connecting to jump host..." -ForegroundColor Cyan
    
    # Use ssh with password authentication
    $copyScript = @"
echo '$publicKey' > /tmp/panda_staging_key.pub
chmod 600 /tmp/panda_staging_key.pub
ssh -o StrictHostKeyChecking=no $TargetUser@$TargetHost 'mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys' < /tmp/panda_staging_key.pub
rm -f /tmp/panda_staging_key.pub
echo 'Key copied successfully'
"@
    
    # Use ssh with expect-like functionality via here-string
    # Since PowerShell SSH doesn't support -p password easily, we'll use a workaround
    
    Write-Host "[INFO] Attempting automated copy..." -ForegroundColor Cyan
    Write-Host "[WARNING] This requires SSH password authentication..." -ForegroundColor Yellow
    
    # Try using SSH command with password prompt
    # For automation, we might need to use sshpass or Plink
    # Let's try with ssh command directly
    
    # Check if Plink is available (PuTTY)
    $plinkPath = Get-Command plink -ErrorAction SilentlyContinue
    
    if ($plinkPath) {
        Write-Host "[INFO] Using Plink (PuTTY)..." -ForegroundColor Cyan
        
        # Use Plink with password
        $plinkCommand = "-ssh $JumpUser@$JumpHost -pw $JumpPassword `"$copyScript`""
        
        $result = & plink $plinkCommand.Split(' ')
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Key copied successfully via Plink!" -ForegroundColor Green
        } else {
            Write-Host "[ERROR] Plink failed" -ForegroundColor Red
            Write-Host $result -ForegroundColor Red
            throw "Plink failed"
        }
    } else {
        Write-Host "[INFO] Plink not found, using manual instructions..." -ForegroundColor Yellow
        
        # Provide manual copy instructions
        Write-Host "`n========================================" -ForegroundColor Yellow
        Write-Host "MANUAL COPY INSTRUCTIONS" -ForegroundColor Yellow
        Write-Host "========================================" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "1. Connect to jump host:" -ForegroundColor White
        Write-Host "   ssh $JumpUser@$JumpHost" -ForegroundColor Cyan
        Write-Host "   Password: $JumpPassword" -ForegroundColor Gray
        Write-Host ""
        Write-Host "2. From jump host, connect to target host:" -ForegroundColor White
        Write-Host "   ssh $TargetUser@$TargetHost" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "3. On target host, run these commands:" -ForegroundColor White
        Write-Host "   mkdir -p ~/.ssh" -ForegroundColor Cyan
        Write-Host "   chmod 700 ~/.ssh" -ForegroundColor Cyan
        Write-Host "   echo '$publicKey' >> ~/.ssh/authorized_keys" -ForegroundColor Cyan
        Write-Host "   chmod 600 ~/.ssh/authorized_keys" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "4. Test the connection:" -ForegroundColor White
        Write-Host "   Exit from target host, then from jump host" -ForegroundColor Gray
        Write-Host "   ssh -i $PublicKeyPath -o ProxyJump=$JumpUser@$JumpHost $TargetUser@$TargetHost 'hostname'" -ForegroundColor Cyan
        Write-Host ""
        
        # Or try one more automated approach with SSH
        Write-Host "[INFO] Trying alternative automated method..." -ForegroundColor Cyan
        
        # Create a simple script file that can be executed
        $sshScript = @"
#!/bin/bash
echo '$publicKey' > /tmp/key_to_copy.pub
ssh -o StrictHostKeyChecking=no $TargetUser@$TargetHost 'mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys' < /tmp/key_to_copy.pub
rm -f /tmp/key_to_copy.pub
echo 'SUCCESS: Key copied'
"@
        
        $sshScriptFile = Join-Path $env:TEMP "copy_key.sh"
        $sshScript | Out-File -FilePath $sshScriptFile -Encoding UTF8
        
        Write-Host "[INFO] Script saved to: $sshScriptFile" -ForegroundColor Gray
        Write-Host "[INFO] You can manually execute it on jump host:" -ForegroundColor Yellow
        Write-Host "   scp $sshScriptFile $JumpUser@$JumpHost:/tmp/" -ForegroundColor Cyan
        Write-Host "   ssh $JumpUser@$JumpHost 'bash /tmp/copy_key.sh'" -ForegroundColor Cyan
        
        # Cleanup
        Remove-Item $tempKeyFile -ErrorAction SilentlyContinue
        
        exit 1
    }
    
    # Cleanup
    Remove-Item $tempKeyFile -ErrorAction SilentlyContinue
    
    Write-Host "`n[SUCCESS] SSH key copied successfully!" -ForegroundColor Green
    
} catch {
    Write-Host "[ERROR] Failed to copy key: $_" -ForegroundColor Red
    
    Write-Host "`n[INFO] Manual copy required. See instructions above." -ForegroundColor Yellow
    
    Remove-Item $tempKeyFile -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "`n[OK] Done!" -ForegroundColor Green

