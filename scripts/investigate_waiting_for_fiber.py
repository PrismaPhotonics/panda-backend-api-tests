#!/usr/bin/env python3
"""
Script to investigate "waiting for fiber" issue in PZ codebase.

Performs 4 investigations:
1. Check pz_core_libs for the error message
2. Check Git History of pz_core_libs for recent changes
3. Check Focus Server logs for when the error first appeared
4. Check system state - focus_manager.fiber_metadata.prr when system is in "waiting for fiber" state
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager
from src.infrastructure.kubernetes_manager import KubernetesManager
from src.apis.focus_server_api import FocusServerAPI

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


def check_pz_core_libs_error(pz_path: Path) -> Dict[str, Any]:
    """
    Investigation 1: Check pz_core_libs for the error message.
    
    Args:
        pz_path: Path to PZ repository
        
    Returns:
        Dictionary with findings
    """
    logger.info("=" * 80)
    logger.info("INVESTIGATION 1: Checking pz_core_libs for error message")
    logger.info("=" * 80)
    
    findings = {
        "error_found": False,
        "files_found": [],
        "error_message": "Cannot proceed: Missing required fiber metadata fields: prr"
    }
    
    # Search for the error message in PZ codebase
    error_patterns = [
        "Cannot proceed",
        "Missing required.*metadata",
        "Missing.*fiber.*metadata",
        "Missing.*prr"
    ]
    
    try:
        # Use grep to search for error patterns
        for pattern in error_patterns:
            try:
                result = subprocess.run(
                    ["grep", "-r", "-i", pattern, str(pz_path)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0 and result.stdout:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if any(keyword in line.lower() for keyword in ["cannot proceed", "missing required", "prr"]):
                            findings["files_found"].append(line)
                            findings["error_found"] = True
                            logger.info(f"Found match: {line[:100]}")
            except FileNotFoundError:
                # grep not available on Windows, use Python search instead
                logger.info("grep not available, using Python file search...")
                for py_file in pz_path.rglob("*.py"):
                    try:
                        with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if pattern.lower() in content.lower():
                                findings["files_found"].append(str(py_file))
                                findings["error_found"] = True
                                logger.info(f"Found in: {py_file}")
                    except Exception as e:
                        continue
    except Exception as e:
        logger.error(f"Error searching pz_core_libs: {e}")
    
    logger.info(f"Found {len(findings['files_found'])} files with error patterns")
    return findings


def check_git_history_pz_core_libs(pz_path: Path) -> Dict[str, Any]:
    """
    Investigation 2: Check Git History of pz_core_libs for recent changes.
    
    Args:
        pz_path: Path to PZ repository
        
    Returns:
        Dictionary with findings
    """
    logger.info("=" * 80)
    logger.info("INVESTIGATION 2: Checking Git History of pz_core_libs")
    logger.info("=" * 80)
    
    findings = {
        "commits_found": [],
        "recent_changes": []
    }
    
    try:
        # Check if pz_core_libs is a submodule or separate repo
        os.chdir(pz_path)
        
        # Search for commits related to metadata validation
        search_terms = ["metadata", "validation", "prr", "fiber", "recording_metadata"]
        
        for term in search_terms:
            try:
                result = subprocess.run(
                    ["git", "log", "--all", "--since=2 weeks ago", "--oneline", "--grep", term, "-i"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0 and result.stdout:
                    commits = result.stdout.strip().split('\n')
                    for commit in commits:
                        if commit and commit not in findings["commits_found"]:
                            findings["commits_found"].append(commit)
                            logger.info(f"Found commit: {commit}")
            except Exception as e:
                logger.warning(f"Error checking git history for '{term}': {e}")
        
        # Check for changes in recording_metadata files
        try:
            result = subprocess.run(
                ["git", "log", "--all", "--since=2 weeks ago", "--oneline", "--", "*recording_metadata*"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout:
                commits = result.stdout.strip().split('\n')
                findings["recent_changes"].extend(commits)
                logger.info(f"Found {len(commits)} commits related to recording_metadata")
        except Exception as e:
            logger.warning(f"Error checking recording_metadata changes: {e}")
            
    except Exception as e:
        logger.error(f"Error checking git history: {e}")
    
    return findings


def check_focus_server_logs(config_manager: ConfigManager) -> Dict[str, Any]:
    """
    Investigation 3: Check Focus Server logs for when the error first appeared.
    
    Args:
        config_manager: Configuration manager instance
        
    Returns:
        Dictionary with findings
    """
    logger.info("=" * 80)
    logger.info("INVESTIGATION 3: Checking Focus Server logs")
    logger.info("=" * 80)
    
    findings = {
        "error_found_in_logs": False,
        "first_occurrence": None,
        "log_entries": []
    }
    
    try:
        # Initialize Kubernetes manager
        k8s_manager = KubernetesManager(config_manager)
        
        # Get Focus Server pods
        pods = k8s_manager.get_pods(namespace="panda")
        focus_pods = [p for p in pods if "focus-server" in p.get("name", "").lower()]
        
        if not focus_pods:
            logger.warning("No Focus Server pods found")
            return findings
        
        logger.info(f"Found {len(focus_pods)} Focus Server pod(s)")
        
        # Check logs from each pod
        error_patterns = [
            "Cannot proceed",
            "Missing required fiber metadata fields",
            "validation failed",
            "waiting for fiber"
        ]
        
        for pod in focus_pods:
            pod_name = pod.get("name")
            logger.info(f"Checking logs from pod: {pod_name}")
            
            try:
                # Get recent logs (last 1000 lines)
                logs = k8s_manager.get_pod_logs(pod_name, namespace="panda", tail_lines=1000)
                
                # Search for error patterns
                log_lines = logs.split('\n')
                for i, line in enumerate(log_lines):
                    for pattern in error_patterns:
                        if pattern.lower() in line.lower():
                            findings["error_found_in_logs"] = True
                            findings["log_entries"].append({
                                "pod": pod_name,
                                "line_number": i + 1,
                                "content": line[:200]  # First 200 chars
                            })
                            
                            if not findings["first_occurrence"]:
                                # Try to extract timestamp if available
                                findings["first_occurrence"] = {
                                    "pod": pod_name,
                                    "line": line[:200]
                                }
                            
                            logger.info(f"Found error in logs: {line[:100]}")
                            break
            except Exception as e:
                logger.error(f"Error getting logs from pod {pod_name}: {e}")
        
    except Exception as e:
        logger.error(f"Error checking Focus Server logs: {e}")
    
    return findings


def check_system_state(config_manager: ConfigManager) -> Dict[str, Any]:
    """
    Investigation 4: Check system state - focus_manager.fiber_metadata.prr.
    
    Args:
        config_manager: Configuration manager instance
        
    Returns:
        Dictionary with findings
    """
    logger.info("=" * 80)
    logger.info("INVESTIGATION 4: Checking system state")
    logger.info("=" * 80)
    
    findings = {
        "metadata_available": False,
        "prr_value": None,
        "is_waiting_for_fiber": False,
        "metadata_details": {}
    }
    
    try:
        # Initialize Focus Server API
        focus_api = FocusServerAPI(config_manager)
        
        # Get live metadata
        try:
            metadata = focus_api.get_live_metadata_flat()
            findings["metadata_available"] = True
            findings["prr_value"] = metadata.prr
            findings["is_waiting_for_fiber"] = metadata.is_waiting_for_fiber
            
            findings["metadata_details"] = {
                "prr": metadata.prr,
                "dx": metadata.dx,
                "sw_version": metadata.sw_version,
                "fiber_description": metadata.fiber_description,
                "number_of_channels": metadata.number_of_channels,
                "fiber_start_meters": metadata.fiber_start_meters,
                "fiber_length_meters": metadata.fiber_length_meters
            }
            
            logger.info(f"Metadata retrieved successfully:")
            logger.info(f"  PRR: {metadata.prr}")
            logger.info(f"  DX: {metadata.dx}")
            logger.info(f"  SW Version: {metadata.sw_version}")
            logger.info(f"  Is Waiting for Fiber: {metadata.is_waiting_for_fiber}")
            
            if metadata.is_waiting_for_fiber:
                logger.warning("⚠️  System is in 'waiting for fiber' state!")
                logger.warning(f"   PRR: {metadata.prr}")
                logger.warning(f"   DX: {metadata.dx}")
                logger.warning(f"   SW Version: {metadata.sw_version}")
            
        except Exception as e:
            logger.error(f"Error getting metadata: {e}")
            findings["error"] = str(e)
        
    except Exception as e:
        logger.error(f"Error checking system state: {e}")
        findings["error"] = str(e)
    
    return findings


def main():
    """Main investigation function."""
    logger.info("Starting investigation of 'waiting for fiber' issue")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    # Initialize config manager
    try:
        config_manager = ConfigManager(env="staging")
    except Exception as e:
        logger.error(f"Failed to initialize config manager: {e}")
        return
    
    # Path to PZ repository
    pz_path = Path("pz")
    if not pz_path.exists():
        logger.warning(f"PZ repository not found at {pz_path}")
        pz_path = None
    
    # Run all investigations
    results = {
        "timestamp": datetime.now().isoformat(),
        "investigations": {}
    }
    
    # Investigation 1: Check pz_core_libs
    if pz_path:
        results["investigations"]["pz_core_libs_search"] = check_pz_core_libs_error(pz_path)
    else:
        results["investigations"]["pz_core_libs_search"] = {"error": "PZ path not found"}
    
    # Investigation 2: Check Git History
    if pz_path:
        results["investigations"]["git_history"] = check_git_history_pz_core_libs(pz_path)
    else:
        results["investigations"]["git_history"] = {"error": "PZ path not found"}
    
    # Investigation 3: Check Focus Server logs
    results["investigations"]["focus_server_logs"] = check_focus_server_logs(config_manager)
    
    # Investigation 4: Check system state
    results["investigations"]["system_state"] = check_system_state(config_manager)
    
    # Print summary
    logger.info("=" * 80)
    logger.info("INVESTIGATION SUMMARY")
    logger.info("=" * 80)
    
    logger.info("\n1. pz_core_libs Search:")
    inv1 = results["investigations"]["pz_core_libs_search"]
    logger.info(f"   Error found: {inv1.get('error_found', False)}")
    logger.info(f"   Files found: {len(inv1.get('files_found', []))}")
    
    logger.info("\n2. Git History:")
    inv2 = results["investigations"]["git_history"]
    logger.info(f"   Commits found: {len(inv2.get('commits_found', []))}")
    logger.info(f"   Recent changes: {len(inv2.get('recent_changes', []))}")
    
    logger.info("\n3. Focus Server Logs:")
    inv3 = results["investigations"]["focus_server_logs"]
    logger.info(f"   Error found in logs: {inv3.get('error_found_in_logs', False)}")
    logger.info(f"   Log entries: {len(inv3.get('log_entries', []))}")
    
    logger.info("\n4. System State:")
    inv4 = results["investigations"]["system_state"]
    logger.info(f"   Metadata available: {inv4.get('metadata_available', False)}")
    logger.info(f"   PRR value: {inv4.get('prr_value', 'N/A')}")
    logger.info(f"   Is waiting for fiber: {inv4.get('is_waiting_for_fiber', False)}")
    
    # Save results to file
    output_file = project_root / "docs" / "04_testing" / "analysis" / f"WAITING_FOR_FIBER_INVESTIGATION_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Waiting for Fiber Investigation Report\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Summary\n\n")
        f.write(f"- Error found in pz_core_libs: {inv1.get('error_found', False)}\n")
        f.write(f"- Commits found: {len(inv2.get('commits_found', []))}\n")
        f.write(f"- Error found in logs: {inv3.get('error_found_in_logs', False)}\n")
        f.write(f"- System waiting for fiber: {inv4.get('is_waiting_for_fiber', False)}\n")
        f.write(f"- PRR value: {inv4.get('prr_value', 'N/A')}\n\n")
        f.write("## Detailed Results\n\n")
        f.write("```json\n")
        import json
        f.write(json.dumps(results, indent=2, default=str))
        f.write("\n```\n")
    
    logger.info(f"\nResults saved to: {output_file}")
    logger.info("Investigation complete!")


if __name__ == "__main__":
    main()

