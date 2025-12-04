# איך להפעיל את ה-GitHub Actions Workflow

## הבעיה
ה-workflow לא רץ כי הוא עדיין לא ב-GitHub! הקובץ קיים רק מקומית.

## פתרון - שלבים

### שלב 1: בדוק שאתה על branch הנכון

ה-workflow מוגדר לרוץ על `main` או `develop`. בדוק:

```powershell
git branch --show-current
```

אם אתה על branch אחר (כמו `chore/add-roy-tests`), יש שתי אפשרויות:

#### אפשרות א: שנה את ה-workflow לרוץ על כל branch

ערוך את `.github/workflows/build-sentinel.yml`:

```yaml
on:
  push:
    branches:
      - '*'  # כל branch
  workflow_dispatch:  # הרצה ידנית
```

#### אפשרות ב: העבר ל-main או develop

```powershell
git checkout main
# או
git checkout develop
```

### שלב 2: Commit את הקובץ

```powershell
# בדוק מה השתנה
git status

# הוסף את הקובץ
git add .github/workflows/build-sentinel.yml

# Commit
git commit -m "Add Sentinel Docker build workflow"

# Push ל-GitHub
git push
```

### שלב 3: הפעל ידנית (אם צריך)

אם אתה לא על main/develop, תוכל להפעיל ידנית:

1. לך ל-GitHub repository
2. לחץ על "Actions"
3. בחר "Build Sentinel Docker Image"
4. לחץ על "Run workflow"
5. בחר את ה-branch שלך
6. לחץ "Run workflow"

## בדיקה שהכל עובד

### 1. בדוק שהקובץ קיים ב-GitHub

לך ל: `https://github.com/YOUR_USERNAME/YOUR_REPO/blob/main/.github/workflows/build-sentinel.yml`

### 2. בדוק שה-workflow רץ

לך ל: `https://github.com/YOUR_USERNAME/YOUR_REPO/actions`

תראה את ה-workflow "Build Sentinel Docker Image" ברשימה.

### 3. בדוק את ה-Image

לאחר שהבנייה מסתיימת, ה-image יהיה ב:
- `ghcr.io/YOUR_USERNAME/automation-run-sentinel:latest`

לך ל: `https://github.com/YOUR_USERNAME/YOUR_REPO/pkgs/container/automation-run-sentinel`

## פתרון מהיר - הרצה ידנית

אם אתה רוצה להריץ עכשיו בלי לשנות branches:

1. **Commit ו-Push את הקובץ**:
   ```powershell
   git add .github/workflows/build-sentinel.yml
   git commit -m "Add Sentinel build workflow"
   git push
   ```

2. **לך ל-GitHub Actions**:
   - פתח את ה-repository ב-GitHub
   - לחץ על "Actions"
   - בחר "Build Sentinel Docker Image"
   - לחץ על "Run workflow"
   - בחר את ה-branch שלך
   - לחץ "Run workflow"

## אם זה עדיין לא עובד

### בדוק את ה-logs

1. לך ל-Actions ב-GitHub
2. לחץ על ה-workflow run
3. בדוק את ה-logs - מה השגיאה?

### בעיות נפוצות

1. **"Workflow file not found"**
   - הקובץ לא ב-GitHub - צריך לעשות push

2. **"No matching branches"**
   - אתה לא על branch הנכון - שנה את ה-workflow או העבר branch

3. **"Permission denied"**
   - צריך לאפשר write permissions ל-packages ב-GitHub

4. **"Dockerfile not found"**
   - בדוק ש-`Dockerfile.sentinel` קיים ב-root של ה-repository

## מה הלאה?

לאחר שה-workflow רץ בהצלחה:

1. **עדכן את ה-deployment** להשתמש ב-image:
   ```yaml
   image: ghcr.io/YOUR_USERNAME/automation-run-sentinel:latest
   ```

2. **פרוס**:
   ```powershell
   kubectl apply -k k8s/sentinel/
   ```

