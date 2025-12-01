# Automation Run Sentinel

Autonomous monitoring and analysis service for automation runs on Kubernetes.

## Overview

The Automation Run Sentinel automatically:
- Detects automation run starts and ends
- Monitors Kubernetes resources (pods, jobs, services)
- Streams and analyzes logs
- Detects anomalies in infrastructure, application, and tests
- Validates run structure against requirements
- Sends alerts via Slack, email, or webhooks
- Maintains historical data for trend analysis

## Quick Start

### Prerequisites

- Python 3.8+
- Kubernetes cluster access (kubeconfig or in-cluster)
- Required Python packages (see requirements.txt)

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install additional Sentinel dependencies
pip install kubernetes psycopg2-binary flask requests
```

### Configuration

1. Copy and edit `config/sentinel_config.yaml`:

```yaml
# Set your Slack webhook URL
channels:
  - type: "slack"
    webhook_url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

2. Configure Kubernetes access (kubeconfig or in-cluster)

### Running

```bash
# Run Sentinel service
python scripts/sentinel/run_sentinel.py

# Or with custom config
python scripts/sentinel/run_sentinel.py --config /path/to/config.yaml
```

## Architecture

### Components

1. **RunDetector** - Detects run starts from CI webhooks, K8s jobs, or logs
2. **K8sWatcher** - Monitors Kubernetes pods, jobs, and services
3. **LogStreamer** - Streams and parses logs from pods/jobs
4. **StructureAnalyzer** - Validates test structure against rules
5. **AnomalyEngine** - Detects anomalies across infrastructure, app, and tests
6. **RunHistoryStore** - Persists run data to database
7. **AlertDispatcher** - Sends alerts to configured channels

### Data Flow

```
CI/CD → RunDetector → K8sWatcher → AnomalyEngine → AlertDispatcher
                    ↓
              LogStreamer → StructureAnalyzer
                    ↓
              RunHistoryStore
```

## API Endpoints

When API is enabled, the following endpoints are available:

- `GET /health` - Health check
- `GET /ready` - Readiness check
- `GET /api/runs` - List runs (with filters)
- `GET /api/runs/<run_id>` - Get run details
- `GET /api/runs/<run_id>/anomalies` - Get run anomalies
- `POST /api/webhooks/github` - GitHub Actions webhook
- `POST /api/webhooks/jenkins` - Jenkins webhook
- `POST /api/webhooks/generic` - Generic webhook
- `GET /api/stats` - Service statistics

## Configuration

See `config/sentinel_config.yaml` for full configuration options:

- Kubernetes namespaces and label selectors
- Log detection patterns
- Pipeline structure rules
- Anomaly detection thresholds
- Alert channels (Slack, email, webhooks)
- Database configuration

## Deployment

### Kubernetes Deployment

See `deployments/sentinel-deployment.yaml` for Kubernetes deployment manifest.

### Docker

```bash
docker build -t automation-run-sentinel .
docker run -v /path/to/config:/app/config automation-run-sentinel
```

## Monitoring

The Sentinel itself can be monitored via:
- Health endpoints (`/health`, `/ready`)
- Metrics (if Prometheus integration added)
- Logs (structured logging)

## Troubleshooting

### Common Issues

1. **Kubernetes connection failed**
   - Check kubeconfig or in-cluster service account
   - Verify RBAC permissions

2. **Logs not streaming**
   - Check pod names and namespaces
   - Verify log streaming permissions

3. **Alerts not sending**
   - Check webhook URLs and credentials
   - Verify alert cooldown settings

## Development

### Running Tests

```bash
pytest tests/sentinel/
```

### Code Structure

```
src/sentinel/
├── core/          # Core components
├── main/          # Main service
├── api/           # REST API
└── models.py      # Data models
```

## License

See project LICENSE file.




