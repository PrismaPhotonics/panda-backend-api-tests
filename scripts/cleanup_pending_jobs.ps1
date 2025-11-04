# PowerShell script to delete all pending jobs in Kubernetes
# Usage: .\scripts\cleanup_pending_jobs.ps1 [-Namespace panda] [-Force]

param(
    [Parameter(Mandatory=$false)]
    [string]$Namespace = "panda",
    
    [Parameter(Mandatory=$false)]
    [switch]$Force = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$AllJobs = $false
)

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "Kubernetes Jobs Cleanup Script" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if kubectl is available
$kubectlPath = Get-Command kubectl -ErrorAction SilentlyContinue
if (-not $kubectlPath) {
    Write-Host "[ERROR] kubectl not found!" -ForegroundColor Red
    Write-Host "Please install kubectl or run via SSH" -ForegroundColor Yellow
    exit 1
}

Write-Host "[INFO] Using namespace: $Namespace" -ForegroundColor Yellow
Write-Host ""

# Option 1: Delete all pending jobs (by pod status)
Write-Host "Option 1: Finding jobs with pending pods..." -ForegroundColor Cyan
Write-Host ""

$pendingJobs = kubectl get pods -n $Namespace --field-selector=status.phase=Pending -o jsonpath='{.items[*].metadata.ownerReferences[*].name}' 2>$null

if ($pendingJobs) {
    $uniqueJobs = $pendingJobs -split ' ' | Where-Object { $_ } | Sort-Object -Unique
    
    if ($uniqueJobs) {
        Write-Host "[INFO] Found $($uniqueJobs.Count) unique jobs with pending pods:" -ForegroundColor Yellow
        foreach ($job in $uniqueJobs) {
            Write-Host "  - $job" -ForegroundColor White
        }
        Write-Host ""
        
        if ($Force) {
            Write-Host "[ACTION] Deleting jobs with pending pods..." -ForegroundColor Yellow
            foreach ($job in $uniqueJobs) {
                kubectl delete job $job -n $Namespace --grace-period=0 --force 2>&1 | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "  [OK] Deleted: $job" -ForegroundColor Green
                } else {
                    Write-Host "  [WARNING] Failed to delete: $job" -ForegroundColor Yellow
                }
            }
        } else {
            Write-Host "[DRY RUN] Would delete the following jobs:" -ForegroundColor Cyan
            Write-Host "  kubectl delete jobs -n $Namespace $($uniqueJobs -join ' ')" -ForegroundColor White
            Write-Host ""
            Write-Host "Run with -Force to actually delete them" -ForegroundColor Yellow
        }
    } else {
        Write-Host "[INFO] No jobs with pending pods found" -ForegroundColor Green
    }
} else {
    Write-Host "[INFO] No pending pods found" -ForegroundColor Green
}

Write-Host ""

# Option 2: Delete all jobs (nuclear option)
if ($AllJobs) {
    Write-Host "Option 2: Deleting ALL jobs in namespace $Namespace..." -ForegroundColor Cyan
    Write-Host ""
    
    if ($Force) {
        $allJobs = kubectl get jobs -n $Namespace -o jsonpath='{.items[*].metadata.name}' 2>$null
        if ($allJobs) {
            $jobList = $allJobs -split ' ' | Where-Object { $_ }
            Write-Host "[INFO] Found $($jobList.Count) jobs total" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "[ACTION] Deleting all jobs..." -ForegroundColor Yellow
            
            # Delete all at once
            kubectl delete jobs --all -n $Namespace --grace-period=0 --force 2>&1 | Out-Null
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "[OK] All jobs deleted successfully" -ForegroundColor Green
            } else {
                Write-Host "[WARNING] Some jobs may not have been deleted" -ForegroundColor Yellow
            }
        } else {
            Write-Host "[INFO] No jobs found in namespace" -ForegroundColor Green
        }
    } else {
        Write-Host "[DRY RUN] Would delete all jobs with:" -ForegroundColor Cyan
        Write-Host "  kubectl delete jobs --all -n $Namespace --grace-period=0 --force" -ForegroundColor White
        Write-Host ""
        Write-Host "Run with -Force to actually delete them" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "Cleanup Complete" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

