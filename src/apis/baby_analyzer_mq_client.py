"""
Baby Analyzer MQ Client
========================

RabbitMQ client for sending commands to Baby Analyzer instances.
Supports all Baby Analyzer command interface operations.
"""

import json
import logging
from typing import Optional, Any, Dict
import pika
from pika.exceptions import AMQPConnectionError, AMQPChannelError

from src.core.exceptions import InfrastructureError, ValidationError
from src.models.baby_analyzer_models import (
    KeepaliveCommand, KeepaliveCommandValue,
    InputChangedCommand, RecordingMetadata,
    ColormapCommand, ColorMap,
    CaxisCommand, CAxisRange,
    RegionOfInterestCommand, RegionOfInterest,
    MonitorQueuesCommand, MonitorQueuesValue
)


class BabyAnalyzerMQClient:
    """
    RabbitMQ client for Baby Analyzer command interface.
    
    Provides high-level methods for sending commands to baby analyzer instances
    via RabbitMQ message bus. Handles connection management, message serialization,
    and error handling.
    
    Attributes:
        host (str): RabbitMQ server host
        port (int): RabbitMQ server port
        username (str): RabbitMQ username
        password (str): RabbitMQ password
        exchange (str): RabbitMQ exchange name
        connection (pika.BlockingConnection): Active RabbitMQ connection
        channel (pika.channel.Channel): Active RabbitMQ channel
        logger (logging.Logger): Logger instance
    """
    
    def __init__(
        self,
        host: str,
        port: int = 5672,
        username: str = "guest",
        password: str = "guest",
        exchange: str = "baby_analyzer_commands",
        virtual_host: str = "/"
    ):
        """
        Initialize Baby Analyzer MQ client.
        
        Args:
            host: RabbitMQ server host
            port: RabbitMQ server port (default: 5672)
            username: RabbitMQ username (default: "guest")
            password: RabbitMQ password (default: "guest")
            exchange: RabbitMQ exchange name (default: "baby_analyzer_commands")
            virtual_host: RabbitMQ virtual host (default: "/")
            
        Raises:
            ValidationError: If connection parameters are invalid
        """
        if not host:
            raise ValidationError("RabbitMQ host must be provided")
        
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.exchange = exchange
        self.virtual_host = virtual_host
        
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Baby Analyzer MQ client initialized for {host}:{port}")
    
    def connect(self) -> None:
        """
        Establish connection to RabbitMQ server.
        
        Creates connection and channel, declares exchange.
        
        Raises:
            InfrastructureError: If connection fails
        """
        try:
            # Create credentials
            credentials = pika.PlainCredentials(self.username, self.password)
            
            # Create connection parameters
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.virtual_host,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            
            # Establish connection
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare exchange (topic exchange for routing commands)
            self.channel.exchange_declare(
                exchange=self.exchange,
                exchange_type='topic',
                durable=True
            )
            
            self.logger.info(f"Connected to RabbitMQ at {self.host}:{self.port}")
            
        except AMQPConnectionError as e:
            error_msg = f"Failed to connect to RabbitMQ at {self.host}:{self.port}: {e}"
            self.logger.error(error_msg)
            raise InfrastructureError(error_msg) from e
        
        except Exception as e:
            error_msg = f"Unexpected error connecting to RabbitMQ: {e}"
            self.logger.error(error_msg)
            raise InfrastructureError(error_msg) from e
    
    def disconnect(self) -> None:
        """
        Close connection to RabbitMQ server.
        
        Safely closes channel and connection.
        """
        try:
            if self.channel and self.channel.is_open:
                self.channel.close()
                self.logger.debug("RabbitMQ channel closed")
            
            if self.connection and self.connection.is_open:
                self.connection.close()
                self.logger.info("Disconnected from RabbitMQ")
                
        except Exception as e:
            self.logger.warning(f"Error during disconnect: {e}")
    
    def _publish_command(
        self,
        routing_key: str,
        command: Dict[str, Any],
        delivery_mode: int = 2
    ) -> None:
        """
        Publish command to RabbitMQ exchange.
        
        Args:
            routing_key: Routing key for message delivery
            command: Command dictionary to publish
            delivery_mode: Delivery mode (1=non-persistent, 2=persistent)
            
        Raises:
            InfrastructureError: If publishing fails
            ValidationError: If not connected
        """
        if not self.channel or not self.channel.is_open:
            raise ValidationError("Not connected to RabbitMQ. Call connect() first.")
        
        try:
            # Serialize command to JSON
            message_body = json.dumps(command)
            
            # Publish message
            self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=routing_key,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=delivery_mode,
                    content_type='application/json'
                )
            )
            
            self.logger.debug(
                f"Published command to routing_key={routing_key}: "
                f"{command.get('type', 'unknown')}"
            )
            
        except AMQPChannelError as e:
            error_msg = f"Failed to publish command: {e}"
            self.logger.error(error_msg)
            raise InfrastructureError(error_msg) from e
        
        except Exception as e:
            error_msg = f"Unexpected error publishing command: {e}"
            self.logger.error(error_msg)
            raise InfrastructureError(error_msg) from e
    
    def send_keepalive(self, source: str, routing_key: str = "keepalive") -> None:
        """
        Send keepalive command to baby analyzer.
        
        Purpose: Resets baby analyzer timeout counter to keep it alive.
        
        Args:
            source: Source identifier sending the keepalive
            routing_key: Routing key for message delivery (default: "keepalive")
            
        Raises:
            ValidationError: If source is invalid or not connected
            InfrastructureError: If command sending fails
        """
        if not source:
            raise ValidationError("Source identifier must be provided")
        
        self.logger.debug(f"Sending keepalive command from source: {source}")
        
        # Create keepalive command
        command = KeepaliveCommand(
            value=KeepaliveCommandValue(source=source)
        )
        
        # Publish command
        self._publish_command(routing_key, command.model_dump())
        
        self.logger.info(f"Keepalive sent from {source}")
    
    def send_input_changed(
        self,
        metadata: RecordingMetadata,
        routing_key: str = "input_changed"
    ) -> None:
        """
        Send input changed command to baby analyzer.
        
        Purpose: Notifies baby analyzer of input stream metadata changes.
        
        Args:
            metadata: Updated recording metadata
            routing_key: Routing key for message delivery (default: "input_changed")
            
        Raises:
            ValidationError: If metadata is invalid or not connected
            InfrastructureError: If command sending fails
        """
        if not isinstance(metadata, RecordingMetadata):
            raise ValidationError("metadata must be a RecordingMetadata instance")
        
        self.logger.debug("Sending input changed command")
        
        # Create input changed command
        command = InputChangedCommand(metadata=metadata)
        
        # Publish command
        self._publish_command(routing_key, command.model_dump())
        
        self.logger.info("Input changed command sent")
    
    def send_colormap_change(
        self,
        colormap: ColorMap,
        routing_key: str = "colormap"
    ) -> None:
        """
        Send colormap change command to baby analyzer.
        
        Purpose: Changes colormap for PNG output backend.
        
        Args:
            colormap: Colormap name (parula, grayscale, jet)
            routing_key: Routing key for message delivery (default: "colormap")
            
        Raises:
            ValidationError: If colormap is invalid or not connected
            InfrastructureError: If command sending fails
        """
        if not isinstance(colormap, ColorMap):
            raise ValidationError("colormap must be a ColorMap enum value")
        
        self.logger.debug(f"Sending colormap change command: {colormap}")
        
        # Create colormap command
        command = ColormapCommand(value=colormap)
        
        # Publish command
        self._publish_command(routing_key, command.model_dump())
        
        self.logger.info(f"Colormap changed to {colormap}")
    
    def send_caxis_adjust(
        self,
        min_value: float,
        max_value: float,
        routing_key: str = "caxis"
    ) -> None:
        """
        Send color axis adjustment command to baby analyzer.
        
        Purpose: Adjusts color axis range for visualization.
        
        Args:
            min_value: Minimum color axis value
            max_value: Maximum color axis value
            routing_key: Routing key for message delivery (default: "caxis")
            
        Raises:
            ValidationError: If values are invalid or not connected
            InfrastructureError: If command sending fails
        """
        if max_value <= min_value:
            raise ValidationError("max_value must be > min_value")
        
        self.logger.debug(f"Sending caxis adjustment command: [{min_value}, {max_value}]")
        
        # Create caxis command
        command = CaxisCommand(
            value=CAxisRange(min=min_value, max=max_value)
        )
        
        # Publish command
        self._publish_command(routing_key, command.model_dump())
        
        self.logger.info(f"Caxis adjusted to [{min_value}, {max_value}]")
    
    def send_roi_change(
        self,
        start: int,
        end: int,
        routing_key: str = "roi"
    ) -> None:
        """
        Send region of interest change command to baby analyzer.
        
        Purpose: Dynamically changes sensor range (ROI) during processing.
        Triggers pipeline reinitialization with new ROI.
        
        Args:
            start: Start sensor index
            end: End sensor index
            routing_key: Routing key for message delivery (default: "roi")
            
        Raises:
            ValidationError: If ROI is invalid or not connected
            InfrastructureError: If command sending fails
        """
        # Validate non-negative values first (more specific error)
        if start < 0 or end < 0:
            raise ValidationError("Sensor indices must be non-negative")
        
        # Then validate range order
        if end <= start:
            raise ValidationError("end sensor must be > start sensor")
        
        self.logger.debug(f"Sending ROI change command: sensors [{start}, {end}]")
        
        # Create ROI command
        command = RegionOfInterestCommand(
            value=RegionOfInterest(start=start, end=end)
        )
        
        # Publish command
        self._publish_command(routing_key, command.model_dump())
        
        self.logger.info(f"ROI changed to sensors [{start}, {end}]")
    
    def send_monitor_queues(
        self,
        queues_to_monitor: list[str],
        routing_key: str = "monitor_queues"
    ) -> None:
        """
        Send monitor queues command to baby analyzer.
        
        Purpose: Adds queues to monitor for throttling control.
        
        Args:
            queues_to_monitor: List of queue names to monitor
            routing_key: Routing key for message delivery (default: "monitor_queues")
            
        Raises:
            ValidationError: If queues list is invalid or not connected
            InfrastructureError: If command sending fails
        """
        if not queues_to_monitor or not isinstance(queues_to_monitor, list):
            raise ValidationError("queues_to_monitor must be a non-empty list")
        
        self.logger.debug(f"Sending monitor queues command: {len(queues_to_monitor)} queues")
        
        # Create monitor queues command
        command = MonitorQueuesCommand(
            value=MonitorQueuesValue(queues_to_monitor=queues_to_monitor)
        )
        
        # Publish command
        self._publish_command(routing_key, command.model_dump())
        
        self.logger.info(f"Monitor queues command sent for {len(queues_to_monitor)} queues")
    
    def __enter__(self):
        """Context manager entry - connects to RabbitMQ."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - disconnects from RabbitMQ."""
        self.disconnect()
        return False
    
    def is_connected(self) -> bool:
        """
        Check if currently connected to RabbitMQ.
        
        Returns:
            True if connected and channel is open
        """
        return (
            self.connection is not None
            and self.connection.is_open
            and self.channel is not None
            and self.channel.is_open
        )
    
    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get current connection information.
        
        Returns:
            Dictionary with connection details
        """
        return {
            "host": self.host,
            "port": self.port,
            "exchange": self.exchange,
            "virtual_host": self.virtual_host,
            "connected": self.is_connected()
        }

