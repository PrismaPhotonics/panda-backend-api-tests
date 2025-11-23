# התקנת Runner - סקריפט מתוקן

## הבעיה הייתה:
- ה-URL של ה-runner לא היה נכון
- צריך להשתמש ב-latest release URL

## סקריפט מתוקן - Copy & Paste:

```bash
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
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then exit 1; fi
fi

# Create installation directory
echo "Creating installation directory..."
sudo mkdir -p "$INSTALL_PATH"
cd "$INSTALL_PATH"

# Download runner - using latest release URL
echo "Downloading GitHub Actions Runner..."
RUNNER_URL="https://github.com/actions/runner/releases/latest/download/actions-runner-linux-x64-2.311.0.tar.gz"

# Try latest first, fallback to specific version
if ! sudo curl -L -f -o actions-runner.tar.gz "$RUNNER_URL" 2>/dev/null; then
    echo "Trying alternative URL..."
    RUNNER_URL="https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz"
    if ! sudo curl -L -f -o actions-runner.tar.gz "$RUNNER_URL"; then
        echo "❌ Failed to download runner from both URLs"
        echo "Trying to get latest version..."
        # Get latest version dynamically
        LATEST_VERSION=$(curl -s https://api.github.com/repos/actions/runner/releases/latest | grep '"tag_name":' | sed -E 's/.*"v([^"]+)".*/\1/')
        if [ -z "$LATEST_VERSION" ]; then
            echo "❌ Could not determine latest version"
            exit 1
        fi
        RUNNER_URL="https://github.com/actions/runner/releases/download/v${LATEST_VERSION}/actions-runner-linux-x64-${LATEST_VERSION}.tar.gz"
        echo "Using version: $LATEST_VERSION"
        if ! sudo curl -L -f -o actions-runner.tar.gz "$RUNNER_URL"; then
            echo "❌ Failed to download runner"
            exit 1
        fi
    fi
fi

echo "✅ Download completed"

# Verify it's a valid tar.gz file
if ! file actions-runner.tar.gz | grep -q "gzip"; then
    echo "❌ Downloaded file is not a valid gzip archive"
    echo "File type: $(file actions-runner.tar.gz)"
    exit 1
fi

# Extract runner
echo "Extracting runner..."
if ! sudo tar xzf actions-runner.tar.gz; then
    echo "❌ Failed to extract runner"
    exit 1
fi
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
sudo bash /tmp/install_runner.sh
```

---

## או: הורד ידנית

אם הסקריפט עדיין לא עובד, הורד ידנית:

```bash
# על worker-node:
cd /opt
sudo mkdir -p actions-runner
cd actions-runner

# הורד את ה-runner (נסה את זה):
sudo curl -L -o actions-runner.tar.gz https://github.com/actions/runner/releases/latest/download/actions-runner-linux-x64-2.311.0.tar.gz

# או נסה גרסה אחרת:
sudo curl -L -o actions-runner.tar.gz https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz

# בדוק שהקובץ תקין:
file actions-runner.tar.gz
# צריך להראות: gzip compressed data

# חלץ:
sudo tar xzf actions-runner.tar.gz
sudo rm actions-runner.tar.gz

# הגדר:
sudo ./config.sh --url https://github.com/PrismaPhotonics/panda-backend-api-tests --token <TOKEN> --name staging-contract-tests-runner --labels "self-hosted,Linux" --replace

# התקן כשירות:
sudo ./svc.sh install
sudo ./svc.sh start
```

---

**הסקריפט המתוקן כולל בדיקות נוספות ו-fallback URLs. נסה אותו!**

