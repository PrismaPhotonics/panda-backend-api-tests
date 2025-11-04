"""
Unit Tests - Validators
=========================

Comprehensive unit tests for validation utilities.

Author: QA Automation Architect
Date: 2025-10-07
"""

import pytest
from datetime import datetime, timedelta

from src.utils.validators import (
    validate_task_id_format,
    validate_time_format_yymmddHHMMSS,
    validate_sensor_range,
    validate_frequency_range,
    validate_nfft_value,
    validate_roi_change_safety,
    validate_configuration_compatibility,
    ValidationError as CustomValidationError
)
from src.models.baby_analyzer_models import RecordingMetadata


class TestTaskIDValidation:
    """Unit tests for task ID validation."""
    
    def test_valid_task_id(self):
        """Test: Valid task ID formats."""
        valid_ids = [
            "task_123",
            "test-task",
            "my_test_task_001",
            "TASK123",
            "task-with-hyphens-and_underscores"
        ]
        
        for task_id in valid_ids:
            assert validate_task_id_format(task_id)
    
    def test_invalid_task_id_special_chars(self):
        """Test: Invalid task ID with special characters."""
        invalid_ids = [
            "task@123",
            "task#test",
            "task%20",
            "task!invalid"
        ]
        
        for task_id in invalid_ids:
            with pytest.raises(CustomValidationError):
                validate_task_id_format(task_id)
    
    def test_empty_task_id(self):
        """Test: Empty task ID."""
        with pytest.raises(CustomValidationError):
            validate_task_id_format("")
    
    def test_none_task_id(self):
        """Test: None task ID."""
        with pytest.raises(CustomValidationError):
            validate_task_id_format(None)
    
    def test_very_long_task_id(self):
        """Test: Very long task ID (exceeds 256 chars)."""
        long_id = "a" * 300
        
        with pytest.raises(CustomValidationError) as exc_info:
            validate_task_id_format(long_id)
        
        assert "too long" in str(exc_info.value).lower()


class TestTimeFormatValidation:
    """Unit tests for time format validation."""
    
    def test_valid_time_format(self):
        """Test: Valid time formats."""
        valid_times = [
            "251007120000",  # 2025-10-07 12:00:00
            "240101000000",  # 2024-01-01 00:00:00
            "231231235959"   # 2023-12-31 23:59:59
        ]
        
        for time_str in valid_times:
            assert validate_time_format_yymmddHHMMSS(time_str)
    
    def test_invalid_time_length(self):
        """Test: Invalid time length."""
        invalid_times = [
            "2510071200",      # Too short
            "25100712000000"   # Too long
        ]
        
        for time_str in invalid_times:
            with pytest.raises(CustomValidationError):
                validate_time_format_yymmddHHMMSS(time_str)
    
    def test_invalid_time_format(self):
        """Test: Invalid time format (non-digits)."""
        with pytest.raises(CustomValidationError):
            validate_time_format_yymmddHHMMSS("25-10-07-12-00")
    
    def test_invalid_month(self):
        """Test: Invalid month (13)."""
        with pytest.raises(CustomValidationError) as exc_info:
            validate_time_format_yymmddHHMMSS("251307120000")  # Month=13
        
        assert "month" in str(exc_info.value).lower()
    
    def test_invalid_day(self):
        """Test: Invalid day (32)."""
        with pytest.raises(CustomValidationError) as exc_info:
            validate_time_format_yymmddHHMMSS("251032120000")  # Day=32
        
        assert "day" in str(exc_info.value).lower()
    
    def test_invalid_hour(self):
        """Test: Invalid hour (25)."""
        with pytest.raises(CustomValidationError) as exc_info:
            validate_time_format_yymmddHHMMSS("251007250000")  # Hour=25
        
        assert "hour" in str(exc_info.value).lower()


class TestSensorRangeValidation:
    """Unit tests for sensor range validation."""
    
    def test_valid_sensor_range(self):
        """Test: Valid sensor range."""
        assert validate_sensor_range(
            min_sensor=0,
            max_sensor=100,
            total_sensors=200
        )
    
    def test_sensor_range_exceeds_total(self):
        """Test: Sensor range exceeds total sensors."""
        with pytest.raises(CustomValidationError) as exc_info:
            validate_sensor_range(
                min_sensor=0,
                max_sensor=250,
                total_sensors=200
            )
        
        assert "exceeds" in str(exc_info.value).lower()
    
    def test_reversed_sensor_range(self):
        """Test: Reversed sensor range (max < min)."""
        with pytest.raises(CustomValidationError):
            validate_sensor_range(
                min_sensor=100,
                max_sensor=50,
                total_sensors=200
            )
    
    def test_negative_sensor_index(self):
        """Test: Negative sensor index."""
        with pytest.raises(CustomValidationError):
            validate_sensor_range(
                min_sensor=-10,
                max_sensor=100,
                total_sensors=200
            )


class TestFrequencyRangeValidation:
    """Unit tests for frequency range validation."""
    
    def test_valid_frequency_range(self):
        """Test: Valid frequency range within Nyquist limit."""
        assert validate_frequency_range(
            min_freq=0,
            max_freq=500,
            prr=2000.0  # Nyquist = 1000 Hz
        )
    
    def test_frequency_exceeds_nyquist(self):
        """Test: Frequency exceeds Nyquist limit."""
        with pytest.raises(CustomValidationError) as exc_info:
            validate_frequency_range(
                min_freq=0,
                max_freq=1500,  # Exceeds Nyquist (1000 Hz)
                prr=2000.0
            )
        
        assert "nyquist" in str(exc_info.value).lower()
    
    def test_reversed_frequency_range(self):
        """Test: Reversed frequency range."""
        with pytest.raises(CustomValidationError):
            validate_frequency_range(
                min_freq=500,
                max_freq=100,
                prr=2000.0
            )
    
    def test_negative_frequency(self):
        """Test: Negative frequency."""
        with pytest.raises(CustomValidationError):
            validate_frequency_range(
                min_freq=-100,
                max_freq=500,
                prr=2000.0
            )


class TestNFFTValidation:
    """Unit tests for NFFT validation."""
    
    def test_valid_nfft_power_of_2(self):
        """Test: Valid NFFT (power of 2)."""
        powers_of_2 = [128, 256, 512, 1024, 2048, 4096]
        
        for nfft in powers_of_2:
            assert validate_nfft_value(nfft)
    
    def test_non_power_of_2_nfft(self):
        """Test: Non-power-of-2 NFFT (with warning)."""
        with pytest.warns(UserWarning):
            validate_nfft_value(1000)  # Not power of 2
    
    # REMOVED: test_zero_nfft - duplicate of test_config_validation_nfft_frequency.py::test_zero_nfft
    # REMOVED: test_negative_nfft - duplicate of test_config_validation_nfft_frequency.py::test_negative_nfft


class TestROIChangeSafety:
    """Unit tests for ROI change safety validation."""
    
    def test_safe_roi_change(self):
        """Test: Safe ROI change (small change)."""
        result = validate_roi_change_safety(
            current_min=0,
            current_max=100,
            new_min=10,
            new_max=110,
            max_change_percent=50.0
        )
        
        assert result["is_safe"]
        assert len(result["warnings"]) == 0
    
    def test_unsafe_roi_range_change(self):
        """Test: Unsafe ROI change (large range change)."""
        result = validate_roi_change_safety(
            current_min=0,
            current_max=100,
            new_min=0,
            new_max=200,  # 100% increase
            max_change_percent=50.0
        )
        
        assert not result["is_safe"]
        assert len(result["warnings"]) > 0
    
    def test_unsafe_roi_shift(self):
        """Test: Unsafe ROI change (large shift)."""
        result = validate_roi_change_safety(
            current_min=0,
            current_max=100,
            new_min=100,
            new_max=200,  # 100% shift
            max_change_percent=50.0
        )
        
        assert not result["is_safe"]
        assert len(result["warnings"]) > 0


class TestConfigurationCompatibility:
    """Unit tests for configuration compatibility validation."""
    
    def test_compatible_configuration(self):
        """Test: Compatible configuration."""
        result = validate_configuration_compatibility(
            nfft=1024,
            sensor_range=100,
            prr=2000.0
        )
        
        assert result["is_compatible"]
        assert "spectrogram_rows_per_sec" in result["estimates"]
        assert "output_data_rate_mbps" in result["estimates"]
    
    def test_high_throughput_configuration(self):
        """Test: High throughput configuration (warnings)."""
        result = validate_configuration_compatibility(
            nfft=64,  # Very small NFFT to generate high row rate
            sensor_range=1000,  # Large sensor range
            prr=10000.0  # Very high PRR
        )
        
        # Should have warnings about high data rate
        # With these params: rows_per_sec = 10000/64 = 156.25 (OK)
        # output_mbps = (156.25 * 1000 * 32 * 4 * 8) / 1e6 = ~160 Mbps (>100, triggers warning)
        assert len(result["warnings"]) > 0
        assert result["is_compatible"]  # Still compatible, just has warnings
    
    def test_low_throughput_configuration(self):
        """Test: Low throughput configuration."""
        result = validate_configuration_compatibility(
            nfft=8192,  # Large NFFT
            sensor_range=20,  # Small sensor range
            prr=1000.0  # Low PRR
        )
        
        # May have warnings about low rate
        estimates = result["estimates"]
        assert estimates["spectrogram_rows_per_sec"] < 1.0


# ===================================================================
# Integration with Models Tests
# ===================================================================

class TestMetadataConsistencyValidation:
    """Unit tests for metadata consistency validation."""
    
    def test_valid_metadata(self):
        """Test: Valid metadata consistency."""
        from src.utils.validators import validate_metadata_consistency
        
        metadata = RecordingMetadata(
            prr=2000.0,
            num_samples_per_trace=1000,
            dtype="float32",
            dx=10.0,
            fiber_start_meters=0,
            fiber_length_meters=10000,
            number_of_channels=100
        )
        
        assert validate_metadata_consistency(metadata)
    
    def test_invalid_fiber_geometry(self):
        """Test: Invalid fiber geometry (start >= length)."""
        from src.utils.validators import validate_metadata_consistency
        
        metadata = RecordingMetadata(
            prr=2000.0,
            num_samples_per_trace=1000,
            dtype="float32",
            dx=10.0,
            fiber_start_meters=10000,  # Invalid: >= length
            fiber_length_meters=5000,
            number_of_channels=100
        )
        
        with pytest.raises(CustomValidationError):
            validate_metadata_consistency(metadata)



