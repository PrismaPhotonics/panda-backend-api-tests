"""Pydantic models for Focus API contract tests.

These models define the request/response payloads used by the Focus/Streaming
server. They are used by tests to validate schema conformity of API responses.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, field_validator


class ChannelRange(BaseModel):
    """Represents the available channel range on the server.

    Attributes:
        lowest_channel: The lowest channel index (inclusive).
        highest_channel: The highest channel index (inclusive).
    """
    lowest_channel: int
    highest_channel: int

class Channels(BaseModel):
    """Requested channel bounds for processing/visualization.

    Attributes:
        min: Lower bound of desired channel selection (inclusive).
        max: Upper bound of desired channel selection (inclusive).
    """
    min: int
    max: int

    @field_validator("max")
    @classmethod
    def check_min_le_max(cls, v: int, info) -> int:
        min_val = info.data.get("min")
        if min_val is not None and v < min_val:
            raise ValueError("channels.max must be >= channels.min")
        return v

class FrequencyRange(BaseModel):
    """Requested frequency range in Hz.

    Attributes:
        min: Lower bound frequency in Hz.
        max: Upper bound frequency in Hz.
    """
    min: int
    max: int

    @field_validator("max")
    @classmethod
    def check_freq_min_le_max(cls, v: int, info) -> int:
        min_val = info.data.get("min")
        if min_val is not None and v < min_val:
            raise ValueError("frequencyRange.max must be >= frequencyRange.min")
        return v

class DisplayInfo(BaseModel):
    """Display configuration for the visualization surface."""
    height: int

ViewType = str

class ConfigureRequest(BaseModel):
    """Configuration payload for creating/updating a streaming job.

    Notes:
        - For waterfall view_type, frequencyRange and displayTimeAxisDuration
          are not applicable and nfftSelection should be 1.
        - start_time/end_time are epoch seconds for historical windows.
    """
    displayInfo: DisplayInfo
    channels: Channels
    view_type: ViewType
    displayTimeAxisDuration: Optional[int] = None
    nfftSelection: Optional[int] = None
    frequencyRange: Optional[FrequencyRange] = None
    start_time: Optional[int] = None
    end_time: Optional[int] = None

class ConfigureResponse(BaseModel):
    """Response describing the created/updated streaming job and stream info.

    Attributes provide mapping of channels to stream indices, streaming
    endpoints, and spectral parameters (frequencies, lines_dt, etc.).
    """
    status: str
    frequencies_list: List[float]
    lines_dt: float
    channel_to_stream_index: Dict[str, int]
    stream_amount: int
    job_id: str
    frequencies_amount: int
    channel_amount: int
    stream_port: int
    stream_url: str
    view_type: ViewType
    
    @field_validator("view_type", mode="before")
    @classmethod
    def convert_view_type(cls, v) -> str:
        """Convert int to string if server returns numeric view_type."""
        if isinstance(v, int):
            # Map common view_type integers to strings
            view_type_map = {
                0: "MultiChannelSpectrogram",
                1: "Waterfall",
                2: "SingleChannel",
            }
            return view_type_map.get(v, str(v))
        return str(v)

class LiveMetadata(BaseModel):
    """Live system metadata describing acquisition and system characteristics.

    Attributes:
        dx: Spatial sampling resolution (meters per channel).
        prr: Pulse repetition rate (samples per second).
        fiber_start_meters: Optional fiber starting position in meters.
        fiber_length_meters: Optional fiber length in meters.
        sw_version: Software version string.
        number_of_channels: Number of channels available (may be float from server, converted to int).
        fiber_description: Descriptive string for the fiber.
    """
    dx: float
    prr: float
    fiber_start_meters: Optional[int] = None
    fiber_length_meters: Optional[int] = None
    sw_version: str
    number_of_channels: int
    fiber_description: str
    
    @field_validator("number_of_channels", mode="before")
    @classmethod
    def convert_number_of_channels(cls, v) -> int:
        """Convert float to int if server returns fractional number."""
        if isinstance(v, float):
            return int(v)
        return int(v)

class RecordingsInTimeRangeRequest(BaseModel):
    """Request payload for querying recordings between two epoch timestamps."""
    start_time: int
    end_time: int

class RecordingsInTimeRangeResponse(BaseModel):
    """Response model containing a list of [start, end] epoch tuples.

    Ongoing recordings are represented with end == -1.
    """
    recordings: List[Tuple[int, int]]
