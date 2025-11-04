# ============================================================================
# K9s Setup Script - Quick Installation
# ============================================================================

Write-Host "`n╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         K9s Setup - Kubernetes Pods Access                ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

# Step 1: Check if kubeconfig exists
Write-Host "`n[1/3] Checking for kubeconfig..." -ForegroundColor Yellow

$possiblePaths = @(
    "$env:USERPROFILE\Downloads\kubeconfig",
    "$env:USERPROFILE\Downloads\kubeconfig.yaml",
    "$env:USERPROFILE\Downloads\config",
    "$env:USERPROFILE\Downloads\k3s.yaml"
)

$kubeconfigFound = $null
foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $kubeconfigFound = $path
        Write-Host "   Found kubeconfig: $path" -ForegroundColor Green
        break
    }
}

if ($kubeconfigFound) {
    # Copy to correct location
    $targetPath = "$env:USERPROFILE\.kube\config-panda"
    Copy-Item $kubeconfigFound $targetPath -Force
    Write-Host "   Copied to: $targetPath" -ForegroundColor Green
} else {
    Write-Host "   Kubeconfig not found in Downloads!" -ForegroundColor Red
    Write-Host "   Please download from: https://10.10.100.102/" -ForegroundColor Yellow
    Write-Host "   Then run this script again." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 2: Download and install K9s
Write-Host "`n[2/3] Installing K9s..." -ForegroundColor Yellow

$k9sInstallPath = "$env:LOCALAPPDATA\Microsoft\WindowsApps"
$k9sExe = "$k9sInstallPath\k9s.exe"

if (Test-Path $k9sExe) {
    Write-Host "   K9s already installed!" -ForegroundColor Green
} else {
    Write-Host "   Downloading K9s..." -ForegroundColor Yellow
    
    # Try to download K9s
    $version = "v0.32.4"
    $downloadUrl = "https://github.com/derailed/k9s/releases/download/$version/k9s_Windows_amd64.zip"
    $zipPath = "$env:TEMP\k9s.zip"
    $extractPath = "$env:TEMP\k9s_extract"
    
    try {
        # Download
        Invoke-WebRequest -Uri $downloadUrl -OutFile $zipPath -UseBasicParsing -ErrorAction Stop
        Write-Host "   Downloaded successfully" -ForegroundColor Green
        
        # Extract
        Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force
        
        # Move to PATH
        Copy-Item "$extractPath\k9s.exe" $k9sExe -Force
        Write-Host "   K9s installed to: $k9sExe" -ForegroundColor Green
        
        # Cleanup
        Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
        Remove-Item $extractPath -Recurse -Force -ErrorAction SilentlyContinue
        
    } catch {
        Write-Host "   Auto-download failed: $_" -ForegroundColor Red
        Write-Host "   Please download manually from: https://github.com/derailed/k9s/releases" -ForegroundColor Yellow
        Write-Host "   1. Download: k9s_Windows_amd64.zip" -ForegroundColor White
        Write-Host "   2. Extract k9s.exe" -ForegroundColor White
        Write-Host "   3. Move to: $k9sInstallPath" -ForegroundColor White
        Read-Host "Press Enter to continue after manual installation"
    }
}

# Step 3: Test and run
Write-Host "`n[3/3] Testing connection..." -ForegroundColor Yellow

$env:KUBECONFIG = "$env:USERPROFILE\.kube\config-panda"

# Test kubectl
try {
    $namespaces = kubectl get namespaces --no-headers 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   kubectl connection: OK" -ForegroundColor Green
        
        # Check if panda namespace exists
        if ($namespaces -match "panda") {
            Write-Host "   Found 'panda' namespace!" -ForegroundColor Green
        } else {
            Write-Host "   Warning: 'panda' namespace not found" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   kubectl connection failed" -ForegroundColor Red
        Write-Host "   Error: $namespaces" -ForegroundColor Red
    }
} catch {
    Write-Host "   kubectl not available or connection failed" -ForegroundColor Red
}

# Summary
Write-Host "`n╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                   Setup Complete!                          ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`nTo use K9s, run:" -ForegroundColor Yellow
Write-Host "   `$env:KUBECONFIG = '$env:USERPROFILE\.kube\config-panda'" -ForegroundColor Green
Write-Host "   k9s -n panda" -ForegroundColor Green

Write-Host "`nOr use this quick command:" -ForegroundColor Yellow
Write-Host "   . .\set_production_env.ps1; k9s -n panda" -ForegroundColor Green

Write-Host ""
$response = Read-Host "Do you want to start K9s now? (y/n)"
if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host "`nStarting K9s..." -ForegroundColor Green
    $env:KUBECONFIG = "$env:USERPROFILE\.kube\config-panda"
    k9s -n panda
}

