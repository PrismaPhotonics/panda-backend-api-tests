"""
Deploy Code Only to GitHub
==========================

Deploy only code changes and automation-related documentation, excluding general documents.
"""

import subprocess
import sys
from pathlib import Path

def run_cmd(cmd, cwd=None):
    """Run command and return output."""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, capture_output=True, text=True, encoding='utf-8'
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    """Main deployment function."""
    repo_path = Path(r"C:\Projects\focus_server_automation")
    
    print("=" * 80)
    print("Deploying Code and Automation Documentation Only")
    print("=" * 80)
    print()
    
    # Step 1: Unstage everything
    print("Step 1: Unstaging all changes...")
    success, stdout, stderr = run_cmd("git reset", cwd=repo_path)
    if not success:
        print(f"Error: {stderr}")
        return
    
    # Step 2: Add only code files and automation-related documentation
    print("\nStep 2: Adding code files and automation documentation...")
    
    # Source code directories
    code_dirs = [
        "src/",
        "tests/",
        "scripts/",
        "external/",
        "config/"
    ]
    
    for dir_path in code_dirs:
        full_path = repo_path / dir_path
        if full_path.exists():
            success, stdout, stderr = run_cmd(f'git add "{dir_path}"', cwd=repo_path)
            if success:
                print(f"  Added directory: {dir_path}")
            else:
                print(f"  Warning: Could not add {dir_path}: {stderr}")
    
    # Configuration files
    config_files = [
        "pytest.ini",
        "requirements.txt",
        "README.md",
        ".github/workflows/"
    ]
    
    for path in config_files:
        full_path = repo_path / path
        if full_path.exists():
            success, stdout, stderr = run_cmd(f'git add "{path}"', cwd=repo_path)
            if success:
                print(f"  Added: {path}")
            else:
                print(f"  Warning: Could not add {path}: {stderr}")
    
    # Step 4: Check what will be committed
    print("\nStep 4: Checking staged files...")
    success, stdout, stderr = run_cmd("git status --short", cwd=repo_path)
    if success:
        staged = [line for line in stdout.split('\n') if line.startswith('A ') or line.startswith('M ')]
        print(f"\nFiles to be committed: {len(staged)}")
        for line in staged[:20]:  # Show first 20
            print(f"  {line}")
        if len(staged) > 20:
            print(f"  ... and {len(staged) - 20} more")
    
    # Step 5: Commit
    print("\nStep 5: Committing changes...")
    commit_message = "chore: update automation code and tests - exclude general documentation"
    success, stdout, stderr = run_cmd(f'git commit -m "{commit_message}"', cwd=repo_path)
    if success:
        print("  Commit successful!")
    else:
        if "nothing to commit" in stderr.lower():
            print("  No changes to commit (all changes are already committed or excluded)")
        else:
            print(f"  Error: {stderr}")
            return
    
    # Step 5: Get current branch
    print("\nStep 5: Getting current branch...")
    success, stdout, stderr = run_cmd("git branch --show-current", cwd=repo_path)
    if success:
        current_branch = stdout.strip()
        print(f"  Current branch: {current_branch}")
    else:
        current_branch = "main"
        print(f"  Could not determine branch, using: {current_branch}")
    
    # Step 6: Push to GitHub
    print("\nStep 6: Pushing to GitHub...")
    success, stdout, stderr = run_cmd(f"git push origin {current_branch}", cwd=repo_path)
    if success:
        print("  Push successful!")
        print(f"\n{'=' * 80}")
        print("Deployment complete!")
        print(f"{'=' * 80}")
    else:
        print(f"  Error: {stderr}")
        print("\nTrying to push to main/master...")
        for branch in ["main", "master"]:
            success, stdout, stderr = run_cmd(f"git push origin {branch}", cwd=repo_path)
            if success:
                print(f"  Push to {branch} successful!")
                return
        print("  Could not push. Please check your branch and remote configuration.")

if __name__ == "__main__":
    main()

