# 🚀 Story 1: מדריך מהיר - gRPC Stream Validation

**גרסה:** 2.0  
**תאריך עדכון:** 2025-10-27  
**זמן קריאה:** 5 דקות

---

## 📌 מה השתנה?

### ⚠️ עדכון קריטי

**Story Points:** 8 → **13** (הגדלה של 62%)

**הסיבה:** הסיפור המקורי לא לקח בחשבון:
1. יצירת **proto files** מאפס (אין קבצי protobuf קיימים בפרויקט)
2. טיפול ב-**self-signed SSL certificates**
3. **Retry logic** מתקדם לטיפול בכשלים זמניים
4. **Performance metrics collection** מקיפה
5. **Integration** עמוקה עם תשתית קיימת

---

## 🎯 סיכום הסיפור המעודכן

### מטרה עסקית

**בתור** מהנדס QA Automation  
**אני רוצה** לוודא שstream של gRPC מספק נתוני spectrogram תקינים  
**כדי** לוודא שהנתונים זורמים נכון מ-Focus Server דרך gRPC Job ועד Frontend

### הפער הנוכחי

| יש לנו ✅ | חסר לנו ❌ |
|----------|-----------|
| בדיקות REST API מלאות | בדיקת קישוריות gRPC |
| תשתית Kubernetes | בדיקת streaming בזמן אמת |
| RabbitMQ automation | מדידת ביצועי stream |
| MongoDB validation | טיפול בשגיאות streaming |

---

## 🏗️ ארכיטקטורה טכנית

### רכיבים חדשים שייבנו

```
📦 protos/
  └─ datastream.proto           ← הגדרת Protocol Buffers

📦 src/models/proto_generated/
  ├─ datastream_pb2.py          ← קוד Python מ-proto
  └─ datastream_pb2_grpc.py     ← gRPC stubs

📦 src/apis/
  └─ grpc_stream_client.py      ← Client מתקדם לgRPC

📦 tests/integration/grpc/
  ├─ conftest.py                ← Fixtures
  ├─ test_grpc_connectivity.py  ← בדיקות חיבור
  ├─ test_grpc_data_validity.py ← בדיקות תוכן
  └─ test_grpc_performance.py   ← בדיקות ביצועים
```

### התלויות שנוסיף

```python
# requirements.txt
grpcio>=1.59.0                    # gRPC runtime
grpcio-tools>=1.59.0              # Protobuf compiler
protobuf>=4.25.0                  # Protocol buffers
grpcio-health-checking>=1.59.0    # Health check support
```

---

## 📋 פירוט המשימות (6 Tasks)

### Task 1.1: Setup Infrastructure (4h)

**מה עושים:**
- יוצרים מבנה תיקיות
- מוסיפים dependencies
- יוצרים `datastream.proto`
- מייצרים Python code מה-proto
- יוצרים fixtures ל-pytest

**קריטריוני הצלחה:**
```bash
# בודקים שהקומפילציה עובדת
python -m grpc_tools.protoc --version

# מייצרים את הקבצים
bash scripts/generate_proto.sh

# בודקים ייבוא
python -c "from src.models.proto_generated import datastream_pb2"
```

---

### Task 1.2: Implement GrpcStreamClient (8h)

**מה בונים:**

```python
class GrpcStreamClient:
    """
    Client מתקדם ל-gRPC streaming.
    
    Features:
    - חיבור אוטומטי עם retry
    - Streaming עם timeouts
    - TLS/SSL support
    - Metrics collection
    - Logging מקיף
    """
    
    def connect(self, url: str, port: int) -> bool:
        """מתחבר לשרת gRPC"""
    
    def stream_spectrograms(self, job_id: str, max_frames: int):
        """Stream נתוני spectrogram"""
        
    def disconnect(self):
        """סוגר חיבור"""
    
    def get_metrics(self) -> StreamMetrics:
        """מחזיר מדדי ביצועים"""
```

**שימוש לדוגמה:**

```python
# חיבור פשוט
client = GrpcStreamClient(connection_timeout=10)
client.connect("10.10.100.100", 50051)

# Stream data
for frame in client.stream_spectrograms("12-70788", max_frames=100):
    print(f"Received {len(frame.rows)} rows")

client.disconnect()

# או עם context manager
with client.connect_context("10.10.100.100", 50051):
    for frame in client.stream_spectrograms("12-70788"):
        process_frame(frame)
# Disconnect אוטומטי
```

---

### Task 1.3: Connectivity Tests (4h)

**בדיקות שניישם:**

1. ✅ **test_grpc_stream_connects_successfully**
   - בודק שהחיבור מצליח
   - זמן תגובה < 10 שניות

2. ✅ **test_grpc_stream_delivers_first_frame**
   - Frame ראשון מגיע תוך < 5 שניות
   - Frame תקין ומכיל נתונים

3. ✅ **test_grpc_stream_handles_invalid_job_id**
   - טיפול תקין ב-job_id לא חוקי
   - שגיאה ברורה למשתמש

4. ✅ **test_grpc_stream_stops_on_job_completion**
   - Stream נעצר בצורה תקינה
   - אין timeouts או תקיעות

---

### Task 1.4: Data Validity Tests (5h)

**בדיקות שניישם:**

1. ✅ **test_grpc_stream_frame_structure_valid**
   ```python
   # בודק שיש:
   - frame.rows (רשימת שורות)
   - frame.current_max_amp (אמפליטודה מקסימלית)
   - frame.current_min_amp (אמפליטודה מינימלית)
   ```

2. ✅ **test_grpc_stream_data_dimensions_correct**
   ```python
   # בודק:
   - מספר sensors תואם תצורה
   - אורך intensity array נכון
   - מספר frequency bins תקין
   ```

3. ✅ **test_grpc_stream_frequency_range_correct**
   ```python
   # מוודא:
   - תדרים בטווח המוגדר
   - אין ערכים out-of-range
   ```

4. ✅ **test_grpc_stream_data_not_all_zeros**
   ```python
   # מוודא שיש נתונים אמיתיים:
   - לא כל הערכים אפס
   - אמפליטודה סבירה
   - Stream לא תקוע
   ```

---

### Task 1.5: Performance Tests (4h)

**בדיקות ביצועים:**

1. ✅ **test_grpc_stream_continuous_delivery**
   ```python
   # מודד:
   - Frame rate consistency (ללא drops)
   - Jitter (שונות בזמנים)
   ```

2. ✅ **test_grpc_stream_performance_metrics**
   ```python
   # מדדים:
   - Throughput: > 10 fps
   - Latency P95: < 1 שניה
   - Bandwidth: MB/sec
   ```

---

### Task 1.6: Documentation (3h)

**תיעוד שניצור:**

1. **README.md** - סקירת הפרויקט
2. **GRPC_TESTING_GUIDE.md** - מדריך משתמש
3. **GRPC_CLIENT_API.md** - תיעוד API
4. **TROUBLESHOOTING.md** - פתרון בעיות נפוצות

---

## 📊 מדדי הצלחה

### מדדים כמותיים

| מדד | יעד | איך מודדים |
|-----|-----|------------|
| **Test Coverage** | >90% | `pytest --cov=src/apis/grpc_stream_client` |
| **Success Rate** | >95% | 100 ריצות רצופות |
| **First Frame Latency** | <5s | מדידה אוטומטית |
| **Throughput** | >10 fps | Performance tests |

### מדדים איכותיים

- ✅ Code review מאושר על ידי 2+ senior engineers
- ✅ אפס באגים קריטיים בפרודקשן אחרי חודש
- ✅ הצוות מאמץ את הפריימוורק לפיצ'רים חדשים
- ✅ Feedback חיובי מהמפתחים

---

## 🚧 סיכונים וצעדי מניעה

### סיכונים טכניים

| סיכון | השפעה | הסתברות | מניעה |
|-------|-------|---------|-------|
| **אין proto files רשמיים** | 🔴 High | 🟡 Medium | לבקש מצוות הפיתוח / reverse engineer |
| **Self-signed SSL** | 🟡 Medium | 🔴 High | תמיכה ב-insecure connections |
| **Network instability** | 🟡 Medium | 🔴 High | Retry logic + timeouts |
| **gRPC job startup delay** | 🟡 Medium | 🟡 Medium | Polling + increased timeouts |

### המלצות

1. **התחל עם Proto Files:**
   - בקש proto files רשמיים מצוות Backend
   - אם לא זמינים - צור מתיעוד + reverse engineering

2. **SSL Certificates:**
   - בסביבת Test: השתמש ב-`insecure_channel`
   - בסביבת Production: הוסף self-signed cert למערכת

3. **Timeouts:**
   - Connection: 10 שניות
   - Stream: 300 שניות (5 דקות)
   - Retry: 3 ניסיונות עם 2 שניות delay

4. **Cleanup:**
   - תמיד השתמש ב-fixtures עם cleanup
   - בדוק שאין resource leaks
   - נקה gRPC jobs אחרי כל טסט

---

## 🎯 Definition of Done

### Checklist

- [ ] כל הקוד merged ל-main branch
- [ ] כל הטסטים עוברים ב-CI/CD
- [ ] Code review מאושר על ידי 2+ reviewers
- [ ] תיעוד מלא ונבדק
- [ ] Demo הוצג לצוות
- [ ] אין באגים קריטיים/גבוהים
- [ ] Test coverage >90%
- [ ] Performance benchmarks מתועדים

---

## 🔗 קישורים רלוונטיים

### תיעוד קיים

- [Focus Server API Endpoints](./FOCUS_SERVER_API_ENDPOINTS.md)
- [gRPC Job Lifecycle](../infrastructure/GRPC_JOB_LIFECYCLE.md)
- [Testing Guide](./MEETING_PREPARATION_SUMMARY.md)

### תיעוד חיצוני

- [gRPC Python Documentation](https://grpc.io/docs/languages/python/)
- [Protocol Buffers Guide](https://developers.google.com/protocol-buffers)
- [pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)

---

## 💡 Quick Start (5 דקות)

### התקנה

```bash
# 1. התקן dependencies
pip install -r requirements.txt

# 2. התקן gRPC tools
pip install grpcio grpcio-tools

# 3. יצור proto files
bash scripts/generate_proto.sh

# 4. בדוק שהכל עובד
python -c "from src.models.proto_generated import datastream_pb2"
```

### שימוש ראשון

```python
from src.apis.grpc_stream_client import GrpcStreamClient

# יצור client
client = GrpcStreamClient()

# התחבר
client.connect("10.10.100.100", 50051)

# Stream data
for frame in client.stream_spectrograms("12-70788", max_frames=10):
    print(f"Frame: {len(frame.rows)} rows")

# נתק
client.disconnect()
```

### הרצת טסטים

```bash
# כל טסטי gRPC
pytest tests/integration/grpc/ -v

# רק connectivity tests
pytest tests/integration/grpc/test_grpc_connectivity.py -v

# עם coverage
pytest tests/integration/grpc/ --cov=src/apis/grpc_stream_client
```

---

## 📞 שאלות?

**Story Owner:** QA Automation TL  
**Technical Lead:** Backend Architect  
**Slack:** #automation-framework

**תאריך עדכון:** 2025-10-27  
**גרסה:** 2.0

