# RabbitMQ Quick Reference - Focus Server Automation

## 🎯 **TL;DR**

אוהד אמר: "תסתכל על bit" → **bit = Built-In Tests microservice** שמשתמש ב-RabbitMQ לשלוח תוצאות בדיקות.

**4 דפוסים עיקריים:**
1. **RPC** (data_manager) - Request/Response
2. **Producer** (bit) - Fire-and-forget metrics
3. **Command** (baby_analyzer) - Control commands
4. **Worker** (data_manager) - Background processing

---

## 📂 **Where to Look**

```
external/pz/microservices/
├── bit/                           ← Main: Built-In Tests
│   ├── __main__.py               ← Entry point
│   └── invokers/
│       └── telegraf_post_invoker.py  ← RabbitMQ Producer pattern
├── data_manager/                  ← RPC Server/Client pattern
│   └── data_manager_service.py
└── data_collection_server/        ← Another RPC example
    └── data_collection_service.py
```

---

## 🚀 **Quick Commands**

### **Test RabbitMQ Connection:**
```bash
py scripts/rabbitmq_helper.py --test-connection --env=staging
```

### **Send Test Commands:**
```bash
py scripts/rabbitmq_helper.py --send-commands --env=staging
```

### **Inspect Queues:**
```bash
py scripts/rabbitmq_helper.py --inspect-queues --env=staging
```

### **Run Pattern Demos:**
```bash
py scripts/pz_rpc_integration_example.py --demo=all
```

### **Run Integration Tests (with RabbitMQ):**
```bash
py -m pytest tests/integration/api/ -v -m rabbitmq
```

---

## 💡 **Code Examples**

### **1. Baby Analyzer Commands (Already Implemented!)**
```python
from src.apis.baby_analyzer_mq_client import BabyAnalyzerMQClient
from src.models.baby_analyzer_models import ColorMap

with BabyAnalyzerMQClient(host='10.10.10.101', port=5672) as mq:
    mq.send_keepalive(source="test")
    mq.send_roi_change(start=100, end=200)
    mq.send_colormap_change(ColorMap.JET)
```

### **2. RPC Pattern (from data_manager)**
```python
from pz_core_libs.msgbus import rpc

# Server
class MyService(rpc.RpcServer):
    @rpc.method()
    def my_method(self, param):
        return result

# Client
class MyClient(rpc.RpcClient):
    @rpc.interface
    def my_method(self, param):
        pass  # Auto-implemented!
```

### **3. Producer Pattern (from bit)**
```python
from pz_core_libs.msgbus.producer import Producer

producer = Producer()
message = InfluxLineMetricMessage(metrics)
producer.publish(message)
```

---

## 🔧 **SSH to RabbitMQ Server**

```bash
# Connect
ssh prisma@10.10.10.150  # password: PASSW0RD

# Check status
sudo rabbitmqctl status
sudo rabbitmqctl list_queues
sudo rabbitmqctl list_connections
```

---

## 🌐 **Management UI**

```
http://10.10.10.101:15672
Username: guest (or from config)
Password: guest (or from config)
```

---

## 📖 **Full Documentation**

See: [`docs/BIT_RABBITMQ_PATTERNS.md`](./BIT_RABBITMQ_PATTERNS.md)

---

## ✅ **What We Created**

| File | Purpose |
|------|---------|
| `src/apis/baby_analyzer_mq_client.py` | RabbitMQ client for Baby Analyzer |
| `src/models/baby_analyzer_models.py` | Pydantic models for commands |
| `scripts/rabbitmq_helper.py` | Testing & debugging tool |
| `scripts/pz_rpc_integration_example.py` | Pattern demonstrations |
| `tests/integration/api/test_dynamic_roi_adjustment.py` | ROI tests with RabbitMQ |
| `tests/integration/api/test_spectrogram_pipeline.py` | Colormap/caxis tests |

---

**Updated:** 08/10/2025

