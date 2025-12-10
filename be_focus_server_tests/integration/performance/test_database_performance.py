"""
Integration Tests - Performance: Database Performance
=====================================================

Performance tests for database query performance.

Tests Covered (Xray):
    - PZ-14797: Performance - Database Query Performance

Author: QA Automation Architect
Date: 2025-11-09
"""

import pytest
import logging
import time
from typing import Dict, Any

from src.apis.focus_server_api import FocusServerAPI
from src.core.exceptions import APIError
from src.models.focus_server_models import ConfigureRequest, ViewType

logger = logging.getLogger(__name__)


@pytest.mark.api



@pytest.mark.regression
class TestDatabasePerformance:
    """
    Test suite for database query performance.
    
    Tests covered:
        - PZ-14797: Database Query Performance
    """
    
    @pytest.mark.xray("PZ-14797")

    
    @pytest.mark.regression
    def test_database_query_performance(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-14797: Performance - Database Query Performance.
        
        Objective:
            Verify that database queries perform efficiently and
            maintain acceptable response times.
        
        Steps:
            1. Send requests that trigger database queries
            2. Measure response times
            3. Verify queries complete within acceptable time
        
        Expected:
            Database queries complete within acceptable time limits.
        """
        logger.info("=" * 80)
        logger.info("TEST: Performance - Database Query Performance (PZ-14797)")
        logger.info("=" * 80)
        
        # Note: This test measures overall API response time which includes
        # database queries. Direct database query monitoring would require
        # infrastructure access.
        
        # Test 1: GET /channels (likely queries database)
        logger.info("Testing GET /channels endpoint (database query)...")
        
        start_time = time.time()
        try:
            channels = focus_server_api.get_channels()
            elapsed_time = time.time() - start_time
            
            logger.info(f"GET /channels response time: {elapsed_time:.3f} seconds")
            
            max_query_time = 3.0  # 3 seconds
            assert elapsed_time <= max_query_time, \
                f"Channels query time {elapsed_time:.3f}s exceeds threshold {max_query_time}s"
            
            logger.info(f"✅ Channels query completed within threshold: {elapsed_time:.3f}s <= {max_query_time}s")
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Channels query failed after {elapsed_time:.3f} seconds: {e}")
            pytest.fail(f"Channels query failed: {e}")
        
        # Test 2: GET /metadata (likely queries database)
        logger.info("\nTesting GET /metadata endpoint (database query)...")
        
        start_time = time.time()
        try:
            metadata = focus_server_api.get_live_metadata_flat()
            elapsed_time = time.time() - start_time
            
            logger.info(f"GET /metadata response time: {elapsed_time:.3f} seconds")
            
            max_query_time = 2.0  # 2 seconds
            assert elapsed_time <= max_query_time, \
                f"Metadata query time {elapsed_time:.3f}s exceeds threshold {max_query_time}s"
            
            logger.info(f"✅ Metadata query completed within threshold: {elapsed_time:.3f}s <= {max_query_time}s")
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Metadata query failed after {elapsed_time:.3f} seconds: {e}")
            pytest.fail(f"Metadata query failed: {e}")
        
        # Test 3: POST /configure (may trigger database writes)
        logger.info("\nTesting POST /configure endpoint (database write)...")
        
        payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 1000},
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        config_request = ConfigureRequest(**payload)
        
        start_time = time.time()
        try:
            response = focus_server_api.configure_streaming_job(config_request)
            elapsed_time = time.time() - start_time
            
            logger.info(f"POST /configure response time: {elapsed_time:.3f} seconds")
            
            max_query_time = 5.0  # 5 seconds
            assert elapsed_time <= max_query_time, \
                f"Configure query time {elapsed_time:.3f}s exceeds threshold {max_query_time}s"
            
            logger.info(f"✅ Configure query completed within threshold: {elapsed_time:.3f}s <= {max_query_time}s")
            
            # Cleanup
            if response.job_id:
                try:
                    focus_server_api.cancel_job(response.job_id)
                except Exception as e:
                    logger.warning(f"Could not cancel job: {e}")
                    
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Configure query failed after {elapsed_time:.3f} seconds: {e}")
            pytest.fail(f"Configure query failed: {e}")
        
        logger.info("\n✅ All database query performance tests completed")
        logger.info("=" * 80)

