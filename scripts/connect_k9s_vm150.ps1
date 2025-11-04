# ============================================================================
# Quick Connect to K9s via 10.10.10.150 (vm-150)
# ============================================================================
# This script provides a quick way to connect to k9s on 10.10.10.150
# Prerequisites: Run setup_ssh_agent_vm150.ps1 first to setup SSH agent
# ============================================================================

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("connect", "test", "setup")]
    [string]$Action = "connect"
)

$SSH_HOST = "vm-150"  # SSH config alias
$SSH_USER = "prisma"
$SSH_TARGET = "prisma@10.10.10.150"
$K8S_NAMESPACE = "panda"

switch ($Action) {
    "setup" {
        Write-Host "`n🔧 Setting up SSH agent with vm_150_key..." -ForegroundColor Yellow
        Write-Host ""
        
        if (-not (Test-Path "$PSScriptRoot\setup_ssh_agent_vm150.ps1")) {
            Write-Host "[ERROR] Setup script not found!" -ForegroundColor Red
            exit 1
        }
        
        & "$PSScriptRoot\setup_ssh_agent_vm150.ps1"
    }
    
    "test" {
        Write-Host "`n🧪 Testing SSH connection to 10.10.10.150..." -ForegroundColor Yellow
        Write-Host ""
        
        # Check if key is loaded
        Write-Host "Checking SSH agent..." -ForegroundColor Cyan
        $keys = ssh-add -l 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[WARNING] No SSH keys loaded in agent" -ForegroundColor Yellow
            Write-Host "Run: .\connect_k9s_vm150.ps1 -Action setup" -ForegroundColor Cyan
        } else {
            Write-Host "[OK] SSH keys loaded:" -ForegroundColor Green
            ssh-add -l
        }
        
        Write-Host "`nTesting connection..." -ForegroundColor Cyan
        ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no $SSH_TARGET "echo '✅ Connection successful!'; hostname; which k9s"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n[SUCCESS] Connection test passed!" -ForegroundColor Green
        } else {
            Write-Host "`n[FAILED] Connection test failed" -ForegroundColor Red
            Write-Host "Troubleshooting:" -ForegroundColor Yellow
            Write-Host "  1. Ensure SSH key is added to agent: .\connect_k9s_vm150.ps1 -Action setup" -ForegroundColor White
            Write-Host "  2. Verify public key is in server's ~/.ssh/authorized_keys" -ForegroundColor White
            Write-Host "  3. Check server is accessible: Test-NetConnection 10.10.10.150 -Port 22" -ForegroundColor White
        }
    }
    
    "connect" {
        Write-Host "`n════════════════════════════════════════════════════════════" -ForegroundColor Cyan
        Write-Host "  Quick Connect to K9s - 10.10.10.150" -ForegroundColor Cyan
        Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
        Write-Host ""
        
        # Check if key is loaded
        $keys = ssh-add -l 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[WARNING] No SSH keys loaded in agent" -ForegroundColor Yellow
            Write-Host "Setting up SSH agent first..." -ForegroundColor Cyan
            & "$PSScriptRoot\connect_k9s_vm150.ps1" -Action setup
            Write-Host ""
        }
        
        Write-Host "🚀 Connecting to 10.10.10.150..." -ForegroundColor Green
        Write-Host ""
        Write-Host "After connecting, run:" -ForegroundColor Yellow
        Write-Host "  k9s              # Launch k9s" -ForegroundColor White
        Write-Host "  k9s -n $K8S_NAMESPACE   # Launch k9s with namespace" -ForegroundColor White
        Write-Host ""
        Write-Host "Quick K9s commands:" -ForegroundColor Cyan
        Write-Host "  :pods          - View pods" -ForegroundColor DarkGray
        Write-Host "  :svc           - View services" -ForegroundColor DarkGray
        Write-Host "  :deploy        - View deployments" -ForegroundColor DarkGray
        Write-Host "  l              - View logs" -ForegroundColor DarkGray
        Write-Host "  ?              - Help" -ForegroundColor DarkGray
        Write-Host ""
        
        # Connect via SSH config alias (recommended)
        Write-Host "Connecting via SSH config alias: $SSH_HOST" -ForegroundColor DarkGray
        Start-Process "ssh" -ArgumentList $SSH_HOST -NoNewWindow
    }
}

Write-Host ""

