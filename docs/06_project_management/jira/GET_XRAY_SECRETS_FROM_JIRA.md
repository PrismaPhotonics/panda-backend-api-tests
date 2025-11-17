# איך להשיג Xray Secrets דרך Jira
## How to Get Xray Secrets via Jira

**תאריך:** 2025-11-09  
**מטרה:** יצירת Xray Client ID/Secret דרך Jira UI

---

## 🎯 דרך Jira (אם יש לך גישה)

### שלב 1: היכנס ל-Jira

1. לך ל: https://prismaphotonics.atlassian.net
2. התחבר עם החשבון שלך (`roy.avrahami@prismaphotonics.com`)

### שלב 2: נווט ל-Xray Settings

**אפשרות A - דרך Apps:**

1. לחץ על **Settings** (⚙️) בפינה הימנית העליונה
2. בחר **Apps** → **Manage apps**
3. מצא **Xray** ברשימה
4. לחץ על **Xray** → **Settings** או **Configuration**
5. חפש **"API Keys"** או **"Cloud API"** או **"API Credentials"**

**אפשרות B - דרך Project Settings:**

1. לך לפרויקט **PZ**
2. לחץ על **Project Settings** (⚙️)
3. בתפריט השמאלי, חפש **Xray** או **Test Management**
4. לחץ על **Xray Settings**
5. חפש **"API Keys"** או **"Cloud API"**

**אפשרות C - דרך Xray Test Repository:**

1. לך ל: https://prismaphotonics.atlassian.net/projects/PZ?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.xpandit.plugins.xray__testing-board
2. לחץ על **Settings** או **Configuration**
3. חפש **"API Keys"** או **"Cloud API"**

### שלב 3: צור API Key

1. לחץ על **"Create API Key"** או **"Generate"** או **"New API Key"**
2. תן שם (למשל: "GitHub Actions Integration")
3. לחץ **"Generate"** או **"Create"**

### שלב 4: העתק את ה-Credentials

- **Client ID** - העתק את הערך
- **Client Secret** - העתק את הערך (⚠️ מוצג רק פעם אחת!)

---

## 🔍 אם לא מוצאים API Keys ב-Jira

אז צריך ליצור דרך **Xray Cloud Portal** ישירות:

### דרך Xray Cloud Portal:

1. לך ל: https://xray.cloud.getxray.app/
2. התחבר עם אותו חשבון Atlassian
3. לחץ על **Settings** (⚙️) → **API Keys**
4. לחץ **"Create API Key"**
5. העתק את ה-Client ID ו-Client Secret

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

## 🐛 אם אתה לא רואה את ה-API Keys

**אפשרויות:**

1. **פנה למנהל המערכת** - אולי צריך הרשאות נוספות
2. **נסה דרך Xray Cloud Portal ישירות** - https://xray.cloud.getxray.app/
3. **בדוק אם יש לך גישה ל-Xray** - אולי צריך רישיון או הרשאות

---

## 📞 עזרה

אם אתה לא מוצא את ה-API Keys:
- בדוק עם מנהל המערכת שלך ב-Atlassian
- נסה דרך Xray Cloud Portal ישירות
- בדוק את התיעוד של Xray: https://docs.getxray.app/

---

**עודכן:** 2025-11-09

