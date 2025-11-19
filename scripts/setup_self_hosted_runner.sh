#!/bin/bash
# Script to setup self-hosted runner on Linux
# Run this script on the lab machine

set -e

REPO_URL="${1:-}"
RUNNER_NAME="${2:-lab-linux-runner-01}"
INSTALL_PATH="${3:-./actions-runner}"

echo "=========================================="
echo "Setting up Self-Hosted Runner"
echo "=========================================="
echo ""

if [ -z "$REPO_URL" ]; then
    echo "⚠️  Repository URL not provided, using default..."
    REPO_URL="https://github.com/PrismaPhotonics/panda-backend-api-tests"
    echo "Using: $REPO_URL"
fi

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
    --labels "self-hosted,linux,lab" \
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

