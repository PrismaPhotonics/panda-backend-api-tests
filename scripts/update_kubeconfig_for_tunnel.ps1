# Update kubeconfig to use localhost (for SSH tunnel)

$configPath = "$env:USERPROFILE\.kube\config"

Write-Host "Updating kubeconfig to use localhost:6443 for SSH tunnel..." -ForegroundColor Cyan

# Backup current config
$backupPath = "$configPath.backup_direct"
Copy-Item $configPath $backupPath -Force
Write-Host "[OK] Backup saved to: $backupPath" -ForegroundColor Green

# Read config
$config = Get-Content $configPath -Raw

# Update server address to localhost
$newConfig = $config -replace 'server: https://10\.10\.100\.102:6443', 'server: https://localhost:6443'

# Save updated config
Set-Content $configPath $newConfig -Encoding UTF8

Write-Host "[OK] Kubeconfig updated to use localhost:6443" -ForegroundColor Green
Write-Host ""
Write-Host "Now you need to:" -ForegroundColor Yellow
Write-Host "1. Open a new PowerShell/CMD window" -ForegroundColor White
Write-Host "2. Run: .\scripts\simple_k8s_tunnel.bat" -ForegroundColor White
Write-Host "3. Enter password: PASSW0RD" -ForegroundColor White
Write-Host "4. Keep that window open!" -ForegroundColor White
Write-Host "5. In this window, run: kubectl get nodes" -ForegroundColor White
