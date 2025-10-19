# 🚀 Enhanced Logging - Quick Start

## ⚡ הדרך הכי מהירה להתחיל

### שלב 1: הפעל את Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

### שלב 2: הרץ טסט עם Enhanced Logging

**אופציה 1: בקצרה (ישירות)**
```powershell
$env:PYTHONPATH = "$PWD"; python -m pytest tests/integration/api/test_singlechannel_view_mapping.py -v
```

**אופציה 2: עם הסקריפט** (אוטומטי)
```powershell
.\scripts\test_with_enhanced_logging.ps1
```

---

## 💡 מה תראה?

### HTTP Request מלא:
```
→ POST http://10.10.10.150:5000/configure
Request Body (JSON):
  {
    "view_type": "1",
    "channels": {"min": 7, "max": 7},
    ...
  }
```

### HTTP Response עם Timing:
```
← 200 OK (107.94ms)
Response Body (JSON):
  {
    "stream_amount": 1,
    "channel_to_stream_index": {"7": 0},
    ...
  }
```

---

## 🎯 Use Cases

### Debug בעיה
```powershell
# הרץ טסט ספציפי עם enhanced logging
$env:PYTHONPATH = "$PWD"; python -m pytest tests/integration/api/test_singlechannel_view_mapping.py::test_configure_singlechannel_mapping -v
```

### שמור לוגים לקובץ
```powershell
# שמור את הפלט לקובץ
$env:PYTHONPATH = "$PWD"; python -m pytest tests/integration/api/ -v > test_output.txt 2>&1
```

### הרץ רק טסט שנכשל
```powershell
# הרץ רק טסטים שנכשלו בריצה הקודמת
$env:PYTHONPATH = "$PWD"; python -m pytest tests/integration/api/ -v --lf
```

---

## ⚙️ אופציות נוספות

### Log Level
```powershell
# Debug level (כל הפרטים)
$env:PYTHONPATH = "$PWD"; python -m pytest tests/ -v -log-cli-level=DEBUG

# Warning level (רק אזהרות ושגיאות)
$env:PYTHONPATH = "$PWD"; python -m pytest tests/ -v -log-cli-level=WARNING
```

### מספר Workers (Parallel)
```powershell
# הרץ טסטים במקביל (מהיר יותר)
$env:PYTHONPATH = "$PWD"; python -m pytest tests/ -v -n 4
```

### Specific Test Class
```powershell
# הרץ קלאס ספציפי
$env:PYTHONPATH = "$PWD"; python -m pytest tests/integration/api/test_singlechannel_view_mapping.py::TestSingleChannelViewHappyPath -v
```

---

## 🐛 Troubleshooting

### שגיאה: `ModuleNotFoundError: No module named 'config'`
**פתרון**: הוסף `$env:PYTHONPATH = "$PWD"` לפני pytest
```powershell
$env:PYTHONPATH = "$PWD"; python -m pytest tests/ -v
```

### שגיאה: `python.exe failed to run`
**פתרון**: השתמש בנתיב המלא
```powershell
$env:PYTHONPATH = "$PWD"; .\.venv\Scripts\python.exe -m pytest tests/ -v
```

### שגיאה: `SSH connection refused`
**פתרון**: בדוק ש-SSH עובד
```powershell
ssh prisma@10.10.10.150
```

---

## 📊 Example Output

### לפני Enhanced Logging:
```
test_configure_singlechannel_mapping PASSED  [100%]
1 passed in 2.34s
```

### אחרי Enhanced Logging:
```
→ POST http://10.10.10.150:5000/configure
Request Body (JSON): {view_type: "1", channels: {min: 7, max: 7}, ...}
← 200 OK (107.94ms)
Response Body (JSON): {stream_amount: 1, channel_to_stream_index: {"7": 0}, ...}

✅ stream_amount = 1
✅ channel_to_stream_index has 1 entry
✅ Channel mapping verified: {'7': 0}
test_configure_singlechannel_mapping PASSED  [100%]
```

**עכשיו אתה רואה הכל!** 👀

---

## 🚀 Next Steps

1. **הרץ טסט**: `$env:PYTHONPATH = "$PWD"; python -m pytest tests/ -v`
2. **קרא מדריך מלא**: `docs/ENHANCED_LOGGING_GUIDE.md`
3. **ראה דוגמאות**: `EXAMPLE_OUTPUT.md`

---

## 💡 Pro Tips

### שמור את PYTHONPATH לכל הסשן
```powershell
# הוסף בתחילת הסשן
$env:PYTHONPATH = "$PWD"

# אז תוכל להריץ בלי לחזור על זה
python -m pytest tests/ -v
python -m pytest tests/test_other.py -v
```

### צור Alias
```powershell
# הוסף ל-PowerShell profile שלך
function pyt {
    $env:PYTHONPATH = "$PWD"
    python -m pytest $args
}

# עכשיו תוכל להריץ:
pyt tests/ -v
pyt tests/test_singlechannel.py -v
```

### הרץ עם Watch Mode
```powershell
# התקן pytest-watch
pip install pytest-watch

# הרץ אוטומטית כשקבצים משתנים
$env:PYTHONPATH = "$PWD"; ptw tests/ -v
```

---

**Success!** 🎉  
עכשיו יש לך visibility מלא לתוך הטסטים!

