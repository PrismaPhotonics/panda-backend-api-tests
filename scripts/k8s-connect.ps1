# Professional Kubernetes Connection Manager
# ==========================================
param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("start", "stop", "status", "test", "direct")]
    [string]$Action = "status"
)

$ErrorActionPreference = "Stop"

# Configuration
$BASTION_HOST = "10.10.100.3"
$K8S_API = "10.10.100.102"
$K8S_API_PORT = 6443
$LOCAL_PORT = 6443

function Write-Status {
    param([string]$Message, [string]$Type = "INFO")
    
    $color = switch($Type) {
        "SUCCESS" { "Green" }
        "ERROR" { "Red" }
        "WARNING" { "Yellow" }
        default { "Cyan" }
    }
    
    $prefix = switch($Type) {
        "SUCCESS" { "[OK]" }
        "ERROR" { "[ERROR]" }
        "WARNING" { "[WARN]" }
        default { "[INFO]" }
    }
    
    Write-Host "$prefix $Message" -ForegroundColor $color
}

function Test-SSHTunnel {
    $tunnel = Get-Process ssh -ErrorAction SilentlyContinue | 
              Where-Object { $_.CommandLine -like "*$LOCAL_PORT*$K8S_API*" -or 
                           $_.CommandLine -like "*k8s-tunnel*" }
    return $null -ne $tunnel
}

function Start-K8sTunnel {
    Write-Host "`n=== Starting Kubernetes API Tunnel ===" -ForegroundColor Cyan
    
    if (Test-SSHTunnel) {
        Write-Status "Tunnel already running" "WARNING"
        return $true
    }
    
    Write-Status "Creating SSH tunnel to Kubernetes API..."
    
    # Try using SSH config first
    try {
        $process = Start-Process ssh -ArgumentList "-fN", "k8s-tunnel" -PassThru -WindowStyle Hidden
        Start-Sleep -Seconds 2
        
        if (Test-SSHTunnel) {
            Write-Status "Tunnel established via SSH config" "SUCCESS"
            Update-Kubeconfig
            return $true
        }
    } catch {
        Write-Status "SSH config not found, using direct connection" "WARNING"
    }
    
    # Fallback to direct connection
    Write-Status "Enter password when prompted: PASSW0RD" "WARNING"
    $process = Start-Process ssh -ArgumentList `
        "-N", "-L", "${LOCAL_PORT}:${K8S_API}:${K8S_API_PORT}", "root@$BASTION_HOST" `
        -PassThru
    
    Write-Status "Waiting for tunnel to establish..."
    Start-Sleep -Seconds 3
    
    if (Test-SSHTunnel) {
        Write-Status "Tunnel established successfully" "SUCCESS"
        Update-Kubeconfig
        return $true
    } else {
        Write-Status "Failed to establish tunnel" "ERROR"
        return $false
    }
}

function Stop-K8sTunnel {
    Write-Host "`n=== Stopping Kubernetes API Tunnel ===" -ForegroundColor Cyan
    
    $tunnels = Get-Process ssh -ErrorAction SilentlyContinue | 
               Where-Object { $_.CommandLine -like "*$LOCAL_PORT*$K8S_API*" -or 
                            $_.CommandLine -like "*k8s-tunnel*" }
    
    if ($tunnels) {
        $tunnels | Stop-Process -Force
        Write-Status "Tunnel stopped" "SUCCESS"
    } else {
        Write-Status "No tunnel running" "WARNING"
    }
}

function Get-TunnelStatus {
    Write-Host "`n=== Kubernetes Connection Status ===" -ForegroundColor Cyan
    
    # Check SSH tunnel
    if (Test-SSHTunnel) {
        $tunnel = Get-Process ssh -ErrorAction SilentlyContinue | 
                  Where-Object { $_.CommandLine -like "*$LOCAL_PORT*" -or 
                               $_.CommandLine -like "*k8s-tunnel*" } | 
                  Select-Object -First 1
        Write-Status "SSH Tunnel: Active (PID: $($tunnel.Id))" "SUCCESS"
    } else {
        Write-Status "SSH Tunnel: Not running" "ERROR"
    }
    
    # Check port availability
    $tcpTest = Test-NetConnection -ComputerName localhost -Port $LOCAL_PORT -WarningAction SilentlyContinue
    if ($tcpTest.TcpTestSucceeded) {
        Write-Status "Local port $LOCAL_PORT : Open" "SUCCESS"
    } else {
        Write-Status "Local port $LOCAL_PORT : Closed" "ERROR"
    }
    
    # Check kubectl
    try {
        $env:KUBECONFIG = "$env:USERPROFILE\.kube\config"
        $nodes = kubectl get nodes --request-timeout=3s 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Kubectl: Connected" "SUCCESS"
            Write-Host "`nCluster Nodes:" -ForegroundColor Cyan
            Write-Host $nodes
        } else {
            Write-Status "Kubectl: Not connected" "ERROR"
        }
    } catch {
        Write-Status "Kubectl: Not available" "ERROR"
    }
    
    # Check current kubeconfig
    $kubeconfig = Get-Content "$env:USERPROFILE\.kube\config" -Raw
    if ($kubeconfig -like "*localhost:$LOCAL_PORT*") {
        Write-Status "Kubeconfig: Configured for tunnel" "SUCCESS"
    } else {
        Write-Status "Kubeconfig: Using direct connection" "WARNING"
    }
}

function Update-Kubeconfig {
    $configPath = "$env:USERPROFILE\.kube\config"
    
    if (-not (Test-Path $configPath)) {
        Write-Status "Kubeconfig not found" "ERROR"
        return
    }
    
    $config = Get-Content $configPath -Raw
    
    if ($config -like "*localhost:$LOCAL_PORT*") {
        Write-Status "Kubeconfig already configured for tunnel" "WARNING"
        return
    }
    
    # Backup
    $backupPath = "$configPath.direct"
    if (-not (Test-Path $backupPath)) {
        Copy-Item $configPath $backupPath
        Write-Status "Backup created: $backupPath" "SUCCESS"
    }
    
    # Update to localhost
    $newConfig = $config -replace "https://[\d\.]+:6443", "https://localhost:$LOCAL_PORT"
    Set-Content $configPath $newConfig
    Write-Status "Kubeconfig updated for tunnel access" "SUCCESS"
}

function Test-K8sConnection {
    Write-Host "`n=== Testing Kubernetes Connection ===" -ForegroundColor Cyan
    
    if (-not (Test-SSHTunnel)) {
        Write-Status "Starting tunnel for test..." "WARNING"
        Start-K8sTunnel
    }
    
    Write-Status "Running connection tests..."
    
    # Test 1: API Version
    Write-Host "`n1. API Version:" -ForegroundColor Yellow
    kubectl version --short --request-timeout=5s
    
    # Test 2: Namespaces
    Write-Host "`n2. Namespaces:" -ForegroundColor Yellow
    kubectl get namespaces --request-timeout=5s
    
    # Test 3: Nodes
    Write-Host "`n3. Cluster Nodes:" -ForegroundColor Yellow
    kubectl get nodes -o wide --request-timeout=5s
    
    # Test 4: Panda namespace
    Write-Host "`n4. Panda Namespace Pods:" -ForegroundColor Yellow
    kubectl get pods -n panda --request-timeout=5s
    
    if ($LASTEXITCODE -eq 0) {
        Write-Status "All tests passed!" "SUCCESS"
    } else {
        Write-Status "Some tests failed" "ERROR"
    }
}

function Connect-Direct {
    Write-Host "`n=== Direct SSH Connection ===" -ForegroundColor Cyan
    Write-Status "Connecting to bastion host..."
    Write-Status "Password: PASSW0RD" "WARNING"
    ssh prisma-bastion
}

# Main execution
Write-Host @"
================================================================================
Kubernetes Connection Manager
================================================================================
"@ -ForegroundColor Cyan

switch ($Action) {
    "start" { 
        Start-K8sTunnel
        Get-TunnelStatus
    }
    "stop" { 
        Stop-K8sTunnel 
    }
    "status" { 
        Get-TunnelStatus 
    }
    "test" { 
        Test-K8sConnection 
    }
    "direct" { 
        Connect-Direct 
    }
}

Write-Host "`n================================================================================`n" -ForegroundColor Cyan
