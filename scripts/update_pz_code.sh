#!/bin/bash
# ============================================================================
# Update PZ Code from Bitbucket
# ============================================================================
# This script updates PZ code on the worker node from Bitbucket repository
# Usage: ./update_pz_code.sh [branch_name]
# ============================================================================

set -e  # Exit on error

# Configuration
PZ_DIR="/home/prisma/pz"
BACKUP_DIR="/home/prisma/pz_backups"
DEFAULT_BRANCH="master"
BRANCH="${1:-$DEFAULT_BRANCH}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  PZ Code Update Script${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"

# Check if we're on the correct host
HOSTNAME=$(hostname)
echo -e "${YELLOW}[INFO]${NC} Running on: $HOSTNAME"

# Check if PZ directory exists
if [ ! -d "$PZ_DIR" ]; then
    echo -e "${RED}[ERROR]${NC} PZ directory not found: $PZ_DIR"
    echo -e "${YELLOW}[INFO]${NC} Please clone the repository first."
    exit 1
fi

# Navigate to PZ directory
cd "$PZ_DIR" || exit 1
echo -e "${GREEN}[OK]${NC} Changed to: $(pwd)"

# Check if it's a git repository
if [ ! -d ".git" ]; then
    echo -e "${RED}[ERROR]${NC} Not a git repository!"
    exit 1
fi

# Display current status
echo -e "\n${YELLOW}[INFO]${NC} Current Git Status:"
echo "─────────────────────────────────────────────────────────────"
git status --short
echo "─────────────────────────────────────────────────────────────"

# Display current branch and commit
CURRENT_BRANCH=$(git branch --show-current)
CURRENT_COMMIT=$(git rev-parse --short HEAD)
echo -e "${YELLOW}[INFO]${NC} Current branch: ${CYAN}$CURRENT_BRANCH${NC}"
echo -e "${YELLOW}[INFO]${NC} Current commit: ${CYAN}$CURRENT_COMMIT${NC}"

# Check for uncommitted changes
if [[ -n $(git status --porcelain) ]]; then
    echo -e "\n${YELLOW}[WARNING]${NC} You have uncommitted changes!"
    git status --short
    
    read -p "Do you want to stash these changes? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        git stash save "Auto-stash before pull - $TIMESTAMP"
        echo -e "${GREEN}[OK]${NC} Changes stashed"
        STASHED=true
    else
        echo -e "${RED}[ABORT]${NC} Please commit or stash your changes first"
        exit 1
    fi
fi

# Fetch latest changes
echo -e "\n${YELLOW}[INFO]${NC} Fetching latest changes from remote..."
git fetch origin

# Check if branch exists on remote
if git ls-remote --exit-code --heads origin "$BRANCH" > /dev/null 2>&1; then
    echo -e "${GREEN}[OK]${NC} Branch '$BRANCH' exists on remote"
else
    echo -e "${RED}[ERROR]${NC} Branch '$BRANCH' not found on remote"
    echo -e "${YELLOW}[INFO]${NC} Available branches:"
    git branch -r
    exit 1
fi

# Checkout the branch if different
if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
    echo -e "\n${YELLOW}[INFO]${NC} Switching to branch: $BRANCH"
    git checkout "$BRANCH"
    echo -e "${GREEN}[OK]${NC} Switched to branch: $BRANCH"
fi

# Show what will be updated
echo -e "\n${YELLOW}[INFO]${NC} Changes to be pulled:"
echo "─────────────────────────────────────────────────────────────"
git log HEAD..origin/$BRANCH --oneline --max-count=10
echo "─────────────────────────────────────────────────────────────"

# Ask for confirmation
read -p "Do you want to pull these changes? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}[ABORT]${NC} Pull cancelled by user"
    exit 1
fi

# Pull the latest changes
echo -e "\n${YELLOW}[INFO]${NC} Pulling latest changes from origin/$BRANCH..."
git pull origin "$BRANCH"
NEW_COMMIT=$(git rev-parse --short HEAD)

echo -e "${GREEN}[OK]${NC} Code updated successfully!"
echo -e "${YELLOW}[INFO]${NC} Previous commit: ${CYAN}$CURRENT_COMMIT${NC}"
echo -e "${YELLOW}[INFO]${NC} New commit:      ${CYAN}$NEW_COMMIT${NC}"

# Restore stashed changes if any
if [ "$STASHED" = true ]; then
    echo -e "\n${YELLOW}[INFO]${NC} Restoring stashed changes..."
    if git stash pop; then
        echo -e "${GREEN}[OK]${NC} Stashed changes restored"
    else
        echo -e "${RED}[WARNING]${NC} Conflicts while restoring stashed changes"
        echo -e "${YELLOW}[INFO]${NC} Please resolve conflicts manually"
    fi
fi

# Show what changed
echo -e "\n${YELLOW}[INFO]${NC} Files changed in this update:"
echo "─────────────────────────────────────────────────────────────"
git diff --name-status $CURRENT_COMMIT..$NEW_COMMIT
echo "─────────────────────────────────────────────────────────────"

# Check if config files were updated
if git diff --name-only $CURRENT_COMMIT..$NEW_COMMIT | grep -q "config/py/"; then
    echo -e "\n${YELLOW}[WARNING]${NC} Configuration files were updated!"
    echo -e "${YELLOW}[INFO]${NC} You may need to restart the Focus Server pod"
    
    read -p "Do you want to restart the Focus Server pod now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "\n${YELLOW}[INFO]${NC} Restarting Focus Server pod..."
        POD_NAME=$(kubectl get pods -n panda -l app.kubernetes.io/name=panda-panda-focus-server -o name | head -1)
        
        if [ -n "$POD_NAME" ]; then
            kubectl delete $POD_NAME -n panda
            echo -e "${GREEN}[OK]${NC} Pod deleted. It will restart automatically."
            echo -e "${YELLOW}[INFO]${NC} Wait ~30 seconds for the new pod to be ready"
            
            # Wait and show pod status
            sleep 5
            echo -e "\n${YELLOW}[INFO]${NC} Current pod status:"
            kubectl get pods -n panda | grep focus-server
        else
            echo -e "${RED}[ERROR]${NC} Could not find Focus Server pod"
        fi
    fi
fi

echo -e "\n${CYAN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Update completed successfully!${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"

# Show summary
echo -e "\n${YELLOW}Summary:${NC}"
echo "  • Branch:        $BRANCH"
echo "  • Old commit:    $CURRENT_COMMIT"
echo "  • New commit:    $NEW_COMMIT"
echo "  • Files changed: $(git diff --name-only $CURRENT_COMMIT..$NEW_COMMIT | wc -l)"
echo ""

