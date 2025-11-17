# 🔧 K9s Connection Guide - Kubernetes Cluster

**Date:** October 16, 2025  
**Status:** ✅ **Cluster Accessible**

---

## 🎯 התשובה המהירה

**כתובת Kubernetes API Server:**
```
https://10.10.10.151:6443
```

**Kubeconfig Location:**
```
C:\Users\roy.avrahami\.kube\config
```

**Current Context:**
```
default
```

---

## 🚀 איך להתקין ולהריץ K9s

### שלב 1: התקנת K9s

#### באמצעות Chocolatey (מומלץ):
```powershell
choco install k9s
```

#### באמצעות Scoop:
```powershell
scoop install k9s
```

#### הורדה ידנית:
1. לך ל: https://github.com/derailed/k9s/releases
2. הורד את הקובץ המתאים ל-Windows (k9s_Windows_amd64.tar.gz)
3. חלץ את הקובץ
4. העבר את `k9s.exe` לתיקיה ב-PATH (למשל `C:\Windows\System32\`)

---

### שלב 2: הרצת K9s

#### הרצה רגילה (יתחבר לcontext הנוכחי):
```powershell
k9s
```

#### הרצה עם namespace ספציפי:
```powershell
# RabbitMQ namespace
k9s -n rabbitmq

# Webapp namespace
k9s -n webapp

# Map-server namespace
k9s -n map-server

# Monitoring namespace
k9s -n monitoring
```

#### הרצה עם כל ה-namespaces:
```powershell
k9s --all-namespaces
```

או בקיצור:
```powershell
k9s -A
```

---

## 🗺️ Namespaces זמינים ב-Cluster

| Namespace | Age | Purpose |
|-----------|-----|---------|
| **kube-system** | 460 days | Kubernetes system components |
| **default** | 460 days | Default namespace |
| **kube-public** | 460 days | Public resources |
| **kube-node-lease** | 460 days | Node heartbeats |
| **gpu-operator** | 453 days | GPU support |
| **metallb-system** | 437 days | Load balancer (MetalLB) |
| **map-server** | 83 days | Map server application |
| **postgres** | 83 days | PostgreSQL database |
| **rabbitmq** | 83 days | RabbitMQ messaging ✅ |
| **webapp** | 83 days | Web application |
| **monitoring** | 34 days | Monitoring stack |

---

## 🔍 ה-Services שמצאנו - איפה הם?

### אם יש cluster נוסף עם namespace "panda":

ייתכן שיש **cluster נוסף** עם ה-namespace `panda` שבו רצים:
- `panda-panda-focus-server`
- `grpc-service-1-343`
- `mongodb`
- `rabbitmq-panda`

**כדי להתחבר אליו**, צריך:

1. **להוסיף את ה-cluster ל-kubeconfig:**
   ```powershell
   # אם יש לך kubeconfig נוסף
   $env:KUBECONFIG = "C:\Users\roy.avrahami\.kube\config;C:\path\to\panda-cluster-config"
   ```

2. **לראות את כל ה-contexts:**
   ```powershell
   kubectl config get-contexts
   ```

3. **לעבור ל-context של ה-panda cluster:**
   ```powershell
   kubectl config use-context <panda-context-name>
   ```

4. **להריץ K9s:**
   ```powershell
   k9s -n panda
   ```

---

## 📊 Cluster הנוכחי - מידע מלא

### API Server
```
URL:      https://10.10.10.151:6443
Status:   ✅ Running
```

### Cluster Components
```
✅ Kubernetes control plane   - https://10.10.10.151:6443
✅ CoreDNS                     - Running
✅ Metrics-server              - Running
✅ MetalLB (Load Balancer)     - Active
```

### Current Configuration
```
Context:    default
Cluster:    default
User:       default
Namespace:  (default)
```

---

## 🎮 K9s קיצורי מקלדת שימושיים

| Key | Action | תיאור |
|-----|--------|-------|
| **:ns** | Namespaces | רשימת namespaces |
| **:pod** | Pods | רשימת pods |
| **:svc** | Services | רשימת services |
| **:deploy** | Deployments | רשימת deployments |
| **:ing** | Ingress | רשימת ingress |
| **:node** | Nodes | רשימת nodes |
| **0** | Show all namespaces | הצג כל ה-namespaces |
| **/** | Filter | סינון |
| **l** | Logs | לוגים של pod |
| **d** | Describe | מידע מפורט |
| **e** | Edit | עריכה |
| **y** | YAML | הצג YAML |
| **Ctrl+d** | Delete | מחיקה |
| **?** | Help | עזרה |
| **Ctrl+a** | Show all | הצג הכל |

---

## 🔧 בדיקות חיבור

### בדוק חיבור ל-API Server:
```powershell
kubectl cluster-info
```

**Expected output:**
```
Kubernetes control plane is running at https://10.10.10.151:6443
```

### בדוק גישה ל-namespaces:
```powershell
kubectl get namespaces
```

### בדוק services ב-rabbitmq namespace:
```powershell
kubectl get services -n rabbitmq
```

### בדוק pods ב-webapp namespace:
```powershell
kubectl get pods -n webapp
```

---

## 📁 Kubeconfig File Location

**Current kubeconfig:**
```
C:\Users\roy.avrahami\.kube\config
```

### לקרוא את ה-kubeconfig:
```powershell
# Show full config
kubectl config view

# Show current context
kubectl config current-context

# Show clusters
kubectl config get-clusters
```

---

## 🔍 איך למצוא את ה-"panda" namespace?

ה-services שהראית לי מגיעים מ-namespace בשם `panda`, אבל ב-cluster הנוכחי אין namespace כזה.

**אפשרויות:**

### 1. זה cluster אחר
ייתכן שיש cluster נוסף. בדוק:
```powershell
# האם יש קבצי kubeconfig נוספים?
Get-ChildItem -Path "$env:USERPROFILE\.kube\" -Recurse -Filter "*.config" -File

# או
Get-ChildItem -Path "$env:USERPROFILE\.kube\" -Recurse -Filter "config*" -File
```

### 2. זה context אחר באותו kubeconfig
```powershell
# Show all contexts
kubectl config get-contexts

# Try to find panda context
kubectl config get-contexts | Select-String "panda"
```

### 3. ה-UI של Kubernetes שממנו לקחת את המידע

אם המידע על ה-services בא מממשק UI (Rancher/Lens/Dashboard), בדוק שם:
- מה שם ה-cluster
- מה שם ה-context
- האם יש אפשרות להוריד kubeconfig מהממשק

---

## 🚀 התחלה מהירה

### אם K9s מותקן:

```powershell
# הצג את כל ה-namespaces
k9s

# לחץ :ns ו-Enter
# תראה את כל ה-namespaces

# לחץ על rabbitmq ו-Enter
# תראה את כל ה-resources ב-namespace
```

### אם K9s לא מותקן:

```powershell
# התקן עם Chocolatey
choco install k9s

# או עם Scoop
scoop install k9s

# הרץ
k9s
```

---

## 🎯 RabbitMQ שמצאנו - איך לראות אותו ב-K9s

אחרי שK9s פועל:

1. **פתח K9s עם namespace של RabbitMQ:**
   ```powershell
   k9s -n rabbitmq
   ```

2. **בתוך K9s:**
   ```
   :svc        → רשימת Services
   :pod        → רשימת Pods
   :deploy     → רשימת Deployments
   :ing        → רשימת Ingress
   ```

3. **לראות logs של RabbitMQ pod:**
   - לחץ `:pod`
   - בחר את ה-RabbitMQ pod
   - לחץ `l` (logs)

---

## 📝 סיכום מהיר

### מה יש לך עכשיו:

✅ **Kubeconfig:** `C:\Users\roy.avrahami\.kube\config`  
✅ **API Server:** `https://10.10.10.151:6443`  
✅ **Context:** `default`  
✅ **Cluster:** Connected & Working  

### כדי להשתמש ב-K9s:

```powershell
# 1. התקן K9s (אם עדיין לא)
choco install k9s

# 2. הרץ K9s
k9s

# 3. או עם namespace ספציפי
k9s -n rabbitmq
k9s -n webapp
k9s -n monitoring

# 4. או עם כל ה-namespaces
k9s -A
```

---

## 🔍 למצוא את ה-"panda" Cluster

אם אתה צריך את ה-namespace `panda` שממנו באים ה-services האלה:
- `panda-panda-focus-server`
- `mongodb.panda`
- `rabbitmq-panda.panda`

**בדוק:**

1. **ב-UI שממנו לקחת את המידע** (Rancher/Lens/K8s Dashboard):
   - לחץ על Kubeconfig Download
   - שמור את הקובץ
   - העתק אותו ל: `C:\Users\roy.avrahami\.kube\config-panda`

2. **השתמש בו:**
   ```powershell
   $env:KUBECONFIG = "C:\Users\roy.avrahami\.kube\config-panda"
   kubectl get namespaces
   k9s -n panda
   ```

---

## 📞 קיצור דרך

```
┌─────────────────────────────────────────────────┐
│   K9s Quick Start                                │
├─────────────────────────────────────────────────┤
│                                                  │
│  API Server:  10.10.10.151:6443                 │
│  Kubeconfig:  ~/.kube/config                    │
│  Context:     default                           │
│                                                  │
│  Install:     choco install k9s                 │
│  Run:         k9s                               │
│  Namespaces:  k9s -A                            │
│  Specific:    k9s -n rabbitmq                   │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

**Last Updated:** October 16, 2025  
**Status:** ✅ Cluster accessible, K9s ready to install

