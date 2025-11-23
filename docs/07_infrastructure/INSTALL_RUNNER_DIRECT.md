# התקנת Runner - ישירות על worker-node

## אתה כבר על worker-node! עכשיו:

### שלב 1: צור את הסקריפט ישירות

```bash
# על worker-node, צור את הסקריפט:
cat > /tmp/install_runner.sh << 'EOF'
#!/bin/bash
set -e

REPO="https://github.com/PrismaPhotonics/panda-backend-api-tests"
RUNNER_NAME="staging-contract-tests-runner"
INSTALL_PATH="/opt/actions-runner"

echo "=========================================="
echo "Contract Tests Runner Setup"
echo "=========================================="
echo ""

# Check network access
echo "Checking network access..."
if curl -sk --max-time 5 https://10.10.10.100/focus-server/channels > /dev/null 2>&1; then
    echo "✅ Network access OK"
else
    echo "⚠️  WARNING: Cannot reach 10.10.10.100"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create installation directory
echo "Creating installation directory..."
sudo mkdir -p "$INSTALL_PATH"
cd "$INSTALL_PATH"

# Download runner
echo "Downloading GitHub Actions Runner..."
RUNNER_VERSION="2.311.0"
RUNNER_URL="https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz"

if ! sudo curl -L -o actions-runner.tar.gz "$RUNNER_URL"; then
    echo "❌ Failed to download runner"
    exit 1
fi

echo "✅ Download completed"

# Extract runner
echo "Extracting runner..."
sudo tar xzf actions-runner.tar.gz
sudo rm actions-runner.tar.gz
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

sudo ./config.sh \
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
sudo ./svc.sh install
sudo ./svc.sh start

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Runner Name: $RUNNER_NAME"
echo "Installation Path: $INSTALL_PATH"
echo ""
echo "Service Status:"
sudo ./svc.sh status
echo ""
echo "To check runner online:"
echo "  Visit: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners"
echo ""
EOF

chmod +x /tmp/install_runner.sh
```

### שלב 2: הרץ את הסקריפט

```bash
# הרץ עם sudo:
sudo bash /tmp/install_runner.sh
```

### שלב 3: קבל Token מ-GitHub

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/new
2. בחר **Linux**
3. העתק את ה-token
4. הדבק בסקריפט כשהוא שואל

---

## או: Clone את ה-repo

אם יש לך git על worker-node:

```bash
# Clone את ה-repo
git clone https://github.com/PrismaPhotonics/panda-backend-api-tests.git
cd panda-backend-api-tests

# הרץ את הסקריפט
sudo bash scripts/install_contract_tests_runner.sh
```

---

## Copy & Paste הכל ביחד:

```bash
# צור את הסקריפט:
cat > /tmp/install_runner.sh << 'EOF'
#!/bin/bash
set -e
REPO="https://github.com/PrismaPhotonics/panda-backend-api-tests"
RUNNER_NAME="staging-contract-tests-runner"
INSTALL_PATH="/opt/actions-runner"
echo "=========================================="
echo "Contract Tests Runner Setup"
echo "=========================================="
echo "Checking network access..."
if curl -sk --max-time 5 https://10.10.10.100/focus-server/channels > /dev/null 2>&1; then
    echo "✅ Network access OK"
else
    echo "⚠️  WARNING: Cannot reach 10.10.10.100"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then exit 1; fi
fi
echo "Creating installation directory..."
sudo mkdir -p "$INSTALL_PATH"
cd "$INSTALL_PATH"
echo "Downloading GitHub Actions Runner..."
RUNNER_VERSION="2.311.0"
RUNNER_URL="https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz"
if ! sudo curl -L -o actions-runner.tar.gz "$RUNNER_URL"; then
    echo "❌ Failed to download runner"
    exit 1
fi
echo "✅ Download completed"
echo "Extracting runner..."
sudo tar xzf actions-runner.tar.gz
sudo rm actions-runner.tar.gz
echo "✅ Extraction completed"
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
sudo ./config.sh --url "$REPO" --token "$TOKEN" --name "$RUNNER_NAME" --labels "self-hosted,Linux" --work "_work" --replace
echo "✅ Configuration completed"
echo ""
echo "Installing as systemd service..."
sudo ./svc.sh install
sudo ./svc.sh start
echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Runner Name: $RUNNER_NAME"
echo "Installation Path: $INSTALL_PATH"
sudo ./svc.sh status
echo ""
echo "To check runner online:"
echo "  Visit: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners"
echo ""
EOF

chmod +x /tmp/install_runner.sh
sudo bash /tmp/install_runner.sh
```

---

**זה הכל! אחרי שהתקנת, ה-runner יהיה online וה-contract tests ירוצו אוטומטית! 🚀**

