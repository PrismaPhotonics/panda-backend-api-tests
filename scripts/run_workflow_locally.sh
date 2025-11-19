#!/bin/bash
# Script to run GitHub Actions workflows locally using Act
# https://github.com/nektos/act

set -e

WORKFLOW_NAME="${1:-smoke-tests}"
ACT_VERSION="${ACT_VERSION:-latest}"

echo "=========================================="
echo "Running GitHub Actions Workflow Locally"
echo "=========================================="
echo "Workflow: $WORKFLOW_NAME"
echo "Using Act: $ACT_VERSION"
echo ""

# Check if act is installed
if ! command -v act &> /dev/null; then
    echo "❌ Act is not installed!"
    echo ""
    echo "Install Act:"
    echo "  Windows (choco): choco install act-cli"
    echo "  macOS (brew):    brew install act"
    echo "  Linux:           curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash"
    echo ""
    echo "Or download from: https://github.com/nektos/act/releases"
    exit 1
fi

# Check if .secrets file exists
if [ ! -f ".secrets" ]; then
    echo "⚠️  Warning: .secrets file not found!"
    echo "Creating template .secrets file..."
    cat > .secrets << EOF
# GitHub Secrets for local testing
# Copy values from GitHub repository settings -> Secrets -> Actions
FOCUS_BASE_URL=https://your-focus-server-url
FOCUS_API_PREFIX=/focus-server
VERIFY_SSL=false
EOF
    echo "✅ Created .secrets template. Please fill in your values."
    echo ""
fi

# Run the workflow
echo "🚀 Running workflow: $WORKFLOW_NAME"
echo ""

act workflow_dispatch \
    --workflows ".github/workflows/${WORKFLOW_NAME}.yml" \
    --secret-file .secrets \
    --env FOCUS_ENV=local \
    --container-architecture linux/amd64 \
    --verbose

echo ""
echo "✅ Workflow completed!"

