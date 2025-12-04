# 🛠️ המלצות לכלי MCP שיכולים לעזור לפרויקט

**תאריך:** 2025-12-02  
**מטרה:** רשימת כלי MCP מ-[cursor.directory/mcp](https://cursor.directory/mcp) שיכולים לשפר את הפרויקט

---

## 📋 סיכום מהיר

| כלי | מטרה | רמת התאמה | סיבה |
|-----|------|------------|------|
| **Atono MCP** | ניהול backlog ו-stories | ⭐⭐⭐⭐⭐ | מתאים מעולה - עובד עם Jira |
| **Postman MCP** | ניהול Postman collections | ⭐⭐⭐⭐ | יכול לעזור לבדיקות API |
| **Slack MCP** | אינטגרציה עם Slack | ⭐⭐⭐⭐ | יכול לעזור להתראות ותקשורת צוות |
| **Kubernetes MCP** | ניהול Kubernetes | ⭐⭐⭐ | שימושי אם יש deployment ל-K8s |
| **MailerSend/Postmark MCP** | שליחת אימיילים | ⭐⭐⭐ | יכול לעזור להתראות על תוצאות בדיקות |
| **Statsig MCP** | Feature flags | ⭐⭐ | לא רלוונטי כרגע (אין feature flags) |
| **Midday MCP** | ניהול עסקי | ⭐ | לא רלוונטי לפרויקט |

---

## 🎯 כלים מומלצים ביותר

### 1. **Atono MCP** ⭐⭐⭐⭐⭐

**מה זה:**
- כלי לניהול backlog ו-stories ישירות מ-Cursor
- מתחבר ל-Jira שלך (אתה כבר משתמש ב-Atlassian Rovo MCP)
- מאפשר לקרוא requirements, לעדכן workflow, לתעד fixes, ולנהל assignments

**למה זה מתאים לך:**
- ✅ יש לך אינטגרציה חזקה עם Jira (כבר יש לך Atlassian Rovo MCP)
- ✅ יש לך הרבה scripts לעבודה עם Jira (`scripts/jira/`)
- ✅ אתה יוצר ועדכן טיקטים דרך Python scripts
- ✅ זה יכול להחליף חלק מהעבודה הידנית ב-Jira

**איך זה עוזר:**
```
במקום:
1. לפתוח Jira בדפדפן
2. לחפש story
3. לעדכן status
4. לחזור ל-Cursor

עכשיו:
"Update story PZ-12345 to status 'In Progress'"
"Create a bug ticket for the API endpoint failure"
"Show me all open stories in project PZ"
```

**התקנה:**
```json
{
  "mcpServers": {
    "atono": {
      "command": "npx",
      "args": ["-y", "@atono/mcp-server"]
    }
  }
}
```

**קישור:** [Atono MCP Documentation](https://docs.atono.io/docs/mcp-server-for-atono#cursor)

---

### 2. **Postman MCP** ⭐⭐⭐⭐

**מה זה:**
- כלי לניהול Postman collections ישירות מ-Cursor
- מאפשר להריץ API tests, לנהל environments, ולעבוד עם workspaces

**למה זה מתאים לך:**
- ✅ יש לך הרבה בדיקות API (`be_focus_server_tests/integration/api/`)
- ✅ אתה בודק REST APIs של Focus Server
- ✅ זה יכול לעזור לך לנהל ולבדוק APIs בצורה מהירה יותר

**איך זה עוזר:**
```
"Run the Postman collection for Focus Server API tests"
"Show me all failed API requests from the last test run"
"Update the environment variable 'base_url' to staging"
```

**התקנה:**
```json
{
  "mcpServers": {
    "postman": {
      "command": "npx",
      "args": ["-y", "@postman/mcp-server"]
    }
  }
}
```

**קישור:** [Postman MCP Documentation](https://www.postman.com/ai/mcp-server/)

**הערה:** זה דורש שיש לך Postman account ו-collections מוגדרות. אם אין לך, זה יכול להיות הזדמנות ליצור collections לבדיקות API שלך.

---

### 3. **Slack MCP** ⭐⭐⭐⭐

**מה זה:**
- כלי לאינטגרציה עם Slack ישירות מ-Cursor
- מאפשר לשלוח הודעות, לנהל channels, ולעבוד עם Slack workspaces
- אין צורך ב-bot או אישור מנהל workspace

**למה זה מתאים לך:**
- ✅ אתה יכול לשלוח התראות על תוצאות בדיקות ל-Slack
- ✅ אתה יכול לעדכן את הצוות על deployments ו-tests
- ✅ זה יכול להחליף שליחת הודעות ידנית ב-Slack
- ✅ אינטגרציה טובה עם ה-workflow הקיים

**איך זה עוזר:**
```
"Send a message to #dev-team about test failures"
"Notify #general that deployment is complete"
"Post test summary to #qa-team channel"
"Send DM to @username about critical bug"
```

**התקנה:**
```json
{
  "mcpServers": {
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_TOKEN": "xoxp-your-token-here"
      }
    }
  }
}
```

**קישור:** [Slack MCP Documentation](https://cursor.directory/mcp/slack)

**הערה:** דורש Slack token מ-Slack API. ראה [מדריך ההתקנה המלא](./SLACK_MCP_SETUP.md) לפרטים.

---

### 4. **Kubernetes MCP** ⭐⭐⭐

**מה זה:**
- כלי לניהול משאבי Kubernetes ישירות מ-Cursor
- מאפשר לנהל pods, deployments, services, ו-resources נוספים
- עובד עם כל Kubernetes cluster (local, cloud, או on-premise)

**למה זה יכול לעזור:**
- ✅ אם אתה מפרסם ל-Kubernetes, זה יכול לעזור לניהול
- ✅ אתה יכול לבדוק סטטוס של pods ו-deployments
- ✅ אתה יכול לקבל logs ישירות מ-Cursor
- ✅ זה יכול לעזור ב-debugging של בעיות deployment

**איך זה עוזר:**
```
"List all pods in the default namespace"
"Get logs from pod my-app-123"
"Show me the status of deployment focus-server"
"Scale deployment test-runner to 5 replicas"
```

**התקנה:**
```json
{
  "mcpServers": {
    "kubernetes": {
      "command": "npx",
      "args": ["-y", "mcp-server-kubernetes"],
      "env": {}
    }
  }
}
```

**קישור:** [Kubernetes MCP Documentation](https://cursor.directory/mcp/kubernetes)

**הערה:** דורש `kubectl` מותקן ומוגדר. ראה [מדריך ההתקנה המלא](./KUBERNETES_MCP_SETUP.md) לפרטים.

---

### 5. **MailerSend MCP** / **Postmark MCP** ⭐⭐⭐

**מה זה:**
- כלי לשליחת אימיילים דרך API ישירות מ-Cursor
- MailerSend ו-Postmark הם שירותי transactional email

**למה זה יכול לעזור:**
- ✅ אתה יכול לשלוח התראות על תוצאות בדיקות
- ✅ אתה יכול לשלוח דוחות יומיים על תוצאות בדיקות
- ✅ זה יכול להחליף שליחת אימיילים ידנית

**איך זה עוזר:**
```
"Send email notification about failed tests to the team"
"Send daily test report summary"
"Notify me when load tests complete"
```

**התקנה (MailerSend):**
```json
{
  "mcpServers": {
    "mailersend": {
      "command": "npx",
      "args": ["-y", "@mailersend/mcp-server"],
      "env": {
        "MAILERSEND_API_KEY": "your-api-key"
      }
    }
  }
}
```

**התקנה (Postmark):**
```json
{
  "mcpServers": {
    "postmark": {
      "command": "npx",
      "args": ["-y", "@postmark/mcp-server"],
      "env": {
        "POSTMARK_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

**הערה:** זה דורש הרשמה לשירות ו-API key. אם אתה כבר משתמש בשירות אחר (כמו SendGrid), זה יכול להיות מיותר.

---

## ⚠️ כלים פחות רלוונטיים

### 6. **Statsig MCP** ⭐⭐

**מה זה:**
- כלי לניהול feature flags

**למה זה לא מתאים כרגע:**
- ❌ אין לך feature flags בפרויקט
- ❌ זה לא חלק מה-workflow שלך

**מתי זה יכול להיות שימושי:**
- אם תרצה להוסיף feature flags לבדיקות (למשל, להפעיל/לכבות בדיקות מסוימות)

---

### 7. **Midday MCP** ⭐

**מה זה:**
- כלי לניהול עסקי (tracking time, invoices, reports)

**למה זה לא מתאים:**
- ❌ זה לא קשור לפרויקט אוטומציה
- ❌ זה יותר לניהול עסקי כללי

---

## 🚀 המלצות להתקנה

### שלב 1: התקן את Atono MCP (מומלץ ביותר)

```json
{
  "mcpServers": {
    "atlassian-rovo": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.atlassian.com/v1/sse"],
      "env": {}
    },
    "atono": {
      "command": "npx",
      "args": ["-y", "@atono/mcp-server"]
    }
  }
}
```

**למה להתחיל עם זה:**
- זה משלים את Atlassian Rovo MCP שכבר יש לך
- זה יכול להחליף חלק מהעבודה הידנית ב-Jira
- זה יכול לחסוך זמן רב בעבודה עם stories ו-bugs

### שלב 2: שקול Postman MCP (אם יש לך Postman)

אם יש לך Postman collections, זה יכול לעזור לך לנהל ולבדוק APIs בצורה מהירה יותר.

### שלב 3: שקול Slack MCP (אם אתה משתמש ב-Slack)

אם אתה משתמש ב-Slack, זה יכול להיות דרך מעולה לשלוח התראות על תוצאות בדיקות ו-deployments.

### שלב 4: שקול Kubernetes MCP (אם יש deployment ל-K8s)

אם אתה מפרסם ל-Kubernetes, זה יכול לעזור לניהול ו-debugging.

### שלב 5: שקול MailerSend/Postmark (אם צריך התראות באימייל)

אם אתה צריך לשלוח התראות על תוצאות בדיקות באימייל, זה יכול לעזור.

---

## 📝 דוגמאות שימוש

### עם Atono MCP:

```
"Create a bug ticket for the API endpoint /channels returning 500 error"
"Show me all open bugs assigned to me"
"Update story PZ-12345 to status 'In Progress'"
"Link bug PZ-12346 to story PZ-12345"
"Create a story for implementing gradual load tests"
```

### עם Postman MCP:

```
"Run the Focus Server API test collection"
"Show me all failed requests from the last run"
"Update the base_url environment variable to production"
```

### עם Slack MCP:

```
"Send a message to #dev-team about test failures"
"Notify #general that deployment is complete"
"Post test summary to #qa-team channel"
"Send DM to @username about critical bug"
```

### עם Kubernetes MCP:

```
"List all pods in the default namespace"
"Get logs from pod focus-server-123"
"Show me the status of deployment test-runner"
"Scale deployment api-server to 3 replicas"
```

### עם MailerSend/Postmark:

```
"Send email notification about failed tests to roy.avrahami@prismaphotonics.com"
"Send daily test summary report"
```

---

## 🔗 קישורים שימושיים

- [cursor.directory/mcp](https://cursor.directory/mcp) - רשימת כל הכלים
- [Atono MCP Documentation](https://docs.atono.io/docs/mcp-server-for-atono#cursor)
- [Postman MCP Documentation](https://www.postman.com/ai/mcp-server/)
- [Slack MCP Documentation](https://cursor.directory/mcp/slack)
- [Kubernetes MCP Documentation](https://cursor.directory/mcp/kubernetes)
- [MailerSend MCP](https://lobehub.com/mcp/mailersend-mcp)
- [Postmark MCP](https://lobehub.com/mcp/postmark-mcp)

### מדריכי התקנה מפורטים:

- [מדריך Slack MCP Setup](./SLACK_MCP_SETUP.md)
- [מדריך Kubernetes MCP Setup](./KUBERNETES_MCP_SETUP.md)

---

## ✅ סיכום

**הכלי המומלץ ביותר:** **Atono MCP** - זה הכלי הכי רלוונטי לפרויקט שלך כי:
1. אתה כבר עובד עם Jira
2. יש לך הרבה scripts לעבודה עם Jira
3. זה יכול לחסוך זמן רב בעבודה ידנית

**הכלי השני:** **Postman MCP** - אם יש לך Postman collections, זה יכול לעזור לבדיקות API.

**הכלי השלישי:** **Slack MCP** - אם אתה משתמש ב-Slack, זה דרך מעולה להתראות ותקשורת.

**הכלי הרביעי:** **Kubernetes MCP** - אם אתה מפרסם ל-Kubernetes, זה יכול לעזור לניהול.

**הכלי החמישי:** **MailerSend/Postmark** - אם אתה צריך לשלוח התראות על תוצאות בדיקות באימייל.

---

**עודכן לאחרונה:** 2025-12-02

