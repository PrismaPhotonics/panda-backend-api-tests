#!/usr/bin/env bash
################################################################################
# Update PZ Git Submodule to Latest Version
################################################################################
#
# This Bash script updates the PZ development repository submodule
# to the latest version from the remote repository.
#
# Features:
# - Automatic submodule initialization if needed
# - Fetches latest changes from remote
# - Shows before/after commit info
# - Error handling and status reporting
#
# Usage:
#   ./update_pz_submodule.sh                  # Update to latest master
#   ./update_pz_submodule.sh --branch develop # Update to specific branch
#   ./update_pz_submodule.sh --status         # Show status only
#   ./update_pz_submodule.sh --init           # Initialize submodule
#
# Author: QA Automation Architect
# Requires: Git installed and in PATH
################################################################################

set -euo pipefail

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly CYAN='\033[0;36m'
readonly MAGENTA='\033[0;35m'
readonly NC='\033[0m' # No Color

# Default values
BRANCH="master"
OPERATION="sync"

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PZ_SUBMODULE_PATH="$PROJECT_ROOT/external/pz"

################################################################################
# Output functions
################################################################################

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

print_header() {
    echo -e "\n${MAGENTA}$(printf '=%.0s' {1..80})${NC}"
    echo -e "${MAGENTA}$1${NC}"
    echo -e "${MAGENTA}$(printf '=%.0s' {1..80})${NC}"
}

################################################################################
# Helper functions
################################################################################

check_git_installed() {
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed or not in PATH"
        exit 1
    fi
}

test_submodule_exists() {
    if [ ! -d "$PZ_SUBMODULE_PATH" ]; then
        return 1
    fi

    if [ ! -d "$PZ_SUBMODULE_PATH/.git" ] && [ ! -f "$PZ_SUBMODULE_PATH/.git" ]; then
        return 1
    fi

    return 0
}

initialize_submodule() {
    print_info "Initializing PZ submodule..."

    cd "$PROJECT_ROOT"

    if git submodule update --init --recursive external/pz; then
        print_success "Submodule initialized successfully"
        return 0
    else
        print_error "Submodule initialization failed"
        return 1
    fi
}

get_current_commit() {
    cd "$PZ_SUBMODULE_PATH"
    git rev-parse HEAD 2>/dev/null | cut -c1-8 || echo "unknown"
}

get_current_branch() {
    cd "$PZ_SUBMODULE_PATH"
    git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown"
}

get_last_commit_info() {
    cd "$PZ_SUBMODULE_PATH"
    git log -1 --format="%ci - %s" 2>/dev/null || echo "Unknown"
}

################################################################################
# Main operations
################################################################################

show_submodule_status() {
    print_header "📊 PZ Repository Status"

    if ! test_submodule_exists; then
        print_warning "Submodule not initialized"
        print_info "Run: ./update_pz_submodule.sh --init"
        return
    fi

    local commit=$(get_current_commit)
    local branch=$(get_current_branch)
    local last_commit=$(get_last_commit_info)

    # Get file count
    cd "$PZ_SUBMODULE_PATH"
    local file_count=$(git ls-files 2>/dev/null | wc -l)

    echo
    print_info "📍 Location: $PZ_SUBMODULE_PATH"
    print_info "🌿 Branch: $branch"
    print_info "📌 Commit: $commit"
    print_info "📅 Last Commit: $last_commit"
    print_info "📦 Files: $file_count"
    echo -e "${MAGENTA}$(printf '=%.0s' {1..80})${NC}\n"
}

sync_submodule_to_latest() {
    local target_branch=$1

    print_header "🔄 Starting PZ Repository Sync"

    # Check if submodule exists
    if ! test_submodule_exists; then
        print_info "Submodule not initialized. Initializing..."
        if ! initialize_submodule; then
            return 1
        fi
    fi

    # Show current state
    local current_commit=$(get_current_commit)
    local current_branch=$(get_current_branch)

    if [ "$current_commit" != "unknown" ] && [ "$current_branch" != "unknown" ]; then
        print_info "📌 Current state: $current_branch @ $current_commit"
    fi

    # Fetch latest changes
    print_info "📥 Fetching latest changes from remote..."
    cd "$PZ_SUBMODULE_PATH"

    if ! git fetch origin 2>&1; then
        print_error "Failed to fetch from remote"
        return 1
    fi

    # Checkout specific branch
    print_info "🔀 Checking out branch: $target_branch"
    if ! git checkout "$target_branch" 2>&1; then
        print_error "Failed to checkout branch: $target_branch"
        return 1
    fi

    # Pull latest changes
    print_info "⬇️  Pulling latest changes..."
    if ! git pull origin "$target_branch" 2>&1; then
        print_error "Failed to pull latest changes"
        return 1
    fi

    # Get new state
    local new_commit=$(get_current_commit)
    local new_branch=$(get_current_branch)

    print_header "✅ Sync Completed Successfully!"
    print_success "📌 New state: $new_branch @ $new_commit"

    # Show summary
    if [ "$current_commit" != "$new_commit" ]; then
        print_info "📝 Updated from $current_commit to $new_commit"
    else
        print_info "📝 Already up-to-date"
    fi

    echo -e "${MAGENTA}$(printf '=%.0s' {1..80})${NC}\n"
    return 0
}

################################################################################
# Argument parsing
################################################################################

show_help() {
    cat << EOF
Usage: $0 [OPTIONS]

Update PZ Git Submodule to Latest Version

OPTIONS:
    --branch BRANCH    Specific branch to sync to (default: master)
    --init             Initialize submodule if not already done
    --status           Show current submodule status without updating
    -h, --help         Show this help message

EXAMPLES:
    $0                        # Update to latest master
    $0 --branch develop       # Update to latest develop branch
    $0 --status               # Show current status
    $0 --init                 # Initialize submodule

EOF
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --branch)
            BRANCH="$2"
            shift 2
            ;;
        --init)
            OPERATION="init"
            shift
            ;;
        --status)
            OPERATION="status"
            shift
            ;;
        -h|--help)
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            ;;
    esac
done

################################################################################
# Main execution
################################################################################

main() {
    check_git_installed

    case $OPERATION in
        status)
            show_submodule_status
            ;;
        init)
            if test_submodule_exists; then
                print_success "Submodule already initialized"
                show_submodule_status
            else
                if initialize_submodule; then
                    show_submodule_status
                    exit 0
                else
                    exit 1
                fi
            fi
            ;;
        sync)
            if sync_submodule_to_latest "$BRANCH"; then
                exit 0
            else
                exit 1
            fi
            ;;
        *)
            print_error "Unknown operation: $OPERATION"
            exit 1
            ;;
    esac
}

main
