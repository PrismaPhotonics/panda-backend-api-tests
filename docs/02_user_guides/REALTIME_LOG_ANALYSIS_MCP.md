# 🔍 כלי MCP לניתוח לוגים בזמן אמת

**תאריך:** 2025-12-02  
**מטרה:** כלי MCP מותאם אישית לניתוח וחקירה של לוגים בזמן אמת של טסטים

---

## 🎯 מה אתה צריך

אתה מחפש כלי שיכול:
- ✅ לרוץ על Cursor (MCP server)
- ✅ לנתח לוגים בזמן אמת (real-time analysis)
- ✅ לחקור בעיות בטסטים
- ✅ לעבוד עם לוגים של פנדה ופוקוס
- ✅ לעבוד עם הפורמט הטקסטואלי שלך (לא JSON)

---

## 🔧 פתרון מומלץ: כלי MCP מותאם אישית

מכיוון שאין כלי MCP קיים שמתאים בדיוק לצרכים שלך, הפתרון הטוב ביותר הוא לבנות כלי MCP מותאם אישית.

### למה כלי מותאם אישית?

1. ✅ **עובד עם הפורמט שלך** - לוגים בפורמט טקסט (לא JSON)
2. ✅ **מבין את המבנה שלך** - `test_runs/`, `errors/`, `warnings/`, `pod_logs/`
3. ✅ **מתחבר למערכות שלך** - פנדה ופוקוס
4. ✅ **ניתוח בזמן אמת** - יכול לעקוב אחרי לוגים בזמן שהם נכתבים

---

## 📋 תכונות מומלצות לכלי

### 1. קריאת לוגים בזמן אמת
```
"Show me the latest test logs"
"Tail the current test run logs"
"Follow the errors log file"
```

### 2. ניתוח לוגים
```
"Analyze the last test run for errors"
"What errors occurred in the last 10 minutes?"
"Find all timeout errors in today's logs"
```

### 3. חיפוש וסינון
```
"Search for 'connection timeout' in all logs"
"Show me all MongoDB errors from today"
"Find all failed tests in the last hour"
```

### 4. ניתוח לפי טסט
```
"Show me logs for test_gradual_historic_load"
"What happened during test_mongodb_data_quality?"
```

### 5. ניתוח לפי שירות (Pod)
```
"Show me Focus Server logs from the last test"
"What errors are in MongoDB logs?"
```

---

## 🚀 איך לבנות את הכלי

### אפשרות 1: Python MCP Server (מומלץ)

**יתרונות:**
- ✅ אתה כבר משתמש ב-Python בפרויקט
- ✅ קל לשלב עם המערכת הקיימת שלך
- ✅ יכול להשתמש ב-`realtime_pod_monitor.py` הקיים

**דוגמה בסיסית:**

```python
# mcp_log_analyzer/server.py
from mcp.server import Server
from mcp.types import Tool, TextContent
import asyncio
from pathlib import Path
from datetime import datetime
import re

server = Server("log-analyzer")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="tail_logs",
            description="Tail log files in real-time",
            inputSchema={
                "type": "object",
                "properties": {
                    "log_type": {
                        "type": "string",
                        "enum": ["test_runs", "errors", "warnings", "pod_logs"],
                        "description": "Type of log to tail"
                    },
                    "lines": {
                        "type": "integer",
                        "default": 50,
                        "description": "Number of lines to show"
                    }
                }
            }
        ),
        Tool(
            name="analyze_errors",
            description="Analyze errors in logs",
            inputSchema={
                "type": "object",
                "properties": {
                    "time_range": {
                        "type": "string",
                        "description": "Time range (e.g., 'last 10 minutes', 'today')"
                    }
                }
            }
        ),
        Tool(
            name="search_logs",
            description="Search logs for patterns",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Search pattern"
                    },
                    "log_type": {
                        "type": "string",
                        "enum": ["test_runs", "errors", "warnings", "pod_logs", "all"]
                    }
                }
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "tail_logs":
        log_type = arguments.get("log_type", "test_runs")
        lines = arguments.get("lines", 50)
        return await tail_logs(log_type, lines)
    elif name == "analyze_errors":
        time_range = arguments.get("time_range", "last hour")
        return await analyze_errors(time_range)
    elif name == "search_logs":
        pattern = arguments.get("pattern")
        log_type = arguments.get("log_type", "all")
        return await search_logs(pattern, log_type)

async def tail_logs(log_type: str, lines: int):
    """Tail log files"""
    log_dir = Path(f"logs/{log_type}")
    if not log_dir.exists():
        return TextContent(
            type="text",
            text=f"Log directory {log_dir} does not exist"
        )
    
    # Find latest log file
    log_files = sorted(log_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not log_files:
        return TextContent(type="text", text="No log files found")
    
    latest_log = log_files[0]
    with open(latest_log, 'r', encoding='utf-8') as f:
        content = f.read()
        lines_list = content.split('\n')
        last_lines = '\n'.join(lines_list[-lines:])
    
    return TextContent(
        type="text",
        text=f"Latest {lines} lines from {latest_log.name}:\n\n{last_lines}"
    )

async def analyze_errors(time_range: str):
    """Analyze errors in logs"""
    # Implementation here
    pass

async def search_logs(pattern: str, log_type: str):
    """Search logs for pattern"""
    # Implementation here
    pass

if __name__ == "__main__":
    asyncio.run(server.run())
```

### אפשרות 2: TypeScript/Node.js MCP Server

**יתרונות:**
- ✅ קל להתקין דרך npm
- ✅ תואם לרוב כלי MCP הקיימים

---

## 📦 התקנה והגדרה

### שלב 1: יצירת המבנה

```bash
mkdir -p mcp_log_analyzer
cd mcp_log_analyzer
```

### שלב 2: התקנת תלויות

```bash
pip install mcp python-dotenv
```

### שלב 3: הגדרת MCP ב-Cursor

הוסף ל-`~/.cursor/mcp.json`:

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

---

## 🎨 דוגמאות שימוש

### ניתוח בזמן אמת

```
"Show me the last 50 lines from the current test run"
"Tail the errors log file"
"What errors occurred in the last test?"
```

### חיפוש וסינון

```
"Search for 'timeout' in all today's logs"
"Find all MongoDB connection errors"
"Show me all failed tests from the last hour"
```

### ניתוח לפי טסט

```
"Analyze logs for test_gradual_historic_load"
"What happened during the last load test?"
```

### ניתוח לפי שירות

```
"Show me Focus Server logs from the last test run"
"What errors are in MongoDB pod logs?"
```

---

## 🔗 אינטגרציה עם המערכת הקיימת

הכלי יכול להשתמש ב:

1. **`src/utils/realtime_pod_monitor.py`** - לניטור לוגים בזמן אמת
2. **`be_focus_server_tests/pytest_logging_plugin.py`** - למבנה הלוגים
3. **`config/sentinel_config.yaml`** - לדפוסי שגיאות

---

## 📚 משאבים

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Cursor MCP Documentation](https://docs.cursor.com/mcp)

---

## ✅ סיכום

**הפתרון המומלץ:** בנה כלי MCP מותאם אישית ב-Python ש:
1. ✅ עובד עם הפורמט הטקסטואלי שלך
2. ✅ מבין את המבנה שלך (`test_runs/`, `errors/`, וכו')
3. ✅ יכול לנתח לוגים בזמן אמת
4. ✅ מתחבר למערכות פנדה ופוקוס

**השלבים הבאים:**
1. בנה את הכלי הבסיסי (tail, search, analyze)
2. הוסף תכונות מתקדמות (real-time monitoring, pattern detection)
3. אינטגר עם המערכת הקיימת שלך

רוצה שאעזור לך לבנות את הכלי?

---

**עודכן לאחרונה:** 2025-12-02

