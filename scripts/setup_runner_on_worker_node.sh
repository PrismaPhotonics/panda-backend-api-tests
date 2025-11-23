#!/bin/bash
# Complete setup script - run this on worker-node after SSH connection
# This script downloads and installs everything needed

set -e

echo "=========================================="
echo "Contract Tests Runner - Complete Setup"
echo "=========================================="
echo ""
echo "This script will:"
echo "  1. Download the installation script"
echo "  2. Install GitHub Actions Runner"
echo "  3. Configure it for contract tests"
echo ""

# Check if we can access Focus Server
echo "Checking network access..."
if curl -sk --max-time 5 https://10.10.10.100/focus-server/channels > /dev/null 2>&1; then
    echo "✅ Can access Focus Server (10.10.10.100)"
else
    echo "⚠️  WARNING: Cannot access Focus Server"
    echo "   Contract tests will fail if server is unreachable"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Download installation script
echo ""
echo "Downloading installation script..."
INSTALL_SCRIPT="/tmp/install_contract_tests_runner.sh"
curl -L -o "$INSTALL_SCRIPT" https://raw.githubusercontent.com/PrismaPhotonics/panda-backend-api-tests/main/scripts/install_contract_tests_runner.sh

if [ ! -f "$INSTALL_SCRIPT" ]; then
    echo "❌ Failed to download script"
    echo ""
    echo "Alternative: Clone the repo first:"
    echo "  git clone https://github.com/PrismaPhotonics/panda-backend-api-tests.git"
    echo "  cd panda-backend-api-tests"
    echo "  sudo bash scripts/install_contract_tests_runner.sh"
    exit 1
fi

chmod +x "$INSTALL_SCRIPT"
echo "✅ Script downloaded"

# Run installation
echo ""
echo "=========================================="
echo "Starting installation..."
echo "=========================================="
echo ""
echo "You will need a registration token from GitHub:"
echo "  1. Go to: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/new"
echo "  2. Select 'Linux'"
echo "  3. Copy the registration token"
echo ""

sudo bash "$INSTALL_SCRIPT"

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Verify runner is online: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners"
echo "  2. Push a commit to trigger contract tests"
echo ""

