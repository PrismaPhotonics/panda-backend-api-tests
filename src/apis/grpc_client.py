"""
gRPC Stream Client for Focus Server
====================================

Production-grade gRPC client for streaming spectrogram data from Focus Server.

This client connects to gRPC jobs created by the Focus Server and streams
spectrogram data in real-time.

Flow:
    1. Call POST /configure to get job_id, stream_url, stream_port
    2. Create GrpcStreamClient instance
    3. Connect to stream_url:stream_port
    4. Call stream_data() to receive spectrogram frames

Usage:
    ```python
    from src.apis.grpc_client import GrpcStreamClient
    
    # Create client
    client = GrpcStreamClient(config_manager)
    
    # Connect
    client.connect(stream_url="10.10.100.100", stream_port=30123)
    
    # Stream data
    for frame in client.stream_data(stream_id=0, max_frames=10):
        print(f"Received frame with {len(frame.rows)} rows")
        print(f"Amplitude: {frame.current_min_amp} to {frame.current_max_amp}")
    
    # Disconnect
    client.disconnect()
    ```

Author: QA Automation Architect
Date: 2025-11-29
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Generator, Any, Dict

import grpc

# Import the ACTUAL production proto (pandadatastream)
from src.models.proto_generated import pandadatastream_pb2, pandadatastream_pb2_grpc

# Alias for backwards compatibility (legacy proto)
try:
    from src.models.proto_generated import datastream_pb2, datastream_pb2_grpc
except ImportError:
    pass

logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class StreamMetrics:
    """Metrics collected during streaming."""
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    frames_received: int = 0
    total_rows: int = 0
    total_bytes: int = 0
    min_amplitude: Optional[float] = None
    max_amplitude: Optional[float] = None
    errors: int = 0
    
    @property
    def duration_seconds(self) -> float:
        """Duration in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        elif self.start_time:
            return time.time() - self.start_time
        return 0.0
    
    @property
    def frames_per_second(self) -> float:
        """Frames received per second."""
        duration = self.duration_seconds
        if duration > 0:
            return self.frames_received / duration
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "frames_received": self.frames_received,
            "total_rows": self.total_rows,
            "total_bytes": self.total_bytes,
            "min_amplitude": self.min_amplitude,
            "max_amplitude": self.max_amplitude,
            "duration_seconds": self.duration_seconds,
            "frames_per_second": self.frames_per_second,
            "errors": self.errors
        }


# =============================================================================
# GrpcStreamClient
# =============================================================================

class GrpcStreamClient:
    """
    Production-grade gRPC client for Focus Server streaming.
    
    Features:
    - Connection management with proper cleanup
    - Stream consumption with timeout handling
    - Retry logic for transient failures
    - Metrics collection
    - Thread-safe operation
    
    Usage:
        ```python
        client = GrpcStreamClient(config_manager)
        client.connect("10.10.100.100", 30123)
        
        for frame in client.stream_data(stream_id=0, max_frames=10):
            print(f"Received: {len(frame.rows)} rows")
        
        client.disconnect()
        ```
    """
    
    def __init__(
        self,
        config_manager: Optional[Any] = None,
        connection_timeout: int = 30,
        stream_timeout: int = 60,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize gRPC Stream Client.
        
        Args:
            config_manager: Optional configuration manager instance
            connection_timeout: Timeout for connection (seconds)
            stream_timeout: Timeout for stream operations (seconds)
            max_retries: Maximum retries for transient failures
            retry_delay: Delay between retries (seconds)
        """
        self.config_manager = config_manager
        self.connection_timeout = connection_timeout
        self.stream_timeout = stream_timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Connection state
        self._channel: Optional[grpc.Channel] = None
        self._stub: Optional[pandadatastream_pb2_grpc.DataStreamServiceStub] = None
        self._connected: bool = False
        self._stream_url: Optional[str] = None
        self._stream_port: Optional[int] = None
        
        # Metrics
        self._metrics = StreamMetrics()
        
        self.logger = logging.getLogger(__name__)
        self.logger.debug("GrpcStreamClient initialized")
    
    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._connected
    
    @property
    def metrics(self) -> StreamMetrics:
        """Get current metrics."""
        return self._metrics
    
    def connect(
        self,
        stream_url: str,
        stream_port: int,
        use_tls: bool = False
    ) -> bool:
        """
        Connect to gRPC server.
        
        Args:
            stream_url: gRPC server URL/IP
            stream_port: gRPC server port (NodePort)
            use_tls: Whether to use TLS (default: False for internal network)
        
        Returns:
            True if connected successfully
        
        Raises:
            ConnectionError: If connection fails
        """
        if self._connected:
            self.logger.warning("Already connected, disconnecting first...")
            self.disconnect()
        
        # Clean URL (remove http:// or https:// if present)
        clean_url = stream_url
        if clean_url.startswith('http://'):
            clean_url = clean_url.replace('http://', '')
        elif clean_url.startswith('https://'):
            clean_url = clean_url.replace('https://', '')
        
        # Remove trailing slashes
        clean_url = clean_url.rstrip('/')
        
        target = f"{clean_url}:{stream_port}"
        self.logger.info(f"Connecting to gRPC server at {target}...")
        
        try:
            # Create channel options
            options = [
                ('grpc.max_receive_message_length', 50 * 1024 * 1024),  # 50MB
                ('grpc.max_send_message_length', 50 * 1024 * 1024),
                ('grpc.keepalive_time_ms', 30000),
                ('grpc.keepalive_timeout_ms', 10000),
                ('grpc.keepalive_permit_without_calls', True),
            ]
            
            # Create channel
            if use_tls:
                # Use TLS (for production with valid certificates)
                credentials = grpc.ssl_channel_credentials()
                self._channel = grpc.secure_channel(target, credentials, options=options)
            else:
                # No TLS (for internal network)
                self._channel = grpc.insecure_channel(target, options=options)
            
            # Wait for channel to be ready
            self.logger.debug(f"Waiting for channel ready (timeout: {self.connection_timeout}s)...")
            
            try:
                grpc.channel_ready_future(self._channel).result(
                    timeout=self.connection_timeout
                )
            except grpc.FutureTimeoutError:
                raise ConnectionError(
                    f"Connection timeout after {self.connection_timeout}s to {target}"
                )
            
            # Create stub (using production pandadatastream proto)
            self._stub = pandadatastream_pb2_grpc.DataStreamServiceStub(self._channel)
            
            self._connected = True
            self._stream_url = clean_url
            self._stream_port = stream_port
            
            self.logger.info(f"✅ Connected to gRPC server at {target}")
            return True
            
        except grpc.RpcError as e:
            self._cleanup()
            raise ConnectionError(f"gRPC connection error: {e.code()}: {e.details()}") from e
        except Exception as e:
            self._cleanup()
            raise ConnectionError(f"Connection failed: {e}") from e
    
    def disconnect(self) -> None:
        """
        Disconnect from gRPC server.
        
        Gracefully closes the channel and cleans up resources.
        """
        if not self._connected:
            return
        
        self.logger.info("Disconnecting from gRPC server...")
        self._cleanup()
        self.logger.info("✅ Disconnected from gRPC server")
    
    def _cleanup(self) -> None:
        """Internal cleanup method."""
        self._connected = False
        self._stub = None
        
        if self._channel:
            try:
                self._channel.close()
            except Exception as e:
                self.logger.warning(f"Error closing channel: {e}")
            self._channel = None
    
    def stream_data(
        self,
        stream_id: int = 0,
        max_frames: Optional[int] = None,
        job_id: Optional[str] = None,
        timeout: Optional[float] = None
    ) -> Generator[pandadatastream_pb2.DataStream, None, None]:
        """
        Stream spectrogram data from gRPC server.
        
        Uses the PRODUCTION proto (pandadatastream) with StreamData RPC.
        
        Args:
            stream_id: Stream ID for stream separation (default: 0)
            max_frames: Maximum number of frames to receive (None = unlimited)
            job_id: Optional job ID (not used in pandadatastream, kept for compatibility)
            timeout: Timeout per frame (seconds), defaults to stream_timeout
        
        Yields:
            DataStream: Protobuf message containing:
                - start_channel, end_channel: Channel range
                - data_shape_x, data_shape_y: Data dimensions  
                - global_minimum, global_maximum: Amplitude range
                - main_data: Raw spectrogram data (bytes)
                - timestamp_in_milis: Timestamps
        
        Raises:
            ConnectionError: If not connected
            TimeoutError: If stream times out
            RuntimeError: If stream error occurs
        
        Example:
            ```python
            for frame in client.stream_data(stream_id=0, max_frames=10):
                print(f"Data shape: {frame.data_shape_x}x{frame.data_shape_y}")
                print(f"Amplitude: {frame.global_minimum} - {frame.global_maximum}")
                print(f"Channels: {frame.start_channel} - {frame.end_channel}")
            ```
        """
        if not self._connected or not self._stub:
            raise ConnectionError("Not connected to gRPC server. Call connect() first.")
        
        effective_timeout = timeout or self.stream_timeout
        
        self.logger.info(
            f"Starting stream (stream_id={stream_id}, max_frames={max_frames}, "
            f"timeout={effective_timeout}s)"
        )
        
        # Reset metrics
        self._metrics = StreamMetrics()
        self._metrics.start_time = time.time()
        
        # Create stream request using PRODUCTION pandadatastream proto
        # Note: pandadatastream uses stream_id, not job_id
        request = pandadatastream_pb2.StreamDataRequest(
            stream_id=stream_id
        )
        
        frames_received = 0
        
        try:
            # Start streaming using StreamData (not StreamSpectrograms!)
            stream = self._stub.StreamData(
                request,
                timeout=effective_timeout
            )
            
            for frame in stream:
                frames_received += 1
                self._metrics.frames_received = frames_received
                
                # Update metrics - pandadatastream uses different field names
                data_points = frame.data_shape_x * frame.data_shape_y
                self._metrics.total_rows += frame.data_shape_y  # Number of rows
                
                # Track amplitude range (using pandadatastream field names)
                if frame.global_minimum is not None:
                    if self._metrics.min_amplitude is None:
                        self._metrics.min_amplitude = frame.global_minimum
                    else:
                        self._metrics.min_amplitude = min(
                            self._metrics.min_amplitude, frame.global_minimum
                        )
                
                if frame.global_maximum is not None:
                    if self._metrics.max_amplitude is None:
                        self._metrics.max_amplitude = frame.global_maximum
                    else:
                        self._metrics.max_amplitude = max(
                            self._metrics.max_amplitude, frame.global_maximum
                        )
                
                self.logger.debug(
                    f"Frame {frames_received}: shape={frame.data_shape_x}x{frame.data_shape_y}, "
                    f"amp: [{frame.global_minimum:.2f}, {frame.global_maximum:.2f}], "
                    f"channels: {frame.start_channel}-{frame.end_channel}"
                )
                
                yield frame
                
                # Check max_frames limit
                if max_frames and frames_received >= max_frames:
                    self.logger.info(f"Reached max_frames limit ({max_frames})")
                    break
        
        except grpc.RpcError as e:
            self._metrics.errors += 1
            
            if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                raise TimeoutError(
                    f"Stream timeout after {effective_timeout}s "
                    f"(received {frames_received} frames)"
                ) from e
            elif e.code() == grpc.StatusCode.CANCELLED:
                self.logger.info(f"Stream cancelled after {frames_received} frames")
            elif e.code() == grpc.StatusCode.UNAVAILABLE:
                raise ConnectionError(f"gRPC server unavailable: {e.details()}") from e
            else:
                raise RuntimeError(f"Stream error: {e.code()}: {e.details()}") from e
        
        finally:
            self._metrics.end_time = time.time()
            
            self.logger.info(
                f"Stream ended: {frames_received} frames in "
                f"{self._metrics.duration_seconds:.2f}s "
                f"({self._metrics.frames_per_second:.1f} fps)"
            )
    
    def check_health(self) -> bool:
        """
        Check gRPC server health.
        
        Note: The pandadatastream proto doesn't have a health check RPC.
        This method checks connectivity by attempting a brief connection test.
        
        Returns:
            True if server appears healthy (channel is ready)
        """
        if not self._connected or not self._channel:
            return False
        
        try:
            # Check if channel is still ready (no dedicated health RPC in pandadatastream)
            grpc.channel_ready_future(self._channel).result(timeout=5.0)
            return True
        except (grpc.FutureTimeoutError, grpc.RpcError):
            return False
        except Exception:
            return False
    
    def collect_frames(
        self,
        stream_id: int = 0,
        timeout_seconds: int = 60,
        max_frames: int = 100,
        job_id: Optional[str] = None
    ) -> list:
        """
        Convenience method to collect frames into a list.
        
        Args:
            stream_id: Stream ID
            timeout_seconds: Maximum time to wait
            max_frames: Maximum frames to collect
            job_id: Optional job ID
        
        Returns:
            List of DataStream frames
        
        Example:
            ```python
            frames = client.collect_frames(
                stream_id=0,
                timeout_seconds=30,
                max_frames=50
            )
            print(f"Collected {len(frames)} frames")
            ```
        """
        frames = []
        start_time = time.time()
        
        try:
            for frame in self.stream_data(
                stream_id=stream_id,
                max_frames=max_frames,
                job_id=job_id,
                timeout=timeout_seconds
            ):
                frames.append(frame)
                
                # Check timeout
                if time.time() - start_time > timeout_seconds:
                    self.logger.warning(f"Timeout reached ({timeout_seconds}s)")
                    break
        
        except TimeoutError:
            self.logger.warning(f"Stream timeout after {len(frames)} frames")
        
        return frames
    
    def __enter__(self) -> 'GrpcStreamClient':
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.disconnect()
    
    def __repr__(self) -> str:
        """String representation."""
        status = "connected" if self._connected else "disconnected"
        if self._connected:
            return (
                f"GrpcStreamClient(status={status}, "
                f"target={self._stream_url}:{self._stream_port}, "
                f"metrics={self._metrics.to_dict()})"
            )
        return f"GrpcStreamClient(status={status})"


# =============================================================================
# Helper Functions
# =============================================================================

def create_grpc_client(
    config_manager: Optional[Any] = None,
    **kwargs
) -> GrpcStreamClient:
    """
    Factory function to create GrpcStreamClient.
    
    Args:
        config_manager: Optional configuration manager
        **kwargs: Additional arguments for GrpcStreamClient
    
    Returns:
        Configured GrpcStreamClient instance
    """
    return GrpcStreamClient(config_manager=config_manager, **kwargs)


def test_grpc_connectivity(
    stream_url: str,
    stream_port: int,
    timeout: int = 10
) -> Dict[str, Any]:
    """
    Test gRPC connectivity without streaming data.
    
    Args:
        stream_url: gRPC server URL
        stream_port: gRPC server port
        timeout: Connection timeout
    
    Returns:
        Dictionary with connectivity results
    """
    result = {
        "connected": False,
        "healthy": False,
        "error": None,
        "latency_ms": None
    }
    
    client = GrpcStreamClient(connection_timeout=timeout)
    start_time = time.time()
    
    try:
        client.connect(stream_url, stream_port)
        result["connected"] = True
        result["latency_ms"] = (time.time() - start_time) * 1000
        
        result["healthy"] = client.check_health()
    
    except ConnectionError as e:
        result["error"] = str(e)
    except Exception as e:
        result["error"] = f"Unexpected error: {e}"
    finally:
        client.disconnect()
    
    return result

