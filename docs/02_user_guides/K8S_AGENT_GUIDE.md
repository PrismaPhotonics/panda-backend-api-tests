# Kubernetes Agent - User Guide
================================

**תאריך:** 2025-11-09  
**גרסה:** 1.0  
**מטרה:** מדריך שימוש מלא ל-Kubernetes Agent לניהול סביבות K8s

---

## 📋 תוכן עניינים

1. [הקדמה](#הקדמה)
2. [התקנה והגדרה](#התקנה-והגדרה)
3. [הפעלה](#הפעלה)
4. [פקודות זמינות](#פקודות-זמינות)
5. [דוגמאות שימוש](#דוגמאות-שימוש)
6. [טיפים ואזהרות](#טיפים-ואזהרות)

---

## 🎯 הקדמה

**Kubernetes Agent** הוא כלי אינטראקטיבי לניהול סביבות Kubernetes (staging ו-production/kefar saba).

### תכונות עיקריות:

- ✅ **תמיכה בשתי סביבות**: staging ו-production (kefar saba)
- ✅ **ניטור מלא**: pods, jobs, deployments, cluster info
- ✅ **מחיקה בטוחה**: אישור לפני כל פעולה הרסנית
- ✅ **ניהול קונפיגורציה**: שינוי סביבה דינמי
- ✅ **תמיכה ב-SSH fallback**: עבודה גם ללא גישה ישירה ל-K8s API

---

## 🚀 התקנה והגדרה

### דרישות מוקדמות:

1. **Python 3.8+** מותקן
2. **תלויות הפרויקט** מותקנות:
   ```bash
   pip install -r requirements.txt
   ```

3. **קונפיגורציה** מוגדרת ב-`config/environments.yaml`:
   - סביבת staging
   - סביבת production

### אין צורך בהתקנה נוספת!

הכלי משתמש בתשתית הקיימת של הפרויקט.

---

## 🎮 הפעלה

### הפעלה בסיסית:

```bash
# הפעלה עם סביבת staging (ברירת מחדל)
python scripts/k8s_agent.py

# הפעלה עם סביבת production
python scripts/k8s_agent.py --env production

# או
python scripts/k8s_agent.py --environment staging
```

### תפריט ראשי:

לאחר ההפעלה, תראה תפריט אינטראקטיבי:

```
================================================================================
  Kubernetes Agent - Staging (10.10.10.100)
================================================================================

📊 Monitoring Commands:
  1.  List all pods
  2.  List gRPC job pods
  3.  List all jobs
  4.  List deployments
  5.  Show cluster info
  6.  Get pod logs
  7.  Get pod details

🗑️  Deletion Commands (with confirmation):
  8.  Delete pod (by name)
  9.  Delete gRPC job pods (all)
  10. Delete gRPC job pods (by pattern)
  11. Delete job (by name)
  12. Delete multiple pods (by pattern)

⚙️  Management Commands:
  13. Restart pod (delete and recreate)
  14. Scale deployment
  15. Switch environment
  16. Reconnect

  0.  Exit
--------------------------------------------------------------------------------
```

---

## 📊 פקודות זמינות

### 📊 פקודות ניטור

#### 1. List all pods
רשימת כל ה-pods בקלאסטר.

**דוגמה:**
```
Enter command number: 1

📦 Found 15 pod(s):
----------------------------------------------------------------------------------------------------
NAME                                                  STATUS          READY       RESTARTS   NODE
----------------------------------------------------------------------------------------------------
panda-panda-focus-server-7d8f9c4b5-abc12             Running         True        0          node-1
grpc-service-12-70788-xyz                           Running         True        0          node-2
mongodb-0                                            Running         True        0          node-1
...
```

#### 2. List gRPC job pods
רשימת pods של gRPC jobs בלבד.

**דוגמה:**
```
Enter command number: 2

📦 Found 5 pod(s):
----------------------------------------------------------------------------------------------------
NAME                                                  STATUS          READY       RESTARTS   NODE
----------------------------------------------------------------------------------------------------
grpc-service-12-70788-xyz                           Running         True        0          node-2
grpc-service-13-70789-abc                           Running         True        0          node-2
...
```

#### 3. List all jobs
רשימת כל ה-Kubernetes jobs.

#### 4. List deployments
רשימת כל ה-deployments בקלאסטר.

#### 5. Show cluster info
הצגת מידע על הקלאסטר (גרסה, nodes, וכו').

**דוגמה:**
```
Enter command number: 5

📊 Cluster Information:
------------------------------------------------------------
Version: v1.28.0
Node Count: 3

Nodes:
  - node-1: Ready (master)
  - node-2: Ready (worker)
  - node-3: Ready (worker)
```

#### 6. Get pod logs
קבלת לוגים של pod ספציפי.

**דוגמה:**
```
Enter command number: 6
Enter pod name: grpc-service-12-70788-xyz
Number of lines (default 100): 50

📄 Logs from pod 'grpc-service-12-70788-xyz':
--------------------------------------------------------------------------------
2025-11-09 10:30:15 INFO Starting gRPC service...
2025-11-09 10:30:16 INFO Connected to MongoDB
...
```

#### 7. Get pod details
הצגת פרטים מלאים על pod ספציפי.

---

### 🗑️ פקודות מחיקה (עם אישור)

**⚠️ חשוב:** כל פעולות המחיקה דורשות אישור מפורש!

#### 8. Delete pod (by name)
מחיקת pod ספציפי לפי שם.

**דוגמה:**
```
Enter command number: 8
Enter pod name to delete: grpc-service-12-70788-xyz

📦 Pod Information:
   Name: grpc-service-12-70788-xyz
   Status: Running
   Ready: True
   Node: node-2

⚠️  Are you sure you want to delete pod grpc-service-12-70788-xyz? (yes/no): yes
✅ Pod 'grpc-service-12-70788-xyz' deleted successfully
```

#### 9. Delete gRPC job pods (all)
מחיקת כל ה-gRPC job pods.

**דוגמה:**
```
Enter command number: 9

📦 Found 5 pod(s):
...
📦 Pods to be deleted (5):
   - grpc-service-12-70788-xyz (Status: Running)
   - grpc-service-13-70789-abc (Status: Running)
   ...

⚠️  Are you sure you want to delete 5 gRPC job pod(s)? (yes/no): yes
✅ Deleted pod: grpc-service-12-70788-xyz
✅ Deleted pod: grpc-service-13-70789-abc
...

📊 Summary: 5 deleted, 0 failed
```

#### 10. Delete gRPC job pods (by pattern)
מחיקת gRPC job pods לפי pattern.

**דוגמה:**
```
Enter command number: 10
Enter pattern to filter pod names: 12-70788

📦 Found 1 pod(s) matching pattern:
   - grpc-service-12-70788-xyz (Status: Running)

⚠️  Are you sure you want to delete 1 gRPC job pod(s)? (yes/no): yes
✅ Deleted pod: grpc-service-12-70788-xyz
```

#### 11. Delete job (by name)
מחיקת Kubernetes job ספציפי.

#### 12. Delete multiple pods (by pattern)
מחיקת pods מרובים לפי pattern.

---

### ⚙️ פקודות ניהול

#### 13. Restart pod
הפעלה מחדש של pod (מחיקה ויצירה מחדש).

**דוגמה:**
```
Enter command number: 13
Enter pod name to restart: grpc-service-12-70788-xyz

⚠️  Are you sure you want to restart pod grpc-service-12-70788-xyz? (yes/no): yes
✅ Pod 'grpc-service-12-70788-xyz' restarted successfully
```

#### 14. Scale deployment
שינוי מספר ה-replicas של deployment.

**דוגמה:**
```
Enter command number: 14
Enter deployment name: panda-panda-focus-server
Enter number of replicas: 3

⚠️  Are you sure you want to scale deployment 'panda-panda-focus-server' to 3 replicas? (yes/no): yes
✅ Deployment 'panda-panda-focus-server' scaled to 3 replicas
```

#### 15. Switch environment
החלפת סביבה (staging ↔ production).

**דוגמה:**
```
Enter command number: 15

Available environments:
  1. staging
  2. production
Select environment (1 or 2): 2

🔌 Connecting to Production - Kefar Saba (10.10.100.100)...
✅ Connected successfully!
   Cluster Version: v1.28.0
   Nodes: 3
```

#### 16. Reconnect
התחברות מחדש לקלאסטר.

---

## 💡 דוגמאות שימוש

### דוגמה 1: ניקוי gRPC jobs בסביבת staging

```bash
# הפעלת הכלי
python scripts/k8s_agent.py --env staging

# בתפריט:
# 1. בחר 2 (List gRPC job pods) - לבדיקה
# 2. בחר 9 (Delete gRPC job pods) - למחיקה
# 3. אישר את המחיקה
```

### דוגמה 2: בדיקת pod ספציפי

```bash
# בתפריט:
# 1. בחר 7 (Get pod details)
# 2. הזן שם pod
# 3. בחר 6 (Get pod logs) לבדיקת לוגים
```

### דוגמה 3: ניהול deployment

```bash
# בתפריט:
# 1. בחר 4 (List deployments) - לראות deployments
# 2. בחר 14 (Scale deployment) - לשנות מספר replicas
```

### דוגמה 4: מעבר בין סביבות

```bash
# התחלה בסביבת staging
python scripts/k8s_agent.py --env staging

# בתפריט:
# 1. בחר 15 (Switch environment)
# 2. בחר 2 (production)
# 3. הכלי יתחבר לסביבת production
```

---

## ⚠️ טיפים ואזהרות

### ✅ טיפים:

1. **בדיקה לפני מחיקה**: תמיד השתמש בפקודה 1 או 2 כדי לראות את ה-pods לפני מחיקה
2. **שימוש ב-pattern**: השתמש ב-pattern כדי למחוק pods מרובים בבת אחת
3. **לוגים**: השתמש בפקודה 6 כדי לבדוק לוגים לפני מחיקת pod
4. **סביבות**: ודא שאתה בסביבה הנכונה לפני ביצוע פעולות

### ⚠️ אזהרות:

1. **מחיקה ב-production**: היזהר במיוחד בעת מחיקת pods בסביבת production!
2. **אישור מחיקה**: תמיד קרא את האישור לפני אישור מחיקה
3. **gRPC jobs**: מחיקת gRPC job pods תעצור את העבודה - ודא שזה מה שאתה רוצה
4. **Deployments**: שינוי מספר replicas יכול להשפיע על זמינות השירות

### 🔒 הגנות:

- ✅ כל פעולת מחיקה דורשת אישור מפורש
- ✅ הצגת מידע לפני מחיקה
- ✅ תמיכה ב-SSH fallback (עבודה גם ללא גישה ישירה)
- ✅ בדיקת קיום resource לפני מחיקה

---

## 🐛 פתרון בעיות

### בעיה: "Not connected to cluster"

**פתרון:**
1. בדוק את קונפיגורציית SSH ב-`config/environments.yaml`
2. נסה להשתמש בפקודה 16 (Reconnect)
3. ודא שיש גישה ל-K8s API או SSH

### בעיה: "Failed to get pods"

**פתרון:**
1. בדוק את ה-namespace בקונפיגורציה
2. ודא שיש הרשאות מתאימות
3. נסה להתחבר מחדש (פקודה 16)

### בעיה: "SSH connection failed"

**פתרון:**
1. בדוק את פרטי ה-SSH ב-`config/environments.yaml`
2. ודא שיש גישה ל-jump host ו-target host
3. בדוק את ה-SSH keys אם נדרש

---

## 📚 קישורים נוספים

- [Kubernetes Manager Documentation](../03_architecture/KUBERNETES_MANAGER.md)
- [Environment Configuration](../01_getting_started/ENVIRONMENT_SETUP.md)
- [SSH Manager Documentation](../03_architecture/SSH_MANAGER.md)

---

## 📝 הערות

- הכלי משתמש ב-`KubernetesManager` הקיים של הפרויקט
- תמיכה מלאה ב-SSH fallback עבור סביבות ללא גישה ישירה
- כל הפעולות מתועדות ב-logs

---

**עדכון אחרון:** 2025-11-09  
**מחבר:** Focus Server Automation Team

