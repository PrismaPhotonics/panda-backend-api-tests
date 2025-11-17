#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to remove Hebrew-named files from Git repository
"""
import subprocess
import sys
import os

def run_git_command(cmd):
    """Run git command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return result.stdout.strip(), result.returncode
    except Exception as e:
        print(f"Error running command: {e}")
        return None, 1

def main():
    # Hebrew file names to remove
    hebrew_files = [
        "דוח_השוואה_JIRA_מול_אוטומציה.md",
        "הסבר_קטגוריות_טסטים_חסרים.md",
        "רשימת_ספסיפיקציות_נדרשות_לפגישה.md"
    ]
    
    print("Removing Hebrew-named files from Git...")
    
    for file in hebrew_files:
        print(f"\nAttempting to remove: {file}")
        
        # Check if file exists in git
        cmd = f'git ls-files --error-unmatch "{file}"'
        output, code = run_git_command(cmd)
        
        if code == 0:
            # File exists, remove it
            cmd = f'git rm --cached "{file}"'
            output, code = run_git_command(cmd)
            
            if code == 0:
                print(f"✓ Successfully removed: {file}")
            else:
                print(f"✗ Failed to remove: {file}")
                print(f"  Error: {output}")
        else:
            print(f"  File not found in git index: {file}")
    
    # Show status
    print("\n" + "="*60)
    print("Current git status:")
    output, _ = run_git_command("git status --short")
    if output:
        print(output)
    else:
        print("No changes to commit")

if __name__ == "__main__":
    main()

