# ============================================================================
# Set Environment Variables for New Production Testing
# ============================================================================
# Run this script before running tests:
#   . .\set_production_env.ps1
# ============================================================================

Write-Host "`n=== Setting Production Environment Variables ===" -ForegroundColor Cyan

# Focus Server Configuration
$env:FOCUS_ENV = "new_production"
$env:FOCUS_SERVER_HOST = "10.10.100.100"
$env:FOCUS_SERVER_PORT = "443"
$env:FOCUS_BASE_URL = "https://10.10.100.100"  # Base URL without path - prefix will be added
$env:FOCUS_API_PREFIX = "/focus-server"         # API prefix (will create: /focus-server/channels)
$env:FOCUS_SITE_ID = "prisma-210-1000"

# MongoDB Configuration
# NOTE: These are development/testing credentials - DO NOT use production passwords here
$env:MONGODB_URI = "mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma"
$env:MONGODB_HOST = "10.10.100.108"
$env:MONGODB_PORT = "27017"
$env:MONGODB_USER = "prisma"
$env:MONGODB_PASSWORD = "prisma"
$env:MONGODB_DATABASE = "prisma"
$env:MONGODB_AUTH_SOURCE = "prisma"

# RabbitMQ Configuration
$env:RABBITMQ_HOST = "10.10.100.107"
$env:RABBITMQ_PORT = "5672"
$env:RABBITMQ_SSL_PORT = "5671"
$env:RABBITMQ_MANAGEMENT_PORT = "15672"
$env:RABBITMQ_USER = "user"
$env:RABBITMQ_PASSWORD = "prismapanda"
$env:RABBITMQ_VHOST = "/"

# Kubernetes Configuration
$env:K8S_API_SERVER = "https://10.10.100.102:6443"
$env:K8S_NAMESPACE = "panda"
$env:K8S_DASHBOARD = "https://10.10.100.102/"
$env:K8S_CONTEXT = "panda-cluster"

# SSH Access to K9s (for monitoring pods/logs)
$env:SSH_JUMP_HOST = "10.10.100.3"
$env:SSH_JUMP_USER = "root"
$env:SSH_TARGET_HOST = "10.10.100.113"
$env:SSH_TARGET_USER = "prisma"

# Kubernetes Services (Internal)
$env:FOCUS_SERVER_K8S_SERVICE = "panda-panda-focus-server.panda"
$env:FOCUS_SERVER_K8S_PORT = "5000"
$env:MONGODB_K8S_SERVICE = "mongodb.panda"
$env:RABBITMQ_K8S_SERVICE = "rabbitmq-panda.panda"

# SSL Configuration
$env:VERIFY_SSL = "false"

# API Testing
$env:API_BASE = "/focus-server"

# Load Testing (Locust)
$env:CREATE_JOB_ON_START = "true"
$env:MAX_CONCURRENT_CONFIG = "3"
$env:RETRY_ON_TIMEOUT = "true"
$env:METADATA_POLL_TIMEOUT = "120"
$env:METADATA_POLL_INTERVAL = "0.2"
$env:INITIAL_POLL_DELAY_SEC = "1.5"

# Configuration Payload Defaults
$env:CHANNEL_MIN = "1"
$env:CHANNEL_MAX = "750"
$env:VIEW_TYPE = "0"
$env:NFFT_SELECTION = "2048"
$env:FREQ_MIN = "0"
$env:FREQ_MAX = "300"
$env:DISPLAY_TIME_AXIS_DURATION = "60"
$env:DISPLAY_HEIGHT = "200"

Write-Host "`n✅ Environment variables set for:" -ForegroundColor Green
Write-Host "   Backend:        $env:FOCUS_BASE_URL$env:FOCUS_API_PREFIX/" -ForegroundColor White
Write-Host "   MongoDB:        $env:MONGODB_HOST`:$env:MONGODB_PORT" -ForegroundColor White
Write-Host "   RabbitMQ:       $env:RABBITMQ_HOST`:$env:RABBITMQ_PORT (AMQP)" -ForegroundColor White
Write-Host "   RabbitMQ UI:    $env:RABBITMQ_HOST`:$env:RABBITMQ_MANAGEMENT_PORT" -ForegroundColor White
Write-Host "   Kubernetes:     $env:K8S_API_SERVER" -ForegroundColor White
Write-Host "   K8s Namespace:  $env:K8S_NAMESPACE" -ForegroundColor White
Write-Host "   K8s Dashboard:  $env:K8S_DASHBOARD" -ForegroundColor White
Write-Host "   Database:       $env:MONGODB_DATABASE" -ForegroundColor White
Write-Host ""
Write-Host "SSH Access for K9s/Logs:" -ForegroundColor Cyan
Write-Host "   Jump Host:      $env:SSH_JUMP_HOST (user: $env:SSH_JUMP_USER)" -ForegroundColor White
Write-Host "   Target Host:    $env:SSH_TARGET_HOST (user: $env:SSH_TARGET_USER)" -ForegroundColor White
Write-Host "   Connect:        ssh $env:SSH_JUMP_USER@$env:SSH_JUMP_HOST then ssh $env:SSH_TARGET_USER@$env:SSH_TARGET_HOST" -ForegroundColor Yellow
Write-Host ""

Write-Host "Ready to run tests!" -ForegroundColor Green
Write-Host ""
Write-Host "Examples:" -ForegroundColor Yellow
Write-Host "  pytest be_focus_server_tests/unit/ -v" -ForegroundColor White
Write-Host "  pytest be_focus_server_tests/integration/data_quality/test_mongodb_data_quality.py -v" -ForegroundColor White
Write-Host "  pytest focus_server_api_load_tests/focus_api_tests/ -v" -ForegroundColor White
Write-Host ""

