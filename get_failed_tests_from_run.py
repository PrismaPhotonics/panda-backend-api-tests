#!/usr/bin/env python3
"""
Get Failed Tests from GitHub Actions Run
========================================

Downloads artifacts and extracts failed test names from JUnit XML.
"""

import sys
import requests
import os
import zipfile
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict

GITHUB_API_BASE = "https://api.github.com"


def get_github_token() -> str:
    """Get GitHub token from environment."""
    return os.getenv("GITHUB_TOKEN", "")


def get_repo_info() -> tuple[str, str]:
    """Get repository owner and name."""
    import subprocess
    try:
        remote_url = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        if "github.com" in remote_url:
            if remote_url.startswith("https://"):
                parts = remote_url.replace("https://github.com/", "").replace(".git", "").split("/")
            elif remote_url.startswith("git@"):
                parts = remote_url.replace("git@github.com:", "").replace(".git", "").split("/")
            else:
                parts = remote_url.split("/")
            
            if len(parts) >= 2:
                return parts[0], parts[1]
    except:
        pass
    
    return "PrismaPhotonics", "panda-backend-api-tests"


def download_artifacts(run_id: str) -> List[str]:
    """Download artifacts from GitHub Actions run."""
    token = get_github_token()
    owner, repo = get_repo_info()
    
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    
    # Get artifacts
    artifacts_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts"
    artifacts_response = requests.get(artifacts_url, headers=headers)
    
    if artifacts_response.status_code != 200:
        print(f"Failed to get artifacts: {artifacts_response.status_code}")
        return []
    
    artifacts = artifacts_response.json().get("artifacts", [])
    
    if not artifacts:
        print("No artifacts found")
        print("Note: Artifacts may not be available via API without authentication")
        print("Try downloading manually from GitHub Actions UI")
        return []
    
    # Download regression test reports
    xml_files = []
    for artifact in artifacts:
        if "regression" in artifact.get("name", "").lower():
            artifact_id = artifact.get("id")
            download_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip"
            
            # Download zip
            download_response = requests.get(download_url, headers=headers, stream=True)
            if download_response.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_file:
                    for chunk in download_response.iter_content(chunk_size=8192):
                        tmp_file.write(chunk)
                    tmp_file_path = tmp_file.name
                
                # Extract XML files
                with zipfile.ZipFile(tmp_file_path, 'r') as zip_ref:
                    extract_dir = tempfile.mkdtemp()
                    zip_ref.extractall(extract_dir)
                    
                    # Find XML files
                    for root, dirs, files in os.walk(extract_dir):
                        for file in files:
                            if file.endswith('.xml'):
                                xml_files.append(os.path.join(root, file))
                
                os.unlink(tmp_file_path)
    
    return xml_files


def parse_failed_tests(xml_file: str) -> List[Dict[str, str]]:
    """Parse JUnit XML and extract failed tests."""
    failed_tests = []
    
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Handle both testsuites and testsuite root elements
        suites = root.findall('.//testsuite') if root.tag != 'testsuite' else [root]
        if not suites:
            suites = [root]
        
        for suite in suites:
            for testcase in suite.findall('.//testcase'):
                # Check for failures
                failure = testcase.find('failure')
                error = testcase.find('error')
                
                if failure is not None or error is not None:
                    test_name = testcase.get('name', 'Unknown')
                    classname = testcase.get('classname', 'Unknown')
                    failure_msg = failure.get('message', '') if failure is not None else ''
                    error_msg = error.get('message', '') if error is not None else ''
                    
                    failed_tests.append({
                        'name': test_name,
                        'classname': classname,
                        'failure_message': failure_msg or error_msg,
                        'type': 'failure' if failure is not None else 'error'
                    })
    
    except Exception as e:
        print(f"Error parsing {xml_file}: {e}")
    
    return failed_tests


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python get_failed_tests_from_run.py <run_id>")
        print("\nExample:")
        print("  python get_failed_tests_from_run.py 19866607156")
        sys.exit(1)
    
    run_id = sys.argv[1]
    
    print(f"Downloading artifacts from run {run_id}...")
    xml_files = download_artifacts(run_id)
    
    if not xml_files:
        print("No XML files found in artifacts")
        print("\nTrying to get failure info from API...")
        # Fallback: try to get info from API
        return
    
    print(f"Found {len(xml_files)} XML file(s)")
    print()
    
    all_failed_tests = []
    for xml_file in xml_files:
        print(f"Parsing {xml_file}...")
        failed_tests = parse_failed_tests(xml_file)
        all_failed_tests.extend(failed_tests)
    
    if all_failed_tests:
        print("="*80)
        print(f"FAILED TESTS: {len(all_failed_tests)}")
        print("="*80)
        print()
        
        # Group by classname
        by_class = {}
        for test in all_failed_tests:
            classname = test['classname']
            if classname not in by_class:
                by_class[classname] = []
            by_class[classname].append(test)
        
        for classname, tests in sorted(by_class.items()):
            print(f"Class: {classname}")
            for test in tests:
                print(f"  - {test['name']} ({test['type']})")
                if test['failure_message']:
                    msg = test['failure_message'][:100] + "..." if len(test['failure_message']) > 100 else test['failure_message']
                    print(f"    Message: {msg}")
            print()
        
        print("="*80)
        print(f"Total: {len(all_failed_tests)} failed test(s)")
        print("="*80)
    else:
        print("No failed tests found in XML files")


if __name__ == "__main__":
    main()

