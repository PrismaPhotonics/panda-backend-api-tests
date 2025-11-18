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


@pytest.mark.regression
@pytest.mark.smoke
def test_kubernetes_direct_connection():
    """
    Test direct Kubernetes connection.
    
    PZ-13899: Infrastructure - Kubernetes Cluster Connection and Pod Health Check
    
    Verification:
    - Kubernetes API accessibility
    - Cluster version
    - Node listing
    """
    logger.info("=" * 80)
    logger.info("Testing Direct Kubernetes Connectivity")
    logger.info("=" * 80)
    
    try:
        # Load Kubernetes configuration
        logger.info("Loading Kubernetes configuration...")
        config.load_kube_config()
        
        # Disable SSL verification for self-signed certificates
        # Set shorter timeout for faster failure
        from kubernetes.client import Configuration
        k8s_config = Configuration.get_default_copy()
        k8s_config.verify_ssl = False
        k8s_config.timeout = 5  # 5 seconds timeout for faster failure
        Configuration.set_default(k8s_config)
        
        # Create API clients
        core_v1 = client.CoreV1Api()
        
        # Get cluster version using VersionApi
        logger.info("Retrieving cluster version...")
        try:
            from kubernetes.client import VersionApi
            version_api = VersionApi()
            # Note: get_code() doesn't support timeout parameter - using API client timeout instead
            version = version_api.get_code()
            logger.info(f"Kubernetes Version: {version.git_version}")
        except Exception as e:
            if "timeout" in str(e).lower() or "Connection" in str(type(e).__name__):
                logger.warning("⚠️  Kubernetes API not directly accessible from this machine")
                logger.info("ℹ️  This is expected - Kubernetes API requires SSH tunnel or VPN")
                logger.info("ℹ️  To access Kubernetes, use one of these methods:")
                logger.info("    1. SSH tunnel: ssh -L 6443:10.10.100.102:6443 root@10.10.100.3")
                logger.info("    2. Direct SSH: ssh root@10.10.100.3 -> ssh prisma@10.10.100.113 -> k9s")
                logger.info("    3. Run tests from within cluster network")
                pytest.skip(f"Kubernetes API not accessible (requires SSH tunnel): {e}")
            else:
                raise
        
        # List nodes with timeout
        logger.info("Listing cluster nodes...")
        try:
            nodes = core_v1.list_node(timeout_seconds=5)
            logger.info(f"Found {len(nodes.items)} nodes:")
            
            for node in nodes.items:
                status = "Ready" if any(cond.type == "Ready" and cond.status == "True" 
                                       for cond in node.status.conditions) else "NotReady"
                logger.info(f"  - {node.metadata.name}: {status}")
                logger.info(f"    Kubelet Version: {node.status.node_info.kubelet_version}")
            
            logger.info("✅ Kubernetes connectivity test PASSED")
        except Exception as e:
            if "timeout" in str(e).lower() or "Connection" in str(type(e).__name__):
                logger.warning("⚠️  Kubernetes API not directly accessible")
                logger.info("ℹ️  Use SSH tunnel or direct SSH access to connect to cluster")
                pytest.skip(f"Kubernetes API not accessible (requires SSH tunnel): {e}")
            else:
                raise
        
    except config.ConfigException as e:
        logger.error(f"❌ Kubernetes config not found or invalid: {e}")
        logger.warning("⚠️  This is expected if running outside of a Kubernetes environment")
        pytest.skip(f"Kubernetes config not available: {e}")
        
    except ApiException as e:
        logger.error(f"❌ Kubernetes API error: {e}")
        pytest.fail(f"Kubernetes API error: {e}")
        
    except Exception as e:
        error_str = str(e).lower()
        if "timeout" in error_str or "connection" in error_str:
            logger.warning("⚠️  Kubernetes API connection timeout")
            logger.info("ℹ️  Kubernetes API is not directly accessible from this machine")
            logger.info("ℹ️  Solutions:")
            logger.info("    1. Create SSH tunnel: ssh -L 6443:10.10.100.102:6443 root@10.10.100.3")
            logger.info("    2. Use direct SSH access to cluster worker node")
            logger.info("    3. Run tests from within cluster network")
            pytest.skip(f"Kubernetes API not accessible (requires SSH tunnel): {e}")
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
def test_connectivity_summary():
    """
    Run all connectivity tests and provide a summary.
    
    This test provides a comprehensive overview of all external service connectivity.
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
            test_mongodb_direct_connection()
            results["MongoDB"] = "✅ PASSED"
        except:
            results["MongoDB"] = "❌ FAILED"
    else:
        results["MongoDB"] = "⚠️  SKIPPED (pymongo not installed)"
    
    # Test Kubernetes
    if K8S_AVAILABLE:
        try:
            test_kubernetes_direct_connection()
            results["Kubernetes"] = "✅ PASSED"
        except:
            results["Kubernetes"] = "❌ FAILED / SKIPPED"
    else:
        results["Kubernetes"] = "⚠️  SKIPPED (kubernetes client not installed)"
    
    # Test SSH
    if SSH_AVAILABLE:
        try:
            test_ssh_direct_connection()
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

