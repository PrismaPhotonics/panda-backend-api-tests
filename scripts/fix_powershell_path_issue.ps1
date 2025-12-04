# Fix PowerShell Path Issue for VS Code Terminal
# Error: 2147942402 (0x80070002) - The system cannot find the file specified

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PowerShell Path Diagnostic & Fix" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"

# Check 1: Find PowerShell executable
Write-Host "[1/5] Locating PowerShell executables..." -ForegroundColor Yellow

$powershellPaths = @(
    "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe",
    "$env:SystemRoot\SysWOW64\WindowsPowerShell\v1.0\powershell.exe",
    "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
    "C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe"
)

$foundPowershell = $null
foreach ($path in $powershellPaths) {
    if (Test-Path $path) {
        $foundPowershell = $path
        Write-Host "  [OK] Found PowerShell at: $path" -ForegroundColor Green
        $fileInfo = Get-Item $path
        Write-Host "      Size: $([math]::Round($fileInfo.Length / 1KB, 2)) KB" -ForegroundColor Gray
        Write-Host "      Modified: $($fileInfo.LastWriteTime)" -ForegroundColor Gray
        break
    }
}

if (-not $foundPowershell) {
    Write-Host "  [ERROR] PowerShell.exe not found in standard locations!" -ForegroundColor Red
    Write-Host "  [ACTION] This is unusual. Checking alternative locations..." -ForegroundColor Yellow
    
    # Try to find via Get-Command
    try {
        $psCommand = Get-Command powershell.exe -ErrorAction Stop
        $foundPowershell = $psCommand.Source
        Write-Host "  [FOUND] PowerShell found via Get-Command: $foundPowershell" -ForegroundColor Green
    } catch {
        Write-Host "  [ERROR] PowerShell not found anywhere!" -ForegroundColor Red
        Write-Host "  [ACTION REQUIRED] PowerShell may be corrupted or missing." -ForegroundColor Yellow
        Write-Host "  Consider running Windows Update or System File Checker:" -ForegroundColor Yellow
        Write-Host "    sfc /scannow" -ForegroundColor Gray
        exit 1
    }
}

# Check 2: Verify SystemRoot environment variable
Write-Host ""
Write-Host "[2/5] Checking SystemRoot environment variable..." -ForegroundColor Yellow

$systemRoot = $env:SystemRoot
if ($systemRoot) {
    Write-Host "  [OK] SystemRoot = $systemRoot" -ForegroundColor Green
    
    if (-not (Test-Path $systemRoot)) {
        Write-Host "  [ERROR] SystemRoot path does not exist!" -ForegroundColor Red
        Write-Host "  [ACTION] This indicates a serious system issue." -ForegroundColor Yellow
    } else {
        Write-Host "  [OK] SystemRoot path exists" -ForegroundColor Green
    }
} else {
    Write-Host "  [ERROR] SystemRoot environment variable is not set!" -ForegroundColor Red
    Write-Host "  [ACTION] This is a critical system issue." -ForegroundColor Yellow
}

# Check 3: Check VS Code settings
Write-Host ""
Write-Host "[3/5] Checking VS Code terminal settings..." -ForegroundColor Yellow

$settingsPath = "$env:APPDATA\Code\User\settings.json"
if (Test-Path $settingsPath) {
    Write-Host "  [OK] Found VS Code settings.json" -ForegroundColor Green
    
    try {
        $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json -ErrorAction Stop
        
        # Check for terminal profile settings
        $terminalProfile = $settings.'terminal.integrated.profiles.windows'
        $defaultProfile = $settings.'terminal.integrated.defaultProfile.windows'
        
        if ($terminalProfile) {
            Write-Host "  [INFO] Custom terminal profiles found" -ForegroundColor Cyan
            Write-Host "  [ACTION] Checking profile paths..." -ForegroundColor Yellow
            
            if ($terminalProfile.PSObject.Properties.Name -contains 'PowerShell') {
                $psProfile = $terminalProfile.PowerShell
                if ($psProfile.path) {
                    Write-Host "    PowerShell profile path: $($psProfile.path)" -ForegroundColor Gray
                    if (Test-Path $psProfile.path) {
                        Write-Host "    [OK] Path exists" -ForegroundColor Green
                    } else {
                        Write-Host "    [ERROR] Path does not exist!" -ForegroundColor Red
                        Write-Host "    [FIX] Updating to correct path..." -ForegroundColor Yellow
                        
                        # Fix the path
                        $psProfile.path = $foundPowershell
                        Write-Host "    [OK] Updated to: $foundPowershell" -ForegroundColor Green
                    }
                }
            }
        } else {
            Write-Host "  [INFO] No custom terminal profiles (using defaults)" -ForegroundColor Gray
        }
        
        if ($defaultProfile) {
            Write-Host "  [INFO] Default profile: $defaultProfile" -ForegroundColor Cyan
        }
        
    } catch {
        Write-Host "  [WARN] Could not parse settings.json: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [INFO] VS Code settings.json not found (will be created)" -ForegroundColor Gray
}

# Check 4: Test PowerShell execution
Write-Host ""
Write-Host "[4/5] Testing PowerShell execution..." -ForegroundColor Yellow

try {
    $testResult = & $foundPowershell -NoProfile -Command "Write-Host 'Test'; exit 0" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] PowerShell executes successfully" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] PowerShell executed but returned exit code: $LASTEXITCODE" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [ERROR] PowerShell execution failed: $_" -ForegroundColor Red
}

# Check 5: Generate fix
Write-Host ""
Write-Host "[5/5] Generating VS Code settings fix..." -ForegroundColor Yellow

$fixSettings = @{
    "terminal.integrated.defaultProfile.windows" = "PowerShell"
    "terminal.integrated.profiles.windows" = @{
        "PowerShell" = @{
            "path" = $foundPowershell
            "args" = @("-NoProfile")
        }
    }
}

Write-Host "  [INFO] Recommended VS Code settings:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Add to settings.json:" -ForegroundColor Yellow
Write-Host "  {" -ForegroundColor Gray
Write-Host "    `"terminal.integrated.defaultProfile.windows`": `"PowerShell`"," -ForegroundColor Gray
Write-Host "    `"terminal.integrated.profiles.windows`": {" -ForegroundColor Gray
Write-Host "      `"PowerShell`": {" -ForegroundColor Gray
Write-Host "        `"path`": `"$foundPowershell`"," -ForegroundColor Gray
Write-Host "        `"args`": [`"-NoProfile`"]" -ForegroundColor Gray
Write-Host "      }" -ForegroundColor Gray
Write-Host "    }" -ForegroundColor Gray
Write-Host "  }" -ForegroundColor Gray
Write-Host ""

# Ask if user wants to apply fix
Write-Host "  Do you want to apply this fix to VS Code settings? (Y/N)" -ForegroundColor Cyan
$response = Read-Host

if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host "  [ACTION] Applying fix..." -ForegroundColor Yellow
    
    try {
        # Read current settings
        if (Test-Path $settingsPath) {
            $settingsContent = Get-Content $settingsPath -Raw
            $currentSettings = $settingsContent | ConvertFrom-Json -ErrorAction Stop
        } else {
            $currentSettings = New-Object PSObject
        }
        
        # Convert to hashtable for easier manipulation
        $settingsHash = @{}
        $currentSettings.PSObject.Properties | ForEach-Object {
            $settingsHash[$_.Name] = $_.Value
        }
        
        # Add/update terminal settings
        $settingsHash['terminal.integrated.defaultProfile.windows'] = 'PowerShell'
        
        # Handle profiles
        if (-not $settingsHash.ContainsKey('terminal.integrated.profiles.windows')) {
            $settingsHash['terminal.integrated.profiles.windows'] = @{}
        }
        
        # Convert profiles to hashtable if it's a PSCustomObject
        if ($settingsHash['terminal.integrated.profiles.windows'] -is [PSCustomObject]) {
            $profilesHash = @{}
            $settingsHash['terminal.integrated.profiles.windows'].PSObject.Properties | ForEach-Object {
                $profilesHash[$_.Name] = $_.Value
            }
            $settingsHash['terminal.integrated.profiles.windows'] = $profilesHash
        }
        
        # Add PowerShell profile
        $settingsHash['terminal.integrated.profiles.windows']['PowerShell'] = @{
            path = $foundPowershell
            args = @('-NoProfile')
        }
        
        # Convert back to JSON with proper formatting
        $jsonContent = $settingsHash | ConvertTo-Json -Depth 10 -Compress:$false
        
        # Create backup
        $backupPath = "$settingsPath.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"
        if (Test-Path $settingsPath) {
            Copy-Item $settingsPath $backupPath -Force
            Write-Host "  [INFO] Backup created: $backupPath" -ForegroundColor Gray
        }
        
        # Save settings
        $jsonContent | Set-Content $settingsPath -Encoding UTF8 -NoNewline
        
        Write-Host "  [OK] Settings updated successfully!" -ForegroundColor Green
        Write-Host "  [ACTION] Please restart VS Code for changes to take effect" -ForegroundColor Yellow
        
    } catch {
        Write-Host "  [ERROR] Could not update settings: $_" -ForegroundColor Red
        Write-Host "  [ACTION] Please update settings.json manually" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  Manual fix:" -ForegroundColor Yellow
        Write-Host "  1. Open: $settingsPath" -ForegroundColor Gray
        Write-Host "  2. Add the settings shown above" -ForegroundColor Gray
    }
} else {
    Write-Host "  [SKIPPED] Fix not applied" -ForegroundColor Yellow
    Write-Host "  [ACTION] Please update settings.json manually using the settings above" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "PowerShell Location: $foundPowershell" -ForegroundColor Cyan
Write-Host "SystemRoot: $systemRoot" -ForegroundColor Cyan
Write-Host ""

Write-Host "If the issue persists:" -ForegroundColor Yellow
Write-Host "  1. Restart VS Code" -ForegroundColor Gray
Write-Host "  2. Check VS Code Output panel for more details" -ForegroundColor Gray
Write-Host "  3. Try running PowerShell directly: $foundPowershell" -ForegroundColor Gray
Write-Host "  4. Check Windows Event Viewer for system errors" -ForegroundColor Gray

Write-Host ""
Write-Host "Script completed!" -ForegroundColor Green

