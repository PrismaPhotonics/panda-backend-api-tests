# Quick Setup Script with Token
# =============================
# This script helps you set up the runner on the slave laptop with the token you got from GitHub

param(
    [Parameter(Mandatory=$true)]
    [string]$SSHUser,
    
    [Parameter(Mandatory=$false)]
    [string]$SSHPassword,
    
    [Parameter(Mandatory=$false)]
    [string]$SSHKeyFile,
    
    [Parameter(Mandatory=$false)]
    [string]$SlaveIP = "10.50.0.36",
    
    [Parameter(Mandatory=$false)]
    [string]$Token = "BXBPK45XRW4YHLQ7DEJI6Y3JEWENK"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "GitHub Actions Runner Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Target: $SlaveIP" -ForegroundColor Yellow
Write-Host "Token: $($Token.Substring(0,10))..." -ForegroundColor Yellow
Write-Host ""

# Check if we have authentication
if ([string]::IsNullOrEmpty($SSHPassword) -and [string]::IsNullOrEmpty($SSHKeyFile)) {
    Write-Host "Authentication required:" -ForegroundColor Yellow
    $authMethod = Read-Host "Method: (1) Password (2) SSH Key"
    if ($authMethod -eq "2") {
        $SSHKeyFile = Read-Host "SSH key file path"
    } else {
        $securePassword = Read-Host "SSH password" -AsSecureString
        $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
        $SSHPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
    }
}

# Run the Python script
Write-Host ""
Write-Host "Running setup script..." -ForegroundColor Cyan
Write-Host ""

$pythonArgs = @(
    "scripts\setup_runner_on_slave_laptop.py"
    "--user", $SSHUser
    "--slave-ip", $SlaveIP
    "--token", $Token
)

if ($SSHPassword) {
    $pythonArgs += "--password", $SSHPassword
} elseif ($SSHKeyFile) {
    $pythonArgs += "--key", $SSHKeyFile
}

py $pythonArgs

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "✅ Setup Complete!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Verify runner is online:" -ForegroundColor Cyan
    Write-Host "https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "❌ Setup Failed" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
}

