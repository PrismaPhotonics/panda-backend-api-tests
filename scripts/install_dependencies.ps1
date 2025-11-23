$ErrorActionPreference = 'Stop'

python -m pip install -U pip setuptools wheel

function Install-PipWithRetry {
  param(
    [string]$groupName,
    [string]$packages,
    [string]$isFatal = "true"
  )

  $maxAttempts = 3

  for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
    Write-Host "Attempt $($attempt)/$($maxAttempts): Installing $($groupName)"
    try {
      # Run pip and capture verbose output to a per-group log
      pip install --no-cache-dir --prefer-binary $packages -v 2>&1 | Tee-Object -FilePath "pip-install-$($groupName).log"
      if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] $($groupName) installed successfully (attempt $($attempt))"
        return 0
      }
    } catch {
      Write-Host "pip exited with error on attempt $($attempt) for $($groupName): $($_.Exception.Message)"
    }

    Write-Host "[FAIL] Attempt $($attempt) failed for $($groupName)"
    if ($attempt -lt $maxAttempts) { Start-Sleep -Seconds (5 * $attempt) }
  }

  Write-Host "All attempts failed for $($groupName)"
  pip --version
  python -V
  if ($isFatal -eq "true") {
    Write-Host "::error::Failed installing $($groupName) after $($maxAttempts) attempts. See pip-install-$($groupName).log"
    exit 1
  } else {
    Write-Host "Optional group $($groupName) failed to install; continuing without these optional packages. See pip-install-$($groupName).log"
  }
}

Write-Host "Installing core test packages..."
Install-PipWithRetry -groupName 'core-test-packages' -packages 'pytest==9.0.1 pytest-asyncio pytest-timeout pytest-mock pytest-html pytest-cov pytest-json-report pytest-xdist' -isFatal "true"

Write-Host "Installing HTTP and data packages..."
Install-PipWithRetry -groupName 'http-data-packages' -packages 'requests httpx beautifulsoup4 pydantic pydantic-settings orjson pyyaml' -isFatal "true"

Write-Host "Installing infra packages..."
Install-PipWithRetry -groupName 'infra-packages' -packages 'kubernetes pymongo paramiko pika structlog colorlog python-dateutil pytz psutil python-dotenv netaddr' -isFatal "true"

Write-Host "Installing pinned isort..."
Install-PipWithRetry -groupName 'isort' -packages 'isort==5.13.2' -isFatal "true"

Write-Host "Installing optional packages (non-fatal)..."
Install-PipWithRetry -groupName 'optional-packages' -packages 'allure-pytest jinja2 asyncio-mqtt aiofiles' -isFatal "false"

Write-Host "Dependency installation completed!"

# Attempt to list installed packages to a file (non-fatal)
try {
  $ErrorActionPreference = 'Continue'
  pip list --format=freeze 2>&1 | Select-Object -First 40 | ForEach-Object { Write-Host $_ }
} catch {
  Write-Host "Could not list packages (non-critical)"
}

