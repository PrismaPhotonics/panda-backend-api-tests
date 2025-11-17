# 🔑 קבלת Kubeconfig דרך SSH

**תאריך:** 19 אוקטובר 2025  
**שרת:** `prisma@10.10.10.150`  
**סטטוס:** ✅ **יש לך גישה SSH!**

---

## 🎯 עכשיו אפשר להעתיק את ה-Kubeconfig!

אתה מחובר ל-`10.10.10.150` דרך SSH - זה מושלם!

---

## 🚀 שלבים להעתקת Kubeconfig

### שלב 1: מצא את ה-Kubeconfig על השרת

**בתוך SSH (על השרver), הרץ:**

```bash
# בדוק אם יש kubeconfig ב-home directory
ls -la ~/.kube/config

# או בדוק אם זה K3s
ls -la /etc/rancher/k3s/k3s.yaml

# או בדוק כ-root
sudo ls -la /root/.kube/config
```

**תראה משהו כזה:**
```
-rw------- 1 prisma prisma 6234 Oct 16 10:30 /home/prisma/.kube/config
```

---

### שלב 2: הצג את התוכן

```bash
# הצג את ה-kubeconfig
cat ~/.kube/config

# או אם זה K3s
sudo cat /etc/rancher/k3s/k3s.yaml
```

**תראה משהו כזה:**
```yaml
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: LS0tLS...
    server: https://10.10.100.102:6443
  name: default
contexts:
- context:
    cluster: default
    user: default
  name: default
current-context: default
...
```

---

### שלב 3: העתק את הקובץ למחשב שלך

#### אפשרות 1: SCP (מומלץ!)

**צא מה-SSH (Ctrl+D או `exit`)**, ואז במחשב שלך:

```powershell
# העתק את הקובץ
scp prisma@10.10.10.150:~/.kube/config C:\Users\roy.avrahami\.kube\config-panda

# או אם זה K3s
scp prisma@10.10.10.150:/etc/rancher/k3s/k3s.yaml C:\Users\roy.avrahami\.kube\config-panda
```

**אם צריך sudo:**
```powershell
# תחילה על השרת, העתק לתיקיה נגישה
# בתוך SSH:
sudo cp /etc/rancher/k3s/k3s.yaml ~/k3s-config.yaml
sudo chown prisma:prisma ~/k3s-config.yaml

# עכשיו במחשב שלך:
scp prisma@10.10.10.150:~/k3s-config.yaml C:\Users\roy.avrahami\.kube\config-panda
```

#### אפשרות 2: העתק-הדבק ידני

1. **בתוך SSH, על השרת:**
   ```bash
   cat ~/.kube/config
   # או
   sudo cat /etc/rancher/k3s/k3s.yaml
   ```

2. **העתק את כל הפלט**

3. **במחשב שלך:**
   ```powershell
   notepad C:\Users\roy.avrahami\.kube\config-panda
   ```

4. **הדבק את התוכן ושמור**

---

### שלב 4: תקן את כתובת השרת בקובץ

⚠️ **חשוב!** לעיתים הקובץ מכיל `server: https://127.0.0.1:6443`

**צריך לשנות ל:**
```yaml
server: https://10.10.100.102:6443
```

**עריכה:**
```powershell
# פתח את הקובץ
notepad C:\Users\roy.avrahami\.kube\config-panda

# חפש את השורה:
    server: https://127.0.0.1:6443
    
# שנה ל:
    server: https://10.10.100.102:6443
    
# שמור (Ctrl+S)
```

---

### שלב 5: בדוק שזה עובד!

```powershell
# הגדר את ה-kubeconfig
$env:KUBECONFIG = "C:\Users\roy.avrahami\.kube\config-panda"

# בדוק חיבור
kubectl config current-context

# בדוק cluster
kubectl cluster-info

# רשימת namespaces - אמור לראות "panda"!
kubectl get namespaces
```

**אמור לראות:**
```
NAME              STATUS   AGE
panda             Active   20d
kube-system       Active   460d
default           Active   460d
...
```

---

## 🎮 אחרי שיש Kubeconfig - התקן K9s

### הורדה ידנית של K9s

```powershell
# צור תיקייה זמנית
New-Item -ItemType Directory -Path "$env:TEMP\k9s" -Force

# הורד (דרך דפדפן)
Start-Process "https://github.com/derailed/k9s/releases/latest"

# חפש: k9s_Windows_amd64.tar.gz או k9s_Windows_amd64.zip
# הורד והוצא
```

**או דרך PowerShell:**
```powershell
# הורד את הגרסה האחרונה
$version = "v0.32.4"
$url = "https://github.com/derailed/k9s/releases/download/$version/k9s_Windows_amd64.zip"
$output = "$env:TEMP\k9s.zip"

Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing

# חלץ
Expand-Archive -Path $output -DestinationPath "$env:TEMP\k9s" -Force

# העבר ל-PATH
Move-Item "$env:TEMP\k9s\k9s.exe" "$env:LOCALAPPDATA\Microsoft\WindowsApps\k9s.exe" -Force

# בדוק
k9s version
```

---

## 🚀 הרץ K9s!

```powershell
# הגדר kubeconfig
$env:KUBECONFIG = "C:\Users\roy.avrahami\.kube\config-panda"

# הרץ K9s עם namespace panda
k9s -n panda
```

---

## 🔍 בדיקות על השרת (אופציונלי)

אם אתה רוצה לבדוק דברים על השרת עצמו:

```bash
# בדוק אם kubectl מותקן
which kubectl
kubectl version

# בדוק clusters
kubectl config get-contexts

# בדוק namespaces
kubectl get namespaces

# בדוק services ב-panda
kubectl get services -n panda

# בדוק pods ב-panda
kubectl get pods -n panda

# אם K9s מותקן על השרת
k9s -n panda
```

---

## 📝 סיכום פקודות מהיר

### במחשב שלך (Windows):

```powershell
# 1. העתק kubeconfig מהשרת
scp prisma@10.10.10.150:~/.kube/config C:\Users\roy.avrahami\.kube\config-panda

# 2. תקן את כתובת השרת (אם צריך)
notepad C:\Users\roy.avrahami\.kube\config-panda
# שנה: server: https://127.0.0.1:6443
# ל:    server: https://10.10.100.102:6443

# 3. הגדר משתנה סביבה
$env:KUBECONFIG = "C:\Users\roy.avrahami\.kube\config-panda"

# 4. בדוק
kubectl get namespaces

# 5. הרץ K9s (אחרי התקנה)
k9s -n panda
```

---

## 💡 טיפים

### שמור את הסיסמה ב-SSH Config

במקום להקליד סיסמה כל פעם, צור SSH key:

```powershell
# צור SSH key
ssh-keygen -t rsa -b 4096

# העתק ל-server
cat ~/.ssh/id_rsa.pub | ssh prisma@10.10.10.150 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

### שימוש ב-PSCP (אם SCP לא עובד)

```powershell
# הורד PuTTY/PSCP
# ואז:
pscp prisma@10.10.10.150:~/.kube/config C:\Users\roy.avrahami\.kube\config-panda
```

---

## ⚠️ אבטחה

**חשוב:**
- Kubeconfig מכיל אישורים רגישים!
- אל תשתף את הקובץ
- שמור הרשאות: `chmod 600 ~/.kube/config`

---

## 📞 תזכורת

```
┌─────────────────────────────────────────────────────────┐
│  מה יש לך עכשיו:                                        │
│                                                          │
│  ✅ SSH access: prisma@10.10.10.150                     │
│  ✅ שרת: workernode (Ubuntu 20.04)                      │
│                                                          │
│  מה לעשות:                                               │
│  1. העתק kubeconfig מהשרת (SCP או copy-paste)          │
│  2. שמור ב: ~/.kube/config-panda                        │
│  3. תקן server address אם צריך                          │
│  4. בדוק: kubectl get namespaces                        │
│  5. התקן K9s                                            │
│  6. הרץ: k9s -n panda                                   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

**עודכן:** 19 אוקטובר 2025  
**סטטוס:** ✅ יש גישת SSH - מוכן להעתקה!

