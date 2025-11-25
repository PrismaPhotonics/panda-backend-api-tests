# Script to setup GitHub Actions Runner on Slave Laptop (10.50.0.36)
# ===================================================================
# This script connects to the slave laptop and sets up a self-hosted runner
# for the panda-backend-api-tests repository

param(
    [string]$SlaveIP = "10.50.0.36",
    [string]$SSHUser = "",
    [string]$SSHPassword = "",
    [string]$SSHKeyFile = "",
    [string]$RepoUrl = "https://github.com/PrismaPhotonics/panda-backend-api-tests",
    [string]$RunnerName = "slave-laptop-runner",
    [string]$InstallPath = "",
    [string]$RegistrationToken = ""
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "GitHub Actions Runner Setup on Slave Laptop" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Target: $SlaveIP" -ForegroundColor Yellow
Write-Host "Repository: $RepoUrl" -ForegroundColor Yellow
Write-Host ""

# Check if paramiko is available (for Python SSH)
$pythonAvailable = $false
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python") {
        $pythonAvailable = $true
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Python not found - will use PowerShell SSH commands" -ForegroundColor Yellow
}

# Function to test SSH connection
function Test-SSHConnection {
    param(
        [string]$Host,
        [string]$User,
        [string]$Password,
        [string]$KeyFile
    )
    
    Write-Host "Testing SSH connection to $User@$Host..." -ForegroundColor Yellow
    
    if ($pythonAvailable) {
        # Use Python with paramiko for better SSH handling
        $testScript = @"
import paramiko
import sys
from pathlib import Path

host = '$Host'
user = '$User'
password = '$Password'
key_file = '$KeyFile'

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    if key_file and Path(key_file).expanduser().exists():
        ssh.connect(hostname=host, username=user, key_filename=str(Path(key_file).expanduser()), timeout=10)
    elif password:
        ssh.connect(hostname=host, username=user, password=password, timeout=10)
    else:
        print('ERROR: No authentication method provided')
        sys.exit(1)
    
    stdin, stdout, stderr = ssh.exec_command('hostname')
    hostname = stdout.read().decode().strip()
    print(f'SUCCESS: Connected to {hostname}')
    
    # Detect OS
    stdin, stdout, stderr = ssh.exec_command('uname -a 2>/dev/null || echo Windows')
    os_info = stdout.read().decode().strip()
    print(f'OS_INFO: {os_info}')
    
    ssh.close()
    sys.exit(0)
except Exception as e:
    print(f'ERROR: {str(e)}')
    sys.exit(1)
"@
        $testScript | python
        return $LASTEXITCODE -eq 0
    } else {
        # Fallback to PowerShell SSH (requires OpenSSH client)
        try {
            if ($KeyFile) {
                ssh -i $KeyFile -o StrictHostKeyChecking=no -o ConnectTimeout=10 "$User@$Host" "hostname" 2>&1 | Out-Null
            } else {
                # Note: PowerShell SSH doesn't support password directly, need sshpass or key
                Write-Host "⚠️  Password authentication requires sshpass or SSH key" -ForegroundColor Yellow
                return $false
            }
            return $true
        } catch {
            return $false
        }
    }
}

# Function to execute remote command
function Invoke-RemoteCommand {
    param(
        [string]$Host,
        [string]$User,
        [string]$Password,
        [string]$KeyFile,
        [string]$Command
    )
    
    if ($pythonAvailable) {
        $execScript = @"
import paramiko
import sys
from pathlib import Path

host = '$Host'
user = '$User'
password = '$Password'
key_file = '$KeyFile'
command = '''$Command'''

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    if key_file and Path(key_file).expanduser().exists():
        ssh.connect(hostname=host, username=user, key_filename=str(Path(key_file).expanduser()), timeout=30)
    elif password:
        ssh.connect(hostname=host, username=user, password=password, timeout=30)
    else:
        print('ERROR: No authentication method')
        sys.exit(1)
    
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_code = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='ignore')
    errors = stderr.read().decode('utf-8', errors='ignore')
    
    if output:
        print(output)
    if errors:
        print(f'STDERR: {errors}', file=sys.stderr)
    
    ssh.close()
    sys.exit(exit_code)
except Exception as e:
    print(f'ERROR: {str(e)}', file=sys.stderr)
    sys.exit(1)
"@
        $execScript | python
        return $LASTEXITCODE
    } else {
        Write-Host "❌ Python required for remote command execution" -ForegroundColor Red
        return 1
    }
}

# Get SSH credentials if not provided
if ([string]::IsNullOrEmpty($SSHUser)) {
    $SSHUser = Read-Host "Enter SSH username for $SlaveIP"
}

if ([string]::IsNullOrEmpty($SSHPassword) -and [string]::IsNullOrEmpty($SSHKeyFile)) {
    $authMethod = Read-Host "Authentication method: (1) Password (2) SSH Key"
    if ($authMethod -eq "2") {
        $SSHKeyFile = Read-Host "Enter path to SSH key file"
    } else {
        $securePassword = Read-Host "Enter SSH password" -AsSecureString
        $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
        $SSHPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
    }
}

# Test SSH connection
Write-Host ""
Write-Host "Step 1: Testing SSH Connection" -ForegroundColor Cyan
Write-Host "-------------------------------" -ForegroundColor Cyan

if (-not (Test-SSHConnection -Host $SlaveIP -User $SSHUser -Password $SSHPassword -KeyFile $SSHKeyFile)) {
    Write-Host "❌ Failed to connect via SSH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please verify:" -ForegroundColor Yellow
    Write-Host "  1. SSH service is running on $SlaveIP" -ForegroundColor Yellow
    Write-Host "  2. Credentials are correct" -ForegroundColor Yellow
    Write-Host "  3. Network connectivity to $SlaveIP" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ SSH connection successful" -ForegroundColor Green

# Detect OS
Write-Host ""
Write-Host "Step 2: Detecting Operating System" -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan

$osDetectCommand = "if (Test-Path 'C:\Windows') { Write-Output 'Windows' } elseif (Test-Path '/etc/os-release') { Write-Output 'Linux' } else { Write-Output 'Unknown' }"
$osResult = Invoke-RemoteCommand -Host $SlaveIP -User $SSHUser -Password $SSHPassword -KeyFile $SSHKeyFile -Command $osDetectCommand

# Try alternative detection
if ($osResult -ne 0) {
    $osDetectCommand = "uname -a 2>/dev/null || echo Windows"
    $osInfo = Invoke-RemoteCommand -Host $SlaveIP -User $SSHUser -Password $SSHPassword -KeyFile $SSHKeyFile -Command $osDetectCommand
    if ($osInfo -match "Windows" -or $osInfo -match "MINGW" -or $osInfo -match "MSYS") {
        $isWindows = $true
    } elseif ($osInfo -match "Linux") {
        $isWindows = $false
    } else {
        Write-Host "⚠️  Could not detect OS, assuming Windows" -ForegroundColor Yellow
        $isWindows = $true
    }
} else {
    $isWindows = $true  # PowerShell command suggests Windows
}

if ($isWindows) {
    Write-Host "✅ Detected: Windows" -ForegroundColor Green
    if ([string]::IsNullOrEmpty($InstallPath)) {
        $InstallPath = "C:\actions-runner"
    }
    $runnerUrl = "https://github.com/actions/runner/releases/latest/download/actions-runner-win-x64-2.311.0.zip"
    $extractCommand = "Expand-Archive"
    $configScript = ".\config.cmd"
    $serviceScript = ".\svc.cmd"
} else {
    Write-Host "✅ Detected: Linux" -ForegroundColor Green
    if ([string]::IsNullOrEmpty($InstallPath)) {
        $InstallPath = "/opt/actions-runner"
    }
    $runnerUrl = "https://github.com/actions/runner/releases/latest/download/actions-runner-linux-x64-2.311.0.tar.gz"
    $extractCommand = "tar xzf"
    $configScript = "./config.sh"
    $serviceScript = "./svc.sh"
}

Write-Host "Installation path: $InstallPath" -ForegroundColor Yellow

# Get registration token
Write-Host ""
Write-Host "Step 3: Getting Registration Token" -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan

if ([string]::IsNullOrEmpty($RegistrationToken)) {
    Write-Host ""
    Write-Host "To get a registration token:" -ForegroundColor Yellow
    Write-Host "  1. Go to: $RepoUrl/settings/actions/runners/new" -ForegroundColor Cyan
    Write-Host "  2. Select: $(if ($isWindows) { 'Windows' } else { 'Linux' })" -ForegroundColor Cyan
    Write-Host "  3. Copy the registration token" -ForegroundColor Cyan
    Write-Host ""
    $RegistrationToken = Read-Host "Enter registration token"
}

if ([string]::IsNullOrEmpty($RegistrationToken)) {
    Write-Host "❌ Registration token is required" -ForegroundColor Red
    exit 1
}

# Create installation script
Write-Host ""
Write-Host "Step 4: Creating Installation Script" -ForegroundColor Cyan
Write-Host "-------------------------------------" -ForegroundColor Cyan

if ($isWindows) {
    $installScript = @"
`$ErrorActionPreference = 'Stop'
`$InstallPath = '$InstallPath'
`$RepoUrl = '$RepoUrl'
`$RunnerName = '$RunnerName'
`$Token = '$RegistrationToken'

Write-Host 'Creating installation directory...'
New-Item -ItemType Directory -Path `$InstallPath -Force | Out-Null
Set-Location `$InstallPath

Write-Host 'Downloading GitHub Actions Runner...'
`$zipFile = 'actions-runner.zip'
Invoke-WebRequest -Uri '$runnerUrl' -OutFile `$zipFile

Write-Host 'Extracting runner...'
Expand-Archive -Path `$zipFile -DestinationPath . -Force
Remove-Item `$zipFile

Write-Host 'Configuring runner...'
.\config.cmd --url `$RepoUrl --token `$Token --name `$RunnerName --labels 'self-hosted,$(if ($isWindows) { 'Windows' } else { 'Linux' }),slave-laptop' --work '_work' --replace

Write-Host 'Installing as service...'
.\svc.cmd install
.\svc.cmd start

Write-Host 'Setup complete!'
"@
} else {
    $installScript = @"
#!/bin/bash
set -e
INSTALL_PATH='$InstallPath'
REPO_URL='$RepoUrl'
RUNNER_NAME='$RunnerName'
TOKEN='$RegistrationToken'

echo 'Creating installation directory...'
sudo mkdir -p `$INSTALL_PATH
cd `$INSTALL_PATH

echo 'Downloading GitHub Actions Runner...'
curl -L -o actions-runner.tar.gz '$runnerUrl'

echo 'Extracting runner...'
tar xzf actions-runner.tar.gz
rm actions-runner.tar.gz

echo 'Configuring runner...'
sudo ./config.sh --url `$REPO_URL --token `$TOKEN --name `$RUNNER_NAME --labels 'self-hosted,Linux,slave-laptop' --work '_work' --replace

echo 'Installing as service...'
sudo ./svc.sh install
sudo ./svc.sh start

echo 'Setup complete!'
"@
}

# Save script to temp file
$tempScript = [System.IO.Path]::GetTempFileName()
if ($isWindows) {
    $tempScript = $tempScript -replace '\.tmp$', '.ps1'
    $installScript | Out-File -FilePath $tempScript -Encoding UTF8
} else {
    $tempScript = $tempScript -replace '\.tmp$', '.sh'
    $installScript | Out-File -FilePath $tempScript -Encoding UTF8
}

Write-Host "✅ Installation script created: $tempScript" -ForegroundColor Green

# Copy script to remote machine and execute
Write-Host ""
Write-Host "Step 5: Copying and Executing Installation Script" -ForegroundColor Cyan
Write-Host "---------------------------------------------------" -ForegroundColor Cyan

# For Windows, we'll execute commands directly
# For Linux, we'll copy the script and execute it

if ($isWindows) {
    Write-Host "Executing installation commands on Windows..." -ForegroundColor Yellow
    
    # Execute commands step by step
    $commands = @(
        "New-Item -ItemType Directory -Path '$InstallPath' -Force",
        "Set-Location '$InstallPath'",
        "Invoke-WebRequest -Uri '$runnerUrl' -OutFile 'actions-runner.zip'",
        "Expand-Archive -Path 'actions-runner.zip' -DestinationPath . -Force",
        "Remove-Item 'actions-runner.zip'",
        ".\config.cmd --url '$RepoUrl' --token '$RegistrationToken' --name '$RunnerName' --labels 'self-hosted,Windows,slave-laptop' --work '_work' --replace",
        ".\svc.cmd install",
        ".\svc.cmd start"
    )
    
    foreach ($cmd in $commands) {
        Write-Host "Executing: $cmd" -ForegroundColor Gray
        $result = Invoke-RemoteCommand -Host $SlaveIP -User $SSHUser -Password $SSHPassword -KeyFile $SSHKeyFile -Command $cmd
        if ($result -ne 0) {
            Write-Host "❌ Command failed: $cmd" -ForegroundColor Red
            Write-Host "You may need to run this manually on the slave laptop" -ForegroundColor Yellow
            exit 1
        }
    }
} else {
    # Linux - copy script and execute
    Write-Host "Copying script to remote machine..." -ForegroundColor Yellow
    
    # Use SCP if available, otherwise use base64 encoding
    $scriptContent = Get-Content $tempScript -Raw
    $base64Script = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($scriptContent))
    
    $copyCommand = "echo '$base64Script' | base64 -d > /tmp/setup_runner.sh && chmod +x /tmp/setup_runner.sh"
    Invoke-RemoteCommand -Host $SlaveIP -User $SSHUser -Password $SSHPassword -KeyFile $SSHKeyFile -Command $copyCommand
    
    Write-Host "Executing installation script..." -ForegroundColor Yellow
    Invoke-RemoteCommand -Host $SlaveIP -User $SSHUser -Password $SSHPassword -KeyFile $SSHKeyFile -Command "sudo bash /tmp/setup_runner.sh"
}

# Cleanup
Remove-Item $tempScript -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Runner Setup Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Runner Name: $RunnerName" -ForegroundColor Yellow
Write-Host "Installation Path: $InstallPath" -ForegroundColor Yellow
Write-Host ""
Write-Host "To verify the runner is online:" -ForegroundColor Cyan
Write-Host "  Visit: $RepoUrl/settings/actions/runners" -ForegroundColor Green
Write-Host ""
Write-Host "To check status on the slave laptop:" -ForegroundColor Cyan
if ($isWindows) {
    Write-Host "  ssh $SSHUser@$SlaveIP" -ForegroundColor Green
    Write-Host "  cd $InstallPath" -ForegroundColor Green
    Write-Host "  .\svc.cmd status" -ForegroundColor Green
} else {
    Write-Host "  ssh $SSHUser@$SlaveIP" -ForegroundColor Green
    Write-Host "  cd $InstallPath" -ForegroundColor Green
    Write-Host "  sudo ./svc.sh status" -ForegroundColor Green
}
Write-Host ""

