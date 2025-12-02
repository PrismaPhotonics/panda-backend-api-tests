# Script to check if VS Code terminal files are present
# Run this after adding antivirus exclusions and reinstalling VS Code

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VS Code Terminal Files Checker" -ForegroundColor Cyan
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
    exit 1
}

# Critical files to check
$releasePath = Join-Path $foundPath "resources\app\node_modules.asar.unpacked\node-pty\build\Release"
$criticalFiles = @(
    @{Name="winpty.dll"; Description="Windows PTY DLL"},
    @{Name="winpty-agent.exe"; Description="Windows PTY Agent"},
    @{Name="conpty.node"; Description="ConPTY Node Module"},
    @{Name="conpty_console_list.node"; Description="ConPTY Console List Module"}
)

Write-Host ""
Write-Host "Checking critical terminal files..." -ForegroundColor Yellow
Write-Host "Path: $releasePath" -ForegroundColor Gray
Write-Host ""

$allFilesPresent = $true
$missingFiles = @()
$presentFiles = @()

foreach ($file in $criticalFiles) {
    $filePath = Join-Path $releasePath $file.Name
    if (Test-Path $filePath) {
        $fileInfo = Get-Item $filePath
        $sizeKB = [math]::Round($fileInfo.Length / 1KB, 2)
        Write-Host "  [OK] $($file.Name)" -ForegroundColor Green -NoNewline
        Write-Host " ($sizeKB KB) - $($file.Description)" -ForegroundColor Gray
        $presentFiles += $file.Name
    } else {
        Write-Host "  [MISSING] $($file.Name)" -ForegroundColor Red -NoNewline
        Write-Host " - $($file.Description)" -ForegroundColor Gray
        $missingFiles += $file.Name
        $allFilesPresent = $false
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($allFilesPresent) {
    Write-Host "[SUCCESS] All critical terminal files are present!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your VS Code terminal should work correctly now." -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Restart VS Code" -ForegroundColor Gray
    Write-Host "  2. Try opening a terminal (Ctrl+`)" -ForegroundColor Gray
    Write-Host "  3. If it still doesn't work, check VS Code Output panel for errors" -ForegroundColor Gray
} else {
    Write-Host "[ERROR] Missing $($missingFiles.Count) critical file(s):" -ForegroundColor Red
    foreach ($file in $missingFiles) {
        Write-Host "  - $file" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "Action required:" -ForegroundColor Yellow
    Write-Host "  1. Make sure VS Code folder is added to antivirus exclusions" -ForegroundColor Yellow
    Write-Host "  2. Reinstall VS Code to restore missing files" -ForegroundColor Yellow
    Write-Host "  3. Check antivirus quarantine and restore files if found" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "VS Code folder to exclude:" -ForegroundColor Cyan
    Write-Host "  $foundPath" -ForegroundColor White
}

Write-Host ""
Write-Host "Files present: $($presentFiles.Count)/$($criticalFiles.Count)" -ForegroundColor $(if ($allFilesPresent) { "Green" } else { "Yellow" })

# Check if directory exists
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DIRECTORY CHECK" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (Test-Path $releasePath) {
    Write-Host "[OK] Release directory exists: $releasePath" -ForegroundColor Green
    
    # List all files in the directory
    $parentDir = Split-Path $releasePath -Parent
    if (Test-Path $parentDir) {
        Write-Host ""
        Write-Host "Contents of parent directory:" -ForegroundColor Gray
        Get-ChildItem $parentDir -ErrorAction SilentlyContinue | ForEach-Object {
            Write-Host "  - $($_.Name)" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "[ERROR] Release directory does not exist!" -ForegroundColor Red
    Write-Host "Path: $releasePath" -ForegroundColor Red
    Write-Host ""
    Write-Host "This suggests VS Code installation may be incomplete." -ForegroundColor Yellow
    Write-Host "Try reinstalling VS Code." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Script completed!" -ForegroundColor Green

