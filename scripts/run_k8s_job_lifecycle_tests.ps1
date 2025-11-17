# Run K8s Job Lifecycle Tests
# ============================
# This script runs all K8s job lifecycle tests with detailed logging and monitoring

param(
    [switch]$SkipHealthCheck = $false,
    [string]$LogLevel = "INFO",
    [switch]$Verbose = $false
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "K8s Job Lifecycle Tests Runner" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to project root
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

Write-Host "Project Root: $projectRoot" -ForegroundColor Gray
Write-Host ""

# Build pytest command
$pytestArgs = @(
    "be_focus_server_tests/infrastructure/test_k8s_job_lifecycle.py"
    "-v"
    "--tb=short"
    "--log-cli-level=$LogLevel"
    "--log-cli-format=`"%(asctime)s [%(levelname)8s] %(name)s: %(message)s`""
    "--log-cli-date-format=`"%Y-%m-%d %H:%M:%S`""
)

if ($SkipHealthCheck) {
    $pytestArgs += "--skip-health-check"
}

if ($Verbose) {
    $pytestArgs += "-s"
}

Write-Host "Running pytest with arguments:" -ForegroundColor Yellow
Write-Host "  $($pytestArgs -join ' ')" -ForegroundColor Gray
Write-Host ""

# Run tests
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Test Execution..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$startTime = Get-Date

try {
    $output = py -m pytest $pytestArgs 2>&1
    $exitCode = $LASTEXITCODE
    
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Test Execution Completed" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Display output
    $output | Write-Host
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Summary" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Exit Code: $exitCode" -ForegroundColor $(if ($exitCode -eq 0) { "Green" } else { "Red" })
    Write-Host "Duration: $($duration.ToString('mm\:ss'))" -ForegroundColor Gray
    Write-Host ""
    
    # Parse results
    $passedCount = ($output | Select-String -Pattern "passed" | Select-Object -First 1).ToString()
    $failedCount = ($output | Select-String -Pattern "failed" | Select-Object -First 1).ToString()
    $skippedCount = ($output | Select-String -Pattern "skipped" | Select-Object -First 1).ToString()
    
    if ($passedCount) {
        Write-Host "✅ $passedCount" -ForegroundColor Green
    }
    if ($failedCount) {
        Write-Host "❌ $failedCount" -ForegroundColor Red
    }
    if ($skippedCount) {
        Write-Host "⏭️  $skippedCount" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "Log files saved to:" -ForegroundColor Gray
    Write-Host "  logs\test_runs\" -ForegroundColor Gray
    Write-Host ""
    
    # Exit with pytest exit code
    exit $exitCode
    
} catch {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Error Running Tests" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    exit 1
}

