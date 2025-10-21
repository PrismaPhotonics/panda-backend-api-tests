# 🎯 Critical Missing Specifications for Automation Testing
## Complete List of Required Specs for Clear Pass/Fail Results

**Project:** Panda Focus Server  
**Date:** 2025-10-21  
**Purpose:** Define exact values needed for automation assertions  

---

## 1️⃣ API PERFORMANCE SPECIFICATIONS

### Response Time Thresholds
```yaml
# REQUIRED VALUES:
POST /config/{task_id}:
  p95_latency_ms: ?        # Currently: No assertion
  p99_latency_ms: ?        # Currently: No assertion
  max_timeout_sec: ?       # Currently: No timeout

GET /waterfall/{task_id}/{row_count}:
  live_mode:
    p95_latency_ms: ?      # Currently: No assertion
    p99_latency_ms: ?      # Currently: No assertion
    max_timeout_sec: ?     # Currently: No timeout
  historic_mode:
    p95_latency_ms: ?      # Currently: No assertion
    p99_latency_ms: ?      # Currently: No assertion
    max_timeout_sec: ?     # Currently: No timeout

GET /metadata/{task_id}:
  p95_latency_ms: ?        # Currently: No assertion
  p99_latency_ms: ?        # Currently: No assertion
  max_timeout_sec: ?       # Currently: No timeout

GET /channels:
  p95_latency_ms: ?        # Currently: No assertion
  p99_latency_ms: ?        # Currently: No assertion

GET /live_metadata:
  p95_latency_ms: ?        # Currently: No assertion
  p99_latency_ms: ?        # Currently: No assertion
```

### Polling Specifications
```yaml
waterfall_polling:
  interval_ms: ?           # Currently: Random/hardcoded
  max_retries: ?           # Currently: No limit
  backoff_strategy: ?      # Currently: None
  timeout_before_failure: ? # Currently: Infinite wait
  
status_200_no_data:
  max_duration_sec: ?      # How long can we get 200 before timeout?
  alert_threshold_sec: ?   # When to warn about no data?
```

### End-to-End Flow Timing
```yaml
live_flow:
  config_to_first_data_sec: ?     # Currently: No assertion
  acceptable_delay_sec: ?         # Currently: No check

historic_flow:
  config_to_completion_sec: ?     # Currently: No assertion
  max_playback_duration_sec: ?    # Currently: No limit
```

---

## 2️⃣ DATA QUALITY SPECIFICATIONS

### Waterfall Data Validation
```yaml
amplitude:
  expected_min_value: ?      # Currently: No validation
  expected_max_value: ?      # Currently: No validation
  outlier_threshold: ?       # Currently: No check
  noise_floor: ?            # Currently: No check
  
data_completeness:
  max_missing_data_percent: ?     # Currently: No check
  max_gap_between_rows_ms: ?      # Currently: No validation
  max_empty_sensors_per_row: ?    # Currently: No limit
  min_sensors_with_data: ?        # Currently: No minimum
  
data_consistency:
  max_timestamp_drift_ms: ?       # Currently: No check
  duplicate_tolerance_count: ?    # Currently: No check
  metadata_vs_data_tolerance: ?   # Currently: No validation
```

### Sensor Configuration Limits
```yaml
sensors:
  absolute_min: ?           # Currently: Accepts any value
  absolute_max: ?           # Currently: No limit
  range_minimum: ?          # Min sensors in single config (e.g., 10)
  range_maximum: ?          # Max sensors in single config (e.g., 1000)
  
  # VALIDATION NEEDED:
  # Currently code accepts: sensors_min=0, sensors_max=50
  # Is this correct? What are the real limits?
```

### Frequency Configuration Limits
```yaml
frequency:
  absolute_min_hz: ?        # Currently: Accepts negative!
  absolute_max_hz: ?        # Currently: No limit
  range_minimum_hz: ?       # Min frequency span
  range_maximum_hz: ?       # Max frequency span
  
prr_limits:
  min_samples_per_sec: ?    # Currently: No validation
  max_samples_per_sec: ?    # Currently: No validation
  
nyquist:
  enforcement: ?            # "hard_limit" or "warning"?
  safety_margin_percent: ?  # Currently: No margin
```

### NFFT Configuration
```yaml
nfft:
  valid_values: [?]         # Currently: Accepts any integer
  must_be_power_of_2: ?     # Currently: Warning only
  minimum: ?                # Currently: No minimum
  maximum: ?                # Currently: No maximum
  recommended_values: [?]   # Currently: No recommendation
```

### Canvas Configuration
```yaml
canvas:
  height_minimum: ?         # Currently: No validation
  height_maximum: ?         # Currently: No validation
  width_minimum: ?          # Currently: No validation
  width_maximum: ?          # Currently: No validation
```

---

## 3️⃣ ROI (REGION OF INTEREST) SPECIFICATIONS

### ROI Change Limits
```yaml
roi_adjustment:
  max_change_percent: ?     # CURRENTLY: 50% HARDCODED - NEED CONFIRMATION!
  max_shift_sensors: ?      # Currently: No limit
  max_changes_per_minute: ? # Currently: No limit
  cooldown_period_sec: ?    # Currently: No cooldown
  
  safety_checks:
    unsafe_threshold: ?     # When to block change?
    warning_threshold: ?    # When to warn?
    auto_reject_if: ?       # Conditions for auto-rejection
```

### ROI Validation Rules
```yaml
roi_validation:
  min_roi_size: ?           # Minimum sensors in ROI
  max_roi_size: ?           # Maximum sensors in ROI
  overlap_allowed: ?        # Can ROIs overlap?
  max_overlap_percent: ?    # If yes, how much?
  
  impact_on_live:
    disruption_duration_ms: ?     # How long does change take?
    data_loss_expected: ?         # Will we lose data during change?
    recovery_time_ms: ?           # Time to stabilize after change?
```

---

## 4️⃣ MONGODB SPECIFICATIONS

### Connection & Availability
```yaml
mongodb:
  connection_timeout_ms: ?   # Currently: Default driver timeout
  max_retries: ?            # Currently: No retry logic
  retry_backoff_ms: ?       # Currently: No backoff
  
  outage_handling:
    recovery_time_max_sec: ?      # Currently: No SLA
    failover_automatic: ?         # Currently: Unknown
    cache_during_outage: ?        # Currently: No caching
    
  query_performance:
    max_query_latency_ms: ?       # Currently: No limit
    max_documents_per_query: ?    # Currently: No limit
    index_scan_ratio_threshold: ? # Currently: No monitoring
```

### Data Lifecycle Rules
```yaml
recording_lifecycle:
  live_to_historical_threshold_hours: ?  # CURRENTLY: 1 HOUR HARDCODED - NEED CONFIRMATION!
  orphaned_recording_timeout_hours: ?    # Currently: No cleanup
  retention_policy_days: ?               # Currently: No policy
  
  state_transitions:
    live_duration_max_hours: ?           # Currently: No limit
    historical_accessible_for_days: ?    # Currently: Unknown
    archived_after_days: ?               # Currently: No archiving
```

---

## 5️⃣ RABBITMQ SPECIFICATIONS

### Message Delivery
```yaml
rabbitmq:
  command_timeout_ms: ?      # Currently: No timeout
  max_retries: ?            # Currently: No retry
  retry_interval_ms: ?      # Currently: No interval
  acknowledgment_required: ? # Currently: Unknown
  message_ttl_sec: ?        # Currently: No TTL
  
  queue_management:
    max_queue_size: ?       # Currently: No limit
    queue_full_behavior: ?  # "drop_oldest" / "reject_new" / "block"?
    dead_letter_queue: ?    # Currently: Not configured
```

### Command Execution Times
```yaml
commands:
  RegionOfInterestCommand:
    max_execution_time_ms: ?      # Currently: No timeout
    expected_completion_time_ms: ? # Currently: No expectation
    
  PauseCommand:
    max_execution_time_ms: ?      # Currently: No timeout
    
  ResumeCommand:
    max_execution_time_ms: ?      # Currently: No timeout
    
  priority_levels: ?               # Currently: No priority
```

---

## 6️⃣ ERROR HANDLING SPECIFICATIONS

### HTTP Status Code Semantics
```yaml
status_codes:
  200_no_data:
    max_duration_before_timeout_sec: ?   # Currently: Infinite
    is_this_normal: ?                    # Currently: Assumed yes
    
  201_with_data:
    must_have_data: ?                    # Currently: Assumed yes
    min_data_size: ?                     # Currently: No check
    
  208_already_reported:
    is_success_or_warning: ?             # Currently: Unknown
    retry_allowed: ?                     # Currently: Unknown
    
  400_bad_request:
    error_message_format: ?              # Currently: No standard
    retry_allowed: ?                     # Currently: Unknown
    
  404_not_found:
    when_task_not_found: ?               # Currently: Unknown
    cleanup_after_sec: ?                 # Currently: No cleanup
    
  503_service_unavailable:
    expected_recovery_time_sec: ?        # Currently: Unknown
    max_retries: ?                       # Currently: No retry
```

### Invalid Configuration Handling
```yaml
invalid_config:
  behavior: ?                # "reject" or "auto_fix"?
  
  out_of_range_values:
    handling: ?              # "reject" or "clamp_to_valid"?
    
  validation_errors:
    format: ?                # "detailed" or "generic"?
    include_suggestions: ?   # Currently: No suggestions
```

### Time Range Validation
```yaml
time_validation:
  start_greater_than_end:
    behavior: ?              # "reject" or "swap"?
    
  future_time:
    max_future_minutes: ?    # Currently: Accepts any future
    behavior: ?              # "reject" or "allow"?
    
  past_time:
    max_past_days: ?         # Currently: No limit
    behavior: ?              # "reject" or "allow"?
    
  historic_range:
    max_duration_hours: ?    # Currently: No limit
    min_duration_seconds: ?  # Currently: No minimum
```

### Task Lifecycle Management
```yaml
task_lifecycle:
  task_id_must_be_unique: ?  # Currently: Unknown
  
  duplicate_config:
    behavior: ?              # "replace" or "reject"?
    
  task_timeout:
    auto_cleanup_after_hours: ?  # Currently: No cleanup
    warning_after_hours: ?        # Currently: No warning
    
  max_concurrent_tasks: ?         # Currently: No limit
```

---

## 7️⃣ INFRASTRUCTURE FAILURE BEHAVIOR

### MongoDB Outage
```yaml
mongodb_down:
  api_status_code: ?         # Currently: Unknown
  continue_live_data: ?      # Currently: Unknown
  cache_locally: ?           # Currently: No
  user_notification: ?       # Currently: No
  recovery_behavior: ?       # Currently: Unknown
```

### RabbitMQ Outage
```yaml
rabbitmq_down:
  command_handling: ?        # "queue_locally" or "reject"?
  fallback_mechanism: ?      # Currently: None
  user_notification: ?       # Currently: No
  recovery_behavior: ?       # Currently: Unknown
```

### Baby Analyzer Failure
```yaml
baby_analyzer_crash:
  expected_behavior: ?       # Currently: Unknown
  auto_restart: ?           # Currently: Unknown
  max_restart_attempts: ?   # Currently: No limit
  recovery_time_sec: ?      # Currently: Unknown
  user_alert: ?             # Currently: No
```

---

## 8️⃣ KUBERNETES & INFRASTRUCTURE

### Pod Health Criteria
```yaml
pod_health:
  readiness_probe:
    endpoint: ?              # Currently: Not defined
    timeout_sec: ?          # Currently: Default
    success_threshold: ?    # Currently: Default
    
  liveness_probe:
    endpoint: ?             # Currently: Not defined
    timeout_sec: ?          # Currently: Default
    failure_threshold: ?    # Currently: Default
    
  restart_policy:
    max_restarts: ?         # Currently: No limit
    grace_period_sec: ?     # Currently: Default
```

### Service Level Agreement
```yaml
sla:
  uptime_percent: ?         # Currently: No SLA
  planned_downtime_hours_per_month: ?  # Currently: Unknown
  unplanned_downtime_tolerance_minutes: ? # Currently: Unknown
  
  rollback:
    trigger_conditions: ?   # Currently: Manual only
    automatic: ?           # Currently: No
```

### Resource Limits
```yaml
resources:
  cpu:
    request: ?              # Currently: Not defined
    limit: ?               # Currently: Not defined
    alert_threshold_percent: ?  # Currently: No alert
    
  memory:
    request: ?             # Currently: Not defined
    limit: ?              # Currently: Not defined
    oom_threshold_mb: ?   # Currently: No monitoring
    
  scaling:
    trigger_cpu_percent: ?  # Currently: No autoscale
    trigger_memory_percent: ? # Currently: No autoscale
    min_replicas: ?        # Currently: 1
    max_replicas: ?        # Currently: 1
```

---

## 9️⃣ SINGLECHANNEL VIEW SPECIFICATIONS

### Channel Mapping Rules
```yaml
singlechannel:
  channel_range:
    min: ?                  # Currently: No validation
    max: ?                  # Currently: No validation
    
  channel_validation:
    must_be_in_sensor_range: ?  # Currently: Unknown
    behavior_if_missing: ?       # Currently: Unknown
    
  display_mapping:
    valid_display_sensor_ids: [?]  # Currently: No validation
    max_offset: ?                   # Currently: No limit
    multiple_channels_per_display: ? # Currently: Unknown
```

---

## 🔟 LOAD TESTING SPECIFICATIONS

### Load Profiles
```yaml
load_testing:
  steady_state:
    concurrent_users: ?     # Currently: Not tested
    duration_hours: ?       # Currently: Not tested
    
  spike:
    baseline_users: ?       # Currently: Not tested
    spike_users: ?         # Currently: Not tested
    spike_duration_sec: ?  # Currently: Not tested
    
  ramp:
    start_users: ?         # Currently: Not tested
    end_users: ?          # Currently: Not tested
    ramp_duration_min: ?  # Currently: Not tested
    
  soak:
    users: ?              # Currently: Not tested
    duration_hours: ?     # Currently: Not tested
    memory_leak_threshold_percent_per_hour: ?  # Currently: Not monitored
```

### Performance Under Load
```yaml
degradation_thresholds:
  response_time_increase_percent: ?  # Currently: No threshold
  error_rate_percent: ?              # Currently: No threshold
  throughput_decrease_percent: ?     # Currently: No threshold
  
breaking_point:
  definition: ?           # Currently: Not defined
  recovery_required: ?    # Currently: Unknown
```

---

## 1️⃣1️⃣ SECURITY SPECIFICATIONS

### Authentication & Authorization
```yaml
security:
  authentication:
    required: ?            # Currently: No auth
    method: ?             # Currently: None
    token_expiry_hours: ? # Currently: N/A
    
  authorization:
    roles: [?]            # Currently: No roles
    endpoint_permissions: {} # Currently: No permissions
    
  rate_limiting:
    enabled: ?            # Currently: No
    requests_per_minute: ? # Currently: Unlimited
    burst_size: ?         # Currently: N/A
```

### Input Validation
```yaml
input_validation:
  max_request_size_mb: ?   # Currently: No limit
  sql_injection_protection: ? # Currently: Unknown
  xss_protection: ?        # Currently: Unknown
  command_injection_protection: ? # Currently: Unknown
  
  sanitization:
    special_characters: ?  # Currently: No sanitization
    encoding_validation: ? # Currently: No validation
```

---

## 1️⃣2️⃣ FIBER OPTICS DOMAIN SPECIFICATIONS

### Fiber Geometry Validation
```yaml
fiber_optics:
  fiber_length_meters:
    min: ?                 # Currently: No validation
    max: ?                 # Currently: No validation
    
  dx_spatial_resolution:
    min: ?                 # Currently: No validation
    max: ?                 # Currently: No validation
    
  fiber_start_meters:
    min: ?                 # Currently: No validation
    max: ?                 # Currently: No validation
    must_be_less_than_length: ? # Currently: Checked but no spec
    
  number_of_channels:
    min: ?                 # Currently: No validation
    max: ?                 # Currently: No validation
```

---

## 1️⃣3️⃣ RECORDING METADATA SPECIFICATIONS

### Required Fields
```yaml
metadata_validation:
  mandatory_fields: [?]     # Currently: No validation
  
  field_validation:
    site_id:
      format: ?            # Currently: No validation
      max_length: ?        # Currently: No limit
      
    recording_id:
      format: ?            # Currently: No validation
      uniqueness: ?        # Currently: Not enforced
      
    timestamp:
      format: ?            # Currently: yymmddHHMMSS
      timezone: ?          # Currently: Unknown
      
  default_values: {}       # Currently: No defaults defined
```

---

## 1️⃣4️⃣ LOGGING & MONITORING SPECIFICATIONS

### Log Levels
```yaml
logging:
  error_conditions: [?]     # Currently: Ad-hoc
  warning_conditions: [?]   # Currently: Ad-hoc
  info_content: [?]        # Currently: Ad-hoc
  debug_content: [?]       # Currently: Everything
  
  format:
    timestamp_format: ?    # Currently: Various
    structure: ?          # Currently: Unstructured
    correlation_id: ?     # Currently: None
```

### Metrics & Alerting
```yaml
monitoring:
  critical_metrics: [?]     # Currently: Not defined
  sampling_rate_sec: ?      # Currently: Unknown
  retention_days: ?         # Currently: Unknown
  
  alerts:
    thresholds: {}         # Currently: No alerts
    recipients: []         # Currently: No recipients
    escalation_policy: ?   # Currently: None
    severity_levels: [?]   # Currently: Not defined
```

---

## 📊 SUMMARY OF CRITICAL GAPS

### 🔴 **MOST CRITICAL (Blocking Testing)**
1. **API Response Time Thresholds** - Can't determine performance pass/fail
2. **Data Quality Limits** - Can't validate data integrity
3. **ROI Change Limit (50%)** - Hardcoded value needs validation
4. **Live/Historical Threshold (1 hour)** - Hardcoded value needs validation
5. **MongoDB/RabbitMQ Outage Behavior** - Unknown expected behavior

### 🟡 **HIGH PRIORITY (Affecting Test Quality)**
6. **Sensor/Frequency Ranges** - No validation limits
7. **Task Lifecycle Rules** - No cleanup/timeout specs
8. **Error Handling Semantics** - Unknown expected behaviors
9. **Load Testing Profiles** - No performance baselines
10. **Resource Limits** - No capacity planning

### 🟢 **MEDIUM PRIORITY (Nice to Have)**
11. **Security Requirements** - Currently no auth/authz
12. **Logging Standards** - Inconsistent logging
13. **Monitoring Metrics** - No defined KPIs
14. **Fiber Optics Validation** - Domain-specific rules

---

## 🎯 HOW TO USE THIS DOCUMENT

### For the Meeting:
1. **Go through each section** systematically
2. **Fill in the "?" marks** with actual values
3. **Mark items as N/A** if not applicable
4. **Prioritize** what needs immediate implementation

### For Implementation:
After getting the values, update these files:
```python
# 1. Update validators with thresholds
src/utils/validators.py

# 2. Add performance configs
config/settings.yaml

# 3. Update test assertions
tests/integration/api/*.py

# 4. Create new test fixtures
tests/conftest.py

# 5. Document in Xray
Jira Xray test cases
```

### Expected Outcome:
With these specs defined, every test will have:
- ✅ Clear pass/fail criteria
- ✅ Specific numeric thresholds
- ✅ Expected behavior definitions
- ✅ Timeout and retry logic
- ✅ Proper error handling

---

**Document Status:** Ready for Review  
**Total Missing Specs:** 200+  
**Critical Specs:** 50+  
**Implementation Effort:** ~2 weeks after specs defined
