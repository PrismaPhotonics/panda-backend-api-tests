"""
Kubernetes Manager
==================

Kubernetes infrastructure manager for cluster operations and monitoring.
"""

import logging
import time
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
        
        # Kubernetes clients
        self.k8s_apps_v1: Optional[client.AppsV1Api] = None
        self.k8s_core_v1: Optional[client.CoreV1Api] = None
        self.k8s_batch_v1: Optional[client.BatchV1Api] = None
        
        self._load_k8s_config()
        self.logger.info("Kubernetes manager initialized")
    
    def _load_k8s_config(self):
        """Load Kubernetes configuration."""
        try:
            config.load_kube_config()
            self.k8s_apps_v1 = client.AppsV1Api()
            self.k8s_core_v1 = client.CoreV1Api()
            self.k8s_batch_v1 = client.BatchV1Api()
            self.logger.debug("Kubernetes configuration loaded successfully")
        except config.ConfigException as e:
            raise InfrastructureError(f"Failed to load Kubernetes config: {e}") from e
    
    def get_pods(self, namespace: Optional[str] = None, label_selector: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get pods in the specified namespace.
        
        Args:
            namespace: Kubernetes namespace (defaults to configured namespace)
            label_selector: Label selector for filtering pods
            
        Returns:
            List of pod information dictionaries
        """
        if not namespace:
            namespace = self.k8s_config.get("namespace", "default")
        
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
            raise InfrastructureError(f"Failed to get pods: {e}") from e
    
    def get_deployments(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get deployments in the specified namespace.
        
        Args:
            namespace: Kubernetes namespace (defaults to configured namespace)
            
        Returns:
            List of deployment information dictionaries
        """
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
        try:
            # Get cluster version
            version = self.k8s_core_v1.get_code()
            
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
            raise InfrastructureError(f"Failed to get cluster info: {e}") from e
    
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
