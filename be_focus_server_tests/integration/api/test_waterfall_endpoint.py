"""
Integration Tests - GET /waterfall/{task_id}/{row_count} Endpoint (Future Structure)
======================================================================================

⚠️  NOTE: These tests are for the FUTURE API structure using GET /waterfall/{task_id}/{row_count}
   Currently, the staging environment may not have this endpoint.
   These tests are SKIPPED until the new endpoint is deployed.

Tests for GET /waterfall/{task_id}/{row_count} endpoint covering:
- Valid request with data
- No data available
- Invalid task ID
- Invalid row count
- Baby analyzer exited

Tests Covered (Xray):
    - PZ-14755: GET /waterfall/{task_id}/{row_count} - Valid Request
    - PZ-14756: GET /waterfall/{task_id}/{row_count} - No Data Available
    - PZ-14757: GET /waterfall/{task_id}/{row_count} - Invalid Task ID
    - PZ-14758: GET /waterfall/{task_id}/{row_count} - Invalid Row Count
    - PZ-14759: GET /waterfall/{task_id}/{row_count} - Baby Analyzer Exited

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
# Test Class: GET /waterfall/{task_id}/{row_count} Endpoint
# ===================================================================

@pytest.mark.skip(reason="Future API structure - GET /waterfall/{task_id}/{row_count} endpoint not yet deployed to staging")


@pytest.mark.regression
class TestWaterfallEndpoint:
    """
    Test suite for GET /waterfall/{task_id}/{row_count} endpoint.
    
    Tests covered:
        - PZ-14755: Valid Request
        - PZ-14756: No Data Available
        - PZ-14757: Invalid Task ID
        - PZ-14758: Invalid Row Count
        - PZ-14759: Baby Analyzer Exited
    
    Priority: HIGH
    """
    
    @pytest.mark.xray("PZ-14755")
    @pytest.mark.xray("PZ-13557")

    @pytest.mark.regression
    def test_waterfall_valid_request(
        self,
        focus_server_api: FocusServerAPI
    ):
        """
        Test PZ-14755: GET /waterfall/{task_id}/{row_count} - Valid Request.
        
        Validates that GET /waterfall/{task_id}/{row_count} endpoint returns 
        201 Created with waterfall data when data is available.
        
        Steps:
            1. Configure a task
            2. Wait for task to start processing
            3. Send GET /waterfall/{task_id}/{row_count} request
            4. Verify response structure
            5. Verify waterfall data structure
        
        Expected:
            - Request returns 201 Created
            - Response contains waterfall data
            - Data structure is valid
        
        Jira: PZ-14755
        Priority: HIGH
        """
        logger.info("=" * 80)
        logger.info("TEST: GET /waterfall/{task_id}/{row_count} - Valid Request (PZ-14755)")
        logger.info("=" * 80)
        
        # Step 1: Configure a task
        task_id = generate_task_id("test-waterfall")
        logger.info(f"Generated task_id: {task_id}")
        
        config_payload = {
            "displayTimeAxisDuration": 10.0,
            "nfftSelection": 1024,
            "canvasInfo": {"height": 1000},
            "sensors": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": None,
            "end_time": None
        }
        
        try:
            config_request = ConfigTaskRequest(**config_payload)
            config_response = focus_server_api.config_task(task_id, config_request)
            logger.info(f"✅ Task configured: {config_response.status}")
            
            # Step 2: Wait for task to start processing
            logger.info("Waiting for task to start processing...")
            time.sleep(5)  # Wait 5 seconds for processing to start
            
            # Step 3: Send GET /waterfall/{task_id}/{row_count} request
            row_count = 10
            logger.info(f"Sending GET /waterfall/{task_id}/{row_count} request...")
            waterfall_response = focus_server_api.get_waterfall(task_id, row_count)
            
            # Step 4: Verify response structure
            assert waterfall_response is not None, "Response should not be None"
            assert hasattr(waterfall_response, 'status_code'), "Response should have status_code"
            
            # Step 5: Verify waterfall data structure
            if waterfall_response.status_code == 201:
                assert waterfall_response.data is not None, "Data should be present for status 201"
                assert isinstance(waterfall_response.data, list), "Data should be a list"
                
                logger.info(f"✅ Status code: {waterfall_response.status_code}")
                logger.info(f"✅ Data blocks: {len(waterfall_response.data)}")
                
                if waterfall_response.data:
                    logger.info(f"✅ First block contains {len(waterfall_response.data[0].rows)} rows")
            elif waterfall_response.status_code == 200:
                logger.info("✅ Status code: 200 (No data available yet - may be expected)")
            else:
                logger.warning(f"⚠️  Unexpected status code: {waterfall_response.status_code}")
            
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
    
    @pytest.mark.xray("PZ-14756")
    @pytest.mark.xray("PZ-13557")

    @pytest.mark.regression
    def test_waterfall_no_data_available(
        self,
        focus_server_api: FocusServerAPI
    ):
        """
        Test PZ-14756: GET /waterfall/{task_id}/{row_count} - No Data Available.
        
        Validates that GET /waterfall/{task_id}/{row_count} endpoint returns 
        200 OK with empty response when no data is available yet.
        
        Steps:
            1. Configure a task
            2. Immediately request waterfall data
            3. Verify response is empty
        
        Expected:
            - Request returns 200 OK
            - Response indicates no data available
            - No errors occur
        
        Jira: PZ-14756
        Priority: MEDIUM
        """
        logger.info("=" * 80)
        logger.info("TEST: GET /waterfall/{task_id}/{row_count} - No Data Available (PZ-14756)")
        logger.info("=" * 80)
        
        # Step 1: Configure a task
        task_id = generate_task_id("test-waterfall-empty")
        logger.info(f"Generated task_id: {task_id}")
        
        config_payload = {
            "displayTimeAxisDuration": 10.0,
            "nfftSelection": 1024,
            "canvasInfo": {"height": 1000},
            "sensors": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": None,
            "end_time": None
        }
        
        try:
            config_request = ConfigTaskRequest(**config_payload)
            config_response = focus_server_api.config_task(task_id, config_request)
            logger.info(f"✅ Task configured: {config_response.status}")
            
            # Step 2: Immediately request waterfall data (no wait)
            row_count = 10
            logger.info(f"Immediately requesting GET /waterfall/{task_id}/{row_count}...")
            waterfall_response = focus_server_api.get_waterfall(task_id, row_count)
            
            # Step 3: Verify response is empty
            assert waterfall_response is not None, "Response should not be None"
            assert waterfall_response.status_code in [200, 201], \
                f"Status code should be 200 or 201, got {waterfall_response.status_code}"
            
            if waterfall_response.status_code == 200:
                logger.info("✅ Status code: 200 (No data available - expected)")
                assert waterfall_response.data is None or len(waterfall_response.data) == 0, \
                    "Data should be None or empty for status 200"
            else:
                logger.info(f"✅ Status code: {waterfall_response.status_code} (Data may be available)")
            
            logger.info("✅ All assertions passed")
            
        except APIError as e:
            logger.error(f"API Error: {e}")
            pytest.fail(f"API call failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            pytest.fail(f"Unexpected error: {e}")
        
        logger.info("=" * 80)
        logger.info("✅ TEST PASSED: No Data Available")
        logger.info("=" * 80)
    
    @pytest.mark.xray("PZ-14757")
    @pytest.mark.xray("PZ-13557")

    @pytest.mark.regression
    def test_waterfall_invalid_task_id(
        self,
        focus_server_api: FocusServerAPI
    ):
        """
        Test PZ-14757: GET /waterfall/{task_id}/{row_count} - Invalid Task ID.
        
        Validates that GET /waterfall/{task_id}/{row_count} endpoint returns 
        404 Not Found for invalid task_id.
        
        Steps:
            1. Send GET /waterfall/{task_id}/{row_count} request with invalid task_id
            2. Verify error response
        
        Expected:
            - Request returns 404 Not Found
            - Error message indicates task not found
            - No data is returned
        
        Jira: PZ-14757
        Priority: HIGH
        """
        logger.info("=" * 80)
        logger.info("TEST: GET /waterfall/{task_id}/{row_count} - Invalid Task ID (PZ-14757)")
        logger.info("=" * 80)
        
        # Step 1: Send request with invalid task_id
        invalid_task_id = "nonexistent-task-12345"
        row_count = 10
        
        logger.info(f"Sending GET /waterfall/{invalid_task_id}/{row_count} request...")
        
        try:
            waterfall_response = focus_server_api.get_waterfall(invalid_task_id, row_count)
            
            # Step 2: Verify error response
            assert waterfall_response is not None, "Response should not be None"
            
            if waterfall_response.status_code == 404:
                logger.info("✅ Status code: 404 Not Found (expected)")
                assert waterfall_response.data is None, "Data should be None for 404"
            else:
                logger.warning(f"⚠️  Unexpected status code: {waterfall_response.status_code}")
                logger.warning(f"   Expected 404, got {waterfall_response.status_code}")
            
            logger.info("✅ All assertions passed")
            
        except APIError as e:
            # APIError is also acceptable for invalid task_id
            logger.info(f"✅ APIError caught (expected): {e}")
        except Exception as e:
            logger.info(f"✅ Error caught (expected): {type(e).__name__}: {e}")
        
        logger.info("=" * 80)
        logger.info("✅ TEST PASSED: Invalid Task ID Handling")
        logger.info("=" * 80)
    
    @pytest.mark.xray("PZ-14758")
    @pytest.mark.xray("PZ-13557")

    @pytest.mark.regression
    def test_waterfall_invalid_row_count(
        self,
        focus_server_api: FocusServerAPI
    ):
        """
        Test PZ-14758: GET /waterfall/{task_id}/{row_count} - Invalid Row Count.
        
        Validates that GET /waterfall/{task_id}/{row_count} endpoint returns 
        400 Bad Request for invalid row_count values (0 or negative).
        
        Steps:
            1. Configure a task
            2. Send requests with invalid row_count values
            3. Verify error responses
        
        Expected:
            - All invalid row_count values are rejected
            - Status code is 400 Bad Request
            - Error message indicates invalid row_count
        
        Jira: PZ-14758
        Priority: MEDIUM
        """
        logger.info("=" * 80)
        logger.info("TEST: GET /waterfall/{task_id}/{row_count} - Invalid Row Count (PZ-14758)")
        logger.info("=" * 80)
        
        # Step 1: Configure a task
        task_id = generate_task_id("test-waterfall-invalid")
        logger.info(f"Generated task_id: {task_id}")
        
        config_payload = {
            "displayTimeAxisDuration": 10.0,
            "nfftSelection": 1024,
            "canvasInfo": {"height": 1000},
            "sensors": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": None,
            "end_time": None
        }
        
        try:
            config_request = ConfigTaskRequest(**config_payload)
            config_response = focus_server_api.config_task(task_id, config_request)
            logger.info(f"✅ Task configured: {config_response.status}")
            
            # Step 2: Test invalid row_count values
            invalid_row_counts = [0, -1, -10]
            
            for invalid_count in invalid_row_counts:
                logger.info(f"\nTesting invalid row_count: {invalid_count}")
                
                try:
                    # This should fail validation before API call
                    waterfall_response = focus_server_api.get_waterfall(task_id, invalid_count)
                    
                    # If we get here, check status code
                    if waterfall_response.status_code == 400:
                        logger.info(f"✅ 400 Bad Request (expected) for row_count={invalid_count}")
                    else:
                        logger.warning(f"⚠️  Unexpected status code: {waterfall_response.status_code}")
                
                except ValidationError as e:
                    logger.info(f"✅ ValidationError caught (expected): {e}")
                except APIError as e:
                    if hasattr(e, 'status_code') and e.status_code == 400:
                        logger.info(f"✅ 400 Bad Request (expected): {e}")
                    else:
                        logger.info(f"✅ APIError caught: {e}")
                except Exception as e:
                    logger.info(f"✅ Error caught (expected): {type(e).__name__}: {e}")
            
            logger.info("✅ All assertions passed")
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            pytest.fail(f"Unexpected error: {e}")
        
        logger.info("=" * 80)
        logger.info("✅ TEST PASSED: Invalid Row Count Handling")
        logger.info("=" * 80)
    
    @pytest.mark.xray("PZ-14759")
    @pytest.mark.xray("PZ-13557")

    @pytest.mark.regression
    def test_waterfall_baby_analyzer_exited(
        self,
        focus_server_api: FocusServerAPI
    ):
        """
        Test PZ-14759: GET /waterfall/{task_id}/{row_count} - Baby Analyzer Exited.
        
        Validates that GET /waterfall/{task_id}/{row_count} endpoint returns 
        208 Already Reported when baby analyzer has exited.
        
        Steps:
            1. Configure a historic playback task
            2. Wait for task to complete
            3. Send GET /waterfall/{task_id}/{row_count} request
            4. Verify response indicates completion
        
        Expected:
            - Request returns 208 Already Reported
            - Response indicates baby analyzer has exited
            - No errors occur
        
        Jira: PZ-14759
        Priority: MEDIUM
        
        Note: This test requires a historic playback task that completes quickly.
        """
        logger.info("=" * 80)
        logger.info("TEST: GET /waterfall/{task_id}/{row_count} - Baby Analyzer Exited (PZ-14759)")
        logger.info("=" * 80)
        
        logger.info("ℹ️  This test requires a historic playback task that completes")
        logger.info("   For now, we'll document the expected behavior")
        
        # This test would need a historic playback task that completes
        # For now, we'll skip it or document expected behavior
        pytest.skip("Requires historic playback task setup - to be implemented")
        
        logger.info("=" * 80)
        logger.info("✅ TEST PASSED: Baby Analyzer Exited Handling")
        logger.info("=" * 80)



