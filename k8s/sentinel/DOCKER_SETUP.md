# Docker Setup Guide for Windows

מדריך להתקנת Docker ב-Windows עבור בניית Sentinel image.

## אפשרות 1: Docker Desktop (מומלץ)

### התקנה

1. הורד Docker Desktop:
   - https://www.docker.com/products/docker-desktop/
   - בחר את הגרסה ל-Windows

2. התקן את Docker Desktop:
   - הרץ את ה-installer
   - הפעל מחדש את המחשב אם נדרש
   - פתח את Docker Desktop

3. בדוק שההתקנה הצליחה:
   ```powershell
   docker --version
   docker ps
   ```

### שימוש

לאחר ההתקנה, תוכל לבנות את ה-image:

```powershell
# בניית Image
docker build -f Dockerfile.sentinel -t automation-run-sentinel:latest .

# בדיקה
docker images | Select-String "automation-run-sentinel"

# הרצה מקומית (אופציונלי)
docker run -p 5000:5000 automation-run-sentinel:latest
```

## אפשרות 2: Podman (חלופה ל-Docker)

אם אתה מעדיף לא להתקין Docker Desktop:

1. התקן Podman:
   ```powershell
   # דרך Chocolatey
   choco install podman

   # או דרך winget
   winget install RedHat.Podman
   ```

2. השתמש ב-Podman במקום Docker:
   ```powershell
   podman build -f Dockerfile.sentinel -t automation-run-sentinel:latest .
   ```

## אפשרות 3: בנייה ב-CI/CD או Remote Server

אם יש לך גישה ל-CI/CD pipeline או לשרת מרוחק:

### GitHub Actions

```yaml
# .github/workflows/build-sentinel.yml
name: Build Sentinel Image
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: |
          docker build -f Dockerfile.sentinel -t automation-run-sentinel:latest .
      - name: Push to registry
        run: |
          docker tag automation-run-sentinel:latest your-registry/automation-run-sentinel:latest
          docker push your-registry/automation-run-sentinel:latest
```

### Jenkins

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'docker build -f Dockerfile.sentinel -t automation-run-sentinel:latest .'
            }
        }
        stage('Push') {
            steps {
                sh 'docker tag automation-run-sentinel:latest your-registry/automation-run-sentinel:latest'
                sh 'docker push your-registry/automation-run-sentinel:latest'
            }
        }
    }
}
```

## אפשרות 4: שימוש ב-Image קיים

אם יש לך גישה ל-registry עם image קיים, תוכל לדלג על הבנייה:

```yaml
# עדכן deployment.yaml
image: your-registry/automation-run-sentinel:latest
imagePullPolicy: Always
```

## אפשרות 5: בנייה ב-Kubernetes ישירות

אם יש לך גישה ל-Kubernetes cluster, תוכל לבנות ישירות שם:

```bash
# השתמש ב-Kaniko או BuildKit
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: sentinel-builder
spec:
  containers:
  - name: kaniko
    image: gcr.io/kaniko-project/executor:latest
    args:
    - --dockerfile=Dockerfile.sentinel
    - --context=.
    - --destination=your-registry/automation-run-sentinel:latest
    volumeMounts:
    - name: source
      mountPath: /workspace
  volumes:
  - name: source
    hostPath:
      path: /path/to/source
EOF
```

## פתרון בעיות

### Docker לא מזוהה ב-PowerShell

```powershell
# בדוק אם Docker ב-PATH
$env:PATH -split ';' | Select-String "docker"

# הוסף ל-PATH אם צריך
$env:PATH += ";C:\Program Files\Docker\Docker\resources\bin"
```

### Docker Desktop לא מתחיל

1. בדוק ש-WSL2 מותקן:
   ```powershell
   wsl --status
   ```

2. הפעל מחדש את Docker Desktop

3. בדוק את ה-logs:
   - פתח Docker Desktop
   - Settings > Troubleshoot > View logs

### בעיות עם Virtualization

אם יש לך Hyper-V או VirtualBox פעילים, ייתכן שיהיו קונפליקטים. נסה:

1. השבת Hyper-V זמנית
2. או השתמש ב-Docker Desktop עם WSL2 backend

## המלצות

1. **לפיתוח מקומי**: השתמש ב-Docker Desktop
2. **ל-Production**: בנה ב-CI/CD pipeline
3. **לבדיקות**: השתמש ב-image קיים מ-registry

## מה הלאה?

לאחר שהתקנת Docker:

1. בנה את ה-image:
   ```powershell
   docker build -f Dockerfile.sentinel -t automation-run-sentinel:latest .
   ```

2. בדוק שהכל עובד:
   ```powershell
   docker run -p 5000:5000 automation-run-sentinel:latest
   ```

3. המשך לפריסה ב-Kubernetes לפי המדריך ב-`README.md`

