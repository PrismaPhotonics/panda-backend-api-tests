#!/bin/bash
# Run K8s Job Lifecycle Tests
# ============================
# This script runs all K8s job lifecycle tests with detailed logging and monitoring

set -e

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT"

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}K8s Job Lifecycle Tests Runner${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

echo -e "${GRAY}Project Root: $PROJECT_ROOT${NC}"
echo ""

# Build pytest command
PYTEST_ARGS=(
    "be_focus_server_tests/infrastructure/test_k8s_job_lifecycle.py"
    "-v"
    "--tb=short"
    "--log-cli-level=INFO"
    "--log-cli-format=%(asctime)s [%(levelname)8s] %(name)s: %(message)s"
    "--log-cli-date-format=%Y-%m-%d %H:%M:%S"
)

# Check for skip-health-check flag
if [[ "$*" == *"--skip-health-check"* ]]; then
    PYTEST_ARGS+=("--skip-health-check")
fi

# Check for verbose flag
if [[ "$*" == *"--verbose"* ]] || [[ "$*" == *"-v"* ]]; then
    PYTEST_ARGS+=("-s")
fi

echo -e "${YELLOW}Running pytest with arguments:${NC}"
echo -e "${GRAY}  ${PYTEST_ARGS[*]}${NC}"
echo ""

# Run tests
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}Starting Test Execution...${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

START_TIME=$(date +%s)

python -m pytest "${PYTEST_ARGS[@]}" "$@"
EXIT_CODE=$?

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}Test Execution Completed${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}Exit Code: $EXIT_CODE${NC}"
else
    echo -e "${RED}Exit Code: $EXIT_CODE${NC}"
fi

MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))
echo -e "${GRAY}Duration: ${MINUTES}m ${SECONDS}s${NC}"
echo ""

echo -e "${GRAY}Log files saved to:${NC}"
echo -e "${GRAY}  logs/test_runs/${NC}"
echo ""

exit $EXIT_CODE

