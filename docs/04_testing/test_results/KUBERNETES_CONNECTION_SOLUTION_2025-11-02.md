# פתרון בעיית חיבור Kubernetes API - 2 בנובמבר 2025

## 🔴 הבעיה
Kubernetes API (10.10.100.102:6443) לא נגיש מהמכונה המקומית שלך

## 🎯 הסיבה
ה-Kubernetes API server נמצא ברשת פנימית ולא נגיש ישירות מבחוץ

## ✅ פתרונות אפשריים

### פתרון 1: SSH Tunnel (מומלץ לטסטים מקומיים)

#### שלב 1: פתח חלון PowerShell חדש
```powershell
# הרץ את הפקודה הבאה
ssh -L 6443:10.10.100.102:6443 root@10.10.100.3

# הכנס סיסמה
PASSW0RD

# השאר את החלון פתוח!
```

#### שלב 2: עדכן kubeconfig (פעם אחת בלבד)
```powershell
# גבה את הקובץ המקורי
Copy-Item ~\.kube\config ~\.kube\config.backup

# עדכן לשימוש ב-localhost
(Get-Content ~\.kube\config) -replace 'server: https://10.10.100.102:6443', 'server: https://localhost:6443' | Set-Content ~\.kube\config
```

#### שלב 3: בדוק שעובד
```powershell
kubectl get nodes
```

### פתרון 2: גישה ישירה דרך SSH (לעבודה ידנית)

```bash
# שלב 1: התחבר ל-Jump Host
ssh root@10.10.100.3
# סיסמה: PASSW0RD

# שלב 2: התחבר ל-Worker Node
ssh prisma@10.10.100.113
# דורש SSH key!

# שלב 3: הרץ k9s או kubectl
k9s
# או
kubectl get pods -n panda
```

### פתרון 3: הרצת טסטים מתוך הרשת (אם יש לך VM ברשת)

אם יש לך גישה ל-VM ברשת הפנימית, הרץ את הטסטים משם.

## 📝 סטטוס נוכחי

### מה תוקן:
✅ kubeconfig עודכן לכתובת הנכונה (10.10.100.102:6443)
✅ SSL verification מבוטל (self-signed cert)

### מה נדרש:
❌ SSH tunnel או גישה מהרשת הפנימית

## 🔧 סקריפטים שנוצרו

1. **scripts/fix_kubernetes_connection.py** - אבחון ותיקון אוטומטי
2. **scripts/setup_k8s_tunnel.ps1** - הגדרת SSH tunnel ב-PowerShell
3. **scripts/test_k8s_fixed.py** - בדיקת חיבור עם error handling משופר
4. **src/infrastructure/kubernetes_manager_fixed.py** - Manager משופר עם fallback

## 🎯 המלצה

**לטסטים מקומיים:**
1. הרץ SSH tunnel בחלון נפרד
2. עדכן kubeconfig ל-localhost:6443
3. הרץ טסטים

**לעבודה ידנית:**
השתמש בגישה ישירה דרך SSH ו-k9s

## 📊 השפעה על טסטים

**טסטים שיעברו אחרי הפתרון:**
- test_kubernetes_connection
- test_mongodb_scale_down_outage_returns_503_no_orchestration

**סה"כ:** 2 טסטים נוספים יעברו

## ⚠️ הערות חשובות

1. **SSH Tunnel חייב להישאר פתוח** במהלך הרצת הטסטים
2. **אל תשכח להחזיר** את kubeconfig למצב המקורי אחרי הטסטים:
   ```powershell
   Copy-Item ~\.kube\config.backup ~\.kube\config
   ```
3. **בעיית ה-SSH key** ל-10.10.100.113 עדיין קיימת - נדרש SSH key

---

**תאריך:** 2 בנובמבר 2025
**סטטוס:** פתרון זמין, דורש פעולה ידנית (SSH tunnel)
