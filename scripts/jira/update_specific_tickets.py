"""
Update Specific Jira Tickets with Test Location
===============================================

Quick script to update specific tickets with test location including
specific file paths in GitHub repository.
"""

import sys
import os
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from external.jira import JiraClient

# GitHub repository URL for tests
TEST_REPOSITORY_URL = "https://github.com/PrismaPhotonics/panda-backend-api-tests.git"
TEST_REPOSITORY_DISPLAY = "https://github.com/PrismaPhotonics/panda-backend-api-tests"
TEST_REPOSITORY_BASE = "https://github.com/PrismaPhotonics/panda-backend-api-tests"

# Get current branch from git
def get_current_branch():
    """Get current git branch."""
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent
        )
        branch = result.stdout.strip()
        
        # Check if branch exists on remote
        if branch:
            check_result = subprocess.run(
                ['git', 'ls-remote', '--heads', 'origin', branch],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent.parent
            )
            # If branch exists on remote, use it; otherwise use main
            if check_result.stdout.strip():
                return branch
        
        # Default to main if branch not found or not on remote
        return 'main'
    except:
        return 'main'

# Current branch for GitHub links
GITHUB_BRANCH = get_current_branch()

# Remove debug print - it will be shown when script runs

# Mapping of ticket keys to test file paths
TICKET_TO_TEST_FILE = {
    'PZ-14504': {
        'files': [
            'tests/integration/api/test_orchestration_validation.py',
            'tests/infrastructure/test_k8s_job_lifecycle.py'
        ],
        'description': 'Kubernetes orchestration and job lifecycle tests'
    },
    'PZ-14509': {
        'files': [
            'tests/data_quality/test_mongodb_schema_validation.py',
            'tests/data_quality/test_mongodb_data_quality.py',
            'tests/unit/test_models_validation.py'
        ],
        'description': 'Data validation and schema tests'
    },
    'PZ-14518': {
        'files': [
            'tests/load/test_job_capacity_limits.py',
            'tests/integration/performance/test_performance_high_priority.py',
            'tests/performance/test_mongodb_outage_resilience.py'
        ],
        'description': 'Performance and load tests'
    },
    'PZ-14526': {
        'files': [
            'tests/infrastructure/test_basic_connectivity.py',
            'tests/infrastructure/test_external_connectivity.py',
            'tests/infrastructure/test_k8s_job_lifecycle.py',
            'tests/infrastructure/test_pz_integration.py',
            'tests/infrastructure/test_rabbitmq_connectivity.py',
            'tests/infrastructure/test_system_behavior.py'
        ],
        'description': 'Infrastructure and setup tests'
    },
    'PZ-14488': {
        'files': [
            'tests/integration/api/test_api_endpoints_high_priority.py',
            'tests/integration/api/test_api_endpoints_additional.py',
            'tests/integration/api/test_health_check.py',
            'tests/integration/api/test_live_monitoring_flow.py',
            'tests/integration/api/test_historic_playback_e2e.py',
            'tests/integration/api/test_orchestration_validation.py'
        ],
        'description': 'API endpoint tests for Focus Server'
    }
}

def format_test_location_section(ticket_key, test_files=None):
    """
    Format test location section for ticket description.
    
    Args:
        ticket_key: Ticket key (e.g., "PZ-14504")
        test_files: List of test file paths (optional)
    
    Returns:
        Formatted test location section
    """
    ticket_info = TICKET_TO_TEST_FILE.get(ticket_key, {})
    files = test_files or ticket_info.get('files', [])
    description = ticket_info.get('description', 'Test files')
    
    section = f"""
---
## Test Location

**Repository:** {TEST_REPOSITORY_DISPLAY}

**Git URL:** `{TEST_REPOSITORY_URL}`

**Status:** ✅ Tests implemented and available in repository

"""
    
    if files:
        section += f"**Test Files:**\n\n"
        for file_path in files:
            # Create GitHub URL to file - use main branch (default branch)
            github_url = f"{TEST_REPOSITORY_BASE}/blob/main/{file_path}"
            # Use Jira-compatible link format
            section += f"* [{file_path}|{github_url}]\n"
        
        section += f"\n**Description:** {description}\n"
    
    section += "\n---\n"
    
    return section

def has_test_location(ticket):
    """Check if ticket already has test location information."""
    description = ticket.get('description', '')
    test_markers = [
        'test location',
        'test repository',
        'github.com/prismaphotonics/panda-backend-api-tests',
        'panda-backend-api-tests'
    ]
    description_lower = description.lower()
    return any(marker in description_lower for marker in test_markers)

def find_test_files_for_ticket(ticket_key, ticket_summary):
    """
    Find test files related to a ticket based on ticket key and summary.
    
    Args:
        ticket_key: Ticket key (e.g., "PZ-14504")
        ticket_summary: Ticket summary
    
    Returns:
        List of test file paths
    """
    # Check if we have a mapping for this ticket
    if ticket_key in TICKET_TO_TEST_FILE:
        return TICKET_TO_TEST_FILE[ticket_key]['files']
    
    # If not in mapping, try to infer from summary
    summary_lower = ticket_summary.lower()
    test_files = []
    
    # Search for matching test files based on keywords
    tests_dir = Path(__file__).parent.parent.parent / 'tests'
    
    if 'orchestration' in summary_lower or 'kubernetes' in summary_lower or 'k8s' in summary_lower:
        # Look for orchestration/K8s tests
        for pattern in ['**/test_*orchestration*.py', '**/test_*k8s*.py', '**/test_*kubernetes*.py']:
            for file_path in tests_dir.glob(pattern):
                rel_path = str(file_path.relative_to(tests_dir.parent))
                test_files.append(rel_path)
    
    elif 'validation' in summary_lower or 'schema' in summary_lower or 'data' in summary_lower:
        # Look for validation/schema tests
        for pattern in ['**/test_*validation*.py', '**/test_*schema*.py', '**/test_*data*.py']:
            for file_path in tests_dir.glob(pattern):
                rel_path = str(file_path.relative_to(tests_dir.parent))
                if 'data_quality' in rel_path or 'validation' in rel_path:
                    test_files.append(rel_path)
    
    elif 'performance' in summary_lower or 'load' in summary_lower:
        # Look for performance/load tests
        for pattern in ['**/test_*performance*.py', '**/test_*load*.py']:
            for file_path in tests_dir.glob(pattern):
                rel_path = str(file_path.relative_to(tests_dir.parent))
                test_files.append(rel_path)
    
    elif 'infrastructure' in summary_lower or 'setup' in summary_lower:
        # Look for infrastructure tests
        for pattern in ['**/test_*infrastructure*.py', '**/test_*connectivity*.py']:
            for file_path in tests_dir.glob(pattern):
                rel_path = str(file_path.relative_to(tests_dir.parent))
                if 'infrastructure' in rel_path:
                    test_files.append(rel_path)
    
    # Remove duplicates and sort
    test_files = sorted(list(set(test_files)))
    
    return test_files

def main():
    """Update specific tickets."""
    client = JiraClient()
    
    ticket_keys = ['PZ-14504', 'PZ-14509', 'PZ-14518', 'PZ-14526', 'PZ-14488']
    
    print("=" * 80)
    print("Updating specific tickets with test location...")
    print("=" * 80)
    
    updated = []
    skipped = []
    errors = []
    
    for ticket_key in ticket_keys:
        try:
            print(f"\nChecking ticket: {ticket_key}")
            ticket = client.get_issue(ticket_key)
            
            summary = ticket.get('summary', 'N/A')
            status = ticket.get('status', 'N/A')
            
            print(f"  Summary: {summary}")
            print(f"  Status: {status}")
            
            # Find test files for this ticket
            test_files = find_test_files_for_ticket(ticket_key, summary)
            
            if test_files:
                print(f"  Found {len(test_files)} test file(s):")
                for file_path in test_files:
                    print(f"    - {file_path}")
            else:
                print(f"  [WARNING] No test files found for this ticket")
            
            # Check if already has test location
            if has_test_location(ticket):
                print(f"  [INFO] Already has test location, but will update with specific file paths")
            
            # Get current description
            current_description = ticket.get('description', '')
            
            # Remove old test location section if exists
            if '## Test Location' in current_description:
                # Find and remove the old test location section
                lines = current_description.split('\n')
                new_lines = []
                skip_section = False
                for line in lines:
                    if line.strip().startswith('## Test Location'):
                        skip_section = True
                        continue
                    elif skip_section and line.strip().startswith('---'):
                        skip_section = False
                        continue
                    elif not skip_section:
                        new_lines.append(line)
                current_description = '\n'.join(new_lines).strip()
            
            # Add new test location section with specific file paths
            test_location_section = format_test_location_section(ticket_key, test_files)
            
            if current_description:
                new_description = f"{current_description}\n{test_location_section}"
            else:
                new_description = test_location_section.strip()
            
            # Update ticket
            updated_ticket = client.update_issue(
                issue_key=ticket_key,
                description=new_description
            )
            
            print(f"  [OK] Updated successfully!")
            print(f"  URL: {ticket.get('url', 'N/A')}")
            updated.append({
                'key': ticket_key,
                'summary': summary,
                'files': test_files
            })
            
        except Exception as e:
            print(f"  [ERROR] Error: {e}")
            import traceback
            traceback.print_exc()
            errors.append({'key': ticket_key, 'error': str(e)})
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"[OK] Updated: {len(updated)}")
    print(f"[SKIP] Skipped: {len(skipped)}")
    print(f"[ERROR] Errors: {len(errors)}")
    
    if updated:
        print("\nUpdated tickets:")
        for item in updated:
            print(f"  [OK] {item['key']}: {item['summary']}")
            if item['files']:
                print(f"    Test files ({len(item['files'])}):")
                for file_path in item['files']:
                    print(f"      - {file_path}")
    
    if skipped:
        print("\nSkipped tickets (already have test location):")
        for key in skipped:
            print(f"  [SKIP] {key}")
    
    if errors:
        print("\nErrors:")
        for err in errors:
            print(f"  [ERROR] {err['key']}: {err['error']}")

if __name__ == '__main__':
    main()
