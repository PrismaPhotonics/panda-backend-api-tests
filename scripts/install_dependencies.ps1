$ErrorActionPreference = 'Stop'

python -m pip install -U pip setuptools wheel

function Install-PipWithRetry {
  param(
    [string]$groupName,
    [array]$packages,
    [string]$isFatal = "true"
  )

  $maxAttempts = 3
  $failedPackages = @()
  $succeededPackages = @()

  Write-Host "========================================" -ForegroundColor Cyan
  Write-Host "Installing group: $groupName" -ForegroundColor Cyan
  Write-Host "========================================" -ForegroundColor Cyan

  foreach ($pkg in $packages) {
    Write-Host ""
    Write-Host "Installing package: $pkg" -ForegroundColor Yellow
    $installed = $false

    for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
      Write-Host "  Attempt $($attempt)/$($maxAttempts)..."
      try {
        pip install --no-cache-dir --prefer-binary $pkg -v 2>&1 | Tee-Object -FilePath "pip-install-$($groupName)-$($pkg.Replace('==', '-')).log"
        if ($LASTEXITCODE -eq 0) {
          Write-Host "  [OK] $pkg installed successfully" -ForegroundColor Green
          $succeededPackages += $pkg
          $installed = $true
          break
        }
      } catch {
        Write-Host "  pip error: $($_.Exception.Message)" -ForegroundColor Red
      }

      if ($attempt -lt $maxAttempts) {
        $waitTime = 5 * $attempt
        Write-Host "  Retrying in $waitTime seconds..." -ForegroundColor Yellow
        Start-Sleep -Seconds $waitTime
      }
    }

    if (-not $installed) {
      Write-Host "  [FAIL] $pkg failed to install after $maxAttempts attempts" -ForegroundColor Red
      $failedPackages += $pkg
    }
  }

  Write-Host ""
  Write-Host "========================================" -ForegroundColor Cyan
  Write-Host "Summary for $groupName" -ForegroundColor Cyan
  Write-Host "========================================" -ForegroundColor Cyan
  Write-Host "Succeeded: $($succeededPackages.Count)/$($packages.Count)" -ForegroundColor Green
  if ($succeededPackages.Count -gt 0) {
    Write-Host "  $($succeededPackages -join ', ')" -ForegroundColor Green
  }
  
  if ($failedPackages.Count -gt 0) {
    Write-Host "Failed: $($failedPackages.Count)/$($packages.Count)" -ForegroundColor Red
    Write-Host "  $($failedPackages -join ', ')" -ForegroundColor Red
    
    if ($isFatal -eq "true") {
      Write-Host ""
      Write-Host "::error::Failed installing the following packages in $groupName : $($failedPackages -join ', ')"
      Write-Host "Check logs: pip-install-$groupName-*.log"
      pip --version
      python -V
      exit 1
    } else {
      Write-Host ""
      Write-Host "::warning::Optional packages failed but continuing: $($failedPackages -join ', ')"
    }
  }
  
  Write-Host ""
}

Write-Host "Installing core test packages..."
Install-PipWithRetry -groupName 'core-test-packages' -packages @(
  'pytest==9.0.1',
  'pytest-asyncio',
  'pytest-timeout',
  'pytest-mock',
  'pytest-html',
  'pytest-cov',
  'pytest-json-report',
  'pytest-xdist'
) -isFatal "true"

Write-Host "Installing HTTP and data packages..."
Install-PipWithRetry -groupName 'http-data-packages' -packages @(
  'requests',
  'httpx',
  'beautifulsoup4',
  'pydantic',
  'pydantic-settings',
  'orjson',
  'pyyaml'
) -isFatal "true"

Write-Host "Installing infra packages..."
Install-PipWithRetry -groupName 'infra-packages' -packages @(
  'kubernetes',
  'pymongo',
  'paramiko',
  'pika',
  'structlog',
  'colorlog',
  'python-dateutil',
  'pytz',
  'psutil',
  'python-dotenv',
  'netaddr'
) -isFatal "true"

Write-Host "Installing pinned isort..."
Install-PipWithRetry -groupName 'isort' -packages @('isort==5.13.2') -isFatal "true"

Write-Host "Installing optional packages (non-fatal)..."
Install-PipWithRetry -groupName 'optional-packages' -packages @(
  'allure-pytest',
  'jinja2',
  'asyncio-mqtt',
  'aiofiles'
) -isFatal "false"

Write-Host "Dependency installation completed!"
Write-Host ""

# Attempt to list installed packages (non-fatal)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installed Packages (First 40)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
try {
  $ErrorActionPreference = 'Continue'
  $packages = pip list --format=freeze 2>&1 | Select-Object -First 40
  foreach ($pkg in $packages) {
    Write-Host $pkg
  }
  Write-Host ""
  Write-Host "Total packages shown: $($packages.Count)" -ForegroundColor Green
} catch {
  Write-Host "Could not list packages (non-critical)" -ForegroundColor Yellow
}

# Ensure we exit with success code
exit 0

