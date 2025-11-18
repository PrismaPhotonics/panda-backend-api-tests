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
        
        Tries SSH-based kubectl first (faster and more reliable), 
        falls back to direct API access if SSH is not available.
        """
        # Try SSH fallback first (preferred method - faster and more reliable)
        self.logger.info("Attempting SSH-based kubectl connection first...")
        if self._init_ssh_fallback():
            self.logger.info("Using SSH-based kubectl for Kubernetes operations")
            return
        
        # SSH fallback failed - try direct API access as fallback
        self.logger.info("SSH fallback not available, trying direct Kubernetes API access...")
        try:
            # Try to load kubeconfig and create API clients
            config.load_kube_config()
            self.k8s_apps_v1 = client.AppsV1Api()
            self.k8s_core_v1 = client.CoreV1Api()
            self.k8s_batch_v1 = client.BatchV1Api()
            self.logger.debug("Kubernetes configuration loaded successfully")
            
            # Test connection (quick check with very short timeout)
            try:
                # Use very short timeout to fail fast
                self.k8s_core_v1.list_node(timeout_seconds=2)
                self.logger.debug("Direct Kubernetes API connection verified")
                self.logger.info("Using direct Kubernetes API access")
            except Exception as e:
                # Connection failed - likely timeout or network issue
                error_str = str(e).lower()
                if "timeout" in error_str or "connection" in error_str or "timed out" in error_str:
                    self.logger.warning("Direct Kubernetes API not accessible (timeout)")
                    # Clear the API clients since they won't work
                    self.k8s_apps_v1 = None
                    self.k8s_core_v1 = None
                    self.k8s_batch_v1 = None
                    raise InfrastructureError(
                        "Neither SSH fallback nor direct Kubernetes API access is available. "
                        "Please ensure SSH access or kubeconfig is configured."
                    )
                else:
                    raise
                    
        except config.ConfigException as e:
            # No kubeconfig available
            self.logger.warning(f"Kubernetes config not available: {e}")
            raise InfrastructureError(
                "Neither SSH fallback nor direct Kubernetes API access is available. "
                "Please ensure SSH access or kubeconfig is configured."
            )
        except InfrastructureError:
            # Re-raise infrastructure errors
            raise
        except Exception as e:
            # Other errors
            error_str = str(e).lower()
            if "timeout" in error_str or "connection" in error_str or "timed out" in error_str:
                self.logger.warning(f"Direct Kubernetes API connection failed: {e}")
                raise InfrastructureError(
                    "Neither SSH fallback nor direct Kubernetes API access is available. "
                    "Please ensure SSH access or kubeconfig is configured."
                )
            else:
                # Unknown error
                self.logger.warning(f"Unexpected error loading Kubernetes config: {e}")
                raise InfrastructureError(
                    f"Failed to initialize Kubernetes connection: {e}. "
                    "Please ensure SSH access or kubeconfig is configured."
                )
    
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
        
        # Use SSH fallback if direct API is not available
        if self.use_ssh_fallback:
            return self._get_deployments_via_ssh(namespace)
        
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
            # If API fails, try SSH fallback
            error_str = str(e).lower()
            if "timeout" in error_str or "connection" in error_str:
                self.logger.warning("Direct API failed, falling back to SSH-based kubectl")
                self._init_ssh_fallback()
                return self._get_deployments_via_ssh(namespace)
            raise InfrastructureError(f"Failed to get deployments: {e}") from e
        except Exception as e:
            # Other errors - try SSH fallback
            error_str = str(e).lower()
            if "timeout" in error_str or "connection" in error_str:
                self.logger.warning("Direct API failed, falling back to SSH-based kubectl")
                self._init_ssh_fallback()
                return self._get_deployments_via_ssh(namespace)
            raise InfrastructureError(f"Failed to get deployments: {e}") from e
    
    def _get_deployments_via_ssh(self, namespace: Optional[str]) -> List[Dict[str, Any]]:
        """Get deployments via SSH kubectl command."""
        if not namespace:
            namespace = self.k8s_config.get("namespace", "default")
        
        # Build kubectl command
        cmd = f"get deployments -o json"
        
        result = self._execute_kubectl_via_ssh(cmd, timeout=30)
        
        if not result["success"]:
            raise InfrastructureError(f"Failed to get deployments via SSH: {result['stderr']}")
        
        # Parse JSON output
        try:
            deployments_data = json.loads(result["stdout"])
            deployment_list = []
            
            for deployment_item in deployments_data.get("items", []):
                metadata = deployment_item.get("metadata", {})
                spec = deployment_item.get("spec", {})
                status = deployment_item.get("status", {})
                
                deployment_info = {
                    "name": metadata.get("name"),
                    "namespace": metadata.get("namespace"),
                    "replicas": spec.get("replicas", 0),
                    "ready_replicas": status.get("readyReplicas", 0),
                    "available_replicas": status.get("availableReplicas", 0),
                    "labels": metadata.get("labels", {})
                }
                deployment_list.append(deployment_info)
            
            self.logger.debug(f"Retrieved {len(deployment_list)} deployments from namespace '{namespace}' via SSH")
            return deployment_list
            
        except json.JSONDecodeError as e:
            raise InfrastructureError(f"Failed to parse kubectl output as JSON: {e}")
    
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
        
        # Use SSH fallback if direct API is not available
        if self.use_ssh_fallback:
            return self._get_jobs_via_ssh(namespace)
        
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
            # If API fails, try SSH fallback
            error_str = str(e).lower()
            if "timeout" in error_str or "connection" in error_str:
                self.logger.warning("Direct API failed, falling back to SSH-based kubectl")
                self._init_ssh_fallback()
                return self._get_jobs_via_ssh(namespace)
            raise InfrastructureError(f"Failed to get jobs: {e}") from e
    
    def _get_jobs_via_ssh(self, namespace: Optional[str]) -> List[Dict[str, Any]]:
        """Get jobs via SSH kubectl command."""
        if not namespace:
            namespace = self.k8s_config.get("namespace", "default")
        
        # Build kubectl command
        cmd = f"get jobs -o json"
        
        result = self._execute_kubectl_via_ssh(cmd, timeout=30)
        
        if not result["success"]:
            raise InfrastructureError(f"Failed to get jobs via SSH: {result['stderr']}")
        
        # Parse JSON output
        try:
            jobs_data = json.loads(result["stdout"])
            job_list = []
            
            for job_item in jobs_data.get("items", []):
                metadata = job_item.get("metadata", {})
                spec = job_item.get("spec", {})
                status = job_item.get("status", {})
                
                conditions = status.get("conditions", [])
                status_type = conditions[0].get("type", "Unknown") if conditions else "Unknown"
                
                job_info = {
                    "name": metadata.get("name"),
                    "namespace": metadata.get("namespace"),
                    "status": status_type,
                    "completions": spec.get("completions", 1),
                    "succeeded": status.get("succeeded", 0),
                    "failed": status.get("failed", 0),
                    "labels": metadata.get("labels", {})
                }
                job_list.append(job_info)
            
            self.logger.debug(f"Retrieved {len(job_list)} jobs from namespace '{namespace}' via SSH")
            return job_list
            
        except json.JSONDecodeError as e:
            raise InfrastructureError(f"Failed to parse kubectl output as JSON: {e}") from e
    
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
        if not namespace:
            namespace = self.k8s_config.get("namespace", "default")
        
        # Use SSH fallback if direct API is not available
        if self.use_ssh_fallback or self.k8s_core_v1 is None:
            if not self.ssh_manager:
                self._init_ssh_fallback()
            
            if self.ssh_manager:
                # Use kubectl via SSH
                container_arg = f" -c {container}" if container else ""
                cmd = f"kubectl logs {pod_name} -n {namespace}{container_arg} --tail={tail_lines}"
                result = self.ssh_manager.execute_command(cmd, timeout=60)
                if result["success"]:
                    return result["stdout"]
                else:
                    raise InfrastructureError(f"Failed to get logs via SSH: {result['stderr']}")
            else:
                raise InfrastructureError("SSH fallback not available for log retrieval")
        
        # Direct API access
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
        
        # Use SSH fallback if direct API is not available
        if self.use_ssh_fallback:
            return self._scale_deployment_via_ssh(deployment_name, replicas, namespace)
        
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
            # If API fails, try SSH fallback
            error_str = str(e).lower()
            if "timeout" in error_str or "connection" in error_str:
                self.logger.warning("Direct API failed, falling back to SSH-based kubectl")
                if self._init_ssh_fallback():
                    return self._scale_deployment_via_ssh(deployment_name, replicas, namespace)
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
        
        # Use SSH fallback if direct API is not available
        if self.use_ssh_fallback:
            return self._delete_pod_via_ssh(pod_name, namespace)
        
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
            # If API fails, try SSH fallback
            error_str = str(e).lower()
            if "timeout" in error_str or "connection" in error_str:
                self.logger.warning("Direct API failed, falling back to SSH-based kubectl")
                if self._init_ssh_fallback():
                    return self._delete_pod_via_ssh(pod_name, namespace)
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
        
        # Use SSH fallback if direct API is not available
        if self.use_ssh_fallback:
            return self._delete_job_via_ssh(job_name, namespace)
        
        try:
            self.logger.info(f"Deleting job '{job_name}'...")
            
            self.k8s_batch_v1.delete_namespaced_job(
                name=job_name,
                namespace=namespace
            )
            
            self.logger.info(f"Job '{job_name}' deleted successfully")
            return True
            
        except ApiException as e:
            # If API fails, try SSH fallback
            error_str = str(e).lower()
            if "timeout" in error_str or "connection" in error_str:
                self.logger.warning("Direct API failed, falling back to SSH-based kubectl")
                self._init_ssh_fallback()
                return self._delete_job_via_ssh(job_name, namespace)
            self.logger.error(f"Failed to delete job '{job_name}': {e}")
            return False
    
    def _delete_job_via_ssh(self, job_name: str, namespace: str) -> bool:
        """Delete job via SSH kubectl command."""
        try:
            self.logger.info(f"Deleting job '{job_name}' via SSH...")
            
            cmd = f"delete job {job_name}"
            result = self._execute_kubectl_via_ssh(cmd, timeout=30)
            
            if result["success"]:
                self.logger.info(f"Job '{job_name}' deleted successfully via SSH")
                return True
            else:
                self.logger.error(f"Failed to delete job '{job_name}' via SSH: {result['stderr']}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting job '{job_name}' via SSH: {e}")
            return False
    
    def _delete_pod_via_ssh(self, pod_name: str, namespace: str) -> bool:
        """Delete pod via SSH kubectl command."""
        try:
            self.logger.info(f"Deleting pod '{pod_name}' via SSH...")
            
            cmd = f"delete pod {pod_name}"
            result = self._execute_kubectl_via_ssh(cmd, timeout=30)
            
            if result["success"]:
                # Wait for pod deletion
                self._wait_for_pod_deletion(pod_name, namespace)
                self.logger.info(f"Pod '{pod_name}' deleted successfully via SSH")
                return True
            else:
                self.logger.error(f"Failed to delete pod '{pod_name}' via SSH: {result['stderr']}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting pod '{pod_name}' via SSH: {e}")
            return False
    
    def _scale_deployment_via_ssh(self, deployment_name: str, replicas: int, namespace: str) -> bool:
        """Scale deployment via SSH kubectl command."""
        try:
            self.logger.info(f"Scaling deployment '{deployment_name}' to {replicas} replicas via SSH...")
            
            cmd = f"scale deployment {deployment_name} --replicas={replicas}"
            result = self._execute_kubectl_via_ssh(cmd, timeout=30)
            
            if result["success"]:
                # Wait for scaling to complete
                self._wait_for_deployment_scale(deployment_name, replicas, namespace)
                self.logger.info(f"Deployment '{deployment_name}' scaled to {replicas} replicas successfully via SSH")
                return True
            else:
                self.logger.error(f"Failed to scale deployment '{deployment_name}' via SSH: {result['stderr']}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error scaling deployment '{deployment_name}' via SSH: {e}")
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
                if self.use_ssh_fallback:
                    # Use kubectl via SSH to check deployment status
                    cmd = f"get deployment {deployment_name} -o json"
                    result = self._execute_kubectl_via_ssh(cmd, timeout=10)
                    
                    if result["success"]:
                        deployment_data = json.loads(result["stdout"])
                        status = deployment_data.get("status", {})
                        ready_replicas = status.get("readyReplicas", 0)
                        
                        if ready_replicas == expected_replicas:
                            self.logger.debug(f"Deployment '{deployment_name}' reached {expected_replicas} replicas")
                            return
                        
                        self.logger.debug(f"Deployment '{deployment_name}' has {ready_replicas} ready replicas, waiting...")
                    else:
                        self.logger.warning(f"Failed to get deployment status via SSH: {result['stderr']}")
                else:
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
            except Exception as e:
                self.logger.warning(f"Error while waiting for deployment scale: {e}")
            
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
                if self.use_ssh_fallback:
                    # Use kubectl via SSH to check if pod exists
                    cmd = f"get pod {pod_name}"
                    result = self._execute_kubectl_via_ssh(cmd, timeout=10)
                    
                    if not result["success"]:
                        # Pod doesn't exist anymore (deleted)
                        self.logger.debug(f"Pod '{pod_name}' deleted successfully")
                        return
                    
                    self.logger.debug(f"Pod '{pod_name}' still exists, waiting...")
                else:
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
    
    def get_pod_by_name(self, pod_name: str, namespace: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get pod by exact name.
        
        Args:
            pod_name: Name of the pod
            namespace: Kubernetes namespace (defaults to configured namespace)
            
        Returns:
            Pod information dictionary or None if not found
        """
        self._ensure_k8s_available()
        
        if not namespace:
            namespace = self.k8s_config.get("namespace", "default")
        
        try:
            if self.use_ssh_fallback:
                return self._get_pod_by_name_via_ssh(pod_name, namespace)
            
            pod = self.k8s_core_v1.read_namespaced_pod(name=pod_name, namespace=namespace)
            
            pod_info = {
                "name": pod.metadata.name,
                "namespace": pod.metadata.namespace,
                "status": pod.status.phase,
                "ready": "True" if pod.status.conditions and any(
                    c.type == "Ready" and c.status == "True" for c in pod.status.conditions
                ) else "False",
                "restart_count": pod.status.container_statuses[0].restart_count if pod.status.container_statuses else 0,
                "node_name": pod.spec.node_name,
                "labels": pod.metadata.labels,
                "creation_timestamp": pod.metadata.creation_timestamp.isoformat() if pod.metadata.creation_timestamp else None
            }
            
            self.logger.debug(f"Retrieved pod '{pod_name}' from namespace '{namespace}'")
            return pod_info
            
        except ApiException as e:
            if e.status == 404:
                self.logger.debug(f"Pod '{pod_name}' not found in namespace '{namespace}'")
                return None
            else:
                raise InfrastructureError(f"Failed to get pod '{pod_name}': {e}") from e
    
    def _get_pod_by_name_via_ssh(self, pod_name: str, namespace: str) -> Optional[Dict[str, Any]]:
        """Get pod by name via SSH kubectl command."""
        cmd = f"get pod {pod_name} -n {namespace} -o json"
        result = self._execute_kubectl_via_ssh(cmd, timeout=30)
        
        if not result["success"]:
            if "NotFound" in result.get("stderr", ""):
                return None
            raise InfrastructureError(f"Failed to get pod via SSH: {result['stderr']}")
        
        try:
            pod_data = json.loads(result["stdout"])
            metadata = pod_data.get("metadata", {})
            spec = pod_data.get("spec", {})
            status = pod_data.get("status", {})
            conditions = status.get("conditions", [])
            
            ready_condition = next((c for c in conditions if c.get("type") == "Ready"), None)
            ready = "True" if ready_condition and ready_condition.get("status") == "True" else "False"
            
            container_statuses = status.get("containerStatuses", [])
            restart_count = container_statuses[0].get("restartCount", 0) if container_statuses else 0
            
            pod_info = {
                "name": metadata.get("name"),
                "namespace": metadata.get("namespace"),
                "status": status.get("phase", "Unknown"),
                "ready": ready,
                "restart_count": restart_count,
                "node_name": spec.get("nodeName"),
                "labels": metadata.get("labels", {}),
                "creation_timestamp": metadata.get("creationTimestamp")
            }
            
            return pod_info
            
        except json.JSONDecodeError as e:
            raise InfrastructureError(f"Failed to parse kubectl output as JSON: {e}") from e
    
    def get_pod_status(self, pod_name: str, namespace: Optional[str] = None) -> str:
        """
        Get current pod status (phase).
        
        Args:
            pod_name: Name of the pod
            namespace: Kubernetes namespace (defaults to configured namespace)
            
        Returns:
            Pod status phase (Running, Pending, Failed, etc.)
        """
        pod_info = self.get_pod_by_name(pod_name, namespace)
        if pod_info:
            return pod_info.get("status", "Unknown")
        return "NotFound"
    
    def wait_for_pod_ready(self, pod_name: str, namespace: Optional[str] = None, timeout: int = 120) -> bool:
        """
        Wait for pod to become ready.
        
        Args:
            pod_name: Name of the pod
            namespace: Kubernetes namespace (defaults to configured namespace)
            timeout: Timeout in seconds
            
        Returns:
            True if pod became ready, False if timeout
        """
        if not namespace:
            namespace = self.k8s_config.get("namespace", "default")
        
        self.logger.debug(f"Waiting for pod '{pod_name}' to be ready (timeout: {timeout}s)...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            pod_info = self.get_pod_by_name(pod_name, namespace)
            
            if pod_info:
                status = pod_info.get("status", "Unknown")
                ready = pod_info.get("ready", "False")
                
                if status == "Running" and ready == "True":
                    self.logger.debug(f"Pod '{pod_name}' is ready")
                    return True
                
                if status in ["Failed", "Unknown"]:
                    self.logger.warning(f"Pod '{pod_name}' entered unexpected state: {status}")
                    return False
            
            time.sleep(2)
        
        self.logger.warning(f"Pod '{pod_name}' did not become ready within {timeout} seconds")
        return False
    
    def restart_pod(self, pod_name: str, namespace: Optional[str] = None) -> bool:
        """
        Restart a pod by deleting it (Kubernetes will recreate it automatically).
        
        Args:
            pod_name: Name of the pod to restart
            namespace: Kubernetes namespace (defaults to configured namespace)
            
        Returns:
            True if restart was successful
        """
        self.logger.info(f"Restarting pod '{pod_name}' by deletion...")
        return self.delete_pod(pod_name, namespace)
    
    def scale_statefulset(self, statefulset_name: str, replicas: int, 
                         namespace: Optional[str] = None) -> bool:
        """
        Scale a StatefulSet to the specified number of replicas.
        
        Args:
            statefulset_name: Name of the StatefulSet
            replicas: Number of replicas to scale to
            namespace: Kubernetes namespace (defaults to configured namespace)
            
        Returns:
            True if scaling was successful
        """
        self._ensure_k8s_available()
        
        if not namespace:
            namespace = self.k8s_config.get("namespace", "default")
        
        try:
            self.logger.info(f"Scaling StatefulSet '{statefulset_name}' to {replicas} replicas...")
            
            # Patch StatefulSet scale
            self.k8s_apps_v1.patch_namespaced_stateful_set_scale(
                name=statefulset_name,
                namespace=namespace,
                body={"spec": {"replicas": replicas}}
            )
            
            # Wait for scaling to complete
            self._wait_for_statefulset_scale(statefulset_name, replicas, namespace)
            
            self.logger.info(f"StatefulSet '{statefulset_name}' scaled to {replicas} replicas successfully")
            return True
            
        except ApiException as e:
            self.logger.error(f"Failed to scale StatefulSet '{statefulset_name}': {e}")
            return False
    
    def _wait_for_statefulset_scale(self, statefulset_name: str, expected_replicas: int, 
                                    namespace: str, timeout: int = 120):
        """
        Wait for StatefulSet to reach expected number of replicas.
        
        Args:
            statefulset_name: Name of the StatefulSet
            expected_replicas: Expected number of replicas
            namespace: Kubernetes namespace
            timeout: Timeout in seconds
        """
        self.logger.debug(f"Waiting for StatefulSet '{statefulset_name}' to reach {expected_replicas} replicas...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                statefulset = self.k8s_apps_v1.read_namespaced_stateful_set(
                    name=statefulset_name,
                    namespace=namespace
                )
                
                ready_replicas = statefulset.status.ready_replicas or 0
                
                if ready_replicas == expected_replicas:
                    self.logger.debug(f"StatefulSet '{statefulset_name}' reached {expected_replicas} replicas")
                    return
                
                self.logger.debug(f"StatefulSet '{statefulset_name}' has {ready_replicas} ready replicas, waiting...")
                
            except ApiException as e:
                self.logger.warning(f"K8s API error while waiting for StatefulSet scale: {e}")
            
            time.sleep(5)
        
        raise InfrastructureError(
            f"StatefulSet '{statefulset_name}' did not reach {expected_replicas} replicas within {timeout} seconds"
        )
    
    def get_ingress(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get Ingress resources in the specified namespace.
        
        Args:
            namespace: Kubernetes namespace (defaults to configured namespace)
            
        Returns:
            List of Ingress information dictionaries
        """
        self._ensure_k8s_available()
        
        if not namespace:
            namespace = self.k8s_config.get("namespace", "panda")
        
        # Use SSH fallback if direct API is not available
        if self.use_ssh_fallback:
            return self._get_ingress_via_ssh(namespace)
        
        try:
            from kubernetes.client import NetworkingV1Api
            networking_v1 = NetworkingV1Api()
            
            ingress_list = networking_v1.list_namespaced_ingress(namespace=namespace)
            
            ingress_info_list = []
            for ingress in ingress_list.items:
                rules = []
                for rule in ingress.spec.rules or []:
                    paths = []
                    if rule.http:
                        for path in rule.http.paths or []:
                            paths.append({
                                "path": path.path,
                                "path_type": path.path_type,
                                "service_name": path.backend.service.name if path.backend.service else None,
                                "service_port": path.backend.service.port.number if path.backend.service and path.backend.service.port else None
                            })
                    rules.append({
                        "host": rule.host,
                        "paths": paths
                    })
                
                ingress_info = {
                    "name": ingress.metadata.name,
                    "namespace": ingress.metadata.namespace,
                    "rules": rules,
                    "labels": ingress.metadata.labels or {}
                }
                ingress_info_list.append(ingress_info)
            
            self.logger.debug(f"Retrieved {len(ingress_info_list)} Ingress resources from namespace '{namespace}'")
            return ingress_info_list
            
        except ApiException as e:
            error_str = str(e).lower()
            if "timeout" in error_str or "connection" in error_str:
                self.logger.warning("Direct API failed, falling back to SSH-based kubectl")
                self._init_ssh_fallback()
                return self._get_ingress_via_ssh(namespace)
            raise InfrastructureError(f"Failed to get Ingress resources: {e}") from e
    
    def _get_ingress_via_ssh(self, namespace: str) -> List[Dict[str, Any]]:
        """Get Ingress resources via SSH kubectl command."""
        cmd = f"get ingress -n {namespace} -o json"
        result = self._execute_kubectl_via_ssh(cmd, timeout=30)
        
        if not result["success"]:
            raise InfrastructureError(f"Failed to get Ingress via SSH: {result['stderr']}")
        
        try:
            ingress_data = json.loads(result["stdout"])
            ingress_list = []
            
            for item in ingress_data.get("items", []):
                metadata = item.get("metadata", {})
                spec = item.get("spec", {})
                
                rules = []
                for rule in spec.get("rules", []):
                    paths = []
                    http = rule.get("http", {})
                    for path in http.get("paths", []):
                        backend = path.get("backend", {})
                        service = backend.get("service", {})
                        paths.append({
                            "path": path.get("path"),
                            "path_type": path.get("pathType"),
                            "service_name": service.get("name"),
                            "service_port": service.get("port", {}).get("number")
                        })
                    rules.append({
                        "host": rule.get("host"),
                        "paths": paths
                    })
                
                ingress_info = {
                    "name": metadata.get("name"),
                    "namespace": metadata.get("namespace"),
                    "rules": rules,
                    "labels": metadata.get("labels", {})
                }
                ingress_list.append(ingress_info)
            
            return ingress_list
        except json.JSONDecodeError as e:
            raise InfrastructureError(f"Failed to parse Ingress JSON: {e}") from e
    
    def get_services(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get Services in the specified namespace.
        
        Args:
            namespace: Kubernetes namespace (defaults to configured namespace)
            
        Returns:
            List of Service information dictionaries
        """
        self._ensure_k8s_available()
        
        if not namespace:
            namespace = self.k8s_config.get("namespace", "panda")
        
        # Use SSH fallback if direct API is not available
        if self.use_ssh_fallback:
            return self._get_services_via_ssh(namespace)
        
        try:
            services = self.k8s_core_v1.list_namespaced_service(namespace=namespace)
            
            service_list = []
            for svc in services.items:
                ports = []
                for port in svc.spec.ports or []:
                    ports.append({
                        "name": port.name,
                        "port": port.port,
                        "target_port": port.target_port if isinstance(port.target_port, int) else str(port.target_port),
                        "protocol": port.protocol
                    })
                
                service_info = {
                    "name": svc.metadata.name,
                    "namespace": svc.metadata.namespace,
                    "type": svc.spec.type,
                    "cluster_ip": svc.spec.cluster_ip,
                    "ports": ports,
                    "labels": svc.metadata.labels or {}
                }
                service_list.append(service_info)
            
            self.logger.debug(f"Retrieved {len(service_list)} Services from namespace '{namespace}'")
            return service_list
            
        except ApiException as e:
            error_str = str(e).lower()
            if "timeout" in error_str or "connection" in error_str:
                self.logger.warning("Direct API failed, falling back to SSH-based kubectl")
                self._init_ssh_fallback()
                return self._get_services_via_ssh(namespace)
            raise InfrastructureError(f"Failed to get Services: {e}") from e
    
    def _get_services_via_ssh(self, namespace: str) -> List[Dict[str, Any]]:
        """Get Services via SSH kubectl command."""
        cmd = f"get svc -n {namespace} -o json"
        result = self._execute_kubectl_via_ssh(cmd, timeout=30)
        
        if not result["success"]:
            raise InfrastructureError(f"Failed to get Services via SSH: {result['stderr']}")
        
        try:
            svc_data = json.loads(result["stdout"])
            service_list = []
            
            for item in svc_data.get("items", []):
                metadata = item.get("metadata", {})
                spec = item.get("spec", {})
                
                ports = []
                for port in spec.get("ports", []):
                    ports.append({
                        "name": port.get("name"),
                        "port": port.get("port"),
                        "target_port": port.get("targetPort"),
                        "protocol": port.get("protocol", "TCP")
                    })
                
                service_info = {
                    "name": metadata.get("name"),
                    "namespace": metadata.get("namespace"),
                    "type": spec.get("type", "ClusterIP"),
                    "cluster_ip": spec.get("clusterIP"),
                    "ports": ports,
                    "labels": metadata.get("labels", {})
                }
                service_list.append(service_info)
            
            return service_list
        except json.JSONDecodeError as e:
            raise InfrastructureError(f"Failed to parse Services JSON: {e}") from e
    
    def get_endpoints(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get Endpoints in the specified namespace.
        
        Args:
            namespace: Kubernetes namespace (defaults to configured namespace)
            
        Returns:
            List of Endpoint information dictionaries
        """
        self._ensure_k8s_available()
        
        if not namespace:
            namespace = self.k8s_config.get("namespace", "panda")
        
        # Use SSH fallback if direct API is not available
        if self.use_ssh_fallback:
            return self._get_endpoints_via_ssh(namespace)
        
        try:
            endpoints = self.k8s_core_v1.list_namespaced_endpoints(namespace=namespace)
            
            endpoint_list = []
            for ep in endpoints.items:
                subsets = []
                for subset in ep.subsets or []:
                    addresses = []
                    for addr in subset.addresses or []:
                        addresses.append({
                            "ip": addr.ip,
                            "hostname": addr.hostname,
                            "target_ref": {
                                "kind": addr.target_ref.kind if addr.target_ref else None,
                                "name": addr.target_ref.name if addr.target_ref else None,
                                "namespace": addr.target_ref.namespace if addr.target_ref else None
                            } if addr.target_ref else None
                        })
                    
                    ports = []
                    for port in subset.ports or []:
                        ports.append({
                            "name": port.name,
                            "port": port.port,
                            "protocol": port.protocol
                        })
                    
                    subsets.append({
                        "addresses": addresses,
                        "ports": ports
                    })
                
                endpoint_info = {
                    "name": ep.metadata.name,
                    "namespace": ep.metadata.namespace,
                    "subsets": subsets,
                    "labels": ep.metadata.labels or {}
                }
                endpoint_list.append(endpoint_info)
            
            self.logger.debug(f"Retrieved {len(endpoint_list)} Endpoints from namespace '{namespace}'")
            return endpoint_list
            
        except ApiException as e:
            error_str = str(e).lower()
            if "timeout" in error_str or "connection" in error_str:
                self.logger.warning("Direct API failed, falling back to SSH-based kubectl")
                self._init_ssh_fallback()
                return self._get_endpoints_via_ssh(namespace)
            raise InfrastructureError(f"Failed to get Endpoints: {e}") from e
    
    def _get_endpoints_via_ssh(self, namespace: str) -> List[Dict[str, Any]]:
        """Get Endpoints via SSH kubectl command."""
        cmd = f"get endpoints -n {namespace} -o json"
        result = self._execute_kubectl_via_ssh(cmd, timeout=30)
        
        if not result["success"]:
            raise InfrastructureError(f"Failed to get Endpoints via SSH: {result['stderr']}")
        
        try:
            ep_data = json.loads(result["stdout"])
            endpoint_list = []
            
            for item in ep_data.get("items", []):
                metadata = item.get("metadata", {})
                subsets_data = item.get("subsets", [])
                
                subsets = []
                for subset in subsets_data:
                    addresses = []
                    for addr in subset.get("addresses", []):
                        target_ref = addr.get("targetRef", {})
                        addresses.append({
                            "ip": addr.get("ip"),
                            "hostname": addr.get("hostname"),
                            "target_ref": {
                                "kind": target_ref.get("kind"),
                                "name": target_ref.get("name"),
                                "namespace": target_ref.get("namespace")
                            } if target_ref else None
                        })
                    
                    ports = []
                    for port in subset.get("ports", []):
                        ports.append({
                            "name": port.get("name"),
                            "port": port.get("port"),
                            "protocol": port.get("protocol", "TCP")
                        })
                    
                    subsets.append({
                        "addresses": addresses,
                        "ports": ports
                    })
                
                endpoint_info = {
                    "name": metadata.get("name"),
                    "namespace": metadata.get("namespace"),
                    "subsets": subsets,
                    "labels": metadata.get("labels", {})
                }
                endpoint_list.append(endpoint_info)
            
            return endpoint_list
        except json.JSONDecodeError as e:
            raise InfrastructureError(f"Failed to parse Endpoints JSON: {e}") from e
