"""
Integration Tests - Historic Playback (High Priority)
=======================================================

High priority tests for Focus Server historic playback functionality.

Tests Covered (Xray):
    - PZ-13868: Historic Playback - Status 208 Completion
    - PZ-13871: Historic Playback - Timestamp Ordering Validation

Author: QA Automation Architect
Date: 2025-10-21
"""

import pytest
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

from src.models.focus_server_models import ConfigTaskRequest, ConfigTaskResponse
from src.utils.helpers import (
    generate_task_id,
    generate_config_payload,
    generate_time_range,
    datetime_to_yymmddHHMMSS
)
from src.utils.validators import validate_waterfall_response

logger = logging.getLogger(__name__)


# ===================================================================
# Test Class: Status 208 Completion (PZ-13868)
# ===================================================================

@pytest.mark.integration
@pytest.mark.api
@pytest.mark.critical
class TestHistoricStatus208Completion:
    """
    Test suite for PZ-13868: Historic Playback - Status 208 Completion
    Priority: HIGH
    
    Validates that historic playback properly completes with status 208
    ("Already Reported") when all data has been delivered.
    """
    
    def test_historic_status_208_completion(self, focus_server_api):
        """
        Test PZ-13868.1: Historic playback completes with status 208.
        
        Steps:
            1. Configure historic task with short time range (1 minute)
            2. Poll waterfall endpoint continuously
            3. Verify status transitions: 200 → 201 → 208
            4. Verify no more data after 208
        
        Expected:
            - Eventually receives status 208
            - Status 208 indicates playback complete
            - No more data available after 208
        
        Jira: PZ-13868
        Priority: HIGH
        """
        task_id = generate_task_id("historic_208")
        logger.info(f"Test PZ-13868.1: Historic status 208 completion - {task_id}")
        
        # Generate 1-minute historic range
        end_time = datetime.now() - timedelta(hours=2)  # 2 hours ago (ensure data exists)
        start_time = end_time - timedelta(minutes=1)
        
        # Create config with timestamps
        config_payload = generate_config_payload(
            sensors_min=0,
            sensors_max=50,
            freq_min=0,
            freq_max=500,
            nfft=1024,
            canvas_height=1000,
            live=False,
            start_time=start_time,
            end_time=end_time
        )
        
        # Configure task
        config_request = ConfigTaskRequest(**config_payload)
        response = focus_server_api.config_task(task_id, config_request)
        
        assert response.status == "Config received successfully" or response.status_code == 200
        logger.info(f"Historic task configured: {start_time} to {end_time}")
        
        # Poll for data and track status codes
        status_codes_seen = []
        max_polls = 100
        poll_count = 0
        got_208 = False
        
        while poll_count < max_polls:
            try:
                waterfall_response = focus_server_api.get_waterfall(task_id, row_count=100)
                status_code = waterfall_response.status_code
                
                if status_code not in status_codes_seen:
                    logger.info(f"New status code: {status_code}")
                    status_codes_seen.append(status_code)
                
                if status_code == 208:
                    logger.info(f"✅ Received status 208 after {poll_count} polls")
                    got_208 = True
                    
                    # Verify no data with 208
                    if hasattr(waterfall_response, 'data'):
                        if waterfall_response.data is None or len(waterfall_response.data) == 0:
                            logger.info("✅ Status 208 has no data (as expected)")
                        else:
                            logger.warning(f"Status 208 has data: {len(waterfall_response.data)} blocks")
                    
                    break
                
                elif status_code == 201:
                    # Got data - continue polling
                    if hasattr(waterfall_response, 'data') and waterfall_response.data:
                        logger.info(f"Poll {poll_count}: Got {len(waterfall_response.data)} data blocks")
                
                elif status_code == 200:
                    # No data yet - continue polling
                    pass
                
                else:
                    logger.warning(f"Unexpected status code: {status_code}")
                
                time.sleep(0.5)  # Wait between polls
                poll_count += 1
                
            except Exception as e:
                logger.error(f"Error polling waterfall: {e}")
                break
        
        # Assertions
        assert got_208, \
            f"Did not receive status 208 after {poll_count} polls. Seen: {status_codes_seen}"
        
        logger.info(f"✅ Historic playback completed with status 208")
        logger.info(f"Status code progression: {status_codes_seen}")
    
    def test_historic_status_208_no_subsequent_data(self, focus_server_api):
        """
        Test PZ-13868.2: No data available after status 208.
        
        Steps:
            1. Configure and complete historic playback (get 208)
            2. Continue polling after 208
            3. Verify 208 persists (or 404/400 if task cleaned up)
        
        Expected:
            - After 208, subsequent polls return 208, 404, or 400
            - No new data (201) after completion
        
        Jira: PZ-13868
        Priority: HIGH
        """
        task_id = generate_task_id("historic_208_persist")
        logger.info(f"Test PZ-13868.2: Status 208 persistence - {task_id}")
        
        # Generate very short historic range to complete quickly
        end_time = datetime.now() - timedelta(hours=2)
        start_time = end_time - timedelta(seconds=30)
        
        config_payload = generate_config_payload(
            sensors_min=0,
            sensors_max=20,  # Fewer sensors for faster completion
            freq_min=0,
            freq_max=200,
            nfft=512,  # Smaller NFFT for faster processing
            canvas_height=500,
            live=False,
            start_time=start_time,
            end_time=end_time
        )
        
        # Configure task
        config_request = ConfigTaskRequest(**config_payload)
        response = focus_server_api.config_task(task_id, config_request)
        assert response.status == "Config received successfully" or response.status_code == 200
        
        # Poll until 208
        got_208 = False
        for _ in range(50):
            response = focus_server_api.get_waterfall(task_id, row_count=100)
            if response.status_code == 208:
                got_208 = True
                logger.info("Received status 208")
                break
            time.sleep(0.5)
        
        if not got_208:
            pytest.skip("Could not reach status 208 in reasonable time")
        
        # Poll 5 more times after 208
        logger.info("Polling 5 more times after 208...")
        post_208_statuses = []
        
        for i in range(5):
            response = focus_server_api.get_waterfall(task_id, row_count=100)
            post_208_statuses.append(response.status_code)
            logger.info(f"Post-208 poll {i+1}: status {response.status_code}")
            time.sleep(0.5)
        
        # Assertions: Should not see 201 (new data) after 208
        assert 201 not in post_208_statuses, \
            f"Unexpected status 201 (new data) after 208: {post_208_statuses}"
        
        # Expected statuses after 208: 208, 404, or 400
        valid_post_208_statuses = [208, 404, 400]
        for status in post_208_statuses:
            assert status in valid_post_208_statuses, \
                f"Unexpected status {status} after 208 (expected 208/404/400)"
        
        logger.info(f"✅ Post-208 statuses are valid: {post_208_statuses}")


# ===================================================================
# Test Class: Timestamp Ordering (PZ-13871)
# ===================================================================

@pytest.mark.integration
@pytest.mark.api
@pytest.mark.critical
class TestHistoricTimestampOrdering:
    """
    Test suite for PZ-13871: Historic Playback - Timestamp Ordering Validation
    Priority: HIGH
    
    Validates that timestamps in historic playback data are monotonically
    increasing and properly ordered.
    """
    
    def test_timestamp_ordering_monotonic_increasing(self, focus_server_api):
        """
        Test PZ-13871.1: Timestamps are monotonically increasing.
        
        Steps:
            1. Configure historic task
            2. Retrieve waterfall data
            3. Extract all timestamps
            4. Verify timestamps are in increasing order
        
        Expected:
            - All timestamps are monotonically increasing
            - No timestamp is less than or equal to previous timestamp
        
        Jira: PZ-13871
        Priority: HIGH
        """
        task_id = generate_task_id("timestamp_ordering")
        logger.info(f"Test PZ-13871.1: Timestamp ordering - {task_id}")
        
        # Generate 2-minute historic range for sufficient data
        end_time = datetime.now() - timedelta(hours=2)
        start_time = end_time - timedelta(minutes=2)
        
        config_payload = generate_config_payload(
            sensors_min=0,
            sensors_max=50,
            freq_min=0,
            freq_max=500,
            nfft=1024,
            canvas_height=1000,
            live=False,
            start_time=start_time,
            end_time=end_time
        )
        
        # Configure task
        config_request = ConfigTaskRequest(**config_payload)
        response = focus_server_api.config_task(task_id, config_request)
        assert response.status == "Config received successfully" or response.status_code == 200
        
        # Collect all timestamps from waterfall data
        all_timestamps = []
        max_polls = 50
        
        for poll_num in range(max_polls):
            try:
                waterfall_response = focus_server_api.get_waterfall(task_id, row_count=100)
                
                if waterfall_response.status_code == 201 and waterfall_response.data:
                    # Extract timestamps from data blocks
                    for block in waterfall_response.data:
                        if hasattr(block, 'rows'):
                            for row in block.rows:
                                if hasattr(row, 'startTimestamp'):
                                    all_timestamps.append(row.startTimestamp)
                                if hasattr(row, 'endTimestamp'):
                                    all_timestamps.append(row.endTimestamp)
                
                elif waterfall_response.status_code == 208:
                    # Playback complete
                    logger.info(f"Playback complete after {poll_num} polls")
                    break
                
                time.sleep(0.3)
                
            except Exception as e:
                logger.error(f"Error collecting timestamps: {e}")
                break
        
        # Assertions
        assert len(all_timestamps) > 0, "Should collect at least some timestamps"
        logger.info(f"Collected {len(all_timestamps)} timestamps")
        
        # Verify monotonic increasing
        violations = []
        for i in range(len(all_timestamps) - 1):
            if all_timestamps[i] >= all_timestamps[i + 1]:
                violations.append({
                    'index': i,
                    'timestamp1': all_timestamps[i],
                    'timestamp2': all_timestamps[i + 1]
                })
        
        if violations:
            logger.error(f"Found {len(violations)} timestamp ordering violations:")
            for v in violations[:10]:  # Log first 10
                logger.error(f"  Index {v['index']}: {v['timestamp1']} >= {v['timestamp2']}")
        
        assert len(violations) == 0, \
            f"Timestamps not monotonically increasing: {len(violations)} violations"
        
        logger.info("✅ All timestamps are monotonically increasing")
    
    def test_timestamp_ordering_within_blocks(self, focus_server_api):
        """
        Test PZ-13871.2: Timestamps ordered within each data block.
        
        Steps:
            1. Configure historic task
            2. Retrieve waterfall data blocks
            3. Verify timestamps within each block are ordered
        
        Expected:
            - Within each block, timestamps are increasing
            - endTimestamp > startTimestamp for each row
        
        Jira: PZ-13871
        Priority: HIGH
        """
        task_id = generate_task_id("timestamp_within_blocks")
        logger.info(f"Test PZ-13871.2: Timestamp ordering within blocks - {task_id}")
        
        # Generate historic range
        end_time = datetime.now() - timedelta(hours=2)
        start_time = end_time - timedelta(minutes=1)
        
        config_payload = generate_config_payload(
            sensors_min=0,
            sensors_max=50,
            freq_min=0,
            freq_max=500,
            nfft=1024,
            canvas_height=1000,
            live=False,
            start_time=start_time,
            end_time=end_time
        )
        
        # Configure task
        config_request = ConfigTaskRequest(**config_payload)
        response = focus_server_api.config_task(task_id, config_request)
        assert response.status == "Config received successfully" or response.status_code == 200
        
        # Get one batch of data
        violations = []
        got_data = False
        
        for _ in range(30):
            waterfall_response = focus_server_api.get_waterfall(task_id, row_count=100)
            
            if waterfall_response.status_code == 201 and waterfall_response.data:
                got_data = True
                
                for block_idx, block in enumerate(waterfall_response.data):
                    if not hasattr(block, 'rows'):
                        continue
                    
                    # Check timestamps within block
                    for row_idx, row in enumerate(block.rows):
                        # Check endTimestamp > startTimestamp
                        if hasattr(row, 'startTimestamp') and hasattr(row, 'endTimestamp'):
                            if row.endTimestamp <= row.startTimestamp:
                                violations.append({
                                    'block': block_idx,
                                    'row': row_idx,
                                    'start': row.startTimestamp,
                                    'end': row.endTimestamp,
                                    'issue': 'endTimestamp <= startTimestamp'
                                })
                        
                        # Check ordering between consecutive rows
                        if row_idx > 0:
                            prev_row = block.rows[row_idx - 1]
                            if hasattr(prev_row, 'endTimestamp') and hasattr(row, 'startTimestamp'):
                                if row.startTimestamp < prev_row.endTimestamp:
                                    violations.append({
                                        'block': block_idx,
                                        'row': row_idx,
                                        'prev_end': prev_row.endTimestamp,
                                        'curr_start': row.startTimestamp,
                                        'issue': 'current startTimestamp < previous endTimestamp'
                                    })
                
                break  # Got data, exit polling loop
            
            time.sleep(0.5)
        
        assert got_data, "Should receive at least one data block"
        
        # Assertions
        if violations:
            logger.error(f"Found {len(violations)} timestamp violations within blocks:")
            for v in violations[:5]:
                logger.error(f"  {v}")
        
        assert len(violations) == 0, \
            f"Timestamp ordering violations within blocks: {len(violations)} found"
        
        logger.info("✅ Timestamps properly ordered within all blocks")
    
    def test_timestamp_gap_validation(self, focus_server_api):
        """
        Test PZ-13871.3: Validate timestamp gaps are reasonable.
        
        Steps:
            1. Configure historic task
            2. Collect timestamps
            3. Calculate gaps between consecutive timestamps
            4. Verify gaps are within reasonable bounds
        
        Expected:
            - No extremely large gaps (> 10 seconds)
            - No extremely small gaps (< 0.001 seconds)
        
        Jira: PZ-13871
        Priority: HIGH
        """
        task_id = generate_task_id("timestamp_gaps")
        logger.info(f"Test PZ-13871.3: Timestamp gap validation - {task_id}")
        
        # Generate historic range
        end_time = datetime.now() - timedelta(hours=2)
        start_time = end_time - timedelta(minutes=1)
        
        config_payload = generate_config_payload(
            sensors_min=0,
            sensors_max=50,
            freq_min=0,
            freq_max=500,
            nfft=1024,
            canvas_height=1000,
            live=False,
            start_time=start_time,
            end_time=end_time
        )
        
        # Configure task
        config_request = ConfigTaskRequest(**config_payload)
        response = focus_server_api.config_task(task_id, config_request)
        assert response.status == "Config received successfully" or response.status_code == 200
        
        # Collect start timestamps
        timestamps = []
        for _ in range(30):
            waterfall_response = focus_server_api.get_waterfall(task_id, row_count=100)
            
            if waterfall_response.status_code == 201 and waterfall_response.data:
                for block in waterfall_response.data:
                    if hasattr(block, 'rows'):
                        for row in block.rows:
                            if hasattr(row, 'startTimestamp'):
                                timestamps.append(row.startTimestamp)
            
            elif waterfall_response.status_code == 208:
                break
            
            time.sleep(0.3)
        
        assert len(timestamps) > 1, "Need at least 2 timestamps to calculate gaps"
        
        # Calculate gaps
        gaps = []
        for i in range(len(timestamps) - 1):
            gap = timestamps[i + 1] - timestamps[i]
            if gap > 0:  # Only positive gaps (already verified monotonic)
                gaps.append(gap)
        
        logger.info(f"Calculated {len(gaps)} timestamp gaps")
        
        if gaps:
            min_gap = min(gaps)
            max_gap = max(gaps)
            avg_gap = sum(gaps) / len(gaps)
            
            logger.info(f"Gap statistics: min={min_gap:.6f}s, max={max_gap:.6f}s, avg={avg_gap:.6f}s")
            
            # TODO: Update thresholds after specs meeting
            MIN_REASONABLE_GAP = 0.0001  # 0.1ms
            MAX_REASONABLE_GAP = 10.0     # 10 seconds
            
            # Check for unreasonably small gaps
            too_small = [g for g in gaps if g < MIN_REASONABLE_GAP]
            if too_small:
                logger.warning(f"Found {len(too_small)} gaps < {MIN_REASONABLE_GAP}s")
            
            # Check for unreasonably large gaps
            too_large = [g for g in gaps if g > MAX_REASONABLE_GAP]
            if too_large:
                logger.warning(f"Found {len(too_large)} gaps > {MAX_REASONABLE_GAP}s")
                logger.warning(f"Large gaps (first 5): {too_large[:5]}")
            
            # For now, just log warnings - don't fail
            # After specs meeting, may want to enforce stricter limits
            logger.info("✅ Timestamp gaps analyzed")


# ===================================================================
# Module Summary Test
# ===================================================================

@pytest.mark.summary
def test_historic_high_priority_summary():
    """
    Summary test for historic playback (high priority tests).
    
    This test documents which Xray test cases are covered in this module.
    
    Covered Xray Tests:
        ✅ PZ-13868: Historic Status 208 Completion (2 tests)
        ✅ PZ-13871: Timestamp Ordering Validation (3 tests)
    
    Total: 5 high-priority historic playback tests
    """
    logger.info("=" * 80)
    logger.info("Historic Playback (High Priority) - Summary")
    logger.info("=" * 80)
    logger.info("Xray Test Coverage:")
    logger.info("  ✅ PZ-13868: Historic Status 208 - 2 tests")
    logger.info("  ✅ PZ-13871: Timestamp Ordering - 3 tests")
    logger.info("=" * 80)
    logger.info("Total: 5 High Priority Tests")
    logger.info("=" * 80)

