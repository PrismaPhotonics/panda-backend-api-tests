# ✅ סביבת Staging הוגדרה בהצלחה!

**תאריך:** 2025-11-02  
**סביבה:** `staging`  
**סטטוס:** ✅ הוגדר ומוכן לשימוש

---

## 📋 פרטי הסביבה החדשה

### 🌐 **כתובות URL:**

| רכיב | כתובת | שינוי |
|------|--------|-------|
| **Backend** | `https://10.10.10.100/focus-server/` | ✅ עודכן מ-`10.10.100.100` |
| **Frontend** | `https://10.10.10.100/liveView` | ✅ ללא שינוי |
| **Frontend API** | `https://10.10.10.100/prisma/api/internal/sites/prisma-210-1000` | ✅ עודכן |
| **Site ID** | `prisma-210-1000` | ✅ ללא שינוי |

### 🔧 **תשתיות (ללא שינוי):**

| שירות | כתובת | פורט |
|-------|--------|------|
| **MongoDB** | `10.10.100.108` | 27017 |
| **RabbitMQ** | `10.10.100.107` | 5672 |
| **Kubernetes API** | `10.10.100.102` | 6443 |

---

## 📝 **מה השתנה?**

### 🆕 **שינויים עיקריים:**

1. **Backend URL** שונה מ-`10.10.100.100` ← `10.10.10.100` 
2. **Frontend API** שונה מ-`10.10.10.150:30443` ← `10.10.10.100`
3. **Default Environment** עודכן ל-`staging`

### 📦 **קבצים שנוצרו/עודכנו:**

1. ✅ `config/environments.yaml` - הוספה סביבת `staging`
2. ✅ Default environment שונה ל-`staging`
3. ✅ `config/pandaapp_config_v2.json` - קונפיגורציית PandaApp המלאה
4. ✅ Test configurations הוגדרו לסביבה החדשה

---

## 🚀 **איך להשתמש בסביבה החדשה?**

### **1. הסביבה מוגדרת כ-Default:**
```bash
# The automation will automatically use new_production_v2 environment
pytest -m xray -v
```

### **2. להריץ טסטים ספציפיים:**
```bash
# Run health check tests
pytest -m xray -k "health" -v

# Run all xray tests except 200 jobs
pytest -m xray -k "not 200_concurrent_jobs" -v

# Run specific test file
pytest tests/integration/api/test_health_check.py -v
```

### **3. לבדוק את הקונפיגורציה:**
```python
from config.config_manager import ConfigManager

cm = ConfigManager()
print(f"Environment: {cm.environment}")
print(f"Backend: {cm.get('focus_server').get('base_url')}")
print(f"Frontend: {cm.get('focus_server').get('frontend_url')}")
```

---

## ✅ **בדיקת תקינות - Connectivity Test:**

```bash
# Test backend connectivity
Test-NetConnection -ComputerName 10.10.10.100 -Port 443

# Test MongoDB connectivity
Test-NetConnection -ComputerName 10.10.100.108 -Port 27017

# Test RabbitMQ connectivity
Test-NetConnection -ComputerName 10.10.100.107 -Port 5672
```

---

## 🔒 **SSL Configuration:**

- **SSL Enabled:** Yes
- **Verify SSL:** No (self-signed certificates)
- **Certificates:** Self-signed (production environment)

---

## 🎯 **Test Configurations:**

### **Enabled:**
- ✅ Performance Tests (safe, read-only)
- ✅ Load Tests (controlled - max 200 concurrent jobs)
- ✅ All Integration Tests
- ✅ All API Tests
- ✅ Health Check Tests

### **Disabled:**
- ❌ MongoDB Outage Tests (destructive)
- ❌ RabbitMQ Outage Tests (destructive)

---

## 📊 **Configuration Details:**

### **NFFT Options:**
```
128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536
```

### **Constraints:**
- Frequency Max: 1000 Hz
- Frequency Min: 0 Hz
- Sensors Range: 0-2222
- Max Windows: 30
- Num Live Screens: 30

### **gRPC Configuration:**
- Timeout: 500 seconds
- Stream Min Timeout: 600 seconds
- Num Retries: 10

---

## 🔄 **חזרה לסביבה הקודמת (אם צריך):**

אם תרצה לחזור לסביבה הקודמת (`new_production`):

1. **ערוך את `config/environments.yaml`:**
```yaml
default_environment: "new_production"  # Change back
```

2. **או השתמש ב-Environment Variable:**
```bash
$env:FOCUS_ENV = "new_production"
pytest -m xray -v
```

---

## 📁 **קבצי Reference:**

### **מקור הקונפיגורציה:**
- `docs/09_env_config/usersettings (1).json` - הקובץ המקורי
- `config/usersettings.new_production_client.json` - הסביבה הקודמת
- `config/environments.yaml` - הקונפיגורציה המרכזית

### **תיעוד נוסף:**
- `config/README.md` - מדריך קונפיגורציה
- `docs/02_user_guides/` - מדריכי משתמש
- `docs/03_architecture/` - ארכיטקטורה

---

## 🧪 **בדיקת Sanity מומלצת:**

```bash
# 1. בדוק קישוריות
pytest tests/infrastructure/test_basic_connectivity.py -v

# 2. הרץ health checks
pytest -m xray -k "health" -v

# 3. הרץ טסט אחד פשוט
pytest tests/integration/api/test_health_check.py::TestHealthCheckValidResponses::test_ack_health_check_valid_response -v

# 4. הרץ את כל הטסטים (בלי 200 jobs)
pytest -m xray -k "not 200_concurrent_jobs" -v
```

---

## ⚠️ **הערות חשובות:**

1. **סביבת Production:** זו סביבת production - היזהר עם טסטים הרסניים
2. **Load Tests:** מוגבלים ל-200 concurrent jobs (PZ-14088)
3. **SSL Certificates:** Self-signed - הגדר `verify_ssl: false`
4. **MongoDB/RabbitMQ:** שימוש באותן כתובות כמו קודם

---

## 📞 **במקרה של בעיות:**

1. בדוק connectivity עם `Test-NetConnection`
2. ודא ש-SSL verify מכובה (`verify_ssl: false`)
3. בדוק שה-VPN/network access פעיל
4. ריץ: `pytest --collect-only` לוודא שהטסטים נאספים

---

## ✅ **סטטוס סופי:**

```
✅ סביבה הוגדרה: new_production_v2
✅ Backend: https://10.10.10.100/focus-server/
✅ Frontend: https://10.10.10.100/liveView
✅ MongoDB: 10.10.100.108:27017
✅ RabbitMQ: 10.10.100.107:5672
✅ Default Environment: new_production_v2

🎯 המערכת מוכנה לריצת טסטים!
```

---

**נוצר על ידי:** Focus Server Automation Framework  
**תאריך:** 2025-10-30  
**גרסה:** Production V2 (November 2025)

