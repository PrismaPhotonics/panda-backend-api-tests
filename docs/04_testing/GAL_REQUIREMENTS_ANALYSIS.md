# ניתוח דרישות גיא - טסטים נוספים נדרשים

**תאריך:** 29 אוקטובר 2025  
**מקור:** בקשה מגיא למספר טסטים שחסרים

---

## 📋 ארבעת הדרישות העיקריות

### 1️⃣ בדיקת חישובים ומספרים במערכת
**מה גיא ביקש:**
> "בדיקה של החישובים שנעשים במערכת ובדיקה שהמספרים נכונים ומגיעים מתחילת ועד סוף התהליכים וגם מוצגים נכון"

### 2️⃣ בדיקות resilience ברמת Kubernetes
**מה גיא ביקש:**
> "בדיקה של הסביבה ברמת Kubernetes. לראות איך המערכת מתמודדת כאשר קומפוננט של המערכת לא למעלה או לא מתפקדות וכיצד ה-Focus Server מתמודד עם המצבים הללו"

### 3️⃣ בדיקת Data Flow (מה נשלח vs מה התקבל)
**מה גיא ביקש:**
> "להוסיף בדיקות שבודקות מה נשלח ומה התקבל ואיך הוא מוצג במערכת"

### 4️⃣ בדיקת Exceptions והצגה בקליינט
**מה גיא ביקש:**
> "לבדוק exceptions שונים במערכת והאם הם מוצגים בקליינט"

---

## 🔍 ניתוח מה קיים VS מה חסר

### 1️⃣ בדיקת חישובים - מה קיים

#### ✅ קיים (חלקי):

**טסטים קיימים:**
- `PZ-13903` - Nyquist Limit Enforcement (בודק שתדר לא עולה על Nyquist)
- `PZ-13901` - NFFT Values Validation (בודק ערכי NFFT תקפים)
- `PZ-13874, PZ-13875` - NFFT Zero/Negative Validation

**מה הם בודקים:**
```python
# test_config_validation_nfft_frequency.py

def test_frequency_range_within_nyquist():
    """בודק שתדר לא עולה על Nyquist limit"""
    prr = 1000  # samples/sec
    nyquist = prr / 2  # 500 Hz
    
    config = {"frequencyRange": {"min": 0, "max": 600}}  # > Nyquist!
    
    # ✅ מצפים לדחייה
    assert response.status_code == 400
```

#### ❌ חסר:

**חישובים שצריך לבדוק:**

1. **חישוב NFFT → Frequency Resolution:**
```python
# חסר טסט!
def test_nfft_affects_frequency_resolution():
    """
    בדוק שNFFT משפיע על רזולוציית התדר.
    
    נוסחה: frequency_resolution = PRR / NFFT
    
    דוגמה:
    - PRR = 1000 Hz
    - NFFT = 512
    - Expected: frequency_resolution = 1000/512 = 1.953 Hz
    """
    pass
```

2. **חישוב Overlap → Output Rate:**
```python
# חסר טסט!
def test_overlap_affects_output_rate():
    """
    בדוק שOverlap משפיע על קצב הפלט.
    
    נוסחה: output_rate = PRR / (NFFT - Overlap)
    
    דוגמה:
    - PRR = 1000 Hz
    - NFFT = 512
    - Overlap = 256
    - Expected: output_rate = 1000/(512-256) = 3.906 frames/sec
    """
    pass
```

3. **חישוב Channel Mapping (SingleChannel):**
```python
# חסר טסט!
def test_singlechannel_mapping_calculation():
    """
    בדוק שמיפוי הערוצים נכון.
    
    Request: channels = {min: 7, max: 7}
    Expected Response:
    - channel_to_stream_index = {7: 0}
    - channel_amount = 1
    - stream_amount = 1
    """
    pass
```

4. **חישוב Time Axis:**
```python
# חסר טסט!
def test_time_axis_calculation():
    """
    בדוק שציר הזמן מחושב נכון.
    
    נוסחה: lines_dt = (NFFT - Overlap) / PRR
    
    דוגמה:
    - NFFT = 512
    - Overlap = 256
    - PRR = 1000
    - Expected: lines_dt = (512-256)/1000 = 0.256 seconds
    """
    pass
```

5. **חישוב Frequency Bins:**
```python
# חסר טסט!
def test_frequency_bins_calculation():
    """
    בדוק שמספר הבינים התדריים נכון.
    
    נוסחה: frequencies_amount = NFFT / 2 + 1
    
    דוגמה:
    - NFFT = 512
    - Expected: frequencies_amount = 257
    """
    pass
```

---

### 2️⃣ בדיקות Resilience - מה קיים

#### ✅ קיים:

**טסטים קיימים:**
- `PZ-13767` - MongoDB Outage Handling
- `PZ-13768` - RabbitMQ Outage Handling
- `PZ-13603` - Mongo Outage on History Configure
- `PZ-13604` - Orchestrator Error Triggers Rollback
- `test_mongodb_outage_resilience.py` - 8 טסטים מקיפים

**מה הם בודקים:**
- MongoDB down → 503 error
- RabbitMQ down → error handling
- Orchestration failure → rollback

#### ❌ חסר:

**תרחישים נוספים שצריך לבדוק:**

1. **Focus Server Pod Restart:**
```python
# חסר טסט!
def test_focus_server_pod_restart_resilience():
    """
    בדוק מה קורה כש-Focus Server עצמו מתחיל מחדש.
    
    תרחיש:
    1. יש job פעיל
    2. Focus Server נופל/מתחדש
    3. בדוק: Job ממשיך לרוץ? נשמר ב-MongoDB?
    4. בדוק: אפשר לשאול על status אחרי restart?
    """
    pass
```

2. **gRPC Job Pod Failure:**
```python
# חסר טסט!
def test_grpc_job_pod_failure():
    """
    בדוק מה קורה כש-gRPC job נכשל באמצע.
    
    תרחיש:
    1. יצירת job
    2. Job רץ
    3. מוחקים את ה-Pod באמצע
    4. בדוק: האם Cleanup Job מתקנה?
    5. בדוק: האם המשאבים משתחררים?
    """
    pass
```

3. **Network Partition:**
```python
# חסר טסט!
def test_network_partition_between_components():
    """
    בדוק מה קורה כשיש בעיית רשת בין קומפוננטות.
    
    תרחישים:
    - Focus Server לא מגיע ל-MongoDB (אבל MongoDB חי)
    - Focus Server לא מגיע ל-RabbitMQ (אבל RabbitMQ חי)
    - גRPC Job לא מגיע ל-RabbitMQ
    """
    pass
```

4. **CPU/Memory Exhaustion:**
```python
# חסר טסט!
def test_resource_exhaustion_handling():
    """
    בדוק מה קורה כשאוזלים משאבים.
    
    תרחישים:
    - יותר מדי jobs concurrent (>30)
    - אין GPU פנוי
    - אין זיכרון
    - CPU ב-100%
    """
    pass
```

5. **MongoDB Slow (לא Down, אבל איטי):**
```python
# חסר טסט!
def test_mongodb_slow_response():
    """
    בדוק מה קורה כ-MongoDB איטי (לא down, פשוט slow).
    
    תרחיש:
    1. MongoDB עונה אבל לוקח 10+ שניות
    2. בדוק: האם יש timeout?
    3. בדוק: האם User מקבל שגיאה או תקוע?
    """
    pass
```

---

### 3️⃣ בדיקת Data Flow - מה קיים

#### ✅ קיים (מינימלי):

**יש validation בסיסי:**
```python
# בקוד API client
def configure_streaming_job(self, payload):
    response = self.post("/configure", json=payload_dict)
    configure_response = ConfigureResponse(**response_data)  # Pydantic validation
    return configure_response
```

#### ❌ חסר:

**טסטים מפורטים של Data Flow:**

1. **Request/Response Field Mapping:**
```python
# חסר טסט!
def test_request_response_field_mapping():
    """
    בדוק שכל שדה בRequest מופיע נכון בResponse.
    
    Request:
    {
        "viewType": 1,
        "channels": {"min": 1, "max": 8},
        "frequencyRange": {"min": 100, "max": 500},
        "nfftSelection": 512,
        ...
    }
    
    Response - בדוק שמופיע:
    {
        "view_type": "1",  # ✓ מתאים
        "channel_amount": 8,  # ✓ מחושב נכון (8-1+1)
        "frequencies_amount": 257,  # ✓ מחושב נכון (512/2+1)
        ...
    }
    """
    pass
```

2. **Data Integrity Through Pipeline:**
```python
# חסר טסט!
def test_data_integrity_through_pipeline():
    """
    בדוק שהנתונים לא משתנים בדרך.
    
    Flow:
    1. שלח configure request עם ערכים ספציפיים
    2. שלוף מ-MongoDB את ה-job document
    3. בדוק ש-MongoDB document תואם את ה-request
    4. קרא /metadata/{job_id}
    5. בדוק ש-metadata תואם את MongoDB
    6. השווה הכל - אין שינויים לא מתועדים
    """
    pass
```

3. **Timestamp Consistency:**
```python
# חסר טסט!
def test_timestamp_consistency_across_system():
    """
    בדוק שהטיימסטמפים עקביים בכל המערכת.
    
    בדוק:
    1. Request timestamp (start_time, end_time)
    2. MongoDB recorded timestamp
    3. Metadata timestamp
    4. gRPC stream timestamp
    
    ווידוא:
    - כולם באותו פורמט (epoch? ISO?)
    - כולם באותו timezone
    - אין הסטות בשניות
    """
    pass
```

4. **Channel Mapping Consistency:**
```python
# חסר טסט!
def test_channel_mapping_end_to_end():
    """
    בדוק ש-channel mapping עקבי.
    
    Request: channels = {min: 5, max: 10}
    
    ווידוא בכל שלב:
    1. Configure response: channel_to_stream_index correct?
    2. MongoDB document: channels saved correctly?
    3. Metadata: channel info consistent?
    4. gRPC stream: right channels streamed?
    """
    pass
```

---

### 4️⃣ בדיקת Exceptions - מה קיים

#### ✅ קיים (חלקי):

**API Quality Tests (PZ-13291-13299):**
- Error uniformity
- OpenAPI alignment
- Stack traces in 4xx errors
- Metadata readiness
- Time validation

**מה הם בודקים:**
```python
def test_no_stack_traces_in_4xx_errors():
    """בודק שאין stack traces בשגיאות 400"""
    response = api.configure(invalid_payload)
    assert "Traceback" not in response.text
    assert "File \"" not in response.text
```

#### ❌ חסר:

**טסטים נוספים לException Handling:**

1. **Error Message Clarity:**
```python
# חסר טסט!
def test_error_messages_are_user_friendly():
    """
    בדוק שהודעות שגיאה ברורות למשתמש.
    
    BAD: "Validation error in field x.y.z"
    GOOD: "NFFT must be 256, 512, 1024, or 2048. You provided: 1000"
    
    BAD: "Internal server error"
    GOOD: "Database temporarily unavailable, please try again"
    """
    pass
```

2. **Error Code Consistency:**
```python
# חסר טסט!
def test_error_codes_are_consistent():
    """
    בדוק שכל שגיאה זהה מקבלת אותו קוד.
    
    דוגמה:
    - Missing field → תמיד "MISSING_REQUIRED_FIELD"
    - Invalid range → תמיד "INVALID_RANGE"
    - Out of bounds → תמיד "VALUE_OUT_OF_BOUNDS"
    """
    pass
```

3. **Frontend Error Display:**
```python
# חסר טסט!
def test_frontend_receives_and_displays_errors():
    """
    בדוק שה-Frontend מקבל ומציג שגיאות.
    
    תרחיש:
    1. שלח request שגוי דרך Frontend
    2. Backend מחזיר 400 עם הודעה
    3. בדוק: האם Frontend מציג את ההודעה?
    4. בדוק: האם ההודעה מוצגת במקום הנכון?
    5. בדוק: האם User יכול להבין מה לתקן?
    """
    pass
```

4. **Exception Logging:**
```python
# חסר טסט!
def test_exceptions_are_logged_correctly():
    """
    בדוק שכל exception נרשם בלוגים.
    
    בדוק:
    1. שגיאה → יש לוג ב-Focus Server
    2. הלוג כולל context (user, request, timestamp)
    3. הלוג כולל severity level (ERROR/WARN/INFO)
    4. הלוג לא כולל sensitive data
    """
    pass
```

5. **500 Errors Prevention:**
```python
# חסר טסט!
def test_no_500_errors_on_invalid_input():
    """
    בדוק ש-NEVER מחזירים 500 על input לא תקף.
    
    כלל: 500 = בעיה בשרת, לא בקליינט
    
    בדוק:
    - Invalid JSON → 400 (לא 500)
    - Missing fields → 400 (לא 500)
    - Invalid types → 400 (לא 500)
    - Out of range → 400 (לא 500)
    
    רק אלה יכולים להיות 500:
    - MongoDB down
    - Out of memory
    - Unhandled exception בקוד
    """
    pass
```

---

## 📊 סיכום - מה קיים ומה חסר

| קטגוריה | קיים | חסר | אחוז כיסוי |
|---------|------|-----|-----------|
| **1. בדיקת חישובים** | 4 טסטים בסיסיים | 10+ טסטים מתקדמים | ~30% |
| **2. Resilience** | 8 טסטים | 15+ תרחישים נוספים | ~35% |
| **3. Data Flow** | Validation בסיסי | 12+ טסטי E2E | ~20% |
| **4. Exceptions** | 9 טסטי API Quality | 15+ טסטי UX/Logging | ~40% |
| **סה"כ** | ~30 טסטים | ~50 טסטים חסרים | **~38%** |

---

## 🎯 המלצה: תוכנית עבודה

### Phase 1: Calculations (שבועיים)
**עדיפות: גבוהה**
- 10 טסטים לחישובים מתמטיים
- Validation של נוסחאות
- End-to-end calculation testing

### Phase 2: Data Flow (3 שבועות)
**עדיפות: גבוהה מאוד**
- 12 טסטי E2E למעקב אחרי data
- Request/Response validation מלא
- Integrity checks

### Phase 3: Resilience (שבועיים)
**עדיפות: בינונית-גבוהה**
- 15 תרחישי Kubernetes failures
- Network partition tests
- Resource exhaustion tests

### Phase 4: Exception Handling (שבוע)
**עדיפות: בינונית**
- 15 טסטי UX/Error messages
- Logging validation
- Frontend integration tests

**סה"כ זמן משוער:** 8-10 שבועות  
**משאבים:** 1 QA Engineer (full-time)

---

**מסמך זה ממתין לאישור ותעדוף מגיא לפני תחילת העבודה.**

