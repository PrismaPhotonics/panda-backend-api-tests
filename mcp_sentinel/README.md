# MCP Sentinel Server

MCP server for Automation Run Sentinel - Monitoring service for automation runs.
Provides tools to query runs, anomalies, and monitor automation executions directly from Cursor.

## תכונות

- ✅ **קבלת הרצות פעילות** - רשימת כל ההרצות הפעילות כרגע
- ✅ **פרטי הרצה** - קבלת פרטים מלאים על הרצה ספציפית
- ✅ **חיפוש הרצות** - חיפוש הרצות לפי pipeline, environment, status
- ✅ **אנומליות** - קבלת אנומליות של הרצה ספציפית או אנומליות אחרונות
- ✅ **סטטיסטיקות** - סטטיסטיקות על הרצות פעילות
- ✅ **ניטור בזמן אמת** - ניטור הרצה ספציפית

## התקנה

### 1. התקנת תלויות

```bash
pip install mcp
```

(התלויות של Sentinel כבר קיימות ב-requirements-sentinel.txt)

### 2. הגדרת MCP ב-Cursor

הוסף ל-`~/.cursor/mcp.json` (או `C:\Users\<USERNAME>\.cursor\mcp.json` ב-Windows):

```json
{
  "mcpServers": {
    "sentinel": {
      "command": "python",
      "args": ["-m", "mcp_sentinel.server"],
      "cwd": "C:\\Projects\\focus_server_automation"
    }
  }
}
```

**חשוב:** עדכן את `cwd` לנתיב הנכון של הפרויקט שלך.

### 3. הפעלה מחדש של Cursor

לחץ על **Reload Window** או הפעל מחדש את Cursor.

## שימוש

### דוגמאות פקודות ב-Cursor Chat:

```
"Show me all active automation runs"
"Get details for run abc123"
"Find runs for pipeline regression-nightly"
"Show me anomalies for run xyz789"
"Get recent critical anomalies"
"What are the current run statistics?"
"Monitor run abc123"
"Trigger GitHub workflow build-sentinel.yml"
"Run GitHub workflow smoke-tests.yml on branch develop"
"List all GitHub workflows"
"Trigger workflow build-sentinel.yml with inputs tag=v1.0.0"
"Add schedule to smoke-tests.yml: run daily at 8 AM"
"Get YAML content of smoke-tests.yml"
"Update workflow schedule for regression-tests.yml to run every Monday at 9 AM"
"Remove schedule from load-tests.yml"
"List all scheduled workflows"
"Update workflow YAML for smoke-tests.yml"
"Get detailed information for workflow run 19862020040"
"Monitor workflow run smoke-tests.yml with full details"
"Show me what failed in workflow run 19862020040"
```

### כלים זמינים:

1. **get_active_runs** - קבלת כל ההרצות הפעילות
   - מחזיר רשימה של כל ההרצות שכרגע רצות

2. **get_run** - פרטי הרצה ספציפית
   - `run_id`: מזהה ההרצה

3. **query_runs** - חיפוש הרצות היסטוריות
   - `pipeline`: שם ה-pipeline
   - `environment`: סביבה
   - `status`: סטטוס (running, completed, failed, cancelled)
   - `limit`: מספר תוצאות מקסימלי

4. **get_run_anomalies** - אנומליות של הרצה
   - `run_id`: מזהה ההרצה

5. **get_recent_anomalies** - אנומליות אחרונות
   - `severity`: רמת חומרה (critical, warning, info)
   - `hours`: מספר שעות אחורה
   - `limit`: מספר תוצאות מקסימלי

6. **get_run_stats** - סטטיסטיקות על הרצות
   - מחזיר סטטיסטיקות על הרצות פעילות

7. **monitor_run** - ניטור הרצה בזמן אמת
   - `run_id`: מזהה ההרצה
   - מחזיר את הסטטוס הנוכחי של ההרצה

8. **trigger_github_workflow** - הפעלת GitHub Actions workflow
   - `workflow_file`: שם קובץ ה-workflow (למשל: "build-sentinel.yml") או workflow ID
   - `ref`: branch, tag, או commit SHA (ברירת מחדל: "main")
   - `inputs`: פרמטרים אופציונליים ל-workflow (אם workflow_dispatch)
   - `repository`: repository בפורמט "owner/repo" (אופציונלי, משתמש ב-repo הנוכחי)

9. **list_github_workflows** - רשימת workflows זמינים
   - `repository`: repository בפורמט "owner/repo" (אופציונלי, משתמש ב-repo הנוכחי)

10. **get_workflow_yaml** - קבלת תוכן YAML של workflow
    - `workflow_file`: שם קובץ ה-workflow
    - `repository`: repository בפורמט "owner/repo" (אופציונלי)

11. **update_workflow_schedule** - הוספה/עדכון schedule (cron) ל-workflow
    - `workflow_file`: שם קובץ ה-workflow
    - `schedule`: ביטוי cron (למשל: "0 8 * * *" ל-8 בבוקר כל יום)
    - `timezone`: timezone (ברירת מחדל: "UTC")
    - `repository`: repository בפורמט "owner/repo" (אופציונלי)

12. **remove_workflow_schedule** - הסרת schedule מ-workflow
    - `workflow_file`: שם קובץ ה-workflow
    - `repository`: repository בפורמט "owner/repo" (אופציונלי)

13. **update_workflow_yaml** - עדכון מלא של קובץ workflow YAML
    - `workflow_file`: שם קובץ ה-workflow
    - `yaml_content`: תוכן YAML מלא (יחליף את כל הקובץ)
    - `repository`: repository בפורמט "owner/repo" (אופציונלי)

14. **list_workflow_schedules** - רשימת כל ה-workflows המתוזמנים
    - `repository`: repository בפורמט "owner/repo" (אופציונלי)

15. **get_workflow_run_details** - פרטים מפורטים על הרצת workflow
    - `run_id`: מזהה ההרצה ב-GitHub Actions
    - `repository`: repository בפורמט "owner/repo" (אופציונלי)
    - `include_logs`: האם לכלול לוגים של steps שנכשלו (ברירת מחדל: false)
    - מחזיר: jobs, steps, זמני ריצה, שגיאות, לוגים, וסיכום

16. **monitor_workflow_run_detailed** - ניטור מפורט של הרצת workflow
    - `workflow_file`: שם קובץ ה-workflow
    - `run_id`: מזהה הרצה ספציפי (אופציונלי, אם לא מוגדר - הרצה האחרונה)
    - `repository`: repository בפורמט "owner/repo" (אופציונלי)
    - `poll_interval`: מרווח בדיקה בשניות (ברירת מחדל: 10)
    - מחזיר: סטטוס מפורט עם jobs, steps, וזמני ריצה

## דרישות

- Python 3.11+
- `mcp` package מותקן
- `requests` package מותקן (לכלי GitHub)
- `pyyaml` package מותקן (לעריכת YAML)
- Sentinel service מוגדר ופועל
- קובץ קונפיגורציה `config/sentinel_config.yaml` (אופציונלי)
- GitHub token מוגדר (ב-`GITHUB_TOKEN` או ב-`mcp.json`)

## פתרון בעיות

### השרת לא נטען ב-Cursor

1. ודא ש-`mcp` מותקן: `pip install mcp`
2. ודא שהנתיב ב-`mcp.json` נכון
3. בדוק את ה-logs של Cursor (Developer Tools → Console)

### שגיאות בקריאת נתונים

1. ודא ש-Sentinel service פועל
2. בדוק את קובץ הקונפיגורציה `config/sentinel_config.yaml`
3. ודא שה-Kubernetes connection עובד (אם משתמש ב-K8s)

### "Sentinel service is not available"

1. בדוק שהקוד של Sentinel קיים ב-`src/sentinel/`
2. בדוק שהתלויות מותקנות (`requirements-sentinel.txt`)
3. בדוק את ה-logs של Cursor לפרטים נוספים

## מבנה

```
mcp_sentinel/
├── __init__.py      # Package initialization
├── server.py        # MCP server implementation
└── README.md        # This file
```

## פיתוח עתידי

תכונות אפשריות להוספה:

- [ ] Real-time streaming של הרצות
- [ ] התראות על אנומליות חדשות
- [ ] אינטגרציה עם Slack/Email
- [ ] ניתוח מגמות
- [ ] השוואה בין הרצות

## רישיון

חלק מהפרויקט Focus Server Automation.

