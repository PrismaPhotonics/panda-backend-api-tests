# ============================================================================
# Run Automation Tests on Production (כפר סבא) - Light Mode
# ============================================================================
# This script runs automation tests on production environment
# WITHOUT heavy tests (200 jobs, outage tests)
# ============================================================================

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("all", "api", "integration", "infrastructure")]
    [string]$TestType = "all",
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipSlow = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun = $false
)

Write-Host "`n════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Run Automation on Production (כפר סבא) - Light Mode" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Build pytest command
$pytestArgs = @(
    "--env=production"
    "-m", "not capacity and not mongodb_outage and not rabbitmq_outage"
    "-v"
)

# Add test type filter
if ($TestType -ne "all") {
    $pytestArgs += "-m", $TestType
}

# Add slow filter if requested
if ($SkipSlow) {
    $pytestArgs += "-m", "not slow"
}

# Add dry run if requested
if ($DryRun) {
    $pytestArgs += "--collect-only"
    Write-Host "🔍 DRY RUN MODE - Will only collect tests, not run them" -ForegroundColor Yellow
}

# Add additional options
$pytestArgs += @(
    "-s"
    "--tb=short"
    "--log-cli-level=INFO"
)

# Display what will be run
Write-Host "🚀 Running tests on: PRODUCTION (כפר סבא)" -ForegroundColor Green
Write-Host ""
Write-Host "❌ Excluded tests:" -ForegroundColor Red
Write-Host "   • 200 Jobs Capacity Test (capacity marker)" -ForegroundColor White
Write-Host "   • MongoDB Outage Tests (mongodb_outage marker)" -ForegroundColor White
Write-Host "   • RabbitMQ Outage Tests (rabbitmq_outage marker)" -ForegroundColor White

if ($SkipSlow) {
    Write-Host "   • Slow tests (slow marker)" -ForegroundColor White
}

Write-Host ""
Write-Host "📋 Test type: $TestType" -ForegroundColor Cyan
Write-Host ""
Write-Host "Command:" -ForegroundColor Yellow
Write-Host "pytest $($pytestArgs -join ' ')" -ForegroundColor White
Write-Host ""

$continue = Read-Host "Press Enter to start (or Ctrl+C to cancel)"

# Run pytest
Write-Host "`n════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Starting Test Execution..." -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

& pytest $pytestArgs

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Tests completed successfully!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️ Some tests failed (exit code: $LASTEXITCODE)" -ForegroundColor Yellow
}

Write-Host ""

