# Automation Run Sentinel Helm Chart

This Helm chart deploys the Automation Run Sentinel monitoring service to Kubernetes.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- kubectl configured to access your cluster

## Installation

### Quick Start

```bash
# Add the chart repository (if using a chart repository)
helm repo add sentinel ./helm/sentinel
helm repo update

# Install with default values
helm install sentinel ./helm/sentinel

# Or install with custom values
helm install sentinel ./helm/sentinel -f my-values.yaml
```

### Building and Pushing Docker Image

Before deploying, you need to build and push the Docker image:

```bash
# Build the image
docker build -f Dockerfile.sentinel -t automation-run-sentinel:latest .

# Tag for your registry
docker tag automation-run-sentinel:latest your-registry/automation-run-sentinel:latest

# Push to registry
docker push your-registry/automation-run-sentinel:latest

# Update values.yaml with your image repository
# image:
#   repository: your-registry/automation-run-sentinel
#   tag: latest
```

## Configuration

### Required Configuration

1. **Secrets**: Update `values.yaml` with your webhook URLs and credentials:
   ```yaml
   secrets:
     SLACK_WEBHOOK_URL: "https://hooks.slack.com/services/..."
     GENERIC_WEBHOOK_URL: "https://your-webhook-url.com/..."
   ```

2. **Kubernetes Namespaces**: Configure which namespaces to monitor:
   ```yaml
   config:
     k8s_namespaces:
       - "panda"
       - "default"
   ```

### Optional Configuration

- **Database**: Switch to PostgreSQL by updating database config
- **Resources**: Adjust CPU/memory limits
- **Replicas**: Scale horizontally (note: use shared database)
- **Persistence**: Enable persistent storage for history

## Values Reference

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Image repository | `automation-run-sentinel` |
| `image.tag` | Image tag | `latest` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `5000` |
| `config.environment` | Environment name | `production` |
| `config.k8s_namespaces` | Namespaces to monitor | `["panda", "default"]` |
| `config.database.type` | Database type | `sqlite` |
| `persistence.enabled` | Enable persistent storage | `false` |
| `resources.requests.memory` | Memory request | `256Mi` |
| `resources.limits.memory` | Memory limit | `512Mi` |

## Upgrading

```bash
helm upgrade sentinel ./helm/sentinel -f my-values.yaml
```

## Uninstalling

```bash
helm uninstall sentinel
```

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods -n sentinel
kubectl logs -n sentinel deployment/automation-run-sentinel
```

### Check Service

```bash
kubectl get svc -n sentinel
kubectl port-forward -n sentinel svc/automation-run-sentinel 5000:5000
```

### Check ConfigMap

```bash
kubectl get configmap -n sentinel
kubectl describe configmap -n sentinel sentinel-config
```

### Check RBAC

```bash
kubectl get role,rolebinding,clusterrole,clusterrolebinding -n sentinel
```

## Security

- The service runs as non-root user (UID 1000)
- RBAC is configured with minimal required permissions (read-only)
- Secrets are stored in Kubernetes Secrets (not in ConfigMap)
- Consider using external secret management (Vault, Sealed Secrets) for production

## Production Recommendations

1. **Use PostgreSQL** for shared storage across replicas
2. **Enable persistence** for data retention
3. **Set resource limits** based on your workload
4. **Configure ingress** for external access (if needed)
5. **Use image pull secrets** for private registries
6. **Set up monitoring** for the Sentinel itself
7. **Configure backup** for persistent volumes

