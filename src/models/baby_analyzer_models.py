"""
Baby Analyzer Data Models
===========================

Pydantic models for Baby Analyzer commands, requests, and responses.
Supports RabbitMQ command interface and CLI argument validation.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict, ValidationInfo
from typing import List, Dict, Optional, Any, Literal
from enum import Enum


# ===================================================================
# Baby Analyzer Command Models (RabbitMQ Interface)
# ===================================================================

class CommandType(str, Enum):
    """Baby Analyzer command types sent via RabbitMQ."""
    KEEPALIVE = "KeepaliveCommand"
    INPUT_CHANGED = "InputChangedCommand"
    COLORMAP = "ColormapCommand"
    CAXIS = "CaxisCommand"
    REGION_OF_INTEREST = "RegionOfInterestCommand"
    MONITOR_QUEUES = "MonitorQueuesCommand"


class ColorMap(str, Enum):
    """Supported colormap options for PNG output backend."""
    PARULA = "parula"
    GRAYSCALE = "grayscale"
    JET = "jet"


class KeepaliveCommandValue(BaseModel):
    """Keepalive command value structure."""
    source: str = Field(..., description="Source identifier sending the keepalive")
    
    model_config = ConfigDict(validate_assignment=True)


class KeepaliveCommand(BaseModel):
    """
    Keepalive command to reset baby analyzer timeout counter.
    
    Purpose: Keeps baby analyzer alive by resetting the timeout counter.
    Sent periodically to prevent auto-exit due to inactivity.
    """
    type: Literal[CommandType.KEEPALIVE] = CommandType.KEEPALIVE
    value: KeepaliveCommandValue = Field(..., description="Keepalive command payload")
    
    model_config = ConfigDict(validate_assignment=True, use_enum_values=True)


class RecordingMetadata(BaseModel):
    """
    Recording metadata structure for InputChangedCommand.
    
    Contains comprehensive metadata about the DAS recording stream.
    """
    prr: float = Field(..., description="Pulse repetition rate (samples per second)", gt=0)
    num_samples_per_trace: int = Field(..., description="Number of samples per trace", gt=0)
    dtype: str = Field(..., description="Data type of the recording (e.g., 'float32', 'int16')")
    dx: Optional[float] = Field(None, description="Distance between consecutive sensors (meters)", gt=0)
    fiber_start_meters: Optional[int] = Field(None, description="Fiber start offset (meters)", ge=0)
    fiber_length_meters: Optional[int] = Field(None, description="Total fiber length (meters)", gt=0)
    sw_version: Optional[str] = Field(None, description="Software version")
    number_of_channels: Optional[int] = Field(None, description="Total number of channels", gt=0)
    
    model_config = ConfigDict(validate_assignment=True)


class InputChangedCommand(BaseModel):
    """
    Input changed command to notify baby analyzer of metadata changes.
    
    Purpose: Notifies baby analyzer when the input stream metadata has changed.
    Triggers reconfiguration of the processing pipeline.
    """
    type: Literal[CommandType.INPUT_CHANGED] = CommandType.INPUT_CHANGED
    metadata: RecordingMetadata = Field(..., description="Updated recording metadata")
    
    model_config = ConfigDict(validate_assignment=True, use_enum_values=True)


class ColormapCommand(BaseModel):
    """
    Colormap command to change PNG output colormap.
    
    Purpose: Dynamically changes the colormap used for PNG output generation.
    """
    type: Literal[CommandType.COLORMAP] = CommandType.COLORMAP
    value: ColorMap = Field(..., description="Colormap name")
    
    model_config = ConfigDict(validate_assignment=True, use_enum_values=True)


class CAxisRange(BaseModel):
    """Color axis range structure."""
    min: float = Field(..., description="Minimum color axis value")
    max: float = Field(..., description="Maximum color axis value")
    
    @field_validator('max')
    @classmethod
    def validate_range(cls, v: float, info: ValidationInfo) -> float:
        if info.data.get('min') is not None and v <= info.data['min']:
            raise ValueError('max must be > min')
        return v
    
    model_config = ConfigDict(validate_assignment=True)


class CaxisCommand(BaseModel):
    """
    Caxis command to adjust color axis range.
    
    Purpose: Dynamically adjusts the color axis range for visualization.
    Used for adjusting contrast and brightness in output.
    """
    type: Literal[CommandType.CAXIS] = CommandType.CAXIS
    value: CAxisRange = Field(..., description="Color axis range")
    
    model_config = ConfigDict(validate_assignment=True, use_enum_values=True)


class RegionOfInterest(BaseModel):
    """Region of interest structure for sensor range."""
    start: int = Field(..., description="Start sensor index", ge=0)
    end: int = Field(..., description="End sensor index", ge=0)
    
    @field_validator('end')
    @classmethod
    def validate_range(cls, v: int, info: ValidationInfo) -> int:
        if info.data.get('start') is not None and v <= info.data['start']:
            raise ValueError('end must be > start')
        return v
    
    model_config = ConfigDict(validate_assignment=True)


class RegionOfInterestCommand(BaseModel):
    """
    Region of interest command to change sensor range.
    
    Purpose: Dynamically changes the region of interest (sensor range) during processing.
    Triggers pipeline reinitialization with new ROI.
    """
    type: Literal[CommandType.REGION_OF_INTEREST] = CommandType.REGION_OF_INTEREST
    value: RegionOfInterest = Field(..., description="Region of interest range")
    
    model_config = ConfigDict(validate_assignment=True, use_enum_values=True)


class MonitorQueuesValue(BaseModel):
    """Monitor queues value structure."""
    queues_to_monitor: List[str] = Field(
        ..., 
        description="List of queue names to monitor for throttling",
        min_length=1
    )
    
    model_config = ConfigDict(validate_assignment=True)


class MonitorQueuesCommand(BaseModel):
    """
    Monitor queues command to add queues for throttling.
    
    Purpose: Adds queues to monitor for throttling control.
    Used to prevent memory overflow by monitoring queue depths.
    """
    type: Literal[CommandType.MONITOR_QUEUES] = CommandType.MONITOR_QUEUES
    value: MonitorQueuesValue = Field(..., description="Queues to monitor")
    
    model_config = ConfigDict(validate_assignment=True, use_enum_values=True)


# ===================================================================
# Focus Server Waterfall API Models
# ===================================================================

class SensorData(BaseModel):
    """Individual sensor data in a waterfall row."""
    id: int = Field(..., description="Sensor ID", ge=0)
    intensity: List[float] = Field(..., description="Intensity values for this sensor")
    
    model_config = ConfigDict(validate_assignment=True)


class WaterfallRow(BaseModel):
    """Single row of waterfall data."""
    canvasId: str = Field(..., description="Canvas identifier")
    sensors: List[SensorData] = Field(..., description="Sensor data for this row")
    startTimestamp: int = Field(..., description="Row start timestamp (epoch millis)", ge=0)
    endTimestamp: int = Field(..., description="Row end timestamp (epoch millis)", ge=0)
    
    @field_validator('endTimestamp')
    @classmethod
    def validate_timestamps(cls, v: int, info: ValidationInfo) -> int:
        if info.data.get('startTimestamp') and v <= info.data['startTimestamp']:
            raise ValueError('endTimestamp must be > startTimestamp')
        return v
    
    model_config = ConfigDict(validate_assignment=True)


class WaterfallResponseData(BaseModel):
    """Waterfall response data structure."""
    rows: List[WaterfallRow] = Field(..., description="Waterfall rows")
    current_max_amp: float = Field(..., description="Current maximum amplitude")
    current_min_amp: float = Field(..., description="Current minimum amplitude")
    
    @field_validator('current_max_amp')
    @classmethod
    def validate_amplitude_range(cls, v: float, info: ValidationInfo) -> float:
        if info.data.get('current_min_amp') is not None and v < info.data['current_min_amp']:
            raise ValueError('current_max_amp must be >= current_min_amp')
        return v
    
    model_config = ConfigDict(validate_assignment=True)


class WaterfallResponse(BaseModel):
    """
    Response model for waterfall endpoint.
    
    Status codes:
    - 200: Empty response (no data available yet)
    - 201: Data retrieved successfully
    - 208: Baby analyzer has exited
    - 400: Invalid row_count
    - 404: Consumer not found
    """
    status_code: int = Field(..., description="HTTP status code")
    data: Optional[List[WaterfallResponseData]] = Field(None, description="Waterfall data (if available)")
    message: Optional[str] = Field(None, description="Status message")
    
    model_config = ConfigDict(validate_assignment=True)
    
    @field_validator('status_code')
    @classmethod
    def validate_status_code(cls, v: int) -> int:
        valid_codes = [200, 201, 208, 400, 404]
        if v not in valid_codes:
            raise ValueError(f'status_code must be one of: {valid_codes}')
        return v


# ===================================================================
# Focus Server Configuration Models (Updated)
# ===================================================================

class CanvasInfo(BaseModel):
    """Canvas information for configuration."""
    height: int = Field(..., description="Canvas height in pixels", gt=0)
    
    model_config = ConfigDict(validate_assignment=True)


class SensorRange(BaseModel):
    """Sensor range configuration."""
    min: int = Field(..., description="Minimum sensor index", ge=0)
    max: int = Field(..., description="Maximum sensor index", ge=0)
    
    @field_validator('max')
    @classmethod
    def validate_range(cls, v: int, info: ValidationInfo) -> int:
        if info.data.get('min') is not None and v <= info.data['min']:
            raise ValueError('max sensor must be > min sensor')
        return v
    
    model_config = ConfigDict(validate_assignment=True)


class FrequencyRangeConfig(BaseModel):
    """Frequency range configuration."""
    min: int = Field(..., description="Minimum frequency (Hz)", ge=0)
    max: int = Field(..., description="Maximum frequency (Hz)", ge=0)
    
    @field_validator('max')
    @classmethod
    def validate_range(cls, v: int, info: ValidationInfo) -> int:
        if info.data.get('min') is not None and v <= info.data['min']:
            raise ValueError('max frequency must be > min frequency')
        return v
    
    model_config = ConfigDict(validate_assignment=True)


class FocusServerConfigRequest(BaseModel):
    """
    Configuration request for Focus Server /config/{task_id} endpoint.
    
    Creates and starts a new baby analyzer instance for processing DAS data.
    """
    displayTimeAxisDuration: float = Field(..., description="Display time axis duration", gt=0)
    nfftSelection: int = Field(..., description="NFFT selection for spectrogram", gt=0)
    canvasInfo: CanvasInfo = Field(..., description="Canvas display configuration")
    sensors: SensorRange = Field(..., description="Sensor range to process")
    frequencyRange: FrequencyRangeConfig = Field(..., description="Frequency range for processing")
    start_time: Optional[str] = Field(None, description="Start time (format: yymmddHHMMSS) or null for live")
    end_time: Optional[str] = Field(None, description="End time (format: yymmddHHMMSS) or null for live")
    
    model_config = ConfigDict(validate_assignment=True)
    
    @field_validator('start_time', 'end_time')
    @classmethod
    def validate_time_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate time format if provided."""
        if v is not None and len(v) != 12:
            raise ValueError('Time format must be: yymmddHHMMSS (12 characters)')
        return v
    
    @field_validator('end_time')
    @classmethod
    def validate_time_range(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        """Validate end_time > start_time if both provided."""
        start = info.data.get('start_time')
        if v is not None and start is not None:
            if v <= start:
                raise ValueError('end_time must be > start_time')
        return v


class SensorsResponse(BaseModel):
    """
    Response model for /sensors endpoint.
    
    Returns the total number of available sensors on the fiber.
    """
    sensors: List[int] = Field(..., description="List of available sensor indices")
    
    model_config = ConfigDict(validate_assignment=True)


class TaskMetadataResponse(BaseModel):
    """
    Response model for /metadata/{task_id} endpoint.
    
    Returns metadata for a specific task's recording.
    """
    status_code: int = Field(..., description="HTTP status code (200=not running, 201=active, 404=invalid)")
    metadata: Optional[RecordingMetadata] = Field(None, description="Recording metadata (if available)")
    
    model_config = ConfigDict(validate_assignment=True)
    
    @field_validator('status_code')
    @classmethod
    def validate_status_code(cls, v: int) -> int:
        valid_codes = [200, 201, 404]
        if v not in valid_codes:
            raise ValueError(f'status_code must be one of: {valid_codes}')
        return v


# ===================================================================
# Baby Analyzer CLI Argument Models
# ===================================================================

class BabyAnalyzerConfig(BaseModel):
    """
    Configuration model for Baby Analyzer CLI arguments.
    
    Validates all command-line arguments for the baby analyzer processing pipeline.
    This is useful for programmatically generating baby analyzer commands.
    """
    # Input/Output
    in_paths: List[str] = Field(..., description="Input recording paths", min_length=1)
    out_path: str = Field(..., description="Output path")
    queue_name: Optional[str] = Field(None, description="Custom queue name for MQ input")
    backend: Optional[Literal["prp2", "segy", "png", "wav"]] = Field(None, description="Output backend")
    
    # Region of Interest
    roi_start: Optional[int] = Field(None, description="ROI start sensor/pixel", ge=0)
    roi_end: Optional[int] = Field(None, description="ROI end sensor/pixel", ge=0)
    roi_use_meters: bool = Field(False, description="Interpret ROI as meters instead of pixels")
    
    # Spectrogram
    spectrogram_nfft: Optional[int] = Field(None, description="Spectrogram NFFT bins", gt=0)
    sg_overlap: float = Field(0.5, description="Spectrogram window overlap", ge=0, le=1)
    sg_window_time: Optional[float] = Field(None, description="STFT window duration (seconds)", gt=0)
    sg_range_start: Optional[int] = Field(None, description="Spectrogram frequency range start (Hz)", ge=0)
    sg_range_end: Optional[int] = Field(None, description="Spectrogram frequency range end (Hz)", ge=0)
    sg_log_scale: bool = Field(False, description="Output in logarithmic dB scale")
    sg_normalize_window: bool = Field(False, description="Normalize by window factor")
    
    # Decimation
    decimation_x: Optional[int] = Field(None, description="Spatial axis decimation factor", gt=0)
    decimation_t: Optional[int] = Field(None, description="Time axis decimation factor", gt=0)
    
    # Time Range & Playback
    time_start: Optional[str] = Field(None, description="Start datetime (YYYY-MM-DD:HH:MM:SS)")
    time_end: Optional[str] = Field(None, description="End datetime (YYYY-MM-DD:HH:MM:SS)")
    playrate: float = Field(1.0, description="Playback speed multiplier", gt=0)
    
    # Output Configuration
    caxis_min: Optional[float] = Field(None, description="Minimum value for PNG/WAV normalization")
    caxis_max: Optional[float] = Field(None, description="Maximum value for PNG/WAV normalization")
    colormap: ColorMap = Field(ColorMap.PARULA, description="PNG colormap")
    
    # Control & Monitoring
    big_boy_stream: Optional[str] = Field(None, description="Enable command listening on stream")
    keepalive_timeout: Optional[int] = Field(None, description="Auto-exit timeout (seconds)", gt=0)
    eoj: bool = Field(False, description="Send end-of-job message on completion")
    
    # Logging
    log_name: Optional[str] = Field(None, description="Log file name")
    verbose_console: bool = Field(False, description="Verbose console logging")
    verbose_file: bool = Field(False, description="Verbose file logging")
    debug: bool = Field(False, description="Enable debug mode")
    
    model_config = ConfigDict(validate_assignment=True, use_enum_values=True)
    
    @field_validator('roi_end')
    @classmethod
    def validate_roi_range(cls, v: Optional[int], info: ValidationInfo) -> Optional[int]:
        """Validate ROI end > start."""
        roi_start = info.data.get('roi_start')
        if v is not None and roi_start is not None and v <= roi_start:
            raise ValueError('roi_end must be > roi_start')
        return v
    
    @field_validator('sg_range_end')
    @classmethod
    def validate_sg_range(cls, v: Optional[int], info: ValidationInfo) -> Optional[int]:
        """Validate spectrogram frequency range."""
        sg_start = info.data.get('sg_range_start')
        if v is not None and sg_start is not None and v <= sg_start:
            raise ValueError('sg_range_end must be > sg_range_start')
        return v
    
    @field_validator('caxis_max')
    @classmethod
    def validate_caxis_range(cls, v: Optional[float], info: ValidationInfo) -> Optional[float]:
        """Validate color axis range."""
        caxis_min = info.data.get('caxis_min')
        if v is not None and caxis_min is not None and v <= caxis_min:
            raise ValueError('caxis_max must be > caxis_min')
        return v
    
    def to_cli_args(self) -> List[str]:
        """
        Convert configuration to CLI arguments list.
        
        Returns:
            List of command-line arguments for baby_analyzer
        """
        args = []
        
        # Input/Output
        args.extend(self.in_paths)
        args.append(self.out_path)
        
        if self.queue_name:
            args.extend(["--queue-name", self.queue_name])
        
        if self.backend:
            args.extend(["--backend", self.backend])
        
        # ROI
        if self.roi_start is not None and self.roi_end is not None:
            args.extend(["-r", str(self.roi_start), str(self.roi_end)])
            if self.roi_use_meters:
                args.append("--roi-use-meters")
        
        # Spectrogram
        if self.spectrogram_nfft:
            args.extend(["-sg", str(self.spectrogram_nfft)])
            
            if self.sg_overlap != 0.5:
                args.extend(["--sg-overlap", str(self.sg_overlap)])
            
            if self.sg_window_time:
                args.extend(["--sg-window-time", str(self.sg_window_time)])
            
            if self.sg_range_start is not None and self.sg_range_end is not None:
                args.extend(["--sg-range", str(self.sg_range_start), str(self.sg_range_end)])
            
            if self.sg_log_scale:
                args.append("--sg-log-scale")
            
            if self.sg_normalize_window:
                args.append("--sg-normalize-window")
        
        # Decimation
        if self.decimation_x:
            args.extend(["-dx", str(self.decimation_x)])
        
        if self.decimation_t:
            args.extend(["-dt", str(self.decimation_t)])
        
        # Time Range
        if self.time_start:
            args.extend(["--time-start", self.time_start])
        
        if self.time_end:
            args.extend(["--time-end", self.time_end])
        
        if self.playrate != 1.0:
            args.extend(["--playrate", str(self.playrate)])
        
        # Output Configuration
        if self.caxis_min is not None and self.caxis_max is not None:
            args.extend(["--caxis", str(self.caxis_min), str(self.caxis_max)])
        
        if self.colormap != ColorMap.PARULA:
            args.extend(["--colormap", self.colormap])
        
        # Control
        if self.big_boy_stream:
            args.extend(["--big-boy", self.big_boy_stream])
        
        if self.keepalive_timeout:
            args.extend(["--keepalive-timeout", str(self.keepalive_timeout)])
        
        if self.eoj:
            args.append("--eoj")
        
        # Logging
        if self.log_name:
            args.extend(["--log-name", self.log_name])
        
        if self.verbose_console:
            args.append("-vc")
        
        if self.verbose_file:
            args.append("-vf")
        
        if self.debug:
            args.append("--debug")
        
        return args

