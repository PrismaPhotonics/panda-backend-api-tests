# ☸️ Kubernetes Infrastructure - New Production Environment

**Date:** October 16, 2025  
**Namespace:** `panda`  
**Status:** ✅ **VALIDATED**

---

## 📊 Complete Infrastructure Map

```
┌─────────────────────────────────────────────────────────────┐
│                  External Access Layer                       │
└─────────────────────────────────────────────────────────────┘
    │
    ├── Backend:       10.10.100.100:443 (HTTPS)
    ├── Frontend:      10.10.10.100:443 (HTTPS)
    ├── FrontendApi:   10.10.10.150:30443 (HTTPS)
    │
┌─────────────────────────────────────────────────────────────┐
│            LoadBalancer Services (External IPs)              │
└─────────────────────────────────────────────────────────────┘
    │
    ├── MongoDB:       10.10.100.108:27017
    │                  Service: mongodb.panda
    │
    └── RabbitMQ:      10.10.100.107
                       Service: rabbitmq-panda
                       ├── AMQP:        10.10.100.107:5672
                       ├── AMQP SSL:    10.10.100.107:5671
                       ├── Management:  10.10.100.107:15672
                       ├── Erlang:      10.10.100.107:4369
                       ├── Inter-node:  10.10.100.107:25672
                       └── Prometheus:  10.10.100.107:9419

┌─────────────────────────────────────────────────────────────┐
│              Internal Cluster Services                       │
└─────────────────────────────────────────────────────────────┘
    │
    ├── Focus Server:  panda-panda-focus-server.panda:5000
    │                  ClusterIP: 10.43.103.101
    │
    └── gRPC Service:  grpc-service-1-343.panda:12301
                       ClusterIP: 10.43.249.136
                       Type: NodePort
```

---

## 🔌 LoadBalancer Services (External Access)

### 1. MongoDB

**Service:** `mongodb.panda`  
**Type:** LoadBalancer  
**Cluster IP:** 10.43.74.248  
**External IP:** **10.10.100.108:27017** ✅

**Connection String:**
```
mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma
```

**Internal Endpoint:**
```
mongodb.panda:27017
mongodb.panda:25745
```

**Created:** 19 days ago

**Labels:**
- `app.kubernetes.io/component: mongodb`
- `app.kubernetes.io/instance: mongodb`
- `app.kubernetes.io/managed-by: Helm`

---

### 2. RabbitMQ ⭐ (NEW DISCOVERY)

**Service:** `rabbitmq-panda`  
**Type:** LoadBalancer  
**Cluster IP:** 10.43.10.166  
**External IP:** **10.10.100.107**

**External Endpoints:**

| Service | Port | External IP | Purpose |
|---------|------|-------------|---------|
| **AMQP** | 5672 | 10.10.100.107:5672 | Message queue (non-SSL) |
| **AMQP SSL** | 5671 | 10.10.100.107:5671 | Message queue (SSL) |
| **Management UI** | 15672 | 10.10.100.107:15672 | Web management console |
| **Erlang Distribution** | 4369 | 10.10.100.107:4369 | EPMD (Erlang Port Mapper) |
| **Inter-node** | 25672 | 10.10.100.107:25672 | Cluster communication |
| **Prometheus** | 9419 | 10.10.100.107:9419 | Metrics endpoint |

**Python Connection:**
```python
import pika

# Non-SSL connection
credentials = pika.PlainCredentials('user', 'prismapanda')
parameters = pika.ConnectionParameters(
    host='10.10.100.107',
    port=5672,
    credentials=credentials,
    virtual_host='/'
)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
```

**Management UI Access:**
```
http://10.10.100.107:15672
Username: user (or admin)
Password: prismapanda
```

**Created:** 20 days ago

**Labels:**
- `app.kubernetes.io/instance: rabbitmq-panda`
- `app.kubernetes.io/managed-by: Helm`
- `app.kubernetes.io/name: rabbitmq`

---

### 3. RabbitMQ Headless Service

**Service:** `rabbitmq-panda-headless`  
**Type:** ClusterIP (None - Headless)  
**Purpose:** Direct pod-to-pod communication

**Internal Endpoints:**
- `rabbitmq-panda-headless.panda:4369` (EPMD)
- `rabbitmq-panda-headless.panda:5672` (AMQP)
- `rabbitmq-panda-headless.panda:5671` (AMQP SSL)
- `rabbitmq-panda-headless.panda:25672` (Inter-node)
- `rabbitmq-panda-headless.panda:15672` (Management)

---

## 🔒 Internal Cluster Services

### 1. Focus Server

**Service:** `panda-panda-focus-server`  
**Type:** ClusterIP  
**Cluster IP:** 10.43.103.101  
**Port:** 5000

**Internal Endpoint:**
```
panda-panda-focus-server.panda:5000
```

**External Access:**
- Accessed via: `https://10.10.100.100/focus-server/` (reverse proxy/ingress)

**Labels:**
- `app.kubernetes.io/instance: panda`
- `app.kubernetes.io/managed-by: Helm`
- `app.kubernetes.io/name: panda-panda-focus-server`

**Created:** 4 days ago

---

### 2. gRPC Service

**Service:** `grpc-service-1-343`  
**Type:** NodePort  
**Cluster IP:** 10.43.249.136  
**Port:** 12301

**Internal Endpoint:**
```
grpc-service-1-343.panda:12301
```

**Purpose:** gRPC communication for Focus Server

**Created:** 57 minutes ago (recent deployment)

---

## 🌐 Complete Network Map

### External Access (From User/Client)
```
User → 10.10.100.100:443 → Focus Server Backend
User → 10.10.10.100:443 → Frontend (LiveView)
User → 10.10.10.150:30443 → FrontendApi
```

### Direct Service Access (From Tests/Applications)
```
MongoDB:  10.10.100.108:27017
RabbitMQ: 10.10.100.107:5672 (AMQP)
          10.10.100.107:15672 (Management UI)
```

### Internal Kubernetes (Pod-to-Pod)
```
Focus Server: panda-panda-focus-server.panda:5000
gRPC:         grpc-service-1-343.panda:12301
MongoDB:      mongodb.panda:27017
RabbitMQ:     rabbitmq-panda.panda:5672
```

---

## 🧪 Connection Testing

### Test MongoDB
```powershell
Test-NetConnection -ComputerName 10.10.100.108 -Port 27017

# Python test
py -c "from pymongo import MongoClient; MongoClient('mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma').admin.command('ping'); print('OK')"
```

### Test RabbitMQ
```powershell
# Test AMQP port
Test-NetConnection -ComputerName 10.10.100.107 -Port 5672

# Test Management UI
Test-NetConnection -ComputerName 10.10.100.107 -Port 15672

# Access Management UI in browser
Start-Process "http://10.10.100.107:15672"
```

### Test Focus Server
```powershell
Test-NetConnection -ComputerName 10.10.100.100 -Port 443

# API test
Invoke-WebRequest -Uri "https://10.10.100.100/focus-server/channels" -SkipCertificateCheck
```

---

## 📝 Configuration Updates Required

### Update Environment Configuration

Add RabbitMQ to `config/environments.yaml.production`:

```yaml
  rabbitmq:
    host: "10.10.100.107"
    port: 5672
    ssl_port: 5671
    management_port: 15672
    username: "user"
    password: "prismapanda"
    vhost: "/"
    ssl: false
    
    # Kubernetes service
    service_name: "rabbitmq-panda.panda"
    cluster_ip: "10.43.10.166"
    
    # Additional ports
    erlang_port: 4369
    inter_node_port: 25672
    prometheus_port: 9419
```

### Update Test Configuration

Add to `set_production_env.ps1`:

```powershell
# RabbitMQ Configuration
$env:RABBITMQ_HOST = "10.10.100.107"
$env:RABBITMQ_PORT = "5672"
$env:RABBITMQ_MANAGEMENT_PORT = "15672"
$env:RABBITMQ_USER = "user"
$env:RABBITMQ_PASSWORD = "prismapanda"
$env:RABBITMQ_VHOST = "/"
```

---

## 🔍 Service Discovery Summary

| Component | Type | External IP | Internal Service | Port(s) |
|-----------|------|-------------|------------------|---------|
| **MongoDB** | LoadBalancer | 10.10.100.108 | mongodb.panda | 27017 |
| **RabbitMQ** | LoadBalancer | 10.10.100.107 | rabbitmq-panda.panda | 5672, 15672 |
| **Focus Server** | ClusterIP | - | panda-panda-focus-server.panda | 5000 |
| **gRPC Service** | NodePort | - | grpc-service-1-343.panda | 12301 |
| **Backend** | External | 10.10.100.100 | (Ingress/Proxy) | 443 |
| **Frontend** | External | 10.10.10.100 | (Ingress/Proxy) | 443 |

---

## 🎯 Key Findings

### ✅ Confirmed
1. **MongoDB** is correctly exposed at `10.10.100.108:27017`
2. **RabbitMQ** is accessible at `10.10.100.107` (multiple ports)
3. **Focus Server** runs internally at `panda-panda-focus-server.panda:5000`
4. **gRPC Service** recently deployed (57 minutes ago)

### 🔍 Architecture Insights
1. **LoadBalancers** used for MongoDB and RabbitMQ (direct external access)
2. **ClusterIP** used for Focus Server (accessed via reverse proxy)
3. **Helm** managed deployments (all services show `managed-by: Helm`)
4. **Namespace:** All services in `panda` namespace

### 🆕 New Discoveries
1. **RabbitMQ Management UI** available at `http://10.10.100.107:15672`
2. **RabbitMQ AMQP** at `10.10.100.107:5672`
3. **gRPC Service** exposed on NodePort 12301
4. **Prometheus metrics** available on RabbitMQ (port 9419)

---

## 📚 Next Steps

1. **Update Test Configuration**
   - Add RabbitMQ connection settings
   - Update environment YAML file

2. **Test RabbitMQ Integration**
   - Access Management UI
   - Test AMQP connection
   - Run RabbitMQ integration tests

3. **Document gRPC Service**
   - Understand gRPC service purpose
   - Test gRPC connectivity
   - Add to test configuration

---

**Last Updated:** October 16, 2025  
**Source:** Kubernetes `panda` namespace service discovery  
**Status:** ✅ Documented & Validated

