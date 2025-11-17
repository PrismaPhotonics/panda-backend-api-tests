# ✨ Enhanced Logging - Implementation Summary

## 🎉 מה הוספנו?

### 1. ✅ HTTP Request/Response Logging מפורט
**קובץ**: `src/core/api_client.py`

**מה זה עושה:**
- מציג כל בקשת HTTP עם פרטים מלאים (URL, Headers, Body)
- מציג כל תשובת HTTP עם פרטים מלאים (Status, Headers, Body)
- JSON מעוצב בצורה קריאה
- זמן תגובה במילישניות
- הכל אוטומטי - לא צריך לשנות קוד!

**דוגמה:**
```
================================================================================
→ POST http://10.10.10.150:5000/configure
Request Body (JSON):
  {
    "view_type": "1",
    "channels": {"min": 7, "max": 7},
    ...
  }
← 200 OK (342.56ms)
Response Body (JSON):
  {
    "stream_amount": 1,
    "channel_to_stream_index": {"7": 0},
    ...
  }
================================================================================
```

---

### 2. ✅ Pod Logs Collection מ-Kubernetes
**קובץ**: `src/utils/pod_logs_collector.py`

**מה זה עושה:**
- מתחבר לפודים דרך SSH + kubectl
- אוסף לוגים מ-Focus Server, RabbitMQ, וכו'
- שני מצבים:
  - **Real-time streaming**: רואה לוגים בזמן אמת בזמן הטסטים
  - **Save to files**: שומר לוגים לקבצים לאחר הריצה
- עובד ברקע ולא מפריע לטסטים

**דוגמה:**
```
[focus-server] 2025-10-12 15:44:43 INFO: Received configure request
[focus-server] 2025-10-12 15:44:43 INFO: Job 31-3633 created successfully
[rabbitmq-panda] 2025-10-12 15:44:43 INFO: New connection established
```

---

### 3. ✅ Pytest Integration
**קובץ**: `tests/conftest.py`

**מה הוספנו:**
- `--collect-pod-logs` - הפעל streaming של לוגים
- `--save-pod-logs` - שמור לוגים לקבצים
- `pod_logs_collector` fixture - אוטומטי!

---

## 📚 תיעוד שנוצר

| קובץ | תיאור |
|------|-------|
| `docs/ENHANCED_LOGGING_GUIDE.md` | מדריך מלא ומפורט |
| `LOGGING_QUICK_REFERENCE.md` | כרטיס עזר מהיר |
| `ENHANCED_LOGGING_SUMMARY.md` | המסמך הזה |

---

## 🚀 איך להשתמש?

### אופציה 1: הרצת טסט רגילה (עם HTTP logging)
```bash
pytest tests/integration/api/test_singlechannel_view_mapping.py -v
```

**מה תראה:**
- ✅ HTTP requests/responses מלאים
- ✅ זמני תגובה
- ✅ JSON מעוצב

---

### אופציה 2: עם לוגים מהשרתים (Real-time)
```bash
pytest tests/integration/api/test_singlechannel_view_mapping.py --collect-pod-logs -v
```

**מה תראה:**
- ✅ HTTP requests/responses
- ✅ לוגים מ-Focus Server בזמן אמת
- ✅ לוגים מ-RabbitMQ בזמן אמת
- ✅ רואה מה קורה בשרת בזמן שהטסט רץ!

---

### אופציה 3: עם שמירת לוגים לקבצים
```bash
pytest tests/integration/api/test_singlechannel_view_mapping.py --save-pod-logs -v
```

**מה תקבל:**
- ✅ HTTP requests/responses
- ✅ קבצי לוג ב-`reports/logs/pod_logs/`
  - `focus-server_latest.log`
  - `rabbitmq-panda_latest.log`

---

### אופציה 4: Full Debug Mode (הכל!)
```bash
pytest tests/integration/api/test_singlechannel_view_mapping.py --collect-pod-logs --save-pod-logs -v -s -log-cli-level=DEBUG
```

**מה תקבל:**
- ✅ HTTP requests/responses מלאים (כולל headers)
- ✅ לוגים real-time מהשרתים
- ✅ לוגים נשמרים לקבצים
- ✅ DEBUG level (הכל!)
- ✅ print statements שלך

---

### אופציה 5: איסוף ידני של לוגים (בלי טסטים)
```bash
python scripts/collect_pod_logs_manual.py --service focus-server --lines 200
```

**מה זה עושה:**
- אוסף לוגים מהשרת בלי להריץ טסטים
- שימושי לדיבוג מהיר

---

## 📁 מבנה הקבצים החדשים

```
focus_server_automation/
├── src/
│   ├── core/
│   │   └── api_client.py                    ← שופר עם logging מפורט
│   └── utils/
│       └── pod_logs_collector.py            ← כלי חדש לאיסוף לוגים
├── tests/
│   └── conftest.py                          ← הוסף fixtures ללוגים
├── scripts/
│   ├── test_with_enhanced_logging.ps1       ← סקריפט עזר (PowerShell)
│   └── collect_pod_logs_manual.py           ← איסוף לוגים ידני
├── docs/
│   └── ENHANCED_LOGGING_GUIDE.md            ← מדריך מלא
├── LOGGING_QUICK_REFERENCE.md               ← עזר מהיר
└── ENHANCED_LOGGING_SUMMARY.md              ← המסמך הזה
```

---

## 💡 דוגמאות שימוש

### דוגמה 1: לדבג טסט שנכשל
```bash
# הרץ עם כל הלוגים
pytest tests/integration/api/test_singlechannel_view_mapping.py::test_configure_singlechannel_mapping \
    --collect-pod-logs \
    --save-pod-logs \
    -v \
    -s

# בדוק את הלוגים
cat reports/logs/pod_logs/focus-server_latest.log
```

### דוגמה 2: לראות מה השרת עושה
```bash
# הרץ עם streaming
pytest tests/integration/api/ --collect-pod-logs -v

# תראה בזמן אמת:
# [focus-server] INFO: Creating job...
# [focus-server] INFO: Job created successfully
```

### דוגמה 3: לאסוף לוגים לצוות Backend
```bash
# שמור לוגים לקבצים
pytest tests/integration/api/ --save-pod-logs -v

# שלח את הקבצים:
# reports/logs/pod_logs/focus-server_latest.log
# reports/logs/pod_logs/rabbitmq-panda_latest.log
```

---

## 🎓 Best Practices

### ✅ פיתוח יומיומי
```bash
pytest tests/ -v
```
רק HTTP logging - מספיק לרוב המקרים

### ✅ דיבוג בעיות
```bash
pytest tests/test_failing.py --collect-pod-logs --save-pod-logs -v
```
רואה מה קורה בשרת + שומר לוגים

### ✅ CI/CD
```bash
pytest tests/ --save-pod-logs -v -log-cli-level=WARNING
```
שומר לוגים לארכיון, רק אזהרות בקונסול

### ✅ דיבוג עמוק
```bash
pytest tests/test_problem.py --collect-pod-logs --save-pod-logs -v -s -log-cli-level=DEBUG > debug.txt 2>&1
```
הכל! לקובץ

---

## 🔧 התקנה / הגדרה

### ווידוא שהכל עובד:
```bash
# 1. Virtual environment
.\.venv\Scripts\Activate.ps1

# 2. בדוק שהחבילות מותקנות
pip list | grep -E "paramiko|requests"

# 3. בדוק את ההגדרות
cat config/environments.yaml | grep -A 3 "kubernetes"

# Should see:
#   ssh_host: "10.10.10.150"
#   ssh_user: "prisma"
#   ssh_password: "PASSW0RD"
```

### אם חסר משהו:
```bash
pip install paramiko requests
```

---

## 🐛 Troubleshooting

| בעיה | פתרון |
|------|--------|
| **אין לוגים מהפודים** | בדוק `config/environments.yaml` - SSH credentials |
| **SSH connection refused** | `ssh prisma@10.10.10.150` - וודא שעובד ידנית |
| **יותר מדי output** | השתמש ב-`-log-cli-level=WARNING` |
| **Pod not found** | `kubectl get pods -n default` - בדוק ששם השירות נכון |

---

## 📊 לפני ואחרי

### לפני (ללא enhanced logging):
```
test_configure_singlechannel_mapping PASSED
```
זה כל מה שראית...

### אחרי (עם enhanced logging):
```
================================================================================
→ POST http://10.10.10.150:5000/configure
Request Body: {"view_type": "1", "channels": {"min": 7, "max": 7}, ...}
← 200 OK (342.56ms)
Response: {"stream_amount": 1, "channel_to_stream_index": {"7": 0}, ...}
================================================================================
[focus-server] INFO: Received configure request for view_type=1
[focus-server] INFO: Creating baby analyzer job for channel 7
[focus-server] INFO: Validating channel range: min=7, max=7
[focus-server] INFO: Creating stream with ID: stream-0
[focus-server] INFO: Mapping channel 7 -> stream 0
[focus-server] INFO: Job 31-3633 created successfully
[focus-server] INFO: Returning response with stream_amount=1
test_configure_singlechannel_mapping PASSED
```

**עכשיו אתה רואה הכל!** 🎉

---

## 🚀 הצעדים הבאים

1. ✅ נסה את הפקודות למעלה
2. ✅ קרא את המדריך המלא: `docs/ENHANCED_LOGGING_GUIDE.md`
3. ✅ השתמש ב-Quick Reference: `LOGGING_QUICK_REFERENCE.md`
4. ✅ הרץ עם `--collect-pod-logs` ותראה מה קורה בשרת!

---

## 📞 שאלות?

- קרא את המדריך המלא: `docs/ENHANCED_LOGGING_GUIDE.md`
- בדוק דוגמאות בקוד: `src/utils/pod_logs_collector.py`
- הרץ את הסקריפט לדוגמה: `python scripts/collect_pod_logs_manual.py`

---

**סיכום:** עכשיו יש לך יכולת לראות **בדיוק מה קורה** בטסטים:
- ✅ בקשות/תשובות HTTP מלאות
- ✅ לוגים מהשרתים בזמן אמת
- ✅ שמירה לקבצים לניתוח מאוחר יותר
- ✅ הכל אוטומטי וקל לשימוש!

**תהנה מהדיבוג! 🎉**

