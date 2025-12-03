# 🔧 מה Kubernetes MCP צריך כדי לעבוד

**תאריך:** 2025-12-02  
**מטרה:** הסבר מפורט על כל מה ש-Kubernetes MCP צריך כדי לעבוד

---

## 📋 דרישות בסיסיות

### 1. **kubectl מותקן ומוגדר** ✅

Kubernetes MCP משתמש ב-`kubectl` כדי לתקשר עם ה-cluster. הוא לא צריך credentials ישירות - הוא משתמש ב-kubectl שלך.

**בדיקה:**
```bash
kubectl version --client
```

**מיקום ברירת מחדל:**
- השרת מחפש את `kubectl` ב-PATH של המערכת
- אם `kubectl` לא נמצא, השרת לא יעבוד

---

### 2. **kubeconfig קובץ** ✅

השרת צריך גישה לקובץ kubeconfig שמכיל את כל המידע על ה-cluster:
- Cluster endpoint (API server URL)
- Certificates (CA certificate)
- User credentials (tokens, certificates, או username/password)
- Contexts (איזה cluster ו-user להשתמש)

**מיקום ברירת מחדל:**
- **Windows:** `C:\Users\<USERNAME>\.kube\config`
- **Mac/Linux:** `~/.kube/config`

**איך השרת מוצא את ה-kubeconfig:**
1. אם יש משתנה סביבה `KUBECONFIG` - משתמש בו
2. אחרת - משתמש במיקום ברירת המחדל (`~/.kube/config`)

**בדיקה:**
```bash
# בדוק אם קובץ קיים
ls ~/.kube/config  # Mac/Linux
dir %USERPROFILE%\.kube\config  # Windows

# בדוק את התוכן
kubectl config view
```

---

### 3. **גישה ל-Kubernetes Cluster** ⚠️

השרת צריך להיות מסוגל להתחבר ל-cluster. זה אומר:
- ה-cluster צריך להיות פעיל
- ה-network צריך לאפשר חיבור ל-API server
- ה-credentials ב-kubeconfig צריכים להיות תקפים

**בדיקה:**
```bash
kubectl get nodes
kubectl cluster-info
```

**אם יש בעיית חיבור:**
- בדוק שה-cluster פעיל
- בדוק שה-network מאפשר חיבור
- בדוק שה-credentials תקפים

---

## 🔧 הגדרות אופציונליות

### משתנה סביבה KUBECONFIG

אם יש לך מספר kubeconfig files או שאתה צריך להגדיר path ספציפי:

```json
{
  "mcpServers": {
    "kubernetes": {
      "command": "npx",
      "args": ["-y", "mcp-server-kubernetes"],
      "env": {
        "KUBECONFIG": "C:\\Users\\roy.avrahami\\.kube\\config"
      }
    }
  }
}
```

**מתי צריך את זה:**
- יש לך מספר kubeconfig files
- ה-kubeconfig לא במיקום ברירת המחדל
- אתה רוצה להשתמש ב-kubeconfig ספציפי

**דוגמה למספר kubeconfig files:**
```json
"env": {
  "KUBECONFIG": "C:\\path\\to\\config1:C:\\path\\to\\config2"
}
```

---

### מצב Non-Destructive (קריאה בלבד)

אם אתה רוצה להגביל את השרת לפעולות קריאה בלבד:

```json
{
  "mcpServers": {
    "kubernetes-readonly": {
      "command": "npx",
      "args": ["-y", "mcp-server-kubernetes"],
      "env": {
        "ALLOW_ONLY_NON_DESTRUCTIVE_TOOLS": "true"
      }
    }
  }
}
```

**מה זה עושה:**
- מאפשר פעולות קריאה (get, describe, logs)
- מאפשר יצירה ועדכון (create, apply, scale)
- חוסם פעולות הרסניות (delete, uninstall)

---

## 📊 מה השרת לא צריך

### ❌ לא צריך:
- **API Keys** - השרת משתמש ב-kubectl שלך
- **Tokens ישירים** - הכל דרך kubeconfig
- **Credentials נפרדים** - הכל דרך kubectl
- **הגדרות נוספות** - ברירת המחדל מספיקה ברוב המקרים

---

## ✅ בדיקת תקינות

### שלב 1: בדוק ש-kubectl עובד
```bash
kubectl version --client
kubectl config current-context
```

### שלב 2: בדוק ש-kubeconfig קיים
```bash
kubectl config view
```

### שלב 3: בדוק חיבור ל-cluster
```bash
kubectl get nodes
kubectl cluster-info
```

### שלב 4: בדוק שהשרת נטען ב-Cursor
1. פתח Cursor Settings (Ctrl+,)
2. חפש "MCP" או "Model Context Protocol"
3. ודא ש-"kubernetes" מופיע ברשימה
4. ודא שהסטטוס הוא "Connected" או "Running"

---

## 🔍 פתרון בעיות

### בעיה: "Unable to connect to Kubernetes cluster"

**סיבות אפשריות:**
1. ה-cluster לא פעיל
2. ה-network לא מאפשר חיבור
3. ה-credentials ב-kubeconfig לא תקפים
4. ה-kubeconfig לא נמצא

**פתרונות:**
```bash
# בדוק חיבור
kubectl get nodes

# בדוק את ה-kubeconfig
kubectl config view

# בדוק context נוכחי
kubectl config current-context

# נסה context אחר
kubectl config use-context <context-name>
```

### בעיה: השרת לא נטען ב-Cursor

**סיבות אפשריות:**
1. kubectl לא מותקן או לא ב-PATH
2. Node.js לא מותקן
3. שגיאה בקובץ mcp.json

**פתרונות:**
```bash
# בדוק ש-kubectl מותקן
kubectl version --client

# בדוק ש-Node.js מותקן
node --version

# בדוק את הקובץ mcp.json
# ודא שהפורמט JSON תקין
```

---

## 📝 סיכום

**מה Kubernetes MCP צריך:**
1. ✅ **kubectl** מותקן ומוגדר
2. ✅ **kubeconfig** קובץ עם credentials תקפים
3. ✅ **גישה ל-cluster** (network + cluster פעיל)
4. ⚙️ **אופציונלי:** משתנה סביבה `KUBECONFIG` אם צריך path ספציפי

**מה הוא לא צריך:**
- ❌ API Keys
- ❌ Tokens ישירים
- ❌ הגדרות נוספות (ברוב המקרים)

**הכל עובד דרך kubectl שלך!**

---

**עודכן לאחרונה:** 2025-12-02

