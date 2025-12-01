# Automation Run Sentinel - Architecture

## System Overview

The Automation Run Sentinel is a distributed monitoring system designed to track automation runs on Kubernetes clusters. It operates as an autonomous agent that continuously monitors infrastructure, application behavior, and test execution.

## Component Architecture

### Core Components

#### 1. RunDetector
**Purpose**: Detects the start and end of automation runs

**Inputs**:
- CI/CD webhooks (GitHub Actions, Jenkins)
- Kubernetes Job creation events
- Log pattern matching

**Outputs**:
- RunContext objects
- Run start/end events

**Key Methods**:
- `detect_from_webhook()` - Process CI webhook
- `detect_from_k8s_job()` - Detect from K8s Job
- `detect_from_log()` - Pattern-based detection

#### 2. K8sWatcher
**Purpose**: Monitors Kubernetes resources in real-time

**Monitors**:
- Pods (phase, restarts, errors)
- Jobs (status, failures)
- Services (health)
- Events (OOM, ImagePullBackOff)

**Implementation**:
- Uses Kubernetes Watch API
- Multi-threaded for concurrent namespace monitoring
- Event-driven architecture

#### 3. LogStreamer
**Purpose**: Streams and parses logs from pods/jobs

**Features**:
- Real-time log streaming via K8s API
- Pattern-based event extraction
- Test event recognition
- Error signature detection

**Patterns**:
- Test markers (TEST_START, TEST_PASS, TEST_FAIL)
- Suite markers (SUITE_START, SUITE_END)
- Run markers (RUN_START, RUN_END)

#### 4. StructureAnalyzer
**Purpose**: Validates test run structure

**Validations**:
- Required suites present
- Forbidden suites absent
- Test counts within ranges
- Required tags present
- Baseline comparison

**Rules**:
- Defined per pipeline type
- Configurable via YAML
- Historical baseline support

#### 5. AnomalyEngine
**Purpose**: Detects anomalies across all layers

**Detection Types**:
- **Infrastructure**: Pod crashes, restarts, OOM
- **Application**: 5xx spikes, DB errors, timeouts
- **Test**: Failure spikes, hanging tests, flakiness
- **Structure**: Missing suites, wrong test counts

**Thresholds**:
- Configurable per anomaly type
- Historical baseline comparison
- Severity classification

#### 6. RunHistoryStore
**Purpose**: Persists and queries historical data

**Storage**:
- Run metadata
- Test results
- Anomalies
- Infrastructure snapshots

**Backends**:
- SQLite (default)
- PostgreSQL (optional)
- In-memory (fallback)

#### 7. AlertDispatcher
**Purpose**: Delivers alerts to configured channels

**Channels**:
- Slack (webhook)
- Email (SMTP)
- Generic webhooks

**Features**:
- Severity filtering
- Cooldown periods
- Rich formatting

## Data Flow

### Run Start Flow

```
CI/CD Trigger
    ↓
RunDetector.detect_from_webhook()
    ↓
Create RunContext
    ↓
Register with:
    - K8sWatcher (start monitoring pods/jobs)
    - LogStreamer (start streaming logs)
    - AnomalyEngine (start anomaly detection)
```

### Live Monitoring Flow

```
K8sWatcher → PodHealthEvent → AnomalyEngine → AlertDispatcher
LogStreamer → TestEvent → StructureAnalyzer → AnomalyEngine
LogStreamer → Error → AnomalyEngine → AlertDispatcher
```

### Run End Flow

```
RunDetector.detect_run_end()
    ↓
StructureAnalyzer.analyze_run_structure()
    ↓
RunHistoryStore.save_run()
    ↓
StructureAnalyzer.update_baseline()
    ↓
Unregister from components
```

## Data Models

### RunContext
Central data structure representing a single automation run:
- Metadata (run_id, pipeline, environment, branch, commit)
- Status and timing
- Test structure (suites, tests)
- Anomalies detected
- Infrastructure snapshots

### Anomaly
Represents a detected anomaly:
- Severity (info, warning, critical)
- Category (infra, app, test, structure)
- Context (affected component, root cause hints)
- Timestamp and metadata

### TestEvent
Structured event from log parsing:
- Event type (TEST_START, TEST_PASS, etc.)
- Test/suite information
- Status and timing
- Metadata

## Configuration

Configuration is loaded from `config/sentinel_config.yaml`:

- **Kubernetes**: Namespaces, label selectors
- **Log Patterns**: Regex patterns for event detection
- **Structure Rules**: Pipeline-specific requirements
- **Anomaly Thresholds**: Detection sensitivity
- **Alert Channels**: Slack, email, webhook URLs
- **Database**: Connection settings

## Deployment

### Standalone Mode
Run as a Python service:
```bash
python scripts/sentinel/run_sentinel.py
```

### Kubernetes Deployment
Deploy as a Deployment in the cluster:
- Service account with read-only K8s permissions
- ConfigMap for configuration
- Secrets for webhooks/credentials

### API Mode
When API is enabled, provides REST endpoints:
- Health checks
- Run queries
- Webhook ingestion
- Statistics

## Scalability Considerations

### Horizontal Scaling
- Multiple Sentinel instances can run concurrently
- Each instance tracks different runs (by label/namespace)
- History store should be shared (PostgreSQL)

### Performance
- Log streaming uses async/threading
- K8s watch uses efficient streaming API
- Database queries are indexed
- Alert cooldown prevents spam

### Resilience
- Graceful shutdown handling
- Re-attach to ongoing runs on restart
- Database connection retry logic
- Degraded mode if K8s unavailable

## Security

### Access Control
- Read-only K8s access (RBAC)
- Secrets stored in K8s Secrets/Vault
- Webhook authentication (if supported)

### Data Privacy
- No sensitive test data stored
- Anonymized error messages
- Configurable data retention

## Monitoring the Sentinel

The Sentinel itself can be monitored:
- Health endpoints (`/health`, `/ready`)
- Structured logging
- Metrics (if Prometheus integration added)
- Alert history

## Future Enhancements

- Prometheus metrics export
- Grafana dashboards
- Machine learning for anomaly detection
- Auto-remediation suggestions
- Integration with incident management tools




