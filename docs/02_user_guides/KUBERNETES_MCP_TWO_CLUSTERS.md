# 🔍 בעיית חיבור ל-Kubernetes: שני Clusters שונים

**תאריך:** 2025-12-02  
**בעיה:** יש שני clusters שונים - אחד ב-Windows ואחד ב-Linux

---

## 📊 המצב הנוכחי

### Windows (המחשב המקומי) ❌

**מיקום kubeconfig:**
- `C:\Users\roy.avrahami\.kube\config`

**Cluster:**
- Endpoint: `https://10.10.100.102:6443`
- Status: **לא מגיב** (connection timeout)

**הבעיה:**
```
dial tcp 10.10.100.102:6443: connectex: A connection attempt failed
```

---

### Linux (worker-node) ✅

**מיקום kubeconfig:**
- `/home/prisma/.kube/config` (כנראה)

**Cluster:**
- Endpoint: `https://10.10.10.151:6443`
- Status: **עובד מצוין**
- Nodes: `master-node`, `worker-node`
- Pods: רבים ופעילים

**מה עובד:**
- ✅ `kubectl cluster-info` - עובד
- ✅ `kubectl get nodes` - עובד
- ✅ `kubectl get pods` - עובד

---

## 🔍 הבעיה

יש לך **שני clusters שונים**:
1. **Windows:** `10.10.100.102:6443` - לא פעיל/לא נגיש
2. **Linux:** `10.10.10.151:6443` - פעיל ועובד

ה-kubeconfig ב-Windows מצביע על cluster שלא נגיש מהמחשב שלך.

---

## ✅ פתרונות

### פתרון 1: העתקת kubeconfig מ-Linux ל-Windows (מומלץ)

אם אתה רוצה להשתמש ב-cluster שעובד:

1. **ב-Linux (worker-node):**
   ```bash
   # בדוק את מיקום ה-kubeconfig
   echo $KUBECONFIG
   # או
   ls ~/.kube/config
   
   # הצג את התוכן (ללא credentials רגישים)
   kubectl config view --raw
   ```

2. **העתק את הקובץ ל-Windows:**
   ```bash
   # ב-Linux - שמור את ה-kubeconfig לקובץ
   kubectl config view --raw > ~/kubeconfig-backup.yaml
   
   # העתק ל-Windows (דרך SCP או דרך shared folder)
   # לדוגמה:
   scp prisma@worker-node:~/kubeconfig-backup.yaml C:\Users\roy.avrahami\.kube\config
   ```

3. **ב-Windows - עדכן את הקובץ:**
   ```powershell
   # גבה את הקובץ הישן
   Copy-Item "$env:USERPROFILE\.kube\config" "$env:USERPROFILE\.kube\config.backup"
   
   # העתק את הקובץ החדש
   # (אחרי שהעתקת מ-Linux)
   ```

4. **בדוק:**
   ```powershell
   kubectl config current-context
   kubectl cluster-info
   kubectl get nodes
   ```

---

### פתרון 2: הגדרת KUBECONFIG ב-mcp.json

אם יש לך מספר kubeconfig files, תוכל להגדיר path ספציפי:

```json
{
  "mcpServers": {
    "kubernetes": {
      "command": "npx",
      "args": ["-y", "mcp-server-kubernetes"],
      "env": {
        "KUBECONFIG": "C:\\Users\\roy.avrahami\\.kube\\config-linux"
      }
    }
  }
}
```

---

### פתרון 3: שימוש ב-SSH Tunnel (אם צריך)

אם ה-cluster ב-Linux לא נגיש ישירות מ-Windows, תוכל להשתמש ב-SSH tunnel:

```powershell
# יצירת SSH tunnel
ssh -L 6443:10.10.10.151:6443 prisma@worker-node

# ב-terminal אחר, עדכן את ה-kubeconfig להשתמש ב-localhost
kubectl config set-cluster default --server=https://localhost:6443
```

---

### פתרון 4: עדכון ה-kubeconfig ב-Windows

אם אתה רוצה לעדכן את ה-cluster ב-Windows:

```powershell
# עדכן את ה-cluster endpoint
kubectl config set-cluster default --server=https://10.10.10.151:6443

# או צור context חדש
kubectl config set-cluster linux-cluster --server=https://10.10.10.151:6443
kubectl config set-context linux-context --cluster=linux-cluster --user=default
kubectl config use-context linux-context
```

**⚠️ אבל:** תצטרך גם את ה-certificates וה-credentials מה-Linux cluster.

---

## 🎯 המלצה

**הפתרון הכי פשוט:** העתק את ה-kubeconfig מ-Linux ל-Windows.

**שלבים:**
1. ב-Linux: `kubectl config view --raw > ~/kubeconfig.yaml`
2. העתק את הקובץ ל-Windows
3. ב-Windows: החלף את `C:\Users\roy.avrahami\.kube\config`
4. בדוק: `kubectl get nodes`

---

## 🔍 בדיקות

### ב-Windows (אחרי העתקה):

```powershell
# בדוק context
kubectl config current-context

# בדוק cluster info
kubectl cluster-info

# בדוק nodes
kubectl get nodes

 nodes

# בדוק pods
kubectl get pods --all-namespaces
```

---

## 📝 הערות חשובות

1. **אבטחה:** ה-kubeconfig מכיל credentials רגישים - אל תשתף אותו
2. **גיבוי:** תמיד גבה את ה-kubeconfig הישן לפני החלפה
3. **Network:** ודא שיש חיבור network ל-cluster (אם צריך VPN או SSH tunnel)

---

**עודכן לאחרונה:** 2025-12-02

