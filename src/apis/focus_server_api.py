"""
Focus Server API Client
========================

API client for Focus Server with comprehensive error handling and validation.
"""

import logging
from typing import Dict, Any, Optional

from src.core.api_client import BaseAPIClient
from src.core.exceptions import APIError, ValidationError
from src.models.focus_server_models import (
    ConfigureRequest, ConfigureResponse, ChannelRange, LiveMetadata,
    RecordingsInTimeRangeRequest, RecordingsInTimeRangeResponse,
    ConfigTaskRequest, ConfigTaskResponse, SensorsListResponse,
    LiveMetadataFlat, WaterfallGetResponse, TaskMetadataGetResponse
)


class FocusServerAPI(BaseAPIClient):
    """
    Focus Server API client with comprehensive functionality.
    
    Provides methods for all Focus Server endpoints with proper
    error handling, validation, and logging.
    """
    
    def __init__(self, config_manager):
        """
        Initialize Focus Server API client.
        
        Args:
            config_manager: Configuration manager instance
        """
        # Get API configuration
        api_config = config_manager.get_api_config()
        base_url = api_config.get("base_url")
        timeout = config_manager.get("api_client.timeout", 60)
        max_retries = config_manager.get("api_client.retry.max_attempts", 3)
        
        if not base_url:
            raise ValidationError("Focus Server base URL not configured")
        
        super().__init__(base_url, timeout, max_retries)
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"Focus Server API client initialized for {base_url}")
    
    def configure_streaming_job(self, payload: ConfigureRequest) -> ConfigureResponse:
        """
        Configure a streaming job.
        
        Args:
            payload: Configuration request payload
            
        Returns:
            Configuration response
            
        Raises:
            APIError: If API call fails
            ValidationError: If payload validation fails
        """
        self.logger.info("Configuring streaming job")
        
        try:
            # Validate payload
            if not isinstance(payload, ConfigureRequest):
                raise ValidationError("Payload must be a ConfigureRequest instance")
            
            # Convert to dict for JSON serialization
            payload_dict = payload.model_dump()
            
            # Send request
            response = self.post("/configure", json=payload_dict)
            
            # Parse response
            response_data = response.json()
            configure_response = ConfigureResponse(**response_data)
            
            self.logger.info(f"Streaming job configured successfully: {configure_response.job_id}")
            return configure_response
            
        except Exception as e:
            self.logger.error(f"Failed to configure streaming job: {e}")
            if isinstance(e, (APIError, ValidationError)):
                raise
            raise APIError(f"Failed to configure streaming job: {e}") from e
    
    def get_channels(self) -> ChannelRange:
        """
        Get available channel range.
        
        Returns:
            Channel range information
            
        Raises:
            APIError: If API call fails
        """
        self.logger.debug("Getting channel range")
        
        try:
            response = self.get("/channels")
            response_data = response.json()
            
            channel_range = ChannelRange(**response_data)
            self.logger.debug(f"Channel range: {channel_range.lowest_channel}-{channel_range.highest_channel}")
            
            return channel_range
            
        except Exception as e:
            self.logger.error(f"Failed to get channel range: {e}")
            if isinstance(e, APIError):
                raise
            raise APIError(f"Failed to get channel range: {e}") from e
    
    def get_live_metadata(self) -> LiveMetadata:
        """
        Get live metadata information.
        
        Returns:
            Live metadata information
            
        Raises:
            APIError: If API call fails
        """
        self.logger.debug("Getting live metadata")
        
        try:
            response = self.get("/live_metadata")
            response_data = response.json()
            
            live_metadata = LiveMetadata(**response_data)
            self.logger.debug(f"Live metadata: {live_metadata.sw_version}, {live_metadata.number_of_channels} channels")
            
            return live_metadata
            
        except Exception as e:
            self.logger.error(f"Failed to get live metadata: {e}")
            if isinstance(e, APIError):
                raise
            raise APIError(f"Failed to get live metadata: {e}") from e
    
    def get_job_metadata(self, job_id: str) -> ConfigureResponse:
        """
        Get job metadata by job ID.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job metadata
            
        Raises:
            APIError: If API call fails
            ValidationError: If job_id is invalid
        """
        if not job_id or not isinstance(job_id, str):
            raise ValidationError("Job ID must be a non-empty string")
        
        self.logger.debug(f"Getting job metadata for job ID: {job_id}")
        
        try:
            response = self.get(f"/metadata/{job_id}")
            response_data = response.json()
            
            job_metadata = ConfigureResponse(**response_data)
            self.logger.debug(f"Job metadata retrieved for job ID: {job_id}")
            
            return job_metadata
            
        except Exception as e:
            self.logger.error(f"Failed to get job metadata for job ID {job_id}: {e}")
            if isinstance(e, APIError):
                raise
            raise APIError(f"Failed to get job metadata: {e}") from e
    
    def get_recordings_in_time_range(self, payload: RecordingsInTimeRangeRequest) -> RecordingsInTimeRangeResponse:
        """
        Get recordings available in a time range.
        
        Args:
            payload: Time range request payload
            
        Returns:
            Recordings in time range response
            
        Raises:
            APIError: If API call fails
            ValidationError: If payload validation fails
        """
        self.logger.debug("Getting recordings in time range")
        
        try:
            # Validate payload
            if not isinstance(payload, RecordingsInTimeRangeRequest):
                raise ValidationError("Payload must be a RecordingsInTimeRangeRequest instance")
            
            # Convert to dict for JSON serialization
            payload_dict = payload.model_dump()
            
            # Send request
            response = self.post("/recordings_in_time_range", json=payload_dict)
            
            # Parse response
            response_data = response.json()
            recordings_response = RecordingsInTimeRangeResponse(root=response_data)
            
            self.logger.debug(f"Found {len(recordings_response.root)} recordings in time range")
            return recordings_response
            
        except Exception as e:
            self.logger.error(f"Failed to get recordings in time range: {e}")
            if isinstance(e, (APIError, ValidationError)):
                raise
            raise APIError(f"Failed to get recordings in time range: {e}") from e
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of the Focus Server.
        
        Returns:
            Health status information
            
        Raises:
            APIError: If API call fails
        """
        self.logger.debug("Getting health status")
        
        try:
            response = self.get("/health")
            health_data = response.json()
            
            self.logger.debug(f"Health status: {health_data.get('status', 'unknown')}")
            return health_data
            
        except Exception as e:
            self.logger.error(f"Failed to get health status: {e}")
            if isinstance(e, APIError):
                raise
            raise APIError(f"Failed to get health status: {e}") from e
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get job status by job ID.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job status information
            
        Raises:
            APIError: If API call fails
            ValidationError: If job_id is invalid
        """
        if not job_id or not isinstance(job_id, str):
            raise ValidationError("Job ID must be a non-empty string")
        
        self.logger.debug(f"Getting job status for job ID: {job_id}")
        
        try:
            response = self.get(f"/job/{job_id}/status")
            status_data = response.json()
            
            self.logger.debug(f"Job status for {job_id}: {status_data.get('status', 'unknown')}")
            return status_data
            
        except Exception as e:
            self.logger.error(f"Failed to get job status for job ID {job_id}: {e}")
            if isinstance(e, APIError):
                raise
            raise APIError(f"Failed to get job status: {e}") from e
    
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a job by job ID.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if job was cancelled successfully
            
        Raises:
            APIError: If API call fails
            ValidationError: If job_id is invalid
        """
        if not job_id or not isinstance(job_id, str):
            raise ValidationError("Job ID must be a non-empty string")
        
        self.logger.info(f"Cancelling job: {job_id}")
        
        try:
            response = self.delete(f"/job/{job_id}")
            
            if response.status_code == 200:
                self.logger.info(f"Job {job_id} cancelled successfully")
                return True
            else:
                self.logger.warning(f"Job {job_id} cancellation returned status {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to cancel job {job_id}: {e}")
            if isinstance(e, APIError):
                raise
            raise APIError(f"Failed to cancel job: {e}") from e
    
    def validate_connection(self) -> bool:
        """
        Validate connection to Focus Server.
        
        Returns:
            True if connection is valid
        """
        try:
            # Try to get channels as a simple health check
            self.get_channels()
            self.logger.info("Focus Server connection validated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Focus Server connection validation failed: {e}")
            return False
    
    def get_api_info(self) -> Dict[str, Any]:
        """
        Get API information and version.
        
        Returns:
            API information
            
        Raises:
            APIError: If API call fails
        """
        self.logger.debug("Getting API information")
        
        try:
            response = self.get("/info")
            api_info = response.json()
            
            self.logger.debug(f"API version: {api_info.get('version', 'unknown')}")
            return api_info
            
        except Exception as e:
            self.logger.error(f"Failed to get API information: {e}")
            if isinstance(e, APIError):
                raise
            raise APIError(f"Failed to get API information: {e}") from e
    
    # ===================================================================
    # New API Methods (Complete API Documentation)
    # ===================================================================
    
    def config_task(self, task_id: str, payload: ConfigTaskRequest) -> ConfigTaskResponse:
        """
        Configure and start a new baby analyzer instance for processing DAS data.
        
        POST /config/{task_id}
        
        Args:
            task_id: Unique identifier for the processing task
            payload: Configuration request payload
            
        Returns:
            Configuration response
            
        Raises:
            APIError: If API call fails (500: error parsing configuration)
            ValidationError: If payload validation fails
        
        Flow:
            - Creates baby analyzer command with spectrogram processing
            - Starts baby analyzer via SvClient
            - Creates buffered recording consumer for the task
            - Determines live vs historic mode based on timestamps
        """
        if not task_id or not isinstance(task_id, str):
            raise ValidationError("task_id must be a non-empty string")
        
        self.logger.info(f"Configuring task: {task_id}")
        
        try:
            # Validate payload
            if not isinstance(payload, ConfigTaskRequest):
                raise ValidationError("Payload must be a ConfigTaskRequest instance")
            
            # Convert to dict for JSON serialization
            payload_dict = payload.model_dump()
            
            # Send request
            response = self.post(f"/config/{task_id}", json=payload_dict)
            
            # Parse response
            response_data = response.json()
            config_response = ConfigTaskResponse(**response_data)
            
            self.logger.info(f"Task {task_id} configured successfully")
            return config_response
            
        except Exception as e:
            self.logger.error(f"Failed to configure task {task_id}: {e}")
            if isinstance(e, (APIError, ValidationError)):
                raise
            raise APIError(f"Failed to configure task: {e}") from e
    
    def get_sensors(self) -> SensorsListResponse:
        """
        Get total number of available sensors on the fiber.
        
        GET /sensors
        
        Returns:
            SensorsListResponse containing list of sensor indices [0, 1, 2, ..., n]
            
        Raises:
            APIError: If API call fails
        """
        self.logger.debug("Getting sensors list")
        
        try:
            response = self.get("/sensors")
            response_data = response.json()
            
            sensors_response = SensorsListResponse(**response_data)
            self.logger.debug(f"Retrieved {len(sensors_response.sensors)} sensors")
            
            return sensors_response
            
        except Exception as e:
            self.logger.error(f"Failed to get sensors list: {e}")
            if isinstance(e, APIError):
                raise
            raise APIError(f"Failed to get sensors list: {e}") from e
    
    def get_live_metadata_flat(self) -> LiveMetadataFlat:
        """
        Retrieve current fiber metadata from live stream.
        
        GET /live_metadata
        
        Returns:
            Flat dictionary of RecordingMetadata fields including:
            - prr (pulse repetition rate)
            - num_samples_per_trace
            - dtype
            - Other metadata fields
            
        Raises:
            APIError: If API call fails
        """
        self.logger.debug("Getting live metadata (flat)")
        
        try:
            response = self.get("/live_metadata")
            response_data = response.json()
            
            live_metadata = LiveMetadataFlat(**response_data)
            self.logger.debug(
                f"Live metadata: PRR={live_metadata.prr}, "
                f"channels={live_metadata.number_of_channels}"
            )
            
            return live_metadata
            
        except Exception as e:
            self.logger.error(f"Failed to get live metadata: {e}")
            if isinstance(e, APIError):
                raise
            raise APIError(f"Failed to get live metadata: {e}") from e
    
    def get_waterfall(self, task_id: str, row_count: int) -> WaterfallGetResponse:
        """
        Retrieve processed waterfall data for a specific task.
        
        GET /waterfall/{task_id}/{row_count}
        
        Args:
            task_id: Task identifier
            row_count: Number of rows requested (must be > 0)
            
        Returns:
            WaterfallGetResponse with status code and data:
            - 200: Empty response (no data available yet)
            - 201: Data retrieved successfully
            - 208: Baby analyzer has exited
            - 400: Invalid row_count
            - 404: Consumer not found
            
        Raises:
            APIError: If API call fails
            ValidationError: If task_id or row_count is invalid
        
        Flow:
            - Checks if consumer exists and is running
            - Retrieves data from buffered queue
            - Sends keepalive to baby analyzer
            - Returns processed spectrogram rows
        
        Response Format:
            [{
                "rows": [{
                    "canvasId": str,
                    "sensors": [{
                        "id": int,
                        "intensity": [float, ...]
                    }],
                    "startTimestamp": int (epoch millis),
                    "endTimestamp": int (epoch millis)
                }],
                "current_max_amp": float,
                "current_min_amp": float
            }]
        """
        if not task_id or not isinstance(task_id, str):
            raise ValidationError("task_id must be a non-empty string")
        
        if not isinstance(row_count, int) or row_count <= 0:
            raise ValidationError("row_count must be a positive integer")
        
        self.logger.debug(f"Getting waterfall data for task {task_id}, row_count={row_count}")
        
        try:
            response = self.get(f"/waterfall/{task_id}/{row_count}")
            status_code = response.status_code
            
            # Handle different response codes
            if status_code == 200:
                # Empty response - no data yet
                waterfall_response = WaterfallGetResponse(
                    status_code=200,
                    data=None,
                    message="No data available yet"
                )
            elif status_code == 201:
                # Data retrieved successfully
                response_data = response.json()
                waterfall_response = WaterfallGetResponse(
                    status_code=201,
                    data=response_data,
                    message="Data retrieved successfully"
                )
            elif status_code == 208:
                # Baby analyzer has exited
                waterfall_response = WaterfallGetResponse(
                    status_code=208,
                    data=None,
                    message="Baby analyzer has exited"
                )
            elif status_code == 400:
                # Invalid row_count
                waterfall_response = WaterfallGetResponse(
                    status_code=400,
                    data=None,
                    message="Invalid row_count"
                )
            elif status_code == 404:
                # Consumer not found
                waterfall_response = WaterfallGetResponse(
                    status_code=404,
                    data=None,
                    message="Consumer not found for task_id"
                )
            else:
                raise APIError(f"Unexpected status code: {status_code}")
            
            self.logger.debug(
                f"Waterfall response for task {task_id}: "
                f"status={status_code}, message={waterfall_response.message}"
            )
            
            return waterfall_response
            
        except Exception as e:
            self.logger.error(f"Failed to get waterfall data for task {task_id}: {e}")
            if isinstance(e, (APIError, ValidationError)):
                raise
            raise APIError(f"Failed to get waterfall data: {e}") from e
    
    def get_task_metadata(self, task_id: str) -> TaskMetadataGetResponse:
        """
        Get metadata for a specific task's recording.
        
        GET /metadata/{task_id}
        
        Args:
            task_id: Task identifier
            
        Returns:
            TaskMetadataGetResponse with status code and metadata:
            - 200: Empty (consumer not running)
            - 201: Metadata dictionary
            - 404: Invalid task_id
            
        Raises:
            APIError: If API call fails
            ValidationError: If task_id is invalid
        """
        if not task_id or not isinstance(task_id, str):
            raise ValidationError("task_id must be a non-empty string")
        
        self.logger.debug(f"Getting task metadata for task: {task_id}")
        
        try:
            response = self.get(f"/metadata/{task_id}")
            status_code = response.status_code
            
            # Handle different response codes
            if status_code == 200:
                # Empty - consumer not running
                metadata_response = TaskMetadataGetResponse(
                    status_code=200,
                    metadata=None
                )
            elif status_code == 201:
                # Metadata available
                response_data = response.json()
                metadata_response = TaskMetadataGetResponse(
                    status_code=201,
                    metadata=LiveMetadataFlat(**response_data)
                )
            elif status_code == 404:
                # Invalid task_id
                metadata_response = TaskMetadataGetResponse(
                    status_code=404,
                    metadata=None
                )
            else:
                raise APIError(f"Unexpected status code: {status_code}")
            
            self.logger.debug(f"Task metadata response for {task_id}: status={status_code}")
            
            return metadata_response
            
        except Exception as e:
            self.logger.error(f"Failed to get task metadata for {task_id}: {e}")
            if isinstance(e, (APIError, ValidationError)):
                raise
            raise APIError(f"Failed to get task metadata: {e}") from e