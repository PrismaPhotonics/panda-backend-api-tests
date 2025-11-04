#!/bin/bash
# Find how to access Focus Server externally

echo "================================================================================="
echo "Finding External Access to Focus Server"
echo "================================================================================="
echo ""

echo "1. Checking for Ingress:"
kubectl get ingress -n panda
echo ""

echo "2. Checking all LoadBalancer services:"
kubectl get svc -n panda -o wide | grep LoadBalancer
echo ""

echo "3. Checking for NodePort services (Focus Server):"
kubectl get svc -n panda | grep focus
echo ""

echo "4. Checking what 10.10.100.100 is (from your config):"
echo "   This might be an Ingress controller or reverse proxy"
echo "   Run from bastion: curl -k https://10.10.100.100/focus-server/"
echo ""

echo "5. Checking if there's a reverse proxy or ingress controller:"
kubectl get pods -A | grep -E "(nginx|traefik|ingress|haproxy|proxy)"
echo ""

echo "================================================================================="
echo "Summary:"
echo "  - Focus Server service is ClusterIP (internal only)"
echo "  - External access might be via:"
echo "    1. Ingress (check above)"
echo "    2. Reverse proxy at 10.10.100.100"
echo "    3. Port-forward (for testing)"
echo "================================================================================="
