#!/usr/bin/env python3
"""
PZ Repository Sync Script
==========================

This script synchronizes the PZ development repository submodule
to ensure tests always run against the latest production code.

Usage:
    python scripts/sync_pz_code.py [--branch BRANCH] [--verbose]

Author: QA Automation Architect
"""

import sys
import os
import subprocess
import argparse
import logging
from pathlib import Path
from typing import Optional, Tuple


# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


logger = logging.getLogger(__name__)


class PZSyncManager:
    """
    Manages synchronization of PZ repository submodule.
    
    This class handles Git submodule operations to keep the PZ
    codebase up-to-date with the latest development changes.
    """
    
    def __init__(self, project_root: Path, verbose: bool = False):
        """
        Initialize sync manager.
        
        Args:
            project_root: Path to project root directory
            verbose: Enable verbose logging
        """
        self.project_root = project_root
        self.pz_submodule_path = project_root / "external" / "pz"
        self.verbose = verbose
        
        # Configure logging
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s [%(levelname)8s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def run_command(
        self,
        command: list,
        cwd: Optional[Path] = None,
        timeout: int = 300
    ) -> Tuple[int, str, str]:
        """
        Run shell command and return result.
        
        Args:
            command: Command as list of strings
            cwd: Working directory for command
            timeout: Command timeout in seconds
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        cwd = cwd or self.project_root
        
        logger.debug(f"Running command: {' '.join(command)}")
        logger.debug(f"Working directory: {cwd}")
        
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return result.returncode, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Command timed out after {timeout}s")
            return -1, "", "Command timeout"
        except Exception as e:
            logger.error(f"❌ Command failed: {e}")
            return -1, "", str(e)
    
    def check_submodule_exists(self) -> bool:
        """
        Check if PZ submodule is initialized.
        
        Returns:
            True if submodule exists and is initialized
        """
        if not self.pz_submodule_path.exists():
            logger.warning("⚠️  PZ submodule directory does not exist")
            return False
        
        # Check if it's a git repository
        git_dir = self.pz_submodule_path / ".git"
        if not git_dir.exists():
            logger.warning("⚠️  PZ submodule not initialized (no .git)")
            return False
        
        logger.info("✅ PZ submodule exists and is initialized")
        return True
    
    def initialize_submodule(self) -> bool:
        """
        Initialize PZ submodule if not already done.
        
        Returns:
            True if successful
        """
        logger.info("🔄 Initializing PZ submodule...")
        
        exit_code, stdout, stderr = self.run_command(
            ["git", "submodule", "update", "--init", "--recursive", "external/pz"]
        )
        
        if exit_code == 0:
            logger.info("✅ Submodule initialized successfully")
            return True
        else:
            logger.error(f"❌ Submodule initialization failed: {stderr}")
            return False
    
    def get_current_commit(self) -> Optional[str]:
        """
        Get current commit hash of PZ submodule.
        
        Returns:
            Commit hash or None if failed
        """
        exit_code, stdout, stderr = self.run_command(
            ["git", "rev-parse", "HEAD"],
            cwd=self.pz_submodule_path
        )
        
        if exit_code == 0:
            return stdout.strip()[:8]
        return None
    
    def get_current_branch(self) -> Optional[str]:
        """
        Get current branch of PZ submodule.
        
        Returns:
            Branch name or None if failed
        """
        exit_code, stdout, stderr = self.run_command(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=self.pz_submodule_path
        )
        
        if exit_code == 0:
            return stdout.strip()
        return None
    
    def sync_to_latest(self, branch: Optional[str] = None) -> bool:
        """
        Sync PZ submodule to latest version.
        
        Args:
            branch: Specific branch to sync to (default: remote HEAD)
            
        Returns:
            True if successful
        """
        logger.info("=" * 80)
        logger.info("🔄 Starting PZ Repository Sync")
        logger.info("=" * 80)
        
        # Check if submodule exists
        if not self.check_submodule_exists():
            logger.info("Initializing submodule for the first time...")
            if not self.initialize_submodule():
                return False
        
        # Show current state
        current_commit = self.get_current_commit()
        current_branch = self.get_current_branch()
        
        if current_commit and current_branch:
            logger.info(f"📌 Current state: {current_branch} @ {current_commit}")
        
        # Fetch latest changes
        logger.info("📥 Fetching latest changes from remote...")
        exit_code, stdout, stderr = self.run_command(
            ["git", "fetch", "origin"],
            cwd=self.pz_submodule_path
        )
        
        if exit_code != 0:
            logger.error(f"❌ Fetch failed: {stderr}")
            return False
        
        # Checkout specific branch if requested
        if branch:
            logger.info(f"🔀 Checking out branch: {branch}")
            exit_code, stdout, stderr = self.run_command(
                ["git", "checkout", branch],
                cwd=self.pz_submodule_path
            )
            
            if exit_code != 0:
                logger.error(f"❌ Checkout failed: {stderr}")
                return False
        
        # Pull latest changes
        logger.info("⬇️  Pulling latest changes...")
        exit_code, stdout, stderr = self.run_command(
            ["git", "pull", "origin", branch or "master"],
            cwd=self.pz_submodule_path
        )
        
        if exit_code != 0:
            logger.error(f"❌ Pull failed: {stderr}")
            return False
        
        # Get new state
        new_commit = self.get_current_commit()
        new_branch = self.get_current_branch()
        
        logger.info("=" * 80)
        logger.info("✅ Sync completed successfully!")
        logger.info(f"📌 New state: {new_branch} @ {new_commit}")
        logger.info("=" * 80)
        
        # Show summary
        if current_commit != new_commit:
            logger.info(f"📝 Updated from {current_commit} to {new_commit}")
        else:
            logger.info("📝 Already up-to-date")
        
        return True
    
    def show_status(self) -> None:
        """Display current PZ submodule status."""
        logger.info("=" * 80)
        logger.info("📊 PZ Repository Status")
        logger.info("=" * 80)
        
        if not self.check_submodule_exists():
            logger.warning("⚠️  Submodule not initialized")
            logger.info("\nRun: python scripts/sync_pz_code.py --sync")
            return
        
        # Get info
        commit = self.get_current_commit()
        branch = self.get_current_branch()
        
        # Get last commit info
        exit_code, stdout, stderr = self.run_command(
            ["git", "log", "-1", "--format=%ci - %s"],
            cwd=self.pz_submodule_path
        )
        last_commit_info = stdout.strip() if exit_code == 0 else "Unknown"
        
        # Get file count
        exit_code, stdout, stderr = self.run_command(
            ["git", "ls-files"],
            cwd=self.pz_submodule_path
        )
        file_count = len(stdout.splitlines()) if exit_code == 0 else 0
        
        # Display info
        logger.info(f"\n📍 Location: {self.pz_submodule_path}")
        logger.info(f"🌿 Branch: {branch}")
        logger.info(f"📌 Commit: {commit}")
        logger.info(f"📅 Last Commit: {last_commit_info}")
        logger.info(f"📦 Files: {file_count:,}")
        logger.info("\n" + "=" * 80)


def main():
    """Main entry point for sync script."""
    parser = argparse.ArgumentParser(
        description="Sync PZ development repository to latest version"
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Perform sync operation"
    )
    parser.add_argument(
        "--branch",
        type=str,
        default=None,
        help="Specific branch to sync to (default: master)"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show current status without syncing"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Create sync manager
    manager = PZSyncManager(
        project_root=project_root,
        verbose=args.verbose
    )
    
    # Execute requested operation
    if args.status:
        manager.show_status()
    elif args.sync:
        success = manager.sync_to_latest(branch=args.branch)
        sys.exit(0 if success else 1)
    else:
        # Default: show status
        manager.show_status()
        print("\nℹ️  Use --sync to update to latest version")
        print("   Use --status to show current status")


if __name__ == "__main__":
    main()

