# Script to run GitHub Actions workflows locally using Act
# https://github.com/nektos/act

param(
    [string]$WorkflowName = "smoke-tests",
    [string]$ActVersion = "latest"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Running GitHub Actions Workflow Locally" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Workflow: $WorkflowName" -ForegroundColor Yellow
Write-Host "Using Act: $ActVersion" -ForegroundColor Yellow
Write-Host ""

# Check if act is installed
$actInstalled = Get-Command act -ErrorAction SilentlyContinue
if (-not $actInstalled) {
    Write-Host "❌ Act is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Install Act:" -ForegroundColor Yellow
    Write-Host "  Windows (choco): choco install act-cli" -ForegroundColor Green
    Write-Host "  Or download from: https://github.com/nektos/act/releases" -ForegroundColor Green
    Write-Host ""
    exit 1
}

# Check if .secrets file exists
if (-not (Test-Path ".secrets")) {
    Write-Host "⚠️  Warning: .secrets file not found!" -ForegroundColor Yellow
    Write-Host "Creating template .secrets file..." -ForegroundColor Yellow
    
    @"
# GitHub Secrets for local testing
# Copy values from GitHub repository settings -> Secrets -> Actions
FOCUS_BASE_URL=https://your-focus-server-url
FOCUS_API_PREFIX=/focus-server
VERIFY_SSL=false
"@ | Out-File -FilePath ".secrets" -Encoding UTF8
    
    Write-Host "✅ Created .secrets template. Please fill in your values." -ForegroundColor Green
    Write-Host ""
}

# Run the workflow
Write-Host "🚀 Running workflow: $WorkflowName" -ForegroundColor Cyan
Write-Host ""

$workflowPath = ".github/workflows/${WorkflowName}.yml"
if (-not (Test-Path $workflowPath)) {
    Write-Host "❌ Workflow file not found: $workflowPath" -ForegroundColor Red
    exit 1
}

act workflow_dispatch `
    --workflows $workflowPath `
    --secret-file .secrets `
    --env FOCUS_ENV=local `
    --container-architecture linux/amd64 `
    --verbose

Write-Host ""
Write-Host "✅ Workflow completed!" -ForegroundColor Green

