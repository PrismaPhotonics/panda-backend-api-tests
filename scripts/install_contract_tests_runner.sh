#!/bin/bash
# Quick install script for Contract Tests Linux Runner
# Run this on worker-node (10.10.10.150) or any Linux machine in staging network

set -e

REPO="https://github.com/PrismaPhotonics/panda-backend-api-tests"
RUNNER_NAME="staging-contract-tests-runner"
INSTALL_PATH="/opt/actions-runner"

echo "=========================================="
echo "Contract Tests Runner Setup"
echo "=========================================="
echo ""
echo "This will install a Linux self-hosted runner for contract tests"
echo "Repository: $REPO"
echo "Runner Name: $RUNNER_NAME"
echo "Install Path: $INSTALL_PATH"
echo ""
echo "⚠️  Make sure this machine can access 10.10.10.100"
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  This script needs sudo privileges for service installation"
    echo "   Run with: sudo $0"
    exit 1
fi

# Check network access
echo "Checking network access to Focus Server..."
if curl -sk --max-time 5 https://10.10.10.100/focus-server/channels > /dev/null 2>&1; then
    echo "✅ Network access OK"
else
    echo "⚠️  WARNING: Cannot reach 10.10.10.100"
    echo "   Contract tests will fail if server is unreachable"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create installation directory
echo ""
echo "Creating installation directory..."
mkdir -p "$INSTALL_PATH"
cd "$INSTALL_PATH"

# Download runner
echo "Downloading GitHub Actions Runner..."
# Try latest release URL first
RUNNER_URL="https://github.com/actions/runner/releases/latest/download/actions-runner-linux-x64-2.311.0.tar.gz"

if ! curl -L -f -o actions-runner.tar.gz "$RUNNER_URL" 2>/dev/null; then
    # Fallback to specific version
    RUNNER_VERSION="2.311.0"
    RUNNER_URL="https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz"
    if ! curl -L -f -o actions-runner.tar.gz "$RUNNER_URL"; then
        echo "❌ Failed to download runner"
        echo "Tried URLs:"
        echo "  - https://github.com/actions/runner/releases/latest/download/actions-runner-linux-x64-2.311.0.tar.gz"
        echo "  - $RUNNER_URL"
        exit 1
    fi
fi

echo "✅ Download completed"

# Verify it's a valid tar.gz file
if ! file actions-runner.tar.gz 2>/dev/null | grep -q "gzip\|compressed"; then
    echo "⚠️  Warning: Downloaded file might not be valid gzip"
    echo "File info: $(file actions-runner.tar.gz 2>/dev/null || echo 'unknown')"
fi

# Extract runner
echo "Extracting runner..."
if ! tar xzf actions-runner.tar.gz; then
    echo "❌ Failed to extract runner archive"
    echo "File might be corrupted. Try downloading again."
    exit 1
fi
rm actions-runner.tar.gz
echo "✅ Extraction completed"

# Configure runner
echo ""
echo "=========================================="
echo "Runner Configuration"
echo "=========================================="
echo ""
echo "You need a registration token from GitHub:"
echo "  1. Go to: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/new"
echo "  2. Select 'Linux'"
echo "  3. Copy the registration token"
echo ""

read -p "Enter registration token: " TOKEN

if [ -z "$TOKEN" ]; then
    echo "❌ Token is required"
    exit 1
fi

./config.sh \
    --url "$REPO" \
    --token "$TOKEN" \
    --name "$RUNNER_NAME" \
    --labels "self-hosted,Linux" \
    --work "_work" \
    --replace

echo "✅ Configuration completed"

# Install as service
echo ""
echo "Installing as systemd service..."
./svc.sh install
./svc.sh start

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Runner Name: $RUNNER_NAME"
echo "Installation Path: $INSTALL_PATH"
echo ""
echo "Service Status:"
./svc.sh status
echo ""
echo "To check runner online:"
echo "  Visit: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners"
echo ""
echo "To view logs:"
echo "  journalctl -u actions.runner.${RUNNER_NAME}.service -f"
echo ""
echo "To restart:"
echo "  cd $INSTALL_PATH"
echo "  sudo ./svc.sh stop"
echo "  sudo ./svc.sh start"
echo ""

