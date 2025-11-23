#!/bin/bash
# Cleanup all gRPC and cleanup jobs in Kubernetes
# Usage: ./k8s_cleanup_all_jobs.sh [namespace]
# Default namespace: panda

NAMESPACE="${1:-panda}"

echo "=========================================="
echo "Kubernetes Jobs Cleanup Script"
echo "=========================================="
echo "Namespace: $NAMESPACE"
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ Error: kubectl not found. Please install kubectl first."
    exit 1
fi

# Check namespace exists
if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
    echo "❌ Error: Namespace '$NAMESPACE' not found."
    exit 1
fi

echo "🔍 Searching for gRPC and cleanup jobs..."
echo ""

# Count jobs before deletion
GRPC_JOBS=$(kubectl get jobs -n "$NAMESPACE" -o name 2>/dev/null | grep -E "grpc-job" || true)
CLEANUP_JOBS=$(kubectl get jobs -n "$NAMESPACE" -o name 2>/dev/null | grep -E "cleanup-job" || true)

GRPC_COUNT=$(echo "$GRPC_JOBS" | grep -c . || echo "0")
CLEANUP_COUNT=$(echo "$CLEANUP_JOBS" | grep -c . || echo "0")
TOTAL=$((GRPC_COUNT + CLEANUP_COUNT))

if [ "$TOTAL" -eq 0 ]; then
    echo "✅ No jobs found to delete"
    exit 0
fi

echo "📋 Found:"
echo "   - $GRPC_COUNT gRPC job(s)"
echo "   - $CLEANUP_COUNT cleanup job(s)"
echo "   - Total: $TOTAL job(s)"
echo ""

# Show sample jobs
if [ "$GRPC_COUNT" -gt 0 ] || [ "$CLEANUP_COUNT" -gt 0 ]; then
    echo "📋 Sample jobs to be deleted:"
    kubectl get jobs -n "$NAMESPACE" 2>/dev/null | grep -E "(grpc-job|cleanup-job)" | head -10
    if [ "$TOTAL" -gt 10 ]; then
        echo "   ... and $((TOTAL - 10)) more"
    fi
    echo ""
fi

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
echo ""

# Delete all jobs
ALL_JOBS=$(kubectl get jobs -n "$NAMESPACE" -o name 2>/dev/null | grep -E "(grpc-job|cleanup-job)" || true)

if [ -z "$ALL_JOBS" ]; then
    echo "✅ No jobs to delete"
    exit 0
fi

# Delete jobs one by one to show progress
DELETED=0
FAILED=0

while IFS= read -r job; do
    if [ -n "$job" ]; then
        job_name=$(echo "$job" | sed 's/job\.//')
        echo -n "   Deleting $job_name... "
        if kubectl delete "$job" -n "$NAMESPACE" --ignore-not-found=true &>/dev/null; then
            echo "✅"
            DELETED=$((DELETED + 1))
        else
            echo "❌"
            FAILED=$((FAILED + 1))
        fi
    fi
done <<< "$ALL_JOBS"

echo ""
echo "=========================================="
echo "Summary:"
echo "   Total found: $TOTAL"
echo "   Successfully deleted: $DELETED"
if [ "$FAILED" -gt 0 ]; then
    echo "   Failed: $FAILED"
fi
echo "=========================================="

# Verify deletion
echo ""
echo "🔍 Verifying deletion..."
REMAINING=$(kubectl get jobs -n "$NAMESPACE" -o name 2>/dev/null | grep -E "(grpc-job|cleanup-job)" | wc -l || echo "0")
if [ "$REMAINING" -eq 0 ]; then
    echo "✅ All jobs deleted successfully"
else
    echo "⚠️  Warning: $REMAINING job(s) still remain"
    echo "   You may need to force delete them:"
    echo "   kubectl get jobs -n $NAMESPACE -o name | grep -E '(grpc-job|cleanup-job)' | xargs -I {} kubectl delete {} -n $NAMESPACE --grace-period=0 --force"
fi

