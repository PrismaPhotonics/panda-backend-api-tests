#!/usr/bin/env python3
"""
Script to check alert logs in Kubernetes pods.

Usage:
    python scripts/check_alert_logs.py --pod-name <pod-name> --alert-id <alert-id>
    python scripts/check_alert_logs.py --service focus-server --alert-id test-sd-123
    python scripts/check_alert_logs.py --service focus-server --follow
    python scripts/check_alert_logs.py --service rabbitmq --tail=200
"""

import argparse
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.infrastructure.kubernetes_manager import KubernetesManager
from src.infrastructure.ssh_manager import SSHManager
from config.config_manager import ConfigManager


def find_pod_by_service(k8s_manager: KubernetesManager, service_name: str, namespace: str = "panda") -> str:
    """Find pod name by service name."""
    service_selectors = {
        "focus-server": "app.kubernetes.io/name=panda-panda-focus-server",
        "rabbitmq": "app.kubernetes.io/instance=rabbitmq-panda",
        "mongodb": "app.kubernetes.io/instance=mongodb",
        "grpc-job": "app=grpc-job",  # Will match any grpc-job pod
    }
    
    selector = service_selectors.get(service_name.lower())
    if not selector:
        print(f"❌ Unknown service: {service_name}")
        print(f"Available services: {', '.join(service_selectors.keys())}")
        sys.exit(1)
    
    pods = k8s_manager.get_pods(namespace=namespace, label_selector=selector)
    if not pods:
        print(f"❌ No pods found for service: {service_name}")
        sys.exit(1)
    
    pod_name = pods[0]['metadata']['name']
    print(f"✅ Found pod: {pod_name}")
    return pod_name


def check_alert_logs(pod_name: str, alert_id: str = None, namespace: str = "panda", 
                     tail_lines: int = 500, follow: bool = False):
    """Check alert logs in a pod."""
    config_manager = ConfigManager()
    k8s_manager = KubernetesManager(config_manager)
    
    print(f"\n{'='*80}")
    print(f"Checking logs for pod: {pod_name}")
    print(f"{'='*80}\n")
    
    if follow:
        print("Following logs (Ctrl+C to stop)...\n")
        # For follow mode, use SSH directly
        ssh_manager = SSHManager(config_manager)
        ssh_manager.connect()
        
        try:
            cmd = f"kubectl logs -n {namespace} {pod_name} -f"
            ssh_manager.execute_command(cmd, timeout=None)
        except KeyboardInterrupt:
            print("\n\nStopped following logs")
        finally:
            ssh_manager.disconnect()
    else:
        # Get logs
        logs = k8s_manager.get_pod_logs(pod_name, namespace=namespace, tail_lines=tail_lines)
        
        if alert_id:
            # Filter logs by alert ID
            print(f"Searching for alert ID: {alert_id}\n")
            matching_lines = [line for line in logs.split('\n') if alert_id in line]
            
            if matching_lines:
                print(f"✅ Found {len(matching_lines)} lines containing '{alert_id}':\n")
                print('\n'.join(matching_lines))
            else:
                print(f"❌ No logs found containing '{alert_id}'")
                print("\nLast 50 lines of logs:")
                print('\n'.join(logs.split('\n')[-50:]))
        else:
            # Show all logs
            print("Recent logs:\n")
            print(logs)
            
            # Search for alert-related keywords
            alert_keywords = ['alert', 'push-to-rabbit', 'Algorithm.AlertReport', 'MLGroundAlertReport']
            print(f"\n{'='*80}")
            print("Searching for alert-related keywords...")
            print(f"{'='*80}\n")
            
            for keyword in alert_keywords:
                matching_lines = [line for line in logs.split('\n') if keyword.lower() in line.lower()]
                if matching_lines:
                    print(f"✅ Found {len(matching_lines)} lines containing '{keyword}':")
                    print('\n'.join(matching_lines[-10:]))  # Show last 10 matches
                    print()


def main():
    parser = argparse.ArgumentParser(description="Check alert logs in Kubernetes pods")
    parser.add_argument("--pod-name", help="Pod name (e.g., panda-panda-focus-server-78dbcfd9d9-4ld4s)")
    parser.add_argument("--service", help="Service name (focus-server, rabbitmq, mongodb, grpc-job)")
    parser.add_argument("--alert-id", help="Alert ID to search for")
    parser.add_argument("--namespace", default="panda", help="Kubernetes namespace (default: panda)")
    parser.add_argument("--tail", type=int, default=500, help="Number of lines to retrieve (default: 500)")
    parser.add_argument("--follow", "-f", action="store_true", help="Follow logs in real-time")
    
    args = parser.parse_args()
    
    if not args.pod_name and not args.service:
        parser.error("Either --pod-name or --service must be specified")
    
    config_manager = ConfigManager()
    k8s_manager = KubernetesManager(config_manager)
    
    # Find pod name
    if args.service:
        pod_name = find_pod_by_service(k8s_manager, args.service, args.namespace)
    else:
        pod_name = args.pod_name
    
    # Check logs
    check_alert_logs(
        pod_name=pod_name,
        alert_id=args.alert_id,
        namespace=args.namespace,
        tail_lines=args.tail,
        follow=args.follow
    )


if __name__ == "__main__":
    main()

