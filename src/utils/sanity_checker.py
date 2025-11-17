"""
Sanity Check Module for Test Execution
======================================

This module provides pre-test sanity checks to ensure all infrastructure
components are available and responsive before running tests.

Usage:
    The sanity check runs automatically before test execution via pytest hooks.
    To skip sanity checks, use: pytest --skip-sanity-check
"""

import logging
import time
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SanityCheckResult:
    """Result of a single sanity check."""
    component: str
    success: bool
    message: str
    duration_ms: float
    error: Optional[Exception] = None


class SanityChecker:
    """
    Sanity checker for infrastructure components.
    
    Performs quick connectivity and health checks before test execution.
    """
    
    def __init__(self, config_manager):
        """
        Initialize sanity checker.
        
        Args:
            config_manager: ConfigManager instance
        """
        self.config_manager = config_manager
        self.results: List[SanityCheckResult] = []
        self.environment = config_manager.environment
        
    def check_focus_server(self) -> SanityCheckResult:
        """
        Check Focus Server API connectivity and health.
        
        Returns:
            SanityCheckResult
        """
        component = "Focus Server API"
        start_time = time.time()
        
        try:
            from src.apis.focus_server_api import FocusServerAPI
            
            api_client = FocusServerAPI(self.config_manager)
            
            # Use validate_connection method for health check
            try:
                is_valid = api_client.validate_connection()
                duration_ms = (time.time() - start_time) * 1000
                
                if is_valid:
                    return SanityCheckResult(
                        component=component,
                        success=True,
                        message="Focus Server is responding and accessible",
                        duration_ms=duration_ms
                    )
                else:
                    return SanityCheckResult(
                        component=component,
                        success=False,
                        message="Focus Server connection validation failed",
                        duration_ms=duration_ms
                    )
                    
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                return SanityCheckResult(
                    component=component,
                    success=False,
                    message=f"Focus Server API call failed: {str(e)}",
                    duration_ms=duration_ms,
                    error=e
                )
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return SanityCheckResult(
                component=component,
                success=False,
                message=f"Failed to initialize Focus Server API: {str(e)}",
                duration_ms=duration_ms,
                error=e
            )
    
    def check_mongodb(self) -> SanityCheckResult:
        """
        Check MongoDB connectivity.
        
        Returns:
            SanityCheckResult
        """
        component = "MongoDB"
        start_time = time.time()
        
        try:
            from src.infrastructure.mongodb_manager import MongoDBManager
            
            manager = MongoDBManager(self.config_manager)
            
            # Try to connect
            if manager.connect():
                # Try a simple ping
                try:
                    manager.client.admin.command('ping')
                    duration_ms = (time.time() - start_time) * 1000
                    manager.disconnect()
                    
                    return SanityCheckResult(
                        component=component,
                        success=True,
                        message="MongoDB is reachable and responding",
                        duration_ms=duration_ms
                    )
                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000
                    manager.disconnect()
                    return SanityCheckResult(
                        component=component,
                        success=False,
                        message=f"MongoDB ping failed: {str(e)}",
                        duration_ms=duration_ms,
                        error=e
                    )
            else:
                duration_ms = (time.time() - start_time) * 1000
                return SanityCheckResult(
                    component=component,
                    success=False,
                    message="MongoDB connection failed",
                    duration_ms=duration_ms
                )
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return SanityCheckResult(
                component=component,
                success=False,
                message=f"Failed to initialize MongoDB manager: {str(e)}",
                duration_ms=duration_ms,
                error=e
            )
    
    def check_kubernetes(self) -> SanityCheckResult:
        """
        Check Kubernetes cluster connectivity.
        
        Returns:
            SanityCheckResult
        """
        component = "Kubernetes"
        start_time = time.time()
        
        try:
            from src.infrastructure.kubernetes_manager import KubernetesManager
            
            manager = KubernetesManager(self.config_manager)
            
            # Try to get cluster info
            try:
                cluster_info = manager.get_cluster_info()
                node_count = cluster_info.get('node_count', 0)
                duration_ms = (time.time() - start_time) * 1000
                
                if node_count > 0:
                    return SanityCheckResult(
                        component=component,
                        success=True,
                        message=f"Kubernetes cluster is reachable ({node_count} nodes)",
                        duration_ms=duration_ms
                    )
                else:
                    return SanityCheckResult(
                        component=component,
                        success=False,
                        message="Kubernetes cluster accessible but no nodes found",
                        duration_ms=duration_ms
                    )
                    
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                return SanityCheckResult(
                    component=component,
                    success=False,
                    message=f"Kubernetes API call failed: {str(e)}",
                    duration_ms=duration_ms,
                    error=e
                )
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return SanityCheckResult(
                component=component,
                success=False,
                message=f"Failed to initialize Kubernetes manager: {str(e)}",
                duration_ms=duration_ms,
                error=e
            )
    
    def check_ssh(self) -> SanityCheckResult:
        """
        Check SSH connectivity.
        
        Returns:
            SanityCheckResult
        """
        component = "SSH"
        start_time = time.time()
        
        try:
            from src.infrastructure.ssh_manager import SSHManager
            
            manager = SSHManager(self.config_manager)
            
            # Try to connect
            if manager.connect():
                try:
                    # Try a simple command
                    result = manager.execute_command("echo 'test'")
                    duration_ms = (time.time() - start_time) * 1000
                    manager.disconnect()
                    
                    # execute_command returns a dict with 'exit_code' key
                    exit_code = result.get('exit_code', -1) if isinstance(result, dict) else -1
                    
                    if result and exit_code == 0:
                        return SanityCheckResult(
                            component=component,
                            success=True,
                            message="SSH connection successful",
                            duration_ms=duration_ms
                        )
                    else:
                        return SanityCheckResult(
                            component=component,
                            success=False,
                            message=f"SSH command execution failed (exit_code: {exit_code})",
                            duration_ms=duration_ms
                        )
                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000
                    manager.disconnect()
                    return SanityCheckResult(
                        component=component,
                        success=False,
                        message=f"SSH command execution error: {str(e)}",
                        duration_ms=duration_ms,
                        error=e
                    )
            else:
                duration_ms = (time.time() - start_time) * 1000
                return SanityCheckResult(
                    component=component,
                    success=False,
                    message="SSH connection failed",
                    duration_ms=duration_ms
                )
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return SanityCheckResult(
                component=component,
                success=False,
                message=f"Failed to initialize SSH manager: {str(e)}",
                duration_ms=duration_ms,
                error=e
            )
    
    def check_rabbitmq(self) -> SanityCheckResult:
        """
        Check RabbitMQ connectivity (optional).
        
        Returns:
            SanityCheckResult
        """
        component = "RabbitMQ"
        start_time = time.time()
        
        try:
            from src.infrastructure.rabbitmq_manager import RabbitMQConnectionManager
            
            # RabbitMQ is optional, so we'll just check if we can initialize
            # Full connection check might be too slow for sanity check
            duration_ms = (time.time() - start_time) * 1000
            
            return SanityCheckResult(
                component=component,
                success=True,
                message="RabbitMQ manager available (connection check skipped - optional)",
                duration_ms=duration_ms
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return SanityCheckResult(
                component=component,
                success=True,  # Optional component, don't fail if not available
                message=f"RabbitMQ not available (optional): {str(e)}",
                duration_ms=duration_ms
            )
    
    def run_all_checks(self, skip_optional: bool = False) -> List[SanityCheckResult]:
        """
        Run all sanity checks.
        
        Args:
            skip_optional: If True, skip optional components (RabbitMQ)
            
        Returns:
            List of SanityCheckResult objects
        """
        logger.info("=" * 100)
        logger.info("SANITY CHECK: Verifying infrastructure components...")
        logger.info("=" * 100)
        logger.info(f"Environment: {self.environment}")
        logger.info("")
        
        # Required components
        checks = [
            ("Focus Server API", self.check_focus_server),
            ("MongoDB", self.check_mongodb),
            ("Kubernetes", self.check_kubernetes),
            ("SSH", self.check_ssh),
        ]
        
        # Optional components
        if not skip_optional:
            checks.append(("RabbitMQ", self.check_rabbitmq))
        
        results = []
        total_start = time.time()
        
        for component_name, check_func in checks:
            logger.info(f"Checking {component_name}...")
            result = check_func()
            results.append(result)
            self.results.append(result)
            
            status = "✅ PASS" if result.success else "❌ FAIL"
            logger.info(f"  {status}: {result.message} ({result.duration_ms:.1f}ms)")
            
            if result.error:
                logger.debug(f"    Error details: {result.error}")
        
        total_duration = (time.time() - total_start) * 1000
        
        logger.info("")
        logger.info("=" * 100)
        logger.info("SANITY CHECK SUMMARY")
        logger.info("=" * 100)
        
        passed = sum(1 for r in results if r.success)
        failed = len(results) - passed
        
        logger.info(f"Total checks: {len(results)}")
        logger.info(f"✅ Passed: {passed}")
        logger.info(f"❌ Failed: {failed}")
        logger.info(f"⏱️  Total duration: {total_duration:.1f}ms")
        logger.info("")
        
        # Print failed checks
        if failed > 0:
            logger.warning("Failed components:")
            for result in results:
                if not result.success:
                    logger.warning(f"  ❌ {result.component}: {result.message}")
        
        logger.info("=" * 100)
        logger.info("")
        
        return results
    
    def all_passed(self) -> bool:
        """
        Check if all required checks passed.
        
        Returns:
            True if all checks passed
        """
        # RabbitMQ is optional, so we don't count it as required
        required_results = [r for r in self.results if r.component != "RabbitMQ"]
        return all(r.success for r in required_results)
    
    def get_summary(self) -> Dict[str, any]:
        """
        Get summary of sanity check results.
        
        Returns:
            Dictionary with summary information
        """
        passed = sum(1 for r in self.results if r.success)
        failed = len(self.results) - passed
        
        return {
            'total': len(self.results),
            'passed': passed,
            'failed': failed,
            'all_passed': self.all_passed(),
            'results': [
                {
                    'component': r.component,
                    'success': r.success,
                    'message': r.message,
                    'duration_ms': r.duration_ms
                }
                for r in self.results
            ]
        }

