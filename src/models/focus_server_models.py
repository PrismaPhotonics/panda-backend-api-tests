"""
Focus Server Data Models
========================

Pydantic models for Focus Server API requests and responses.

Configuration Constraints (from New Production Client Config):
    - MAX_CHANNELS: 2222 (SensorsRange from usersettings.new_production_client.json)
    - MAX_FREQUENCY_HZ: 1000 (FrequencyMax from usersettings.new_production_client.json)
    - MIN_FREQUENCY_HZ: 0
    - MAX_NFFT: 2048 (for multi-channel view)
    - MAX_NFFT_SINGLE_CHANNEL: 65536 (for single-channel view)
"""

from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict, ValidationInfo
from typing import List, Dict, Tuple, Optional, Union, Any
from datetime import datetime


# ===================================================================
# Configuration Constants (from Client Config)
# ===================================================================

# Client Configuration: usersettings.new_production_client.json
# These values are enforced by the Panda client application

MAX_CHANNELS = 2222  # Maximum channels (SensorsRange)
MAX_FREQUENCY_HZ = 1000  # Maximum frequency in Hz (FrequencyMax)
MIN_FREQUENCY_HZ = 0  # Minimum frequency in Hz (FrequencyMin)
MIN_FREQUENCY_RANGE = 1  # Minimum frequency range size (FrequencyMinRange)

# NFFT Constraints
MAX_NFFT_MULTICHANNEL = 2048  # Maximum NFFT for multi-channel view
MAX_NFFT_SINGLECHANNEL = 65536  # Maximum NFFT for single-channel view
VALID_NFFT_POWER_OF_2 = [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]

# View Constraints
MAX_WINDOWS = 30  # Maximum concurrent windows


class ViewType(str, Enum):
    """View type enumeration for Focus Server."""
    MULTICHANNEL = "0"
    SINGLECHANNEL = "1"
    WATERFALL = "2"


class DisplayInfo(BaseModel):
    """Display information for the canvas."""
    height: int = Field(..., description="Height of the canvas", gt=0)
    
    @field_validator('height')
    @classmethod
    def validate_height(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('Height must be positive')
        return v


class Channels(BaseModel):
    """
    Channel range configuration.
    
    Constraints (from client config):
        - min >= 1
        - max >= min
        - total channels (max - min + 1) <= 2222 (MAX_CHANNELS)
    """
    min: int = Field(..., description="Minimum channel value", ge=1)
    max: int = Field(..., description="Maximum channel value", ge=1)
    
    @field_validator('max')
    @classmethod
    def validate_channel_range(cls, v: int, info: ValidationInfo) -> int:
        min_val = info.data.get('min')
        if min_val and v < min_val:
            raise ValueError(f'max channel ({v}) must be >= min channel ({min_val})')
        
        # Validate total channel count (from client config)
        if min_val:
            channel_count = v - min_val + 1
            if channel_count > MAX_CHANNELS:
                raise ValueError(
                    f'Channel count ({channel_count}) exceeds maximum ({MAX_CHANNELS}). '
                    f'Valid range: 1-{MAX_CHANNELS} channels'
                )
        
        return v


class FrequencyRange(BaseModel):
    """
    Frequency range configuration.
    
    Constraints (from client config):
        - min >= 0 (MIN_FREQUENCY_HZ)
        - max <= 1000 (MAX_FREQUENCY_HZ)
        - max > min (range must be positive)
        - (max - min) >= 1 (MIN_FREQUENCY_RANGE)
    """
    min: int = Field(..., description="Minimum frequency required", ge=MIN_FREQUENCY_HZ)
    max: int = Field(..., description="Maximum frequency required", ge=MIN_FREQUENCY_HZ)
    
    @field_validator('max')
    @classmethod
    def validate_frequency_range(cls, v: int, info: ValidationInfo) -> int:
        # Check max > min
        min_val = info.data.get('min')
        if min_val is not None and v < min_val:
            raise ValueError(f'max frequency ({v}) must be >= min frequency ({min_val})')
        
        # Check max <= MAX_FREQUENCY_HZ (from client config)
        if v > MAX_FREQUENCY_HZ:
            raise ValueError(
                f'Frequency max ({v} Hz) exceeds maximum ({MAX_FREQUENCY_HZ} Hz). '
                f'Valid range: {MIN_FREQUENCY_HZ}-{MAX_FREQUENCY_HZ} Hz'
            )
        
        # Check minimum range size
        if min_val is not None:
            range_size = v - min_val
            if range_size < MIN_FREQUENCY_RANGE:
                raise ValueError(
                    f'Frequency range ({range_size} Hz) is too small. '
                    f'Minimum range: {MIN_FREQUENCY_RANGE} Hz'
                )
        
        return v


class ConfigureRequest(BaseModel):
    """Request model for Focus Server configure endpoint."""
    displayTimeAxisDuration: Optional[int] = Field(
        None, 
        description="Duration to display on the time axis, not applicable for 'waterfall'",
        gt=0
    )
    nfftSelection: Optional[int] = Field(
        None, 
        description="NFFT selection, set to 1 for 'waterfall'",
        gt=0
    )
    displayInfo: DisplayInfo = Field(..., description="Display information")
    channels: Channels = Field(..., description="Channel range configuration")
    frequencyRange: Optional[FrequencyRange] = Field(
        None, 
        description="Frequency range, not applicable for 'waterfall'"
    )
    start_time: Optional[int] = Field(
        None, 
        description="Start time in epoch format",
        ge=0
    )
    end_time: Optional[int] = Field(
        None, 
        description="End time in epoch format",
        ge=0
    )
    view_type: ViewType = Field(..., description="Type of view to render")
    
    model_config = ConfigDict(use_enum_values=True, validate_assignment=True)
    
    @field_validator('view_type', mode='before')
    @classmethod
    def convert_view_type_input(cls, v: Union[int, str]) -> str:
        """Convert integer view_type to string for enum validation."""
        if isinstance(v, int):
            return str(v)
        return v
    
    @field_validator('end_time')
    @classmethod
    def validate_time_range(cls, v: Optional[int], info: ValidationInfo) -> Optional[int]:
        if v is not None and info.data.get('start_time') is not None:
            if v <= info.data['start_time']:
                raise ValueError('end_time must be > start_time')
        return v
    
    @field_validator('view_type')
    @classmethod
    def validate_waterfall_requirements(cls, v: ViewType, info: ValidationInfo) -> ViewType:
        if v == ViewType.WATERFALL:
            # For waterfall view, certain fields should not be set
            if info.data.get('displayTimeAxisDuration') is not None:
                raise ValueError('displayTimeAxisDuration not applicable for waterfall view')
            if info.data.get('frequencyRange') is not None:
                raise ValueError('frequencyRange not applicable for waterfall view')
            if info.data.get('nfftSelection') and info.data['nfftSelection'] != 1:
                raise ValueError('nfftSelection must be 1 for waterfall view')
        return v


class ConfigureResponse(BaseModel):
    """Response model for Focus Server configure endpoint."""
    status: str = Field(..., description="Status of the configuration")
    frequencies_list: List[float] = Field(..., description="List of predicted frequencies")
    lines_dt: float = Field(..., description="DT in seconds between two consecutive spectrogram calculations")
    channel_to_stream_index: Dict[str, int] = Field(..., description="Mapping of channel number to data stream ID")
    stream_amount: int = Field(..., description="Number of data streams")
    job_id: str = Field(..., description="Unique identifier for the streaming job")
    frequencies_amount: int = Field(..., description="Number of frequencies")
    channel_amount: int = Field(..., description="Number of channels")
    stream_port: Union[int, str] = Field(..., description="Port for the gRPC stream")
    stream_url: str = Field(..., description="URL for the gRPC stream")
    view_type: ViewType = Field(..., description="Type of view rendered")
    
    model_config = ConfigDict(use_enum_values=True, validate_assignment=True)
    
    @field_validator('view_type', mode='before')
    @classmethod
    def convert_view_type(cls, v: Union[int, str]) -> str:
        """Convert integer view_type to string for enum validation."""
        if isinstance(v, int):
            return str(v)
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        # Empty string is allowed (server may return this)
        if v == '':
            return v
        valid_statuses = ['success', 'error', 'pending', 'failed']
        if v.lower() not in valid_statuses:
            raise ValueError(f'Status must be one of: {valid_statuses}')
        return v.lower()
    
    @field_validator('stream_amount', 'frequencies_amount', 'channel_amount')
    @classmethod
    def validate_positive_counts(cls, v: int) -> int:
        if v < 0:
            raise ValueError('Count values must be non-negative')
        return v
    
    @field_validator('stream_port')
    @classmethod
    def validate_port_range(cls, v: Union[int, str]) -> Union[int, str]:
        # Convert to int if string
        port = int(v) if isinstance(v, str) else v
        if not (1 <= port <= 65535):
            raise ValueError('Port must be between 1 and 65535')
        return v


class ChannelRange(BaseModel):
    """Response model for channel range endpoint."""
    lowest_channel: int = Field(..., description="The lowest available channel number", ge=1)
    highest_channel: int = Field(..., description="The highest available channel number", ge=1)
    
    @field_validator('highest_channel')
    @classmethod
    def validate_channel_range(cls, v: int, info: ValidationInfo) -> int:
        if info.data.get('lowest_channel') and v < info.data['lowest_channel']:
            raise ValueError('highest_channel must be >= lowest_channel')
        return v


class LiveMetadata(BaseModel):
    """Response model for live metadata endpoint."""
    dx: float = Field(..., description="The distance between two consecutive channels", gt=0)
    prr: float = Field(..., description="Number of samples per second, default is 2000", gt=0)
    fiber_start_meters: Optional[int] = Field(
        None, 
        description="The distance from the start of the machine to the start of the monitored fiber",
        ge=0
    )
    fiber_length_meters: Optional[int] = Field(
        None, 
        description="The length of the fiber in meters",
        gt=0
    )
    sw_version: str = Field(..., description="Recording machine software version")
    number_of_channels: int = Field(..., description="Number of traces (sensors/channels)", gt=0)
    fiber_description: str = Field(..., description="Recording machine description of the fiber")
    
    @field_validator('fiber_length_meters')
    @classmethod
    def validate_fiber_length(cls, v: Optional[int], info: ValidationInfo) -> Optional[int]:
        if v is not None and info.data.get('fiber_start_meters') is not None:
            if v <= info.data['fiber_start_meters']:
                raise ValueError('fiber_length_meters must be > fiber_start_meters')
        return v


class RecordingsInTimeRangeRequest(BaseModel):
    """Request model for recordings in time range endpoint."""
    start_time: int = Field(..., description="Start time in epoch format", ge=0)
    end_time: int = Field(..., description="End time in epoch format", ge=0)
    
    @field_validator('end_time')
    @classmethod
    def validate_time_range(cls, v: int, info: ValidationInfo) -> int:
        if info.data.get('start_time') and v <= info.data['start_time']:
            raise ValueError('end_time must be > start_time')
        return v


class RecordingsInTimeRangeResponse(BaseModel):
    """Response model for recordings in time range endpoint."""
    root: List[Tuple[int, int]] = Field(..., description="List of (start_time, end_time) tuples for available recordings")
    
    @field_validator('root')
    @classmethod
    def validate_recordings(cls, v: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        for recording in v:
            if len(recording) != 2:
                raise ValueError('Each recording must be a tuple of (start_time, end_time)')
            start_time, end_time = recording
            if start_time < 0 or end_time < 0:
                raise ValueError('Recording times must be non-negative')
            if end_time <= start_time:
                raise ValueError('Recording end_time must be > start_time')
        return v


class ErrorResponse(BaseModel):
    """Error response model for API errors."""
    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: Optional[datetime] = Field(None, description="Error timestamp")
    
    model_config = ConfigDict(validate_assignment=True)


class HealthCheckResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Health status")
    version: Optional[str] = Field(None, description="Service version")
    uptime: Optional[float] = Field(None, description="Service uptime in seconds")
    dependencies: Optional[Dict[str, str]] = Field(None, description="Dependency status")
    timestamp: Optional[datetime] = Field(None, description="Health check timestamp")
    
    model_config = ConfigDict(validate_assignment=True)
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid_statuses = ['healthy', 'unhealthy', 'degraded']
        if v.lower() not in valid_statuses:
            raise ValueError(f'Status must be one of: {valid_statuses}')
        return v.lower()


class JobStatusResponse(BaseModel):
    """Job status response model."""
    job_id: str = Field(..., description="Job identifier")
    status: str = Field(..., description="Job status")
    progress: Optional[float] = Field(None, description="Job progress percentage", ge=0, le=100)
    message: Optional[str] = Field(None, description="Status message")
    created_at: Optional[datetime] = Field(None, description="Job creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    completed_at: Optional[datetime] = Field(None, description="Job completion timestamp")
    
    model_config = ConfigDict(validate_assignment=True)
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid_statuses = ['pending', 'running', 'completed', 'failed', 'cancelled']
        if v.lower() not in valid_statuses:
            raise ValueError(f'Status must be one of: {valid_statuses}')
        return v.lower()


# ===================================================================
# New API Models (As per Complete API Documentation)
# ===================================================================

class ConfigTaskRequest(BaseModel):
    """
    Configuration request for POST /config/{task_id} endpoint.
    
    Configures and starts a new baby analyzer instance for processing DAS data.
    """
    displayTimeAxisDuration: float = Field(..., description="Display time axis duration", gt=0)
    nfftSelection: int = Field(..., description="NFFT selection for spectrogram", gt=0)
    canvasInfo: Dict[str, int] = Field(..., description="Canvas info with height key")
    sensors: Dict[str, int] = Field(..., description="Sensor range (min, max)")
    frequencyRange: Dict[str, int] = Field(..., description="Frequency range (min, max)")
    start_time: Optional[str] = Field(None, description="Start time (yymmddHHMMSS) or null for live")
    end_time: Optional[str] = Field(None, description="End time (yymmddHHMMSS) or null for live")
    
    model_config = ConfigDict(validate_assignment=True)
    
    @field_validator('canvasInfo')
    @classmethod
    def validate_canvas_info(cls, v: Dict[str, int]) -> Dict[str, int]:
        """Validate canvas info contains height."""
        if 'height' not in v or v['height'] <= 0:
            raise ValueError('canvasInfo must contain positive height')
        return v
    
    @field_validator('sensors')
    @classmethod
    def validate_sensors(cls, v: Dict[str, int]) -> Dict[str, int]:
        """Validate sensor range."""
        if 'min' not in v or 'max' not in v:
            raise ValueError('sensors must contain min and max keys')
        if v['max'] <= v['min']:
            raise ValueError('sensors.max must be > sensors.min')
        return v
    
    @field_validator('frequencyRange')
    @classmethod
    def validate_frequency_range(cls, v: Dict[str, int]) -> Dict[str, int]:
        """Validate frequency range."""
        if 'min' not in v or 'max' not in v:
            raise ValueError('frequencyRange must contain min and max keys')
        if v['max'] <= v['min']:
            raise ValueError('frequencyRange.max must be > frequencyRange.min')
        return v
    
    @model_validator(mode='after')
    def validate_time_range(self) -> 'ConfigTaskRequest':
        """Validate time range for historic playback."""
        # Only validate if both times are provided (historic mode)
        if self.start_time and self.end_time:
            # Both times should be valid format (yymmddHHMMSS)
            import re
            time_pattern = r'^\d{12}$'
            
            if not re.match(time_pattern, self.start_time):
                raise ValueError('start_time must be in format yymmddHHMMSS (12 digits)')
            if not re.match(time_pattern, self.end_time):
                raise ValueError('end_time must be in format yymmddHHMMSS (12 digits)')
            
            # Check that end_time > start_time
            if self.end_time <= self.start_time:
                raise ValueError('end_time must be > start_time for historic playback')
        
        return self


class ConfigTaskResponse(BaseModel):
    """
    Response model for POST /config/{task_id} endpoint.
    
    Response codes:
    - 200: Config received successfully
    - 500: Error parsing configuration
    """
    status: str = Field(..., description="Response status message")
    task_id: Optional[str] = Field(None, description="Task ID that was configured")
    
    model_config = ConfigDict(validate_assignment=True)


class SensorsListResponse(BaseModel):
    """
    Response model for GET /sensors endpoint.
    
    Returns list of available sensor indices.
    """
    sensors: List[int] = Field(..., description="List of sensor indices [0, 1, 2, ..., n]")
    
    model_config = ConfigDict(validate_assignment=True)


class LiveMetadataFlat(BaseModel):
    """
    Response model for GET /live_metadata endpoint.
    
    Returns flat dictionary of RecordingMetadata fields.
    """
    prr: float = Field(..., description="Pulse repetition rate", gt=0)
    num_samples_per_trace: int = Field(..., description="Samples per trace", gt=0)
    dtype: str = Field(..., description="Data type")
    dx: Optional[float] = Field(None, description="Distance between sensors (meters)", gt=0)
    fiber_start_meters: Optional[int] = Field(None, description="Fiber start offset", ge=0)
    fiber_length_meters: Optional[int] = Field(None, description="Fiber length", gt=0)
    sw_version: Optional[str] = Field(None, description="Software version")
    number_of_channels: Optional[int] = Field(None, description="Number of channels", gt=0)
    fiber_description: Optional[str] = Field(None, description="Fiber description")
    
    model_config = ConfigDict(validate_assignment=True)


class WaterfallSensorData(BaseModel):
    """Individual sensor data in waterfall row."""
    id: int = Field(..., description="Sensor ID", ge=0)
    intensity: List[float] = Field(..., description="Intensity values")
    
    model_config = ConfigDict(validate_assignment=True)


class WaterfallRowData(BaseModel):
    """Single waterfall row."""
    canvasId: str = Field(..., description="Canvas identifier")
    sensors: List[WaterfallSensorData] = Field(..., description="Sensor data")
    startTimestamp: int = Field(..., description="Start timestamp (epoch millis)", ge=0)
    endTimestamp: int = Field(..., description="End timestamp (epoch millis)", ge=0)
    
    @field_validator('endTimestamp')
    @classmethod
    def validate_timestamps(cls, v: int, info: ValidationInfo) -> int:
        if info.data.get('startTimestamp') and v <= info.data['startTimestamp']:
            raise ValueError('endTimestamp must be > startTimestamp')
        return v
    
    model_config = ConfigDict(validate_assignment=True)


class WaterfallDataBlock(BaseModel):
    """Waterfall data block containing rows and amplitude range."""
    rows: List[WaterfallRowData] = Field(..., description="Waterfall rows")
    current_max_amp: float = Field(..., description="Current maximum amplitude")
    current_min_amp: float = Field(..., description="Current minimum amplitude")
    
    model_config = ConfigDict(validate_assignment=True)


class WaterfallGetResponse(BaseModel):
    """
    Response model for GET /waterfall/{task_id}/{row_count} endpoint.
    
    Response codes:
    - 200: Empty response (no data available yet)
    - 201: Data retrieved successfully
    - 208: Baby analyzer has exited
    - 400: Invalid row_count (must be > 0)
    - 404: Consumer not found for task_id
    """
    status_code: int = Field(..., description="HTTP status code")
    data: Optional[List[WaterfallDataBlock]] = Field(None, description="Waterfall data blocks")
    message: Optional[str] = Field(None, description="Status message")
    
    model_config = ConfigDict(validate_assignment=True)
    
    @field_validator('status_code')
    @classmethod
    def validate_status_code(cls, v: int) -> int:
        valid_codes = [200, 201, 208, 400, 404]
        if v not in valid_codes:
            raise ValueError(f'status_code must be one of: {valid_codes}')
        return v


class TaskMetadataGetResponse(BaseModel):
    """
    Response model for GET /metadata/{task_id} endpoint.
    
    Response codes:
    - 200: Empty (consumer not running)
    - 201: Metadata dictionary returned
    - 404: Invalid task_id
    """
    status_code: int = Field(..., description="HTTP status code")
    metadata: Optional[LiveMetadataFlat] = Field(None, description="Task metadata")
    
    model_config = ConfigDict(validate_assignment=True)
    
    @field_validator('status_code')
    @classmethod
    def validate_status_code(cls, v: int) -> int:
        valid_codes = [200, 201, 404]
        if v not in valid_codes:
            raise ValueError(f'status_code must be one of: {valid_codes}')
        return v