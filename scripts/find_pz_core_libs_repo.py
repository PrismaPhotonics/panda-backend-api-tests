#!/usr/bin/env python3
"""
Script to find pz_core_libs repository and check for validation changes.

This script:
1. Tries to find pz_core_libs repository location
2. Checks git history for validation changes
3. Searches for the validation code
"""

import sys
import subprocess
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


def find_pz_core_libs_repo() -> Optional[Path]:
    """Try to find pz_core_libs repository."""
    logger.info("Searching for pz_core_libs repository...")
    
    # Common locations
    search_paths = [
        Path("C:/Projects"),
        Path("C:/Projects/pz"),
        Path("C:/Projects/focus_server_automation/pz"),
        Path.home() / "Projects",
        Path.home() / "workspace",
    ]
    
    for base_path in search_paths:
        if not base_path.exists():
            continue
        
        # Look for pz-core-libs directory
        for path in base_path.rglob("pz-core-libs"):
            if (path / ".git").exists():
                logger.info(f"Found pz-core-libs repository at: {path}")
                return path
        
        # Look for pz_core_libs directory
        for path in base_path.rglob("pz_core_libs"):
            if (path / ".git").exists():
                logger.info(f"Found pz_core_libs repository at: {path}")
                return path
    
    logger.warning("pz_core_libs repository not found in common locations")
    return None


def check_git_history(repo_path: Path) -> Dict[str, Any]:
    """Check git history for validation changes."""
    logger.info("=" * 80)
    logger.info("Checking git history for validation changes")
    logger.info("=" * 80)
    
    findings = {
        "commits_found": [],
        "validation_commits": [],
        "prr_commits": []
    }
    
    try:
        os.chdir(repo_path)
        
        # Search for commits related to validation
        search_terms = [
            ("validation", "validation_commits"),
            ("prr", "prr_commits"),
            ("metadata", "commits_found"),
            ("Cannot proceed", "commits_found"),
            ("Missing required", "commits_found")
        ]
        
        for term, key in search_terms:
            try:
                result = subprocess.run(
                    ["git", "log", "--all", "--since=3 weeks ago", "--oneline", "--grep", term, "-i"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0 and result.stdout:
                    commits = result.stdout.strip().split('\n')
                    if commits and commits[0]:  # Check if not empty
                        findings[key].extend(commits)
                        logger.info(f"Found {len(commits)} commits related to '{term}'")
            except Exception as e:
                logger.warning(f"Error searching for '{term}': {e}")
        
        # Search for changes in recording_metadata files
        try:
            result = subprocess.run(
                ["git", "log", "--all", "--since=3 weeks ago", "--oneline", "--", "*recording_metadata*"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout:
                commits = result.stdout.strip().split('\n')
                if commits and commits[0]:
                    findings["commits_found"].extend(commits)
                    logger.info(f"Found {len(commits)} commits in recording_metadata files")
        except Exception as e:
            logger.warning(f"Error searching recording_metadata changes: {e}")
        
        # Remove duplicates
        for key in findings:
            findings[key] = list(set(findings[key]))
    
    except Exception as e:
        logger.error(f"Error checking git history: {e}")
    
    return findings


def search_validation_code(repo_path: Path) -> Dict[str, Any]:
    """Search for validation code in the repository."""
    logger.info("=" * 80)
    logger.info("Searching for validation code")
    logger.info("=" * 80)
    
    findings = {
        "files_found": [],
        "validation_code": []
    }
    
    # Search patterns
    patterns = [
        "Cannot proceed.*Missing required.*prr",
        "Missing required fiber metadata fields",
        "prr.*>.*0|prr.*<=.*0",
        "@.*validator.*prr|model_validator.*prr",
        "def.*validate.*prr"
    ]
    
    try:
        for py_file in repo_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    for i, line in enumerate(lines):
                        # Check for validation patterns
                        for pattern in patterns:
                            if pattern.lower().replace('.*', '') in line.lower():
                                findings["files_found"].append(str(py_file))
                                
                                # Get context
                                start = max(0, i - 5)
                                end = min(len(lines), i + 6)
                                context = '\n'.join(lines[start:end])
                                
                                findings["validation_code"].append({
                                    "file": str(py_file),
                                    "line": i + 1,
                                    "code": line.strip(),
                                    "context": context
                                })
                                
                                logger.info(f"Found validation code in {py_file} at line {i+1}")
                                break
            except Exception as e:
                continue
    
    except Exception as e:
        logger.error(f"Error searching validation code: {e}")
    
    return findings


def main():
    """Main investigation function."""
    logger.info("=" * 80)
    logger.info("Finding and checking pz_core_libs repository")
    logger.info("=" * 80)
    
    # Find repository
    repo_path = find_pz_core_libs_repo()
    
    if not repo_path:
        logger.error("Could not find pz_core_libs repository")
        logger.info("\nTrying alternative approach:")
        logger.info("1. Check if pz_core_libs is installed via pip:")
        logger.info("   pip show pz_core_libs")
        logger.info("2. Check git repository URL:")
        logger.info("   git+ssh://git@github.com/PrismaPhotonics/pz-core-libs.git")
        logger.info("3. Clone the repository manually:")
        logger.info("   git clone git@github.com:PrismaPhotonics/pz-core-libs.git")
        return
    
    # Check git history
    git_findings = check_git_history(repo_path)
    
    logger.info("\n" + "=" * 80)
    logger.info("Git History Summary:")
    logger.info("=" * 80)
    logger.info(f"Validation commits: {len(git_findings['validation_commits'])}")
    logger.info(f"PRR commits: {len(git_findings['prr_commits'])}")
    logger.info(f"Total commits: {len(git_findings['commits_found'])}")
    
    if git_findings['validation_commits']:
        logger.info("\nValidation commits:")
        for commit in git_findings['validation_commits'][:10]:
            logger.info(f"  {commit}")
    
    if git_findings['prr_commits']:
        logger.info("\nPRR commits:")
        for commit in git_findings['prr_commits'][:10]:
            logger.info(f"  {commit}")
    
    # Search for validation code
    code_findings = search_validation_code(repo_path)
    
    logger.info("\n" + "=" * 80)
    logger.info("Validation Code Summary:")
    logger.info("=" * 80)
    logger.info(f"Files found: {len(set(code_findings['files_found']))}")
    logger.info(f"Code blocks found: {len(code_findings['validation_code'])}")
    
    if code_findings['validation_code']:
        logger.info("\nValidation code found:")
        for code_block in code_findings['validation_code'][:5]:  # First 5
            logger.info(f"\nFile: {code_block['file']}")
            logger.info(f"Line: {code_block['line']}")
            logger.info(f"Code: {code_block['code']}")
            logger.info(f"Context:\n{code_block['context']}")
    
    # Save results
    output_file = Path(__file__).parent.parent / "docs" / "04_testing" / "analysis" / f"PZ_CORE_LIBS_REPO_CHECK_{Path(__file__).stem}.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# pz_core_libs Repository Check\n\n")
        f.write(f"**Repository Path:** {repo_path}\n\n")
        f.write("## Git History\n\n")
        f.write(f"- Validation commits: {len(git_findings['validation_commits'])}\n")
        f.write(f"- PRR commits: {len(git_findings['prr_commits'])}\n")
        f.write(f"- Total commits: {len(git_findings['commits_found'])}\n\n")
        
        if git_findings['validation_commits']:
            f.write("### Validation Commits\n\n")
            for commit in git_findings['validation_commits']:
                f.write(f"- {commit}\n")
            f.write("\n")
        
        if code_findings['validation_code']:
            f.write("## Validation Code Found\n\n")
            for code_block in code_findings['validation_code']:
                f.write(f"### {code_block['file']} (Line {code_block['line']})\n\n")
                f.write(f"```python\n{code_block['context']}\n```\n\n")
    
    logger.info(f"\nResults saved to: {output_file}")
    logger.info("Investigation complete!")


if __name__ == "__main__":
    main()

