# 🚀 מדריך הגדרת Kubernetes MCP Server

**תאריך:** 2025-12-02  
**סטטוס:** ✅ מדריך מלא

---

## 📋 מבוא

**מה זה Kubernetes MCP Server:**
- כלי לניהול משאבי Kubernetes ישירות מ-Cursor
- מאפשר לנהל pods, deployments, services, ו-resources נוספים
- עובד עם כל Kubernetes cluster (local, cloud, או on-premise)

**איך זה עובד:**
- השרת מתחבר ל-Kubernetes cluster שלך דרך `kubectl`
- משתמש ב-kubeconfig שלך לאימות
- מאפשר לבצע פעולות Kubernetes דרך שאלות טבעיות ב-Cursor

---

## 🎯 דרישות מוקדמות

### לפני שמתחילים:

1. ✅ **Kubernetes cluster** פעיל (local או remote)
2. ✅ **kubectl** מותקן ומוגדר
3. ✅ **kubeconfig** מוגדר ומתחבר ל-cluster
4. ✅ **Cursor** מותקן (או כלי MCP תומך אחר)
5. ✅ **Node.js v18+** (להפעלת `npx`)

### בדיקת התקנה:

```bash
# בדוק ש-kubectl מותקן
kubectl version --client

# בדוק ש-kubeconfig מוגדר
kubectl config current-context

# בדוק חיבור ל-cluster
kubectl get nodes
```

---

## 🔧 הגדרה ב-Cursor

### שלב 1: פתיחת קובץ ההגדרות

1. פתח את קובץ ההגדרות של Cursor:
   - **Windows:** `C:\Users\<USERNAME>\.cursor\mcp.json`
   - **Mac/Linux:** `~/.cursor/mcp.json`

2. או פתח את הקובץ ישירות ב-Cursor:
   - לחץ על **File → Open File**
   - נווט ל-`.cursor\mcp.json` בתיקיית הבית שלך

### שלב 2: הוספת הגדרת Kubernetes MCP Server

**הוסף את ההגדרה הבאה לקובץ `mcp.json`:**

```json
{
  "mcpServers": {
    "kubernetes": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-server-kubernetes"
      ],
      "env": {}
    }
  }
}
```

**⚠️ חשוב:** השרת משתמש ב-kubeconfig שלך אוטומטית. ודא ש-`KUBECONFIG` מוגדר או ש-kubeconfig נמצא במיקום ברירת המחדל (`~/.kube/config`).

**דוגמה לקובץ מלא עם שרתים נוספים:**

```json
{
  "mcpServers": {
    "atlassian-rovo": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.atlassian.com/v1/sse"],
      "env": {}
    },
    "kubernetes": {
      "command": "npx",
      "args": ["-y", "mcp-server-kubernetes"],
      "env": {}
    }
  }
}
```

### שלב 3: הגדרת משתני סביבה (אופציונלי)

אם יש לך מספר kubeconfig files או שאתה צריך להגדיר context ספציפי:

```json
{
  "mcpServers": {
    "kubernetes": {
      "command": "npx",
      "args": ["-y", "mcp-server-kubernetes"],
      "env": {
        "KUBECONFIG": "/path/to/your/kubeconfig"
      }
    }
  }
}
```

### שלב 4: שמירה והפעלה מחדש

1. **שמור את הקובץ** (Ctrl+S)
2. **הפעל מחדש את Cursor** (או לחץ על **Reload Window**)
3. Cursor יטען את שרתי MCP החדשים אוטומטית

---

## ✅ אימות שההגדרה עובדת

### בדיקה 1: וידוא שהשרת נטען ב-Cursor

1. **פתח את Cursor Settings** (Ctrl+,)
2. **חפש "MCP"** או **"Model Context Protocol"**
3. **בדוק** ש-**"kubernetes"** מופיע ברשימת שרתי MCP
4. **ודא** שהסטטוס הוא **"Connected"** או **"Running"**

### בדיקה 2: בדיקה דרך Chat ב-Cursor

1. **פתח Chat** ב-Cursor (Ctrl+L)
2. **נסה שאלות** כמו:
   ```
   "List all pods in the default namespace"
   "Show me all deployments"
   "What nodes are in the cluster?"
   "Get logs from pod my-app-123"
   ```
3. **אם זה עובד**, תראה תשובה עם נתונים מ-Kubernetes
4. **אם לא**, תראה הודעת שגיאה (בדוק את הלוגים)

### בדיקה 3: בדיקת לוגים (אם יש בעיות)

1. **פתח את Developer Tools** ב-Cursor (Ctrl+Shift+I)
2. **עבור לטאב "Console"**
3. **חפש הודעות** הקשורות ל-MCP או Kubernetes
4. **אם יש שגיאות**, תראה אותן כאן

---

## 🎨 דוגמאות שימוש

### ניהול Pods:

```
"List all pods in the default namespace"
"Show me pods that are not running"
"Get logs from pod my-app-123"
"Describe pod my-app-123"
"Delete pod my-app-123"
```

### ניהול Deployments:

```
"List all deployments"
"Scale deployment my-app to 5 replicas"
"Show me the status of deployment my-app"
"Rollout restart deployment my-app"
```

### ניהול Services:

```
"List all services"
"Show me service details for my-service"
"Get endpoints for service my-service"
```

### ניהול ConfigMaps ו-Secrets:

```
"List all configmaps"
"Show me the contents of configmap my-config"
"List all secrets"
```

### ניהול Nodes:

```
"List all nodes"
"Show me node resources"
"Describe node node-1"
```

### ניהול Namespaces:

```
"List all namespaces"
"Create namespace test"
"Delete namespace test"
```

### ניהול Helm Charts:

```
"Install Helm chart nginx-ingress in namespace ingress"
"Upgrade Helm chart my-app to version 1.2.0"
"List all Helm releases"
"Uninstall Helm chart my-app"
```

### Port Forwarding:

```
"Port forward to pod my-app-123 on port 8080"
"Port forward to service my-service on port 80"
"Stop port forward on port 8080"
```

### ניהול Nodes:

```
"Cordon node node-1 for maintenance"
"Drain node node-1"
"Uncordon node node-1"
```

### ניקוי Pods בעייתיים:

```
"Clean up evicted pods in namespace default"
"Clean up pods in CrashLoopBackOff state"
```

---

## ⚠️ בעיות נפוצות ופתרונות

### בעיה 1: "Unable to connect to Kubernetes cluster"

**פתרון:**
1. ודא ש-`kubectl` מותקן ומוגדר
2. בדוק ש-kubeconfig קיים ומוגדר:
   ```bash
   kubectl config view
   ```
3. בדוק חיבור ל-cluster:
   ```bash
   kubectl get nodes
   ```
4. אם יש לך מספר kubeconfig files, הגדר `KUBECONFIG` ב-`env`:

```json
{
  "mcpServers": {
    "kubernetes": {
      "command": "npx",
      "args": ["-y", "mcp-server-kubernetes"],
      "env": {
        "KUBECONFIG": "/path/to/your/kubeconfig"
      }
    }
  }
}
```

### בעיה 2: "Permission denied" או "Forbidden"

**פתרון:**
- השרת משתמש בהרשאות של `kubectl` שלך
- ודא שיש לך הרשאות מתאימות ב-cluster
- בדוק את ה-RBAC rules שלך:
  ```bash
  kubectl auth can-i list pods --all-namespaces
  ```

### בעיה 3: השרת לא נטען ב-Cursor

**פתרון:**
1. ודא ש-Node.js v18+ מותקן:
   ```bash
   node --version
   ```
2. נסה להריץ את השרת ידנית:
   ```bash
   npx -y @modelcontextprotocol/server-kubernetes
   ```
3. בדוק את הלוגים ב-Cursor Developer Tools

### בעיה 4: שגיאות עם kubeconfig מרובה

**פתרון:**
אם יש לך מספר kubeconfig files, צרף אותם:

```bash
export KUBECONFIG=/path/to/config1:/path/to/config2
```

או הגדר ב-`mcp.json`:

```json
{
  "mcpServers": {
    "kubernetes": {
      "command": "npx",
      "args": ["-y", "mcp-server-kubernetes"],
      "env": {
        "KUBECONFIG": "/path/to/config1:/path/to/config2"
      }
    }
  }
}
```

---

## 🛡️ מצב Non-Destructive (קריאה בלבד)

אם אתה רוצה להגביל את השרת לפעולות קריאה בלבד (ללא מחיקות או פעולות הרסניות), תוכל להפעיל את **Non-Destructive Mode**:

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

### פעולות זמינות במצב Non-Destructive:

✅ **קריאת מידע:**
- `kubectl_get` - קבלת רשימת משאבים
- `kubectl_describe` - תיאור מפורט של משאבים
- `kubectl_logs` - קבלת לוגים
- `explain_resource` - הסבר על משאבי Kubernetes
- `list_api_resources` - רשימת משאבי API זמינים

✅ **יצירה ועדכון:**
- `kubectl_apply` - החלת YAML manifests
- `kubectl_create` - יצירת משאבים חדשים
- `kubectl_scale` - שינוי מספר replicas
- `kubectl_patch` - עדכון שדות של משאבים
- `kubectl_rollout` - ניהול rollouts

✅ **Helm Operations:**
- `install_helm_chart` - התקנת Helm charts
- `upgrade_helm_chart` - עדכון Helm charts
- `helm_template_apply` - החלת templates

✅ **חיבורים:**
- `port_forward` - Port forwarding ל-pods ו-services
- `kubectl_context` - ניהול contexts

### פעולות חסומות במצב Non-Destructive:

❌ **פעולות הרסניות:**
- `kubectl_delete` - מחיקת משאבים
- `uninstall_helm_chart` - הסרת Helm charts
- `cleanup_pods` - ניקוי pods בעייתיים
- `node_management` - ניהול nodes (יכול ל-drain nodes)
- `kubectl_generic` - פקודות kubectl כלליות (עשויות לכלול פעולות הרסניות)

---

## 🔒 אבטחה והרשאות

### איך זה עובד:

1. ✅ השרת משתמש ב-kubeconfig שלך לאימות
2. ✅ כל פעולה מתבצעת עם ההרשאות של המשתמש שלך
3. ✅ אין אחסון של credentials - הכל דרך kubeconfig
4. ✅ כל פעולה מתועדת ב-Kubernetes audit logs

### ניהול הרשאות:

- **RBAC (Role-Based Access Control)** קובע מה אתה יכול לעשות
- **Service Accounts** יכולים לשמש לאימות
- **Context switching** מאפשר לעבור בין clusters

### המלצות אבטחה:

- ✅ אל תשתף kubeconfig files
- ✅ השתמש ב-context switching לעבודה עם מספר clusters
- ✅ בדוק הרשאות לפני ביצוע פעולות הרסניות
- ✅ השתמש ב-namespaces לבידוד משאבים

---

## 📚 משאבים נוספים

### תיעוד רשמי:

- [Kubernetes MCP Server GitHub](https://github.com/Flux159/mcp-server-kubernetes) - Repository רשמי
- [Kubernetes MCP Server npm](https://www.npmjs.com/package/mcp-server-kubernetes) - חבילת npm
- [Kubernetes MCP Server Documentation](https://cursor.directory/mcp/kubernetes) - מדריך התקנה
- [Kubernetes Documentation](https://kubernetes.io/docs/) - תיעוד רשמי של Kubernetes
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/) - מדריך kubectl

### קישורים שימושיים:

- [Kubernetes API Reference](https://kubernetes.io/docs/reference/kubernetes-api/)
- [kubectl Commands](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands)

---

## 🎯 סיכום

**מה למדנו:**

1. ✅ Kubernetes MCP Server מאפשר ניהול Kubernetes resources ישירות מ-Cursor
2. ✅ מתחברים אליו דרך Cursor על ידי עריכת קובץ `mcp.json`
3. ✅ השרת משתמש ב-kubeconfig שלך לאימות
4. ✅ ניתן לבצע פעולות Kubernetes דרך שאלות טבעיות

**השלבים הבאים:**

1. ✅ **הוספת ההגדרה** ל-`mcp.json`
2. ⏳ **הפעלה מחדש** של Cursor
3. ⏳ **בדיקה** שהשרת נטען בהצלחה
4. ⏳ **שימוש** בשאלות טבעיות לניהול Kubernetes

---

## 📝 הערות טכניות

### מיקום קובץ ההגדרות:

- **Windows:** `C:\Users\<USERNAME>\.cursor\mcp.json`
- **Mac:** `~/.cursor/mcp.json`
- **Linux:** `~/.cursor/mcp.json`

### דרישות:

- ✅ **Node.js v18+** (להפעלת `npx`)
- ✅ **kubectl** מותקן ומוגדר
- ✅ **kubeconfig** מוגדר ומתחבר ל-cluster
- ✅ **גישה ל-Kubernetes cluster**
- ✅ **Helm v3** (אופציונלי - רק אם אתה רוצה להשתמש ב-Helm operations)

### מיקום kubeconfig ברירת מחדל:

- **Windows:** `C:\Users\<USERNAME>\.kube\config`
- **Mac/Linux:** `~/.kube/config`

---

**עודכן לאחרונה:** 2025-12-02  
**גרסה:** 1.0


