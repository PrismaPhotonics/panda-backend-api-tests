#!/usr/bin/env python3
"""Delete old workflow runs from GitHub Actions to clean up sidebar."""
import requests
import os
import sys

def main():
    # Get GitHub token
    token = os.environ.get('GITHUB_TOKEN', '')
    if not token:
        print("ERROR: GITHUB_TOKEN not set in environment")
        print("Please set it with:")
        print('  $env:GITHUB_TOKEN = "ghp_your_token_here"')
        print("\nYou can create a token at: https://github.com/settings/tokens")
        print("Required scopes: repo, workflow")
        sys.exit(1)

    repo = 'PrismaPhotonics/panda-backend-api-tests'
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Workflows to delete (by filename)
    workflows_to_delete = [
        'smoke.yml',
        'ci.yml', 
        'readme-check.yml',
        'reusable-python-tests.yml'
    ]

    print(f"Fetching workflows from {repo}...")
    
    # List all workflows
    url = f'https://api.github.com/repos/{repo}/actions/workflows'
    r = requests.get(url, headers=headers)
    
    if r.status_code != 200:
        print(f"Error fetching workflows: {r.status_code} - {r.text}")
        sys.exit(1)
    
    workflows = r.json().get('workflows', [])
    print(f"Found {len(workflows)} workflows\n")

    for workflow in workflows:
        workflow_name = workflow['name']
        workflow_path = workflow['path']
        workflow_id = workflow['id']
        
        # Check if this workflow should be deleted
        filename = workflow_path.split('/')[-1]
        if filename not in workflows_to_delete:
            print(f"SKIP: {workflow_name} ({filename})")
            continue
        
        print(f"\n{'='*60}")
        print(f"DELETING: {workflow_name} ({filename})")
        print(f"{'='*60}")
        
        # Get all runs for this workflow
        runs_url = f'https://api.github.com/repos/{repo}/actions/workflows/{workflow_id}/runs'
        runs_response = requests.get(runs_url, headers=headers, params={'per_page': 100})
        
        if runs_response.status_code != 200:
            print(f"  Error fetching runs: {runs_response.status_code}")
            continue
        
        runs = runs_response.json().get('workflow_runs', [])
        print(f"  Found {len(runs)} runs to delete")
        
        deleted_count = 0
        for run in runs:
            run_id = run['id']
            run_number = run['run_number']
            
            # Delete the run
            delete_url = f'https://api.github.com/repos/{repo}/actions/runs/{run_id}'
            delete_response = requests.delete(delete_url, headers=headers)
            
            if delete_response.status_code == 204:
                deleted_count += 1
                print(f"  Deleted run #{run_number}")
            else:
                print(f"  Failed to delete run #{run_number}: {delete_response.status_code}")
        
        print(f"  Total deleted: {deleted_count}/{len(runs)}")
    
    print(f"\n{'='*60}")
    print("DONE! Refresh GitHub Actions page to see changes.")
    print("Note: Workflows will disappear from sidebar after all runs are deleted.")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()

