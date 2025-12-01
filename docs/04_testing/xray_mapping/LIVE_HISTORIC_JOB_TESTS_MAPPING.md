# 🔗 Live & Historic Job Tests - Xray Mapping

**Created:** November 30, 2025  
**Author:** Roy Avrahami (via Cursor Agent)  
**Total Tests Created:** 16

---

## 📊 Summary

| Category | Tests Created | Jira Key Range |
|----------|---------------|----------------|
| **Live Job Tests** | 7 | PZ-15234 → PZ-15240 |
| **Historic Job Tests** | 9 | PZ-15241 → PZ-15249 |
| **Total** | **16** | |

---

## 🔴 Live Job Tests (`test_live_load.py`)

| Jira Key | Test Function | Description |
|----------|---------------|-------------|
| **PZ-15234** | `test_single_live_job` | Single Live Job Complete Flow |
| **PZ-15235** | `test_live_job_timing` | Job Timing Meets SLA |
| **PZ-15236** | `test_concurrent_live_jobs` | Multiple Concurrent Jobs |
| **PZ-15237** | `test_live_retry_behavior` | Retry Behavior (gRPC Connection) |
| **PZ-15238** | `test_heavy_channel_live` | Heavy Channel Load (500 Channels) |
| **PZ-15239** | `test_sustained_live_load` | Sustained Load Test |
| **PZ-15240** | `test_max_concurrent_live` | Maximum Concurrent Jobs Stress |

### Test Classes

- `TestLiveJobLoad` - Basic Live job tests (PZ-15234 to PZ-15237)
- `TestLiveHeavyLoad` - Heavy load tests (PZ-15238, PZ-15239)
- `TestLiveStress` - Stress tests (PZ-15240)

---

## 📼 Historic Job Tests (`test_historic_load.py`)

| Jira Key | Test Function | Description |
|----------|---------------|-------------|
| **PZ-15241** | `test_single_historic_job` | Single Historic Job Complete Flow |
| **PZ-15242** | `test_historic_job_timing` | Job Timing Meets SLA |
| **PZ-15243** | `test_concurrent_historic_jobs` | Multiple Concurrent Jobs |
| **PZ-15244** | `test_historic_retry_behavior` | Retry Behavior |
| **PZ-15245** | `test_heavy_channel_historic` | Heavy Channel Load (500 Channels) |
| **PZ-15246** | `test_sustained_historic_load` | Sustained Load Test |
| **PZ-15247** | `test_max_concurrent_historic` | Maximum Concurrent Jobs Stress |
| **PZ-15248** | `test_recording_availability` | Recording Availability Check |
| **PZ-15249** | `test_historic_playback_complete` | Playback Runs to Completion |

### Test Classes

- `TestHistoricJobLoad` - Basic Historic job tests (PZ-15241 to PZ-15244)
- `TestHistoricHeavyLoad` - Heavy load tests (PZ-15245, PZ-15246)
- `TestHistoricStress` - Stress tests (PZ-15247)
- `TestHistoricSpecific` - Historic-specific tests (PZ-15248, PZ-15249)

---

## 🏃 Running the Tests

### All Live Tests
```bash
pytest be_focus_server_tests/load/test_live_load.py -v --env staging
```

### All Historic Tests
```bash
pytest be_focus_server_tests/load/test_historic_load.py -v --env staging
```

### By Marker
```bash
# Live only
pytest -m "live and job_load" -v --env staging

# Historic only
pytest -m "historic and job_load" -v --env staging

# All job load tests
pytest -m "job_load" -v --env staging
```

### By Xray Key
```bash
pytest -m "xray" --xray-key PZ-15234 -v --env staging
```

---

## 📝 Jira Links

- [PZ-15234](https://prismaphotonics.atlassian.net/browse/PZ-15234) - Live Single Job
- [PZ-15235](https://prismaphotonics.atlassian.net/browse/PZ-15235) - Live Timing SLA
- [PZ-15236](https://prismaphotonics.atlassian.net/browse/PZ-15236) - Live Concurrent
- [PZ-15237](https://prismaphotonics.atlassian.net/browse/PZ-15237) - Live Retry Behavior
- [PZ-15238](https://prismaphotonics.atlassian.net/browse/PZ-15238) - Live Heavy Channel
- [PZ-15239](https://prismaphotonics.atlassian.net/browse/PZ-15239) - Live Sustained
- [PZ-15240](https://prismaphotonics.atlassian.net/browse/PZ-15240) - Live Max Concurrent
- [PZ-15241](https://prismaphotonics.atlassian.net/browse/PZ-15241) - Historic Single Job
- [PZ-15242](https://prismaphotonics.atlassian.net/browse/PZ-15242) - Historic Timing SLA
- [PZ-15243](https://prismaphotonics.atlassian.net/browse/PZ-15243) - Historic Concurrent
- [PZ-15244](https://prismaphotonics.atlassian.net/browse/PZ-15244) - Historic Retry
- [PZ-15245](https://prismaphotonics.atlassian.net/browse/PZ-15245) - Historic Heavy Channel
- [PZ-15246](https://prismaphotonics.atlassian.net/browse/PZ-15246) - Historic Sustained
- [PZ-15247](https://prismaphotonics.atlassian.net/browse/PZ-15247) - Historic Max Concurrent
- [PZ-15248](https://prismaphotonics.atlassian.net/browse/PZ-15248) - Recording Availability
- [PZ-15249](https://prismaphotonics.atlassian.net/browse/PZ-15249) - Playback Complete

---

## 🔄 Old → New Key Mapping

For reference, here's the mapping from the placeholder keys to the real Jira keys:

| Old Placeholder | New Jira Key |
|-----------------|--------------|
| PZ-LOAD-200 | **PZ-15234** |
| PZ-LOAD-201 | **PZ-15235** |
| PZ-LOAD-202 | **PZ-15236** |
| PZ-LOAD-203 | **PZ-15237** |
| PZ-LOAD-210 | **PZ-15238** |
| PZ-LOAD-211 | **PZ-15239** |
| PZ-LOAD-220 | **PZ-15240** |
| PZ-LOAD-300 | **PZ-15241** |
| PZ-LOAD-301 | **PZ-15242** |
| PZ-LOAD-302 | **PZ-15243** |
| PZ-LOAD-303 | **PZ-15244** |
| PZ-LOAD-310 | **PZ-15245** |
| PZ-LOAD-311 | **PZ-15246** |
| PZ-LOAD-320 | **PZ-15247** |
| PZ-LOAD-330 | **PZ-15248** |
| PZ-LOAD-331 | **PZ-15249** |

