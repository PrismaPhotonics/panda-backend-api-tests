# Professional SSH Setup Script for Kubernetes Access
# =====================================================

Write-Host @"
================================================================================
Professional SSH & Kubernetes Setup
================================================================================
"@ -ForegroundColor Cyan

# Check if SSH keys already exist
$keyPath = "$env:USERPROFILE\.ssh\k8s_prisma_key"
$configPath = "$env:USERPROFILE\.ssh\config"

Write-Host "`nStep 1: SSH Key Setup" -ForegroundColor Yellow
Write-Host "---------------------" -ForegroundColor Yellow

if (Test-Path "$keyPath") {
    Write-Host "[OK] SSH key already exists at: $keyPath" -ForegroundColor Green
} else {
    Write-Host "Creating new SSH key pair..." -ForegroundColor Cyan
    
    # Generate SSH key
    ssh-keygen -t ed25519 -C "$env:USERNAME@prisma" -f $keyPath -N '""'
    
    if (Test-Path "$keyPath") {
        Write-Host "[OK] SSH key created successfully" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Failed to create SSH key" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`nStep 2: SSH Config Setup" -ForegroundColor Yellow
Write-Host "------------------------" -ForegroundColor Yellow

# Create SSH config
$sshConfig = @"
# ========================================
# Prisma Kubernetes Infrastructure Access
# ========================================

# Bastion Host (Jump Server)
Host prisma-bastion
    HostName 10.10.100.3
    User root
    Port 22
    IdentityFile ~/.ssh/k8s_prisma_key
    PasswordAuthentication yes
    PreferredAuthentications publickey,password
    StrictHostKeyChecking accept-new
    
# Worker Node (via Bastion)
Host prisma-worker
    HostName 10.10.100.113
    User prisma
    Port 22
    ProxyJump prisma-bastion
    IdentityFile ~/.ssh/k8s_prisma_key
    StrictHostKeyChecking accept-new
    
# Kubernetes API Tunnel
Host k8s-tunnel
    HostName 10.10.100.3
    User root
    Port 22
    LocalForward 6443 10.10.100.102:6443
    IdentityFile ~/.ssh/k8s_prisma_key
    PasswordAuthentication yes
    ControlMaster auto
    ControlPath ~/.ssh/k8s-control-%h-%p-%r
    ControlPersist 10m
    ServerAliveInterval 30
    ServerAliveCountMax 3
    StrictHostKeyChecking accept-new

# Alternative Staging Access
Host staging-host
    HostName 10.10.10.10
    User root
    Port 22
    IdentityFile ~/.ssh/k8s_prisma_key
    PasswordAuthentication yes
    StrictHostKeyChecking accept-new
"@

# Backup existing config if exists
if (Test-Path $configPath) {
    $backupPath = "$configPath.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item $configPath $backupPath
    Write-Host "[OK] Existing SSH config backed up to: $backupPath" -ForegroundColor Green
}

# Write new config
Set-Content -Path $configPath -Value $sshConfig -Encoding UTF8
Write-Host "[OK] SSH config created/updated" -ForegroundColor Green

Write-Host "`nStep 3: Known Hosts Setup" -ForegroundColor Yellow
Write-Host "-------------------------" -ForegroundColor Yellow

# Add known hosts (using the keys you provided)
$knownHostsPath = "$env:USERPROFILE\.ssh\known_hosts"
$knownHosts = @"
10.10.100.3 ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFlVqfheQgyFc9HYCyLmCtpPSI+B5AuuAL1RRJqrHyqM
10.10.100.3 ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC6xfdtGpQqjNYi42xmmI/yOugCDB9hJ69Zz7RNGZY6B48bPpz5V+A6vr5Agtt5Oo2Z3gUn4HZfbYSTgD3nxKhB/ObKvNsu0hp7QQH+9FmgD8+IUFq6C2/O0iCX3cnwdVgZ+pk4Gb6yqVm4V3tkc9J+4hGWiIFRZrHRS1Cq3QJQB+PeHn2MeRVAa4ppOwfTYmVf2F/0nguPl21ssKRlIdZwSFJLIeOLNn4QKVk8kitAmcNsOyUTghySLcqSqFUvAjp1aeGB/pCAFYslg4MdUncT2xzMYbhDfVaMnmYWx8VtccsGq9QvBLONqdNjsfqxhQ3+qUreHE6c/Zs4xUf448+5ladxe80rs+FSlydE7txaToDEl5OeQaajLVnb3IJBX+mExt/NfYB8TQwBoplJLP3DXxHHeUEpwKaNmrkSPUq1tiZunVmf3VWciNaaGmtz/Oaez56MfP8aIrQb4REEDGViKoCxFwMeZzTkTWYueMtVaiCV6MODjZOkscvRDZv5SQE=
10.10.100.3 ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBHVm+7aUu1/nFKPyXnuSr+/KWsSWv2wEgbhkOvBwZqVh2c2LUIX7Ln9LmNphxIhDsmyaLUGC2FizO7OKf3JLzgM=
10.10.10.10 ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIF6kCSpbMuSv6E5uGhyxtwdnFT8lwNT1LAf1hRRd7mCR
10.10.10.10 ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC7XQTF4LAwq+scsv6JeuLXaSQBwLwfZPfMy0099jOcJVsS2goRav5C6MOjOV1cQeJVOAEWjfccgHw1HN11A9PuCsxm0DfSrW/5q3nrmrbijUPoXdLMxcZ5j6EaW8qtaBlBem/BMoG3X+1Itq+J7i+FQbuDy6Vvt2VPqzgJ2sWEg5vCmWXp5yRuYbEu3pzburkxy7/H0ZURwzy3HBfyIZbTH9enQG2zsJMI5E7Csyb+HZsao77zCeCSxVgxyVyq14R1VPs6jkpNK5Vnj9FfjBBD1PTQb0Mcd5UEpaKus50hNatLZklILcimG44WNHM2XExynbZ4zc1M7Pw206qUcslsRKHmz3AavoXjg411xihuNJdEG/Whkd8R9PnAmyoNl+K3MP5q92CgRUeDrCluu9AhYbtIyfDjJv7zHB6vW42rfn9dGueTKTFi7gGYjJLsf3OlLlb1+xzYwUZMAgN/E36HjtD5oQxv1XK37Z7HthvC8Uli9zk7lhQzbt1BoL3rG60=
"@

# Append to known_hosts if not already there
if (Test-Path $knownHostsPath) {
    $existingHosts = Get-Content $knownHostsPath -Raw
    if ($existingHosts -notlike "*10.10.100.3*") {
        Add-Content -Path $knownHostsPath -Value "`n$knownHosts"
        Write-Host "[OK] Added known hosts for 10.10.100.3" -ForegroundColor Green
    } else {
        Write-Host "[OK] Known hosts already configured" -ForegroundColor Green
    }
} else {
    Set-Content -Path $knownHostsPath -Value $knownHosts
    Write-Host "[OK] Created known_hosts file" -ForegroundColor Green
}

Write-Host "`nStep 4: Display SSH Key (for copying to servers)" -ForegroundColor Yellow
Write-Host "------------------------------------------------" -ForegroundColor Yellow

if (Test-Path "$keyPath.pub") {
    $pubKey = Get-Content "$keyPath.pub"
    Write-Host "`nYour public key:" -ForegroundColor Cyan
    Write-Host $pubKey -ForegroundColor White
    Write-Host "`nTo add this key to the servers, run:" -ForegroundColor Yellow
    Write-Host "1. ssh root@10.10.100.3" -ForegroundColor White
    Write-Host "2. Add the key to ~/.ssh/authorized_keys" -ForegroundColor White
    Write-Host "3. Then from bastion: ssh-copy-id -i ~/.ssh/k8s_prisma_key.pub prisma@10.10.100.113" -ForegroundColor White
}

Write-Host "`nStep 5: Quick Connection Commands" -ForegroundColor Yellow
Write-Host "---------------------------------" -ForegroundColor Yellow

Write-Host "`nYou can now use these commands:" -ForegroundColor Cyan
Write-Host "  ssh prisma-bastion     # Connect to bastion (10.10.100.3)" -ForegroundColor White
Write-Host "  ssh prisma-worker      # Connect to worker via bastion" -ForegroundColor White
Write-Host "  ssh -fN k8s-tunnel     # Start K8s API tunnel (background)" -ForegroundColor White
Write-Host "  ssh staging-host       # Connect to staging (10.10.10.10)" -ForegroundColor White

Write-Host "`n================================================================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
