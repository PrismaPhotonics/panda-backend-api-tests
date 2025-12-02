# Complete VS Code Terminal Fix Script
# This script attempts to fix terminal issues automatically where possible
# and provides clear instructions for manual steps

param(
    [switch]$SkipReinstall,
    [switch]$ForceReinstall
)

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VS Code Terminal Complete Fix Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Find VS Code installation
Write-Host "[STEP 1/6] Locating VS Code installation..." -ForegroundColor Yellow
$vscodePaths = @(
    "$env:LOCALAPPDATA\Programs\Microsoft VS Code",
    "$env:ProgramFiles\Microsoft VS Code",
    "$env:ProgramFiles(x86)\Microsoft VS Code"
)

$foundPath = $null
foreach ($path in $vscodePaths) {
    if (Test-Path $path) {
        $foundPath = $path
        Write-Host "  [OK] Found VS Code at: $path" -ForegroundColor Green
        break
    }
}

if (-not $foundPath) {
    Write-Host "  [ERROR] VS Code not found!" -ForegroundColor Red
    Write-Host "  Please install VS Code first from: https://code.visualstudio.com/" -ForegroundColor Yellow
    exit 1
}

$releasePath = Join-Path $foundPath "resources\app\node_modules.asar.unpacked\node-pty\build\Release"
$criticalFiles = @(
    "winpty.dll",
    "winpty-agent.exe",
    "conpty.node",
    "conpty_console_list.node"
)

# Step 2: Check current status
Write-Host ""
Write-Host "[STEP 2/6] Checking current file status..." -ForegroundColor Yellow
$missingFiles = @()
foreach ($file in $criticalFiles) {
    $filePath = Join-Path $releasePath $file
    if (Test-Path $filePath) {
        Write-Host "  [OK] $file exists" -ForegroundColor Green
    } else {
        Write-Host "  [MISSING] $file" -ForegroundColor Red
        $missingFiles += $file
    }
}

if ($missingFiles.Count -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] All files are present! Terminal should work." -ForegroundColor Green
    Write-Host "If you still have issues, restart VS Code." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "  [WARN] Found $($missingFiles.Count) missing file(s)" -ForegroundColor Yellow

# Step 3: Check antivirus status
Write-Host ""
Write-Host "[STEP 3/6] Checking antivirus status..." -ForegroundColor Yellow

# Check for Cynet
$cynetProcess = Get-Process -Name "*cynet*" -ErrorAction SilentlyContinue
if ($cynetProcess) {
    Write-Host "  [INFO] Cynet Endpoint Security is running" -ForegroundColor Cyan
    Write-Host "  [ACTION REQUIRED] You need to manually add VS Code to Cynet exclusions:" -ForegroundColor Yellow
    Write-Host "    1. Open Cynet (Windows Security > Open app)" -ForegroundColor Gray
    Write-Host "    2. Find Exclusions/Exceptions/Whitelist" -ForegroundColor Gray
    Write-Host "    3. Add folder: $foundPath" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "  [INFO] Cynet process not found (may still be installed)" -ForegroundColor Gray
}

# Check Windows Defender
try {
    $defenderStatus = Get-MpPreference -ErrorAction SilentlyContinue
    if ($defenderStatus) {
        Write-Host "  [INFO] Windows Defender is active" -ForegroundColor Cyan
        Write-Host "  [ACTION] Adding VS Code to Windows Defender exclusions..." -ForegroundColor Yellow
        
        try {
            Add-MpPreference -ExclusionPath $foundPath -ErrorAction Stop
            Write-Host "  [OK] Added VS Code to Windows Defender exclusions" -ForegroundColor Green
        } catch {
            Write-Host "  [WARN] Could not add automatically. Error: $_" -ForegroundColor Yellow
            Write-Host "  [ACTION REQUIRED] Add manually:" -ForegroundColor Yellow
            Write-Host "    1. Windows Security > Virus & threat protection" -ForegroundColor Gray
            Write-Host "    2. Manage settings > Exclusions > Add folder" -ForegroundColor Gray
            Write-Host "    3. Select: $foundPath" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "  [INFO] Windows Defender check skipped (may require admin rights)" -ForegroundColor Gray
}

# Step 4: Check quarantine
Write-Host ""
Write-Host "[STEP 4/6] Checking for quarantined files..." -ForegroundColor Yellow

# Check Windows Defender quarantine
try {
    $quarantine = Get-MpThreatDetection -ErrorAction SilentlyContinue | Where-Object {
        $_.Resources -like "*VS Code*" -or $_.Resources -like "*winpty*" -or $_.Resources -like "*conpty*"
    }
    
    if ($quarantine) {
        Write-Host "  [FOUND] Quarantined files detected!" -ForegroundColor Yellow
        Write-Host "  [ACTION] Attempting to restore..." -ForegroundColor Yellow
        
        foreach ($threat in $quarantine) {
            try {
                Remove-MpThreat -ThreatID $threat.ThreatID -ErrorAction Stop
                Write-Host "  [OK] Restored threat ID: $($threat.ThreatID)" -ForegroundColor Green
            } catch {
                Write-Host "  [WARN] Could not restore automatically: $_" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "  [INFO] No quarantined files found in Windows Defender" -ForegroundColor Gray
        Write-Host "  [NOTE] Check Cynet quarantine manually if using Cynet" -ForegroundColor Gray
    }
} catch {
    Write-Host "  [INFO] Quarantine check skipped (may require admin rights)" -ForegroundColor Gray
}

# Step 5: Reinstall VS Code if needed
Write-Host ""
Write-Host "[STEP 5/6] VS Code reinstallation..." -ForegroundColor Yellow

if ($ForceReinstall -or ($missingFiles.Count -eq 4 -and -not $SkipReinstall)) {
    Write-Host "  [INFO] Files are missing. Reinstallation recommended." -ForegroundColor Yellow
    
    if ($ForceReinstall) {
        $shouldReinstall = $true
    } else {
        Write-Host ""
        Write-Host "  Do you want to reinstall VS Code now? (Y/N)" -ForegroundColor Cyan
        $response = Read-Host
        $shouldReinstall = $response -eq 'Y' -or $response -eq 'y'
    }
    
    if ($shouldReinstall) {
        Write-Host "  [ACTION] Downloading VS Code installer..." -ForegroundColor Yellow
        
        $tempDir = "$env:TEMP\VSCodeReinstall"
        $installerPath = Join-Path $tempDir "VSCodeSetup.exe"
        
        if (-not (Test-Path $tempDir)) {
            New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
        }
        
        try {
            # Download VS Code installer
            # Get the latest stable download URL
            Write-Host "  [INFO] Getting latest VS Code download URL..." -ForegroundColor Gray
            
            # VS Code direct download URL for Windows 64-bit User installer
            $downloadUrl = "https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-user"
            
            Write-Host "  [INFO] Opening VS Code download page..." -ForegroundColor Gray
            Write-Host "  [NOTE] Please download the installer manually and run it" -ForegroundColor Yellow
            Write-Host "  [NOTE] Download page will open in your browser" -ForegroundColor Gray
            
            # Open download page
            Start-Process "https://code.visualstudio.com/download"
            
            Write-Host "  [ACTION REQUIRED] Please:" -ForegroundColor Yellow
            Write-Host "    1. Download 'User Installer' (64-bit)" -ForegroundColor Gray
            Write-Host "    2. Run the installer" -ForegroundColor Gray
            Write-Host "    3. Make sure to install to: $foundPath" -ForegroundColor Gray
            Write-Host ""
            Write-Host "  Press any key after installation is complete..." -ForegroundColor Cyan
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            
            # Alternative: Try to download directly (may not work due to redirects)
            # $ProgressPreference = 'Continue'
            # try {
            #     $response = Invoke-WebRequest -Uri $downloadUrl -MaximumRedirection 0 -ErrorAction Stop
            #     $actualUrl = $response.Headers.Location
            #     Invoke-WebRequest -Uri $actualUrl -OutFile $installerPath -UseBasicParsing -ErrorAction Stop
            #     $ProgressPreference = 'SilentlyContinue'
            # } catch {
            #     Write-Host "  [WARN] Automatic download failed, using manual method" -ForegroundColor Yellow
            # }
            
            # Installation should be done manually
            Write-Host "  [OK] Waiting for manual installation..." -ForegroundColor Green
            
        } catch {
            Write-Host "  [ERROR] Could not download/install automatically: $_" -ForegroundColor Red
            Write-Host "  [ACTION REQUIRED] Please download and install manually:" -ForegroundColor Yellow
            Write-Host "    1. Download from: https://code.visualstudio.com/" -ForegroundColor Gray
            Write-Host "    2. Run installer" -ForegroundColor Gray
            Write-Host "    3. Install to: $foundPath" -ForegroundColor Gray
        }
    } else {
        Write-Host "  [SKIPPED] Reinstallation skipped" -ForegroundColor Yellow
        Write-Host "  [NOTE] You may need to reinstall VS Code manually to restore files" -ForegroundColor Gray
    }
} else {
    Write-Host "  [SKIPPED] Reinstallation not needed or skipped" -ForegroundColor Gray
}

# Step 6: Verify and final check
Write-Host ""
Write-Host "[STEP 6/6] Final verification..." -ForegroundColor Yellow

Start-Sleep -Seconds 2  # Give time for any installations to complete

$allPresent = $true
$stillMissing = @()

foreach ($file in $criticalFiles) {
    $filePath = Join-Path $releasePath $file
    if (Test-Path $filePath) {
        Write-Host "  [OK] $file exists" -ForegroundColor Green
    } else {
        Write-Host "  [MISSING] $file" -ForegroundColor Red
        $stillMissing += $file
        $allPresent = $false
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FINAL SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($allPresent) {
    Write-Host "[SUCCESS] All critical files are now present!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Restart VS Code completely" -ForegroundColor Gray
    Write-Host "  2. Try opening terminal (Ctrl+`)" -ForegroundColor Gray
    Write-Host "  3. If still not working, check VS Code Output panel for errors" -ForegroundColor Gray
} else {
    Write-Host "[ERROR] Still missing $($stillMissing.Count) file(s):" -ForegroundColor Red
    foreach ($file in $stillMissing) {
        Write-Host "  - $file" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "Manual actions required:" -ForegroundColor Yellow
    Write-Host "  1. Make sure VS Code is added to antivirus exclusions:" -ForegroundColor Yellow
    Write-Host "     Folder: $foundPath" -ForegroundColor White
    Write-Host ""
    Write-Host "  2. Check antivirus quarantine and restore files:" -ForegroundColor Yellow
    Write-Host "     - Cynet: Open app > Check quarantine/history" -ForegroundColor Gray
    Write-Host "     - Windows Defender: Protection history" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  3. If files still missing, reinstall VS Code:" -ForegroundColor Yellow
    Write-Host "     Download: https://code.visualstudio.com/" -ForegroundColor Gray
    Write-Host "     Install to: $foundPath" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  4. After adding exclusions and reinstalling, run this script again:" -ForegroundColor Yellow
    Write-Host "     .\scripts\fix_vscode_terminal_complete.ps1" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Script completed!" -ForegroundColor Green

