# Live vs Historic Mode - Complete Analysis

**Date:** October 23, 2025  
**Author:** QA Automation Architect  
**Purpose:** Document requirements and validation rules for Live and Historic modes

---

## 📋 Executive Summary

The Focus Server supports **two distinct operating modes**:

1. **🔴 Live Mode** - Real-time streaming from sensors
2. **📼 Historic Mode** - Playback of previously recorded data

**Critical Finding:** The current tests do NOT properly distinguish between these modes, which have different validation requirements.

---

## 🔍 Mode Detection

### How the Server Determines Mode

| Field | Live Mode | Historic Mode |
|-------|-----------|---------------|
| `start_time` | `null` or absent | **Required** (epoch timestamp) |
| `end_time` | `null` or absent | **Required** (epoch timestamp) |
| Behavior | Streams real-time data | Plays back recording from time range |

**Rule:** If **both** `start_time` and `end_time` are provided → Historic Mode. Otherwise → Live Mode.

---

## 🔴 Live Mode - Detailed Requirements

### 1. Field Requirements

```python
# Live Mode Configuration
{
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {"height": 1000},
    "channels": {"min": 1, "max": 50},
    "frequencyRange": {"min": 0, "max": 500},
    "start_time": null,       # ✅ MUST be null
    "end_time": null,          # ✅ MUST be null
    "view_type": "0"
}
```

### 2. Validation Rules

| Field | Requirement | Validation | Notes |
|-------|------------|------------|-------|
| `start_time` | Must be `null` | No validation | Streaming from current time |
| `end_time` | Must be `null` | No validation | Continuous streaming |
| `displayTimeAxisDuration` | Optional | `> 0` if provided | Specifies time window display |
| `nfftSelection` | Optional | `> 0` if provided | FFT window size |
| `frequencyRange` | Optional | `min >= 0`, `max > min` | Frequency band |
| `channels` | **Required** | `min >= 1`, `max >= min` | Sensor range |
| `displayInfo.height` | **Required** | `> 0` | Canvas height |
| `view_type` | **Required** | Valid enum | View type |

### 3. Behavior

- ✅ **Connects to sensors** in real-time
- ✅ **Streams continuously** until client disconnects
- ✅ **No end condition** - runs indefinitely
- ✅ **Low latency** - displays data as it arrives

### 4. Use Cases

1. **Monitoring:** Real-time sensor monitoring
2. **Detection:** Live event detection and alerts
3. **Debugging:** Real-time system diagnostics
4. **Demos:** Live demonstrations to stakeholders

---

## 📼 Historic Mode - Detailed Requirements

### 1. Field Requirements

```python
# Historic Mode Configuration (Old API - ConfigureRequest)
{
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {"height": 1000},
    "channels": {"min": 1, "max": 50},
    "frequencyRange": {"min": 0, "max": 500},
    "start_time": 1697500000,  # ✅ REQUIRED - epoch seconds (int)
    "end_time": 1697510000,    # ✅ REQUIRED - epoch seconds (int)
    "view_type": "0"
}

# Historic Mode Configuration (New API - ConfigTaskRequest)
{
    "displayTimeAxisDuration": 10.0,
    "nfftSelection": 1024,
    "canvasInfo": {"height": 1000},
    "sensors": {"min": 1, "max": 50},
    "frequencyRange": {"min": 0, "max": 500},
    "start_time": "251023120000",  # ✅ REQUIRED - yymmddHHMMSS format (string)
    "end_time": "251023130000"     # ✅ REQUIRED - yymmddHHMMSS format (string)
}
```

### 2. Validation Rules

| Field | Requirement | Validation | Error |
|-------|------------|------------|-------|
| `start_time` | **REQUIRED** | `>= 0` (epoch) | 400 Bad Request |
| `end_time` | **REQUIRED** | `>= 0` (epoch) | 400 Bad Request |
| Time range | **REQUIRED** | `end_time > start_time` | 400 Bad Request |
| Time format (new API) | **REQUIRED** | `yymmddHHMMSS` (12 digits) | 400 Bad Request |
| `displayTimeAxisDuration` | Optional | `> 0` if provided | - |
| `nfftSelection` | Optional | `> 0` if provided | - |
| `frequencyRange` | Optional | `min >= 0`, `max > min` | - |
| `channels` | **Required** | `min >= 1`, `max >= min` | - |
| `displayInfo.height` | **Required** | `> 0` | - |
| `view_type` | **Required** | Valid enum | - |

### 3. Behavior

- ✅ **Queries MongoDB** for recordings in time range
- ✅ **Plays back** historical data from storage (S3/local)
- ✅ **Finite duration** - ends when time range is complete
- ✅ **Reproducible** - same inputs always produce same output

### 4. Use Cases

1. **Analysis:** Post-event analysis of recorded data
2. **Investigation:** Root cause analysis
3. **Training:** Training ML models on historical data
4. **Compliance:** Regulatory auditing and reporting
5. **Research:** Scientific research on past events

---

## ⚖️ Key Differences

### Comparison Matrix

| Aspect | Live Mode | Historic Mode |
|--------|-----------|---------------|
| **Data Source** | Real-time sensors | Recorded files (S3/storage) |
| **start_time** | `null` | Epoch timestamp (**required**) |
| **end_time** | `null` | Epoch timestamp (**required**) |
| **Duration** | Infinite | Finite (end_time - start_time) |
| **Latency** | Low (< 1s) | Variable (depends on file size) |
| **Database query** | Not needed | **MongoDB** query for recordings |
| **Reproducible** | ❌ No (always changing) | ✅ Yes (same data every time) |
| **Use case** | Monitoring, detection | Analysis, investigation |

### Validation Differences

| Validation | Live Mode | Historic Mode |
|------------|-----------|---------------|
| **Time fields** | Must be `null` | Must be provided (both) |
| **Time range** | N/A | `end_time > start_time` |
| **Time format** | N/A | Epoch (old) or yymmddHHMMSS (new) |
| **Recording existence** | N/A | Must exist in MongoDB |
| **Data availability** | Sensors must be active | Files must exist in storage |

---

## 🔧 Current Models

### ConfigureRequest (Old API - POST /configure)

```python
class ConfigureRequest(BaseModel):
    displayTimeAxisDuration: Optional[int] = Field(None, gt=0)
    nfftSelection: Optional[int] = Field(None, gt=0)
    displayInfo: DisplayInfo = Field(...)
    channels: Channels = Field(...)
    frequencyRange: Optional[FrequencyRange] = Field(None)
    start_time: Optional[int] = Field(None, ge=0)  # Epoch seconds
    end_time: Optional[int] = Field(None, ge=0)    # Epoch seconds
    view_type: ViewType = Field(...)
    
    @field_validator('end_time')
    def validate_time_range(cls, v: Optional[int], info: ValidationInfo):
        if v is not None and info.data.get('start_time') is not None:
            if v <= info.data['start_time']:
                raise ValueError('end_time must be > start_time')
        return v
```

**Issue:** ⚠️ Model does NOT enforce that both times must be provided together for historic mode.

### ConfigTaskRequest (New API - POST /config/{task_id})

```python
class ConfigTaskRequest(BaseModel):
    displayTimeAxisDuration: float = Field(..., gt=0)
    nfftSelection: int = Field(..., gt=0)
    canvasInfo: Dict[str, int] = Field(...)
    sensors: Dict[str, int] = Field(...)
    frequencyRange: Dict[str, int] = Field(...)
    start_time: Optional[str] = Field(None)  # yymmddHHMMSS format
    end_time: Optional[str] = Field(None)    # yymmddHHMMSS format
    
    @model_validator(mode='after')
    def validate_time_range(self):
        # Only validate if both times are provided (historic mode)
        if self.start_time and self.end_time:
            # Validate format (12 digits)
            if not re.match(r'^\d{12}$', self.start_time):
                raise ValueError('start_time must be yymmddHHMMSS')
            if not re.match(r'^\d{12}$', self.end_time):
                raise ValueError('end_time must be yymmddHHMMSS')
            # Validate range
            if self.end_time <= self.start_time:
                raise ValueError('end_time must be > start_time')
        return self
```

**Issue:** ⚠️ Model does NOT enforce that both times must be provided together for historic mode.

---

## ❌ Current Test Problems

### 1. Tests Don't Distinguish Modes

Current tests use **Live Mode configuration** (start_time=null, end_time=null) but don't validate mode-specific behavior.

```python
# Current test payload - implicitly Live Mode
config_payload = {
    "displayTimeAxisDuration": 10,
    "nfftSelection": 1024,
    "displayInfo": {"height": 1000},
    "channels": {"min": 1, "max": 50},
    "frequencyRange": {"min": 0, "max": 500},
    "start_time": None,  # ← Live Mode
    "end_time": None,    # ← Live Mode
    "view_type": "0"
}
```

**Problem:** Tests don't validate:
- ❌ What happens if only `start_time` is provided (invalid state)?
- ❌ What happens if only `end_time` is provided (invalid state)?
- ❌ Does server enforce both times for historic mode?
- ❌ Does server reject invalid time ranges?
- ❌ Does server validate time format?

### 2. Missing Historic Mode Tests

No tests exist for:
- ❌ Valid historic configuration
- ❌ Invalid historic time ranges
- ❌ Missing start_time or end_time in historic mode
- ❌ Time format validation (yymmddHHMMSS)
- ❌ Recordings not found for time range

### 3. Missing Mode Validation Tests

No tests for:
- ❌ Server distinguishes between live and historic
- ❌ Server rejects partial time specification (only start OR only end)
- ❌ Server handles mode-specific errors correctly

---

## ✅ Required Test Coverage

### Live Mode Tests

```python
class TestLiveMode:
    """Tests for Live Mode validation."""
    
    def test_live_mode_with_null_times():
        """Valid: Both times are null."""
        config = {..., "start_time": None, "end_time": None}
        # ✅ Should succeed
    
    def test_live_mode_rejects_only_start_time():
        """Invalid: Only start_time provided."""
        config = {..., "start_time": 123456, "end_time": None}
        # ❌ Should reject (ambiguous mode)
    
    def test_live_mode_rejects_only_end_time():
        """Invalid: Only end_time provided."""
        config = {..., "start_time": None, "end_time": 789012}
        # ❌ Should reject (ambiguous mode)
```

### Historic Mode Tests

```python
class TestHistoricMode:
    """Tests for Historic Mode validation."""
    
    def test_historic_mode_valid_time_range():
        """Valid: Both times provided, end > start."""
        config = {..., "start_time": 1697500000, "end_time": 1697510000}
        # ✅ Should succeed
    
    def test_historic_mode_rejects_equal_times():
        """Invalid: start_time == end_time."""
        config = {..., "start_time": 1697500000, "end_time": 1697500000}
        # ❌ Should reject with 400
    
    def test_historic_mode_rejects_inverted_range():
        """Invalid: end_time < start_time."""
        config = {..., "start_time": 1697510000, "end_time": 1697500000}
        # ❌ Should reject with 400
    
    def test_historic_mode_rejects_negative_time():
        """Invalid: Negative timestamp."""
        config = {..., "start_time": -100, "end_time": 1697510000}
        # ❌ Should reject with 400
    
    def test_historic_mode_rejects_missing_start():
        """Invalid: Missing start_time in historic mode."""
        config = {..., "start_time": None, "end_time": 1697510000}
        # ❌ Should reject (incomplete spec)
    
    def test_historic_mode_rejects_missing_end():
        """Invalid: Missing end_time in historic mode."""
        config = {..., "start_time": 1697500000, "end_time": None}
        # ❌ Should reject (incomplete spec)
```

### Mode Detection Tests

```python
class TestModeDetection:
    """Tests for server mode detection logic."""
    
    def test_server_detects_live_mode():
        """Server correctly identifies live mode."""
        # Send live config, verify live behavior
    
    def test_server_detects_historic_mode():
        """Server correctly identifies historic mode."""
        # Send historic config, verify historic behavior
    
    def test_server_rejects_ambiguous_mode():
        """Server rejects config with only one time field."""
        # Send partial time spec, verify 400 error
```

---

## 📝 Recommended Implementation

### 1. Add Mode Enum (Optional but Recommended)

```python
class ConfigMode(str, Enum):
    """Configuration mode."""
    LIVE = "live"
    HISTORIC = "historic"
```

### 2. Enhanced Model Validation

```python
class ConfigureRequest(BaseModel):
    # ... existing fields ...
    
    @model_validator(mode='after')
    def validate_mode_consistency(self):
        """Ensure time fields are consistent with intended mode."""
        has_start = self.start_time is not None
        has_end = self.end_time is not None
        
        # Both or neither - clear intent
        if has_start and has_end:
            # Historic mode - validate range
            if self.end_time <= self.start_time:
                raise ValueError('Historic mode: end_time must be > start_time')
            return self
        
        if not has_start and not has_end:
            # Live mode - OK
            return self
        
        # One but not the other - ambiguous!
        raise ValueError(
            'Ambiguous mode: provide both start_time and end_time for historic mode, '
            'or neither for live mode'
        )
```

### 3. Server-Side Validation

```python
def configure_endpoint(config: ConfigureRequest):
    """Configure endpoint with mode detection."""
    
    # Detect mode
    is_historic = config.start_time is not None and config.end_time is not None
    is_live = config.start_time is None and config.end_time is None
    
    if not is_historic and not is_live:
        return 400, {"error": "Invalid mode: must specify both times or neither"}
    
    if is_historic:
        # Validate recordings exist
        recordings = db.query_recordings(config.start_time, config.end_time)
        if not recordings:
            return 404, {"error": f"No recordings found for time range"}
        
        # Start historic playback
        return start_historic_job(config, recordings)
    
    else:  # is_live
        # Start live streaming
        return start_live_job(config)
```

---

## 🎯 Next Steps

### Phase 1: Documentation ✅
- [x] Research and document mode differences
- [x] Identify validation requirements
- [x] Document test gaps

### Phase 2: Test Updates (In Progress)
- [ ] Update existing tests to explicitly specify mode
- [ ] Add Live Mode validation tests
- [ ] Add Historic Mode validation tests
- [ ] Add Mode Detection tests
- [ ] Add Requirement tests (xfail) for server-side validation

### Phase 3: Model Updates (Future)
- [ ] Enhance Pydantic models with mode validation
- [ ] Add explicit mode field (optional)
- [ ] Add comprehensive validators

### Phase 4: Server Updates (Future - Backend Team)
- [ ] Implement server-side mode validation
- [ ] Add clear error messages for mode violations
- [ ] Update API documentation

---

**Created:** October 23, 2025  
**Status:** Research Complete, Implementation Pending  
**Priority:** HIGH

