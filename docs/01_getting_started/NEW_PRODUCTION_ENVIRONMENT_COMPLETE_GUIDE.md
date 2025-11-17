# 🚀 New Production Environment - Configuration & Access Guide
**Environment:** `new_production`  
**Namespace:** `panda`  
**Last Updated:** October 22, 2025

---

## 📡 **Backend & Frontend Services**

### Focus Server (Backend)
- **Base URL:** `https://10.10.100.100/focus-server/`
- **Swagger API:** `https://10.10.100.100/api/swagger/#/`
- **Protocol:** HTTPS (self-signed certificate - use `verify_ssl: false`)

### Frontend (LiveView)
- **URL:** `https://10.10.10.100/liveView`
- **With Site ID:** `https://10.10.10.100/liveView?siteId=prisma-210-1000`
- **Site ID:** `prisma-210-1000`

---

## 🗄️ **MongoDB Database**

### External Access (LoadBalancer)
- **Host:** `10.10.100.108`
- **Port:** `27017`
- **Connection String:** `mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma`

### Credentials
- **Username:** `prisma`
- **Password:** `prisma`
- **Auth Source:** `prisma`
- **Database:** `prisma`

### Internal K8s Access
- **Service Name:** `mongodb.panda`
- **Internal Endpoint:** `mongodb.panda:27017`
- **ClusterIP:** `10.43.74.248`
- **Service Type:** LoadBalancer

---

## 🐰 **RabbitMQ Message Queue**

### External Access (LoadBalancer)
- **Host:** `10.10.100.107`
- **AMQP Port:** `5672`
- **AMQP SSL Port:** `5671`
- **Management UI:** `http://10.10.100.107:15672`
- **Prometheus Metrics:** `http://10.10.100.107:9419`
- **Erlang Port Mapper:** `4369`
- **Inter-node Communication:** `25672`

### Credentials
- **Username:** `prisma`
- **Password:** `prismapanda`
- **VHost:** `/`
- **Exchange:** `prisma`

### Internal K8s Access
- **Service Name:** `rabbitmq-panda.panda`
- **Internal Endpoint:** `rabbitmq-panda.panda:5672`
- **ClusterIP:** `10.43.10.166`
- **Service Type:** LoadBalancer

---

## ☸️ **Kubernetes Cluster**

### Cluster Access
- **API Server:** `https://10.10.100.102:6443`
- **Dashboard:** `https://10.10.100.102/`
- **Namespace:** `panda`
- **Context:** `panda-cluster`
- **Kubeconfig:** `~/.kube/config-panda`

### Services in `panda` Namespace

#### Focus Server
- **Service Name:** `panda-panda-focus-server`
- **Type:** ClusterIP
- **ClusterIP:** `10.43.103.101`
- **Internal Endpoint:** `panda-panda-focus-server.panda:5000`
- **Pod Selector:** `app.kubernetes.io/name=panda-panda-focus-server`

#### MongoDB
- **Service Name:** `mongodb`
- **Type:** LoadBalancer
- **ClusterIP:** `10.43.74.248`
- **Internal Endpoint:** `mongodb.panda:27017`
- **External IP:** `10.10.100.108:27017`

#### RabbitMQ
- **Service Name:** `rabbitmq-panda`
- **Type:** LoadBalancer
- **ClusterIP:** `10.43.10.166`
- **Internal Endpoint:** `rabbitmq-panda.panda:5672`
- **External IP:** `10.10.100.107`

#### gRPC Services
- **Service Name:** `grpc-service-*` (dynamic)
- **Type:** NodePort
- **Port Range:** Starts from `12301` and increments per service
- **Example:** `grpc-service-1-343.panda:12301`
- **Note:** Port number is dynamic and varies per service instance

---

## 🔐 **SSH & K9s Access**

### Connect to K9s (3-Step Process)

**Step 1: SSH to Jump Host**
```bash
ssh root@10.10.100.3
```
- **Host:** `10.10.100.3` (panda2worker - Proxmox worker node)
- **Username:** `root`
- **Password:** Contact team lead
- **Port:** `22`

**Step 2: SSH to Worker Node**
```bash
ssh prisma@10.10.100.113
```
- **Host:** `10.10.100.113` (K8s worker node with kubectl/k9s)
- **Username:** `prisma`
- **Password:** Contact team lead
- **Port:** `22`

**Step 3: Launch K9s**
```bash
k9s
```
- **Default Namespace:** `panda`
- **Tools Available:** `kubectl`, `k9s`

### Quick K9s Commands
- `:pods` - View pods
- `:svc` - View services
- `:logs` - View pod logs
- `:deployments` - View deployments
- `Ctrl+C` - Exit

---

## 🧪 **Testing & Automation**

### Pytest Configuration
- **Default Environment:** `new_production`
- **Config File:** `config/environments.yaml`
- **Conftest:** `tests/conftest.py`

### Run Tests
```bash
# Run all tests on new_production
pytest --env=new_production

# Run specific test suite
pytest -m "integration and api" tests/integration/api/

# Run with coverage
pytest --cov=src --cov-report=html --env=new_production
```

### Environment Variables (Optional)
```bash
export MONGODB_URI="mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma"
export FOCUS_BASE_URL="https://10.10.100.100"
export FOCUS_API_PREFIX="/focus-server"
export RABBITMQ_HOST="10.10.100.107"
export RABBITMQ_PORT="5672"
```

---

## 🔧 **Network Validation**

### Test Connectivity (PowerShell)
```powershell
# Backend
Test-NetConnection -ComputerName 10.10.100.100 -Port 443

# Frontend
Test-NetConnection -ComputerName 10.10.10.100 -Port 443

# MongoDB
Test-NetConnection -ComputerName 10.10.100.108 -Port 27017

# RabbitMQ AMQP
Test-NetConnection -ComputerName 10.10.100.107 -Port 5672

# RabbitMQ Management UI
Test-NetConnection -ComputerName 10.10.100.107 -Port 15672

# Kubernetes API
Test-NetConnection -ComputerName 10.10.100.102 -Port 6443
```

### Test Connectivity (Linux/Mac)
```bash
# Backend
curl -k https://10.10.100.100/focus-server/

# MongoDB
nc -zv 10.10.100.108 27017

# RabbitMQ
nc -zv 10.10.100.107 5672
```

---

## ⚠️ **Important Notes**

### SSL Certificates
- **All HTTPS endpoints use self-signed certificates**
- **For automation/testing:** Set `verify_ssl: false` or `--insecure`
- **For browsers:** Accept certificate warnings

### Credentials Security
- **Do NOT commit passwords to Git**
- **Use environment variables or secure vaults**
- **Rotate passwords regularly**

### Production Environment
- **Read-only access recommended for testing**
- **No destructive operations** (scale down, delete pods, etc.)
- **Load testing disabled by default**
- **Outage tests disabled**

---

## 📞 **Support & Troubleshooting**

### Common Issues

**1. SSL Certificate Errors**
- Solution: Use `verify_ssl: false` in automation or `-k` flag in curl

**2. MongoDB Connection Timeout**
- Check: `Test-NetConnection -ComputerName 10.10.100.108 -Port 27017`
- Verify: Credentials are correct (`prisma:prisma`)

**3. RabbitMQ Connection Refused**
- Check: Service is running in K8s (`k9s` → `:pods` → verify `rabbitmq-panda`)
- Verify: Port `5672` is accessible

**4. K9s Access Issues**
- Verify: SSH connection to both jump host and worker node
- Check: User has proper permissions on worker node

### Get Help
- **Team Lead:** Benny Koren
- **DevOps:** Contact for infrastructure issues
- **Documentation:** `C:\Projects\focus_server_automation\documentation\`

---

## 📚 **Additional Resources**

- **API Documentation:** https://10.10.100.100/api/swagger/#/
- **Automation Project:** `C:\Projects\focus_server_automation\`
- **Test Documentation:** 75 tests documented in `COMPLETE_XRAY_TEST_DOCUMENTATION_PART*.md`
- **Jira Xray:** Tests ready for import
- **GitHub Repository:** https://github.com/PrismaPhotonics/panda-backend-api-tests.git

---

**Status:** ✅ **Environment Verified & Operational**  
**All services accessible and tested**


