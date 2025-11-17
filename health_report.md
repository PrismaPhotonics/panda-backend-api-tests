# Pre-Test System Health Check Report
**Date:** 2025-11-16 15:13:29
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

### ✅ SSH
**Status:** OK
**Details:**
- Connection: OK
- Command Execution: OK
- Hostname: worker-node

### ✅ Kubernetes
**Status:** OK
**Details:**
- Connection Method: SSH Fallback ✅
- Cluster Version: v1.25.12+k3s1
- Node Count: 2
- Cluster Info: OK
- Deployments: 4
- Focus Server Deployment: Found
- Focus Server Ready: 1
- Focus Server Total: 1
- Total Pods: 55
- Running Pods: 55
- Pending Pods: 0
- gRPC Jobs: 25

### ✅ MongoDB
**Status:** OK
**Details:**
- Connection: OK
- Status Check: OK
- Connected: True
- Ready Replicas: 1
- Total Replicas: 1

### ✅ RabbitMQ
**Status:** OK
**Details:**
- Connection: OK
- Host: 10.10.10.150
- Service: rabbitmq-panda
- Credentials: OK
- Username: user
- Port: 5672

## Summary

- **Total Checks:** 5
- **Passed:** 5
- **Failed:** 0
