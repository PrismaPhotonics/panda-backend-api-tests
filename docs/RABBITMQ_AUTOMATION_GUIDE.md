# RabbitMQ Automation Guide

## 🎯 **Overview**

מדריך מלא לאוטומציה של חיבור RabbitMQ בבדיקות, כולל:
- ✅ Auto-discovery של RabbitMQ services ב-Kubernetes
- ✅ Auto-extraction של credentials מ-K8s secrets
- ✅ Auto port-forward עם cleanup אוטומטי
- ✅ Context managers ל-lifecycle management
- ✅ Pytest fixtures מוכנים לשימוש

---

## 📚 **מה יצרנו?**

### **1️⃣ RabbitMQConnectionManager**

Class מלא שמנהל את כל lifecycle של החיבור:

```python
from src.infrastructure.rabbitmq_manager import RabbitMQConnectionManager

# Auto-setup with cleanup
with RabbitMQConnectionManager(k8s_host='10.10.10.150') as conn_info:
    # conn_info = {host, port, username, password, ...}
    # Use for testing
    pass
# Automatic cleanup!
```

**Features:**
- 🔍 **Auto-discovery**: מוצא RabbitMQ services ב-K8s
- 🔑 **Auto-credentials**: מחלץ מ-secrets
- 🚀 **Auto port-forward**: מגדיר kubectl port-forward
- 🧹 **Auto-cleanup**: מנקה הכל בסיום

---

### **2️⃣ Helper Context Manager**

Context manager פשוט לשימוש מהיר:

```python
from src.infrastructure.rabbitmq_manager import rabbitmq_connection

with rabbitmq_connection(service='rabbitmq-panda') as conn:
    # conn מכיל את כל פרטי החיבור
    client = BabyAnalyzerMQClient(**conn)
    client.send_keepalive()
```

---

### **3️⃣ Pytest Fixtures**

Fixtures מוכנים לשימוש בבדיקות:

```python
# tests/conftest.py
@pytest.fixture(scope="session")
def auto_rabbitmq_connection(config_manager):
    """Auto-setup RabbitMQ with discovery and port-forward."""
    from src.infrastructure.rabbitmq_manager import RabbitMQConnectionManager
    
    k8s_host = config_manager.get("kubernetes.cluster_host", "10.10.10.150")
    
    with RabbitMQConnectionManager(k8s_host=k8s_host) as conn_info:
        yield conn_info


def test_rabbitmq_commands(auto_rabbitmq_connection):
    """Test using auto-managed RabbitMQ connection."""
    client = BabyAnalyzerMQClient(**auto_rabbitmq_connection)
    client.send_keepalive()
```

---

## 🚀 **שימוש מהיר**

### **תרחיש 1: Manual Setup**

```python
from src.infrastructure.rabbitmq_manager import RabbitMQConnectionManager

manager = RabbitMQConnectionManager(
    k8s_host="10.10.10.150",
    preferred_service="rabbitmq-panda",
    namespace="default"
)

try:
    conn_info = manager.setup()
    print(f"Connected: {conn_info}")
    
    # Use connection...
    
finally:
    manager.cleanup()
```

---

### **תרחיש 2: Context Manager**

```python
from src.infrastructure.rabbitmq_manager import rabbitmq_connection

with rabbitmq_connection() as conn:
    from src.apis.baby_analyzer_mq_client import BabyAnalyzerMQClient
    
    client = BabyAnalyzerMQClient(
        host=conn['host'],
        port=conn['port'],
        username=conn['username'],
        password=conn['password']
    )
    
    client.send_roi_change(start=100, end=200)
```

---

### **תרחיש 3: Pytest Tests**

```python
import pytest
from src.apis.baby_analyzer_mq_client import BabyAnalyzerMQClient
from src.models.baby_analyzer_models import ColorMap


@pytest.mark.rabbitmq
def test_send_commands(auto_rabbitmq_connection):
    """Test sending commands with auto-managed connection."""
    
    client = BabyAnalyzerMQClient(**auto_rabbitmq_connection)
    
    # Test commands
    client.send_keepalive(source="automated_test")
    client.send_colormap_change(ColorMap.JET)
    client.send_roi_change(start=50, end=150)
    
    # Assertions...
    assert True  # Commands sent successfully
```

---

## 🔧 **איך זה עובד?**

### **Workflow מלא:**

```
1. Discovery
   ↓
   RabbitMQConnectionManager מחפש services:
   - kubectl get svc -n default
   - מזהה: rabbitmq-panda, rabbitmq-prisma
   
2. Credentials
   ↓
   מחלץ מ-K8s secrets:
   - kubectl get secret rabbitmq-panda -o jsonpath=...
   - Username: user (default)
   - Password: prismapanda
   
3. Port-Forward
   ↓
   SSH tunnel + kubectl port-forward:
   - ssh -L 5672:localhost:5672 user@10.10.10.150
   - kubectl port-forward svc/rabbitmq-panda 5672:5672
   
4. Use
   ↓
   מחזיר connection info:
   {
     'host': 'localhost',
     'port': 5672,
     'username': 'user',
     'password': 'prismapanda'
   }
   
5. Cleanup
   ↓
   אוטומטית:
   - עוצר port-forward
   - סוגר SSH tunnel
   - מנקה resources
```

---

## 📖 **API Reference**

### **RabbitMQConnectionManager**

```python
class RabbitMQConnectionManager:
    def __init__(
        self,
        k8s_host: str,              # K8s cluster host
        ssh_user: str = "prisma",    # SSH username
        ssh_password: Optional[str] = None,  # SSH password (optional)
        namespace: str = "default",  # K8s namespace
        preferred_service: str = "rabbitmq-panda",  # Preferred service
        local_port: int = 5672,      # Local AMQP port
        local_mgmt_port: int = 15672 # Local management port
    ):
        """Initialize manager."""
        
    def discover_rabbitmq_services(self) -> Dict[str, str]:
        """Find all RabbitMQ services in K8s."""
        
    def extract_credentials(self, service_name: str) -> RabbitMQCredentials:
        """Extract credentials from K8s secret."""
        
    def start_port_forward(self, service_name: str) -> bool:
        """Start kubectl port-forward on remote host."""
        
    def stop_port_forward(self):
        """Stop port-forward process."""
        
    def setup(self) -> Dict[str, any]:
        """Complete setup (discover + extract + port-forward)."""
        
    def cleanup(self):
        """Cleanup resources."""
        
    def __enter__(self):
        """Context manager entry."""
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
```

---

### **rabbitmq_connection() Context Manager**

```python
@contextmanager
def rabbitmq_connection(
    k8s_host: str = "10.10.10.150",
    service: str = "rabbitmq-panda",
    namespace: str = "default"
) -> Dict[str, any]:
    """
    Simple context manager for RabbitMQ connection.
    
    Usage:
        with rabbitmq_connection() as conn:
            # Use conn dict...
    """
```

---

## 🎯 **Integration עם הבדיקות הקיימות**

### **עדכון conftest.py:**

```python
# tests/conftest.py

from src.infrastructure.rabbitmq_manager import RabbitMQConnectionManager

@pytest.fixture(scope="session")
def auto_rabbitmq_setup(config_manager):
    """
    Auto-setup RabbitMQ with full automation.
    
    Features:
    - Auto-discovers RabbitMQ services
    - Extracts credentials automatically
    - Sets up port-forward
    - Cleans up on teardown
    """
    k8s_config = config_manager.get("kubernetes", {})
    k8s_host = k8s_config.get("cluster_host", "10.10.10.150")
    
    manager = RabbitMQConnectionManager(k8s_host=k8s_host)
    
    try:
        conn_info = manager.setup()
        yield conn_info
    finally:
        manager.cleanup()


@pytest.fixture(scope="function")
def baby_analyzer_mq_client_auto(auto_rabbitmq_setup):
    """
    BabyAnalyzerMQClient with auto-managed connection.
    
    This replaces the manual connection setup.
    """
    from src.apis.baby_analyzer_mq_client import BabyAnalyzerMQClient
    
    client = BabyAnalyzerMQClient(
        host=auto_rabbitmq_setup['host'],
        port=auto_rabbitmq_setup['port'],
        username=auto_rabbitmq_setup['username'],
        password=auto_rabbitmq_setup['password']
    )
    
    client.connect()
    yield client
    client.disconnect()
```

---

### **שימוש בבדיקות:**

```python
# tests/integration/api/test_dynamic_roi_adjustment.py

@pytest.mark.rabbitmq
class TestDynamicROIWithAutomation:
    """ROI tests with automated RabbitMQ setup."""
    
    def test_roi_change_automated(self, baby_analyzer_mq_client_auto, focus_server_api):
        """Test ROI change with fully automated setup."""
        
        # Send ROI command (connection already set up!)
        baby_analyzer_mq_client_auto.send_roi_change(start=100, end=200)
        
        # Verify...
        # (rest of test logic)
```

---

## 🛠️ **Scripts להרצה ידנית**

### **Setup Script:**

```python
# scripts/setup_rabbitmq.py

from src.infrastructure.rabbitmq_manager import RabbitMQConnectionManager
import logging

logging.basicConfig(level=logging.INFO)

def main():
    print("🚀 Setting up RabbitMQ connection...")
    
    manager = RabbitMQConnectionManager(k8s_host="10.10.10.150")
    
    try:
        conn_info = manager.setup()
        
        print("✅ RabbitMQ ready!")
        print(f"   Host: {conn_info['host']}:{conn_info['port']}")
        print(f"   Username: {conn_info['username']}")
        print(f"   Management UI: http://{conn_info['host']}:{conn_info['management_port']}")
        
        input("\nPress Enter to cleanup and exit...")
        
    finally:
        manager.cleanup()
        print("✅ Cleanup done!")


if __name__ == "__main__":
    main()
```

**הרצה:**
```bash
py scripts/setup_rabbitmq.py
```

---

## ⚙️ **Configuration**

### **environments.yaml:**

```yaml
kubernetes:
  cluster_host: "10.10.10.150"
  namespace: "default"
  
rabbitmq:
  preferred_service: "rabbitmq-panda"  # או "rabbitmq-prisma"
  # Credentials יחולצו אוטומטית מ-K8s secrets
```

---

## 🎓 **Best Practices**

### **1. Use Context Managers**

✅ **Good:**
```python
with rabbitmq_connection() as conn:
    # Use connection
    pass
# Auto cleanup!
```

❌ **Bad:**
```python
manager = RabbitMQConnectionManager(...)
conn = manager.setup()
# Use connection...
# Forgot cleanup! 😱
```

---

### **2. Session-Scoped Fixtures**

✅ **Good:**
```python
@pytest.fixture(scope="session")
def rabbitmq_setup():
    # Setup once for all tests
    pass
```

❌ **Bad:**
```python
@pytest.fixture(scope="function")
def rabbitmq_setup():
    # Setup for EVERY test (slow!)
    pass
```

---

### **3. Error Handling**

✅ **Good:**
```python
try:
    with rabbitmq_connection() as conn:
        # Use connection
        pass
except RuntimeError as e:
    pytest.skip(f"RabbitMQ not available: {e}")
```

---

## 🐛 **Troubleshooting**

### **בעיה: "No RabbitMQ services found"**

**פתרון:**
```bash
# בדוק אם יש K8s access:
kubectl get svc -n default | grep rabbit

# אם לא - וודא שyou're connected לcluster
```

---

### **בעיה: "Failed to extract credentials"**

**פתרון:**
```bash
# בדוק secrets ידנית:
kubectl get secret rabbitmq-panda -n default -o yaml

# וודא שיש שדות rabbitmq-username ו-rabbitmq-password
```

---

### **בעיה: "Port-forward failed to start"**

**פתרון:**
1. וודא שSSH access עובד:
   ```bash
   ssh prisma@10.10.10.150
   ```

2. בדוק אם הפורט תפוס:
   ```bash
   netstat -an | findstr :5672
   ```

3. נסה פורט אחר:
   ```python
   RabbitMQConnectionManager(local_port=5673)
   ```

---

## 📊 **סיכום השיפורים**

| לפני | אחרי |
|------|------|
| ❌ Setup ידני | ✅ Auto-setup |
| ❌ Credentials בקובץ | ✅ Auto-extract מsecrets |
| ❌ Port-forward ידני | ✅ Auto port-forward |
| ❌ Cleanup ידני | ✅ Auto cleanup |
| ❌ 5+ steps | ✅ 1 line of code |

---

## 🎯 **Next Steps**

1. ✅ השתמש ב-`RabbitMQConnectionManager` בכל הבדיקות
2. ✅ עדכן `conftest.py` עם fixtures חדשים
3. ✅ הרץ בדיקות ווודא שהכל עובד
4. ✅ תעדכן documentation בREADME.md

---

**נוצר על ידי:** QA Automation Architect  
**תאריך:** 08/10/2025  
**גרסה:** 1.0

