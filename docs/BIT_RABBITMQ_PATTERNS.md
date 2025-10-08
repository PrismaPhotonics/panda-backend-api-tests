# מה למדנו מה-microservice `bit`?

## 🎯 **Overview: מה זה BIT?**

**BIT = Built-In Tests** - microservice של PZ שמריץ בדיקות אוטומטיות על כל הרכיבים במערכת (analyzer, interrogator, focus_server, baby_analyzer, וכו').

### **איפה הקוד?**
```
external/pz/microservices/bit/
├── __main__.py                    # Entry point
├── bit_directory.py               # Test registry
├── bits/                          # Test implementations
├── invokers/
│   ├── bit_invoker.py            # Test executor
│   └── telegraf_post_invoker.py  # RabbitMQ producer (MAIN!)
├── bit_vertical_tree/             # Tests per component
│   ├── analyzer/
│   ├── interrogator/
│   └── common/
└── status/                        # Status tracking
```

---

## 📚 **4 דפוסי שימוש ב-RabbitMQ שמשתמשים ב-PZ**

### **1️⃣ RPC Server/Client Pattern**

**משמש ב:** `data_manager`, `data_collection_server`, `focus_server`

#### **Server Side (מקבל בקשות):**
```python
from pz_core_libs.msgbus import rpc

class DataManagerService(rpc.RpcServer):
    def __init__(self):
        rpc.RpcServer.__init__(self, 'DataManager')  # Queue name
    
    @rpc.method()  # Exposed RPC method
    def initiate_data_job(self, job_id: str, job_type: str, payload: Dict):
        """Handle data job requests."""
        # Process the request...
        return f'job started with id {job_id}'
    
    @rpc.method()
    def get_status_list(self):
        """Get list of job statuses."""
        return jobs_status
```

**קוד אמיתי:** `external/pz/microservices/data_manager/data_manager_service.py` (שורות 59-175)

---

#### **Client Side (שולח בקשות):**
```python
from pz_core_libs.msgbus import rpc

class DataManagerClient(rpc.RpcClient):
    def __init__(self, broker_uri: Optional[str] = None):
        super().__init__('DataManager', broker_uri=broker_uri)
    
    @rpc.interface  # Client interface - implementation auto-generated!
    def initiate_data_job(self, job_id: str, job_type: str, payload: Dict):
        pass  # Decorator generates the actual RPC call
    
    @rpc.interface
    def get_status_list(self):
        pass
```

**איך זה עובד:**
1. Client קורא ל-`initiate_data_job(...)` 
2. Decorator סידרת את הבקשה ושולח ל-RabbitMQ queue `DataManager`
3. Server מקבל, מפענח, ומריץ את ה-method המתאים
4. Server מחזיר תוצאה דרך RabbitMQ
5. Client מקבל את התוצאה ומחזיר אותה לקוד שקרא

**קוד אמיתי:** `external/pz/microservices/data_manager/data_manager_service.py` (שורות 148-174)

---

### **2️⃣ Producer Pattern (Fire-and-Forget)**

**משמש ב:** `bit` (שליחת תוצאות בדיקות)

```python
from pz_core_libs.msgbus.producer import Producer as RabbitProducer
from pz_core_libs.msgbus.message import InfluxLineMetricMessage

class TelegrafRabbitProducer:
    def __init__(self):
        self.producer = RabbitProducer()
    
    def publish(self, metrics):
        """Send metrics to RabbitMQ (no response expected)."""
        message = InfluxLineMetricMessage(metrics)
        return self.producer.publish(message)
```

**דוגמה לשימוש:**
```python
producer = TelegrafRabbitProducer.get_single_instance()

# Send test results
metric = Metric(measurement='bit-test')
metric.add_tag('component', 'focus_server')
metric.add_tag('test_name', 'config_validation')
metric.add_value('passed', 1)

producer.publish(metric)
```

**קוד אמיתי:** `external/pz/microservices/bit/invokers/telegraf_post_invoker.py` (שורות 37-52)

---

### **3️⃣ Command Pattern (Baby Analyzer)**

**משמש ב:** `baby_analyzer` (שליחת פקודות control)

**זה בדיוק מה שיצרנו ב-`BabyAnalyzerMQClient`!**

```python
from src.apis.baby_analyzer_mq_client import BabyAnalyzerMQClient
from src.models.baby_analyzer_models import ColorMap

# Connect
with BabyAnalyzerMQClient(host='10.10.10.101', port=5672) as client:
    # Send commands
    client.send_keepalive(source="test_script")
    client.send_roi_change(start=100, end=200)
    client.send_colormap_change(ColorMap.JET)
    client.send_caxis_adjust(min_value=-10.0, max_value=10.0)
```

**מאפיינים:**
- שליחה חד-כיוונית (לא מחכים לתשובה)
- Pydantic models לולידציה
- Context manager לניהול חיבור
- Multiple command types

---

### **4️⃣ Worker Pattern (Background Processing)**

**משמש ב:** `data_manager` workers

```python
import threading
import queue

class DataManagerWorker(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = True
        self.job_queue = queue.SimpleQueue()
        self.lock = threading.Lock()
    
    def run(self):
        """Main worker loop."""
        while True:
            job = self.job_queue.get()
            if job == '':  # Stop signal
                break
            
            with self.lock:
                # Process job safely
                process_job(job)
    
    def call_job(self, job_id, job_type, payload):
        """Add job to queue."""
        self.job_queue.put({
            'job_id': job_id,
            'job_type': job_type,
            'payload': payload
        })
```

**מאפיינים:**
- Background thread
- Thread-safe queue
- Lock למניעת race conditions
- Graceful shutdown

**קוד אמיתי:** `external/pz/microservices/data_manager/data_manager_service.py` (שורות 177-192)

---

## 🔍 **איך לחקור את bit בעצמך**

### **1. הבן את המבנה:**
```bash
# בדוק את entry point
external/pz/microservices/bit/__main__.py

# הבן איך tests מאורגנים
external/pz/microservices/bit/bit_directory.py

# ראה איך שולחים ל-RabbitMQ
external/pz/microservices/bit/invokers/telegraf_post_invoker.py
```

### **2. התמקד ב-RabbitMQ Integration:**
```bash
# RPC pattern
external/pz/microservices/data_manager/data_manager_service.py
external/pz/microservices/data_collection_server/data_collection_service.py

# Producer pattern  
external/pz/microservices/bit/invokers/telegraf_post_invoker.py
```

### **3. הבן את ה-Tests:**
```bash
# Services tests (כמו שלנו!)
external/pz/microservices/bit/bit_vertical_tree/analyzer/services.py
external/pz/microservices/bit/bit_vertical_tree/interrogator/services.py
```

---

## 🚀 **איך להשתמש בזה בבדיקות שלנו?**

### **Scenario 1: REST API Testing**
```python
from src.apis.focus_server_api import FocusServerAPI

# כבר יצרנו!
api = FocusServerAPI(base_url="http://10.10.10.101:8500")
response = api.config_task(task_id="test_001", config={...})
```

### **Scenario 2: RabbitMQ Commands (Baby Analyzer)**
```python
from src.apis.baby_analyzer_mq_client import BabyAnalyzerMQClient

# כבר יצרנו!
with BabyAnalyzerMQClient(host='...', port=5672) as mq:
    mq.send_roi_change(start=100, end=200)
```

### **Scenario 3: Integration Testing (REST + RabbitMQ)**
```python
# Test flow:
# 1. Configure via REST API
response = api.config_task(task_id="test_001", config={...})

# 2. Send commands via RabbitMQ
mq.send_roi_change(start=50, end=150)

# 3. Verify results via REST API
waterfall = api.get_waterfall(task_id="test_001", row_count=100)
assert waterfall['data']  # Verify ROI was applied
```

---

## 📊 **Comparison: bit vs. Our Framework**

| Feature | bit Microservice | Our Framework |
|---------|-----------------|---------------|
| **Purpose** | System health checks | API/Integration testing |
| **RabbitMQ Usage** | Metrics publishing | Commands + RPC |
| **Test Types** | Built-in hardware/software tests | API flows + E2E scenarios |
| **Patterns Used** | Producer (metrics) | Producer (commands) + REST |
| **Integration** | Telegraf → InfluxDB → Grafana | pytest → HTML reports |
| **Scope** | All PZ components | Focus Server + Baby Analyzer |

---

## 🛠️ **Tools & Scripts**

### **1. RabbitMQ Helper Script**
```bash
# Test connection
py scripts/rabbitmq_helper.py --test-connection --env=staging

# Send test commands
py scripts/rabbitmq_helper.py --send-commands --env=staging

# Inspect queues
py scripts/rabbitmq_helper.py --inspect-queues --env=staging

# Run all
py scripts/rabbitmq_helper.py --all --env=staging
```

### **2. PZ RPC Integration Example**
```bash
# See RPC pattern demo
py scripts/pz_rpc_integration_example.py --demo=rpc

# See Producer pattern demo
py scripts/pz_rpc_integration_example.py --demo=producer

# See Baby Analyzer commands (needs RabbitMQ)
py scripts/pz_rpc_integration_example.py --demo=baby_analyzer --env=staging

# Run all demos
py scripts/pz_rpc_integration_example.py --demo=all
```

---

## 🎓 **Key Takeaways**

### **✅ מה למדנו:**
1. **RPC over RabbitMQ** - Request/Response pattern עם decorators
2. **Producer Pattern** - Fire-and-forget messages
3. **Command Pattern** - Control commands עם Pydantic validation
4. **Worker Pattern** - Background processing עם threading

### **✅ איך זה עוזר לנו:**
1. הבנו איך PZ microservices מתקשרים ביניהם
2. יצרנו Baby Analyzer MQ Client בהתאם לדפוסים הנכונים
3. יש לנו scripts לבדיקת חיבור ל-RabbitMQ
4. יש לנו דוגמאות קוד אמיתיות מהפרויקט

### **✅ Next Steps:**
1. **הרץ bit בפועל** כדי לראות איך הוא שולח metrics
2. **צפה ב-RabbitMQ Management UI** (http://10.10.10.101:15672) כדי לראות queues
3. **התממשק עם data_manager RPC** אם צריך data jobs
4. **הרחב את BabyAnalyzerMQClient** אם צריך פקודות נוספות

---

## 📖 **Reference: Key Files to Study**

### **Must Read:**
```
1. bit/__main__.py                              # Entry point & orchestration
2. bit/invokers/telegraf_post_invoker.py        # RabbitMQ producer pattern
3. data_manager/data_manager_service.py         # RPC server/client pattern
4. data_collection_server/data_collection_service.py  # Another RPC example
```

### **Advanced:**
```
5. bit/bit_directory.py                         # Test registry pattern
6. bit/invokers/bit_invoker.py                  # Invoker pattern
7. bit/bit_vertical_tree/analyzer/services.py   # Actual tests
```

---

## 🔗 **Useful Commands**

### **Inspect RabbitMQ (SSH to server):**
```bash
# SSH to RabbitMQ server
ssh prisma@10.10.10.150  # password: PASSW0RD

# Check RabbitMQ status
sudo rabbitmqctl status

# List queues
sudo rabbitmqctl list_queues

# List connections
sudo rabbitmqctl list_connections

# List exchanges
sudo rabbitmqctl list_exchanges
```

### **Port Forward (if needed):**
```bash
# Forward RabbitMQ ports
kubectl -n default port-forward svc/rabbitmq-service 5672:5672 15672:15672

# Or via SSH tunnel
ssh -L 5672:localhost:5672 -L 15672:localhost:15672 prisma@10.10.10.150
```

---

## 🎯 **Summary**

**אוהד התכוון:**
> "תסתכל על bit כדי לראות איך משתמשים ב-RabbitMQ נכון בפרויקט PZ"

**מה גילינו:**
1. ✅ RPC Server/Client pattern ל-Request/Response
2. ✅ Producer pattern ל-metrics/commands
3. ✅ Command pattern ל-control commands
4. ✅ Worker pattern ל-background jobs

**מה יצרנו:**
1. ✅ `BabyAnalyzerMQClient` - Command pattern implementation
2. ✅ `rabbitmq_helper.py` - Testing & debugging tool
3. ✅ `pz_rpc_integration_example.py` - Pattern demonstrations
4. ✅ Integration tests עם RabbitMQ support

---

**נכתב על ידי:** QA Automation Architect  
**תאריך:** 08/10/2025  
**מבוסס על:** `external/pz/microservices/bit/` + data_manager + data_collection_server

