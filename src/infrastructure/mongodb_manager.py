"""
MongoDB Manager
===============

MongoDB infrastructure manager for outage simulation and management.
"""

import logging
import time
import subprocess
from typing import Optional, Dict, Any

import pymongo
from kubernetes import client, config
from kubernetes.client.rest import ApiException

from src.core.exceptions import InfrastructureError, DatabaseError
from config.config_manager import ConfigManager


class MongoDBManager:
    """
    MongoDB infrastructure manager for testing and operations.
    
    Provides methods for:
    - MongoDB connection management
    - Outage simulation (scale down, delete pod, network block)
    - Service restoration
    - Health monitoring
    """
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize MongoDB manager.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.mongo_config = config_manager.get_database_config()
        self.k8s_config = config_manager.get_kubernetes_config()
        self.logger = logging.getLogger(__name__)
        
        # MongoDB client
        self.client: Optional[pymongo.MongoClient] = None
        
        # Kubernetes clients
        self.k8s_apps_v1: Optional[client.AppsV1Api] = None
        self.k8s_core_v1: Optional[client.CoreV1Api] = None
        
        self._load_k8s_config()
        self.logger.info("MongoDB manager initialized")
    
    def _load_k8s_config(self):
        """Load Kubernetes configuration."""
        try:
            config.load_kube_config()
            self.k8s_apps_v1 = client.AppsV1Api()
            self.k8s_core_v1 = client.CoreV1Api()
            self.logger.debug("Kubernetes configuration loaded successfully")
        except config.ConfigException as e:
            raise InfrastructureError(f"Failed to load Kubernetes config: {e}") from e
    
    def connect(self) -> bool:
        """
        Connect to MongoDB.
        
        Returns:
            True if connection successful
        """
        try:
            self.logger.debug("Connecting to MongoDB...")
            
            # Create MongoDB client
            self.client = pymongo.MongoClient(
                host=self.mongo_config["host"],
                port=self.mongo_config["port"],
                username=self.mongo_config["username"],
                password=self.mongo_config["password"],
                authSource=self.mongo_config.get("auth_source", "admin"),
                serverSelectionTimeoutMS=5000,  # 5 seconds timeout
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            
            # Test connection with ping
            self.client.admin.command('ping')
            
            self.logger.info("Successfully connected to MongoDB")
            return True
            
        except pymongo.errors.ConnectionFailure as e:
            self.logger.error(f"MongoDB connection failed: {e}")
            return False
        except pymongo.errors.ServerSelectionTimeoutError as e:
            self.logger.error(f"MongoDB server selection timeout: {e}")
            return False
        except pymongo.errors.OperationFailure as e:
            self.logger.error(f"MongoDB operation failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during MongoDB connection: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
            self.client = None
            self.logger.info("Disconnected from MongoDB")
    
    def _get_mongodb_deployment_name(self) -> str:
        """Get MongoDB deployment name from configuration."""
        return self.mongo_config.get("service_name", "mongodb")
    
    def _get_mongodb_pod_name(self) -> Optional[str]:
        """
        Get MongoDB pod name.
        
        Returns:
            Pod name or None if not found
        """
        try:
            deployment_name = self._get_mongodb_deployment_name()
            namespace = self.k8s_config["namespace"]
            
            # Get pods with the deployment label
            pods = self.k8s_core_v1.list_namespaced_pod(
                namespace=namespace,
                label_selector=f"app={deployment_name}"
            )
            
            if pods.items:
                pod_name = pods.items[0].metadata.name
                self.logger.debug(f"Found MongoDB pod: {pod_name}")
                return pod_name
            else:
                self.logger.warning("No MongoDB pods found")
                return None
                
        except ApiException as e:
            raise InfrastructureError(f"K8s API error getting MongoDB pod name: {e}") from e
    
    def scale_down_mongodb(self, replicas: int = 0):
        """
        Scale down MongoDB deployment to specified number of replicas.
        
        Args:
            replicas: Number of replicas to scale to
        """
        deployment_name = self._get_mongodb_deployment_name()
        namespace = self.k8s_config["namespace"]
        
        try:
            self.logger.info(f"Scaling down MongoDB deployment '{deployment_name}' to {replicas} replicas...")
            
            # Patch deployment scale
            self.k8s_apps_v1.patch_namespaced_deployment_scale(
                name=deployment_name,
                namespace=namespace,
                body={"spec": {"replicas": replicas}}
            )
            
            # Wait for scaling to complete
            self._wait_for_mongodb_replicas(replicas)
            
            self.logger.info(f"MongoDB deployment '{deployment_name}' scaled to {replicas} replicas")
            
        except ApiException as e:
            raise InfrastructureError(f"K8s API error scaling MongoDB deployment: {e}") from e
    
    def delete_mongodb_pod(self):
        """Delete MongoDB pod to simulate pod failure."""
        pod_name = self._get_mongodb_pod_name()
        namespace = self.k8s_config["namespace"]
        
        if not pod_name:
            self.logger.warning("No MongoDB pod found to delete")
            return
        
        try:
            self.logger.info(f"Deleting MongoDB pod '{pod_name}'...")
            
            # Delete pod
            self.k8s_core_v1.delete_namespaced_pod(
                name=pod_name,
                namespace=namespace
            )
            
            # Wait for pod deletion
            self._wait_for_mongodb_pod_deletion(pod_name)
            
            self.logger.info(f"MongoDB pod '{pod_name}' deleted successfully")
            
        except ApiException as e:
            raise InfrastructureError(f"K8s API error deleting MongoDB pod: {e}") from e
    
    def restore_mongodb(self, replicas: int = 1):
        """
        Restore MongoDB to normal operation.
        
        Args:
            replicas: Number of replicas to restore to
        """
        self.logger.info(f"Restoring MongoDB to {replicas} replicas...")
        self.scale_down_mongodb(replicas)
        
        # Wait for MongoDB to become ready
        time.sleep(10)
        
        # Verify connection
        if self.connect():
            self.logger.info("MongoDB restored successfully")
            self.disconnect()
        else:
            self.logger.warning("MongoDB restoration completed but connection verification failed")
    
    def _wait_for_mongodb_replicas(self, expected_replicas: int, timeout: int = 120):
        """
        Wait for MongoDB deployment to reach expected number of replicas.
        
        Args:
            expected_replicas: Expected number of replicas
            timeout: Timeout in seconds
        """
        deployment_name = self._get_mongodb_deployment_name()
        namespace = self.k8s_config["namespace"]
        
        self.logger.debug(f"Waiting for MongoDB deployment to reach {expected_replicas} replicas...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                deployment = self.k8s_apps_v1.read_namespaced_deployment(
                    name=deployment_name,
                    namespace=namespace
                )
                
                ready_replicas = deployment.status.ready_replicas or 0
                
                if ready_replicas == expected_replicas:
                    self.logger.debug(f"MongoDB deployment reached {expected_replicas} replicas")
                    return
                
                self.logger.debug(f"MongoDB deployment has {ready_replicas} ready replicas, waiting...")
                
            except ApiException as e:
                self.logger.warning(f"K8s API error while waiting for replicas: {e}")
            
            time.sleep(5)
        
        raise InfrastructureError(
            f"MongoDB deployment '{deployment_name}' did not reach {expected_replicas} replicas within {timeout} seconds"
        )
    
    def _wait_for_mongodb_pod_deletion(self, pod_name: str, timeout: int = 120):
        """
        Wait for MongoDB pod to be deleted.
        
        Args:
            pod_name: Name of the pod to wait for deletion
            timeout: Timeout in seconds
        """
        namespace = self.k8s_config["namespace"]
        
        self.logger.debug(f"Waiting for MongoDB pod '{pod_name}' to be deleted...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                self.k8s_core_v1.read_namespaced_pod(
                    name=pod_name,
                    namespace=namespace
                )
                self.logger.debug(f"MongoDB pod '{pod_name}' still exists, waiting...")
                
            except ApiException as e:
                if e.status == 404:  # Pod not found, meaning it's deleted
                    self.logger.debug(f"MongoDB pod '{pod_name}' deleted successfully")
                    return
                else:
                    raise InfrastructureError(f"K8s API error while waiting for pod deletion: {e}") from e
            
            time.sleep(5)
        
        raise InfrastructureError(f"MongoDB pod '{pod_name}' was not deleted within {timeout} seconds")
    
    def block_network_access(self, node_ip: str, port: int):
        """
        Block network access to MongoDB using iptables.
        
        Args:
            node_ip: Node IP address
            port: MongoDB port
        """
        self.logger.info(f"Blocking network access to MongoDB on {node_ip}:{port}...")
        
        try:
            # This would require SSH access to the node
            # For now, we'll log the operation
            self.logger.warning(
                "Network blocking via iptables requires SSH access to the node. "
                "This operation is not implemented directly in this manager."
            )
            
            # Example of what would be done via SSH:
            # ssh_client.exec_command(f"sudo iptables -A INPUT -p tcp --dport {port} -j DROP")
            
        except Exception as e:
            raise InfrastructureError(f"Failed to block network access: {e}") from e
    
    def unblock_network_access(self, node_ip: str, port: int):
        """
        Unblock network access to MongoDB using iptables.
        
        Args:
            node_ip: Node IP address
            port: MongoDB port
        """
        self.logger.info(f"Unblocking network access to MongoDB on {node_ip}:{port}...")
        
        try:
            # This would require SSH access to the node
            # For now, we'll log the operation
            self.logger.warning(
                "Network unblocking via iptables requires SSH access to the node. "
                "This operation is not implemented directly in this manager."
            )
            
            # Example of what would be done via SSH:
            # ssh_client.exec_command(f"sudo iptables -D INPUT -p tcp --dport {port} -j DROP")
            
        except Exception as e:
            raise InfrastructureError(f"Failed to unblock network access: {e}") from e
    
    def get_mongodb_status(self) -> Dict[str, Any]:
        """
        Get MongoDB status information.
        
        Returns:
            Dictionary containing MongoDB status
        """
        status = {
            "connected": False,
            "deployment_name": self._get_mongodb_deployment_name(),
            "pod_name": None,
            "replicas": 0,
            "ready_replicas": 0
        }
        
        try:
            # Check connection
            if self.connect():
                status["connected"] = True
                self.disconnect()
            
            # Get deployment status
            deployment_name = self._get_mongodb_deployment_name()
            namespace = self.k8s_config["namespace"]
            
            deployment = self.k8s_apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )
            
            status["replicas"] = deployment.spec.replicas or 0
            status["ready_replicas"] = deployment.status.ready_replicas or 0
            
            # Get pod name
            status["pod_name"] = self._get_mongodb_pod_name()
            
        except Exception as e:
            self.logger.error(f"Error getting MongoDB status: {e}")
            status["error"] = str(e)
        
        return status
    
    def create_outage_scale_down(self):
        """Create MongoDB outage by scaling down to 0 replicas."""
        self.logger.info("Creating MongoDB outage by scaling down to 0 replicas")
        self.scale_down_mongodb(replicas=0)
    
    def create_outage_delete_pod(self):
        """Create MongoDB outage by deleting the pod."""
        self.logger.info("Creating MongoDB outage by deleting pod")
        self.delete_mongodb_pod()
    
    def create_outage_network_block(self, node_ip: Optional[str] = None, port: Optional[int] = None):
        """
        Create MongoDB outage by blocking network access.
        
        Args:
            node_ip: Node IP address (defaults to configured value)
            port: MongoDB port (defaults to configured value)
        """
        if not node_ip:
            node_ip = self.k8s_config.get("cluster_host", "localhost")
        if not port:
            port = self.mongo_config["port"]
        
        self.logger.info(f"Creating MongoDB outage by blocking network access to {node_ip}:{port}")
        self.block_network_access(node_ip, port)
    
    def restore_from_outage(self):
        """Restore MongoDB from any type of outage."""
        self.logger.info("Restoring MongoDB from outage")
        self.restore_mongodb()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()