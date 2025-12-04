# Kubernetes Deployment Guide - Automation Run Sentinel

מדריך פריסה מלא עבור שירות Sentinel ב-Kubernetes.

## מבנה הקבצים

```
k8s/sentinel/
├── namespace.yaml          # Namespace definition
├── serviceaccount.yaml     # ServiceAccount
├── role.yaml              # RBAC Role & ClusterRole
├── rolebinding.yaml        # RBAC RoleBinding & ClusterRoleBinding
├── configmap.yaml          # Configuration
├── secret.yaml             # Secrets template
├── deployment.yaml         # Deployment
├── service.yaml            # Service
├── kustomization.yaml      # Kustomize configuration
└── README.md               # This file
```

## דרישות מוקדמות

- Kubernetes cluster (1.19+)
- kubectl configured
- Docker image built and pushed to registry
- Access to create namespaces, service accounts, and RBAC resources

## שלבי הפריסה

### 1. בניית Docker Image

```bash
# Build the image
docker build -f Dockerfile.sentinel -t automation-run-sentinel:latest .

# Tag for your registry
docker tag automation-run-sentinel:latest your-registry/automation-run-sentinel:latest

# Push to registry
docker push your-registry/automation-run-sentinel:latest
```

### 2. הגדרת Secrets

ערוך את `secret.yaml` והוסף את הערכים הנדרשים:

```bash
# Create secret manually
kubectl create secret generic sentinel-secrets \
  --from-literal=SLACK_WEBHOOK_URL='https://hooks.slack.com/services/...' \
  --from-literal=GENERIC_WEBHOOK_URL='https://your-webhook-url.com/...' \
  -n sentinel

# Or edit secret.yaml and apply
kubectl apply -f k8s/sentinel/secret.yaml
```

### 3. עדכון ConfigMap

ערוך את `configmap.yaml` לפי הצרכים שלך:

- `k8s_namespaces`: Namespaces לניטור
- `k8s_label_selectors`: Labels לזיהוי resources
- `pipeline_structure_rules`: כללי מבנה לפי pipeline
- `anomaly_thresholds`: ספי אנומליות

### 4. עדכון Deployment

ערוך את `deployment.yaml`:

- `image`: עדכן את שם התמונה ל-registry שלך
- `resources`: התאם limits לפי הצרכים
- `replicas`: מספר replicas (מומלץ 1 עם SQLite, יותר עם PostgreSQL)

### 5. פריסה

#### שימוש ב-kubectl ישירות:

```bash
# Create namespace
kubectl apply -f k8s/sentinel/namespace.yaml

# Create RBAC
kubectl apply -f k8s/sentinel/serviceaccount.yaml
kubectl apply -f k8s/sentinel/role.yaml
kubectl apply -f k8s/sentinel/rolebinding.yaml

# Create ConfigMap and Secret
kubectl apply -f k8s/sentinel/configmap.yaml
kubectl apply -f k8s/sentinel/secret.yaml

# Deploy application
kubectl apply -f k8s/sentinel/deployment.yaml
kubectl apply -f k8s/sentinel/service.yaml
```

#### שימוש ב-Kustomize:

```bash
kubectl apply -k k8s/sentinel/
```

#### שימוש ב-Helm (מומלץ):

```bash
helm install sentinel ./helm/sentinel -f helm/sentinel/values.yaml
```

## בדיקת הפריסה

### בדיקת Pods

```bash
kubectl get pods -n sentinel
kubectl describe pod -n sentinel -l app=automation-run-sentinel
kubectl logs -n sentinel -l app=automation-run-sentinel --tail=100
```

### בדיקת Service

```bash
kubectl get svc -n sentinel
kubectl describe svc -n sentinel automation-run-sentinel
```

### בדיקת Health Checks

```bash
# Port forward
kubectl port-forward -n sentinel svc/automation-run-sentinel 5000:5000

# Test health endpoint
curl http://localhost:5000/health
curl http://localhost:5000/ready
```

### בדיקת RBAC

```bash
kubectl get role,rolebinding,clusterrole,clusterrolebinding -n sentinel
kubectl describe role -n sentinel sentinel-role
```

## Troubleshooting

### Pod לא מתחיל

```bash
# בדוק events
kubectl get events -n sentinel --sort-by='.lastTimestamp'

# בדוק logs
kubectl logs -n sentinel -l app=automation-run-sentinel

# בדוק describe
kubectl describe pod -n sentinel -l app=automation-run-sentinel
```

### בעיות עם Kubernetes API

```bash
# בדוק ServiceAccount
kubectl get sa -n sentinel sentinel
kubectl describe sa -n sentinel sentinel

# בדוק RBAC
kubectl auth can-i get pods --as=system:serviceaccount:sentinel:sentinel -n panda
kubectl auth can-i list jobs --as=system:serviceaccount:sentinel:sentinel -n panda
```

### בעיות עם ConfigMap

```bash
# בדוק ConfigMap
kubectl get configmap -n sentinel sentinel-config
kubectl describe configmap -n sentinel sentinel-config

# בדוק שהקובץ מוטען ב-pod
kubectl exec -n sentinel -it deployment/automation-run-sentinel -- cat /app/config/sentinel_config.yaml
```

### בעיות עם Secrets

```bash
# בדוק Secrets (לא יראה את התוכן)
kubectl get secret -n sentinel sentinel-secrets
kubectl describe secret -n sentinel sentinel-secrets

# בדוק שהסודות נטענים כ-env vars
kubectl exec -n sentinel -it deployment/automation-run-sentinel -- env | grep SLACK
```

## עדכון

### עדכון Image

```bash
# Build new image
docker build -f Dockerfile.sentinel -t automation-run-sentinel:v1.1.0 .

# Push to registry
docker push your-registry/automation-run-sentinel:v1.1.0

# Update deployment
kubectl set image deployment/automation-run-sentinel \
  sentinel=your-registry/automation-run-sentinel:v1.1.0 \
  -n sentinel

# Or edit deployment.yaml and apply
kubectl apply -f k8s/sentinel/deployment.yaml
```

### עדכון ConfigMap

```bash
# Edit configmap.yaml
# Apply changes
kubectl apply -f k8s/sentinel/configmap.yaml

# Restart pods to pick up changes
kubectl rollout restart deployment/automation-run-sentinel -n sentinel
```

## מחיקה

```bash
# Delete all resources
kubectl delete -k k8s/sentinel/

# Or delete individually
kubectl delete -f k8s/sentinel/deployment.yaml
kubectl delete -f k8s/sentinel/service.yaml
kubectl delete -f k8s/sentinel/configmap.yaml
kubectl delete -f k8s/sentinel/secret.yaml
kubectl delete -f k8s/sentinel/rolebinding.yaml
kubectl delete -f k8s/sentinel/role.yaml
kubectl delete -f k8s/sentinel/serviceaccount.yaml
kubectl delete -f k8s/sentinel/namespace.yaml
```

## Production Best Practices

1. **Use PostgreSQL**: עבור production, השתמש ב-PostgreSQL במקום SQLite
2. **Enable Persistence**: הפעל PersistentVolume עבור data retention
3. **Resource Limits**: הגדר limits מתאימים לפי workload
4. **Monitoring**: הוסף monitoring עבור השירות עצמו
5. **Backup**: הגדר backup עבור database
6. **Security**: 
   - השתמש ב-external secret management (Vault, Sealed Secrets)
   - הגבל RBAC permissions למינימום הנדרש
   - השתמש ב-network policies
7. **High Availability**: 
   - הפעל מספר replicas עם PostgreSQL
   - השתמש ב-PodDisruptionBudget

## תמיכה

לשאלות ותמיכה, פנה ל-DevOps team או פתח issue ב-repository.

