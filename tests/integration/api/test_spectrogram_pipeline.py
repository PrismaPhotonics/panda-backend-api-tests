"""
Integration Tests - Spectrogram Processing Pipeline
=====================================================

Comprehensive integration tests for the spectrogram processing pipeline.

Test Flow:
    1. Configure baby analyzer with various spectrogram parameters
    2. Verify correct NFFT, frequency range, and processing
    3. Test different pipeline configurations (decimation, filtering, etc.)

Author: QA Automation Architect
Date: 2025-10-07
"""

import pytest
import time
import logging
from typing import Dict, Any

from src.models.focus_server_models import ConfigTaskRequest
from src.apis.baby_analyzer_mq_client import BabyAnalyzerMQClient
from src.models.baby_analyzer_models import ColorMap, CAxisRange
from src.utils.helpers import generate_task_id, generate_config_payload
from src.utils.validators import (
    validate_nfft_value,
    validate_frequency_range,
    validate_configuration_compatibility
)

logger = logging.getLogger(__name__)


# ===================================================================
# Fixtures
# ===================================================================

@pytest.fixture
def mq_client(config_manager):
    """Fixture to provide RabbitMQ client for baby analyzer commands."""
    rabbitmq_config = config_manager.get("rabbitmq", {})
    
    client = BabyAnalyzerMQClient(
        host=rabbitmq_config.get("host", "localhost"),
        port=rabbitmq_config.get("port", 5672),
        username=rabbitmq_config.get("username", "guest"),
        password=rabbitmq_config.get("password", "guest")
    )
    
    client.connect()
    yield client
    client.disconnect()


# ===================================================================
# NFFT Configuration Tests
# ===================================================================

@pytest.mark.integration
@pytest.mark.api
class TestNFFTConfiguration:
    """Test suite for NFFT parameter validation and configuration."""
    
    def test_valid_nfft_power_of_2(self, focus_server_api):
        """Test: Configure with valid NFFT (power of 2)."""
        task_id = generate_task_id("nfft_256")
        logger.info(f"Test: NFFT=256 for task {task_id}")
        
        # Validate NFFT
        assert validate_nfft_value(256)
        
        # Configure with NFFT=256
        payload = generate_config_payload(nfft=256, live=True)
        config_request = ConfigTaskRequest(**payload)
        response = focus_server_api.config_task(task_id, config_request)
        
        assert response.status == "Config received successfully"
        logger.info("✅ NFFT=256 configuration successful")
    
    def test_nfft_variations(self, focus_server_api):
        """Test: Various valid NFFT values."""
        nfft_values = [128, 256, 512, 1024, 2048, 4096]
        
        for nfft in nfft_values:
            task_id = generate_task_id(f"nfft_{nfft}")
            logger.info(f"Testing NFFT={nfft}")
            
            assert validate_nfft_value(nfft)
            
            payload = generate_config_payload(nfft=nfft, live=True)
            config_request = ConfigTaskRequest(**payload)
            response = focus_server_api.config_task(task_id, config_request)
            
            assert response.status == "Config received successfully"
        
        logger.info(f"✅ All {len(nfft_values)} NFFT values tested successfully")
    
    def test_nfft_non_power_of_2(self, focus_server_api):
        """Test: Configure with non-power-of-2 NFFT (with warning)."""
        task_id = generate_task_id("nfft_1000")
        nfft = 1000  # Not power of 2
        
        logger.info(f"Test: NFFT={nfft} (not power of 2)")
        
        # Validation should pass but with warning
        with pytest.warns(UserWarning):
            validate_nfft_value(nfft)
        
        # Configuration may still succeed
        payload = generate_config_payload(nfft=nfft, live=True)
        config_request = ConfigTaskRequest(**payload)
        response = focus_server_api.config_task(task_id, config_request)
        
        assert response.status == "Config received successfully"
        logger.info("✅ Non-power-of-2 NFFT accepted with warning")


# ===================================================================
# Frequency Range Tests
# ===================================================================

@pytest.mark.integration
@pytest.mark.api
class TestFrequencyRangeConfiguration:
    """Test suite for frequency range configuration."""
    
    def test_frequency_range_within_nyquist(self, focus_server_api, live_metadata):
        """Test: Frequency range within Nyquist limit."""
        task_id = generate_task_id("freq_valid")
        
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
        
        payload = generate_config_payload(
            freq_min=0,
            freq_max=freq_max,
            live=True
        )
        
        config_request = ConfigTaskRequest(**payload)
        response = focus_server_api.config_task(task_id, config_request)
        
        assert response.status == "Config received successfully"
        logger.info(f"✅ Frequency range [0, {freq_max}] configured successfully")
    
    def test_frequency_range_variations(self, focus_server_api):
        """Test: Various frequency ranges."""
        frequency_ranges = [
            (0, 100),
            (0, 250),
            (0, 500),
            (100, 300),
            (200, 600)
        ]
        
        for freq_min, freq_max in frequency_ranges:
            task_id = generate_task_id(f"freq_{freq_min}_{freq_max}")
            logger.info(f"Testing frequency range [{freq_min}, {freq_max}]")
            
            payload = generate_config_payload(
                freq_min=freq_min,
                freq_max=freq_max,
                live=True
            )
            
            config_request = ConfigTaskRequest(**payload)
            response = focus_server_api.config_task(task_id, config_request)
            
            assert response.status == "Config received successfully"
        
        logger.info(f"✅ All {len(frequency_ranges)} frequency ranges tested")


# ===================================================================
# Colormap and Visualization Tests
# ===================================================================

@pytest.mark.integration
@pytest.mark.rabbitmq
class TestVisualizationConfiguration:
    """Test suite for visualization configuration (colormap, caxis)."""
    
    def test_colormap_commands(self, mq_client):
        """Test: Send colormap change commands."""
        logger.info("Test: Colormap commands")
        
        colormaps = [ColorMap.PARULA, ColorMap.GRAYSCALE, ColorMap.JET]
        
        for colormap in colormaps:
            logger.info(f"Sending colormap: {colormap}")
            mq_client.send_colormap_change(colormap=colormap)
            time.sleep(0.5)
        
        logger.info(f"✅ All {len(colormaps)} colormap commands sent")
    
    def test_caxis_adjustment(self, mq_client):
        """Test: Send color axis adjustment commands."""
        logger.info("Test: Caxis adjustment")
        
        caxis_ranges = [
            (-1.0, 1.0),
            (0.0, 10.0),
            (-5.0, 5.0)
        ]
        
        for min_val, max_val in caxis_ranges:
            logger.info(f"Sending caxis: [{min_val}, {max_val}]")
            mq_client.send_caxis_adjust(min_value=min_val, max_value=max_val)
            time.sleep(0.5)
        
        logger.info(f"✅ All {len(caxis_ranges)} caxis commands sent")
    
    def test_caxis_with_invalid_range(self, mq_client):
        """Test: Caxis with invalid range (max < min)."""
        logger.info("Test: Invalid caxis range")
        
        with pytest.raises(Exception) as exc_info:
            mq_client.send_caxis_adjust(min_value=10.0, max_value=5.0)
        
        assert "greater" in str(exc_info.value).lower() or ">" in str(exc_info.value)
        logger.info(f"✅ Invalid caxis rejected: {exc_info.value}")


# ===================================================================
# Configuration Compatibility Tests
# ===================================================================

@pytest.mark.integration
@pytest.mark.api
class TestConfigurationCompatibility:
    """Test suite for configuration parameter compatibility."""
    
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
    
    def test_high_throughput_configuration(self, focus_server_api):
        """Test: Configuration with high throughput."""
        task_id = generate_task_id("high_throughput")
        logger.info(f"Test: High throughput configuration for task {task_id}")
        
        # High throughput config
        payload = generate_config_payload(
            sensors_min=0,
            sensors_max=200,  # Large sensor range
            freq_min=0,
            freq_max=500,
            nfft=256,  # Small NFFT = high output rate
            live=True
        )
        
        # Check compatibility
        compat_result = validate_configuration_compatibility(
            nfft=256,
            sensor_range=200,
            prr=2000.0
        )
        
        logger.info(f"Expected output rate: {compat_result['estimates']['output_data_rate_mbps']:.2f} Mbps")
        
        if len(compat_result["warnings"]) > 0:
            logger.warning(f"Configuration warnings: {compat_result['warnings']}")
        
        # Configure task
        config_request = ConfigTaskRequest(**payload)
        response = focus_server_api.config_task(task_id, config_request)
        
        assert response.status == "Config received successfully"
        logger.info("✅ High throughput configuration accepted")
    
    def test_low_throughput_configuration(self, focus_server_api):
        """Test: Configuration with low throughput."""
        task_id = generate_task_id("low_throughput")
        logger.info(f"Test: Low throughput configuration for task {task_id}")
        
        # Low throughput config
        payload = generate_config_payload(
            sensors_min=0,
            sensors_max=20,  # Small sensor range
            freq_min=0,
            freq_max=100,
            nfft=4096,  # Large NFFT = low output rate
            live=True
        )
        
        # Check compatibility
        compat_result = validate_configuration_compatibility(
            nfft=4096,
            sensor_range=20,
            prr=2000.0
        )
        
        logger.info(f"Expected output rate: {compat_result['estimates']['output_data_rate_mbps']:.2f} Mbps")
        
        # Configure task
        config_request = ConfigTaskRequest(**payload)
        response = focus_server_api.config_task(task_id, config_request)
        
        assert response.status == "Config received successfully"
        logger.info("✅ Low throughput configuration accepted")


# ===================================================================
# Error Handling Tests
# ===================================================================

@pytest.mark.integration
@pytest.mark.api
class TestSpectrogramPipelineErrors:
    """Test suite for spectrogram pipeline error handling."""
    
    def test_zero_nfft(self, focus_server_api):
        """Test: Configure with NFFT=0."""
        task_id = generate_task_id("nfft_zero")
        logger.info(f"Test: NFFT=0 for task {task_id}")
        
        with pytest.raises(Exception) as exc_info:
            validate_nfft_value(0)
        
        assert "positive" in str(exc_info.value).lower()
        logger.info(f"✅ NFFT=0 rejected: {exc_info.value}")
    
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

