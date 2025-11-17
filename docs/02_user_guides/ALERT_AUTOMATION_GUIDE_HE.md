# 🚨 מדריך אוטומציה לשליחת Alerts למערכת Panda

**תאריך:** 13 בנובמבר 2025  
**מטרה:** הסבר מפורט על תהליך אוטומציה של שליחת alerts למערכת Panda

---

## 📋 תוכן עניינים

1. [סקירה כללית](#סקירה-כללית)
2. [ארכיטקטורה של המערכת](#ארכיטקטורה-של-המערכת)
3. [תהליך שליחת Alert - שלב אחר שלב](#תהליך-שליחת-alert)
4. [API Endpoint - פרטים טכניים](#api-endpoint)
5. [פורמט ה-Alert Payload](#פורמט-ה-alert-payload)
6. [דוגמאות קוד](#דוגמאות-קוד)
7. [אימות ו-Validation](#אימות-ו-validation)
8. [טיפים ופתרון בעיות](#טיפים-ופתרון-בעיות)

---

## 🎯 סקירה כללית

### מה זה Alert?
Alert הוא התרעה שמגיעה למערכת Panda ומציגה אירוע שזוהה על הסיב (fiber). ה-Alert מכיל:
- **Alert ID** - מזהה ייחודי
- **Class ID** - סוג האירוע (103 = SC, 104 = SD)
- **Severity** - חומרה (1, 2, או 3)
- **DOF (Distance of Fiber)** - מרחק על הסיב במטרים
- **Alerts Amount** - כמות alerts

### למה צריך אוטומציה?
- ✅ בדיקות אוטומטיות של תכונות alerts
- ✅ בדיקת קבוצות alerts (alert grouping)
- ✅ בדיקת סינון alerts
- ✅ בדיקת תצוגת alerts במפה
- ✅ בדיקת תחקירים מ-alerts

---

## 🏗️ ארכיטקטורה של המערכת

### תזרים הנתונים:

```
┌─────────────────┐
│  Automation     │
│  Script/Test    │
└────────┬────────┘
         │
         │ POST /prisma-210-1000/api/push-to-rabbit
         │ (with authentication)
         ▼
┌─────────────────┐
│  Prisma Web     │
│  App API        │
│  (Backend)      │
└────────┬────────┘
         │
         │ Publish to RabbitMQ Exchange
         ▼
┌─────────────────┐
│  RabbitMQ       │
│  Exchange:      │
│  "prisma"       │
└────────┬────────┘
         │
         │ Message Queue
         ▼
┌─────────────────┐
│  Panda App      │
│  (Frontend)     │
│  - Map View     │
│  - Journal      │
│  - Alerts       │
└─────────────────┘
```

### רכיבי המערכת:

1. **Prisma Web App API** (`https://10.10.10.100/prisma/api/`)
   - מטפל ב-authentication
   - מקבל את ה-alert דרך endpoint
   - מפרסם ל-RabbitMQ

2. **RabbitMQ** (`10.10.10.100:5672`)
   - Exchange: `prisma` (יחיד במערכת!)
   - Queue: דינמי לפי site ID
   - מעביר את ה-alert ל-Panda App

3. **Panda App** (Desktop Application)
   - מקבל alerts דרך RabbitMQ
   - מציג במפה (Map View)
   - מציג ב-Journal
   - מאפשר תחקירים

---

## 🔄 תהליך שליחת Alert - שלב אחר שלב

### שלב 1: Authentication

**Endpoint:** `POST /prisma/api/auth/login`

**Request:**
```json
{
  "username": "prisma",
  "password": "prisma"
}
```

**Response:**
- Status: `201 Created`
- Cookies:
  - `access-token` - JWT token
  - `refresh-token` - Refresh token

**קוד Python:**
```python
import requests

def login_session(base_url: str, username: str, password: str):
    session = requests.Session()
    session.verify = False  # SSL verification disabled
    
    resp = session.post(
        f"{base_url}/auth/login",
        json={"username": username, "password": password},
        timeout=15
    )
    resp.raise_for_status()
    return session
```

---

### שלב 2: יצירת Alert Object

**מבנה Alert:**
```python
@dataclass
class Alert:
    alert_id: str              # מזהה ייחודי, למשל: "test-123.4567"
    classId: int               # 103 = SC, 104 = SD
    severity: int              # 1, 2, או 3
    dof_m: int                 # מרחק על הסיב במטרים (200-8700)
    alerts_amount: int         # כמות alerts (בדרך כלל 1)
    coordinates: Optional[str]  # קואורדינטות (אופציונלי)
    sensor: Optional[int]       # מספר סנסור (אופציונלי)
    report_line: Optional[int]  # קו דיווח (אופציונלי)
    start_dt: Optional[datetime] # זמן התחלה (אופציונלי)
    end_dt: Optional[datetime]  # זמן סיום (אופציונלי)
```

**דוגמה ליצירת Alert:**
```python
from datetime import datetime
from blocksAndRepo.panda.entities.Alert import Alert

# יצירת alert מסוג SD (104) עם חומרה 3
alert = Alert(
    alert_id="test-123.4567",
    classId=104,        # SD
    severity=3,         # חומרה גבוהה
    dof_m=4163,        # 4163 מטר על הסיב
    alerts_amount=1
)
```

---

### שלב 3: שליחת Alert דרך API

**Endpoint:** `POST /prisma-210-1000/api/push-to-rabbit`

**Base URL:** `https://10.10.10.100/prisma/api/`  
**Full URL:** `https://10.10.10.100/prisma/api/prisma-210-1000/api/push-to-rabbit`

**Headers:**
- `Content-Type: application/json`
- `Cookie: access-token=...` (מהשלב הקודם)

**Payload:**
```json
{
  "alertsAmount": 1,
  "dofM": 4163,
  "classId": 104,
  "severity": 3,
  "alertIds": ["test-123.4567"]
}
```

**קוד Python:**
```python
def push_alert(session: requests.Session, base_url: str, alert: Alert):
    """
    שולח alert למערכת דרך API
    """
    payload = {
        "alertsAmount": alert.alerts_amount,
        "dofM": alert.dof_m,
        "classId": alert.classId,
        "severity": alert.severity,
        "alertIds": [alert.alert_id]
    }
    
    # ה-URL המלא: base_url + "prisma-210-1000/api/push-to-rabbit"
    resp = session.post(
        f"{base_url}prisma-210-1000/api/push-to-rabbit",
        json=payload,
        timeout=15
    )
    resp.raise_for_status()
    
    # מחזיר JSON response אם אפשרי
    ctype = resp.headers.get("content-type", "").lower()
    return resp.json() if "application/json" in ctype else resp.text
```

---

### שלב 4: עיבוד ב-RabbitMQ

**Exchange:** `prisma` (יחיד במערכת!)

**Routing Key:** דינמי לפי site ID (`prisma-210-1000`)

**Queue:** נוצר אוטומטית על ידי Panda App

**הערה:** אין צורך ליצור queue ידנית - Panda App יוצר אותו אוטומטית

---

### שלב 5: קבלה ב-Panda App

1. **Panda App מקבל את ה-alert** דרך RabbitMQ
2. **מציג במפה** - balloon על המפה במיקום המתאים
3. **מציג ב-Journal** - שורה בטבלת alerts
4. **מאפשר תחקיר** - לחיצה על ה-alert פותחת תחקיר

---

## 📡 API Endpoint - פרטים טכניים

### Base URL
```
https://10.10.10.100/prisma/api/
```

### Site ID
```
prisma-210-1000
```

### Full Endpoint Path
```
POST /prisma-210-1000/api/push-to-rabbit
```

### Authentication
- **Method:** Cookie-based (JWT token)
- **Cookie Name:** `access-token`
- **Login Endpoint:** `POST /auth/login`

### SSL Verification
- **Production:** `verify_ssl=False` (self-signed certificate)
- **Development:** `verify_ssl=False`

### Timeout
- **Default:** 15 seconds
- **Recommended:** 15-30 seconds

---

## 📦 פורמט ה-Alert Payload

### שדות חובה:

| שדה | סוג | תיאור | דוגמה |
|-----|-----|-------|-------|
| `alertsAmount` | `int` | כמות alerts | `1` |
| `dofM` | `int` | מרחק על הסיב במטרים | `4163` |
| `classId` | `int` | סוג alert: 103=SC, 104=SD | `104` |
| `severity` | `int` | חומרה: 1, 2, או 3 | `3` |
| `alertIds` | `array[str]` | רשימת מזההי alerts | `["test-123.4567"]` |

### שדות אופציונליים (לא בשימוש כרגע):

| שדה | סוג | תיאור |
|-----|-----|-------|
| `externalRabbitIp` | `string` | IP של RabbitMQ חיצוני |

### דוגמאות Payload:

**Alert מסוג SD (104) עם חומרה 3:**
```json
{
  "alertsAmount": 1,
  "dofM": 4163,
  "classId": 104,
  "severity": 3,
  "alertIds": ["test-123.4567"]
}
```

**Alert מסוג SC (103) עם חומרה 2:**
```json
{
  "alertsAmount": 1,
  "dofM": 5682,
  "classId": 103,
  "severity": 2,
  "alertIds": ["test-456.7890"]
}
```

**Multiple Alerts:**
```json
{
  "alertsAmount": 3,
  "dofM": 5000,
  "classId": 104,
  "severity": 1,
  "alertIds": ["test-111.2222", "test-333.4444", "test-555.6666"]
}
```

---

## 💻 דוגמאות קוד

### דוגמה 1: שליחת Alert בודד

```python
import requests
from blocksAndRepo.panda.entities.Alert import Alert
from tests.panda.testHelpers.ApiHelper import login_session, push_alert

# הגדרות
BASE_URL = "https://10.10.10.100/prisma/api/"
USERNAME = "prisma"
PASSWORD = "prisma"
SITE_ID = "prisma-210-1000"

# 1. התחברות
session = login_session(BASE_URL, USERNAME, PASSWORD, verify_ssl=False)

# 2. יצירת Alert
alert = Alert(
    alert_id="test-123.4567",
    classId=104,        # SD
    severity=3,         # חומרה גבוהה
    dof_m=4163,        # 4163 מטר
    alerts_amount=1
)

# 3. שליחת Alert
result = push_alert(session, BASE_URL, {
    "alertsAmount": alert.alerts_amount,
    "dofM": alert.dof_m,
    "classId": alert.classId,
    "severity": alert.severity,
    "alertIds": [alert.alert_id]
})

print(f"Alert sent successfully: {result}")
```

---

### דוגמה 2: שליחת מספר Alerts

```python
import random
from datetime import datetime
from time import sleep
from blocksAndRepo.panda.entities.Alert import Alert
from tests.panda.testHelpers.ApiHelper import login_session, push_alert
from tests.panda.testHelpers.TestHelper import gen_alert_id_no_all_zeros

def push_multiple_random_alerts(num_alerts: int, base_url: str, username: str, password: str):
    """
    שולח מספר alerts אקראיים למערכת
    """
    session = login_session(base_url, username, password, verify_ssl=False)
    alerts = []
    
    for i in range(num_alerts):
        # יצירת alert ID ייחודי
        alert_id = gen_alert_id_no_all_zeros()
        
        # פרמטרים אקראיים
        dof_m = random.randint(200, 8700)
        alert_type = random.choice([103, 104])  # SC או SD
        severity = random.choice([1, 2, 3])
        
        # יצירת Alert
        alert = Alert(
            alert_id=alert_id,
            dof_m=dof_m,
            classId=alert_type,
            severity=severity,
            alerts_amount=1
        )
        
        # שליחת Alert
        push_alert(session, base_url, {
            "alertsAmount": alert.alerts_amount,
            "dofM": alert.dof_m,
            "classId": alert.classId,
            "severity": alert.severity,
            "alertIds": [alert.alert_id]
        })
        
        alerts.append(alert)
        sleep(2)  # המתנה בין alerts
    
    return alerts

# שימוש
alerts = push_multiple_random_alerts(
    num_alerts=5,
    base_url="https://10.10.10.100/prisma/api/",
    username="prisma",
    password="prisma"
)
```

---

### דוגמה 3: שימוש ב-AlertsBlocks (מהקוד הקיים)

```python
from blocksAndRepo.panda.alerts.AlertsBlocks import AlertsBlocks
from blocksAndRepo.panda.entities.Alert import Alert
from common.appium.AppiumTools import AppiumTools
from tests.panda.testHelpers.TestHelper import gen_alert_id_no_all_zeros

# יצירת AlertsBlocks (דורש AppiumTools)
app_tools = AppiumTools(...)  # הגדרה של AppiumTools
alerts_bb = AlertsBlocks(app_tools)

# יצירת Alert
alert_id = gen_alert_id_no_all_zeros()
alert = Alert(
    alert_id=alert_id,
    dof_m=4163,
    classId=104,
    severity=3,
    alerts_amount=1
)

# שליחת Alert דרך AlertsBlocks
alerts_bb.push_alert(
    alert=alert,
    base_url="https://10.10.10.100/prisma/api/",
    api_username="prisma",
    api_password="prisma"
)
```

---

### דוגמה 4: בדיקת Alert Grouping

```python
import pytest
from datetime import datetime
from blocksAndRepo.panda.entities.Alert import Alert
from tests.panda.testHelpers.TestHelper import gen_alert_id_no_all_zeros

@pytest.mark.alert_grouping
def test_alerts_sd_grouping(settings, alerts_bb, alerts_grouping_bb):
    """
    בדיקה ששליחת מספר alerts קרובים יוצרת קבוצה
    """
    # הגדרות קבוצה
    time_range = 16  # דקות
    sensor_allowed_diff = 2
    alert_type = "SD"
    
    # הפעלת alert grouping
    alerts_grouping_bb.edit_and_enable_alerts_grouping(
        alert_type, 
        time_range, 
        "דקות", 
        sensor_allowed_diff
    )
    
    all_alerts = []
    
    # Alert 1
    alert_id = gen_alert_id_no_all_zeros()
    alert = Alert(alert_id=alert_id, alerts_amount=1, dof_m=4163, classId=104, severity=3)
    alerts_bb.push_alert(alert, settings.apiBaseUrl, settings.pandaLoginUser, settings.pandaLoginPassword)
    all_alerts.append(alert)
    
    # Alert 2 (קרוב ל-Alert 1)
    alert_id = gen_alert_id_no_all_zeros()
    alert = Alert(alert_id=alert_id, alerts_amount=1, dof_m=4162, classId=104, severity=2)
    alerts_bb.push_alert(alert, settings.apiBaseUrl, settings.pandaLoginUser, settings.pandaLoginPassword)
    all_alerts.append(alert)
    
    # Alert 3 (רחוק יותר)
    alert_id = gen_alert_id_no_all_zeros()
    alert = Alert(alert_id=alert_id, alerts_amount=1, dof_m=4150, classId=104, severity=2)
    alerts_bb.push_alert(alert, settings.apiBaseUrl, settings.pandaLoginUser, settings.pandaLoginPassword)
    all_alerts.append(alert)
    
    # אימות שהקבוצה נוצרה נכון
    alerts_grouping_bb.verify_grouping(
        all_alerts=all_alerts,
        expected_alert_type=alert_type,
        expected_number_of_alerts=2,  # רק 2 alerts קרובים
        time_range_in_minutes_or_hours="דקות",
        sensor_allowed_diff=sensor_allowed_diff
    )
    
    # כיבוי alert grouping
    alerts_grouping_bb.diable_alerts_grouping(alert_type)
```

---

## ✅ אימות ו-Validation

### 1. אימות Alert במפה (Map View)

```python
def verify_alert_on_map(alerts_bb, alert: Alert, expected_dt: datetime):
    """
    אימות שה-alert מופיע במפה עם הפרטים הנכונים
    """
    alerts_bb.navigate_tab("map")
    
    # אימות פרטי Alert ב-sidebar
    alerts_bb.verify_alert_details_on_side_bar(
        alert=alert,
        expected_dt=expected_dt,
        wait_for_end_time=False
    )
```

### 2. אימות Alert ב-Journal

```python
def verify_alert_in_journal(alerts_bb, alert: Alert):
    """
    אימות שה-alert מופיע ב-Journal
    """
    alerts_bb.navigate_tab("journal")
    
    # חיפוש alert לפי ID
    alert_element = [AppiumBy.XPATH, f"//p[contains(.,'{alert.alert_id}')]"]
    alerts_bb.app_tools.click_web(alert_element)
    
    # אימות שהפרטים נכונים
    # ...
```

### 3. אימות Alert Bell (התראה)

```python
def verify_alert_bell_notification(alerts_bb):
    """
    אימות שהופיעה התראה (red dot) על ה-bell
    """
    alerts_bb.verify_alert_bell_red_dot()
```

---

## 🔧 טיפים ופתרון בעיות

### טיפים:

1. **יצירת Alert ID ייחודי:**
   ```python
   from tests.panda.testHelpers.TestHelper import gen_alert_id_no_all_zeros
   alert_id = gen_alert_id_no_all_zeros()
   ```

2. **המתנה בין alerts:**
   ```python
   from time import sleep
   sleep(2)  # המתנה של 2 שניות בין alerts
   ```

3. **רענון תצוגה:**
   ```python
   # לאחר שליחת alert, לעבור בין טאבים לרענון
   alerts_bb.navigate_tab("journal")
   alerts_bb.navigate_tab("map")
   ```

4. **זמן סיום Alert:**
   - Alert נסגר אוטומטית לאחר **170 שניות** (2.83 דקות)
   - ניתן להגדיר ב-`project.properties`: `alertEndTimeAfterPush=170`

### בעיות נפוצות:

#### 1. Alert לא מופיע במפה

**סיבות אפשריות:**
- Alert ID לא ייחודי
- לא חיכינו מספיק זמן
- Panda App לא מחובר ל-RabbitMQ

**פתרון:**
```python
# המתנה לפני אימות
from time import sleep
sleep(5)  # המתנה של 5 שניות

# רענון תצוגה
alerts_bb.navigate_tab("journal")
alerts_bb.navigate_tab("map")
```

#### 2. שגיאת Authentication

**סיבות אפשריות:**
- Username/Password שגויים
- Token פג תוקף

**פתרון:**
```python
# יצירת session חדש
session = login_session(base_url, username, password, verify_ssl=False)
```

#### 3. שגיאת Connection

**סיבות אפשריות:**
- שרת לא זמין
- VPN לא מחובר
- Firewall חוסם

**פתרון:**
```python
# בדיקת חיבור
import requests
try:
    resp = requests.get("https://10.10.10.100/prisma/api/login-configuration", verify=False, timeout=5)
    print(f"Connection OK: {resp.status_code}")
except Exception as e:
    print(f"Connection failed: {e}")
```

#### 4. Alert לא נסגר אחרי 170 שניות

**סיבות אפשריות:**
- בעיה ב-RabbitMQ
- בעיה ב-Panda App

**פתרון:**
```python
# המתנה מפורשת לזמן סיום
alerts_bb.wait_for_end_time(alert_id_last_part)
```

---

## 📚 קבצים רלוונטיים בקוד

### Frontend Tests (`fe_panda_tests/`):

- **`blocksAndRepo/panda/alerts/AlertsBlocks.py`** - Blocks לשליחת alerts
- **`blocksAndRepo/panda/entities/Alert.py`** - מבנה Alert
- **`tests/panda/testHelpers/ApiHelper.py`** - Helper functions ל-API
- **`tests/panda/sanity/alerts/TestAlertsGrouping.py`** - בדיקות alert grouping
- **`config/project.properties`** - הגדרות API ו-RabbitMQ

### Backend Tests (`be_focus_server_tests/`):

- **`infrastructure/test_rabbitmq_connectivity.py`** - בדיקות RabbitMQ
- **`infrastructure/test_rabbitmq_outage_handling.py`** - בדיקות outage

---

## 🎓 סיכום

### תהליך מלא:

1. ✅ **Authentication** → קבלת `access-token`
2. ✅ **יצירת Alert Object** → עם כל הפרטים הנדרשים
3. ✅ **שליחת Alert** → דרך `POST /prisma-210-1000/api/push-to-rabbit`
4. ✅ **עיבוד ב-RabbitMQ** → Exchange `prisma`
5. ✅ **קבלה ב-Panda App** → תצוגה במפה וב-Journal
6. ✅ **אימות** → בדיקה שהכל עובד נכון

### נקודות חשובות:

- 🔐 **Authentication חובה** - צריך `access-token` cookie
- 🆔 **Alert ID ייחודי** - להשתמש ב-`gen_alert_id_no_all_zeros()`
- ⏱️ **זמן המתנה** - להמתין בין alerts ולאחר שליחה
- 🔄 **רענון תצוגה** - לעבור בין טאבים לרענון
- 📍 **Site ID** - `prisma-210-1000` (מוגדר ב-config)

---

**תאריך עדכון:** 13 בנובמבר 2025  
**גרסה:** 1.0.0

