# SSH Jump Host Setup Guide
# ========================

## Overview

The staging environment requires SSH access through a jump host:
- **Jump Host**: `root@10.10.10.10`
- **Target Host**: `prisma@10.10.10.150`

The target host (`prisma@10.10.10.150`) **requires SSH key authentication** and does not accept password authentication.

## Solution Options

### Option 1: Configure SSH Key in environments.yaml (Recommended)

1. **Generate SSH Key Pair** (if not exists):
   ```powershell
   ssh-keygen -t ed25519 -f $HOME\.ssh\panda_staging_key -N '""'
   ```

2. **Copy Public Key to Jump Host**:
   ```powershell
   # First, connect to jump host and copy your public key
   type $HOME\.ssh\panda_staging_key.pub
   # Then manually add it to ~/.ssh/authorized_keys on jump host
   ssh root@10.10.10.10
   # Then from jump host, copy to target host
   ssh prisma@10.10.10.150
   ```

   OR use `ssh-copy-id` through jump host:
   ```powershell
   ssh root@10.10.10.10 "mkdir -p ~/.ssh && echo 'YOUR_PUBLIC_KEY' >> ~/.ssh/authorized_keys"
   ssh root@10.10.10.10 "ssh prisma@10.10.10.150 'mkdir -p ~/.ssh && echo \"YOUR_PUBLIC_KEY\" >> ~/.ssh/authorized_keys'"
   ```

3. **Update environments.yaml**:
   ```yaml
   ssh:
     jump_host:
       host: "10.10.10.10"
       port: 22
       username: "root"
       password: "PASSW0RD"  # For jump host only
       key_file: null  # Optional: use key for jump host too
     target_host:
       host: "10.10.10.150"
       port: 22
       username: "prisma"
       password: null  # Not used - key required
       key_file: "~/.ssh/panda_staging_key"  # REQUIRED
   ```

### Option 2: Use SSH Agent Forwarding

1. **Start SSH Agent** (Windows):
   ```powershell
   # Start SSH agent service
   Get-Service ssh-agent | Set-Service -StartupType Automatic
   Start-Service ssh-agent
   
   # Add your key to agent
   ssh-add $HOME\.ssh\panda_staging_key
   ```

2. **Ensure Key is on Target Host**:
   - Copy your public key to `~/.ssh/authorized_keys` on `prisma@10.10.10.150`

3. **Update environments.yaml** (keep password, but also allow agent):
   ```yaml
   ssh:
     target_host:
       key_file: "~/.ssh/panda_staging_key"  # For agent forwarding
   ```

### Option 3: Manual Key Copy Through Jump Host

1. **Generate Key** (if needed):
   ```powershell
   ssh-keygen -t ed25519 -f $HOME\.ssh\panda_staging_key -N '""'
   ```

2. **Copy Public Key Through Jump Host**:
   ```powershell
   # Read your public key
   $pubKey = Get-Content $HOME\.ssh\panda_staging_key.pub
   
   # Copy to jump host first
   ssh root@10.10.10.10 "echo '$pubKey' >> ~/.ssh/authorized_keys"
   
   # Then copy to target host through jump host
   ssh root@10.10.10.10 "ssh prisma@10.10.10.150 'mkdir -p ~/.ssh && echo \"$pubKey\" >> ~/.ssh/authorized_keys'"
   ```

3. **Update environments.yaml**:
   ```yaml
   ssh:
     target_host:
       key_file: "~/.ssh/panda_staging_key"
   ```

## Testing

After configuration, test the connection:

```powershell
python scripts/test_ssh_connection.py --env staging
```

## Troubleshooting

### Error: "Bad authentication type; allowed types: ['publickey']"

**Problem**: Target host requires SSH key authentication.

**Solution**: 
1. Ensure you have a valid SSH key pair
2. Copy your public key to `~/.ssh/authorized_keys` on the target host
3. Configure `key_file` in `environments.yaml`

### Error: "Permission denied (publickey)"

**Problem**: SSH key is not authorized on target host.

**Solution**:
1. Verify your public key is in `~/.ssh/authorized_keys` on target host
2. Check file permissions on target host: `chmod 600 ~/.ssh/authorized_keys`
3. Verify key file path in `environments.yaml` is correct

### Error: "Connection refused"

**Problem**: Cannot reach target host through jump host.

**Solution**:
1. Verify jump host connection: `ssh root@10.10.10.10`
2. Verify target host is reachable from jump host: `ssh root@10.10.10.10 "ssh prisma@10.10.10.150 hostname"`

## Security Notes

- **Never commit SSH private keys to git**
- **Use strong passphrases** for SSH keys in production
- **Rotate keys regularly** for security
- **Use different keys** for different environments

## References

- [SSH Key Authentication Guide](../03_architecture/SSH_KEY_AUTHENTICATION.md)
- [Professional K8s Setup](../04_testing/test_results/PROFESSIONAL_K8S_SETUP_2025-11-02.md)

