"""
Fixed Kubernetes Manager with proper error handling
"""

import logging
import time
from typing import List, Dict, Any, Optional
import urllib3
import warnings

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

from kubernetes import client, config
from kubernetes.client.rest import ApiException

from src.core.exceptions import InfrastructureError
from config.config_manager import ConfigManager


class KubernetesManagerFixed:
    """
    Fixed Kubernetes manager that handles connection issues properly.
    """
    
    def __init__(self, config_manager: ConfigManager):
        """Initialize Kubernetes manager with better error handling."""
        self.config_manager = config_manager
        self.k8s_config = config_manager.get_kubernetes_config()
        self.logger = logging.getLogger(__name__)
        
        # Kubernetes clients
        self.k8s_apps_v1: Optional[client.AppsV1Api] = None
        self.k8s_core_v1: Optional[client.CoreV1Api] = None
        self.k8s_batch_v1: Optional[client.BatchV1Api] = None
        
        # Connection status
        self.connected = False
        self.connection_error = None
        
        self._load_k8s_config()
        
    def _load_k8s_config(self):
        """Load Kubernetes configuration with multiple fallback options."""
        try:
            # Try loading standard kubeconfig
            config.load_kube_config()
            
            # Get and modify configuration for self-signed certs
            configuration = client.Configuration.get_default_copy()
            
            # Disable SSL verification for self-signed certificates
            configuration.verify_ssl = False
            configuration.debug = False
            
            # Set as default
            client.Configuration.set_default(configuration)
            
            # Create API clients
            self.k8s_apps_v1 = client.AppsV1Api()
            self.k8s_core_v1 = client.CoreV1Api()
            self.k8s_batch_v1 = client.BatchV1Api()
            
            # Test connection
            try:
                self.k8s_core_v1.list_namespace(timeout_seconds=5)
                self.connected = True
                self.logger.info("Kubernetes configuration loaded and connected successfully")
            except Exception as e:
                self.connected = False
                self.connection_error = str(e)
                self.logger.warning(f"Kubernetes API not accessible: {e}")
                self.logger.info("Kubernetes operations will work in degraded mode")
                
        except config.ConfigException as e:
            # Try in-cluster config
            try:
                config.load_incluster_config()
                configuration = client.Configuration.get_default_copy()
                configuration.verify_ssl = False
                client.Configuration.set_default(configuration)
                
                self.k8s_apps_v1 = client.AppsV1Api()
                self.k8s_core_v1 = client.CoreV1Api()
                self.k8s_batch_v1 = client.BatchV1Api()
                self.connected = True
                self.logger.info("In-cluster Kubernetes configuration loaded")
            except:
                # No valid config available
                self.logger.warning(f"Kubernetes config not available: {e}")
                self.logger.info("Kubernetes operations will be disabled (OK for local dev)")
                self.connected = False
                self.connection_error = "No valid Kubernetes configuration found"
    
    def _ensure_k8s_available(self):
        """Ensure Kubernetes is available, provide helpful error if not."""
        if not self.connected or self.k8s_apps_v1 is None or self.k8s_core_v1 is None:
            error_msg = (
                "Kubernetes is not available. "
                f"Connection error: {self.connection_error}\n"
                "Possible solutions:\n"
                "1. Create SSH tunnel: ssh -L 6443:10.10.100.102:6443 root@10.10.100.3\n"
                "2. Update kubeconfig to use localhost:6443 after creating tunnel\n"
                "3. Run tests from within the cluster network\n"
                "4. Use direct SSH access: ssh root@10.10.100.3 -> ssh prisma@10.10.100.113 -> k9s"
            )
            raise InfrastructureError(error_msg)
    
    def get_cluster_info(self) -> Dict[str, Any]:
        """
        Get cluster information with proper error handling.
        
        Returns:
            Dictionary containing cluster information or error details
        """
        if not self.connected:
            return {
                "connected": False,
                "error": self.connection_error,
                "hint": "Create SSH tunnel: ssh -L 6443:10.10.100.102:6443 root@10.10.100.3"
            }
        
        try:
            # Get cluster version using a more reliable method
            v1 = client.CoreV1Api()
            
            # Get nodes
            nodes = v1.list_node(timeout_seconds=5)
            
            cluster_info = {
                "connected": True,
                "node_count": len(nodes.items),
                "nodes": []
            }
            
            for node in nodes.items:
                node_info = {
                    "name": node.metadata.name,
                    "status": "Ready" if any(c.type == "Ready" and c.status == "True" 
                                            for c in node.status.conditions) else "NotReady",
                    "roles": [label.split("/")[-1] 
                             for label in node.metadata.labels.keys() 
                             if label.startswith("node-role.kubernetes.io/")],
                    "kubelet_version": node.status.node_info.kubelet_version
                }
                cluster_info["nodes"].append(node_info)
            
            # Try to get version (may fail but not critical)
            try:
                from kubernetes.client import VersionApi
                version_api = VersionApi()
                version = version_api.get_code()
                cluster_info["version"] = version.git_version
            except:
                cluster_info["version"] = "Unknown"
            
            self.logger.debug(f"Retrieved cluster info: {cluster_info['node_count']} nodes")
            return cluster_info
            
        except ApiException as e:
            if e.status == 401:
                error_msg = "Authentication failed - check credentials"
            elif e.status == 403:
                error_msg = "Permission denied - check RBAC permissions"
            else:
                error_msg = f"API error: {e.reason}"
            
            return {
                "connected": False,
                "error": error_msg,
                "status_code": e.status
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
                "type": type(e).__name__
            }
    
    def test_connection(self) -> bool:
        """
        Test Kubernetes connection.
        
        Returns:
            True if connected, False otherwise
        """
        if not self.k8s_core_v1:
            return False
        
        try:
            self.k8s_core_v1.list_namespace(timeout_seconds=2)
            return True
        except:
            return False
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get detailed connection status.
        
        Returns:
            Dictionary with connection details
        """
        return {
            "connected": self.connected,
            "error": self.connection_error,
            "api_available": self.k8s_core_v1 is not None,
            "test_connection": self.test_connection() if self.k8s_core_v1 else False,
            "hints": [
                "Create SSH tunnel: ssh -L 6443:10.10.100.102:6443 root@10.10.100.3",
                "Or connect directly: ssh root@10.10.100.3 -> ssh prisma@10.10.100.113"
            ] if not self.connected else []
        }
