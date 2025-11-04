# PowerShell script to setup SSH tunnel for Kubernetes API
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host "Setting up SSH Tunnel for Kubernetes API Access" -ForegroundColor Cyan
Write-Host "=================================================================================" -ForegroundColor Cyan

Write-Host "`nThis script will create an SSH tunnel to access Kubernetes API"
Write-Host "The tunnel will forward localhost:6443 to 10.10.100.102:6443"

# Check if ssh is available
$sshPath = Get-Command ssh -ErrorAction SilentlyContinue
if (-not $sshPath) {
    Write-Host "`n[ERROR] SSH client not found!" -ForegroundColor Red
    Write-Host "Please install OpenSSH client or use Git Bash"
    exit 1
}

Write-Host "`n[OK] SSH client found" -ForegroundColor Green

# Start SSH tunnel in background
Write-Host "`nStarting SSH tunnel..." -ForegroundColor Yellow
Write-Host "You will be prompted for password: PASSW0RD" -ForegroundColor Yellow

$tunnelCommand = "ssh -N -L 6443:10.10.100.102:6443 root@10.10.100.3"

Write-Host "`nCommand: $tunnelCommand" -ForegroundColor Cyan

# Start the tunnel process
Start-Process -FilePath "ssh" -ArgumentList "-N", "-L", "6443:10.10.100.102:6443", "root@10.10.100.3" -PassThru

Write-Host "`n[INFO] SSH tunnel process started" -ForegroundColor Green
Write-Host "Please enter the password in the SSH window: PASSW0RD" -ForegroundColor Yellow

# Wait a bit for tunnel to establish
Start-Sleep -Seconds 3

# Test if tunnel is working
Write-Host "`nTesting tunnel connection..." -ForegroundColor Cyan
$testConnection = Test-NetConnection -ComputerName localhost -Port 6443 -WarningAction SilentlyContinue

if ($testConnection.TcpTestSucceeded) {
    Write-Host "[OK] Tunnel is working! Port 6443 is accessible on localhost" -ForegroundColor Green
    
    # Update kubeconfig to use localhost
    Write-Host "`nUpdating kubeconfig to use localhost..." -ForegroundColor Cyan
    $kubeconfigPath = "$env:USERPROFILE\.kube\config"
    
    if (Test-Path $kubeconfigPath) {
        # Backup current config
        $backupPath = "$kubeconfigPath.backup"
        Copy-Item $kubeconfigPath $backupPath
        Write-Host "[OK] Backup created: $backupPath" -ForegroundColor Green
        
        # Read and update config
        $content = Get-Content $kubeconfigPath -Raw
        $newContent = $content -replace "server: https://10.10.100.102:6443", "server: https://localhost:6443"
        Set-Content $kubeconfigPath $newContent
        
        Write-Host "[OK] Kubeconfig updated to use localhost:6443" -ForegroundColor Green
    }
    
    Write-Host "`n=================================================================================" -ForegroundColor Green
    Write-Host "SUCCESS! SSH Tunnel is ready" -ForegroundColor Green
    Write-Host "=================================================================================" -ForegroundColor Green
    Write-Host "`nYou can now run Kubernetes tests!"
    Write-Host "Keep this window open to maintain the tunnel."
} else {
    Write-Host "[ERROR] Tunnel is not working!" -ForegroundColor Red
    Write-Host "Please check the SSH window for errors" -ForegroundColor Yellow
}

Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
