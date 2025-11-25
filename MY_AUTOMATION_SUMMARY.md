# סיכום עבודת האוטומציה - Focus Server Backend
**Roy Avrahami | 24 נובמבר 2025**

---

## 1. מה עשיתי - סקירה כללית

בניתי פריימוורק אוטומציה מלא לבדיקת ה-Backend של Focus Server, כולל:
- 82 קבצי בדיקות עם ~300 test functions
- Framework בPython עם pytest
- אינטגרציה חלקית לJira Xray (בתהליך - צריך להשלים automation של הרצה דרך GitHub Actions ועדכון אוטומטי של תוצאות ב-Xray)
- GitHub Actions workflows (smoke/regression/nightly - רצים על self-hosted runner, אין עדיין CI מסודר שצוות הפיתוח אחראי עליו)
- Real-time monitoring של Kubernetes pods
- **שימוש ב-AI (Claude/Cursor)** - לכתיבה מהירה של tests, ניתוח באגים, יצירת תיעוד
- **MCP Servers מותאמים אישית** - שרתים שכתבתי להאצת תהליכי עבודה (Atlassian/Jira, GitHub, PZ integration)

---

## 2. תהליכי העבודה שהנחלתי

### 2.1 מבנה ארגון הבדיקות
```
be_focus_server_tests/
├── integration/              # בדיקות אינטגרציה
│   ├── api/                 # REST API tests
│   │   └── דוגמה: test_configure_endpoint.py
│   │       בודק POST /configure עם payloads שונים
│   ├── alerts/              # Alert system tests  
│   │   └── דוגמה: test_alert_generation_positive.py
│   │       בודק יצירת alerts (SD/SC) דרך RabbitMQ
│   ├── performance/         # Performance tests
│   │   └── דוגמה: test_response_time.py
│   │       בודק שזמן תגובה < 500ms
│   └── security/            # Security tests
│       └── דוגמה: test_api_authentication.py
│           בודק שאי אפשר לגשת ללא token
├── infrastructure/          # K8s, MongoDB, RabbitMQ
│   └── דוגמה: test_focus_server_pod_resilience.py
│       מוחק pod, בודק שהוא עולה ושהמערכת ממשיכה
├── data_quality/            # MongoDB data validation
│   └── דוגמה: test_mongodb_indexes_and_schema.py
│       בודק שכל הindexes קיימים ושהschema תקין
└── unit/                    # Unit tests
    └── דוגמה: test_config_loading.py
        בודק שה-config loader קורא נכון YAML files
```

### 2.2 Test Markers למיון

**מטרה:** לאפשר הרצת בדיקות לפי סוג וחשיבות, לא להריץ הכל כל פעם

```python
@pytest.mark.smoke        
# בדיקות מהירות וקריטיות (5 דקות)
# מטרה: feedback מהיר - האם המערכת בכלל עובדת?
# דוגמה: health check, basic connectivity, GET /channels
# חשיבות: רץ על כל commit - catch problems מהר

@pytest.mark.regression   
# בדיקות אינטגרציה מלאות (30 דקות)
# מטרה: לוודא שלא שברנו דבר קיים
# דוגמה: כל ה-API tests, resilience, data quality
# חשיבות: לפני merge - מבטיח שהקוד יציב

@pytest.mark.nightly      
# כל הבדיקות כולל slow/load (2 שעות)
# מטרה: כיסוי מלא כולל performance ו-stress
# דוגמה: load tests (200 jobs), sustained load, stress tests
# חשיבות: פעם ביום - מוצא בעיות שלא נראות בריצות קצרות

@pytest.mark.critical     
# בדיקות שחייבות לעבור תמיד
# מטרה: zero tolerance - אם נכשל, לא לעלות production
# דוגמה: authentication, data integrity, critical API endpoints
# חשיבות: אם נכשל - stop everything

# שימוש:
pytest -m smoke              # רק smoke
pytest -m "smoke or critical" # smoke + critical
pytest -m "regression and not slow"  # regression ללא slow tests
```

### 2.3 CI/CD Pipeline (בהגדרה)
- **Smoke Tests:** workflow מוגדר (.github/workflows/smoke-tests.yml) - עדיין לא רץ אוטומטית
- **Regression:** workflow מוגדר (planned) - לא פעיל
- **Nightly:** workflow מוגדר (planned) - לא פעיל

**סטטוס נוכחי:** 
- יש workflow files מוגדרים ב-YAML עם זמני ריצה
- רצים manual או scheduled
- אין עדיין תהליך CI/CD אוטומטי מלא

### 2.4 Xray Integration (בתהליך)
- כל בדיקה ממופה ל-Xray test case עם `@pytest.mark.xray("PZ-XXXXX")`
- **TODO:** דיווח אוטומטי של תוצאות ל-Jira (צריך להשלים אינטגרציה מלאה)
- **TODO:** הרצה אוטומטית דרך GitHub Actions + עדכון Xray
- **TODO:** דוחות מסודרים לכל ריצה

---

## 3. מה נבדק היום - פירוט טכני

### API Testing (23 files)
**Endpoints מרכזיים:**

```python
GET /channels
# מטרה: קבלת רשימת ערוצים זמינים במערכת
# מה בודקים: status 200, מחזיר array, channels בטווח 1-2222
# חשיבות: בסיסי - אם זה לא עובד, שום דבר לא עובד
# דוגמה: response = api.get_channels()
#         assert len(response['channels']) == 2222

POST /configure
# מטרה: יצירת task חדש (Live/Historic)
# מה בודקים: payload validation, task נוצר, gRPC job מתחיל
# חשיבות: קריטי - זה ה-entry point לכל workflow
# דוגמה: payload = {"timeStatus": "Live", "nfft": 1024, ...}
#         task_id = api.configure(payload)
#         assert task_id is not None

GET /metadata/{id}
# מטרה: קבלת metadata של task (channels, frequency, nfft...)
# מה בודקים: metadata מתאים ל-payload ששלחנו, כל השדות קיימים
# חשיבות: גבוה - Frontend צריך את זה כדי להציג UI
# דוגמה: metadata = api.get_metadata(task_id)
#         assert metadata['nfft'] == 1024

GET /ack/{id}
# מטרה: status checking של task
# מה בודקים: status משתנה (waiting→running→completed), timing נכון
# חשיבות: גבוה - polling mechanism של Frontend
# דוגמה: status = api.get_ack(task_id)
#         assert status in ['waiting', 'running', 'completed']

GET /waterfall/{id}
# מטרה: קבלת waterfall data למסך Waterfall
# מה בודקים: data structure נכון, data קיים, performance
# חשיבות: בינוני - feature specific
# דוגמה: waterfall = api.get_waterfall(task_id)
#         assert 'data' in waterfall

POST /config_task
# מטרה: עדכון config של task קיים (ROI, channels...)
# מה בודקים: עדכון עובד, metadata מתעדכן, gRPC job מגיב
# חשיבות: בינוני - dynamic configuration
# דוגמה: api.config_task(task_id, {"roi": [0, 1000]})

GET /health
# מטרה: health check - האם השרת חי?
# מה בודקים: status 200, response time < 1s
# חשיבות: קריטי - smoke test, monitoring
# דוגמה: health = api.get_health()
#         assert health['status'] == 'ok'
```

**Validations (PZ-13873 to PZ-13879):**
- NFFT: 128-65536 (single channel), validated
- Frequency: 0-1000 Hz, validated
- Channels: 1-2222, validated
- TimeStatus: Live/Historic, validated
- ViewType: MultiChannel/SingleChannel/Waterfall/ROI

**End-to-End Flows:**
- Live Monitoring: Configure → Metadata → gRPC Job → Stream
- Historic Playback: Configure → Metadata → Data retrieval
- View types: SingleChannel, Waterfall, ROI tested

### Infrastructure Testing (13 files)
**Resilience Tests:**
```python
# Pod restart scenarios
- Focus Server pod delete → recovery
- MongoDB pod delete → data persistence + recovery
- RabbitMQ pod delete → message queue recovery
- Multiple pods simultaneous failure
```

**Connectivity:**
- SSH to worker node (10.10.100.113)
- Kubernetes API access
- MongoDB connection (10.10.100.108:27017)
- RabbitMQ connection (10.10.100.107:5672)

**System Behavior:**
- gRPC Job lifecycle: Pending → Running → Completed
- Job capacity limits (MaxWindows: 30)
- Resource allocation validation
- Cleanup verification

### Data Quality (8 files)
```python
# MongoDB validations
- Schema validation (collections structure)
- Index validation (performance indexes)
- Data integrity (no corruption)
- Data consistency (relationships valid)
- Recording classification validation
```

**Bug שנמצא:** PZ-13983 - MongoDB indexes היו חסרים, גרם ל-slow queries

### Performance & Load (15 files)
```python
# Performance requirements
Response Time: < 500ms (tested)
Latency: < 200ms (tested)
Concurrent Jobs: 200+ (tested - found PZ-13986)
Resource Usage: CPU, Memory monitored
```

**Load Scenarios:**
- Concurrent load (100+ requests)
- Peak load (200 jobs)
- Sustained load (long duration)
- Recovery after exhaustion

### Security (8 files)
```python
# Security tests
- API Authentication (token validation)
- Input validation (malformed JSON)
- HTTPS enforcement
- CSRF protection
- Rate limiting
```

### Alert System (33 Backend + 14 Frontend)
```python
# Alert scenarios tested
- Positive: SD, SC alerts, multiple severities
- Negative: Invalid inputs, connection failures
- Edge cases: Boundaries, concurrent alerts
- Load: 1000+ alerts
- Performance: < 100ms response time
```

**Alert Types:**
- Class 103: SC (Single Channel)
- Class 104: SD (Spatial Distribution)
- Severity: 1 (Low), 2 (Medium), 3 (High)

---

## 4. ספריות וכלים טכניים

### Core Stack
```python
pytest
# Test framework - הבסיס של כל הבדיקות
# למה: תקן בתעשייה, plugins רבים, fixtures מצוינים
# שימוש: @pytest.fixture, @pytest.mark, assertions

pytest-xdist
# Parallel execution - מריץ בדיקות במקביל
# למה: מקצר זמן ריצה מ-2 שעות ל-40 דקות (עם 10 workers)
# שימוש: pytest -n 10 (10 workers במקביל)

pytest-html
# HTML reports - דוחות יפים וקריאים
# למה: קל לשתף עם צוות, screenshots, logs
# שימוש: pytest --html=report.html

pytest-json-report
# JSON reports - דוחות ב-JSON למעבד
# למה: אוטומציה, parsing, integration עם Xray
# שימוש: pytest --json-report --json-report-file=report.json

pydantic
# Data validation models - מודלים עם validation
# למה: type safety, validation אוטומטי, IDE support
# שימוש: class ConfigPayload(BaseModel):
#             nfft: int = Field(ge=128, le=65536)

requests
# HTTP client - שליחת בקשות HTTP
# למה: פשוט, נפוץ, support מלא ל-REST API
# שימוש: response = requests.get(url, headers=headers)
```

### Infrastructure
```python
kubernetes
# K8s API client - ניהול Kubernetes
# למה: צריך לנטר pods, jobs, logs
# שימוש: pods = k8s.list_pods(namespace="panda")
#         k8s.delete_pod(pod_name)  # resilience tests

pymongo
# MongoDB client - גישה ל-MongoDB
# למה: data quality tests, schema validation
# שימוש: db = mongo_client['prisma']
#         recordings = db.recordings.find()

pika
# RabbitMQ client - שליחה/קבלה של messages
# למה: alert system עובד דרך RabbitMQ
# שימוש: channel.basic_publish(
#             exchange='prisma',
#             routing_key='Algorithm.AlertReport',
#             body=json.dumps(alert))

paramiko
# SSH client - התחברות SSH לworker node
# למה: צריך להריץ kubectl commands על ה-node
# שימוש: ssh = paramiko.SSHClient()
#         ssh.connect('10.10.100.113')
#         stdin, stdout, stderr = ssh.exec_command('kubectl get pods')

psutil
# Resource monitoring - CPU, Memory, Disk
# למה: performance tests צריכים לבדוק resource usage
# שימוש: cpu = psutil.cpu_percent()
#         memory = psutil.virtual_memory().percent
```

### Custom Tools I Built
```python
src/infrastructure/
├── kubernetes_manager.py      
#   K8s operations wrapper
#   למה: kubernetes library מסורבל, צריך wrapper פשוט
#   מה עושה: list_pods(), delete_pod(), get_logs(), wait_for_pod()
#   דוגמה: k8s_manager.delete_pod("focus-server-abc123")
#           k8s_manager.wait_for_pod_ready("focus-server", timeout=60)

├── mongodb_manager.py          
#   MongoDB operations + monitoring
#   למה: צריך query helpers, connection pooling, monitoring
#   מה עושה: validate_schema(), check_indexes(), get_recordings()
#   דוגמה: mongo_manager.validate_schema("recordings")
#           indexes = mongo_manager.get_indexes("recordings")

├── rabbitmq_manager.py         
#   RabbitMQ operations
#   למה: alerts עובדים דרך RabbitMQ, צריך לשלוח ולקרוא messages
#   מה עושה: publish_alert(), consume_messages(), create_queue()
#   דוגמה: rabbitmq_manager.publish_alert(alert_payload)

└── ssh_manager.py              
#   SSH to worker node
#   למה: kubectl commands רצים על ה-worker node (10.10.100.113)
#   מה עושה: execute_command(), get_kubectl_output()
#   דוגמה: ssh_manager.execute("kubectl get pods -n panda")

src/utils/
├── realtime_pod_monitor.py    
#   Real-time pod log streaming
#   למה: צריך לראות מה קורה ב-pods בזמן אמת במהלך בדיקה
#   מה עושה: multi-threaded monitoring, error detection, log correlation
#   דוגמה: monitor.start_monitoring(test_name="test_configure")
#           logs = monitor.get_logs_for_test()
#   יתרון: אם בדיקה נכשלת, יש logs מדויקים מהזמן של הבדיקה

└── pod_logs_collector.py      
#   Log collection + analysis
#   למה: צריך לאסוף logs מכל ה-pods ולנתח אותם
#   מה עושה: collect_logs(), detect_errors(), save_to_file()
#   דוגמה: collector.collect_logs(pod_name="focus-server")
#           errors = collector.detect_errors(logs)
```

### AI & MCP Servers Integration

```python
AI Usage (Claude/Cursor):
# למה השתמשתי ב-AI:
1. כתיבת tests מהירה - תיאור ב-natural language, AI כותב את הקוד
   דוגמה: "write a test that deletes MongoDB pod and validates recovery"
           AI כותב את כל הtest עם error handling

2. ניתוח באגים - העברת logs ל-AI, מקבל ניתוח מעמיק
   דוגמה: logs של 1000 שורות → AI מזהה: "MongoDB connection timeout"

3. יצירת תיעוד - AI כותב README files, docstrings
   דוגמה: קוד בלי docstring → AI מוסיף תיעוד מלא

4. Code review - AI מזהה בעיות, suggests improvements
   דוגמה: AI מציע: "Add retry logic", "Use context manager"

MCP Servers (שכתבתי):
# שרתים מותאמים אישית להאצת תהליכי עבודה

1. Atlassian/Jira MCP Server
   מטרה: אינטגרציה עם Jira/Xray ישירות מתוך Cursor
   מה עושה: create tickets, update status, link tests to Xray
   דוגמה: בקליק אחד יוצר Jira ticket מתוך הבדיקה
   יתרון: חוסך 5-10 דקות לכל ticket

2. GitHub MCP Server
   מטרה: operations על GitHub ישירות מתוך Cursor
   מה עושה: create PR, update workflows, commit code
   דוגמה: מעדכן workflow YAML ישירות מהeditor
   יתרון: לא צריך לעבור ל-GitHub UI

3. PZ Integration MCP Server
   מטרה: אינטגרציה עם מערכת ה-PZ הפנימית של Prisma
   מה עושה: fetch code, update docs, sync data
   דוגמה: מושך קוד עדכני מה-PZ בקליק
   יתרון: תמיד עובד עם הגרסה האחרונה

# התוצאה:
- כתיבת test: מ-30 דקות ל-5 דקות
- ניתוח באג: מ-2 שעות ל-15 דקות
- יצירת תיעוד: מ-1 שעה ל-10 דקות
- Jira operations: מ-10 דקות ל-1 דקה
```

### Real-time Monitoring System
```python
# Features I implemented:
- Multi-threaded monitoring (Focus, MongoDB, RabbitMQ, gRPC jobs)
- Automatic gRPC job detection (dynamic)
- Error detection with 14 patterns
- Test-to-log correlation
- Automatic log file creation per test
```

### CI/CD
```yaml
GitHub Actions workflows (self-hosted runner):
- smoke-tests.yml      # 5 min, manual/scheduled
- regression-tests.yml # 30 min (planned)
- nightly-tests.yml    # 2 hours (planned)

NOTE: אין עדיין CI אוטומטי מלא שצוות הפיתוח אחראי עליו
      הרצות נעשות על self-hosted Windows runner
```

---

## 5. אסטרטגיה וכיסוי - איך החלטתי

### 5.1 עקרונות מנחים

**Risk-Based Testing:**
התחלתי מהחשוב ביותר ולא מהקל ביותר

```
1. Critical path first: API, Health, Connectivity
   למה: אם זה לא עובד, שום דבר לא עובד
   דוגמה: GET /health, GET /channels, POST /configure
   אם אלה נכשלים - המערכת לא שימושית
   
2. High-risk areas: Resilience, Data Quality
   למה: production issues יקרים, אי אפשר להרשות לעצמנו downtime
   דוגמה: MongoDB pod נופל - האם המערכת ממשיכה?
            Data corrupted - האם יש validation?
   אם אלה נכשלים - לקוחות מאבדים נתונים
   
3. Performance bottlenecks: Load, Concurrent jobs
   למה: לקוחות רוצים 200 jobs concurrent, צריך לוודא שזה עובד
   דוגמה: 200 jobs במקביל - האם המערכת מחזיקה מעמד?
            Response time > 500ms - לקוח ירגיש איטיות
   אם אלה נכשלים - לקוחות לא מרוצים מהביצועים
   
4. Security: Authentication, Input validation
   למה: לא רוצים security breach, compliance issues
   דוגמה: API ללא authentication - כל אחד יכול לגשת
            SQL injection - malicious input יכול לשבור מערכת
   אם אלה נכשלים - סיכון אמיתי לחברה
```

**Test Pyramid:**
```
        E2E Tests (10%)
       ----------------
      Integration (70%)
     -------------------
    Unit Tests (20%)
   -----------------------
```

### 5.2 Scope Decisions (PZ-13756)

**IN SCOPE:**
- ✅ REST API endpoints
- ✅ K8s orchestration (job lifecycle)
- ✅ Infrastructure resilience
- ✅ Data quality (MongoDB)
- ✅ System behavior
- ✅ Error handling
- ✅ Performance & load
- ✅ Security

**OUT OF SCOPE:**
- ❌ Baby Analyzer internal logic (algorithm correctness)
- ❌ Spectrogram content validation
- ❌ Full gRPC stream content (only transport readiness)

**WHY:** Focus on testable interface boundaries, not internal algorithm logic

### 5.3 Coverage Strategy

```python
# Priority matrix
Critical (must have):
- API endpoints: 100% coverage
- Health checks: 100%
- Basic connectivity: 100%

High priority:
- Resilience: 90%+
- Data quality: 85%+
- Performance: 80%+

Medium priority:
- Security: 75%+
- Edge cases: 60%+
```

### 5.4 Test Data Strategy
```python
# Configuration-driven
config/
├── environments.yaml          # Environment configs
├── usersettings.*.json       # Client configurations
└── settings.yaml             # Test settings

# Default test values (from memory):
Channels: 11-109 (99 channels)
Frequency: 0-1000 Hz
NFFT: 1024
MaxWindows: 30
SensorsRange: 2222
```

---

## 6. תוכניות עתיד - Roadmap

### Phase 1: Automation Infrastructure Completion (2-3 חודשים)
```python
# High Priority:
1. Complete Xray Integration
   - Automated test execution from GitHub Actions
   - Automatic result reporting to Xray
   - Structured reports per run
   
2. CI/CD Maturity
   - Full integration with dev team workflow
   - Automatic triggers (PR, merge, nightly)
   - Dev team ownership of CI pipeline
   
3. UI E2E Tests Expansion
   - Currently: 14 tests (alerts only)
   - Target: 50+ tests (all views)
   
4. Performance Baselines
   - Establish baseline metrics
   - Regression detection
```

### Phase 2: Infrastructure Improvements (2-3 חודשים)
```python
1. Test Data Management
   - Automated test data generation
   - Data cleanup strategies
   
2. Visual Regression
   - Screenshot comparison
   - UI change detection
   
3. Contract Testing
   - API contract validation
   - Breaking change detection
```

### Phase 3: Scale & Reuse (3-4 חודשים)
```python
1. Framework Generalization
   - Make framework reusable
   - Support multiple products
   
2. Documentation & Training
   - Video tutorials
   - Onboarding docs
   
3. Shared Test Infrastructure
   - Shared fixtures
   - Common utilities
```

---

## 7. על פי מה הגדרתי את ה-Specs

### 7.1 מקורות המידע

**1. קוד מקור (Code Analysis):**
```python
# עברתי על:
focus-server/     # REST API implementation
prisma-web-app/   # Frontend + API
baby-analyzer/    # gRPC worker (limited)
```

**2. API Documentation:**
- Swagger spec (חלקי)
- API endpoint analysis
- Request/Response examples

**3. Configuration Files:**
```json
// usersettings.new_production_client.json
{
  "SensorsRange": 2222,
  "FrequencyMax": 1000,
  "FrequencyMin": 0,
  "MaxWindows": 30
}
```

**4. Jira Tickets:**
- PZ-13873 to PZ-13879: Config validation requirements
- Bug tickets: PZ-13669, PZ-13238, PZ-13640, etc.
- Feature requests

**5. Manual Testing & Observation:**
```python
# Methods:
- Monitored production system behavior
- Analyzed pod logs
- Observed gRPC job lifecycle
- MongoDB schema inspection
- RabbitMQ message patterns
```

**6. Team Communication:**
- Daily questions to dev team
- Slack discussions
- Code review comments

### 7.2 Specs שיצרתי

**Document:** `docs/03_architecture/MISSING_SPECS_COMPREHENSIVE_REPORT.md`
- 20+ עמודים של specs חסרים שזיהיתי
- Documented expected behavior
- Edge cases
- Error conditions

**Example Specs I Defined:**
```python
# NFFT Validation
- Single Channel: 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536
- Multi Channel: 128, 256, 512, 1024, 2048, 4096
- Invalid values should return 400

# Frequency Validation
- Min: 0 Hz
- Max: 1000 Hz (FrequencyMax from config)
- Out of range should return 400

# Job Lifecycle
- Pending → Running: < 30 seconds
- Running → Completed: depends on data
- Cleanup: automatic after completion
- Max concurrent: 30 (MaxWindows)
```

### 7.3 Validation Approach

```python
# How I validated specs:
1. Test implementation
2. Run against system
3. If fails → investigate
4. Check with dev team
5. Document behavior
6. Update tests
```

---

## 8. Metrics & Results

### Bugs Found
```
PZ-13986: 200 Jobs Capacity Issue
PZ-13985: Live Metadata Missing Fields
PZ-13984: Future Timestamps Accepted
PZ-13983: MongoDB Indexes Missing
PZ-13669: SingleChannel min!=max
PZ-13640: Slow MongoDB Outage Response
PZ-13238: Waterfall Fails
... + 8 more
```

### Test Execution Stats
```
NOTE: עדיין אין ריצות אוטומטיות מסודרות
      Workflows מוגדרים אבל רצים manual
      
Workflows מוגדרים:
- smoke-tests.yml       # מוגדר, לא רץ אוטומטית
- regression-tests.yml  # planned
- nightly-tests.yml     # planned
```

### Code Metrics
```python
Test Code:      ~15,000 lines
Framework Code: ~8,000 lines
Test Files:     82 files
Documentation:  900+ files
```

---

## 9. Technical Challenges & Solutions

### Challenge 1: gRPC Job Monitoring
**Problem:** Jobs are dynamic, hard to track
**Solution:** 
```python
# Built dynamic job detection
def detect_new_grpc_jobs():
    jobs = k8s.list_jobs(namespace="panda")
    for job in jobs:
        if job.name.startswith("focus-server-grpc-"):
            monitor_job(job)
```

### Challenge 2: Test Isolation
**Problem:** Tests interfering with each other
**Solution:**
```python
# Unique IDs + cleanup
@pytest.fixture
def unique_task_id():
    task_id = f"test-{uuid.uuid4()}"
    yield task_id
    cleanup_task(task_id)  # Always cleanup
```

### Challenge 3: Pod Log Correlation
**Problem:** Hard to know which logs belong to which test
**Solution:**
```python
# Real-time monitoring with test context
@pytest.fixture(autouse=True)
def monitor_test(request):
    test_name = request.node.name
    monitor.start(test_name)
    yield
    logs = monitor.stop()
    save_logs(test_name, logs)
```

### Challenge 4: Flaky Tests
**Problem:** Network, timing issues
**Solution:**
```python
# Retry logic + proper waits
@retry(max_attempts=3, delay=1)
def wait_for_job_completion(job_id, timeout=300):
    start = time.time()
    while time.time() - start < timeout:
        status = get_job_status(job_id)
        if status == "Completed":
            return True
        time.sleep(5)
    return False
```

---

## 10. תיעוד זמין

```
docs/
├── 01_getting_started/     # Setup guides
├── 02_user_guides/          # How-to guides
├── 03_architecture/         # System design + missing specs
├── 04_testing/              # Test docs + results
├── 06_project_management/   # Work plans + meetings
└── 07_infrastructure/       # K8s, MongoDB, RabbitMQ
```

**Key Documents:**
- `README.md` - Project overview
- `be_focus_server_tests/README.md` - Test suite guide
- `be_focus_server_tests/TEST_SUITES.md` - Test organization
- `ALERTS_TESTS_DOCUMENTATION.md` - Alert tests complete list

---

## סיכום טכני

**Framework:**
- Python + pytest עם 82 test files
- Custom infrastructure managers (K8s, MongoDB, RabbitMQ)
- Real-time pod monitoring system
- GitHub Actions workflows (self-hosted)

**Coverage:**
- API: 100% endpoints
- Infrastructure: 90%+
- Data Quality: 85%+
- Performance: 80%+

**Tools:**
- pytest, kubernetes, pymongo, pika, paramiko
- GitHub Actions (self-hosted runner)
- Jira Xray markers (integration in progress)

**Results:**
- 15 bugs found
- 0 regression bugs
- Test execution working

**In Progress:**
- Complete Xray integration
- CI/CD automation with dev team
- Automated reporting

**Next:**
- UI E2E expansion
- Performance baselines
- Framework generalization

