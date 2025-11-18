"""
Integration Tests - Configuration Validation (NFFT & Frequency Range)
======================================================================

⚠️  SCOPE REFINED - 2025-10-27
--------------------------------------
Following meeting decision (PZ-13756), this file focuses on:
- ✅ IN SCOPE: Configuration validation (NFFT, frequency, channels)
- ✅ IN SCOPE: Pre-launch validations
- ✅ IN SCOPE: Predictable error handling
- ❌ OUT OF SCOPE: Spectrogram content validation (removed)
- ❌ OUT OF SCOPE: Baby processing validation (removed)

⚠️  MIGRATED TO OLD API - 2025-10-23
These tests have been MIGRATED to work with POST /configure API.

Test Flow:
    1. Validate NFFT configuration parameters
    2. Validate frequency range against Nyquist limit
    3. Validate configuration compatibility
    4. Test predictable error handling

Author: QA Automation Architect
Date: 2025-10-07
Last Updated: 2025-10-27 (SCOPE REFINED)
"""

import pytest
import logging
from typing import Dict, Any

from src.models.focus_server_models import ConfigureRequest, ConfigureResponse, ViewType
from src.utils.validators import (
    validate_nfft_value,
    validate_frequency_range,
    validate_configuration_compatibility
)

logger = logging.getLogger(__name__)


# ===================================================================
# NFFT Configuration Tests
# ===================================================================

@pytest.mark.api


@pytest.mark.regression
class TestNFFTConfiguration:
    """Test suite for NFFT parameter validation and configuration."""
    
    @pytest.mark.xray("PZ-13873")

    
    @pytest.mark.regression
    def test_valid_nfft_power_of_2(self, focus_server_api):
        """Test: Configure with valid NFFT (power of 2).
        
        PZ-13873: integration - Valid Configuration - All Parameters"""
        logger.info(f"Test: NFFT=256 configuration")
        
        # Validate NFFT
        assert validate_nfft_value(256)
        
        # Configure with NFFT=256 (POST /configure format)
        payload = {
            "displayTimeAxisDuration": 30,
            "nfftSelection": 256,
            "displayInfo": {"height": 1000},
            "channels": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        config_request = ConfigureRequest(**payload)
        response = focus_server_api.configure_streaming_job(config_request)
        
        assert hasattr(response, 'job_id') and response.job_id
        logger.info("✅ NFFT=256 configuration successful")
    
    @pytest.mark.xray("PZ-13873")

    
    @pytest.mark.regression
    def test_nfft_variations(self, focus_server_api):
        """Test: Various valid NFFT values."""
        nfft_values = [128, 256, 512, 1024, 2048, 4096]
        
        for nfft in nfft_values:
            logger.info(f"Testing NFFT={nfft}")
            
            assert validate_nfft_value(nfft)
            
            # Configure with this NFFT (POST /configure format)
            payload = {
                "displayTimeAxisDuration": 30,
                "nfftSelection": nfft,
                "displayInfo": {"height": 1000},
                "channels": {"min": 1, "max": 50},
                "frequencyRange": {"min": 0, "max": 500},
                "start_time": None,
                "end_time": None,
                "view_type": ViewType.MULTICHANNEL
            }
            config_request = ConfigureRequest(**payload)
            response = focus_server_api.configure_streaming_job(config_request)
            
            assert hasattr(response, 'job_id') and response.job_id
        
        logger.info(f"✅ All {len(nfft_values)} NFFT values tested successfully")
    
    @pytest.mark.xray("PZ-13901")

    
    @pytest.mark.regression
    def test_nfft_non_power_of_2(self, focus_server_api):
        """Test: Configure with non-power-of-2 NFFT (with warning).
        
        PZ-13901: Integration - NFFT Values Validation - All Supported Values"""
        nfft = 1000  # Not power of 2
        
        logger.info(f"Test: NFFT={nfft} (not power of 2)")
        
        # Validation should pass but with warning
        with pytest.warns(UserWarning):
            validate_nfft_value(nfft)
        
        # Configuration may still succeed (POST /configure format)
        payload = {
            "displayTimeAxisDuration": 30,
            "nfftSelection": nfft,
            "displayInfo": {"height": 1000},
            "channels": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        config_request = ConfigureRequest(**payload)
        response = focus_server_api.configure_streaming_job(config_request)
        
        assert hasattr(response, 'job_id') and response.job_id
        logger.info("✅ Non-power-of-2 NFFT accepted with warning")


# ===================================================================
# Frequency Range Tests
# ===================================================================

@pytest.mark.api


@pytest.mark.regression
class TestFrequencyRangeConfiguration:
    """Test suite for frequency range configuration."""
    
    @pytest.mark.xray("PZ-14100")

    
    @pytest.mark.regression
    def test_frequency_range_within_nyquist(self, focus_server_api, live_metadata):
        """Test: Frequency range within Nyquist limit.
        
        PZ-13902: Integration - Frequency Range Within Nyquist Limit"""
        # Get PRR from metadata
        prr = live_metadata.prr
        nyquist = prr / 2
        
        logger.info(f"Test: Frequency range with PRR={prr}, Nyquist={nyquist}")
        
        # Configure with frequency range below Nyquist
        freq_max = int(nyquist * 0.8)  # 80% of Nyquist
        
        # Validate frequency range
        assert validate_frequency_range(
            min_freq=0,
            max_freq=freq_max,
            prr=prr
        )
        
        # Configure (POST /configure format)
        payload = {
            "displayTimeAxisDuration": 30,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": freq_max},
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        config_request = ConfigureRequest(**payload)
        response = focus_server_api.configure_streaming_job(config_request)
        
        assert hasattr(response, 'job_id') and response.job_id
        logger.info(f"✅ Frequency range [0, {freq_max}] configured successfully")
    
    @pytest.mark.xray("PZ-13819", "PZ-13904")

    
    @pytest.mark.regression
    def test_frequency_range_variations(self, focus_server_api):
        """Test: Various frequency ranges.
        
        PZ-13819: API – SingleChannel View with Various Frequency Ranges
        PZ-13904: Integration - Frequency Range Variations"""
        frequency_ranges = [
            (0, 100),
            (0, 250),
            (0, 500),
            (100, 300),
            (200, 600)
        ]
        
        for freq_min, freq_max in frequency_ranges:
            logger.info(f"Testing frequency range [{freq_min}, {freq_max}]")
            
            # Configure (POST /configure format)
            payload = {
                "displayTimeAxisDuration": 30,
                "nfftSelection": 1024,
                "displayInfo": {"height": 1000},
                "channels": {"min": 1, "max": 50},
                "frequencyRange": {"min": freq_min, "max": freq_max},
                "start_time": None,
                "end_time": None,
                "view_type": ViewType.MULTICHANNEL
            }
            
            config_request = ConfigureRequest(**payload)
            response = focus_server_api.configure_streaming_job(config_request)
            
            assert hasattr(response, 'job_id') and response.job_id
        
        logger.info(f"✅ All {len(frequency_ranges)} frequency ranges tested")


# ===================================================================
# Configuration Compatibility Tests
# ===================================================================

@pytest.mark.api


@pytest.mark.regression
class TestConfigurationCompatibility:
    """Test suite for configuration parameter compatibility."""
    
    @pytest.mark.regression
def test_configuration_resource_estimation(self, focus_server_api):
        """Test: Estimate resource usage for configuration."""
        logger.info("Test: Configuration resource estimation")
        
        # Test configuration
        nfft = 1024
        sensor_range = 100
        prr = 2000.0
        
        # Validate compatibility
        compat_result = validate_configuration_compatibility(
            nfft=nfft,
            sensor_range=sensor_range,
            prr=prr,
            expected_throughput_mbps=10.0
        )
        
        logger.info(f"Compatibility result: {compat_result}")
        logger.info(f"  - Spectrogram rate: {compat_result['estimates']['spectrogram_rows_per_sec']:.2f} rows/sec")
        logger.info(f"  - Output data rate: {compat_result['estimates']['output_data_rate_mbps']:.2f} Mbps")
        
        assert compat_result["is_compatible"]
        logger.info("✅ Configuration compatible")
    
    @pytest.mark.xray("PZ-13905")

    
    @pytest.mark.regression
    def test_high_throughput_configuration(self, focus_server_api):
        """Test: Configuration with high throughput.
        
        PZ-13905: Integration - High Throughput Configuration"""
        logger.info(f"Test: High throughput configuration")
        
        # Check compatibility
        compat_result = validate_configuration_compatibility(
            nfft=256,
            sensor_range=200,
            prr=2000.0
        )
        
        logger.info(f"Expected output rate: {compat_result['estimates']['output_data_rate_mbps']:.2f} Mbps")
        
        if len(compat_result["warnings"]) > 0:
            logger.warning(f"Configuration warnings: {compat_result['warnings']}")
        
        # High throughput config (POST /configure format)
        payload = {
            "displayTimeAxisDuration": 30,
            "nfftSelection": 256,  # Small NFFT = high output rate
            "displayInfo": {"height": 1000},
            "channels": {"min": 1, "max": 200},  # Large sensor range
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        config_request = ConfigureRequest(**payload)
        response = focus_server_api.configure_streaming_job(config_request)
        
        assert hasattr(response, 'job_id') and response.job_id
        logger.info("✅ High throughput configuration accepted")
    
    @pytest.mark.xray("PZ-13906")

    
    @pytest.mark.regression
    def test_low_throughput_configuration(self, focus_server_api):
        """Test: Configuration with low throughput.
        
        PZ-13906: Integration - Low Throughput Configuration Edge Case"""
        logger.info(f"Test: Low throughput configuration")
        
        # Check compatibility
        compat_result = validate_configuration_compatibility(
            nfft=4096,
            sensor_range=20,
            prr=2000.0
        )
        
        logger.info(f"Expected output rate: {compat_result['estimates']['output_data_rate_mbps']:.2f} Mbps")
        
        # Low throughput config (POST /configure format)
        payload = {
            "displayTimeAxisDuration": 30,
            "nfftSelection": 4096,  # Large NFFT = low output rate
            "displayInfo": {"height": 1000},
            "channels": {"min": 1, "max": 20},  # Small sensor range
            "frequencyRange": {"min": 0, "max": 100},
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        config_request = ConfigureRequest(**payload)
        response = focus_server_api.configure_streaming_job(config_request)
        
        assert hasattr(response, 'job_id') and response.job_id
        logger.info("✅ Low throughput configuration accepted")


# ===================================================================
# Error Handling Tests
# ===================================================================

@pytest.mark.api


@pytest.mark.regression
class TestSpectrogramPipelineErrors:
    """Test suite for spectrogram pipeline error handling."""
    
    @pytest.mark.xray("PZ-13874")

    
    @pytest.mark.regression
    def test_zero_nfft(self, focus_server_api):
        """Test: Configure with NFFT=0.
        
        PZ-13874: Integration - Invalid NFFT - Zero Value"""
        logger.info("Test: NFFT=0 validation")
        
        with pytest.raises(Exception) as exc_info:
            validate_nfft_value(0)
        
        assert "positive" in str(exc_info.value).lower()
        logger.info(f"✅ NFFT=0 rejected: {exc_info.value}")
    
    @pytest.mark.xray("PZ-13875")
    @pytest.mark.xray("PZ-13555")

    @pytest.mark.regression
    def test_negative_nfft(self, focus_server_api):
        """Test: Configure with negative NFFT."""
        logger.info("Test: Negative NFFT")
        
        with pytest.raises(Exception) as exc_info:
            validate_nfft_value(-512)
        
        assert "positive" in str(exc_info.value).lower()
        logger.info(f"✅ Negative NFFT rejected: {exc_info.value}")


# ===================================================================
# Additional Fixtures (if needed)
# ===================================================================

@pytest.fixture
def live_metadata(focus_server_api):
    """Fixture to get live metadata."""
    try:
        return focus_server_api.get_live_metadata_flat()
    except Exception:
        pytest.skip("Live metadata not available")

