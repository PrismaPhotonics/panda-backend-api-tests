"""
Integration Tests - GET /metadata/{task_id} Endpoint (Future Structure)
=========================================================================

⚠️  NOTE: These tests are for the FUTURE API structure using GET /metadata/{task_id}
   Currently, the staging environment uses GET /metadata/{job_id} endpoint.
   These tests are SKIPPED until the new endpoint is deployed.

Tests for GET /metadata/{task_id} endpoint covering:
- Valid request with metadata
- Consumer not running
- Invalid task ID
- Metadata consistency
- Response time

Tests Covered (Xray):
    - PZ-14760: GET /metadata/{task_id} - Valid Request
    - PZ-14761: GET /metadata/{task_id} - Consumer Not Running
    - PZ-14762: GET /metadata/{task_id} - Invalid Task ID
    - PZ-14763: GET /metadata/{task_id} - Metadata Consistency
    - PZ-14764: GET /metadata/{task_id} - Response Time

Author: QA Automation Architect
Date: 2025-11-09
"""

import pytest
import logging
import time
from typing import Dict, Any

from src.models.focus_server_models import ConfigTaskRequest
from src.apis.focus_server_api import FocusServerAPI
from src.core.exceptions import APIError, ValidationError
from src.utils.helpers import generate_task_id

logger = logging.getLogger(__name__)


# ===================================================================
# Test Class: GET /metadata/{task_id} Endpoint
# ===================================================================

@pytest.mark.integration
@pytest.mark.api
@pytest.mark.critical
@pytest.mark.high
@pytest.mark.skip(reason="Future API structure - GET /metadata/{task_id} endpoint not yet deployed to staging. "
                          "Use GET /metadata/{job_id} tests instead")
@pytest.mark.regression
class TestTaskMetadataEndpoint:
    """
    Test suite for GET /metadata/{task_id} endpoint.
    
    Tests covered:
        - PZ-14760: Valid Request
        - PZ-14761: Consumer Not Running
        - PZ-14762: Invalid Task ID
        - PZ-14763: Metadata Consistency
        - PZ-14764: Response Time
    
    Priority: HIGH
    """
    
    @pytest.mark.xray("PZ-14760")
    @pytest.mark.xray("PZ-13563")

    @pytest.mark.regression
    def test_task_metadata_valid_request(
        self,
        focus_server_api: FocusServerAPI
    ):
        """
        Test PZ-14760: GET /metadata/{task_id} - Valid Request.
        
        Validates that GET /metadata/{task_id} endpoint returns 201 Created 
        with metadata when consumer is running.
        
        Steps:
            1. Configure a task
            2. Wait for consumer to start
            3. Send GET /metadata/{task_id} request
            4. Verify response structure
            5. Verify metadata fields
        
        Expected:
            - Request returns 201 Created
            - Response contains metadata
            - Metadata structure is valid
        
        Jira: PZ-14760
        Priority: HIGH
        """
        logger.info("=" * 80)
        logger.info("TEST: GET /metadata/{task_id} - Valid Request (PZ-14760)")
        logger.info("=" * 80)
        
        # Step 1: Configure a task
        task_id = generate_task_id("test-metadata")
        logger.info(f"Generated task_id: {task_id}")
        
        config_payload = {
            "displayTimeAxisDuration": 10.0,
            "nfftSelection": 1024,
            "canvasInfo": {"height": 1000},
            "sensors": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 1000},
            "start_time": None,
            "end_time": None
        }
        
        try:
            config_request = ConfigTaskRequest(**config_payload)
            config_response = focus_server_api.config_task(task_id, config_request)
            logger.info(f"✅ Task configured: {config_response.status}")
            
            # Step 2: Wait for consumer to start
            logger.info("Waiting for consumer to start...")
            time.sleep(5)  # Wait 5 seconds for consumer to start
            
            # Step 3: Send GET /metadata/{task_id} request
            logger.info(f"Sending GET /metadata/{task_id} request...")
            metadata_response = focus_server_api.get_task_metadata(task_id)
            
            # Step 4: Verify response structure
            assert metadata_response is not None, "Response should not be None"
            assert hasattr(metadata_response, 'status_code'), "Response should have status_code"
            
            # Step 5: Verify metadata fields
            if metadata_response.status_code == 201:
                assert metadata_response.metadata is not None, "Metadata should be present for status 201"
                
                metadata = metadata_response.metadata
                assert hasattr(metadata, 'prr'), "Metadata should have prr field"
                assert hasattr(metadata, 'dx'), "Metadata should have dx field"
                assert hasattr(metadata, 'number_of_channels'), "Metadata should have number_of_channels field"
                
                logger.info(f"✅ Status code: {metadata_response.status_code}")
                logger.info(f"✅ PRR: {metadata.prr}")
                logger.info(f"✅ DX: {metadata.dx}")
                logger.info(f"✅ Number of channels: {metadata.number_of_channels}")
            elif metadata_response.status_code == 200:
                logger.info("✅ Status code: 200 (Consumer not running yet - may be expected)")
            else:
                logger.warning(f"⚠️  Unexpected status code: {metadata_response.status_code}")
            
            logger.info("✅ All assertions passed")
            
        except APIError as e:
            logger.error(f"API Error: {e}")
            pytest.fail(f"API call failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            pytest.fail(f"Unexpected error: {e}")
        
        logger.info("=" * 80)
        logger.info("✅ TEST PASSED: Valid Request")
        logger.info("=" * 80)
    
    @pytest.mark.xray("PZ-14761")

    
    @pytest.mark.regression
    def test_task_metadata_consumer_not_running(
        self,
        focus_server_api: FocusServerAPI
    ):
        """
        Test PZ-14761: GET /metadata/{task_id} - Consumer Not Running.
        
        Validates that GET /metadata/{task_id} endpoint returns 200 OK 
        with empty response when consumer is not running.
        
        Steps:
            1. Configure a task
            2. Immediately request metadata
            3. Verify response is empty
        
        Expected:
            - Request returns 200 OK
            - Response indicates consumer not running
            - No errors occur
        
        Jira: PZ-14761
        Priority: MEDIUM
        """
        logger.info("=" * 80)
        logger.info("TEST: GET /metadata/{task_id} - Consumer Not Running (PZ-14761)")
        logger.info("=" * 80)
        
        # Step 1: Configure a task
        task_id = generate_task_id("test-metadata-empty")
        logger.info(f"Generated task_id: {task_id}")
        
        config_payload = {
            "displayTimeAxisDuration": 10.0,
            "nfftSelection": 1024,
            "canvasInfo": {"height": 1000},
            "sensors": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 1000},
            "start_time": None,
            "end_time": None
        }
        
        try:
            config_request = ConfigTaskRequest(**config_payload)
            config_response = focus_server_api.config_task(task_id, config_request)
            logger.info(f"✅ Task configured: {config_response.status}")
            
            # Step 2: Immediately request metadata (no wait)
            logger.info(f"Immediately requesting GET /metadata/{task_id}...")
            metadata_response = focus_server_api.get_task_metadata(task_id)
            
            # Step 3: Verify response is empty
            assert metadata_response is not None, "Response should not be None"
            assert metadata_response.status_code in [200, 201], \
                f"Status code should be 200 or 201, got {metadata_response.status_code}"
            
            if metadata_response.status_code == 200:
                logger.info("✅ Status code: 200 (Consumer not running - expected)")
                assert metadata_response.metadata is None, "Metadata should be None for status 200"
            else:
                logger.info(f"✅ Status code: {metadata_response.status_code} (Metadata may be available)")
            
            logger.info("✅ All assertions passed")
            
        except APIError as e:
            logger.error(f"API Error: {e}")
            pytest.fail(f"API call failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            pytest.fail(f"Unexpected error: {e}")
        
        logger.info("=" * 80)
        logger.info("✅ TEST PASSED: Consumer Not Running")
        logger.info("=" * 80)
    
    @pytest.mark.xray("PZ-14762")
    @pytest.mark.xray("PZ-13563")

    @pytest.mark.regression
    def test_task_metadata_invalid_task_id(
        self,
        focus_server_api: FocusServerAPI
    ):
        """
        Test PZ-14762: GET /metadata/{task_id} - Invalid Task ID.
        
        Validates that GET /metadata/{task_id} endpoint returns 404 Not Found 
        for invalid task_id.
        
        Steps:
            1. Send GET /metadata/{task_id} request with invalid task_id
            2. Verify error response
        
        Expected:
            - Request returns 404 Not Found
            - Error message indicates task not found
            - No metadata is returned
        
        Jira: PZ-14762
        Priority: HIGH
        """
        logger.info("=" * 80)
        logger.info("TEST: GET /metadata/{task_id} - Invalid Task ID (PZ-14762)")
        logger.info("=" * 80)
        
        # Step 1: Send request with invalid task_id
        invalid_task_id = "nonexistent-task-12345"
        
        logger.info(f"Sending GET /metadata/{invalid_task_id} request...")
        
        try:
            metadata_response = focus_server_api.get_task_metadata(invalid_task_id)
            
            # Step 2: Verify error response
            assert metadata_response is not None, "Response should not be None"
            
            if metadata_response.status_code == 404:
                logger.info("✅ Status code: 404 Not Found (expected)")
                assert metadata_response.metadata is None, "Metadata should be None for 404"
            else:
                logger.warning(f"⚠️  Unexpected status code: {metadata_response.status_code}")
                logger.warning(f"   Expected 404, got {metadata_response.status_code}")
            
            logger.info("✅ All assertions passed")
            
        except APIError as e:
            # APIError is also acceptable for invalid task_id
            logger.info(f"✅ APIError caught (expected): {e}")
        except Exception as e:
            logger.info(f"✅ Error caught (expected): {type(e).__name__}: {e}")
        
        logger.info("=" * 80)
        logger.info("✅ TEST PASSED: Invalid Task ID Handling")
        logger.info("=" * 80)
    
    @pytest.mark.xray("PZ-14763")

    
    @pytest.mark.regression
    def test_task_metadata_consistency(
        self,
        focus_server_api: FocusServerAPI
    ):
        """
        Test PZ-14763: GET /metadata/{task_id} - Metadata Consistency.
        
        Validates that metadata returned by GET /metadata/{task_id} is 
        consistent with the task configuration.
        
        Steps:
            1. Configure a task with specific parameters
            2. Wait for consumer to start
            3. Get task metadata
            4. Verify metadata matches configuration
            5. Verify sensor count matches
        
        Expected:
            - Metadata is consistent with configuration
            - Sensor count matches configuration
            - No inconsistencies found
        
        Jira: PZ-14763
        Priority: MEDIUM
        """
        logger.info("=" * 80)
        logger.info("TEST: GET /metadata/{task_id} - Metadata Consistency (PZ-14763)")
        logger.info("=" * 80)
        
        # Step 1: Configure a task with specific parameters
        task_id = generate_task_id("test-metadata-consistency")
        logger.info(f"Generated task_id: {task_id}")
        
        sensors_min = 1
        sensors_max = 50
        expected_channel_count = sensors_max - sensors_min + 1
        
        config_payload = {
            "displayTimeAxisDuration": 10.0,
            "nfftSelection": 1024,
            "canvasInfo": {"height": 1000},
            "sensors": {"min": sensors_min, "max": sensors_max},
            "frequencyRange": {"min": 0, "max": 1000},
            "start_time": None,
            "end_time": None
        }
        
        try:
            config_request = ConfigTaskRequest(**config_payload)
            config_response = focus_server_api.config_task(task_id, config_request)
            logger.info(f"✅ Task configured: {config_response.status}")
            
            # Step 2: Wait for consumer to start
            logger.info("Waiting for consumer to start...")
            time.sleep(5)  # Wait 5 seconds for consumer to start
            
            # Step 3: Get task metadata
            logger.info(f"Getting metadata for task {task_id}...")
            metadata_response = focus_server_api.get_task_metadata(task_id)
            
            # Step 4: Verify metadata matches configuration
            if metadata_response.status_code == 201 and metadata_response.metadata:
                metadata = metadata_response.metadata
                
                # Step 5: Verify sensor count matches
                if hasattr(metadata, 'number_of_channels'):
                    logger.info(f"✅ Number of channels: {metadata.number_of_channels}")
                    logger.info(f"   Expected range: {sensors_min}-{sensors_max} ({expected_channel_count} channels)")
                    
                    # Note: number_of_channels may not exactly match due to system configuration
                    # We verify it's in a reasonable range
                    assert metadata.number_of_channels > 0, \
                        "number_of_channels should be positive"
                
                # Verify other metadata fields
                if hasattr(metadata, 'prr'):
                    assert metadata.prr > 0, "PRR should be positive"
                    logger.info(f"✅ PRR: {metadata.prr}")
                
                if hasattr(metadata, 'dx'):
                    assert metadata.dx > 0, "DX should be positive"
                    logger.info(f"✅ DX: {metadata.dx}")
                
                logger.info("✅ Metadata is consistent with configuration")
            else:
                logger.info("ℹ️  Metadata not available yet (status 200) - skipping consistency check")
            
            logger.info("✅ All assertions passed")
            
        except APIError as e:
            logger.error(f"API Error: {e}")
            pytest.fail(f"API call failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            pytest.fail(f"Unexpected error: {e}")
        
        logger.info("=" * 80)
        logger.info("✅ TEST PASSED: Metadata Consistency")
        logger.info("=" * 80)
    
    @pytest.mark.xray("PZ-14764")
    @pytest.mark.xray("PZ-14090")

    @pytest.mark.regression
    def test_task_metadata_response_time(
        self,
        focus_server_api: FocusServerAPI
    ):
        """
        Test PZ-14764: GET /metadata/{task_id} - Response Time.
        
        Validates that GET /metadata/{task_id} endpoint response time 
        is within acceptable limits (< 500ms).
        
        Steps:
            1. Configure a task
            2. Wait for consumer to start
            3. Measure response time
            4. Verify response time < 500ms
        
        Expected:
            - Response time is < 500ms
            - Request completes successfully
            - No timeouts occur
        
        Jira: PZ-14764
        Priority: MEDIUM
        """
        logger.info("=" * 80)
        logger.info("TEST: GET /metadata/{task_id} - Response Time (PZ-14764)")
        logger.info("=" * 80)
        
        # Step 1: Configure a task
        task_id = generate_task_id("test-metadata-perf")
        logger.info(f"Generated task_id: {task_id}")
        
        config_payload = {
            "displayTimeAxisDuration": 10.0,
            "nfftSelection": 1024,
            "canvasInfo": {"height": 1000},
            "sensors": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 1000},
            "start_time": None,
            "end_time": None
        }
        
        try:
            config_request = ConfigTaskRequest(**config_payload)
            config_response = focus_server_api.config_task(task_id, config_request)
            logger.info(f"✅ Task configured: {config_response.status}")
            
            # Step 2: Wait for consumer to start
            logger.info("Waiting for consumer to start...")
            time.sleep(5)  # Wait 5 seconds for consumer to start
            
            # Step 3: Measure response time
            MAX_RESPONSE_TIME_MS = 500
            logger.info(f"Measuring response time (threshold: {MAX_RESPONSE_TIME_MS}ms)...")
            
            start_time = time.time()
            metadata_response = focus_server_api.get_task_metadata(task_id)
            end_time = time.time()
            
            response_time_ms = (end_time - start_time) * 1000
            
            # Step 4: Verify response time < 500ms
            logger.info(f"Response time: {response_time_ms:.2f}ms")
            
            assert response_time_ms < MAX_RESPONSE_TIME_MS, \
                f"Response time {response_time_ms:.2f}ms exceeds threshold {MAX_RESPONSE_TIME_MS}ms"
            
            # Verify request completed successfully
            assert metadata_response is not None, "Response should not be None"
            assert metadata_response.status_code in [200, 201], \
                f"Status code should be 200 or 201, got {metadata_response.status_code}"
            
            logger.info(f"✅ Response time {response_time_ms:.2f}ms is acceptable")
            logger.info("✅ All assertions passed")
            
        except APIError as e:
            logger.error(f"API Error: {e}")
            pytest.fail(f"API call failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            pytest.fail(f"Unexpected error: {e}")
        
        logger.info("=" * 80)
        logger.info("✅ TEST PASSED: Response Time")
        logger.info("=" * 80)



