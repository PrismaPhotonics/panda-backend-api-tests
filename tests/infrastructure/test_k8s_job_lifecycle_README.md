# K8s Job Lifecycle Tests

**Created:** 27 October 2025  
**Related:** PZ-13756 (Meeting decision - K8s/Orchestration in scope)

---

## Purpose

These tests validate Kubernetes orchestration of Focus Server jobs.

## Tests Included

1. **test_k8s_job_creation_triggers_pod_spawn()**
   - Validates: Job → Pod creation
   - Checks: Pod labels, status, containers
   
2. **test_k8s_job_resource_allocation()**
   - Validates: CPU/Memory allocation
   - Checks: Requests, limits, proper configuration
   
3. **test_k8s_job_port_exposure()**
   - Validates: gRPC port exposure
   - Checks: Port mapping, service discovery
   - Note: Transport readiness only (IN SCOPE)
   
4. **test_k8s_job_cancellation_and_cleanup()**
   - Validates: Clean cancellation and cleanup
   - Checks: Pod termination, resource cleanup
   
5. **test_k8s_job_observability()**
   - Validates: Logs, events, metrics
   - Checks: Observability for debugging

## Running Tests

```bash
# All K8s lifecycle tests
pytest tests/infrastructure/test_k8s_job_lifecycle.py -v

# Specific test
pytest tests/infrastructure/test_k8s_job_lifecycle.py::TestK8sJobCreation::test_k8s_job_creation_triggers_pod_spawn -v

# With markers
pytest -m "kubernetes and job_lifecycle" -v
```

## Prerequisites

- Kubernetes cluster access
- kubectl configured
- Focus Server deployed

## Expected Duration

- All 5 tests: ~5 minutes
- Individual test: ~30-60 seconds

