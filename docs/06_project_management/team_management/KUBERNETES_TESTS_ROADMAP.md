# Kubernetes Tests Roadmap

**Created:** 2025-11-04  
**Owner:** QA Team Lead  
**Purpose:** Add Kubernetes-focused tests to Focus Server BE tests

---

## 📋 Overview

### Existing Tests

**Location:** `tests/infrastructure/test_k8s_job_lifecycle.py`

**Current Coverage:**
- ✅ Job Creation → Pod Spawn
- ✅ Resource Allocation (CPU/Memory)
- ✅ Port Exposure and Service Discovery
- ✅ Job Cancellation and Cleanup
- ✅ Observability (Logs, Events, Metrics)

### Tests to Add

**Total:** 6 new test categories

---

## 🎯 New Test Categories

### 1. Pod Health Checks

**Ticket:** `PZ-XXXX` - K8s Pod Health Monitoring

**Location:** `tests/infrastructure/test_k8s_pod_health.py`

**Tests:**
1. **test_pod_liveness_probe**
   - Validates: Pod liveness probe configuration
   - Checks: Probe settings, failure handling

2. **test_pod_readiness_probe**
   - Validates: Pod readiness probe configuration
   - Checks: Probe settings, startup behavior

3. **test_pod_startup_probe**
   - Validates: Pod startup probe configuration
   - Checks: Probe settings, initial delay

4. **test_pod_restart_policy**
   - Validates: Pod restart policy
   - Checks: Always, OnFailure, Never policies

5. **test_pod_health_after_failures**
   - Validates: Pod recovery after failures
   - Checks: Restart behavior, health recovery

**Priority:** 🔴 High

**Estimated Effort:** 5 Story Points

---

### 2. Resource Management

**Ticket:** `PZ-XXXX` - K8s Resource Management Tests

**Location:** `tests/infrastructure/test_k8s_resources.py`

**Tests:**
1. **test_cpu_requests_limits**
   - Validates: CPU requests and limits
   - Checks: Resource configuration, enforcement

2. **test_memory_requests_limits**
   - Validates: Memory requests and limits
   - Checks: Resource configuration, enforcement

3. **test_resource_quotas**
   - Validates: Resource quotas at namespace level
   - Checks: Quota enforcement, limit compliance

4. **test_resource_constraints**
   - Validates: Resource constraints behavior
   - Checks: OOMKilled scenarios, throttling

5. **test_oom_killed_scenario**
   - Validates: OOMKilled pod behavior
   - Checks: Pod termination, restart behavior

**Priority:** 🔴 High

**Estimated Effort:** 5 Story Points

---

### 3. Deployment Strategy

**Ticket:** `PZ-XXXX` - K8s Deployment Strategy Tests

**Location:** `tests/infrastructure/test_k8s_deployment.py`

**Tests:**
1. **test_rolling_update_strategy**
   - Validates: Rolling update deployment
   - Checks: Update process, zero downtime

2. **test_blue_green_deployment**
   - Validates: Blue-Green deployment strategy
   - Checks: Traffic switching, rollback

3. **test_canary_deployment**
   - Validates: Canary deployment strategy
   - Checks: Gradual rollout, traffic splitting

4. **test_deployment_rollback**
   - Validates: Deployment rollback functionality
   - Checks: Rollback process, version restoration

5. **test_deployment_health_during_updates**
   - Validates: Deployment health during updates
   - Checks: Service availability, pod health

**Priority:** 🟡 Medium

**Estimated Effort:** 8 Story Points

---

### 4. Service Discovery

**Ticket:** `PZ-XXXX` - K8s Service Discovery Tests

**Location:** `tests/infrastructure/test_k8s_service_discovery.py`

**Tests:**
1. **test_service_creation_and_exposure**
   - Validates: Service creation and exposure
   - Checks: Service type, ports, selectors

2. **test_endpoint_resolution**
   - Validates: Endpoint resolution
   - Checks: Endpoint creation, pod matching

3. **test_service_to_pod_communication**
   - Validates: Service-to-Pod communication
   - Checks: Network connectivity, routing

4. **test_dns_resolution**
   - Validates: DNS resolution for services
   - Checks: Service DNS names, resolution

5. **test_load_balancing**
   - Validates: Load balancing behavior
   - Checks: Traffic distribution, pod selection

**Priority:** 🟡 Medium

**Estimated Effort:** 5 Story Points

---

### 5. Configuration Management

**Ticket:** `PZ-XXXX` - K8s Configuration Management Tests

**Location:** `tests/infrastructure/test_k8s_config.py`

**Tests:**
1. **test_configmap_creation_and_usage**
   - Validates: ConfigMap creation and usage
   - Checks: ConfigMap data, pod mounting

2. **test_secrets_management**
   - Validates: Secrets management
   - Checks: Secret creation, pod mounting, encryption

3. **test_environment_variables_injection**
   - Validates: Environment variables injection
   - Checks: Env vars from ConfigMap/Secrets

4. **test_configuration_updates**
   - Validates: Configuration updates
   - Checks: Hot reload, pod restart behavior

5. **test_configuration_rollback**
   - Validates: Configuration rollback
   - Checks: Version restoration, consistency

**Priority:** 🟢 Low

**Estimated Effort:** 5 Story Points

---

### 6. Resilience Tests

**Ticket:** `PZ-XXXX` - K8s Resilience Tests

**Location:** `tests/infrastructure/test_k8s_resilience.py`

**Tests:**
1. **test_pod_disruption_budget**
   - Validates: Pod Disruption Budget (PDB)
   - Checks: PDB enforcement, pod eviction limits

2. **test_node_failure_handling**
   - Validates: Node failure handling
   - Checks: Pod rescheduling, service continuity

3. **test_network_partition_handling**
   - Validates: Network partition handling
   - Checks: Pod isolation, communication recovery

4. **test_storage_failure_handling**
   - Validates: Storage failure handling
   - Checks: PVC behavior, data persistence

5. **test_autoscaling_behavior**
   - Validates: Horizontal Pod Autoscaling (HPA)
   - Checks: Scaling triggers, pod count adjustment

**Priority:** 🔴 High

**Estimated Effort:** 8 Story Points

---

## 📅 Priority Order and Sprint Planning

### Sprint 1 (High Priority)

**Goal:** Add critical tests

1. **Pod Health Checks** (5 Story Points)
   - ✅ `test_k8s_pod_health.py`
   - ✅ 5 tests

2. **Resource Management** (5 Story Points)
   - ✅ `test_k8s_resources.py`
   - ✅ 5 tests

**Total:** 10 Story Points

---

### Sprint 2 (High Priority Continued)

**Goal:** Add Resilience tests

1. **Resilience Tests** (8 Story Points)
   - ✅ `test_k8s_resilience.py`
   - ✅ 5 tests

**Total:** 8 Story Points

---

### Sprint 3 (Medium Priority)

**Goal:** Add Deployment and Service Discovery tests

1. **Service Discovery** (5 Story Points)
   - ✅ `test_k8s_service_discovery.py`
   - ✅ 5 tests

2. **Deployment Strategy** (8 Story Points)
   - ✅ `test_k8s_deployment.py`
   - ✅ 5 tests

**Total:** 13 Story Points

---

### Sprint 4 (Low Priority)

**Goal:** Add Configuration Management tests

1. **Configuration Management** (5 Story Points)
   - ✅ `test_k8s_config.py`
   - ✅ 5 tests

**Total:** 5 Story Points

---

## 📊 Summary

| Category | Priority | Story Points | Tests | Sprint |
|----------|----------|--------------|-------|--------|
| Pod Health Checks | 🔴 High | 5 | 5 | Sprint 1 |
| Resource Management | 🔴 High | 5 | 5 | Sprint 1 |
| Resilience Tests | 🔴 High | 8 | 5 | Sprint 2 |
| Service Discovery | 🟡 Medium | 5 | 5 | Sprint 3 |
| Deployment Strategy | 🟡 Medium | 8 | 5 | Sprint 3 |
| Configuration Management | 🟢 Low | 5 | 5 | Sprint 4 |
| **Total** | - | **36** | **30** | **4 Sprints** |

---

## 🛠️ Template for New K8s Test

```python
"""
Integration Tests - Kubernetes [Feature Name]
=============================================

⚠️  SCOPE: [Scope description]
--------------------------------------
These tests focus on:
- ✅ IN SCOPE: [What's in scope]
- ❌ OUT OF SCOPE: [What's out of scope]

Test Coverage:
    1. [Test 1 description]
    2. [Test 2 description]
    3. [Test 3 description]

Author: QA Automation Architect
Date: [Date]
Related: [Jira Ticket]
"""

import pytest
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.infrastructure.kubernetes_manager import KubernetesManager
from src.core.exceptions import APIError

logger = logging.getLogger(__name__)


# ===================================================================
# Fixtures
# ===================================================================

@pytest.fixture
def k8s_manager(config_manager):
    """
    Fixture to provide KubernetesManager instance.
    
    Yields:
        KubernetesManager: Kubernetes manager
    """
    logger.info("Initializing Kubernetes manager...")
    
    manager = KubernetesManager(config_manager)
    
    if manager.k8s_core_v1 is None:
        pytest.skip("Kubernetes not available (no kubeconfig)")
    
    yield manager
    
    logger.info("Kubernetes manager fixture cleanup complete")


# ===================================================================
# Test Classes
# ===================================================================

@pytest.mark.kubernetes
@pytest.mark.infrastructure
class TestK8s[FeatureName]:
    """Test Kubernetes [feature] functionality."""
    
    def test_k8s_[feature]_[scenario](self, k8s_manager):
        """
        Test that [scenario] works correctly.
        
        Steps:
        1. [Step 1]
        2. [Step 2]
        3. [Step 3]
        
        Expected:
        - [Expected result 1]
        - [Expected result 2]
        """
        logger.info("Starting [scenario] test...")
        
        # Test implementation
        try:
            # Test logic here
            pass
        except Exception as e:
            logger.error(f"Test failed: {e}")
            raise
        
        logger.info("[scenario] test completed successfully")
```

---

## 📝 Tickets to Create in Jira

### Sprint 1

- [ ] `PZ-XXXX` - K8s Pod Health Monitoring
- [ ] `PZ-XXXX` - K8s Resource Management Tests

### Sprint 2

- [ ] `PZ-XXXX` - K8s Resilience Tests

### Sprint 3

- [ ] `PZ-XXXX` - K8s Service Discovery Tests
- [ ] `PZ-XXXX` - K8s Deployment Strategy Tests

### Sprint 4

- [ ] `PZ-XXXX` - K8s Configuration Management Tests

---

## 📚 Related Documents

- [Team Processes and Sprint Management](TEAM_PROCESSES_AND_SPRINT_MANAGEMENT.md)
- [Jira Ticket Template](JIRA_TICKET_TEMPLATE.md)
- [Infrastructure Tests](../../../tests/infrastructure/README.md)

---

**Last Updated:** 2025-11-04  
**Owner:** QA Team Lead

