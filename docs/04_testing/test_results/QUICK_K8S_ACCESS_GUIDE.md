# מדריך גישה מהירה ל-Kubernetes

## ✅ נתיב הגישה הנוכחי שעובד:

```
[Windows] 
  ↓ SSH
[10.10.10.10 - panda-staging-host] 
  ↓ SSH
[10.10.10.150 - worker-node] 
  ↓ kubectl/k9s
[Kubernetes Cluster]
```

## 🚀 פקודות מהירות:

### 1. התחברות (מהמחשב שלך):

```powershell
ssh root@10.10.10.10
# סיסמה: [הסיסמה שלך]

ssh prisma@10.10.10.150
# עובד ישירות!
```

### 2. מהשרת worker-node (10.10.10.150):

```bash
# בדוק אם kubectl מותקן
kubectl version --client

# בדוק אם k9s מותקן
k9s version

# אם kubectl מותקן - בדוק את הקשר
kubectl get nodes

# אם k9s מותקן - פתח את הכלי הגרפי
k9s

# עבודה עם pods
kubectl get pods -n panda

# עבודה עם deployments
kubectl get deployments -n panda

# עבודה עם services
kubectl get services -n panda
```

### 3. הגדרת kubeconfig (אם נדרש):

```bash
# בדוק אם יש kubeconfig
ls -la ~/.kube/config

# אם אין - הגדר
mkdir -p ~/.kube
# העתק את הconfig מהשרת הראשי או הגדר ידנית
```

## 📋 פקודות שימושיות:

### ניטור:
```bash
# כל הפודים ב-namespace
kubectl get pods -n panda -o wide

# לוגים של פוד ספציפי
kubectl logs <pod-name> -n panda

# describe פוד
kubectl describe pod <pod-name> -n panda

# watch פודים
kubectl get pods -n panda -w
```

### עבודה עם MongoDB:
```bash
# בדוק MongoDB pods
kubectl get pods -n panda | grep mongodb

# בדוק MongoDB service
kubectl get svc -n panda | grep mongodb

# לוגים של MongoDB
kubectl logs -n panda <mongodb-pod-name>
```

### עבודה עם RabbitMQ:
```bash
# בדוק RabbitMQ pods
kubectl get pods -n panda | grep rabbitmq

# בדוק RabbitMQ service
kubectl get svc -n panda | grep rabbitmq
```

### עבודה עם Focus Server:
```bash
# בדוק Focus Server pods
kubectl get pods -n panda | grep focus

# בדוק Focus Server service
kubectl get svc -n panda | grep focus

# לוגים של Focus Server
kubectl logs -n panda <focus-server-pod-name> --tail=100 -f
```

## 🎯 k9s - כלי גרפי (אם מותקן):

```bash
# פתח את k9s
k9s

# בתוך k9s:
# :pod       - רשימת פודים
# :svc       - רשימת שירותים
# :deploy    - רשימת deployments
# :ns        - החלפת namespace
# /<search>  - חיפוש
# q          - יציאה
```

## 📝 סקריפט PowerShell להחלפה מהירה:

```powershell
# scripts/quick-k8s-access.ps1
ssh root@10.10.10.10 -t "ssh prisma@10.10.10.150 -t 'bash -l'"
```

## ✅ מה עובד:

1. ✅ SSH ל-10.10.10.10 (staging-host)
2. ✅ SSH ל-10.10.10.150 (worker-node)
3. ✅ אתה עכשיו ב-worker node

## 🔍 מה לבדוק עכשיו:

1. **kubectl** - `kubectl version --client`
2. **k9s** - `k9s version`
3. **kubeconfig** - `ls -la ~/.kube/config`
4. **גישה ל-cluster** - `kubectl get nodes`

## 💡 טיפים:

1. **השתמש ב-tmux/screen** לשמירה על session:
   ```bash
   tmux new -s k8s
   # או
   screen -S k8s
   ```

2. **alias פשוט** ב-`~/.bashrc`:
   ```bash
   alias k='kubectl'
   alias k9='k9s'
   ```

3. **הגדר KUBECONFIG** אם צריך:
   ```bash
   export KUBECONFIG=~/.kube/config
   ```

---

**זה הנתיב שעובד הכי טוב כרגע!** 🚀
