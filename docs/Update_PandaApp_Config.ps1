# ═══════════════════════════════════════════════════════════════
# Update PandaApp Configuration Script
# ═══════════════════════════════════════════════════════════════
# This script updates the usersettings.json in PandaApp folder
# 
# INSTRUCTIONS:
# 1. Right-click this file → "Run with PowerShell" (Admin required)
# 2. Or: Open PowerShell as Admin and run: .\Update_PandaApp_Config.ps1
# ═══════════════════════════════════════════════════════════════

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host ""
    Write-Host "ERROR: This script requires Administrator privileges!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please:" -ForegroundColor Yellow
    Write-Host "1. Right-click on this file" -ForegroundColor Yellow
    Write-Host "2. Select 'Run with PowerShell (Admin)'" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  PandaApp Configuration Update Script" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Target file
$targetFile = "C:\Program Files\Prisma\PandaApp\usersettings.json"

# Check if PandaApp is running
$pandaProcess = Get-Process -Name "PandaApp*" -ErrorAction SilentlyContinue

if ($pandaProcess) {
    Write-Host "[WARNING] PandaApp is currently running!" -ForegroundColor Yellow
    Write-Host ""
    $response = Read-Host "Do you want to close it and continue? (Y/N)"
    
    if ($response -eq 'Y' -or $response -eq 'y') {
        Write-Host "Closing PandaApp..." -ForegroundColor Yellow
        Stop-Process -Name "PandaApp*" -Force
        Start-Sleep -Seconds 2
        Write-Host "[OK] PandaApp closed." -ForegroundColor Green
    } else {
        Write-Host "[CANCELLED] Please close PandaApp manually and run this script again." -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 0
    }
}

# Backup existing file
if (Test-Path $targetFile) {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = "$targetFile.backup_$timestamp"
    
    Write-Host "[INFO] Creating backup..." -ForegroundColor Cyan
    try {
        Copy-Item -Path $targetFile -Destination $backupFile -Force
        Write-Host "[OK] Backup created: $backupFile" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Failed to create backup: $_" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "[WARNING] usersettings.json not found. Creating new file." -ForegroundColor Yellow
}

# New configuration content
$newConfig = @"
{
  "Communication": {
    "Backend": "https://10.10.100.100/focus-server/",
    "Frontend": "https://10.10.10.100/liveView",
    "GrpcStreamMinTimeout_sec": 600,
    "GrpcTimeout": 500,
    "LogEndpoint": "log",
    "NumGrpcRetries": 10,
    "SiteId": "prisma-210-1000",
    "FrontendApi": "https://10.10.100.100:30443/prisma/api/internal/sites/prisma-210-1000"
  },
  "SavedData": {
    "Folder": "C:\\Panda\\SavedData",
    "EnableSave": true,
    "EnableLoad": true
  },
  "Constraints": {
    "FrequencyMax": 1000,
    "FrequencyMin": 0,
    "FrequencyMinRange": 1,
    "MaxWindows": 30,
    "SensorsRange": 2222
  },
  "Defaults": {
    "DisplayTimeAxisDuration": 30,
    "EndChannel": 109,
    "EndFrequency_hz": 1000,
    "FixedThreshold": 0,
    "Nfft": 1024,
    "NumLinesToDisplay": 200,
    "SpatialCenterSize": 3,
    "SpatialWindowSize": 7,
    "SpectralCenterSize": 5,
    "SpectralWindowSize": 11,
    "StartChannel": 11,
    "StartFrequency_hz": 0,
    "StartTime": "2023-01-11T09:35:00",
    "TimeStatus": "Live",
    "TimeWindow": "30s",
    "ViewType": "MultiChannelSpectrogram"
  },
  "EnableDebugTools": false,
  "EnableReconnection": true,
  "FullScreen": false,
  "Logger": {
    "LogGrpcMessages": false,
    "LogGrpcValidation": false,
    "LogPaging": false,
    "LogWorkingQueue": false
  },
  "NumLiveScreens": 30,
  "NumTabs": 10,
  "RefreshRate": 20,
  "Serilog": {
    "WriteTo": [
      {
        "Args": {
          "outputTemplate": " [{Level:u3}] {Timestamp:HH:mm:ss.fff} {Message:lj}{NewLine}{Exception}"
        },
        "Name": "Console"
      }
    ]
  },
  "SplitScreen": true,
  "Options": {
    "nfftSingleChannel": [
      128,
      256,
      512,
      1024,
      2048,
      4096,
      8192,
      16384,
      32768,
      65536
    ]
  },
  "TemplateTypes": [
    "SD",
    "SC"
  ]
}
"@

# Write new configuration
Write-Host ""
Write-Host "[INFO] Updating usersettings.json..." -ForegroundColor Cyan

try {
    $newConfig | Out-File -FilePath $targetFile -Encoding UTF8 -Force
    Write-Host "[OK] Configuration file updated successfully!" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to update file: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  Configuration Updated Successfully!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT: You must restart PandaApp for changes to take effect!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Configuration Summary:" -ForegroundColor Cyan
Write-Host "  Backend:  https://10.10.100.100/focus-server/" -ForegroundColor White
Write-Host "  Frontend: https://10.10.10.100/liveView" -ForegroundColor White
Write-Host "  SiteId:   prisma-210-1000" -ForegroundColor White
Write-Host ""

$launch = Read-Host "Do you want to launch PandaApp now? (Y/N)"

if ($launch -eq 'Y' -or $launch -eq 'y') {
    Write-Host ""
    Write-Host "[INFO] Launching PandaApp..." -ForegroundColor Cyan
    $exePath = "C:\Program Files\Prisma\PandaApp\PandaApp-1.2.41.exe"
    
    if (Test-Path $exePath) {
        Start-Process -FilePath $exePath
        Write-Host "[OK] PandaApp started!" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] Could not find PandaApp executable." -ForegroundColor Yellow
        Write-Host "Please launch it manually." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Press Enter to exit..." -ForegroundColor Gray
Read-Host

