# Technical Requirements from Interrogator Team - Automation Advancement

**Document:** Technical and environmental requirements for advancing Focus Server automation  
**Author:** Roy Avrahami - QA Team Lead  
**Date:** 2025-12-06  
**Version:** 1.0  
**Status:** Requirements for submission to Interrogator team

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Kubernetes Requirements](#kubernetes-requirements)
3. [Database Requirements](#database-requirements)
4. [Network & Security Requirements](#network--security-requirements)
5. [Monitoring & Logging Requirements](#monitoring--logging-requirements)
6. [Development Environment Requirements](#development-environment-requirements)
7. [CI/CD Requirements](#cicd-requirements)
8. [Documentation Requirements](#documentation-requirements)
9. [Implementation Plan](#implementation-plan)

---

## Executive Summary

### Document Purpose

This document specifies all technical and environmental requirements needed from the Interrogator team to enable significant advancement of Focus Server automation from a technical perspective.

### Current State

**What we already have:**
- ✅ Access to Kubernetes via SSH tunnel (jump host)
- ✅ Access to MongoDB via LoadBalancer (read/write)
- ✅ Access to RabbitMQ via LoadBalancer
- ✅ Access to Focus Server API
- ✅ Staging and production environments configured

**What is missing:**
- ❌ Direct access to Kubernetes API (only via SSH)
- ❌ ServiceAccount with appropriate permissions
- ❌ Access to metrics and monitoring
- ❌ Separate dev/test environment
- ❌ Access to backups/restore
- ❌ Architecture documentation

---

## Kubernetes Requirements

### 1. Direct Access to Kubernetes API

**Current requirement:**
- Access only via SSH tunnel → `kubectl` on worker node
- Slow and not suitable for advanced automation

**Required:**
- Direct access to Kubernetes API Server
- `kubeconfig` with valid credentials
- Ability to connect from CI/CD runners

**Technical details:**
```yaml
# Required:
- API Server: https://10.10.100.102:6443 (or staging equivalent)
- kubeconfig file with:
  - Cluster CA certificate
  - User credentials (token/certificate)
  - Context: panda-cluster
  - Namespace: panda
```

**Required permissions:**
- `get`, `list`, `watch` on pods, services, deployments
- `get`, `list` on logs
- `create`, `delete` on jobs (for testing)
- `get`, `list` on events

### 2. ServiceAccount with RBAC

**Required:**
- Dedicated ServiceAccount for automation: `focus-automation-sa`
- Role/RoleBinding with minimal required permissions
- Ability for impersonation from CI/CD

**Required RBAC:**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: focus-automation-role
  namespace: panda
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log", "services", "events"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["batch"]
  resources: ["jobs"]
  verbs: ["get", "list", "watch", "create", "delete"]
```

### 3. Access to Metrics & Monitoring

**Required:**
- Access to Prometheus metrics (if available)
- Access to Kubernetes metrics API
- Ability to query resource usage (CPU, Memory)

**Usage:**
- Real-time performance monitoring during tests
- Memory leak detection
- Resource exhaustion detection

### 4. Separate Namespace for Testing

**Required:**
- Dedicated namespace: `focus-automation-test`
- Full permissions in this namespace
- Complete isolation from production

**Usage:**
- Running isolated load/stress tests
- Outage simulation tests
- Deployment/rollback tests

---

## Database Requirements

### 1. Access to MongoDB with Advanced Permissions

**What we have:**
- ✅ Basic read/write access
- ✅ Credentials: `prisma/prisma`

**What is missing:**
- ❌ Access to admin operations (backup/restore)
- ❌ Access to replica set configuration
- ❌ Access to oplog (for sync testing)

**Requirements:**
- User with `readWrite` + `backup` + `restore` permissions
- Access to `admin` database (for health checks)
- Access to `local` database (for replica set testing)

### 2. Access to PostgreSQL (if available)

**Required:**
- Credentials for PostgreSQL (if exists)
- Read-only access for testing
- Schema documentation

### 3. Database Snapshots & Backups

**Required:**
- Access to backup snapshots (for environment restoration)
- Ability to create snapshot before destructive tests
- Ability to restore snapshot after tests

**Usage:**
- Data integrity tests
- Recovery tests
- Migration tests

---

## Network & Security Requirements

### 1. Direct Access to Services (without SSH tunnel)

**What we have:**
- ✅ Access via SSH jump host
- ✅ LoadBalancer IPs available

**What is missing:**
- ❌ Direct access from CI/CD runners
- ❌ VPN access or network routing

**Required:**
- VPN access or network routing to internal network
- Or: LoadBalancer IPs with appropriate firewall rules
- Or: Ingress controller with authentication

### 2. Firewall Rules

**Required:**
- Opening required ports from CI/CD runners:
  - `6443` - Kubernetes API
  - `27017` - MongoDB
  - `5672` - RabbitMQ
  - `5000` - Focus Server API
  - `15672` - RabbitMQ Management UI

### 3. SSL/TLS Certificates

**Required:**
- CA certificates for self-signed certificates
- Or: valid SSL certificates (preferred)
- Documentation of certificate chain

---

## Monitoring & Logging Requirements

### 1. Access to Centralized Logs

**Required:**
- Access to centralized logging (if available)
- Or: Access to pod logs via Kubernetes API
- Ability to query logs by time range

**Usage:**
- Error analysis in tests
- Pattern detection in issues
- Production issue debugging

### 2. Access to Alerts & Notifications

**Required:**
- Access to alerting system (if available)
- Ability to create alerts for tests
- Integration with Slack/Email

### 3. Metrics & Dashboards

**Required:**
- Access to Grafana dashboards (if available)
- Or: Access to Prometheus queries
- Metrics on:
  - Pod resource usage
  - API response times
  - Database query performance
  - Queue depths

---

## Development Environment Requirements

### 1. Separate Dev/Test Environment

**Required:**
- Dev environment separate from staging/production
- With:
  - Separate Kubernetes cluster (or isolated namespace)
  - Separate MongoDB instance
  - Separate RabbitMQ instance
  - Separate Focus Server instance

**Usage:**
- Developing new tests
- Destructive tests without risk
- Technical experiments

### 2. Improved Staging Environment

**What we have:**
- ✅ Basic staging environment

**What is missing:**
- ❌ Sufficient test data
- ❌ Stable environment (not constantly updating)
- ❌ Ability to reset environment

**Required:**
- Stable staging environment
- Pre-defined test data
- Ability to reset environment to clean state

### 3. Test Data Management

**Required:**
- Access to create/delete test data
- Pre-defined test data
- Ability to seed data before tests

---

## CI/CD Requirements

### 1. GitHub Actions Runner Access

**Required:**
- Self-hosted runner with access to internal network
- Or: VPN access from GitHub-hosted runners
- Or: Appropriate network routing

**Current:**
- ✅ Self-hosted runner: `panda_automation`
- ❓ Access to internal network?

### 2. Secrets Management

**Required:**
- GitHub Secrets configured with:
  - Kubernetes credentials
  - Database credentials
  - SSH keys
  - API tokens

**Current:**
- ✅ Some items exist
- ❓ Update and completion required

### 3. Container Registry Access

**Required:**
- Access to container registry (if available)
- Ability to pull images for testing
- Or: documentation on image locations

---

## Documentation Requirements

### 1. Architecture

**Required:**
- Architecture documentation of the system:
  - Microservices and relationships between them
  - Data flow
  - Event flow
  - Dependencies

### 2. Infrastructure Documentation

**Required:**
- Infrastructure documentation:
  - Kubernetes cluster topology
  - Network architecture
  - Database schema
  - Service dependencies

### 3. API Documentation

**Required:**
- Updated OpenAPI/Swagger specs
- gRPC services documentation
- Message queue schemas documentation

### 4. Runbooks & Troubleshooting

**Required:**
- Runbooks for common operations
- Troubleshooting guides
- Known issues and workarounds

---

## Implementation Plan

### Phase 1: Critical Requirements (Month 1)

**High priority:**
1. ✅ Direct access to Kubernetes API
2. ✅ ServiceAccount with RBAC
3. ✅ Access to MongoDB with advanced permissions
4. ✅ Separate dev/test environment

**Expected outcome:**
- Ability to develop advanced tests
- Ability to test outage scenarios
- Ability to test recovery

### Phase 2: Important Requirements (Month 2)

**Medium priority:**
1. ✅ Access to Metrics & Monitoring
2. ✅ Access to Centralized Logs
3. ✅ Database Snapshots & Backups
4. ✅ Network & Security improvements

**Expected outcome:**
- Real-time monitoring capability
- Problem analysis capability
- Environment restoration capability

### Phase 3: Additional Requirements (Month 3+)

**Low priority:**
1. ✅ Comprehensive documentation
2. ✅ CI/CD improvements
3. ✅ Advanced monitoring

**Expected outcome:**
- Complete and professional automation
- Easy maintenance capability
- Scalability capability

---

## Specific Request List for Interrogator Team

### Request #1: Kubernetes API Access

**What is required:**
- kubeconfig file with valid credentials
- Direct access to API Server: `https://10.10.100.102:6443`
- Or: VPN access to internal network

**Usage:**
- Developing advanced Kubernetes tests
- Real-time pod monitoring
- Deployment/rollback tests

**Priority:** 🔴 High

---

### Request #2: ServiceAccount with RBAC

**What is required:**
- ServiceAccount: `focus-automation-sa` in namespace `panda`
- Role with permissions:
  - `get`, `list`, `watch` on pods, services, deployments
  - `get`, `list` on logs
  - `create`, `delete` on jobs

**Usage:**
- Running tests from CI/CD
- Resource monitoring
- Job execution tests

**Priority:** 🔴 High

---

### Request #3: MongoDB Advanced Permissions

**What is required:**
- User with permissions:
  - `readWrite` on database `prisma`
  - `backup` + `restore` permissions
  - Access to `admin` database (read-only)

**Usage:**
- Backup/restore tests
- Data integrity tests
- Recovery tests

**Priority:** 🟡 Medium

---

### Request #4: Separate Dev/Test Environment

**What is required:**
- Separate dev environment with:
  - Kubernetes namespace: `focus-automation-dev`
  - Separate MongoDB instance
  - Separate RabbitMQ instance
  - Separate Focus Server instance

**Usage:**
- Developing new tests
- Destructive tests without risk
- Technical experiments

**Priority:** 🟡 Medium

---

### Request #5: Access to Metrics & Monitoring

**What is required:**
- Access to Prometheus (if available)
- Or: Access to Kubernetes metrics API
- Access to Grafana dashboards (if available)

**Usage:**
- Real-time performance monitoring
- Memory leak detection
- Resource exhaustion detection

**Priority:** 🟡 Medium

---

### Request #6: Database Snapshots & Backups

**What is required:**
- Access to backup snapshots
- Ability to create snapshot before tests
- Ability to restore snapshot after tests

**Usage:**
- Data integrity tests
- Recovery tests
- Migration tests

**Priority:** 🟢 Low

---

### Request #7: Architecture Documentation

**What is required:**
- Microservices and relationships documentation
- Data flow documentation
- Event flow documentation
- Dependencies documentation

**Usage:**
- Understanding the system
- Developing appropriate tests
- Troubleshooting

**Priority:** 🟢 Low

---

## Summary

### Critical Requirements (Must Have)

1. **Kubernetes API Access** - Cannot develop advanced tests without this
2. **ServiceAccount with RBAC** - Required for CI/CD integration
3. **MongoDB Advanced Permissions** - Required for recovery tests

### Important Requirements (Recommended)

4. **Dev/Test Environment** - Enables safe development
5. **Metrics & Monitoring** - Enables advanced monitoring
6. **Database Snapshots** - Enables recovery tests

### Additional Requirements (Nice to Have)

7. **Comprehensive Documentation** - Improves development and maintenance capability

---

## Additional Notes

### Communication with Interrogator Team

**Recommended:**
- Initial meeting to present requirements
- Establishing a regular point of contact
- Weekly updates on progress

### Timeline

**Desired:**
- Critical requirements: Within 1 month
- Important requirements: Within 2-3 months
- Additional requirements: As needed

### Technical Support

**Required:**
- Technical support in setting up access
- Training on infrastructure usage
- Support for technical issues

---

**This document serves as a basis for discussion with the Interrogator team on technical requirements for advancing automation.**

