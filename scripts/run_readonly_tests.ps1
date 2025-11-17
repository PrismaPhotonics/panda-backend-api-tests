# Run Read-Only Tests (Safe for "waiting for fiber" state)
# =========================================================
# This script runs only read-only tests that don't require configuration
# Safe to run when system is in "waiting for fiber" state

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Running Read-Only Tests" -ForegroundColor Cyan
Write-Host "Safe for 'waiting for fiber' state" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment if exists
if (Test-Path .venv\Scripts\Activate.ps1) {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    . .venv\Scripts\Activate.ps1
} elseif (Test-Path venv\Scripts\Activate.ps1) {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    . venv\Scripts\Activate.ps1
}

# Get Python executable
$python = if (Test-Path .venv\Scripts\python.exe) { ".venv\Scripts\python.exe" } 
          elseif (Test-Path venv\Scripts\python.exe) { "venv\Scripts\python.exe" }
          else { "python" }

Write-Host ""
Write-Host "Running tests..." -ForegroundColor Green
Write-Host ""

# Run all tests in one command
$testPaths = @(
    "be_focus_server_tests/integration/api/test_api_endpoints_high_priority.py::TestHealthCheck",
    "be_focus_server_tests/integration/api/test_api_endpoints_high_priority.py::TestChannelsEndpoint",
    "be_focus_server_tests/integration/api/test_api_endpoints_high_priority.py::TestSensorsEndpoint",
    "be_focus_server_tests/integration/api/test_api_endpoints_high_priority.py::TestLiveMetadataEndpoint",
    "be_focus_server_tests/infrastructure/",
    "be_focus_server_tests/data_quality/",
    "be_focus_server_tests/unit/"
)

# Build pytest command
$pytestArgs = @(
    "-v",
    "-s",
    "--tb=short"
)

# Add test paths
foreach ($path in $testPaths) {
    $pytestArgs += $path
}

# Add filter for infrastructure and data_quality to exclude configure tests
$pytestArgs += "-k", "not configure"

# Run pytest
Write-Host "Command: pytest $($pytestArgs -join ' ')" -ForegroundColor Cyan
Write-Host ""

& $python -m pytest $pytestArgs

$exitCode = $LASTEXITCODE

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($exitCode -eq 0) {
    Write-Host "All tests completed successfully!" -ForegroundColor Green
} else {
    Write-Host "Some tests failed (exit code: $exitCode)" -ForegroundColor Red
}
Write-Host "========================================" -ForegroundColor Cyan

exit $exitCode

