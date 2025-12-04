# 🚀 מדריך התקנה: MCP Log Analyzer

**תאריך:** 2025-12-02  
**מטרה:** כלי MCP לניתוח לוגים בזמן אמת של טסטים

---

## ✅ מה הכלי עושה

הכלי מאפשר לך לנתח לוגים של טסטים ישירות מ-Cursor:

- ✅ **Tail לוגים בזמן אמת** - צפייה בלוגים האחרונים
- ✅ **חיפוש בלוגים** - חיפוש לפי pattern (תמיכה ב-regex)
- ✅ **ניתוח שגיאות** - זיהוי וניתוח שגיאות בטווח זמן
- ✅ **לוגים לפי טסט** - חיפוש לוגים של טסט ספציפי
- ✅ **רשימת לוגים** - רשימת קבצי לוג אחרונים

---

## 📦 התקנה

### שלב 1: התקנת תלויות

```bash
pip install mcp
```

### שלב 2: הגדרת MCP ב-Cursor

1. **פתח את קובץ ההגדרות של Cursor:**
   - **Windows:** `C:\Users\<USERNAME>\.cursor\mcp.json`
   - **Mac/Linux:** `~/.cursor/mcp.json`

2. **הוסף את ההגדרה הבאה:**

```json
{
  "mcpServers": {
    "atlassian-rovo": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.atlassian.com/v1/sse"],
      "env": {}
    },
    "log-analyzer": {
      "command": "python",
      "args": ["-m", "mcp_log_analyzer.server"],
      "cwd": "C:\\Projects\\focus_server_automation"
    }
  }
}
```

**⚠️ חשוב:** עדכן את `cwd` לנתיב הנכון של הפרויקט שלך!

**דוגמה לקובץ מלא:**

```json
{
  "mcpServers": {
    "playwright": {
      "args": ["@playwright/mcp@latest", "--isolated"],
      "command": "npx"
    },
    "atlassian-rovo": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.atlassian.com/v1/sse"],
      "env": {}
    },
    "log-analyzer": {
      "command": "python",
      "args": ["-m", "mcp_log_analyzer.server"],
      "cwd": "C:\\Projects\\focus_server_automation"
    }
  }
}
```

### שלב 3: הפעלה מחדש של Cursor

1. **שמור את הקובץ** (Ctrl+S)
2. **הפעל מחדש את Cursor** (או לחץ על **Reload Window**)

---

## ✅ אימות שההתקנה עובדת

### בדיקה 1: וידוא שהשרת נטען

1. **פתח את Cursor Settings** (Ctrl+,)
2. **חפש "MCP"** או **"Model Context Protocol"**
3. **בדוק** ש-**"log-analyzer"** מופיע ברשימת שרתי MCP
4. **ודא** שהסטטוס הוא **"Connected"** או **"Running"**

### בדיקה 2: בדיקה דרך Chat ב-Cursor

1. **פתח Chat** ב-Cursor (Ctrl+L)
2. **נסה שאלות** כמו:
   ```
   "Show me the last 50 lines from the current test run"
   "Tail the errors log file"
   "Search for 'timeout' in all logs"
   ```

---

## 🎨 דוגמאות שימוש

### 1. Tail לוגים בזמן אמת

```
"Show me the last 50 lines from the current test run"
"Tail the errors log file"
"What's in the latest warnings log?"
```

### 2. חיפוש בלוגים

```
"Search for 'timeout' in all logs"
"Find all MongoDB errors"
"Show me all 'connection refused' errors"
```

### 3. ניתוח שגיאות

```
"Analyze errors from the last hour"
"What errors occurred today?"
"Show me errors from the last 10 minutes"
```

### 4. לוגים לפי טסט

```
"Get logs for test_gradual_historic_load"
"Show me logs for test_mongodb_data_quality"
"What happened during test_historic_playback_e2e?"
```

### 5. רשימת לוגים

```
"List recent log files"
"Show me the last 10 log files"
"What log files do I have?"
```

---

## 🔧 כלים זמינים

### 1. `tail_logs` - Tail לוגים בזמן אמת

**פרמטרים:**
- `log_type`: test_runs, errors, warnings, pod_logs
- `lines`: מספר שורות להצגה (ברירת מחדל: 50)

**דוגמה:**
```
"Tail the test_runs log with 100 lines"
```

### 2. `search_logs` - חיפוש בלוגים

**פרמטרים:**
- `pattern`: Pattern לחיפוש (תמיכה ב-regex)
- `log_type`: סוג לוג לחיפוש (all, test_runs, errors, warnings, pod_logs)
- `max_results`: מספר תוצאות מקסימלי (ברירת מחדל: 100)

**דוגמה:**
```
"Search for 'timeout' in all logs"
"Find 'connection.*refused' in errors logs"
```

### 3. `analyze_errors` - ניתוח שגיאות

**פרמטרים:**
- `time_range`: טווח זמן (למשל: "last hour", "last day", "last 10 minutes")

**דוגמה:**
```
"Analyze errors from the last hour"
"What errors occurred today?"
```

### 4. `get_test_logs` - לוגים לפי טסט

**פרמטרים:**
- `test_name`: שם הטסט או pattern
- `log_type`: סוג לוג (all, test_runs, errors, warnings, pod_logs)

**דוגמה:**
```
"Get logs for test_gradual_historic_load"
"Show me logs for tests containing 'mongodb'"
```

### 5. `list_recent_logs` - רשימת לוגים אחרונים

**פרמטרים:**
- `log_type`: סוג לוג (all, test_runs, errors, warnings, pod_logs)
- `limit`: מספר קבצים מקסימלי (ברירת מחדל: 10)

**דוגמה:**
```
"List recent log files"
"Show me the last 20 log files"
```

---

## 🐛 פתרון בעיות

### בעיה 1: הכלי לא נטען ב-Cursor

**פתרון:**
1. ודא ש-`mcp` מותקן: `pip install mcp`
2. ודא שהנתיב ב-`mcp.json` נכון (במיוחד `cwd`)
3. בדוק את ה-logs של Cursor:
   - פתח **Developer Tools** (Ctrl+Shift+I)
   - עבור לטאב **Console**
   - חפש שגיאות הקשורות ל-MCP

### בעיה 2: שגיאות בקריאת לוגים

**פתרון:**
1. ודא שהתיקייה `logs/` קיימת בפרויקט
2. ודא שיש קבצי לוג בתיקיות המתאימות:
   - `logs/test_runs/`
   - `logs/errors/`
   - `logs/warnings/`
   - `logs/pod_logs/`

### בעיה 3: הכלי לא מוצא לוגים

**פתרון:**
1. ודא שהרצת טסטים לפחות פעם אחת
2. בדוק שהקבצים נשמרים בפורמט `.log`
3. נסה להשתמש ב-`list_recent_logs` כדי לראות אילו קבצים קיימים

---

## 📚 מבנה הלוגים

הכלי עובד עם המבנה הבא:

```
logs/
├── test_runs/     # לוגים של הרצות טסטים
│   └── YYYY-MM-DD_HH-MM-SS_<test_type>.log
├── errors/        # לוגים של שגיאות בלבד
│   └── YYYY-MM-DD_HH-MM-SS_<test_type>_ERRORS.log
├── warnings/      # לוגים של אזהרות
│   └── YYYY-MM-DD_HH-MM-SS_<test_type>_WARNINGS.log
└── pod_logs/      # לוגים של pods (Kubernetes)
    ├── focus-server_realtime.log
    ├── mongodb_realtime.log
    └── ...
```

---

## 🚀 פיתוח עתידי

תכונות אפשריות להוספה:

- [ ] Real-time streaming (tail -f) - עדכון אוטומטי בזמן אמת
- [ ] ניתוח סטטיסטיקות - סטטיסטיקות על שגיאות וביצועים
- [ ] זיהוי דפוסים אוטומטי - זיהוי דפוסים חוזרים
- [ ] אינטגרציה עם pod monitoring - שימוש ב-`realtime_pod_monitor.py`
- [ ] התראות על שגיאות חדשות - התראה כשמופיעות שגיאות חדשות

---

## 📝 הערות

- הכלי עובד עם לוגים בפורמט טקסט (לא JSON)
- הכלי מבין את המבנה שלך (`test_runs/`, `errors/`, וכו')
- הכלי מחפש בלוגים מהשעה האחרונה (ברירת מחדל)
- הכלי תומך ב-regex לחיפוש מתקדם

---

**עודכן לאחרונה:** 2025-12-02  
**גרסה:** 1.0.0

