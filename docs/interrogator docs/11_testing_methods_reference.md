# InterrogatorQA - Testing Methods Reference

**Source:** Confluence Page ID 2086961164  
**Extracted:** December 8, 2024

---

## Test Suite Categories - Essential Table

| **WHAT** | **Smoke** | **Long-term** | **Recoverability** | **Reliability** |
|----------|-----------|---------------|--------------------|-----------------||
| **Purpose** | Quick bring-up and sanity checks | Validate long-running stability | Validate recovery after crashes | Extended recovery with strict criteria |
| **Duration** | Minutes (<10) | Hours 24/48 | Minutes | Long / PF-driven |
| **Frequency** | Every commit (CI) | Daily/nightly | On-demand or nightly | Weekly |
| **Test File** | `test_smoke.py` | `test_longterm.py` | `test_recoverability.py` | `test_smoke.py` |
| **CLI** | `--suite smoke` | `--suite longterm` | `--suite recoverability` | `--suite reliability` |

---

## Running Tests

### Smoke Tests

```bash
python -m pytest .\tests\test_smoke.py --config effective_params.yaml --suite smoke -vv -s -rA --preclean --log-level=INFO
```

### Long-term Tests

```bash
python -m pytest .\tests\test_longterm.py --config effective_params.yaml --suite longterm -vv -s -rA --preclean --log-level=INFO --test-time 48H
```

### Recoverability Tests

```bash
python -m pytest .\tests\test_recoverability.py --config effective_params.yaml --suite recoverability -vv -s -rA --preclean --log-level=INFO
```

### Reliability Tests

```bash
python -m pytest .\tests\test_smoke.py --config effective_params.yaml --suite reliability -vv -s -rA --preclean --log-level=INFO
```

---

## Test Suite Details

### 1. Smoke Tests

**Purpose:** Quick validation of core system functionality

**Key Test Areas:**
- Service startup and basic health
- Player functionality and data playback
- Alert generation and collection
- Basic resource monitoring
- Queue performance validation

**Includes:**
- ServicesChecker and process monitoring
- RabbitMQ validation (queues, metrics, routing keys)
- Heartbeats and KeepAlive checks
- Critical messages monitoring
- Basic PRP and heatmap validation

### 2. Long-term Tests

**Purpose:** Validate system stability over extended periods

**Key Test Areas:**
- Memory leak detection
- Performance degradation monitoring
- Resource usage trending
- Heatmap generation over time
- Extended alert pattern validation

**Configuration Example:**

```yaml
longterm_test_time: 7200  # 2 hours in seconds
longterm_heatmap_expected_values:
  heatmap_type_1:
    period: 300  # seconds between heatmaps
    expected_size_kb: 1024
resource_monitoring:
  enabled: true
  interval: 60
```

### 3. Recoverability Tests

**Purpose:** Validate system recovery after failures

**Key Test Areas:**
- Data backup integrity
- System restore procedures
- Configuration recovery
- Database restoration
- Service reconfiguration

**Includes:**
- Terminating services and verifying return to running state
- Measuring recovery time
- Supervisor restart resilience
- Matrix process restart validation

### 4. Reliability Tests

**Purpose:** Extended recovery testing with strict thresholds

**Configuration Example:**

```yaml
reliability:
  service: "supervisor"
  restart_behavior:
    downtime_seconds: 30
    stabilization_seconds: 60
    when_fraction_of_test: 0.5
    clear_downtime_failures: true
```

---

## Example Test Code

### Cyclic Check Test

```python
@pytest.mark.xray("IQ-79")
def test_cyclic_check(self, orchestrator: Orchestrator, sv_cli: SvCli):
    """Validate continuous system health monitoring."""
    test_time = orchestrator.play_estimator.play_time_real
    cyclic_check(
        test_time=test_time,
        orchestrator=orchestrator,
        sv_cli=sv_cli,
        cyclic_checkers_manager=cyclic_checkers_manager,
        kill_player_after_timeout=False
    )
```

### Alert Pipeline Integration Test

```python
def test_alert_pipeline_integration(self, orchestrator: Orchestrator):
    """Test alert generation through collection pipeline."""
    # Generate alerts through algo mock
    orchestrator.am.alert_player.create_alert(class_id=61, distance_m=1000)

    # Verify collection through both drivers
    collector_alerts = orchestrator.collector_alerts_driver.get_all_alerts()
    externalizer_alerts = orchestrator.externalizer_alerts_driver.get_all_alerts()

    assert len(collector_alerts) > 0
    assert len(externalizer_alerts) > 0
```

### Service Restart Recovery Test

```python
def test_service_restart_recovery(self, orchestrator: Orchestrator):
    """Validate system recovery after service restart."""
    service = orchestrator.conf.get_reliability_service()
    downtime = orchestrator.conf.get_reliability_downtime(service)
    stabilization = orchestrator.conf.get_reliability_stabilization(service)

    reliability_tester = ReliabilityTester(orchestrator, service)
    recovery_success = reliability_tester.test_restart_recovery(
        downtime_seconds=downtime,
        stabilization_seconds=stabilization
    )
    assert recovery_success, "Service failed to recover properly"
```

---

## Mock & Stub Integration

### Algorithm Mock

```python
from libs.algo_mock.algo_mock import AlgoMock, AlertsPlayerParams

algo_mock = AlgoMock(algo_player_params=AlertsPlayerParams(8))
for alert_config in alerts_to_play:
    alert_data = algo_mock.alert_player.create_alert(
        class_id=alert_config['class_id'],
        distance_m=alert_config['distance_m']
    )
```

### Control Center Mock

```python
if conf.get_control_center_mock_enabled():
    control_center_mock = ControlCenterMock()
    control_center_mock.start_collecting()
```

### Mock Configuration (PF Criteria)

```yaml
control_center_mock: enabled
alerts_to_play:
  - {"class_id": 61, "distance_m": 4567}
  - {"class_id": 123, "distance_m": 5577}
```

---

## Best Practices

1. **Test Organization:** Group related tests in classes
2. **Configuration Management:** Use environment-specific config files
3. **Error Handling:** Implement comprehensive assertion messages
4. **Performance:** Run expensive tests in appropriate suites
