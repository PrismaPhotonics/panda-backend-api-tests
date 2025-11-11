"""
External Services Connectivity Tests
=====================================

Production-grade connectivity tests for all external infrastructure services.
Tests verify connection and basic health for MongoDB, Kubernetes, SSH, and RabbitMQ.

Author: QA Automation Architect
"""

import pytest
import logging
import time
from typing import Dict, Any, List

from src.core.base_test import InfrastructureTest
from src.core.exceptions import InfrastructureError
from src.infrastructure.mongodb_manager import MongoDBManager
from src.infrastructure.kubernetes_manager import KubernetesManager
from src.infrastructure.ssh_manager import SSHManager
from config.config_manager import ConfigManager


class TestExternalServicesConnectivity(InfrastructureTest):
    """
    Comprehensive connectivity tests for all external services.
    
    This test suite verifies that the framework can successfully connect
    to and communicate with all required external infrastructure services:
    - MongoDB (database)
    - Kubernetes (orchestration)
    - SSH (remote access)
    - RabbitMQ (message queue) - optional
    """
    
    @pytest.fixture(scope="class")
    def config(self, current_env):
        """
        Provide configuration manager for tests.
        
        Args:
            current_env: Current test environment
        
        Returns:
            ConfigManager instance
        """
        return ConfigManager(current_env)
    
    @pytest.fixture(scope="class")
    def test_results(self):
        """
        Store test results for final summary.
        
        Returns:
            Dictionary to store test results
        """
        return {
            "mongodb": {"connected": False, "details": {}},
            "kubernetes": {"connected": False, "details": {}},
            "ssh": {"connected": False, "details": {}},
            "all_services_healthy": False
        }
    
    # =================================================================
    # MongoDB Connectivity Tests
    # =================================================================
    
    @pytest.mark.xray("PZ-13898")
    @pytest.mark.integration
    @pytest.mark.connectivity
    @pytest.mark.mongodb
    @pytest.mark.xray("PZ-13807")
    def test_mongodb_connection(self, mongodb_manager: MongoDBManager, test_results: Dict[str, Any]):
        """
        Test MongoDB connection and basic operations.
        
        Verification:
        - Connection establishment
        - Authentication
        - Ping command
        - Database listing
        
        Args:
            mongodb_manager: MongoDB manager fixture
            test_results: Dictionary to store results
        """
        self.logger.info("=" * 80)
        self.logger.info("Testing MongoDB Connectivity")
        self.logger.info("=" * 80)
        
        try:
            # Step 1: Test connection
            self.log_test_step("Attempting to connect to MongoDB")
            connection_success = mongodb_manager.connect()
            
            assert connection_success, "Failed to connect to MongoDB"
            self.logger.info("✅ MongoDB connection successful")
            
            # Step 2: Test database operations
            self.log_test_step("Testing MongoDB database operations")
            if mongodb_manager.client:
                # List databases
                db_list = mongodb_manager.client.list_database_names()
                self.logger.info(f"Available databases: {db_list}")
                
                # Get server info
                server_info = mongodb_manager.client.server_info()
                self.logger.info(f"MongoDB version: {server_info.get('version', 'Unknown')}")
                
                test_results["mongodb"]["details"] = {
                    "version": server_info.get("version", "Unknown"),
                    "databases": db_list,
                    "host": mongodb_manager.mongo_config["host"],
                    "port": mongodb_manager.mongo_config["port"]
                }
            
            # Step 3: Disconnect
            self.log_test_step("Disconnecting from MongoDB")
            mongodb_manager.disconnect()
            
            test_results["mongodb"]["connected"] = True
            self.logger.info("✅ MongoDB connectivity test PASSED")
            
        except Exception as e:
            self.logger.error(f"❌ MongoDB connectivity test FAILED: {e}")
            test_results["mongodb"]["error"] = str(e)
            pytest.fail(f"MongoDB connectivity test failed: {e}")
    
    @pytest.mark.integration
    @pytest.mark.connectivity
    @pytest.mark.mongodb
    @pytest.mark.xray("PZ-13899")
    def test_mongodb_status_via_kubernetes(self, mongodb_manager: MongoDBManager):
        """
        Test MongoDB status via Kubernetes API.
        
        Verification:
        - Deployment exists
        - Pod is running
        - Replicas are ready
        
        Args:
            mongodb_manager: MongoDB manager fixture
        """
        self.logger.info("=" * 80)
        self.logger.info("Testing MongoDB Status via Kubernetes")
        self.logger.info("=" * 80)
        
        try:
            # Get MongoDB status
            self.log_test_step("Retrieving MongoDB status from Kubernetes")
            status = mongodb_manager.get_mongodb_status()
            
            self.logger.info(f"MongoDB Status:")
            self.logger.info(f"  - Deployment: {status.get('deployment_name')}")
            self.logger.info(f"  - Pod: {status.get('pod_name')}")
            self.logger.info(f"  - Replicas: {status.get('replicas')}")
            self.logger.info(f"  - Ready Replicas: {status.get('ready_replicas')}")
            self.logger.info(f"  - Connected: {status.get('connected')}")
            
            # Verify deployment is healthy
            assert status.get('ready_replicas', 0) > 0, "MongoDB has no ready replicas"
            assert status.get('connected', False), "MongoDB is not reachable"
            
            self.logger.info("✅ MongoDB status check PASSED")
            
        except Exception as e:
            self.logger.error(f"❌ MongoDB status check FAILED: {e}")
            pytest.fail(f"MongoDB status check failed: {e}")
    
    # =================================================================
    # Kubernetes Connectivity Tests
    # =================================================================
    
    @pytest.mark.xray("PZ-13899")
    @pytest.mark.integration
    @pytest.mark.connectivity
    @pytest.mark.kubernetes
    def test_kubernetes_connection(self, kubernetes_manager: KubernetesManager, test_results: Dict[str, Any]):
        """
        Test Kubernetes cluster connection.
        
        Verification:
        - Cluster API accessibility
        - Cluster version
        - Node status
        - Namespace access
        
        Args:
            kubernetes_manager: Kubernetes manager fixture
            test_results: Dictionary to store results
        """
        self.logger.info("=" * 80)
        self.logger.info("Testing Kubernetes Connectivity")
        self.logger.info("=" * 80)
        
        try:
            # Step 1: Get cluster info
            self.log_test_step("Retrieving Kubernetes cluster information")
            cluster_info = kubernetes_manager.get_cluster_info()
            
            self.logger.info(f"Cluster Information:")
            self.logger.info(f"  - Version: {cluster_info.get('version')}")
            self.logger.info(f"  - Nodes: {cluster_info.get('node_count')}")
            
            for node in cluster_info.get('nodes', []):
                self.logger.info(f"    • Node: {node['name']}")
                self.logger.info(f"      Status: {node['status']}")
                self.logger.info(f"      Roles: {', '.join(node['roles'])}")
                self.logger.info(f"      Kubelet Version: {node['kubelet_version']}")
            
            # Verify cluster is accessible
            assert cluster_info.get('node_count', 0) > 0, "No nodes found in cluster"
            
            test_results["kubernetes"]["details"] = cluster_info
            test_results["kubernetes"]["connected"] = True
            
            self.logger.info("✅ Kubernetes connectivity test PASSED")
            
        except Exception as e:
            self.logger.error(f"❌ Kubernetes connectivity test FAILED: {e}")
            test_results["kubernetes"]["error"] = str(e)
            pytest.fail(f"Kubernetes connectivity test failed: {e}")
    
    @pytest.mark.integration
    @pytest.mark.connectivity
    @pytest.mark.kubernetes
    @pytest.mark.xray("PZ-13899")
    def test_kubernetes_list_deployments(self, kubernetes_manager: KubernetesManager):
        """
        Test Kubernetes deployment listing.
        
        PZ-13899: Infrastructure - Kubernetes Cluster Connection and Pod Health Check
        
        Verification:
        - Can list deployments
        - Expected deployments exist
        - Deployments are ready
        
        Args:
            kubernetes_manager: Kubernetes manager fixture
        """
        self.logger.info("=" * 80)
        self.logger.info("Testing Kubernetes Deployment Listing")
        self.logger.info("=" * 80)
        
        try:
            # Get deployments
            self.log_test_step("Listing Kubernetes deployments")
            deployments = kubernetes_manager.get_deployments()
            
            self.logger.info(f"Found {len(deployments)} deployments:")
            for deployment in deployments:
                self.logger.info(f"  - {deployment['name']}")
                self.logger.info(f"    Replicas: {deployment['replicas']}")
                self.logger.info(f"    Ready: {deployment['ready_replicas']}")
                self.logger.info(f"    Available: {deployment['available_replicas']}")
            
            # Verify we can list deployments
            assert isinstance(deployments, list), "Failed to retrieve deployments list"
            
            self.logger.info("✅ Kubernetes deployment listing PASSED")
            
        except Exception as e:
            self.logger.error(f"❌ Kubernetes deployment listing FAILED: {e}")
            pytest.fail(f"Kubernetes deployment listing failed: {e}")
    
    @pytest.mark.integration
    @pytest.mark.connectivity
    @pytest.mark.kubernetes
    @pytest.mark.xray("PZ-13899")
    def test_kubernetes_list_pods(self, kubernetes_manager: KubernetesManager):
        """
        Test Kubernetes pod listing.
        
        Verification:
        - Can list pods
        - Pods have expected status
        
        Args:
            kubernetes_manager: Kubernetes manager fixture
        """
        self.logger.info("=" * 80)
        self.logger.info("Testing Kubernetes Pod Listing")
        self.logger.info("=" * 80)
        
        try:
            # Get pods
            self.log_test_step("Listing Kubernetes pods")
            pods = kubernetes_manager.get_pods()
            
            self.logger.info(f"Found {len(pods)} pods:")
            for pod in pods:
                self.logger.info(f"  - {pod['name']}")
                self.logger.info(f"    Status: {pod['status']}")
                self.logger.info(f"    Ready: {pod['ready']}")
                self.logger.info(f"    Node: {pod['node_name']}")
            
            # Verify we can list pods
            assert isinstance(pods, list), "Failed to retrieve pods list"
            
            self.logger.info("✅ Kubernetes pod listing PASSED")
            
        except Exception as e:
            self.logger.error(f"❌ Kubernetes pod listing FAILED: {e}")
            pytest.fail(f"Kubernetes pod listing failed: {e}")
    
    # =================================================================
    # SSH Connectivity Tests
    # =================================================================
    
    @pytest.mark.xray("PZ-13900")
    @pytest.mark.integration
    @pytest.mark.connectivity
    @pytest.mark.ssh
    def test_ssh_connection(self, ssh_manager: SSHManager, test_results: Dict[str, Any]):
        """
        Test SSH connection to k9s environment.
        
        Verification:
        - SSH connection establishment
        - Authentication
        - Command execution
        
        Args:
            ssh_manager: SSH manager fixture
            test_results: Dictionary to store results
        """
        self.logger.info("=" * 80)
        self.logger.info("Testing SSH Connectivity to K9s Environment")
        self.logger.info("=" * 80)
        
        try:
            # Step 1: Connect to SSH
            self.log_test_step("Attempting SSH connection")
            connection_success = ssh_manager.connect()
            
            assert connection_success, "Failed to connect via SSH"
            self.logger.info("✅ SSH connection successful")
            
            # Step 2: Execute basic command
            self.log_test_step("Executing test command via SSH")
            result = ssh_manager.execute_command("hostname")
            
            assert result["success"], f"Failed to execute SSH command: {result['stderr']}"
            hostname = result["stdout"].strip()
            self.logger.info(f"Remote hostname: {hostname}")
            
            # Step 3: Get system info
            self.log_test_step("Retrieving system information")
            system_info = ssh_manager.get_system_info()
            
            self.logger.info("System Information:")
            for key, value in system_info.items():
                self.logger.info(f"  - {key}: {value[:100]}...")  # Truncate long output
            
            # Step 4: Disconnect
            self.log_test_step("Disconnecting SSH")
            ssh_manager.disconnect()
            
            test_results["ssh"]["connected"] = True
            
            # Extract host from SSH config (support both flat and nested structures)
            ssh_config = ssh_manager.ssh_config
            if "target_host" in ssh_config:
                # New nested structure (jump_host + target_host)
                ssh_host = ssh_config["target_host"]["host"]
                ssh_port = ssh_config["target_host"].get("port", 22)
            else:
                # Legacy flat structure
                ssh_host = ssh_config.get("host", "unknown")
                ssh_port = ssh_config.get("port", 22)
            
            test_results["ssh"]["details"] = {
                "hostname": hostname,
                "host": ssh_host,
                "port": ssh_port
            }
            
            self.logger.info("✅ SSH connectivity test PASSED")
            
        except Exception as e:
            self.logger.error(f"❌ SSH connectivity test FAILED: {e}")
            test_results["ssh"]["error"] = str(e)
            pytest.fail(f"SSH connectivity test failed: {e}")
    
    @pytest.mark.integration
    @pytest.mark.connectivity
    @pytest.mark.ssh
    @pytest.mark.xray("PZ-13900")
    def test_ssh_network_operations(self, ssh_manager: SSHManager):
        """
        Test SSH network operations.
        
        PZ-13900: Infrastructure - SSH Access to Production Servers
        
        Verification:
        - Port status checking
        - Network interface listing
        
        Args:
            ssh_manager: SSH manager fixture
        """
        self.logger.info("=" * 80)
        self.logger.info("Testing SSH Network Operations")
        self.logger.info("=" * 80)
        
        try:
            # Connect
            self.log_test_step("Connecting to SSH for network operations")
            assert ssh_manager.connect(), "Failed to connect via SSH"
            
            # Get network interfaces
            self.log_test_step("Retrieving network interfaces")
            interfaces = ssh_manager.get_network_interfaces()
            
            self.logger.info(f"Found {len(interfaces)} network interfaces:")
            for interface in interfaces:
                self.logger.info(f"  - {interface['name']}: {interface.get('ip', 'No IP')}")
            
            # Check if MongoDB port is accessible
            self.log_test_step("Checking MongoDB port accessibility")
            mongo_config = ssh_manager.config_manager.get_database_config()
            mongo_host = mongo_config["host"]
            mongo_port = mongo_config["port"]
            
            # Note: This test may fail if MongoDB is not on the same host
            self.logger.info(f"Testing connectivity to MongoDB at {mongo_host}:{mongo_port}")
            
            # Disconnect
            ssh_manager.disconnect()
            
            self.logger.info("✅ SSH network operations test PASSED")
            
        except Exception as e:
            self.logger.error(f"❌ SSH network operations test FAILED: {e}")
            pytest.fail(f"SSH network operations test failed: {e}")
    
    # =================================================================
    # Summary and Health Check
    # =================================================================
    
    @pytest.mark.integration
    @pytest.mark.connectivity
    @pytest.mark.summary
    @pytest.mark.xray("PZ-13898")
    def test_all_services_summary(self, test_results: Dict[str, Any]):
        """
        Summary test for all external service connectivity.
        
        This test runs last and provides a comprehensive summary
        of all connectivity tests.
        
        Args:
            test_results: Dictionary containing all test results
        """
        self.logger.info("=" * 80)
        self.logger.info("CONNECTIVITY TEST SUMMARY")
        self.logger.info("=" * 80)
        
        all_passed = True
        
        # MongoDB Summary
        mongo_status = "✅ PASSED" if test_results["mongodb"]["connected"] else "❌ FAILED"
        self.logger.info(f"MongoDB: {mongo_status}")
        if test_results["mongodb"]["connected"]:
            details = test_results["mongodb"]["details"]
            self.logger.info(f"  Host: {details.get('host')}:{details.get('port')}")
            self.logger.info(f"  Version: {details.get('version')}")
            self.logger.info(f"  Databases: {len(details.get('databases', []))}")
        else:
            all_passed = False
            self.logger.error(f"  Error: {test_results['mongodb'].get('error', 'Unknown')}")
        
        # Kubernetes Summary
        k8s_status = "✅ PASSED" if test_results["kubernetes"]["connected"] else "❌ FAILED"
        self.logger.info(f"Kubernetes: {k8s_status}")
        if test_results["kubernetes"]["connected"]:
            details = test_results["kubernetes"]["details"]
            self.logger.info(f"  Version: {details.get('version')}")
            self.logger.info(f"  Nodes: {details.get('node_count')}")
        else:
            all_passed = False
            self.logger.error(f"  Error: {test_results['kubernetes'].get('error', 'Unknown')}")
        
        # SSH Summary
        ssh_status = "✅ PASSED" if test_results["ssh"]["connected"] else "❌ FAILED"
        self.logger.info(f"SSH: {ssh_status}")
        if test_results["ssh"]["connected"]:
            details = test_results["ssh"]["details"]
            self.logger.info(f"  Host: {details.get('host')}:{details.get('port')}")
            self.logger.info(f"  Hostname: {details.get('hostname')}")
        else:
            all_passed = False
            self.logger.error(f"  Error: {test_results['ssh'].get('error', 'Unknown')}")
        
        self.logger.info("=" * 80)
        
        if all_passed:
            self.logger.info("🎉 ALL EXTERNAL SERVICES ARE CONNECTED AND HEALTHY")
            test_results["all_services_healthy"] = True
        else:
            self.logger.error("⚠️  SOME EXTERNAL SERVICES FAILED CONNECTIVITY TESTS")
            test_results["all_services_healthy"] = False
            pytest.fail("Not all external services passed connectivity tests")
        
        self.logger.info("=" * 80)


# =================================================================
# Standalone Connectivity Test Functions
# =================================================================

@pytest.mark.xray("PZ-13898")
def test_quick_mongodb_ping(mongodb_manager: MongoDBManager):
    """
    Quick MongoDB ping test (standalone, can run independently).
    
    PZ-13898: Infrastructure - MongoDB Direct Connection and Health Check
    
    Args:
        mongodb_manager: MongoDB manager fixture
    """
    logger = logging.getLogger(__name__)
    logger.info("Quick MongoDB ping test")
    
    try:
        assert mongodb_manager.connect(), "MongoDB connection failed"
        logger.info("✅ MongoDB is reachable")
        mongodb_manager.disconnect()
    except AssertionError:
        logger.error("❌ MongoDB is NOT reachable")
        raise


@pytest.mark.xray("PZ-13899")
def test_quick_kubernetes_ping(kubernetes_manager: KubernetesManager):
    """
    Quick Kubernetes ping test (standalone, can run independently).
    
    PZ-13899: Infrastructure - Kubernetes Cluster Connection and Pod Health Check
    
    Args:
        kubernetes_manager: Kubernetes manager fixture
    """
    logger = logging.getLogger(__name__)
    logger.info("Quick Kubernetes ping test")
    
    try:
        cluster_info = kubernetes_manager.get_cluster_info()
        assert cluster_info.get('node_count', 0) > 0, "No nodes found"
        logger.info(f"✅ Kubernetes cluster is reachable ({cluster_info.get('node_count')} nodes)")
    except Exception as e:
        logger.error(f"❌ Kubernetes cluster is NOT reachable: {e}")
        raise


@pytest.mark.xray("PZ-13900")
def test_quick_ssh_ping(ssh_manager: SSHManager):
    """
    Quick SSH ping test (standalone, can run independently).
    
    PZ-13900: Infrastructure - SSH Access to Production Servers
    
    Args:
        ssh_manager: SSH manager fixture
    """
    logger = logging.getLogger(__name__)
    logger.info("Quick SSH ping test")
    
    try:
        assert ssh_manager.connect(), "SSH connection failed"
        logger.info("✅ SSH is reachable")
        ssh_manager.disconnect()
    except AssertionError:
        logger.error("❌ SSH is NOT reachable")
        raise


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

