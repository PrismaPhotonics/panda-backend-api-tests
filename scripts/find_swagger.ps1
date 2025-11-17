#!/usr/bin/env pwsh
# Find Swagger Documentation in New Production Environment

Write-Host ""
Write-Host "=== Searching for Swagger Documentation ===" -ForegroundColor Cyan
Write-Host ""

# Activate venv to use Python
if (Test-Path ".venv\Scripts\Activate.ps1") {
    . .venv\Scripts\Activate.ps1
}

# Possible Swagger URLs
$urls = @(
    "https://10.10.100.100/focus-server/swagger/",
    "https://10.10.100.100/focus-server/api-docs/",
    "https://10.10.100.100/focus-server/docs/",
    "https://10.10.100.100/swagger/",
    "https://10.10.100.100/api/swagger/",
    "https://10.10.100.100/api-docs/",
    "https://10.10.10.100/api/swagger/",
    "https://10.10.10.100/swagger/",
    "https://10.10.10.150:30443/api/swagger/"
)

Write-Host "Testing URLs..." -ForegroundColor Yellow
Write-Host ""

foreach ($url in $urls) {
    Write-Host "Testing: $url" -NoNewline
    
    try {
        # Use Python requests to test (supports SSL verification disable)
        $result = python -c @"
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
try:
    r = requests.get('$url', verify=False, timeout=5, allow_redirects=True)
    print(f'{r.status_code}|{r.url}|{len(r.text)}')
except Exception as e:
    print(f'ERROR|{str(e)}|0')
"@
        
        $parts = $result -split '\|'
        $statusCode = $parts[0]
        $finalUrl = $parts[1]
        $contentLength = $parts[2]
        
        if ($statusCode -eq "200") {
            Write-Host " → ✓ FOUND! (200 OK, ${contentLength} bytes)" -ForegroundColor Green
            if ($finalUrl -ne $url) {
                Write-Host "   Redirected to: $finalUrl" -ForegroundColor Yellow
            }
        }
        elseif ($statusCode -eq "401") {
            Write-Host " → 🔒 EXISTS (401 Unauthorized - needs auth)" -ForegroundColor Yellow
        }
        elseif ($statusCode -eq "404") {
            Write-Host " → ✗ Not Found (404)" -ForegroundColor DarkGray
        }
        elseif ($statusCode -match "^\d{3}$") {
            Write-Host " → Status: $statusCode" -ForegroundColor Cyan
        }
        else {
            Write-Host " → Error: $statusCode" -ForegroundColor Red
        }
    }
    catch {
        Write-Host " → Connection Error" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== Manual Check ===" -ForegroundColor Cyan
Write-Host "If none found automatically, try opening in browser:" -ForegroundColor Yellow
Write-Host "  https://10.10.100.100/focus-server/" -ForegroundColor White
Write-Host "  https://10.10.10.100/" -ForegroundColor White
Write-Host ""
Write-Host "Common Swagger paths to append:" -ForegroundColor Yellow
Write-Host "  /swagger/" -ForegroundColor White
Write-Host "  /api/swagger/" -ForegroundColor White
Write-Host "  /api-docs/" -ForegroundColor White
Write-Host "  /docs/" -ForegroundColor White
Write-Host ""

