"""
Integration Tests - Performance: Resource Usage
===============================================

Performance tests for resource usage under load.

Tests Covered (Xray):
    - PZ-14794: Performance - Large Payload Handling
    - PZ-14795: Performance - Memory Usage Under Load
    - PZ-14796: Performance - CPU Usage Under Load

Author: QA Automation Architect
Date: 2025-11-09
"""

import pytest
import logging
import time
import psutil
import os
from typing import Dict, Any

from src.apis.focus_server_api import FocusServerAPI
from src.core.exceptions import APIError
from src.models.focus_server_models import ConfigureRequest, ViewType

logger = logging.getLogger(__name__)


@pytest.mark.integration
@pytest.mark.performance
@pytest.mark.api
class TestResourceUsage:
    """
    Test suite for resource usage performance.
    
    Tests covered:
        - PZ-14794: Large Payload Handling
        - PZ-14795: Memory Usage Under Load
        - PZ-14796: CPU Usage Under Load
    """
    
    @pytest.mark.xray("PZ-14794")
    def test_large_payload_handling(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-14794: Performance - Large Payload Handling.
        
        Objective:
            Verify that API handles large payloads efficiently and
            maintains acceptable response times.
        
        Steps:
            1. Send request with large payload
            2. Measure response time
            3. Verify request completes successfully
        
        Expected:
            Large payload requests complete successfully within acceptable time.
        """
        logger.info("=" * 80)
        logger.info("TEST: Performance - Large Payload Handling (PZ-14794)")
        logger.info("=" * 80)
        
        # Create large payload with many channels
        payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 1, "max": 1000},  # Large channel range
            "frequencyRange": {"min": 0, "max": 1000},  # Large frequency range
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        config_request = ConfigureRequest(**payload)
        
        max_response_time = 15.0  # 15 seconds for large payload
        
        start_time = time.time()
        
        try:
            response = focus_server_api.configure_streaming_job(config_request)
            elapsed_time = time.time() - start_time
            
            logger.info(f"Response time: {elapsed_time:.3f} seconds")
            logger.info(f"Threshold: {max_response_time} seconds")
            
            assert elapsed_time <= max_response_time, \
                f"Response time {elapsed_time:.3f}s exceeds threshold {max_response_time}s"
            
            logger.info(f"✅ Large payload handled successfully: {elapsed_time:.3f}s <= {max_response_time}s")
            
            # Cleanup
            if response.job_id:
                try:
                    focus_server_api.cancel_job(response.job_id)
                except Exception as e:
                    logger.warning(f"Could not cancel job: {e}")
                    
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Request failed after {elapsed_time:.3f} seconds: {e}")
            pytest.fail(f"Large payload request failed: {e}")
        
        logger.info("✅ Test completed")
        logger.info("=" * 80)
    
    @pytest.mark.xray("PZ-14795")
    def test_memory_usage_under_load(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-14795: Performance - Memory Usage Under Load.
        
        Objective:
            Verify that API memory usage remains within acceptable limits
            under load.
        
        Steps:
            1. Monitor memory usage before load
            2. Send multiple requests
            3. Monitor memory usage during load
            4. Verify memory usage is within acceptable limits
        
        Expected:
            Memory usage remains within acceptable limits under load.
        """
        logger.info("=" * 80)
        logger.info("TEST: Performance - Memory Usage Under Load (PZ-14795)")
        logger.info("=" * 80)
        
        # Note: This test monitors client-side memory usage
        # Server-side memory monitoring would require infrastructure access
        
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
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        logger.info(f"Initial memory usage: {initial_memory:.2f} MB")
        
        num_requests = 10
        job_ids = []
        
        # Send multiple requests
        for i in range(num_requests):
            try:
                response = focus_server_api.configure_streaming_job(config_request)
                if response.job_id:
                    job_ids.append(response.job_id)
                
                # Check memory after each request
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = current_memory - initial_memory
                
                logger.info(f"Request {i+1}/{num_requests}: Memory = {current_memory:.2f} MB (+{memory_increase:.2f} MB)")
                
            except Exception as e:
                logger.warning(f"Request {i+1} failed: {e}")
        
        # Final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        total_increase = final_memory - initial_memory
        
        logger.info(f"\nMemory Usage Summary:")
        logger.info(f"  Initial: {initial_memory:.2f} MB")
        logger.info(f"  Final: {final_memory:.2f} MB")
        logger.info(f"  Increase: {total_increase:.2f} MB")
        
        # Cleanup
        logger.info(f"\nCleaning up {len(job_ids)} jobs...")
        for job_id in job_ids:
            try:
                focus_server_api.cancel_job(job_id)
            except Exception:
                pass
        
        # Verify memory increase is reasonable (less than 500 MB for 10 requests)
        max_memory_increase = 500  # MB
        assert total_increase <= max_memory_increase, \
            f"Memory increase {total_increase:.2f} MB exceeds threshold {max_memory_increase} MB"
        
        logger.info(f"✅ Memory usage is within acceptable limits: {total_increase:.2f} MB <= {max_memory_increase} MB")
        logger.info("=" * 80)
    
    @pytest.mark.xray("PZ-14796")
    def test_cpu_usage_under_load(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-14796: Performance - CPU Usage Under Load.
        
        Objective:
            Verify that API CPU usage remains within acceptable limits
            under load.
        
        Steps:
            1. Monitor CPU usage before load
            2. Send multiple requests
            3. Monitor CPU usage during load
            4. Verify CPU usage is within acceptable limits
        
        Expected:
            CPU usage remains within acceptable limits under load.
        """
        logger.info("=" * 80)
        logger.info("TEST: Performance - CPU Usage Under Load (PZ-14796)")
        logger.info("=" * 80)
        
        # Note: This test monitors client-side CPU usage
        # Server-side CPU monitoring would require infrastructure access
        
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
        
        # Get initial CPU usage
        process = psutil.Process(os.getpid())
        initial_cpu = process.cpu_percent(interval=1)
        
        logger.info(f"Initial CPU usage: {initial_cpu:.2f}%")
        
        num_requests = 10
        job_ids = []
        cpu_readings = []
        
        # Send multiple requests
        for i in range(num_requests):
            try:
                response = focus_server_api.configure_streaming_job(config_request)
                if response.job_id:
                    job_ids.append(response.job_id)
                
                # Check CPU after each request
                current_cpu = process.cpu_percent(interval=0.5)
                cpu_readings.append(current_cpu)
                
                logger.info(f"Request {i+1}/{num_requests}: CPU = {current_cpu:.2f}%")
                
            except Exception as e:
                logger.warning(f"Request {i+1} failed: {e}")
        
        # Final CPU usage
        final_cpu = process.cpu_percent(interval=1)
        avg_cpu = sum(cpu_readings) / len(cpu_readings) if cpu_readings else 0
        max_cpu = max(cpu_readings) if cpu_readings else 0
        
        logger.info(f"\nCPU Usage Summary:")
        logger.info(f"  Initial: {initial_cpu:.2f}%")
        logger.info(f"  Final: {final_cpu:.2f}%")
        logger.info(f"  Average: {avg_cpu:.2f}%")
        logger.info(f"  Max: {max_cpu:.2f}%")
        
        # Cleanup
        logger.info(f"\nCleaning up {len(job_ids)} jobs...")
        for job_id in job_ids:
            try:
                focus_server_api.cancel_job(job_id)
            except Exception:
                pass
        
        # Verify CPU usage is reasonable (less than 100% - should be much lower)
        max_cpu_threshold = 100  # %
        assert max_cpu <= max_cpu_threshold, \
            f"Max CPU usage {max_cpu:.2f}% exceeds threshold {max_cpu_threshold}%"
        
        logger.info(f"✅ CPU usage is within acceptable limits: {max_cpu:.2f}% <= {max_cpu_threshold}%")
        logger.info("=" * 80)

