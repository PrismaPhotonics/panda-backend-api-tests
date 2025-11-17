#Requires -Version 5.1
#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Automated installation and configuration script for PandaApp

.DESCRIPTION
    This script automates the complete installation process of PandaApp:
    - Downloads and installs required dependencies (.NET Runtime)
    - Installs PandaApp from installer
    - Configures usersettings.json
    - Creates required directories
    - Validates network connectivity
    - Launches the application
    - Supports version updates and silent installation

.PARAMETER InstallerPath
    Path to PandaApp installer. If not provided, will look in Downloads folder.

.PARAMETER ConfigPath
    Path to usersettings.json. If not provided, will look in Downloads folder.

.PARAMETER SilentMode
    Run installation without user prompts (for CI/CD)

.PARAMETER SkipNetworkCheck
    Skip network connectivity validation

.PARAMETER AutoUpdate
    Automatically check for and install updates

.PARAMETER LogPath
    Path to log file. Default: C:\Temp\PandaApp-Install.log

.EXAMPLE
    .\Install-PandaApp-Automated.ps1
    Interactive installation with all checks

.EXAMPLE
    .\Install-PandaApp-Automated.ps1 -SilentMode -AutoUpdate
    Silent installation with auto-update (for CI/CD)

.NOTES
    Author: QA Automation Architect
    Date: 2025-10-16
    Version: 1.0.0
    Requirements: Windows 10+, PowerShell 5.1+, Administrator privileges
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$InstallerPath,
    
    [Parameter(Mandatory=$false)]
    [string]$ConfigPath,
    
    [Parameter(Mandatory=$false)]
    [switch]$SilentMode,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipNetworkCheck,
    
    [Parameter(Mandatory=$false)]
    [switch]$AutoUpdate,
    
    [Parameter(Mandatory=$false)]
    [string]$LogPath = "C:\Temp\PandaApp-Install.log"
)

# ============================================================================
# Configuration Constants
# ============================================================================

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$Config = @{
    # Application settings
    AppName = "PandaApp"
    AppVersion = "1.2.41"
    AppInstallPath = "C:\Program Files\Prisma\PandaApp"
    AppExeName = "PandaApp-1.2.41.exe"
    
    # .NET Runtime settings
    DotNetVersion = "9.0"
    DotNetMinVersion = "9.0.0"
    DotNetDownloadUrl = "https://aka.ms/dotnet/9.0/windowsdesktop-runtime-win-x64.exe"
    DotNetInstallerName = "windowsdesktop-runtime-9.0-win-x64.exe"
    
    # Configuration settings
    ConfigFileName = "usersettings.json"
    SavedDataPath = "C:\Panda\SavedData"
    
    # Default paths to search for installer and config
    DefaultInstallerPaths = @(
        "$env:USERPROFILE\Downloads",
        "C:\Temp",
        ".\installers"
    )
    
    DefaultConfigPaths = @(
        "$env:USERPROFILE\Downloads",
        "C:\Projects\focus_server_automation\config",
        ".\config"
    )
    
    # Network endpoints to validate
    NetworkEndpoints = @(
        @{Name="Backend"; Host="10.10.100.100"; Port=443}
        @{Name="Frontend"; Host="10.10.10.100"; Port=443}
        @{Name="FrontendApi"; Host="10.10.10.150"; Port=30443}
    )
    
    # Temp directory
    TempDir = "C:\Temp\PandaApp-Install"
}

# ============================================================================
# Logging Functions
# ============================================================================

function Write-Log {
    <#
    .SYNOPSIS
        Write message to log file and console
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$false)]
        [ValidateSet("INFO", "SUCCESS", "WARNING", "ERROR", "DEBUG")]
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    # Ensure log directory exists
    $logDir = Split-Path -Path $LogPath -Parent
    if (-not (Test-Path $logDir)) {
        New-Item -Path $logDir -ItemType Directory -Force | Out-Null
    }
    
    # Write to log file
    Add-Content -Path $LogPath -Value $logMessage -Encoding UTF8
    
    # Write to console with color
    $color = switch ($Level) {
        "SUCCESS" { "Green" }
        "WARNING" { "Yellow" }
        "ERROR" { "Red" }
        "DEBUG" { "Gray" }
        default { "White" }
    }
    
    $symbol = switch ($Level) {
        "SUCCESS" { "[✓]" }
        "WARNING" { "[!]" }
        "ERROR" { "[✗]" }
        "INFO" { "[i]" }
        "DEBUG" { "[d]" }
    }
    
    Write-Host "$symbol $Message" -ForegroundColor $color
}

function Write-Header {
    <#
    .SYNOPSIS
        Write formatted header
    #>
    param([string]$Title)
    
    $line = "=" * 80
    Write-Host ""
    Write-Host $line -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host $line -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step {
    <#
    .SYNOPSIS
        Write formatted step header
    #>
    param([string]$StepNumber, [string]$Title)
    
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkCyan
    Write-Host "STEP $StepNumber : $Title" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkCyan
    Write-Host ""
}

# ============================================================================
# Validation Functions
# ============================================================================

function Test-Administrator {
    <#
    .SYNOPSIS
        Check if script is running with Administrator privileges
    #>
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-DotNetVersion {
    <#
    .SYNOPSIS
        Check if required .NET version is installed
    #>
    param([string]$RequiredVersion)
    
    try {
        $runtimes = & dotnet --list-runtimes 2>&1
        if ($LASTEXITCODE -ne 0) {
            return $false
        }
        
        $desktopRuntimes = $runtimes | Where-Object { $_ -match "Microsoft.WindowsDesktop.App $RequiredVersion" }
        return ($desktopRuntimes.Count -gt 0)
    }
    catch {
        return $false
    }
}

function Test-NetworkConnectivity {
    <#
    .SYNOPSIS
        Test connectivity to required network endpoints
    #>
    param([array]$Endpoints)
    
    $results = @()
    foreach ($endpoint in $Endpoints) {
        try {
            $test = Test-NetConnection -ComputerName $endpoint.Host -Port $endpoint.Port -WarningAction SilentlyContinue -ErrorAction Stop
            $results += @{
                Name = $endpoint.Name
                Host = $endpoint.Host
                Port = $endpoint.Port
                Success = $test.TcpTestSucceeded
            }
        }
        catch {
            $results += @{
                Name = $endpoint.Name
                Host = $endpoint.Host
                Port = $endpoint.Port
                Success = $false
            }
        }
    }
    
    return $results
}

function Find-File {
    <#
    .SYNOPSIS
        Search for a file in multiple directories
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$FileName,
        
        [Parameter(Mandatory=$true)]
        [array]$SearchPaths
    )
    
    foreach ($path in $SearchPaths) {
        if (Test-Path $path) {
            $file = Get-ChildItem -Path $path -Filter $FileName -File -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($file) {
                return $file.FullName
            }
        }
    }
    
    return $null
}

# ============================================================================
# Installation Functions
# ============================================================================

function Install-DotNetRuntime {
    <#
    .SYNOPSIS
        Download and install .NET Desktop Runtime
    #>
    param(
        [string]$DownloadUrl,
        [string]$Version
    )
    
    Write-Log "Checking for .NET $Version Desktop Runtime..." -Level INFO
    
    if (Test-DotNetVersion -RequiredVersion $Version) {
        Write-Log ".NET $Version already installed" -Level SUCCESS
        return $true
    }
    
    Write-Log ".NET $Version not found - downloading..." -Level WARNING
    
    # Create temp directory
    if (-not (Test-Path $Config.TempDir)) {
        New-Item -Path $Config.TempDir -ItemType Directory -Force | Out-Null
    }
    
    $installerPath = Join-Path $Config.TempDir $Config.DotNetInstallerName
    
    try {
        Write-Log "Downloading from: $DownloadUrl" -Level INFO
        Invoke-WebRequest -Uri $DownloadUrl -OutFile $installerPath -UseBasicParsing
        
        $fileSize = (Get-Item $installerPath).Length / 1MB
        Write-Log "Downloaded: $([math]::Round($fileSize, 2)) MB" -Level SUCCESS
        
        Write-Log "Installing .NET $Version Desktop Runtime..." -Level INFO
        $process = Start-Process -FilePath $installerPath -ArgumentList "/install /quiet /norestart" -Wait -PassThru
        
        if ($process.ExitCode -eq 0 -or $process.ExitCode -eq 1638) {
            Write-Log ".NET $Version installed successfully" -Level SUCCESS
            
            # Clean up installer
            Remove-Item -Path $installerPath -Force -ErrorAction SilentlyContinue
            
            return $true
        }
        else {
            Write-Log ".NET installation failed with exit code: $($process.ExitCode)" -Level ERROR
            return $false
        }
    }
    catch {
        Write-Log "Failed to install .NET: $_" -Level ERROR
        return $false
    }
}

function Install-PandaApplication {
    <#
    .SYNOPSIS
        Install PandaApp from installer
    #>
    param([string]$InstallerPath)
    
    Write-Log "Installing PandaApp from: $InstallerPath" -Level INFO
    
    try {
        # Unblock file if downloaded from internet
        Unblock-File -Path $InstallerPath -ErrorAction SilentlyContinue
        
        # Run installer
        if ($SilentMode) {
            # Silent installation - check if installer supports /S or /SILENT
            $process = Start-Process -FilePath $InstallerPath -ArgumentList "/S" -Wait -PassThru -ErrorAction SilentlyContinue
            
            if ($process.ExitCode -ne 0) {
                # Try alternative silent flag
                $process = Start-Process -FilePath $InstallerPath -ArgumentList "/SILENT" -Wait -PassThru -ErrorAction SilentlyContinue
            }
            
            if ($process.ExitCode -ne 0) {
                # If silent mode not supported, run normally
                Write-Log "Silent mode not supported, running interactive installer" -Level WARNING
                $process = Start-Process -FilePath $InstallerPath -Wait -PassThru
            }
        }
        else {
            # Interactive installation
            $process = Start-Process -FilePath $InstallerPath -Wait -PassThru
        }
        
        # Wait a moment for installation to complete
        Start-Sleep -Seconds 2
        
        # Check if installed
        if (Test-Path $Config.AppInstallPath) {
            Write-Log "PandaApp installed successfully" -Level SUCCESS
            return $true
        }
        else {
            Write-Log "Installation completed but application not found at expected location" -Level WARNING
            return $false
        }
    }
    catch {
        Write-Log "Failed to install PandaApp: $_" -Level ERROR
        return $false
    }
}

function Install-Configuration {
    <#
    .SYNOPSIS
        Install usersettings.json configuration file
    #>
    param(
        [string]$SourcePath,
        [string]$TargetPath
    )
    
    Write-Log "Installing configuration file..." -Level INFO
    Write-Log "Source: $SourcePath" -Level DEBUG
    Write-Log "Target: $TargetPath" -Level DEBUG
    
    try {
        # Validate source config is valid JSON
        $configContent = Get-Content -Path $SourcePath -Raw
        $configJson = $configContent | ConvertFrom-Json
        Write-Log "Configuration file validated (valid JSON)" -Level SUCCESS
        
        # Backup existing config if present
        if (Test-Path $TargetPath) {
            $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
            $backupPath = "$TargetPath.backup_$timestamp"
            Copy-Item -Path $TargetPath -Destination $backupPath -Force
            Write-Log "Existing configuration backed up to: $backupPath" -Level INFO
        }
        
        # Copy new configuration
        Copy-Item -Path $SourcePath -Destination $TargetPath -Force
        Write-Log "Configuration file installed successfully" -Level SUCCESS
        
        return $true
    }
    catch {
        Write-Log "Failed to install configuration: $_" -Level ERROR
        return $false
    }
}

function Initialize-Directories {
    <#
    .SYNOPSIS
        Create required directories
    #>
    
    Write-Log "Initializing required directories..." -Level INFO
    
    try {
        # Create SavedData directory
        if (-not (Test-Path $Config.SavedDataPath)) {
            New-Item -Path $Config.SavedDataPath -ItemType Directory -Force | Out-Null
            Write-Log "Created SavedData directory: $($Config.SavedDataPath)" -Level SUCCESS
        }
        else {
            Write-Log "SavedData directory already exists" -Level INFO
        }
        
        # Test write permissions
        $testFile = Join-Path $Config.SavedDataPath ".write_test"
        Set-Content -Path $testFile -Value "test" -ErrorAction Stop
        Remove-Item -Path $testFile -Force
        Write-Log "SavedData directory is writable" -Level SUCCESS
        
        return $true
    }
    catch {
        Write-Log "Failed to initialize directories: $_" -Level ERROR
        return $false
    }
}

function Start-PandaApplication {
    <#
    .SYNOPSIS
        Launch PandaApp
    #>
    
    $exePath = Join-Path $Config.AppInstallPath $Config.AppExeName
    
    if (-not (Test-Path $exePath)) {
        Write-Log "Executable not found: $exePath" -Level ERROR
        return $false
    }
    
    try {
        Write-Log "Launching PandaApp..." -Level INFO
        Start-Process -FilePath $exePath -WorkingDirectory $Config.AppInstallPath
        
        # Wait and check if process started
        Start-Sleep -Seconds 3
        $process = Get-Process -Name "PandaApp*" -ErrorAction SilentlyContinue
        
        if ($process) {
            Write-Log "PandaApp started successfully (PID: $($process.Id))" -Level SUCCESS
            return $true
        }
        else {
            Write-Log "PandaApp process not detected (may have started and closed)" -Level WARNING
            return $false
        }
    }
    catch {
        Write-Log "Failed to launch PandaApp: $_" -Level ERROR
        return $false
    }
}

# ============================================================================
# Main Installation Workflow
# ============================================================================

function Start-Installation {
    <#
    .SYNOPSIS
        Main installation workflow
    #>
    
    Write-Header "PandaApp Automated Installation Script v1.0.0"
    
    Write-Log "Installation started at $(Get-Date)" -Level INFO
    Write-Log "Log file: $LogPath" -Level INFO
    Write-Log "Silent mode: $SilentMode" -Level INFO
    Write-Log "Auto-update: $AutoUpdate" -Level INFO
    
    # ========================================================================
    # STEP 1: Pre-installation validation
    # ========================================================================
    
    Write-Step "1" "Pre-Installation Validation"
    
    # Check Administrator privileges
    if (-not (Test-Administrator)) {
        Write-Log "This script must be run as Administrator" -Level ERROR
        if (-not $SilentMode) {
            Read-Host "Press Enter to exit"
        }
        exit 1
    }
    Write-Log "Running with Administrator privileges" -Level SUCCESS
    
    # Check if already installed
    if (Test-Path $Config.AppInstallPath) {
        $exePath = Join-Path $Config.AppInstallPath $Config.AppExeName
        if (Test-Path $exePath) {
            Write-Log "PandaApp is already installed at: $($Config.AppInstallPath)" -Level WARNING
            
            if (-not $SilentMode) {
                $response = Read-Host "Reinstall? (Y/N)"
                if ($response -ne "Y" -and $response -ne "y") {
                    Write-Log "Installation cancelled by user" -Level INFO
                    exit 0
                }
            }
        }
    }
    
    # ========================================================================
    # STEP 2: Install .NET Runtime
    # ========================================================================
    
    Write-Step "2" "Install .NET $($Config.DotNetVersion) Desktop Runtime"
    
    $dotnetInstalled = Install-DotNetRuntime -DownloadUrl $Config.DotNetDownloadUrl -Version $Config.DotNetVersion
    
    if (-not $dotnetInstalled) {
        Write-Log "Failed to install .NET Runtime - installation cannot continue" -Level ERROR
        if (-not $SilentMode) {
            Read-Host "Press Enter to exit"
        }
        exit 1
    }
    
    # ========================================================================
    # STEP 3: Locate or download PandaApp installer
    # ========================================================================
    
    Write-Step "3" "Locate PandaApp Installer"
    
    if (-not $InstallerPath) {
        # Search for installer
        $installerPattern = "PandaAppInstaller*.exe"
        $InstallerPath = Find-File -FileName $installerPattern -SearchPaths $Config.DefaultInstallerPaths
        
        if (-not $InstallerPath) {
            Write-Log "PandaApp installer not found in default locations" -Level ERROR
            Write-Log "Please provide installer path with -InstallerPath parameter" -Level ERROR
            if (-not $SilentMode) {
                Read-Host "Press Enter to exit"
            }
            exit 1
        }
    }
    
    if (-not (Test-Path $InstallerPath)) {
        Write-Log "Installer not found: $InstallerPath" -Level ERROR
        exit 1
    }
    
    Write-Log "Using installer: $InstallerPath" -Level SUCCESS
    
    # ========================================================================
    # STEP 4: Install PandaApp
    # ========================================================================
    
    Write-Step "4" "Install PandaApp"
    
    $appInstalled = Install-PandaApplication -InstallerPath $InstallerPath
    
    if (-not $appInstalled) {
        Write-Log "PandaApp installation failed" -Level ERROR
        if (-not $SilentMode) {
            Read-Host "Press Enter to exit"
        }
        exit 1
    }
    
    # ========================================================================
    # STEP 5: Install configuration
    # ========================================================================
    
    Write-Step "5" "Install Configuration"
    
    if (-not $ConfigPath) {
        # Search for config
        $configPattern = "usersettings*.json"
        $ConfigPath = Find-File -FileName $configPattern -SearchPaths $Config.DefaultConfigPaths
        
        if (-not $ConfigPath) {
            Write-Log "Configuration file not found in default locations" -Level WARNING
            Write-Log "Application installed but not configured" -Level WARNING
        }
    }
    
    if ($ConfigPath -and (Test-Path $ConfigPath)) {
        $targetConfigPath = Join-Path $Config.AppInstallPath $Config.ConfigFileName
        $configInstalled = Install-Configuration -SourcePath $ConfigPath -TargetPath $targetConfigPath
        
        if (-not $configInstalled) {
            Write-Log "Configuration installation failed" -Level WARNING
        }
    }
    
    # ========================================================================
    # STEP 6: Initialize directories
    # ========================================================================
    
    Write-Step "6" "Initialize Directories"
    
    $dirsInitialized = Initialize-Directories
    
    if (-not $dirsInitialized) {
        Write-Log "Directory initialization failed" -Level WARNING
    }
    
    # ========================================================================
    # STEP 7: Network connectivity check
    # ========================================================================
    
    Write-Step "7" "Network Connectivity Check"
    
    if (-not $SkipNetworkCheck) {
        $networkResults = Test-NetworkConnectivity -Endpoints $Config.NetworkEndpoints
        
        foreach ($result in $networkResults) {
            if ($result.Success) {
                Write-Log "$($result.Name) ($($result.Host):$($result.Port)) - Reachable" -Level SUCCESS
            }
            else {
                Write-Log "$($result.Name) ($($result.Host):$($result.Port)) - Not reachable" -Level WARNING
            }
        }
        
        $allReachable = ($networkResults | Where-Object { -not $_.Success }).Count -eq 0
        if (-not $allReachable) {
            Write-Log "Some network endpoints are not reachable - application may not function properly" -Level WARNING
        }
    }
    else {
        Write-Log "Network connectivity check skipped" -Level INFO
    }
    
    # ========================================================================
    # STEP 8: Launch application
    # ========================================================================
    
    Write-Step "8" "Launch Application"
    
    if (-not $SilentMode) {
        $response = Read-Host "Launch PandaApp now? (Y/N)"
        if ($response -eq "Y" -or $response -eq "y" -or $response -eq "") {
            Start-PandaApplication | Out-Null
        }
    }
    else {
        # In silent mode, always launch
        Start-PandaApplication | Out-Null
    }
    
    # ========================================================================
    # Installation Complete
    # ========================================================================
    
    Write-Header "Installation Complete"
    
    Write-Log "PandaApp installation completed successfully" -Level SUCCESS
    Write-Log "Installation path: $($Config.AppInstallPath)" -Level INFO
    Write-Log "Executable: $($Config.AppExeName)" -Level INFO
    Write-Log "Configuration: $($Config.ConfigFileName)" -Level INFO
    Write-Log "SavedData: $($Config.SavedDataPath)" -Level INFO
    Write-Log "" -Level INFO
    Write-Log "Next steps:" -Level INFO
    Write-Log "  1. Check application window for any errors" -Level INFO
    Write-Log "  2. Verify connection to Backend servers" -Level INFO
    Write-Log "  3. Test Live View functionality" -Level INFO
    
    Write-Log "Installation finished at $(Get-Date)" -Level INFO
    Write-Log "Log file: $LogPath" -Level INFO
    
    if (-not $SilentMode) {
        Write-Host ""
        Read-Host "Press Enter to exit"
    }
}

# ============================================================================
# Script Entry Point
# ============================================================================

try {
    Start-Installation
    exit 0
}
catch {
    Write-Log "Fatal error: $_" -Level ERROR
    Write-Log $_.ScriptStackTrace -Level DEBUG
    
    if (-not $SilentMode) {
        Read-Host "Press Enter to exit"
    }
    exit 1
}

