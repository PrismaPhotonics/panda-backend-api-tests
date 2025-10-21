# 📋 Critical Tests Missing in Xray - NO WATERFALL
## רק טסטים שלא קשורים ל-waterfall

**תאריך:** 2025-10-21  
**סה"כ טסטים:** 11 (לא 14!)  

---

## 🔴 CRITICAL - 6 טסטים קריטיים

### 1️⃣ test_get_sensors_list

**📍 מיקום:** `tests/integration/api/test_live_monitoring_flow.py:129`

**🎯 מטרה:**
קורא endpoint `GET /sensors` שמחזיר רשימה של כל הסנסורים הזמינים.

**💡 למה חשוב:**
- זה ה**endpoint הראשון** שכל לקוח קורא
- בלי רשימת sensors, לא יודעים אילו channels חוקיים
- אם זה לא עובד, לא יכולים לקבוע ROI

**🔗 קשר לאוטומציה:**
- אתה משתמש ב-`focus_server_api.get_sensors()` בטסטים
- זה prerequisite לכל sensor range validation
- בלי זה לא יודעים אם `channels: {min: 0, max: 50}` חוקי

**📊 מה נבדק:**
- Endpoint מחזיר HTTP 200
- רשימה לא ריקה
- סנסורים רציפים (0, 1, 2, 3...)
- אין gaps

---

### 2️⃣ test_mongodb_connection

**📍 מיקום:** `tests/integration/infrastructure/test_external_connectivity.py:68`

**🎯 מטרה:**
בודק חיבור ישיר ל-MongoDB (`10.10.100.108:27017`) ואימות שה-database נגיש.

**💡 למה חשוב:**
- MongoDB הוא **ה-backbone** של כל המערכת
- בלי MongoDB: אין recordings, אין metadata, אין task tracking
- כשיש בעיה, צריך לדעת אם זה Focus Server או MongoDB

**🔗 קשר לאוטומציה:**
- כל הטסטים **תלויים** ב-MongoDB
- כש-test נכשל, צריך לדעת אם זה בגלל MongoDB down
- זה **diagnostic test** ראשון

**📊 מה נבדק:**
- חיבור TCP ל-MongoDB
- Authentication (prisma/prisma)
- Database `prisma` קיים
- Collections קיימות (`recordings`, `tasks`)
- Ping response < 100ms

---

### 3️⃣ test_kubernetes_connection

**📍 מיקום:** `tests/integration/infrastructure/test_external_connectivity.py:172`

**🎯 מטרה:**
בודק חיבור ל-Kubernetes cluster ואימות ש-Focus Server pod פועל.

**💡 למה חשוב:**
- Focus Server רץ **על Kubernetes** (namespace: panda)
- אם K8s לא נגיש, לא יכולים:
  - לראות pod status
  - לעשות restart
  - לקרוא logs
  - לעשות scale

**🔗 קשר לאוטומציה:**
- כשיש performance issues, צריך לבדוק pods (CPU, Memory)
- כשיש crashes, צריך לראות pod restarts
- זה **health check** למערכת הניהול

**📊 מה נבדק:**
- Kubernetes API נגיש (`10.10.100.102:6443`)
- Namespace `panda` קיים
- Focus Server pod running
- Services זמינים (ClusterIP, LoadBalancer)

---

### 4️⃣ test_nfft_variations

**📍 מיקום:** `tests/integration/api/test_spectrogram_pipeline.py:80`

**🎯 מטרה:**
בודק שהמערכת תומכת ב**כל ערכי NFFT חוקיים** (128, 256, 512, 1024, 2048, 4096).

**💡 למה חשוב:**
- NFFT קובע **resolution של frequency analysis**
- משתמשים שונים צריכים NFFT שונה:
  - NFFT גבוה (4096) = resolution טובה, אבל איטי
  - NFFT נמוך (256) = מהיר, אבל resolution גרועה
- צריך לוודא ש**כל הערכים עובדים**

**🔗 קשר לאוטומציה:**
- הטסטים שלך **תמיד** משתמשים ב-NFFT=1024
- **לעולם לא בדקת** אם 2048 או 512 עובדים
- יכול להיות ש-NFFT=4096 קורס או איטי מדי!

**📊 מה נבדק:**
- ערכים: 128, 256, 512, 1024, 2048, 4096
- כל ערך מתקבל ללא error
- Configuration מצליח
- אין crashes

---

### 5️⃣ test_frequency_range_within_nyquist

**📍 מיקום:** `tests/integration/api/test_spectrogram_pipeline.py:127`

**🎯 מטרה:**
בודק שהמערכת **אוכפת את חוק Nyquist** - לא מאפשרת תדרים גבוהים מ-PRR/2.

**💡 למה חשוב:**
- **זה הכי קריטי מבחינה פיזיקלית!**
- חוק Nyquist: `max_frequency ≤ PRR/2`
- אם עוברים את הגבול → **aliasing** = נתונים שגויים לחלוטין!
- זה לא bug תוכנה - זה **חוק פיזיקלי**

**🔗 קשר לאוטומציה:**
- כל הטסטים שלך עם `freq_max: 500`
- אבל **לא בדקת** מה קורה אם PRR=800 (Nyquist=400)
- האם המערכת **דוחה** freq_max=500? או מקבלת ונותנת נתונים שגויים?

**📊 מה נבדק:**
1. קורא PRR מה-live_metadata
2. מחשב Nyquist = PRR / 2
3. Config עם freq < Nyquist ✅ (צריך לעבור)
4. Config עם freq > Nyquist ❌ (צריך להידחות!)

**⚠️ זה המסוכן ביותר!** אם לא בודקים Nyquist, אפשר לקבל **data corruption**.

---

### 6️⃣ test_ssh_connection

**📍 מיקום:** `tests/integration/infrastructure/test_external_connectivity.py:304`

**🎯 מטרה:**
בודק SSH access לservers (`10.10.100.3` → `10.10.100.113`) לצורך maintenance.

**💡 למה חשוב:**
- SSH צריך ל-troubleshooting
- SSH צריך ל-log access
- SSH צריך ל-manual intervention
- אם SSH לא עובד, תקועים!

**🔗 קשר לאוטומציה:**
- כשיש בעיה, צריך SSH לבדוק logs
- כשצריך restart manual, צריך SSH
- זה **access verification**

**📊 מה נבדק:**
- Jump host accessible (`root@10.10.100.3`)
- Target host accessible (`prisma@10.10.100.113`)
- Commands executable
- Network operations work

---

## 🟡 HIGH - 5 טסטים גבוהים

### 7️⃣ test_config_with_missing_start_time

**📍 מיקום:** צריך ליצור! (חסר בקוד)

**🎯 מטרה:**
בודק מה קורה כש-**historic config חסר start_time**.

**💡 למה חשוב:**
- Historic mode **דורש** start_time + end_time
- אם חסר → צריך **400 error** ברור
- לא crash או undefined behavior

**🔗 קשר לאוטומציה:**
- כל ה-historic tests שלך **תמיד** שולחים start_time
- **לא בדקת** missing field scenario
- זה **validation gap**

**📊 מה צריך לבדוק:**
```json
{
  "channels": {"min": 0, "max": 50},
  "end_time": "251021120000"
  // Missing "start_time" ← should reject!
}
```

---

### 8️⃣ test_config_with_missing_end_time

**📍 מיקום:** צריך ליצור! (חסר בקוד)

**🎯 מטרה:**
בודק מה קורה כש-**historic config חסר end_time**.

**💡 למה חשוב:**
- Pair ל-test 7
- Validation של שדות חובה

**🔗 קשר לאוטומציה:**
- Validation gap נוסף
- צריך לבדוק **שני הכיוונים**

**📊 מה צריך לבדוק:**
```json
{
  "channels": {"min": 0, "max": 50},
  "start_time": "251021120000"
  // Missing "end_time" ← should reject!
}
```

---

### 9️⃣ test_configuration_resource_estimation

**📍 מיקום:** `tests/integration/api/test_spectrogram_pipeline.py:246`

**🎯 מטרה:**
**מעריך resource usage** (CPU, Memory, Bandwidth) על בסיס config.

**💡 למה חשוב:**
- לפני task creation, רוצים לדעת **כמה resources** זה ידרוש
- Configuration עם `nfft=4096, sensors=200` → **very expensive**
- Configuration עם `nfft=256, sensors=10` → **lightweight**
- זה **capacity planning**

**🔗 קשר לאוטומציה:**
- אתה משתמש ב-`validate_configuration_compatibility()` 
- זה מחשב:
  - Spectrogram rows/sec
  - Bytes per row  
  - Output data rate (Mbps)
- אבל לא תיעדת ב-Xray!

**📊 מה נבדק:**
1. מחשב estimates
2. מזהה configs יקרים מדי
3. נותן warnings
4. Estimates הגיוניים

---

### 🔟 test_high_throughput_configuration

**📍 מיקום:** `tests/integration/api/test_spectrogram_pipeline.py:270`

**🎯 מטרה:**
בודק config עם **throughput גבוה** (> 50 Mbps).

**💡 למה חשוב:**
- Configs מסוימים → **המון data**
- Many sensors × small NFFT = gigabits/second
- צריך לבדוק שהמערכת:
  - מזהה throughput גבוה
  - נותנת warning או דוחה

**🔗 קשר לאוטומציה:**
- הטסטים שלך עם configs "נורמליים"
- לא בדקת **extreme scenarios**
- זה **stress test** על pipeline

**📊 מה נבדק:**
```python
config = {
    "nfft": 512,  # Small = more rows/sec
    "channels": {"min": 0, "max": 200}  # Many sensors
}
# Output: > 50 Mbps
```

---

### 1️⃣1️⃣ test_low_throughput_configuration

**📍 מיקום:** `tests/integration/api/test_spectrogram_pipeline.py:304`

**🎯 מטרה:**
בודק config עם **throughput נמוך** (< 1 Mbps).

**💡 למה חשוב:**
- Low throughput זה OK, אבל **too low**?
- אם < 1 row/sec, זה בקושי real-time
- צריך לדעת אם זה valid או warning

**🔗 קשר לאוטומציה:**
- לא בדקת **extreme low** scenarios
- זה **edge case** validation

**📊 מה נבדק:**
```python
config = {
    "nfft": 4096,  # Large = fewer rows/sec
    "channels": {"min": 5, "max": 10}  # Few sensors
}
# Output: < 1 Mbps
```

---

## 🔵 ADDITIONAL - 5 טסטים נוספים חשובים

### 1️⃣2️⃣ test_roi_verification_after_change

**📍 מיקום:** צריך ליצור בקוד

**🎯 מטרה:**
מוודא שאחרי ROI change דרך RabbitMQ, ה-**configuration באמת השתנתה**.

**💡 למה חשוב:**
- שולחים ROI command דרך MQ
- צריך לוודא שזה **באמת עבד**
- לא רק שהcommand נשלח, אלא שה-baby analyzer **התאתחל מחדש** עם ROI חדש

**🔗 קשר לאוטומציה:**
- יש לך `test_roi_change_via_rabbitmq` ב-`test_dynamic_roi_adjustment.py`
- אבל האם **אימתת** שהשינוי בפועל קרה?
- צריך לבדוק את ה-**result**, לא רק שהcommand נשלח

**📊 מה צריך לבדוק:**
1. שלח ROI command: sensors 10-20
2. המתן לbaby analyzer restart
3. Query metadata → verify sensors = 10-20 ✅
4. או query config → verify ROI updated ✅

---

### 1️⃣3️⃣ test_roi_concurrent_changes

**📍 מיקום:** צריך ליצור בקוד

**🎯 מטרה:**
בודק מה קורה כש**שולחים 2 ROI commands ביחד** (race condition).

**💡 למה חשוב:**
- אם 2 users שולחים ROI changes **בו-זמנית**:
  - מי מנצח?
  - יש corruption?
  - יש undefined behavior?
- צריך **locking mechanism** או **queue**

**🔗 קשר לאוטומציה:**
- הטסטים שלך שולחים ROI אחד אחרי השני
- **לא בדקת** concurrent scenario
- זה **real production risk**

**📊 מה צריך לבדוק:**
1. שלח 2 ROI commands ביחד:
   - Command 1: sensors 0-30
   - Command 2: sensors 40-70
2. בדוק מה קרה:
   - אחד זוכה? ✅
   - שניהם נדחים? ✅
   - corruption? ❌
3. וודא consistency

---

### 1️⃣4️⃣ test_roi_rollback_on_error

**📍 מיקום:** צריך ליצור בקוד

**🎯 מטרה:**
בודק שאם ROI change **נכשל**, המערכת **חוזרת ל-ROI הקודם**.

**💡 למה חשוב:**
- אם ROI change נכשל באמצע (baby analyzer crash):
  - לא רוצים להישאר במצב **undefined**
  - צריך **rollback** ל-ROI הקודם
  - זה **data integrity**

**🔗 קשר לאוטומציה:**
- הטסטים שלך מניחים ROI change **תמיד מצליח**
- מה קורה כש**נכשל**?
- זה **error recovery** test

**📊 מה צריך לבדוק:**
1. ROI התחלתי: sensors 0-50
2. שלח ROI command לא חוקי: sensors 9999-10000
3. Command נכשל ✅
4. **וודא שחזרנו ל-0-50** (rollback) ✅
5. System stable

---

### 1️⃣5️⃣ test_config_with_start_equals_end

**📍 מיקום:** צריך ליצור בקוד

**🎯 מטרה:**
בודק historic config עם **start_time == end_time** (zero duration).

**💡 למה חשוב:**
- Edge case: מה קורה עם time range של 0 שניות?
- האם זה:
  - Valid (snapshot)?
  - Invalid (צריך duration)?
  - Warning?
- צריך **specification** ברורה

**🔗 קשר לאוטומציה:**
- הטסטים שלך עם durations נורמליים (1 min, 5 min)
- לא בדקת **zero duration**
- זה **edge case** שצריך להגדיר

**📊 מה צריך לבדוק:**
```json
{
  "start_time": "251021120000",
  "end_time": "251021120000"  // Same time!
}
```
מה צפוי? 400? 200? צריך specs!

---

### 1️⃣6️⃣ test_historic_timeout_behavior

**📍 מיקום:** צריך ליצור בקוד

**🎯 מטרה:**
בודק מה קורה אם historic playback **תקוע ולא מסתיים**.

**💡 למה חשוב:**
- אם playback תקוע, הלקוח **ימתין לנצח**
- צריך **timeout mechanism**:
  - אחרי כמה זמן timeout?
  - מה ה-status code? (503? 408?)
  - האם ה-task מתנקה אוטומטית?

**🔗 קשר לאוטומציה:**
- הטסטים שלך מניחים playback **תמיד מסתיים** עם 208
- מה קורה אם **לא** מסתיים?
- זה **timeout logic** test

**📊 מה צריך לבדוק:**
1. Configure historic עם time range ארוך (או לא קיים)
2. Poll עד timeout
3. מה קורה? 
   - 503 Service Unavailable?
   - 408 Request Timeout?
   - Task cleanup?

---

## 📊 סיכום - 11 טסטים (לא 14!)

| # | Test | Category | Why Critical |
|---|------|----------|--------------|
| 1 | `test_get_sensors_list` | API | Prerequisite לכל config |
| 2 | `test_mongodb_connection` | Infrastructure | Backbone של המערכת |
| 3 | `test_kubernetes_connection` | Infrastructure | Orchestration health |
| 4 | `test_nfft_variations` | Validation | כל NFFT values חייבים לעבוד |
| 5 | **test_frequency_range_within_nyquist** | **Data Quality** | **מונע data corruption!** |
| 6 | `test_ssh_connection` | Infrastructure | Access לtroubleshooting |
| 7 | `test_config_with_missing_start_time` | Validation | Required fields |
| 8 | `test_config_with_missing_end_time` | Validation | Required fields |
| 9 | `test_configuration_resource_estimation` | Planning | Capacity planning |
| 10 | `test_high_throughput_configuration` | Performance | Max capacity |
| 11 | `test_low_throughput_configuration` | Edge Cases | Min viable config |

**מחקתי 3 טסטים שקשורים ל-waterfall:**
- ❌ `test_complete_live_monitoring_flow` (כולל waterfall polling)
- ❌ `test_waterfall_with_invalid_task_id` (waterfall endpoint)
- ❌ `test_rapid_waterfall_polling` (waterfall stress test)

---

## 🎯 הטסט הכי קריטי מכולם

**🏆 test_frequency_range_within_nyquist**

למה? כי זה **היחיד** שאם לא בודקים אותו, אפשר לקבל **נתונים שגויים פיזיקלית**.

כל השאר:
- Validation errors → לקוח מקבל 400 ויודע שטעה
- Infrastructure down → אין service, ברור שיש בעיה
- Performance slow → רואים שזה איטי

אבל **Nyquist violation** → המערכת **עובדת**, נותנת **נתונים**, אבל הנתונים **שגויים** (aliasing)!

זה המסוכן ביותר כי לא מבינים שיש בעיה.

---

## ✅ פעולות נדרשות

**קיימים בקוד - רק צריך תיעוד בXray:**
1. test_get_sensors_list ✅
2. test_mongodb_connection ✅
3. test_kubernetes_connection ✅
4. test_nfft_variations ✅
5. test_frequency_range_within_nyquist ✅
6. test_ssh_connection ✅
7. test_configuration_resource_estimation ✅
8. test_high_throughput_configuration ✅
9. test_low_throughput_configuration ✅

**צריך ליצור בקוד + לתעד בXray:**
10. test_config_with_missing_start_time ❌ (צריך ליצור)
11. test_config_with_missing_end_time ❌ (צריך ליצור)

**Optional (ROI related):**
12. test_roi_verification_after_change (אם יש ROI בXray)
13. test_roi_concurrent_changes (אם יש ROI בXray)
14. test_roi_rollback_on_error (אם יש ROI בXray)
15. test_config_with_start_equals_end (edge case)
16. test_historic_timeout_behavior (timeout logic)

---

**Bottom Line:** 11 טסטים (לא waterfall) שחשובים לתיעוד ב-Xray כדי להראות **test coverage מלא** של הfunctionality הקריטי.
