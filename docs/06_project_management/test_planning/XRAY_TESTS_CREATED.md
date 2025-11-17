# Xray Tests Created - Kubernetes Pod Resilience
================================================

**Date:** 2025-11-08  
**Status:** ✅ All 30 tests created successfully  
**Folder ID:** 68d91b9f681e183ea2e83e16

---

## 📊 Summary

**Total Tests Created:** 30  
**Success Rate:** 100% (30/30)  
**Failed:** 0

---

## 📋 Test Mapping

### MongoDB Pod Resilience (6 tests)

| Test ID | Summary | Priority | URL |
|---------|---------|----------|-----|
| **PZ-14715** | MongoDB Pod Deletion and Recreation | Highest | [View](https://prismaphotonics.atlassian.net/browse/PZ-14715) |
| **PZ-14716** | MongoDB Scale Down to 0 Replicas | Highest | [View](https://prismaphotonics.atlassian.net/browse/PZ-14716) |
| **PZ-14717** | MongoDB Pod Restart During Job Creation | High | [View](https://prismaphotonics.atlassian.net/browse/PZ-14717) |
| **PZ-14718** | MongoDB Outage Graceful Degradation | Highest | [View](https://prismaphotonics.atlassian.net/browse/PZ-14718) |
| **PZ-14719** | MongoDB Recovery After Outage | Highest | [View](https://prismaphotonics.atlassian.net/browse/PZ-14719) |
| **PZ-14720** | MongoDB Pod Status Monitoring | Medium | [View](https://prismaphotonics.atlassian.net/browse/PZ-14720) |

### RabbitMQ Pod Resilience (6 tests)

| Test ID | Summary | Priority | URL |
|---------|---------|----------|-----|
| **PZ-14721** | RabbitMQ Pod Deletion and Recreation | Highest | [View](https://prismaphotonics.atlassian.net/browse/PZ-14721) |
| **PZ-14722** | RabbitMQ Scale Down to 0 Replicas | Highest | [View](https://prismaphotonics.atlassian.net/browse/PZ-14722) |
| **PZ-14723** | RabbitMQ Pod Restart During Operations | High | [View](https://prismaphotonics.atlassian.net/browse/PZ-14723) |
| **PZ-14724** | RabbitMQ Outage Graceful Degradation | Highest | [View](https://prismaphotonics.atlassian.net/browse/PZ-14724) |
| **PZ-14725** | RabbitMQ Recovery After Outage | Highest | [View](https://prismaphotonics.atlassian.net/browse/PZ-14725) |
| **PZ-14726** | RabbitMQ Pod Status Monitoring | Medium | [View](https://prismaphotonics.atlassian.net/browse/PZ-14726) |

### Focus Server Pod Resilience (6 tests)

| Test ID | Summary | Priority | URL |
|---------|---------|----------|-----|
| **PZ-14727** | Focus Server Pod Deletion and Recreation | Highest | [View](https://prismaphotonics.atlassian.net/browse/PZ-14727) |
| **PZ-14728** | Focus Server Scale Down to 0 Replicas | Highest | [View](https://prismaphotonics.atlassian.net/browse/PZ-14728) |
| **PZ-14729** | Focus Server Pod Restart During Job Creation | High | [View](https://prismaphotonics.atlassian.net/browse/PZ-14729) |
| **PZ-14730** | Focus Server Outage Graceful Degradation | Highest | [View](https://prismaphotonics.atlassian.net/browse/PZ-14730) |
| **PZ-14731** | Focus Server Recovery After Outage | Highest | [View](https://prismaphotonics.atlassian.net/browse/PZ-14731) |
| **PZ-14732** | Focus Server Pod Status Monitoring | Medium | [View](https://prismaphotonics.atlassian.net/browse/PZ-14732) |

### SEGY Recorder Pod Resilience (5 tests)

| Test ID | Summary | Priority | URL |
|---------|---------|----------|-----|
| **PZ-14733** | SEGY Recorder Pod Deletion and Recreation | High | [View](https://prismaphotonics.atlassian.net/browse/PZ-14733) |
| **PZ-14734** | SEGY Recorder Scale Down to 0 Replicas | High | [View](https://prismaphotonics.atlassian.net/browse/PZ-14734) |
| **PZ-14735** | SEGY Recorder Pod Restart During Recording | Medium | [View](https://prismaphotonics.atlassian.net/browse/PZ-14735) |
| **PZ-14736** | SEGY Recorder Outage Behavior | Medium | [View](https://prismaphotonics.atlassian.net/browse/PZ-14736) |
| **PZ-14737** | SEGY Recorder Recovery After Outage | High | [View](https://prismaphotonics.atlassian.net/browse/PZ-14737) |

### Multiple Pods Resilience (4 tests)

| Test ID | Summary | Priority | URL |
|---------|---------|----------|-----|
| **PZ-14738** | MongoDB + RabbitMQ Down Simultaneously | High | [View](https://prismaphotonics.atlassian.net/browse/PZ-14738) |
| **PZ-14739** | MongoDB + Focus Server Down Simultaneously | High | [View](https://prismaphotonics.atlassian.net/browse/PZ-14739) |
| **PZ-14740** | RabbitMQ + Focus Server Down Simultaneously | High | [View](https://prismaphotonics.atlassian.net/browse/PZ-14740) |
| **PZ-14741** | Focus Server + SEGY Recorder Down Simultaneously | Medium | [View](https://prismaphotonics.atlassian.net/browse/PZ-14741) |

### Pod Recovery Scenarios (3 tests)

| Test ID | Summary | Priority | URL |
|---------|---------|----------|-----|
| **PZ-14742** | Recovery Order Validation | High | [View](https://prismaphotonics.atlassian.net/browse/PZ-14742) |
| **PZ-14743** | Cascading Recovery Scenarios | Medium | [View](https://prismaphotonics.atlassian.net/browse/PZ-14743) |
| **PZ-14744** | Recovery Time Measurement | Medium | [View](https://prismaphotonics.atlassian.net/browse/PZ-14744) |

---

## 🔄 Next Steps

### 1. Update Test Files with Real Xray IDs

Update all test files to use the real Xray test IDs instead of placeholders:

- `tests/infrastructure/resilience/test_mongodb_pod_resilience.py`
- `tests/infrastructure/resilience/test_rabbitmq_pod_resilience.py`
- `tests/infrastructure/resilience/test_focus_server_pod_resilience.py`
- `tests/infrastructure/resilience/test_segy_recorder_pod_resilience.py`
- `tests/infrastructure/resilience/test_multiple_pods_resilience.py`
- `tests/infrastructure/resilience/test_pod_recovery_scenarios.py`

**Mapping:**
- PZ-TBD-001 → PZ-14715
- PZ-TBD-002 → PZ-14716
- PZ-TBD-003 → PZ-14717
- ... (and so on)

### 2. Assign Tests to Xray Folder

**Note:** The tests were created but folder assignment requires Xray API access.  
**Folder ID:** `68d91b9f681e183ea2e83e16`

To assign tests to folder manually:
1. Go to Jira → Test Repository
2. Navigate to folder `68d91b9f681e183ea2e83e16`
3. Move tests to this folder

Or use Xray REST API:
```bash
# Example (requires Xray API credentials)
curl -X POST "https://xray.cloud.getxray.app/api/v1/test/{test_key}/folder/{folder_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Link Tests to Requirements

Link tests to requirement:
- **PZ-13756** (Infrastructure Resilience)

### 4. Verify Test Details

Verify each test has:
- ✅ Summary
- ✅ Description with Objective, Steps, Expected Results
- ✅ Priority
- ✅ Labels/Components
- ✅ Automation Status
- ✅ Test Function reference

---

## 📝 Script Used

**Script:** `scripts/jira/create_xray_resilience_tests.py`

**Usage:**
```bash
# Dry run (preview)
python scripts/jira/create_xray_resilience_tests.py --dry-run

# Create all tests
python scripts/jira/create_xray_resilience_tests.py --folder-id 68d91b9f681e183ea2e83e16
```

---

## ✅ Completion Status

- [x] All 30 tests created in Jira Xray
- [x] Test summaries and descriptions added
- [x] Priorities assigned
- [x] Labels and components configured
- [ ] Tests assigned to folder (requires Xray API or manual)
- [ ] Tests linked to requirements (PZ-13756)
- [ ] Test files updated with real Xray IDs

---

**Created:** 2025-11-08  
**Author:** Automation Script  
**Related:** PZ-13756 (Infrastructure Resilience)

