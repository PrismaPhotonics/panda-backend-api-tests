#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Update PZ Git Submodule to Latest Version

.DESCRIPTION
    This PowerShell script updates the PZ development repository submodule
    to the latest version from the remote repository.

    Features:
    - Automatic submodule initialization if needed
    - Fetches latest changes from remote
    - Shows before/after commit info
    - Error handling and status reporting

.PARAMETER Branch
    Specific branch to sync to (default: master)

.PARAMETER Init
    Initialize submodule if not already done

.PARAMETER Status
    Show current submodule status without updating

.EXAMPLE
    .\update_pz_submodule.ps1
    Updates to latest master branch

.EXAMPLE
    .\update_pz_submodule.ps1 -Branch develop
    Updates to latest develop branch

.EXAMPLE
    .\update_pz_submodule.ps1 -Status
    Shows current submodule status

.NOTES
    Author: QA Automation Architect
    Requires: Git installed and in PATH
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$Branch = "master",

    [Parameter(Mandatory=$false)]
    [switch]$Init,

    [Parameter(Mandatory=$false)]
    [switch]$Status
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Color functions
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success { param([string]$Message) Write-ColorOutput "✅ $Message" "Green" }
function Write-Error { param([string]$Message) Write-ColorOutput "❌ $Message" "Red" }
function Write-Warning { param([string]$Message) Write-ColorOutput "⚠️  $Message" "Yellow" }
function Write-Info { param([string]$Message) Write-ColorOutput "ℹ️  $Message" "Cyan" }
function Write-Header { param([string]$Message) Write-ColorOutput "`n$('=' * 80)`n$Message`n$('=' * 80)" "Magenta" }

# Get project root (parent of scripts directory)
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PZSubmodulePath = Join-Path $ProjectRoot "external\pz"

# Function to check if submodule exists
function Test-SubmoduleExists {
    if (-not (Test-Path $PZSubmodulePath)) {
        return $false
    }

    $gitDir = Join-Path $PZSubmodulePath ".git"
    if (-not (Test-Path $gitDir)) {
        return $false
    }

    return $true
}

# Function to initialize submodule
function Initialize-Submodule {
    Write-Info "Initializing PZ submodule..."

    Push-Location $ProjectRoot
    try {
        git submodule update --init --recursive external/pz
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Submodule initialized successfully"
            return $true
        } else {
            Write-Error "Submodule initialization failed"
            return $false
        }
    } finally {
        Pop-Location
    }
}

# Function to get current commit hash
function Get-CurrentCommit {
    Push-Location $PZSubmodulePath
    try {
        $commit = git rev-parse HEAD 2>$null
        if ($LASTEXITCODE -eq 0) {
            return $commit.Substring(0, 8)
        }
        return $null
    } finally {
        Pop-Location
    }
}

# Function to get current branch
function Get-CurrentBranch {
    Push-Location $PZSubmodulePath
    try {
        $branch = git rev-parse --abbrev-ref HEAD 2>$null
        if ($LASTEXITCODE -eq 0) {
            return $branch
        }
        return $null
    } finally {
        Pop-Location
    }
}

# Function to get last commit info
function Get-LastCommitInfo {
    Push-Location $PZSubmodulePath
    try {
        $info = git log -1 --format="%ci - %s" 2>$null
        if ($LASTEXITCODE -eq 0) {
            return $info
        }
        return "Unknown"
    } finally {
        Pop-Location
    }
}

# Function to show submodule status
function Show-SubmoduleStatus {
    Write-Header "📊 PZ Repository Status"

    if (-not (Test-SubmoduleExists)) {
        Write-Warning "Submodule not initialized"
        Write-Info "Run: .\update_pz_submodule.ps1 -Init"
        return
    }

    $commit = Get-CurrentCommit
    $branch = Get-CurrentBranch
    $lastCommit = Get-LastCommitInfo

    # Get file count
    Push-Location $PZSubmodulePath
    $fileCount = (git ls-files 2>$null | Measure-Object).Count
    Pop-Location

    Write-Info "📍 Location: $PZSubmodulePath"
    Write-Info "🌿 Branch: $branch"
    Write-Info "📌 Commit: $commit"
    Write-Info "📅 Last Commit: $lastCommit"
    Write-Info "📦 Files: $($fileCount.ToString('N0'))"
    Write-ColorOutput "$('=' * 80)" "Magenta"
}

# Function to sync submodule to latest
function Sync-SubmoduleToLatest {
    param([string]$TargetBranch)

    Write-Header "🔄 Starting PZ Repository Sync"

    # Check if submodule exists
    if (-not (Test-SubmoduleExists)) {
        Write-Info "Submodule not initialized. Initializing..."
        if (-not (Initialize-Submodule)) {
            return $false
        }
    }

    # Show current state
    $currentCommit = Get-CurrentCommit
    $currentBranch = Get-CurrentBranch

    if ($currentCommit -and $currentBranch) {
        Write-Info "📌 Current state: $currentBranch @ $currentCommit"
    }

    # Fetch latest changes
    Write-Info "📥 Fetching latest changes from remote..."
    Push-Location $PZSubmodulePath

    try {
        git fetch origin 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to fetch from remote"
            return $false
        }

        # Checkout specific branch
        Write-Info "🔀 Checking out branch: $TargetBranch"
        git checkout $TargetBranch 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to checkout branch: $TargetBranch"
            return $false
        }

        # Pull latest changes
        Write-Info "⬇️  Pulling latest changes..."
        git pull origin $TargetBranch 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to pull latest changes"
            return $false
        }

        # Get new state
        $newCommit = Get-CurrentCommit
        $newBranch = Get-CurrentBranch

        Write-Header "✅ Sync Completed Successfully!"
        Write-Success "📌 New state: $newBranch @ $newCommit"

        # Show summary
        if ($currentCommit -ne $newCommit) {
            Write-Info "📝 Updated from $currentCommit to $newCommit"
        } else {
            Write-Info "📝 Already up-to-date"
        }

        Write-ColorOutput "$('=' * 80)" "Magenta"
        return $true

    } catch {
        Write-Error "Sync failed with exception: $_"
        return $false
    } finally {
        Pop-Location
    }
}

# Main script execution
try {
    # Check if git is installed
    $gitVersion = git --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Git is not installed or not in PATH"
        exit 1
    }

    # Execute requested operation
    if ($Status) {
        Show-SubmoduleStatus
    } elseif ($Init) {
        if (Test-SubmoduleExists) {
            Write-Success "Submodule already initialized"
            Show-SubmoduleStatus
        } else {
            if (Initialize-Submodule) {
                Show-SubmoduleStatus
            } else {
                exit 1
            }
        }
    } else {
        # Default: sync to latest
        if (Sync-SubmoduleToLatest -TargetBranch $Branch) {
            exit 0
        } else {
            exit 1
        }
    }

} catch {
    Write-Error "Script failed: $_"
    exit 1
}
