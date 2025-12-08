# Statement of Work (SOW)
## Interrogator Automation - Phase 1

**Version:** 1.0  
**Date:** December 8, 2024  
**Author:** Roy Avrahami, QA Team Lead  
**Duration:** 5-6 months

---

## Executive Summary

| # | Work Package | Duration | Owner |
|---|--------------|----------|-------|
| 1 | Data Path Mapping & Validation | 2 months | Roy |
| 2 | SVC Commands & Alerts Testing | 1 month | Roy |
| 3 | Failure Simulation & Resilience | 2-3 months | Roy |

---

## 1. Data Path Mapping & Validation

**Duration:** 2 months

### Goal

- Research all existing data flows in the Interrogator system
- Understand which paths are active per configuration/version
- Create a manifest-based approach to extract active paths from effective_params.yaml
- Identify which manual test scenarios can be automated and which cannot
- Build automated validation tests for critical data paths
- Enable version-specific testing based on configuration manifest

### Deliverables

| # | Deliverable | Due |
|---|-------------|-----|
| 1 | Data Path Inventory | Week 2 |
| 2 | Configuration Manifest Parser | Week 6 |
| 3 | Path Validation Tests | Week 8 |
| 4 | Automation Feasibility Report | Week 8 |

### Core Data Paths

| Path | Flow | Description |
|------|------|-------------|
| 1 | Digitizer → Preprocessor → Smart Recorder | PRP Recording |
| 2 | Digitizer → Preprocessor → Heatmap Recorder | Heatmaps |
| 3 | Digitizer → Preprocessor → ML Algo → Collector | Alerts |
| 4 | Digitizer → Preprocessor → Fiber Inspector | Fiber Health (OTDR) |
| 5 | Preprocessor → Baby Analyzer → Focus/UI | Live View |
| 6 | Collector → Externalizer → External Systems | Alert Distribution |

### Acceptance Criteria

- [ ] All 6 paths documented
- [ ] Manifest parser works with effective_params.yaml
- [ ] At least 3 paths with automated tests
- [ ] Clear report on what cannot be automated (with justification)

---

## 2. SVC Commands & Alerts Testing

**Duration:** 1 month

### Goal

- Document all available Supervisor CLI (SVC) commands
- Map each command to its expected system response and alerts
- Verify that executing SVC commands produces the correct alerts in MongoDB
- Verify that system state changes are reflected in RabbitMQ messages
- Build automated test suite for command execution and alert verification
- Enable NOC-related testing through SVC command automation

### Deliverables

| # | Deliverable | Due |
|---|-------------|-----|
| 1 | SVC Commands Inventory | Week 2 |
| 2 | Command → Alert Mapping | Week 2 |
| 3 | SVC Test Suite | Week 4 |

### Commands to Test

| Category | Example Commands |
|----------|------------------|
| Service Control | start, stop, restart service |
| Status Queries | get_status, list_services |
| System Operations | shutdown, reload_config |
| BIT Triggers | run_bit, get_bit_status |

### Alert Verification

| Action | Expected Result |
|--------|-----------------|
| Stop critical service | Service down alert in MongoDB |
| Restart service | Recovery alert / KeepAlive update |
| Kill process | ProcessCrash message in RabbitMQ |
| BIT failure | Alert in bit_status.log |

### Acceptance Criteria

- [ ] All SVC commands documented
- [ ] At least 10 commands with automated tests
- [ ] Alert verification in MongoDB and RabbitMQ

---

## 3. Failure Simulation & Resilience

**Duration:** 2-3 months

### Goal

- Build a failure simulation framework (chaos engineering approach)
- Simulate fiber issues and verify Fiber Inspector detects and reports correctly
- Simulate service crashes and verify Supervisor recovers services automatically
- Simulate infrastructure failures (DB, message queue, disk) and verify graceful handling
- Measure recovery times and compare against defined thresholds
- Verify system generates correct alerts for each failure type
- Enable resilience testing as part of regression/release validation

### Deliverables

| # | Deliverable | Due |
|---|-------------|-----|
| 1 | Failure Simulation Framework | Week 4 |
| 2 | Fiber Issue Test Suite | Week 6 |
| 3 | Service Crash Test Suite | Week 8 |
| 4 | Infrastructure Failure Tests | Week 10 |

### Failure Scenarios

#### Service Failures
| Scenario | Expected Response |
|----------|-------------------|
| Process crash (kill -9) | Auto-recovery within 30s |
| Service timeout | Restart by Supervisor |
| Memory exhaustion | Graceful degradation |

#### Fiber Issues
| Scenario | Expected Response |
|----------|-------------------|
| Fiber cut | fiber_cut alert |
| Attenuation change | visibility_change alert |
| OTDR anomaly | Detection + notification |

#### Infrastructure
| Scenario | Expected Response |
|----------|-------------------|
| RabbitMQ down | Queue recovery |
| MongoDB disconnect | Reconnection |
| Disk full | Graceful degradation |

### Acceptance Criteria

- [ ] At least 5 crash scenarios with recovery validation
- [ ] Fiber Inspector tests for 4 failure types
- [ ] Recovery time measured against defined thresholds

---

## Timeline

```
Month 1-2: WP1 - Data Path Mapping
Month 2:   WP2 - SVC Commands (parallel)
Month 3-5: WP3 - Failure Simulation
```

---

## Dependencies

| Item | Owner | Status |
|------|-------|--------|
| Repository access (nc_pz, interrogatorqa) | DevOps | Pending |
| Test environment | Interrogator team | Available |
| Knowledge transfer sessions | Inbar | To schedule |

---

## Resources

| Role | Allocation |
|------|------------|
| Roy Avrahami | 30-40% |
| Interrogator Team Support | 5-10h/month |

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Data paths documented | 100% |
| Paths with automated tests | ≥50% |
| SVC commands tested | ≥10 |
| Failure scenarios automated | ≥10 |

---

## Approval

| Role | Name | Date |
|------|------|------|
| QA Team Lead | Roy Avrahami | |
| QA Manager | Ronen | |
| Interrogator Team Lead | Inbar | |

---

*Phase 2 (CI/CD, Multi-Vertical) to be defined separately after Phase 1 completion.*
