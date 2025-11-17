#!/usr/bin/env python3
"""
Pre-Test System Health Check Script
====================================

בודק את כל הקומפוננטות של המערכת לפני תחילת הטסטים:
- Focus Server API
- MongoDB
- Kubernetes (חיבור, GPU resources, pods)
- RabbitMQ
- SSH

Usage:
    python scripts/pre_test_health_check.py [--env=staging]
    
Exit Codes:
    0 - כל הקומפוננטות תקינות
    1 - יש בעיות בקומפוננטות
"""

import sys
import os
import argparse
import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime

# Try to import colorama for colored output (optional)
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    # Fallback if colorama not available
    class Fore:
        GREEN = ''
        RED = ''
        YELLOW = ''
        CYAN = ''
    
    class Style:
        RESET_ALL = ''
    
    COLORAMA_AVAILABLE = False

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config.config_manager import ConfigManager
from src.apis.focus_server_api import FocusServerAPI
from src.infrastructure.mongodb_manager import MongoDBManager
from src.infrastructure.kubernetes_manager import KubernetesManager
from src.infrastructure.ssh_manager import SSHManager
from src.infrastructure.rabbitmq_manager import RabbitMQConnectionManager
from src.core.exceptions import InfrastructureError, APIError


class HealthCheckResult:
    """Represents a health check result for a component."""
    
    def __init__(self, name: str, status: bool, details: Dict[str, Any] = None, error: str = None):
        self.name = name
        self.status = status
        self.details = details or {}
        self.error = error
    
    def __str__(self):
        status_icon = "✅" if self.status else "❌"
        status_text = "OK" if self.status else "FAILED"
        status_color = Fore.GREEN if self.status else Fore.RED
        
        result = f"{status_icon} {self.name}: {status_color}{status_text}{Style.RESET_ALL}\n"
        
        if self.details:
            for key, value in self.details.items():
                result += f"   {key}: {value}\n"
        
        if self.error:
            result += f"   {Fore.RED}Error: {self.error}{Style.RESET_ALL}\n"
        
        return result


class PreTestHealthChecker:
    """Comprehensive health checker for all system components."""
    
    def __init__(self, environment: str = "staging"):
        """
        Initialize health checker.
        
        Args:
            environment: Environment name (staging, production, local)
        """
        self.environment = environment
        self.config_manager = ConfigManager(environment)
        self.logger = logging.getLogger(__name__)
        self.results: List[HealthCheckResult] = []
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def check_focus_server(self) -> HealthCheckResult:
        """Check Focus Server API connectivity and health."""
        name = "Focus Server API"
        details = {}
        error = None
        
        try:
            self.logger.info(f"Checking {name}...")
            # Initialize API client
            api = FocusServerAPI(self.config_manager)
            details["Base URL"] = api.base_url
            self.logger.debug(f"Focus Server base URL: {api.base_url}")
            
            # Test /ack endpoint (health check)
            self.logger.debug("Testing /ack endpoint...")
            try:
                response = api.get("/ack")
                if response.status_code == 200:
                    details["Health Check"] = "OK"
                    details["Status Code"] = response.status_code
                    self.logger.info(f"{name}: Health check passed (status {response.status_code})")
                else:
                    error = f"Health check returned status {response.status_code}"
                    self.logger.warning(f"{name}: Health check returned status {response.status_code}")
            except Exception as e:
                error = f"Health check failed: {str(e)}"
                self.logger.error(f"{name}: Health check failed - {e}")
            
            # Test /channels endpoint
            self.logger.debug("Testing /channels endpoint...")
            try:
                channels = api.get_channels()
                details["Channels Endpoint"] = "OK"
                details["Channel Range"] = f"{channels.lowest_channel}-{channels.highest_channel}"
                self.logger.info(f"{name}: Channels endpoint OK (range: {channels.lowest_channel}-{channels.highest_channel})")
            except Exception as e:
                details["Channels Endpoint"] = f"Failed: {str(e)}"
                self.logger.warning(f"{name}: Channels endpoint failed - {e}")
            
            status = error is None
            
        except Exception as e:
            status = False
            error = f"Failed to initialize API client: {str(e)}"
            self.logger.error(f"{name}: Failed to initialize - {e}")
        
        return HealthCheckResult(name, status, details, error)
    
    def check_mongodb(self) -> HealthCheckResult:
        """Check MongoDB connectivity and status."""
        name = "MongoDB"
        details = {}
        error = None
        
        try:
            self.logger.info(f"Checking {name}...")
            # Initialize Kubernetes manager first (for SSH fallback support)
            self.logger.debug("Initializing Kubernetes manager for MongoDB status check...")
            try:
                k8s_manager = KubernetesManager(self.config_manager)
                self.logger.debug("Kubernetes manager initialized successfully")
            except Exception as e:
                k8s_manager = None
                details["Kubernetes Manager"] = f"Not available: {str(e)}"
                self.logger.warning(f"{name}: Kubernetes manager not available - {e}")
            
            # Initialize MongoDB manager with Kubernetes manager (for SSH fallback)
            self.logger.debug("Initializing MongoDB manager...")
            mongodb_manager = MongoDBManager(
                self.config_manager,
                kubernetes_manager=k8s_manager if k8s_manager else None
            )
            
            # Test connection
            self.logger.debug("Testing MongoDB connection...")
            if mongodb_manager.connect():
                details["Connection"] = "OK"
                self.logger.info(f"{name}: Connection successful")
                
                # Get MongoDB status via Kubernetes (if available)
                self.logger.debug("Getting MongoDB status via Kubernetes...")
                try:
                    status = mongodb_manager.get_mongodb_status()
                    details["Status Check"] = "OK"
                    details["Connected"] = status.get("connected", False)
                    details["Ready Replicas"] = status.get("ready_replicas", 0)
                    details["Total Replicas"] = status.get("replicas", 0)
                    self.logger.info(f"{name}: Status check OK (ready: {status.get('ready_replicas', 0)}/{status.get('replicas', 0)})")
                    
                    if status.get("error"):
                        # If error but connection works, it's a warning not a failure
                        details["Status Warning"] = status["error"]
                        self.logger.warning(f"{name}: Status warning - {status['error']}")
                except Exception as e:
                    error_msg = str(e)
                    if "timeout" in error_msg.lower():
                        details["Status Check"] = "Timeout (Kubernetes API not accessible)"
                        details["Note"] = "MongoDB connection works, but K8s status unavailable"
                        self.logger.warning(f"{name}: Status check timeout - K8s API not accessible")
                    else:
                        details["Status Check"] = f"Failed: {str(e)}"
                        self.logger.warning(f"{name}: Status check failed - {e}")
                
                mongodb_manager.disconnect()
                self.logger.debug(f"{name}: Disconnected")
                status = True
            else:
                status = False
                error = "Failed to connect to MongoDB"
                self.logger.error(f"{name}: Connection failed")
        
        except Exception as e:
            status = False
            error = f"MongoDB check failed: {str(e)}"
            self.logger.error(f"{name}: Check failed with exception - {e}", exc_info=True)
        
        return HealthCheckResult(name, status, details, error)
    
    def check_kubernetes(self) -> HealthCheckResult:
        """Check Kubernetes connectivity and resources."""
        name = "Kubernetes"
        details = {}
        error = None
        
        try:
            self.logger.info(f"Checking {name}...")
            # Initialize Kubernetes manager
            self.logger.debug("Initializing Kubernetes manager...")
            k8s_manager = KubernetesManager(self.config_manager)
            
            # Check connection method
            if k8s_manager.use_ssh_fallback:
                details["Connection Method"] = "SSH Fallback ✅"
                self.logger.info(f"{name}: Using SSH fallback")
            else:
                details["Connection Method"] = "Direct API"
                self.logger.info(f"{name}: Using direct API")
            
            # Get cluster info (with timeout handling)
            self.logger.debug("Getting cluster info...")
            try:
                cluster_info = k8s_manager.get_cluster_info()
                details["Cluster Version"] = cluster_info.get("version", "Unknown")
                details["Node Count"] = cluster_info.get("node_count", 0)
                details["Cluster Info"] = "OK"
                self.logger.info(f"{name}: Cluster info OK (version: {cluster_info.get('version', 'Unknown')}, nodes: {cluster_info.get('node_count', 0)})")
            except Exception as e:
                error_msg = str(e)
                if "timeout" in error_msg.lower() or "connection" in error_msg.lower():
                    # If timeout, try to initialize SSH fallback explicitly
                    if not k8s_manager.use_ssh_fallback:
                        details["Cluster Info"] = "Timeout - trying SSH fallback..."
                        try:
                            if k8s_manager._init_ssh_fallback():
                                details["SSH Fallback"] = "Initialized"
                                # Try again with SSH fallback
                                cluster_info = k8s_manager.get_cluster_info()
                                details["Cluster Version"] = cluster_info.get("version", "Unknown")
                                details["Node Count"] = cluster_info.get("node_count", 0)
                                details["Cluster Info"] = "OK (via SSH)"
                            else:
                                details["Cluster Info"] = "Failed - SSH fallback also failed"
                                error = "Kubernetes API timeout and SSH fallback failed"
                        except Exception as e2:
                            details["Cluster Info"] = f"Failed: {str(e2)}"
                            error = f"Kubernetes check failed: {str(e2)}"
                    else:
                        details["Cluster Info"] = f"Failed: {error_msg}"
                        error = f"Kubernetes check failed: {error_msg}"
                else:
                    details["Cluster Info"] = f"Failed: {error_msg}"
                    error = f"Kubernetes check failed: {error_msg}"
            
            # Check deployments (only if cluster info succeeded)
            if error is None:
                self.logger.debug("Getting deployments...")
                try:
                    deployments = k8s_manager.get_deployments()
                    details["Deployments"] = len(deployments)
                    self.logger.debug(f"{name}: Found {len(deployments)} deployments")
                    
                    # Check Focus Server deployment
                    focus_deployments = [d for d in deployments if "focus" in d["name"].lower()]
                    if focus_deployments:
                        fs_deployment = focus_deployments[0]
                        details["Focus Server Deployment"] = "Found"
                        details["Focus Server Ready"] = fs_deployment.get("ready_replicas", 0)
                        details["Focus Server Total"] = fs_deployment.get("replicas", 0)
                        self.logger.info(f"{name}: Focus Server deployment found (ready: {fs_deployment.get('ready_replicas', 0)}/{fs_deployment.get('replicas', 0)})")
                    else:
                        details["Focus Server Deployment"] = "Not Found"
                        self.logger.warning(f"{name}: Focus Server deployment not found")
                except Exception as e:
                    details["Deployments"] = f"Failed: {str(e)}"
                    self.logger.warning(f"{name}: Failed to get deployments - {e}")
            
            # Check pods (only if cluster info succeeded)
            if error is None:
                self.logger.debug("Getting pods...")
                try:
                    pods = k8s_manager.get_pods()
                    running_pods = [p for p in pods if p["status"] == "Running"]
                    pending_pods = [p for p in pods if p["status"] == "Pending"]
                    
                    details["Total Pods"] = len(pods)
                    details["Running Pods"] = len(running_pods)
                    details["Pending Pods"] = len(pending_pods)
                    self.logger.info(f"{name}: Pods status (total: {len(pods)}, running: {len(running_pods)}, pending: {len(pending_pods)})")
                    
                    # Check for gRPC jobs (should be minimal before tests)
                    grpc_pods = [p for p in pods if "grpc-job" in p["name"]]
                    details["gRPC Jobs"] = len(grpc_pods)
                    self.logger.debug(f"{name}: Found {len(grpc_pods)} gRPC jobs")
                    
                    if len(pending_pods) > 10:
                        error = f"Too many pending pods: {len(pending_pods)}"
                        self.logger.warning(f"{name}: Too many pending pods ({len(pending_pods)})")
                except Exception as e:
                    details["Pods"] = f"Failed: {str(e)}"
                    self.logger.warning(f"{name}: Failed to get pods - {e}")
            
            status = error is None
            
        except Exception as e:
            status = False
            error = f"Kubernetes check failed: {str(e)}"
            self.logger.error(f"{name}: Check failed with exception - {e}", exc_info=True)
        
        return HealthCheckResult(name, status, details, error)
    
    def check_rabbitmq(self) -> HealthCheckResult:
        """Check RabbitMQ connectivity."""
        name = "RabbitMQ"
        details = {}
        error = None
        
        try:
            self.logger.info(f"Checking {name}...")
            # Get SSH config (RabbitMQ manager uses SSH to connect)
            self.logger.debug("Getting SSH configuration...")
            ssh_config = self.config_manager.get("ssh", {})
            
            # Extract SSH connection details (support both nested and flat structures)
            if "target_host" in ssh_config:
                # Nested structure
                ssh_host = ssh_config["target_host"]["host"]
                ssh_user = ssh_config["target_host"]["username"]
                ssh_password = ssh_config["target_host"].get("password")
                ssh_key_file = ssh_config["target_host"].get("key_file")
            else:
                # Legacy flat structure
                ssh_host = ssh_config.get("host")
                ssh_user = ssh_config.get("username", "prisma")
                ssh_password = ssh_config.get("password")
                ssh_key_file = ssh_config.get("key_file")
            
            # Get RabbitMQ config from environment config
            rabbitmq_config = self.config_manager.get("rabbitmq", {})
            
            if not ssh_host:
                status = False
                error = "SSH host not configured"
                self.logger.error(f"{name}: SSH host not configured")
                return HealthCheckResult(name, status, details, error)
            
            # Expand SSH key path if needed
            if ssh_key_file and ssh_key_file.startswith('~'):
                from pathlib import Path
                home = str(Path.home())
                ssh_key_file = ssh_key_file.replace('~', home, 1)
            
            # Initialize RabbitMQ manager
            self.logger.debug(f"Initializing RabbitMQ manager (host: {ssh_host}, service: {rabbitmq_config.get('name', 'rabbitmq-panda')})...")
            rabbitmq_manager = RabbitMQConnectionManager(
                k8s_host=ssh_host,
                ssh_user=ssh_user,
                ssh_password=ssh_password,
                ssh_key_file=ssh_key_file,
                preferred_service=rabbitmq_config.get("name", "rabbitmq-panda")
            )
            
            # Test connection using setup() method
            self.logger.debug("Running RabbitMQ setup (discovering services, extracting credentials)...")
            try:
                # setup() discovers services and extracts credentials
                conn_info = rabbitmq_manager.setup()
                
                if conn_info:
                    details["Connection"] = "OK"
                    details["Host"] = ssh_host
                    details["Service"] = rabbitmq_config.get("name", "rabbitmq-panda")
                    self.logger.info(f"{name}: Setup successful (host: {ssh_host}, service: {rabbitmq_config.get('name', 'rabbitmq-panda')})")
                    
                    # Check if credentials were extracted
                    if rabbitmq_manager.credentials:
                        details["Credentials"] = "OK"
                        details["Username"] = rabbitmq_manager.credentials.username
                        details["Port"] = rabbitmq_manager.credentials.port
                        self.logger.info(f"{name}: Credentials extracted (username: {rabbitmq_manager.credentials.username})")
                    
                    # Cleanup
                    self.logger.debug("Cleaning up RabbitMQ connection...")
                    rabbitmq_manager.cleanup()
                    status = True
                else:
                    status = False
                    error = "Failed to setup RabbitMQ connection"
                    self.logger.error(f"{name}: Setup failed - no connection info returned")
            except Exception as e:
                status = False
                error = f"RabbitMQ setup failed: {str(e)}"
                self.logger.error(f"{name}: Setup failed with exception - {e}", exc_info=True)
                # Try to cleanup if setup failed
                try:
                    rabbitmq_manager.cleanup()
                except:
                    pass
        
        except Exception as e:
            status = False
            error = f"RabbitMQ check failed: {str(e)}"
            self.logger.error(f"{name}: Check failed with exception - {e}", exc_info=True)
        
        return HealthCheckResult(name, status, details, error)
    
    def check_ssh(self) -> HealthCheckResult:
        """Check SSH connectivity."""
        name = "SSH"
        details = {}
        error = None
        
        try:
            self.logger.info(f"Checking {name}...")
            # Initialize SSH manager
            self.logger.debug("Initializing SSH manager...")
            ssh_manager = SSHManager(self.config_manager)
            
            # Test connection
            self.logger.debug("Testing SSH connection...")
            if ssh_manager.connect():
                details["Connection"] = "OK"
                self.logger.info(f"{name}: Connection successful")
                
                # Test command execution
                self.logger.debug("Testing command execution...")
                try:
                    result = ssh_manager.execute_command("hostname", timeout=10)
                    if result["success"]:
                        details["Command Execution"] = "OK"
                        details["Hostname"] = result["stdout"].strip()
                        self.logger.info(f"{name}: Command execution OK (hostname: {result['stdout'].strip()})")
                    else:
                        details["Command Execution"] = f"Failed: {result['stderr']}"
                        self.logger.warning(f"{name}: Command execution failed - {result['stderr']}")
                except Exception as e:
                    details["Command Execution"] = f"Failed: {str(e)}"
                    self.logger.warning(f"{name}: Command execution failed with exception - {e}")
                
                self.logger.debug("Disconnecting SSH...")
                ssh_manager.disconnect()
                status = True
            else:
                status = False
                error = "Failed to connect via SSH"
                self.logger.error(f"{name}: Connection failed")
        
        except Exception as e:
            status = False
            error = f"SSH check failed: {str(e)}"
            self.logger.error(f"{name}: Check failed with exception - {e}", exc_info=True)
        
        return HealthCheckResult(name, status, details, error)
    
    def run_all_checks(self) -> Tuple[bool, List[HealthCheckResult]]:
        """
        Run all health checks and return results.
        
        Returns:
            Tuple of (all_passed, results_list)
        """
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"Pre-Test System Health Check - {self.environment.upper()}")
        print(f"{'='*80}{Style.RESET_ALL}\n")
        
        self.results = []
        
        # Define checks to run
        checks = [
            ("Focus Server API", self.check_focus_server),
            ("SSH", self.check_ssh),
            ("Kubernetes", self.check_kubernetes),
            ("MongoDB", self.check_mongodb),
            ("RabbitMQ", self.check_rabbitmq),
        ]
        
        print(f"{Fore.YELLOW}Running health checks...{Style.RESET_ALL}\n")
        
        # Run each check with progress updates
        for idx, (check_name, check_func) in enumerate(checks, 1):
            print(f"{Fore.CYAN}[{idx}/{len(checks)}] Checking {check_name}...{Style.RESET_ALL}", end=" ", flush=True)
            self.logger.info(f"Starting health check: {check_name}")
            
            try:
                result = check_func()
                self.results.append(result)
                
                # Print immediate status
                if result.status:
                    print(f"{Fore.GREEN}✅ OK{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ FAILED{Style.RESET_ALL}")
                    if result.error:
                        print(f"   {Fore.RED}Error: {result.error}{Style.RESET_ALL}")
                
                # Print details
                if result.details:
                    for key, value in result.details.items():
                        if "Error" not in key and "Warning" not in key:
                            print(f"   {Fore.GREEN}✓{Style.RESET_ALL} {key}: {value}")
                    # Show warnings/errors in details
                    for key, value in result.details.items():
                        if "Warning" in key or "Error" in key:
                            print(f"   {Fore.YELLOW}⚠{Style.RESET_ALL} {key}: {value}")
                
                self.logger.info(f"Health check completed: {check_name} - {'PASSED' if result.status else 'FAILED'}")
                
            except Exception as e:
                error_result = HealthCheckResult(check_name, False, {}, f"Unexpected error: {str(e)}")
                self.results.append(error_result)
                print(f"{Fore.RED}❌ ERROR: {str(e)}{Style.RESET_ALL}")
                self.logger.error(f"Health check failed with exception: {check_name} - {e}", exc_info=True)
            
            print()  # Empty line between checks
        
        # Summary
        print(f"\n{Fore.CYAN}{'='*80}")
        print("Summary")
        print(f"{'='*80}{Style.RESET_ALL}\n")
        
        total_count = len(self.results)
        passed_count = sum(1 for r in self.results if r.status)
        
        print(f"Total Checks: {total_count}")
        print(f"{Fore.GREEN}Passed: {passed_count}{Style.RESET_ALL}")
        print(f"{Fore.RED}Failed: {total_count - passed_count}{Style.RESET_ALL}\n")
        
        all_passed = all(r.status for r in self.results)
        
        if all_passed:
            print(f"{Fore.GREEN}✅ All components are healthy! Ready to run tests.{Style.RESET_ALL}\n")
        else:
            print(f"{Fore.RED}❌ Some components have issues. Please fix them before running tests.{Style.RESET_ALL}\n")
            print(f"{Fore.YELLOW}Failed components:{Style.RESET_ALL}")
            for result in self.results:
                if not result.status:
                    print(f"  - {result.name}: {result.error or 'See details above'}")
            print()
        
        return all_passed, self.results
    
    def generate_report(self, output_file: str = None):
        """
        Generate a detailed health check report.
        
        Args:
            output_file: Optional file path to save report
        """
        report_lines = [
            "# Pre-Test System Health Check Report",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Environment:** {self.environment}",
            "",
            "## Results",
            ""
        ]
        
        for result in self.results:
            status_icon = "✅" if result.status else "❌"
            report_lines.append(f"### {status_icon} {result.name}")
            report_lines.append(f"**Status:** {'OK' if result.status else 'FAILED'}")
            
            if result.details:
                report_lines.append("**Details:**")
                for key, value in result.details.items():
                    report_lines.append(f"- {key}: {value}")
            
            if result.error:
                report_lines.append(f"**Error:** {result.error}")
            
            report_lines.append("")
        
        # Summary
        passed_count = sum(1 for r in self.results if r.status)
        total_count = len(self.results)
        
        report_lines.extend([
            "## Summary",
            "",
            f"- **Total Checks:** {total_count}",
            f"- **Passed:** {passed_count}",
            f"- **Failed:** {total_count - passed_count}",
            ""
        ])
        
        report = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"{Fore.GREEN}Report saved to: {output_file}{Style.RESET_ALL}\n")
        else:
            print("\n" + report)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Pre-test system health check",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/pre_test_health_check.py
  python scripts/pre_test_health_check.py --env=staging
  python scripts/pre_test_health_check.py --env=production --report=health_report.md
        """
    )
    
    parser.add_argument(
        "--env",
        default="staging",
        help="Environment name (default: staging)"
    )
    
    parser.add_argument(
        "--report",
        help="Generate markdown report file"
    )
    
    args = parser.parse_args()
    
    # Run health checks
    checker = PreTestHealthChecker(environment=args.env)
    all_passed, results = checker.run_all_checks()
    
    # Generate report if requested
    if args.report:
        checker.generate_report(args.report)
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()

