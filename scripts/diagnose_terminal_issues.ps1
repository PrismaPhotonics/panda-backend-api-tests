# VS Code Terminal Launch Failure Diagnostic Script
# Based on VS Code troubleshooting guide
# Run this script to diagnose terminal launch issues

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VS Code Terminal Diagnostic Tool" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$issuesFound = @()
$warnings = @()
$info = @()

# Check 1: VS Code Version
Write-Host "[1/10] Checking VS Code version..." -ForegroundColor Yellow
try {
    $vscodeVersion = code --version 2>&1 | Select-Object -First 1
    if ($vscodeVersion) {
        Write-Host "  [OK] VS Code version: $vscodeVersion" -ForegroundColor Green
        $info += "VS Code version: $vscodeVersion"
    } else {
        $warnings += "Could not determine VS Code version. Make sure 'code' command is in PATH."
    }
} catch {
    $warnings += "Could not check VS Code version: $_"
}

# Check 2: PowerShell Version
Write-Host "[2/10] Checking PowerShell versions..." -ForegroundColor Yellow
try {
    $psVersion = $PSVersionTable.PSVersion.ToString()
    Write-Host "  [OK] Current PowerShell version: $psVersion" -ForegroundColor Green
    $info += "PowerShell version: $psVersion"
    
    # Check for PowerShell Core (pwsh)
    $pwshPath = Get-Command pwsh -ErrorAction SilentlyContinue
    if ($pwshPath) {
        $pwshVersion = pwsh --version 2>&1
        Write-Host "  [OK] PowerShell Core (pwsh) found: $pwshVersion" -ForegroundColor Green
        $info += "PowerShell Core (pwsh): $pwshVersion"
    } else {
        $warnings += "PowerShell Core (pwsh) not found. Consider installing for better cross-platform support."
    }
} catch {
    $issuesFound += "Error checking PowerShell version: $_"
}

# Check 3: Windows Version
Write-Host "[3/10] Checking Windows version..." -ForegroundColor Yellow
$osVersion = [System.Environment]::OSVersion.Version
$buildNumber = (Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion" -Name CurrentBuild).CurrentBuild
Write-Host "  [OK] Windows Build: $buildNumber" -ForegroundColor Green

if ([int]$buildNumber -lt 18362) {
    $issuesFound += "Windows 10 build $buildNumber is below 1903 (18362). Consider upgrading to use ConPTY backend."
    Write-Host "  [WARN] Warning: Old Windows version may use legacy winpty backend" -ForegroundColor Yellow
} else {
    Write-Host "  [OK] Windows version supports ConPTY backend" -ForegroundColor Green
    $info += "Windows build supports ConPTY"
}

# Check 4: Compatibility Mode
Write-Host "[4/10] Checking VS Code compatibility mode..." -ForegroundColor Yellow
$vscodeExe = Get-Command code -ErrorAction SilentlyContinue
if ($vscodeExe) {
    $vscodePath = (Get-Item $vscodeExe.Source).Target
    if (-not $vscodePath) {
        $vscodePath = $vscodeExe.Source
    }
    
    $compatMode = (Get-ItemProperty -Path $vscodePath -ErrorAction SilentlyContinue).CompatibilityFlags
    if ($compatMode) {
        $issuesFound += "VS Code has compatibility mode enabled. This can break terminal functionality."
        Write-Host "  [ERROR] Compatibility mode is ENABLED - This will break terminal!" -ForegroundColor Red
    } else {
        Write-Host "  [OK] Compatibility mode is disabled" -ForegroundColor Green
    }
} else {
    $warnings += "Could not check compatibility mode. VS Code executable not found in PATH."
}

# Check 5: VS Code Settings
Write-Host "[5/10] Checking VS Code terminal settings..." -ForegroundColor Yellow
$settingsPath = "$env:APPDATA\Code\User\settings.json"
if (Test-Path $settingsPath) {
    $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json -ErrorAction SilentlyContinue
    if ($settings) {
        $terminalSettings = @(
            "terminal.integrated.defaultProfile.windows",
            "terminal.integrated.profiles.windows",
            "terminal.integrated.cwd",
            "terminal.integrated.env.windows",
            "terminal.integrated.inheritEnv",
            "terminal.integrated.automationProfile.windows",
            "terminal.integrated.windowsEnableConpty"
        )
        
        $foundSettings = @()
        foreach ($setting in $terminalSettings) {
            $prop = $setting -replace '\.', '_'
            if ($settings.PSObject.Properties.Name -contains $prop -or 
                $settings.PSObject.Properties.Name -contains $setting) {
                $foundSettings += $setting
            }
        }
        
        if ($foundSettings.Count -gt 0) {
            Write-Host "  [OK] Found $($foundSettings.Count) terminal-related settings:" -ForegroundColor Green
            foreach ($setting in $foundSettings) {
                Write-Host "    - $setting" -ForegroundColor Gray
            }
            $info += "Terminal settings found: $($foundSettings.Count)"
        } else {
            Write-Host "  [OK] No custom terminal settings found (using defaults)" -ForegroundColor Green
        }
    } else {
        $warnings += "Could not parse VS Code settings.json"
    }
} else {
    $warnings += "VS Code settings.json not found at: $settingsPath"
}

# Check 6: Anti-virus Exclusions
Write-Host "[6/10] Checking VS Code installation path..." -ForegroundColor Yellow
$vscodeInstallPath = $env:LOCALAPPDATA + "\Programs\Microsoft VS Code"
if (Test-Path $vscodeInstallPath) {
    $nodePtyPath = Join-Path $vscodeInstallPath "resources\app\node_modules.asar.unpacked\node-pty\build\Release"
    Write-Host "  [OK] VS Code installation found" -ForegroundColor Green
    
    $criticalFiles = @(
        "winpty.dll",
        "winpty-agent.exe",
        "conpty.node",
        "conpty_console_list.node"
    )
    
    $missingFiles = @()
    foreach ($file in $criticalFiles) {
        $filePath = Join-Path $nodePtyPath $file
        if (-not (Test-Path $filePath)) {
            $missingFiles += $file
        }
    }
    
    if ($missingFiles.Count -gt 0) {
        $issuesFound += "Critical terminal files missing: $($missingFiles -join ', '). Anti-virus may have blocked them."
        Write-Host "  [ERROR] Missing files (may be blocked by anti-virus):" -ForegroundColor Red
        foreach ($file in $missingFiles) {
            Write-Host "    - $file" -ForegroundColor Red
        }
        Write-Host "  -> Add VS Code folder to anti-virus exclusions" -ForegroundColor Yellow
    } else {
        Write-Host "  [OK] All critical terminal files present" -ForegroundColor Green
    }
} else {
    $warnings += "VS Code installation not found at standard location: $vscodeInstallPath"
}

# Check 7: Legacy Console Mode
Write-Host "[7/10] Checking legacy console mode..." -ForegroundColor Yellow
try {
    $legacyConsole = (Get-ItemProperty -Path "HKCU:\Console" -Name "ForceV2" -ErrorAction SilentlyContinue).ForceV2
    if ($legacyConsole -eq 0) {
        $issuesFound += "Legacy console mode is enabled. This can cause exit code 3221225786."
        Write-Host "  [ERROR] Legacy console mode is ENABLED - This can cause issues!" -ForegroundColor Red
        Write-Host "  -> Disable via: cmd.exe Properties > Options > Uncheck 'Use legacy console'" -ForegroundColor Yellow
    } else {
        Write-Host "  [OK] Legacy console mode is disabled" -ForegroundColor Green
    }
} catch {
    $warnings += "Could not check legacy console mode: $_"
}

# Check 8: Shell Availability
Write-Host "[8/10] Testing shell availability..." -ForegroundColor Yellow
$shells = @(
    @{Name="PowerShell"; Command="powershell.exe"; Args="-NoProfile -Command 'Write-Host Test'"},
    @{Name="PowerShell Core"; Command="pwsh.exe"; Args="-NoProfile -Command 'Write-Host Test'"},
    @{Name="CMD"; Command="cmd.exe"; Args="/c echo Test"},
    @{Name="Git Bash"; Command="bash.exe"; Args="--version"}
)

foreach ($shell in $shells) {
    try {
        $result = & $shell.Command $shell.Args 2>&1
        if ($LASTEXITCODE -eq 0 -or $result) {
            Write-Host "  [OK] $($shell.Name) is available" -ForegroundColor Green
            $info += "$($shell.Name) available"
        }
    } catch {
        Write-Host "  [WARN] $($shell.Name) not found or failed" -ForegroundColor Yellow
        $warnings += "$($shell.Name) not available"
    }
}

# Check 9: Environment Variables
Write-Host "[9/10] Checking critical environment variables..." -ForegroundColor Yellow
$criticalEnvVars = @("PATH", "TEMP", "TMP", "USERPROFILE")
foreach ($var in $criticalEnvVars) {
    $value = [Environment]::GetEnvironmentVariable($var)
    if ($value) {
        Write-Host "  [OK] $var is set" -ForegroundColor Green
    } else {
        $issuesFound += "Critical environment variable $var is not set"
        Write-Host "  [ERROR] $var is NOT set" -ForegroundColor Red
    }
}

# Check 10: Process Conflicts
Write-Host "[10/10] Checking for process conflicts..." -ForegroundColor Yellow
$terminalProcesses = Get-Process | Where-Object {
    $_.ProcessName -match "powershell|pwsh|cmd|bash|wsl" -and
    $_.StartTime -lt (Get-Date).AddMinutes(-30)
}
if ($terminalProcesses.Count -gt 10) {
    $warnings += "Many terminal processes running ($($terminalProcesses.Count)). May cause exit code 259."
    Write-Host "  [WARN] Found $($terminalProcesses.Count) terminal processes running" -ForegroundColor Yellow
} else {
    Write-Host "  [OK] No excessive terminal processes found" -ForegroundColor Green
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DIAGNOSTIC SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($issuesFound.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "[OK] No issues found! Your terminal configuration looks good." -ForegroundColor Green
} else {
    if ($issuesFound.Count -gt 0) {
        Write-Host "[ERROR] ISSUES FOUND ($($issuesFound.Count)):" -ForegroundColor Red
        foreach ($issue in $issuesFound) {
            Write-Host "  • $issue" -ForegroundColor Red
        }
        Write-Host ""
    }
    
    if ($warnings.Count -gt 0) {
        Write-Host "[WARN] WARNINGS ($($warnings.Count)):" -ForegroundColor Yellow
        foreach ($warning in $warnings) {
            Write-Host "  • $warning" -ForegroundColor Yellow
        }
        Write-Host ""
    }
}

if ($info.Count -gt 0) {
    Write-Host "[INFO] INFORMATION:" -ForegroundColor Cyan
    foreach ($item in $info) {
        Write-Host "  • $item" -ForegroundColor Gray
    }
    Write-Host ""
}

# Recommendations
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RECOMMENDATIONS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($issuesFound.Count -gt 0) {
    Write-Host "1. Fix the issues listed above" -ForegroundColor Yellow
    Write-Host "2. Restart VS Code after making changes" -ForegroundColor Yellow
    Write-Host "3. Enable trace logging in VS Code:" -ForegroundColor Yellow
    Write-Host "   - Open Command Palette (Ctrl+Shift+P)" -ForegroundColor Gray
    Write-Host "   - Run: 'Developer: Set Log Level'" -ForegroundColor Gray
    Write-Host "   - Select: 'Trace'" -ForegroundColor Gray
    Write-Host "   - Try opening terminal and check Output panel" -ForegroundColor Gray
} else {
    Write-Host "[OK] Your configuration looks good!" -ForegroundColor Green
    Write-Host ""
    Write-Host "If you're still experiencing issues:" -ForegroundColor Yellow
    Write-Host "1. Enable trace logging (see above)" -ForegroundColor Yellow
    Write-Host "2. Check VS Code Output panel for terminal errors" -ForegroundColor Yellow
    Write-Host "3. Try running your shell directly outside VS Code" -ForegroundColor Yellow
    Write-Host "4. Check VS Code release notes for terminal fixes" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "For more help, see:" -ForegroundColor Cyan
Write-Host "  https://code.visualstudio.com/docs/terminal/troubleshooting" -ForegroundColor Blue

