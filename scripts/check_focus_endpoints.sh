#!/bin/bash
# Check Focus Server endpoints

POD_NAME="panda-panda-focus-server-78dbcfd9d9-d22wn"
NAMESPACE="panda"

echo "================================================================================="
echo "Checking Focus Server Endpoints"
echo "================================================================================="
echo ""

echo "1. Testing root endpoint:"
kubectl exec -it $POD_NAME -n $NAMESPACE -- curl -s http://localhost:5000/ | head -20
echo ""

echo "2. Testing /focus-server endpoint:"
kubectl exec -it $POD_NAME -n $NAMESPACE -- curl -s http://localhost:5000/focus-server/
echo ""

echo "3. Testing /api endpoint:"
kubectl exec -it $POD_NAME -n $NAMESPACE -- curl -s http://localhost:5000/api/
echo ""

echo "4. Testing /health endpoint:"
kubectl exec -it $POD_NAME -n $NAMESPACE -- curl -s http://localhost:5000/health
echo ""

echo "5. Testing /configure endpoint (GET):"
kubectl exec -it $POD_NAME -n $NAMESPACE -- curl -s -X GET http://localhost:5000/focus-server/configure
echo ""

echo "6. Checking what ports are listening:"
kubectl exec -it $POD_NAME -n $NAMESPACE -- netstat -tlnp 2>/dev/null | grep 5000 || \
kubectl exec -it $POD_NAME -n $NAMESPACE -- ss -tlnp 2>/dev/null | grep 5000
echo ""

echo "7. Checking environment variables:"
kubectl exec -it $POD_NAME -n $NAMESPACE -- env | grep -E "(PZ|PRISMA|FOCUS)" | sort
echo ""

echo "================================================================================="
