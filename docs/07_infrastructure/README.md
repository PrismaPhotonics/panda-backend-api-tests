# Infrastructure Documentation

> Kubernetes, MongoDB, RabbitMQ, and system infrastructure guides

---

## 📋 Overview

This directory contains 23 documents covering all infrastructure components and configurations.

## 📁 Key Documents

### Kubernetes & Production Environment
- **[NEW_ENVIRONMENT_MASTER_DOCUMENT.md](NEW_ENVIRONMENT_MASTER_DOCUMENT.md)** - Master environment document
- **[NEW_PRODUCTION_API_ENDPOINTS.md](NEW_PRODUCTION_API_ENDPOINTS.md)** - API endpoints
- **[COMPLETE_INFRASTRUCTURE_SUMMARY.md](COMPLETE_INFRASTRUCTURE_SUMMARY.md)** - Complete summary
- **[AUTOMATION_CONFIG_SUMMARY_HE.md](AUTOMATION_CONFIG_SUMMARY_HE.md)** - Config summary (Hebrew)

### Configuration & Testing
- **[TEST_CONFIGURATION_SUMMARY.md](TEST_CONFIGURATION_SUMMARY.md)** - Test configuration
- **[CONNECTIVITY_TEST_REPORT.md](CONNECTIVITY_TEST_REPORT.md)** - Connectivity tests

### gRPC & Job Management
- **[GRPC_JOB_LIFECYCLE.md](GRPC_JOB_LIFECYCLE.md)** - gRPC job lifecycle

### Monitoring
- **[POD_MONITORING_CONFIG.md](POD_MONITORING_CONFIG.md)** - Pod monitoring configuration

### RabbitMQ (6 documents)
- **[RABBITMQ_AUTOMATION_GUIDE.md](RABBITMQ_AUTOMATION_GUIDE.md)** - Complete RabbitMQ automation
- **[RABBITMQ_CONNECTION_GUIDE.md](RABBITMQ_CONNECTION_GUIDE.md)** - Connection guide
- **[RABBITMQ_QUICK_REFERENCE.md](RABBITMQ_QUICK_REFERENCE.md)** - Quick reference
- **[COMPLETE_RABBITMQ_JOURNEY.md](COMPLETE_RABBITMQ_JOURNEY.md)** - Complete journey
- **[BIT_RABBITMQ_PATTERNS.md](BIT_RABBITMQ_PATTERNS.md)** - Patterns & best practices
- **[RABBITMQ_AUTOMATION_QUICK_START.md](RABBITMQ_AUTOMATION_QUICK_START.md)** - Quick start

### MongoDB (4 documents)
- **[HOW_TO_DISCOVER_DATABASE_SCHEMA.md](HOW_TO_DISCOVER_DATABASE_SCHEMA.md)** - Schema discovery
- **[MONGODB_SCHEMA_REAL_FINDINGS.md](MONGODB_SCHEMA_REAL_FINDINGS.md)** - Real findings
- MongoDB clarification documents
- Collection documentation

---

## 🏗️ Infrastructure Components

### Kubernetes (Panda Namespace)
- **Cluster:** panda-cluster
- **Namespace:** panda
- **Access:** SSH via 10.10.100.3 → 10.10.100.113

### Services
- **Focus Server:** 10.10.100.100:443 (LoadBalancer)
- **Frontend:** 10.10.10.100:443 (LoadBalancer)
- **MongoDB:** 10.10.100.108:27017 (LoadBalancer)
- **RabbitMQ:** 10.10.100.107:5672 (LoadBalancer)

---

## 📊 Coverage

- ✅ All infrastructure documented
- ✅ Configuration guides complete
- ✅ Monitoring setup documented
- ✅ Troubleshooting guides available

---

**[← Back to Docs Home](../README.md)**

