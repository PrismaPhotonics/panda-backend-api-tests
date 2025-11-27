# Script to change runner service to run under current user
# Run this on PL5012 as administrator

param(
    [string]$ServiceUser = "pl5012\roy.avrahami",
    [string]$ServicePassword = ""
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Fixing Runner Service User" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Get the service
$service = Get-WmiObject Win32_Service | Where-Object {$_.Name -like "*actions.runner*"}

if (-not $service) {
    Write-Host "ERROR: Runner service not found!" -ForegroundColor Red
    exit 1
}

Write-Host "Current Service Configuration:" -ForegroundColor Yellow
Write-Host "  Name: $($service.Name)" -ForegroundColor Gray
Write-Host "  Display Name: $($service.DisplayName)" -ForegroundColor Gray
Write-Host "  Current User: $($service.StartName)" -ForegroundColor $(if ($service.StartName -eq "LocalSystem") { "Red" } else { "Green" })
Write-Host "  State: $($service.State)" -ForegroundColor Gray
Write-Host ""

if ($service.StartName -eq $ServiceUser) {
    Write-Host "Service is already running under $ServiceUser" -ForegroundColor Green
    exit 0
}

# Stop the service
Write-Host "Stopping service..." -ForegroundColor Yellow
$service.StopService()
Start-Sleep -Seconds 3

# Wait for service to stop
$timeout = 30
$elapsed = 0
while ($service.State -ne "Stopped" -and $elapsed -lt $timeout) {
    Start-Sleep -Seconds 1
    $elapsed++
    $service = Get-WmiObject Win32_Service | Where-Object {$_.Name -eq $service.Name}
}

if ($service.State -ne "Stopped") {
    Write-Host "WARNING: Service did not stop within timeout. Trying to continue..." -ForegroundColor Yellow
}

# Change the service user
Write-Host "Changing service user to: $ServiceUser" -ForegroundColor Yellow

if ([string]::IsNullOrEmpty($ServicePassword)) {
    Write-Host "Please enter password for $ServiceUser:" -ForegroundColor Yellow
    $securePassword = Read-Host -AsSecureString
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
    $ServicePassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
}

try {
    $result = $service.Change($null, $null, $null, $null, $null, $false, $ServiceUser, $ServicePassword)
    
    if ($result.ReturnValue -eq 0) {
        Write-Host "Service user changed successfully!" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Failed to change service user. Return code: $($result.ReturnValue)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "ERROR: Exception while changing service user: $_" -ForegroundColor Red
    exit 1
}

# Start the service
Write-Host "Starting service..." -ForegroundColor Yellow
$service.StartService()
Start-Sleep -Seconds 3

# Verify
$service = Get-WmiObject Win32_Service | Where-Object {$_.Name -eq $service.Name}
Write-Host ""
Write-Host "New Service Configuration:" -ForegroundColor Yellow
Write-Host "  Name: $($service.Name)" -ForegroundColor Gray
Write-Host "  User: $($service.StartName)" -ForegroundColor $(if ($service.StartName -eq $ServiceUser) { "Green" } else { "Red" })
Write-Host "  State: $($service.State)" -ForegroundColor $(if ($service.State -eq "Running") { "Green" } else { "Yellow" })
Write-Host ""

if ($service.StartName -eq $ServiceUser -and $service.State -eq "Running") {
    Write-Host "✅ SUCCESS: Service is now running under $ServiceUser" -ForegroundColor Green
    Write-Host ""
    Write-Host "SSH key should be at: C:\Users\roy.avrahami\.ssh\panda_staging_key" -ForegroundColor Cyan
} else {
    Write-Host "⚠️  WARNING: Service configuration may not be correct" -ForegroundColor Yellow
    Write-Host "   Please check manually:" -ForegroundColor Yellow
    Write-Host "   services.msc" -ForegroundColor Gray
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan

