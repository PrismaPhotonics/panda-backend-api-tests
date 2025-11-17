#!/usr/bin/env python3
"""
Script to check pz_core_libs for RecordingMetadata validation that checks prr > 0.

This script tries to:
1. Import pz_core_libs and find RecordingMetadata class
2. Check for validators that validate prr > 0
3. Find the source code location
4. Check git history if possible
"""

import sys
import os
import inspect
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


def find_recording_metadata_source() -> Optional[str]:
    """Find the source file of RecordingMetadata class."""
    try:
        from pz_core_libs.recording_metadata import RecordingMetadata
        
        # Get the source file
        source_file = inspect.getfile(RecordingMetadata)
        logger.info(f"Found RecordingMetadata source: {source_file}")
        return source_file
    except ImportError as e:
        logger.error(f"Failed to import RecordingMetadata: {e}")
        return None
    except Exception as e:
        logger.error(f"Error finding source: {e}")
        return None


def check_validation_code(source_file: Optional[str]) -> Dict[str, Any]:
    """Check the source file for validation code."""
    findings = {
        "validators_found": [],
        "prr_validation_found": False,
        "validation_code": []
    }
    
    if not source_file or not os.path.exists(source_file):
        logger.warning(f"Source file not found: {source_file}")
        return findings
    
    try:
        with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        # Search for validation patterns
        for i, line in enumerate(lines):
            # Look for validators
            if 'validator' in line.lower() or 'model_validator' in line.lower():
                findings["validators_found"].append({
                    "line": i + 1,
                    "code": line.strip()
                })
            
            # Look for prr validation
            if 'prr' in line.lower() and ('>' in line or 'if' in line.lower() or 'raise' in line.lower()):
                findings["prr_validation_found"] = True
                # Get context (5 lines before and after)
                start = max(0, i - 5)
                end = min(len(lines), i + 6)
                context = ''.join(lines[start:end])
                findings["validation_code"].append({
                    "line": i + 1,
                    "code": line.strip(),
                    "context": context
                })
                logger.info(f"Found prr validation at line {i + 1}: {line.strip()}")
            
            # Look for "Cannot proceed" or "Missing required"
            if 'cannot proceed' in line.lower() or 'missing required' in line.lower():
                start = max(0, i - 5)
                end = min(len(lines), i + 6)
                context = ''.join(lines[start:end])
                findings["validation_code"].append({
                    "line": i + 1,
                    "code": line.strip(),
                    "context": context,
                    "type": "error_message"
                })
                logger.info(f"Found error message at line {i + 1}: {line.strip()}")
    
    except Exception as e:
        logger.error(f"Error reading source file: {e}")
    
    return findings


def check_git_history(source_file: Optional[str]) -> Dict[str, Any]:
    """Check git history of the source file."""
    findings = {
        "git_available": False,
        "commits_found": [],
        "recent_changes": []
    }
    
    if not source_file:
        return findings
    
    # Find git root
    current_dir = Path(source_file).parent
    git_root = None
    
    for parent in [current_dir] + list(current_dir.parents):
        if (parent / '.git').exists():
            git_root = parent
            break
    
    if not git_root:
        logger.warning("Git repository not found")
        return findings
    
    findings["git_available"] = True
    logger.info(f"Found git root: {git_root}")
    
    # Get relative path from git root
    rel_path = Path(source_file).relative_to(git_root)
    
    try:
        import subprocess
        
        # Check recent commits for this file
        result = subprocess.run(
            ["git", "log", "--all", "--since=2 weeks ago", "--oneline", "--", str(rel_path)],
            cwd=git_root,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout:
            commits = result.stdout.strip().split('\n')
            findings["commits_found"] = commits
            logger.info(f"Found {len(commits)} recent commits for {rel_path}")
        
        # Check for commits related to validation or prr
        result = subprocess.run(
            ["git", "log", "--all", "--since=2 weeks ago", "--oneline", "--grep", "validation", "-i", "--", str(rel_path)],
            cwd=git_root,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout:
            commits = result.stdout.strip().split('\n')
            findings["recent_changes"].extend(commits)
            logger.info(f"Found {len(commits)} commits related to validation")
        
        # Check for commits related to prr
        result = subprocess.run(
            ["git", "log", "--all", "--since=2 weeks ago", "--oneline", "--grep", "prr", "-i", "--", str(rel_path)],
            cwd=git_root,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout:
            commits = result.stdout.strip().split('\n')
            findings["recent_changes"].extend(commits)
            logger.info(f"Found {len(commits)} commits related to prr")
        
    except Exception as e:
        logger.error(f"Error checking git history: {e}")
    
    return findings


def main():
    """Main investigation function."""
    logger.info("=" * 80)
    logger.info("Checking pz_core_libs for RecordingMetadata validation")
    logger.info("=" * 80)
    
    # Find source file
    source_file = find_recording_metadata_source()
    
    if not source_file:
        logger.error("Could not find RecordingMetadata source file")
        logger.info("Trying to find pz_core_libs installation...")
        
        # Try to find where pz_core_libs is installed
        try:
            import pz_core_libs
            logger.info(f"pz_core_libs module location: {pz_core_libs.__file__}")
            logger.info(f"pz_core_libs package location: {pz_core_libs.__path__}")
        except Exception as e:
            logger.error(f"Could not import pz_core_libs: {e}")
        
        return
    
    # Check validation code
    logger.info("=" * 80)
    logger.info("Checking validation code in source file")
    logger.info("=" * 80)
    
    validation_findings = check_validation_code(source_file)
    
    logger.info(f"Found {len(validation_findings['validators_found'])} validators")
    logger.info(f"Found prr validation: {validation_findings['prr_validation_found']}")
    logger.info(f"Found {len(validation_findings['validation_code'])} validation code blocks")
    
    # Check git history
    logger.info("=" * 80)
    logger.info("Checking git history")
    logger.info("=" * 80)
    
    git_findings = check_git_history(source_file)
    
    logger.info(f"Git available: {git_findings['git_available']}")
    logger.info(f"Commits found: {len(git_findings['commits_found'])}")
    logger.info(f"Recent changes: {len(git_findings['recent_changes'])}")
    
    # Print detailed findings
    if validation_findings['validation_code']:
        logger.info("=" * 80)
        logger.info("VALIDATION CODE FOUND:")
        logger.info("=" * 80)
        for code_block in validation_findings['validation_code']:
            logger.info(f"\nLine {code_block['line']}:")
            logger.info(code_block['code'])
            if 'context' in code_block:
                logger.info("\nContext:")
                logger.info(code_block['context'])
    
    # Save results
    output_file = Path(__file__).parent.parent / "docs" / "04_testing" / "analysis" / f"PZ_CORE_LIBS_VALIDATION_CHECK_{Path(__file__).stem}.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# pz_core_libs Validation Check\n\n")
        f.write(f"**Source File:** {source_file}\n\n")
        f.write("## Findings\n\n")
        f.write(f"- Validators found: {len(validation_findings['validators_found'])}\n")
        f.write(f"- PRR validation found: {validation_findings['prr_validation_found']}\n")
        f.write(f"- Validation code blocks: {len(validation_findings['validation_code'])}\n")
        f.write(f"- Git available: {git_findings['git_available']}\n")
        f.write(f"- Recent commits: {len(git_findings['commits_found'])}\n\n")
        
        if validation_findings['validation_code']:
            f.write("## Validation Code\n\n")
            for code_block in validation_findings['validation_code']:
                f.write(f"### Line {code_block['line']}\n\n")
                f.write(f"```python\n{code_block.get('context', code_block['code'])}\n```\n\n")
    
    logger.info(f"\nResults saved to: {output_file}")
    logger.info("Investigation complete!")


if __name__ == "__main__":
    main()

