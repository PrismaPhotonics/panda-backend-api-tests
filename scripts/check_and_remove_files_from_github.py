"""
Check and remove files from GitHub repository
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
    """Check and remove files."""
    repo_path = Path(r"C:\Projects\focus_server_automation")
    
    # Get all files in HEAD
    print("Checking files in HEAD...")
    success, stdout, stderr = run_cmd(
        "git ls-tree -r --name-only HEAD",
        cwd=repo_path
    )
    
    if not success:
        print(f"Error: {stderr}")
        return
    
    all_files = [line.strip() for line in stdout.split('\n') if line.strip()]
    
    # Files to remove - patterns to match
    patterns_to_remove = [
        "COMPLETE_HIGH_PRIORITY",
        "COMPLETE_XRAY",
        "CRITICAL_MISSING",
        "CRITICAL_TESTS",
        "EXPLANATION_14",
        "FINAL_XRAY",
        "GITHUB_UPDATE",
        "MISSING_IN_AUTOMATION",
        "MONGODB_CLARIFICATION",
        "MONGODB_COLLECTIONS",
        "MONGODB_ISSUE",
        "MONGODB_NODE2",
        "PROJECT_CLEANUP",
        "PZ_UPDATE",
        "SPECS_REQUIREMENTS",
        "TESTS_IN_CODE_MISSING",
        "TESTS_TO_ADD_TO_CODE",
        "TESTS_TO_ADD_TO_JIRA",
        "URGENT_JIRA",
        "XRAY_9_MISSING",
        "XRAY_ALL_MISSING",
        "XRAY_COMPLETE",
        "XRAY_HIGH_PRIORITY",
        "XRAY_INTEGRATION",
        "XRAY_MISSING",
        "XRAY_TESTS_ANALYSIS",
        "XRAY_TESTS_MAPPING",
        "XRAY_TESTS_TO_FIX",
        "XRAY_VS_CODE",
        "specs_checklist",
        "Install-PandaApp-Automated",
        "SETUP_K9S",
        "check_connections",
        "connect_k9s",
        "find_swagger",
        "fix_server_config",
        "run_all_tests",
        "set_production_env",
        "setup_panda_config",
        "setup_pz",
        "דוח_השוואה",
        "הסבר_קטגוריות",
        "רשימת_ספסיפיקציות"
    ]
    
    files_to_remove = []
    for file in all_files:
        # Only check root level files
        if '/' not in file or file.count('/') == 1:
            filename = Path(file).name
            for pattern in patterns_to_remove:
                if pattern in filename:
                    files_to_remove.append(file)
                    break
    
    if not files_to_remove:
        print("No files found to remove!")
        return
    
    print(f"\nFound {len(files_to_remove)} files to remove:")
    for file in files_to_remove:
        print(f"  - {file}")
    
    # Remove files
    print("\nRemoving files...")
    for file in files_to_remove:
        success, stdout, stderr = run_cmd(
            f'git rm "{file}"',
            cwd=repo_path
        )
        if success:
            print(f"  ✓ Removed: {file}")
        else:
            print(f"  ✗ Error removing {file}: {stderr}")
    
    # Commit
    if files_to_remove:
        print("\nCommitting changes...")
        success, stdout, stderr = run_cmd(
            'git commit -m "chore: remove all general documentation and script files from root"',
            cwd=repo_path
        )
        if success:
            print("  ✓ Commit successful!")
        else:
            if "nothing to commit" in stderr.lower():
                print("  No changes to commit")
            else:
                print(f"  ✗ Error: {stderr}")
                return
        
        # Push
        print("\nPushing to GitHub...")
        success, stdout, stderr = run_cmd(
            "git branch --show-current",
            cwd=repo_path
        )
        if success:
            current_branch = stdout.strip()
            success, stdout, stderr = run_cmd(
                f"git push origin {current_branch}",
                cwd=repo_path
            )
            if success:
                print("  ✓ Push successful!")
                print(f"\nAll files removed from GitHub repository!")
            else:
                print(f"  ✗ Error: {stderr}")

if __name__ == "__main__":
    main()

