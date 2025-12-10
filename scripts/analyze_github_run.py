#!/usr/bin/env python
"""
Analyze GitHub Actions Run Results
"""
import requests
import subprocess
import json
import sys

def get_github_token():
    """Get GitHub token from gh CLI."""
    try:
        result = subprocess.run(['gh', 'auth', 'token'], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"Error getting token: {e}")
        return None

def analyze_run(run_id: int, repo: str = "PrismaPhotonics/panda-backend-api-tests"):
    """Analyze a GitHub Actions run."""
    token = get_github_token()
    if not token:
        print("ERROR: Could not get GitHub token")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Get run details
    run_url = f'https://api.github.com/repos/{repo}/actions/runs/{run_id}'
    run_response = requests.get(run_url, headers=headers)
    
    if run_response.status_code != 200:
        print(f"ERROR: Failed to get run details: {run_response.status_code}")
        print(run_response.text)
        return
    
    run_data = run_response.json()
    
    print("=" * 60)
    print("RUN DETAILS")
    print("=" * 60)
    print(f"Name: {run_data.get('name', 'N/A')}")
    print(f"Status: {run_data.get('status', 'N/A')}")
    print(f"Conclusion: {run_data.get('conclusion', 'N/A')}")
    print(f"Branch: {run_data.get('head_branch', 'N/A')}")
    print(f"SHA: {run_data.get('head_sha', 'N/A')[:8]}")
    print(f"Created: {run_data.get('created_at', 'N/A')}")
    print(f"Updated: {run_data.get('updated_at', 'N/A')}")
    print(f"Run attempt: {run_data.get('run_attempt', 'N/A')}")
    print(f"URL: {run_data.get('html_url', 'N/A')}")
    
    # Get jobs
    jobs_url = f'{run_url}/jobs'
    jobs_response = requests.get(jobs_url, headers=headers)
    jobs_data = jobs_response.json()
    
    print("\n" + "=" * 60)
    print("JOBS")
    print("=" * 60)
    
    failed_steps = []
    
    for job in jobs_data.get('jobs', []):
        job_name = job.get('name', 'N/A')
        job_conclusion = job.get('conclusion', 'N/A')
        job_status = job.get('status', 'N/A')
        
        icon = "✅" if job_conclusion == "success" else "❌" if job_conclusion == "failure" else "⏺"
        print(f"\n{icon} Job: {job_name}")
        print(f"   Status: {job_status}")
        print(f"   Conclusion: {job_conclusion}")
        print(f"   Started: {job.get('started_at', 'N/A')}")
        print(f"   Completed: {job.get('completed_at', 'N/A')}")
        
        print("\n   Steps:")
        for step in job.get('steps', []):
            step_name = step.get('name', 'N/A')
            step_conclusion = step.get('conclusion', step.get('status', 'N/A'))
            step_number = step.get('number', '?')
            
            if step_conclusion == 'failure':
                print(f"   {step_number}. ❌ FAILED: {step_name}")
                failed_steps.append({
                    'job': job_name,
                    'step': step_name,
                    'number': step_number
                })
            elif step_conclusion == 'success':
                print(f"   {step_number}. ✅ {step_name}")
            elif step_conclusion == 'skipped':
                print(f"   {step_number}. ⏭️ SKIPPED: {step_name}")
            else:
                print(f"   {step_number}. ⏺ {step_name}: {step_conclusion}")
    
    if failed_steps:
        print("\n" + "=" * 60)
        print("FAILED STEPS SUMMARY")
        print("=" * 60)
        for fs in failed_steps:
            print(f"❌ [{fs['job']}] Step {fs['number']}: {fs['step']}")
    
    # Get artifacts
    artifacts_url = f'{run_url}/artifacts'
    artifacts_response = requests.get(artifacts_url, headers=headers)
    artifacts_data = artifacts_response.json()
    
    if artifacts_data.get('artifacts'):
        print("\n" + "=" * 60)
        print("ARTIFACTS")
        print("=" * 60)
        for artifact in artifacts_data.get('artifacts', []):
            print(f"📦 {artifact.get('name', 'N/A')} ({artifact.get('size_in_bytes', 0) / 1024:.1f} KB)")
    
    return {
        'run_data': run_data,
        'jobs_data': jobs_data,
        'failed_steps': failed_steps
    }

if __name__ == "__main__":
    run_id = 20025367790
    if len(sys.argv) > 1:
        run_id = int(sys.argv[1])
    
    analyze_run(run_id)
