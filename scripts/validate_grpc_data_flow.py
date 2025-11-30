"""
Validate gRPC Data Flow - Comprehensive Test Script

This script tests the gRPC data flow in the Focus Server system.
It tries multiple methods to ensure data is flowing.

Usage:
    python scripts/validate_grpc_data_flow.py

Author: QA Automation
Date: 2025-11-29
"""

import sys
import os
import time
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_output(result):
    """Extract stdout from result dict."""
    if isinstance(result, dict):
        return result.get('stdout', '') or result.get('output', '')
    return str(result) if result else ''


def main():
    config_manager = ConfigManager()
    ssh = SSHManager(config_manager)
    
    print("=" * 80)
    print("gRPC Data Flow Validation Script")
    print("=" * 80)
    
    try:
        ssh.connect()
        
        # =================================================================
        # Step 1: Check current grpc-job status
        # =================================================================
        print("\n📊 Step 1: Checking current gRPC jobs...")
        result = ssh.execute_command(
            """kubectl get jobs -n panda | grep grpc-job 2>&1"""
        )
        jobs_output = get_output(result)
        print(jobs_output if jobs_output else "No gRPC jobs running")
        
        # Get one active pod
        result = ssh.execute_command(
            """kubectl get pods -n panda | grep grpc-job | grep Running | head -1 | awk '{print $1}'"""
        )
        active_pod = get_output(result).strip()
        
        if active_pod:
            print(f"\n✅ Found active gRPC job pod: {active_pod}")
            
            # Check if port 5000 is listening
            print("\n🔍 Checking if gRPC server (port 5000) is listening...")
            result = ssh.execute_command(
                f"""kubectl exec -n panda {active_pod} -- netstat -tlnp 2>/dev/null | grep 5000 || echo "Port 5000 NOT listening" """
            )
            port_status = get_output(result)
            print(f"   {port_status.strip()}")
            
            if "5000" in port_status and "LISTEN" in port_status:
                print("\n✅ gRPC server IS listening! Let's connect to it.")
                
                # Get the NodePort
                pod_parts = active_pod.replace('grpc-job-', 'grpc-service-').split('-')[:3]
                svc_pattern = '-'.join(pod_parts) if pod_parts else 'grpc-service'
                # Actually, let's get the nodeport differently
                result = ssh.execute_command(
                    """kubectl get svc -n panda -o wide | grep grpc-service | head -1"""
                )
                svc_output = get_output(result)
                print(f"   Service: {svc_output.strip() if svc_output else 'Not found'}")
                
            else:
                print("\n⏳ gRPC server is NOT listening yet. Checking logs...")
                result = ssh.execute_command(
                    f"""kubectl logs -n panda {active_pod} --tail=10 2>&1"""
                )
                logs = get_output(result)
                print(f"   Last logs:\n{logs}")
                
        else:
            print("\n⚠️ No active gRPC job pods found")
        
        # =================================================================
        # Step 2: Check RabbitMQ for grpc-job queues
        # =================================================================
        print("\n📊 Step 2: Checking RabbitMQ for gRPC job queues...")
        result = ssh.execute_command(
            """curl -s -u prisma:prismapanda 'http://10.10.10.107:15672/api/queues' 2>&1 | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    grpc_queues = [q for q in data if 'grpc-job' in q.get('name', '')]
    for q in grpc_queues[:5]:
        print(f'  Queue: {q[\"name\"]} - Messages: {q.get(\"messages\", 0)}, Consumers: {q.get(\"consumers\", 0)}')
    if not grpc_queues:
        print('  No grpc-job queues found')
except Exception as e:
    print(f'  Error parsing: {e}')
" 2>&1"""
        )
        print(get_output(result))
        
        # =================================================================
        # Step 3: Check if there's a way to start data flow
        # =================================================================
        print("\n📊 Step 3: Checking data source options...")
        
        # Check for recent recordings
        result = ssh.execute_command(
            """ls -lt /prisma/root/recordings/ 2>&1 | head -5"""
        )
        print("   Recent recordings:")
        print(f"   {get_output(result)}")
        
        # =================================================================
        # Step 4: Test Option - Start mock gRPC server
        # =================================================================
        print("\n📊 Step 4: Can we use the Mock gRPC Server?")
        result = ssh.execute_command(
            """ls -la /home/prisma/debug-codebase/pz/microservices/focus_server/tests/grpc_mock_server.py 2>&1"""
        )
        mock_exists = "grpc_mock_server.py" in get_output(result)
        print(f"   Mock server exists: {'✅ Yes' if mock_exists else '❌ No'}")
        
        if mock_exists:
            print("\n   💡 You can start the mock server with:")
            print("   kubectl exec -n panda <focus-server-pod> -- python /home/prisma/debug-codebase/pz/microservices/focus_server/tests/grpc_mock_server.py")
        
        # =================================================================
        # Step 5: Summary and Recommendations
        # =================================================================
        print("\n" + "=" * 80)
        print("📋 SUMMARY AND RECOMMENDATIONS")
        print("=" * 80)
        
        print("""
הבעיה שזוהתה:
- ה-gRPC job נוצר ומחכה לדאטה מ-RabbitMQ
- ה-baby_analyzer מחכה ל-PrpInfoMessage שאף פעם לא מגיע
- אין forwarder/simulator פעיל שדוחף דאטה

פתרונות אפשריים:

1. 🎯 הפעלת livefs_forwarder (מומלץ לייצור):
   - ערוך את focus_server.yaml
   - שנה livefs_forwarder: false ל-true
   - Restart the Focus Server

2. 🧪 שימוש ב-Mock Server לבדיקות:
   - השתמש ב-grpc_mock_server.py
   - הוא מייצר דאטה ישירות ב-gRPC בלי RabbitMQ

3. 🔄 שימוש ב-Player להשמעת הקלטות:
   - יש הקלטות טריות בתיקיית recordings
   - השתמש ב-Player class להשמעה ל-RabbitMQ

4. 📝 לבדיקות עומס - הוספת validation בקוד:
   - ה-GrpcStreamClient שיצרנו כבר מוכן
   - צריך רק לוודא שיש מקור דאטה פעיל
""")
        
        print("\n" + "=" * 80)
        print("🔧 NEXT STEPS")
        print("=" * 80)
        print("""
כדי להפעיל את הבדיקות עם דאטה אמיתי:

1. בקש מצוות הפיתוח להפעיל את ה-livefs_forwarder
   או
2. הרץ את ה-mock server לבדיקות

לאחר שיש מקור דאטה, הטסטים שיצרנו יעבדו:
- test_live_investigation_grpc_data.py
- GrpcStreamClient ב-src/apis/grpc_client.py
""")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        ssh.disconnect()


if __name__ == "__main__":
    main()

