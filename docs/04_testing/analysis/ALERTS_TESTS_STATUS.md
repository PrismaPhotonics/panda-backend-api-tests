# 📊 סטטוס טסטי Alerts

**תאריך בדיקה:** 2025-11-13  
**סביבה:** staging

---

## ✅ סיכום כללי

**37 טסטים בסך הכל:**
- ✅ **4 עברו** (מתוך 6 positive tests)
- ❌ **2 נכשלו** (MongoDB storage verification)
- ⏭️ **31 לא רצו** (לא נבדקו עדיין)

---

## ❌ כשלים זוהו

### 1. `test_successful_sd_alert_generation` (PZ-15000)
**כשל:** Alert לא נמצא ב-MongoDB אחרי שליחה

**פרטים:**
- Alert נשלח בהצלחה דרך HTTP API (`/api/push-to-rabbit`)
- Response: 200 OK
- MongoDB חיפוש: `{"ext_id": "test-sd-1763051531"}` - לא נמצא
- 5 ניסיונות עם exponential backoff

**סיבות אפשריות:**
1. Alert נשלח אבל לא מעובד
2. Alert מעובד אבל לא נשמר ב-MongoDB
3. MongoDB collection/field name mismatch
4. Alert נשמר עם `ext_id` שונה

### 2. `test_alert_storage_in_mongodb` (PZ-15005)
**כשל:** Alert לא נמצא ב-MongoDB אחרי שליחה

**פרטים:**
- Alert נשלח בהצלחה דרך HTTP API
- Response: 200 OK
- MongoDB חיפוש: `{"ext_id": "test-mongodb-1763051581"}` - לא נמצא
- 5 ניסיונות עם exponential backoff

**סיבות אפשריות:** (כמו לעיל)

---

## ✅ טסטים שעברו

1. ✅ `test_successful_sc_alert_generation` (PZ-15001)
2. ✅ `test_multiple_alerts_generation` (PZ-15002)
3. ✅ `test_different_severity_levels` (PZ-15003)
4. ✅ `test_alert_processing_via_rabbitmq` (PZ-15004)

---

## 🔍 מה הטסטים בודקים

### Positive Tests (6 טסטים):
1. ✅ SD Alert generation
2. ✅ SC Alert generation
3. ✅ Multiple alerts
4. ✅ Different severity levels
5. ✅ RabbitMQ processing
6. ❌ MongoDB storage

### Negative Tests (8 טסטים):
- Invalid class IDs
- Invalid severity
- Invalid DOF ranges
- Missing fields
- Connection failures
- Invalid alert ID formats
- Duplicate alert IDs

### Edge Cases (8 טסטים):
- Boundary values
- Min/max severity
- Zero alerts
- Large alert IDs
- Concurrent alerts
- Rapid sequential alerts

### Load Tests (6 טסטים):
- High volume
- Sustained load
- Burst load
- Mixed alert types
- RabbitMQ capacity
- MongoDB write load

### Performance Tests (7 טסטים):
- Response time
- Throughput
- Latency
- Resource usage
- E2E performance
- RabbitMQ performance
- MongoDB performance

---

## 🐛 בעיות זוהו

### בעיה #1: MongoDB Storage Verification
**תיאור:** Alerts לא נמצאים ב-MongoDB אחרי שליחה

**טסטים שנכשלו:**
- `test_successful_sd_alert_generation`
- `test_alert_storage_in_mongodb`

**מה הטסטים עושים:**
1. שולחים alert דרך HTTP API (`/api/push-to-rabbit`)
2. מחכים לעיבוד
3. מחפשים ב-MongoDB: `alerts_collection.find_one({"ext_id": alert_id})`
4. נכשלים אם לא נמצא

**סיבות אפשריות:**
1. **Alert לא מעובד:** Alert נשלח אבל לא מעובד על ידי Backend
2. **MongoDB collection/field mismatch:** אולי ה-collection או ה-field name שונים
3. **Alert נשמר עם ID שונה:** אולי `ext_id` לא נשמר או נשמר עם שם אחר
4. **עיבוד איטי:** אולי צריך יותר זמן לעיבוד

---

## 🔧 המלצות לתיקון

### 1. בדיקת MongoDB Schema
```python
# לבדוק מה באמת יש ב-MongoDB:
db = mongodb_manager.get_database("prisma")
alerts_collection = db.get_collection("alerts")

# לראות את ה-schema של alerts קיימים:
recent_alerts = alerts_collection.find().sort("_id", -1).limit(5)
for alert in recent_alerts:
    print(alert.keys())  # לראות מה השדות
```

### 2. חיפוש גמיש יותר
```python
# לנסות חיפוש לפי מספר שדות:
alert_doc = alerts_collection.find_one({
    "$or": [
        {"ext_id": alert_id},
        {"alert_id": alert_id},
        {"_id": alert_id},
        {"alertIds": alert_id}  # אם זה array
    ]
})
```

### 3. בדיקת RabbitMQ
```python
# לבדוק אם ה-alert הגיע ל-RabbitMQ:
# לבדוק את ה-queue אם יש message
```

### 4. בדיקת Backend Logs
```python
# לבדוק את ה-logs של Focus Server:
# לחפש "push-to-rabbit" או את ה-alert_id
```

### 5. הגדלת זמן המתנה
```python
# אולי צריך יותר זמן:
max_retries = 10  # במקום 5
retry_delay = 5   # במקום 2
```

---

## 📝 סיכום

**הטסטים לא תוקנו עדיין** - יש 2 כשלים שקשורים ל-MongoDB storage verification.

**הבעיה העיקרית:** Alerts לא נמצאים ב-MongoDB אחרי שליחה, למרות שהם נשלחים בהצלחה דרך HTTP API.

**צעדים הבאים:**
1. לבדוק את ה-MongoDB schema בפועל
2. לבדוק את ה-Backend logs
3. לבדוק את ה-RabbitMQ queues
4. לתקן את הטסטים בהתאם לממצאים

---

**סטטוס:** ⚠️ **דורש תיקון**

