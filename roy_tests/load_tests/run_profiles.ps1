# PowerShell script: run three Locust profiles sequentially with 60s gaps
# Usage: run from the load/ directory with active venv
# Ensures results are tagged per profile and timestamps

param(
    [string]$HostUrl = "http://localhost:8500",
    [string]$LocustFile = "locustfile.py"
)

$ErrorActionPreference = "Stop"

# Ensure results dir exists
if (!(Test-Path -Path "results")) {
    New-Item -ItemType Directory -Path "results" | Out-Null
}

function Run-Profile {
    param(
        [string]$ProfileName,
        [hashtable]$Env,
        [string]$Duration,
        [int]$Users,
        [int]$SpawnRate
    )

    # Resolve host and base path/SSL defaults
    $apiBase = if ([string]::IsNullOrWhiteSpace($Env["API_BASE"])) { "/api" } else { $Env["API_BASE"] }
    $verifySsl = if ([string]::IsNullOrWhiteSpace($Env["VERIFY_SSL"])) { "false" } else { $Env["VERIFY_SSL"] }
    $connectTimeout = if ([string]::IsNullOrWhiteSpace($Env["CONNECT_TIMEOUT"])) { "3" } else { $Env["CONNECT_TIMEOUT"] }
    $readTimeout = if ([string]::IsNullOrWhiteSpace($Env["READ_TIMEOUT"])) { "15" } else { $Env["READ_TIMEOUT"] }
    $env["API_BASE"] = $apiBase
    $env["VERIFY_SSL"] = $verifySsl
    $env["CONNECT_TIMEOUT"] = $connectTimeout
    $env["READ_TIMEOUT"] = $readTimeout

    Write-Host "Running profile '$ProfileName' for $Duration with $Users users (r=$SpawnRate) against $HostUrl (API_BASE=$apiBase, VERIFY_SSL=$verifySsl)" -ForegroundColor Cyan

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $csvBase = "results/${ProfileName}_$timestamp"

    # Build environment variables string
    $envBackup = @{}
    foreach ($k in $Env.Keys) {
        $envBackup[$k] = [System.Environment]::GetEnvironmentVariable($k, "Process")
        [System.Environment]::SetEnvironmentVariable($k, $Env[$k], "Process")
    }

    # Common vars
    [System.Environment]::SetEnvironmentVariable("RESULTS_DIR", "results", "Process")

    $args = @(
        "-m", "locust",
        "-f", $LocustFile,
        "--headless",
        "-u", $Users,
        "-r", $SpawnRate,
        "-t", $Duration,
        "--host", $HostUrl,
        "--csv", $csvBase,
        "--html", "${csvBase}.html",
        "--loglevel", "INFO"
    )

    python @args | Out-Host

    # Restore env
    foreach ($k in $Env.Keys) {
        [System.Environment]::SetEnvironmentVariable($k, $envBackup[$k], "Process")
    }
}

# RAMP profile
Run-Profile -ProfileName "ramp" -Env @{ LOAD_SHAPE = "ramp"; RAMP_USERS = "20"; RAMP_SPAWN_RATE = "2"; RAMP_STAGE_SECS = "60" } -Duration "3m" -Users 1 -SpawnRate 1

Start-Sleep -Seconds 60

# STEADY profile
Run-Profile -ProfileName "steady" -Env @{ LOAD_SHAPE = "steady"; STEADY_USERS = "20"; STEADY_SPAWN_RATE = "2"; STEADY_DURATION = "180" } -Duration "3m" -Users 1 -SpawnRate 1

Start-Sleep -Seconds 60

# SPIKE profile
Run-Profile -ProfileName "spike" -Env @{ LOAD_SHAPE = "spike"; SPIKE_BASE = "5"; SPIKE_PEAK = "50"; SPIKE_RISE_SECS = "10"; SPIKE_HOLD_SECS = "20"; SPIKE_FALL_SECS = "10"; SPIKE_SPAWN_RATE = "5" } -Duration "1m" -Users 1 -SpawnRate 1
