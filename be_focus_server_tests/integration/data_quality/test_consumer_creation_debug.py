"""
Integration Tests - Data Quality: Consumer Creation Debugging
=============================================================

Deep investigation tests for consumer creation issues.
These tests help identify why consumers are not being created after configure.

Tests Covered:
    - Consumer creation timing
    - Metadata vs Waterfall endpoint comparison
    - Backend logs analysis
    - RabbitMQ consumer registration

Author: QA Automation
Date: 2025-11-13
"""

import pytest
import logging
import time
import threading
from typing import Dict, Any, List, Optional
from collections import deque

from src.apis.focus_server_api import FocusServerAPI
from src.core.exceptions import APIError
from src.models.focus_server_models import ConfigureRequest, ViewType
from src.infrastructure.kubernetes_manager import KubernetesManager

logger = logging.getLogger(__name__)


def monitor_k8s_pods(
    k8s_manager: KubernetesManager,
    job_id: str,
    stop_event: threading.Event,
    pod_history: deque,
    poll_interval: float = 0.5
):
    """
    Monitor K8s pods in parallel thread.
    
    This function runs in a separate thread and monitors K8s pods
    that match the job_id, collecting information about their creation
    and status.
    
    Args:
        k8s_manager: KubernetesManager instance
        job_id: Job ID to monitor
        stop_event: Threading event to signal when to stop monitoring
        pod_history: Deque to store pod history
        poll_interval: How often to poll K8s (in seconds)
    """
    logger.info(f"🔍 K8s Pod Monitor started for job_id: {job_id}")
    
    namespace = k8s_manager.k8s_config.get("namespace", "panda")
    start_time = time.time()
    
    while not stop_event.is_set():
        try:
            elapsed = time.time() - start_time
            
            # Search for pods with job_id label
            pods_with_label = k8s_manager.get_pods(
                namespace=namespace,
                label_selector=f"job_id={job_id}"
            )
            
            # Also search for pods that might contain job_id in name or labels
            all_pods = k8s_manager.get_pods(namespace=namespace)
            
            # Search for pods by name pattern (e.g., "grpc-job-19-5-xxx")
            pods_by_name = [
                pod for pod in all_pods
                if job_id in pod.get("name", "")
            ]
            
            # Search for grpc/baby-analyzer pods
            grpc_pods = [
                pod for pod in all_pods
                if ("grpc" in pod.get("name", "").lower() or
                    "baby" in pod.get("name", "").lower() or
                    "analyzer" in pod.get("name", "").lower()) and
                   job_id in pod.get("name", "")
            ]
            
            # Combine all pods (remove duplicates)
            all_matching_pods = {}
            for pod in pods_with_label:
                pod_name = pod.get("name")
                if pod_name:
                    all_matching_pods[pod_name] = pod
            
            for pod in pods_by_name:
                pod_name = pod.get("name")
                if pod_name and pod_name not in all_matching_pods:
                    all_matching_pods[pod_name] = pod
            
            for pod in grpc_pods:
                pod_name = pod.get("name")
                if pod_name and pod_name not in all_matching_pods:
                    all_matching_pods[pod_name] = pod
            
            pods = list(all_matching_pods.values())
            
            # Record pod information
            pod_snapshot = {
                "time": elapsed,
                "pods_with_job_id_label": len(pods_with_label),
                "pods_with_job_id_in_name": len(pods_by_name),
                "grpc_pods_found": len(grpc_pods),
                "total_matching_pods": len(pods),
                "pods": []
            }
            
            # Add all matching pods with their match type
            for pod in pods:
                pod_name = pod.get("name", "")
                matched_by = []
                
                # Determine how this pod was matched
                if pod in pods_with_label:
                    matched_by.append("job_id_label")
                if pod in pods_by_name:
                    matched_by.append("name_contains_job_id")
                if pod in grpc_pods:
                    matched_by.append("grpc_name_pattern")
                
                pod_info = {
                    "name": pod_name,
                    "status": pod.get("status"),
                    "ready": pod.get("ready"),
                    "restart_count": pod.get("restart_count", 0),
                    "node_name": pod.get("node_name"),
                    "labels": pod.get("labels", {}),
                    "matched_by": ", ".join(matched_by) if matched_by else "unknown"
                }
                pod_snapshot["pods"].append(pod_info)
            
            pod_history.append(pod_snapshot)
            
            if pods:
                logger.info(
                    f"⏱️  [{elapsed:.2f}s] Found {len(pods)} pod(s) matching job_id={job_id} "
                    f"(label: {len(pods_with_label)}, name: {len(pods_by_name)}, grpc: {len(grpc_pods)})"
                )
                # Log details about each pod found
                for pod in pods:
                    pod_name = pod.get('name', 'unknown')
                    pod_status = pod.get('status', 'unknown')
                    pod_ready = pod.get('ready', 'unknown')
                    
                    # Determine match type
                    matched_by_list = []
                    if pod in pods_with_label:
                        matched_by_list.append("label")
                    if pod in pods_by_name:
                        matched_by_list.append("name")
                    if pod in grpc_pods:
                        matched_by_list.append("grpc_pattern")
                    matched_by = ", ".join(matched_by_list) if matched_by_list else "unknown"
                    
                    logger.info(
                        f"    📦 Pod: {pod_name} | Status: {pod_status} | "
                        f"Ready: {pod_ready} | Matched by: {matched_by}"
                    )
            
        except Exception as e:
            logger.warning(f"⚠️  Error monitoring K8s pods: {e}")
        
        # Wait before next poll
        stop_event.wait(timeout=poll_interval)
    
    logger.info(f"🔍 K8s Pod Monitor stopped for job_id: {job_id}")


@pytest.mark.integration
@pytest.mark.data_quality
@pytest.mark.api
class TestConsumerCreationDebug:
    """
    Test suite for debugging consumer creation issues.
    
    These tests help identify why consumers are not being created
    after configure_streaming_job.
    """
    
    def test_consumer_creation_timing(
        self,
        focus_server_api: FocusServerAPI,
        config_manager
    ):
        """
        Test: Measure time for consumer creation.
        
        Objective:
            Measure how long it takes for a consumer to be created
            after configure_streaming_job is called.
        
        Steps:
            1. Configure job and record start time
            2. Poll metadata endpoint every 100ms
            3. Record time until consumer is ready
            4. Verify timing is within acceptable range
        
        Expected:
            Consumer should be created within 30 seconds (allowing for backend processing time).
        """
        logger.info("=" * 80)
        logger.info("TEST: Consumer Creation Timing")
        logger.info("=" * 80)
        
        payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        config_request = ConfigureRequest(**payload)
        
        try:
            # Step 1: Configure job
            logger.info("Step 1: Configuring job...")
            start_time = time.time()
            response = focus_server_api.configure_streaming_job(config_request)
            configure_time = time.time() - start_time
            job_id = response.job_id
            
            assert job_id, "Job ID must be returned from configure_streaming_job"
            logger.info(f"Job configured in {configure_time:.3f}s: {job_id}")
            
            # Step 1.5: Start K8s pod monitoring in parallel thread
            k8s_manager = None
            pod_monitor_thread = None
            pod_stop_event = threading.Event()
            pod_history = deque(maxlen=1000)  # Store up to 1000 snapshots
            
            try:
                k8s_manager = KubernetesManager(config_manager)
                if k8s_manager.k8s_core_v1 is not None or k8s_manager.use_ssh_fallback:
                    logger.info("🔍 Starting K8s pod monitoring thread...")
                    pod_monitor_thread = threading.Thread(
                        target=monitor_k8s_pods,
                        args=(k8s_manager, job_id, pod_stop_event, pod_history, 0.5),
                        daemon=True
                    )
                    pod_monitor_thread.start()
                    logger.info("✅ K8s pod monitoring thread started")
                else:
                    logger.warning("⚠️  K8s not available - skipping pod monitoring")
            except Exception as e:
                logger.warning(f"⚠️  Failed to start K8s pod monitoring: {e}")
            
            # Step 2: Poll metadata endpoint to detect consumer creation
            logger.info("Step 2: Polling metadata endpoint for consumer creation...")
            max_wait = 30  # 30 seconds - allow time for backend to create consumer
            poll_interval = 0.1  # 100ms
            creation_times = []
            status_history = []
            
            consumer_ready = False
            poll_start = time.time()
            
            while time.time() - poll_start < max_wait:
                try:
                    # Use get_job_metadata instead of get_task_metadata
                    # get_job_metadata throws exception on 404, so if we get here, consumer exists
                    metadata = focus_server_api.get_job_metadata(job_id)
                    elapsed = time.time() - start_time
                    status_history.append({
                        "time": elapsed,
                        "status": "success",
                        "message": "Consumer exists"
                    })
                    
                    # If we got here without exception, consumer exists!
                    creation_time = elapsed
                    creation_times.append(creation_time)
                    consumer_ready = True
                    logger.info(f"✅ Consumer ready after {creation_time:.3f}s")
                    break
                    
                except APIError as e:
                    elapsed = time.time() - start_time
                    error_msg = str(e)
                    status_history.append({
                        "time": elapsed,
                        "status": "error",
                        "message": error_msg
                    })
                    
                    # 404 means consumer not found yet, keep waiting
                    if "404" in error_msg or "not found" in error_msg.lower() or "Invalid job_id" in error_msg:
                        # Consumer not ready yet, continue polling
                        time.sleep(poll_interval)
                    else:
                        # Unexpected error
                        logger.warning(f"Unexpected error polling metadata: {e}")
                        time.sleep(poll_interval)
                except Exception as e:
                    elapsed = time.time() - start_time
                    logger.warning(f"Error polling metadata: {e}")
                    status_history.append({
                        "time": elapsed,
                        "status": "exception",
                        "message": str(e)
                    })
                    time.sleep(poll_interval)
            
            # Step 2.5: Stop K8s pod monitoring
            if pod_monitor_thread and pod_monitor_thread.is_alive():
                logger.info("🔍 Stopping K8s pod monitoring...")
                pod_stop_event.set()
                pod_monitor_thread.join(timeout=5)
                logger.info("✅ K8s pod monitoring stopped")
            
            # Step 3: Report results
            logger.info("=" * 80)
            logger.info("RESULTS:")
            logger.info(f"  Configure time: {configure_time:.3f}s")
            if creation_times:
                logger.info(f"  Consumer creation time: {creation_times[0]:.3f}s")
                logger.info(f"  Total time: {creation_times[0]:.3f}s")
            else:
                logger.warning(f"  Consumer NOT created within {max_wait}s")
            
            logger.info("\nStatus History:")
            for entry in status_history[:20]:  # Show first 20
                status_str = entry.get('status', 'unknown')
                message = entry.get('message', 'N/A')
                logger.info(f"  {entry['time']:.3f}s: {status_str} - {message}")
            
            # Step 3.5: Report K8s pod monitoring results
            if pod_history:
                logger.info("\n" + "=" * 80)
                logger.info("K8S POD MONITORING RESULTS:")
                logger.info("=" * 80)
                
                # Find first pod creation
                first_pod_time = None
                for snapshot in pod_history:
                    if snapshot["total_matching_pods"] > 0:
                        first_pod_time = snapshot["time"]
                        logger.info(f"  First pod detected at: {first_pod_time:.3f}s")
                        break
                
                # Show pod summary
                if first_pod_time is None:
                    logger.warning("  ⚠️  No pods detected during monitoring period")
                else:
                    logger.info(f"  Pod creation time: {first_pod_time:.3f}s")
                    logger.info(f"  Total pod snapshots: {len(pod_history)}")
                    
                    # Show all unique pods found
                    all_pods_seen = {}
                    for snapshot in pod_history:
                        for pod in snapshot["pods"]:
                            pod_name = pod["name"]
                            if pod_name not in all_pods_seen:
                                all_pods_seen[pod_name] = pod
                    
                    logger.info(f"\n  Pods found ({len(all_pods_seen)} unique):")
                    for pod_name, pod_info in all_pods_seen.items():
                        logger.info(f"    - {pod_name}")
                        logger.info(f"      Status: {pod_info.get('status')}")
                        logger.info(f"      Ready: {pod_info.get('ready')}")
                        logger.info(f"      Matched by: {pod_info.get('matched_by')}")
                        labels = pod_info.get('labels', {})
                        if labels:
                            logger.info(f"      Labels: {labels}")
                        
                        # Verify job_id match
                        pod_job_id = labels.get('job_id')
                        if pod_job_id:
                            if pod_job_id == job_id:
                                logger.info(f"      ✅ job_id matches: {pod_job_id}")
                            else:
                                logger.warning(f"      ⚠️  job_id mismatch: expected {job_id}, got {pod_job_id}")
                        else:
                            logger.warning(f"      ⚠️  No job_id label found")
                    
                    # Compare pod creation time with consumer creation time
                    if creation_times:
                        pod_to_consumer_delay = creation_times[0] - first_pod_time
                        logger.info(f"\n  Timing Analysis:")
                        logger.info(f"    Pod created: {first_pod_time:.3f}s")
                        logger.info(f"    Consumer ready: {creation_times[0]:.3f}s")
                        logger.info(f"    Delay: {pod_to_consumer_delay:.3f}s")
                        if pod_to_consumer_delay > 5.0:
                            logger.warning(f"    ⚠️  Large delay between pod creation and consumer readiness")
                
                logger.info("=" * 80)
            
            # Step 4: Verify timing
            if not consumer_ready:
                last_status = status_history[-1] if status_history else 'N/A'
                pytest.fail(f"Consumer not created within {max_wait} seconds. "
                          f"Last status: {last_status}")
            
            if creation_times and creation_times[0] > 20.0:
                logger.warning(f"⚠️  Consumer creation took {creation_times[0]:.3f}s (expected < 20s)")
            
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            pytest.fail(f"Test failed: {e}")
    
    
    @pytest.mark.skip(reason="GET /waterfall/{task_id}/{row_count} endpoint not yet implemented in backend")
    def test_metadata_vs_waterfall_endpoints(self, focus_server_api: FocusServerAPI):
        """
        Test: Compare metadata and waterfall endpoints.
        
        Objective:
            Check if metadata endpoint works before waterfall endpoint.
            This helps identify if the issue is specific to waterfall
            or affects all endpoints.
        
        Steps:
            1. Configure job
            2. Try metadata endpoint
            3. Try waterfall endpoint
            4. Compare results
        
        Expected:
            Both endpoints should work if consumer exists.
        """
        logger.info("=" * 80)
        logger.info("TEST: Metadata vs Waterfall Endpoints Comparison")
        logger.info("=" * 80)
        
        payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        config_request = ConfigureRequest(**payload)
        
        try:
            # Step 1: Configure job
            logger.info("Step 1: Configuring job...")
            response = focus_server_api.configure_streaming_job(config_request)
            job_id = response.job_id
            
            assert job_id, "Job ID must be returned from configure_streaming_job"
            logger.info(f"Job configured: {job_id}")
            
            # Step 2: Wait a bit for consumer creation
            logger.info("Step 2: Waiting 2 seconds for consumer creation...")
            time.sleep(2)
            
            # Step 3: Try metadata endpoint
            logger.info("Step 3: Trying metadata endpoint...")
            metadata_results = []
            for i in range(5):
                try:
                    # Use get_job_metadata - the correct API for job_id
                    metadata = focus_server_api.get_job_metadata(job_id)
                    metadata_results.append({
                        "attempt": i + 1,
                        "status": "success",
                        "message": "Metadata retrieved successfully"
                    })
                    logger.info(f"  Attempt {i+1}: ✅ Metadata retrieved")
                    time.sleep(0.5)
                except APIError as e:
                    error_msg = str(e)
                    metadata_results.append({
                        "attempt": i + 1,
                        "status": "error",
                        "error": error_msg
                    })
                    logger.warning(f"  Attempt {i+1}: Error - {e}")
                except Exception as e:
                    logger.warning(f"  Attempt {i+1}: Error - {e}")
                    metadata_results.append({
                        "attempt": i + 1,
                        "status": "exception",
                        "error": str(e)
                    })
            
            # Step 4: Try waterfall endpoint
            logger.info("Step 4: Trying waterfall endpoint...")
            waterfall_results = []
            for i in range(5):
                try:
                    waterfall = focus_server_api.get_waterfall(job_id, row_count=10)
                    waterfall_results.append({
                        "attempt": i + 1,
                        "status_code": waterfall.status_code,
                        "message": getattr(waterfall, 'message', None)
                    })
                    logger.info(f"  Attempt {i+1}: Status {waterfall.status_code}")
                    time.sleep(0.5)
                except Exception as e:
                    logger.warning(f"  Attempt {i+1}: Error - {e}")
                    waterfall_results.append({
                        "attempt": i + 1,
                        "status_code": None,
                        "error": str(e)
                    })
            
            # Step 5: Compare results
            logger.info("=" * 80)
            logger.info("COMPARISON RESULTS:")
            logger.info("\nMetadata Endpoint:")
            for result in metadata_results:
                status = result.get('status', 'unknown')
                msg = result.get('message', result.get('error', 'N/A'))
                logger.info(f"  Attempt {result['attempt']}: {status} - {msg}")
            
            logger.info("\nWaterfall Endpoint:")
            for result in waterfall_results:
                status_code = result.get('status_code', 'ERROR')
                msg = result.get('message', result.get('error', 'N/A'))
                logger.info(f"  Attempt {result['attempt']}: {status_code} - {msg}")
            
            # Analyze
            # Metadata: count errors (404 or APIError)
            metadata_error_count = sum(1 for r in metadata_results if r.get('status') in ['error', 'exception'])
            # Waterfall: count 404s
            waterfall_404_count = sum(1 for r in waterfall_results if r.get('status_code') == 404)
            
            logger.info("\nAnalysis:")
            logger.info(f"  Metadata errors: {metadata_error_count}/5")
            logger.info(f"  Waterfall 404 count: {waterfall_404_count}/5")
            
            if metadata_error_count == 5 and waterfall_404_count == 5:
                logger.error("❌ Both endpoints fail - Consumer NOT created")
                pytest.fail("Consumer not created - both endpoints fail")
            elif metadata_error_count < 5 and waterfall_404_count == 5:
                logger.warning("⚠️  Metadata works but waterfall doesn't - Waterfall endpoint not implemented")
            elif metadata_error_count == 5 and waterfall_404_count < 5:
                logger.warning("⚠️  Waterfall works but metadata doesn't - Unexpected")
            else:
                logger.info("✅ Both endpoints work - Consumer exists")
            
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            pytest.fail(f"Test failed: {e}")
    
    
    @pytest.mark.skip(reason="GET /waterfall/{task_id}/{row_count} endpoint not yet implemented in backend")
    def test_waterfall_status_code_handling(self, focus_server_api: FocusServerAPI):
        """
        Test: Verify waterfall endpoint status code handling.
        
        Objective:
            Test all possible status codes from waterfall endpoint
            and verify they are handled correctly.
        
        Steps:
            1. Configure job
            2. Poll waterfall endpoint
            3. Record all status codes received
            4. Verify handling is correct
        
        Expected:
            Status codes should be handled correctly:
            - 200: No data yet (consumer exists)
            - 201: Data available (consumer exists)
            - 404: Consumer not found
            - 208: Baby analyzer exited
        """
        logger.info("=" * 80)
        logger.info("TEST: Waterfall Status Code Handling")
        logger.info("=" * 80)
        
        payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        config_request = ConfigureRequest(**payload)
        
        try:
            # Step 1: Configure job
            logger.info("Step 1: Configuring job...")
            response = focus_server_api.configure_streaming_job(config_request)
            job_id = response.job_id
            
            assert job_id, "Job ID must be returned from configure_streaming_job"
            logger.info(f"Job configured: {job_id}")
            
            # Step 2: Poll waterfall endpoint and record status codes
            logger.info("Step 2: Polling waterfall endpoint...")
            max_wait = 30  # 30 seconds
            poll_interval = 1  # 1 second
            status_codes_seen = {}
            status_history = []
            
            start_time = time.time()
            while time.time() - start_time < max_wait:
                try:
                    waterfall = focus_server_api.get_waterfall(job_id, row_count=10)
                    status_code = waterfall.status_code
                    elapsed = time.time() - start_time
                    
                    # Count status codes
                    status_codes_seen[status_code] = status_codes_seen.get(status_code, 0) + 1
                    
                    # Record history
                    status_history.append({
                        "time": elapsed,
                        "status_code": status_code,
                        "message": getattr(waterfall, 'message', None),
                        "has_data": waterfall.data is not None and len(waterfall.data) > 0 if waterfall.data else False
                    })
                    
                    logger.info(f"  {elapsed:.1f}s: Status {status_code} - {getattr(waterfall, 'message', 'N/A')}")
                    
                    # If we get 200 or 201, consumer exists
                    if status_code in [200, 201]:
                        logger.info(f"✅ Consumer exists (status {status_code})")
                        break
                    
                    time.sleep(poll_interval)
                except Exception as e:
                    logger.warning(f"Error polling waterfall: {e}")
                    time.sleep(poll_interval)
            
            # Step 3: Report results
            logger.info("=" * 80)
            logger.info("STATUS CODE ANALYSIS:")
            logger.info(f"\nStatus codes seen:")
            for code, count in sorted(status_codes_seen.items()):
                logger.info(f"  {code}: {count} times")
            
            logger.info(f"\nStatus History (first 20):")
            for entry in status_history[:20]:
                logger.info(f"  {entry['time']:.1f}s: {entry['status_code']} - {entry.get('message', 'N/A')} "
                          f"(data: {entry['has_data']})")
            
            # Step 4: Verify handling
            if 404 in status_codes_seen and status_codes_seen[404] > 0:
                logger.warning(f"⚠️  Received {status_codes_seen[404]} 404 responses - Consumer not found")
            
            if 200 in status_codes_seen or 201 in status_codes_seen:
                logger.info("✅ Consumer exists - received 200 or 201")
            else:
                logger.error("❌ Consumer does not exist - only 404 received")
                pytest.fail(f"Consumer not created. Status codes seen: {status_codes_seen}")
            
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            pytest.fail(f"Test failed: {e}")

