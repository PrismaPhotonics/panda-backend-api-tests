# פריסת Sentinel ללא Docker מקומי

מדריך לפריסת Sentinel ב-Kubernetes ללא צורך בבניית Docker image מקומית.

## אפשרות 1: שימוש ב-GitHub Actions (מומלץ)

יצרתי עבורך GitHub Actions workflow שמבנה את ה-image אוטומטית.

### איך זה עובד?

1. **Push ל-GitHub**: כשאתה מעלה קוד ל-GitHub, ה-workflow בונה את ה-image אוטומטית
2. **Image נשמר ב-GitHub Container Registry**: ה-image זמין ב-`ghcr.io/your-org/automation-run-sentinel`
3. **שימוש ב-image**: עדכן את ה-deployment להשתמש ב-image מה-registry

### שלבים:

#### 1. הפעל את ה-Workflow

```bash
# Commit את השינויים
git add .github/workflows/build-sentinel.yml
git commit -m "Add Sentinel build workflow"
git push
```

#### 2. בדוק שהבנייה הצליחה

1. לך ל-GitHub repository
2. לחץ על "Actions"
3. בדוק שה-workflow "Build Sentinel Docker Image" רץ בהצלחה
4. לחץ על ה-run כדי לראות את ה-image שנבנה

#### 3. עדכן את ה-Deployment

ערוך את `k8s/sentinel/deployment.yaml`:

```yaml
image: ghcr.io/YOUR_GITHUB_USERNAME/automation-run-sentinel:latest
imagePullPolicy: Always
```

או עם Helm, עדכן את `helm/sentinel/values.yaml`:

```yaml
image:
  repository: ghcr.io/YOUR_GITHUB_USERNAME/automation-run-sentinel
  tag: latest
  pullPolicy: Always
```

#### 4. הוסף Image Pull Secret (אם צריך)

אם ה-image הוא private, צריך להוסיף secret:

```bash
# Create secret from GitHub token
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=YOUR_GITHUB_USERNAME \
  --docker-password=YOUR_GITHUB_TOKEN \
  --docker-email=YOUR_EMAIL \
  -n sentinel
```

ועדכן את ה-deployment:

```yaml
spec:
  template:
    spec:
      imagePullSecrets:
      - name: ghcr-secret
```

#### 5. פרוס

```bash
kubectl apply -k k8s/sentinel/
```

## אפשרות 2: שימוש ב-Jenkins

אם יש לך גישה ל-Jenkins, תוכל להוסיף stage לבניית ה-image:

```groovy
pipeline {
    agent any
    
    stages {
        stage('Build Sentinel Image') {
            steps {
                script {
                    sh '''
                        docker build -f Dockerfile.sentinel \
                          -t your-registry/automation-run-sentinel:latest .
                        docker push your-registry/automation-run-sentinel:latest
                    '''
                }
            }
        }
    }
}
```

## אפשרות 3: שימוש ב-Kubernetes ישירות (Kaniko)

אם יש לך גישה ל-Kubernetes, תוכל לבנות ישירות שם:

```bash
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: sentinel-builder
  namespace: sentinel
spec:
  containers:
  - name: kaniko
    image: gcr.io/kaniko-project/executor:latest
    args:
    - --dockerfile=Dockerfile.sentinel
    - --context=dir:///workspace
    - --destination=your-registry/automation-run-sentinel:latest
    volumeMounts:
    - name: source
      mountPath: /workspace
  volumes:
  - name: source
    persistentVolumeClaim:
      claimName: sentinel-source-pvc
EOF
```

## אפשרות 4: שימוש ב-Image קיים

אם יש לך image קיים ב-registry, פשוט עדכן את ה-deployment:

```yaml
image: your-existing-registry/automation-run-sentinel:latest
```

## המלצה

**השתמש ב-GitHub Actions** - זה הכי פשוט ואוטומטי:

1. Push את הקוד
2. ה-image נבנה אוטומטית
3. עדכן את ה-deployment להשתמש ב-image מה-registry
4. פרוס

## בדיקה

לאחר הפריסה, בדוק:

```bash
# Check pods
kubectl get pods -n sentinel

# Check image
kubectl describe pod -n sentinel -l app=automation-run-sentinel | grep Image

# Check logs
kubectl logs -n sentinel -l app=automation-run-sentinel
```

## פתרון בעיות

### Image לא נמצא

```bash
# בדוק את ה-image ב-registry
docker pull ghcr.io/YOUR_USERNAME/automation-run-sentinel:latest

# או בדוק ב-GitHub
# לך ל-Packages ב-GitHub repository
```

### Permission denied

אם ה-image הוא private, צריך:
1. ליצור GitHub token עם `read:packages` permission
2. ליצור secret ב-Kubernetes
3. להוסיף imagePullSecrets ל-deployment

### Build failed

בדוק את ה-logs ב-GitHub Actions:
1. לך ל-Actions ב-GitHub
2. לחץ על ה-workflow run
3. בדוק את ה-logs

## מה הלאה?

1. **Commit את ה-workflow**:
   ```bash
   git add .github/workflows/build-sentinel.yml
   git commit -m "Add Sentinel build workflow"
   git push
   ```

2. **חכה שהבנייה תסתיים** (כמה דקות)

3. **עדכן את ה-deployment** עם ה-image מה-registry

4. **פרוס**:
   ```bash
   kubectl apply -k k8s/sentinel/
   ```

זה הכל! אין צורך ב-Docker מקומי.

