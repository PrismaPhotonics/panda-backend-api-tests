# ============================================================================
# Manual Connection to 10.10.10.150 via Jump Host
# ============================================================================
# Since ProxyJump requires password, this script opens manual connection
# ============================================================================

Write-Host "`n════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Manual Connection to VM-150 via Jump Host" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "This will connect you through jump host (10.10.10.10) to target (10.10.10.150)" -ForegroundColor Yellow
Write-Host ""

Write-Host "Steps:" -ForegroundColor Cyan
Write-Host "  1. Connect to jump host: root@10.10.10.10" -ForegroundColor White
Write-Host "     Password: ask team lead" -ForegroundColor DarkGray
Write-Host "  2. From jump host, connect to target: ssh prisma@10.10.10.150" -ForegroundColor White
Write-Host "     This should work WITHOUT password (key is already added)" -ForegroundColor Green
Write-Host "  3. Run k9s" -ForegroundColor White
Write-Host ""

$continue = Read-Host "Press Enter to start connection (or Ctrl+C to cancel)"

Write-Host "`nConnecting to jump host..." -ForegroundColor Cyan
Write-Host "After connecting, run: ssh prisma@10.10.10.150" -ForegroundColor Yellow
Write-Host ""

# Connect to jump host - user will continue manually from there
Start-Process "ssh" -ArgumentList "root@10.10.10.10" -NoNewWindow

Write-Host "`nOnce connected to target server, run:" -ForegroundColor Cyan
Write-Host "  k9s           # Launch k9s" -ForegroundColor White
Write-Host "  k9s -n panda  # Launch k9s with namespace" -ForegroundColor White
Write-Host ""

