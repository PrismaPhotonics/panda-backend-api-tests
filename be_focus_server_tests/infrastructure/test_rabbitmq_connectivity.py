"""
Infrastructure Tests - RabbitMQ Connectivity
=============================================

Tests for RabbitMQ connection and health validation.

Based on Xray Test: PZ-13602

Tests covered:
    - PZ-13602: RabbitMQ Connection

Author: QA Automation Architect  
Date: 2025-10-27
"""

import pytest
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Check if pika is available
try:
    import pika
    PIKA_AVAILABLE = True
except ImportError:
    PIKA_AVAILABLE = False
    logger.warning("pika not installed - RabbitMQ tests will be skipped")


# ===================================================================
# Test Class: RabbitMQ Connectivity
# ===================================================================

@pytest.mark.skipif(not PIKA_AVAILABLE, reason="pika not installed")


@pytest.mark.regression
class TestRabbitMQConnectivity:
    """
    Test suite for RabbitMQ connectivity.
    
    Tests covered:
        - PZ-13602: RabbitMQ Connection
    
    Priority: MEDIUM
    """
    
    @pytest.mark.xray("PZ-13602")
    @pytest.mark.regression
    @pytest.mark.smoke
    def test_rabbitmq_connection(self, config_manager):
        """
        Test PZ-13602: RabbitMQ Connection.
        
        Steps:
            1. Get RabbitMQ configuration
            2. Create connection
            3. Create channel
            4. Verify connection success
            5. Close connection
        
        Expected:
            - Connection established
            - Channel created
            - No errors
        
        Jira: PZ-13602
        Priority: MEDIUM
        """
        logger.info("=" * 80)
        logger.info("TEST: RabbitMQ Connection (PZ-13602)")
        logger.info("=" * 80)
        
        # Get RabbitMQ configuration
        rabbitmq_config = config_manager.get("rabbitmq", {})
        
        host = rabbitmq_config.get("host", "localhost")
        port = rabbitmq_config.get("port", 5672)
        username = rabbitmq_config.get("username", "guest")
        password = rabbitmq_config.get("password", "guest")
        
        logger.info(f"Connecting to RabbitMQ:")
        logger.info(f"  Host: {host}")
        logger.info(f"  Port: {port}")
        logger.info(f"  Username: {username}")
        
        try:
            # Create credentials
            credentials = pika.PlainCredentials(username, password)
            
            # Create connection parameters
            parameters = pika.ConnectionParameters(
                host=host,
                port=port,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            
            # Connect
            logger.info("Establishing connection...")
            connection = pika.BlockingConnection(parameters)
            
            logger.info("✅ RabbitMQ connection established")
            
            # Create channel
            logger.info("Creating channel...")
            channel = connection.channel()
            
            logger.info("✅ RabbitMQ channel created")
            
            # Verify connection is open
            assert connection.is_open, "Connection should be open"
            assert channel.is_open, "Channel should be open"
            
            logger.info("✅ Connection and channel verified")
            
            # Close
            logger.info("Closing connection...")
            channel.close()
            connection.close()
            
            logger.info("✅ Connection closed gracefully")
            
            logger.info("=" * 80)
            logger.info("✅ TEST PASSED: RabbitMQ Connection Success")
            logger.info("=" * 80)
            
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"❌ RabbitMQ connection failed: {e}")
            pytest.fail(f"RabbitMQ connection failed: {e}")
            
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            pytest.fail(f"RabbitMQ test failed: {e}")


# ===================================================================
# Module Summary Test
# ===================================================================

@pytest.mark.summary


@pytest.mark.regression
@pytest.mark.skip(reason="Documentation only - no executable assertions")
@pytest.mark.smoke
def test_rabbitmq_connectivity_summary():
    """
    Summary test for RabbitMQ connectivity tests.
    
    Xray Tests Covered:
        - PZ-13602: RabbitMQ Connection
    
    NOTE: This test is skipped - it's documentation only.
    Real tests are in the class above.
    """
    logger.info("=" * 80)
    logger.info("RabbitMQ Connectivity Tests Suite Summary")
    logger.info("=" * 80)
    logger.info("Tests in this module:")
    logger.info("  1. PZ-13602: RabbitMQ connection and channel creation")
    logger.info("=" * 80)

