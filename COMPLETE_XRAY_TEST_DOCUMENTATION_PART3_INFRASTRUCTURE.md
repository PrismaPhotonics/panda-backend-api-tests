# 📋 Complete Xray Test Documentation - Part 3: Infrastructure Tests (25 Tests)

**Generated:** 2025-10-20  
**Category:** Infrastructure Connectivity & Health  
**Total Tests:** 25  
**Source Files:** `tests/integration/infrastructure/test_basic_connectivity.py`, `test_external_connectivity.py`, `test_pz_integration.py`

---

## SECTION A: MongoDB Tests (8 Tests)

---

## TC-INFRA-001: MongoDB Direct Connection

**Summary:** Infrastructure – MongoDB Direct TCP Connection and Authentication

**Objective:** Verify Focus Server can establish direct TCP connection to MongoDB server, authenticate successfully, and execute basic ping command.

**Priority:** Critical

**Components/Labels:** focus-server, mongodb, infrastructure, database, connectivity

**Requirements:** FOCUS-INFRA-MONGODB, FOCUS-DB-CONNECTION

**Pre-Conditions:**
- PC-001: MongoDB server running at configured host/port
- PC-002: MongoDB credentials configured (username/password)
- PC-003: Authentication database accessible
- PC-004: pymongo client library installed

**Test Data:**
```json
MongoDB Configuration:
{
  "host": "10.10.100.108",
  "port": 27017,
  "username": "prisma",
  "password": "prisma",
  "auth_source": "prisma",
  "database": "prisma",
  "connection_timeout_ms": 10000,
  "server_selection_timeout_ms": 10000
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Load MongoDB config | ConfigManager("new_production") | Config loaded |
| 2 | Create MongoClient | host, port, credentials | Client created |
| 3 | Establish TCP connection | - | Connection established |
| 4 | Authenticate | authSource="prisma" | Authentication success |
| 5 | Send ping command | client.admin.command('ping') | {'ok': 1.0} |
| 6 | Get server info | client.server_info() | Version returned |
| 7 | List databases | client.list_database_names() | Database list returned |
| 8 | Verify prisma DB exists | "prisma" in db_list | True |
| 9 | Close connection | client.close() | Clean disconnect |

**Expected Result (overall):**
- TCP connection to MongoDB successful
- Authentication passes with prisma/prisma credentials
- Ping command returns {'ok': 1.0}
- Server version retrieved (e.g., "7.0.5")
- Database list includes "prisma"
- Connection closes cleanly without errors

**Post-Conditions:**
- MongoDB connection closed
- No hanging connections

**Assertions:**
```python
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

config_manager = ConfigManager("new_production")
mongo_config = config_manager.get_database_config()

# Create client
client = MongoClient(
    host=mongo_config["host"],  # 10.10.100.108
    port=mongo_config["port"],  # 27017
    username=mongo_config["username"],  # prisma
    password=mongo_config["password"],  # prisma
    authSource=mongo_config.get("auth_source", "admin"),
    serverSelectionTimeoutMS=10000,
    connectTimeoutMS=10000,
    socketTimeoutMS=10000
)

# Test connection with ping
ping_result = client.admin.command('ping')
assert ping_result['ok'] == 1.0

# Get server info
server_info = client.server_info()
assert 'version' in server_info
logger.info(f"MongoDB Version: {server_info['version']}")

# List databases
db_list = client.list_database_names()
assert 'prisma' in db_list
assert len(db_list) > 0

# Close
client.close()
logger.info("✅ MongoDB connectivity test PASSED")
```

**Environment:** Staging, Production

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_mongodb_direct_connection`  
**Test File:** `tests/integration/infrastructure/test_basic_connectivity.py`

---

## TC-INFRA-002: MongoDB Connection (Managed via ConfigManager)

**Summary:** Infrastructure – MongoDB Connection Using Focus Server Config

**Objective:** Verify MongoDB connection works using Focus Server's ConfigManager for consistent configuration across application.

**Priority:** High

**Components/Labels:** focus-server, mongodb, config-manager

**Requirements:** FOCUS-CONFIG-MONGODB

**Pre-Conditions:**
- PC-001: ConfigManager configured
- PC-002: MongoDB config in environments.yaml

**Test Data:**
```yaml
new_production:
  mongodb:
    host: "10.10.100.108"
    port: 27017
    username: "prisma"
    password: "prisma"
    database: "prisma"
    auth_source: "prisma"
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Initialize ConfigManager | env="new_production" | Manager created |
| 2 | Get database config | get_database_config() | Config dict returned |
| 3 | Verify host | config["host"] | "10.10.100.108" |
| 4 | Verify port | config["port"] | 27017 |
| 5 | Create MongoDB client | Using config | Client created |
| 6 | Test connection | ping | Success |

**Expected Result (overall):**
- ConfigManager loads MongoDB config correctly
- All connection parameters accurate
- Connection successful using config

**Post-Conditions:**
- Connection closed

**Assertions:**
```python
config_manager = ConfigManager("new_production")
mongo_config = config_manager.get_database_config()

assert mongo_config["host"] == "10.10.100.108"
assert mongo_config["port"] == 27017
assert mongo_config["username"] == "prisma"
assert mongo_config["database"] == "prisma"

# Test connection with config
client = MongoClient(**mongo_config)
ping_result = client.admin.command('ping')
assert ping_result['ok'] == 1.0

client.close()
logger.info("✅ MongoDB connection via ConfigManager works")
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_mongodb_connection`  
**Test File:** `tests/integration/infrastructure/test_basic_connectivity.py`

---

## TC-INFRA-003: MongoDB Status via Kubernetes

**Summary:** Infrastructure – Query MongoDB Status Through Kubernetes API

**Objective:** Verify MongoDB pod is running and healthy in Kubernetes cluster.

**Priority:** High

**Components/Labels:** mongodb, kubernetes, infrastructure, pod-status

**Requirements:** FOCUS-K8S-MONGODB

**Pre-Conditions:**
- PC-001: Kubernetes API accessible
- PC-002: Namespace "panda" exists
- PC-003: MongoDB deployed as pod/statefulset

**Test Data:**
```json
Kubernetes:
{
  "namespace": "panda",
  "pod_label": "app.kubernetes.io/name=mongodb",
  "service_name": "mongodb"
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Load kubeconfig | config.load_kube_config() | Config loaded |
| 2 | Create CoreV1Api client | - | Client created |
| 3 | List pods in namespace | namespace="panda" | Pod list returned |
| 4 | Find MongoDB pods | label_selector="app=mongodb" | Pod(s) found |
| 5 | Check pod status | pod.status.phase | "Running" |
| 6 | Check container ready | container.ready | True |
| 7 | Get service info | mongodb.panda:27017 | Service exists |

**Expected Result (overall):**
- MongoDB pod(s) found in panda namespace
- Pod status is "Running"
- All containers ready
- Service "mongodb" accessible

**Post-Conditions:**
- None

**Assertions:**
```python
from kubernetes import client, config

config.load_kube_config()
v1 = client.CoreV1Api()

# List pods
pods = v1.list_namespaced_pod(
    namespace="panda",
    label_selector="app.kubernetes.io/name=mongodb"
)

assert len(pods.items) > 0, "No MongoDB pods found"

# Check each pod
for pod in pods.items:
    logger.info(f"MongoDB Pod: {pod.metadata.name}")
    assert pod.status.phase == "Running", f"Pod not running: {pod.status.phase}"
    
    # Check containers
    for container_status in pod.status.container_statuses:
        assert container_status.ready == True, f"Container not ready"

logger.info("✅ MongoDB pod healthy in Kubernetes")
```

**Environment:** Production (K8s)

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_mongodb_status_via_kubernetes`  
**Test File:** `tests/integration/infrastructure/test_basic_connectivity.py`

---

## TC-INFRA-004: MongoDB Quick Ping (Performance)

**Summary:** Infrastructure – MongoDB Quick Response Time Test

**Objective:** Verify MongoDB responds to ping within acceptable time limit (<100ms).

**Priority:** Medium

**Components/Labels:** mongodb, performance, latency

**Requirements:** FOCUS-MONGO-PERFORMANCE

**Pre-Conditions:**
- PC-001: MongoDB accessible
- PC-002: Normal load conditions

**Test Data:**
```json
Performance Criteria:
{
  "max_response_time_ms": 100,
  "acceptable_response_time_ms": 50
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Connect to MongoDB | - | Connected |
| 2 | Record start time | time.time() | Timestamp captured |
| 3 | Send ping command | client.admin.command('ping') | Response received |
| 4 | Record end time | time.time() | Timestamp captured |
| 5 | Calculate latency | (end - start) * 1000 | Latency in ms |
| 6 | Verify latency | latency < 100ms | Pass if under threshold |
| 7 | Log result | - | Latency logged |

**Expected Result (overall):**
- Ping response time < 100ms
- Ideally < 50ms
- Consistent performance

**Post-Conditions:**
- Connection closed

**Assertions:**
```python
import time

client = MongoClient(host="10.10.100.108", port=27017)

# Measure ping time
start_time = time.time()
ping_result = client.admin.command('ping')
end_time = time.time()

latency_ms = (end_time - start_time) * 1000

assert ping_result['ok'] == 1.0
assert latency_ms < 100, f"MongoDB ping too slow: {latency_ms:.2f}ms"

logger.info(f"✅ MongoDB ping: {latency_ms:.2f}ms")

if latency_ms < 50:
    logger.info("⚡ Excellent latency!")
elif latency_ms < 100:
    logger.info("✓ Acceptable latency")

client.close()
```

**Environment:** All

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_quick_mongodb_ping`  
**Test File:** `tests/integration/infrastructure/test_basic_connectivity.py`

---

## TC-INFRA-005: MongoDB Collections Exist

**Summary:** Data Quality – Verify Required MongoDB Collections Exist

**Objective:** Confirm all required MongoDB collections exist for Focus Server operation.

**Priority:** Critical

**Components/Labels:** mongodb, data-quality, collections

**Requirements:** FOCUS-MONGO-SCHEMA

**Pre-Conditions:**
- PC-001: MongoDB accessible
- PC-002: Database "prisma" exists

**Test Data:**
```json
Required Collections:
[
  "recordings",
  "node4",
  "tasks",
  "jobs"
]
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Connect to MongoDB | database="prisma" | Connected |
| 2 | List collections | db.list_collection_names() | Collection list |
| 3 | Verify "recordings" | "recordings" in collections | True |
| 4 | Verify "node4" | "node4" in collections | True |
| 5 | Verify "tasks" | "tasks" in collections | True |
| 6 | Verify "jobs" | "jobs" in collections | True |
| 7 | Check collection counts | db[col].count_documents({}) | >= 0 |

**Expected Result (overall):**
- All required collections exist
- Collections are accessible
- No permission errors

**Post-Conditions:**
- None

**Assertions:**
```python
client = MongoClient(host="10.10.100.108", port=27017,
                     username="prisma", password="prisma")
db = client["prisma"]

collections = db.list_collection_names()

required_collections = ["recordings", "node4", "tasks", "jobs"]

for col_name in required_collections:
    assert col_name in collections, f"Collection '{col_name}' not found"
    logger.info(f"✓ Collection '{col_name}' exists")
    
    # Check accessible
    count = db[col_name].count_documents({})
    logger.info(f"  Documents: {count}")

logger.info("✅ All required collections exist")
client.close()
```

**Environment:** Production

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_required_collections_exist`  
**Test File:** `tests/integration/infrastructure/test_mongodb_data_quality.py`

---

## TC-INFRA-006: MongoDB Indexes Validation

**Summary:** Data Quality – Verify Critical MongoDB Indexes Exist

**Objective:** Confirm performance-critical indexes exist on recordings collection.

**Priority:** High

**Components/Labels:** mongodb, indexes, performance

**Requirements:** FOCUS-MONGO-INDEXES

**Pre-Conditions:**
- PC-001: recordings collection exists
- PC-002: Index creation completed

**Test Data:**
```json
Required Indexes on "recordings":
[
  {"field": "start_time", "type": "ascending"},
  {"field": "end_time", "type": "ascending"},
  {"field": "uuid", "type": "ascending"},
  {"field": "_id", "type": "ascending"}
]
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Connect to MongoDB | - | Connected |
| 2 | Get recordings collection | db["recordings"] | Collection object |
| 3 | List indexes | collection.list_indexes() | Index list |
| 4 | Verify start_time index | "start_time_1" in indexes | True |
| 5 | Verify end_time index | "end_time_1" in indexes | True |
| 6 | Verify uuid index | "uuid_1" in indexes | True |
| 7 | Log index details | - | All indexes logged |

**Expected Result (overall):**
- start_time index exists
- end_time index exists
- uuid index exists
- All indexes are ascending

**Post-Conditions:**
- None

**Assertions:**
```python
client = MongoClient(host="10.10.100.108", port=27017,
                     username="prisma", password="prisma")
db = client["prisma"]
collection = db["recordings"]

# Get indexes
indexes = list(collection.list_indexes())
index_names = [idx['name'] for idx in indexes]

logger.info(f"Found {len(indexes)} indexes:")
for idx in indexes:
    logger.info(f"  - {idx['name']}: {idx['key']}")

# Verify required indexes
required_indexes = ["start_time_1", "end_time_1", "uuid_1"]

for idx_name in required_indexes:
    assert idx_name in index_names, f"Missing index: {idx_name}"
    logger.info(f"✓ Index '{idx_name}' exists")

logger.info("✅ All critical indexes exist")
client.close()
```

**Environment:** Production

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_mongodb_indexes_exist_and_optimal`  
**Test File:** `tests/integration/infrastructure/test_mongodb_data_quality.py`

---

## TC-INFRA-007: MongoDB Recordings Schema Validation

**Summary:** Data Quality – Validate Recordings Document Schema

**Objective:** Verify recordings in MongoDB have all required fields with correct data types.

**Priority:** High

**Components/Labels:** mongodb, data-quality, schema, recordings

**Requirements:** FOCUS-MONGO-SCHEMA

**Pre-Conditions:**
- PC-001: recordings collection has data
- PC-002: At least one recording exists

**Test Data:**
```json
Required Recording Fields:
{
  "uuid": "string",
  "start_time": "number (epoch)",
  "end_time": "number (epoch)",
  "path": "string",
  "node": "string",
  "sensor_min": "number",
  "sensor_max": "number"
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Connect to MongoDB | - | Connected |
| 2 | Query recent recording | limit=1, sort=-start_time | Recording found |
| 3 | Verify uuid field | type(doc["uuid"]) | str |
| 4 | Verify start_time | type(doc["start_time"]) | int/float |
| 5 | Verify end_time | type(doc["end_time"]) | int/float |
| 6 | Verify path | type(doc["path"]) | str |
| 7 | Check start < end | start_time < end_time | True |
| 8 | Validate all required fields | - | All present |

**Expected Result (overall):**
- Recording has all required fields
- Field types correct
- start_time < end_time
- uuid is valid string
- path is valid file path

**Post-Conditions:**
- None

**Assertions:**
```python
client = MongoClient(host="10.10.100.108", port=27017,
                     username="prisma", password="prisma")
db = client["prisma"]
recordings = db["recordings"]

# Get one recording
recording = recordings.find_one(sort=[("start_time", -1)])

assert recording is not None, "No recordings found"

# Validate schema
required_fields = ["uuid", "start_time", "end_time", "path"]

for field in required_fields:
    assert field in recording, f"Missing field: {field}"
    logger.info(f"✓ Field '{field}' present")

# Validate types
assert isinstance(recording["uuid"], str)
assert isinstance(recording["start_time"], (int, float))
assert isinstance(recording["end_time"], (int, float))
assert isinstance(recording["path"], str)

# Validate logic
assert recording["start_time"] < recording["end_time"], "Invalid time range"

logger.info("✅ Recording schema valid")
client.close()
```

**Environment:** Production

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_recording_schema_validation`  
**Test File:** `tests/integration/infrastructure/test_mongodb_data_quality.py`

---

## TC-INFRA-008: MongoDB Recordings Metadata Completeness

**Summary:** Data Quality – Verify Recordings Have Complete Metadata

**Objective:** Confirm recordings have all required metadata fields populated (not null/empty).

**Priority:** Medium

**Components/Labels:** mongodb, data-quality, metadata

**Requirements:** FOCUS-MONGO-METADATA

**Pre-Conditions:**
- PC-001: recordings collection accessible
- PC-002: Sample size >= 10 recordings

**Test Data:**
```json
Required Non-Empty Fields:
[
  "uuid",
  "start_time",
  "end_time",
  "path",
  "node"
]
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Connect to MongoDB | - | Connected |
| 2 | Query 10 recent recordings | limit=10 | Recordings retrieved |
| 3 | For each recording | - | Check all fields |
| 4 | Verify uuid not empty | uuid != "" | True for all |
| 5 | Verify times not zero | start_time > 0 | True for all |
| 6 | Verify path not empty | path != "" | True for all |
| 7 | Count complete records | - | All 10 complete |

**Expected Result (overall):**
- All sampled recordings have complete metadata
- No null or empty required fields
- High data quality

**Post-Conditions:**
- None

**Assertions:**
```python
client = MongoClient(host="10.10.100.108", port=27017,
                     username="prisma", password="prisma")
db = client["prisma"]
recordings = db["recordings"]

# Get sample
sample = list(recordings.find().sort("start_time", -1).limit(10))

assert len(sample) >= 10, f"Not enough recordings: {len(sample)}"

required_fields = ["uuid", "start_time", "end_time", "path"]

for idx, rec in enumerate(sample, 1):
    logger.info(f"Checking recording {idx}/{len(sample)}")
    
    for field in required_fields:
        value = rec.get(field)
        assert value is not None, f"Field '{field}' is None"
        assert value != "", f"Field '{field}' is empty"
        
        if field in ["start_time", "end_time"]:
            assert value > 0, f"Field '{field}' is zero"

logger.info("✅ All recordings have complete metadata")
client.close()
```

**Environment:** Production

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_recordings_have_all_required_metadata`  
**Test File:** `tests/integration/infrastructure/test_mongodb_data_quality.py`

---

## SECTION B: Kubernetes Tests (8 Tests)

---

## TC-INFRA-009: Kubernetes Direct Connection

**Summary:** Infrastructure – Kubernetes API Direct Connection

**Objective:** Verify connection to Kubernetes API server and ability to query cluster information.

**Priority:** Critical

**Components/Labels:** kubernetes, infrastructure, k8s-api

**Requirements:** FOCUS-K8S-CONNECTION

**Pre-Conditions:**
- PC-001: kubeconfig file available
- PC-002: Kubernetes API server accessible
- PC-003: Valid authentication credentials

**Test Data:**
```json
Kubernetes API:
{
  "api_server": "https://10.10.100.102:6443",
  "namespace": "panda"
}
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Load kubeconfig | config.load_kube_config() | Config loaded |
| 2 | Create CoreV1Api client | - | Client created |
| 3 | Get cluster version | version_api.get_code() | Version returned |
| 4 | List nodes | core_v1.list_node() | Node list returned |
| 5 | Check node status | node.status.conditions | At least 1 Ready |
| 6 | List namespaces | core_v1.list_namespace() | Namespace list |
| 7 | Verify panda namespace | "panda" in namespaces | True |

**Expected Result (overall):**
- Kubernetes API accessible
- Cluster version retrieved
- At least one node Ready
- Namespace "panda" exists

**Post-Conditions:**
- None

**Assertions:**
```python
from kubernetes import client, config
from kubernetes.client import VersionApi

config.load_kube_config()
core_v1 = client.CoreV1Api()

# Get version
version_api = VersionApi()
version = version_api.get_code()
logger.info(f"Kubernetes Version: {version.git_version}")
assert version.git_version is not None

# List nodes
nodes = core_v1.list_node()
assert len(nodes.items) > 0, "No nodes found"

for node in nodes.items:
    status = "Ready" if any(
        cond.type == "Ready" and cond.status == "True" 
        for cond in node.status.conditions
    ) else "NotReady"
    logger.info(f"Node: {node.metadata.name} - {status}")

# Verify at least one Ready
ready_nodes = [n for n in nodes.items if any(
    c.type == "Ready" and c.status == "True" 
    for c in n.status.conditions
)]
assert len(ready_nodes) > 0, "No Ready nodes"

logger.info("✅ Kubernetes connectivity test PASSED")
```

**Environment:** Production (K8s)

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_kubernetes_direct_connection`  
**Test File:** `tests/integration/infrastructure/test_basic_connectivity.py`

---

## TC-INFRA-010: Kubernetes Connection (Managed)

**Summary:** Infrastructure – Kubernetes Connection via ConfigManager

**Objective:** Verify Kubernetes connection using application configuration.

**Priority:** High

**Components/Labels:** kubernetes, config-manager

**Requirements:** FOCUS-K8S-CONFIG

**Pre-Conditions:**
- PC-001: K8s config in environments.yaml

**Test Data:**
```yaml
kubernetes:
  api_server: "https://10.10.100.102:6443"
  namespace: "panda"
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Load config | ConfigManager() | Config loaded |
| 2 | Get K8s config | get_kubernetes_config() | Config dict |
| 3 | Verify namespace | config["namespace"] | "panda" |
| 4 | Connect to API | - | Connected |

**Expected Result (overall):**
- Config loads correctly
- K8s connection works

**Post-Conditions:**
- None

**Assertions:**
```python
config_manager = ConfigManager("new_production")
k8s_config = config_manager.get_kubernetes_config()

assert k8s_config["namespace"] == "panda"
assert "api_server" in k8s_config

# Test connection
config.load_kube_config()
v1 = client.CoreV1Api()
namespaces = v1.list_namespace()

assert any(ns.metadata.name == "panda" for ns in namespaces.items)

logger.info("✅ K8s connection via ConfigManager works")
```

**Environment:** Production (K8s)

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_kubernetes_connection`  
**Test File:** `tests/integration/infrastructure/test_basic_connectivity.py`

---

## TC-INFRA-011: Kubernetes List Pods

**Summary:** Infrastructure – List Pods in Panda Namespace

**Objective:** Verify ability to list all pods in panda namespace and check their status.

**Priority:** High

**Components/Labels:** kubernetes, pods, namespace

**Requirements:** FOCUS-K8S-PODS

**Pre-Conditions:**
- PC-001: K8s API accessible
- PC-002: Namespace "panda" exists
- PC-003: At least Focus Server pod running

**Test Data:**
```json
Expected Pods:
[
  "panda-panda-focus-server-*",
  "mongodb-*",
  "rabbitmq-panda-*"
]
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Connect to K8s | - | Connected |
| 2 | List pods in panda | namespace="panda" | Pod list |
| 3 | Check pod count | len(pods.items) | > 0 |
| 4 | Check Focus Server pod | name contains "focus-server" | Found |
| 5 | Verify pod status | pod.status.phase | "Running" |
| 6 | Check container ready | container.ready | True |
| 7 | Log all pods | - | All pods logged |

**Expected Result (overall):**
- At least 3 pods in panda namespace
- Focus Server pod running
- All critical pods healthy

**Post-Conditions:**
- None

**Assertions:**
```python
config.load_kube_config()
v1 = client.CoreV1Api()

pods = v1.list_namespaced_pod(namespace="panda")

assert len(pods.items) > 0, "No pods found in panda namespace"

logger.info(f"Found {len(pods.items)} pods in panda namespace:")

focus_server_found = False

for pod in pods.items:
    name = pod.metadata.name
    phase = pod.status.phase
    logger.info(f"  - {name}: {phase}")
    
    if "focus-server" in name:
        focus_server_found = True
        assert phase == "Running", f"Focus Server pod not running: {phase}"

assert focus_server_found, "Focus Server pod not found"

logger.info("✅ Kubernetes pod listing works")
```

**Environment:** Production (K8s)

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_kubernetes_list_pods`  
**Test File:** `tests/integration/infrastructure/test_basic_connectivity.py`

---

## TC-INFRA-012: Kubernetes List Deployments

**Summary:** Infrastructure – List Deployments in Panda Namespace

**Objective:** Verify deployments exist and are healthy.

**Priority:** Medium

**Components/Labels:** kubernetes, deployments

**Requirements:** FOCUS-K8S-DEPLOYMENTS

**Pre-Conditions:**
- PC-001: K8s API accessible

**Test Data:**
```json
Expected Deployments:
[
  "panda-panda-focus-server"
]
```

**Steps:**

| # | Action | Data | Expected Result |
|---|--------|------|-----------------|
| 1 | Connect to K8s | - | Connected |
| 2 | List deployments | namespace="panda" | Deployment list |
| 3 | Find focus-server deployment | - | Found |
| 4 | Check replicas | spec.replicas | >= 1 |
| 5 | Check ready replicas | status.ready_replicas | >= 1 |
| 6 | Verify conditions | - | Available=True |

**Expected Result (overall):**
- Deployments exist
- Replicas ready
- Conditions healthy

**Post-Conditions:**
- None

**Assertions:**
```python
config.load_kube_config()
apps_v1 = client.AppsV1Api()

deployments = apps_v1.list_namespaced_deployment(namespace="panda")

assert len(deployments.items) > 0, "No deployments found"

logger.info(f"Found {len(deployments.items)} deployments:")

for dep in deployments.items:
    name = dep.metadata.name
    replicas = dep.spec.replicas
    ready = dep.status.ready_replicas or 0
    
    logger.info(f"  - {name}: {ready}/{replicas} ready")
    
    if "focus-server" in name:
        assert ready >= 1, "Focus Server deployment not ready"

logger.info("✅ Kubernetes deployment listing works")
```

**Environment:** Production (K8s)

**Automation Status:** IMPLEMENTED  
**Test Function:** `test_kubernetes_list_deployments`  
**Test File:** `tests/integration/infrastructure/test_basic_connectivity.py`

---

Due to length, continuing in next file...

**Progress:** 12/25 Infrastructure tests documented (48% complete)

Shall I continue with the remaining 13 Infrastructure tests?
