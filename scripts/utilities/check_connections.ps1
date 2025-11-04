#!/usr/bin/env pwsh
# Connection Health Check - Focus Server Automation

Write-Host ""
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host "  Connection Health Check" -ForegroundColor Cyan
Write-Host "=================================================================================" -ForegroundColor Cyan

# Load environment variables automatically
if (Test-Path ".\set_production_env.ps1") {
    Write-Host ""
    Write-Host "[0/7] Loading environment variables..." -ForegroundColor Yellow
    . .\set_production_env.ps1 | Out-Null
    Write-Host "   Environment: LOADED" -ForegroundColor Green
}

$allGood = $true

# 1. Check Virtual Environment
Write-Host ""
Write-Host "[1/7] Checking Virtual Environment..." -ForegroundColor Yellow
if ($env:VIRTUAL_ENV) {
    Write-Host "   Status: ACTIVE" -ForegroundColor Green
    Write-Host "   Path: $env:VIRTUAL_ENV" -ForegroundColor DarkGray
} else {
    Write-Host "   Status: NOT ACTIVE" -ForegroundColor Red
    Write-Host "   Run: .venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    $allGood = $false
}

# 2. Check Python Packages
Write-Host ""
Write-Host "[2/7] Checking Python Packages..." -ForegroundColor Yellow
$packages = @("pymongo", "pika", "requests", "pytest")
foreach ($pkg in $packages) {
    try {
        $version = python -c "import $pkg; print($pkg.__version__)" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   $pkg : $version" -ForegroundColor Green
        } else {
            Write-Host "   $pkg : NOT INSTALLED" -ForegroundColor Red
            $allGood = $false
        }
    } catch {
        Write-Host "   $pkg : ERROR" -ForegroundColor Red
        $allGood = $false
    }
}

# 3. Check Environment Variables
Write-Host ""
Write-Host "[3/7] Checking Environment Variables..." -ForegroundColor Yellow
if ($env:MONGODB_URI) {
    Write-Host "   MONGODB_URI: SET" -ForegroundColor Green
    Write-Host "   Value: $env:MONGODB_URI" -ForegroundColor DarkGray
} else {
    Write-Host "   MONGODB_URI: NOT SET" -ForegroundColor Red
    Write-Host "   ERROR: Environment variables failed to load!" -ForegroundColor Red
    $allGood = $false
}

# 4. Check MongoDB Connectivity
Write-Host ""
Write-Host "[4/7] Checking MongoDB Connectivity..." -ForegroundColor Yellow
$mongoTest = Test-NetConnection -ComputerName 10.10.100.108 -Port 27017 -InformationLevel Quiet -WarningAction SilentlyContinue
if ($mongoTest) {
    Write-Host "   10.10.100.108:27017 : ACCESSIBLE" -ForegroundColor Green
    
    # Test MongoDB authentication
    Write-Host "   Testing authentication..." -ForegroundColor DarkGray
    try {
        $mongoAuth = python -c "from pymongo import MongoClient; c = MongoClient('mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma', serverSelectionTimeoutMS=5000); print('OK')" 2>$null
        if ($mongoAuth -eq "OK") {
            Write-Host "   Authentication: SUCCESS" -ForegroundColor Green
        } else {
            Write-Host "   Authentication: FAILED" -ForegroundColor Red
            $allGood = $false
        }
    } catch {
        Write-Host "   Authentication: ERROR" -ForegroundColor Red
        $allGood = $false
    }
} else {
    Write-Host "   10.10.100.108:27017 : NOT ACCESSIBLE" -ForegroundColor Red
    $allGood = $false
}

# 5. Check RabbitMQ Connectivity
Write-Host ""
Write-Host "[5/7] Checking RabbitMQ Connectivity..." -ForegroundColor Yellow
$rabbitTest = Test-NetConnection -ComputerName 10.10.100.107 -Port 5672 -InformationLevel Quiet -WarningAction SilentlyContinue
if ($rabbitTest) {
    Write-Host "   10.10.100.107:5672 : ACCESSIBLE" -ForegroundColor Green
} else {
    Write-Host "   10.10.100.107:5672 : NOT ACCESSIBLE" -ForegroundColor Red
    $allGood = $false
}

$rabbitMgmtTest = Test-NetConnection -ComputerName 10.10.100.107 -Port 15672 -InformationLevel Quiet -WarningAction SilentlyContinue
if ($rabbitMgmtTest) {
    Write-Host "   10.10.100.107:15672 (Management): ACCESSIBLE" -ForegroundColor Green
} else {
    Write-Host "   10.10.100.107:15672 (Management): NOT ACCESSIBLE" -ForegroundColor Red
}

# 6. Check Backend Connectivity
Write-Host ""
Write-Host "[6/7] Checking Backend Connectivity..." -ForegroundColor Yellow
$backendTest = Test-NetConnection -ComputerName 10.10.100.100 -Port 443 -InformationLevel Quiet -WarningAction SilentlyContinue
if ($backendTest) {
    Write-Host "   10.10.100.100:443 : ACCESSIBLE" -ForegroundColor Green
} else {
    Write-Host "   10.10.100.100:443 : NOT ACCESSIBLE" -ForegroundColor Red
    $allGood = $false
}

# 7. Check Configuration Files
Write-Host ""
Write-Host "[7/7] Checking Configuration Files..." -ForegroundColor Yellow
if (Test-Path "config\environments.yaml") {
    Write-Host "   environments.yaml : EXISTS" -ForegroundColor Green
    
    $defaultEnv = Select-String -Path "config\environments.yaml" -Pattern "default_environment:" | Select-Object -First 1
    if ($defaultEnv -match "new_production") {
        Write-Host "   Default environment: new_production" -ForegroundColor Green
    } else {
        Write-Host "   Default environment: NOT new_production" -ForegroundColor Yellow
    }
} else {
    Write-Host "   environments.yaml : MISSING" -ForegroundColor Red
    $allGood = $false
}

if (Test-Path "tests\conftest.py") {
    Write-Host "   conftest.py : EXISTS" -ForegroundColor Green
} else {
    Write-Host "   conftest.py : MISSING" -ForegroundColor Red
    $allGood = $false
}

# Summary
Write-Host ""
Write-Host "=================================================================================" -ForegroundColor Cyan
if ($allGood) {
    Write-Host "  ALL CHECKS PASSED - READY TO RUN TESTS" -ForegroundColor Green
} else {
    Write-Host "  SOME CHECKS FAILED - FIX ISSUES BEFORE RUNNING TESTS" -ForegroundColor Red
}
Write-Host "=================================================================================" -ForegroundColor Cyan

# Recommendations
if (-not $allGood) {
    Write-Host ""
    Write-Host "Recommendations:" -ForegroundColor Yellow
    
    if (-not $env:VIRTUAL_ENV) {
        Write-Host "  1. Activate virtual environment:" -ForegroundColor White
        Write-Host "     .venv\Scripts\Activate.ps1" -ForegroundColor Cyan
    }
    
    if (-not $env:MONGODB_URI) {
        Write-Host "  2. ERROR: Environment variables were loaded but MONGODB_URI is still not set!" -ForegroundColor Red
        Write-Host "     Check set_production_env.ps1 for errors" -ForegroundColor Yellow
    }
    
    Write-Host "  3. Check documentation/troubleshooting/TROUBLESHOOTING_CONNECTION_ERRORS.md" -ForegroundColor White
}

Write-Host ""
