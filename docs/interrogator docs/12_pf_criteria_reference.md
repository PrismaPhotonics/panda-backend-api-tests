# PF Criteria (Pass/Fail) Reference

**Source:** Confluence Page ID 2097184772  
**Extracted:** December 8, 2024

---

## Overview

PF criteria YAML files define validation thresholds used by the InterrogatorQA test suites.  
Location: `interrogatorqa/tests/*_PF_criteria.yaml`

---

## Common Structure and Fields

### Supervisor

```yaml
supervisor:
  restart_at_test_setup: true   # Stop and start Supervisor at test setup
  kill_after_test: true         # Stop/terminate Supervisor during teardown
  service_states_exceptions:    # Override default "running" expectation
    service_name:
      - allowed_state_1
      - allowed_state_2
```

### Telegraf

```yaml
telegraf:
  type: service              # 'service' or 'process'
  restart_at_test_setup: true
  kill_after_test: true
  ignore_errors:             # Regex patterns for expected/ignored errors
    - "pattern1"
    - "pattern2"
```

### Timing

```yaml
startup_delay: 30              # Seconds after Supervisor start
telegraf_start_delay: 10       # Additional delay for Telegraf
cyclic_tests_run_time: 300     # Seconds to run cyclic checkers
```

---

## Alerts Configuration

### alerts_to_play

```yaml
alerts_to_play:
  - class_id: 61
    distance_m: 4567
  - class_id: 123
    distance_m: 5577
```

### alerts_to_detect

```yaml
alerts_to_detect:
  - class_id: 61
    algorun_id: "algo_v1"
    creation_time_tolerance: [0, 60]    # seconds relative to PRP start
    alert_cycle: [5, 15]                # seconds between alerts
    externalizer_alert_cycle: [5, 15]
    birth_location_m: [1000, 5000]
    distance_m: [4000, 5000]

allow_unexpected: 0  # Max unexpected alerts allowed (0 = any fails)
```

---

## Queue Monitoring

```yaml
queues_monitoring:
  queue_stats:
    queue_name:
      average_publish_rate_per_minute: [min, max]
      maximum_silence_time: 30           # Max seconds with no publishing
      maximum_buffer_size: 1000          # Max in-queue messages
  
  queues_to_ignore:
    - test_queue_1
    - test_queue_2
  
  unexpected_queues_wildcards:
    - "pattern.*"                        # Regex patterns
  
  defaults:                              # Default thresholds
    average_publish_rate_per_minute: [10, 100]
    maximum_silence_time: 60
    maximum_buffer_size: 500
```

---

## Cyclic Checkers

```yaml
cyclic_checkers:
  critical_messages: enabled
  keep_alive: enabled
  rabbit_queues: enabled
  services: enabled
  heartbeats: enabled
  prp_recording: enabled         # Only for longterm tests

cyclic_checkers_fail_fast: true  # Abort on first failure
```

---

## Heartbeats & Keep-Alive

```yaml
heartbeats_acceptable_range: [5, 15]  # [min_sec, max_sec]

keep_alive_checker:
  minimum_keep_alive_per_minute: 4
  extended_warning_limit_per_minute: 2
```

---

## Recovery Monitor

```yaml
recovery_monitor:
  enabled: true
  max_dead_proc_allowed: 0
  short_recover_time: 30          # Normal recovery (seconds)
  long_recovery_time: 120         # Complex scenarios (seconds)
  ignore_processes:
    - player
    - storage_stream_migrator
```

---

## Resource Monitoring

```yaml
resource_monitoring:
  enabled: true
  interval: 6                     # Sampling interval (seconds)
  
  cpu:
    percent_overall:
      max: 90
      avg: 70
    percent_per_core:
      max: 95
      avg: 80
  
  memory:
    percent_used:
      max: 85
      avg: 70
  
  swap:
    percent_used:
      max: 50
      avg: 30
  
  disk:
    percent_used:
      max: 90
      avg: 70
  
  gpu:
    utilization.gpu_percent:
      max: 95
      avg: 70
    utilization.memory_percent:
      max: 90
      avg: 70
    memory.percent_used:
      max: 90
      avg: 70
    temperature_celsius:
      max: 85
      avg: 70
    power_usage_watts:
      max: 300
      avg: 200
  
  allowed_range_limits:
    allowed_range_differences:
      cpu_range_difference: 20
      memory_range_difference: 15
    cpu_out_of_range_percentage: 5.0
    memory_out_of_range_percentage: 5.0
  
  peak_limits:
    relative_change_threshold: 0.2
    max_cpu_peaks: 10
    max_memory_peaks: 5
```

---

## Reliability Configuration

```yaml
reliability:
  service: "rabbit"                    # Component under test
  restart_behavior:
    trigger: true                      # Framework triggers restart
    when_fraction_of_test: 0.5         # Fraction of test duration
    downtime_seconds: 30               # Enforced STOP period
    stabilization_seconds: 60          # Grace period after up
    trigger_after_seconds: null        # Absolute time (overrides fraction)
    clear_downtime_failures: true      # Ignore downtime-induced failures
```

---

## Other Settings

```yaml
# Service states override
service_states_exceptions:
  service_name:
    required: ["running"]              # Must be seen at least once
    allowed: ["running", "restarting"] # Accepted states

# Heatmap validation
expected_heatmap_recordings: ${PRISMA_TEST_DATA}\heatmaps_ref
heatmaps:
  publish_rate:
    heatmap_type_1:
      tolerance: 0.1
  individual_tolerance_per_heatmap: true
  allow_missing_queues:
    enabled: true
    queues: ["optional_heatmap"]

# Control Center mock
control_center_mock: enabled

# BIT verification
bit_test_verification: enabled

# PRP comparison
expected_prp_path: ${PRISMA_TEST_DATA}\expected_uuid

# Player configuration
player:
  largs: ${PRP_PATH}
  playrate: 1.0
  sv_delay: 5
  sv_eoj_key: "EndOfJob"
  sv_quit_when_eoj: true
  thqueue: "target_queue"
```

---

## Suite-Specific Behaviors

### Smoke
- Shorter run time
- `rabbit_queues` cyclic checker disabled
- Post-run average publish rate validation
- Shorter resource monitoring interval (6s)

### Longterm
- `aggregate_snapshots` for background data collection
- `alerts_silence_phase` for reduced alerting periods
- Extended heatmap validation
- Full resource monitoring

### Reliability
- Extends Smoke PF criteria
- `rabbit_queues` enabled with downtime exclusion
- Automatic subtraction of broker downtime

### Recoverability
- Inherits Smoke PF config
- All cyclic checkers disabled
- Focus on `recovery_monitor` only

---

## File Locations

| Suite | File |
|-------|------|
| Smoke Power | `smoke_power_PF_criteria.yaml` |
| Smoke Flow | `smoke_flow_PF_criteria.yaml` |
| Longterm Power | `longterm_power_PF_criteria.yaml` |
| Reliability Power | `reliability_power_PF_criteria.yaml` |
| Recoverability Power | `recoverability_power_PF_criteria.yaml` |
