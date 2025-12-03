# MCP Log Analyzer

כלי MCP לניתוח לוגים בזמן אמת של טסטים - מותאם אישית לפרויקט Focus Server Automation.

## תכונות

- ✅ **Tail לוגים בזמן אמת** - צפייה בלוגים האחרונים
- ✅ **חיפוש בלוגים** - חיפוש לפי pattern (תמיכה ב-regex)
- ✅ **ניתוח שגיאות** - זיהוי וניתוח שגיאות בטווח זמן
- ✅ **לוגים לפי טסט** - חיפוש לוגים של טסט ספציפי
- ✅ **רשימת לוגים** - רשימת קבצי לוג אחרונים

## התקנה

### 1. התקנת תלויות

```bash
pip install mcp
```

### 2. הגדרת MCP ב-Cursor

הוסף ל-`~/.cursor/mcp.json` (או `C:\Users\<USERNAME>\.cursor\mcp.json` ב-Windows):

```json
{
  "mcpServers": {
    "log-analyzer": {
      "command": "python",
      "args": ["-m", "mcp_log_analyzer.server"],
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
"Show me the last 50 lines from the current test run"
"Tail the errors log file"
"Search for 'timeout' in all logs"
"Analyze errors from the last hour"
"Get logs for test_gradual_historic_load"
"List recent log files"
```

### כלים זמינים:

1. **tail_logs** - Tail לוגים בזמן אמת
   - `log_type`: test_runs, errors, warnings, pod_logs
   - `lines`: מספר שורות להצגה

2. **search_logs** - חיפוש בלוגים
   - `pattern`: Pattern לחיפוש (תמיכה ב-regex)
   - `log_type`: סוג לוג לחיפוש
   - `max_results`: מספר תוצאות מקסימלי

3. **analyze_errors** - ניתוח שגיאות
   - `time_range`: טווח זמן (למשל: "last hour", "last day")

4. **get_test_logs** - לוגים לפי טסט
   - `test_name`: שם הטסט או pattern
   - `log_type`: סוג לוג

5. **list_recent_logs** - רשימת לוגים אחרונים
   - `log_type`: סוג לוג
   - `limit`: מספר קבצים מקסימלי

## מבנה הלוגים

הכלי עובד עם המבנה הבא:

```
logs/
├── test_runs/     # לוגים של הרצות טסטים
├── errors/        # לוגים של שגיאות בלבד
├── warnings/      # לוגים של אזהרות
└── pod_logs/      # לוגים של pods (Kubernetes)
```

## פתרון בעיות

### הכלי לא נטען ב-Cursor

1. ודא ש-`mcp` מותקן: `pip install mcp`
2. ודא שהנתיב ב-`mcp.json` נכון
3. בדוק את ה-logs של Cursor (Developer Tools → Console)

### שגיאות בקריאת לוגים

1. ודא שהתיקייה `logs/` קיימת בפרויקט
2. ודא שיש קבצי לוג בתיקיות המתאימות

## פיתוח עתידי

תכונות אפשריות להוספה:

- [ ] Real-time streaming (tail -f)
- [ ] ניתוח סטטיסטיקות
- [ ] זיהוי דפוסים אוטומטי
- [ ] אינטגרציה עם pod monitoring
- [ ] התראות על שגיאות חדשות

## רישיון

חלק מהפרויקט Focus Server Automation.

