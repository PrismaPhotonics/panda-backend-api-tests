"""
Find RabbitMQ - Helper script to locate RabbitMQ in the cluster.

This script helps diagnose where RabbitMQ is actually running.

Author: QA Automation Architect
Date: 2025-10-08
"""

import sys
import logging
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.config_manager import ConfigManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def find_rabbitmq_via_kubectl(env="staging"):
    """
    Try to find RabbitMQ pods/services in Kubernetes.
    
    Args:
        env: Environment name
    """
    import subprocess
    
    logger.info("=" * 70)
    logger.info("Searching for RabbitMQ in Kubernetes...")
    logger.info("=" * 70)
    
    config = ConfigManager(env)
    k8s_config = config.get("kubernetes", {})
    context = k8s_config.get("context", "staging")
    
    try:
        # Find pods
        logger.info(f"\n[1] Searching for RabbitMQ pods (context: {context})...")
        result = subprocess.run(
            ["kubectl", "--context", context, "get", "pods", "-A"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            rabbit_pods = [line for line in lines if 'rabbit' in line.lower()]
            
            if rabbit_pods:
                logger.info("[+] Found RabbitMQ pods:")
                for pod in rabbit_pods:
                    logger.info(f"    {pod}")
            else:
                logger.warning("[!] No RabbitMQ pods found")
        else:
            logger.error(f"[X] kubectl get pods failed: {result.stderr}")
        
        # Find services
        logger.info(f"\n[2] Searching for RabbitMQ services...")
        result = subprocess.run(
            ["kubectl", "--context", context, "get", "svc", "-A"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            rabbit_svcs = [line for line in lines if 'rabbit' in line.lower()]
            
            if rabbit_svcs:
                logger.info("[+] Found RabbitMQ services:")
                for svc in rabbit_svcs:
                    logger.info(f"    {svc}")
            else:
                logger.warning("[!] No RabbitMQ services found")
        else:
            logger.error(f"[X] kubectl get svc failed: {result.stderr}")
        
        # Find deployments/statefulsets
        logger.info(f"\n[3] Searching for RabbitMQ deployments/statefulsets...")
        result = subprocess.run(
            ["kubectl", "--context", context, "get", "deploy,sts", "-A"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            rabbit_deploys = [line for line in lines if 'rabbit' in line.lower()]
            
            if rabbit_deploys:
                logger.info("[+] Found RabbitMQ deployments/statefulsets:")
                for deploy in rabbit_deploys:
                    logger.info(f"    {deploy}")
            else:
                logger.warning("[!] No RabbitMQ deployments/statefulsets found")
        else:
            logger.error(f"[X] kubectl get deploy,sts failed: {result.stderr}")
        
        return True
        
    except FileNotFoundError:
        logger.error("[X] kubectl not found! Please install kubectl.")
        return False
    except Exception as e:
        logger.error(f"[X] Error: {e}")
        return False


def suggest_port_forward(env="staging"):
    """Suggest port-forward command."""
    logger.info("\n" + "=" * 70)
    logger.info("SUGGESTED PORT-FORWARD COMMANDS")
    logger.info("=" * 70)
    
    config = ConfigManager(env)
    k8s_config = config.get("kubernetes", {})
    context = k8s_config.get("context", "staging")
    namespace = k8s_config.get("namespace", "default")
    
    logger.info("\nIf RabbitMQ service is found, run:")
    logger.info(f"  kubectl --context={context} -n {namespace} port-forward svc/rabbitmq-service 5672:5672 15672:15672")
    logger.info("\nOr if it's a pod:")
    logger.info(f"  kubectl --context={context} -n {namespace} port-forward <pod-name> 5672:5672 15672:15672")
    logger.info("\nThen test connection using 'local' environment:")
    logger.info("  py scripts/rabbitmq_helper.py --test-connection --env=local")


def check_direct_connection(env="staging"):
    """Try direct connection to configured host."""
    import socket
    
    logger.info("\n" + "=" * 70)
    logger.info("Testing direct connection...")
    logger.info("=" * 70)
    
    config = ConfigManager(env)
    rabbitmq = config.get("rabbitmq", {})
    host = rabbitmq.get("host", "localhost")
    port = rabbitmq.get("port", 5672)
    
    logger.info(f"\n[>] Testing connection to {host}:{port}...")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    
    try:
        result = sock.connect_ex((host, port))
        if result == 0:
            logger.info(f"[+] Port {port} is OPEN on {host}!")
            sock.close()
            return True
        else:
            logger.warning(f"[!] Port {port} is CLOSED on {host} (error: {result})")
            sock.close()
            return False
    except socket.gaierror:
        logger.error(f"[X] Hostname {host} could not be resolved")
        return False
    except socket.timeout:
        logger.error(f"[X] Connection to {host}:{port} timed out")
        return False
    except Exception as e:
        logger.error(f"[X] Error: {e}")
        return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Find RabbitMQ in cluster")
    parser.add_argument("--env", default="staging", help="Environment name")
    
    args = parser.parse_args()
    
    # Check direct connection first
    is_reachable = check_direct_connection(args.env)
    
    if not is_reachable:
        logger.info("\n[!] Direct connection failed. Checking Kubernetes...")
        find_rabbitmq_via_kubectl(args.env)
        suggest_port_forward(args.env)
    else:
        logger.info("\n[+] RabbitMQ is reachable directly!")
        logger.info("    You can test connection with:")
        logger.info(f"    py scripts/rabbitmq_helper.py --test-connection --env={args.env}")
    
    logger.info("\n" + "=" * 70)


if __name__ == "__main__":
    main()

