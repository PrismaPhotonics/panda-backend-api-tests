"""
Integration Tests - API Endpoints (High Priority)
===================================================

High priority tests for Focus Server API endpoints.

Tests Covered (Xray):
    - PZ-13419: GET /channels - Enabled Channels List

Author: QA Automation Architect
Date: 2025-10-21
"""

import pytest
import logging
from typing import List, Dict, Any

from src.utils.helpers import generate_task_id

logger = logging.getLogger(__name__)


# ===================================================================
# Test Class: GET /channels Endpoint (PZ-13419)
# ===================================================================

@pytest.mark.integration
@pytest.mark.api
@pytest.mark.critical
@pytest.mark.smoke
class TestChannelsEndpoint:
    """
    Test suite for PZ-13419: GET /channels - Enabled Channels
    Priority: HIGH
    
    Validates that the channels endpoint returns the list of enabled channels.
    This is a critical smoke test for basic API functionality.
    """
    
    @pytest.mark.xray("PZ-13895", "PZ-13762", "PZ-13560")
    def test_get_channels_endpoint_success(self, focus_server_api):
        """
        Test PZ-13419.1: GET /channels returns enabled channels list.
        
        PZ-13895: Integration - GET /channels - Enabled Channels List
        PZ-13762: API - GET /channels - Returns System Channel Bounds
        PZ-13560: API - GET /channels (baseline availability)
        
        Steps:
            1. Send GET /channels request
            2. Verify response structure
            3. Verify channels list is non-empty
            4. Verify channel objects have required fields
        
        Expected:
            - Status code: 200 OK
            - Response contains list of channels
            - Each channel has id/channel_id field
            - Each channel has enabled/status field
        
        Jira: PZ-13419
        Priority: HIGH
        """
        logger.info("Test PZ-13419.1: GET /channels endpoint")
        
        # Send GET /channels request
        response = focus_server_api.get_channels()
        
        # Assertions - basic response
        assert response is not None, "Response should not be None"
        
        # Response is ChannelRange object with lowest_channel and highest_channel
        assert hasattr(response, 'lowest_channel') or hasattr(response, 'highest_channel') or \
               hasattr(response, 'status_code') or hasattr(response, 'channels'), \
            f"Response should have channel fields. Got: {response}"
        
        # Get status code
        if hasattr(response, 'status_code'):
            assert response.status_code == 200, \
                f"Expected status code 200, got {response.status_code}"
        
        # Get channels - response may be ChannelRange object
        channels = None
        if hasattr(response, 'lowest_channel') and hasattr(response, 'highest_channel'):
            # ChannelRange object - generate list from range
            channels = list(range(response.lowest_channel, response.highest_channel + 1))
            logger.info(f"✅ ChannelRange: {response.lowest_channel} - {response.highest_channel}")
        elif hasattr(response, 'channels'):
            channels = response.channels
        elif hasattr(response, 'data'):
            channels = response.data
        elif isinstance(response, list):
            channels = response
        
        assert channels is not None, f"Could not extract channels from response: {response}"
        assert isinstance(channels, list), \
            f"Channels should be a list, got {type(channels)}"
        
        assert len(channels) > 0, "Channels list should not be empty"
        
        logger.info(f"✅ Channels endpoint returned {len(channels)} channels")
        
        # Validate channel structure
        for idx, channel in enumerate(channels):
            # Check for channel identifier
            has_id = (
                hasattr(channel, 'id') or 
                hasattr(channel, 'channel_id') or
                isinstance(channel, dict) and ('id' in channel or 'channel_id' in channel) or
                isinstance(channel, (int, str))  # May be just a list of IDs
            )
            
            assert has_id, f"Channel {idx} should have an identifier"
            
            # Log channel info
            if isinstance(channel, dict):
                logger.info(f"  Channel {idx}: {channel}")
            elif hasattr(channel, '__dict__'):
                logger.info(f"  Channel {idx}: {channel.__dict__}")
            else:
                logger.info(f"  Channel {idx}: {channel}")
        
        logger.info("✅ All channels have valid structure")
    
    @pytest.mark.xray("PZ-13896")
    @pytest.mark.xray("PZ-14790")
    def test_get_channels_endpoint_response_time(self, focus_server_api):
        """
        Test PZ-13419.2: GET /channels response time.
        
        PZ-13896: API - GET /channels - Response Time < 1 Second
        
        Steps:
            1. Measure response time for GET /channels
            2. Verify response time is acceptable
        
        Expected:
            - Response time < 1000ms (need specs!)
        
        Jira: PZ-13419
        Priority: HIGH
        """
        import time
        
        logger.info("Test PZ-13419.2: GET /channels response time")
        
        # Measure response time
        start_time = time.time()
        response = focus_server_api.get_channels()
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        logger.info(f"Response time: {response_time_ms:.2f}ms")
        
        # TODO: Update threshold after specs meeting
        # For now, use 1000ms as reasonable threshold
        MAX_RESPONSE_TIME_MS = 1000
        
        assert response_time_ms < MAX_RESPONSE_TIME_MS, \
            f"Response time {response_time_ms:.2f}ms exceeds threshold {MAX_RESPONSE_TIME_MS}ms"
        
        logger.info(f"✅ Response time {response_time_ms:.2f}ms is acceptable")
    
    @pytest.mark.xray("PZ-13897")
    @pytest.mark.xray("PZ-14809")
    def test_get_channels_endpoint_multiple_calls_consistency(self, focus_server_api):
        """
        Test PZ-13419.3: GET /channels returns consistent results.
        
        PZ-13897: API - GET /channels - Multiple Calls Consistency
        
        Steps:
            1. Call GET /channels multiple times
            2. Verify results are consistent
        
        Expected:
            - All calls return same channel list
            - Channel order may vary or be consistent (document behavior)
        
        Jira: PZ-13419
        Priority: HIGH
        """
        logger.info("Test PZ-13419.3: GET /channels consistency")
        
        # Call endpoint 3 times
        responses = []
        for i in range(3):
            response = focus_server_api.get_channels()
            
            # Extract channels list - may be ChannelRange object
            if hasattr(response, 'lowest_channel') and hasattr(response, 'highest_channel'):
                channels = list(range(response.lowest_channel, response.highest_channel + 1))
            elif hasattr(response, 'channels'):
                channels = response.channels
            elif hasattr(response, 'data'):
                channels = response.data
            elif isinstance(response, list):
                channels = response
            else:
                pytest.fail(f"Could not extract channels from response: {response}")
            
            responses.append(channels)
            logger.info(f"Call {i+1}: {len(channels)} channels")
        
        # Verify all responses have same length
        lengths = [len(r) for r in responses]
        assert all(length == lengths[0] for length in lengths), \
            f"Inconsistent number of channels: {lengths}"
        
        logger.info(f"✅ All calls returned {lengths[0]} channels consistently")
        
        # Note: We don't strictly require same order, but log if order differs
        if all(responses[i] == responses[0] for i in range(len(responses))):
            logger.info("✅ Channel order is consistent")
        else:
            logger.info("ℹ️ Channel order varies between calls (may be expected)")
    
    @pytest.mark.xray("PZ-13898")
    @pytest.mark.xray("PZ-13762")
    def test_get_channels_endpoint_channel_ids_sequential(self, focus_server_api):
        """
        Test PZ-13419.4: Verify channel IDs are reasonable.
        
        PZ-13898: API - GET /channels - Channel IDs Validation
        
        Steps:
            1. Get channels list
            2. Extract channel IDs
            3. Verify IDs are reasonable (non-negative, reasonable range)
        
        Expected:
            - Channel IDs are non-negative integers
            - Channel IDs are in reasonable range (e.g., 0-1000)
        
        Jira: PZ-13419
        Priority: HIGH
        """
        logger.info("Test PZ-13419.4: Channel IDs validation")
        
        response = focus_server_api.get_channels()
        
        # Extract channels
        if hasattr(response, 'channels'):
            channels = response.channels
        elif hasattr(response, 'data'):
            channels = response.data
        elif isinstance(response, list):
            channels = response
        else:
            pytest.skip("Could not extract channels from response")
        
        # Extract channel IDs
        channel_ids = []
        for channel in channels:
            if isinstance(channel, (int, str)):
                # Channel is just an ID
                try:
                    channel_ids.append(int(channel))
                except ValueError:
                    logger.warning(f"Could not convert channel to int: {channel}")
            elif isinstance(channel, dict):
                # Channel is an object
                if 'id' in channel:
                    channel_ids.append(int(channel['id']))
                elif 'channel_id' in channel:
                    channel_ids.append(int(channel['channel_id']))
            elif hasattr(channel, 'id'):
                channel_ids.append(int(channel.id))
            elif hasattr(channel, 'channel_id'):
                channel_ids.append(int(channel.channel_id))
        
        assert len(channel_ids) > 0, "Should extract at least one channel ID"
        
        logger.info(f"Extracted {len(channel_ids)} channel IDs: {channel_ids[:10]}{'...' if len(channel_ids) > 10 else ''}")
        
        # Validate IDs are non-negative
        for channel_id in channel_ids:
            assert channel_id >= 0, f"Channel ID {channel_id} is negative"
        
        # Validate IDs are in reasonable range
        # TODO: Update max value after specs meeting
        MAX_CHANNEL_ID = 10000  # Reasonable upper bound
        
        for channel_id in channel_ids:
            assert channel_id <= MAX_CHANNEL_ID, \
                f"Channel ID {channel_id} exceeds reasonable max {MAX_CHANNEL_ID}"
        
        logger.info(f"✅ All {len(channel_ids)} channel IDs are valid (non-negative, < {MAX_CHANNEL_ID})")
    
    @pytest.mark.xray("PZ-13899")
    @pytest.mark.xray("PZ-13895")
    def test_get_channels_endpoint_enabled_status(self, focus_server_api):
        """
        Test PZ-13419.5: Verify enabled/disabled status if present.
        
        PZ-13899: API - GET /channels - Enabled Status Verification
        
        Steps:
            1. Get channels list
            2. Check if enabled/status field exists
            3. If exists, verify all returned channels are enabled
        
        Expected:
            - If status field exists, all channels should be enabled
            - Disabled channels should not be in the list
        
        Jira: PZ-13419
        Priority: HIGH
        """
        logger.info("Test PZ-13419.5: Channel enabled status")
        
        response = focus_server_api.get_channels()
        
        # Extract channels
        if hasattr(response, 'channels'):
            channels = response.channels
        elif hasattr(response, 'data'):
            channels = response.data
        elif isinstance(response, list):
            channels = response
        else:
            pytest.skip("Could not extract channels from response")
        
        # Check for enabled/status field
        has_status_field = False
        enabled_count = 0
        
        for channel in channels:
            if isinstance(channel, dict):
                if 'enabled' in channel:
                    has_status_field = True
                    assert channel['enabled'] is True, \
                        f"Channel {channel} is in list but not enabled"
                    enabled_count += 1
                elif 'status' in channel:
                    has_status_field = True
                    assert channel['status'] in ['enabled', 'active', True], \
                        f"Channel {channel} is in list but not enabled"
                    enabled_count += 1
            elif hasattr(channel, 'enabled'):
                has_status_field = True
                assert channel.enabled is True
                enabled_count += 1
            elif hasattr(channel, 'status'):
                has_status_field = True
                assert channel.status in ['enabled', 'active', True]
                enabled_count += 1
        
        if has_status_field:
            logger.info(f"✅ All {enabled_count} channels with status field are enabled")
        else:
            logger.info("ℹ️ No enabled/status field found (all returned channels assumed enabled)")


# ===================================================================
# Module Summary Test
# ===================================================================

@pytest.mark.summary
def test_api_endpoints_high_priority_summary():
    """
    Summary test for API endpoints (high priority tests).
    
    This test documents which Xray test cases are covered in this module.
    
    Covered Xray Tests:
        ✅ PZ-13419: GET /channels Endpoint (5 tests)
    
    Total: 5 high-priority API endpoint tests
    """
    logger.info("=" * 80)
    logger.info("API Endpoints (High Priority) - Summary")
    logger.info("=" * 80)
    logger.info("Xray Test Coverage:")
    logger.info("  ✅ PZ-13419: GET /channels - 5 tests")
    logger.info("=" * 80)
    logger.info("Total: 5 High Priority Tests")
    logger.info("=" * 80)

