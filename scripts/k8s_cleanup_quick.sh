#!/bin/bash
# Quick cleanup script for gRPC and cleanup jobs
# Usage: ./k8s_cleanup_quick.sh [namespace]
# Default namespace: panda

NAMESPACE="${1:-panda}"

echo "🔍 Finding gRPC and cleanup jobs in namespace '$NAMESPACE'..."

# Count jobs before deletion
GRPC_COUNT=$(kubectl get jobs -n $NAMESPACE -o name | grep -E "grpc-job" | wc -l)
CLEANUP_COUNT=$(kubectl get jobs -n $NAMESPACE -o name | grep -E "cleanup-job" | wc -l)
TOTAL=$((GRPC_COUNT + CLEANUP_COUNT))

if [ $TOTAL -eq 0 ]; then
    echo "✅ No jobs found to delete"
    exit 0
fi

echo "📋 Found:"
echo "   - $GRPC_COUNT gRPC job(s)"
echo "   - $CLEANUP_COUNT cleanup job(s)"
echo "   - Total: $TOTAL job(s)"
echo ""

# Show first few jobs
echo "📋 Sample jobs to be deleted:"
kubectl get jobs -n $NAMESPACE | grep -E "(grpc-job|cleanup-job)" | head -5
if [ $TOTAL -gt 5 ]; then
    echo "   ... and $((TOTAL - 5)) more"
fi

echo ""
echo "⚠️  WARNING: This will delete all gRPC and cleanup jobs!"
echo "   Associated pods will also be deleted automatically."
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Cancelled"
    exit 0
fi

echo ""
echo "🗑️  Deleting jobs..."

# The magic command!
kubectl get jobs -n $NAMESPACE -o name | grep -E "(grpc-job|cleanup-job)" | xargs -I {} kubectl delete {} -n $NAMESPACE

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully deleted $TOTAL job(s)"
    echo "ℹ️  Associated pods will be deleted automatically by Kubernetes"
else
    echo ""
    echo "❌ Some errors occurred during deletion"
    exit 1
fi

