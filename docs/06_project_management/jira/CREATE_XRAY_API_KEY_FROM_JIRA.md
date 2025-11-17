# יצירת Xray API Key דרך Jira
## Create Xray API Key from Jira

**תאריך:** 2025-11-09  
**מטרה:** יצירת Xray Client ID/Secret דרך Jira UI

---

## 🎯 דרך מהירה

### שלב 1: היכנס ל-Jira

1. לך ל: https://prismaphotonics.atlassian.net
2. התחבר עם החשבון שלך

### שלב 2: נווט ל-Xray API Keys

**אפשרות A - דרך Jira Settings (מומלץ):**

1. לחץ על **Settings** (⚙️) בפינה הימנית העליונה
2. בחר **Apps** → **Manage apps**
3. מצא **Xray** ברשימה
4. לחץ על **Xray** → **Settings** או **Configuration**
5. בתפריט השמאלי, חפש **"API Keys"** או **"Global Settings"**
6. לחץ על **"API Keys"**

**אפשרות B - דרך URL ישיר:**

לך ישירות ל:
```
https://prismaphotonics.atlassian.net/plugins/servlet/ac/com.xpandit.plugins.xray/xray-global-settings-api-keys
```

או דרך Xray Cloud Portal:
```
https://us.xray.cloud.getxray.app/view/settings/global/apiKeys
```

### שלב 3: צור API Key

1. לחץ על **"Create API Key"** או **"Generate"** או **"New API Key"**
2. תן שם (למשל: "GitHub Actions Integration")
3. לחץ **"Generate"** או **"Create"**

### שלב 4: העתק את ה-Credentials

- **Client ID** - העתק את הערך (נראה כמו: `ABC123DEF456...`)
- **Client Secret** - העתק את הערך (נראה כמו: `XYZ789ABC123...`)
- ⚠️ **חשוב:** ה-Client Secret מוצג רק פעם אחת! העתק אותו מיד.

---

## 📋 דרך Jira Admin Menu

אם אתה Admin:

1. **Settings** → **Apps** → **Manage apps**
2. מצא **Xray** → לחץ עליו
3. בתפריט השמאלי, תחת **"Xray"**:
   - **Features**
   - **Miscellaneous**
   - **Test Types**
   - **Test Environments**
   - **API Keys** ← כאן!
   - **Storage**
   - וכו'...

4. לחץ על **"API Keys"**
5. לחץ **"Create API Key"**

---

## 🔍 אם אתה לא רואה את ה-API Keys

**בדוק:**

1. **הרשאות:** אתה צריך להיות **Admin** ב-Jira
2. **Xray מותקן:** ודא ש-Xray מותקן ופעיל
3. **גרסה:** ודא שיש לך גרסה תומכת (Xray Cloud)

**אם אין לך הרשאות Admin:**

- פנה למנהל המערכת שלך ב-Atlassian
- בקש ממנו ליצור API Key עבורך
- או בקש הרשאות Admin זמניות

---

## 📝 הוספה ל-GitHub Secrets

לאחר שיש לך את ה-Credentials:

1. לך ל-GitHub Repository → **Settings** → **Secrets** → **Actions**
2. לחץ **"New repository secret"**
3. הוסף:
   - **Name:** `XRAY_CLIENT_ID`
   - **Secret:** הדבק את ה-Client ID
4. לחץ **"Add secret"**
5. חזור על התהליך:
   - **Name:** `XRAY_CLIENT_SECRET`
   - **Secret:** הדבק את ה-Client Secret

---

## ✅ בדיקה

לאחר הוספת ה-Secrets, בדוק:

```bash
# בדיקה מקומית (אם יש לך את ה-Secrets)
export XRAY_CLIENT_ID="your_client_id"
export XRAY_CLIENT_SECRET="your_client_secret"
python scripts/xray/get_test_plan_tests.py --test-plan PZ-14024
```

או הרץ את ה-Workflow ב-GitHub Actions.

---

## 🎯 סיכום - איפה למצוא

### דרך Jira:
1. **Settings** → **Apps** → **Xray** → **Settings** → **API Keys**
2. או URL ישיר: `https://prismaphotonics.atlassian.net/plugins/servlet/ac/com.xpandit.plugins.xray/xray-global-settings-api-keys`

### דרך Xray Cloud Portal:
1. **https://us.xray.cloud.getxray.app/** → **Settings** → **API Keys**
2. או URL ישיר: `https://us.xray.cloud.getxray.app/view/settings/global/apiKeys`

---

## 📞 עזרה

אם אתה לא מוצא את ה-API Keys:
- בדוק שיש לך הרשאות Admin
- נסה דרך Xray Cloud Portal ישירות
- פנה למנהל המערכת שלך

---

**עודכן:** 2025-11-09

