# Complete PowerShell Diagnostic and Fix Script
# Based on comprehensive troubleshooting guide
# Checks PowerShell existence, PATH, VS Code config, and provides fixes

param(
    [switch]$FixVSCode,
    [switch]$FixPATH,
    [switch]$RunDISM,
    [switch]$AutoFix
)

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Complete PowerShell Diagnostic & Fix" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$issuesFound = @()
$fixesApplied = @()
$requiresAdmin = $false

# ============================================================================
# STEP 1: Check if PowerShell exists on disk
# ============================================================================

Write-Host "[STEP 1/6] Checking PowerShell installation..." -ForegroundColor Yellow
Write-Host ""

$powershellPath = "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
$powershellDir = "C:\Windows\System32\WindowsPowerShell\v1.0"

# Check if directory exists
if (-not (Test-Path $powershellDir)) {
    Write-Host "  [ERROR] PowerShell directory does not exist!" -ForegroundColor Red
    Write-Host "  Path: $powershellDir" -ForegroundColor Red
    $issuesFound += "PowerShell directory missing"
    Write-Host ""
    Write-Host "  [SEVERE] This indicates Windows installation corruption" -ForegroundColor Red
    Write-Host "  [ACTION] Run DISM + SFC repair (see Step 4)" -ForegroundColor Yellow
} else {
    Write-Host "  [OK] PowerShell directory exists" -ForegroundColor Green
    Write-Host "  Path: $powershellDir" -ForegroundColor Gray
    
    # Check if powershell.exe exists
    if (Test-Path $powershellPath) {
        Write-Host "  [OK] powershell.exe found" -ForegroundColor Green
        $fileInfo = Get-Item $powershellPath
        Write-Host "  Size: $([math]::Round($fileInfo.Length / 1KB, 2)) KB" -ForegroundColor Gray
        Write-Host "  Modified: $($fileInfo.LastWriteTime)" -ForegroundColor Gray
        
        # Test execution
        Write-Host ""
        Write-Host "  Testing PowerShell execution..." -ForegroundColor Yellow
        try {
            $testResult = & $powershellPath -NoProfile -Command "Write-Host 'PowerShell Test'; exit 0" 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  [OK] PowerShell executes successfully" -ForegroundColor Green
            } else {
                Write-Host "  [WARN] PowerShell executed but returned exit code: $LASTEXITCODE" -ForegroundColor Yellow
                $issuesFound += "PowerShell execution issues"
            }
        } catch {
            Write-Host "  [ERROR] PowerShell execution failed: $_" -ForegroundColor Red
            $issuesFound += "PowerShell execution failed"
        }
    } else {
        Write-Host "  [ERROR] powershell.exe NOT found in directory!" -ForegroundColor Red
        $issuesFound += "powershell.exe missing"
        Write-Host ""
        Write-Host "  [SEVERE] System binary is missing" -ForegroundColor Red
        Write-Host "  [ACTION] Run DISM + SFC repair (see Step 4)" -ForegroundColor Yellow
    }
}

# ============================================================================
# STEP 2: Check System PATH
# ============================================================================

Write-Host ""
Write-Host "[STEP 2/6] Checking System PATH..." -ForegroundColor Yellow
Write-Host ""

$powershellInPath = $false
$systemPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$combinedPath = "$systemPath;$userPath"

if ($combinedPath -like "*WindowsPowerShell\v1.0*" -or $combinedPath -like "*WindowsPowerShell/v1.0*") {
    Write-Host "  [OK] PowerShell path found in PATH variable" -ForegroundColor Green
    $powershellInPath = $true
} else {
    Write-Host "  [WARN] PowerShell path NOT in PATH variable" -ForegroundColor Yellow
    $issuesFound += "PowerShell not in PATH"
    
    if ($FixPATH -or $AutoFix) {
        Write-Host "  [ACTION] Adding PowerShell to PATH..." -ForegroundColor Yellow
        try {
            $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
            if ($currentPath -notlike "*WindowsPowerShell\v1.0*") {
                $newPath = "$currentPath;C:\Windows\System32\WindowsPowerShell\v1.0"
                [Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
                Write-Host "  [OK] Added to System PATH" -ForegroundColor Green
                $fixesApplied += "Added PowerShell to PATH"
                $powershellInPath = $true
            }
        } catch {
            Write-Host "  [ERROR] Requires administrator rights: $_" -ForegroundColor Red
            Write-Host "  [ACTION] Run this script as Administrator to fix PATH" -ForegroundColor Yellow
            $requiresAdmin = $true
        }
    } else {
        Write-Host "  [ACTION REQUIRED] Add PowerShell to PATH manually:" -ForegroundColor Yellow
        Write-Host "    1. Win+R → sysdm.cpl → Enter" -ForegroundColor Gray
        Write-Host "    2. Advanced → Environment Variables" -ForegroundColor Gray
        Write-Host "    3. System variables → Path → Edit" -ForegroundColor Gray
        Write-Host "    4. Add: C:\Windows\System32\WindowsPowerShell\v1.0" -ForegroundColor Gray
    }
}

# ============================================================================
# STEP 3: Check VS Code Terminal Configuration
# ============================================================================

Write-Host ""
Write-Host "[STEP 3/6] Checking VS Code terminal configuration..." -ForegroundColor Yellow
Write-Host ""

$settingsPath = "$env:APPDATA\Code\User\settings.json"
if (Test-Path $settingsPath) {
    Write-Host "  [OK] Found VS Code settings.json" -ForegroundColor Green
    
    try {
        $settingsContent = Get-Content $settingsPath -Raw
        $settings = $settingsContent | ConvertFrom-Json -ErrorAction Stop
        
        $hasTerminalConfig = $false
        $needsFix = $false
        
        # Check for terminal settings
        $settings.PSObject.Properties | ForEach-Object {
            if ($_.Name -like "terminal.integrated.*") {
                $hasTerminalConfig = $true
                Write-Host "  [INFO] Found terminal setting: $($_.Name)" -ForegroundColor Cyan
                
                # Check if path is wrong
                if ($_.Value -is [PSCustomObject] -and $_.Value.path) {
                    if ($_.Value.path -notlike "*WindowsPowerShell*" -and $_.Value.path -notlike "*pwsh*") {
                        Write-Host "    [WARN] Custom path may be incorrect: $($_.Value.path)" -ForegroundColor Yellow
                        $needsFix = $true
                    }
                }
            }
        }
        
        if (-not $hasTerminalConfig) {
            Write-Host "  [INFO] No custom terminal configuration (using defaults)" -ForegroundColor Gray
        }
        
        if ($needsFix -or ($FixVSCode -or $AutoFix)) {
            Write-Host ""
            Write-Host "  [ACTION] Fixing VS Code terminal configuration..." -ForegroundColor Yellow
            
            # Convert to hashtable
            $settingsHash = @{}
            $settings.PSObject.Properties | ForEach-Object {
                $settingsHash[$_.Name] = $_.Value
            }
            
            # Add/update terminal settings
            $settingsHash['terminal.integrated.defaultProfile.windows'] = 'PowerShell'
            
            if (-not $settingsHash.ContainsKey('terminal.integrated.profiles.windows')) {
                $settingsHash['terminal.integrated.profiles.windows'] = @{}
            }
            
            # Ensure PowerShell profile uses correct path
            if ($settingsHash['terminal.integrated.profiles.windows'] -is [PSCustomObject]) {
                $profilesHash = @{}
                $settingsHash['terminal.integrated.profiles.windows'].PSObject.Properties | ForEach-Object {
                    $profilesHash[$_.Name] = $_.Value
                }
                $settingsHash['terminal.integrated.profiles.windows'] = $profilesHash
            }
            
            $settingsHash['terminal.integrated.profiles.windows']['PowerShell'] = @{
                path = $powershellPath
                args = @('-NoProfile')
            }
            
            # Create backup
            $backupPath = "$settingsPath.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"
            Copy-Item $settingsPath $backupPath -Force
            Write-Host "  [INFO] Backup created: $backupPath" -ForegroundColor Gray
            
            # Save
            $settingsHash | ConvertTo-Json -Depth 10 -Compress:$false | Set-Content $settingsPath -Encoding UTF8 -NoNewline
            Write-Host "  [OK] VS Code settings updated" -ForegroundColor Green
            $fixesApplied += "Fixed VS Code terminal configuration"
        }
        
    } catch {
        Write-Host "  [WARN] Could not parse settings.json: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [INFO] VS Code settings.json not found" -ForegroundColor Gray
    if ($FixVSCode -or $AutoFix) {
        Write-Host "  [ACTION] Creating VS Code settings..." -ForegroundColor Yellow
        $newSettings = @{
            'terminal.integrated.defaultProfile.windows' = 'PowerShell'
            'terminal.integrated.profiles.windows' = @{
                'PowerShell' = @{
                    path = $powershellPath
                    args = @('-NoProfile')
                }
            }
        }
        
        $settingsDir = Split-Path $settingsPath -Parent
        if (-not (Test-Path $settingsDir)) {
            New-Item -ItemType Directory -Path $settingsDir -Force | Out-Null
        }
        
        $newSettings | ConvertTo-Json -Depth 10 -Compress:$false | Set-Content $settingsPath -Encoding UTF8 -NoNewline
        Write-Host "  [OK] Created VS Code settings" -ForegroundColor Green
        $fixesApplied += "Created VS Code terminal configuration"
    }
}

# ============================================================================
# STEP 4: DISM + SFC Repair (if needed)
# ============================================================================

Write-Host ""
Write-Host "[STEP 4/6] Windows System Repair..." -ForegroundColor Yellow
Write-Host ""

if ($issuesFound -contains "powershell.exe missing" -or $issuesFound -contains "PowerShell directory missing") {
    Write-Host "  [ACTION REQUIRED] PowerShell is missing - system repair needed" -ForegroundColor Yellow
    Write-Host ""
    
    if ($RunDISM -or $AutoFix) {
        Write-Host "  [INFO] Starting DISM repair (this may take 10-30 minutes)..." -ForegroundColor Cyan
        Write-Host "  [NOTE] This requires Administrator rights" -ForegroundColor Yellow
        
        # Check if running as admin
        $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
        
        if ($isAdmin) {
            Write-Host "  [OK] Running as Administrator" -ForegroundColor Green
            Write-Host ""
            Write-Host "  Running: DISM /Online /Cleanup-Image /RestoreHealth" -ForegroundColor Cyan
            Write-Host "  (This will take a while...)" -ForegroundColor Yellow
            
            try {
                $dismResult = DISM /Online /Cleanup-Image /RestoreHealth 2>&1
                Write-Host "  [OK] DISM completed" -ForegroundColor Green
                Write-Host ""
                Write-Host "  Running: sfc /scannow" -ForegroundColor Cyan
                $sfcResult = sfc /scannow 2>&1
                Write-Host "  [OK] SFC completed" -ForegroundColor Green
                Write-Host ""
                Write-Host "  [ACTION] Please reboot your computer and run this script again" -ForegroundColor Yellow
                $fixesApplied += "Ran DISM + SFC repair"
            } catch {
                Write-Host "  [ERROR] Repair failed: $_" -ForegroundColor Red
            }
        } else {
            Write-Host "  [ERROR] Requires Administrator rights" -ForegroundColor Red
            Write-Host "  [ACTION] Run this script as Administrator:" -ForegroundColor Yellow
            Write-Host "    Right-click PowerShell → Run as Administrator" -ForegroundColor Gray
            Write-Host "    Then run: .\scripts\fix_powershell_complete.ps1 -RunDISM" -ForegroundColor Gray
            $requiresAdmin = $true
        }
    } else {
        Write-Host "  [MANUAL STEPS REQUIRED]:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  1. Open Command Prompt as Administrator:" -ForegroundColor Gray
        Write-Host "     Start → type 'cmd' → Right-click → Run as administrator" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  2. Run DISM:" -ForegroundColor Gray
        Write-Host "     DISM /Online /Cleanup-Image /RestoreHealth" -ForegroundColor White
        Write-Host "     (Wait for completion - may take 10-30 minutes)" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  3. Run SFC:" -ForegroundColor Gray
        Write-Host "     sfc /scannow" -ForegroundColor White
        Write-Host ""
        Write-Host "  4. Reboot and check if PowerShell is restored" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  OR run this script with -RunDISM flag as Administrator" -ForegroundColor Cyan
    }
} else {
    Write-Host "  [OK] PowerShell exists - system repair not needed" -ForegroundColor Green
}

# ============================================================================
# STEP 5: Check GitHub Actions Runner
# ============================================================================

Write-Host ""
Write-Host "[STEP 5/6] Checking GitHub Actions Runner..." -ForegroundColor Yellow
Write-Host ""

$runnerServices = Get-Service | Where-Object { $_.DisplayName -like "*GitHub*Actions*" -or $_.DisplayName -like "*Actions Runner*" }
if ($runnerServices) {
    Write-Host "  [INFO] Found GitHub Actions Runner service(s):" -ForegroundColor Cyan
    foreach ($service in $runnerServices) {
        Write-Host "    - $($service.DisplayName) ($($service.Name))" -ForegroundColor Gray
        Write-Host "      Status: $($service.Status)" -ForegroundColor $(if ($service.Status -eq 'Running') { 'Green' } else { 'Yellow' })
    }
    
    if ($powershellInPath -and (Test-Path $powershellPath)) {
        Write-Host ""
        Write-Host "  [OK] PowerShell is available - runner should work" -ForegroundColor Green
        Write-Host "  [NOTE] Restart runner service after PATH changes:" -ForegroundColor Yellow
        Write-Host "    Restart-Service $($runnerServices[0].Name)" -ForegroundColor Gray
    } else {
        Write-Host ""
        Write-Host "  [WARN] PowerShell issues may affect runner" -ForegroundColor Yellow
        Write-Host "  [ACTION] Fix PowerShell first, then restart runner service" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [INFO] No GitHub Actions Runner service found" -ForegroundColor Gray
}

# ============================================================================
# STEP 6: Summary and Recommendations
# ============================================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($fixesApplied.Count -gt 0) {
    Write-Host "[FIXES APPLIED]:" -ForegroundColor Green
    foreach ($fix in $fixesApplied) {
        Write-Host "  [OK] $fix" -ForegroundColor Green
    }
    Write-Host ""
}

if ($issuesFound.Count -gt 0) {
    Write-Host "[ISSUES FOUND]:" -ForegroundColor Yellow
    foreach ($issue in $issuesFound) {
        Write-Host "  - $issue" -ForegroundColor Yellow
    }
    Write-Host ""
}

if ($requiresAdmin) {
    Write-Host "[ACTION REQUIRED]:" -ForegroundColor Red
    Write-Host "  Some fixes require Administrator rights" -ForegroundColor Yellow
    Write-Host "  Run this script as Administrator to apply all fixes" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "[NEXT STEPS]:" -ForegroundColor Cyan
if ($issuesFound -contains "powershell.exe missing" -or $issuesFound -contains "PowerShell directory missing") {
    Write-Host "  1. Run DISM + SFC repair (as Administrator)" -ForegroundColor Yellow
    Write-Host "  2. Reboot computer" -ForegroundColor Yellow
    Write-Host "  3. Run this script again to verify" -ForegroundColor Yellow
} elseif ($issuesFound.Count -eq 0) {
    Write-Host "  [OK] All checks passed!" -ForegroundColor Green
    Write-Host "  1. Restart VS Code" -ForegroundColor Yellow
    Write-Host "  2. Try opening terminal (Ctrl+`)" -ForegroundColor Yellow
    Write-Host "  3. Restart GitHub Actions Runner service if needed" -ForegroundColor Yellow
} else {
    Write-Host "  1. Review issues above" -ForegroundColor Yellow
    Write-Host "  2. Apply recommended fixes" -ForegroundColor Yellow
    Write-Host "  3. Restart VS Code and test terminal" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Script completed!" -ForegroundColor Green

