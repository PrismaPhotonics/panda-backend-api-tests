# 🚀 מדריך הגדרת Atlassian Rovo MCP Server

**תאריך:** 2025-11-09  
**סטטוס:** ✅ מדריך מלא

---

## 📋 מבוא

**חשוב להבין:** Atlassian Rovo MCP Server **אינו תוכנה שמורידים** - זה שירות ענן (cloud-based service) שמתחבר אליו דרך OAuth 2.1.

**איך זה עובד:**
- השרת נמצא ב-`https://mcp.atlassian.com/v1/sse`
- מתחברים אליו דרך כלי MCP תומך (כמו Cursor)
- עוברים תהליך OAuth 2.1 בדפדפן
- מקבלים גישה לנתונים מ-Jira, Confluence, ו-Compass

---

## 🎯 דרישות מוקדמות

### לפני שמתחילים:

1. ✅ **אתר Atlassian Cloud** עם Jira, Confluence, או Compass
2. ✅ **Cursor** מותקן (או כלי MCP תומך אחר)
3. ✅ **דפדפן מודרני** להשלמת תהליך OAuth
4. ✅ **גישה לאתר Atlassian** שלך

---

## 🔧 הגדרה ב-Cursor

### שלב 1: פתיחת קובץ ההגדרות

1. פתח את קובץ ההגדרות של Cursor:
   - **Windows:** `C:\Users\<USERNAME>\.cursor\mcp.json`
   - **Mac/Linux:** `~/.cursor/mcp.json`

2. או פתח את הקובץ ישירות ב-Cursor:
   - לחץ על **File → Open File**
   - נווט ל-`.cursor\mcp.json` בתיקיית הבית שלך

### שלב 2: הוספת הגדרת Atlassian Rovo MCP Server

**הוסף את ההגדרה הבאה לקובץ `mcp.json`:**

```json
{
  "mcpServers": {
    "atlassian-rovo": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.atlassian.com/v1/sse"
      ],
      "env": {}
    }
  }
}
```

**⚠️ חשוב:** השתמש ב-`mcp-remote` (לא `@modelcontextprotocol/server-remote` - החבילה הזו לא קיימת ב-npm)

**דוגמה לקובץ מלא עם שרתים נוספים:**
```json
{
  "mcpServers": {
    "playwright": {
      "args": [
        "@playwright/mcp@latest",
        "--isolated"
      ],
      "command": "npx"
    },
    "atlassian-rovo": {
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.atlassian.com/v1/sse"
      ],
      "command": "npx",
      "env": {}
    }
  }
}
```

### שלב 3: שמירה והפעלה מחדש

1. **שמור את הקובץ** (Ctrl+S)
2. **הפעל מחדש את Cursor** (או לחץ על **Reload Window**)
3. Cursor יטען את שרתי MCP החדשים אוטומטית

---

## 🔐 תהליך האימות (OAuth 2.1)

### שלב 1: הפעלת החיבור

1. **פתח Chat ב-Cursor** (Ctrl+L או Cmd+L)
2. **נסה לשאול שאלה** שדורשת גישה ל-Jira/Confluence, למשל:
   ```
   "Find all open bugs in my Jira project"
   ```
3. **Cursor יזהה** שצריך להתחבר ל-Atlassian
4. **יפתח דפדפן** עם דף התחברות של Atlassian

### שלב 2: התחברות ל-Atlassian

1. **התחבר** עם חשבון Atlassian שלך
2. **אשר את ההרשאות** הנדרשות:
   - ✅ גישה ל-Jira
   - ✅ גישה ל-Confluence
   - ✅ גישה ל-Compass (אם רלוונטי)
3. **לחץ על "Authorize"** או "Allow"

### שלב 3: אישור ההתקנה

1. **לאחר ההתחברות**, תועבר חזרה ל-Cursor
2. **תראה הודעה** שהחיבור הצליח (או שהשאלה שלך תתחיל להיענות)
3. **האפליקציה תופיע** ב-**Connected Apps** באתר Atlassian שלך:
   - היכנס ל-**Atlassian Admin**
   - עבור ל-**Manage apps** → **Connected apps**
   - תראה: **"Atlassian Rovo MCP Server"** ברשימה

---

## ✅ אימות שההגדרה עובדת

### בדיקה 1: וידוא שהשרת נטען ב-Cursor

1. **פתח את Cursor Settings** (Ctrl+,)
2. **חפש "MCP"** או **"Model Context Protocol"**
3. **בדוק** ש-**"atlassian-rovo"** מופיע ברשימת שרתי MCP
4. **ודא** שהסטטוס הוא **"Connected"** או **"Running"**

### בדיקה 2: בדיקה דרך Chat ב-Cursor

1. **פתח Chat** ב-Cursor (Ctrl+L)
2. **נסה שאלות** כמו:
   ```
   "Find all open bugs in my Jira project"
   "What Jira issues are assigned to me?"
   "List all Jira projects I have access to"
   ```
3. **אם זה עובד**, תראה תשובה עם נתונים מ-Jira
4. **אם לא**, תראה הודעה שמבקשת להתחבר (ואז תעבור תהליך OAuth)

### בדיקה 3: בדיקה באתר Atlassian

1. **היכנס** ל-**Atlassian Admin** (אתר Atlassian שלך)
2. **עבור** ל-**Manage apps** → **Connected apps**
3. **ודא** ש-**"Atlassian Rovo MCP Server"** מופיע ברשימה
4. **לחץ עליו** כדי לראות פרטים נוספים (הרשאות, תאריך התחברות, וכו')

### בדיקה 4: בדיקת לוגים (אם יש בעיות)

1. **פתח את Developer Tools** ב-Cursor (Ctrl+Shift+I)
2. **עבור לטאב "Console"**
3. **חפש הודעות** הקשורות ל-MCP או Atlassian
4. **אם יש שגיאות**, תראה אותן כאן

---

## 🎨 דוגמאות שימוש

### עבודה עם Jira:

```
"Find all open bugs in Project Alpha"
"Create a story titled 'Redesign onboarding'"
"Make five Jira issues from these notes"
```

### עבודה עם Confluence:

```
"Summarize the Q2 planning page"
"Create a page titled 'Team Goals Q3'"
"What spaces do I have access to?"
```

### עבודה עם Compass:

```
"Create a service component based on the current repository"
"What depends on the api-gateway service?"
```

---

## ⚠️ בעיות נפוצות ופתרונות

### בעיה 1: "Your site admin must authorize this app"

**פתרון:**
- מנהל האתר צריך להיות הראשון להתחבר
- לאחר שהמנהל מתחבר, כל המשתמשים יכולים להתחבר

### בעיה 2: האפליקציה לא מופיעה ב-Connected Apps

**פתרון:**
1. ודא שהתחברת עם החשבון הנכון
2. ודא שהאתר הנכון נבחר
3. נסה להתנתק ולהתחבר מחדש

### בעיה 3: אין גישה לנתונים מסוימים

**פתרון:**
- ההרשאות תלויות בהרשאות המשתמש שלך ב-Atlassian
- ודא שיש לך גישה לפרויקט/מרחב המבוקש

---

## 🔒 אבטחה והרשאות

### איך זה עובד:

1. ✅ כל התקשורת מוצפנת ב-HTTPS (TLS 1.2+)
2. ✅ OAuth 2.1 מבטיח אימות מאובטח
3. ✅ הגישה תלויה בהרשאות המשתמש שלך ב-Atlassian
4. ✅ כל פעולה מתועדת ב-Audit Log

### ניהול הרשאות:

- **מנהלי אתר** יכולים לנהל/לבטל גישה מ-**Manage apps**
- **משתמשים** יכולים לבטל את ההרשאה שלהם מהפרופיל
- **מנהלים** יכולים לחסום התקנת אפליקציות OAuth (3LO)

---

## 📚 משאבים נוספים

### תיעוד רשמי:

- [Getting Started with Atlassian Rovo MCP Server](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/)
- [Setting up IDEs (like VS Code or Cursor)](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/setting-up-ides-desktop-clients/)
- [Authentication and authorization](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/authentication-and-authorization/)

### תמיכה:

- [Atlassian Support Portal](https://support.atlassian.com/)
- [Atlassian Community](https://community.atlassian.com/)

---

## 🎯 סיכום

**מה למדנו:**

1. ✅ Atlassian Rovo MCP Server הוא שירות ענן - לא משהו שמורידים
2. ✅ מתחברים אליו דרך Cursor על ידי עריכת קובץ `mcp.json`
3. ✅ עוברים תהליך OAuth 2.1 בדפדפן (אוטומטית כשמשתמשים בשרת)
4. ✅ מקבלים גישה לנתונים מ-Jira, Confluence, ו-Compass

**השלבים הבאים:**

1. ✅ **הוספת ההגדרה** ל-`mcp.json` (כבר עשינו!)
2. ⏳ **הפעלה מחדש** של Cursor
3. ⏳ **בדיקה** שהשרת נטען בהצלחה
4. ⏳ **שימוש** בשאלות טבעיות - תהליך OAuth יתחיל אוטומטית

---

## 📝 הערות טכניות

### מיקום קובץ ההגדרות:

- **Windows:** `C:\Users\<USERNAME>\.cursor\mcp.json`
- **Mac:** `~/.cursor/mcp.json`
- **Linux:** `~/.cursor/mcp.json`

### דרישות:

- ✅ **Node.js v18+** (להפעלת `npx`)
- ✅ **גישה לאינטרנט** (לחיבור לשרת הענן)
- ✅ **חשבון Atlassian Cloud** פעיל

---

**עודכן לאחרונה:** 2025-11-09  
**גרסה:** 1.0

