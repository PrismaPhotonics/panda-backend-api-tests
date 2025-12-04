# Script to check which user the runner service is running under
# Run this on PL5012 to see the service user

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Checking Runner Service User" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Get the service
$service = Get-WmiObject Win32_Service | Where-Object {$_.Name -like "*actions.runner*"}

if ($service) {
    Write-Host "Service Name: $($service.Name)" -ForegroundColor Yellow
    Write-Host "Display Name: $($service.DisplayName)" -ForegroundColor Yellow
    Write-Host "State: $($service.State)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "StartName (User): $($service.StartName)" -ForegroundColor $(if ($service.StartName -like "*SYSTEM*" -or $service.StartName -like "*PL5012$*") { "Red" } else { "Green" })
    Write-Host ""
    
    if ($service.StartName -like "*SYSTEM*") {
        Write-Host "⚠️  WARNING: Service is running under LocalSystem" -ForegroundColor Red
        Write-Host "   This means it cannot access user profile directories" -ForegroundColor Yellow
        Write-Host "   Solution: Change service to run under 'pl5012\roy.avrahami'" -ForegroundColor Yellow
    } elseif ($service.StartName -like "*PL5012$*") {
        Write-Host "⚠️  WARNING: Service is running under Machine Account (PL5012$)" -ForegroundColor Red
        Write-Host "   This means it cannot access user profile directories" -ForegroundColor Yellow
        Write-Host "   Solution: Change service to run under 'pl5012\roy.avrahami'" -ForegroundColor Yellow
    } elseif ($service.StartName -like "*roy.avrahami*") {
        Write-Host "✅ Service is running under correct user: $($service.StartName)" -ForegroundColor Green
        Write-Host "   SSH key should be at: C:\Users\roy.avrahami\.ssh\panda_staging_key" -ForegroundColor Green
    } else {
        Write-Host "ℹ️  Service is running under: $($service.StartName)" -ForegroundColor Cyan
        Write-Host "   SSH key should be at: C:\Users\$($service.StartName.Split('\')[-1])\.ssh\panda_staging_key" -ForegroundColor Cyan
    }
} else {
    Write-Host "❌ No runner service found!" -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

