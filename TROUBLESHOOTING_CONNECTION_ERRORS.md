# פתרון בעיות חיבור - מדריך מקיף

**תאריך**: 19 אוקטובר 2025

---

## 🔍 בדיקה ראשונית

MongoDB: ✅ נגיש (10.10.100.108:27017)  
RabbitMQ: ✅ נגיש (10.10.100.107:5672)  
Backend: ⚠️ SSL Certificate issue

---

## 🐛 שגיאות נפוצות ופתרונות

### 1. שגיאת SSL Certificate (Backend)

#### שגיאה:
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
requests.exceptions.SSLError: HTTPSConnectionPool
```

#### פתרון:
הבעיה היא self-signed certificate. צריך להוסיף `verify=False` בקריאות ל-Backend.

**בקובץ**: `src/apis/focus_server_api.py` או דומה:
```python
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# בקריאות HTTP:
response = requests.get(url, verify=False)
```

---

### 2. שגיאת Authentication למונגו

#### שגיאה:
```
pymongo.errors.OperationFailure: Authentication failed
```

#### סיבה:
- Username/Password שגויים
- Auth source שגוי

#### פתרון:
וודא ש-URI נכון:
```
mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma
```

**לא**:
```
mongodb://prisma:prisma@10.10.100.108:27017/?authSource=admin  ❌
```

---

### 3. שגיאת Timeout למונגו

#### שגיאה:
```
pymongo.errors.ServerSelectionTimeoutError: No servers found yet
```

#### סיבה:
- MongoDB לא נגיש
- Firewall חוסם
- Network issue

#### פתרון:
```powershell
# בדוק חיבור:
Test-NetConnection -ComputerName 10.10.100.108 -Port 27017

# בדוק מתוך Python:
python -c "from pymongo import MongoClient; c = MongoClient('mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma', serverSelectionTimeoutMS=5000); print(c.server_info())"
```

---

### 4. שגיאת RabbitMQ Authentication

#### שגיאה:
```
pika.exceptions.ProbableAuthenticationError
ACCESS_REFUSED - Login was refused
```

#### סיבה:
- Username/Password שגויים
- User לא קיים ב-RabbitMQ

#### פתרון:
בדוק credentials:
```yaml
rabbitmq:
  username: "prisma"  # או "user"
  password: "prismapanda"
```

אם לא עובד, נסה:
```yaml
username: "user"
password: "prismapanda"
```

---

### 5. שגיאת Connection Refused (RabbitMQ)

#### שגיאה:
```
pika.exceptions.AMQPConnectionError: Connection refused
```

#### סיבה:
- RabbitMQ לא רץ
- Port שגוי
- Network issue

#### פתרון:
```powershell
# בדוק חיבור:
Test-NetConnection -ComputerName 10.10.100.107 -Port 5672

# בדוק Management UI:
Start-Process "http://10.10.100.107:15672"
# Login: prisma / prismapanda
```

---

### 6. שגיאת Port-Forward (SSH)

#### שגיאה:
```
paramiko.ssh_exception.NoValidConnectionsError
Connection refused
```

#### סיבה:
- SSH לא נגיש
- Credentials שגויים
- Network issue

#### פתרון:
```powershell
# בדוק SSH ידנית:
ssh root@10.10.100.3
# Password: PASSW0RD

ssh prisma@10.10.100.113
# Password: PASSW0RD
```

---

### 7. שגיאת Kubernetes API

#### שגיאה:
```
kubernetes.client.exceptions.ApiException: Unauthorized
```

#### סיבה:
- Kubeconfig לא נכון
- Context שגוי
- Namespace לא קיים

#### פתרון:
```bash
# בדוק namespace:
kubectl get namespaces | grep panda

# בדוק pods:
kubectl get pods -n panda
```

---

### 8. שגיאת Import

#### שגיאה:
```
ModuleNotFoundError: No module named 'src'
ImportError: cannot import name 'ConfigManager'
```

#### סיבה:
- Virtual environment לא מופעל
- Dependencies לא מותקנים
- PYTHONPATH לא נכון

#### פתרון:
```powershell
# הפעל virtual environment:
.venv\Scripts\Activate.ps1

# התקן dependencies:
pip install -r requirements.txt

# או התקן את הפרויקט:
pip install -e .
```

---

## 🔧 בדיקות מהירות

### בדיקה 1: Virtual Environment
```powershell
# בדוק אם .venv מופעל:
if ($env:VIRTUAL_ENV) {
    Write-Host "✅ Virtual environment active: $env:VIRTUAL_ENV"
} else {
    Write-Host "❌ Virtual environment NOT active"
    Write-Host "Run: .venv\Scripts\Activate.ps1"
}
```

### בדיקה 2: Python Packages
```powershell
# בדוק packages חשובים:
python -c "import pymongo; print('pymongo:', pymongo.version)"
python -c "import pika; print('pika:', pika.__version__)"
python -c "import requests; print('requests:', requests.__version__)"
```

### בדיקה 3: Environment Variables
```powershell
# בדוק משתני סביבה:
echo $env:MONGODB_URI
echo $env:FOCUS_BASE_URL
echo $env:RABBITMQ_HOST
```

### בדיקה 4: Network Connectivity
```powershell
# MongoDB:
Test-NetConnection -ComputerName 10.10.100.108 -Port 27017

# RabbitMQ:
Test-NetConnection -ComputerName 10.10.100.107 -Port 5672

# Backend:
Test-NetConnection -ComputerName 10.10.100.100 -Port 443
```

---

## 📋 Checklist לפני ריצת טסטים

- [ ] Virtual environment מופעל (`.venv\Scripts\Activate.ps1`)
- [ ] Dependencies מותקנים (`pip install -r requirements.txt`)
- [ ] MongoDB נגיש (port 27017)
- [ ] RabbitMQ נגיש (port 5672)
- [ ] Backend נגיש (port 443)
- [ ] Environment variables מוגדרים (`. .\set_production_env.ps1`)
- [ ] Config files נכונים (`environments.yaml`)

---

## 🚨 אם הכל נכשל

### אפשרות 1: הרץ טסטים עם debug mode
```powershell
pytest tests/unit/ -v -s --log-cli-level=DEBUG
```

### אפשרות 2: הרץ בדיקת חיבור פשוטה
```python
# test_connection.py
from pymongo import MongoClient
import requests

# Test MongoDB
try:
    client = MongoClient("mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma", serverSelectionTimeoutMS=5000)
    print("✅ MongoDB connected:", client.server_info()['version'])
except Exception as e:
    print("❌ MongoDB failed:", e)

# Test Backend
try:
    response = requests.get("https://10.10.100.100/", verify=False, timeout=5)
    print("✅ Backend connected:", response.status_code)
except Exception as e:
    print("❌ Backend failed:", e)
```

### אפשרות 3: בדוק לוגים של הפודים
```bash
# Connect via SSH:
ssh root@10.10.100.3
ssh prisma@10.10.100.113

# Check Focus Server logs:
kubectl logs -n panda $(kubectl get pods -n panda -l app.kubernetes.io/name=panda-panda-focus-server -o name | head -1) --tail=50

# Check RabbitMQ logs:
kubectl logs -n panda rabbitmq-panda-0 --tail=50
```

---

## 📞 עזרה נוספת

אם אתה רואה שגיאות ספציפיות, העתק אותן והרץ:

```powershell
# חפש בתיעוד:
Select-String -Path "documentation\**\*.md" -Pattern "<error_text>"
```

או:
- בדוק `MONITORING_LOGS_GUIDE.md` לניטור לוגים
- בדוק `COMPLETE_INFRASTRUCTURE_SUMMARY.md` לפרטי תשתית
- בדוק `TEST_SUITE_INVENTORY.md` לרשימת טסטים

---

**נוצר**: 19 אוקטובר 2025  
**גרסה**: 1.0

