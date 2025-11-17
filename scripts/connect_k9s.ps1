# ============================================================================
# Connect to K9s in Production Environment (Panda Namespace)
# ============================================================================
# This script helps you connect to K9s for monitoring Kubernetes pods
# ============================================================================

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("instructions", "connect", "quick")]
    [string]$Mode = "instructions"
)

Write-Host "`n════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  K9s Connection - New Production Environment" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan

# Connection details
$JUMP_HOST = "10.10.100.3"
$JUMP_USER = "root"
# NOTE: Password required - ask team lead or check secure vault
$JUMP_PASSWORD = $env:JUMP_PASSWORD

$TARGET_HOST = "10.10.100.113"
$TARGET_USER = "prisma"
# NOTE: Password required - ask team lead or check secure vault
$TARGET_PASSWORD = $env:TARGET_PASSWORD

$K8S_NAMESPACE = "panda"

switch ($Mode) {
    "instructions" {
        Write-Host "`n📋 Connection Instructions:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "1️⃣  Connect to Jump Host (panda2worker):" -ForegroundColor Green
        Write-Host "    ssh $JUMP_USER@$JUMP_HOST" -ForegroundColor White
        Write-Host "    Password: <ask team lead>" -ForegroundColor DarkGray
        Write-Host ""
        Write-Host "2️⃣  From Jump Host, connect to Worker Node:" -ForegroundColor Green
        Write-Host "    ssh $TARGET_USER@$TARGET_HOST" -ForegroundColor White
        Write-Host "    Password: <ask team lead>" -ForegroundColor DarkGray
        Write-Host ""
        Write-Host "3️⃣  Launch K9s:" -ForegroundColor Green
        Write-Host "    k9s" -ForegroundColor White
        Write-Host "    # OR specify namespace:" -ForegroundColor DarkGray
        Write-Host "    k9s -n $K8S_NAMESPACE" -ForegroundColor White
        Write-Host ""
        Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "📌 K9s Quick Reference:" -ForegroundColor Yellow
        Write-Host "   :pods          - View all pods" -ForegroundColor White
        Write-Host "   :svc           - View services" -ForegroundColor White
        Write-Host "   :deploy        - View deployments" -ForegroundColor White
        Write-Host "   :logs          - View logs" -ForegroundColor White
        Write-Host "   :describe      - Describe resource" -ForegroundColor White
        Write-Host "   /filter        - Filter by name" -ForegroundColor White
        Write-Host "   l              - View logs of selected pod" -ForegroundColor White
        Write-Host "   d              - Describe selected resource" -ForegroundColor White
        Write-Host "   e              - Edit resource" -ForegroundColor White
        Write-Host "   s              - Shell into pod" -ForegroundColor White
        Write-Host "   ctrl+d         - Delete resource" -ForegroundColor White
        Write-Host "   ?              - Help" -ForegroundColor White
        Write-Host ""
        Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "📦 Important Pods in 'panda' namespace:" -ForegroundColor Yellow
        Write-Host "   • panda-panda-focus-server-*    - Main Focus Server" -ForegroundColor White
        Write-Host "   • mongodb-*                     - MongoDB Database" -ForegroundColor White
        Write-Host "   • rabbitmq-panda-0              - RabbitMQ Message Broker" -ForegroundColor White
        Write-Host "   • grpc-job-*                    - gRPC Processing Jobs" -ForegroundColor White
        Write-Host "   • panda-panda-player-*          - Player Service" -ForegroundColor White
        Write-Host "   • panda-panda-segy-recorder-*   - SEGY Recorder" -ForegroundColor White
        Write-Host ""
        Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "🔧 Kubectl Commands (from worker node):" -ForegroundColor Yellow
        Write-Host "   kubectl get pods -n $K8S_NAMESPACE" -ForegroundColor White
        Write-Host "   kubectl get svc -n $K8S_NAMESPACE" -ForegroundColor White
        Write-Host "   kubectl logs <pod-name> -n $K8S_NAMESPACE" -ForegroundColor White
        Write-Host "   kubectl logs <pod-name> -n $K8S_NAMESPACE -f   # Follow logs" -ForegroundColor White
        Write-Host "   kubectl describe pod <pod-name> -n $K8S_NAMESPACE" -ForegroundColor White
        Write-Host "   kubectl exec -it <pod-name> -n $K8S_NAMESPACE -- /bin/bash" -ForegroundColor White
        Write-Host ""
        Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "💡 Tips:" -ForegroundColor Yellow
        Write-Host "   • K9s is already installed on the worker node" -ForegroundColor White
        Write-Host "   • No need to download kubeconfig - kubectl is already configured" -ForegroundColor White
        Write-Host "   • All pods are in the 'panda' namespace" -ForegroundColor White
        Write-Host "   • For automation tests, use this SSH path to collect logs" -ForegroundColor White
        Write-Host ""
        Write-Host "Run: .\connect_k9s.ps1 -Mode connect   # To open SSH" -ForegroundColor Cyan
        Write-Host ""
    }
    
    "connect" {
        Write-Host "`n🚀 Launching SSH connection..." -ForegroundColor Green
        Write-Host ""
        Write-Host "Connecting to: $JUMP_USER@$JUMP_HOST" -ForegroundColor Yellow
        Write-Host "Password: <from environment variable>" -ForegroundColor DarkGray
        Write-Host ""
        Write-Host "After connecting, run:" -ForegroundColor Cyan
        Write-Host "  ssh $TARGET_USER@$TARGET_HOST" -ForegroundColor White
        Write-Host "  k9s" -ForegroundColor White
        Write-Host ""
        
        # Open SSH
        Start-Process "ssh" -ArgumentList "$JUMP_USER@$JUMP_HOST" -NoNewWindow -Wait
    }
    
    "quick" {
        Write-Host "`n⚡ Quick SSH Commands:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "# Copy and paste into your terminal:" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "ssh $JUMP_USER@$JUMP_HOST" -ForegroundColor White
        Write-Host "# Password: <ask team lead>" -ForegroundColor DarkGray
        Write-Host ""
        Write-Host "ssh $TARGET_USER@$TARGET_HOST" -ForegroundColor White
        Write-Host "# Password: <ask team lead>" -ForegroundColor DarkGray
        Write-Host ""
        Write-Host "k9s -n $K8S_NAMESPACE" -ForegroundColor White
        Write-Host ""
    }
}

Write-Host "════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

