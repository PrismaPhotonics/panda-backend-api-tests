# Enhanced Logging Test Script
# ============================
# 
# This script demonstrates the new enhanced logging capabilities.

param(
    [string]$TestFile = "tests/integration/api/test_singlechannel_view_mapping.py",
    [switch]$CollectPodLogs,
    [switch]$SavePodLogs,
    [switch]$FullDebug,
    [string]$LogLevel = "INFO"
)

Write-Host "`n" -NoNewline
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "                 ENHANCED LOGGING TEST RUNNER" -ForegroundColor Yellow
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""

# Set PYTHONPATH to current directory (required for imports)
$env:PYTHONPATH = $PWD
Write-Host "→ Set PYTHONPATH to: $PWD" -ForegroundColor Gray

# Activate virtual environment
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    Write-Host "→ Activating virtual environment..." -ForegroundColor Gray
    & .\.venv\Scripts\Activate.ps1
} else {
    Write-Host "✗ Virtual environment not found!" -ForegroundColor Red
    Write-Host "  Run: python -m venv .venv" -ForegroundColor Gray
    exit 1
}

# Build pytest command
$Command = "python -m pytest `"$TestFile`" -v"

# Add log level
$Command += " -log-cli-level=$LogLevel"

# Add pod logs collection
if ($CollectPodLogs) {
    Write-Host "✓ Real-time pod logs enabled" -ForegroundColor Green
    $Command += " --collect-pod-logs"
}

if ($SavePodLogs) {
    Write-Host "✓ Save pod logs enabled" -ForegroundColor Green
    $Command += " --save-pod-logs"
}

# Full debug mode
if ($FullDebug) {
    Write-Host "✓ Full debug mode enabled" -ForegroundColor Magenta
    $Command += " --collect-pod-logs --save-pod-logs -s -log-cli-level=DEBUG"
}

Write-Host ""
Write-Host "→ Running command:" -ForegroundColor Gray
Write-Host "  $Command" -ForegroundColor DarkGray
Write-Host ""
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""

# Execute
Invoke-Expression $Command

$ExitCode = $LASTEXITCODE

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Cyan
if ($ExitCode -eq 0) {
    Write-Host "                         ✓ TESTS PASSED" -ForegroundColor Green
} else {
    Write-Host "                         ✗ TESTS FAILED" -ForegroundColor Red
}
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""

# Show log locations
if ($SavePodLogs -or $FullDebug) {
    Write-Host "📁 Pod logs saved to:" -ForegroundColor Yellow
    Write-Host "   reports\logs\pod_logs\" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "📄 Full test logs:" -ForegroundColor Yellow
Write-Host "   reports\logs\pytest_execution.log" -ForegroundColor Gray
Write-Host ""

exit $ExitCode

