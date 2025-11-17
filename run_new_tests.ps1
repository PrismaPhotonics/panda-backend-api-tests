# Run New Tests Script
# ====================
# This script runs only the 41 new tests created on 2025-11-09

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Running New Tests (41 tests)" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Activate virtual environment
if (Test-Path ".venv\Scripts\Activate.ps1") {
    . .venv\Scripts\Activate.ps1
}

# Define test paths
$testPaths = @(
    "be_focus_server_tests/integration/security/",
    "be_focus_server_tests/integration/error_handling/",
    "be_focus_server_tests/integration/performance/test_response_time.py",
    "be_focus_server_tests/integration/performance/test_concurrent_performance.py",
    "be_focus_server_tests/integration/performance/test_resource_usage.py",
    "be_focus_server_tests/integration/performance/test_database_performance.py",
    "be_focus_server_tests/integration/performance/test_network_latency.py",
    "be_focus_server_tests/integration/load/",
    "be_focus_server_tests/integration/data_quality/"
)

# Build pytest command
$pytestArgs = $testPaths + @(
    "-v",
    "--tb=short"
)

# Add optional arguments if provided
if ($args -contains "--html") {
    $pytestArgs += "--html=reports/new_tests_report.html"
    $pytestArgs += "--self-contained-html"
}

if ($args -contains "--junit") {
    $pytestArgs += "--junitxml=reports/new_tests_junit.xml"
}

if ($args -contains "--skip-health-check") {
    $pytestArgs += "--skip-health-check"
}

if ($args -contains "-x") {
    $pytestArgs += "-x"
}

# Run tests
Write-Host "Running pytest with arguments:" -ForegroundColor Yellow
Write-Host "  Test paths: $($testPaths.Count) paths" -ForegroundColor Gray
Write-Host "  Additional args: $($pytestArgs -join ' ')" -ForegroundColor Gray
Write-Host "`n" -ForegroundColor Gray

pytest $pytestArgs

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Test execution complete" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

