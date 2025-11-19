# Script to setup self-hosted runner on Windows
# Run this script on the lab machine

param(
    [string]$RepoUrl = "",
    [string]$RunnerName = "lab-windows-runner-01",
    [string]$InstallPath = "C:\actions-runner"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setting up Self-Hosted Runner" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

if ([string]::IsNullOrEmpty($RepoUrl)) {
    Write-Host "❌ Repository URL is required!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\scripts\setup_self_hosted_runner.ps1 -RepoUrl 'https://github.com/PrismaPhotonics/panda-backend-api-tests'" -ForegroundColor Green
    Write-Host ""
    Write-Host "Default repository: https://github.com/PrismaPhotonics/panda-backend-api-tests" -ForegroundColor Cyan
    $RepoUrl = "https://github.com/PrismaPhotonics/panda-backend-api-tests"
    Write-Host "Using default: $RepoUrl" -ForegroundColor Yellow
}

# Create installation directory
if (-not (Test-Path $InstallPath)) {
    Write-Host "Creating installation directory: $InstallPath" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
}

# Download runner
Write-Host "Downloading GitHub Actions Runner..." -ForegroundColor Yellow
$runnerUrl = "https://github.com/actions/runner/releases/latest/download/actions-runner-win-x64-2.311.0.zip"
$zipPath = Join-Path $InstallPath "actions-runner.zip"

try {
    Invoke-WebRequest -Uri $runnerUrl -OutFile $zipPath
    Write-Host "✅ Download completed" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to download runner: $_" -ForegroundColor Red
    exit 1
}

# Extract runner
Write-Host "Extracting runner..." -ForegroundColor Yellow
Expand-Archive -Path $zipPath -DestinationPath $InstallPath -Force
Remove-Item $zipPath
Write-Host "✅ Extraction completed" -ForegroundColor Green

# Configure runner
Write-Host ""
Write-Host "Configuring runner..." -ForegroundColor Yellow
Write-Host "You will need a registration token from GitHub:" -ForegroundColor Cyan
Write-Host "  1. Go to: https://github.com/YOUR_ORG/YOUR_REPO/settings/actions/runners/new" -ForegroundColor Cyan
Write-Host "  2. Copy the registration token" -ForegroundColor Cyan
Write-Host ""

$token = Read-Host "Enter registration token"

Push-Location $InstallPath
try {
    .\config.cmd --url $RepoUrl --token $token --name $RunnerName --labels "self-hosted,windows,lab" --work "_work" --replace
    Write-Host "✅ Configuration completed" -ForegroundColor Green
} catch {
    Write-Host "❌ Configuration failed: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

# Install as service
Write-Host ""
Write-Host "Installing as Windows service..." -ForegroundColor Yellow
Push-Location $InstallPath
try {
    .\svc.cmd install
    .\svc.cmd start
    Write-Host "✅ Service installed and started" -ForegroundColor Green
} catch {
    Write-Host "❌ Service installation failed: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Self-Hosted Runner Setup Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Runner Name: $RunnerName" -ForegroundColor Yellow
Write-Host "Installation Path: $InstallPath" -ForegroundColor Yellow
Write-Host ""
Write-Host "To check status:" -ForegroundColor Cyan
Write-Host "  cd $InstallPath" -ForegroundColor Green
Write-Host "  .\svc.cmd status" -ForegroundColor Green
Write-Host ""

