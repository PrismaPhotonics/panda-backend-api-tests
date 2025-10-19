# 🚀 K9s Quick Setup - 2 Steps Only!

**Date:** October 19, 2025

---

## ✅ Step 1: Download the RIGHT Kubeconfig

**Current problem:** You have kubeconfigs for `10.10.10.151` (wrong cluster)  
**We need:** Kubeconfig for `10.10.100.102` (cluster with "panda" namespace)

### How to get it:

1. **Open Dashboard:**
   ```
   https://10.10.100.102/
   ```

2. **Find the kubeconfig download button:**
   - Look in top-right corner (user profile icon)
   - OR: Look for ⚙️ Settings
   - OR: Look for "Kubeconfig" link
   - **Download the file**

3. **Save it as:**
   ```
   C:\Users\roy.avrahami\Downloads\kubeconfig-panda.yaml
   ```

---

## ✅ Step 2: Download K9s Binary

1. **Go to:**
   ```
   https://github.com/derailed/k9s/releases
   ```

2. **Download:**
   ```
   k9s_windows_amd64.tar.gz
   ```
   (From the latest release - NOT source code!)

3. **Extract it** (right-click → Extract All)
   - You'll get `k9s.exe`

---

## ✅ Step 3: Run This Command

After downloading both files, run:

```powershell
# Copy kubeconfig
Copy-Item "$env:USERPROFILE\Downloads\kubeconfig-panda.yaml" "$env:USERPROFILE\.kube\config-panda"

# Copy k9s.exe
Copy-Item "$env:USERPROFILE\Downloads\k9s.exe" "$env:LOCALAPPDATA\Microsoft\WindowsApps\k9s.exe"

# Set environment
$env:KUBECONFIG = "$env:USERPROFILE\.kube\config-panda"

# Test connection
kubectl get namespaces

# If you see "panda" namespace, SUCCESS!
# Then run:
k9s -n panda
```

---

## 🎯 Quick Commands After Setup

```powershell
# Always set kubeconfig first:
$env:KUBECONFIG = "$env:USERPROFILE\.kube\config-panda"

# Then run K9s:
k9s -n panda
```

**Or use the helper script:**
```powershell
. .\set_production_env.ps1
k9s -n panda
```

---

## ⚠️ Common Issues

### Issue: "panda namespace not found"
**Cause:** Using kubeconfig for wrong cluster (10.10.10.151 instead of 10.10.100.102)  
**Fix:** Download new kubeconfig from https://10.10.100.102/

### Issue: "k9s: command not found"
**Cause:** k9s.exe not in PATH  
**Fix:** Copy k9s.exe to: `C:\Users\roy.avrahami\AppData\Local\Microsoft\WindowsApps\`

### Issue: "Unable to connect to server"
**Cause:** Wrong kubeconfig or network issue  
**Fix:** Verify you can access https://10.10.100.102:6443

---

## 📋 Checklist

- [ ] Downloaded kubeconfig from https://10.10.100.102/
- [ ] Downloaded k9s_windows_amd64.tar.gz from GitHub
- [ ] Extracted k9s.exe
- [ ] Copied both files to correct locations
- [ ] Set $env:KUBECONFIG
- [ ] Tested: kubectl get namespaces (should see "panda")
- [ ] Ran: k9s -n panda

---

## 🎉 What You'll See in K9s

Once connected:
- Press `:pod` → See all pods in panda namespace
- Press `:svc` → See all services
- Press `l` on a pod → View logs
- Press `d` on a pod → Describe (details)
- Press `s` on a pod → Shell into pod
- Press `?` → Help

---

**That's it!** 🚀

Good luck!

