# דוח בדיקת בעיות ספציפיות - טיקט PZ-14592

**תאריך:** 2025-11-06  
**סביבה:** Staging (10.10.10.100)

---

## סיכום בעיות

| מפתח Xray | בעיה | סוג | חומרה | סטטוס |
|-----------|------|-----|--------|--------|
| **PZ-13563** | 503 Service Unavailable | תשתית | גבוהה | ❌ נכשל |
| **PZ-13897** | 404 Not Found - /sensors | תשתית | בינונית | ⏭️ דילג |
| **PZ-13764** | Validation Error - "waiting for fiber" | סכמה | בינונית | ⏭️ דילג |
| **PZ-13561** | Validation Error - "waiting for fiber" | סכמה | בינונית | ⏭️ דילג |

---

## בעיה #1: PZ-13563 - 503 Service Unavailable

### תיאור הבעיה

**טסט:** `test_get_metadata_by_job_id`  
**Endpoint:** `POST /focus-server/configure`  
**שגיאה:**
```
APIError: Request failed: HTTPSConnectionPool(host='10.10.10.100', port=443): 
Max retries exceeded with url: /focus-server/configure 
(Caused by ResponseError('too many 503 error responses'))
```

### מה קרה

1. הטסט מנסה ליצור streaming job דרך `POST /focus-server/configure`
2. השרת מחזיר **503 Service Unavailable** 4 פעמים (retries)
3. הטסט נכשל כי לא הצליח ליצור `job_id` (נדרש לטסט)

### ניתוח

**קוד הטסט:**
```python
# tests/integration/api/test_api_endpoints_additional.py:270
response = focus_server_api.configure_streaming_job(request)
job_id = response.job_id  # נכשל כאן כי response לא התקבל
```

**סיבות אפשריות:**
1. ✅ **שרת Focus Server לא זמין** - Pod לא רץ או לא מוכן
2. ✅ **עומס על השרת** - יותר מדי בקשות בו-זמנית
3. ✅ **בעיית תשתית זמנית** - בעיית רשת או Kubernetes
4. ✅ **בעיית קונפיגורציה** - השרת לא מוגדר נכון בסביבת Staging

### בדיקות מומלצות

```bash
# 1. בדיקת סטטוס Pod
kubectl get pods -n panda | grep focus-server

# 2. בדיקת לוגים
kubectl logs -n panda <focus-server-pod-name> --tail=100

# 3. בדיקת health check
curl -k https://10.10.10.100/focus-server/health

# 4. בדיקת connectivity
curl -k -X POST https://10.10.10.100/focus-server/configure \
  -H "Content-Type: application/json" \
  -d '{"displayTimeAxisDuration": 10, "nfftSelection": 1024, ...}'
```

### פתרונות מומלצים

#### פתרון 1: הוספת Retry Logic (מומלץ)

```python
# src/apis/focus_server_api.py
def configure_streaming_job(self, request: ConfigureRequest, max_retries: int = 3) -> ConfigureResponse:
    """Configure streaming job with retry logic."""
    for attempt in range(max_retries):
        try:
            response = self.post("/configure", json=payload_dict)
            return ConfigureResponse(**response.json())
        except APIError as e:
            if "503" in str(e) and attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise
```

#### פתרון 2: הוספת Health Check לפני הטסט

```python
# tests/integration/api/test_api_endpoints_additional.py
def test_get_metadata_by_job_id(self, focus_server_api: FocusServerAPI):
    # Check server health first
    try:
        health = focus_server_api.health_check()
        if not health.is_healthy:
            pytest.skip("Focus Server is not healthy")
    except:
        pytest.skip("Focus Server is not available")
    
    # Continue with test...
```

#### פתרון 3: שיפור Error Handling בטסט

```python
# tests/integration/api/test_api_endpoints_additional.py
try:
    response = focus_server_api.configure_streaming_job(request)
    job_id = response.job_id
except APIError as e:
    if "503" in str(e):
        pytest.skip(f"Server unavailable (503): {e}")
    raise
```

### המלצה

**דחוף (High Priority):**
1. לבדוק את סטטוס Focus Server Pod ב-Kubernetes
2. לבדוק את הלוגים של השרת
3. לנסות שוב מאוחר יותר
4. להוסיף retry logic ל-API client

---

## בעיה #2: PZ-13897 - 404 Not Found - /sensors

### תיאור הבעיה

**טסט:** `test_get_sensors_endpoint`  
**Endpoint:** `GET /focus-server/sensors`  
**שגיאה:**
```
404 Not Found
Response: {"detail": "Not Found"}
```

### מה קרה

1. הטסט מנסה לגשת ל-`GET /focus-server/sensors`
2. השרת מחזיר **404 Not Found**
3. הטסט מדלג (skip) - זה נכון ✅

### ניתוח

**קוד השרת קיים:**
```python
# pz/microservices/focus_server/focus_server.py:143
@app.get('/sensors')
def sensors():
    return ORJSONResponse(content={"sensors": [sensor for sensor in range(focus_manager.sensors)]}, status_code=200)
```

**אבל ה-endpoint לא זמין בסביבת Staging!**

**סיבות אפשריות:**
1. ✅ **Endpoint לא מופעל** - Route לא רשום נכון
2. ✅ **בעיית routing** - Path לא נכון (`/focus-server/sensors` vs `/sensors`)
3. ✅ **Endpoint זמין רק בסביבות מסוימות** - Feature flag או environment check
4. ✅ **בעיית deployment** - קוד ישן או לא מעודכן

### בדיקות מומלצות

```bash
# 1. בדיקת Swagger/API docs
curl -k https://10.10.10.100/api/swagger/#/

# 2. בדיקת endpoints זמינים
curl -k https://10.10.10.100/focus-server/channels  # זה עובד
curl -k https://10.10.10.100/focus-server/sensors   # זה לא עובד

# 3. בדיקת קוד השרת
# לבדוק אם ה-endpoint רשום ב-routes
```

### פתרונות מומלצים

#### פתרון 1: עדכון הטסט לבדוק אם Endpoint קיים (מומלץ)

```python
# tests/integration/api/test_api_endpoints_additional.py
@pytest.mark.xray("PZ-13897")
def test_get_sensors_endpoint(self, focus_server_api: FocusServerAPI):
    """Test PZ-13897: GET /sensors - Retrieve Available Sensors List."""
    
    # Check if endpoint exists first
    try:
        response = focus_server_api.get("/sensors")
        if response.status_code == 404:
            pytest.skip("GET /sensors endpoint not available in this environment")
    except APIError as e:
        if "404" in str(e) or "Not Found" in str(e):
            pytest.skip(f"GET /sensors endpoint not available: {e}")
        raise
    
    # Continue with test...
```

#### פתרון 2: הוספת Marker לטסטים שדורשים Endpoint מסוים

```python
# tests/integration/api/test_api_endpoints_additional.py
@pytest.mark.xray("PZ-13897")
@pytest.mark.requires_endpoint("/sensors")  # Custom marker
def test_get_sensors_endpoint(self, focus_server_api: FocusServerAPI):
    # Test implementation...
```

#### פתרון 3: בדיקה ב-Swagger לפני הרצת הטסט

```python
# conftest.py או לפני הטסט
def check_endpoint_available(endpoint: str) -> bool:
    """Check if endpoint exists in Swagger/API docs."""
    # Implementation...
```

### המלצה

**בינוני (Medium Priority):**
1. לבדוק אם Endpoint קיים ב-Swagger/API docs
2. לבדוק אם Endpoint זמין בסביבת Production
3. לעדכן את הטסט לטפל ב-404 בצורה יותר מפורשת
4. לפתוח טיקט Backend אם Endpoint צריך להיות זמין

---

## בעיה #3: PZ-13764 / PZ-13561 - Validation Error "waiting for fiber"

### תיאור הבעיה

**טסט:** `test_get_live_metadata_available`  
**Endpoint:** `GET /focus-server/live_metadata`  
**שגיאה:**
```
4 validation errors for LiveMetadataFlat:
- prr: Input should be greater than 0 [input_value=0.0]
- dx: Input should be greater than 0 [input_value=0.0]
- num_samples_per_trace: Field required [missing]
- dtype: Field required [missing]
```

### מה קרה

1. הטסט קיבל response מ-`GET /live_metadata` עם status **200 OK**
2. אבל הנתונים לא תקינים:
   ```json
   {
     "dx": 0.0,
     "prr": 0.0,
     "sw_version": "waiting for fiber",
     "number_of_channels": 2337,
     "fiber_description": "waiting for fiber"
   }
   ```
3. המודל `LiveMetadataFlat` דורש:
   - `prr > 0` (required)
   - `dx > 0` (אם קיים)
   - `num_samples_per_trace` (required, חסר)
   - `dtype` (required, חסר)

### ניתוח

**מודל LiveMetadataFlat:**
```python
# src/models/focus_server_models.py:461
class LiveMetadataFlat(BaseModel):
    prr: float = Field(..., description="Pulse repetition rate", gt=0)  # ← דורש > 0
    num_samples_per_trace: int = Field(..., description="Samples per trace", gt=0)  # ← required
    dtype: str = Field(..., description="Data type")  # ← required
    dx: Optional[float] = Field(None, description="Distance between sensors (meters)", gt=0)  # ← אם קיים, דורש > 0
```

**השרת מחזיר מצב "waiting for fiber"** - זה מצב תקין של המערכת, אבל המודל לא תומך בזה!

### פתרונות מומלצים

#### פתרון 1: עדכון המודל לתמוך ב-"waiting for fiber" (מומלץ)

```python
# src/models/focus_server_models.py
class LiveMetadataFlat(BaseModel):
    """Response model for GET /live_metadata endpoint."""
    
    # Make fields optional to support "waiting for fiber" state
    prr: Optional[float] = Field(None, description="Pulse repetition rate", gt=0)
    num_samples_per_trace: Optional[int] = Field(None, description="Samples per trace", gt=0)
    dtype: Optional[str] = Field(None, description="Data type")
    dx: Optional[float] = Field(None, description="Distance between sensors (meters)", gt=0)
    
    # Status fields
    sw_version: Optional[str] = Field(None, description="Software version")
    fiber_description: Optional[str] = Field(None, description="Fiber description")
    number_of_channels: Optional[int] = Field(None, description="Number of channels", gt=0)
    
    @property
    def is_ready(self) -> bool:
        """Check if metadata is ready (not waiting for fiber)."""
        return (
            self.prr is not None and self.prr > 0 and
            self.num_samples_per_trace is not None and
            self.dtype is not None
        )
    
    @property
    def is_waiting_for_fiber(self) -> bool:
        """Check if system is waiting for fiber."""
        return (
            self.sw_version == "waiting for fiber" or
            self.fiber_description == "waiting for fiber"
        )
```

#### פתרון 2: עדכון הטסט לטפל ב-"waiting for fiber"

```python
# tests/integration/api/test_api_endpoints_additional.py
@pytest.mark.xray("PZ-13764", "PZ-13561")
def test_get_live_metadata_available(self, focus_server_api: FocusServerAPI):
    """Test PZ-13764, PZ-13561: GET /live_metadata returns metadata when available."""
    
    try:
        metadata = focus_server_api.get_live_metadata_flat()
        
        # Check if system is waiting for fiber
        if metadata.is_waiting_for_fiber:
            pytest.skip("System is waiting for fiber - metadata not ready yet")
        
        # Verify metadata structure only if ready
        assert metadata.is_ready, "Metadata should be ready"
        assert metadata.prr > 0
        assert metadata.num_samples_per_trace > 0
        assert metadata.dtype is not None
        
    except ValidationError as e:
        # Check if it's a "waiting for fiber" case
        response = focus_server_api.get("/live_metadata")
        response_data = response.json()
        
        if response_data.get("sw_version") == "waiting for fiber":
            pytest.skip("System is waiting for fiber - metadata not ready yet")
        raise
```

#### פתרון 3: יצירת מודל נפרד ל-"waiting for fiber"

```python
# src/models/focus_server_models.py
class LiveMetadataWaiting(BaseModel):
    """Response model when system is waiting for fiber."""
    sw_version: str = "waiting for fiber"
    fiber_description: str = "waiting for fiber"
    number_of_channels: Optional[int] = None

class LiveMetadataFlat(BaseModel):
    """Response model for GET /live_metadata endpoint when ready."""
    prr: float = Field(..., gt=0)
    num_samples_per_trace: int = Field(..., gt=0)
    dtype: str = Field(...)
    # ... rest of fields

# In API client:
def get_live_metadata_flat(self) -> Union[LiveMetadataFlat, LiveMetadataWaiting]:
    """Get live metadata - returns either ready or waiting state."""
    response = self.get("/live_metadata")
    data = response.json()
    
    if data.get("sw_version") == "waiting for fiber":
        return LiveMetadataWaiting(**data)
    return LiveMetadataFlat(**data)
```

### המלצה

**בינוני (Medium Priority):**
1. לעדכן את המודל `LiveMetadataFlat` לתמוך ב-"waiting for fiber"
2. לעדכן את הטסט לטפל במצב "waiting for fiber"
3. להוסיף property `is_ready` לבדיקה נוחה

---

## סיכום המלצות

### דחוף (High Priority):

1. **PZ-13563 - 503 Errors**
   - ✅ לבדוק את סטטוס Focus Server Pod
   - ✅ להוסיף retry logic ל-API client
   - ✅ להוסיף health check לפני הטסט

### בינוני (Medium Priority):

2. **PZ-13897 - Endpoint לא קיים**
   - ✅ לבדוק אם `/sensors` קיים ב-API docs
   - ✅ לעדכן את הטסט לטפל ב-404 בצורה מפורשת
   - ✅ לפתוח טיקט Backend אם צריך

3. **PZ-13764/PZ-13561 - Validation Errors**
   - ✅ לעדכן את המודל לתמוך ב-"waiting for fiber"
   - ✅ לעדכן את הטסט לטפל במצב "waiting for fiber"

---

## קבצים לעדכון

1. `src/models/focus_server_models.py` - עדכון LiveMetadataFlat
2. `src/apis/focus_server_api.py` - הוספת retry logic
3. `tests/integration/api/test_api_endpoints_additional.py` - שיפור error handling

---
*דוח נוצר: 2025-11-06*  
*מבוסס על תוצאות הרצת טסטים מטיקט PZ-14592*

