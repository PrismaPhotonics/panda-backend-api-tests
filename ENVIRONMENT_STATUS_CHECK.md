# בדיקת סטטוס סביבה - האם הכל מוכן לריצת טסטים?

**תאריך בדיקה**: 19 אוקטובר 2025

---

## ✅ מה עשינו עד עכשיו (סיכום)

### 1. 📝 קונפיגורציות עודכנו בהצלחה

#### א. `config/environments.yaml`
✅ **מעודכן לחלוטין!**

- **Environment חדש**: `new_production` (במקום `new_staging`)
- **MongoDB**: `mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma`
- **RabbitMQ**: `10.10.100.107:5672` (LoadBalancer)
- **K8s**: 
  - API: `https://10.10.100.102:6443`
  - Namespace: `panda`
  - Dashboard: `https://10.10.100.102/`
- **Focus Server**:
  - Backend: `https://10.10.100.100/focus-server/`
  - Frontend: `https://10.10.10.100/liveView`
- **SSH Gateway**: `10.10.100.3` → `10.10.100.113`

#### ב. `set_production_env.ps1`
✅ **מעודכן לחלוטין!**

משתני סביבה שמוגדרים:
```powershell
$env:FOCUS_ENV = "new_production"
$env:FOCUS_BASE_URL = "https://10.10.100.100/focus-server/"
$env:MONGODB_URI = "mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma"
$env:MONGODB_HOST = "10.10.100.108"
$env:RABBITMQ_HOST = "10.10.100.107"
$env:RABBITMQ_PORT = "5672"
$env:K8S_API_SERVER = "https://10.10.100.102:6443"
$env:K8S_NAMESPACE = "panda"
# ועוד הרבה משתנים...
```

#### ג. `config/NEW_PRODUCTION_ENV.yaml`
✅ **נוצר ומעודכן!**

קובץ YAML מלא עם כל הפרטים:
- MongoDB connection strings
- RabbitMQ endpoints
- K8s services
- Test configurations

---

## 🎯 האם הטסטים ירוצו על הסביבה החדשה?

### כן! אבל צריך להגדיר משתני סביבה לפני כל ריצה

**סטטוס נוכחי**: משתני סביבה **לא מוגדרים** (בגלל שפתחת terminal חדש)

---

## 🚀 איך להריץ טסטים על הסביבה החדשה

### שיטה 1: עם הסקריפט האוטומטי (מומלץ!)

```powershell
cd C:\Projects\focus_server_automation

# הסקריפט מגדיר סביבה אוטומטית!
.\run_all_tests.ps1
```

הסקריפט עושה את כל העבודה:
1. ✅ מגדיר משתני סביבה אוטומטית (מריץ `set_production_env.ps1`)
2. ✅ מפעיל virtual environment
3. ✅ מריץ את הטסטים
4. ✅ יוצר דוח HTML

---

### שיטה 2: ידנית (שליטה מלאה)

```powershell
cd C:\Projects\focus_server_automation

# שלב 1: הגדר סביבה
. .\set_production_env.ps1

# שלב 2: בדוק שהכל מוגדר
echo $env:FOCUS_ENV          # אמור להדפיס: new_production
echo $env:MONGODB_URI        # אמור להדפיס: mongodb://prisma:prisma@...
echo $env:K8S_NAMESPACE      # אמור להדפיס: panda

# שלב 3: הרץ טסטים
pytest tests/ focus_server_api_load_tests/focus_api_tests/ -v
```

---

## 📊 מה הטסטים בודקים נגד הסביבה החדשה?

### כשמשתני הסביבה מוגדרים, הטסטים רצים נגד:

| רכיב | כתובת | מקור |
|------|--------|------|
| **Focus Server** | `https://10.10.100.100/focus-server/` | `$env:FOCUS_BASE_URL` |
| **MongoDB** | `10.10.100.108:27017` | `$env:MONGODB_URI` |
| **RabbitMQ** | `10.10.100.107:5672` | `$env:RABBITMQ_HOST` |
| **K8s Namespace** | `panda` | `$env:K8S_NAMESPACE` |
| **Frontend** | `https://10.10.10.100/liveView` | קונפיג |

---

## 🔍 איך הטסטים יודעים להשתמש במשתני סביבה?

### דוגמה מקוד הטסטים:

```python
# בקובץ conftest.py או בטסטים עצמם
import os

# הטסט קורא משתני סביבה
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
FOCUS_BASE_URL = os.getenv("FOCUS_BASE_URL", "http://localhost:5000")

# דוגמה לשימוש
def test_mongodb_connection():
    client = MongoClient(MONGODB_URI)
    assert client.server_info()

def test_focus_server_health():
    response = requests.get(f"{FOCUS_BASE_URL}/health")
    assert response.status_code == 200
```

---

## ✅ Checklist - האם הכל מוכן?

- [x] **קובץ `config/environments.yaml` מעודכן** - ✅ יש `new_production` environment
- [x] **קובץ `set_production_env.ps1` מעודכן** - ✅ מגדיר כל המשתנים
- [x] **MongoDB connection string** - ✅ `mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma`
- [x] **RabbitMQ endpoints** - ✅ `10.10.100.107:5672`
- [x] **K8s configuration** - ✅ Namespace `panda`, API `10.10.100.102:6443`
- [x] **PZ code updated** - ✅ Clone מ-Bitbucket בתיקייה `pz/`
- [x] **Documentation organized** - ✅ 72 קבצי MD מסודרים
- [x] **Test runner script** - ✅ `run_all_tests.ps1` מוכן
- [ ] **משתני סביבה מוגדרים** - ❌ צריך להריץ לפני כל session

---

## 🎯 תשובה לשאלה שלך: "האם הטסטים רצים על הסביבה החדשה?"

### כן! אבל עם תנאי:

1. ✅ **הקונפיגורציות מעודכנות** - כל הקבצים נכונים
2. ✅ **משתני הסביבה מוגדרים נכון** - `set_production_env.ps1` מוכן
3. ⚠️ **צריך להריץ את ההגדרה לפני כל session** - כי PowerShell לא שומר משתני סביבה

---

## 📝 סיכום טכני מפורט

### 🔧 מה עודכן:

| קובץ | סטטוס | פרטים |
|------|--------|--------|
| `config/environments.yaml` | ✅ מעודכן | נוסף `new_production` עם כל הפרטים |
| `set_production_env.ps1` | ✅ מעודכן | 20+ משתני סביבה מוגדרים |
| `config/NEW_PRODUCTION_ENV.yaml` | ✅ נוצר | קובץ YAML מפורט |
| `documentation/infrastructure/` | ✅ מעודכן | תיעוד סביבה מלא |
| `pz/` | ✅ נוצר | קוד PZ מ-Bitbucket |
| `run_all_tests.ps1` | ✅ נוצר | סקריפט הרצה אוטומטי |

### 🌐 רכיבי הסביבה החדשה:

```yaml
Production Environment (panda namespace):
  Backend:
    URL: https://10.10.100.100/focus-server/
    Type: HTTPS (self-signed cert)
  
  Frontend:
    URL: https://10.10.10.100/liveView
    SiteId: prisma-210-1000
  
  MongoDB:
    Host: 10.10.100.108:27017
    Connection: mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma
    Database: prisma
    Auth: prisma
    Type: LoadBalancer (K8s)
    Internal: mongodb.panda:27017
  
  RabbitMQ:
    Host: 10.10.100.107
    AMQP: 5672
    AMQP SSL: 5671
    Management: 15672
    Type: LoadBalancer (K8s)
    Internal: rabbitmq-panda.panda:5672
  
  Kubernetes:
    API: https://10.10.100.102:6443
    Dashboard: https://10.10.100.102/
    Namespace: panda
    Context: panda-cluster
  
  SSH Access (for K9s/logs):
    Jump Host: 10.10.100.3 (root)
    Target: 10.10.100.113 (prisma)
    K9s: Available on target host
```

---

## 🚦 צעדים הבאים

### להתחיל לעבוד (2 אופציות):

#### אופציה א: עם הסקריפט (קל!)
```powershell
cd C:\Projects\focus_server_automation
.\run_all_tests.ps1
```

#### אופציה ב: ידני (שליטה מלאה)
```powershell
cd C:\Projects\focus_server_automation

# 1. הגדר סביבה
. .\set_production_env.ps1

# 2. בדוק
echo $env:MONGODB_URI

# 3. הרץ טסטים
pytest tests/unit/ -v
```

---

## 💡 טיפ חשוב!

**כל פעם שאתה פותח terminal חדש**, צריך להריץ:
```powershell
. .\set_production_env.ps1
```

או להשתמש בסקריפט `run_all_tests.ps1` שעושה את זה אוטומטית!

---

## 📚 לקריאה נוספת

- **[QUICK_START_NEW_PRODUCTION.md](documentation/guides/QUICK_START_NEW_PRODUCTION.md)** - התחלה מהירה
- **[COMPLETE_INFRASTRUCTURE_SUMMARY.md](documentation/infrastructure/COMPLETE_INFRASTRUCTURE_SUMMARY.md)** - תיעוד תשתית מלא
- **[TEST_SUITE_INVENTORY.md](documentation/testing/TEST_SUITE_INVENTORY.md)** - רשימת כל הטסטים

---

**סטטוס**: ✅ הכל מוכן! רק צריך להריץ `set_production_env.ps1` לפני כל session

**תאריך בדיקה**: 19 אוקטובר 2025  
**גרסה**: 1.0

