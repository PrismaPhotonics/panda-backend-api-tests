"""
Stress Tests - Extreme Configuration Values
============================================

Tests for system robustness with extreme (but valid) configuration values.

Based on Xray Test: PZ-13880

Tests covered:
    - PZ-13880: Stress - Configuration with Extreme Values

Author: QA Automation Architect  
Date: 2025-10-27
"""

import pytest
import logging
from typing import Dict, Any

from src.models.focus_server_models import ConfigureRequest, ViewType
from src.apis.focus_server_api import FocusServerAPI
from src.core.exceptions import APIError

logger = logging.getLogger(__name__)


# ===================================================================
# Test Class: Extreme Configuration Values
# ===================================================================

@pytest.mark.api
@pytest.mark.load
@pytest.mark.stress
@pytest.mark.regression
class TestExtremeConfigurationValues:
    """
    Test suite for extreme configuration values stress testing.
    
    Tests covered:
        - PZ-13880: Configuration with extreme values
    
    Priority: MEDIUM
    """
    
    @pytest.mark.xray("PZ-13880")
    @pytest.mark.slow
    @pytest.mark.nightly
    @pytest.mark.stress
    @pytest.mark.regression
    def test_configuration_with_extreme_values(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-13880: Configuration with Extreme Values.
        
        Steps:
            1. Create config with extreme (but valid) values
            2. Send POST /configure
            3. Verify server handles without crash
        
        Expected:
            - Option A: Config accepted, server processes (may be slow)
            - Option B: Config rejected with "exceeds limits" (acceptable)
            - No crashes or errors
        
        Jira: PZ-13880
        Priority: MEDIUM
        """
        logger.info("=" * 80)
        logger.info("TEST: Configuration with Extreme Values (PZ-13880)")
        logger.info("=" * 80)
        
        # Extreme configuration
        extreme_config = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 8192,  # Very high NFFT
            "displayInfo": {"height": 5000},  # Very tall canvas
            "channels": {"min": 1, "max": 200},  # Many channels (min must be >= 1 per Pydantic validation)
            "frequencyRange": {"min": 0, "max": 1000},  # Wide frequency
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        logger.info("Extreme values:")
        logger.info(f"  - NFFT: {extreme_config['nfftSelection']}")
        logger.info(f"  - Canvas Height: {extreme_config['displayInfo']['height']}")
        logger.info(f"  - Channels: {extreme_config['channels']['max'] - extreme_config['channels']['min']}")
        logger.info(f"  - Frequency Range: {extreme_config['frequencyRange']['max']}")
        
        try:
            configure_request = ConfigureRequest(**extreme_config)
            response = focus_server_api.configure_streaming_job(configure_request)
            
            # If accepted
            if hasattr(response, 'job_id') and response.job_id:
                logger.info(f"✅ Server accepted extreme configuration: {response.job_id}")
                logger.info("   Server demonstrated robustness")
                
                # Cleanup
                try:
                    focus_server_api.cancel_job(response.job_id)
                    logger.info(f"   Job {response.job_id} cancelled")
                except:
                    pass
            
        except (APIError, ValueError) as e:
            # If rejected, verify it's a reasonable rejection
            error_msg = str(e).lower()
            
            if any(keyword in error_msg for keyword in ['exceed', 'limit', 'maximum', 'too large']):
                logger.info(f"✅ Server rejected extreme values with reasonable error:")
                logger.info(f"   {e}")
                logger.info("   This is acceptable behavior")
            else:
                logger.error(f"❌ Unexpected error: {e}")
                raise
        
        logger.info("=" * 80)
        logger.info("✅ TEST PASSED: Extreme Values Handled Properly")
        logger.info("=" * 80)


# ===================================================================
# Module Summary Test
# ===================================================================

@pytest.mark.summary


@pytest.mark.regression
def test_extreme_configurations_summary():
    """
    Summary test for extreme configurations tests.
    
    Xray Tests Covered:
        - PZ-13880: Configuration with Extreme Values
    
    This test always passes and serves as documentation.
    """
    logger.info("=" * 80)
    logger.info("Extreme Configuration Tests Suite Summary")
    logger.info("=" * 80)
    logger.info("Tests in this module:")
    logger.info("  1. PZ-13880: Configuration with extreme values")
    logger.info("=" * 80)

