"""
Detailed RabbitMQ check - verify if data is actually flowing.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager
import json


def get_output(result):
    if isinstance(result, dict):
        return result.get('stdout', '') or result.get('output', '')
    return str(result) if result else ''


def main():
    config_manager = ConfigManager()
    ssh = SSHManager(config_manager)
    
    print("=" * 70)
    print("🐰 Detailed RabbitMQ Data Flow Check")
    print("=" * 70)
    
    try:
        print("\n🔌 Connecting...")
        ssh.connect()
        print("✅ Connected!")
        
        # 1. Check ALL queues with message counts
        print("\n" + "=" * 70)
        print("📊 ALL RabbitMQ Queues (sorted by message count)")
        print("=" * 70)
        
        result = ssh.execute_command(
            """curl -s -u prisma:prismapanda 'http://10.10.10.107:15672/api/queues' 2>&1""",
            timeout=30
        )
        
        output = get_output(result)
        try:
            queues = json.loads(output)
            # Sort by message count
            sorted_queues = sorted(queues, key=lambda x: x.get('messages', 0), reverse=True)
            
            print(f"\nTotal queues: {len(queues)}")
            print("\nQueues with messages > 0:")
            has_messages = False
            for q in sorted_queues:
                msgs = q.get('messages', 0)
                if msgs > 0:
                    has_messages = True
                    print(f"  ✅ {q['name']}: {msgs} messages, {q.get('consumers', 0)} consumers")
            
            if not has_messages:
                print("  ❌ No queues have messages!")
            
            print("\nAll grpc-job queues:")
            grpc_queues = [q for q in queues if 'grpc-job' in q.get('name', '')]
            for q in grpc_queues[:10]:
                print(f"  • {q['name']}: {q.get('messages', 0)} msgs, {q.get('consumers', 0)} consumers")
            
            print("\nOther interesting queues:")
            for q in sorted_queues[:15]:
                if 'grpc-job' not in q.get('name', ''):
                    print(f"  • {q['name']}: {q.get('messages', 0)} msgs")
                    
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
            print(f"Raw output: {output[:500]}")
        
        # 2. Check message rates (are messages being published?)
        print("\n" + "=" * 70)
        print("📈 Message Rates (is data flowing?)")
        print("=" * 70)
        
        result = ssh.execute_command(
            """curl -s -u prisma:prismapanda 'http://10.10.10.107:15672/api/overview' 2>&1""",
            timeout=30
        )
        
        output = get_output(result)
        try:
            overview = json.loads(output)
            msg_stats = overview.get('message_stats', {})
            
            publish_rate = msg_stats.get('publish_details', {}).get('rate', 0)
            deliver_rate = msg_stats.get('deliver_details', {}).get('rate', 0)
            ack_rate = msg_stats.get('ack_details', {}).get('rate', 0)
            
            print(f"\n  Publish rate: {publish_rate:.2f} msg/sec")
            print(f"  Deliver rate: {deliver_rate:.2f} msg/sec")
            print(f"  Ack rate: {ack_rate:.2f} msg/sec")
            
            if publish_rate > 0:
                print("\n  ✅ Data IS being published to RabbitMQ!")
            else:
                print("\n  ⚠️ No data being published right now")
                
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse: {e}")
        
        # 3. Check exchanges
        print("\n" + "=" * 70)
        print("🔄 Exchanges (where is data routed?)")
        print("=" * 70)
        
        result = ssh.execute_command(
            """curl -s -u prisma:prismapanda 'http://10.10.10.107:15672/api/exchanges' 2>&1""",
            timeout=30
        )
        
        output = get_output(result)
        try:
            exchanges = json.loads(output)
            print(f"\nTotal exchanges: {len(exchanges)}")
            for ex in exchanges:
                name = ex.get('name', '(default)')
                ex_type = ex.get('type', 'unknown')
                if name and name != '':
                    print(f"  • {name} ({ex_type})")
        except:
            print(f"Raw: {output[:300]}")
        
        # 4. Check bindings (how are queues connected to exchanges?)
        print("\n" + "=" * 70)
        print("🔗 Queue Bindings for grpc-job queues")
        print("=" * 70)
        
        # Get one grpc-job queue and check its bindings
        result = ssh.execute_command(
            """curl -s -u prisma:prismapanda 'http://10.10.10.107:15672/api/bindings' 2>&1 | head -c 5000""",
            timeout=30
        )
        
        output = get_output(result)
        try:
            bindings = json.loads(output)
            grpc_bindings = [b for b in bindings if 'grpc-job' in b.get('destination', '')]
            print(f"\nBindings for grpc-job queues: {len(grpc_bindings)}")
            for b in grpc_bindings[:5]:
                print(f"  • {b.get('source', 'default')} -> {b.get('destination')} (key: {b.get('routing_key', 'none')})")
        except:
            pass
        
        # 5. Check what the forwarder queues look like
        print("\n" + "=" * 70)
        print("📤 Forwarder queues (source of data)")
        print("=" * 70)
        
        result = ssh.execute_command(
            """curl -s -u prisma:prismapanda 'http://10.10.10.107:15672/api/queues' 2>&1""",
            timeout=30
        )
        
        output = get_output(result)
        try:
            queues = json.loads(output)
            forwarder_queues = [q for q in queues if 'forwarder' in q.get('name', '').lower()]
            print(f"\nForwarder queues found: {len(forwarder_queues)}")
            for q in forwarder_queues:
                print(f"  • {q['name']}: {q.get('messages', 0)} msgs, rate: {q.get('message_stats', {}).get('publish_details', {}).get('rate', 0):.2f}/s")
        except:
            pass
        
        # 6. Summary
        print("\n" + "=" * 70)
        print("📋 SUMMARY")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            ssh.disconnect()
        except:
            pass


if __name__ == "__main__":
    main()

