# 📋 מדריך מלא: מה צריך למלא ב-mcp.json

**תאריך:** 2025-12-02  
**מטרה:** מדריך מפורט של כל מה שצריך למלא בקובץ `mcp.json`

---

## 📍 מיקום הקובץ

- **Windows:** `C:\Users\<USERNAME>\.cursor\mcp.json`
- **Mac/Linux:** `~/.cursor/mcp.json`

---

## ✅ שרתים שכבר מוגדרים נכון

### 1. **playwright** ✅
- מוגדר נכון, לא צריך שינויים

### 2. **pz_update_agent_mcp** ✅
- מוגדר נכון, לא צריך שינויים

### 3. **atlassian-rovo** ✅
- מוגדר נכון, לא צריך שינויים

### 4. **github** ✅
- מוגדר נכון, לא צריך שינויים

### 5. **github-actions** ✅
- מוגדר נכון, לא צריך שינויים

### 6. **bitbucket** ✅
- מוגדר נכון, לא צריך שינויים

### 7. **log-analyzer** ✅
- מוגדר נכון, לא צריך שינויים

---

## ⚠️ שרתים שצריך למלא/לתקן

### 1. **kubernetes** ⚠️

**סטטוס נוכחי:**
```json
"kubernetes": {
  "args": ["-y", "mcp-server-kubernetes"],
  "env": {},
  "command": "npx"
}
```

**✅ ההגדרה תקינה!** אבל יש בעיית חיבור ל-cluster.

**מה צריך לבדוק:**
1. **ודא ש-kubectl עובד:**
   ```bash
   kubectl version --client
   kubectl config current-context
   ```

2. **בדוק חיבור ל-cluster:**
   ```bash
   kubectl get nodes
   ```

3. **אם יש בעיית חיבור:**
   - בדוק שה-cluster פעיל
   - בדוק שה-kubeconfig נכון
   - אם יש מספר kubeconfig files, הוסף:
   ```json
   "env": {
     "KUBECONFIG": "C:\\Users\\roy.avrahami\\.kube\\config"
   }
   ```

**אופציונלי - מצב Non-Destructive (קריאה בלבד):**
אם אתה רוצה להגביל לפעולות קריאה בלבד:
```json
"kubernetes-readonly": {
  "command": "npx",
  "args": ["-y", "mcp-server-kubernetes"],
  "env": {
    "ALLOW_ONLY_NON_DESTRUCTIVE_TOOLS": "true"
  }
}
```

---

### 2. **slack** ❌ **צריך למלא!**

**סטטוס נוכחי:**
```json
"slack": {
  "args": ["-y", "@modelcontextprotocol/server-slack"],
  "env": {
    "SLACK_TEAM_ID": "YOUR_TEAM_ID_HERE",
    "SLACK_BOT_TOKEN": "YOUR_BOT_TOKEN_HERE"
  },
  "command": "npx"
}
```

**⚠️ צריך למלא 2 ערכים:**

#### שלב 1: קבלת Slack Bot Token

1. **היכנס ל-Slack API:**
   - לך ל-[https://api.slack.com/apps](https://api.slack.com/apps)
   - התחבר עם חשבון Slack שלך

2. **צור App חדש (או בחר קיים):**
   - לחץ על **"Create New App"**
   - בחר **"From scratch"**
   - תן שם ל-App (למשל: "Cursor MCP Integration")
   - בחר את ה-workspace שלך

3. **הגדר Bot Token Scopes:**
   - עבור ל-**"OAuth & Permissions"** בתפריט השמאלי
   - גלול למטה ל-**"Scopes"** → **"Bot Token Scopes"**
   - הוסף את ה-scopes הבאים:
     - `channels:read` - קריאת channels
     - `channels:history` - קריאת היסטוריית channels
     - `chat:write` - שליחת הודעות
     - `users:read` - קריאת מידע על משתמשים
     - `im:write` - שליחת הודעות ישירות
     - `im:read` - קריאת הודעות ישירות

4. **התקן את ה-App ל-Workspace:**
   - גלול למעלה ל-**"Install to Workspace"**
   - לחץ על הכפתור
   - אשר את ההרשאות

5. **קבל את ה-Bot Token:**
   - לאחר ההתקנה, תחזור ל-**"OAuth & Permissions"**
   - תמצא את **"Bot User OAuth Token"** (מתחיל ב-`xoxb-`)
   - העתק את ה-token (תזדקק לו)

#### שלב 2: קבלת Team ID

**אפשרות 1: מה-URL של ה-workspace**
- פתח את ה-workspace שלך ב-Slack
- ה-URL נראה כך: `https://YOUR-WORKSPACE.slack.com`
- ה-Team ID נמצא ב-URL או במידע של ה-workspace (מתחיל ב-`T`)

**אפשרות 2: דרך Slack API**
- לך ל-[https://api.slack.com/methods/auth.test](https://api.slack.com/methods/auth.test)
- השתמש ב-Bot Token שלך
- ה-Team ID יופיע בתשובה

**אפשרות 3: דרך Slack App Settings**
- ב-[Slack API Apps](https://api.slack.com/apps)
- בחר את ה-App שלך
- ה-Team ID מופיע במידע הכללי של ה-App

#### שלב 3: עדכון הקובץ

החלף את הערכים בקובץ `mcp.json`:

```json
"slack": {
  "args": ["-y", "@modelcontextprotocol/server-slack"],
  "env": {
    "SLACK_BOT_TOKEN": "xoxb-YOUR-SLACK-BOT-TOKEN-HERE",
    "SLACK_TEAM_ID": "T01234567"
  },
  "command": "npx"
}
```

**⚠️ חשוב:**
- ה-Bot Token מתחיל ב-`יל ב-`xoxb-`
- ה-Team ID צריך להיות מתחיל ב-`T`
- אל תשתף את ה-tokens - זה כמו סיסמה!

---

## 📝 סיכום - מה צריך לעשות

### Kubernetes MCP:
- ✅ ההגדרה תקינה
- ⚠️ צריך לבדוק חיבור ל-cluster
- אם יש בעיה, הוסף `KUBECONFIG` ב-`env` אם צריך

### Slack MCP:
- ❌ צריך למלא `SLACK_BOT_TOKEN`
- ❌ צריך למלא `SLACK_TEAM_ID`
- עקוב אחרי השלבים למעלה

---

## 🔒 אבטחה

**⚠️ חשוב מאוד:**
- אל תעלה את `mcp.json` ל-Git אם יש בו tokens
- ודא ש-`.cursor/mcp.json` ב-`.gitignore`
- אם token נחשף, בטל אותו מיד ב-Slack API

---

## ✅ אחרי המילוי

1. **שמור את הקובץ** (Ctrl+S)
2. **הפעל מחדש את Cursor** (או לחץ על **Reload Window**)
3. **בדוק ב-Cursor Settings** (Ctrl+,) → חפש "MCP"
4. **ודא** שכל השרתים מופיעים ברשימה

---

## 🧪 בדיקות

### Kubernetes:
```
"List all pods in the default namespace"
"Show me all deployments"
```

### Slack:
```
"List all channels in my Slack workspace"
"Send a message to #general saying 'Hello from Cursor!'"
```

---

**עודכן לאחרונה:** 2025-12-02

