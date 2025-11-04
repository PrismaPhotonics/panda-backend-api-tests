#!/usr/bin/env python3
"""
Upload Test Results to Xray Cloud
==================================

Uploads test execution results to Xray Cloud for automated reporting.

Usage:
    python scripts/xray_upload.py
    python scripts/xray_upload.py --format json
    python scripts/xray_upload.py --format junit
    python scripts/xray_upload.py --test-exec-key PZ-EXE-123

Environment Variables:
    XRAY_CLIENT_ID - Xray Cloud client ID
    XRAY_CLIENT_SECRET - Xray Cloud client secret
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, Any

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class XrayUploader:
    """Upload test results to Xray Cloud."""
    
    def __init__(self):
        self.api_url = "https://xray.cloud.getxray.app/api/v2"
        self.client_id = os.getenv("XRAY_CLIENT_ID")
        self.client_secret = os.getenv("XRAY_CLIENT_SECRET")
        self.project_key = "PZ"
        
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Missing XRAY_CLIENT_ID or XRAY_CLIENT_SECRET environment variables"
            )
    
    def authenticate(self) -> str:
        """Authenticate and get access token."""
        logger.info("Authenticating with Xray Cloud...")
        
        response = requests.post(
            f"{self.api_url}/authenticate",
            json={
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
        )
        response.raise_for_status()
        
        token = response.text.strip('"')
        logger.info("✅ Authentication successful")
        
        return token
    
    def upload_json(self, json_file: str, test_exec_key: str = None) -> Dict[str, Any]:
        """Upload Xray JSON format."""
        logger.info(f"Uploading Xray JSON: {json_file}")
        
        with open(json_file, "rb") as f:
            files = {"file": f}
            data = {"projectKey": self.project_key}
            
            if test_exec_key:
                data["testExecKey"] = test_exec_key
                logger.info(f"Linking to existing Test Execution: {test_exec_key}")
            
            token = self.authenticate()
            
            response = requests.post(
                f"{self.api_url}/import/execution",
                headers={"Authorization": f"Bearer {token}"},
                files=files,
                data=data
            )
        
        response.raise_for_status()
        result = response.json()
        
        logger.info(f"✅ Upload successful!")
        logger.info(f"   Test Execution: {result.get('testExecIssue', {}).get('key')}")
        logger.info(f"   Test Execution ID: {result.get('testExecIssue', {}).get('id')}")
        
        return result
    
    def upload_junit(self, junit_file: str, test_exec_key: str = None) -> Dict[str, Any]:
        """Upload JUnit XML format."""
        logger.info(f"Uploading JUnit XML: {junit_file}")
        
        with open(junit_file, "rb") as f:
            files = {"file": f}
            params = {"projectKey": self.project_key}
            
            if test_exec_key:
                params["testExecKey"] = test_exec_key
                logger.info(f"Linking to existing Test Execution: {test_exec_key}")
            
            token = self.authenticate()
            
            response = requests.post(
                f"{self.api_url}/import/execution/junit",
                headers={"Authorization": f"Bearer {token}"},
                files=files,
                params=params
            )
        
        response.raise_for_status()
        result = response.json()
        
        logger.info(f"✅ Upload successful!")
        logger.info(f"   Test Execution: {result.get('testExecIssue', {}).get('key')}")
        
        return result


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Upload test results to Xray Cloud"
    )
    parser.add_argument(
        "--format",
        choices=["json", "junit", "auto"],
        default="auto",
        help="File format to upload"
    )
    parser.add_argument(
        "--file",
        help="Specific file to upload (default: auto-detect from reports/)"
    )
    parser.add_argument(
        "--test-exec-key",
        help="Link to existing Test Execution key"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Auto-detect file if not provided
    if args.file:
        file_path = Path(args.file)
    else:
        reports_dir = Path("reports")
        
        if args.format == "json":
            file_path = reports_dir / "xray-exec.json"
        elif args.format == "junit":
            file_path = reports_dir / "junit.xml"
        else:
            # Auto-detect: prefer JSON, fallback to JUnit
            if (reports_dir / "xray-exec.json").exists():
                file_path = reports_dir / "xray-exec.json"
            elif (reports_dir / "junit.xml").exists():
                file_path = reports_dir / "junit.xml"
            else:
                logger.error("No test result file found in reports/")
                sys.exit(1)
    
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        sys.exit(1)
    
    # Upload
    uploader = XrayUploader()
    
    try:
        if file_path.suffix == ".json" or (args.format == "json"):
            result = uploader.upload_json(str(file_path), args.test_exec_key)
        else:
            result = uploader.upload_junit(str(file_path), args.test_exec_key)
        
        logger.info("\n🎉 Upload complete!")
        logger.info("You can view results in Jira Xray:")
        if 'testExecIssue' in result:
            test_exec_key = result['testExecIssue'].get('key')
            if test_exec_key:
                logger.info(f"   https://yoursite.atlassian.net/browse/{test_exec_key}")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Upload failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"   Response: {e.response.text}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

