# איך להשיג Xray Secrets ל-GitHub Actions
## How to Get Xray Secrets for GitHub Actions

**תאריך:** 2025-11-09  
**מטרה:** הגדרת XRAY_CLIENT_ID ו-XRAY_CLIENT_SECRET ב-GitHub Secrets

---

## 🎯 מה צריך

1. **XRAY_CLIENT_ID** - Client ID מ-Xray Cloud
2. **XRAY_CLIENT_SECRET** - Client Secret מ-Xray Cloud

---

## 📋 שלב 1: יצירת API Keys ב-Xray Cloud

### דרך 1: דרך Xray Cloud Portal (מומלץ)

1. **היכנס ל-Xray Cloud:**
   - לך ל: https://xray.cloud.getxray.app/
   - התחבר עם חשבון ה-Atlassian שלך

2. **נווט ל-API Keys:**
   - לחץ על **Settings** (⚙️) בפינה הימנית העליונה
   - בחר **API Keys** או **Cloud API**
   - או לך ישירות ל: https://xray.cloud.getxray.app/settings/api-keys

3. **צור API Key חדש:**
   - לחץ על **"Create API Key"** או **"Generate"**
   - תן שם ל-API Key (למשל: "GitHub Actions Integration")
   - לחץ **"Generate"** או **"Create"**

4. **העתק את ה-Credentials:**
   - **Client ID** - העתק את הערך (נראה כמו: `ABC123DEF456...`)
   - **Client Secret** - העתק את הערך (נראה כמו: `XYZ789ABC123...`)
   - ⚠️ **חשוב:** ה-Client Secret מוצג רק פעם אחת! העתק אותו מיד.

### דרך 2: דרך Jira (אם יש גישה)

1. **היכנס ל-Jira:**
   - לך ל: https://prismaphotonics.atlassian.net
   - התחבר

2. **נווט ל-Xray Settings:**
   - לחץ על **Settings** (⚙️) → **Apps**
   - מצא **Xray** → לחץ עליו
   - בחר **Settings** או **Configuration**

3. **צור API Key:**
   - חפש **"API Keys"** או **"Cloud API"**
   - לחץ **"Create"** או **"Generate"**
   - העתק את ה-Client ID ו-Client Secret

---

## 📋 שלב 2: הוספת Secrets ל-GitHub

### דרך GitHub Web UI (מומלץ)

1. **היכנס ל-GitHub Repository:**
   - לך ל: `https://github.com/YOUR_ORG/focus_server_automation`
   - ודא שיש לך הרשאות Admin או Maintainer

2. **נווט ל-Secrets:**
   - לחץ על **Settings** (בתפריט העליון)
   - בתפריט השמאלי, לחץ על **Secrets and variables** → **Actions**
   - או לך ישירות ל: `https://github.com/YOUR_ORG/focus_server_automation/settings/secrets/actions`

3. **הוסף Secret חדש:**
   - לחץ על **"New repository secret"**
   
   **הוסף את הראשון:**
   - **Name:** `XRAY_CLIENT_ID`
   - **Secret:** הדבק את ה-Client ID שהעתקת
   - לחץ **"Add secret"**
   
   **הוסף את השני:**
   - לחץ שוב על **"New repository secret"**
   - **Name:** `XRAY_CLIENT_SECRET`
   - **Secret:** הדבק את ה-Client Secret שהעתקת
   - לחץ **"Add secret"**

### דרך GitHub CLI (אלטרנטיבה)

אם יש לך GitHub CLI מותקן:

```bash
# הוסף XRAY_CLIENT_ID
gh secret set XRAY_CLIENT_ID --repo YOUR_ORG/focus_server_automation

# הוסף XRAY_CLIENT_SECRET
gh secret set XRAY_CLIENT_SECRET --repo YOUR_ORG/focus_server_automation
```

---

## ✅ אימות שהכל עובד

### בדיקה מקומית

1. **הגדר Environment Variables:**
   ```bash
   export XRAY_CLIENT_ID="your_client_id_here"
   export XRAY_CLIENT_SECRET="your_client_secret_here"
   ```

2. **בדוק אימות:**
   ```bash
   python - << 'PY'
   import os
   import requests
   
   client_id = os.getenv("XRAY_CLIENT_ID")
   client_secret = os.getenv("XRAY_CLIENT_SECRET")
   
   response = requests.post(
       "https://xray.cloud.getxray.app/api/v2/authenticate",
       json={"client_id": client_id, "client_secret": client_secret}
   )
   
   if response.status_code == 200:
       print("✅ Authentication successful!")
       print(f"Token: {response.text[:50]}...")
   else:
       print(f"❌ Authentication failed: {response.status_code}")
       print(response.text)
   PY
   ```

3. **בדוק שליפת Test Plan:**
   ```bash
   python scripts/xray/get_test_plan_tests.py --test-plan PZ-14024
   ```

### בדיקה ב-GitHub Actions

1. **הרץ Workflow ידנית:**
   - לך ל-GitHub → Actions
   - בחר "Xray Full Integration - Test Execution"
   - לחץ "Run workflow"
   - בדוק שהריצה מצליחה

2. **בדוק את הלוגים:**
   - אם יש שגיאת אימות, תראה:
     ```
     ❌ Authentication failed: 401
     ```
   - אם הכל תקין, תראה:
     ```
     ✅ Authenticating with Xray Cloud...
     ✅ Authentication successful
     ```

---

## 🔒 אבטחה

### Best Practices:

1. ✅ **אל תעלה Secrets ל-Git** - הם כבר ב-`.gitignore`
2. ✅ **השתמש ב-Repository Secrets** - לא Organization Secrets (אלא אם צריך)
3. ✅ **הגבל גישה** - רק אנשים שצריכים יכולים לראות/לערוך Secrets
4. ✅ **רוטציה תקופתית** - החלף Secrets כל 6-12 חודשים

### אם Secrets נחשפו:

1. **מחק את ה-Secret הישן** ב-GitHub
2. **צור API Key חדש** ב-Xray
3. **הוסף את ה-Secret החדש** ב-GitHub
4. **בדוק שהכל עובד**

---

## 🐛 פתרון בעיות

### בעיה: "Missing XRAY_CLIENT_ID or XRAY_CLIENT_SECRET"

**פתרון:**
1. ודא שה-Secrets מוגדרים ב-GitHub → Settings → Secrets → Actions
2. ודא שהשמות נכונים: `XRAY_CLIENT_ID` ו-`XRAY_CLIENT_SECRET` (בדיוק!)
3. ודא שיש רווחים/תווים מיותרים

### בעיה: "Authentication failed: 401"

**פתרון:**
1. בדוק שה-Client ID ו-Client Secret נכונים
2. ודא שהעתקת את כל ה-Secret (לפעמים נחתך)
3. נסה ליצור API Key חדש ב-Xray
4. ודא שה-API Key לא פג תוקף

### בעיה: "Authentication failed: 403"

**פתרון:**
1. בדוק שיש לך הרשאות ב-Xray
2. ודא שה-API Key לא הוגבל ל-IPs מסוימים
3. בדוק שה-Account פעיל

---

## 📞 עזרה נוספת

### קישורים שימושיים:

- **Xray Cloud Portal:** https://xray.cloud.getxray.app/
- **Xray API Documentation:** https://docs.getxray.app/display/XRAYCLOUD/REST+API
- **GitHub Secrets Documentation:** https://docs.github.com/en/actions/security-guides/encrypted-secrets

### תמיכה:

אם יש בעיות:
1. בדוק את הלוגים ב-GitHub Actions
2. נסה להריץ את הסקריפטים מקומית עם Environment Variables
3. בדוק את ה-Xray Cloud Portal שהכל תקין

---

## 📝 Checklist

לפני שימוש:

- [ ] יצרת API Key ב-Xray Cloud
- [ ] העתקת Client ID
- [ ] העתקת Client Secret
- [ ] הוספת `XRAY_CLIENT_ID` ל-GitHub Secrets
- [ ] הוספת `XRAY_CLIENT_SECRET` ל-GitHub Secrets
- [ ] בדקת אימות מקומי (אופציונלי)
- [ ] הרצת Workflow ב-GitHub Actions לבדיקה

---

**עודכן:** 2025-11-09

