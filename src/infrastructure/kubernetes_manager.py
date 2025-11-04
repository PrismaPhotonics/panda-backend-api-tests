"""
Kubernetes Manager
==================

Kubernetes infrastructure manager for cluster operations and monitoring.
"""

import logging
import time
import json
import platform
from typing import List, Dict, Any, Optional

from kubernetes import client, config
from kubernetes.client.rest import ApiException

from src.core.exceptions import InfrastructureError
from config.config_manager import ConfigManager


class KubernetesManager:
    """
    Kubernetes infrastructure manager for testing and operations.
    
    Provides methods for:
    - Pod management
    - Deployment management
    - Service management
    - Job management
    - Log retrieval
    - Resource monitoring
    
    Supports both direct Kubernetes API access and SSH-based kubectl fallback.
    """
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize Kubernetes manager.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.k8s_config = config_manager.get_kubernetes_config()
        self.logger = logging.getLogger(__name__)
        
        # Kubernetes clients (direct API access)
        self.k8s_apps_v1: Optional[client.AppsV1Api] = None
        self.k8s_core_v1: Optional[client.CoreV1Api] = None
        self.k8s_batch_v1: Optional[client.BatchV1Api] = None
        
        # SSH fallback for kubectl commands
        self.ssh_manager: Optional[Any] = None  # Lazy import to avoid circular dependencies
        self.use_ssh_fallback = False
        
        self._load_k8s_config()
        self.logger.info("Kubernetes manager initialized")
    
    def _load_k8s_config(self):
        """
        Load Kubernetes configuration.
        
        Tries direct API access first, falls back to SSH-based kubectl if needed.
        """
        try:
            # Try to load kubeconfig and create API clients
            config.load_kube_config()
            self.k8s_apps_v1 = client.AppsV1Api()
            self.k8s_core_v1 = client.CoreV1Api()
            self.k8s_batch_v1 = client.BatchV1Api()
            self.logger.debug("Kubernetes configuration loaded successfully")
            
            # Test connection (quick check)
            try:
                self.k8s_core_v1.list_node(timeout_seconds=5)
                self.logger.debug("Direct Kubernetes API connection verified")
            except Exception as e:
                # Connection failed - likely timeout or network issue
                error_str = str(e).lower()
                if "timeout" in error_str or "connection" in error_str:
                    self.logger.warning("Kubernetes API not directly accessible, falling back to SSH-based kubectl")
                    self._init_ssh_fallback()
                else:
                    raise
                    
        except config.ConfigException as e:
            # No kubeconfig available - use SSH fallback
            self.logger.warning(f"Kubernetes config not available: {e}")
            self.logger.info("Falling back to SSH-based kubectl commands")
            self._init_ssh_fallback()
        except Exception as e:
            # Other errors - try SSH fallback
            error_str = str(e).lower()
            if "timeout" in error_str or "connection" in error_str:
                self.logger.warning(f"Kubernetes API connection failed: {e}")
                self.logger.info("Falling back to SSH-based kubectl commands")
                self._init_ssh_fallback()
            else:
                # Unknown error - still try SSH fallback as last resort
                self.logger.warning(f"Unexpected error loading Kubernetes config: {e}")
                self.logger.info("Attempting SSH-based kubectl fallback")
                self._init_ssh_fallback()
    
    def _init_ssh_fallback(self) -> bool:
        """
        Initialize SSH-based kubectl fallback.
        
        Returns:
            True if SSH fallback was successfully initialized
        """
        try:
            from src.infrastructure.ssh_manager import SSHManager
            
            self.ssh_manager = SSHManager(self.config_manager)
            if self.ssh_manager.connect():
                self.use_ssh_fallback = True
                self.logger.info("SSH-based kubectl fallback initialized successfully")
                return True
            else:
                self.logger.warning("Failed to initialize SSH connection for kubectl fallback")
                self.ssh_manager = None
                return False
        except Exception as e:
            self.logger.warning(f"Failed to initialize SSH fallback: {e}")
            self.ssh_manager = None
            return False
    
    def _execute_kubectl_via_ssh(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Execute kubectl command via SSH.
        
        Args:
            command: kubectl command to execute
            timeout: Command timeout in seconds
            
        Returns:
            Dictionary with command results (stdout, stderr, exit_code, success)
        """
        if not self.ssh_manager:
            if not self._init_ssh_fallback():
                raise InfrastructureError("SSH manager not available for kubectl execution")
        
        if not self.ssh_manager.connected:
            if not self.ssh_manager.connect():
                raise InfrastructureError("Failed to connect via SSH for kubectl execution")
        
        namespace = self.k8s_config.get("namespace", "panda")
        full_command = f"kubectl -n {namespace} {command}"
        
        self.logger.debug(f"Executing kubectl via SSH: {full_command}")
        result = self.ssh_manager.execute_command(full_command, timeout=timeout)
        
        if not result["success"]:
            self.logger.warning(f"kubectl command failed: {result['stderr']}")
        
        return result
    
    def _ensure_k8s_available(self):
        """Ensure Kubernetes is available (either direct API or SSH fallback)."""
        if self.use_ssh_fallback:
            if not self.ssh_manager or not self.ssh_manager.connected:
                raise InfrastructureError(
                    "Kubernetes SSH fallback not available. "
                    "SSH connection required for kubectl commands."
                )
        else:
            if self.k8s_apps_v1 is None or self.k8s_core_v1 is None:
                raise InfrastructureError(
                    "Kubernetes is not available. "
                    "This operation requires a valid kubeconfig or SSH access. "
                    "Are you running outside of a Kubernetes environment?"
                )
    
    def get_pods(self, namespace: Optional[str] = None, label_selector: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get pods in the specified namespace.
        
        Args:
            namespace: Kubernetes namespace (defaults to configured namespace)
            label_selector: Label selector for filtering pods
            
        Returns:
            List of pod information dictionaries
        """
        self._ensure_k8s_available()
        
        if not namespace:
            namespace = self.k8s_config.get("namespace", "panda")
        
        # Use SSH fallback if direct API is not available
        if self.use_ssh_fallback:
            return self._get_pods_via_ssh(namespace, label_selector)
        
        try:
            pods = self.k8s_core_v1.list_namespaced_pod(
                namespace=namespace,
                label_selector=label_selector
            )
            
            pod_list = []
            for pod in pods.items:
                pod_info = {
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "status": pod.status.phase,
                    "ready": pod.status.conditions[0].status if pod.status.conditions else "Unknown",
                    "restart_count": pod.status.container_statuses[0].restart_count if pod.status.container_statuses else 0,
                    "node_name": pod.spec.node_name,
                    "labels": pod.metadata.labels
                }
                pod_list.append(pod_info)
            
            self.logger.debug(f"Retrieved {len(pod_list)} pods from namespace '{namespace}'")
            return pod_list
            
        except ApiException as e:
            # If API fails, try SSH fallback
            error_str = str(e).lower()
            if "timeout" in error_str or "connection" in error_str:
                self.logger.warning("Direct API failed, falling back to SSH-based kubectl")
                self._init_ssh_fallback()
                return self._get_pods_via_ssh(namespace, label_selector)
            raise InfrastructureError(f"Failed to get pods: {e}") from e
    
    def _get_pods_via_ssh(self, namespace: Optional[str], label_selector: Optional[str]) -> List[Dict[str, Any]]:
        """Get pods via SSH kubectl command."""
        if not namespace:
            namespace = self.k8s_config.get("namespace", "panda")
        
        # Build kubectl command
        cmd = f"get pods -o json"
        if label_selector:
            cmd += f" -l {label_selector}"
        
        result = self._execute_kubectl_via_ssh(cmd, timeout=30)
        
        if not result["success"]:
            raise InfrastructureError(f"Failed to get pods via SSH: {result['stderr']}")
        
        # Parse JSON output
        try:
            pods_data = json.loads(result["stdout"])
            pod_list = []
            
            for pod_item in pods_data.get("items", []):
                metadata = pod_item.get("metadata", {})
                status = pod_item.get("status", {})
                spec = pod_item.get("spec", {})
                
                conditions = status.get("conditions", [])
                ready_condition = next(
                    (c for c in conditions if c.get("type") == "Ready"),
                    None
                )
                
                container_statuses = status.get("containerStatuses", [])
                restart_count = container_statuses[0].get("restartCount", 0) if container_statuses else 0
                
                pod_info = {
                    "name": metadata.get("name"),
                    "namespace": metadata.get("namespace"),
                    "status": status.get("phase", "Unknown"),
                    "ready": ready_condition.get("status", "Unknown") if ready_condition else "Unknown",
                    "restart_count": restart_count,
                    "node_name": spec.get("nodeName"),
                    "labels": metadata.get("labels", {})
                }
                pod_list.append(pod_info)
            
            self.logger.debug(f"Retrieved {len(pod_list)} pods from namespace '{namespace}' via SSH")
            return pod_list
            
        except json.JSONDecodeError as e:
            raise InfrastructureError(f"Failed to parse kubectl output as JSON: {e}")
    
    def get_deployments(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get deployments in the specified namespace.
        
        Args:
            namespace: Kubernetes namespace (defaults to configured namespace)
            
        Returns:
            List of deployment information dictionaries
        """
        self._ensure_k8s_available()
        
        if not namespace:
            namespace = self.k8s_config.get("namespace", "default")
        
        try:
            deployments = self.k8s_apps_v1.list_namespaced_deployment(namespace=namespace)
            
            deployment_list = []
            for deployment in deployments.items:
                deployment_info = {
                    "name": deployment.metadata.name,
                    "namespace": deployment.metadata.namespace,
                    "replicas": deployment.spec.replicas,
                    "ready_replicas": deployment.status.ready_replicas or 0,
                    "available_replicas": deployment.status.available_replicas or 0,
                    "labels": deployment.metadata.labels
                }
                deployment_list.append(deployment_info)
            
            self.logger.debug(f"Retrieved {len(deployment_list)} deployments from namespace '{namespace}'")
            return deployment_list
            
        except ApiException as e:
            raise InfrastructureError(f"Failed to get deployments: {e}") from e
    
    def get_jobs(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get jobs in the specified namespace.
        
        Args:
            namespace: Kubernetes namespace (defaults to configured namespace)
            
        Returns:
            List of job information dictionaries
        """
        self._ensure_k8s_available()
        
        if not namespace:
            namespace = self.k8s_config.get("namespace", "default")
        
        try:
            jobs = self.k8s_batch_v1.list_namespaced_job(namespace=namespace)
            
            job_list = []
            for job in jobs.items:
                job_info = {
                    "name": job.metadata.name,
                    "namespace": job.metadata.namespace,
                    "status": job.status.conditions[0].type if job.status.conditions else "Unknown",
                    "completions": job.spec.completions,
                    "succeeded": job.status.succeeded or 0,
                    "failed": job.status.failed or 0,
                    "labels": job.metadata.labels
                }
                job_list.append(job_info)
            
            self.logger.debug(f"Retrieved {len(job_list)} jobs from namespace '{namespace}'")
            return job_list
            
        except ApiException as e:
            raise InfrastructureError(f"Failed to get jobs: {e}") from e
    
    def get_pod_logs(self, pod_name: str, namespace: Optional[str] = None, 
                    container: Optional[str] = None, tail_lines: int = 100) -> str:
        """
        Get logs from a pod.
        
        Args:
            pod_name: Name of the pod
            namespace: Kubernetes namespace (defaults to configured namespace)
            container: Container name (optional)
            tail_lines: Number of lines to retrieve
            
        Returns:
            Pod logs as string
        """
        self._ensure_k8s_available()
        
        if not namespace:
            namespace = self.k8s_config.get("namespace", "default")
        
        try:
            logs = self.k8s_core_v1.read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace,
                container=container,
                tail_lines=tail_lines
            )
            
            self.logger.debug(f"Retrieved {len(logs)} characters of logs from pod '{pod_name}'")
            return logs
            
        except ApiException as e:
            raise InfrastructureError(f"Failed to get logs from pod '{pod_name}': {e}") from e
    
    def scale_deployment(self, deployment_name: str, replicas: int, 
                        namespace: Optional[str] = None) -> bool:
        """
        Scale a deployment to the specified number of replicas.
        
        Args:
            deployment_name: Name of the deployment
            replicas: Number of replicas to scale to
            namespace: Kubernetes namespace (defaults to configured namespace)
            
        Returns:
            True if scaling was successful
        """
        self._ensure_k8s_available()
        
        if not namespace:
            namespace = self.k8s_config.get("namespace", "default")
        
        try:
            self.logger.info(f"Scaling deployment '{deployment_name}' to {replicas} replicas...")
            
            # Patch deployment scale
            self.k8s_apps_v1.patch_namespaced_deployment_scale(
                name=deployment_name,
                namespace=namespace,
                body={"spec": {"replicas": replicas}}
            )
            
            # Wait for scaling to complete
            self._wait_for_deployment_scale(deployment_name, replicas, namespace)
            
            self.logger.info(f"Deployment '{deployment_name}' scaled to {replicas} replicas successfully")
            return True
            
        except ApiException as e:
            self.logger.error(f"Failed to scale deployment '{deployment_name}': {e}")
            return False
    
    def delete_pod(self, pod_name: str, namespace: Optional[str] = None) -> bool:
        """
        Delete a pod.
        
        Args:
            pod_name: Name of the pod to delete
            namespace: Kubernetes namespace (defaults to configured namespace)
            
        Returns:
            True if deletion was successful
        """
        self._ensure_k8s_available()
        
        if not namespace:
            namespace = self.k8s_config.get("namespace", "default")
        
        try:
            self.logger.info(f"Deleting pod '{pod_name}'...")
            
            self.k8s_core_v1.delete_namespaced_pod(
                name=pod_name,
                namespace=namespace
            )
            
            # Wait for pod deletion
            self._wait_for_pod_deletion(pod_name, namespace)
            
            self.logger.info(f"Pod '{pod_name}' deleted successfully")
            return True
            
        except ApiException as e:
            self.logger.error(f"Failed to delete pod '{pod_name}': {e}")
            return False
    
    def delete_job(self, job_name: str, namespace: Optional[str] = None) -> bool:
        """
        Delete a job.
        
        Args:
            job_name: Name of the job to delete
            namespace: Kubernetes namespace (defaults to configured namespace)
            
        Returns:
            True if deletion was successful
        """
        self._ensure_k8s_available()
        
        if not namespace:
            namespace = self.k8s_config.get("namespace", "default")
        
        try:
            self.logger.info(f"Deleting job '{job_name}'...")
            
            self.k8s_batch_v1.delete_namespaced_job(
                name=job_name,
                namespace=namespace
            )
            
            self.logger.info(f"Job '{job_name}' deleted successfully")
            return True
            
        except ApiException as e:
            self.logger.error(f"Failed to delete job '{job_name}': {e}")
            return False
    
    def _wait_for_deployment_scale(self, deployment_name: str, expected_replicas: int, 
                                 namespace: str, timeout: int = 120):
        """
        Wait for deployment to reach expected number of replicas.
        
        Args:
            deployment_name: Name of the deployment
            expected_replicas: Expected number of replicas
            namespace: Kubernetes namespace
            timeout: Timeout in seconds
        """
        self.logger.debug(f"Waiting for deployment '{deployment_name}' to reach {expected_replicas} replicas...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                deployment = self.k8s_apps_v1.read_namespaced_deployment(
                    name=deployment_name,
                    namespace=namespace
                )
                
                ready_replicas = deployment.status.ready_replicas or 0
                
                if ready_replicas == expected_replicas:
                    self.logger.debug(f"Deployment '{deployment_name}' reached {expected_replicas} replicas")
                    return
                
                self.logger.debug(f"Deployment '{deployment_name}' has {ready_replicas} ready replicas, waiting...")
                
            except ApiException as e:
                self.logger.warning(f"K8s API error while waiting for deployment scale: {e}")
            
            time.sleep(5)
        
        raise InfrastructureError(
            f"Deployment '{deployment_name}' did not reach {expected_replicas} replicas within {timeout} seconds"
        )
    
    def _wait_for_pod_deletion(self, pod_name: str, namespace: str, timeout: int = 120):
        """
        Wait for pod to be deleted.
        
        Args:
            pod_name: Name of the pod
            namespace: Kubernetes namespace
            timeout: Timeout in seconds
        """
        self.logger.debug(f"Waiting for pod '{pod_name}' to be deleted...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                self.k8s_core_v1.read_namespaced_pod(
                    name=pod_name,
                    namespace=namespace
                )
                self.logger.debug(f"Pod '{pod_name}' still exists, waiting...")
                
            except ApiException as e:
                if e.status == 404:  # Pod not found, meaning it's deleted
                    self.logger.debug(f"Pod '{pod_name}' deleted successfully")
                    return
                else:
                    raise InfrastructureError(f"K8s API error while waiting for pod deletion: {e}") from e
            
            time.sleep(5)
        
        raise InfrastructureError(f"Pod '{pod_name}' was not deleted within {timeout} seconds")
    
    def get_cluster_info(self) -> Dict[str, Any]:
        """
        Get cluster information.
        
        Returns:
            Dictionary containing cluster information
        """
        self._ensure_k8s_available()
        
        # Use SSH fallback if direct API is not available
        if self.use_ssh_fallback:
            return self._get_cluster_info_via_ssh()
        
        try:
            # Get cluster version
            from kubernetes.client import VersionApi
            version_api = VersionApi()
            version = version_api.get_code()
            
            # Get nodes
            nodes = self.k8s_core_v1.list_node()
            
            cluster_info = {
                "version": version.git_version,
                "node_count": len(nodes.items),
                "nodes": []
            }
            
            for node in nodes.items:
                node_info = {
                    "name": node.metadata.name,
                    "status": node.status.conditions[0].type if node.status.conditions else "Unknown",
                    "roles": [label.split("/")[-1] for label in node.metadata.labels.keys() if label.startswith("node-role.kubernetes.io/")],
                    "kubelet_version": node.status.node_info.kubelet_version
                }
                cluster_info["nodes"].append(node_info)
            
            self.logger.debug(f"Retrieved cluster info: {cluster_info['node_count']} nodes")
            return cluster_info
            
        except ApiException as e:
            # If API fails, try SSH fallback
            error_str = str(e).lower()
            if "timeout" in error_str or "connection" in error_str:
                self.logger.warning("Direct API failed, falling back to SSH-based kubectl")
                self._init_ssh_fallback()
                return self._get_cluster_info_via_ssh()
            raise InfrastructureError(f"Failed to get cluster info: {e}") from e
        except Exception as e:
            # Other errors - try SSH fallback
            error_str = str(e).lower()
            if "timeout" in error_str or "connection" in error_str:
                self.logger.warning("Direct API failed, falling back to SSH-based kubectl")
                self._init_ssh_fallback()
                return self._get_cluster_info_via_ssh()
            raise
    
    def _get_cluster_info_via_ssh(self) -> Dict[str, Any]:
        """Get cluster info via SSH kubectl commands."""
        cluster_info = {
            "version": "unknown",
            "node_count": 0,
            "nodes": []
        }
        
        try:
            # Get cluster version (no namespace needed)
            if not self.ssh_manager or not self.ssh_manager.connected:
                if not self._init_ssh_fallback():
                    return cluster_info
            
            version_cmd = f"kubectl version -o json --client"
            result = self.ssh_manager.execute_command(version_cmd, timeout=30)
            
            if result["success"]:
                try:
                    version_data = json.loads(result["stdout"])
                    cluster_info["version"] = version_data.get("clientVersion", {}).get("gitVersion", "unknown")
                except json.JSONDecodeError:
                    # Fallback: parse text output
                    for line in result["stdout"].split("\n"):
                        if "GitVersion" in line:
                            cluster_info["version"] = line.split('"')[3] if '"' in line else "unknown"
                            break
        except Exception as e:
            self.logger.warning(f"Failed to get cluster version via SSH: {e}")
        
        try:
            # Get nodes (no namespace needed)
            if not self.ssh_manager or not self.ssh_manager.connected:
                if not self._init_ssh_fallback():
                    return cluster_info
            
            nodes_cmd = f"kubectl get nodes -o json"
            result = self.ssh_manager.execute_command(nodes_cmd, timeout=30)
            
            if result["success"]:
                try:
                    nodes_data = json.loads(result["stdout"])
                    node_items = nodes_data.get("items", [])
                    cluster_info["node_count"] = len(node_items)
                    
                    for node_item in node_items:
                        metadata = node_item.get("metadata", {})
                        status = node_item.get("status", {})
                        labels = metadata.get("labels", {})
                        
                        conditions = status.get("conditions", [])
                        ready_condition = next(
                            (c for c in conditions if c.get("type") == "Ready"),
                            None
                        )
                        
                        roles = [
                            label.split("/")[-1] 
                            for label in labels.keys() 
                            if label.startswith("node-role.kubernetes.io/")
                        ]
                        
                        node_info = {
                            "name": metadata.get("name"),
                            "status": ready_condition.get("type", "Unknown") if ready_condition else "Unknown",
                            "roles": roles,
                            "kubelet_version": status.get("nodeInfo", {}).get("kubeletVersion", "unknown")
                        }
                        cluster_info["nodes"].append(node_info)
                except json.JSONDecodeError as e:
                    self.logger.warning(f"Failed to parse nodes output as JSON: {e}")
        except Exception as e:
            self.logger.warning(f"Failed to get nodes via SSH: {e}")
        
        self.logger.debug(f"Retrieved cluster info via SSH: {cluster_info['node_count']} nodes")
        return cluster_info
    
    def check_resource_exists(self, resource_type: str, resource_name: str, 
                            namespace: Optional[str] = None) -> bool:
        """
        Check if a resource exists in the cluster.
        
        Args:
            resource_type: Type of resource (pod, deployment, service, etc.)
            resource_name: Name of the resource
            namespace: Kubernetes namespace (defaults to configured namespace)
            
        Returns:
            True if resource exists
        """
        self._ensure_k8s_available()
        
        if not namespace:
            namespace = self.k8s_config.get("namespace", "default")
        
        try:
            if resource_type == "pod":
                self.k8s_core_v1.read_namespaced_pod(name=resource_name, namespace=namespace)
            elif resource_type == "deployment":
                self.k8s_apps_v1.read_namespaced_deployment(name=resource_name, namespace=namespace)
            elif resource_type == "service":
                self.k8s_core_v1.read_namespaced_service(name=resource_name, namespace=namespace)
            elif resource_type == "job":
                self.k8s_batch_v1.read_namespaced_job(name=resource_name, namespace=namespace)
            else:
                raise ValueError(f"Unsupported resource type: {resource_type}")
            
            self.logger.debug(f"Resource '{resource_name}' of type '{resource_type}' exists")
            return True
            
        except ApiException as e:
            if e.status == 404:
                self.logger.debug(f"Resource '{resource_name}' of type '{resource_type}' does not exist")
                return False
            else:
                raise InfrastructureError(f"Error checking resource existence: {e}") from e
