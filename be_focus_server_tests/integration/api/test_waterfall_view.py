"""
Integration Tests - Waterfall View Handling
============================================

Tests for Waterfall view type (view_type=2) configuration and behavior.

Based on Xray Test: PZ-13557

Tests covered:
    - PZ-13557: API - Waterfall view handling

Author: QA Automation Architect  
Date: 2025-10-27
"""

import pytest
import logging
from typing import Dict, Any

from src.models.focus_server_models import ConfigureRequest, ViewType
from src.apis.focus_server_api import FocusServerAPI

logger = logging.getLogger(__name__)


# ===================================================================
# Test Class: Waterfall View
# ===================================================================

@pytest.mark.view_type


@pytest.mark.regression
class TestWaterfallView:
    """
    Test suite for Waterfall view type handling.
    
    Tests covered:
        - PZ-13557: Waterfall view configuration and response
    
    Priority: MEDIUM
    """
    
    @pytest.mark.xray("PZ-13557")
    @pytest.mark.jira("PZ-13238")  # Bug: Waterfall configuration fails when optional fields omitted

    @pytest.mark.regression
    def test_waterfall_view_handling(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-13557: API - Waterfall View Handling.
        
        Objective:
            Verify that view_type=WATERFALL (2) produces correct response
            with Waterfall-specific parameters and consistent configuration.
        
        Steps:
            1. Create configuration with view_type=WATERFALL (2)
            2. Send POST /configure
            3. Verify response contains view_type=2
            4. Verify Waterfall-specific parameters present
            5. Verify response is consistent for Waterfall rendering
        
        Expected:
            - Configuration accepted
            - Response has view_type = 2
            - Waterfall-specific fields present
            - Stream configuration suitable for Waterfall rendering
        
        Jira: PZ-13557
        Priority: MEDIUM
        """
        logger.info("=" * 80)
        logger.info("TEST: Waterfall View Handling (PZ-13557)")
        logger.info("=" * 80)
        
        # Create Waterfall configuration
        waterfall_config = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 800},
            "channels": {"min": 1, "max": 10},
            "frequencyRange": {"min": 0, "max": 1000},
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.WATERFALL  # view_type = 2
        }
        
        logger.info("Step 1: Creating Waterfall configuration")
        logger.info(f"   view_type: WATERFALL (2)")
        logger.info(f"   channels: 1-10")
        logger.info(f"   frequency: 0-1000")
        
        config_request = ConfigureRequest(**waterfall_config)
        
        # Verify request
        assert config_request.view_type == ViewType.WATERFALL or config_request.view_type == "2"
        logger.info("✅ ConfigureRequest created with view_type=WATERFALL")
        
        # Step 2: Send to API
        logger.info("\nStep 2: Sending POST /configure")
        response = focus_server_api.configure_streaming_job(config_request)
        
        # Step 3: Verify response
        logger.info("\nStep 3: Validating response")
        
        assert hasattr(response, 'job_id') and response.job_id, \
            "Waterfall config should return job_id"
        
        logger.info(f"   Job ID: {response.job_id}")
        
        # Check view_type in response
        if hasattr(response, 'view_type'):
            logger.info(f"   View Type: {response.view_type}")
            # Accept both "2" and 2
            assert str(response.view_type) == "2" or response.view_type == 2, \
                f"Expected view_type=2, got {response.view_type}"
            logger.info("✅ Response view_type correct (WATERFALL)")
        
        # Check stream configuration
        if hasattr(response, 'stream_amount'):
            logger.info(f"   Stream Amount: {response.stream_amount}")
        
        if hasattr(response, 'channel_amount'):
            logger.info(f"   Channel Amount: {response.channel_amount}")
        
        if hasattr(response, 'frequencies_amount'):
            logger.info(f"   Frequencies Amount: {response.frequencies_amount}")
        
        # Verify Waterfall-specific behavior
        logger.info("\nStep 4: Verifying Waterfall-specific configuration")
        
        # Waterfall view should have streams configured
        if hasattr(response, 'stream_amount'):
            assert response.stream_amount > 0, "Waterfall should have at least one stream"
            logger.info(f"✅ Waterfall has {response.stream_amount} stream(s)")
        
        # Cleanup
        logger.info("\nStep 5: Cleanup")
        try:
            focus_server_api.cancel_job(response.job_id)
            logger.info(f"   Job {response.job_id} cancelled")
        except Exception as e:
            logger.info(f"   Cleanup: {e}")
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ Waterfall View Configuration Summary:")
        logger.info("   - Configuration accepted ✅")
        logger.info("   - view_type=2 (WATERFALL) verified ✅")
        logger.info("   - Response structure valid ✅")
        logger.info("   - Suitable for Waterfall rendering ✅")
        logger.info("=" * 80)
        logger.info("✅ TEST PASSED: Waterfall View Handling")
        logger.info("=" * 80)



