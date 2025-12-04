# Deep VS Code Structure Diagnostic
# Checks the complete VS Code installation structure

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VS Code Installation Structure Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$vscodePath = "$env:LOCALAPPDATA\Programs\Microsoft VS Code"

if (-not (Test-Path $vscodePath)) {
    Write-Host "[ERROR] VS Code installation not found at: $vscodePath" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] VS Code base path exists: $vscodePath" -ForegroundColor Green
Write-Host ""

# Check directory structure
$checkPaths = @(
    @{Path="resources"; Name="Resources folder"},
    @{Path="resources\app"; Name="App folder"},
    @{Path="resources\app\node_modules.asar.unpacked"; Name="Unpacked node_modules"},
    @{Path="resources\app\node_modules.asar.unpacked\node-pty"; Name="node-pty folder"},
    @{Path="resources\app\node_modules.asar.unpacked\node-pty\build"; Name="Build folder"},
    @{Path="resources\app\node_modules.asar.unpacked\node-pty\build\Release"; Name="Release folder"}
)

Write-Host "Checking directory structure..." -ForegroundColor Yellow
Write-Host ""

$lastExistingPath = $vscodePath
$firstMissingPath = $null

foreach ($check in $checkPaths) {
    $fullPath = Join-Path $vscodePath $check.Path
    
    if (Test-Path $fullPath) {
        Write-Host "  [OK] $($check.Name)" -ForegroundColor Green
        Write-Host "       Path: $fullPath" -ForegroundColor Gray
        $lastExistingPath = $fullPath
    } else {
        Write-Host "  [MISSING] $($check.Name)" -ForegroundColor Red
        Write-Host "       Path: $fullPath" -ForegroundColor Gray
        if (-not $firstMissingPath) {
            $firstMissingPath = $check.Path
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ANALYSIS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($firstMissingPath) {
    Write-Host "[ISSUE] Missing path detected: $firstMissingPath" -ForegroundColor Yellow
    Write-Host ""
    
    if ($firstMissingPath -eq "resources") {
        Write-Host "[SEVERE] VS Code installation is severely incomplete!" -ForegroundColor Red
        Write-Host "The entire resources folder is missing." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "SOLUTION: Complete reinstallation required" -ForegroundColor Yellow
        Write-Host "  1. Uninstall VS Code completely" -ForegroundColor Gray
        Write-Host "  2. Delete remaining folder: $vscodePath" -ForegroundColor Gray
        Write-Host "  3. Download fresh installer from: https://code.visualstudio.com/" -ForegroundColor Gray
        Write-Host "  4. Install VS Code" -ForegroundColor Gray
        Write-Host "  5. Add to antivirus exclusions BEFORE opening VS Code" -ForegroundColor Gray
        
    } elseif ($firstMissingPath -like "*node-pty*") {
        Write-Host "[ISSUE] node-pty module is missing or incomplete" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "POSSIBLE CAUSES:" -ForegroundColor Cyan
        Write-Host "  1. Antivirus removed the files during/after installation" -ForegroundColor Gray
        Write-Host "  2. Installation was interrupted" -ForegroundColor Gray
        Write-Host "  3. Corrupted installation" -ForegroundColor Gray
        Write-Host ""
        Write-Host "SOLUTION:" -ForegroundColor Yellow
        Write-Host "  1. Add VS Code to antivirus exclusions FIRST:" -ForegroundColor Yellow
        Write-Host "     Folder: $vscodePath" -ForegroundColor White
        Write-Host ""
        Write-Host "  2. Reinstall VS Code:" -ForegroundColor Yellow
        Write-Host "     - Download from: https://code.visualstudio.com/" -ForegroundColor Gray
        Write-Host "     - Run installer" -ForegroundColor Gray
        Write-Host "     - Choose 'Repair' if option available" -ForegroundColor Gray
        Write-Host "     - OR uninstall and reinstall completely" -ForegroundColor Gray
        
    } else {
        Write-Host "[ISSUE] Partial installation detected" -ForegroundColor Yellow
        Write-Host "Some folders exist but structure is incomplete." -ForegroundColor Gray
        Write-Host ""
        Write-Host "SOLUTION: Reinstall VS Code" -ForegroundColor Yellow
    }
} else {
    Write-Host "[OK] Directory structure is complete" -ForegroundColor Green
    Write-Host "The issue is only with missing files, not directory structure." -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CHECKING FOR ALTERNATIVE LOCATIONS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if files might be in asar archive
$asarPath = Join-Path $vscodePath "resources\app\node_modules.asar"
if (Test-Path $asarPath) {
    Write-Host "[INFO] Found node_modules.asar archive" -ForegroundColor Cyan
    Write-Host "  Path: $asarPath" -ForegroundColor Gray
    $asarSize = (Get-Item $asarPath).Length / 1MB
    Write-Host "  Size: $([math]::Round($asarSize, 2)) MB" -ForegroundColor Gray
    Write-Host ""
    Write-Host "[NOTE] The unpacked folder should exist alongside the .asar file" -ForegroundColor Yellow
    Write-Host "If it's missing, antivirus likely removed it." -ForegroundColor Yellow
} else {
    Write-Host "[WARN] node_modules.asar not found - installation may be corrupted" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RECOMMENDED ACTION PLAN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "STEP 1: Add Antivirus Exclusion (DO THIS FIRST!)" -ForegroundColor Yellow
Write-Host "  Folder: $vscodePath" -ForegroundColor White
Write-Host ""
Write-Host "  For Cynet:" -ForegroundColor Cyan
Write-Host "    1. Open Cynet (Windows Security > Open app)" -ForegroundColor Gray
Write-Host "    2. Find Exclusions/Exceptions/Whitelist" -ForegroundColor Gray
Write-Host "    3. Add folder: $vscodePath" -ForegroundColor Gray
Write-Host ""
Write-Host "  For Windows Defender:" -ForegroundColor Cyan
Write-Host "    1. Windows Security > Virus & threat protection" -ForegroundColor Gray
Write-Host "    2. Manage settings > Exclusions > Add folder" -ForegroundColor Gray
Write-Host "    3. Select: $vscodePath" -ForegroundColor Gray
Write-Host ""

Write-Host "STEP 2: Reinstall VS Code" -ForegroundColor Yellow
Write-Host "  1. Close VS Code completely" -ForegroundColor Gray
Write-Host "  2. Download installer: https://code.visualstudio.com/download" -ForegroundColor Gray
Write-Host "  3. Run installer" -ForegroundColor Gray
Write-Host "  4. Choose 'Repair' if available, or uninstall then reinstall" -ForegroundColor Gray
Write-Host ""

Write-Host "STEP 3: Verify Installation" -ForegroundColor Yellow
Write-Host "  Run: .\scripts\check_vscode_terminal_files.ps1" -ForegroundColor Gray
Write-Host ""

Write-Host "STEP 4: Restart VS Code" -ForegroundColor Yellow
Write-Host "  After verification, restart VS Code and try opening terminal" -ForegroundColor Gray
Write-Host ""

Write-Host "Script completed!" -ForegroundColor Green

