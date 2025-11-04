# Check Focus Server connectivity and status
param(
    [string]$Server = "10.10.100.100"
)

Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host "Focus Server Health Check" -ForegroundColor Cyan
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Basic connectivity
Write-Host "1. Testing TCP connection to $Server :443..." -ForegroundColor Yellow
$tcpTest = Test-NetConnection -ComputerName $Server -Port 443 -WarningAction SilentlyContinue
if ($tcpTest.TcpTestSucceeded) {
    Write-Host "   [OK] Port 443 is open" -ForegroundColor Green
} else {
    Write-Host "   [ERROR] Cannot connect to port 443" -ForegroundColor Red
    exit 1
}

# Test 2: HTTP endpoint check
Write-Host "`n2. Testing HTTP endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://$Server/focus-server/" -Method Get -TimeoutSec 10 -SkipCertificateCheck -ErrorAction Stop
    Write-Host "   [OK] HTTP endpoint responding (Status: $($response.StatusCode))" -ForegroundColor Green
    Write-Host "   Content Length: $($response.Content.Length) bytes" -ForegroundColor Gray
} catch {
    Write-Host "   [WARNING] HTTP endpoint issue: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Test 3: API endpoint check (health or configure)
Write-Host "`n3. Testing API endpoint (health check)..." -ForegroundColor Yellow
try {
    $headers = @{
        "Content-Type" = "application/json"
    }
    
    # Try health endpoint if exists
    $healthUrl = "https://$Server/focus-server/health"
    try {
        $healthResponse = Invoke-WebRequest -Uri $healthUrl -Method Get -Headers $headers -TimeoutSec 10 -SkipCertificateCheck -ErrorAction Stop
        Write-Host "   [OK] Health endpoint responding (Status: $($healthResponse.StatusCode))" -ForegroundColor Green
    } catch {
        Write-Host "   [INFO] Health endpoint not available (normal)" -ForegroundColor Gray
    }
    
    # Try configure endpoint with minimal payload
    $configureUrl = "https://$Server/focus-server/configure"
    $testPayload = @{
        channels = @{
            min = 1
            max = 10
        }
        frequency = @{
            start_hz = 0
            end_hz = 100
        }
        view_type = "MultiChannelSpectrogram"
    } | ConvertTo-Json -Depth 10
    
    Write-Host "`n4. Testing configure endpoint with minimal payload..." -ForegroundColor Yellow
    $configureResponse = Invoke-WebRequest -Uri $configureUrl -Method Post -Body $testPayload -Headers $headers -TimeoutSec 30 -SkipCertificateCheck -ErrorAction Stop
    Write-Host "   [OK] Configure endpoint responding (Status: $($configureResponse.StatusCode))" -ForegroundColor Green
    Write-Host "   Response time: < 30 seconds" -ForegroundColor Gray
    
} catch {
    $errorMsg = $_.Exception.Message
    Write-Host "   [ERROR] API endpoint issue: $errorMsg" -ForegroundColor Red
    
    if ($errorMsg -like "*timeout*") {
        Write-Host "`n   [DIAGNOSIS] Server timeout detected" -ForegroundColor Yellow
        Write-Host "   Possible causes:" -ForegroundColor Yellow
        Write-Host "   1. Server is overloaded" -ForegroundColor White
        Write-Host "   2. Too many concurrent requests" -ForegroundColor White
        Write-Host "   3. Server needs restart" -ForegroundColor White
        Write-Host "   4. Network issues" -ForegroundColor White
    } elseif ($errorMsg -like "*500*") {
        Write-Host "`n   [DIAGNOSIS] Server error (500)" -ForegroundColor Yellow
        Write-Host "   Server is responding but has internal errors" -ForegroundColor Yellow
    } elseif ($errorMsg -like "*connection refused*" -or $errorMsg -like "*refused*") {
        Write-Host "`n   [DIAGNOSIS] Connection refused" -ForegroundColor Yellow
        Write-Host "   Server might be down or service not running" -ForegroundColor Yellow
    }
}

# Test 4: Check via kubectl (if available via SSH)
Write-Host "`n5. Checking via Kubernetes (requires SSH access)..." -ForegroundColor Yellow
Write-Host "   To check Focus Server pods, run:" -ForegroundColor Gray
Write-Host "   ssh root@10.10.10.10 'ssh prisma@10.10.10.150 kubectl get pods -n panda | grep focus'" -ForegroundColor White

Write-Host "`n=================================================================================" -ForegroundColor Cyan
Write-Host "Health Check Complete" -ForegroundColor Cyan
Write-Host "=================================================================================" -ForegroundColor Cyan
