"""
Remove files from specific commit in history
This will rewrite history to remove files from the commit 80e0f6f
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
    """Remove files from specific commit."""
    repo_path = Path(r"C:\Projects\focus_server_automation")
    
    # Files to remove
    files_to_remove = [
        "COMPLETE_HIGH_PRIORITY_TEST_DOCUMENTATION.md",
        "COMPLETE_XRAY_TEST_DOCUMENTATION_PART1_ROI.md",
        "COMPLETE_XRAY_TEST_DOCUMENTATION_PART2_ROI_CONTINUED.md",
        "COMPLETE_XRAY_TEST_DOCUMENTATION_PART3_INFRASTRUCTURE.md",
        "COMPLETE_XRAY_TEST_DOCUMENTATION_PART4_INFRA_SSH_PZ.md",
        "COMPLETE_XRAY_TEST_DOCUMENTATION_PART5_SINGLECHANNEL.md",
        "COMPLETE_XRAY_TEST_DOCUMENTATION_PART6_SINGLECHANNEL_EXTENDED.md",
        "COMPLETE_XRAY_TEST_DOCUMENTATION_PART7_HISTORIC_PLAYBACK.md",
        "COMPLETE_XRAY_TEST_DOCUMENTATION_PART8_CONFIG_VALIDATION.md",
        "CRITICAL_MISSING_SPECS_LIST.md",
        "CRITICAL_TESTS_FOR_XRAY_NO_WATERFALL.md",
        "EXPLANATION_14_CRITICAL_TESTS_MISSING_IN_XRAY.md",
        "FINAL_XRAY_HIGH_PRIORITY_ANALYSIS.md",
        "GITHUB_UPDATE_COMPLETE.md",
        "MISSING_IN_AUTOMATION_CODE.md",
        "MONGODB_CLARIFICATION_WORK_SUMMARY.md",
        "MONGODB_COLLECTIONS_CLARIFICATION.md",
        "MONGODB_ISSUE_INDEX.md",
        "MONGODB_NODE2_NODE4_ISSUE_SUMMARY.md",
        "PROJECT_CLEANUP_AND_REORGANIZATION_PLAN.md",
        "PZ_UPDATE_STATUS.md",
        "SPECS_REQUIREMENTS_FOR_MEETING.md",
        "TESTS_IN_CODE_MISSING_IN_XRAY.md",
        "TESTS_IN_CODE_MISSING_IN_XRAY_NO_WATERFALL.md",
        "TESTS_TO_ADD_TO_CODE.csv",
        "TESTS_TO_ADD_TO_JIRA.csv",
        "URGENT_JIRA_UPDATES_NEEDED.md",
        "XRAY_9_MISSING_CRITICAL_TESTS_FULL_DOCUMENTATION.md",
        "XRAY_ALL_MISSING_TEST_CASES.md",
        "XRAY_COMPLETE_TEST_DOCUMENTATION_SUMMARY.md",
        "XRAY_HIGH_PRIORITY_MISSING_TESTS.md",
        "XRAY_HIGH_PRIORITY_TESTS_DOCUMENTATION.md",
        "XRAY_INTEGRATION_IMPLEMENTATION.md",
        "XRAY_MISSING_TESTS_DOCUMENTATION.md",
        "XRAY_TESTS_ANALYSIS.md",
        "XRAY_TESTS_MAPPING_CORRECTED.md",
        "XRAY_TESTS_TO_FIX_AND_ADD.md",
        "XRAY_VS_CODE_MISSING_TESTS.md",
        "specs_checklist_for_meeting.csv",
        "דוח_השוואה_JIRA_מול_אוטומציה.md",
        "הסבר_קטגוריות_טסטים_חסרים.md",
        "רשימת_ספסיפיקציות_נדרשות_לפגישה.md"
    ]
    
    print("=" * 80)
    print("Removing files from git history completely")
    print("=" * 80)
    print("\nWARNING: This will rewrite git history!")
    print("This operation cannot be easily undone.\n")
    
    # Get current branch
    success, stdout, stderr = run_cmd("git branch --show-current", cwd=repo_path)
    if success:
        current_branch = stdout.strip()
        print(f"Current branch: {current_branch}")
    else:
        print("Error: Could not determine current branch")
        return
    
    # Check if files exist in current HEAD
    print("\nChecking files in current HEAD...")
    files_in_head = []
    for file in files_to_remove:
        success, stdout, stderr = run_cmd(
            f'git ls-files --error-unmatch "{file}"',
            cwd=repo_path
        )
        if success:
            files_in_head.append(file)
            print(f"  Found in HEAD: {file}")
    
    if files_in_head:
        print(f"\n{len(files_in_head)} files still exist in HEAD. Removing...")
        for file in files_in_head:
            success, stdout, stderr = run_cmd(
                f'git rm --cached "{file}"',
                cwd=repo_path
            )
            if success:
                print(f"  Removed from index: {file}")
    
    # Use git filter-branch to remove from all history
    print("\nRemoving files from all git history...")
    print("This may take a while...\n")
    
    # Create filter command
    # We'll use git filter-branch with index-filter
    filter_script = "git rm --cached --ignore-unmatch " + " ".join([f'"{f}"' for f in files_to_remove])
    
    # Use git filter-branch
    # Note: This requires git filter-branch to be available
    cmd = f'git filter-branch --force --index-filter "{filter_script}" --prune-empty --tag-name-filter cat -- --all'
    
    print(f"Running: git filter-branch...")
    print("(This may take several minutes)\n")
    
    success, stdout, stderr = run_cmd(cmd, cwd=repo_path)
    
    if success:
        print("\n✅ Success! Files removed from history.")
        print("\nNext steps:")
        print("1. Force push to update remote: git push origin --force --all")
        print("2. Clean up backup refs: git for-each-ref --format='delete %(refname)' refs/original | git update-ref --stdin")
    else:
        print(f"\n❌ Error: {stderr}")
        print("\nAlternative: Use BFG Repo-Cleaner for better performance")
        print("Download from: https://rtyley.github.io/bfg-repo-cleaner/")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()

