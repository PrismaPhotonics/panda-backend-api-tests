"""
Focus Server Data Models
========================

Pydantic models for Focus Server API requests and responses.
"""

from enum import IntEnum
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Tuple, Optional, Union, Any
from datetime import datetime


class ViewType(IntEnum):
    """View type enumeration for Focus Server."""
    MULTICHANNEL = 0
    SINGLECHANNEL = 1
    WATERFALL = 2


class DisplayInfo(BaseModel):
    """Display information for the canvas."""
    height: int = Field(..., description="Height of the canvas", gt=0)
    
    @validator('height')
    def validate_height(cls, v):
        if v <= 0:
            raise ValueError('Height must be positive')
        return v


class Channels(BaseModel):
    """Channel range configuration."""
    min: int = Field(..., description="Minimum channel value", ge=1)
    max: int = Field(..., description="Maximum channel value", ge=1)
    
    @validator('max')
    def validate_channel_range(cls, v, values):
        if 'min' in values and v < values['min']:
            raise ValueError('max channel must be >= min channel')
        return v


class FrequencyRange(BaseModel):
    """Frequency range configuration."""
    min: int = Field(..., description="Minimum frequency required", ge=0)
    max: int = Field(..., description="Maximum frequency required", ge=0)
    
    @validator('max')
    def validate_frequency_range(cls, v, values):
        if 'min' in values and v < values['min']:
            raise ValueError('max frequency must be >= min frequency')
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
    
    @validator('end_time')
    def validate_time_range(cls, v, values):
        if v is not None and 'start_time' in values and values['start_time'] is not None:
            if v <= values['start_time']:
                raise ValueError('end_time must be > start_time')
        return v
    
    @validator('view_type')
    def validate_waterfall_requirements(cls, v, values):
        if v == ViewType.WATERFALL:
            # For waterfall view, certain fields should not be set
            if 'displayTimeAxisDuration' in values and values['displayTimeAxisDuration'] is not None:
                raise ValueError('displayTimeAxisDuration not applicable for waterfall view')
            if 'frequencyRange' in values and values['frequencyRange'] is not None:
                raise ValueError('frequencyRange not applicable for waterfall view')
            if 'nfftSelection' in values and values['nfftSelection'] != 1:
                raise ValueError('nfftSelection must be 1 for waterfall view')
        return v
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True


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
    stream_port: int = Field(..., description="Port for the gRPC stream")
    stream_url: str = Field(..., description="URL for the gRPC stream")
    view_type: ViewType = Field(..., description="Type of view rendered")
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['success', 'error', 'pending', 'failed']
        if v.lower() not in valid_statuses:
            raise ValueError(f'Status must be one of: {valid_statuses}')
        return v.lower()
    
    @validator('stream_amount', 'frequencies_amount', 'channel_amount')
    def validate_positive_counts(cls, v):
        if v < 0:
            raise ValueError('Count values must be non-negative')
        return v
    
    @validator('stream_port')
    def validate_port_range(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError('Port must be between 1 and 65535')
        return v
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True


class ChannelRange(BaseModel):
    """Response model for channel range endpoint."""
    lowest_channel: int = Field(..., description="The lowest available channel number", ge=1)
    highest_channel: int = Field(..., description="The highest available channel number", ge=1)
    
    @validator('highest_channel')
    def validate_channel_range(cls, v, values):
        if 'lowest_channel' in values and v < values['lowest_channel']:
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
    
    @validator('fiber_length_meters')
    def validate_fiber_length(cls, v, values):
        if v is not None and 'fiber_start_meters' in values and values['fiber_start_meters'] is not None:
            if v <= values['fiber_start_meters']:
                raise ValueError('fiber_length_meters must be > fiber_start_meters')
        return v


class RecordingsInTimeRangeRequest(BaseModel):
    """Request model for recordings in time range endpoint."""
    start_time: int = Field(..., description="Start time in epoch format", ge=0)
    end_time: int = Field(..., description="End time in epoch format", ge=0)
    
    @validator('end_time')
    def validate_time_range(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be > start_time')
        return v


class RecordingsInTimeRangeResponse(BaseModel):
    """Response model for recordings in time range endpoint."""
    root: List[Tuple[int, int]] = Field(..., description="List of (start_time, end_time) tuples for available recordings")
    
    @validator('root')
    def validate_recordings(cls, v):
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
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True


class HealthCheckResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Health status")
    version: Optional[str] = Field(None, description="Service version")
    uptime: Optional[float] = Field(None, description="Service uptime in seconds")
    dependencies: Optional[Dict[str, str]] = Field(None, description="Dependency status")
    timestamp: Optional[datetime] = Field(None, description="Health check timestamp")
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['healthy', 'unhealthy', 'degraded']
        if v.lower() not in valid_statuses:
            raise ValueError(f'Status must be one of: {valid_statuses}')
        return v.lower()
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True


class JobStatusResponse(BaseModel):
    """Job status response model."""
    job_id: str = Field(..., description="Job identifier")
    status: str = Field(..., description="Job status")
    progress: Optional[float] = Field(None, description="Job progress percentage", ge=0, le=100)
    message: Optional[str] = Field(None, description="Status message")
    created_at: Optional[datetime] = Field(None, description="Job creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    completed_at: Optional[datetime] = Field(None, description="Job completion timestamp")
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['pending', 'running', 'completed', 'failed', 'cancelled']
        if v.lower() not in valid_statuses:
            raise ValueError(f'Status must be one of: {valid_statuses}')
        return v.lower()
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True