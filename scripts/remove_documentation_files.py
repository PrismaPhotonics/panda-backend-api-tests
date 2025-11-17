"""
Remove general documentation files from repository
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
    """Remove documentation files."""
    repo_path = Path(r"C:\Projects\focus_server_automation")
    
    # List of files to remove
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
    print("Removing general documentation files")
    print("=" * 80)
    
    removed_count = 0
    not_found_count = 0
    
    for file in files_to_remove:
        file_path = repo_path / file
        if file_path.exists():
            # Check if file is tracked by git
            success, stdout, stderr = run_cmd(
                f'git ls-files --error-unmatch "{file}"', 
                cwd=repo_path
            )
            
            if success:
                # File is tracked, remove it
                success, stdout, stderr = run_cmd(
                    f'git rm "{file}"', 
                    cwd=repo_path
                )
                if success:
                    print(f"  Removed: {file}")
                    removed_count += 1
                else:
                    print(f"  Error removing {file}: {stderr}")
            else:
                # File not tracked, just delete it locally
                try:
                    file_path.unlink()
                    print(f"  Deleted (untracked): {file}")
                    removed_count += 1
                except Exception as e:
                    print(f"  Error deleting {file}: {e}")
        else:
            # Check if it's tracked in git (might be deleted but not committed)
            success, stdout, stderr = run_cmd(
                f'git ls-files --error-unmatch "{file}"', 
                cwd=repo_path
            )
            
            if success:
                # File is tracked but doesn't exist locally, remove from git
                success, stdout, stderr = run_cmd(
                    f'git rm "{file}"', 
                    cwd=repo_path
                )
                if success:
                    print(f"  Removed from git: {file}")
                    removed_count += 1
                else:
                    print(f"  Error removing {file} from git: {stderr}")
            else:
                not_found_count += 1
    
    print(f"\nRemoved: {removed_count} files")
    print(f"Not found: {not_found_count} files")
    
    # Commit changes
    if removed_count > 0:
        print("\nCommitting changes...")
        success, stdout, stderr = run_cmd(
            'git commit -m "chore: remove general documentation files from root"',
            cwd=repo_path
        )
        if success:
            print("  Commit successful!")
        else:
            if "nothing to commit" in stderr.lower():
                print("  No changes to commit")
            else:
                print(f"  Error: {stderr}")
        
        # Push to GitHub
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
                print("  Push successful!")
            else:
                print(f"  Error: {stderr}")
    
    print("\n" + "=" * 80)
    print("Complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()

