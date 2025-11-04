# Run kubectl commands via SSH through worker node
param(
    [Parameter(Mandatory=$false, Position=0)]
    [string[]]$Command = @("get", "nodes")
)

$bastion = "root@10.10.10.10"
$worker = "prisma@10.10.10.150"

Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host "Running kubectl via SSH" -ForegroundColor Cyan
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host "Command: kubectl $($Command -join ' ')" -ForegroundColor Yellow
Write-Host ""

# Build the kubectl command
$kubectlCmd = "kubectl $($Command -join ' ')"

# Run via SSH: bastion -> worker -> kubectl
ssh -t $bastion "ssh -t $worker `"$kubectlCmd`""

Write-Host ""
Write-Host "=================================================================================" -ForegroundColor Cyan
