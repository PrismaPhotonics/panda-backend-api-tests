# ✅ K9s Connection - הכתובת הנכונה

**Date:** October 16, 2025  
**Status:** ✅ **מצאנו את הכתובת הנכונה!**

---

## 🎯 הכתובת הנכונה

**Kubernetes API Server:**
```
https://10.10.100.102:6443
```

**Dashboard UI:**
```
https://10.10.100.102/
```

**Direct link to panda namespace services:**
```
https://10.10.100.102/#/service?namespace=panda
```

---

## ✅ בדיקת חיבור - כל הפורטים פתוחים!

```
✅ Port 443   - Dashboard UI (HTTPS)
✅ Port 6443  - Kubernetes API Server
✅ Port 8080  - Additional service
✅ Port 8443  - Additional service  
✅ Port 10250 - Kubelet API
```

---

## 🚀 איך להתחבר עם K9s

### אפשרות 1: הורד Kubeconfig מה-Dashboard (מומלץ!)

1. **פתח את הדפדפן:**
   ```powershell
   Start-Process "https://10.10.100.102/"
   ```

2. **התחבר ל-Dashboard**

3. **הורד את ה-Kubeconfig:**
   - לחץ על הפרופיל שלך (פינה ימנית עליונה)
   - או: חפש "Kubeconfig File" / "Download kubeconfig"
   - שמור את הקובץ

4. **שים את הקובץ במקום הנכון:**
   ```powershell
   # גבה את ה-config הישן
   Copy-Item "$env:USERPROFILE\.kube\config" "$env:USERPROFILE\.kube\config.old"
   
   # העתק את ה-config החדש
   Copy-Item "C:\Users\roy.avrahami\Downloads\kubeconfig-panda.yaml" "$env:USERPROFILE\.kube\config-panda"
   
   # או החלף לחלוטין
   Copy-Item "C:\Users\roy.avrahami\Downloads\kubeconfig-panda.yaml" "$env:USERPROFILE\.kube\config"
   ```

5. **בדוק שזה עובד:**
   ```powershell
   kubectl config current-context
   kubectl get namespaces
   kubectl get services -n panda
   ```

6. **הרץ K9s:**
   ```powershell
   k9s -n panda
   ```

---

### אפשרות 2: צור Kubeconfig ידנית

אם אין לך אפשרות להוריד מה-Dashboard, תוכל ליצור ידנית:

```powershell
# צור קובץ חדש
$configPath = "$env:USERPROFILE\.kube\config-panda"

@"
apiVersion: v1
kind: Config
clusters:
- cluster:
    server: https://10.10.100.102:6443
    insecure-skip-tls-verify: true
  name: panda-cluster
contexts:
- context:
    cluster: panda-cluster
    user: panda-user
    namespace: panda
  name: panda-context
current-context: panda-context
users:
- name: panda-user
  user:
    token: YOUR_TOKEN_HERE
"@ | Out-File -FilePath $configPath -Encoding UTF8

Write-Host "Config created at: $configPath"
Write-Host "⚠️ You need to add your authentication token!"
```

**לקבל token:**
1. פתח את ה-Dashboard UI
2. חפש את ה-token בהגדרות המשתמש
3. או: שאל את המנהל על Service Account token

---

### אפשרות 3: שתי Configs במקביל

אם אתה רוצה לשמור את שני ה-clusters:

```powershell
# הגדר משתנה עם שני ה-configs
$env:KUBECONFIG = "C:\Users\roy.avrahami\.kube\config;C:\Users\roy.avrahami\.kube\config-panda"

# ראה את כל ה-contexts
kubectl config get-contexts

# עבור ל-context של panda
kubectl config use-context panda-context

# הרץ K9s
k9s -n panda
```

---

## 📊 מה יש ב-namespace panda

לפי המידע שנתת קודם:

### Services:
- **panda-panda-focus-server** (ClusterIP)
  - Port: 5000
  - External: https://10.10.100.100/focus-server/

- **grpc-service-1-343** (NodePort)
  - Port: 12301

- **mongodb** (LoadBalancer)
  - External IP: 10.10.100.108:27017

- **rabbitmq-panda** (LoadBalancer)
  - External IP: 10.10.100.107:5672, 15672

- **rabbitmq-panda-headless** (ClusterIP None)
  - Headless service for RabbitMQ

---

## 🔧 פקודות שימושיות

### בדוק חיבור ל-cluster החדש:
```powershell
# בדוק API server
kubectl --server=https://10.10.100.102:6443 --insecure-skip-tls-verify=true version
```

### אחרי שיש לך kubeconfig:
```powershell
# ראה namespaces
kubectl get namespaces

# ראה services ב-panda
kubectl get services -n panda

# ראה pods ב-panda
kubectl get pods -n panda

# ראה deployments ב-panda
kubectl get deployments -n panda
```

### K9s commands:
```powershell
# פתח K9s ב-namespace panda
k9s -n panda

# פתח K9s עם כל ה-namespaces
k9s -A

# פתח K9s עם context ספציפי
k9s --context panda-context
```

---

## 🎮 K9s קיצורי מקלדת (בתוך K9s)

| Key | Action |
|-----|--------|
| **:ns** | Namespaces |
| **:svc** | Services |
| **:pod** | Pods |
| **:deploy** | Deployments |
| **:ing** | Ingress |
| **/** | סינון |
| **l** | Logs |
| **d** | Describe |
| **e** | Edit |
| **y** | YAML |
| **?** | Help |
| **0** | Show all namespaces |

---

## 📝 שלבים מהירים

### 1️⃣ התקן K9s (אם עדיין לא)
```powershell
choco install k9s
```

### 2️⃣ פתח את Dashboard ב-דפדפן
```powershell
Start-Process "https://10.10.100.102/"
```

### 3️⃣ הורד Kubeconfig
- מהדשבורד, הורד את ה-kubeconfig file
- שמור אותו ב: `C:\Users\roy.avrahami\.kube\config-panda`

### 4️⃣ השתמש בו
```powershell
# החלף את ה-config הנוכחי
$env:KUBECONFIG = "$env:USERPROFILE\.kube\config-panda"

# או שמור את שניהם
$env:KUBECONFIG = "$env:USERPROFILE\.kube\config;$env:USERPROFILE\.kube\config-panda"

# בדוק
kubectl get namespaces

# הרץ K9s
k9s -n panda
```

---

## 🆚 ההבדל בין שני ה-Clusters

### Cluster 1 (הישן): 10.10.10.151:6443
```
Namespaces:
- rabbitmq
- webapp
- map-server
- postgres
- monitoring
```

### Cluster 2 (החדש): 10.10.100.102:6443
```
Namespaces:
- panda ✅ (זה מה שאנחנו צריכים!)
  └── Services:
      ├── panda-panda-focus-server
      ├── grpc-service-1-343
      ├── mongodb (LoadBalancer → 10.10.100.108)
      └── rabbitmq-panda (LoadBalancer → 10.10.100.107)
```

---

## ⚠️ חשוב!

**אתה מחובר כרגע ל-cluster הלא נכון!**

- **Current:** `10.10.10.151:6443` (אין namespace panda)
- **צריך:** `10.10.100.102:6443` (יש namespace panda)

**פתרון:**
1. הורד kubeconfig חדש מ-Dashboard ב-`https://10.10.100.102/`
2. החלף את `~/.kube/config`
3. הרץ `k9s -n panda`

---

## 📞 קיצור דרך

```
┌─────────────────────────────────────────────────┐
│   K9s - הכתובת הנכונה                            │
├─────────────────────────────────────────────────┤
│                                                  │
│  ❌ WRONG: 10.10.10.151:6443 (אין panda)        │
│  ✅ RIGHT: 10.10.100.102:6443 (יש panda!)       │
│                                                  │
│  Dashboard: https://10.10.100.102/              │
│  Namespace: panda                               │
│                                                  │
│  Steps:                                         │
│  1. Open: https://10.10.100.102/               │
│  2. Download kubeconfig                         │
│  3. Save to: ~/.kube/config-panda               │
│  4. Run: k9s -n panda                           │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

**Last Updated:** October 16, 2025  
**Status:** ✅ הכתובת הנכונה התגלתה!

