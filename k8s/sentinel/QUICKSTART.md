# Quick Start Guide - Sentinel Kubernetes Deployment

מדריך מהיר לפריסת Sentinel ב-Kubernetes.

## שלבים מהירים

### 1. בניית Image

```bash
docker build -f Dockerfile.sentinel -t automation-run-sentinel:latest .
docker tag automation-run-sentinel:latest your-registry/automation-run-sentinel:latest
docker push your-registry/automation-run-sentinel:latest
```

### 2. עדכון Secrets

ערוך `secret.yaml` והוסף את ה-webhook URLs שלך:

```yaml
stringData:
  SLACK_WEBHOOK_URL: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

### 3. עדכון Image ב-Deployment

ערוך `deployment.yaml`:

```yaml
image: your-registry/automation-run-sentinel:latest
```

### 4. פריסה

```bash
# Option 1: Using kubectl directly
kubectl apply -k k8s/sentinel/

# Option 2: Using Helm (recommended)
helm install sentinel ./helm/sentinel -f helm/sentinel/values.yaml
```

### 5. בדיקה

```bash
# Check pods
kubectl get pods -n sentinel

# Check logs
kubectl logs -n sentinel -l app=automation-run-sentinel --tail=50

# Test health endpoint
kubectl port-forward -n sentinel svc/automation-run-sentinel 5000:5000
curl http://localhost:5000/health
```

## הגדרות מהירות

### שינוי Namespaces לניטור

ערוך `configmap.yaml`:

```yaml
k8s_namespaces:
  - "your-namespace-1"
  - "your-namespace-2"
```

### שינוי Labels לזיהוי

ערוך `configmap.yaml`:

```yaml
k8s_label_selectors:
  app: "your-app-name"
  component: "your-component"
```

### הפעלת PostgreSQL

ערוך `configmap.yaml`:

```yaml
database:
  type: "postgresql"
  host: "${DB_HOST}"
  port: 5432
  database: "sentinel"
  user: "${DB_USER}"
  password: "${DB_PASSWORD}"
```

והוסף ל-`secret.yaml`:

```yaml
DB_HOST: "your-postgres-host"
DB_USER: "sentinel"
DB_PASSWORD: "your-password"
```

## Troubleshooting מהיר

### Pod לא מתחיל

```bash
kubectl describe pod -n sentinel -l app=automation-run-sentinel
kubectl logs -n sentinel -l app=automation-run-sentinel
```

### בעיות RBAC

```bash
kubectl auth can-i get pods --as=system:serviceaccount:sentinel:sentinel -n panda
```

### בעיות ConfigMap

```bash
kubectl get configmap -n sentinel sentinel-config -o yaml
```

## עדכון

```bash
# Build new image
docker build -f Dockerfile.sentinel -t automation-run-sentinel:v1.1.0 .
docker push your-registry/automation-run-sentinel:v1.1.0

# Update deployment
kubectl set image deployment/automation-run-sentinel \
  sentinel=your-registry/automation-run-sentinel:v1.1.0 \
  -n sentinel
```

## מחיקה

```bash
kubectl delete -k k8s/sentinel/
# או
helm uninstall sentinel
```

