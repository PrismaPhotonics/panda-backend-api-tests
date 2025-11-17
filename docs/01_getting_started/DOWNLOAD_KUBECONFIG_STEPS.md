# 📥 איך להוריד Kubeconfig מה-Dashboard

**תאריך:** 16 אוקטובר 2025  
**Dashboard:** https://10.10.100.102/

---

## ⚠️ הבעיה שיש לך עכשיו

```powershell
PS> $env:KUBECONFIG = "C:\Users\roy.avrahami\.kube\config-panda"
PS> kubectl get namespaces

❌ Error: Unable to connect to the server: dial tcp [::1]:8080
```

**למה?** כי הקובץ `config-panda` **לא קיים**!

---

## ✅ הפתרון: הורד Kubeconfig מה-Dashboard

### שלב 1: פתח את ה-Dashboard

```
https://10.10.100.102/
```

(כבר פתוח בדפדפן שלך!)

### שלב 2: חפש את כפתור הורדת Kubeconfig

**אפשרויות לפי סוג Dashboard:**

#### אם זה **Rancher**:
1. לחץ על שם המשתמש שלך (פינה ימנית עליונה)
2. לחץ **"API & Keys"** או **"Kubeconfig"**
3. לחץ **"Download KubeConfig"**

#### אם זה **Kubernetes Dashboard** רגיל:
1. לחץ על הסימן שלוש נקודות (⋮) או ההגדרות
2. חפש **"Kubeconfig"**
3. העתק את התוכן

#### אם זה **OpenLens** או **Lens**:
1. לחץ על ה-cluster
2. חפש **"Settings"** או **"Access"**
3. לחץ **"Download Kubeconfig"**

### שלב 3: שמור את הקובץ

```powershell
# שמור את הקובץ שהורדת לכאן:
C:\Users\roy.avrahami\.kube\config-panda
```

או אם הוא התקבל כטקסט:
```powershell
# פתח נוטפד והדבק את התוכן
notepad C:\Users\roy.avrahami\.kube\config-panda
```

### שלב 4: בדוק שהקובץ קיים

```powershell
Get-Item C:\Users\roy.avrahami\.kube\config-panda
```

אמור לראות את הקובץ והגודל שלו.

---

## 🔧 לאחר שיש לך את הקובץ

### 1. הגדר את המשתנה

```powershell
$env:KUBECONFIG = "C:\Users\roy.avrahami\.kube\config-panda"
```

### 2. בדוק חיבור

```powershell
kubectl config current-context
kubectl get namespaces
```

אמור לראות את namespace **"panda"**! ✅

### 3. הרץ kubectl

```powershell
# ראה services ב-panda namespace
kubectl get services -n panda

# ראה pods
kubectl get pods -n panda

# ראה deployments
kubectl get deployments -n panda
```

---

## 📦 התקנת K9s (אחר כך)

### אפשרות 1: הורדה ידנית

1. **לך ל:**
   ```
   https://github.com/derailed/k9s/releases
   ```

2. **הורד:**
   - חפש את הגרסה האחרונה (למשל `v0.32.4`)
   - הורד: `k9s_Windows_amd64.zip` או `k9s_Windows_amd64.tar.gz`

3. **חלץ:**
   - חלץ את `k9s.exe`

4. **העבר לתיקייה ב-PATH:**
   ```powershell
   Move-Item k9s.exe C:\Windows\System32\k9s.exe
   ```
   
   או:
   ```powershell
   Move-Item k9s.exe "$env:LOCALAPPDATA\Microsoft\WindowsApps\k9s.exe"
   ```

5. **בדוק:**
   ```powershell
   k9s version
   ```

### אפשרות 2: Scoop (אם יש לך)

```powershell
scoop install k9s
```

### אפשרות 3: Chocolatey (אם יש לך)

```powershell
choco install k9s -y
```

---

## 🚀 אחרי שיש K9s + Kubeconfig

```powershell
# הגדר kubeconfig
$env:KUBECONFIG = "C:\Users\roy.avrahami\.kube\config-panda"

# הרץ K9s
k9s -n panda
```

---

## 🔍 אם אתה לא מצליח למצוא את כפתור ההורדה

### צור Kubeconfig ידנית (אם אין אפשרות להוריד)

אם אין אפשרות להוריד מה-UI, אפשר ליצור בצורה בסיסית:

```powershell
$kubeconfig = @"
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
    namespace: panda
    user: panda-user
  name: panda-context
current-context: panda-context
users:
- name: panda-user
  user:
    token: YOUR_TOKEN_HERE
"@

$kubeconfig | Out-File -FilePath "$env:USERPROFILE\.kube\config-panda" -Encoding UTF8

Write-Host "✅ Kubeconfig created (you need to add token!)"
```

**אבל צריך להוסיף Token!**

כדי לקבל token:
1. פתח את ה-Dashboard
2. חפש "Service Account" או "Token"
3. או שאל את מנהל המערכת

---

## 💡 טיפ: שני Configs במקביל

אם אתה רוצה לשמור את שני ה-clusters:

```powershell
# הגדר שני configs
$env:KUBECONFIG = "C:\Users\roy.avrahami\.kube\config;C:\Users\roy.avrahami\.kube\config-panda"

# ראה את כל ה-contexts
kubectl config get-contexts

# עבור בין contexts
kubectl config use-context default          # Cluster הישן
kubectl config use-context panda-context    # Cluster החדש

# הרץ K9s עם context ספציפי
k9s --context panda-context
```

---

## ❓ עזרה נוספת

### בדוק איזה cluster אתה מחובר

```powershell
kubectl cluster-info
```

### בדוק את ה-config הנוכחי

```powershell
kubectl config view
```

### בדוק את ה-context הנוכחי

```powershell
kubectl config current-context
```

---

## 📞 סיכום מהיר

```
┌─────────────────────────────────────────────────────┐
│  מה חסר לך עכשיו:                                   │
│                                                      │
│  1. ❌ Kubeconfig file (config-panda)                │
│     → פתרון: הורד מ-Dashboard                        │
│     → מקום: https://10.10.100.102/                  │
│                                                      │
│  2. ❌ K9s לא מותקן                                  │
│     → פתרון: הורד מ-GitHub או Scoop                  │
│     → קישור: github.com/derailed/k9s/releases       │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

**עודכן:** 16 אוקטובר 2025  
**סטטוס:** ⚠️ ממתין לקובץ kubeconfig

