# 🚀 Automated Infrastructure Setup

## Overview

The Focus Server Automation framework now **automatically sets up all required infrastructure** before running tests:

- ✅ **RabbitMQ Port-Forward** - Automatic connection to K8s RabbitMQ
- ✅ **Focus Server Port-Forward** - Automatic connection to K8s Focus Server  
- ✅ **SSH Authentication** - Automated using stored credentials
- ✅ **Auto-Cleanup** - All resources cleaned up after tests

**No manual setup required!** Just run the tests and everything is handled automatically.

---

## Quick Start

### **Option 1: Use the Helper Script (Recommended)**

```bash
# Run all tests with auto-setup
py scripts/run_tests_auto.py

# Run only unit tests (no infrastructure)
py scripts/run_tests_auto.py --unit

# Run integration tests
py scripts/run_tests_auto.py --integration

# Run specific test file
py scripts/run_tests_auto.py --file=tests/integration/api/test_live_monitoring_flow.py

# Verbose output
py scripts/run_tests_auto.py -v
```

### **Option 2: Use pytest Directly**

```bash
# Auto-setup happens automatically!
py -m pytest tests/ -v --env=staging

# Skip auto-setup for local testing
py -m pytest tests/ -v --env=local
```

---

## How It Works

### **1. Session-Level Fixture**

The `auto_setup_infrastructure` fixture in `conftest.py` runs once per test session:

```python
@pytest.fixture(scope="session", autouse=True)
def auto_setup_infrastructure(config_manager, request):
    # Automatically sets up RabbitMQ and Focus Server
    # Runs before any tests
    # Cleans up after all tests complete
```

### **2. Port-Forward Managers**

Two managers handle infrastructure:

#### **RabbitMQConnectionManager**
- Discovers RabbitMQ service in K8s
- Extracts credentials from secrets
- Starts `kubectl port-forward` via SSH
- Validates connection

#### **FocusServerConnectionManager**  
- Discovers Focus Server service in K8s
- Starts `kubectl port-forward` via SSH
- Validates HTTP endpoint

### **3. Automated Flow**

```
Start Tests
    ↓
Load Config (SSH credentials from environments.yaml)
    ↓
Connect to K8s host via SSH (using paramiko)
    ↓
Discover services (kubectl get svc)
    ↓
Start port-forwards (kubectl port-forward --address 0.0.0.0)
    ↓
Validate connections
    ↓
RUN TESTS ✅
    ↓
Cleanup (close SSH, stop port-forwards)
    ↓
Done
```

---

## Configuration

### **environments.yaml**

```yaml
staging:
  ssh:
    host: "10.10.10.150"
    port: 22
    username: "prisma"
    password: "PASSW0RD"  # For automation - consider using vault
  
  focus_server:
    base_url: "http://10.10.10.150:8500"  # After port-forward
  
  rabbitmq:
    host: "10.10.10.150"
    port: 5672
    username: "user"
    password: "prismapanda"
```

### **Security Note**

SSH passwords are stored in `environments.yaml` for automation. Consider:
- Using SSH keys instead (set `key_file` instead of `password`)
- Using environment variables
- Using a secrets manager (HashiCorp Vault, AWS Secrets Manager)

---

## Behavior by Environment

| Environment | Auto-Setup | Description |
|------------|-----------|-------------|
| **staging** | ✅ YES | Full auto-setup (port-forwards, SSH) |
| **production** | ✅ YES | Full auto-setup |
| **local** | ❌ NO | Assumes services run locally |

---

## Troubleshooting

### **Port-Forward Fails**

```
⚠️  Focus Server setup FAILED (tests may fail)
```

**Possible causes:**
1. SSH credentials incorrect
2. Kubernetes service not found
3. Network connectivity issue

**Solution:**
```bash
# Test SSH manually
ssh prisma@10.10.10.150

# Check K8s services
ssh prisma@10.10.10.150
kubectl get svc -n default | grep focus-server
```

### **Tests Still Fail After Setup**

Check if services are actually accessible:

```bash
# Test Focus Server (after port-forward)
curl http://10.10.10.150:8500/sensors

# Test RabbitMQ (after port-forward)
telnet 10.10.10.150 5672
```

### **Disable Auto-Setup**

If you need to disable auto-setup:

```bash
# Use local environment (skips auto-setup)
py -m pytest tests/ --env=local
```

---

## Advanced Usage

### **Run Only RabbitMQ Tests**

```bash
py scripts/run_tests_auto.py --markers="rabbitmq" -v
```

### **Run Without RabbitMQ Tests**

```bash
py -m pytest tests/ -v -m "not rabbitmq"
```

### **Custom Port-Forward**

If you need custom port-forward settings, modify:

- `src/infrastructure/focus_server_manager.py`
- `src/infrastructure/rabbitmq_manager.py`

### **Manual Port-Forward**

If auto-setup fails, you can still forward manually:

```bash
# On remote server
ssh prisma@10.10.10.150
kubectl port-forward --address 0.0.0.0 svc/focus-server 8500:8500 &
kubectl port-forward --address 0.0.0.0 svc/rabbitmq-panda 5672:5672 15672:15672 &
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  pytest (Test Runner)                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. conftest.py (auto_setup_infrastructure fixture)         │
│     ↓                                                        │
│  2. FocusServerConnectionManager                            │
│     - SSH → K8s → kubectl port-forward                      │
│     - Validates HTTP endpoint                               │
│     ↓                                                        │
│  3. RabbitMQConnectionManager                               │
│     - SSH → K8s → kubectl get secret                        │
│     - SSH → K8s → kubectl port-forward                      │
│     - Validates MQ connection                               │
│     ↓                                                        │
│  4. RUN TESTS                                               │
│     - tests/unit/ (no infrastructure)                       │
│     - tests/integration/ (uses port-forwards)               │
│     ↓                                                        │
│  5. Cleanup                                                 │
│     - Close SSH connections                                 │
│     - Stop port-forwards                                    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## What's Automated

| Component | Before | After |
|-----------|--------|-------|
| **SSH Connection** | Manual password entry | ✅ Automated (paramiko) |
| **RabbitMQ Port-Forward** | Manual kubectl command | ✅ Automated |
| **Focus Server Port-Forward** | Manual kubectl command | ✅ Automated |
| **Service Discovery** | Manual kubectl get svc | ✅ Automated |
| **Credential Extraction** | Manual kubectl get secret | ✅ Automated |
| **Connection Validation** | Manual testing | ✅ Automated |
| **Cleanup** | Manual process kill | ✅ Automated |

---

## Related Files

- `src/infrastructure/focus_server_manager.py` - Focus Server automation
- `src/infrastructure/rabbitmq_manager.py` - RabbitMQ automation
- `tests/conftest.py` - Auto-setup fixture
- `scripts/run_tests_auto.py` - Helper script
- `config/environments.yaml` - Configuration

---

## Summary

**Before:**
```bash
# Manual steps required
ssh prisma@10.10.10.150
kubectl port-forward svc/focus-server 8500:8500 &
kubectl port-forward svc/rabbitmq-panda 5672:5672 &
# Then run tests
py -m pytest tests/ -v
# Manual cleanup
```

**After:**
```bash
# One command - everything automatic!
py scripts/run_tests_auto.py
```

🎉 **100% Autonomous Testing!**

