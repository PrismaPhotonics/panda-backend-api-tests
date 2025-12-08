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
    
    def __init__(self, config_manager: ConfigManager, kubernetes_manager: Optional[Any] = None):
        """
        Initialize MongoDB manager.
        
        Args:
            config_manager: Configuration manager instance
            kubernetes_manager: Optional KubernetesManager instance (for SSH fallback support)
        """
        self.config_manager = config_manager
        self.mongo_config = config_manager.get_database_config()
        self.k8s_config = config_manager.get_kubernetes_config()
        self.logger = logging.getLogger(__name__)
        
        # MongoDB client
        self.client: Optional[pymongo.MongoClient] = None
        
        # Kubernetes manager (preferred - supports SSH fallback)
        self.kubernetes_manager: Optional[Any] = kubernetes_manager
        
        # Kubernetes clients (fallback - direct API access)
        self.k8s_apps_v1: Optional[client.AppsV1Api] = None
        self.k8s_core_v1: Optional[client.CoreV1Api] = None
        
        # Only load direct K8s config if kubernetes_manager not provided
        if not self.kubernetes_manager:
            self._load_k8s_config()
        
        self.logger.info("MongoDB manager initialized")
    
    def _load_k8s_config(self):
        """Load Kubernetes configuration (optional - only if available)."""
        try:
            config.load_kube_config()
            self.k8s_apps_v1 = client.AppsV1Api()
            self.k8s_core_v1 = client.CoreV1Api()
            self.logger.debug("Kubernetes configuration loaded successfully")
        except config.ConfigException as e:
            # Kubernetes config not available - this is OK for local development
            self.logger.warning(f"Kubernetes config not available: {e}")
            self.logger.info("Kubernetes operations will be disabled (OK for local dev)")
            self.k8s_apps_v1 = None
            self.k8s_core_v1 = None
    
    def _ensure_k8s_available(self):
        """Ensure Kubernetes is available (either direct API or via KubernetesManager with SSH fallback)."""
        # Check if KubernetesManager with SSH fallback is available
        if self.kubernetes_manager is not None:
            # KubernetesManager handles its own availability check
            if hasattr(self.kubernetes_manager, 'use_ssh_fallback') and self.kubernetes_manager.use_ssh_fallback:
                # SSH fallback is available
                return
            if hasattr(self.kubernetes_manager, 'k8s_apps_v1') and self.kubernetes_manager.k8s_apps_v1 is not None:
                # Direct K8s API via KubernetesManager is available
                return
        
        # Check direct K8s API clients
        if self.k8s_apps_v1 is not None and self.k8s_core_v1 is not None:
            return
        
        raise InfrastructureError(
            "Kubernetes is not available. "
            "This operation requires a valid kubeconfig or SSH access to the cluster. "
            "Are you running outside of a Kubernetes environment?"
        )
    
    def is_k8s_available(self) -> bool:
        """
        Check if Kubernetes operations are available.
        
        Returns:
            True if K8s is available (direct API or SSH fallback)
        """
        try:
            self._ensure_k8s_available()
            return True
        except InfrastructureError:
            return False
    
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
                authSource=self.mongo_config.get("auth_source", "prisma"),  # Changed from "admin" to "prisma"
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
    
    def get_database(self, database_name: Optional[str] = None):
        """
        Get MongoDB database instance.
        
        Args:
            database_name: Name of the database (defaults to configured database)
            
        Returns:
            Database instance
        """
        if not self.client:
            raise DatabaseError("MongoDB client not connected. Call connect() first.")
        
        db_name = database_name or self.mongo_config.get("database", "prisma")
        return self.client[db_name]
    
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
            
            # Use KubernetesManager if available (supports SSH fallback)
            if self.kubernetes_manager is not None:
                try:
                    pods = self.kubernetes_manager.get_pods(namespace=namespace)
                    mongodb_pods = [p for p in pods if deployment_name in p["name"]]
                    if mongodb_pods:
                        pod_name = mongodb_pods[0]["name"]
                        self.logger.debug(f"Found MongoDB pod via KubernetesManager: {pod_name}")
                        return pod_name
                except Exception as e:
                    self.logger.warning(f"Failed to get pod name via KubernetesManager: {e}")
            
            # Fallback to direct API access
            if self.k8s_core_v1 is not None:
                # Get pod_selector from config, fallback to legacy format
                pod_selector = self.mongo_config.get("pod_selector", f"app={deployment_name}")
                pods = self.k8s_core_v1.list_namespaced_pod(
                    namespace=namespace,
                    label_selector=pod_selector
                )
                if pods.items:
                    pod_name = pods.items[0].metadata.name
                    self.logger.debug(f"Found MongoDB pod: {pod_name}")
                    return pod_name
                else:
                    self.logger.warning("No MongoDB pods found")
                    return None
            else:
                self.logger.warning("Kubernetes API not available")
                return None
                
        except ApiException as e:
            raise InfrastructureError(f"K8s API error getting MongoDB pod name: {e}") from e
        except Exception as e:
            self.logger.warning(f"Failed to get MongoDB pod name: {e}")
            return None
    
    def scale_down_mongodb(self, replicas: int = 0):
        """
        Scale down MongoDB deployment to specified number of replicas.
        
        Args:
            replicas: Number of replicas to scale to
        """
        self._ensure_k8s_available()
        
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
        self._ensure_k8s_available()
        
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
            replicas: Number of replicas to restore
        """
        self._ensure_k8s_available()
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
        
        Uses KubernetesManager if available (supports SSH fallback),
        otherwise falls back to direct Kubernetes API access.
        
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
            
            # Get deployment status (prefer KubernetesManager for SSH fallback support)
            deployment_name = self._get_mongodb_deployment_name()
            namespace = self.k8s_config["namespace"]
            
            if self.kubernetes_manager is not None:
                # Use KubernetesManager (supports SSH fallback)
                try:
                    deployments = self.kubernetes_manager.get_deployments(namespace=namespace)
                    deployment = next(
                        (d for d in deployments if d["name"] == deployment_name),
                        None
                    )
                    
                    if deployment:
                        status["replicas"] = deployment.get("replicas", 0)
                        status["ready_replicas"] = deployment.get("ready_replicas", 0)
                        status["pod_name"] = self._get_mongodb_pod_name()
                    else:
                        status["error"] = f"Deployment '{deployment_name}' not found"
                except Exception as e:
                    self.logger.error(f"Error getting MongoDB status via KubernetesManager: {e}")
                    status["error"] = str(e)
            elif self.k8s_apps_v1 is not None:
                # Fallback to direct API access
                try:
                    deployment = self.k8s_apps_v1.read_namespaced_deployment(
                        name=deployment_name,
                        namespace=namespace
                    )
                    
                    status["replicas"] = deployment.spec.replicas or 0
                    status["ready_replicas"] = deployment.status.ready_replicas or 0
                    status["pod_name"] = self._get_mongodb_pod_name()
                except Exception as e:
                    self.logger.error(f"Error getting MongoDB status via direct API: {e}")
                    status["error"] = str(e)
            else:
                status["error"] = "Kubernetes not available"
            
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