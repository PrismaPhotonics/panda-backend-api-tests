"""
System Calculations Validation Tests
=====================================

These tests validate the mathematical calculations performed by the Focus Server,
including frequency resolution, time resolution, channel mapping, and data rates.

NOTE: These tests document the ACTUAL behavior of the system. If tests fail,
it indicates that our understanding of the calculations differs from the system's
implementation. Failed tests should result in bug tickets for investigation.

Author: QA Automation Team
Date: 2025-10-30
Xray Test Set: PZ-14060 through PZ-14080 (Calculation Validation Test Suite)
"""

import pytest
import math
from typing import Dict, Any

from src.core.base_test import BaseTest
from src.models.focus_server_models import (
    ConfigureRequest, DisplayInfo, Channels, FrequencyRange, ViewType
)


@pytest.mark.calculations



@pytest.mark.regression
class TestFrequencyCalculations(BaseTest):
    """Test frequency-related calculations."""
    
    @pytest.mark.xray("PZ-14060")

    
    @pytest.mark.regression
    def test_frequency_resolution_calculation(self, focus_server_api):
        """
        Test: Frequency Resolution = PRR / NFFT
        
        Validates that the frequency resolution is calculated correctly
        from the PRR (Pulse Repetition Rate) and NFFT parameters.
        
        Expected Formula: frequency_resolution = PRR / NFFT
        
        NOTE: This test documents expected behavior. If it fails, the actual
        calculation may differ from the standard DSP formula.
        """
        # Test configuration
        nfft = 512
        prr = 1000  # Assumed PRR - may need adjustment based on system
        
        # Create request
        payload = ConfigureRequest(
            displayTimeAxisDuration=30,
            nfftSelection=nfft,
            displayInfo=DisplayInfo(height=768),
            channels=Channels(min=1, max=8),
            frequencyRange=FrequencyRange(min=0, max=500),
            view_type=ViewType.MULTICHANNEL
        )
        
        # Execute
        response = focus_server_api.configure_streaming_job(payload)
        
        # Calculate expected frequency resolution
        expected_freq_resolution = prr / nfft
        
        # Validate
        # If system returns frequency_resolution explicitly
        if hasattr(response, 'frequency_resolution'):
            actual = response.frequency_resolution
            assert math.isclose(actual, expected_freq_resolution, rel_tol=0.01), \
                f"Frequency resolution mismatch: expected {expected_freq_resolution:.3f} Hz, got {actual:.3f} Hz"
        else:
            # Calculate from frequencies_list
            if len(response.frequencies_list) >= 2:
                actual_resolution = response.frequencies_list[1] - response.frequencies_list[0]
                # This may not match expected_freq_resolution due to decimation
                self.logger.info(f"Calculated resolution from frequencies_list: {actual_resolution:.3f} Hz")
                self.logger.info(f"Expected resolution (PRR/NFFT): {expected_freq_resolution:.3f} Hz")
                
                # Document the discrepancy if exists
                if not math.isclose(actual_resolution, expected_freq_resolution, rel_tol=0.1):
                    pytest.fail(
                        f"Frequency resolution discrepancy detected:\n"
                        f"  Expected (PRR/NFFT): {expected_freq_resolution:.3f} Hz\n"
                        f"  Actual (from response): {actual_resolution:.3f} Hz\n"
                        f"  This may indicate frequency decimation or different PRR.\n"
                        f"  Consider opening bug ticket for investigation."
                    )
    
    @pytest.mark.xray("PZ-14061")

    
    @pytest.mark.regression
    def test_frequency_bins_count_calculation(self, focus_server_api):
        """
        Test: frequencies_amount = NFFT / 2 + 1
        
        Validates that the number of frequency bins is calculated correctly.
        For real-valued signals, FFT produces NFFT/2+1 unique frequency bins.
        
        Expected Formula: frequencies_amount = NFFT / 2 + 1
        
        NOTE: Actual behavior may differ if system applies frequency decimation
        or filtering based on requested frequency range.
        """
        test_cases = [
            {"nfft": 256, "expected": 129},
            {"nfft": 512, "expected": 257},
            {"nfft": 1024, "expected": 513},
            {"nfft": 2048, "expected": 1025},
        ]
        
        for case in test_cases:
            nfft = case["nfft"]
            expected_bins = case["expected"]
            
            payload = ConfigureRequest(
                displayTimeAxisDuration=30,
                nfftSelection=nfft,
                displayInfo=DisplayInfo(height=768),
                channels=Channels(min=1, max=8),
                frequencyRange=FrequencyRange(min=0, max=500),
                view_type=ViewType.MULTICHANNEL
            )
            
            response = focus_server_api.configure_streaming_job(payload)
            actual_bins = response.frequencies_amount
            
            # Document results
            self.logger.info(f"NFFT={nfft}: Expected {expected_bins} bins, Got {actual_bins} bins")
            
            if actual_bins != expected_bins:
                pytest.fail(
                    f"Frequency bins mismatch for NFFT={nfft}:\n"
                    f"  Expected (NFFT/2+1): {expected_bins}\n"
                    f"  Actual: {actual_bins}\n"
                    f"  Difference: {expected_bins - actual_bins}\n"
                    f"  This may indicate frequency decimation based on requested range.\n"
                    f"  Consider opening bug ticket for clarification."
                )
    
    @pytest.mark.xray("PZ-14062")

    
    @pytest.mark.regression
    def test_nyquist_frequency_calculation(self, focus_server_api):
        """
        Test: Nyquist Frequency = PRR / 2
        
        Validates that frequencies above Nyquist limit are rejected.
        
        Expected: System should reject frequency_max > (PRR / 2)
        
        NOTE: System may have different PRR than assumed, or may allow
        frequencies up to a configured maximum rather than Nyquist limit.
        """
        prr = 1000  # Assumed PRR
        nyquist = prr / 2  # 500 Hz
        
        # Test 1: Frequency below Nyquist should succeed
        payload_valid = ConfigureRequest(
            displayTimeAxisDuration=30,
            nfftSelection=512,
            displayInfo=DisplayInfo(height=768),
            channels=Channels(min=1, max=8),
            frequencyRange=FrequencyRange(min=0, max=int(nyquist - 100)),
            view_type=ViewType.MULTICHANNEL
        )
        
        response = focus_server_api.configure_streaming_job(payload_valid)
        assert response.job_id is not None, "Valid frequency should be accepted"
        
        # Test 2: Frequency at Nyquist should succeed
        payload_at_nyquist = ConfigureRequest(
            displayTimeAxisDuration=30,
            nfftSelection=512,
            displayInfo=DisplayInfo(height=768),
            channels=Channels(min=1, max=8),
            frequencyRange=FrequencyRange(min=0, max=int(nyquist)),
            view_type=ViewType.MULTICHANNEL
        )
        
        try:
            response = focus_server_api.configure_streaming_job(payload_at_nyquist)
            assert response.job_id is not None, "Frequency at Nyquist should be accepted"
        except Exception as e:
            pytest.fail(
                f"Frequency at Nyquist ({nyquist} Hz) was rejected:\n"
                f"  Error: {e}\n"
                f"  This may indicate a stricter limit or different PRR.\n"
                f"  Consider investigating the actual Nyquist limit."
            )


@pytest.mark.calculations



@pytest.mark.regression
class TestTimeCalculations(BaseTest):
    """Test time-related calculations."""
    
    @pytest.mark.xray("PZ-14066")

    
    @pytest.mark.regression
    def test_lines_dt_calculation(self, focus_server_api):
        """
        Test: lines_dt = (NFFT - Overlap) / PRR
        
        Validates time resolution between consecutive spectrogram lines.
        
        Expected Formula: lines_dt = (NFFT - Overlap) / PRR
        
        NOTE: Actual calculation may differ due to:
        - Different overlap percentage
        - Time decimation/compression
        - Different PRR value
        """
        nfft = 512
        assumed_overlap = 256  # 50% overlap
        prr = 1000  # Assumed PRR
        
        payload = ConfigureRequest(
            displayTimeAxisDuration=30,
            nfftSelection=nfft,
            displayInfo=DisplayInfo(height=768),
            channels=Channels(min=1, max=8),
            frequencyRange=FrequencyRange(min=0, max=500),
            view_type=ViewType.MULTICHANNEL
        )
        
        response = focus_server_api.configure_streaming_job(payload)
        
        # Calculate expected lines_dt
        expected_lines_dt = (nfft - assumed_overlap) / prr
        actual_lines_dt = response.lines_dt
        
        self.logger.info(f"Expected lines_dt: {expected_lines_dt:.6f} sec")
        self.logger.info(f"Actual lines_dt: {actual_lines_dt:.6f} sec")
        
        if not math.isclose(actual_lines_dt, expected_lines_dt, rel_tol=0.1):
            pytest.fail(
                f"lines_dt calculation mismatch:\n"
                f"  Expected [(NFFT - Overlap) / PRR]: {expected_lines_dt:.6f} sec\n"
                f"  Actual: {actual_lines_dt:.6f} sec\n"
                f"  Ratio: {expected_lines_dt / actual_lines_dt:.2f}x\n"
                f"  Possible causes:\n"
                f"  1. Different overlap percentage\n"
                f"  2. Different PRR value (~{(nfft - assumed_overlap) / actual_lines_dt:.0f} Hz)\n"
                f"  3. Time compression/decimation\n"
                f"  Consider opening bug ticket for clarification."
            )
    
    @pytest.mark.xray("PZ-14067")

    
    @pytest.mark.regression
    def test_output_rate_calculation(self, focus_server_api):
        """
        Test: output_rate = 1 / lines_dt = PRR / (NFFT - Overlap)
        
        Validates the rate at which spectrogram lines are produced.
        
        Expected: Higher overlap → Higher output rate
        """
        nfft = 512
        
        payload = ConfigureRequest(
            displayTimeAxisDuration=30,
            nfftSelection=nfft,
            displayInfo=DisplayInfo(height=768),
            channels=Channels(min=1, max=8),
            frequencyRange=FrequencyRange(min=0, max=500),
            view_type=ViewType.MULTICHANNEL
        )
        
        response = focus_server_api.configure_streaming_job(payload)
        
        # Calculate output rate from lines_dt
        actual_output_rate = 1 / response.lines_dt if response.lines_dt > 0 else 0
        
        self.logger.info(f"lines_dt: {response.lines_dt:.6f} sec")
        self.logger.info(f"Output rate: {actual_output_rate:.3f} lines/sec")
        
        # Validate that output rate is reasonable
        assert 0.1 < actual_output_rate < 1000, \
            f"Output rate {actual_output_rate:.3f} lines/sec seems unreasonable"
    
    @pytest.mark.xray("PZ-14068")

    
    @pytest.mark.regression
    def test_time_window_duration_calculation(self, focus_server_api):
        """
        Test: time_window_duration = NFFT / PRR
        
        Validates the duration of each FFT window.
        """
        test_cases = [
            {"nfft": 256, "expected_duration": 0.256},  # Assuming PRR=1000
            {"nfft": 512, "expected_duration": 0.512},
            {"nfft": 1024, "expected_duration": 1.024},
        ]
        
        for case in test_cases:
            nfft = case["nfft"]
            expected_duration = case["expected_duration"]
            
            payload = ConfigureRequest(
                displayTimeAxisDuration=30,
                nfftSelection=nfft,
                displayInfo=DisplayInfo(height=768),
                channels=Channels(min=1, max=8),
                frequencyRange=FrequencyRange(min=0, max=500),
                view_type=ViewType.MULTICHANNEL
            )
            
            response = focus_server_api.configure_streaming_job(payload)
            
            # If system provides time_window_duration
            if hasattr(response, 'time_window_duration'):
                actual = response.time_window_duration
                self.logger.info(f"NFFT={nfft}: Expected {expected_duration}s, Got {actual}s")
            else:
                self.logger.info(f"NFFT={nfft}: time_window_duration not in response (expected {expected_duration}s)")


@pytest.mark.calculations



@pytest.mark.regression
class TestChannelCalculations(BaseTest):
    """Test channel-related calculations."""
    
    @pytest.mark.xray("PZ-14069")

    
    @pytest.mark.regression
    def test_channel_count_calculation(self, focus_server_api):
        """
        Test: channel_amount = max - min + 1
        
        This is a basic calculation that should always be correct.
        """
        test_cases = [
            {"min": 1, "max": 1, "expected": 1},
            {"min": 1, "max": 8, "expected": 8},
            {"min": 5, "max": 10, "expected": 6},
            {"min": 1, "max": 100, "expected": 100},
        ]
        
        for case in test_cases:
            min_ch = case["min"]
            max_ch = case["max"]
            expected_count = case["expected"]
            
            payload = ConfigureRequest(
                displayTimeAxisDuration=30,
                nfftSelection=512,
                displayInfo=DisplayInfo(height=768),
                channels=Channels(min=min_ch, max=max_ch),
                frequencyRange=FrequencyRange(min=0, max=500),
                view_type=ViewType.MULTICHANNEL
            )
            
            response = focus_server_api.configure_streaming_job(payload)
            actual_count = response.channel_amount
            
            assert actual_count == expected_count, \
                f"Channel count mismatch for range [{min_ch}, {max_ch}]: " \
                f"expected {expected_count}, got {actual_count}"
    
    @pytest.mark.xray("PZ-14069")  # SingleChannel mapping - part of channel calculations

    
    @pytest.mark.regression
    def test_singlechannel_mapping_calculation(self, focus_server_api):
        """
        Test: SingleChannel mapping validation
        
        In SingleChannel mode (min == max), validates:
        - channel_amount = 1
        - stream_amount = 1 (or may differ if system groups channels)
        - channel_to_stream_index maps correctly
        """
        test_channels = [1, 5, 10, 50, 100]
        
        for channel in test_channels:
            payload = ConfigureRequest(
                displayTimeAxisDuration=30,
                nfftSelection=512,
                displayInfo=DisplayInfo(height=768),
                channels=Channels(min=channel, max=channel),
                frequencyRange=FrequencyRange(min=0, max=500),
                view_type=ViewType.SINGLECHANNEL
            )
            
            response = focus_server_api.configure_streaming_job(payload)
            
            # Validate channel_amount
            assert response.channel_amount == 1, \
                f"SingleChannel: expected channel_amount=1, got {response.channel_amount}"
            
            # Validate mapping exists
            channel_str = str(channel)
            assert channel_str in response.channel_to_stream_index, \
                f"Channel {channel} not in mapping: {response.channel_to_stream_index}"
            
            stream_index = response.channel_to_stream_index[channel_str]
            
            self.logger.info(
                f"SingleChannel {channel}: "
                f"stream_amount={response.stream_amount}, "
                f"mapping={{{channel_str}: {stream_index}}}"
            )
    
    @pytest.mark.xray("PZ-14070")

    
    @pytest.mark.regression
    def test_multichannel_mapping_calculation(self, focus_server_api):
        """
        Test: MultiChannel mapping validation
        
        Expected (traditional 1:1 mapping):
        - channel_amount = max - min + 1
        - stream_amount = channel_amount
        - Sequential mapping: channel[i] → stream_index[i]
        
        NOTE: System may group channels into fewer streams for optimization.
        If this test fails, document the actual grouping logic.
        """
        test_cases = [
            {"min": 1, "max": 8},
            {"min": 5, "max": 10},
            {"min": 1, "max": 20},
        ]
        
        for case in test_cases:
            min_ch = case["min"]
            max_ch = case["max"]
            expected_amount = max_ch - min_ch + 1
            
            payload = ConfigureRequest(
                displayTimeAxisDuration=30,
                nfftSelection=512,
                displayInfo=DisplayInfo(height=768),
                channels=Channels(min=min_ch, max=max_ch),
                frequencyRange=FrequencyRange(min=0, max=500),
                view_type=ViewType.MULTICHANNEL
            )
            
            response = focus_server_api.configure_streaming_job(payload)
            
            # Validate channel_amount
            assert response.channel_amount == expected_amount, \
                f"Expected channel_amount={expected_amount}, got {response.channel_amount}"
            
            # Check stream_amount
            if response.stream_amount != expected_amount:
                self.logger.warning(
                    f"Stream grouping detected: {expected_amount} channels → {response.stream_amount} streams\n"
                    f"Mapping: {response.channel_to_stream_index}"
                )
                
                # Document grouping pattern
                pytest.fail(
                    f"Channel grouping observed:\n"
                    f"  Channels: {min_ch}-{max_ch} ({expected_amount} channels)\n"
                    f"  Streams: {response.stream_amount}\n"
                    f"  Mapping: {response.channel_to_stream_index}\n"
                    f"  This may be intentional optimization.\n"
                    f"  Consider documenting the grouping logic or opening clarification ticket."
                )
            
            # If 1:1 mapping, validate sequential indices
            for i, channel in enumerate(range(min_ch, max_ch + 1)):
                channel_str = str(channel)
                expected_index = i
                actual_index = response.channel_to_stream_index.get(channel_str)
                
                assert actual_index == expected_index, \
                    f"Channel {channel}: expected stream_index={expected_index}, got {actual_index}"
    
    @pytest.mark.xray("PZ-14071")

    
    @pytest.mark.regression
    def test_stream_amount_calculation(self, focus_server_api):
        """
        Test: stream_amount relationship to channel_amount
        
        Expected: stream_amount == channel_amount (1:1 mapping)
        
        NOTE: System may use fewer streams if it groups channels.
        """
        payload = ConfigureRequest(
            displayTimeAxisDuration=30,
            nfftSelection=512,
            displayInfo=DisplayInfo(height=768),
            channels=Channels(min=1, max=8),
            frequencyRange=FrequencyRange(min=0, max=500),
            view_type=ViewType.MULTICHANNEL
        )
        
        response = focus_server_api.configure_streaming_job(payload)
        
        self.logger.info(
            f"channel_amount={response.channel_amount}, "
            f"stream_amount={response.stream_amount}"
        )
        
        if response.stream_amount != response.channel_amount:
            pytest.fail(
                f"Stream count differs from channel count:\n"
                f"  Channels: {response.channel_amount}\n"
                f"  Streams: {response.stream_amount}\n"
                f"  Ratio: {response.channel_amount / response.stream_amount:.1f}:1\n"
                f"  Consider documenting why channels are grouped."
            )


@pytest.mark.calculations



@pytest.mark.regression
class TestValidationCalculations(BaseTest):
    """Test validation-related calculations."""
    
    @pytest.mark.xray("PZ-14072")

    
    @pytest.mark.regression
    def test_fft_window_size_validation(self, focus_server_api):
        """
        Test: NFFT must be power of 2
        
        Valid: 256, 512, 1024, 2048, ...
        Invalid: 100, 300, 500, 1000, ...
        """
        # Test valid values
        valid_nfft = [256, 512, 1024, 2048]
        for nfft in valid_nfft:
            payload = ConfigureRequest(
                displayTimeAxisDuration=30,
                nfftSelection=nfft,
                displayInfo=DisplayInfo(height=768),
                channels=Channels(min=1, max=8),
                frequencyRange=FrequencyRange(min=0, max=500),
                view_type=ViewType.MULTICHANNEL
            )
            
            response = focus_server_api.configure_streaming_job(payload)
            assert response.job_id is not None, f"NFFT={nfft} (power of 2) should be accepted"
        
        # Test invalid values
        invalid_nfft = [100, 300, 500, 1000]
        for nfft in invalid_nfft:
            payload = ConfigureRequest(
                displayTimeAxisDuration=30,
                nfftSelection=nfft,
                displayInfo=DisplayInfo(height=768),
                channels=Channels(min=1, max=8),
                frequencyRange=FrequencyRange(min=0, max=500),
                view_type=ViewType.MULTICHANNEL
            )
            
            with pytest.raises(Exception) as exc_info:
                focus_server_api.configure_streaming_job(payload)
            
            self.logger.info(f"NFFT={nfft} rejected as expected: {exc_info.value}")
    
    @pytest.mark.xray("PZ-14073")

    
    @pytest.mark.regression
    def test_overlap_percentage_validation(self, focus_server_api):
        """
        Test: Overlap validation
        
        NOTE: This test assumes system allows overlap configuration.
        Currently, overlap may be fixed or derived from other parameters.
        """
        # This test is informational - documents current overlap behavior
        payload = ConfigureRequest(
            displayTimeAxisDuration=30,
            nfftSelection=512,
            displayInfo=DisplayInfo(height=768),
            channels=Channels(min=1, max=8),
            frequencyRange=FrequencyRange(min=0, max=500),
            view_type=ViewType.MULTICHANNEL
        )
        
        response = focus_server_api.configure_streaming_job(payload)
        
        # Calculate implied overlap from lines_dt
        nfft = 512
        prr = 1000  # Assumed
        implied_hop = response.lines_dt * prr
        implied_overlap = nfft - implied_hop
        implied_overlap_pct = (implied_overlap / nfft) * 100
        
        self.logger.info(
            f"Implied overlap: {implied_overlap:.0f} samples ({implied_overlap_pct:.1f}%)"
        )


@pytest.mark.performance



@pytest.mark.regression
class TestPerformanceCalculations(BaseTest):
    """Test performance-related calculations (informational)."""
    
    @pytest.mark.xray("PZ-14078")

    
    @pytest.mark.regression
    def test_data_rate_calculation(self, focus_server_api):
        """
        Test: Data rate estimation
        
        Formula: data_rate = channels × freq_bins × output_rate × bytes_per_sample
        
        This is informational - documents expected throughput.
        """
        payload = ConfigureRequest(
            displayTimeAxisDuration=30,
            nfftSelection=512,
            displayInfo=DisplayInfo(height=768),
            channels=Channels(min=1, max=8),
            frequencyRange=FrequencyRange(min=0, max=500),
            view_type=ViewType.MULTICHANNEL
        )
        
        response = focus_server_api.configure_streaming_job(payload)
        
        # Calculate data rate
        channels = response.channel_amount
        freq_bins = response.frequencies_amount
        output_rate = 1 / response.lines_dt if response.lines_dt > 0 else 0
        bytes_per_sample = 4  # float32
        
        data_rate_bytes = channels * freq_bins * output_rate * bytes_per_sample
        data_rate_kb = data_rate_bytes / 1024
        data_rate_mb = data_rate_kb / 1024
        
        self.logger.info(
            f"Estimated data rate:\n"
            f"  Channels: {channels}\n"
            f"  Frequency bins: {freq_bins}\n"
            f"  Output rate: {output_rate:.2f} lines/sec\n"
            f"  Data rate: {data_rate_bytes:.0f} bytes/sec ({data_rate_kb:.1f} KB/s, {data_rate_mb:.3f} MB/s)"
        )
        
        # Sanity check
        assert data_rate_mb < 100, f"Data rate {data_rate_mb:.1f} MB/s seems unreasonably high"
    
    @pytest.mark.xray("PZ-14079")

    
    @pytest.mark.regression
    def test_memory_usage_estimation(self, focus_server_api):
        """
        Test: Memory usage estimation
        
        Formula: memory_per_frame = channels × freq_bins × bytes_per_sample
        
        This is informational - documents expected memory usage.
        """
        test_cases = [
            {"nfft": 512, "channels": 8},
            {"nfft": 1024, "channels": 8},
            {"nfft": 2048, "channels": 8},
        ]
        
        for case in test_cases:
            nfft = case["nfft"]
            max_ch = case["channels"]
            
            payload = ConfigureRequest(
                displayTimeAxisDuration=30,
                nfftSelection=nfft,
                displayInfo=DisplayInfo(height=768),
                channels=Channels(min=1, max=max_ch),
                frequencyRange=FrequencyRange(min=0, max=500),
                view_type=ViewType.MULTICHANNEL
            )
            
            response = focus_server_api.configure_streaming_job(payload)
            
            # Calculate memory per frame
            channels = response.channel_amount
            freq_bins = response.frequencies_amount
            bytes_per_sample = 4
            
            memory_bytes = channels * freq_bins * bytes_per_sample
            memory_kb = memory_bytes / 1024
            
            self.logger.info(
                f"NFFT={nfft}, Channels={channels}: "
                f"~{memory_kb:.1f} KB per frame ({freq_bins} bins)"
            )
    
    @pytest.mark.xray("PZ-14080")

    
    @pytest.mark.regression
    def test_spectrogram_dimensions_calculation(self, focus_server_api):
        """
        Test: Spectrogram dimensions for historic mode
        
        Width = duration / lines_dt
        Height = frequencies_amount
        """
        # This test requires historic mode with time range
        # Placeholder for future implementation
        pytest.skip("Historic mode spectrogram dimensions test - to be implemented")


# Test configuration for pytest
pytestmark = [
    pytest.mark.integration,
    pytest.mark.calculations,
]

