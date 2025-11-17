# Pre-Test System Health Check Report
**Date:** 2025-11-06 17:08:10
**Environment:** staging

## Results

### ✅ Focus Server API
**Status:** OK
**Details:**
- Base URL: https://10.10.10.100/focus-server
- Health Check: OK
- Status Code: 200
- Channels Endpoint: OK
- Channel Range: 1-2337

### ✅ MongoDB
**Status:** OK
**Details:**
- Connection: OK
- Status Check: OK
- Connected: True
- Ready Replicas: 1
- Total Replicas: 1

### ✅ Kubernetes
**Status:** OK
**Details:**
- Connection Method: SSH Fallback ✅
- Cluster Version: v1.25.12+k3s1
- Node Count: 2
- Cluster Info: OK
- Deployments: 3
- Focus Server Deployment: Found
- Focus Server Ready: 1
- Focus Server Total: 1
- Total Pods: 4
- Running Pods: 4
- Pending Pods: 0
- gRPC Jobs: 0

### ❌ RabbitMQ
**Status:** FAILED
**Error:** RabbitMQ setup failed: Failed to start port-forward

### ✅ SSH
**Status:** OK
**Details:**
- Connection: OK
- Command Execution: OK
- Hostname: worker-node

## Summary

- **Total Checks:** 5
- **Passed:** 4
- **Failed:** 1
