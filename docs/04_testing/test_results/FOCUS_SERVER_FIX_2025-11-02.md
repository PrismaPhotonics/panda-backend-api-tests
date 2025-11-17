# תיקון בעיית Focus Server - 2 בנובמבר 2025

## 🔴 הבעיות שמצאנו:

### 1. כתובת שגויה (אם משתמשים ב-new_production):
- **בקונפיג:** `10.10.100.100`
- **בפועל (Ingress):** `10.10.10.100`
- **זה מסביר את ה-timeout!**

### 2. Endpoint שגוי:
- **ניסינו:** `GET /focus-server/`
- **הנכון:** `POST /focus-server/configure`
- **זה מסביר את ה-404!**

### 3. באג קריטי - Port Conflict:
```
Service "grpc-service-1-65" is invalid: 
spec.ports[0].nodePort: Invalid value: 12301: provided port is already allocated
```
**זה הבאג PZ-13268 - CNI IP Exhaustion!**

## ✅ הפתרון:

### 1. וודא שאתה משתמש בסביבת `staging`:
```bash
# הכתובת נכונה ב-staging:
base_url: "https://10.10.10.100/focus-server/"
```

### 2. השתמש ב-endpoint הנכון:
```python
# ❌ שגוי:
GET https://10.10.10.100/focus-server/

# ✅ נכון:
POST https://10.10.10.100/focus-server/configure
```

### 3. ניקוי Port Conflicts:
```bash
# מהשרת worker-node:
kubectl get svc -n panda | grep grpc-service

# מחק services ישנים שתופסים פורטים:
kubectl delete svc grpc-service-1-65 -n panda  # אם קיים
```

## 📝 מהלוגים ראינו:

1. ✅ **השרת עובד** - `/configure` עובד מצוין
2. ✅ **החיבור עובד** - התקבלה תשובה 200 OK
3. ❌ **Port conflict** - פורט 12301 תפוס (באג!)

## 🎯 פעולות נדרשות:

1. **להריץ טסטים על staging** (לא new_production אם קיים)
2. **לנקות grpc-services ישנים** שהסתיימו
3. **לדווח על הבאג** של port conflict ב-Jira

## 🔍 בדיקה מהירה:

```bash
# מהשרת worker-node:
# 1. בדוק כמה grpc-services יש
kubectl get svc -n panda | grep grpc-service | wc -l

# 2. בדוק איזה פורטים תפוסים
kubectl get svc -n panda -o json | jq '.items[] | select(.spec.type=="NodePort") | {name: .metadata.name, ports: .spec.ports[].nodePort}' | grep -A1 "grpc"

# 3. מחק jobs ישנים
kubectl get jobs -n panda | grep grpc-job | awk '{print $1}' | xargs kubectl delete job -n panda
```

---

**תאריך:** 2 בנובמבר 2025
**ממצא:** Focus Server עובד, אבל יש port conflicts
**פעולה:** ניקוי grpc-services ישנים + שימוש ב-URL הנכון
