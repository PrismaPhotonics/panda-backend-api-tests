# RabbitMQ Automation - Quick Start

## 🎯 **TL;DR**

**במקום התהליך הידני המורכב, עכשיו:**

```python
from src.infrastructure.rabbitmq_manager import rabbitmq_connection

# One line!
with rabbitmq_connection() as conn:
    # RabbitMQ ready to use!
    pass
```

**זהו!** 🎉

---

## 🚀 **3 דרכים להשתמש**

### **1️⃣ Setup Script (הכי פשוט!)**

```bash
# Setup + test connection + test commands
py scripts/setup_rabbitmq_auto.py --test-commands

# Setup ותשאיר רץ
py scripts/setup_rabbitmq_auto.py --keep-alive
```

---

### **2️⃣ Python Code**

```python
from src.infrastructure.rabbitmq_manager import rabbitmq_connection
from src.apis.baby_analyzer_mq_client import BabyAnalyzerMQClient

with rabbitmq_connection() as conn:
    client = BabyAnalyzerMQClient(**conn)
    client.send_keepalive()
```

---

### **3️⃣ Pytest Tests**

```python
@pytest.mark.rabbitmq
def test_my_feature(auto_rabbitmq_connection):
    """Test with auto-managed RabbitMQ."""
    client = BabyAnalyzerMQClient(**auto_rabbitmq_connection)
    # Test...
```

---

## 🎓 **מה זה עושה אוטומטית?**

```
1. 🔍 Discovery    → מוצא rabbitmq-panda, rabbitmq-prisma
2. 🔑 Credentials  → מחלץ user/password מK8s secrets
3. 🚀 Port-Forward → מגדיר kubectl port-forward על השרת
4. ✅ Ready!       → מחזיר connection info
5. 🧹 Cleanup      → מנקה הכל בסיום
```

**כל זה ב-1 שורת קוד!**

---

## 📖 **Full Documentation**

- **מדריך מלא:** [`RABBITMQ_AUTOMATION_GUIDE.md`](./RABBITMQ_AUTOMATION_GUIDE.md)
- **API Reference:** `src/infrastructure/rabbitmq_manager.py`
- **Examples:** `scripts/setup_rabbitmq_auto.py`

---

## 🐛 **Troubleshooting**

| בעיה | פתרון |
|------|-------|
| "No services found" | וודא K8s access: `kubectl get svc` |
| "Credentials failed" | בדוק secrets: `kubectl get secret rabbitmq-panda` |
| "Port-forward failed" | בדוק SSH: `ssh prisma@10.10.10.150` |

---

## 🎯 **Before & After**

### **לפני (Manual):**

```bash
# 1. SSH לשרת
ssh prisma@10.10.10.150

# 2. מצא RabbitMQ
kubectl get svc | grep rabbit

# 3. חלץ credentials
kubectl get secret rabbitmq-panda -o jsonpath=... | base64 -d

# 4. הרץ port-forward
kubectl port-forward svc/rabbitmq-panda 5672:5672

# 5. עדכן config
# (edit environments.yaml)

# 6. הרץ בדיקות
py -m pytest ...

# 7. נקה (אל תשכח!)
# Ctrl+C, exit, etc.
```

**⏱️ זמן:** ~10 דקות  
**📝 שלבים:** 7+  
**❌ סיכון:** שכחת cleanup

---

### **אחרי (Automated):**

```bash
py scripts/setup_rabbitmq_auto.py --test-commands
```

**⏱️ זמן:** ~10 שניות  
**📝 שלבים:** 1  
**✅ Cleanup:** אוטומטי!

---

## 🎉 **Summary**

זכור את כל הקושי שהיה? עכשיו זה:

```python
with rabbitmq_connection() as conn:
    # Magic! ✨
    pass
```

**זהו!** 🚀

---

**Created:** 08/10/2025  
**Author:** QA Automation Architect

