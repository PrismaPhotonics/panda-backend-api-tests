# 🔍 Quick Check - Alert Logs

## Step 1: Check logs WITHOUT grep

```bash
# Focus Server - see all recent logs
kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s --tail=200

# RabbitMQ - see all recent logs  
kubectl logs -n panda rabbitmq-panda-0 --tail=200

# gRPC Job - see all recent logs
kubectl logs -n panda grpc-job-1-3-rm5ms --tail=200
```

## Step 2: Check for other keywords

```bash
# Focus Server - broader search
kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s --tail=500 | grep -i "rabbit\|queue\|message\|api\|post\|prisma"

# RabbitMQ - broader search
kubectl logs -n panda rabbitmq-panda-0 --tail=500 | grep -i "publish\|consume\|exchange\|routing\|prisma"

# gRPC Job - broader search
kubectl logs -n panda grpc-job-1-3-rm5ms --tail=500 | grep -i "report\|algorithm\|mlground\|pulse"
```

## Step 3: Check if alerts were sent

```bash
# Send a test alert first, then check logs
# Use the test script or API directly
```

## Step 4: Check other pods

```bash
# List all pods
kubectl get pods -n panda

# Check if there are other pods handling alerts
kubectl get pods -n panda | grep -i "api\|web\|alert"
```

## Step 5: Follow logs in real-time

```bash
# Open terminal 1: Follow Focus Server logs
kubectl logs -n panda panda-panda-focus-server-78dbcfd9d9-4ld4s -f

# Open terminal 2: Send alert
# Then watch terminal 1 for new logs
```

