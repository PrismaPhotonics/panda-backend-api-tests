# 🔧 Server Configuration Updates for New Environment

**Date:** October 19, 2025  
**File:** `default_config.py` (Server-side configuration)

---

## 🎯 Changes Needed

### 1. RabbitMQ Broker Configuration

**Current (Wrong):**
```python
class Broker:
    broker_server = 'data-rabbitmq.prismaphotonics.net'
    broker_port = 5671
    broker_protocol = 'amqps'
```

**Should be (New Production):**
```python
class Broker:
    # Internal K8s service name
    broker_server = 'rabbitmq-panda.panda'
    # OR full service name:
    # broker_server = 'rabbitmq-panda-0.rabbitmq-panda-headless.panda.svc.cluster.local'
    
    broker_port = 5672  # Changed from 5671
    broker_protocol = 'amqp'  # Changed from 'amqps' (or keep 'amqps' with port 5671)
```

---

### 2. Focus View URL

**Current (Wrong):**
```python
class Focus:
    focus_view_url = 'http://10.10.100.113'
```

**Should be (New Production):**
```python
class Focus:
    focus_view_url = 'http://10.10.10.100'
    # OR with HTTPS:
    # focus_view_url = 'https://10.10.10.100'
```

---

### 3. MongoDB Configuration

**Current (Correct ✅):**
```python
class Mongo:
    host_name = 'mongodb'  # K8s service name - correct!
    mongo_port = 27017
    mongo_hardcoded_user = 'prisma'
    mongo_hardcoded_password = 'prisma'
    
    url = f"mongodb://prisma:prisma@mongodb:27017/"
```

**This is CORRECT for internal K8s communication!**

---

## 📊 Complete Configuration for New Environment

### For Pods Running Inside Kubernetes:

```python
class Broker:
    broker_server = 'rabbitmq-panda.panda'
    broker_port = 5672
    broker_protocol = 'amqp'
    exchange_name = 'prisma'
    heartbeat = 600
    blocked_connection_timeout = 300
    username = 'prisma'
    password = 'prismapanda'
    prefetch_count = 35
    reconnect_attempts = 60
    reconnect_timeout = 1
    tls = False  # Changed from True since using internal service
  
    class ManagementAPI:
        mgmt_port = 15672  # Management UI port

class Mongo:
    schema = 'mongodb'
    host_name = 'mongodb'  # K8s service name
    mongo_port = 27017
    db_name = 'Alerts'
    run_collection = 'Runs'
    algorun_collection = 'Algoruns'
    monitoring_metrics_db_name = 'MonitoringMetrics'
    rec_mapper_db_name = 'prisma'
    authentication_db_name_for_mongo = 'prisma'
    mongo_hardcoded_user = 'prisma'
    mongo_hardcoded_password = 'prisma'
  
    url = f"{schema}://{mongo_hardcoded_user}:{mongo_hardcoded_password}@{host_name}:{mongo_port}/"

class Focus:
    mongo_mapper_url = 'mongodb://prisma:prisma@mongodb'
    storage_mount_path = '/prisma/root/recordings/segy'
    k8s_mode = True
    focus_view_url = 'http://10.10.10.100'  # Updated!
    focus_job_template_location = f"{os.path.join(os.getenv('PRISMA_CONFIG'), 'panda', 'templates', 'job-template.yml')}"
    focus_temporary_job_storage = '/home/prisma'
    focus_fiber_recording_sw_version = "10.7"
    focus_expected_dx = 4.539421081542969
    focus_expected_prr = 2000
    focus_expected_amount_of_channels = 2337
    focus_expected_fiber_start_meters = 0
    focus_expected_fiber_length_meters = 11000
    focus_expected_fiber_description = "Kuler"
    focus_debug_mode = False
    focus_amount_of_gpu_slices = 200
    focus_research_grpc_job_starting_port = 12300
```

---

## 🔍 How to Update This File

### If running in Kubernetes:

1. **Find the pod:**
   ```bash
   kubectl get pods -n panda
   ```

2. **Edit the config:**
   ```bash
   kubectl exec -it <pod-name> -n panda -- /bin/bash
   vi /path/to/default_config.py
   ```

3. **Or update ConfigMap (if used):**
   ```bash
   kubectl edit configmap <config-name> -n panda
   ```

4. **Restart pods:**
   ```bash
   kubectl rollout restart deployment <deployment-name> -n panda
   ```

---

## 🆚 Client vs Server Configuration

| What | File | Location | Updated? |
|------|------|----------|----------|
| **Client (PandaApp)** | `usersettings.json` | `C:\Panda\` | ✅ YES |
| **Server (Focus Server)** | `default_config.py` | Inside Pods | ⚠️ Needs check |

---

## 🎯 Summary

**Changes needed in `default_config.py`:**

1. ✅ **MongoDB:** Already correct (`mongodb`)
2. ⚠️ **RabbitMQ:** Update to `rabbitmq-panda.panda:5672`
3. ❌ **Focus View URL:** Update to `http://10.10.10.100`

**Where to update:**
- Inside Kubernetes pods in namespace `panda`
- May require pod restart after changes

---

**Last Updated:** October 19, 2025  
**Environment:** New Production (10.10.100.x)

