# 📋 9 Critical Tests Missing in Xray - Full Documentation
## תיעוד מלא בפורמט Xray - ללא Waterfall

**תאריך:** 2025-10-21  
**סביבה:** new_production (panda namespace)  
**סה"כ טסטים:** 9 Critical Tests  

---

# TEST 1: GET /sensors Endpoint

## Test ID
**NEW-001** (pending Xray creation)

## Summary
Integration - GET /sensors - Retrieve Available Sensors List

## Objective
Validates that the `GET /sensors` endpoint returns a complete list of all available sensors/channels in the system. This endpoint is a prerequisite for any configuration operation, as clients need to know which sensors are available before selecting a sensor range (ROI). The test verifies that the list is complete, accurate, and properly formatted.

## Priority
**High**

## Components/Labels
* **Component**: Focus Server Backend API
* **Labels**: `api-endpoint`, `sensors`, `smoke-test`, `get-request`, `discovery`, `prerequisite`
* **Test Type**: Integration Test (Smoke)

## Requirements
* **Requirement ID**: FOCUS-API-SENSORS-LIST-001
* **Description**: Server must provide endpoint to query all available sensors for configuration purposes

## Pre-Conditions
1. Focus Server is running at `https://10.10.100.100/focus-server/`
2. System has fiber optic sensors configured
3. At least one sensor is available in the system
4. Baby Analyzer has initialized and knows sensor count
5. Endpoint is accessible (authentication if required)

## Test Data

**No request body required** (GET request)

**Expected Response Structure**:
```json
{
  "sensors": [0, 1, 2, 3, 4, ..., N]
}
```
OR
```json
{
  "sensor_count": N,
  "sensor_list": [0, 1, 2, ...]
}
```

**Query Parameters**: None

**Headers**:
```
Accept: application/json
Content-Type: application/json
```

## Steps

| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Send `GET https://10.10.100.100/focus-server/sensors` request | HTTP 200 OK |
| 2 | Verify response Content-Type is `application/json` | Header: `Content-Type: application/json` |
| 3 | Parse response body as JSON | Valid JSON structure |
| 4 | Extract sensors list from response (field: `sensors` or `sensor_list`) | Array of integers |
| 5 | Verify list is **non-empty** | `sensors.length > 0` (at least 1 sensor) |
| 6 | Verify sensors are **integers** | All elements are type `int` |
| 7 | Verify sensors are **non-negative** | All sensors >= 0 |
| 8 | Verify sensors start at 0 | First sensor = 0 |
| 9 | Verify sensors are **sequential** (no gaps) | sensors = [0, 1, 2, ..., N] |
| 10 | Verify sensor count is reasonable | Count < 10000 (system limit) |
| 11 | Measure response time | Response time < 500ms |
| 12 | Send request **again** to verify consistency | Same list returned |
| 13 | Compare with MongoDB sensor configuration (if available) | Matches system configuration |

## Expected Result
* Endpoint returns **HTTP 200 OK**
* Response contains **array of sensors**
* Sensors list is **non-empty** (at least 1 sensor)
* Sensors are **sequential integers** starting from 0: `[0, 1, 2, 3, ..., N]`
* No gaps in sequence
* Sensor count is reasonable (e.g., 0-1000)
* Response is **consistent** across multiple calls
* Response time < 500ms
* No errors or exceptions

**Example Valid Response**:
```json
{"sensors": [0, 1, 2, 3, 4, 5, ..., 200]}
```

## Post-Conditions
* No state changes (read-only operation)
* Server remains responsive
* Endpoint remains available for subsequent calls

## Environment

**Environment Name**: new_production (panda namespace)

**Backend (Focus Server)**:
- URL: `https://10.10.100.100/focus-server/`
- Endpoint: `GET https://10.10.100.100/focus-server/sensors`
- Alternative: `GET https://10.10.100.100/api/sensors`
- SSL Verification: `False` (self-signed certificate)

**MongoDB** (for validation):
- Host: `10.10.100.108:27017`
- Database: `prisma`
- Connection: `mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma`

**Kubernetes**:
- Namespace: `panda`
- Focus Server Service: `panda-panda-focus-server.panda:5000`

## Automation Status

✅ **Automated**

**Framework**: pytest 7.0+  
**Test Function**: `test_get_sensors_list`  
**Test File**: `tests/integration/api/test_live_monitoring_flow.py`  
**Test Class**: `TestLiveMonitoringHappyPath`  
**Lines**: 129-156

**Run Command**:
```bash
# Run this test
pytest tests/integration/api/test_live_monitoring_flow.py::TestLiveMonitoringHappyPath::test_get_sensors_list -v

# Run with output
pytest tests/integration/api/test_live_monitoring_flow.py::TestLiveMonitoringHappyPath::test_get_sensors_list -v -s
```

**Expected Test Duration**: ~1-2 seconds

---

# TEST 2: MongoDB Connection

## Test ID
**NEW-002** (pending Xray creation)

## Summary
Infrastructure - MongoDB Direct Connection and Health Check

## Objective
Validates direct TCP connection to MongoDB database server and verifies basic operations (authentication, ping, database listing). This is a critical infrastructure test that isolates MongoDB health from Focus Server functionality. Used for diagnostics when system issues occur.

## Priority
**High**

## Components/Labels
* **Component**: MongoDB Infrastructure
* **Labels**: `infrastructure`, `mongodb`, `connectivity`, `health-check`, `diagnostic`
* **Test Type**: Infrastructure Test

## Requirements
* **Requirement ID**: INFRA-MONGODB-CONNECTIVITY-001
* **Description**: MongoDB database must be accessible, authenticated, and operational

## Pre-Conditions
1. MongoDB is deployed and running (pod or external)
2. MongoDB LoadBalancer service exposed at `10.10.100.108:27017`
3. Credentials available: `username=prisma, password=prisma`
4. Database `prisma` exists
5. Network routing allows connection from test client to MongoDB

## Test Data

**Connection String**:
```
mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma
```

**Expected Database**: `prisma`

**Expected Collections**:
- `recordings`
- `tasks`
- `metadata`
- `node4`

## Steps

| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Import pymongo library: `from pymongo import MongoClient` | Library imported successfully |
| 2 | Create connection string: `mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma` | Connection string created |
| 3 | Attempt TCP connection to `10.10.100.108:27017` | TCP connection established (socket open) |
| 4 | Create MongoClient with connection string | Client object created |
| 5 | Execute authentication against `authSource=prisma` | Authentication successful |
| 6 | Execute ping command: `client.admin.command('ping')` | Ping returns `{'ok': 1}` |
| 7 | List all databases: `client.list_database_names()` | Database list returned |
| 8 | Verify database `prisma` exists in list | `'prisma' in databases` = True |
| 9 | Connect to database: `db = client['prisma']` | Database object created |
| 10 | List all collections: `db.list_collection_names()` | Collection list returned |
| 11 | Verify required collections exist: `recordings`, `tasks`, `metadata`, `node4` | All collections found |
| 12 | Execute simple query: `db.recordings.find_one()` | Query executes (with or without results) |
| 13 | Measure ping latency | Latency < 100ms |
| 14 | Close connection gracefully | Connection closed without errors |

## Expected Result
* **TCP connection** to `10.10.100.108:27017` **successful**
* **Authentication** with `prisma/prisma` **successful**
* **Ping** command returns `{'ok': 1}`
* **Database** `prisma` **exists**
* **Collections** `recordings`, `tasks`, `metadata`, `node4` **exist**
* Simple queries execute successfully
* Ping latency < 100ms
* No connection errors or timeouts

## Post-Conditions
* MongoDB connection closed
* No open connections left
* MongoDB state unchanged (read-only operations)

## Environment

**MongoDB LoadBalancer**:
- Host: `10.10.100.108`
- Port: `27017`
- Service: `mongodb.panda` (LoadBalancer)
- Internal Service: `mongodb.panda:27017` (ClusterIP: 10.43.74.248)

**Credentials**:
- Username: `prisma`
- Password: `prisma`
- Auth Source: `prisma`
- Database: `prisma`

**Kubernetes**:
- Namespace: `panda`
- MongoDB Pod: Check with `kubectl get pods -n panda | grep mongodb`

**SSH Access** (for troubleshooting):
- Jump: `ssh root@10.10.100.3`
- Target: `ssh prisma@10.10.100.113`
- Then: `k9s` to view pods

## Automation Status

✅ **Automated**

**Framework**: pytest 7.0+  
**Test Function**: `test_mongodb_connection`  
**Test File**: `tests/integration/infrastructure/test_external_connectivity.py`  
**Test Class**: `TestExternalServicesConnectivity`  
**Lines**: 68-125

**Run Command**:
```bash
# Run MongoDB connectivity test
pytest tests/integration/infrastructure/test_external_connectivity.py::TestExternalServicesConnectivity::test_mongodb_connection -v

# Run with markers
pytest -m "mongodb and infrastructure" -v
```

**Dependencies**:
```python
pymongo>=4.0.0
```

**Expected Test Duration**: ~2-3 seconds

---

# TEST 3: Kubernetes Connection

## Test ID
**NEW-003** (pending Xray creation)

## Summary
Infrastructure - Kubernetes Cluster Connection and Pod Health Check

## Objective
Validates connection to Kubernetes cluster API server and verifies that Focus Server pods are running and healthy. This infrastructure test ensures orchestration layer is functional and allows monitoring pod status, resource usage, and logs. Critical for operational visibility.

## Priority
**High**

## Components/Labels
* **Component**: Kubernetes Infrastructure
* **Labels**: `infrastructure`, `kubernetes`, `orchestration`, `pod-health`, `diagnostic`
* **Test Type**: Infrastructure Test

## Requirements
* **Requirement ID**: INFRA-KUBERNETES-CONNECTIVITY-001
* **Description**: Kubernetes cluster must be accessible and Focus Server pods must be discoverable

## Pre-Conditions
1. Kubernetes cluster is running
2. API Server accessible at `https://10.10.100.102:6443`
3. Valid kubeconfig or service account credentials available
4. Namespace `panda` exists
5. Focus Server deployed in namespace
6. Network allows connection to K8s API server

## Test Data

**Cluster Details**:
- API Server: `https://10.10.100.102:6443`
- Namespace: `panda`
- Expected Deployment: `panda-panda-focus-server`
- Expected Service: `panda-panda-focus-server.panda:5000`

**Expected Pods**:
- At least 1 Focus Server pod running
- Pod name pattern: `panda-panda-focus-server-*`

**Expected Services**:
- Service name: `panda-panda-focus-server`
- Type: ClusterIP
- ClusterIP: `10.43.103.101`
- Port: `5000`

## Steps

| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Import kubernetes library: `from kubernetes import client, config` | Library imported |
| 2 | Load kubeconfig or service account credentials | Config loaded successfully |
| 3 | Create API client: `v1 = client.CoreV1Api()` | Client created |
| 4 | Test connection: Get cluster version | Version info returned (e.g., v1.25.x) |
| 5 | List all namespaces: `v1.list_namespace()` | Namespace list returned |
| 6 | Verify namespace `panda` exists | `'panda' in namespaces` = True |
| 7 | List pods in `panda` namespace: `v1.list_namespaced_pod(namespace='panda')` | Pod list returned |
| 8 | Search for Focus Server pods: filter by name pattern `panda-panda-focus-server-*` | At least 1 pod found |
| 9 | For each Focus Server pod, check status | Status = `Running` |
| 10 | Verify pod readiness: check `ready` condition | Pod is Ready = True |
| 11 | Check pod restart count | Restart count < 5 (acceptable threshold) |
| 12 | List services in `panda` namespace | Service list returned |
| 13 | Verify service `panda-panda-focus-server` exists | Service found |
| 14 | Verify service ClusterIP | ClusterIP = `10.43.103.101` |
| 15 | Verify service port | Port = `5000` |
| 16 | Optional: Get pod logs (last 10 lines) | Logs accessible |

## Expected Result
* Kubernetes **API accessible**
* Cluster version retrieved successfully
* Namespace **`panda` exists**
* At least **1 Focus Server pod** found
* All Focus Server pods in **`Running` state**
* All pods are **Ready**
* Restart count < 5 (acceptable)
* Service **`panda-panda-focus-server` exists**
* Service has correct ClusterIP and port
* Pod logs accessible
* No API errors or authentication failures

## Post-Conditions
* No cluster state changes
* No pods restarted
* API connection closed gracefully

## Environment

**Kubernetes Cluster**:
- API Server: `https://10.10.100.102:6443`
- Dashboard: `https://10.10.100.102/`
- Namespace: `panda`

**Focus Server Deployment**:
- Deployment Name: `panda-panda-focus-server`
- Service: `panda-panda-focus-server.panda:5000`
- ClusterIP: `10.43.103.101`
- External (LoadBalancer): `10.10.100.100:443`

**SSH Access** (for kubectl):
- Jump Host: `ssh root@10.10.100.3`
- Target Host: `ssh prisma@10.10.100.113`
- Then run: `kubectl get pods -n panda` or `k9s`

## Automation Status

✅ **Automated**

**Framework**: pytest 7.0+  
**Test Function**: `test_kubernetes_connection`  
**Test File**: `tests/integration/infrastructure/test_external_connectivity.py`  
**Test Class**: `TestExternalServicesConnectivity`  
**Lines**: 172-219

**Run Command**:
```bash
# Run Kubernetes connectivity test
pytest tests/integration/infrastructure/test_external_connectivity.py::TestExternalServicesConnectivity::test_kubernetes_connection -v

# Run with markers
pytest -m "kubernetes and infrastructure" -v
```

**Dependencies**:
```python
kubernetes>=28.0.0
```

**Expected Test Duration**: ~3-5 seconds

---

# TEST 4: SSH Connection

## Test ID
**NEW-004** (pending Xray creation)

## Summary
Infrastructure - SSH Access to Production Servers

## Objective
Validates SSH connectivity to production servers through jump host for troubleshooting and maintenance operations. SSH access is critical for accessing logs, executing commands, running k9s, and performing manual interventions when needed.

## Priority
**High**

## Components/Labels
* **Component**: SSH Infrastructure
* **Labels**: `infrastructure`, `ssh`, `connectivity`, `access`, `troubleshooting`
* **Test Type**: Infrastructure Test

## Requirements
* **Requirement ID**: INFRA-SSH-ACCESS-001
* **Description**: SSH access must be available for operational support and troubleshooting

## Pre-Conditions
1. Jump host is running at `10.10.100.3`
2. Target host is running at `10.10.100.113`
3. SSH keys or credentials available
4. Network routing allows SSH connections
5. Firewall rules permit SSH traffic

## Test Data

**SSH Connections**:
```
Jump Host: root@10.10.100.3 (port 22)
Target Host: prisma@10.10.100.113 (port 22)
```

**Test Commands**:
```bash
# On jump host
hostname
whoami
uptime

# On target host  
hostname
whoami
kubectl version --client
k9s version
```

## Steps

| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Import paramiko library: `import paramiko` | Library imported |
| 2 | Create SSH client: `ssh = paramiko.SSHClient()` | Client created |
| 3 | Set missing host key policy: `ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())` | Policy set |
| 4 | Connect to jump host: `ssh.connect('10.10.100.3', username='root', password='***')` | Connection established |
| 5 | Execute test command: `stdin, stdout, stderr = ssh.exec_command('hostname')` | Command executed |
| 6 | Read output: `hostname = stdout.read().decode().strip()` | Hostname returned |
| 7 | Verify no errors in stderr | stderr is empty or minimal |
| 8 | Execute `whoami` command | Returns `root` |
| 9 | Execute `uptime` command | Returns system uptime |
| 10 | Close jump host connection | Connection closed |
| 11 | Connect to target host: `ssh.connect('10.10.100.113', username='prisma', password='***')` | Connection established |
| 12 | Execute `kubectl version --client` | kubectl is installed and working |
| 13 | Execute `k9s version` | k9s is installed |
| 14 | Optional: Execute `kubectl get pods -n panda` | Pods listed |
| 15 | Close target host connection | Connection closed |

## Expected Result
* **Jump host** (`10.10.100.3`) **accessible** via SSH
* **Target host** (`10.10.100.113`) **accessible** via SSH
* Commands execute successfully on both hosts
* `kubectl` available on target host
* `k9s` available on target host
* No authentication failures
* No network timeouts
* Connection latency < 2 seconds

## Post-Conditions
* All SSH connections closed
* No hanging connections
* Hosts remain accessible

## Environment

**SSH Hosts**:
- Jump Host: `10.10.100.3` (user: `root`)
- Target Host: `10.10.100.113` (user: `prisma`)

**Available Tools on Target Host**:
- `kubectl` - Kubernetes CLI
- `k9s` - Kubernetes TUI
- `docker` - Container management

**Connection Path**:
```
Test Client → Jump Host (10.10.100.3) → Target Host (10.10.100.113)
```

## Automation Status

✅ **Automated**

**Framework**: pytest 7.0+  
**Test Function**: `test_ssh_connection`  
**Test File**: `tests/integration/infrastructure/test_external_connectivity.py`  
**Test Class**: `TestExternalServicesConnectivity`  
**Lines**: 304-364

**Run Command**:
```bash
# Run SSH connectivity test
pytest tests/integration/infrastructure/test_external_connectivity.py::TestExternalServicesConnectivity::test_ssh_connection -v

# Run with markers
pytest -m "ssh and infrastructure" -v
```

**Dependencies**:
```python
paramiko>=3.0.0
```

**Expected Test Duration**: ~3-5 seconds

---

# TEST 5: NFFT Variations

## Test ID
**NEW-005** (pending Xray creation)

## Summary
Integration - NFFT Values Validation - All Supported Values

## Objective
Validates that Focus Server accepts and processes all valid NFFT values (128, 256, 512, 1024, 2048, 4096). NFFT (FFT size) determines frequency resolution in spectral analysis. Different NFFT values provide different trade-offs between frequency resolution and time resolution. This test ensures complete NFFT support.

## Priority
**High**

## Components/Labels
* **Component**: Focus Server Backend API
* **Labels**: `config-validation`, `nfft`, `spectrogram`, `fft`, `functional-coverage`
* **Test Type**: Integration Test (Functional)

## Requirements
* **Requirement ID**: FOCUS-API-NFFT-SUPPORT-001
* **Description**: Server must support all standard NFFT values (powers of 2 from 128 to 4096)

## Pre-Conditions
1. Focus Server is running
2. System has adequate resources for all NFFT values
3. Baby Analyzer supports configurable NFFT

## Test Data

**NFFT Values to Test**:
```
[128, 256, 512, 1024, 2048, 4096]
```

**Configuration Template** (for each NFFT):
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": <NFFT_VALUE>,
  "displayInfo": {"height": 1000},
  "channels": {"min": 0, "max": 50},
  "frequencyRange": {"min": 0, "max": 500},
  "start_time": null,
  "end_time": null,
  "view_type": 0
}
```

**Trade-offs by NFFT**:
| NFFT | Frequency Resolution | Update Rate | CPU Load |
|------|---------------------|-------------|----------|
| 128  | Low | Very High | Low |
| 256  | Low | High | Low-Medium |
| 512  | Medium | Medium | Medium |
| 1024 | Good | Medium | Medium-High |
| 2048 | High | Low | High |
| 4096 | Very High | Very Low | Very High |

## Steps

| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | For NFFT in [128, 256, 512, 1024, 2048, 4096]: | Loop through all values |
| 2 | Generate unique `task_id` for this NFFT value | task_id created (e.g., `nfft_test_1024_<timestamp>`) |
| 3 | Create configuration with `nfftSelection = NFFT` | Config payload created |
| 4 | Validate NFFT is power of 2: `NFFT & (NFFT-1) == 0` | Validation passes |
| 5 | Send `POST https://10.10.100.100/focus-server/config/{task_id}` | HTTP 200 OK |
| 6 | Verify response: `"Config received successfully"` | Success status |
| 7 | Optional: Query metadata to verify NFFT was applied | metadata.nfft == NFFT |
| 8 | Optional: Measure configuration time | Time < 5 seconds |
| 9 | Log success for this NFFT value | Success logged |
| 10 | Repeat for next NFFT value | Continue loop |
| 11 | Verify all 6 NFFT values accepted | 100% success rate |

## Expected Result
* **All NFFT values accepted**: 128, 256, 512, 1024, 2048, 4096
* Each configuration returns **HTTP 200 OK**
* No errors or rejections
* Server handles all values without crashes
* Configuration time < 5 seconds for each
* System remains stable throughout test

**NFFT Coverage**:
- ✅ NFFT=128 (lowest, fastest)
- ✅ NFFT=256
- ✅ NFFT=512
- ✅ NFFT=1024 (most common)
- ✅ NFFT=2048
- ✅ NFFT=4096 (highest, best resolution)

## Post-Conditions
* All test tasks can be cleaned up
* System resources released
* No performance degradation

## Environment
**Same as TEST 1** (new_production environment)

## Automation Status

✅ **Automated**

**Framework**: pytest 7.0+  
**Test Function**: `test_nfft_variations`  
**Test File**: `tests/integration/api/test_spectrogram_pipeline.py`  
**Test Class**: `TestNFFTConfiguration`  
**Lines**: 80-97

**Run Command**:
```bash
# Run NFFT variations test
pytest tests/integration/api/test_spectrogram_pipeline.py::TestNFFTConfiguration::test_nfft_variations -v
```

**Expected Test Duration**: ~5-10 seconds (6 configs)

---

# TEST 6: Frequency Range Within Nyquist Limit ⭐ MOST CRITICAL

## Test ID
**NEW-006** (pending Xray creation)

## Summary
Integration - Frequency Range Nyquist Limit Enforcement

## Objective
Validates that Focus Server **enforces the Nyquist-Shannon sampling theorem** and rejects frequency ranges that exceed the Nyquist frequency (PRR/2). This is the **most critical data quality test** because violating Nyquist causes **aliasing** - false frequencies appear in the data, leading to completely incorrect measurements and potentially dangerous decisions.

## Priority
**🔴 CRITICAL**

## Components/Labels
* **Component**: Focus Server Backend API
* **Labels**: `data-quality`, `nyquist`, `aliasing-prevention`, `physics`, `critical`, `validation`
* **Test Type**: Integration Test (Data Quality - Critical)

## Requirements
* **Requirement ID**: FOCUS-API-NYQUIST-ENFORCEMENT-001
* **Description**: Server MUST enforce Nyquist limit: max_frequency ≤ PRR/2 to prevent aliasing

## Pre-Conditions
1. Focus Server is running
2. Live metadata available with accurate PRR value
3. System understands Nyquist limit calculation
4. Validation logic implemented

## Test Data

**Step 1: Get PRR from live_metadata**:
```
GET https://10.10.100.100/focus-server/live_metadata
→ Extract PRR value (e.g., PRR = 1000 samples/sec)
→ Calculate Nyquist = PRR / 2 (e.g., 500 Hz)
```

**Test Data 1: Valid (Below Nyquist)**:
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {"min": 0, "max": 50},
  "frequencyRange": {
    "min": 0,
    "max": 400
  },
  "start_time": null,
  "end_time": null,
  "view_type": 0
}
```
**Note**: If PRR=1000, Nyquist=500, max=400 < 500 ✅ **VALID**

**Test Data 2: Invalid (Above Nyquist)**:
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {"min": 0, "max": 50},
  "frequencyRange": {
    "min": 0,
    "max": 600
  },
  "start_time": null,
  "end_time": null,
  "view_type": 0
}
```
**Note**: If PRR=1000, Nyquist=500, max=600 > 500 ❌ **INVALID** (aliasing!)

**Test Data 3: Exactly at Nyquist (Edge Case)**:
```json
{
  "frequencyRange": {
    "min": 0,
    "max": 500
  }
}
```
**Note**: max=500 == Nyquist - edge case (may be valid or invalid)

## Steps

| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Send `GET https://10.10.100.100/focus-server/live_metadata` | HTTP 200 with metadata |
| 2 | Extract PRR value from metadata | PRR value (e.g., 1000 samples/sec) |
| 3 | Calculate Nyquist frequency: `Nyquist = PRR / 2` | Nyquist value (e.g., 500 Hz) |
| 4 | Log Nyquist limit | `"Nyquist limit: 500 Hz for PRR=1000"` |
| 5 | Generate task_id for Test 1 | Valid task_id |
| 6 | Create config with `freq_max = Nyquist * 0.8` (80% of Nyquist) | Config created with safe frequency |
| 7 | Send `POST https://10.10.100.100/focus-server/config/{task_id}` with Test Data 1 | **HTTP 200 OK** - accepted ✅ |
| 8 | Verify no validation warnings | Config accepted without issues |
| 9 | Generate task_id for Test 2 | Valid task_id |
| 10 | Create config with `freq_max = Nyquist * 1.2` (120% of Nyquist) | Config created with excessive frequency |
| 11 | Send `POST https://10.10.100.100/focus-server/config/{task_id}` with Test Data 2 | **HTTP 400 Bad Request** - rejected ❌ |
| 12 | Verify error message: `"max_freq (600 Hz) exceeds Nyquist frequency (500 Hz)"` | Clear error explaining Nyquist violation |
| 13 | Test edge case: `freq_max = Nyquist` exactly | Document behavior (accept or reject) |
| 14 | Verify system remains stable after rejection | No crashes or side effects |

## Expected Result
* **PRR extracted** successfully from live_metadata
* **Nyquist calculated** correctly: `Nyquist = PRR / 2`
* **Frequency below Nyquist** (80%) is **ACCEPTED** ✅
* **Frequency above Nyquist** (120%) is **REJECTED** ❌
* Error message clearly states:
  - Requested frequency
  - Nyquist limit
  - Current PRR
* Edge case (freq == Nyquist) behavior **documented**
* **No aliasing possible** - data integrity protected

**Critical**: This is a **physics-based validation** - not just software correctness!

## Post-Conditions
* No tasks created for invalid configs
* Valid task may exist for below-Nyquist config
* System stable
* **Data quality protected** from aliasing

## Environment
**Same as TEST 1** (new_production environment)

**Critical Note**:
- PRR value is **system-dependent** (varies by fiber config)
- Test must **dynamically calculate** Nyquist from live_metadata
- Cannot use hardcoded values

## Automation Status

✅ **Automated**

**Framework**: pytest 7.0+  
**Test Function**: `test_frequency_range_within_nyquist`  
**Test File**: `tests/integration/api/test_spectrogram_pipeline.py`  
**Test Class**: `TestFrequencyConfiguration`  
**Lines**: 127-157

**Run Command**:
```bash
# Run Nyquist validation test
pytest tests/integration/api/test_spectrogram_pipeline.py::TestFrequencyConfiguration::test_frequency_range_within_nyquist -v
```

**Dependencies**:
```python
# Requires live_metadata fixture
```

**Expected Test Duration**: ~2-3 seconds

**⚠️ WARNING**: This is the **MOST CRITICAL** test for data quality. Failure to enforce Nyquist limit results in **CORRUPTED DATA**.

---

# TEST 7: Configuration Resource Estimation

## Test ID
**NEW-007** (pending Xray creation)

## Summary
Integration - Configuration Resource Usage Estimation

## Objective
Calculates and validates estimated resource usage (CPU, Memory, Network Bandwidth) for a given configuration before task creation. This allows capacity planning and prevents configurations that would exhaust system resources. The test verifies that the system can predict resource requirements accurately.

## Priority
**High**

## Components/Labels
* **Component**: Focus Server Backend API
* **Labels**: `performance`, `resource-planning`, `capacity`, `estimation`, `validation`
* **Test Type**: Integration Test (Performance)

## Requirements
* **Requirement ID**: FOCUS-API-RESOURCE-ESTIMATION-001
* **Description**: System should estimate resource usage and warn about expensive configurations

## Pre-Conditions
1. Focus Server has resource estimation logic
2. System knows performance characteristics (CPU per NFFT, etc.)
3. Validation utilities available

## Test Data

**Test Configuration** (Medium Load):
```json
{
  "nfftSelection": 1024,
  "channels": {"min": 0, "max": 50},
  "frequencyRange": {"min": 0, "max": 500},
  "displayInfo": {"height": 1000}
}
```

**Expected Calculations**:
```
PRR = 1000 samples/sec (from metadata)
NFFT = 1024
Sensor Range = 50
Frequency Bins = NFFT/2 = 512

Spectrogram rows/sec = PRR / NFFT = 1000 / 1024 ≈ 0.98 rows/sec
Bytes per row = sensors × freq_bins × 4 bytes = 50 × 512 × 4 = 102,400 bytes
Output data rate = rows/sec × bytes/row × 8 = 0.98 × 102,400 × 8 ≈ 0.8 Mbps
```

## Steps

| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Get live metadata to extract PRR | PRR value retrieved |
| 2 | Define test configuration (Test Data) | Config defined |
| 3 | Calculate NFFT value from config | NFFT = 1024 |
| 4 | Calculate sensor range: `max - min` | Range = 50 |
| 5 | Calculate spectrogram rows/sec: `PRR / NFFT` | ~0.98 rows/sec |
| 6 | Calculate frequency bins: `NFFT / 2` | 512 bins |
| 7 | Calculate bytes per row: `sensors × bins × 4` | 102,400 bytes/row |
| 8 | Calculate output data rate (Mbps): `rows/sec × bytes/row × 8 / 1,000,000` | ~0.8 Mbps |
| 9 | Verify estimates are reasonable: `0.1 < rate < 100 Mbps` | Within reasonable bounds |
| 10 | Check for warnings: rate > 50 Mbps? | No warning (rate is low) |
| 11 | Verify compatibility: `validate_configuration_compatibility()` | Returns `is_compatible: True` |
| 12 | Log estimates for documentation | Estimates logged |

## Expected Result
* **Estimates calculated** successfully:
  - Spectrogram rows/sec
  - Bytes per row
  - Output data rate (Mbps)
* **Estimates are reasonable**:
  - Rows/sec: 0.1 - 1000
  - Data rate: 0.1 - 100 Mbps
* **Warnings issued** for extreme configs:
  - Warning if rate > 50 Mbps
  - Warning if rows/sec > 1000
  - Warning if rows/sec < 1
* **Compatibility validated**
* No calculation errors or exceptions

## Post-Conditions
* No tasks created (estimation only)
* Calculations documented for capacity planning

## Environment
**Same as TEST 1** (new_production environment)

## Automation Status

✅ **Automated**

**Framework**: pytest 7.0+  
**Test Function**: `test_configuration_resource_estimation`  
**Test File**: `tests/integration/api/test_spectrogram_pipeline.py`  
**Test Class**: `TestSpectrogramPipeline`  
**Lines**: 246-268

**Run Command**:
```bash
pytest tests/integration/api/test_spectrogram_pipeline.py::test_configuration_resource_estimation -v
```

**Expected Test Duration**: ~1-2 seconds

---

# TEST 8: High Throughput Configuration

## Test ID
**NEW-008** (pending Xray creation)

## Summary
Performance - High Throughput Configuration Stress Test

## Objective
Tests configuration with **very high data throughput** (> 50 Mbps) to verify system behavior under heavy load. High throughput occurs with: many sensors, small NFFT (more rows/sec), wide frequency range. This test identifies system limits and validates warnings/rejections for excessive configurations.

## Priority
**High**

## Components/Labels
* **Component**: Focus Server Backend API
* **Labels**: `performance`, `stress-test`, `high-throughput`, `capacity`, `limits`
* **Test Type**: Performance Test (Stress)

## Requirements
* **Requirement ID**: FOCUS-API-HIGH-THROUGHPUT-001
* **Description**: System must handle or reject high-throughput configurations gracefully

## Pre-Conditions
1. Focus Server is running with adequate resources
2. System under normal load (not already stressed)
3. Network can handle high bandwidth

## Test Data

**High Throughput Configuration**:
```json
{
  "nfftSelection": 512,
  "displayInfo": {"height": 2000},
  "channels": {
    "min": 0,
    "max": 200
  },
  "frequencyRange": {
    "min": 0,
    "max": 2000
  },
  "view_type": 0
}
```

**Why High Throughput?**
- Small NFFT (512) → many rows/sec
- Many sensors (200)
- Wide frequency range (2000 Hz)

**Expected Calculation**:
```
PRR = 1000 samples/sec
Rows/sec = 1000 / 512 ≈ 1.95 rows/sec
Bytes/row = 200 sensors × 256 bins × 4 bytes = 204,800 bytes
Data rate = 1.95 × 204,800 × 8 / 1,000,000 ≈ 3.2 Mbps (actually not that high)

To get > 50 Mbps, need:
NFFT = 256, sensors = 500, freq_range = 4000
```

**Adjusted High Throughput Config**:
```json
{
  "nfftSelection": 256,
  "channels": {"min": 0, "max": 500},
  "frequencyRange": {"min": 0, "max": 4000}
}
```

## Steps

| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Get PRR from live_metadata | PRR retrieved (e.g., 1000) |
| 2 | Design config to produce > 50 Mbps throughput | Config created |
| 3 | Calculate expected throughput using estimation formula | Expected: > 50 Mbps |
| 4 | Generate task_id | Valid task_id |
| 5 | Send `POST https://10.10.100.100/focus-server/config/{task_id}` | Response received |
| 6 | Check response: **Option A**: Accepted with warning | Status 200 + warning in response or logs |
| 7 | Check response: **Option B**: Rejected as too expensive | Status 400 + error: "Configuration exceeds throughput limit" |
| 8 | If accepted, monitor actual throughput (optional) | Actual throughput measured |
| 9 | Verify system stability | No crashes or resource exhaustion |
| 10 | Document behavior for specs meeting | Behavior logged |

## Expected Result

**Behavior Options** (to be defined in specs meeting):

**Option A: Accept with Warning**
- HTTP 200 OK
- Warning logged: "High throughput configuration: 75 Mbps"
- Task created
- System monitors resources

**Option B: Reject**
- HTTP 400 Bad Request
- Error: "Configuration throughput (75 Mbps) exceeds system limit (50 Mbps)"
- No task created
- Suggestion provided: "Reduce sensor range or increase NFFT"

**Either way**:
- System remains stable
- No crashes or hangs
- Clear feedback to client

## Post-Conditions
* If accepted: task may consume high resources
* If rejected: no task created
* System stable

## Environment
**Same as TEST 1** (new_production environment)

## Automation Status

✅ **Automated**

**Framework**: pytest 7.0+  
**Test Function**: `test_high_throughput_configuration`  
**Test File**: `tests/integration/api/test_spectrogram_pipeline.py`  
**Test Class**: `TestSpectrogramPipeline`  
**Lines**: 270-302

**Run Command**:
```bash
pytest tests/integration/api/test_spectrogram_pipeline.py::test_high_throughput_configuration -v
```

**Expected Test Duration**: ~2-5 seconds

---

# TEST 9: Low Throughput Configuration

## Test ID
**NEW-009** (pending Xray creation)

## Summary
Integration - Low Throughput Configuration Edge Case

## Objective
Tests configuration with **very low data throughput** (< 1 Mbps) to verify system behavior at the lower performance boundary. Low throughput occurs with: few sensors, large NFFT (fewer rows/sec), narrow frequency range. Validates that low-throughput configs are handled correctly.

## Priority
**Medium-High**

## Components/Labels
* **Component**: Focus Server Backend API
* **Labels**: `performance`, `edge-case`, `low-throughput`, `minimal-config`
* **Test Type**: Integration Test (Edge Case)

## Requirements
* **Requirement ID**: FOCUS-API-LOW-THROUGHPUT-001
* **Description**: System should accept low-throughput configurations (unless below minimum viable)

## Pre-Conditions
1. Focus Server is running
2. System supports low-throughput scenarios
3. Minimum viable configuration defined (or to be determined)

## Test Data

**Low Throughput Configuration**:
```json
{
  "nfftSelection": 4096,
  "displayInfo": {"height": 500},
  "channels": {
    "min": 5,
    "max": 10
  },
  "frequencyRange": {
    "min": 100,
    "max": 200
  },
  "view_type": 0
}
```

**Why Low Throughput?**
- Large NFFT (4096) → few rows/sec
- Few sensors (5)
- Narrow frequency range (100 Hz)

**Expected Calculation**:
```
PRR = 1000 samples/sec
Rows/sec = 1000 / 4096 ≈ 0.24 rows/sec (very slow!)
Bytes/row = 5 sensors × 2048 bins × 4 bytes = 40,960 bytes
Data rate = 0.24 × 40,960 × 8 / 1,000,000 ≈ 0.08 Mbps (very low)
```

## Steps

| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Get PRR from live_metadata | PRR retrieved |
| 2 | Create low-throughput config (Test Data) | Config created |
| 3 | Calculate expected throughput | Expected: < 1 Mbps |
| 4 | Verify rows/sec < 1 | Very slow update rate |
| 5 | Generate task_id | Valid task_id |
| 6 | Send `POST https://10.10.100.100/focus-server/config/{task_id}` | Response received |
| 7 | Verify response: **likely accepted** | HTTP 200 OK (low throughput is OK) |
| 8 | Check for warnings: "Low spectrogram rate: 0.24 rows/sec" | Warning issued (optional) |
| 9 | Verify task can be created | Task created successfully |
| 10 | Document if minimum viable throughput exists | Behavior logged for specs |

## Expected Result

**Expected Behavior**:
- HTTP 200 OK - **configuration accepted**
- Optional warning: "Low update rate: 0.24 rows/sec"
- Task created successfully
- System operates (albeit slowly)

**Questions for Specs Meeting**:
- Is there a **minimum** rows/sec? (e.g., must be > 0.1)
- Is there a **minimum** data rate? (e.g., must be > 0.01 Mbps)
- Should system **warn** or **reject** very low configs?

## Post-Conditions
* Task created (if accepted)
* System stable
* Low resource usage

## Environment
**Same as TEST 1** (new_production environment)

## Automation Status

✅ **Automated**

**Framework**: pytest 7.0+  
**Test Function**: `test_low_throughput_configuration`  
**Test File**: `tests/integration/api/test_spectrogram_pipeline.py`  
**Test Class**: `TestSpectrogramPipeline`  
**Lines**: 304-343

**Run Command**:
```bash
pytest tests/integration/api/test_spectrogram_pipeline.py::test_low_throughput_configuration -v
```

**Expected Test Duration**: ~2-3 seconds

---

# TEST 10: Configuration Missing start_time (Historic)

## Test ID
**NEW-010** (pending Xray creation)

## Summary
Integration - Historic Configuration Missing start_time Field

## Objective
Validates that Focus Server properly **rejects** historic playback configurations that are missing the **required** `start_time` field. Historic mode requires both `start_time` and `end_time` to define the playback time range. Missing `start_time` should result in clear validation error.

## Priority
**High**

## Components/Labels
* **Component**: Focus Server Backend API
* **Labels**: `config-validation`, `historic-playback`, `required-fields`, `negative-test`
* **Test Type**: Integration Test (Negative)

## Requirements
* **Requirement ID**: FOCUS-API-HISTORIC-VALIDATION-001
* **Description**: Historic configurations must include both start_time and end_time fields

## Pre-Conditions
1. Focus Server is running
2. Historic playback validation implemented
3. Required field validation logic exists

## Test Data

**Invalid Configuration** (missing start_time):
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {"min": 0, "max": 50},
  "frequencyRange": {"min": 0, "max": 500},
  "end_time": "251021120000",
  "view_type": 0
}
```
**Note**: Has `end_time` but **missing `start_time`** - should be rejected

## Steps

| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Generate unique task_id | Valid task_id |
| 2 | Create historic configuration **without** `start_time` (Test Data) | Payload created |
| 3 | Verify `end_time` is present but `start_time` is null/missing | start_time missing ✅ |
| 4 | Attempt to send `POST https://10.10.100.100/focus-server/config/{task_id}` | Request sent or validation fails |
| 5 | **Expected**: Receive HTTP 400 Bad Request | Status 400 |
| 6 | Verify error message contains "start_time" | Error mentions missing field |
| 7 | Verify error message is descriptive: `"Historic playback requires start_time field"` | Clear error message |
| 8 | Verify no task created in MongoDB: `db.tasks.find({task_id: task_id})` | No task found |
| 9 | Verify server logs validation error | Error logged |
| 10 | Verify server remains stable | No crashes |

## Expected Result
* Configuration **rejected** with **HTTP 400 Bad Request**
* Error message clearly indicates:
  - Missing field: `start_time`
  - Required for: historic playback
  - Example: `"start_time is required for historic playback mode"`
* **No task created** in the system
* Server stable and responsive
* Validation happens **before** any processing

## Post-Conditions
* No task created
* MongoDB state unchanged
* Server stable

## Environment
**Same as TEST 1** (new_production environment)

## Automation Status

⚠️ **To Be Automated**

**Framework**: pytest 7.0+  
**Test Function**: `test_config_with_missing_start_time` (TO CREATE)  
**Test File**: `tests/integration/api/test_historic_playback_flow.py` (add to existing file)  
**Test Class**: `TestHistoricPlaybackValidation` (new class)  

**Proposed Run Command**:
```bash
pytest tests/integration/api/test_historic_playback_flow.py::TestHistoricPlaybackValidation::test_config_with_missing_start_time -v
```

**Status**: ❌ Not yet implemented - needs to be created

**Expected Test Duration**: ~1 second

---

# TEST 11: Configuration Missing end_time (Historic)

## Test ID
**NEW-011** (pending Xray creation)

## Summary
Integration - Historic Configuration Missing end_time Field

## Objective
Validates that Focus Server properly **rejects** historic playback configurations that are missing the **required** `end_time` field. This is the pair test to NEW-010, ensuring both time boundaries are validated.

## Priority
**High**

## Components/Labels
* **Component**: Focus Server Backend API
* **Labels**: `config-validation`, `historic-playback`, `required-fields`, `negative-test`
* **Test Type**: Integration Test (Negative)

## Requirements
* **Requirement ID**: FOCUS-API-HISTORIC-VALIDATION-002
* **Description**: Historic configurations must include both start_time and end_time fields

## Pre-Conditions
1. Focus Server is running
2. Historic playback validation implemented
3. Required field validation logic exists

## Test Data

**Invalid Configuration** (missing end_time):
```json
{
  "displayTimeAxisDuration": 10,
  "nfftSelection": 1024,
  "displayInfo": {"height": 1000},
  "channels": {"min": 0, "max": 50},
  "frequencyRange": {"min": 0, "max": 500},
  "start_time": "251021120000",
  "view_type": 0
}
```
**Note**: Has `start_time` but **missing `end_time`** - should be rejected

## Steps

| # | Step Description | Expected Result |
|---|------------------|-----------------|
| 1 | Generate unique task_id | Valid task_id |
| 2 | Create historic configuration **without** `end_time` (Test Data) | Payload created |
| 3 | Verify `start_time` is present but `end_time` is null/missing | end_time missing ✅ |
| 4 | Attempt to send `POST https://10.10.100.100/focus-server/config/{task_id}` | Request sent or validation fails |
| 5 | **Expected**: Receive HTTP 400 Bad Request | Status 400 |
| 6 | Verify error message contains "end_time" | Error mentions missing field |
| 7 | Verify error message is descriptive: `"Historic playback requires end_time field"` | Clear error message |
| 8 | Verify no task created in MongoDB: `db.tasks.find({task_id: task_id})` | No task found |
| 9 | Verify server logs validation error | Error logged |
| 10 | Verify server remains stable | No crashes |

## Expected Result
* Configuration **rejected** with **HTTP 400 Bad Request**
* Error message clearly indicates:
  - Missing field: `end_time`
  - Required for: historic playback
  - Example: `"end_time is required for historic playback mode"`
* **No task created** in the system
* Server stable and responsive
* Validation happens **before** any processing

## Post-Conditions
* No task created
* MongoDB state unchanged
* Server stable

## Environment
**Same as TEST 1** (new_production environment)

## Automation Status

⚠️ **To Be Automated**

**Framework**: pytest 7.0+  
**Test Function**: `test_config_with_missing_end_time` (TO CREATE)  
**Test File**: `tests/integration/api/test_historic_playback_flow.py` (add to existing file)  
**Test Class**: `TestHistoricPlaybackValidation` (new class)  

**Proposed Run Command**:
```bash
pytest tests/integration/api/test_historic_playback_flow.py::TestHistoricPlaybackValidation::test_config_with_missing_end_time -v
```

**Status**: ❌ Not yet implemented - needs to be created

**Expected Test Duration**: ~1 second

---

## 📊 Summary - All 9 Tests

| Test # | Test ID | Summary | Priority | Status |
|--------|---------|---------|----------|--------|
| 1 | NEW-001 | GET /sensors Endpoint | High | ✅ Automated |
| 2 | NEW-002 | MongoDB Connection | High | ✅ Automated |
| 3 | NEW-003 | Kubernetes Connection | High | ✅ Automated |
| 4 | NEW-004 | SSH Connection | High | ✅ Automated |
| 5 | NEW-005 | NFFT Variations | High | ✅ Automated |
| 6 | NEW-006 | Nyquist Limit ⭐ | **CRITICAL** | ✅ Automated |
| 7 | NEW-007 | Resource Estimation | High | ✅ Automated |
| 8 | NEW-008 | High Throughput | High | ✅ Automated |
| 9 | NEW-009 | Low Throughput | High | ✅ Automated |
| 10 | NEW-010 | Missing start_time | High | ❌ To Create |
| 11 | NEW-011 | Missing end_time | High | ❌ To Create |

**Ready for Xray**: 9 tests (1-9)  
**Need to Create**: 2 tests (10-11)  

**Total Duration**: ~20-30 seconds for all 9 automated tests

---

## 🎯 Next Steps

### 1. Create Xray Test Cases (9 tests):
- Copy each test documentation above to Jira Xray
- Assign PZ-XXXXX IDs
- Link to automation code
- Mark as "Automated"

### 2. Create Missing Tests in Code (2 tests):
- NEW-010: `test_config_with_missing_start_time`
- NEW-011: `test_config_with_missing_end_time`

### 3. Update Existing Tests in Xray:
- Add automation status
- Link to code files
- Update test steps to match actual implementation

---

**Document Status:** ✅ Ready for Xray Import  
**Format**: Full Xray specification  
**Code References**: Included (but no embedded Python)  
**Environment**: Complete production details
