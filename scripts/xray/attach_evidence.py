#!/usr/bin/env python3
"""
Attach Evidence to Xray Test Execution
======================================

Attaches logs, screenshots, and other evidence files to a Test Execution issue.

Usage:
    python scripts/xray/attach_evidence.py --test-exec PZ-EXE-123 --evidence logs/ --evidence screenshots/
    python scripts/xray/attach_evidence.py --test-exec PZ-EXE-123 --file error.log
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from typing import List

import requests

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.config_manager import ConfigManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class XrayEvidenceAttacher:
    """Attaches evidence files to Xray Test Execution."""
    
    def __init__(self):
        """Initialize the attacher."""
        config_manager = ConfigManager()
        jira_config = config_manager.get("jira", {})
        
        self.base_url = jira_config.get("base_url", "https://prismaphotonics.atlassian.net")
        self.api_token = jira_config.get("api_token")
        self.email = jira_config.get("email")
        
        if not self.api_token or not self.email:
            raise ValueError(
                "Missing JIRA_API_TOKEN or JIRA_EMAIL in configuration"
            )
    
    def attach_file(self, test_exec_key: str, file_path: Path) -> bool:
        """
        Attach a single file to Test Execution.
        
        Args:
            test_exec_key: Test Execution key (e.g., "PZ-EXE-123")
            file_path: Path to file to attach
            
        Returns:
            True if successful
        """
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return False
        
        # Check file size (max 10MB for Jira)
        file_size = file_path.stat().st_size
        max_size = 10 * 1024 * 1024  # 10MB
        
        if file_size > max_size:
            logger.warning(f"File too large ({file_size} bytes > {max_size} bytes): {file_path}")
            return False
        
        logger.info(f"Attaching {file_path.name} ({file_size} bytes) to {test_exec_key}...")
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f, 'application/octet-stream')}
                headers = {
                    'X-Atlassian-Token': 'no-check'
                }
                auth = (self.email, self.api_token)
                
                response = requests.post(
                    f"{self.base_url}/rest/api/3/issue/{test_exec_key}/attachments",
                    headers=headers,
                    files=files,
                    auth=auth
                )
            
            response.raise_for_status()
            logger.info(f"✅ Successfully attached {file_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to attach {file_path.name}: {e}")
            return False
    
    def attach_directory(self, test_exec_key: str, directory: Path, patterns: List[str] = None) -> int:
        """
        Attach all matching files from a directory.
        
        Args:
            test_exec_key: Test Execution key
            directory: Directory to search
            patterns: File patterns to match (e.g., ["*.log", "*.png"])
            
        Returns:
            Number of files attached
        """
        if not directory.exists() or not directory.is_dir():
            logger.warning(f"Directory not found: {directory}")
            return 0
        
        if patterns is None:
            patterns = ["*"]
        
        attached = 0
        
        for pattern in patterns:
            for file_path in directory.rglob(pattern):
                if file_path.is_file():
                    if self.attach_file(test_exec_key, file_path):
                        attached += 1
        
        return attached


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Attach evidence files to Xray Test Execution"
    )
    parser.add_argument(
        "--test-exec",
        type=str,
        required=True,
        help="Test Execution key (e.g., PZ-EXE-123)"
    )
    parser.add_argument(
        "--evidence",
        type=str,
        action="append",
        help="Directory or file to attach (can be specified multiple times)"
    )
    parser.add_argument(
        "--file",
        type=str,
        action="append",
        help="Specific file to attach (can be specified multiple times)"
    )
    parser.add_argument(
        "--pattern",
        type=str,
        action="append",
        default=["*.log", "*.png", "*.jpg", "*.html"],
        help="File patterns to match (default: *.log, *.png, *.jpg, *.html)"
    )
    
    args = parser.parse_args()
    
    try:
        attacher = XrayEvidenceAttacher()
        attached_count = 0
        
        # Attach specific files
        if args.file:
            for file_path_str in args.file:
                file_path = Path(file_path_str)
                if attacher.attach_file(args.test_exec, file_path):
                    attached_count += 1
        
        # Attach from directories
        if args.evidence:
            for evidence_path_str in args.evidence:
                evidence_path = Path(evidence_path_str)
                
                if evidence_path.is_file():
                    if attacher.attach_file(args.test_exec, evidence_path):
                        attached_count += 1
                elif evidence_path.is_dir():
                    count = attacher.attach_directory(
                        args.test_exec,
                        evidence_path,
                        patterns=args.pattern
                    )
                    attached_count += count
                else:
                    logger.warning(f"Path not found: {evidence_path}")
        
        logger.info(f"\n✅ Total files attached: {attached_count}")
        
        if attached_count == 0:
            logger.warning("No files were attached. Check paths and permissions.")
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

