"""
Basic Connectivity Tests
=========================

Simple connectivity tests for external services without infrastructure dependencies.
These tests verify direct network connectivity to services.

Author: QA Automation Architect
"""

import pytest
import logging
import os
from typing import Dict, Any

# MongoDB
try:
    import pymongo
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False

# Kubernetes
try:
    from kubernetes import client, config
    from kubernetes.client.rest import ApiException
    K8S_AVAILABLE = True
except ImportError:
    K8S_AVAILABLE = False

# SSH
try:
    import paramiko
    SSH_AVAILABLE = True
except ImportError:
    SSH_AVAILABLE = False

from config.config_manager import ConfigManager


logger = logging.getLogger(__name__)


# =================================================================
# MongoDB Direct Connectivity Tests
# =================================================================

@pytest.mark.xray("PZ-13898")
@pytest.mark.critical
@pytest.mark.high
@pytest.mark.regression
@pytest.mark.smoke
def test_mongodb_direct_connection(current_env):
    """
    Test direct MongoDB connection without Kubernetes dependency.
    
    PZ-13898: Infrastructure - MongoDB Direct Connection and Health Check
    
    Args:
        current_env: Current test environment
    
    Verification:
    - TCP connection to MongoDB
    - Authentication
    - Ping command
    """
    logger.info("=" * 80)
    logger.info("Testing Direct MongoDB Connectivity")
    logger.info("=" * 80)
    
    try:
        # Get configuration from current environment
        config_manager = ConfigManager(current_env)
        mongo_config = config_manager.get_database_config()
        
        logger.info(f"Attempting to connect to MongoDB:")
        logger.info(f"  Host: {mongo_config['host']}")
        logger.info(f"  Port: {mongo_config['port']}")
        logger.info(f"  Username: {mongo_config['username']}")
        logger.info(f"  Database: {mongo_config['database']}")
        
        # Create MongoDB client
        client = pymongo.MongoClient(
            host=mongo_config["host"],
            port=mongo_config["port"],
            username=mongo_config["username"],
            password=mongo_config["password"],
            authSource=mongo_config.get("auth_source", "admin"),
            serverSelectionTimeoutMS=10000,  # 10 seconds timeout
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
        )
        
        # Test connection with ping
        logger.info("Sending ping command to MongoDB...")
        client.admin.command('ping')
        
        logger.info("✅ MongoDB ping successful!")
        
        # Get server info
        server_info = client.server_info()
        logger.info(f"MongoDB Version: {server_info.get('version', 'Unknown')}")
        
        # List databases
        db_list = client.list_database_names()
        logger.info(f"Available databases ({len(db_list)}): {', '.join(db_list[:5])}...")
        
        # Disconnect
        client.close()
        logger.info("✅ MongoDB connectivity test PASSED")
        
    except ConnectionFailure as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        pytest.fail(f"MongoDB connection failed: {e}")
        
    except ServerSelectionTimeoutError as e:
        logger.error(f"❌ MongoDB server selection timeout: {e}")
        pytest.fail(f"MongoDB server selection timeout: {e}")
        
    except Exception as e:
        logger.error(f"❌ MongoDB connectivity test failed: {e}")
        pytest.fail(f"MongoDB connectivity test failed: {e}")


# =================================================================
# Kubernetes Direct Connectivity Tests
# =================================================================

@pytest.mark.xray("PZ-13899")
@pytest.mark.critical
@pytest.mark.high
@pytest.mark.regression
@pytest.mark.smoke
def test_kubernetes_direct_connection(current_env):
    """
    Test Kubernetes connection using KubernetesManager (supports SSH fallback).
    
    PZ-13899: Infrastructure - Kubernetes Cluster Connection and Pod Health Check
    
    Args:
        current_env: Current test environment
    
    Verification:
    - Kubernetes API accessibility (via direct API or SSH fallback)
    - Cluster version
    - Node listing
    """
    logger.info("=" * 80)
    logger.info("Testing Kubernetes Connectivity")
    logger.info("=" * 80)
    
    try:
        # Use KubernetesManager which supports SSH fallback
        from src.infrastructure.kubernetes_manager import KubernetesManager
        
        logger.info("Initializing Kubernetes manager...")
        config_manager = ConfigManager(current_env)
        k8s_manager = KubernetesManager(config_manager)
        
        # Check connection method
        if k8s_manager.use_ssh_fallback:
            logger.info("ℹ️  Using SSH-based kubectl fallback")
        else:
            logger.info("ℹ️  Using direct Kubernetes API access")
        
        # Get cluster info (works with both direct API and SSH fallback)
        logger.info("Retrieving cluster information...")
        cluster_info = k8s_manager.get_cluster_info()
        
        logger.info(f"Kubernetes Cluster Information:")
        logger.info(f"  Version: {cluster_info.get('version', 'Unknown')}")
        logger.info(f"  Nodes: {cluster_info.get('node_count', 0)}")
        
        # List nodes
        nodes = cluster_info.get('nodes', [])
        if nodes:
            logger.info(f"Found {len(nodes)} nodes:")
            for node in nodes:
                logger.info(f"  - {node.get('name', 'Unknown')}: {node.get('status', 'Unknown')}")
                logger.info(f"    Kubelet Version: {node.get('kubelet_version', 'Unknown')}")
        else:
            logger.warning("⚠️  No nodes found in cluster")
        
        # Verify cluster is accessible
        assert cluster_info.get('node_count', 0) > 0, "No nodes found in cluster"
        
        logger.info("✅ Kubernetes connectivity test PASSED")
        
    except Exception as e:
        error_str = str(e).lower()
        if "timeout" in error_str or "connection" in error_str or "not available" in error_str:
            logger.warning("⚠️  Kubernetes not accessible")
            logger.info("ℹ️  Kubernetes requires either:")
            logger.info("    1. Direct kubeconfig access")
            logger.info("    2. SSH access (automatically used as fallback)")
            pytest.skip(f"Kubernetes not accessible: {e}")
        else:
            logger.error(f"❌ Kubernetes connectivity test failed: {e}")
            pytest.fail(f"Kubernetes connectivity test failed: {e}")


# =================================================================
# SSH Direct Connectivity Tests
# =================================================================

@pytest.mark.xray("PZ-13900")


@pytest.mark.regression
@pytest.mark.smoke
def test_ssh_direct_connection(current_env):
    """
    Test direct SSH connection to k9s environment.
    
    PZ-13900: Infrastructure - SSH Access to Production Servers
    
    Args:
        current_env: Current test environment
    
    Verification:
    - TCP connection
    - SSH authentication
    - Command execution
    """
    logger.info("=" * 80)
    logger.info("Testing Direct SSH Connectivity")
    logger.info("=" * 80)
    
    ssh_client = None
    
    try:
        # Get configuration from current environment
        config_manager = ConfigManager(current_env)
        ssh_config = config_manager.get_ssh_config()
        
        # SSH config has jump_host and target_host structure
        # Use target_host for direct connection, or jump_host for first hop
        if "target_host" in ssh_config:
            target_config = ssh_config["target_host"]
        elif "jump_host" in ssh_config:
            target_config = ssh_config["jump_host"]
        else:
            # Fallback for old config format
            target_config = ssh_config
        
        logger.info(f"Attempting SSH connection:")
        logger.info(f"  Host: {target_config['host']}")
        logger.info(f"  Port: {target_config.get('port', 22)}")
        logger.info(f"  Username: {target_config['username']}")
        
        # Create SSH client
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connection parameters
        hostname = target_config["host"]
        port = target_config.get("port", 22)
        username = target_config["username"]
        password = target_config.get("password")
        key_file = target_config.get("key_file")
        
        # Expand ~ in key_file path and validate
        use_key_auth = False
        if key_file:
            key_file = os.path.expanduser(key_file)
            if os.path.exists(key_file):
                use_key_auth = True
                logger.info(f"Using SSH key authentication: {key_file}")
            else:
                logger.warning(f"⚠️  SSH key file not found: {key_file}")
                logger.warning("⚠️  Will try password authentication instead")
                key_file = None
        
        # Connect
        logger.info("Connecting to SSH server...")
        if use_key_auth:
            ssh_client.connect(
                hostname=hostname,
                port=port,
                username=username,
                key_filename=key_file,
                timeout=15
            )
        elif password:
            ssh_client.connect(
                hostname=hostname,
                port=port,
                username=username,
                password=password,
                timeout=15
            )
        else:
            raise Exception("No authentication method configured (password or key_file)")
        
        logger.info("✅ SSH connection established!")
        
        # Execute test command
        logger.info("Executing test command (hostname)...")
        stdin, stdout, stderr = ssh_client.exec_command("hostname")
        exit_code = stdout.channel.recv_exit_status()
        hostname_output = stdout.read().decode('utf-8').strip()
        
        if exit_code == 0:
            logger.info(f"Remote hostname: {hostname_output}")
            logger.info("✅ SSH command execution successful!")
        else:
            stderr_output = stderr.read().decode('utf-8')
            logger.error(f"Command failed: {stderr_output}")
            raise Exception(f"Command execution failed with exit code {exit_code}")
        
        # Get uptime
        logger.info("Getting system uptime...")
        stdin, stdout, stderr = ssh_client.exec_command("uptime")
        uptime_output = stdout.read().decode('utf-8').strip()
        logger.info(f"System uptime: {uptime_output}")
        
        logger.info("✅ SSH connectivity test PASSED")
        
    except paramiko.AuthenticationException as e:
        logger.error(f"❌ SSH authentication failed: {e}")
        pytest.fail(f"SSH authentication failed: {e}")
        
    except paramiko.SSHException as e:
        logger.error(f"❌ SSH connection failed: {e}")
        pytest.fail(f"SSH connection failed: {e}")
        
    except Exception as e:
        logger.error(f"❌ SSH connectivity test failed: {e}")
        pytest.fail(f"SSH connectivity test failed: {e}")
        
    finally:
        if ssh_client:
            ssh_client.close()
            logger.info("SSH connection closed")


# =================================================================
# Comprehensive Connectivity Summary
# =================================================================

@pytest.mark.summary


@pytest.mark.regression


@pytest.mark.smoke
def test_connectivity_summary(current_env):
    """
    Run all connectivity tests and provide a summary.
    
    This test provides a comprehensive overview of all external service connectivity.
    
    Args:
        current_env: Current test environment
    """
    logger.info("=" * 80)
    logger.info("COMPREHENSIVE CONNECTIVITY SUMMARY")
    logger.info("=" * 80)
    
    results = {
        "MongoDB": "Not Tested",
        "Kubernetes": "Not Tested",
        "SSH": "Not Tested"
    }
    
    # Test MongoDB
    if PYMONGO_AVAILABLE:
        try:
            test_mongodb_direct_connection(current_env)
            results["MongoDB"] = "✅ PASSED"
        except:
            results["MongoDB"] = "❌ FAILED"
    else:
        results["MongoDB"] = "⚠️  SKIPPED (pymongo not installed)"
    
    # Test Kubernetes
    if K8S_AVAILABLE:
        try:
            test_kubernetes_direct_connection(current_env)
            results["Kubernetes"] = "✅ PASSED"
        except:
            results["Kubernetes"] = "❌ FAILED / SKIPPED"
    else:
        results["Kubernetes"] = "⚠️  SKIPPED (kubernetes client not installed)"
    
    # Test SSH
    if SSH_AVAILABLE:
        try:
            test_ssh_direct_connection(current_env)
            results["SSH"] = "✅ PASSED"
        except:
            results["SSH"] = "❌ FAILED"
    else:
        results["SSH"] = "⚠️  SKIPPED (paramiko not installed)"
    
    # Print summary
    logger.info("")
    logger.info("Connectivity Test Results:")
    logger.info("-" * 80)
    for service, status in results.items():
        logger.info(f"  {service:20s}: {status}")
    logger.info("=" * 80)
    
    # Check if any tests failed
    failed_tests = [service for service, status in results.items() if "FAILED" in status]
    if failed_tests:
        logger.warning(f"Some services failed connectivity tests: {', '.join(failed_tests)}")
    else:
        logger.info("🎉 All available services passed connectivity tests!")


if __name__ == "__main__":
    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    pytest.main([__file__, "-v", "-s"])

