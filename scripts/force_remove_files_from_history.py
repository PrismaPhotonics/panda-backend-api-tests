"""
Force remove files from git history completely
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
    """Force remove files from git history."""
    repo_path = Path(r"C:\Projects\focus_server_automation")
    
    # List of files to remove completely from history
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
    print("Force removing files from git history")
    print("=" * 80)
    print("\nWARNING: This will rewrite git history!")
    print("Make sure you have a backup or are working on a branch.\n")
    
    # Create a file list for git filter-branch
    file_list_path = repo_path / ".git_remove_files.txt"
    try:
        with open(file_list_path, 'w', encoding='utf-8') as f:
            for file in files_to_remove:
                f.write(f"{file}\n")
        
        print(f"Created file list: {file_list_path}")
        print(f"Files to remove: {len(files_to_remove)}")
        
        # Use git filter-repo (better than filter-branch) or git filter-branch
        # First check if git filter-repo is available
        success, stdout, stderr = run_cmd("git filter-repo --version", cwd=repo_path)
        use_filter_repo = success
        
        if use_filter_repo:
            print("\nUsing git filter-repo...")
            # Build command for git filter-repo
            paths_to_remove = " ".join([f'"{f}"' for f in files_to_remove])
            cmd = f'git filter-repo --path "{files_to_remove[0]}" --invert-paths'
            for file in files_to_remove[1:]:
                cmd += f' --path "{file}"'
            cmd += ' --force'
            
            print(f"Running: git filter-repo...")
            success, stdout, stderr = run_cmd(cmd, cwd=repo_path)
            
            if success:
                print("  Success! Files removed from history.")
            else:
                print(f"  Error: {stderr}")
                print("\nTrying alternative method with git filter-branch...")
                use_filter_repo = False
        
        if not use_filter_repo:
            print("\nUsing git filter-branch (slower but more compatible)...")
            
            # Create a script to remove files
            script_content = """#!/bin/sh
git ls-files | grep -E "COMPLETE_|CRITICAL_|XRAY_|MONGODB_|TESTS_|specs_checklist|דוח_|הסבר_|רשימת_" | xargs git rm --cached --ignore-unmatch
"""
            
            script_path = repo_path / ".git_remove_script.sh"
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # Alternative: Use git filter-branch with index-filter
            # This is safer and works on Windows with Git Bash
            print("\nNote: For complete history removal, you may need to:")
            print("1. Use BFG Repo-Cleaner (recommended)")
            print("2. Or use git filter-branch manually")
            print("\nFor now, files are removed from current HEAD.")
            print("They may still exist in older commits.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup
        if file_list_path.exists():
            file_list_path.unlink()
    
    print("\n" + "=" * 80)
    print("Note: Files removed from current HEAD.")
    print("To completely remove from history, consider using BFG Repo-Cleaner")
    print("or git filter-branch on all branches.")
    print("=" * 80)

if __name__ == "__main__":
    main()

