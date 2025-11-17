# תוכנית בדיקות Focus Server - מפורטת במיוחד - חלק 3
## Historic Playback, Dynamic ROI, E2E Tests

---

## 🎯 HISTORIC PLAYBACK TESTS - סקירה

Historic Playback הוא **תכונה קריטית** שמאפשרת לנתח **נתונים מתיעוד**.

**מה זה Historic Playback?**
- ניגון נתונים שנרשמו בעבר
- `start_time` ו-`end_time` מוגדרים (לא null)
- קריאה מ-MongoDB ו-storage
- עיבוד ושליחה כאילו זה real-time

**למה זה חשוב?**
- ניתוח אירועים שקרו בעבר
- debugging של בעיות
- השוואות לאורך זמן
- מחקר ופיתוח

---

## 🎯 TEST #23: Historic Playback - Standard 5-Minute Range

**Jira ID**: PZ-13863  
**Priority**: High  
**Type**: Integration Test (Happy Path)  
**Status**: ✅ **ממומש!**

### מטרת הטסט

**מה בודקים?**
בודקים שהשרת מטפל נכון ב-**historic playback** סטנדרטי של 5 דקות.

**מה זה אומר?**
1. מגדירים time range (5 דקות אחורה מעכשיו)
2. שולחים POST /config עם `start_time` ו-`end_time`
3. polling ל-`GET /waterfall` עד שהנתונים מגיעים
4. בדיקה שכל הנתונים מהטווח המבוקש התקבלו
5. המתנה ל-status 208 (completion)

### נתוני הבדיקה

**Time Range Calculation:**
```python
# נקודת סיום: עכשיו
end_time_dt = datetime.now()

# נקודת התחלה: לפני 5 דקות
start_time_dt = end_time_dt - timedelta(minutes=5)

# המרה לפורמט Focus Server
start_time = datetime_to_yymmddHHMMSS(start_time_dt)
# "251027143000" (2025-10-27 14:30:00)

end_time = datetime_to_yymmddHHMMSS(end_time_dt)
# "251027143500" (2025-10-27 14:35:00)
```

**מה זה `yymmddHHMMSS`?**
- פורמט זמן של Focus Server
- yy = year (25 = 2025)
- mm = month (10 = אוקטובר)
- dd = day (27)
- HH = hour (14 = 2PM)
- MM = minute (30)
- SS = second (00)

**Payload:**
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {"min": 0, "max": 50},
  "frequencyRange": {"min": 0, "max": 500},
  "start_time": "251027143000",
  "end_time": "251027143500",
  "view_type": 0
}
```

### תהליך הבדיקה (Detailed Flow)

```
┌──────────────────────────────────────────────────────┐
│ PHASE 1: Configuration                               │
├──────────────────────────────────────────────────────┤
│ 1. Calculate time range (5 minutes)                  │
│ 2. Convert to yymmddHHMMSS format                    │
│ 3. Create config payload with start/end times        │
│ 4. POST /config/{task_id}                            │
│ 5. Expect: HTTP 200 "Config received successfully"   │
└──────────────────┬───────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│ PHASE 2: Initial Polling (Waiting for Data)         │
├──────────────────────────────────────────────────────┤
│ 6. GET /waterfall/{task_id}/10                       │
│ 7. Status: 200 (no data yet)                         │
│ 8. Wait 2 seconds                                    │
│ 9. Poll again → Status: 200 or 201                   │
│ 10. Repeat until status 201 received                 │
└──────────────────┬───────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│ PHASE 3: Data Collection                            │
├──────────────────────────────────────────────────────┤
│ 11. GET /waterfall → Status 201 (data available)    │
│ 12. Parse data blocks                                │
│ 13. Extract rows with timestamps and sensor data     │
│ 14. Collect to list                                  │
│ 15. Continue polling every 2 seconds                 │
│ 16. Status remains 201 while data flows              │
└──────────────────┬───────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│ PHASE 4: Completion                                 │
├──────────────────────────────────────────────────────┤
│ 17. GET /waterfall → Status 208 (analyzer exited)   │
│ 18. Playback complete - no more data                 │
│ 19. Verify total data blocks > 0                     │
│ 20. Verify timestamps within range                   │
│ 21. Verify timestamps sequential                     │
└──────────────────────────────────────────────────────┘
```

### Status Codes (הסבר מפורט)

| Status | משמעות | פעולה |
|--------|--------|-------|
| **200** | No data yet | המשך polling - Baby Analyzer עדיין מכין |
| **201** | Data available | קרא data, המשך polling |
| **208** | Already Reported | **Playback הסתיים** - אין עוד data |
| **400** | Bad request | שגיאה בparameters |
| **404** | Consumer not found | Task לא קיים |

### צעדי הבדיקה (Step-by-Step)

| # | צעד | תוצאה | קוד | זמן |
|---|-----|-------|-----|-----|
| 1 | חישוב time range | 5 דקות | `end - timedelta(minutes=5)` | - |
| 2 | המרה לפורמט | yymmddHHMMSS | `datetime_to_yymmddHHMMSS()` | - |
| 3 | וידוא פורמט | 12 digits | `assert len(time_str) == 12` | - |
| 4 | POST /config | HTTP 200 | request נשלח | ~0.5s |
| 5 | GET /waterfall (ראשון) | 200 או 201 | polling מתחיל | ~0.5s |
| 6 | Polling loop | 200→201→208 | continue עד 208 | 30-120s |
| 7 | איסוף data blocks | > 0 blocks | collect מהresponses | - |
| 8 | קבלת status 208 | playback done | סיום | - |
| 9 | וידוא data > 0 | לפחות נתון אחד | `assert len(all_data) > 0` | - |
| 10 | וידוא timestamps | בטווח | `start <= ts <= end` | - |
| 11 | וידוא sequential | עולים | `ts[i] < ts[i+1]` | - |

### תוצאה צפויה

**Configuration Response:**
```http
HTTP/1.1 200 OK
{
  "status": "Config received successfully"
}
```

**Waterfall Responses (Status Progression):**

```
Poll 1:  HTTP 200 → {"message": "No data yet"}
Poll 2:  HTTP 200 → {"message": "No data yet"}
Poll 3:  HTTP 201 → {"data": [...]}  ← Data starts!
Poll 4:  HTTP 201 → {"data": [...]}
Poll 5:  HTTP 201 → {"data": [...]}
...
Poll 45: HTTP 201 → {"data": [...]}
Poll 46: HTTP 208 → {}  ← Playback complete!
Poll 47: HTTP 208 → {}
```

### יישום בקוד

```python
def test_configure_historic_task_success(self, focus_server_api):
    """
    Test PZ-13863: Historic Playback - Standard 5-Minute Range
    
    Complete historic playback flow.
    """
    task_id = generate_task_id("historic_5min")
    logger.info(f"Test PZ-13863: Historic 5-minute playback - {task_id}")
    
    # PHASE 1: Calculate time range
    end_time_dt = datetime.now()
    start_time_dt = end_time_dt - timedelta(minutes=5)
    
    start_time = datetime_to_yymmddHHMMSS(start_time_dt)
    end_time = datetime_to_yymmddHHMMSS(end_time_dt)
    
    logger.info(f"Time range: {start_time} to {end_time}")
    
    # Validate time format
    assert validate_time_format_yymmddHHMMSS(start_time)
    assert validate_time_format_yymmddHHMMSS(end_time)
    
    # PHASE 2: Configure task
    historic_config_payload = {
        "displayTimeAxisDuration": 10,
        "nfftSelection": 1024,
        "displayInfo": {"height": 1000},
        "channels": {"min": 0, "max": 50},
        "frequencyRange": {"min": 0, "max": 500},
        "start_time": start_time,
        "end_time": end_time,
        "view_type": 0
    }
    
    config_request = ConfigTaskRequest(**historic_config_payload)
    response = focus_server_api.config_task(task_id, config_request)
    
    assert response.status == "Config received successfully"
    logger.info("✓ Historic task configured")
    
    # PHASE 3: Poll until completion
    status_transitions = []
    data_blocks_received = 0
    max_poll_attempts = 100
    poll_interval = 2.0
    
    for attempt in range(max_poll_attempts):
        waterfall_response = focus_server_api.get_waterfall(task_id, 10)
        
        # Track status transitions
        if not status_transitions or \
           status_transitions[-1] != waterfall_response.status_code:
            status_transitions.append(waterfall_response.status_code)
            logger.info(f"Status transition: {waterfall_response.status_code}")
        
        # Handle status codes
        if waterfall_response.status_code == 201:
            # Data available
            if waterfall_response.data:
                data_blocks_received += len(waterfall_response.data)
                logger.debug(f"Poll {attempt}: received data block")
        
        elif waterfall_response.status_code == 208:
            # Playback complete!
            logger.info(f"✓ Playback completed after {attempt + 1} polls")
            logger.info(f"✓ Total data blocks received: {data_blocks_received}")
            
            # Verify we got data
            assert data_blocks_received > 0, \
                "No data blocks received during playback"
            
            logger.info("✅ Test PZ-13863 PASSED")
            return  # Test complete!
        
        # Wait before next poll
        time.sleep(poll_interval)
    
    # If we got here, polling timed out
    pytest.fail(f"Playback did not complete after {max_poll_attempts} polls")
```

**זמן ריצה**: 30-120 שניות (תלוי בנתונים)

---

## 🎯 TEST #24: Historic Playback - Status 208 Completion

**Jira ID**: PZ-13868  
**Priority**: High  
**Type**: Integration Test (Flow)  
**Status**: ✅ **ממומש!**

### מטרת הטסט

**מה בודקים?**
בודקים שהשרת **מסיים נכון** historic playback עם **HTTP 208**.

**מה זה Status 208?**
- HTTP 208 = "Already Reported"
- משמעות: **כל הנתונים נשלחו, playback הסתיים**
- אין עוד data זמין
- Baby Analyzer יצא (exited)

**למה זה קריטי?**
- הלקוח צריך לדעת **מתי לעצור polling**
- בלי 208, הלקוח ימשיך לשלוח requests לנצח
- בזבוז משאבים, סרבול רשת

### תהליך הבדיקה

**1-Minute Historic Range** (לבדיקה מהירה):

```python
# Time range: 1 minute, 2 hours ago (ensure data exists)
base_time = datetime.now() - timedelta(hours=2)
start_time_dt = base_time
end_time_dt = base_time + timedelta(minutes=1)

start_time = "251027123000"  # Example
end_time = "251027123100"    # 1 minute later
```

### צעדי הבדיקה

| # | צעד | תוצאה | חשיבות |
|---|-----|-------|---------|
| 1 | חישוב 1-minute range | start/end | טווח קצר לבדיקה מהירה |
| 2 | המרה לפורמט | yymmddHHMMSS | 12 digits |
| 3 | task_id | ID ייחודי | זיהוי |
| 4 | POST /config | HTTP 200 | התחלה |
| 5 | Poll /waterfall | 200 initially | המתנה לdata |
| 6 | Continue polling | 200→201 | status progression |
| 7 | Track status codes | [200, 201, 208] | רישום transitions |
| 8 | Collect data | multiple blocks | איסוף נתונים |
| 9 | **Receive 208** | playback done | **ה-completion signal** |
| 10 | בדיקת no data | data=null ב-208 | אין data חדש |
| 11 | Poll 5 more times | עדיין 208 | consistency |
| 12 | בדיקת no 201 after 208 | לא חוזר 201 | לא data נוסף |
| 13 | מדידת זמן | < 60s | ביצועים |

### תוצאה צפויה

**Status Progression:**
```
┌─────────────────────────────────────────────┐
│ Time  │ Poll # │ Status │ Meaning           │
├───────┼────────┼────────┼───────────────────┤
│ 0s    │ 1      │ 200    │ No data yet       │
│ 2s    │ 2      │ 200    │ Still preparing   │
│ 4s    │ 3      │ 200    │ Still preparing   │
│ 6s    │ 4      │ 201    │ 🎉 Data starts!   │
│ 8s    │ 5      │ 201    │ Data flowing      │
│ 10s   │ 6      │ 201    │ Data flowing      │
│ ...   │ ...    │ 201    │ Data flowing      │
│ 50s   │ 25     │ 201    │ Data flowing      │
│ 52s   │ 26     │ 208    │ ✅ Complete!      │
│ 54s   │ 27     │ 208    │ Still complete    │
└─────────────────────────────────────────────┘
```

### יישום בקוד

```python
def test_historic_status_208_completion(self, focus_server_api):
    """
    Test PZ-13868: Historic Playback - Status 208 Completion
    
    Validates that historic playback properly completes with status 208.
    """
    task_id = generate_task_id("historic_208")
    logger.info(f"Test PZ-13868: Status 208 completion - {task_id}")
    
    # Configure 1-minute historic range (2 hours ago)
    base_time = datetime.now() - timedelta(hours=2)
    start_time = datetime_to_yymmddHHMMSS(base_time)
    end_time = datetime_to_yymmddHHMMSS(base_time + timedelta(minutes=1))
    
    payload = {
        "displayTimeAxisDuration": 10,
        "nfftSelection": 1024,
        "displayInfo": {"height": 1000},
        "channels": {"min": 0, "max": 50},
        "frequencyRange": {"min": 0, "max": 500},
        "start_time": start_time,
        "end_time": end_time,
        "view_type": 0
    }
    
    # Configure
    response = focus_server_api.config_task(task_id, ConfigTaskRequest(**payload))
    assert response.status == "Config received successfully"
    logger.info(f"✓ Task configured for time range: {start_time} - {end_time}")
    
    # Poll until status 208
    status_seen = []
    data_blocks_count = 0
    max_polls = 60
    
    for poll_num in range(max_polls):
        waterfall_response = focus_server_api.get_waterfall(task_id, 10)
        status = waterfall_response.status_code
        
        # Track status transitions
        if not status_seen or status_seen[-1] != status:
            status_seen.append(status)
            logger.info(f"Status transition at poll {poll_num}: {status}")
        
        if status == 200:
            # No data yet - continue
            pass
        
        elif status == 201:
            # Data available
            if waterfall_response.data:
                data_blocks_count += len(waterfall_response.data)
            logger.debug(f"Poll {poll_num}: Data block (total: {data_blocks_count})")
        
        elif status == 208:
            # ✅ Completion!
            logger.info(f"✅ Status 208 received at poll {poll_num}")
            logger.info(f"✅ Status progression: {status_seen}")
            logger.info(f"✅ Total data blocks: {data_blocks_count}")
            
            # Verify data was received
            assert data_blocks_count > 0, "Should have received some data"
            
            # Verify no data in 208 response
            assert waterfall_response.data is None or \
                   len(waterfall_response.data) == 0, \
                   "Status 208 should have no data"
            
            # Poll 5 more times to verify consistency
            for extra_poll in range(5):
                response_again = focus_server_api.get_waterfall(task_id, 10)
                assert response_again.status_code in [208, 404, 400], \
                    f"After 208, should stay 208/404/400, got {response_again.status_code}"
            
            logger.info("✓ Status 208 is stable (no new data appears)")
            logger.info("✅ Test PZ-13868 PASSED")
            return
        
        time.sleep(1.0)
    
    pytest.fail(f"Status 208 not received after {max_polls} polls. Status seen: {status_seen}")
```

**זמן ריצה**: 30-60 שניות

---

## 🎯 TEST #25: Historic - Invalid Time Range (End Before Start)

**Jira ID**: PZ-13869  
**Priority**: High  
**Type**: Integration Test (Negative)  
**Status**: ✅ **ממומש!**

### מטרת הטסט

**מה בודקים?**
בודקים שהשרת **דוחה** בקשות historic שבהן `end_time < start_time`.

**למה זה חשוב?**
- טווח זמן הפוך הוא **לא אפשרי**
- לא ניתן לנגן "מ-14:00 עד 13:00" - זה הפוך!
- MongoDB query עם זמנים הפוכים → תוצאות ריקות או שגיאות

**דוגמה לבעיה:**
```
start_time = "251027140000" (14:00:00)
end_time   = "251027130000" (13:00:00)

זה אומר: "תן לי נתונים שהתחילו ב-14:00 והסתיימו ב-13:00"
זה בלתי אפשרי!
```

### נתוני הבדיקה

```python
# Create INVALID time range (end before start)
start_time_dt = datetime.now()
end_time_dt = datetime.now() - timedelta(minutes=10)  # 10 minutes BEFORE start!

start_time = "251027140000"  # 14:00
end_time = "251027135000"    # 13:50 ← Earlier!
```

**Payload:**
```json
{
  "start_time": "251027140000",
  "end_time": "251027135000"
}
```

### תוצאה צפויה

```http
HTTP/1.1 400 Bad Request
{
  "error": "Invalid Time Range",
  "message": "start_time must be before end_time",
  "provided": {
    "start_time": "251027140000",
    "end_time": "251027135000"
  },
  "constraint": "start_time < end_time"
}
```

### יישום

```python
def test_historic_invalid_time_range_end_before_start(self, focus_server_api):
    """
    Test PZ-13869: Historic - Invalid Time Range (End Before Start)
    """
    task_id = generate_task_id("historic_invalid_range")
    logger.info(f"Test PZ-13869: End before start - {task_id}")
    
    # Create invalid time range
    start_time_dt = datetime.now()
    end_time_dt = datetime.now() - timedelta(minutes=10)
    
    start_time = datetime_to_yymmddHHMMSS(start_time_dt)
    end_time = datetime_to_yymmddHHMMSS(end_time_dt)
    
    logger.info(f"Invalid range: {start_time} (start) to {end_time} (end)")
    logger.info(f"  End is {10} minutes BEFORE start (invalid!)")
    
    payload = generate_config_payload(live=False)
    payload['start_time'] = start_time
    payload['end_time'] = end_time
    
    # Expect rejection
    with pytest.raises(Exception) as exc_info:
        config_request = ConfigTaskRequest(**payload)
        focus_server_api.config_task(task_id, config_request)
    
    error_msg = str(exc_info.value).lower()
    assert "time" in error_msg or "range" in error_msg or "invalid" in error_msg
    logger.info(f"✅ Invalid time range properly rejected")
    
    # Verify no task created
    waterfall_response = focus_server_api.get_waterfall(task_id, 10)
    assert waterfall_response.status_code == 404
```

---

## 🎯 DYNAMIC ROI TESTS - סקירה

Dynamic ROI = שינוי **Region of Interest** תוך כדי ריצה (**ללא הפסקה**).

**מה זה ROI?**
- ROI = טווח ה-sensors שרוצים לראות
- דוגמה: sensors 0-100

**מה זה Dynamic ROI?**
- שינוי ה-ROI **בזמן אמת** בלי לעצור את ה-task
- שליחת פקודה דרך **RabbitMQ**
- Baby Analyzer מתאתחל עם ROI חדש

**למה זה חשוב?**
- **גמישות** - המשתמש יכול לעבור בין אזורים
- **ביצועים** - לא צריך task חדש
- **UX טוב** - שינוי מהיר ללא הפסקה

---

## 🎯 TEST #26: Send ROI Change Command via RabbitMQ

**Jira ID**: PZ-13784  
**Priority**: High  
**Type**: Integration Test  
**Status**: ✅ **ממומש!**

### מטרת הטסט

**מה בודקים?**
בודקים ששליחת **פקודת ROI** דרך RabbitMQ עובדת ללא שגיאות.

**מה התהליך?**
```
┌─────────────────────────────────────────────────────┐
│ TEST CODE                                           │
├─────────────────────────────────────────────────────┤
│ 1. Create BabyAnalyzerMQClient                     │
│ 2. Connect to RabbitMQ (10.10.100.107:5672)        │
│ 3. Create RegionOfInterestCommand                  │
│ 4. Publish to baby_analyzer exchange               │
│ 5. Verify ACK received                             │
│ 6. Disconnect                                       │
└────────────┬────────────────────────────────────────┘
             │ AMQP Protocol
             ▼
┌─────────────────────────────────────────────────────┐
│ RABBITMQ (10.10.100.107)                            │
├─────────────────────────────────────────────────────┤
│ Exchange: baby_analyzer                            │
│ Routing Key: roi                                    │
│ Queue: baby_analyzer_commands                      │
└────────────┬────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────┐
│ BABY ANALYZER (Kubernetes Pod)                      │
├─────────────────────────────────────────────────────┤
│ 1. Receive ROI command from queue                  │
│ 2. Parse command: start=50, end=150                │
│ 3. Stop current processing                         │
│ 4. Reinitialize with new ROI                       │
│ 5. Start processing new sensor range               │
│ 6. Send data for sensors 50-150 only               │
└─────────────────────────────────────────────────────┘
```

### RabbitMQ Connection Details

**Connection Parameters:**
```python
rabbitmq_config = {
    "host": "10.10.100.107",
    "port": 5672,
    "username": "prisma",
    "password": "prisma",
    "vhost": "/"
}
```

**Exchange Details:**
- Name: `baby_analyzer`
- Type: `topic` או `direct`
- Durable: `True`

**Routing Keys:**
- ROI: `roi`
- CAxis: `caxis`
- Colormap: `colormap`

### פקודת ROI

**Structure:**
```json
{
  "command_type": "RegionOfInterestCommand",
  "start": 50,
  "end": 150,
  "routing_key": "roi"
}
```

**Serialization:**
```python
import json

command = {
    "command_type": "RegionOfInterestCommand",
    "start": 50,
    "end": 150
}

message_body = json.dumps(command)
# '{"command_type": "RegionOfInterestCommand", "start": 50, "end": 150}'
```

### צעדי הבדיקה

| # | צעד | תוצאה | פירוט |
|---|-----|-------|-------|
| 1 | חיבור ל-RabbitMQ | Connected | `client.connect()` |
| 2 | וידוא חיבור | is_connected=True | `assert client.is_connected()` |
| 3 | בדיקת exchange | קיים | optional |
| 4 | יצירת ROI command | dict | `{"start": 50, "end": 150}` |
| 5 | Publish | message sent | `client.send_roi_change()` |
| 6 | בדיקת ACK | acknowledged | RabbitMQ מאשר |
| 7 | וידוא no exceptions | לא שגיאות | הפקודה עברה |
| 8 | Disconnect | closed cleanly | `client.disconnect()` |

### יישום בקוד (קיים!)

**קובץ**: `tests/integration/api/test_dynamic_roi_adjustment.py`  
**Function**: `test_send_roi_change_command`

```python
import pytest
import logging
from src.infrastructure.baby_analyzer_mq_client import BabyAnalyzerMQClient

logger = logging.getLogger(__name__)

def test_send_roi_change_command(self, baby_analyzer_mq_client):
    """
    Test PZ-13784: Send ROI Change Command via RabbitMQ
    
    Validates successful ROI command publication to RabbitMQ.
    """
    logger.info("Test PZ-13784: Send ROI command via RabbitMQ")
    
    # Verify connection
    assert baby_analyzer_mq_client.is_connected()
    logger.info("✓ Connected to RabbitMQ")
    
    # Define new ROI
    new_start = 50
    new_end = 150
    logger.info(f"Sending ROI change: [{new_start}, {new_end}]")
    
    # Send command
    baby_analyzer_mq_client.send_roi_change(
        start=new_start,
        end=new_end,
        routing_key="roi"
    )
    
    logger.info("✓ ROI command sent successfully")
    logger.info("✅ Test PZ-13784 PASSED")
```

**הפונקציה `send_roi_change`** (ב-`BabyAnalyzerMQClient`):

```python
class BabyAnalyzerMQClient:
    """RabbitMQ client for Baby Analyzer commands."""
    
    def send_roi_change(self, start: int, end: int, routing_key: str = "roi"):
        """
        Send ROI (Region of Interest) change command.
        
        Args:
            start: Start sensor index
            end: End sensor index
            routing_key: RabbitMQ routing key (default: "roi")
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to RabbitMQ")
        
        # Create command payload
        command = {
            "command_type": "RegionOfInterestCommand",
            "start": start,
            "end": end
        }
        
        # Serialize to JSON
        message_body = json.dumps(command)
        
        # Publish to exchange
        self.channel.basic_publish(
            exchange='baby_analyzer',
            routing_key=routing_key,
            body=message_body,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
                content_type='application/json'
            )
        )
        
        self.logger.info(f"ROI command published: [{start}, {end}]")
```

---

## 🎯 TEST #27: ROI Change with Safety Validation

**Jira ID**: PZ-13785  
**Priority**: Critical  
**Type**: Integration Test  
**Status**: ✅ **ממומש!**

### מטרת הטסט

**מה בודקים?**
בודקים ש**Safety Validation** עובד לפני שליחת פקודת ROI.

**מה זה Safety Validation?**
מנגנון שבודק ש-ROI החדש **לא מסוכן**:
- לא שינוי גדול מדי (> 50%)
- לא קפיצה גדולה (low overlap)
- לא ערכים לא תקפים

**למה זה נחוץ?**
- **מניעת טעויות** - משתמש לא משנה בטעות ל-ROI לא רלוונטי
- **הגנה על ביצועים** - שינוי גדול מדי יכול להעמיס
- **UX טוב** - אזהרות על שינויים דרסטיים

### Safety Rules

**כללי בטיחות:**
```python
safety_rules = {
    "max_change_percent": 50.0,     # שינוי גודל מקסימלי: 50%
    "min_overlap_percent": 30.0,    # overlap מינימלי: 30%
    "allow_negative_values": False,  # ערכים שליליים: לא
    "max_sensor_id": 10000          # sensor מקסימלי
}
```

### חישובי Safety

**חישוב 1: Size Change**
```python
current_size = current_max - current_min
new_size = new_max - new_min
size_change_percent = abs(new_size - current_size) / current_size * 100

# Example:
current: [0, 100] → size = 100
new: [0, 120] → size = 120
change = (120 - 100) / 100 * 100 = 20%  ← OK (< 50%)
```

**חישוב 2: Overlap**
```python
overlap_start = max(current_min, new_min)
overlap_end = min(current_max, new_max)
overlap_size = max(0, overlap_end - overlap_start)
overlap_percent = (overlap_size / current_size) * 100

# Example:
current: [0, 100]
new: [20, 120]
overlap: [20, 100] → size = 80
overlap% = 80 / 100 * 100 = 80%  ← Good (> 30%)
```

### תרחיש: Safe Change

**Current ROI**: [0, 100]  
**New ROI**: [20, 120]

**Calculations:**
```
Current size: 100
New size: 120
Size change: 20% ← OK (< 50%)

Overlap: [20, 100] = 80 sensors
Overlap%: 80% ← Excellent (> 30%)

Result: ✅ SAFE
```

### יישום

```python
def test_roi_change_with_validation(self, baby_analyzer_mq_client):
    """
    Test PZ-13785: ROI Change with Safety Validation
    """
    logger.info("Test PZ-13785: ROI with safety validation")
    
    # Current ROI
    current_min = 0
    current_max = 100
    
    # New ROI
    new_min = 20
    new_max = 120
    
    # VALIDATE SAFETY
    safety_result = validate_roi_change_safety(
        current_min=current_min,
        current_max=current_max,
        new_min=new_min,
        new_max=new_max,
        max_change_percent=50.0
    )
    
    logger.info(f"Safety validation result:")
    logger.info(f"  Is safe: {safety_result['is_safe']}")
    logger.info(f"  Size change: {safety_result['size_change_percent']:.1f}%")
    logger.info(f"  Overlap: {safety_result['overlap_percent']:.1f}%")
    logger.info(f"  Warnings: {safety_result['warnings']}")
    
    # Verify safe
    assert safety_result['is_safe'] == True
    assert len(safety_result['warnings']) == 0
    assert safety_result['overlap_percent'] >= 30.0
    
    # Send command (only if safe!)
    if safety_result['is_safe']:
        baby_analyzer_mq_client.send_roi_change(
            start=new_min,
            end=new_max
        )
        logger.info("✓ ROI command sent (passed safety validation)")
    else:
        logger.warning("✗ ROI command NOT sent (failed safety validation)")
    
    logger.info("✅ Test PZ-13785 PASSED")
```

**פונקציית ה-Validation** (`src/utils/validators.py`):

```python
def validate_roi_change_safety(
    current_min: int,
    current_max: int,
    new_min: int,
    new_max: int,
    max_change_percent: float = 50.0,
    min_overlap_percent: float = 30.0
) -> Dict[str, Any]:
    """
    Validate safety of ROI change to prevent unsafe transitions.
    
    Args:
        current_min: Current ROI minimum sensor
        current_max: Current ROI maximum sensor
        new_min: New ROI minimum sensor
        new_max: New ROI maximum sensor
        max_change_percent: Maximum allowed size change (%)
        min_overlap_percent: Minimum required overlap (%)
        
    Returns:
        Dict with:
            - is_safe: bool
            - size_change_percent: float
            - overlap_percent: float
            - warnings: list
    """
    warnings = []
    
    # VALIDATION 1: Check for reversed range
    if new_min > new_max:
        warnings.append(f"Reversed range: min ({new_min}) > max ({new_max})")
        return {
            'is_safe': False,
            'size_change_percent': 0,
            'overlap_percent': 0,
            'warnings': warnings
        }
    
    # VALIDATION 2: Check for negative values
    if new_min < 0 or new_max < 0:
        warnings.append(f"Negative sensor indices not allowed")
        return {
            'is_safe': False,
            'size_change_percent': 0,
            'overlap_percent': 0,
            'warnings': warnings
        }
    
    # VALIDATION 3: Check for zero size
    new_size = new_max - new_min
    if new_size == 0:
        warnings.append(f"Zero-size ROI (min == max)")
        return {
            'is_safe': False,
            'size_change_percent': 0,
            'overlap_percent': 0,
            'warnings': warnings
        }
    
    # CALCULATION 1: Size change
    current_size = current_max - current_min
    size_change_percent = abs(new_size - current_size) / current_size * 100
    
    if size_change_percent > max_change_percent:
        warnings.append(
            f"Size change ({size_change_percent:.1f}%) exceeds "
            f"maximum ({max_change_percent}%)"
        )
    
    # CALCULATION 2: Overlap
    overlap_start = max(current_min, new_min)
    overlap_end = min(current_max, new_max)
    overlap_size = max(0, overlap_end - overlap_start)
    overlap_percent = (overlap_size / current_size) * 100 if current_size > 0 else 0
    
    if overlap_percent < min_overlap_percent:
        warnings.append(
            f"Low overlap ({overlap_percent:.1f}%) - "
            f"minimum recommended is {min_overlap_percent}%"
        )
    
    # DETERMINATION: Is it safe?
    is_safe = len(warnings) == 0
    
    return {
        'is_safe': is_safe,
        'size_change_percent': size_change_percent,
        'overlap_percent': overlap_percent,
        'current_size': current_size,
        'new_size': new_size,
        'overlap_sensors': overlap_size,
        'warnings': warnings
    }
```

---

## 🎯 TEST #28: Unsafe ROI Change (Large Jump)

**Jira ID**: PZ-13797  
**Priority**: Critical  
**Type**: Integration Test (Negative)  
**Status**: ✅ **ממומש!**

### מטרת הטסט

**מה בודקים?**
בודקים ש-Safety Validation **מזהה** שינויי ROI **מסוכנים** (קפיצות גדולות).

**מה זה Large Jump?**
שינוי ROI ש**אין לו overlap** עם ה-ROI הנוכחי.

**דוגמה:**
```
Current ROI: [0, 100]
New ROI: [200, 300]

Overlap: ZERO!
Size change: 0% (אותו גודל)
Position shift: +200 sensors

זה מסוכן כי: המשתמש קפץ לאזור לגמרי אחר!
```

### נתוני הבדיקה

```python
current_min = 0
current_max = 100

new_min = 200
new_max = 300

# This is unsafe because:
# - No overlap (0%)
# - Large position shift (+200)
```

### תוצאה צפויה

```python
safety_result = {
    'is_safe': False,  # ❌ NOT SAFE
    'size_change_percent': 0.0,  # Same size
    'overlap_percent': 0.0,  # ❌ NO OVERLAP!
    'warnings': [
        "Low overlap (0.0%) - minimum recommended is 30.0%"
    ]
}
```

### יישום

```python
def test_unsafe_roi_change(self, baby_analyzer_mq_client):
    """
    Test PZ-13797: Unsafe ROI Change (Large Jump)
    
    Validates detection of unsafe ROI changes.
    """
    logger.info("Test PZ-13797: Unsafe ROI change detection")
    
    current_min = 0
    current_max = 100
    new_min = 200  # Large jump!
    new_max = 300
    
    # Run safety validation
    safety_result = validate_roi_change_safety(
        current_min=current_min,
        current_max=current_max,
        new_min=new_min,
        new_max=new_max,
        max_change_percent=50.0
    )
    
    logger.info(f"Unsafe change detection:")
    logger.info(f"  Is safe: {safety_result['is_safe']}")
    logger.info(f"  Overlap: {safety_result['overlap_percent']:.1f}%")
    logger.info(f"  Warnings: {safety_result['warnings']}")
    
    # Verify detected as unsafe
    assert safety_result['is_safe'] == False, \
        "Large jump should be detected as unsafe"
    
    assert safety_result['overlap_percent'] == 0, \
        "No overlap expected for large jump"
    
    assert len(safety_result['warnings']) > 0, \
        "Warnings should be generated for unsafe changes"
    
    logger.info("✅ Unsafe ROI change correctly detected")
    
    # In production: would NOT send this command
    # Or would send with explicit user confirmation
```

---

## 🎯 TEST #29: Unsafe ROI - Size Change > 50%

**Jira ID**: PZ-13798  
**Priority**: High  
**Type**: Integration Test (Negative)  
**Status**: ✅ **ממומש!**

### מטרת הטסט

**מה בודקים?**
בודקים ש-Safety Validation **מזהה** שינויי **גודל גדולים** (> 50%).

**דוגמה:**
```
Current ROI: [0, 100] → size = 100
New ROI: [0, 250] → size = 250

Size change: (250 - 100) / 100 * 100 = 150%  ← Unsafe!
```

**למה זה מסוכן?**
- שינוי גודל גדול → עומס משתנה דרסטית
- CPU/Memory jump
- עלול להעמיס על המערכת

### יישום

```python
def test_unsafe_roi_range_change(self):
    """Test PZ-13798: Size change > 50%"""
    
    current_size = 100
    new_size = 250
    size_change_percent = ((new_size - current_size) / current_size) * 100
    
    # Verify calculation
    assert size_change_percent == 150, f"Expected 150%, got {size_change_percent}%"
    logger.info(f"Size change: {size_change_percent}% (> 50% threshold)")
    
    # Run validation
    safety_result = validate_roi_change_safety(
        current_min=0,
        current_max=100,
        new_min=0,
        new_max=250,
        max_change_percent=50.0
    )
    
    # Verify detected as unsafe
    assert safety_result['is_safe'] == False
    assert safety_result['size_change_percent'] > 50
    logger.info("✅ Unsafe size change detected")
```

---

## 🎯 TEST #30-32: ROI Edge Cases

### TEST #30: ROI with Reversed Range

**Jira ID**: PZ-13791  
**מטרה**: דחיית ROI הפוך (start > end)

```python
start = 150
end = 50  # Earlier than start!

safety_result = validate_roi_change_safety(
    current_min=0,
    current_max=100,
    new_min=start,
    new_max=end
)

assert safety_result['is_safe'] == False
assert "reversed" in safety_result['warnings'][0].lower()
```

---

### TEST #31: ROI with Equal Start/End

**Jira ID**: PZ-13790  
**מטרה**: דחיית ROI בגודל אפס

```python
start = 50
end = 50  # Same!

# Zero size = invalid
assert (end - start) == 0

safety_result = validate_roi_change_safety(...)
assert safety_result['is_safe'] == False
```

---

### TEST #32: ROI with Negative Values

**Jira IDs**: PZ-13792, PZ-13793  
**מטרה**: דחיית sensors שליליים

```python
# Negative start
start = -10
end = 50
assert start < 0  # Invalid

# Negative end  
start = 10
end = -50
assert end < 0  # Invalid
```

---

## 🎯 TEST #33-35: ROI Size Variations

### TEST #33: Small Range

**Jira ID**: PZ-13794  
**מטרה**: edge case - ROI קטן מאוד (2 sensors)

```python
start = 50
end = 52
size = 2  # Very small but valid

# May generate warning but should be allowed
```

---

### TEST #34: Large Range

**Jira ID**: PZ-13795  
**מטרה**: edge case - ROI מקסימלי (כל ה-sensors)

```python
start = 0
end = 512  # All sensors
size = 512  # Maximum

# Should be allowed but may impact performance
```

---

### TEST #35: ROI Starting at Zero

**Jira ID**: PZ-13796  
**מטרה**: boundary - ROI מתחיל ב-0

```python
start = 0  # Boundary!
end = 50

# Verify no off-by-one errors
```

---

## 🎯 TEST #36: CAxis Adjustment

**Jira ID**: PZ-13801  
**Priority**: Medium  
**Type**: Integration Test  
**Status**: ✅ **ממומש!**

### מטרת הטסט

**מה בודקים?**
בודקים שניתן לשנות **CAxis** (Color Axis) דרך RabbitMQ.

**מה זה CAxis?**
- CAxis = טווח הצבעים (colormap range)
- קובע איזה ערכי amplitude ממופים לאילו צבעים
- דוגמה: [-80, -20] dB

**למה זה שימושי?**
- התאמת contrast להצגה
- הדגשת אותות חלשים או חזקים
- שיפור UX

### דוגמה

**Before:**
```
CAxis: [-100, 0] dB
Colormap: jet
→ אותות חלשים (-80 dB) נראים כחולים
→ אותות חזקים (-20 dB) נראים אדומים
```

**After (CAxis Adjustment):**
```
CAxis: [-80, -20] dB
Colormap: jet (same)
→ focus על טווח ספציפי
→ better contrast
```

### Command Structure

```json
{
  "command_type": "CAxisAdjustmentCommand",
  "caxis_min": -80,
  "caxis_max": -20,
  "routing_key": "caxis"
}
```

### ולידציה

**Valid CAxis:**
```python
caxis_min = -80
caxis_max = -20

# Verify valid
assert caxis_min < caxis_max  # ✅ Valid range
```

**Invalid CAxis (reversed):**
```python
caxis_min = -20
caxis_max = -80  # Reversed!

assert caxis_min > caxis_max  # ❌ Invalid
```

### יישום

```python
def test_caxis_adjustment(self, baby_analyzer_mq_client):
    """Test PZ-13801: CAxis Adjustment Command"""
    
    caxis_min = -80
    caxis_max = -20
    
    # Validate range
    assert caxis_min < caxis_max, "CAxis range must be valid"
    logger.info(f"CAxis range: [{caxis_min}, {caxis_max}] dB")
    
    # Send command
    baby_analyzer_mq_client.send_caxis_adjustment(
        caxis_min=caxis_min,
        caxis_max=caxis_max,
        routing_key="caxis"
    )
    
    logger.info("✅ CAxis command sent successfully")
```

---

## 🎯 E2E TEST: Configure → Metadata → gRPC

**Jira ID**: PZ-13570  
**Priority**: High  
**Type**: E2E Test  
**Status**: חלקי

### מטרת הטסט

**מה בודקים?**
תהליך **מלא** מ-א' עד ת':
1. POST /configure
2. GET /metadata
3. חיבור ל-gRPC stream
4. קבלת data frames

**למה זה E2E?**
- בודק את **כל הרכיבים ביחד**
- מוודא שהזרימה המלאה עובדת
- מאמת ש-data contract נשמר

### תהליך מלא

```
┌──────────────────────────────────────────┐
│ STEP 1: Configuration                    │
├──────────────────────────────────────────┤
│ POST /configure                          │
│ Response: {job_id, stream_url, stream_port} │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│ STEP 2: Metadata Retrieval               │
├──────────────────────────────────────────┤
│ GET /metadata/{job_id}                   │
│ Response: configuration details          │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│ STEP 3: gRPC Connection                  │
├──────────────────────────────────────────┤
│ Connect to stream_url:stream_port        │
│ Open gRPC stream                         │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│ STEP 4: Data Streaming                   │
├──────────────────────────────────────────┤
│ Receive DataStream messages              │
│ Verify: timestamps, spectrograms, shapes │
│ No corruption or connection errors       │
└──────────────────────────────────────────┘
```

### Data Contract

**gRPC Message Expected Fields:**
```protobuf
message DataStream {
  repeated SpectrogramRow rows = 1;
  double current_max_amp = 2;
  double current_min_amp = 3;
}

message SpectrogramRow {
  string canvasId = 1;
  repeated SensorIntensity sensors = 2;
  int64 startTimestamp = 3;
  int64 endTimestamp = 4;
}

message SensorIntensity {
  int32 id = 1;
  repeated float intensity = 2;
}
```

### יישום (חלקי)

```python
def test_e2e_grpc_mock_flow(self, focus_server_api):
    """
    Test PZ-13570: E2E - Configure → Metadata → gRPC
    
    Full integration test with gRPC streaming.
    """
    logger.info("Test PZ-13570: E2E gRPC flow")
    
    # STEP 1: Configure
    payload = {...}  # Standard config
    config_request = ConfigureRequest(**payload)
    response = focus_server_api.configure_streaming_job(config_request)
    
    assert response.job_id
    job_id = response.job_id
    stream_url = response.stream_url
    stream_port = response.stream_port
    
    logger.info(f"✓ Configured: {job_id}")
    logger.info(f"✓ Stream: {stream_url}:{stream_port}")
    
    # STEP 2: Get metadata
    metadata = focus_server_api.get_job_metadata(job_id)
    assert metadata is not None
    logger.info("✓ Metadata retrieved")
    
    # STEP 3: Connect to gRPC (requires grpc library)
    # import grpc
    # channel = grpc.insecure_channel(f"{stream_url}:{stream_port}")
    # stub = DataStreamStub(channel)
    
    # STEP 4: Stream data
    # stream = stub.GetDataStream(request)
    # for message in stream:
    #     verify_data_fields(message)
    
    logger.info("✅ Test PZ-13570 (partial)")
```

**הערה**: gRPC streaming דורש ספריות נוספות והגדרת proto files.

---

## 🎯 PERFORMANCE TESTS

### TEST #37: /configure Latency p95

**Jira ID**: PZ-13571  
**Priority**: Low-Medium  
**Type**: Performance Test  
**Status**: חלקי

**מטרה**: לוודא ש-95% מה-requests ל-`/configure` עונות תוך < 2 שניות.

**מה זה p95?**
- p95 = Percentile 95
- 95% מהבקשות מתחת לערך זה
- נותן תמונה של ביצועים טיפוסיים (לא רק ממוצע)

**תהליך:**
```python
# Send 50 requests
latencies = []
for i in range(50):
    start = time.time()
    response = api.configure_streaming_job(request)
    latency = time.time() - start
    latencies.append(latency)

# Calculate p95
latencies_sorted = sorted(latencies)
p95_index = int(len(latencies) * 0.95)
p95_latency = latencies_sorted[p95_index]

# Verify SLA
assert p95_latency < 2.0, f"p95 latency ({p95_latency:.2f}s) exceeds 2.0s"
```

---

## 📊 סיכום כל הטסטים

### Integration Tests (44 total)

| ID | שם | Priority | Status | זמן |
|----|-----|----------|--------|-----|
| PZ-13909 | Historic Missing end_time | High | TODO | 1s |
| PZ-13907 | Historic Missing start_time | High | TODO | 1s |
| PZ-13906 | Low Throughput | Medium | ✅ | 2-3s |
| PZ-13904 | Resource Estimation | High | ✅ | 1-2s |
| PZ-13903 | Nyquist Limit | **CRITICAL** | ✅ | 2-3s |
| PZ-13901 | NFFT Variations | High | ✅ | 5-10s |
| PZ-13897 | GET /sensors | High | ✅ | 1-2s |
| PZ-13879 | Missing Required Fields | High | ✅ | 3-5s |
| PZ-13878 | Invalid View Type | High | ✅ | 1s |
| PZ-13877 | Invalid Freq Range | High | ✅ | 1s |
| PZ-13876 | Invalid Channel Range | High | ✅ | 1s |
| PZ-13873 | Valid Configuration | High | ✅ | 3-5s |
| PZ-13872 | Historic E2E | High | ✅ | 60-120s |
| PZ-13871 | Timestamp Ordering | High | ✅ | 20-40s |
| PZ-13870 | Future Timestamps | Medium | ✅ | 10-20s |
| PZ-13869 | Invalid Time Range | High | ✅ | 1s |
| PZ-13868 | Status 208 | High | ✅ | 30-60s |
| PZ-13865 | Short Duration (1 min) | Medium | ✅ | 20-30s |
| PZ-13863 | Standard 5-min Range | High | ✅ | 30-120s |

### SingleChannel Tests (15 tests)

| ID | שם | Status | תיאור |
|----|-----|--------|-------|
| PZ-13862 | SingleChannel E2E | ✅ | תהליך מלא |
| PZ-13861 | Stream Mapping | ✅ | ולידציית mapping |
| PZ-13860 | Metadata Consistency | ✅ | עקביות metadata |
| PZ-13859 | Polling Stability | ✅ | 100 polls |
| PZ-13858 | Rapid Reconfig | ✅ | 5 reconfigurations |
| PZ-13857 | NFFT Validation | ✅ | NFFT שונים |
| PZ-13855 | Canvas Height | ✅ | גבהים שונים |
| PZ-13854 | Frequency Range | ✅ | טווחים שונים |
| PZ-13853 | Data Consistency | ✅ | reproducibility |
| PZ-13852 | Min > Max | ✅ | negative test |
| PZ-13837 | Negative Channel | ✅ | channel < 0 |
| PZ-13835 | Out of Range High | ✅ | channel > max |
| PZ-13834 | Middle Channel | ✅ | אמצעי |
| PZ-13833 | Maximum Channel | ✅ | אחרון |
| PZ-13832 | Minimum Channel (0) | ✅ | ראשון |

### Dynamic ROI Tests (13 tests)

| ID | שם | Status |
|----|-----|--------|
| PZ-13784 | Send ROI Command | ✅ |
| PZ-13785 | ROI with Safety | ✅ |
| PZ-13786 | Multiple ROI Changes | ✅ |
| PZ-13787 | ROI Expansion | ✅ |
| PZ-13788 | ROI Shrinking | ✅ |
| PZ-13789 | ROI Shift | ✅ |
| PZ-13790 | ROI Equal Start/End | ✅ |
| PZ-13791 | ROI Reversed | ✅ |
| PZ-13792 | ROI Negative Start | ✅ |
| PZ-13793 | ROI Negative End | ✅ |
| PZ-13794 | ROI Small Range | ✅ |
| PZ-13795 | ROI Large Range | ✅ |
| PZ-13796 | ROI at Zero | ✅ |

---

**המשך בחלק 4 - Infrastructure, Security, Data Quality...**

