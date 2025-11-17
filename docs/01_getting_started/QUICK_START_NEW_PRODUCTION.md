# 🚀 Quick Start - ריצת טסטים על הסביבה החדשה

## תן לי 2 דקות והכל יהיה מוכן!

---

## ⚡ הכנה מהירה (פעם אחת)

### 1. הגדר משתני סביבה
```powershell
cd C:\Projects\focus_server_automation
. .\set_production_env.ps1
```

### 2. בדוק חיבור ל-MongoDB
```powershell
python -c "from pymongo import MongoClient; c = MongoClient('$env:MONGODB_URI'); print('✅ MongoDB:', c.server_info()['version'])"
```

### 3. בדוק RabbitMQ Management UI
```powershell
Start-Process "http://10.10.100.107:15672"
# Username: prisma | Password: prismapanda
```

---

## 🧪 הרצת טסטים

### Unit Tests
```powershell
pytest tests/unit/ -v
```

### Integration Tests
```powershell
pytest tests/integration/ -v
```

### API Contract Tests
```powershell
pytest focus_server_api_load_tests/focus_api_tests/ -v
```

### Load Tests (Locust)
```powershell
cd focus_server_api_load_tests\load_tests
locust -f locust_focus_server.py
# Open: http://localhost:8089
# Host: https://10.10.100.100
```

---

## 👀 ניטור לוגים בזמן ריצת טסטים

### פתח Terminal נוסף ל-K9s:

```bash
# Terminal 2 (SSH):
ssh root@10.10.100.3
# Password: PASSW0RD

ssh prisma@10.10.100.113
# Password: PASSW0RD

k9s -n panda
```

### K9s - פקודות מהירות:
- `:pods` → הצג פודים
- `/focus` → חפש focus server
- `l` → הצג לוגים
- `s` → shell לתוך הפוד
- `?` → עזרה

---

## 🎯 מסמכים מפורטים

| מסמך | תיאור |
|------|-------|
| **`AUTOMATION_CONFIG_SUMMARY_HE.md`** | 📋 סיכום מלא של כל העדכונים |
| **`MONITORING_LOGS_GUIDE.md`** | 📜 מדריך מקיף לניטור לוגים |
| **`connect_k9s.ps1`** | 🔧 סקריפט לחיבור ל-K9s |
| **`config/environments.yaml`** | ⚙️ קונפיגורציה מלאה |

---

## 🔗 נקודות קצה חשובות

| שירות | כתובת | פרטי גישה |
|-------|--------|----------|
| **Backend** | `https://10.10.100.100/focus-server/` | - |
| **Frontend** | `https://10.10.10.100/liveView` | - |
| **MongoDB** | `10.10.100.108:27017` | user: `prisma` / pass: `prisma` |
| **RabbitMQ** | `10.10.100.107:5672` | user: `prisma` / pass: `prismapanda` |
| **RabbitMQ UI** | `http://10.10.100.107:15672` | user: `prisma` / pass: `prismapanda` |
| **K8s Dashboard** | `https://10.10.100.102/` | - |
| **K9s (SSH)** | `10.10.100.3 → 10.10.100.113` | root / prisma |

---

## 🆘 בעיות? פתרונות מהירים

### MongoDB לא מגיב?
```powershell
Test-NetConnection -ComputerName 10.10.100.108 -Port 27017
```

### RabbitMQ לא עובד?
```powershell
Test-NetConnection -ComputerName 10.10.100.107 -Port 5672
```

### צריך לראות לוגים אבל אין גישה ל-SSH?
בדוק את `MONITORING_LOGS_GUIDE.md` - יש שם Python class לאיסוף לוגים מרחוק!

---

## ✅ זהו! אתה מוכן!

```powershell
# 1. הגדר סביבה
. .\set_production_env.ps1

# 2. הרץ טסטים
pytest tests/ -v

# 3. צפה בלוגים (terminal נפרד)
ssh root@10.10.100.3
ssh prisma@10.10.100.113
k9s -n panda
```

**בהצלחה! 🎉**

