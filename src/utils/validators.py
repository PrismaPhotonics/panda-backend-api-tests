"""
Response Validators
====================

Validation utilities for API responses, data integrity checks, and business logic validation.
Provides comprehensive validation functions for Focus Server and Baby Analyzer workflows.
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import re

from src.models.focus_server_models import (
    WaterfallGetResponse, WaterfallDataBlock,
    TaskMetadataGetResponse, LiveMetadataFlat
)
from src.models.baby_analyzer_models import RecordingMetadata


class ValidationError(Exception):
    """Custom validation error exception."""
    pass


def validate_task_id_format(task_id: str) -> bool:
    """
    Validate task ID format.
    
    Task IDs should be alphanumeric with optional hyphens/underscores.
    
    Args:
        task_id: Task identifier to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If task_id is invalid
    
    Time Complexity: O(n) where n is length of task_id
    Space Complexity: O(1)
    """
    if not task_id or not isinstance(task_id, str):
        raise ValidationError("task_id must be a non-empty string")
    
    # Allow alphanumeric, hyphens, underscores
    pattern = r'^[a-zA-Z0-9_-]+$'
    
    if not re.match(pattern, task_id):
        raise ValidationError(
            f"Invalid task_id format: {task_id}. "
            "Must contain only alphanumeric characters, hyphens, or underscores."
        )
    
    if len(task_id) > 256:
        raise ValidationError(f"task_id too long: {len(task_id)} characters (max: 256)")
    
    return True


def validate_time_format_yymmddHHMMSS(time_str: str) -> bool:
    """
    Validate time string format: yymmddHHMMSS.
    
    Args:
        time_str: Time string to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If time format is invalid
    
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    if not time_str or not isinstance(time_str, str):
        raise ValidationError("time_str must be a non-empty string")
    
    if len(time_str) != 12:
        raise ValidationError(
            f"Invalid time format: {time_str}. Expected format: yymmddHHMMSS (12 characters)"
        )
    
    # Validate all characters are digits
    if not time_str.isdigit():
        raise ValidationError(f"Time string must contain only digits: {time_str}")
    
    # Parse components
    yy = int(time_str[0:2])
    mm = int(time_str[2:4])
    dd = int(time_str[4:6])
    HH = int(time_str[6:8])
    MM = int(time_str[8:10])
    SS = int(time_str[10:12])
    
    # Validate ranges
    if not (1 <= mm <= 12):
        raise ValidationError(f"Invalid month: {mm} (must be 1-12)")
    
    if not (1 <= dd <= 31):
        raise ValidationError(f"Invalid day: {dd} (must be 1-31)")
    
    if not (0 <= HH <= 23):
        raise ValidationError(f"Invalid hour: {HH} (must be 0-23)")
    
    if not (0 <= MM <= 59):
        raise ValidationError(f"Invalid minute: {MM} (must be 0-59)")
    
    if not (0 <= SS <= 59):
        raise ValidationError(f"Invalid second: {SS} (must be 0-59)")
    
    return True


def validate_sensor_range(min_sensor: int, max_sensor: int, total_sensors: int) -> bool:
    """
    Validate sensor range against total available sensors.
    
    Args:
        min_sensor: Minimum sensor index
        max_sensor: Maximum sensor index
        total_sensors: Total number of available sensors
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If sensor range is invalid
    
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    if not isinstance(min_sensor, int) or not isinstance(max_sensor, int):
        raise ValidationError("Sensor indices must be integers")
    
    if min_sensor < 0 or max_sensor < 0:
        raise ValidationError("Sensor indices must be non-negative")
    
    if max_sensor <= min_sensor:
        raise ValidationError(
            f"max_sensor ({max_sensor}) must be > min_sensor ({min_sensor})"
        )
    
    if max_sensor >= total_sensors:
        raise ValidationError(
            f"max_sensor ({max_sensor}) exceeds total sensors ({total_sensors})"
        )
    
    return True


def validate_frequency_range(min_freq: int, max_freq: int, prr: float) -> bool:
    """
    Validate frequency range against pulse repetition rate (Nyquist limit).
    
    Args:
        min_freq: Minimum frequency (Hz)
        max_freq: Maximum frequency (Hz)
        prr: Pulse repetition rate (samples per second)
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If frequency range is invalid
    
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    if not isinstance(min_freq, int) or not isinstance(max_freq, int):
        raise ValidationError("Frequency values must be integers")
    
    if min_freq < 0 or max_freq < 0:
        raise ValidationError("Frequency values must be non-negative")
    
    if max_freq <= min_freq:
        raise ValidationError(
            f"max_freq ({max_freq}) must be > min_freq ({min_freq})"
        )
    
    # Nyquist frequency
    nyquist_freq = prr / 2
    
    if max_freq > nyquist_freq:
        raise ValidationError(
            f"max_freq ({max_freq} Hz) exceeds Nyquist frequency "
            f"({nyquist_freq} Hz) for PRR={prr}"
        )
    
    return True


def validate_nfft_value(nfft: int) -> bool:
    """
    Validate NFFT value (should be power of 2 for efficiency).
    
    Args:
        nfft: NFFT value to validate
        
    Returns:
        True if valid (with warning if not power of 2)
        
    Raises:
        ValidationError: If nfft is invalid
    
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    if not isinstance(nfft, int):
        raise ValidationError("NFFT must be an integer")
    
    if nfft <= 0:
        raise ValidationError("NFFT must be positive")
    
    # Check if power of 2 (for efficiency)
    is_power_of_2 = (nfft & (nfft - 1)) == 0
    
    if not is_power_of_2:
        import warnings
        warnings.warn(
            f"NFFT={nfft} is not a power of 2. "
            "Performance may be suboptimal. Consider using powers of 2 (e.g., 256, 512, 1024)."
        )
    
    return True


def validate_waterfall_response(response: WaterfallGetResponse) -> Dict[str, Any]:
    """
    Validate waterfall response structure and data integrity.
    
    Args:
        response: Waterfall response to validate
        
    Returns:
        Dictionary with validation results and statistics
        
    Raises:
        ValidationError: If response structure is invalid
    
    Time Complexity: O(n*m) where n=rows, m=sensors per row
    Space Complexity: O(1)
    """
    if not isinstance(response, WaterfallGetResponse):
        raise ValidationError("response must be a WaterfallGetResponse instance")
    
    validation_result = {
        "status_code": response.status_code,
        "has_data": response.data is not None,
        "is_valid": True,
        "warnings": [],
        "statistics": {}
    }
    
    # Validate based on status code
    if response.status_code == 200:
        # No data available yet - this is expected
        if response.data is not None:
            validation_result["warnings"].append(
                "Status 200 should have no data, but data is present"
            )
    
    elif response.status_code == 201:
        # Data should be present
        if response.data is None or len(response.data) == 0:
            raise ValidationError("Status 201 should have data, but data is None or empty")
        
        # Validate data blocks
        total_rows = 0
        total_sensors = 0
        
        for block_idx, block in enumerate(response.data):
            if not isinstance(block, WaterfallDataBlock):
                raise ValidationError(f"Block {block_idx} is not a WaterfallDataBlock")
            
            # Validate amplitude range
            if block.current_max_amp < block.current_min_amp:
                raise ValidationError(
                    f"Block {block_idx}: max_amp ({block.current_max_amp}) < "
                    f"min_amp ({block.current_min_amp})"
                )
            
            # Validate rows
            for row_idx, row in enumerate(block.rows):
                total_rows += 1
                
                # Validate timestamps
                if row.endTimestamp <= row.startTimestamp:
                    raise ValidationError(
                        f"Block {block_idx}, Row {row_idx}: "
                        f"endTimestamp <= startTimestamp"
                    )
                
                # Validate sensors
                if not row.sensors or len(row.sensors) == 0:
                    validation_result["warnings"].append(
                        f"Block {block_idx}, Row {row_idx}: No sensor data"
                    )
                
                total_sensors += len(row.sensors)
        
        validation_result["statistics"] = {
            "total_blocks": len(response.data),
            "total_rows": total_rows,
            "total_sensors": total_sensors,
            "avg_sensors_per_row": total_sensors / total_rows if total_rows > 0 else 0
        }
    
    elif response.status_code == 208:
        # Baby analyzer exited
        if response.data is not None:
            validation_result["warnings"].append(
                "Status 208 (exited) should have no data"
            )
    
    elif response.status_code in [400, 404]:
        # Error responses
        if response.data is not None:
            validation_result["warnings"].append(
                f"Status {response.status_code} (error) should have no data"
            )
    
    return validation_result


def validate_metadata_consistency(
    metadata: Union[LiveMetadataFlat, RecordingMetadata]
) -> bool:
    """
    Validate metadata internal consistency.
    
    Checks for logical consistency between metadata fields.
    
    Args:
        metadata: Metadata to validate
        
    Returns:
        True if consistent
        
    Raises:
        ValidationError: If metadata is inconsistent
    
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    if not isinstance(metadata, (LiveMetadataFlat, RecordingMetadata)):
        raise ValidationError("metadata must be LiveMetadataFlat or RecordingMetadata")
    
    # Validate PRR
    if metadata.prr <= 0:
        raise ValidationError(f"Invalid PRR: {metadata.prr} (must be > 0)")
    
    # Validate num_samples_per_trace
    if metadata.num_samples_per_trace <= 0:
        raise ValidationError(
            f"Invalid num_samples_per_trace: {metadata.num_samples_per_trace} (must be > 0)"
        )
    
    # Validate fiber geometry (if available)
    if hasattr(metadata, 'dx') and metadata.dx is not None:
        if metadata.dx <= 0:
            raise ValidationError(f"Invalid dx: {metadata.dx} (must be > 0)")
    
    if hasattr(metadata, 'fiber_length_meters') and metadata.fiber_length_meters is not None:
        if metadata.fiber_length_meters <= 0:
            raise ValidationError(
                f"Invalid fiber_length_meters: {metadata.fiber_length_meters} (must be > 0)"
            )
        
        # Check fiber_start < fiber_length
        if (hasattr(metadata, 'fiber_start_meters') and 
            metadata.fiber_start_meters is not None):
            if metadata.fiber_start_meters >= metadata.fiber_length_meters:
                raise ValidationError(
                    f"fiber_start_meters ({metadata.fiber_start_meters}) >= "
                    f"fiber_length_meters ({metadata.fiber_length_meters})"
                )
    
    # Validate number_of_channels (if available)
    if hasattr(metadata, 'number_of_channels') and metadata.number_of_channels is not None:
        if metadata.number_of_channels <= 0:
            raise ValidationError(
                f"Invalid number_of_channels: {metadata.number_of_channels} (must be > 0)"
            )
    
    return True


def validate_roi_change_safety(
    current_min: int,
    current_max: int,
    new_min: int,
    new_max: int,
    max_change_percent: float = 50.0
) -> Dict[str, Any]:
    """
    Validate ROI change is safe (not too drastic).
    
    Large ROI changes can cause processing disruptions.
    
    Args:
        current_min: Current minimum sensor
        current_max: Current maximum sensor
        new_min: New minimum sensor
        new_max: New maximum sensor
        max_change_percent: Maximum allowed change percentage (default: 50%)
        
    Returns:
        Dictionary with validation results and warnings
        
    Raises:
        ValidationError: If ROI change is unsafe
    
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    current_range = current_max - current_min
    new_range = new_max - new_min
    
    # Calculate change percentage
    range_change_percent = abs(new_range - current_range) / current_range * 100
    
    # Calculate shift
    current_center = (current_min + current_max) / 2
    new_center = (new_min + new_max) / 2
    shift = abs(new_center - current_center)
    shift_percent = (shift / current_range) * 100
    
    validation_result = {
        "is_safe": True,
        "warnings": [],
        "statistics": {
            "current_range": current_range,
            "new_range": new_range,
            "range_change_percent": range_change_percent,
            "shift": shift,
            "shift_percent": shift_percent
        }
    }
    
    # Check range change
    if range_change_percent > max_change_percent:
        validation_result["warnings"].append(
            f"Large ROI range change: {range_change_percent:.1f}% "
            f"(threshold: {max_change_percent}%)"
        )
    
    # Check shift
    if shift_percent > max_change_percent:
        validation_result["warnings"].append(
            f"Large ROI shift: {shift_percent:.1f}% "
            f"(threshold: {max_change_percent}%)"
        )
    
    # Determine if safe
    if len(validation_result["warnings"]) > 0:
        validation_result["is_safe"] = False
    
    return validation_result


def validate_configuration_compatibility(
    nfft: int,
    sensor_range: int,
    prr: float,
    expected_throughput_mbps: Optional[float] = None
) -> Dict[str, Any]:
    """
    Validate configuration parameters are compatible and estimate resource usage.
    
    Args:
        nfft: NFFT value
        sensor_range: Number of sensors (max - min)
        prr: Pulse repetition rate
        expected_throughput_mbps: Expected data throughput (Mbps), optional
        
    Returns:
        Dictionary with compatibility results and resource estimates
    
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    # Calculate spectrogram output rate
    spectrogram_rows_per_sec = prr / nfft
    
    # Estimate data size per row (assuming float32)
    bytes_per_sample = 4  # float32
    bytes_per_row = sensor_range * (nfft // 2) * bytes_per_sample
    
    # Estimate output data rate
    output_mbps = (spectrogram_rows_per_sec * bytes_per_row * 8) / 1_000_000
    
    result = {
        "is_compatible": True,
        "warnings": [],
        "estimates": {
            "spectrogram_rows_per_sec": spectrogram_rows_per_sec,
            "bytes_per_row": bytes_per_row,
            "output_data_rate_mbps": output_mbps
        }
    }
    
    # Check if output rate is reasonable
    if spectrogram_rows_per_sec < 1:
        result["warnings"].append(
            f"Very low spectrogram rate: {spectrogram_rows_per_sec:.2f} rows/sec"
        )
    
    if spectrogram_rows_per_sec > 1000:
        result["warnings"].append(
            f"Very high spectrogram rate: {spectrogram_rows_per_sec:.0f} rows/sec. "
            "Consider increasing NFFT or decimation."
        )
    
    # Check data rate
    if output_mbps > 100:
        result["warnings"].append(
            f"High output data rate: {output_mbps:.1f} Mbps. "
            "Consider decimation or compression."
        )
    
    # Compare with expected throughput if provided
    if expected_throughput_mbps is not None:
        if output_mbps > expected_throughput_mbps * 1.5:
            result["warnings"].append(
                f"Output rate ({output_mbps:.1f} Mbps) significantly exceeds "
                f"expected throughput ({expected_throughput_mbps} Mbps)"
            )
            result["is_compatible"] = False
    
    return result

