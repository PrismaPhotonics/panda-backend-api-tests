# דרישות טכניות מצוות האינטרגטור - קידום אוטומציה

**מסמך:** דרישות טכניות וסביבתיות לקידום אוטומציית Focus Server  
**מחבר:** רוי אברהמי - QA Team Lead  
**תאריך:** 2025-12-06  
**גרסה:** 1.0  
**סטטוס:** דרישות להעברה לצוות האינטרגטור

---

## תוכן עניינים

1. [סיכום מנהלים](#סיכום-מנהלים)
2. [דרישות Kubernetes](#דרישות-kubernetes)
3. [דרישות Database](#דרישות-database)
4. [דרישות Network & Security](#דרישות-network--security)
5. [דרישות Monitoring & Logging](#דרישות-monitoring--logging)
6. [דרישות סביבת פיתוח](#דרישות-סביבת-פיתוח)
7. [דרישות CI/CD](#דרישות-cicd)
8. [דרישות תיעוד](#דרישות-תיעוד)
9. [תוכנית יישום](#תוכנית-יישום)

---

## סיכום מנהלים

### מטרת המסמך

מסמך זה מפרט את כל הדרישות הטכניות והסביבתיות הנדרשות מצוות האינטרגטור כדי לאפשר קידום משמעותי של אוטומציית Focus Server מבחינה טכנית.

### מצב נוכחי

**מה יש כבר:**
- ✅ גישה ל-Kubernetes דרך SSH tunnel (jump host)
- ✅ גישה ל-MongoDB דרך LoadBalancer (read/write)
- ✅ גישה ל-RabbitMQ דרך LoadBalancer
- ✅ גישה ל-Focus Server API
- ✅ סביבות staging ו-production מוגדרות

**מה חסר:**
- ❌ גישה ישירה ל-Kubernetes API (רק דרך SSH)
- ❌ ServiceAccount עם הרשאות מתאימות
- ❌ גישה ל-metrics ו-monitoring
- ❌ סביבת dev/test נפרדת
- ❌ גישה ל-backups/restore
- ❌ תיעוד ארכיטקטורה

---

## דרישות Kubernetes

### 1. גישה ישירה ל-Kubernetes API

**דרישה נוכחית:**
- גישה רק דרך SSH tunnel → `kubectl` על worker node
- איטי ולא מתאים לאוטומציה מתקדמת

**דרישה:**
- גישה ישירה ל-Kubernetes API Server
- `kubeconfig` עם credentials תקפים
- אפשרות חיבור מ-CI/CD runners

**פרטים טכניים:**
```yaml
# דרוש:
- API Server: https://10.10.100.102:6443 (או staging equivalent)
- kubeconfig file עם:
  - Cluster CA certificate
  - User credentials (token/certificate)
  - Context: panda-cluster
  - Namespace: panda
```

**הרשאות נדרשות:**
- `get`, `list`, `watch` על pods, services, deployments
- `get`, `list` על logs
- `create`, `delete` על jobs (לבדיקות)
- `get`, `list` על events

### 2. ServiceAccount עם RBAC

**דרישה:**
- ServiceAccount ייעודי לאוטומציה: `focus-automation-sa`
- Role/RoleBinding עם הרשאות מינימליות נדרשות
- אפשרות ל-impersonation מ-CI/CD

**RBAC נדרש:**
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

### 3. גישה ל-Metrics & Monitoring

**דרישה:**
- גישה ל-Prometheus metrics (אם קיים)
- גישה ל-Kubernetes metrics API
- אפשרות לשאילתות על resource usage (CPU, Memory)

**שימוש:**
- ניטור ביצועים בזמן אמת במהלך בדיקות
- זיהוי memory leaks
- זיהוי resource exhaustion

### 4. Namespace נפרד לבדיקות

**דרישה:**
- Namespace ייעודי: `focus-automation-test`
- הרשאות מלאות ב-namespace זה
- בידוד מלא מ-production

**שימוש:**
- הרצת בדיקות load/stress מבודדות
- בדיקות outage simulation
- בדיקות deployment/rollback

---

## דרישות Database

### 1. גישה ל-MongoDB עם הרשאות מתקדמות

**מה יש:**
- ✅ גישה read/write בסיסית
- ✅ Credentials: `prisma/prisma`

**מה חסר:**
- ❌ גישה ל-admin operations (backup/restore)
- ❌ גישה ל-replica set configuration
- ❌ גישה ל-oplog (לבדיקות sync)

**דרישות:**
- User עם הרשאות `readWrite` + `backup` + `restore`
- גישה ל-`admin` database (לבדיקות health)
- גישה ל-`local` database (לבדיקות replica set)

### 2. גישה ל-PostgreSQL (אם קיים)

**דרישה:**
- Credentials ל-PostgreSQL (אם יש)
- גישה read-only לבדיקות
- Schema documentation

### 3. Database Snapshots & Backups

**דרישה:**
- גישה ל-backup snapshots (לשחזור סביבה)
- אפשרות ל-create snapshot לפני בדיקות הרסניות
- אפשרות ל-restore snapshot אחרי בדיקות

**שימוש:**
- בדיקות data integrity
- בדיקות recovery
- בדיקות migration

---

## דרישות Network & Security

### 1. גישה ישירה ל-Services (ללא SSH tunnel)

**מה יש:**
- ✅ גישה דרך SSH jump host
- ✅ LoadBalancer IPs זמינים

**מה חסר:**
- ❌ גישה ישירה מ-CI/CD runners
- ❌ VPN access או network routing

**דרישה:**
- VPN access או network routing ל-internal network
- או: LoadBalancer IPs עם firewall rules מתאימים
- או: Ingress controller עם authentication

### 2. Firewall Rules

**דרישה:**
- פתיחת פורטים נדרשים מ-CI/CD runners:
  - `6443` - Kubernetes API
  - `27017` - MongoDB
  - `5672` - RabbitMQ
  - `5000` - Focus Server API
  - `15672` - RabbitMQ Management UI

### 3. SSL/TLS Certificates

**דרישה:**
- CA certificates ל-self-signed certificates
- או: valid SSL certificates (מועדף)
- תיעוד של certificate chain

---

## דרישות Monitoring & Logging

### 1. גישה ל-Logs מרכזיים

**דרישה:**
- גישה ל-centralized logging (אם קיים)
- או: גישה ל-pod logs דרך Kubernetes API
- אפשרות לשאילתות logs לפי time range

**שימוש:**
- ניתוח שגיאות בבדיקות
- זיהוי patterns בבעיות
- דיבוג בעיות production

### 2. גישה ל-Alerts & Notifications

**דרישה:**
- גישה ל-alerting system (אם קיים)
- אפשרות ל-create alerts לבדיקות
- אינטגרציה עם Slack/Email

### 3. Metrics & Dashboards

**דרישה:**
- גישה ל-Grafana dashboards (אם קיים)
- או: גישה ל-Prometheus queries
- metrics על:
  - Pod resource usage
  - API response times
  - Database query performance
  - Queue depths

---

## דרישות סביבת פיתוח

### 1. סביבת Dev/Test נפרדת

**דרישה:**
- סביבת dev נפרדת מ-staging/production
- עם:
  - Kubernetes cluster נפרד (או namespace מבודד)
  - MongoDB instance נפרדת
  - RabbitMQ instance נפרדת
  - Focus Server instance נפרדת

**שימוש:**
- פיתוח בדיקות חדשות
- בדיקות הרסניות ללא סיכון
- ניסויים טכניים

### 2. סביבת Staging משופרת

**מה יש:**
- ✅ סביבת staging בסיסית

**מה חסר:**
- ❌ נתוני test data מספקים
- ❌ סביבה יציבה (לא מתעדכנת כל הזמן)
- ❌ גישה ל-reset סביבה

**דרישה:**
- סביבת staging יציבה
- נתוני test data מוגדרים מראש
- אפשרות ל-reset סביבה למצב נקי

### 3. Test Data Management

**דרישה:**
- גישה ל-create/delete test data
- נתוני test data מוגדרים מראש
- אפשרות ל-seed data לפני בדיקות

---

## דרישות CI/CD

### 1. GitHub Actions Runner Access

**דרישה:**
- Self-hosted runner עם גישה ל-internal network
- או: VPN access מ-GitHub-hosted runners
- או: Network routing מתאים

**נוכחי:**
- ✅ Self-hosted runner: `panda_automation`
- ❓ גישה ל-internal network?

### 2. Secrets Management

**דרישה:**
- GitHub Secrets מוגדרים עם:
  - Kubernetes credentials
  - Database credentials
  - SSH keys
  - API tokens

**נוכחי:**
- ✅ חלק מהדברים קיימים
- ❓ עדכון והשלמה נדרשים

### 3. Container Registry Access

**דרישה:**
- גישה ל-container registry (אם קיים)
- אפשרות ל-pull images לבדיקות
- או: documentation על image locations

---

## דרישות תיעוד

### 1. ארכיטקטורה

**דרישה:**
- תיעוד ארכיטקטורה של המערכת:
  - מיקרו-שירותים וקשרים ביניהם
  - Data flow
  - Event flow
  - Dependencies

### 2. Infrastructure Documentation

**דרישה:**
- תיעוד infrastructure:
  - Kubernetes cluster topology
  - Network architecture
  - Database schema
  - Service dependencies

### 3. API Documentation

**דרישה:**
- OpenAPI/Swagger specs מעודכנים
- תיעוד gRPC services
- תיעוד message queue schemas

### 4. Runbooks & Troubleshooting

**דרישה:**
- Runbooks לפעולות נפוצות
- Troubleshooting guides
- Known issues ו-workarounds

---

## תוכנית יישום

### שלב 1: דרישות קריטיות (חודש 1)

**עדיפות גבוהה:**
1. ✅ גישה ישירה ל-Kubernetes API
2. ✅ ServiceAccount עם RBAC
3. ✅ גישה ל-MongoDB עם הרשאות מתקדמות
4. ✅ סביבת dev/test נפרדת

**תוצאה צפויה:**
- יכולת לפתח בדיקות מתקדמות
- יכולת לבדוק outage scenarios
- יכולת לבדוק recovery

### שלב 2: דרישות חשובות (חודש 2)

**עדיפות בינונית:**
1. ✅ גישה ל-Metrics & Monitoring
2. ✅ גישה ל-Logs מרכזיים
3. ✅ Database Snapshots & Backups
4. ✅ Network & Security improvements

**תוצאה צפויה:**
- יכולת לניטור בזמן אמת
- יכולת לניתוח בעיות
- יכולת לשחזור סביבות

### שלב 3: דרישות נוספות (חודש 3+)

**עדיפות נמוכה:**
1. ✅ תיעוד מקיף
2. ✅ CI/CD improvements
3. ✅ Advanced monitoring

**תוצאה צפויה:**
- אוטומציה מלאה ומקצועית
- יכולת תחזוקה קלה
- יכולת הרחבה

---

## רשימת בקשות ספציפית לצוות האינטרגטור

### בקשה #1: Kubernetes API Access

**מה נדרש:**
- kubeconfig file עם credentials תקפים
- גישה ישירה ל-API Server: `https://10.10.100.102:6443`
- או: VPN access ל-internal network

**שימוש:**
- פיתוח בדיקות Kubernetes מתקדמות
- ניטור pods בזמן אמת
- בדיקות deployment/rollback

**עדיפות:** 🔴 גבוהה

---

### בקשה #2: ServiceAccount עם RBAC

**מה נדרש:**
- ServiceAccount: `focus-automation-sa` ב-namespace `panda`
- Role עם הרשאות:
  - `get`, `list`, `watch` על pods, services, deployments
  - `get`, `list` על logs
  - `create`, `delete` על jobs

**שימוש:**
- הרצת בדיקות מ-CI/CD
- ניטור resources
- בדיקות job execution

**עדיפות:** 🔴 גבוהה

---

### בקשה #3: MongoDB Advanced Permissions

**מה נדרש:**
- User עם הרשאות:
  - `readWrite` על database `prisma`
  - `backup` + `restore` permissions
  - גישה ל-`admin` database (read-only)

**שימוש:**
- בדיקות backup/restore
- בדיקות data integrity
- בדיקות recovery

**עדיפות:** 🟡 בינונית

---

### בקשה #4: סביבת Dev/Test נפרדת

**מה נדרש:**
- סביבת dev נפרדת עם:
  - Kubernetes namespace: `focus-automation-dev`
  - MongoDB instance נפרדת
  - RabbitMQ instance נפרדת
  - Focus Server instance נפרדת

**שימוש:**
- פיתוח בדיקות חדשות
- בדיקות הרסניות ללא סיכון
- ניסויים טכניים

**עדיפות:** 🟡 בינונית

---

### בקשה #5: גישה ל-Metrics & Monitoring

**מה נדרש:**
- גישה ל-Prometheus (אם קיים)
- או: גישה ל-Kubernetes metrics API
- גישה ל-Grafana dashboards (אם קיים)

**שימוש:**
- ניטור ביצועים בזמן אמת
- זיהוי memory leaks
- זיהוי resource exhaustion

**עדיפות:** 🟡 בינונית

---

### בקשה #6: Database Snapshots & Backups

**מה נדרש:**
- גישה ל-backup snapshots
- אפשרות ל-create snapshot לפני בדיקות
- אפשרות ל-restore snapshot אחרי בדיקות

**שימוש:**
- בדיקות data integrity
- בדיקות recovery
- בדיקות migration

**עדיפות:** 🟢 נמוכה

---

### בקשה #7: תיעוד ארכיטקטורה

**מה נדרש:**
- תיעוד מיקרו-שירותים וקשרים
- תיעוד data flow
- תיעוד event flow
- תיעוד dependencies

**שימוש:**
- הבנת המערכת
- פיתוח בדיקות מתאימות
- troubleshooting

**עדיפות:** 🟢 נמוכה

---

## סיכום

### דרישות קריטיות (חייב לקבל)

1. **Kubernetes API Access** - ללא זה לא ניתן לפתח בדיקות מתקדמות
2. **ServiceAccount עם RBAC** - נדרש ל-CI/CD integration
3. **MongoDB Advanced Permissions** - נדרש לבדיקות recovery

### דרישות חשובות (מומלץ לקבל)

4. **סביבת Dev/Test** - מאפשרת פיתוח בטוח
5. **Metrics & Monitoring** - מאפשר ניטור מתקדם
6. **Database Snapshots** - מאפשר בדיקות recovery

### דרישות נוספות (nice to have)

7. **תיעוד מקיף** - משפר יכולת פיתוח ותחזוקה

---

## הערות נוספות

### תקשורת עם צוות האינטרגטור

**מומלץ:**
- פגישה ראשונית להצגת הדרישות
- הגדרת נקודת קשר קבועה
- עדכונים שבועיים על התקדמות

### תזמון

**רצוי:**
- דרישות קריטיות: תוך חודש
- דרישות חשובות: תוך 2-3 חודשים
- דרישות נוספות: לפי צורך

### תמיכה טכנית

**נדרש:**
- תמיכה טכנית בהגדרת הגישות
- הדרכה על השימוש ב-infrastructure
- תמיכה בבעיות טכניות

---

**מסמך זה מהווה בסיס לדיון עם צוות האינטרגטור על דרישות טכניות לקידום אוטומציה.**

