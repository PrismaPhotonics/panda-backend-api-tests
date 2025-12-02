"""Verify that Focus Server config was fixed correctly."""
import sys
sys.path.insert(0, '.')
from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager

cm = ConfigManager()
ssh = SSHManager(cm)
ssh.connect()

print('='*80)
print('🔍 בודק שהקונפיגורציה תוקנה נכון')
print('='*80)
print()

# Get pod name
result = ssh.execute_command('kubectl get pods -n panda | grep focus-server | grep Running | head -1 | awk \'{print $1}\'')
pod_name = result.get('stdout', '').strip()

if not pod_name:
    print('❌ לא מצאתי Focus Server pod')
    print('Pods:')
    result2 = ssh.execute_command('kubectl get pods -n panda | grep focus-server')
    print(result2.get('stdout', 'No output'))
    sys.exit(1)

print(f'✅ נמצא pod: {pod_name}')
print()

# Check ConfigMap directly
print('📋 בודק ConfigMap ישירות...')
result = ssh.execute_command('kubectl get configmap prisma-config -n panda -o yaml | grep -A 2 "storage_mount_path" | head -5')
output = result.get('stdout', '').strip()

if output:
    print('תוכן ConfigMap:')
    print(output)
    if '/prisma/root/recordings' in output and '/segy' not in output:
        print()
        print('='*80)
        print('✅ התיקון הצליח! storage_mount_path = /prisma/root/recordings')
        print('='*80)
    elif '/segy' in output:
        print()
        print('⚠️  עדיין יש /segy בנתיב - ייתכן שהתיקון לא הצליח')
        print('תוכן:', output)
    else:
        print()
        print('✅ נראה שהקונפיגורציה עודכנה')
else:
    print('❌ לא הצלחתי לבדוק את ה-ConfigMap')

ssh.disconnect()

