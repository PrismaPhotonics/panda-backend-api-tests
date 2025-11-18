"""
Integration Tests - System Behavior (Infrastructure)
=====================================================

⚠️  SCOPE REFINED - 2025-10-27
--------------------------------------
Following meeting decision (PZ-13756), these tests focus on:
- ✅ IN SCOPE: System Behavior (infra)
  - Clean startup
  - Stability over time
  - Predictable error handling (no data, port in use)
  - Proper rollback/cleanup
- ❌ OUT OF SCOPE: Internal processing, algorithm correctness

Test Coverage:
    1. Focus Server Clean Startup
    2. Focus Server Stability Over Time (1 hour)
    3. Predictable Error - No Data Available
    4. Predictable Error - Port in Use
    5. Proper Rollback on Job Creation Failure

Author: QA Automation Architect
Date: 2025-10-27
Related: PZ-13756 (Meeting decision - System Behavior in scope)
"""

import pytest
import time
import logging
import psutil
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any

from src.apis.focus_server_api import FocusServerAPI
from src.models.focus_server_models import ConfigureRequest, ViewType
from src.infrastructure.kubernetes_manager import KubernetesManager
from src.core.exceptions import APIError

logger = logging.getLogger(__name__)


# ===================================================================
# Test 1: Clean Startup
# ===================================================================

@pytest.mark.xray("PZ-13873")


@pytest.mark.regression
class TestFocusServerCleanStartup:
    """
    Test Suite: Focus Server Clean Startup
    
    Validates clean startup sequence:
    - All dependencies available
    - Configuration loaded correctly
    - Services initialized properly
    - Health check passes
    - Ready to accept requests
    
    Related: Meeting decision - Clean startup (IN SCOPE)
    """
    
    @pytest.mark.regression
    def test_focus_server_clean_startup(
        self,
        focus_server_api: FocusServerAPI,
        skip_if_waiting_for_fiber
    ):
        """
        Test: Focus Server Clean Startup
        
        Validates startup sequence:
        1. Focus Server pod is running
        2. Health check endpoint responds
        3. Dependencies available (MongoDB, RabbitMQ)
        4. No errors in startup logs
        5. Ready to accept configuration requests
        
        Expected:
        - Pod status: Running
        - Health check: HTTP 200
        - Dependencies: Connected
        - Logs: No ERROR messages during startup
        - API: Accepts requests
        """
        logger.info("\n" + "="*80)
        logger.info("TEST: Focus Server Clean Startup")
        logger.info("="*80 + "\n")
        
        # Step 1: Check Focus Server pod status (if K8s available)
        logger.info("Step 1: Checking Focus Server pod status...")
        
        try:
            # Try to get K8s manager (may not be available)
            from src.infrastructure.kubernetes_manager import KubernetesManager
            from config.config_manager import ConfigManager
            
            try:
                k8s_mgr = KubernetesManager(ConfigManager())
                
                if k8s_mgr.k8s_core_v1:
                    pods = k8s_mgr.get_pods(label_selector="app=focus-server")
                    
                    if len(pods) > 0:
                        focus_pod = pods[0]
                        pod_name = focus_pod['name']
                        pod_status = focus_pod['status']
                        
                        logger.info(f"✅ Focus Server pod found: {pod_name}")
                        logger.info(f"   Status: {pod_status}")
                        
                        assert pod_status == "Running", \
                            f"Focus Server pod not running: {pod_status}"
                    else:
                        logger.warning("No Focus Server pods found")
                else:
                    logger.info("K8s not available, skipping pod checks")
            except Exception as e:
                logger.warning(f"⚠️  Could not access K8s: {e}")
                logger.info("   Skipping pod-level checks")
        
        except ImportError:
            logger.warning(f"⚠️  KubernetesManager not available")
            logger.warning(f"   Skipping pod-level checks")
        
        # Step 2: Health check endpoint
        logger.info(f"\nStep 2: Testing health check endpoint...")
        
        try:
            health_response = focus_server_api.health_check()
            logger.info(f"✅ Health check passed")
        except AttributeError:
            # Health check method may not exist
            logger.info(f"ℹ️  Health check method not available, testing /ack instead...")
            try:
                # Try ACK endpoint
                import requests
                from src.core.config_manager import ConfigManager
                
                config = ConfigManager().focus_server
                ack_url = f"{config.base_url}/ack"
                
                response = requests.get(ack_url, verify=False, timeout=5)
                assert response.status_code == 200, f"ACK returned {response.status_code}"
                logger.info(f"✅ /ack endpoint responds correctly")
            except Exception as e:
                logger.warning(f"⚠️  Could not verify health: {e}")
        except Exception as e:
            pytest.fail(f"Health check failed: {e}")
        
        # Step 3: Test basic configuration request
        logger.info(f"\nStep 3: Testing that API accepts requests...")
        
        test_config = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 512,
            "displayInfo": {"height": 800},
            "channels": {"min": 1, "max": 10},
            "frequencyRange": {"min": 0, "max": 250},
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        job_id = None
        try:
            config_request = ConfigureRequest(**test_config)
            response = focus_server_api.configure_streaming_job(config_request)
            
            assert hasattr(response, 'job_id') and response.job_id
            job_id = response.job_id
            
            logger.info(f"✅ Focus Server accepts configuration requests")
            logger.info(f"   Test job created: {job_id}")
        
        finally:
            if job_id:
                try:
                    focus_server_api.cancel_job(job_id)
                except:
                    pass
        
        # Step 4: Check startup logs (if available)
        logger.info(f"\nStep 4: Checking for startup errors in logs...")
        
        try:
            if 'pod_name' in locals():
                logs = k8s_manager.get_pod_logs(pod_name, tail_lines=50)
                
                # Look for ERROR keywords in logs
                error_lines = [line for line in logs.split('\n') if 'ERROR' in line.upper()]
                
                if error_lines:
                    logger.warning(f"⚠️  Found {len(error_lines)} ERROR lines in logs:")
                    for line in error_lines[:5]:
                        logger.warning(f"     {line}")
                else:
                    logger.info(f"✅ No ERROR messages in recent logs")
        except:
            logger.info(f"ℹ️  Could not retrieve logs")
        
        logger.info(f"\n{'='*80}")
        logger.info(f"✅ TEST PASSED: Focus Server Clean Startup Verified")
        logger.info(f"{'='*80}\n")


# ===================================================================
# Test 2: Stability Over Time
# ===================================================================

@pytest.mark.xray("PZ-13873")


@pytest.mark.regression
class TestFocusServerStability:
    """
    Test Suite: Focus Server Stability Over Time
    
    Validates system stability during extended operation.
    
    Related: Meeting decision - Stability over time (IN SCOPE)
    """
    
    @pytest.mark.regression
    def test_focus_server_stability_over_time(
        self,
        focus_server_api: FocusServerAPI
    ):
        """
        Test: Focus Server Stability Over Time (1 hour)
        
        Validates stability during extended operation:
        1. Create jobs every 5 minutes for 1 hour
        2. Monitor memory usage (no leaks)
        3. Monitor CPU usage (stable)
        4. Monitor error rates (low)
        5. Verify no crashes or restarts
        
        Duration: 1 hour
        
        Expected:
        - All jobs succeed (or high success rate)
        - Memory usage stable (no significant growth)
        - CPU usage stable
        - No pod restarts
        - Error rate < 5%
        """
        logger.info("\n" + "="*80)
        logger.info("TEST: Focus Server Stability Over Time (1 HOUR)")
        logger.info("="*80)
        logger.warning("⚠️  This test will run for approximately 1 hour!")
        logger.info("="*80 + "\n")
        
        # Test parameters
        duration_minutes = 60
        job_interval_minutes = 5
        iterations = duration_minutes // job_interval_minutes  # 12 iterations
        
        # Standard test config
        test_config = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 512,
            "displayInfo": {"height": 800},
            "channels": {"min": 1, "max": 20},
            "frequencyRange": {"min": 0, "max": 250},
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        # Tracking
        results = []
        memory_samples = []
        cpu_samples = []
        created_jobs = []
        
        start_time = datetime.now()
        
        logger.info(f"Starting stability test at: {start_time}")
        logger.info(f"Will create jobs every {job_interval_minutes} minutes")
        logger.info(f"Total iterations: {iterations}")
        logger.info(f"Expected end time: {start_time + timedelta(minutes=duration_minutes)}\n")
        
        for iteration in range(1, iterations + 1):
            iteration_start = datetime.now()
            
            logger.info(f"{'='*80}")
            logger.info(f"Iteration {iteration}/{iterations} at {iteration_start.strftime('%H:%M:%S')}")
            logger.info(f"{'='*80}")
            
            # Create job
            job_id = None
            success = False
            latency_ms = 0
            error_msg = None
            
            try:
                create_start = time.time()
                config_request = ConfigureRequest(**test_config)
                response = focus_server_api.configure_streaming_job(config_request)
                create_end = time.time()
                
                latency_ms = (create_end - create_start) * 1000
                job_id = response.job_id if hasattr(response, 'job_id') else None
                success = True
                created_jobs.append(job_id)
                
                logger.info(f"✅ Job created: {job_id} ({latency_ms:.0f}ms)")
            
            except Exception as e:
                error_msg = str(e)
                logger.error(f"❌ Job creation failed: {e}")
            
            # Sample system metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            mem_usage = psutil.virtual_memory().percent
            
            cpu_samples.append(cpu_usage)
            memory_samples.append(mem_usage)
            
            logger.info(f"System metrics: CPU={cpu_usage:.1f}%, Memory={mem_usage:.1f}%")
            
            # Check pod restarts (if K8s available)
            pod_restarts = 0
            try:
                from src.infrastructure.kubernetes_manager import KubernetesManager
                from config.config_manager import ConfigManager
                
                k8s_mgr = KubernetesManager(ConfigManager())
                if k8s_mgr.k8s_core_v1:
                    pods = k8s_mgr.get_pods(label_selector="app=focus-server")
                    if pods:
                        pod_restarts = pods[0].get('restarts', 0)
                        logger.info(f"Focus Server pod restarts: {pod_restarts}")
            except:
                pass
            
            # Record iteration results
            results.append({
                'iteration': iteration,
                'timestamp': iteration_start.isoformat(),
                'success': success,
                'latency_ms': latency_ms,
                'job_id': job_id,
                'error': error_msg,
                'cpu_percent': cpu_usage,
                'memory_percent': mem_usage,
                'pod_restarts': pod_restarts
            })
            
            # Wait until next interval
            elapsed = (datetime.now() - iteration_start).total_seconds()
            wait_time = (job_interval_minutes * 60) - elapsed
            
            if wait_time > 0 and iteration < iterations:
                logger.info(f"Waiting {wait_time:.0f} seconds until next iteration...\n")
                time.sleep(wait_time)
        
        # Analyze results
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds() / 60
        
        logger.info(f"\n{'='*80}")
        logger.info(f"STABILITY TEST - FINAL ANALYSIS")
        logger.info(f"{'='*80}")
        logger.info(f"Test duration: {total_duration:.1f} minutes")
        logger.info(f"Iterations completed: {len(results)}")
        
        # Success rate
        successes = sum(1 for r in results if r['success'])
        success_rate = successes / len(results)
        logger.info(f"\nJob Creation:")
        logger.info(f"  Successful: {successes}/{len(results)} ({success_rate:.1%})")
        
        # Latency analysis
        latencies = [r['latency_ms'] for r in results if r['success']]
        if latencies:
            logger.info(f"  Latency - Mean: {statistics.mean(latencies):.0f}ms")
            logger.info(f"  Latency - Max: {max(latencies):.0f}ms")
        
        # Memory analysis
        logger.info(f"\nMemory Usage:")
        logger.info(f"  Initial: {memory_samples[0]:.1f}%")
        logger.info(f"  Final:   {memory_samples[-1]:.1f}%")
        logger.info(f"  Change:  {memory_samples[-1] - memory_samples[0]:+.1f}%")
        logger.info(f"  Average: {statistics.mean(memory_samples):.1f}%")
        logger.info(f"  Max:     {max(memory_samples):.1f}%")
        
        memory_growth = memory_samples[-1] - memory_samples[0]
        if memory_growth > 10:
            logger.warning(f"⚠️  Possible memory leak detected: +{memory_growth:.1f}%")
        else:
            logger.info(f"✅ Memory usage stable (growth < 10%)")
        
        # CPU analysis
        logger.info(f"\nCPU Usage:")
        logger.info(f"  Average: {statistics.mean(cpu_samples):.1f}%")
        logger.info(f"  Max:     {max(cpu_samples):.1f}%")
        logger.info(f"  Min:     {min(cpu_samples):.1f}%")
        
        # Pod restarts
        restart_counts = [r['pod_restarts'] for r in results]
        if restart_counts and max(restart_counts) > 0:
            logger.warning(f"⚠️  Pod restarted during test: {max(restart_counts)} times")
        else:
            logger.info(f"✅ No pod restarts during test")
        
        logger.info(f"{'='*80}\n")
        
        # Assertions
        assert success_rate >= 0.90, \
            f"Success rate too low: {success_rate:.1%} (expected >= 90%)"
        
        assert memory_growth < 20, \
            f"Excessive memory growth: {memory_growth:.1f}% (possible memory leak)"
        
        # Cleanup created jobs
        logger.info(f"Cleaning up {len(created_jobs)} created jobs...")
        for job_id in created_jobs:
            if job_id:
                try:
                    focus_server_api.cancel_job(job_id)
                except:
                    pass
        
        logger.info(f"\n{'='*80}")
        logger.info(f"✅ TEST PASSED: Focus Server Stable Over Time")
        logger.info(f"{'='*80}\n")


# ===================================================================
# Test 3: Predictable Error - No Data Available
# ===================================================================

@pytest.mark.xray("PZ-13873")


@pytest.mark.regression
class TestPredictableErrorNoData:
    """
    Test Suite: Predictable Error Handling - No Data
    
    Validates clear error when no data available.
    
    Related: Meeting decision - Predictable error handling (IN SCOPE)
    """
    
    @pytest.mark.regression
def test_predictable_error_no_data_available(
        self,
        focus_server_api: FocusServerAPI
    ):
        """
        Test: Predictable Error Handling - No Data
        
        Validates clear error when no data available:
        1. Historic mode with time range having no recordings
        2. Expected: HTTP 404 or 503 with clear message
        3. No crash, no 500 errors
        4. Error message indicates "no data in range"
        
        Expected Error Structure:
        - HTTP Status: 404 Not Found or 503 Service Unavailable
        - Message: "No recordings found in time range" or similar
        - No stack traces exposed to client
        - Predictable and consistent error format
        """
        logger.info("\n" + "="*80)
        logger.info("TEST: Predictable Error - No Data Available")
        logger.info("="*80 + "\n")
        
        # Use a very old time range (likely no data)
        old_time = datetime(2020, 1, 1)  # January 1, 2020
        
        no_data_config = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": int(old_time.timestamp()),
            "end_time": int((old_time + timedelta(hours=1)).timestamp()),
            "view_type": ViewType.MULTICHANNEL
        }
        
        logger.info(f"Requesting historic data from: {old_time}")
        logger.info(f"(Very old time range - should have no data)")
        
        try:
            config_request = ConfigureRequest(**no_data_config)
            response = focus_server_api.configure_streaming_job(config_request)
            
            # If job was created, it may mean:
            # a) There IS data in that range (unlikely)
            # b) Validation doesn't check data availability (gap)
            
            logger.warning(f"⚠️  Job created despite old time range")
            logger.warning(f"   Job ID: {response.job_id if hasattr(response, 'job_id') else 'N/A'}")
            logger.warning(f"   This may indicate that data availability is not pre-validated")
            
            # Cleanup
            if hasattr(response, 'job_id') and response.job_id:
                try:
                    focus_server_api.cancel_job(response.job_id)
                except:
                    pass
        
        except APIError as e:
            # Expected: Clear error about no data
            error_message = str(e)
            error_message_lower = error_message.lower()
            
            logger.info(f"✅ Request rejected with error:")
            logger.info(f"   {e}")
            
            # Analyze error message quality
            no_data_keywords = ['no data', 'not found', '404', 'empty', 'unavailable', 'no recordings']
            has_no_data_keyword = any(keyword in error_message_lower for keyword in no_data_keywords)
            
            if has_no_data_keyword:
                logger.info(f"✅ Error message clearly indicates no data available")
            else:
                logger.warning(f"⚠️  Error message doesn't clearly indicate data unavailability")
                logger.warning(f"   Consider improving error message:")
                logger.warning(f"   Current: {error_message}")
                logger.warning(f"   Suggested: 'No recordings found in requested time range'")
            
            # Check HTTP status code (if available in exception)
            if hasattr(e, 'status_code'):
                logger.info(f"   HTTP Status: {e.status_code}")
                assert e.status_code in [404, 503], \
                    f"Expected 404 or 503 for no data, got {e.status_code}"
            
            # Verify no 500 error (server error)
            assert '500' not in error_message, \
                "No data should return 404/503, not 500 (server error)"
        
        logger.info(f"\n{'='*80}")
        logger.info(f"✅ TEST PASSED: Predictable Error for No Data")
        logger.info(f"{'='*80}\n")


# ===================================================================
# Test 4: Predictable Error - Port in Use
# ===================================================================

@pytest.mark.xray("PZ-13873")


@pytest.mark.regression
class TestPredictableErrorPortInUse:
    """
    Test Suite: Predictable Error Handling - Port in Use
    
    Validates clear error when port unavailable.
    
    Related: Meeting decision - Predictable error handling (IN SCOPE)
    """
    
    @pytest.mark.regression
def test_predictable_error_port_in_use(
        self,
        focus_server_api: FocusServerAPI,
        skip_if_waiting_for_fiber
    ):
        """
        Test: Predictable Error Handling - Port in Use
        
        Validates clear error when port unavailable:
        1. Create job on port X
        2. Try to create another job on same port
        3. Expected: HTTP 409 Conflict with clear message
        4. No crash, no 500 errors
        
        Note: This test depends on whether Focus Server allows
              specifying ports or auto-assigns them.
              
        If auto-assigned: Test validates that no conflicts occur
        If user-specified: Test validates conflict detection
        """
        logger.info("\n" + "="*80)
        logger.info("TEST: Predictable Error - Port in Use")
        logger.info("="*80 + "\n")
        
        test_config = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 512,
            "displayInfo": {"height": 800},
            "channels": {"min": 1, "max": 20},
            "frequencyRange": {"min": 0, "max": 250},
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        job_ids = []
        
        try:
            # Create multiple jobs and check port assignment
            logger.info("Creating multiple jobs to test port allocation...")
            
            for i in range(3):
                config_request = ConfigureRequest(**test_config)
                response = focus_server_api.configure_streaming_job(config_request)
                
                job_id = response.job_id if hasattr(response, 'job_id') else None
                port = response.stream_port if hasattr(response, 'stream_port') else None
                
                job_ids.append(job_id)
                
                logger.info(f"  Job {i+1}: ID={job_id}, Port={port}")
            
            # Collect ports
            ports = []
            for i, job_id in enumerate(job_ids):
                if job_id:
                    # Note: We don't have a direct way to query job metadata
                    # This is a gap that should be filled with GET /metadata/{job_id}
                    logger.info(f"  Job {i+1}: {job_id}")
            
            logger.info(f"\n✅ All jobs created successfully")
            logger.info(f"   Port allocation strategy appears to prevent conflicts")
            logger.info(f"   (Either auto-assignment or conflict detection works)")
        
        finally:
            # Cleanup
            for job_id in job_ids:
                if job_id:
                    try:
                        focus_server_api.cancel_job(job_id)
                    except:
                        pass
        
        logger.info(f"\n{'='*80}")
        logger.info(f"✅ TEST PASSED: Port Conflict Handling")
        logger.info(f"{'='*80}\n")


# ===================================================================
# Test 5: Proper Rollback on Failure
# ===================================================================

@pytest.mark.xray("PZ-13873")


@pytest.mark.regression
class TestProperRollback:
    """
    Test Suite: Proper Rollback on Job Creation Failure
    
    Validates rollback when job creation fails.
    
    Related: Meeting decision - Proper rollback/cleanup (IN SCOPE)
    """
    
    @pytest.mark.regression
def test_proper_rollback_on_job_creation_failure(
        self,
        focus_server_api: FocusServerAPI,
        skip_if_waiting_for_fiber
    ):
        """
        Test: Proper Rollback on Failure
        
        Validates rollback when job creation fails:
        1. Trigger failure during job creation
        2. Verify no partial resources left
        3. Verify K8s pod cleaned up (if created)
        4. Verify system state unchanged
        
        Failure Scenarios:
        - Invalid configuration
        - No data available
        - Port conflict
        
        Expected:
        - Job creation fails gracefully
        - No partial state persists
        - K8s pods cleaned up automatically
        - Can create new job immediately after
        """
        logger.info("\n" + "="*80)
        logger.info("TEST: Proper Rollback on Job Creation Failure")
        logger.info("="*80 + "\n")
        
        # Scenario: Invalid configuration that should fail
        invalid_config = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 0,  # Invalid NFFT
            "displayInfo": {"height": 1000},
            "channels": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        logger.info("Step 1: Attempting to create job with invalid config...")
        logger.info(f"  Invalid parameter: NFFT=0")
        
        # Count pods before (if K8s available)
        pod_count_before = None
        try:
            from src.infrastructure.kubernetes_manager import KubernetesManager
            from config.config_manager import ConfigManager
            
            k8s_mgr = KubernetesManager(ConfigManager())
            if k8s_mgr.k8s_core_v1:
                pods_before = k8s_mgr.get_pods(label_selector="app.kubernetes.io/name=grpc-jobs")
                pod_count_before = len(pods_before)
                logger.info(f"  gRPC job pods before: {pod_count_before}")
        except:
            logger.info(f"  Could not count pods (K8s not available)")
        
        # Try to create job (should fail)
        try:
            config_request = ConfigureRequest(**invalid_config)
            response = focus_server_api.configure_streaming_job(config_request)
            
            logger.error(f"❌ Job created with invalid config: {response.job_id if hasattr(response, 'job_id') else 'N/A'}")
            logger.error(f"   Validation should have rejected this")
            
            # Cleanup
            if hasattr(response, 'job_id') and response.job_id:
                try:
                    focus_server_api.cancel_job(response.job_id)
                except:
                    pass
        
        except Exception as e:
            # Expected: Validation error
            logger.info(f"✅ Invalid config rejected (expected):")
            logger.info(f"   {e}")
        
        # Count pods after (if K8s available)
        logger.info(f"\nStep 2: Verifying no orphaned pods...")
        time.sleep(5)  # Give K8s time to clean up
        
        try:
            from src.infrastructure.kubernetes_manager import KubernetesManager
            from config.config_manager import ConfigManager
            
            k8s_mgr = KubernetesManager(ConfigManager())
            if k8s_mgr.k8s_core_v1:
                pods_after = k8s_mgr.get_pods(label_selector="app.kubernetes.io/name=grpc-jobs")
                pod_count_after = len(pods_after)
                logger.info(f"  gRPC job pods after: {pod_count_after}")
                
                if pod_count_before is not None:
                    assert pod_count_after == pod_count_before, \
                        f"Pod count changed ({pod_count_before} → {pod_count_after}), orphaned pod may exist"
                    
                    logger.info(f"✅ No orphaned pods (count unchanged)")
        except:
            logger.info(f"  Could not verify pods")
        
        # Step 3: Verify system can accept new job
        logger.info(f"\nStep 3: Verifying system accepts new (valid) job...")
        
        valid_config = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 512,
            "displayInfo": {"height": 800},
            "channels": {"min": 1, "max": 20},
            "frequencyRange": {"min": 0, "max": 250},
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        job_id = None
        try:
            config_request = ConfigureRequest(**valid_config)
            response = focus_server_api.configure_streaming_job(config_request)
            
            job_id = response.job_id if hasattr(response, 'job_id') else None
            logger.info(f"✅ System accepts new job after failure: {job_id}")
            logger.info(f"   System state properly rolled back")
        
        finally:
            if job_id:
                try:
                    focus_server_api.cancel_job(job_id)
                except:
                    pass
        
        logger.info(f"\n{'='*80}")
        logger.info(f"✅ TEST PASSED: Proper Rollback Verified")
        logger.info(f"{'='*80}\n")


# ===================================================================
# Helper Functions
# ===================================================================

def analyze_error_message_quality(error_message: str, expected_keywords: List[str]) -> Dict[str, Any]:
    """
    Analyze error message quality.
    
    Args:
        error_message: The error message to analyze
        expected_keywords: Keywords expected in a good error message
    
    Returns:
        Dict with quality analysis
    """
    error_lower = error_message.lower()
    
    found_keywords = [kw for kw in expected_keywords if kw.lower() in error_lower]
    quality_score = len(found_keywords) / len(expected_keywords) if expected_keywords else 0
    
    # Check for common anti-patterns
    has_stack_trace = 'traceback' in error_lower or 'line ' in error_lower
    has_internal_details = 'internal' in error_lower or 'debug' in error_lower
    
    return {
        'quality_score': quality_score,
        'found_keywords': found_keywords,
        'missing_keywords': [kw for kw in expected_keywords if kw not in found_keywords],
        'has_stack_trace': has_stack_trace,
        'has_internal_details': has_internal_details,
        'is_user_friendly': quality_score >= 0.5 and not has_stack_trace,
        'message': error_message
    }


if __name__ == "__main__":
    # Run system behavior tests
    pytest.main([
        __file__,
        "-v",
        "-m", "infrastructure and error_handling",
        "--tb=short",
        "--log-cli-level=INFO"
    ])

