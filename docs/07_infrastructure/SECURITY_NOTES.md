# Security Notes - SSH Password Storage

## ⚠️ **Important Security Information**

### **SSH Password in Configuration**

לצורכי **automation מלאה**, ה-SSH password נשמר ב-`config/environments.yaml`.

---

## 🔐 **Best Practices**

### **1️⃣ Development Environment (מומלץ)**

```yaml
ssh:
  username: "prisma"
  password: "PASSW0RD"  # OK for dev/staging
```

✅ מתאים ל-**development** ו-**staging**  
⚠️ **לא** מומלץ ל-production

---

### **2️⃣ Production Environment (מומלץ ביותר!)**

**השתמש ב-SSH Keys במקום passwords:**

```bash
# 1. Generate SSH key
ssh-keygen -t ed25519 -f ~/.ssh/pz_automation_key

# 2. Copy to server
ssh-copy-id -i ~/.ssh/pz_automation_key.pub prisma@10.10.10.150

# 3. Update config
```

```yaml
ssh:
  username: "prisma"
  password: null  # Not used
  key_file: "~/.ssh/pz_automation_key"
```

✅ **הרבה יותר מאובטח**  
✅ אין צורך לשמור password  
✅ Key rotation קל

---

### **3️⃣ CI/CD Environment (מומלץ)**

**השתמש ב-Environment Variables:**

```bash
# Set environment variable
export PZ_SSH_PASSWORD="your_password"
```

```python
# In code
import os
ssh_password = os.getenv("PZ_SSH_PASSWORD")
```

✅ Password לא שמור בקוד  
✅ מנוהל ע"י CI/CD system  
✅ Rotation קל

---

### **4️⃣ Secrets Management (הכי מאובטח)**

**השתמש ב-HashiCorp Vault / Azure Key Vault / AWS Secrets Manager:**

```python
from vault_client import get_secret

ssh_password = get_secret("pz/ssh/password")
```

✅ **Enterprise-grade security**  
✅ Audit trail  
✅ Automatic rotation  
✅ Access control

---

## 🛡️ **File Permissions**

וודא ש-`environments.yaml` לא נגיש לכולם:

```bash
# Linux/Mac
chmod 600 config/environments.yaml

# Verify
ls -l config/environments.yaml
# Should show: -rw------- (only you can read/write)
```

---

## 📝 **.gitignore**

וודא ש-`environments.yaml` **לא** נשמר ב-git:

```bash
# Check if in .gitignore
cat .gitignore | grep environments.yaml

# If not, add it:
echo "config/environments.yaml" >> .gitignore
```

---

## 🔄 **Password Rotation**

כשמחליפים password:

```bash
# 1. Update on server
ssh prisma@10.10.10.150
passwd

# 2. Update in config
# Edit config/environments.yaml

# 3. Test
py scripts/setup_rabbitmq_auto.py --test-connection
```

---

## ✅ **Security Checklist**

- [ ] `environments.yaml` ב-.gitignore
- [ ] File permissions: `chmod 600`
- [ ] השתמש ב-SSH keys (production)
- [ ] Password rotation policy
- [ ] Audit access logs
- [ ] Use secrets manager (enterprise)

---

## 🎯 **Recommendations by Environment**

| Environment | Method | Security Level |
|-------------|--------|----------------|
| **Local Dev** | Password in file | ⚠️ Low (OK for dev) |
| **Staging** | Password in file | ⚠️ Low-Medium |
| **CI/CD** | Environment variable | ✅ Medium |
| **Production** | SSH Keys | ✅ High |
| **Enterprise** | Secrets Manager | ✅✅ Very High |

---

## 📖 **More Info**

- [SSH Key Authentication](https://www.ssh.com/academy/ssh/key)
- [HashiCorp Vault](https://www.vaultproject.io/)
- [Azure Key Vault](https://azure.microsoft.com/en-us/services/key-vault/)
- [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/)

---

**Date:** 08/10/2025  
**Author:** QA Automation Architect

