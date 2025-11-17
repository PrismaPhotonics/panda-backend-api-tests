"""
Script to check if Prisma Web App API is a separate service.

This script:
1. Lists all services in the namespace
2. Checks ingress configuration
3. Checks if there's a separate pod for Prisma Web App API
4. Provides recommendations
"""

import logging
import sys
import json

sys.path.insert(0, '.')

from src.infrastructure.ssh_manager import SSHManager
from config.config_manager import ConfigManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)8s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


def check_prisma_web_app_api():
    """Check if Prisma Web App API is a separate service."""
    
    logger.info("=" * 80)
    logger.info("Checking Prisma Web App API Configuration")
    logger.info("=" * 80 + "\n")
    
    config_manager = ConfigManager()
    namespace = "panda"
    
    ssh_manager = SSHManager(config_manager)
    
    try:
        ssh_manager.connect()
    except Exception as e:
        logger.error(f"SSH connection failed: {e}")
        return
    
    # Step 1: List all services
    logger.info("Step 1: Listing all services...\n")
    cmd = f"kubectl get svc -n {namespace} -o json"
    result = ssh_manager.execute_command(cmd, timeout=30)
    
    if result["success"]:
        services = json.loads(result["stdout"])
        logger.info(f"Found {len(services.get('items', []))} services:\n")
        
        for svc in services.get('items', []):
            name = svc['metadata']['name']
            svc_type = svc.get('spec', {}).get('type', 'ClusterIP')
            ports = svc.get('spec', {}).get('ports', [])
            
            logger.info(f"Service: {name}")
            logger.info(f"  Type: {svc_type}")
            logger.info(f"  Ports:")
            for port in ports:
                logger.info(f"    - {port.get('port')} -> {port.get('targetPort')} ({port.get('protocol', 'TCP')})")
            
            # Check if it's related to Prisma Web App
            if 'prisma' in name.lower() or 'web' in name.lower() or 'app' in name.lower():
                logger.info(f"  ⚠️  This might be Prisma Web App API!")
            
            logger.info("")
    
    # Step 2: Check ingress
    logger.info("\n" + "=" * 80)
    logger.info("Step 2: Checking Ingress configuration...")
    logger.info("=" * 80 + "\n")
    
    cmd = f"kubectl get ingress -n {namespace} -o json"
    result = ssh_manager.execute_command(cmd, timeout=30)
    
    if result["success"]:
        ingresses = json.loads(result["stdout"])
        if ingresses.get('items'):
            logger.info(f"Found {len(ingresses.get('items', []))} ingress resources:\n")
            for ingress in ingresses.get('items', []):
                name = ingress['metadata']['name']
                rules = ingress.get('spec', {}).get('rules', [])
                
                logger.info(f"Ingress: {name}")
                for rule in rules:
                    host = rule.get('host', '*')
                    logger.info(f"  Host: {host}")
                    for path in rule.get('http', {}).get('paths', []):
                        path_path = path.get('path', '/')
                        backend = path.get('backend', {})
                        service_name = backend.get('service', {}).get('name', 'N/A')
                        logger.info(f"    Path: {path_path} -> Service: {service_name}")
                logger.info("")
        else:
            logger.info("No ingress resources found")
    
    # Step 3: Check if Focus Server handles Prisma Web App API
    logger.info("\n" + "=" * 80)
    logger.info("Step 3: Checking Focus Server service details...")
    logger.info("=" * 80 + "\n")
    
    cmd = f"kubectl get svc panda-panda-focus-server -n {namespace} -o json"
    result = ssh_manager.execute_command(cmd, timeout=30)
    
    if result["success"]:
        svc = json.loads(result["stdout"])
        selector = svc.get('spec', {}).get('selector', {})
        ports = svc.get('spec', {}).get('ports', [])
        
        logger.info("Focus Server Service:")
        logger.info(f"  Selector: {selector}")
        logger.info(f"  Ports:")
        for port in ports:
            logger.info(f"    - Port {port.get('port')} -> {port.get('targetPort')} ({port.get('name', 'unnamed')})")
        
        # Check if there's a port for Prisma Web App API
        for port in ports:
            port_name = port.get('name', '').lower()
            if 'prisma' in port_name or 'web' in port_name or 'api' in port_name:
                logger.info(f"  ⚠️  Port {port.get('port')} might be for Prisma Web App API!")
    
    # Step 4: Check pods with prisma/web/app labels
    logger.info("\n" + "=" * 80)
    logger.info("Step 4: Checking pods with prisma/web/app labels...")
    logger.info("=" * 80 + "\n")
    
    cmd = f"kubectl get pods -n {namespace} -o json"
    result = ssh_manager.execute_command(cmd, timeout=30)
    
    if result["success"]:
        pods = json.loads(result["stdout"])
        relevant_pods = []
        
        for pod in pods.get('items', []):
            name = pod['metadata']['name']
            labels = pod['metadata'].get('labels', {})
            
            # Check if pod might be Prisma Web App API
            if any(keyword in name.lower() for keyword in ['prisma', 'web', 'app', 'api']):
                if 'focus-server' not in name.lower():
                    relevant_pods.append((name, labels))
        
        if relevant_pods:
            logger.info(f"Found {len(relevant_pods)} potentially relevant pods:\n")
            for pod_name, labels in relevant_pods:
                logger.info(f"Pod: {pod_name}")
                logger.info(f"  Labels: {labels}")
                logger.info("")
        else:
            logger.info("No separate Prisma Web App API pods found")
            logger.info("⚠️  Prisma Web App API might be part of Focus Server")
    
    # Step 5: Recommendations
    logger.info("\n" + "=" * 80)
    logger.info("RECOMMENDATIONS")
    logger.info("=" * 80 + "\n")
    
    logger.info("1. The endpoint '/prisma-210-1000/api/push-to-rabbit' is likely handled by:")
    logger.info("   - Prisma Web App API (separate service)")
    logger.info("   - Or Focus Server with different routing")
    logger.info("")
    
    logger.info("2. To find where logs appear:")
    logger.info("   - Check all pods: kubectl get pods -n panda")
    logger.info("   - Check services: kubectl get svc -n panda")
    logger.info("   - Check ingress: kubectl get ingress -n panda")
    logger.info("")
    
    logger.info("3. The endpoint might be proxied through:")
    logger.info("   - Ingress controller")
    logger.info("   - Load balancer")
    logger.info("   - Service mesh")
    logger.info("")
    
    logger.info("4. To see logs in real-time:")
    logger.info("   - Check all pods: kubectl logs -n panda <pod-name> -f")
    logger.info("   - Or check ingress controller logs")
    logger.info("")
    
    logger.info("\n✅ Investigation complete!\n")
    
    ssh_manager.disconnect()


if __name__ == "__main__":
    check_prisma_web_app_api()

