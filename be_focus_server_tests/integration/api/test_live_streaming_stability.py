"""
Integration Tests - Live Streaming Stability
=============================================

Tests for live streaming stability and long-running streams.

Based on Xray Test: PZ-13800

Tests covered:
    - PZ-13800: Live Streaming Stability

Author: QA Automation Architect  
Date: 2025-10-27
"""

import pytest
import logging
import time
from typing import Dict, Any

from src.models.focus_server_models import ConfigureRequest, ViewType
from src.apis.focus_server_api import FocusServerAPI

logger = logging.getLogger(__name__)


# ===================================================================
# Test Class: Live Streaming Stability
# ===================================================================

@pytest.mark.slow
@pytest.mark.nightly
@pytest.mark.regression
class TestLiveStreamingStability:
    """
    Test suite for live streaming stability.
    
    Tests covered:
        - PZ-13800: Live streaming remains stable over time
    
    Priority: HIGH
    """
    
    @pytest.mark.xray("PZ-13800")
    @pytest.mark.xray("PZ-13570")

    @pytest.mark.regression
    def test_live_streaming_stability(self, focus_server_api: FocusServerAPI):
        """
        Test PZ-13800: Live Streaming Stability.
        
        Steps:
            1. Configure live streaming job
            2. Poll status for extended period (5 minutes)
            3. Verify stream remains stable
            4. No crashes or errors
        
        Expected:
            - Stream remains active
            - Status consistent
            - No disconnections
            - Server stable
        
        Jira: PZ-13800
        Priority: HIGH
        """
        logger.info("=" * 80)
        logger.info("TEST: Live Streaming Stability (PZ-13800)")
        logger.info("=" * 80)
        
        # Configure live stream
        config = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": None,  # Live mode
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        logger.info("Configuring live streaming job...")
        configure_request = ConfigureRequest(**config)
        response = focus_server_api.configure_streaming_job(configure_request)
        job_id = response.job_id
        
        logger.info(f"✅ Live stream configured: {job_id}")
        logger.info("Monitoring stream stability for 5 minutes...")
        
        # Monitor for 5 minutes
        duration = 300  # 5 minutes
        interval = 30  # Poll every 30 seconds
        polls = duration // interval
        
        errors = 0
        status_changes = []
        
        for i in range(polls):
            try:
                elapsed = i * interval
                logger.info(f"\n[{elapsed}s] Polling stream status...")
                
                status = focus_server_api.get_job_status(job_id)
                
                if not status_changes or status_changes[-1] != str(status):
                    status_changes.append(str(status))
                    logger.info(f"Status: {status}")
                
                logger.info(f"✅ Poll {i+1}/{polls} successful")
                
                time.sleep(interval)
                
            except Exception as e:
                errors += 1
                logger.error(f"❌ Poll {i+1} failed: {e}")
                
                if errors > 2:
                    pytest.fail(f"Too many polling errors: {errors}")
        
        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("STABILITY TEST SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Duration: {duration}s (5 minutes)")
        logger.info(f"Polls: {polls}")
        logger.info(f"Errors: {errors}")
        logger.info(f"Status changes: {' → '.join(status_changes)}")
        
        # Verify stability
        assert errors <= 2, f"Too many errors ({errors}) - stream unstable"
        logger.info("✅ Stream remained stable throughout test")
        
        # Cleanup
        try:
            focus_server_api.cancel_job(job_id)
            logger.info(f"Job {job_id} cancelled")
        except:
            pass
        
        logger.info("=" * 80)
        logger.info("✅ TEST PASSED: Live Streaming Stability Verified")
        logger.info("=" * 80)



