# Automation Run Sentinel

## Overview

The Automation Run Sentinel is an autonomous monitoring and analysis service for automation runs on Kubernetes. It automatically detects, tracks, and analyzes automation runs, detects anomalies, validates run structure, and sends alerts.

## Features

- **Automatic Run Detection** - Detects runs from CI webhooks, K8s jobs, or log patterns
- **Kubernetes Monitoring** - Real-time monitoring of pods, jobs, and services
- **Log Streaming** - Streams and parses logs from automation components
- **Anomaly Detection** - Detects infrastructure, application, and test anomalies
- **Structure Validation** - Validates test structure against defined requirements
- **Historical Memory** - Maintains history for trend analysis and baselines
- **Alerting** - Sends alerts via Slack, email, or webhooks

## Quick Start

See `scripts/sentinel/README.md` for detailed setup and usage instructions.

## Architecture

See the main project documentation for architecture details.

## Configuration

Configuration file: `config/sentinel_config.yaml`

Key configuration sections:
- Kubernetes namespaces and labels
- Log detection patterns
- Pipeline structure rules
- Anomaly thresholds
- Alert channels

## API

When enabled, the Sentinel provides REST API endpoints:
- `/health` - Health check
- `/ready` - Readiness check
- `/api/runs` - List runs
- `/api/runs/<run_id>` - Get run details
- `/api/webhooks/*` - Webhook endpoints

## Deployment

### Standalone

```bash
python scripts/sentinel/run_sentinel.py
```

### Kubernetes

Deploy using the provided Kubernetes manifests (see `deployments/` directory).

## Monitoring

The Sentinel itself can be monitored via:
- Health endpoints
- Structured logs
- Metrics (if Prometheus integration added)

## Troubleshooting

Common issues and solutions:
1. **K8s connection** - Check kubeconfig/service account
2. **Log streaming** - Verify pod names and permissions
3. **Alerts** - Check webhook URLs and cooldown settings




