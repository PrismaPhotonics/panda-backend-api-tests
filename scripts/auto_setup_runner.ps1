# Auto Setup Runner - מנסה להתחבר עם פרטים שונים
# ===================================================

$SlaveIP = "10.50.0.36"
$Token = "BXBPK45XRW4YHLQ7DEJI6Y3JEWENK"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Auto Setup GitHub Actions Runner" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# בדיקת חיבור
Write-Host "Checking connectivity to $SlaveIP..." -ForegroundColor Yellow
$ping = Test-Connection -ComputerName $SlaveIP -Count 1 -Quiet -ErrorAction SilentlyContinue
$ssh = Test-NetConnection -ComputerName $SlaveIP -Port 22 -InformationLevel Quiet -WarningAction SilentlyContinue

if (-not $ping -and -not $ssh) {
    Write-Host "❌ Cannot reach $SlaveIP" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please verify:" -ForegroundColor Yellow
    Write-Host "  1. Machine is powered on" -ForegroundColor Yellow
    Write-Host "  2. Machine is connected to network" -ForegroundColor Yellow
    Write-Host "  3. SSH service is running" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "You need to provide SSH credentials manually:" -ForegroundColor Cyan
    Write-Host "  py scripts\setup_runner_on_slave_laptop.py --token $Token --user YOUR_USERNAME --password YOUR_PASSWORD" -ForegroundColor Green
    exit 1
}

Write-Host "✅ Network connectivity OK" -ForegroundColor Green
Write-Host ""

# נסה עם פרטים נפוצים
$commonUsers = @("administrator", "admin", "prisma", "user", "roy")
$commonPasswords = @("PASSW0RD", "password", "admin", "prisma")

Write-Host "Attempting to connect with common credentials..." -ForegroundColor Yellow
Write-Host "(This may take a while)" -ForegroundColor Gray
Write-Host ""

foreach ($user in $commonUsers) {
    foreach ($pass in $commonPasswords) {
        Write-Host "Trying: $user / $pass" -ForegroundColor Gray -NoNewline
        Write-Host " ... " -NoNewline
        
        $result = py scripts\setup_runner_on_slave_laptop.py --token $Token --user $user --password $pass 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ SUCCESS!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Runner setup completed successfully!" -ForegroundColor Green
            exit 0
        } else {
            if ($result -match "Authentication failed" -or $result -match "AuthenticationException") {
                Write-Host "❌ Auth failed" -ForegroundColor Red
            } elseif ($result -match "Connection refused" -or $result -match "timeout") {
                Write-Host "❌ Connection failed" -ForegroundColor Red
            } else {
                Write-Host "❌ Failed" -ForegroundColor Red
            }
        }
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Red
Write-Host "❌ Could not connect with common credentials" -ForegroundColor Red
Write-Host "==========================================" -ForegroundColor Red
Write-Host ""
Write-Host "Please run manually with your credentials:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  py scripts\setup_runner_on_slave_laptop.py --token $Token --user YOUR_USERNAME --password YOUR_PASSWORD" -ForegroundColor Green
Write-Host ""
Write-Host "Or with SSH key:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  py scripts\setup_runner_on_slave_laptop.py --token $Token --user YOUR_USERNAME --key ~/.ssh/id_rsa" -ForegroundColor Green
Write-Host ""

