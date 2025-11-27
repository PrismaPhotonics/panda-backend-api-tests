# gRPC Job Lifecycle - Complete Documentation

## Overview

Based on the Kubernetes job template found in `debug-codebase/pz/config/panda/templates/job-template.yml`, this document explains the complete lifecycle of gRPC jobs created by the Focus Server.

---

## Job Structure

### 1. Main Job: `grpc-job-$JOB_ID`

**Purpose:** Runs the gRPC server that streams spectrogram data to clients

**Key Configuration:**
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: grpc-job-$JOB_ID
spec:
  backoffLimit: 0                    # No retries on failure
  ttlSecondsAfterFinished: 120       # Auto-delete 2 minutes after completion
  template:
    metadata:
      labels:
        app: grpc-job-$JOB_ID        # Pod selector label
```

**Container Image:**
```
262399703539.dkr.ecr.eu-central-1.amazonaws.com/pzlinux:$PZ_IMAGE_TAG
```

**Environment Variables:**
- `PRISMA_RABBIT_MACHINE_NAME`: `data-rabbitmq.prismaphotonics.net`
- `PRISMA_CERTIFICATES`: `/etc/ssl/certs`
- `PRISMA_CONFIG`: `/home/prisma/pz/config`

**Ports:**
- `5000` - gRPC server port (containerPort)

**Resource Limits:**
```yaml
resources:
  limits:
    nvidia.com/gpu.shared: 1    # Requires GPU access
  requests:
    nvidia.com/gpu.shared: 1
  # CPU and memory commented out in current config
  # limits:
  #   cpu: "4"
  #   memory: "32Gi"
  # requests:
  #   cpu: "2"
  #   memory: "32Gi"
```

**Volume Mounts:**
1. **certs** → `/etc/ssl/certs` (RabbitMQ TLS certificates)
2. **active-python-file** → `/home/prisma/active-python-env.sh`
3. **debug-env-volume** → `/home/prisma/debug-codebase`
4. **prisma-config-volume** → `/home/prisma/pz/config`
5. **storage-san-volume** → `/prisma/root/recordings` (Historic data)

---

### 2. Cleanup Job: `cleanup-job-$JOB_ID`

**Purpose:** Monitors the main gRPC job and cleans up resources when done

**Key Configuration:**
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: cleanup-job-$JOB_ID
spec:
  backoffLimit: 0
  ttlSecondsAfterFinished: 10        # Auto-delete 10 seconds after completion
```

**Container Image:**
```
262399703539.dkr.ecr.eu-central-1.amazonaws.com/cleanup-grpc:1.1
```

**Service Account:**
```yaml
serviceAccountName: cleanup-sa       # Needs permissions to delete jobs/services
```

**Environment Variables:**
- `CPU_USAGE_THRESHOLD`: `4` (CPU usage threshold in millicores)
- `ENABLE_CPU_USAGE_CHECK`: `true` (Enable CPU-based cleanup)
- `MAX_CPU_USAGE_COUNT`: `5` (Number of consecutive low CPU readings before cleanup)

---

## Job Lifecycle

### Job Termination Mechanisms

**Current State (November 2025):**

| תרחיש | זמן עד מחיקה | מנגנון |
|-------|-------------|--------|
| **Job לא פותחים אותו** (לא מתחברים) | **~50 שניות** | Cleanup job מזהה CPU נמוך (5 checks × 10s) |
| **Job מסתיים** (Complete/Failed) | **2 דקות** | TTL (`ttlSecondsAfterFinished: 120`) |
| **Stream ללא פעילות** | **3 דקות** | gRPC Timeout (180s) |

#### פירוט מנגנונים:

1. **Job לא פותחים אותו (~50 שניות):**
   - Cleanup job בודק CPU כל 10 שניות
   - אם CPU ≤ 4m (millicores) במשך 5 בדיקות רצופות → מתחיל cleanup
   - זמן כולל: 5 × 10s = **50 שניות**

2. **Job מסתיים (2 דקות):**
   - Kubernetes Job מסתיים (Complete/Failed)
   - `ttlSecondsAfterFinished: 120` → Job נמחק אוטומטית אחרי **2 דקות**

3. **Stream ללא פעילות (3 דקות):**
   - gRPC stream ללא פעילות
   - Timeout של **180 שניות (3 דקות)** → Job נסגר אוטומטית

4. **Job Cancellation Endpoint (Discussed, Not Implemented):**
   - `DELETE /job/{job_id}` → **Currently returns 404**
   - **Status:** Discussed in team conversation (not a formal decision)
   - **Security Concern Raised:** Need to protect against one APP instance cancelling jobs of another (if implemented)

### Phase 1: Job Creation (by Focus Server)

```
User Request → POST /configure → Focus Server
                                      ↓
                        1. Allocate job_id (e.g., "12-70788")
                        2. Substitute $JOB_ID in template
                        3. Create grpc-job-$JOB_ID
                        4. Create cleanup-job-$JOB_ID
                        5. Create grpc-service-$JOB_ID (NodePort)
                        6. Return job_id to client
```

### Phase 2: Job Running

```
grpc-job-$JOB_ID (Pod)
    ↓
Pulls Docker image: pzlinux:$PZ_IMAGE_TAG
    ↓
Executes: $GRPC_JOB_PARAMETERS command
    ↓
Starts gRPC server on port 5000
    ↓
Streams data to client
```

**Concurrent Cleanup Monitoring:**
```
cleanup-job-$JOB_ID (Pod)
    ↓
Monitors grpc-job-$JOB_ID every 10 seconds
    ↓
Checks:
  1. Job status (Complete/Failed)
  2. CPU usage ≤ 4m (millicores) for 5 consecutive checks
    ↓
When done → Cleanup Phase
```

### Phase 3: Cleanup (Automatic)

The cleanup job performs the following actions:

```bash
# 1. Delete gRPC service
kubectl delete service grpc-service-$JOB_ID --ignore-not-found

# 2. Delete gRPC job (force)
kubectl delete job grpc-job-$JOB_ID --ignore-not-found --grace-period=0 --force

# 3. Delete cleanup job itself
kubectl delete job cleanup-job-$JOB_ID --ignore-not-found --grace-period=0 --force

# 4. Delete RabbitMQ queue
queue_name=$(curl -u prisma:prismapanda http://rabbitmq-panda:15672/api/queues | \
             grep -o "\"name\":\"grpc-job-$JOB_ID-[^\"]*\"" | \
             sed 's/"name":"//;s/"//')
curl -u prisma:prismapanda -X DELETE \
     http://rabbitmq-panda:15672/api/queues/%2F/$queue_name
```

### Phase 4: TTL-Based Deletion

```
grpc-job-$JOB_ID: Deleted 120 seconds after completion (ttlSecondsAfterFinished: 120)
cleanup-job-$JOB_ID: Deleted 10 seconds after completion (ttlSecondsAfterFinished: 10)
```

---

## Resource Constraints

### GPU Requirement

**Critical Finding:** All gRPC jobs require GPU access!

```yaml
resources:
  limits:
    nvidia.com/gpu.shared: 1
  requests:
    nvidia.com/gpu.shared: 1
```

**Implication:** If the worker node's GPU is fully allocated, new jobs will be **Pending** indefinitely.

### CPU/Memory (Currently Unlimited)

The CPU and memory limits are **commented out** in the current configuration:

```yaml
# limits:
#   cpu: "4"
#   memory: "32Gi"
# requests:
#   cpu: "2"
#   memory: "32Gi"
```

**Implication:** Jobs can consume unlimited CPU/memory, but GPU is still limited.

---

## Why Jobs Get Stuck in "Pending"

### Root Causes:

1. **GPU Exhaustion** (Most Common)
   - Each job needs `nvidia.com/gpu.shared: 1`
   - Worker node has limited GPU resources
   - If 200+ jobs are pending, GPU is likely exhausted

2. **Worker Node Issues**
   - Node in `NotReady` state (as we saw: `worker-node NotReady`)
   - Node has `SchedulingDisabled` (as we saw: `master-node SchedulingDisabled`)

3. **MaxWindows Constraint**
   - Focus Server limits concurrent jobs to **30** (MaxWindows)
   - But Kubernetes might have >30 pending jobs if cleanup failed

4. **Cleanup Job Failure**
   - If cleanup jobs fail, old jobs remain
   - Old jobs still count toward GPU allocation
   - New jobs can't start

---

## Cleanup Triggers

The cleanup job exits when ANY of these conditions are met:

### 1. Job Completion
```bash
job_status=$(kubectl get job grpc-job-$JOB_ID -o jsonpath='{.status.conditions[?(@.type=="Complete")].status}')
if [ "$job_status" = "True" ]; then
    # Start cleanup
fi
```

### 2. Job Failure
```bash
job_failed=$(kubectl get job grpc-job-$JOB_ID -o jsonpath='{.status.conditions[?(@.type=="Failed")].status}')
if [ "$job_failed" = "True" ]; then
    # Start cleanup
fi
```

### 3. Low CPU Usage (5 consecutive checks)
```bash
if [ "$cpu_usage" -le "1" ]; then
    cpu_usage_count=$((cpu_usage_count + 1))
    if [ "$cpu_usage_count" -ge "5" ]; then
        # CPU idle for 50 seconds (5 checks × 10s)
        # Start cleanup
    fi
fi
```

**Check Interval:** Every 10 seconds

---

## Service Creation

Each gRPC job has an associated Kubernetes Service:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: grpc-service-$JOB_ID
spec:
  type: NodePort
  selector:
    app: grpc-job-$JOB_ID
  ports:
  - protocol: TCP
    port: 12301+     # Port starts from 12301 and increments
    targetPort: 5000
    nodePort: 30000+ # NodePort in range 30000-32767
```

**Port Allocation:**
- **Internal Port:** 5000 (gRPC server)
- **Service Port:** 12301, 12302, 12303, ... (increments per job)
- **NodePort:** Dynamically allocated by Kubernetes (30000-32767)

---

## Monitoring gRPC Jobs

### Get All gRPC Jobs
```bash
kubectl get jobs -n panda -l app | grep grpc-job
```

### Get Pending gRPC Jobs
```bash
kubectl get pods -n panda --field-selector=status.phase=Pending -l app | grep grpc-job
```

### Get Running gRPC Jobs
```bash
kubectl get pods -n panda --field-selector=status.phase=Running -l app | grep grpc-job
```

### Get Cleanup Jobs
```bash
kubectl get jobs -n panda | grep cleanup-job
```

### Check Job Status
```bash
kubectl describe job grpc-job-$JOB_ID -n panda
```

### Check Pod Logs
```bash
# gRPC job logs
kubectl logs -n panda -l app=grpc-job-$JOB_ID

# Cleanup job logs
kubectl logs -n panda -l app=cleanup-job-$JOB_ID
```

---

## Manual Cleanup (Emergency)

### Delete All Pending gRPC Jobs
```bash
kubectl get pods -n panda --field-selector=status.phase=Pending | \
  grep grpc-job | \
  awk '{print $1}' | \
  xargs -I {} kubectl delete pod {} -n panda --grace-period=0 --force
```

### Delete All gRPC Jobs (Nuclear Option)
```bash
# Delete all gRPC jobs
kubectl delete jobs -n panda -l app | grep grpc-job

# Delete all cleanup jobs
kubectl delete jobs -n panda | grep cleanup-job

# Delete all gRPC services
kubectl delete services -n panda | grep grpc-service
```

### Delete Specific Job
```bash
JOB_ID="12-70788"

# Delete service
kubectl delete service grpc-service-$JOB_ID -n panda --ignore-not-found

# Delete gRPC job
kubectl delete job grpc-job-$JOB_ID -n panda --ignore-not-found --grace-period=0 --force

# Delete cleanup job
kubectl delete job cleanup-job-$JOB_ID -n panda --ignore-not-found --grace-period=0 --force
```

---

## Integration with Focus Server

### Job Creation Flow

```python
# Focus Server (simplified)
def create_grpc_job(config):
    # 1. Allocate job_id from pool (0-29, based on MaxWindows)
    job_id = allocate_job_id()  # Returns "12-70788" format
    
    # 2. Load job template
    template = load_template("job-template.yml")
    
    # 3. Substitute variables
    template = template.replace("$JOB_ID", job_id)
    template = template.replace("$PZ_IMAGE_TAG", "latest")
    template = template.replace("$GRPC_JOB_PARAMETERS", generate_command(config))
    
    # 4. Apply to Kubernetes
    kubectl.apply(template)
    
    # 5. Return job_id to client
    return {"job_id": job_id}
```

### Job ID Format

```
Format: "{window_index}-{unique_id}"
Example: "12-70788"
         ↑       ↑
         |       └─ Unique identifier (timestamp-based)
         └───────── Window index (0-29, based on MaxWindows=30)
```

---

## Testing Considerations

### For Test Automation

1. **Job Cleanup After Tests**
   - Tests should verify jobs are cleaned up
   - Monitor pending jobs before/after test runs
   - Alert if pending jobs increase

2. **GPU Resource Monitoring**
   - Check GPU allocation before tests
   - Ensure sufficient GPU resources available

3. **Cleanup Job Monitoring**
   - Verify cleanup jobs complete successfully
   - Check cleanup job logs for errors

4. **Service Cleanup**
   - Ensure gRPC services are deleted
   - Check for orphaned services

### Test Fixtures

```python
@pytest.fixture
def cleanup_grpc_jobs():
    """Ensure no pending gRPC jobs before test."""
    # Get pending jobs
    result = subprocess.run(
        ["kubectl", "get", "pods", "-n", "panda", 
         "--field-selector=status.phase=Pending"],
        capture_output=True
    )
    
    # Warn if too many pending
    pending_count = len(result.stdout.decode().split('\n')) - 1
    if pending_count > 10:
        pytest.fail(f"Too many pending jobs: {pending_count}")
    
    yield
    
    # Cleanup after test
    # (implementation...)
```

---

## Summary

| Component | Purpose | Lifetime | Cleanup Trigger |
|-----------|---------|----------|-----------------|
| `grpc-job-$JOB_ID` | Stream spectrogram data | Until completion or failure | Cleanup job |
| `cleanup-job-$JOB_ID` | Monitor and cleanup | Until main job done + cleanup | TTL (10s) |
| `grpc-service-$JOB_ID` | Expose gRPC server | Same as gRPC job | Cleanup job |
| RabbitMQ Queue | Message passing | Same as gRPC job | Cleanup job |

**Key Constraints:**
- **MaxWindows:** 30 concurrent jobs (Focus Server limit)
- **GPU:** 1 shared GPU per job (Kubernetes limit)
- **Cleanup Delay:** Up to 50 seconds (5 × 10s checks) if CPU-based

**Current Issue (Oct 2025):**
- Worker node `NotReady` → Pods can't schedule
- 200+ pending gRPC jobs → GPU exhausted
- Cleanup jobs can't run → Old jobs not deleted
- **Solution:** Fix worker node + delete pending jobs

---

## References

- Job Template: `debug-codebase/pz/config/panda/templates/job-template.yml`
- Focus Server Config: `config/environments.yaml` (MaxWindows: 30)
- Kubernetes Namespace: `panda`
- GPU Resource: `nvidia.com/gpu.shared`

