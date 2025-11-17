# PZ Repository Setup Script
# ==========================
# This script cleans up and clones the PZ development repository

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "PZ Repository Setup" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

# Step 1: Clean up any existing PZ directory
Write-Host "`n[1/3] Cleaning up existing PZ directory..." -ForegroundColor Yellow

if (Test-Path "external\pz") {
    Write-Host "  - Removing external\pz directory..." -ForegroundColor Gray
    
    # Kill any git processes that might be locking files
    Get-Process git -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    
    Start-Sleep -Seconds 2
    
    # Remove directory using cmd (more reliable on Windows)
    cmd /c "rd /s /q external\pz" 2>$null
    
    Start-Sleep -Seconds 1
    
    if (Test-Path "external\pz") {
        Write-Host "  ❌ Failed to remove directory. Please close any programs accessing it." -ForegroundColor Red
        exit 1
    }
}

Write-Host "  ✅ Cleanup complete" -ForegroundColor Green

# Step 2: Clone PZ repository
Write-Host "`n[2/3] Cloning PZ repository (this will take 5-15 minutes)..." -ForegroundColor Yellow
Write-Host "  Repository: https://bitbucket.org/prismaphotonics/pz.git" -ForegroundColor Gray

try {
    git clone https://bitbucket.org/prismaphotonics/pz.git external/pz
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ❌ Clone failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  ❌ Clone failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host "  ✅ Clone complete" -ForegroundColor Green

# Step 3: Verify installation
Write-Host "`n[3/3] Verifying installation..." -ForegroundColor Yellow

if (-not (Test-Path "external\pz\microservices")) {
    Write-Host "  ❌ Microservices directory not found" -ForegroundColor Red
    exit 1
}

$microservices = Get-ChildItem "external\pz\microservices" -Directory
Write-Host "  ✅ Found $($microservices.Count) microservices" -ForegroundColor Green

# List some microservices
Write-Host "`n📦 Available Microservices (first 10):" -ForegroundColor Cyan
$microservices | Select-Object -First 10 | ForEach-Object {
    Write-Host "  - $($_.Name)" -ForegroundColor Gray
}

if ($microservices.Count -gt 10) {
    Write-Host "  ... and $($microservices.Count - 10) more" -ForegroundColor Gray
}

# Success!
Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
Write-Host "✅ PZ Repository Setup Complete!" -ForegroundColor Green
Write-Host ("=" * 80) -ForegroundColor Cyan

Write-Host "`n📖 Next steps:" -ForegroundColor Yellow
Write-Host "  1. Run tests: pytest -m pz -v" -ForegroundColor Gray
Write-Host "  2. Check status: python scripts/sync_pz_code.py --status" -ForegroundColor Gray
Write-Host "  3. Read docs: docs/PZ_INTEGRATION_GUIDE.md" -ForegroundColor Gray

