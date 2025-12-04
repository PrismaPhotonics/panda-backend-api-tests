# 🚀 מדריך הגדרת Slack MCP Server

**תאריך:** 2025-12-02  
**סטטוס:** ✅ מדריך מלא

---

## 📋 מבוא

**מה זה Slack MCP Server:**
- כלי לאינטגרציה עם Slack ישירות מ-Cursor
- מאפשר לשלוח הודעות, לנהל channels, ולעבוד עם Slack workspaces
- עובד עם כל Slack workspace (אין צורך באישור מנהל)

**איך זה עובד:**
- השרת מתחבר ל-Slack דרך Slack API
- משתמש ב-Slack token לאימות
- מאפשר לשלוח הודעות ולנהל תקשורת דרך שאלות טבעיות ב-Cursor

**יתרונות:**
- ✅ אין צורך ב-bot או אישור מנהל workspace
- ✅ עובד עם stdio ו-SSE transports
- ✅ תמיכה מלאה ב-channels, messages, ו-users

---

## 🎯 דרישות מוקדמות

### לפני שמתחילים:

1. ✅ **Slack workspace** פעיל
2. ✅ **Slack account** עם גישה ל-workspace
3. ✅ **Slack token** (User OAuth Token או Bot Token)
4. ✅ **Cursor** מותקן (או כלי MCP תומך אחר)
5. ✅ **Node.js v18+** (להפעלת `npx`)

---

## 🔑 קבלת Slack Token

### אפשרות 1: User OAuth Token (מומלץ)

**שלבים:**

1. **היכנס ל-Slack API:**
   - לך ל-[https://api.slack.com/apps](https://api.slack.com/apps)
   - התחבר עם חשבון Slack שלך

2. **צור App חדש:**
   - לחץ על **"Create New App"**
   - בחר **"From scratch"**
   - תן שם ל-App (למשל: "Cursor MCP Integration")
   - בחר את ה-workspace שלך

3. **הגדר OAuth Scopes:**
   - עבור ל-**"OAuth & Permissions"** בתפריט השמאלי
   - גלול למטה ל-**"Scopes"** → **"User Token Scopes"**
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

5. **קבל את ה-Token:**
   - לאחר ההתקנה, תחזור ל-**"OAuth & Permissions"**
   - תמצא את **"Bot User OAuth Token"** (מתחיל ב-`xoxb-`)
   - העתק את ה-token (תזדקק לו בהמשך)

6. **קבל את ה-Team ID:**
   - לך ל-[https://api.slack.com/methods/auth.test](https://api.slack.com/methods/auth.test)
   - או פתח את ה-workspace שלך ב-Slack
   - ה-Team ID נמצא ב-URL: `https://YOUR-WORKSPACE.slack.com` (ה-ID מתחיל ב-`T`)
   - או השתמש ב-[Slack API auth.test](https://api.slack.com/methods/auth.test) עם ה-token שלך

**⚠️ הערה חשובה:** השרת דורש **Bot Token** (לא User Token), ולכן תמיד תשתמש ב-**"Bot User OAuth Token"** שמתחיל ב-`xoxb-`.

---

## 🔧 הגדרה ב-Cursor

### שלב 1: פתיחת קובץ ההגדרות

1. פתח את קובץ ההגדרות של Cursor:
   - **Windows:** `C:\Users\<USERNAME>\.cursor\mcp.json`
   - **Mac/Linux:** `~/.cursor/mcp.json`

2. או פתח את הקובץ ישירות ב-Cursor:
   - לחץ על **File → Open File**
   - נווט ל-`.cursor\mcp.json` בתיקיית הבית שלך

### שלב 2: הוספת הגדרת Slack MCP Server

**הוסף את ההגדרה הבאה לקובץ `mcp.json`:**

```json
{
  "mcpServers": {
    "slack": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-slack"
      ],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-your-bot-token-here",
        "SLACK_TEAM_ID": "T00000000"
      }
    }
  }
}
```

**⚠️ חשוב:** 
- החלף את `xoxb-your-bot-token-here` ב-Bot Token האמיתי שלך (מתחיל ב-`xoxb-`)
- החלף את `T00000000` ב-Team ID האמיתי שלך (מתחיל ב-`T`)

**דוגמה לקובץ מלא עם שרתים נוספים:**

```json
{
  "mcpServers": {
    "atlassian-rovo": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.atlassian.com/v1/sse"],
      "env": {}
    },
        "slack": {
          "command": "npx",
          "args": ["-y", "@modelcontextprotocol/server-slack"],
          "env": {
            "SLACK_BOT_TOKEN": "xoxb-your-bot-token-here",
            "SLACK_TEAM_ID": "T00000000"
          }
        }
  }
}
```

### שלב 3: אבטחת ה-Token

**⚠️ חשוב לאבטחה:**

1. **אל תשתף את ה-token** - זה כמו סיסמה
2. **אל תעלה את `mcp.json` ל-Git** - ודא שהוא ב-`.gitignore`
3. **אם ה-token נחשף**, בטל אותו מיד ב-Slack API

**דוגמה ל-`.gitignore`:**

```
.cursor/mcp.json
```

### שלב 4: שמירה והפעלה מחדש

1. **שמור את הקובץ** (Ctrl+S)
2. **הפעל מחדש את Cursor** (או לחץ על **Reload Window**)
3. Cursor יטען את שרתי MCP החדשים אוטומטית

---

## ✅ אימות שההגדרה עובדת

### בדיקה 1: וידוא שהשרת נטען ב-Cursor

1. **פתח את Cursor Settings** (Ctrl+,)
2. **חפש "MCP"** או **"Model Context Protocol"**
3. **בדוק** ש-**"slack"** מופיע ברשימת שרתי MCP
4. **ודא** שהסטטוס הוא **"Connected"** או **"Running"**

### בדיקה 2: בדיקה דרך Chat ב-Cursor

1. **פתח Chat** ב-Cursor (Ctrl+L)
2. **נסה שאלות** כמו:
   ```
   "List all channels in my Slack workspace"
   "Send a message to #general saying 'Hello from Cursor!'"
   "Show me recent messages from #dev-team"
   "List all users in my workspace"
   ```
3. **אם זה עובד**, תראה תשובה עם נתונים מ-Slack
4. **אם לא**, תראה הודעת שגיאה (בדוק את הלוגים)

### בדיקה 3: בדיקת לוגים (אם יש בעיות)

1. **פתח את Developer Tools** ב-Cursor (Ctrl+Shift+I)
2. **עבור לטאב "Console"**
3. **חפש הודעות** הקשורות ל-MCP או Slack
4. **אם יש שגיאות**, תראה אותן כאן

---

## 🎨 דוגמאות שימוש

### ניהול Channels:

```
"List all channels in my workspace"
"Show me channels I'm a member of"
"Join channel #dev-team"
"Leave channel #random"
"Create a new channel called 'cursor-automation'"
```

### שליחת הודעות:

```
"Send a message to #general saying 'Hello team!'"
"Send a message to @username saying 'Check this out'"
"Post a message to #dev-team with the text 'Deployment completed successfully'"
```

### קריאת הודעות:

```
"Show me recent messages from #general"
"Get the last 10 messages from #dev-team"
"Show me messages from @username"
```

### ניהול משתמשים:

```
"List all users in my workspace"
"Show me user details for @username"
"Find users with the name 'John'"
```

### ניהול DMs (Direct Messages):

```
"Send a DM to @username saying 'Hi there!'"
"Show me recent DMs"
"List all my conversations"
```

### אינטגרציה עם פרויקט:

```
"Send a message to #dev-team about the test results"
"Notify #general that the deployment is complete"
"Post test failure summary to #qa-team"
```

---

## ⚠️ בעיות נפוצות ופתרונות

### בעיה 1: "Invalid token" או "not_authed"

**פתרון:**
1. ודא שה-**Bot Token** נכון והועתק במלואו (מתחיל ב-`xoxb-`)
2. ודא שה-**Team ID** נכון (מתחיל ב-`T`)
3. ודא שה-token לא פג תוקף (אם שינית סיסמה, צריך token חדש)
4. בדוק שה-App מותקן ב-workspace:
   - לך ל-[https://api.slack.com/apps](https://api.slack.com/apps)
   - בחר את ה-App שלך
   - ודא שהוא מותקן ב-workspace
5. ודא שאתה משתמש ב-**Bot Token** ולא ב-User Token

### בעיה 2: "missing_scope" או "insufficient_scope"

**פתרון:**
- הוסף את ה-scopes החסרים:
  1. לך ל-[https://api.slack.com/apps](https://api.slack.com/apps)
  2. בחר את ה-App שלך
  3. עבור ל-**"OAuth & Permissions"**
  4. הוסף את ה-scopes הנדרשים
  5. **התקן מחדש** את ה-App ל-workspace (חשוב!)
  6. קבל token חדש

### בעיה 3: "channel_not_found"

**פתרון:**
- ודא שאתה חבר ב-channel
- נסה להצטרף ל-channel ידנית ב-Slack
- או בקש גישה דרך:
  ```
  "Join channel #channel-name"
  ```

### בעיה 4: השרת לא נטען ב-Cursor

**פתרון:**
1. ודא ש-Node.js v18+ מותקן:
   ```bash
   node --version
   ```
2. נסה להריץ את השרת ידנית:
   ```bash
   SLACK_TOKEN=xoxp-your-token npx -y @modelcontextprotocol/server-slack
   ```
3. בדוק את הלוגים ב-Cursor Developer Tools

### בעיה 5: Token נחשף או נדרש token חדש

**פתרון:**
1. **בטל את ה-token הישן:**
   - לך ל-[https://api.slack.com/apps](https://api.slack.com/apps)
   - בחר את ה-App שלך
   - עבור ל-**"OAuth & Permissions"**
   - לחץ על **"Revoke Token"**

2. **קבל token חדש:**
   - התקן מחדש את ה-App ל-workspace
   - העתק את ה-**Bot Token** החדש (מתחיל ב-`xoxb-`)
   - ודא שיש לך את ה-**Team ID** (מתחיל ב-`T`)
   - עדכן את `mcp.json` עם שני הערכים

---

## 🔒 אבטחה והרשאות

### איך זה עובד:

1. ✅ ה-token משמש לאימות עם Slack API
2. ✅ כל פעולה מתבצעת עם ההרשאות של המשתמש/בוט שלך
3. ✅ ה-token מאוחסן מקומית ב-`mcp.json`
4. ✅ כל פעולה מתועדת ב-Slack audit logs

### ניהול הרשאות:

- **Scopes** קובעים מה אתה יכול לעשות
- **User Token** נותן הרשאות של המשתמש שלך
- **Bot Token** נותן הרשאות של ה-Bot

### המלצות אבטחה:

- ✅ **אל תשתף tokens** - זה כמו סיסמה
- ✅ **אל תעלה `mcp.json` ל-Git** - ודא שהוא ב-`.gitignore`
- ✅ **בטל tokens ישנים** אם הם לא בשימוש
- ✅ **השתמש ב-Bot Token** אם אפשר (יותר בטוח)
- ✅ **הגבל scopes** - אל תוסיף scopes מיותרים

### הגנה על Token:

**דוגמה ל-`.gitignore`:**

```
# Cursor MCP configuration (may contain tokens)
.cursor/mcp.json
```

**או אם אתה צריך לשתף את הקובץ:**

```json
{
  "mcpServers": {
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_TOKEN": "${SLACK_TOKEN}"
      }
    }
  }
}
```

ואז הגדר את המשתנה בסביבה:

```bash
# Windows PowerShell
$env:SLACK_TOKEN="xoxp-your-token"

# Mac/Linux
export SLACK_TOKEN="xoxp-your-token"
```

---

## 📚 משאבים נוספים

### תיעוד רשמי:

- [Slack MCP Server](https://cursor.directory/mcp/slack)
- [Slack API Documentation](https://api.slack.com/)
- [Slack OAuth Guide](https://api.slack.com/authentication/oauth-v2)

### קישורים שימושיים:

- [Slack API Methods](https://api.slack.com/methods)
- [Slack Scopes](https://api.slack.com/scopes)
- [Slack App Management](https://api.slack.com/apps)

---

## 🎯 סיכום

**מה למדנו:**

1. ✅ Slack MCP Server מאפשר אינטגרציה עם Slack ישירות מ-Cursor
2. ✅ מתחברים אליו דרך Cursor על ידי עריכת קובץ `mcp.json`
3. ✅ צריך Slack token (User OAuth או Bot Token)
4. ✅ ניתן לשלוח הודעות ולנהל תקשורת דרך שאלות טבעיות

**השלבים הבאים:**

1. ✅ **קבלת Slack token** מ-Slack API
2. ✅ **הוספת ההגדרה** ל-`mcp.json`
3. ⏳ **הפעלה מחדש** של Cursor
4. ⏳ **בדיקה** שהשרת נטען בהצלחה
5. ⏳ **שימוש** בשאלות טבעיות לניהול Slack

---

## 📝 הערות טכניות

### מיקום קובץ ההגדרות:

- **Windows:** `C:\Users\<USERNAME>\.cursor\mcp.json`
- **Mac:** `~/.cursor/mcp.json`
- **Linux:** `~/.cursor/mcp.json`

### דרישות:

- ✅ **Node.js v18+** (להפעלת `npx`)
- ✅ **Slack workspace** פעיל
- ✅ **Slack token** (User OAuth או Bot Token)
- ✅ **גישה לאינטרנט** (לחיבור ל-Slack API)

### סוגי Tokens:

- **Bot User OAuth Token** (`xoxb-`): **זה מה שצריך!** הרשאות של ה-Bot
- **User OAuth Token** (`xoxp-`): לא נתמך על ידי השרת הזה
- **App-Level Token** (`xapp-`): לא מתאים לשימוש זה

**⚠️ חשוב:** השרת דורש **Bot Token** (`xoxb-`) ו-**Team ID** (`T`).

---

**עודכן לאחרונה:** 2025-12-02  
**גרסה:** 1.0


