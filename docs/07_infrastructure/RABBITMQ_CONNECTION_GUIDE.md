# RabbitMQ Connection Setup Guide

## 🎯 **Problem**

RabbitMQ is not accessible directly from your local machine:
- ❌ Port 5672 on 10.10.10.101 is **CLOSED**
- ❌ Port 5672 on localhost is **OCCUPIED** (by another service, not RabbitMQ)
- ❌ kubectl contexts are **NOT CONFIGURED**

---

## ✅ **Solution: SSH Tunnel (Recommended!)**

### **Step 1: Create SSH Tunnel**

Open a **new terminal** and run:

```bash
ssh -L 5673:localhost:5672 -L 15673:localhost:15672 prisma@10.10.10.150
# Password: PASSW0RD
```

**Keep this terminal open!** The tunnel will stay active as long as the SSH connection is alive.

---

### **Step 2: Test Connection**

In **another terminal**:

```bash
# Test RabbitMQ connection
py scripts/rabbitmq_helper.py --test-connection --env=local

# If successful, send test commands
py scripts/rabbitmq_helper.py --send-commands --env=local

# Inspect queues
py scripts/rabbitmq_helper.py --inspect-queues --env=local
```

---

### **Step 3: Run Integration Tests**

```bash
# Run all RabbitMQ integration tests
py -m pytest tests/integration/api/ -v -m rabbitmq

# Or specific tests
py -m pytest tests/integration/api/test_dynamic_roi_adjustment.py -v
py -m pytest tests/integration/api/test_spectrogram_pipeline.py -v
```

---

## 🌐 **Access RabbitMQ Management UI**

With the SSH tunnel running:

```
http://localhost:15673
Username: prisma
Password: prismapanda
```

---

## 🔍 **Troubleshooting**

### **Problem: "Connection Refused" on localhost:5673**

```bash
# Check if SSH tunnel is running
ps aux | grep "ssh -L 5673"

# Or on Windows
tasklist | findstr ssh
```

If not running, restart the SSH tunnel (Step 1).

---

### **Problem: "Port 5673 already in use"**

```bash
# Find what's using the port
netstat -ano | findstr :5673

# Kill the process (Windows) or change the port
```

Or change the port in `config/environments.yaml`:

```yaml
rabbitmq:
  host: "localhost"
  port: 5674  # Use a different port
  management_port: 15674
```

And update the SSH tunnel:

```bash
ssh -L 5674:localhost:5672 -L 15674:localhost:15672 prisma@10.10.10.150
```

---

### **Problem: "Authentication failed"**

Check the credentials in `config/environments.yaml`:

```yaml
rabbitmq:
  username: "prisma"
  password: "prismapanda"
```

Or check on the server:

```bash
ssh prisma@10.10.10.150
sudo rabbitmqctl list_users
```

---

## 📚 **Alternative: Kubectl Port-Forward**

If you have kubectl access configured:

```bash
# Find RabbitMQ service
kubectl get svc -A | grep rabbit

# Port forward
kubectl -n default port-forward svc/rabbitmq-service 5673:5672 15673:15672
```

**Note:** You need a valid kubeconfig file for this to work.

---

## 🚀 **Quick Start Commands**

```bash
# 1. Create SSH tunnel (Terminal 1 - keep it running)
ssh -L 5673:localhost:5672 -L 15673:localhost:15672 prisma@10.10.10.150

# 2. Test connection (Terminal 2)
py scripts/rabbitmq_helper.py --test-connection --env=local

# 3. Run tests
py -m pytest tests/integration/api/ -v -m rabbitmq

# 4. Access Management UI
# Browser: http://localhost:15673
```

---

## ❓ **FAQ**

### **Q: Why port 5673 instead of 5672?**

**A:** Port 5672 on localhost is already occupied by another service (not RabbitMQ). We use 5673 to avoid conflicts.

### **Q: Can I use the staging environment instead?**

**A:** No, 10.10.10.101:5672 is not accessible (port closed). You must use SSH tunnel or kubectl port-forward.

### **Q: Do I need to keep the SSH connection open?**

**A:** Yes! The tunnel is active only while the SSH connection is alive. Close it when you're done.

### **Q: Can I run tests without RabbitMQ?**

**A:** Yes! Run tests without the `rabbitmq` marker:

```bash
py -m pytest tests/integration/api/ -v -m "not rabbitmq"
```

---

**Updated:** 08/10/2025  
**Tested on:** Windows 10, Python 3.13

