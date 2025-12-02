# Fix Missing PowerShell Executable Issue
# This script addresses the REAL problem: powershell.exe missing or not found
# Error: Path to shell executable "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" does not exist

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PowerShell Missing - Diagnostic & Fix" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script checks if PowerShell exists and fixes the real issue." -ForegroundColor Yellow
Write-Host ""

$ErrorActionPreference = "Continue"

# ============================================================================
# STEP 1: Check if PowerShell really exists
# ============================================================================

Write-Host "[STEP 1/4] Checking if PowerShell exists..." -ForegroundColor Yellow
Write-Host ""

$powershellPath = "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
$powershellDir = "C:\Windows\System32\WindowsPowerShell\v1.0"

# Check directory
if (-not (Test-Path $powershellDir)) {
    Write-Host "  [ERROR] PowerShell directory does NOT exist!" -ForegroundColor Red
    Write-Host "  Path: $powershellDir" -ForegroundColor Red
    Write-Host ""
    Write-Host "  [SEVERE] This is OS corruption or corporate policy" -ForegroundColor Red
    Write-Host "  [ACTION] Go to STEP 3 - OS Repair" -ForegroundColor Yellow
    $powershellExists = $false
} else {
    Write-Host "  [OK] PowerShell directory exists" -ForegroundColor Green
    Write-Host "  Path: $powershellDir" -ForegroundColor Gray
    
    # Check executable
    if (Test-Path $powershellPath) {
        Write-Host "  [OK] powershell.exe EXISTS" -ForegroundColor Green
        $fileInfo = Get-Item $powershellPath
        Write-Host "  Size: $([math]::Round($fileInfo.Length / 1KB, 2)) KB" -ForegroundColor Gray
        Write-Host "  Modified: $($fileInfo.LastWriteTime)" -ForegroundColor Gray
        $powershellExists = $true
        
        # Test execution
        Write-Host ""
        Write-Host "  Testing PowerShell execution..." -ForegroundColor Yellow
        try {
            $testResult = & $powershellPath -NoProfile -Command "Write-Host 'Test'; exit 0" 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  [OK] PowerShell executes successfully" -ForegroundColor Green
            } else {
                Write-Host "  [WARN] PowerShell executed but returned exit code: $LASTEXITCODE" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "  [ERROR] PowerShell execution failed: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "  [ERROR] powershell.exe NOT FOUND in directory!" -ForegroundColor Red
        Write-Host ""
        Write-Host "  [SEVERE] System binary is missing" -ForegroundColor Red
        Write-Host "  [ACTION] Go to STEP 3 - OS Repair" -ForegroundColor Yellow
        $powershellExists = $false
    }
}

Write-Host ""

# ============================================================================
# STEP 2: Check PowerShell 7 (pwsh) as workaround
# ============================================================================

Write-Host "[STEP 2/4] Checking for PowerShell 7 (pwsh)..." -ForegroundColor Yellow
Write-Host ""

$pwshPaths = @(
    "C:\Program Files\PowerShell\7\pwsh.exe",
    "C:\Program Files (x86)\PowerShell\7\pwsh.exe",
    "$env:ProgramFiles\PowerShell\7\pwsh.exe"
)

$pwshFound = $null
foreach ($path in $pwshPaths) {
    if (Test-Path $path) {
        $pwshFound = $path
        Write-Host "  [OK] PowerShell 7 found at: $path" -ForegroundColor Green
        break
    }
}

# Also check via Get-Command
if (-not $pwshFound) {
    try {
        $pwshCmd = Get-Command pwsh -ErrorAction Stop
        $pwshFound = $pwshCmd.Source
        Write-Host "  [OK] PowerShell 7 found via PATH: $pwshFound" -ForegroundColor Green
    } catch {
        Write-Host "  [INFO] PowerShell 7 not found" -ForegroundColor Gray
    }
}

if ($pwshFound) {
    Write-Host ""
    Write-Host "  [WORKAROUND AVAILABLE] You can use PowerShell 7 instead:" -ForegroundColor Cyan
    Write-Host "    Path: $pwshFound" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "  [INFO] PowerShell 7 not installed" -ForegroundColor Gray
    Write-Host "  [NOTE] You can install it from: https://aka.ms/powershell-release-page" -ForegroundColor Gray
}

Write-Host ""

# ============================================================================
# STEP 3: OS Repair (if PowerShell missing)
# ============================================================================

if (-not $powershellExists) {
    Write-Host "[STEP 3/4] OS Repair Required..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  [ACTION REQUIRED] PowerShell is missing - OS repair needed" -ForegroundColor Red
    Write-Host ""
    
    # Check if running as admin
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    
    if ($isAdmin) {
        Write-Host "  [OK] Running as Administrator" -ForegroundColor Green
        Write-Host ""
        Write-Host "  [ACTION] Running DISM repair..." -ForegroundColor Yellow
        Write-Host "  (This may take 10-30 minutes)" -ForegroundColor Gray
        Write-Host ""
        
        Write-Host "  Running: DISM /Online /Cleanup-Image /RestoreHealth" -ForegroundColor Cyan
        try {
            $dismResult = DISM /Online /Cleanup-Image /RestoreHealth 2>&1
            Write-Host "  [OK] DISM completed" -ForegroundColor Green
            Write-Host ""
            
            Write-Host "  Running: sfc /scannow" -ForegroundColor Cyan
            $sfcResult = sfc /scannow 2>&1
            Write-Host "  [OK] SFC completed" -ForegroundColor Green
            Write-Host ""
            
            Write-Host "  [ACTION REQUIRED] REBOOT your computer now!" -ForegroundColor Yellow
            Write-Host "  After reboot, run this script again to verify PowerShell is restored" -ForegroundColor Yellow
            
        } catch {
            Write-Host "  [ERROR] Repair failed: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "  [ERROR] Requires Administrator rights" -ForegroundColor Red
        Write-Host ""
        Write-Host "  [MANUAL STEPS]:" -ForegroundColor Yellow
        Write-Host "  1. Open Command Prompt as Administrator:" -ForegroundColor Gray
        Write-Host "     Win+R → type 'cmd' → Right-click → Run as administrator" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  2. Run DISM:" -ForegroundColor Gray
        Write-Host "     DISM /Online /Cleanup-Image /RestoreHealth" -ForegroundColor White
        Write-Host "     (Wait for completion - 10-30 minutes)" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  3. Run SFC:" -ForegroundColor Gray
        Write-Host "     sfc /scannow" -ForegroundColor White
        Write-Host ""
        Write-Host "  4. Reboot and check again:" -ForegroundColor Gray
        Write-Host "     dir C:\Windows\System32\WindowsPowerShell\v1.0" -ForegroundColor White
        Write-Host ""
        Write-Host "  OR run this script as Administrator:" -ForegroundColor Cyan
        Write-Host "    Right-click PowerShell → Run as Administrator" -ForegroundColor Gray
        Write-Host "    cd C:\Projects\focus_server_automation" -ForegroundColor Gray
        Write-Host "    .\scripts\fix_powershell_missing.ps1" -ForegroundColor Gray
    }
} else {
    Write-Host "[STEP 3/4] OS Repair..." -ForegroundColor Yellow
    Write-Host "  [OK] PowerShell exists - OS repair not needed" -ForegroundColor Green
}

Write-Host ""

# ============================================================================
# STEP 4: Workarounds and Next Steps
# ============================================================================

Write-Host "[STEP 4/4] Workarounds and Next Steps..." -ForegroundColor Yellow
Write-Host ""

if ($powershellExists) {
    Write-Host "  [OK] PowerShell exists - you can use it!" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Fix VS Code:" -ForegroundColor Cyan
    Write-Host "    1. Ctrl+Shift+P → 'Terminal: Select Default Profile'" -ForegroundColor Gray
    Write-Host "    2. Choose 'PowerShell' (should auto-detect)" -ForegroundColor Gray
    Write-Host "    3. Or check settings.json for hard-coded wrong paths" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Fix GitHub Actions:" -ForegroundColor Cyan
    Write-Host "    - Runner should work now" -ForegroundColor Gray
    Write-Host "    - Or use 'shell: cmd' or 'shell: pwsh' in workflow YAML" -ForegroundColor Gray
    
} elseif ($pwshFound) {
    Write-Host "  [WORKAROUND] Use PowerShell 7 instead:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  VS Code:" -ForegroundColor Cyan
    Write-Host "    1. Ctrl+Shift+P → 'Terminal: Select Default Profile'" -ForegroundColor Gray
    Write-Host "    2. Choose 'PowerShell' (if it points to pwsh)" -ForegroundColor Gray
    Write-Host "    3. Or add new profile:" -ForegroundColor Gray
    Write-Host "       'terminal.integrated.profiles.windows': {" -ForegroundColor White
    Write-Host "         'PowerShell 7': {" -ForegroundColor White
    Write-Host "           'path': '$pwshFound'" -ForegroundColor White
    Write-Host "         }" -ForegroundColor White
    Write-Host "       }" -ForegroundColor White
    Write-Host ""
    Write-Host "  GitHub Actions:" -ForegroundColor Cyan
    Write-Host "    Use 'shell: pwsh' in workflow steps" -ForegroundColor Gray
    
} else {
    Write-Host "  [TEMPORARY WORKAROUND] Use Command Prompt or Git Bash:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  VS Code:" -ForegroundColor Cyan
    Write-Host "    1. Ctrl+Shift+P → 'Terminal: Select Default Profile'" -ForegroundColor Gray
    Write-Host "    2. Choose 'Command Prompt' or 'Git Bash'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  GitHub Actions:" -ForegroundColor Cyan
    Write-Host "    Use 'shell: cmd' or 'shell: bash' in workflow steps" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Then fix PowerShell (see STEP 3 above)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($powershellExists) {
    Write-Host "[SUCCESS] PowerShell exists and should work!" -ForegroundColor Green
    Write-Host ""
    Write-Host "If VS Code still can't find it:" -ForegroundColor Yellow
    Write-Host "  1. Check VS Code settings.json for hard-coded wrong paths" -ForegroundColor Gray
    Write-Host "  2. Reset terminal profile to auto-detect" -ForegroundColor Gray
    Write-Host "  3. Restart VS Code" -ForegroundColor Gray
} elseif ($pwshFound) {
    Write-Host "[WORKAROUND] Use PowerShell 7 ($pwshFound)" -ForegroundColor Yellow
    Write-Host "  Configure VS Code and GitHub Actions to use pwsh instead" -ForegroundColor Gray
} else {
    Write-Host "[ACTION REQUIRED] PowerShell is missing!" -ForegroundColor Red
    Write-Host ""
    Write-Host "1. Run OS repair (DISM + SFC) - see STEP 3" -ForegroundColor Yellow
    Write-Host "2. Use workarounds (cmd/bash/pwsh) - see STEP 4" -ForegroundColor Yellow
    Write-Host "3. If repair doesn't work, escalate to IT:" -ForegroundColor Yellow
    Write-Host "   'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe is missing." -ForegroundColor Gray
    Write-Host "   VS Code and GitHub Actions runner cannot start." -ForegroundColor Gray
    Write-Host "   DISM and SFC did not restore it." -ForegroundColor Gray
    Write-Host "   Need OS repair / reimage or policy change.'" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Script completed!" -ForegroundColor Green

