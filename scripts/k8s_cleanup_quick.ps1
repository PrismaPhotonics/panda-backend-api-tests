# Quick cleanup script for gRPC and cleanup jobs (PowerShell)
# Usage: .\k8s_cleanup_quick.ps1 [namespace]
# Default namespace: panda

param(
    [string]$Namespace = "panda"
)

Write-Host "🔍 Finding gRPC and cleanup jobs in namespace '$Namespace'..." -ForegroundColor Cyan

# Get all jobs
$allJobs = kubectl get jobs -n $Namespace -o json | ConvertFrom-Json

# Filter gRPC and cleanup jobs
$grpcJobs = $allJobs.items | Where-Object { $_.metadata.name -like "grpc-job-*" }
$cleanupJobs = $allJobs.items | Where-Object { $_.metadata.name -like "cleanup-job-*" }
$totalJobs = $grpcJobs.Count + $cleanupJobs.Count

if ($totalJobs -eq 0) {
    Write-Host "✅ No jobs found to delete" -ForegroundColor Green
    exit 0
}

Write-Host "📋 Found:" -ForegroundColor Yellow
Write-Host "   - $($grpcJobs.Count) gRPC job(s)"
Write-Host "   - $($cleanupJobs.Count) cleanup job(s)"
Write-Host "   - Total: $totalJobs job(s)"
Write-Host ""

# Show first few jobs
Write-Host "📋 Sample jobs to be deleted:" -ForegroundColor Yellow
$allJobsToDelete = $grpcJobs + $cleanupJobs
$allJobsToDelete | Select-Object -First 5 | ForEach-Object {
    Write-Host "   - $($_.metadata.name) (Status: $($_.status.conditions[0].type))"
}
if ($totalJobs -gt 5) {
    Write-Host "   ... and $($totalJobs - 5) more"
}

Write-Host ""
Write-Host "⚠️  WARNING: This will delete all gRPC and cleanup jobs!" -ForegroundColor Red
Write-Host "   Associated pods will also be deleted automatically."
Write-Host ""
$confirm = Read-Host "Continue? (yes/no)"

if ($confirm -ne "yes") {
    Write-Host "❌ Cancelled" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "🗑️  Deleting jobs..." -ForegroundColor Cyan

# The magic command!
$command = "kubectl get jobs -n $Namespace -o name | grep -E '(grpc-job|cleanup-job)' | xargs -I {} kubectl delete {} -n $Namespace"

# Execute via SSH or directly if on Linux
if ($IsWindows -or $env:OS -like "*Windows*") {
    Write-Host "ℹ️  Run this command on the Linux server:" -ForegroundColor Yellow
    Write-Host $command -ForegroundColor White
    Write-Host ""
    Write-Host "Or connect via SSH and run:" -ForegroundColor Yellow
    Write-Host "ssh root@10.10.10.10" -ForegroundColor White
    Write-Host "ssh prisma@10.10.10.150" -ForegroundColor White
    Write-Host $command -ForegroundColor White
} else {
    # Execute directly if on Linux
    Invoke-Expression $command
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Successfully deleted $totalJobs job(s)" -ForegroundColor Green
        Write-Host "ℹ️  Associated pods will be deleted automatically by Kubernetes" -ForegroundColor Cyan
    } else {
        Write-Host ""
        Write-Host "❌ Some errors occurred during deletion" -ForegroundColor Red
        exit 1
    }
}

