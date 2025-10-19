# Panda App Configuration Setup Script
# Run this with Administrator privileges

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Panda App Configuration Setup" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$sourceConfig = "C:\Users\roy.avrahami\Downloads\usersettings.cleaned.json"
$targetDir = "C:\Program Files\Prisma\PandaApp"
$targetConfig = Join-Path $targetDir "usersettings.json"
$savedDataDir = "C:\Panda\SavedData"

# Check if source exists
if (-not (Test-Path $sourceConfig)) {
    Write-Host "[ERROR] Source config not found: $sourceConfig" -ForegroundColor Red
    Write-Host "Please ensure the cleaned config file exists." -ForegroundColor Yellow
    pause
    exit 1
}

# Check if target directory exists
if (-not (Test-Path $targetDir)) {
    Write-Host "[ERROR] PandaApp installation not found: $targetDir" -ForegroundColor Red
    Write-Host "Please install PandaApp first." -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "[INFO] Source config: $sourceConfig" -ForegroundColor Green
Write-Host "[INFO] Target location: $targetConfig" -ForegroundColor Green
Write-Host ""

# Backup existing config if present
if (Test-Path $targetConfig) {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupPath = "$targetConfig.backup_$timestamp"
    Write-Host "[BACKUP] Existing config found, creating backup..." -ForegroundColor Yellow
    try {
        Copy-Item $targetConfig $backupPath -Force
        Write-Host "[SUCCESS] Backup created: $backupPath" -ForegroundColor Green
    }
    catch {
        Write-Host "[WARNING] Could not create backup: $_" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Copy new config
Write-Host "[COPY] Copying cleaned config to PandaApp directory..." -ForegroundColor Cyan
try {
    Copy-Item $sourceConfig $targetConfig -Force
    Write-Host "[SUCCESS] Config file copied successfully!" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Failed to copy config: $_" -ForegroundColor Red
    pause
    exit 1
}

# Verify the copy
if (Test-Path $targetConfig) {
    $configSize = (Get-Item $targetConfig).Length
    Write-Host "[VERIFY] Config file exists: $targetConfig ($configSize bytes)" -ForegroundColor Green
}
else {
    Write-Host "[ERROR] Config file was not created!" -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""

# Create SavedData directory
Write-Host "[FOLDER] Creating SavedData directory..." -ForegroundColor Cyan
try {
    if (-not (Test-Path $savedDataDir)) {
        New-Item -Path $savedDataDir -ItemType Directory -Force | Out-Null
        Write-Host "[SUCCESS] Created: $savedDataDir" -ForegroundColor Green
    }
    else {
        Write-Host "[INFO] SavedData directory already exists" -ForegroundColor Green
    }
}
catch {
    Write-Host "[WARNING] Could not create SavedData directory: $_" -ForegroundColor Yellow
    Write-Host "You may need to create it manually later." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Configuration Complete!" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Launch PandaApp from Start Menu" -ForegroundColor White
Write-Host "  2. Check console logs for connection status" -ForegroundColor White
Write-Host "  3. Verify Live View is working" -ForegroundColor White
Write-Host ""

# Ask if user wants to launch the app
$launch = Read-Host "Launch PandaApp now? (Y/N)"
if ($launch -eq "Y" -or $launch -eq "y" -or $launch -eq "") {
    Write-Host "[LAUNCH] Starting PandaApp..." -ForegroundColor Cyan
    try {
        Start-Process "C:\Program Files\Prisma\PandaApp\PandaApp-1.2.41.exe" -WorkingDirectory "C:\Program Files\Prisma\PandaApp"
        Write-Host "[SUCCESS] PandaApp launched!" -ForegroundColor Green
        Write-Host "Check the application window for any errors." -ForegroundColor Yellow
    }
    catch {
        Write-Host "[ERROR] Failed to launch: $_" -ForegroundColor Red
        Write-Host "Try launching from Start Menu instead." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

