# Script to help add VS Code to antivirus exclusions
# This script will show you the exact paths to exclude

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VS Code Antivirus Exclusion Helper" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Find VS Code installation
$vscodePaths = @(
    "$env:LOCALAPPDATA\Programs\Microsoft VS Code",
    "$env:ProgramFiles\Microsoft VS Code",
    "$env:ProgramFiles(x86)\Microsoft VS Code"
)

$foundPath = $null
foreach ($path in $vscodePaths) {
    if (Test-Path $path) {
        $foundPath = $path
        Write-Host "[OK] Found VS Code at: $path" -ForegroundColor Green
        break
    }
}

if (-not $foundPath) {
    Write-Host "[ERROR] Could not find VS Code installation" -ForegroundColor Red
    Write-Host "Please manually locate VS Code installation folder" -ForegroundColor Yellow
    exit 1
}

# Critical paths to exclude
$criticalPaths = @(
    $foundPath,
    "$foundPath\resources\app\node_modules.asar.unpacked\node-pty",
    "$foundPath\resources\app\node_modules.asar.unpacked\node-pty\build\Release"
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PATHS TO ADD TO ANTIVIRUS EXCLUSIONS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Add these paths to your antivirus exclusions:" -ForegroundColor Yellow
Write-Host ""

foreach ($path in $criticalPaths) {
    if (Test-Path $path) {
        Write-Host "  [OK] $path" -ForegroundColor Green
    } else {
        Write-Host "  [MISSING] $path" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "HOW TO ADD EXCLUSIONS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Cynet Endpoint Security (Most Common):" -ForegroundColor Yellow
Write-Host "  1. In Windows Security, click 'Open app' under 'Cynet Endpoint Security'" -ForegroundColor Gray
Write-Host "     OR click 'Manage providers' > Open Cynet" -ForegroundColor Gray
Write-Host "  2. Look for 'Exclusions', 'Exceptions', 'Whitelist', or 'Exclude Files/Folders'" -ForegroundColor Gray
Write-Host "  3. Add folder: $foundPath" -ForegroundColor Gray
Write-Host "  4. Check quarantine and restore VS Code files if found" -ForegroundColor Gray
Write-Host "  5. Apply changes and restart VS Code" -ForegroundColor Gray
Write-Host ""

Write-Host "Windows Defender:" -ForegroundColor Yellow
Write-Host "  1. Open Windows Security" -ForegroundColor Gray
Write-Host "  2. Virus & threat protection" -ForegroundColor Gray
Write-Host "  3. Virus & threat protection settings > Manage settings" -ForegroundColor Gray
Write-Host "  4. Exclusions > Add or remove exclusions" -ForegroundColor Gray
Write-Host "  5. Add folder > Select: $foundPath" -ForegroundColor Gray
Write-Host ""

Write-Host "Other Antivirus:" -ForegroundColor Yellow
Write-Host "  - Look for 'Exclusions', 'Exceptions', or 'Whitelist' settings" -ForegroundColor Gray
Write-Host "  - Add folder: $foundPath" -ForegroundColor Gray
Write-Host "  - Report false positive to antivirus vendor" -ForegroundColor Gray
Write-Host ""

Write-Host "After adding exclusions:" -ForegroundColor Cyan
Write-Host "  1. Restart VS Code" -ForegroundColor Yellow
Write-Host "  2. Try opening terminal again" -ForegroundColor Yellow
Write-Host "  3. If still not working, you may need to reinstall VS Code" -ForegroundColor Yellow
Write-Host ""

# Check if files exist
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CHECKING CRITICAL FILES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$releasePath = Join-Path $foundPath "resources\app\node_modules.asar.unpacked\node-pty\build\Release"
$criticalFiles = @(
    "winpty.dll",
    "winpty-agent.exe",
    "conpty.node",
    "conpty_console_list.node"
)

$missingFiles = @()
foreach ($file in $criticalFiles) {
    $filePath = Join-Path $releasePath $file
    if (Test-Path $filePath) {
        Write-Host "  [OK] $file" -ForegroundColor Green
    } else {
        Write-Host "  [MISSING] $file" -ForegroundColor Red
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "[WARN] Some files are missing. After adding antivirus exclusions:" -ForegroundColor Yellow
    Write-Host "  1. You may need to reinstall VS Code" -ForegroundColor Yellow
    Write-Host "  2. Or restore files from quarantine if antivirus quarantined them" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Script completed!" -ForegroundColor Green

