# טופס בקשה פורמלי - דרישות טכניות מצוות האינטרגטור

**מסמך:** טופס בקשה פורמלי לדרישות טכניות  
**מחבר:** רוי אברהמי - QA Team Lead  
**תאריך:** 2025-12-06  
**גרסה:** 1.0  
**סטטוס:** מוכן להגשה

---

## פרטי הבקשה

**מבקש:** רוי אברהמי - QA Team Lead  
**צוות:** QA Automation  
**פרויקט:** Focus Server Automation  
**תאריך בקשה:** 2025-12-06  
**מועד יעד:** לפי עדיפות (ראה מטריצת עדיפויות)

---

## רקע והקשר

### מטרת הבקשה

קידום אוטומציית Focus Server מבחינה טכנית דורש גישות מתקדמות ל-infrastructure הבסיסי. הבקשה הנוכחית מפרטת את כל הדרישות הטכניות הנדרשות מצוות האינטרגטור כדי לאפשר:

1. פיתוח בדיקות מתקדמות (Kubernetes, recovery, load)
2. אינטגרציה מלאה עם CI/CD
3. ניטור וניתוח מתקדמים
4. פיתוח בטוח בסביבת dev נפרדת

### מצב נוכחי

**מה יש כבר:**
- ✅ גישה ל-Kubernetes דרך SSH tunnel
- ✅ גישה ל-MongoDB דרך LoadBalancer
- ✅ גישה ל-RabbitMQ דרך LoadBalancer
- ✅ גישה ל-Focus Server API

**מה חסר:**
- ❌ גישה ישירה ל-Kubernetes API
- ❌ ServiceAccount עם הרשאות מתאימות
- ❌ גישה ל-metrics ו-monitoring
- ❌ סביבת dev/test נפרדת

---

## בקשות ספציפיות

### בקשה #1: Kubernetes API Access

**עדיפות:** 🔴 קריטי  
**מועד יעד:** תוך 2 שבועות

#### מה נדרש:

1. **kubeconfig file** עם credentials תקפים
   - Cluster: `panda-cluster`
   - Namespace: `panda`
   - API Server: `https://10.10.100.102:6443`

2. **גישה ישירה ל-Kubernetes API**
   - ללא תלות ב-SSH tunnel
   - גישה מ-CI/CD runners
   - או: VPN access ל-internal network

#### שימוש:

- פיתוח בדיקות Kubernetes מתקדמות
- ניטור pods בזמן אמת
- בדיקות deployment/rollback
- בדיקות resource management

#### השפעה:

**ללא זה:**
- לא ניתן לפתח בדיקות Kubernetes מתקדמות
- מגביל את היכולת לניטור בזמן אמת
- איטי ולא מתאים לאוטומציה מתקדמת

**עם זה:**
- יכולת לפתח בדיקות מתקדמות
- ניטור בזמן אמת
- אינטגרציה מלאה עם CI/CD

#### פרטים טכניים:

```yaml
# דרוש:
apiVersion: v1
kind: Config
clusters:
- name: panda-cluster
  cluster:
    server: https://10.10.100.102:6443
    certificate-authority-data: <CA_CERT>
contexts:
- name: panda-context
  context:
    cluster: panda-cluster
    namespace: panda
    user: focus-automation-user
users:
- name: focus-automation-user
  user:
    token: <TOKEN>
    # או: client-certificate + client-key
current-context: panda-context
```

---

### בקשה #2: ServiceAccount עם RBAC

**עדיפות:** 🔴 קריטי  
**מועד יעד:** תוך 5 ימים  
**תלות:** בקשה #1

#### מה נדרש:

1. **ServiceAccount:**
   - שם: `focus-automation-sa`
   - Namespace: `panda`

2. **Role עם הרשאות:**
   ```yaml
   apiVersion: rbac.authorization.k8s.io/v1
   kind: Role
   metadata:
     name: focus-automation-role
     namespace: panda
   rules:
   - apiGroups: [""]
     resources: ["pods", "pods/log", "services", "events"]
     verbs: ["get", "list", "watch"]
   - apiGroups: ["apps"]
     resources: ["deployments", "replicasets"]
     verbs: ["get", "list", "watch"]
   - apiGroups: ["batch"]
     resources: ["jobs"]
     verbs: ["get", "list", "watch", "create", "delete"]
   ```

3. **RoleBinding:**
   ```yaml
   apiVersion: rbac.authorization.k8s.io/v1
   kind: RoleBinding
   metadata:
     name: focus-automation-role-binding
     namespace: panda
   subjects:
   - kind: ServiceAccount
     name: focus-automation-sa
     namespace: panda
   roleRef:
     kind: Role
     name: focus-automation-role
     apiGroup: rbac.authorization.k8s.io
   ```

#### שימוש:

- הרצת בדיקות מ-CI/CD
- ניטור resources
- בדיקות job execution
- בדיקות pod lifecycle

#### השפעה:

**ללא זה:**
- לא ניתן להריץ בדיקות מ-CI/CD
- מגביל את היכולת לניטור
- לא ניתן לבדוק job execution

**עם זה:**
- אינטגרציה מלאה עם CI/CD
- ניטור resources
- בדיקות job execution

---

### בקשה #3: MongoDB Advanced Permissions

**עדיפות:** 🟡 חשוב  
**מועד יעד:** תוך 3 ימים

#### מה נדרש:

1. **User חדש או הרשאות נוספות:**
   - שם: `focus-automation` (או הרחבה של `prisma`)
   - הרשאות:
     - `readWrite` על database `prisma`
     - `backup` + `restore` permissions
     - `read` על database `admin` (לבדיקות health)

2. **גישה ל-replica set:**
   - גישה ל-`local` database (read-only)
   - גישה ל-oplog (read-only)

#### שימוש:

- בדיקות backup/restore
- בדיקות data integrity
- בדיקות recovery
- בדיקות replica set sync

#### השפעה:

**ללא זה:**
- לא ניתן לבדוק recovery scenarios
- לא ניתן לבדוק data integrity
- לא ניתן לבדוק backup/restore

**עם זה:**
- בדיקות recovery מלאות
- בדיקות data integrity
- בדיקות backup/restore

---

### בקשה #4: סביבת Dev/Test נפרדת

**עדיפות:** 🟡 חשוב  
**מועד יעד:** תוך 4 שבועות  
**תלות:** בקשה #1, #2

#### מה נדרש:

1. **Kubernetes Namespace:**
   - שם: `focus-automation-dev`
   - בידוד מלא מ-production

2. **MongoDB Instance נפרדת:**
   - או: database נפרד באותה instance
   - נתוני test data מוגדרים מראש

3. **RabbitMQ Instance נפרדת:**
   - או: vhost נפרד
   - בידוד מלא

4. **Focus Server Instance נפרדת:**
   - או: deployment נפרד ב-namespace
   - נתוני test data

#### שימוש:

- פיתוח בדיקות חדשות
- בדיקות הרסניות ללא סיכון
- ניסויים טכניים
- בדיקות load/stress מבודדות

#### השפעה:

**ללא זה:**
- לא ניתן לבדוק בדיקות הרסניות
- סיכון ל-production
- מגביל ניסויים טכניים

**עם זה:**
- בדיקות הרסניות בטוחות
- בידוד מלא מ-production
- ניסויים טכניים

---

### בקשה #5: Metrics & Monitoring Access

**עדיפות:** 🟡 חשוב  
**מועד יעד:** תוך 2 שבועות  
**תלות:** בקשה #1

#### מה נדרש:

1. **גישה ל-Prometheus** (אם קיים):
   - URL: `http://prometheus.panda:9090` (או IP מתאים)
   - או: API endpoint
   - Credentials (אם נדרש)

2. **גישה ל-Kubernetes Metrics API:**
   - דרך Kubernetes API
   - metrics על: CPU, Memory, Network

3. **גישה ל-Grafana Dashboards** (אם קיים):
   - URL: `http://grafana.panda:3000` (או IP מתאים)
   - Credentials
   - Dashboards רלוונטיים

#### שימוש:

- ניטור ביצועים בזמן אמת
- זיהוי memory leaks
- זיהוי resource exhaustion
- ניתוח בעיות ביצועים

#### השפעה:

**ללא זה:**
- לא ניתן לניטור מתקדם
- לא ניתן לזיהוי memory leaks
- לא ניתן לניתוח בעיות ביצועים

**עם זה:**
- ניטור מתקדם
- זיהוי בעיות בזמן אמת
- ניתוח ביצועים

---

### בקשה #6: Network/VPN Access

**עדיפות:** 🔴 קריטי  
**מועד יעד:** תוך 3 שבועות

#### מה נדרש:

1. **VPN Access** (מועדף):
   - VPN client configuration
   - Credentials
   - גישה ל-internal network (10.10.100.0/24)

2. **או: Network Routing:**
   - Routing מ-CI/CD runners ל-internal network
   - Firewall rules מתאימים

3. **או: LoadBalancer IPs:**
   - LoadBalancer IPs עם firewall rules
   - גישה מ-CI/CD runners

#### שימוש:

- גישה ישירה מ-CI/CD runners
- פיתוח יעיל יותר
- בדיקות מתקדמות

#### השפעה:

**ללא זה:**
- תלות ב-SSH tunnel (איטי)
- מגביל CI/CD integration
- לא מתאים לאוטומציה מתקדמת

**עם זה:**
- גישה ישירה ויעילה
- CI/CD integration מלא
- אוטומציה מתקדמת

---

### בקשה #7: CI/CD Secrets Management

**עדיפות:** 🟡 חשוב  
**מועד יעד:** תוך 5 ימים  
**תלות:** בקשה #1, #2

#### מה נדרש:

1. **GitHub Secrets:**
   - `KUBECONFIG` - Kubernetes config
   - `KUBERNETES_SERVICE_ACCOUNT_TOKEN` - ServiceAccount token
   - `MONGODB_USERNAME` - MongoDB username
   - `MONGODB_PASSWORD` - MongoDB password
   - `RABBITMQ_USERNAME` - RabbitMQ username
   - `RABBITMQ_PASSWORD` - RabbitMQ password
   - `SSH_PRIVATE_KEY` - SSH key (אם נדרש)

2. **תיעוד:**
   - רשימת כל ה-secrets הנדרשים
   - הוראות עדכון

#### שימוש:

- CI/CD integration
- אבטחה טובה יותר
- אוטומציה מלאה

#### השפעה:

**ללא זה:**
- לא ניתן ל-CI/CD integration מלא
- credentials hardcoded (לא בטוח)
- מגביל אוטומציה

**עם זה:**
- CI/CD integration מלא
- אבטחה טובה
- אוטומציה מלאה

---

### בקשה #8: Logs Centralized Access

**עדיפות:** 🟡 חשוב  
**מועד יעד:** תוך שבוע  
**תלות:** בקשה #1

#### מה נדרש:

1. **גישה ל-Centralized Logging** (אם קיים):
   - URL: `http://logging.panda:9200` (או IP מתאים)
   - או: Elasticsearch/Kibana access
   - Credentials

2. **או: גישה ל-Pod Logs דרך Kubernetes API:**
   - דרך Kubernetes API (כבר נדרש ב-#1)
   - אפשרות לשאילתות לפי time range

#### שימוש:

- ניתוח שגיאות בבדיקות
- זיהוי patterns בבעיות
- דיבוג בעיות production

#### השפעה:

**ללא זה:**
- לא ניתן לניתוח מתקדם
- לא ניתן לזיהוי patterns
- מגביל דיבוג

**עם זה:**
- ניתוח מתקדם
- זיהוי patterns
- דיבוג יעיל

---

### בקשה #9: Database Snapshots & Backups

**עדיפות:** 🟢 נמוכה  
**מועד יעד:** תוך שבוע  
**תלות:** בקשה #3

#### מה נדרש:

1. **גישה ל-Backup Snapshots:**
   - מיקום: path או S3 bucket
   - Credentials
   - רשימת snapshots זמינים

2. **אפשרות ל-Create Snapshot:**
   - לפני בדיקות הרסניות
   - API או command line

3. **אפשרות ל-Restore Snapshot:**
   - אחרי בדיקות הרסניות
   - API או command line

#### שימוש:

- בדיקות data integrity
- בדיקות recovery
- בדיקות migration
- שחזור סביבה

#### השפעה:

**ללא זה:**
- לא ניתן לבדוק recovery scenarios
- לא ניתן לשחזר סביבה
- מגביל בדיקות הרסניות

**עם זה:**
- בדיקות recovery מלאות
- שחזור סביבה
- בדיקות הרסניות בטוחות

---

### בקשה #10: תיעוד ארכיטקטורה

**עדיפות:** 🟢 נמוכה  
**מועד יעד:** מתמשך

#### מה נדרש:

1. **תיעוד מיקרו-שירותים:**
   - רשימת כל השירותים
   - קשרים ביניהם
   - Dependencies

2. **תיעוד Data Flow:**
   - איך נתונים זורמים במערכת
   - איזה שירותים מעורבים
   - נקודות integration

3. **תיעוד Event Flow:**
   - איך events זורמים
   - RabbitMQ queues
   - Event handlers

4. **תיעוד Infrastructure:**
   - Kubernetes cluster topology
   - Network architecture
   - Database schema

#### שימוש:

- הבנת המערכת
- פיתוח בדיקות מתאימות
- Troubleshooting
- Onboarding

#### השפעה:

**ללא זה:**
- קושי בהבנת המערכת
- בדיקות לא מתאימות
- קושי ב-troubleshooting

**עם זה:**
- הבנה טובה של המערכת
- בדיקות מתאימות
- Troubleshooting יעיל

---

## תוכנית יישום מומלצת

### שלב 1: יסודות (שבועות 1-2)

**דרישות קריטיות:**
1. ✅ Kubernetes API Access (#1)
2. ✅ ServiceAccount + RBAC (#2)
3. ✅ Network/VPN Access (#6)

**תוצאה:** יכולת בסיסית לפתח בדיקות

---

### שלב 2: הרחבה (שבועות 3-4)

**דרישות חשובות:**
4. ✅ MongoDB Advanced Permissions (#3)
5. ✅ Metrics & Monitoring Access (#5)
6. ✅ CI/CD Secrets Management (#7)
7. ✅ Logs Centralized Access (#8)

**תוצאה:** שיפור יכולות בדיקה

---

### שלב 3: סביבת פיתוח (שבועות 5-8)

**דרישות חשובות:**
8. ✅ סביבת Dev/Test נפרדת (#4)

**תוצאה:** יכולת לבדיקות הרסניות

---

### שלב 4: שיפורים (שבוע 9+)

**דרישות נוספות:**
9. ✅ Database Snapshots (#9)
10. ✅ תיעוד ארכיטקטורה (#10)

**תוצאה:** שיפורים נוספים

---

## תמיכה נדרשת

### תמיכה טכנית

**נדרש:**
- תמיכה בהגדרת הגישות
- הדרכה על השימוש ב-infrastructure
- תמיכה בבעיות טכניות

**נקודת קשר מומלצת:**
- איש DevOps/Infrastructure מצוות האינטרגטור
- זמינות: לפחות שעתיים בשבוע

---

### תמיכה תיעודית

**נדרש:**
- תיעוד infrastructure
- תיעוד API endpoints
- תיעוד troubleshooting

---

## הערכת השפעה

### ללא הדרישות

**מגבלות:**
- לא ניתן לפתח בדיקות Kubernetes מתקדמות
- לא ניתן לבדוק recovery scenarios
- לא ניתן לניטור מתקדם
- לא ניתן לבדיקות הרסניות

**השפעה על פרויקט:**
- התקדמות איטית
- כיסוי בדיקות מוגבל
- תלות ב-SSH tunnel (איטי)

---

### עם הדרישות

**יכולות:**
- בדיקות Kubernetes מתקדמות
- בדיקות recovery מלאות
- ניטור מתקדם
- בדיקות הרסניות בטוחות

**השפעה על פרויקט:**
- התקדמות מהירה
- כיסוי בדיקות מלא
- אוטומציה מקצועית

---

## סיכום

### דרישות קריטיות (חייב לקבל)

1. **Kubernetes API Access** - ללא זה לא ניתן לפתח בדיקות מתקדמות
2. **ServiceAccount + RBAC** - נדרש ל-CI/CD integration
3. **Network/VPN Access** - נדרש לגישה ישירה

### דרישות חשובות (מומלץ לקבל)

4. **MongoDB Advanced Permissions** - נדרש לבדיקות recovery
5. **סביבת Dev/Test** - מאפשר פיתוח בטוח
6. **Metrics & Monitoring** - מאפשר ניטור מתקדם
7. **CI/CD Secrets** - נדרש ל-CI/CD integration
8. **Logs Access** - מאפשר ניתוח בעיות

### דרישות נוספות (nice to have)

9. **Database Snapshots** - משפר בדיקות recovery
10. **תיעוד** - משפר יכולת פיתוח

---

## אישורים נדרשים

**מאשר:** _______________ (מנהל צוות האינטרגטור)  
**תאריך:** _______________  
**הערות:** _______________

**מאשר:** _______________ (מנהל DevOps/Infrastructure)  
**תאריך:** _______________  
**הערות:** _______________

---

**טופס זה מוכן להגשה לצוות האינטרגטור לדיון ואישור.**

