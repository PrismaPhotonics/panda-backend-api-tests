# 🟤 Infrastructure Tests

**Category:** Infrastructure (Xray-aligned)  
**Purpose:** Validate connectivity and health of infrastructure components

---

## 📋 What Belongs Here?

Tests that validate:
- ✅ MongoDB connectivity and status
- ✅ Kubernetes cluster access and pod management
- ✅ SSH connectivity to servers
- ✅ RabbitMQ connectivity and health
- ✅ PZ system integration
- ✅ Network operations and latency
- ✅ Service discovery and health checks
- ✅ Outage resilience and recovery

---

## 🧪 Current Tests

### test_basic_connectivity.py
Basic connectivity tests for all infrastructure components.

**Tests:**
- Quick ping tests (MongoDB, K8s, SSH)
- Direct connection tests
- Service summary reports

---

### test_external_connectivity.py
External system connectivity and integration.

**Tests:**
- MongoDB connection via Kubernetes
- Kubernetes deployments and pods listing
- SSH network operations
- All services summary

---

### test_mongodb_outage_resilience.py
MongoDB outage handling and resilience tests.

**Tests:**
- MongoDB scale-down outage (returns 503)
- Network block outage (returns 503)
- Outage cleanup and restore
- Outage logging and metrics
- No impact on live streaming

**Related Jira:** PZ-13687, PZ-13767

---

### test_pz_integration.py
PZ system integration tests.

**Tests:**
- PZ repository availability
- Microservices listing
- Focus Server access through PZ
- Version information
- Import capability
- Integration summary

---

## 🚀 Running Tests

```bash
# All infrastructure tests
pytest tests/infrastructure/ -v

# Specific test file
pytest tests/infrastructure/test_basic_connectivity.py -v

# With markers
pytest -m infrastructure -v
pytest -m connectivity -v
pytest -m mongodb -v
pytest -m kubernetes -v
```

---

## 📊 Coverage

| Component | Status | Tests |
|-----------|--------|-------|
| **MongoDB** | ✅ Complete | Connectivity, outage resilience |
| **Kubernetes** | ✅ Complete | Access, pods, deployments |
| **SSH** | ✅ Complete | Connection, network ops |
| **PZ Integration** | ✅ Complete | Repository, microservices |
| **RabbitMQ** | ⚠️ Partial | Basic connectivity only |

---

## 🔧 Configuration

Infrastructure tests use settings from `config/environments.yaml`:

```yaml
mongodb:
  host: "10.10.100.108"
  port: 27017
  database: "prisma"

kubernetes:
  api_url: "https://10.10.100.102:6443"
  namespace: "panda"

ssh:
  host: "10.10.100.3"
  user: "root"
```

---

**Last Updated:** 2025-10-21  
**Maintained by:** QA Automation Team

