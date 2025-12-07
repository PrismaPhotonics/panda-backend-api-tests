"""
K8s Job Verification Module
============================

This module provides functions to verify job configuration from Kubernetes pods.
It can determine whether a job is HISTORIC or LIVE by inspecting the pod's
command arguments (--time-start, --time-end).

Usage:
    from be_focus_server_tests.load.k8s_job_verification import (
        verify_job_from_k8s,
        verify_all_jobs_from_k8s,
        log_k8s_verification_summary,
        K8sJobVerification,
        JobType
    )

    # Verify a single job
    verification = verify_job_from_k8s(k8s_manager, job_id="1-1637")
    print(f"Job type: {verification.job_type.value}")
    
    # Verify multiple jobs
    verifications = verify_all_jobs_from_k8s(k8s_manager, job_ids)
    summary = log_k8s_verification_summary(verifications)

Author: QA Automation Architect
Date: 2025-12-07
"""

import json
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================================================
# Enums and Data Classes
# =============================================================================

class JobType(Enum):
    """Enum for job types."""
    HISTORIC = "historic"
    LIVE = "live"
    UNKNOWN = "unknown"


@dataclass
class K8sJobVerification:
    """
    Data class for storing K8s job verification results.
    
    Contains all relevant information extracted from the Kubernetes pod
    to verify the job type and configuration.
    """
    job_id: str
    pod_name: str
    pod_status: str
    job_type: JobType
    
    # Time parameters (from pod command)
    time_start: Optional[str] = None
    time_end: Optional[str] = None
    time_zone: Optional[str] = None
    
    # Job configuration
    channels_roi: Optional[Tuple[int, int]] = None
    spectrogram_nfft: Optional[int] = None
    spectrogram_range: Optional[Tuple[int, int]] = None
    grpc_streams_num: Optional[int] = None
    queue_name: Optional[str] = None
    
    # Verification status
    verified: bool = False
    verification_error: Optional[str] = None
    pod_command: List[str] = field(default_factory=list)
    
    def is_historic(self) -> bool:
        """Check if this is a historic job."""
        return self.job_type == JobType.HISTORIC
    
    def is_live(self) -> bool:
        """Check if this is a live job."""
        return self.job_type == JobType.LIVE
    
    def get_summary(self) -> str:
        """Get a summary string of the verification."""
        job_type_str = self.job_type.value.upper()
        if self.is_historic():
            return (f"[{job_type_str}] {self.job_id} | "
                   f"time: {self.time_start} → {self.time_end} | "
                   f"pod: {self.pod_name} ({self.pod_status})")
        else:
            return (f"[{job_type_str}] {self.job_id} | "
                   f"pod: {self.pod_name} ({self.pod_status})")


# =============================================================================
# Core Verification Functions
# =============================================================================

def verify_job_from_k8s(
    kubernetes_manager,
    job_id: str,
    namespace: str = "panda",
    timeout: int = 30
) -> K8sJobVerification:
    """
    Verify a job's configuration from Kubernetes by inspecting the pod.
    
    This function:
    1. Finds the pod corresponding to the job_id
    2. Extracts the command arguments from the pod spec
    3. Parses --time-start and --time-end to determine job type
    4. Returns a detailed verification result
    
    Args:
        kubernetes_manager: KubernetesManager instance
        job_id: The Focus Server job ID (e.g., "1-1637")
        namespace: Kubernetes namespace (default: "panda")
        timeout: Command timeout in seconds
        
    Returns:
        K8sJobVerification with all extracted information
    """
    verification = K8sJobVerification(
        job_id=job_id,
        pod_name="",
        pod_status="Unknown",
        job_type=JobType.UNKNOWN
    )
    
    try:
        # Convert job_id to pod name pattern (e.g., "1-1637" → "grpc-job-1-1637-*")
        # The pod name format is: grpc-job-{job_number}-{job_sequence}-{random_suffix}
        parts = job_id.split("-")
        if len(parts) >= 2:
            job_number = parts[0]
            job_sequence = parts[1]
            pod_pattern = f"grpc-job-{job_number}-{job_sequence}"
        else:
            pod_pattern = f"grpc-job-{job_id}"
        
        # Find the pod using kubectl
        cmd = f"get pods -n {namespace} -o json"
        result = kubernetes_manager._execute_kubectl_via_ssh(cmd, timeout=timeout)
        
        if not result["success"]:
            verification.verification_error = f"Failed to list pods: {result.get('stderr', 'Unknown error')}"
            return verification
        
        # Parse pods and find matching pod
        pods_data = json.loads(result["stdout"])
        matching_pod = None
        
        for pod in pods_data.get("items", []):
            pod_name = pod.get("metadata", {}).get("name", "")
            if pod_name.startswith(pod_pattern):
                matching_pod = pod
                break
        
        if not matching_pod:
            verification.verification_error = f"No pod found matching pattern: {pod_pattern}"
            return verification
        
        # Extract pod info
        verification.pod_name = matching_pod.get("metadata", {}).get("name", "")
        verification.pod_status = matching_pod.get("status", {}).get("phase", "Unknown")
        
        # Extract command from container spec
        containers = matching_pod.get("spec", {}).get("containers", [])
        if containers:
            command = containers[0].get("command", [])
            verification.pod_command = command
            
            # Parse command arguments
            command_str = " ".join(command)
            
            # Extract --time-start
            time_start_match = re.search(r'--time-start\s+(\S+)', command_str)
            if time_start_match:
                verification.time_start = time_start_match.group(1)
            
            # Extract --time-end
            time_end_match = re.search(r'--time-end\s+(\S+)', command_str)
            if time_end_match:
                verification.time_end = time_end_match.group(1)
            
            # Extract --time-zone
            time_zone_match = re.search(r'--time-zone\s+(\S+)', command_str)
            if time_zone_match:
                verification.time_zone = time_zone_match.group(1)
            
            # Extract --roi (channels)
            roi_match = re.search(r'--roi\s+(\d+)\s+(\d+)', command_str)
            if roi_match:
                verification.channels_roi = (int(roi_match.group(1)), int(roi_match.group(2)))
            
            # Extract -sg (spectrogram NFFT)
            sg_match = re.search(r'-sg\s+(\d+)', command_str)
            if sg_match:
                verification.spectrogram_nfft = int(sg_match.group(1))
            
            # Extract --sg-range
            sg_range_match = re.search(r'--sg-range\s+(\d+)\s+(\d+)', command_str)
            if sg_range_match:
                verification.spectrogram_range = (int(sg_range_match.group(1)), int(sg_range_match.group(2)))
            
            # Extract --grpc-streams-num
            streams_match = re.search(r'--grpc-streams-num\s+(\d+)', command_str)
            if streams_match:
                verification.grpc_streams_num = int(streams_match.group(1))
            
            # Extract --queue-name
            queue_match = re.search(r'--queue-name\s+(\S+)', command_str)
            if queue_match:
                verification.queue_name = queue_match.group(1)
            
            # Determine job type based on time parameters
            if verification.time_start and verification.time_end:
                # Has both time-start and time-end → HISTORIC
                verification.job_type = JobType.HISTORIC
            else:
                # No time parameters → LIVE
                verification.job_type = JobType.LIVE
        
        verification.verified = True
        
    except json.JSONDecodeError as e:
        verification.verification_error = f"Failed to parse kubectl output: {e}"
    except Exception as e:
        verification.verification_error = f"Verification error: {str(e)}"
    
    return verification


def verify_all_jobs_from_k8s(
    kubernetes_manager,
    job_ids: List[str],
    namespace: str = "panda",
    timeout_per_job: int = 10
) -> List[K8sJobVerification]:
    """
    Verify multiple jobs from Kubernetes.
    
    Args:
        kubernetes_manager: KubernetesManager instance
        job_ids: List of job IDs to verify
        namespace: Kubernetes namespace
        timeout_per_job: Timeout per job verification
        
    Returns:
        List of K8sJobVerification results
    """
    verifications = []
    
    for job_id in job_ids:
        verification = verify_job_from_k8s(
            kubernetes_manager, 
            job_id, 
            namespace, 
            timeout_per_job
        )
        verifications.append(verification)
    
    return verifications


def verify_jobs_batch_from_k8s(
    kubernetes_manager,
    job_ids: List[str],
    namespace: str = "panda",
    timeout: int = 30
) -> List[K8sJobVerification]:
    """
    Verify multiple jobs from Kubernetes in a single kubectl call.
    
    More efficient than calling verify_job_from_k8s for each job.
    
    Args:
        kubernetes_manager: KubernetesManager instance
        job_ids: List of job IDs to verify
        namespace: Kubernetes namespace
        timeout: Total timeout for the kubectl call
        
    Returns:
        List of K8sJobVerification results
    """
    verifications = []
    
    try:
        # Get all pods in one call
        cmd = f"get pods -n {namespace} -o json"
        result = kubernetes_manager._execute_kubectl_via_ssh(cmd, timeout=timeout)
        
        if not result["success"]:
            # Return empty verifications with error
            for job_id in job_ids:
                v = K8sJobVerification(
                    job_id=job_id,
                    pod_name="",
                    pod_status="Unknown",
                    job_type=JobType.UNKNOWN,
                    verification_error=f"Failed to list pods: {result.get('stderr', 'Unknown error')}"
                )
                verifications.append(v)
            return verifications
        
        pods_data = json.loads(result["stdout"])
        pods_list = pods_data.get("items", [])
        
        # Create a mapping of pod patterns to pods
        pod_map = {}
        for pod in pods_list:
            pod_name = pod.get("metadata", {}).get("name", "")
            if pod_name.startswith("grpc-job-"):
                pod_map[pod_name] = pod
        
        # Verify each job
        for job_id in job_ids:
            verification = K8sJobVerification(
                job_id=job_id,
                pod_name="",
                pod_status="Unknown",
                job_type=JobType.UNKNOWN
            )
            
            # Convert job_id to pod name pattern
            parts = job_id.split("-")
            if len(parts) >= 2:
                job_number = parts[0]
                job_sequence = parts[1]
                pod_pattern = f"grpc-job-{job_number}-{job_sequence}"
            else:
                pod_pattern = f"grpc-job-{job_id}"
            
            # Find matching pod
            matching_pod = None
            for pod_name, pod in pod_map.items():
                if pod_name.startswith(pod_pattern):
                    matching_pod = pod
                    break
            
            if not matching_pod:
                verification.verification_error = f"No pod found matching pattern: {pod_pattern}"
                verifications.append(verification)
                continue
            
            # Extract pod info
            verification.pod_name = matching_pod.get("metadata", {}).get("name", "")
            verification.pod_status = matching_pod.get("status", {}).get("phase", "Unknown")
            
            # Extract command from container spec
            containers = matching_pod.get("spec", {}).get("containers", [])
            if containers:
                command = containers[0].get("command", [])
                verification.pod_command = command
                command_str = " ".join(command)
                
                # Extract time parameters
                time_start_match = re.search(r'--time-start\s+(\S+)', command_str)
                if time_start_match:
                    verification.time_start = time_start_match.group(1)
                
                time_end_match = re.search(r'--time-end\s+(\S+)', command_str)
                if time_end_match:
                    verification.time_end = time_end_match.group(1)
                
                time_zone_match = re.search(r'--time-zone\s+(\S+)', command_str)
                if time_zone_match:
                    verification.time_zone = time_zone_match.group(1)
                
                # Extract other parameters
                roi_match = re.search(r'--roi\s+(\d+)\s+(\d+)', command_str)
                if roi_match:
                    verification.channels_roi = (int(roi_match.group(1)), int(roi_match.group(2)))
                
                sg_match = re.search(r'-sg\s+(\d+)', command_str)
                if sg_match:
                    verification.spectrogram_nfft = int(sg_match.group(1))
                
                sg_range_match = re.search(r'--sg-range\s+(\d+)\s+(\d+)', command_str)
                if sg_range_match:
                    verification.spectrogram_range = (int(sg_range_match.group(1)), int(sg_range_match.group(2)))
                
                streams_match = re.search(r'--grpc-streams-num\s+(\d+)', command_str)
                if streams_match:
                    verification.grpc_streams_num = int(streams_match.group(1))
                
                queue_match = re.search(r'--queue-name\s+(\S+)', command_str)
                if queue_match:
                    verification.queue_name = queue_match.group(1)
                
                # Determine job type
                if verification.time_start and verification.time_end:
                    verification.job_type = JobType.HISTORIC
                else:
                    verification.job_type = JobType.LIVE
            
            verification.verified = True
            verifications.append(verification)
        
    except json.JSONDecodeError as e:
        for job_id in job_ids:
            v = K8sJobVerification(
                job_id=job_id,
                pod_name="",
                pod_status="Unknown",
                job_type=JobType.UNKNOWN,
                verification_error=f"Failed to parse kubectl output: {e}"
            )
            verifications.append(v)
    except Exception as e:
        for job_id in job_ids:
            v = K8sJobVerification(
                job_id=job_id,
                pod_name="",
                pod_status="Unknown",
                job_type=JobType.UNKNOWN,
                verification_error=f"Verification error: {str(e)}"
            )
            verifications.append(v)
    
    return verifications


# =============================================================================
# Logging and Summary Functions
# =============================================================================

def log_k8s_verification_summary(
    verifications: List[K8sJobVerification], 
    logger_instance=None
) -> Dict[str, int]:
    """
    Log a summary of K8s job verifications.
    
    Args:
        verifications: List of verification results
        logger_instance: Logger to use (defaults to module logger)
        
    Returns:
        Dictionary with summary counts
    """
    log = logger_instance or logger
    
    total = len(verifications)
    historic_count = sum(1 for v in verifications if v.is_historic())
    live_count = sum(1 for v in verifications if v.is_live())
    unknown_count = sum(1 for v in verifications if v.job_type == JobType.UNKNOWN)
    verified_count = sum(1 for v in verifications if v.verified)
    failed_count = sum(1 for v in verifications if not v.verified)
    
    log.info("")
    log.info("=" * 80)
    log.info("📊 K8S JOB VERIFICATION SUMMARY")
    log.info("=" * 80)
    log.info(f"   Total jobs verified: {total}")
    log.info(f"   ✅ Successfully verified: {verified_count}")
    log.info(f"   ❌ Failed to verify: {failed_count}")
    log.info("")
    log.info("   📋 Job Types:")
    if total > 0:
        log.info(f"      🕐 HISTORIC jobs: {historic_count} ({100*historic_count/total:.1f}%)")
        log.info(f"      🔴 LIVE jobs: {live_count} ({100*live_count/total:.1f}%)")
    else:
        log.info(f"      🕐 HISTORIC jobs: 0")
        log.info(f"      🔴 LIVE jobs: 0")
    if unknown_count > 0:
        log.info(f"      ❓ UNKNOWN jobs: {unknown_count}")
    log.info("")
    
    # Log details for each job
    if verifications:
        log.info("   📝 Job Details:")
        for v in verifications:
            if v.verified:
                type_emoji = "🕐" if v.is_historic() else "🔴" if v.is_live() else "❓"
                type_str = v.job_type.value.upper()
                time_info = f" | {v.time_start} → {v.time_end}" if v.time_start else ""
                log.info(f"      {type_emoji} [{type_str}] {v.job_id}: {v.pod_name} ({v.pod_status}){time_info}")
            else:
                log.info(f"      ❌ {v.job_id}: {v.verification_error}")
    
    log.info("=" * 80)
    
    return {
        "total": total,
        "historic": historic_count,
        "live": live_count,
        "unknown": unknown_count,
        "verified": verified_count,
        "failed": failed_count
    }


def assert_all_jobs_are_historic(verifications: List[K8sJobVerification]) -> None:
    """
    Assert that all verified jobs are HISTORIC type.
    
    Args:
        verifications: List of verification results
        
    Raises:
        AssertionError: If any LIVE jobs are found
    """
    live_jobs = [v for v in verifications if v.is_live()]
    if live_jobs:
        live_job_ids = [v.job_id for v in live_jobs]
        raise AssertionError(
            f"Expected all jobs to be HISTORIC, but found {len(live_jobs)} LIVE jobs: {live_job_ids}"
        )


def assert_all_jobs_are_live(verifications: List[K8sJobVerification]) -> None:
    """
    Assert that all verified jobs are LIVE type.
    
    Args:
        verifications: List of verification results
        
    Raises:
        AssertionError: If any HISTORIC jobs are found
    """
    historic_jobs = [v for v in verifications if v.is_historic()]
    if historic_jobs:
        historic_job_ids = [v.job_id for v in historic_jobs]
        raise AssertionError(
            f"Expected all jobs to be LIVE, but found {len(historic_jobs)} HISTORIC jobs: {historic_job_ids}"
        )


def get_verification_statistics(verifications: List[K8sJobVerification]) -> Dict[str, Any]:
    """
    Get statistics from a list of verifications.
    
    Args:
        verifications: List of verification results
        
    Returns:
        Dictionary with statistics
    """
    total = len(verifications)
    if total == 0:
        return {
            "total": 0,
            "verified": 0,
            "failed": 0,
            "historic": 0,
            "live": 0,
            "unknown": 0,
            "historic_pct": 0.0,
            "live_pct": 0.0,
            "verification_success_rate": 0.0
        }
    
    verified = sum(1 for v in verifications if v.verified)
    historic = sum(1 for v in verifications if v.is_historic())
    live = sum(1 for v in verifications if v.is_live())
    unknown = sum(1 for v in verifications if v.job_type == JobType.UNKNOWN)
    
    return {
        "total": total,
        "verified": verified,
        "failed": total - verified,
        "historic": historic,
        "live": live,
        "unknown": unknown,
        "historic_pct": 100.0 * historic / total,
        "live_pct": 100.0 * live / total,
        "verification_success_rate": 100.0 * verified / total
    }

