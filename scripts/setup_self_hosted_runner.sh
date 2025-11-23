#!/bin/bash
# Script to setup self-hosted runner on Linux
# Run this script on the lab machine

set -e

REPO_URL="${1:-https://github.com/PrismaPhotonics/panda-backend-api-tests}"
RUNNER_NAME="${2:-staging-linux-runner-01}"
INSTALL_PATH="${3:-/opt/actions-runner}"

echo "=========================================="
echo "Setting up Self-Hosted Runner"
echo "=========================================="
echo ""

echo "Repository: $REPO_URL"
echo "Runner Name: $RUNNER_NAME"
echo "Install Path: $INSTALL_PATH"
echo ""

# Create installation directory
mkdir -p "$INSTALL_PATH"
cd "$INSTALL_PATH"

# Download runner
echo "Downloading GitHub Actions Runner..."
RUNNER_VERSION="2.311.0"
RUNNER_URL="https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz"

if ! curl -L -o actions-runner.tar.gz "$RUNNER_URL"; then
    echo "❌ Failed to download runner"
    exit 1
fi

echo "✅ Download completed"

# Extract runner
echo "Extracting runner..."
tar xzf actions-runner.tar.gz
rm actions-runner.tar.gz
echo "✅ Extraction completed"

# Configure runner
echo ""
echo "Configuring runner..."
echo "You will need a registration token from GitHub:"
echo "  1. Go to: https://github.com/YOUR_ORG/YOUR_REPO/settings/actions/runners/new"
echo "  2. Copy the registration token"
echo ""

read -p "Enter registration token: " TOKEN

./config.sh \
    --url "$REPO_URL" \
    --token "$TOKEN" \
    --name "$RUNNER_NAME" \
    --labels "self-hosted,Linux" \
    --work "_work" \
    --replace

echo "✅ Configuration completed"

# Install as service
echo ""
echo "Installing as systemd service..."
sudo ./svc.sh install
sudo ./svc.sh start

echo ""
echo "=========================================="
echo "✅ Self-Hosted Runner Setup Complete!"
echo "=========================================="
echo ""
echo "Runner Name: $RUNNER_NAME"
echo "Installation Path: $INSTALL_PATH"
echo ""
echo "To check status:"
echo "  cd $INSTALL_PATH"
echo "  sudo ./svc.sh status"
echo ""
echo "To verify runner is online:"
echo "  Visit: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners"
echo ""
echo "⚠️  IMPORTANT: Make sure this machine can access 10.10.10.100 (staging network)"
echo "   Test with: curl -k https://10.10.10.100/focus-server/channels"
echo ""

