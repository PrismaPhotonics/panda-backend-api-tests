# ===================================================================
# Repository Cleanup Script
# Removes directories that don't belong in this repository
# ===================================================================

Write-Host "Starting repository cleanup..." -ForegroundColor Cyan
Write-Host ""

# Directories to remove from git tracking
$directoriesToRemove = @(
    "fe_panda_tests",
    "new-gui",
    "interrogatorqa",
    "external",
    "pz",
    "logs",
    "reports"
)

Write-Host "Directories to remove from git:" -ForegroundColor Yellow
foreach ($dir in $directoriesToRemove) {
    if (Test-Path $dir) {
        Write-Host "  - $dir" -ForegroundColor Red
    } else {
        Write-Host "  - $dir (not found)" -ForegroundColor Gray
    }
}

Write-Host ""
$confirm = Read-Host "This will remove these directories from git tracking. Continue? (y/N)"

if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Cleanup cancelled." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Removing directories from git..." -ForegroundColor Yellow

foreach ($dir in $directoriesToRemove) {
    if (Test-Path $dir) {
        Write-Host "  Removing $dir..." -ForegroundColor Yellow
        git rm -r --cached $dir 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "    Removed $dir from git" -ForegroundColor Green
        } else {
            Write-Host "    $dir not tracked in git (already ignored?)" -ForegroundColor Gray
        }
    }
}

Write-Host ""
Write-Host "Cleanup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Review changes: git status" -ForegroundColor White
Write-Host "  2. Commit changes: git commit -m 'Remove unrelated projects from repository'" -ForegroundColor White
Write-Host "  3. Push changes: git push" -ForegroundColor White
Write-Host ""
Write-Host "Note: The directories will still exist locally but won't be tracked by git." -ForegroundColor Yellow
Write-Host "To delete them completely, run: Remove-Item -Recurse -Force directory-name" -ForegroundColor Yellow
