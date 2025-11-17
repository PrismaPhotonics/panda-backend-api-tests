# Environment Selection Script
# ============================
# Allows user to select environment before running tests

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("staging", "production", "local", "show")]
    [string]$Action = "show"
)

$configPath = "config/environments.yaml"

function Show-Environments {
    Write-Host "=================================================================================" -ForegroundColor Cyan
    Write-Host "Available Environments" -ForegroundColor Cyan
    Write-Host "=================================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "1. staging" -ForegroundColor Green
    Write-Host "   URL: https://10.10.10.100/focus-server/" -ForegroundColor Gray
    Write-Host "   Description: Staging environment for testing" -ForegroundColor Gray
    Write-Host "   Load Tests: ENABLED (200 jobs)" -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "2. production" -ForegroundColor Red
    Write-Host "   URL: https://10.10.100.100/focus-server/" -ForegroundColor Gray
    Write-Host "   Description: Production environment" -ForegroundColor Gray
    Write-Host "   Load Tests: DISABLED (safety)" -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "3. local" -ForegroundColor Yellow
    Write-Host "   URL: http://localhost:5000" -ForegroundColor Gray
    Write-Host "   Description: Local development environment" -ForegroundColor Gray
    Write-Host ""
    
    # Check current default
    if (Test-Path $configPath) {
        $content = Get-Content $configPath -Raw
        if ($content -match 'default_environment:\s*"(\w+)"') {
            $current = $matches[1]
            Write-Host "Current Default Environment: " -NoNewline -ForegroundColor Cyan
            Write-Host $current -ForegroundColor Green
        }
    }
    
    Write-Host ""
    Write-Host "=================================================================================" -ForegroundColor Cyan
}

function Set-Environment {
    param([string]$EnvName)
    
    if (-not (Test-Path $configPath)) {
        Write-Host "[ERROR] Config file not found: $configPath" -ForegroundColor Red
        return $false
    }
    
    # Read config
    $content = Get-Content $configPath -Raw
    
    # Validate environment exists
    if ($EnvName -notin @("staging", "production", "local")) {
        Write-Host "[ERROR] Invalid environment: $EnvName" -ForegroundColor Red
        Write-Host "Valid options: staging, production, local" -ForegroundColor Yellow
        return $false
    }
    
    # Check if environment exists in config
    if ($content -notmatch "`n  $EnvName:") {
        Write-Host "[ERROR] Environment '$EnvName' not found in config file" -ForegroundColor Red
        return $false
    }
    
    # Backup
    $backupPath = "$configPath.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item $configPath $backupPath
    Write-Host "[OK] Backup created: $backupPath" -ForegroundColor Green
    
    # Update default environment
    $newContent = $content -replace 'default_environment:\s*"[^"]*"', "default_environment: `"$EnvName`""
    
    # Write updated config
    Set-Content $configPath $newContent -Encoding UTF8
    
    Write-Host "[OK] Default environment set to: $EnvName" -ForegroundColor Green
    
    # Show environment details
    Write-Host ""
    Write-Host "Environment Details:" -ForegroundColor Cyan
    if ($EnvName -eq "staging") {
        Write-Host "  Backend URL: https://10.10.10.100/focus-server/" -ForegroundColor White
        Write-Host "  Frontend URL: https://10.10.10.100/liveView" -ForegroundColor White
        Write-Host "  Load Tests: ENABLED" -ForegroundColor Green
    } elseif ($EnvName -eq "production") {
        Write-Host "  Backend URL: https://10.10.100.100/focus-server/" -ForegroundColor White
        Write-Host "  Frontend URL: https://10.10.100.100/liveView" -ForegroundColor White
        Write-Host "  Load Tests: DISABLED" -ForegroundColor Yellow
        Write-Host "  [WARNING] Production environment - destructive tests are disabled!" -ForegroundColor Yellow
    } elseif ($EnvName -eq "local") {
        Write-Host "  Backend URL: http://localhost:5000" -ForegroundColor White
        Write-Host "  [INFO] Make sure local server is running!" -ForegroundColor Yellow
    }
    
    return $true
}

function Select-EnvironmentInteractive {
    Show-Environments
    
    Write-Host ""
    Write-Host "Select environment:" -ForegroundColor Cyan
    Write-Host "  1. staging" -ForegroundColor White
    Write-Host "  2. production" -ForegroundColor White
    Write-Host "  3. local" -ForegroundColor White
    Write-Host "  q. Cancel" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Host "Enter choice (1-3 or q)"
    
    switch ($choice) {
        "1" { Set-Environment "staging" }
        "2" { Set-Environment "production" }
        "3" { Set-Environment "local" }
        "q" { Write-Host "Cancelled" -ForegroundColor Yellow; return }
        default { Write-Host "[ERROR] Invalid choice" -ForegroundColor Red }
    }
}

# Main execution
Write-Host ""
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host "Environment Selection Tool" -ForegroundColor Cyan
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host ""

switch ($Action) {
    "show" {
        Show-Environments
        Write-Host ""
        Write-Host "To set environment, run:" -ForegroundColor Yellow
        Write-Host "  .\scripts\select_environment.ps1 -Action staging" -ForegroundColor White
        Write-Host "  .\scripts\select_environment.ps1 -Action production" -ForegroundColor White
        Write-Host "  .\scripts\select_environment.ps1 -Action local" -ForegroundColor White
        Write-Host ""
        Write-Host "Or run interactively:" -ForegroundColor Yellow
        Write-Host "  .\scripts\select_environment.ps1 -Action show" -ForegroundColor White
        Write-Host "  Then select option interactively" -ForegroundColor White
    }
    "staging" {
        if (Set-Environment "staging") {
            Write-Host ""
            Write-Host "[SUCCESS] Environment set to staging!" -ForegroundColor Green
            Write-Host "You can now run tests:" -ForegroundColor Cyan
            Write-Host "  pytest be_focus_server_tests/ -v" -ForegroundColor White
        }
    }
    "production" {
        Write-Host "[WARNING] Setting production environment!" -ForegroundColor Yellow
        Write-Host "Load tests and destructive tests are DISABLED in production." -ForegroundColor Yellow
        $confirm = Read-Host "Continue? (y/n)"
        if ($confirm -eq "y") {
            if (Set-Environment "production") {
                Write-Host ""
                Write-Host "[SUCCESS] Environment set to production!" -ForegroundColor Green
                Write-Host "[WARNING] Only safe, read-only tests will run!" -ForegroundColor Yellow
            }
        } else {
            Write-Host "Cancelled" -ForegroundColor Yellow
        }
    }
    "local" {
        if (Set-Environment "local") {
            Write-Host ""
            Write-Host "[SUCCESS] Environment set to local!" -ForegroundColor Green
            Write-Host "[INFO] Make sure local server is running on port 5000!" -ForegroundColor Yellow
        }
    }
    default {
        Select-EnvironmentInteractive
    }
}

Write-Host ""
Write-Host "=================================================================================" -ForegroundColor Cyan
