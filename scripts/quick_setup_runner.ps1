# Quick Setup Script for GitHub Actions Runner on Slave Laptop
# =============================================================
# This script provides an interactive way to set up the runner

param(
    [string]$SlaveIP = "10.50.0.36"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "GitHub Actions Runner Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = py --version 2>&1
    Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.7+" -ForegroundColor Red
    exit 1
}

# Check paramiko
Write-Host "Checking paramiko..." -ForegroundColor Yellow
try {
    py -c "import paramiko; print('paramiko OK')" 2>&1 | Out-Null
    Write-Host "✅ paramiko is installed" -ForegroundColor Green
} catch {
    Write-Host "⚠️  paramiko not found. Installing..." -ForegroundColor Yellow
    py -m pip install paramiko
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install paramiko" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ paramiko installed" -ForegroundColor Green
}

# Check connectivity
Write-Host ""
Write-Host "Checking connectivity to $SlaveIP..." -ForegroundColor Yellow
$pingResult = Test-Connection -ComputerName $SlaveIP -Count 1 -Quiet -ErrorAction SilentlyContinue
if ($pingResult) {
    Write-Host "✅ Ping successful" -ForegroundColor Green
} else {
    Write-Host "⚠️  Ping failed - machine might be offline or firewall blocking" -ForegroundColor Yellow
    Write-Host "   Continuing anyway - SSH might still work..." -ForegroundColor Yellow
}

# Check SSH port
Write-Host "Checking SSH port (22)..." -ForegroundColor Yellow
$sshTest = Test-NetConnection -ComputerName $SlaveIP -Port 22 -InformationLevel Quiet -WarningAction SilentlyContinue
if ($sshTest) {
    Write-Host "✅ SSH port is open" -ForegroundColor Green
} else {
    Write-Host "⚠️  SSH port (22) is not accessible" -ForegroundColor Yellow
    Write-Host "   Please verify:" -ForegroundColor Yellow
    Write-Host "   1. SSH service is running on $SlaveIP" -ForegroundColor Yellow
    Write-Host "   2. Firewall allows SSH (port 22)" -ForegroundColor Yellow
    Write-Host "   3. Machine is powered on and connected to network" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit 0
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Starting Runner Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Run the Python script
py scripts/setup_runner_on_slave_laptop.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "✅ Setup Complete!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Verify runner is online:" -ForegroundColor Yellow
    Write-Host "   https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners" -ForegroundColor Green
    Write-Host ""
    Write-Host "2. Test the runner by running a workflow" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "❌ Setup Failed" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check the error messages above" -ForegroundColor Yellow
    Write-Host "For manual setup instructions, see:" -ForegroundColor Yellow
    Write-Host "  docs/07_infrastructure/SETUP_SLAVE_LAPTOP_RUNNER.md" -ForegroundColor Green
}

