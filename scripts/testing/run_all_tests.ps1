#!/usr/bin/env pwsh
# ============================================================================
# Run All Tests - Focus Server Automation
# ============================================================================

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("all", "unit", "integration", "api", "ui", "quick")]
    [string]$TestSuite = "all",
    
    [Parameter(Mandatory=$false)]
    [switch]$WithCoverage,
    
    [Parameter(Mandatory=$false)]
    [switch]$Parallel,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipEnvSetup
)

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  Running Focus Server Automation Tests" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

# Ensure we're in the correct directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Setup environment variables
if (-not $SkipEnvSetup) {
    Write-Host ""
    Write-Host "[1/4] Setting up environment variables..." -ForegroundColor Yellow
    . .\set_production_env.ps1
    Write-Host "Done: Environment configured" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[1/4] Skipping environment setup" -ForegroundColor Yellow
}

# Activate virtual environment if exists
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host ""
    Write-Host "[2/4] Activating virtual environment..." -ForegroundColor Yellow
    . .venv\Scripts\Activate.ps1
    Write-Host "Done: Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[2/4] No virtual environment found" -ForegroundColor Yellow
}

# Prepare pytest arguments
$pytestArgs = @()
$pytestArgs += "-v"

if ($WithCoverage) {
    $pytestArgs += "--cov=src"
    $pytestArgs += "--cov-report=html"
    $pytestArgs += "--cov-report=term"
}

if ($Parallel) {
    $xdistInstalled = python -c "import pytest_xdist" 2>$null
    if ($LASTEXITCODE -eq 0) {
        $pytestArgs += "-n"
        $pytestArgs += "auto"
        Write-Host "Parallel execution enabled" -ForegroundColor Green
    } else {
        Write-Host "Warning: pytest-xdist not installed" -ForegroundColor Yellow
    }
}

# HTML Report
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$reportPath = "reports/test_report_$timestamp.html"
$pytestArgs += "--html=$reportPath"
$pytestArgs += "--self-contained-html"

# Determine which tests to run
Write-Host ""
Write-Host "[3/4] Running tests: $TestSuite" -ForegroundColor Yellow

$testPaths = @()

switch ($TestSuite) {
    "all" {
        $testPaths += "tests/"
        $testPaths += "focus_server_api_load_tests/focus_api_tests/"
        Write-Host "Running ALL test suites..." -ForegroundColor Cyan
    }
    "unit" {
        $testPaths += "tests/unit/"
        Write-Host "Running UNIT tests only..." -ForegroundColor Cyan
    }
    "integration" {
        $testPaths += "tests/integration/"
        Write-Host "Running INTEGRATION tests only..." -ForegroundColor Cyan
    }
    "api" {
        $testPaths += "focus_server_api_load_tests/focus_api_tests/"
        Write-Host "Running API CONTRACT tests only..." -ForegroundColor Cyan
    }
    "ui" {
        $testPaths += "tests/ui/"
        Write-Host "Running UI tests only..." -ForegroundColor Cyan
    }
    "quick" {
        $testPaths += "tests/unit/"
        $pytestArgs += "-m"
        $pytestArgs += "not slow"
        Write-Host "Running QUICK tests only..." -ForegroundColor Cyan
    }
}

# Add environment flag (uses new_production by default)
$pytestArgs += "--env=new_production"

# Run pytest
$allArgs = $testPaths + $pytestArgs
Write-Host ""
Write-Host "Environment: new_production (MongoDB: 10.10.100.108)" -ForegroundColor Green
Write-Host "Command: pytest $($allArgs -join ' ')" -ForegroundColor DarkGray
Write-Host ""

$startTime = Get-Date
pytest @allArgs
$exitCode = $LASTEXITCODE
$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host ""
Write-Host "[4/4] Test execution completed" -ForegroundColor Yellow

# Summary
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
if ($exitCode -eq 0) {
    Write-Host "  ALL TESTS PASSED" -ForegroundColor Green
} else {
    Write-Host "  SOME TESTS FAILED" -ForegroundColor Red
}
Write-Host "================================================================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Execution Summary:" -ForegroundColor Yellow
Write-Host "  Test Suite:     $TestSuite" -ForegroundColor White
Write-Host "  Duration:       $($duration.TotalSeconds) seconds" -ForegroundColor White
Write-Host "  Exit Code:      $exitCode" -ForegroundColor White
Write-Host "  HTML Report:    $reportPath" -ForegroundColor White

if ($WithCoverage) {
    Write-Host "  Coverage Report: htmlcov/index.html" -ForegroundColor White
}

Write-Host ""

# Open report if tests passed
if ($exitCode -eq 0) {
    $openReport = Read-Host "Open HTML report? (y/n)"
    if ($openReport -eq "y") {
        Start-Process $reportPath
    }
}

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

exit $exitCode
