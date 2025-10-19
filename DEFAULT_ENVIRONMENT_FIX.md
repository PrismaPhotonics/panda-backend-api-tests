# ✅ תיקון: ה-Default Environment עכשיו הוא new_production

**תאריך תיקון**: 19 אוקטובר 2025  
**בעיה**: הטסטים רצו על `staging` במקום על `new_production`  
**פתרון**: שינוי ה-default environment ב-3 מקומות

---

## 🔧 מה תוקן?

### 1. `tests/conftest.py` (שורה 46)

**לפני**:
```python
parser.addoption(
    "--env",
    action="store",
    default="staging",  # ❌ רץ על staging
```

**אחרי**:
```python
parser.addoption(
    "--env",
    action="store",
    default="new_production",  # ✅ רץ על new_production
```

---

### 2. `config/environments.yaml` (שורה 416)

**לפני**:
```yaml
default_environment: "staging"  # ❌ ברירת מחדל: staging
```

**אחרי**:
```yaml
default_environment: "new_production"  # ✅ ברירת מחדל: new_production
```

---

### 3. `run_all_tests.ps1` (שורה 116)

**נוסף**:
```powershell
# Add environment flag (uses new_production by default)
$pytestArgs += "--env=new_production"  # ✅ מפורש
```

---

## 🎯 תוצאה

### עכשיו כשמריצים:

```powershell
pytest tests/ -v
```

או:

```powershell
.\run_all_tests.ps1
```

הטסטים **אוטומטית** משתמשים ב:

| רכיב | ערך |
|------|-----|
| **MongoDB** | `mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma` |
| **Backend** | `https://10.10.100.100/focus-server/` |
| **RabbitMQ** | `10.10.100.107:5672` |
| **K8s Namespace** | `panda` |
| **Environment** | `new_production` |

---

## ✅ אין צורך יותר ב:

- ❌ `--env=new_production` flag
- ❌ הגדרת משתני סביבה ידנית (אם משתמשים ב-pytest ישירות)
- ❌ פקודות מיוחדות

---

## 🚀 פקודות הרצה (פשוט!)

```powershell
# אופציה 1: עם הסקריפט (מומלץ!)
.\run_all_tests.ps1

# אופציה 2: ידני (פשוט!)
pytest tests/ -v

# אופציה 3: טסטים ספציפיים
pytest tests/unit/ -v
pytest tests/integration/ -v
```

**הכל רץ על new_production אוטומטית!**

---

## 📊 בדיקה מהירה

```powershell
# בדוק מה ה-default environment
Select-String -Path "config\environments.yaml" -Pattern "default_environment"
# Output: default_environment: "new_production"  ✅

# בדוק ב-conftest
Select-String -Path "tests\conftest.py" -Pattern 'default="'
# Output: default="new_production"  ✅
```

---

## 💡 למה זה חשוב?

**לפני**: הטסטים רצו על סביבת `staging` ישנה עם MongoDB ישן  
**אחרי**: הטסטים רצים על `new_production` עם MongoDB החדש (`10.10.100.108`)

---

**סטטוס**: ✅ תוקן  
**תאריך**: 19 אוקטובר 2025  
**גרסה**: 1.0

