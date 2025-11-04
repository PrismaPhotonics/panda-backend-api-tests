"""
Unit Tests - Models Validation
================================

Comprehensive unit tests for Pydantic model validation.
Tests all models for proper validation, edge cases, and error handling.

Author: QA Automation Architect
Date: 2025-10-07
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.models.focus_server_models import (
    ConfigTaskRequest,
    SensorsListResponse,
    LiveMetadataFlat,
)
from src.models.baby_analyzer_models import (
    KeepaliveCommand,
    KeepaliveCommandValue,
    InputChangedCommand,
    RecordingMetadata,
    ColormapCommand,
    ColorMap,
    CaxisCommand,
    CAxisRange,
    RegionOfInterestCommand,
    RegionOfInterest,
    MonitorQueuesCommand,
    MonitorQueuesValue
)


# ===================================================================
# Focus Server Models Tests
# ===================================================================

class TestConfigTaskRequest:
    """Unit tests for ConfigTaskRequest model."""
    
    def test_valid_live_config(self):
        """Test: Valid live configuration (no timestamps)."""
        payload = {
            "displayTimeAxisDuration": 10.0,
            "nfftSelection": 1024,
            "canvasInfo": {"height": 1000},
            "sensors": {"min": 0, "max": 100},
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": None,
            "end_time": None
        }
        
        config = ConfigTaskRequest(**payload)
        
        assert config.displayTimeAxisDuration == 10.0
        assert config.nfftSelection == 1024
        assert config.canvasInfo["height"] == 1000
        assert config.start_time is None
        assert config.end_time is None
    
    def test_valid_historic_config(self):
        """Test: Valid historic configuration (with timestamps)."""
        payload = {
            "displayTimeAxisDuration": 10.0,
            "nfftSelection": 1024,
            "canvasInfo": {"height": 1000},
            "sensors": {"min": 0, "max": 100},
            "frequencyRange": {"min": 0, "max": 500},
            "start_time": "251007120000",
            "end_time": "251007130000"
        }
        
        config = ConfigTaskRequest(**payload)
        
        assert config.start_time == "251007120000"
        assert config.end_time == "251007130000"
    
    def test_invalid_sensor_range(self):
        """Test: Invalid sensor range (max < min)."""
        payload = {
            "displayTimeAxisDuration": 10.0,
            "nfftSelection": 1024,
            "canvasInfo": {"height": 1000},
            "sensors": {"min": 100, "max": 50},  # Invalid
            "frequencyRange": {"min": 0, "max": 500}
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ConfigTaskRequest(**payload)
        
        assert "sensor" in str(exc_info.value).lower()
    
    def test_invalid_frequency_range(self):
        """Test: Invalid frequency range (max < min)."""
        payload = {
            "displayTimeAxisDuration": 10.0,
            "nfftSelection": 1024,
            "canvasInfo": {"height": 1000},
            "sensors": {"min": 0, "max": 100},
            "frequencyRange": {"min": 500, "max": 100}  # Invalid
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ConfigTaskRequest(**payload)
        
        assert "frequenc" in str(exc_info.value).lower()
    
    def test_zero_canvas_height(self):
        """Test: Zero canvas height (invalid)."""
        payload = {
            "displayTimeAxisDuration": 10.0,
            "nfftSelection": 1024,
            "canvasInfo": {"height": 0},  # Invalid
            "sensors": {"min": 0, "max": 100},
            "frequencyRange": {"min": 0, "max": 500}
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ConfigTaskRequest(**payload)
        
        assert "height" in str(exc_info.value).lower()
    
    def test_negative_nfft(self):
        """Test: Negative NFFT (invalid)."""
        payload = {
            "displayTimeAxisDuration": 10.0,
            "nfftSelection": -1024,  # Invalid
            "canvasInfo": {"height": 1000},
            "sensors": {"min": 0, "max": 100},
            "frequencyRange": {"min": 0, "max": 500}
        }
        
        with pytest.raises(ValidationError):
            ConfigTaskRequest(**payload)


class TestSensorsListResponse:
    """Unit tests for SensorsListResponse model."""
    
    def test_valid_sensors_list(self):
        """Test: Valid sensors list."""
        response = SensorsListResponse(sensors=[0, 1, 2, 3, 4])
        
        assert len(response.sensors) == 5
        assert response.sensors[0] == 0
        assert response.sensors[-1] == 4
    
    def test_empty_sensors_list(self):
        """Test: Empty sensors list (valid)."""
        response = SensorsListResponse(sensors=[])
        
        assert len(response.sensors) == 0


class TestLiveMetadataFlat:
    """Unit tests for LiveMetadataFlat model."""
    
    def test_valid_metadata(self):
        """Test: Valid live metadata."""
        metadata = LiveMetadataFlat(
            prr=2000.0,
            num_samples_per_trace=1000,
            dtype="float32",
            dx=10.0,
            fiber_start_meters=0,
            fiber_length_meters=10000,
            sw_version="1.0.0",
            number_of_channels=100
        )
        
        assert metadata.prr == 2000.0
        assert metadata.num_samples_per_trace == 1000
        assert metadata.dtype == "float32"
    
    def test_zero_prr(self):
        """Test: Zero PRR (invalid)."""
        with pytest.raises(ValidationError):
            LiveMetadataFlat(
                prr=0.0,  # Invalid
                num_samples_per_trace=1000,
                dtype="float32"
            )
    
    def test_negative_num_samples(self):
        """Test: Negative num_samples_per_trace (invalid)."""
        with pytest.raises(ValidationError):
            LiveMetadataFlat(
                prr=2000.0,
                num_samples_per_trace=-1000,  # Invalid
                dtype="float32"
            )




# ===================================================================
# Baby Analyzer Models Tests
# ===================================================================

class TestKeepaliveCommand:
    """Unit tests for KeepaliveCommand model."""
    
    def test_valid_keepalive_command(self):
        """Test: Valid keepalive command."""
        command = KeepaliveCommand(
            value=KeepaliveCommandValue(source="test_client")
        )
        
        assert command.type == "KeepaliveCommand"
        assert command.value.source == "test_client"
    
    def test_keepalive_command_serialization(self):
        """Test: Keepalive command serialization."""
        command = KeepaliveCommand(
            value=KeepaliveCommandValue(source="test")
        )
        
        data = command.model_dump()
        
        assert data["type"] == "KeepaliveCommand"
        assert data["value"]["source"] == "test"


class TestRecordingMetadata:
    """Unit tests for RecordingMetadata model."""
    
    def test_valid_recording_metadata(self):
        """Test: Valid recording metadata."""
        metadata = RecordingMetadata(
            prr=2000.0,
            num_samples_per_trace=1000,
            dtype="float32",
            dx=10.0,
            number_of_channels=100
        )
        
        assert metadata.prr == 2000.0
        assert metadata.num_samples_per_trace == 1000
    
    def test_zero_prr(self):
        """Test: Zero PRR (invalid)."""
        with pytest.raises(ValidationError):
            RecordingMetadata(
                prr=0.0,  # Invalid
                num_samples_per_trace=1000,
                dtype="float32"
            )


class TestColormapCommand:
    """Unit tests for ColormapCommand model."""
    
    def test_valid_colormap_commands(self):
        """Test: Valid colormap commands."""
        colormaps = [ColorMap.PARULA, ColorMap.GRAYSCALE, ColorMap.JET]
        
        for colormap in colormaps:
            command = ColormapCommand(value=colormap)
            assert command.type == "ColormapCommand"
            assert command.value == colormap
    
    def test_colormap_serialization(self):
        """Test: Colormap command serialization."""
        command = ColormapCommand(value=ColorMap.JET)
        data = command.model_dump()
        
        assert data["type"] == "ColormapCommand"
        assert data["value"] == "jet"


class TestCAxisRange:
    """Unit tests for CAxisRange model."""
    
    def test_valid_caxis_range(self):
        """Test: Valid caxis range."""
        caxis = CAxisRange(min=-10.0, max=10.0)
        
        assert caxis.min == -10.0
        assert caxis.max == 10.0
    
    def test_invalid_caxis_range(self):
        """Test: Invalid caxis range (max < min)."""
        with pytest.raises(ValidationError):
            CAxisRange(min=10.0, max=5.0)  # Invalid


class TestRegionOfInterest:
    """Unit tests for RegionOfInterest model."""
    
    def test_valid_roi(self):
        """Test: Valid ROI."""
        roi = RegionOfInterest(start=0, end=100)
        
        assert roi.start == 0
        assert roi.end == 100
    
    def test_invalid_roi_reversed(self):
        """Test: Invalid ROI (end < start)."""
        with pytest.raises(ValidationError):
            RegionOfInterest(start=100, end=50)  # Invalid
    
    def test_negative_roi_start(self):
        """Test: Negative ROI start (invalid)."""
        with pytest.raises(ValidationError):
            RegionOfInterest(start=-10, end=100)  # Invalid
    
    def test_roi_equal_start_end(self):
        """Test: ROI with start == end (invalid)."""
        with pytest.raises(ValidationError):
            RegionOfInterest(start=50, end=50)  # Invalid


class TestMonitorQueuesValue:
    """Unit tests for MonitorQueuesValue model."""
    
    def test_valid_monitor_queues(self):
        """Test: Valid monitor queues."""
        queues = MonitorQueuesValue(
            queues_to_monitor=["queue1", "queue2", "queue3"]
        )
        
        assert len(queues.queues_to_monitor) == 3
        assert "queue1" in queues.queues_to_monitor
    
    def test_empty_queues_list(self):
        """Test: Empty queues list (invalid)."""
        with pytest.raises(ValidationError):
            MonitorQueuesValue(queues_to_monitor=[])  # Invalid: min_length=1


# ===================================================================
# Edge Cases Tests
# ===================================================================

class TestModelEdgeCases:
    """Unit tests for model edge cases."""
    
    def test_very_large_sensor_range(self):
        """Test: Very large sensor range."""
        config = ConfigTaskRequest(
            displayTimeAxisDuration=10.0,
            nfftSelection=1024,
            canvasInfo={"height": 1000},
            sensors={"min": 0, "max": 100000},  # Very large
            frequencyRange={"min": 0, "max": 500}
        )
        
        assert config.sensors["max"] == 100000
    
    def test_very_small_canvas_height(self):
        """Test: Minimum valid canvas height."""
        config = ConfigTaskRequest(
            displayTimeAxisDuration=10.0,
            nfftSelection=1024,
            canvasInfo={"height": 1},  # Minimum
            sensors={"min": 0, "max": 100},
            frequencyRange={"min": 0, "max": 500}
        )
        
        assert config.canvasInfo["height"] == 1
    
    def test_very_large_nfft(self):
        """Test: Very large NFFT."""
        config = ConfigTaskRequest(
            displayTimeAxisDuration=10.0,
            nfftSelection=65536,  # Very large
            canvasInfo={"height": 1000},
            sensors={"min": 0, "max": 100},
            frequencyRange={"min": 0, "max": 500}
        )
        
        assert config.nfftSelection == 65536
    
    def test_zero_frequency_range(self):
        """Test: Zero-width frequency range (invalid)."""
        with pytest.raises(ValidationError):
            ConfigTaskRequest(
                displayTimeAxisDuration=10.0,
                nfftSelection=1024,
                canvasInfo={"height": 1000},
                sensors={"min": 0, "max": 100},
                frequencyRange={"min": 100, "max": 100}  # Invalid: same min/max
            )

