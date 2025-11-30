# Script to verify that runner service fix worked
# Run this after fixing the service user

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Verifying Runner Service Fix" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check service user
$service = Get-WmiObject Win32_Service | Where-Object {$_.Name -like "*actions.runner*"}
if ($service) {
    Write-Host "Service Configuration:" -ForegroundColor Yellow
    Write-Host "  Name: $($service.Name)" -ForegroundColor Gray
    Write-Host "  User: $($service.StartName)" -ForegroundColor $(if ($service.StartName -like "*roy.avrahami*") { "Green" } else { "Red" })
    Write-Host "  State: $($service.State)" -ForegroundColor $(if ($service.State -eq "Running") { "Green" } else { "Yellow" })
    Write-Host ""
    
    if ($service.StartName -like "*roy.avrahami*") {
        Write-Host "✅ Service is running under correct user!" -ForegroundColor Green
    } else {
        Write-Host "❌ Service is NOT running under correct user!" -ForegroundColor Red
    }
}

Write-Host ""

# Check SSH key location
Write-Host "Checking SSH key..." -ForegroundColor Yellow
$sshKeyPath = "C:\Users\roy.avrahami\.ssh\panda_staging_key"
if (Test-Path $sshKeyPath) {
    $keyInfo = Get-Item $sshKeyPath
    Write-Host "  [OK] SSH key found: $sshKeyPath" -ForegroundColor Green
    Write-Host "  Size: $($keyInfo.Length) bytes" -ForegroundColor Gray
    Write-Host "  Last Modified: $($keyInfo.LastWriteTime)" -ForegroundColor Gray
} else {
    Write-Host "  [FAIL] SSH key NOT found: $sshKeyPath" -ForegroundColor Red
    Write-Host "  This is required for SSH access!" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Run a workflow in GitHub Actions" -ForegroundColor White
Write-Host "  2. Check that health checks pass" -ForegroundColor White
Write-Host "  3. Verify SSH, Kubernetes, and RabbitMQ checks work" -ForegroundColor White
Write-Host ""

