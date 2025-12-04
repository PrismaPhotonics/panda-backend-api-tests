"""
הסבר איפה רואים את storage_mount_path
"""
import sys
sys.path.insert(0, '.')
from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager

cm = ConfigManager()
ssh = SSHManager(cm)
ssh.connect()

pod = 'panda-panda-focus-server-7c767d7688-z6n5p'

print('='*70)
print('איפה רואים את storage_mount_path?')
print('='*70)
print()
print('יש 2 מקומות עיקריים:')
print()

print('='*70)
print('מקום 1: בתוך ה-POD - הקובץ בפועל')
print('='*70)
print('פקודה:')
print(f'kubectl exec -n panda {pod} -- cat /home/prisma/pz/config/py/default_config.py | grep -A 5 "class Focus"')
print()
print('תוצאה:')
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- cat /home/prisma/pz/config/py/default_config.py 2>/dev/null | grep -A 5 "class Focus"')
output = result.get('stdout', '')
if output:
    # Highlight the storage_mount_path line
    lines = output.split('\n')
    for line in lines:
        if 'storage_mount_path' in line:
            print(f'>>> {line} <<<  <-- זה השורה!')
        else:
            print(line)
else:
    print('Not found')

print('\n' + '='*70)
print('מקום 2: ב-ConfigMap ב-Kubernetes - המקור')
print('='*70)
print('פקודה:')
print('kubectl get configmap prisma-config -n panda -o yaml')
print()
print('תוצאה (רק החלק הרלוונטי):')
result = ssh.execute_command('kubectl get configmap prisma-config -n panda -o yaml 2>/dev/null')
configmap_yaml = result.get('stdout', '')

if configmap_yaml:
    # Find the storage_mount_path line in the YAML
    lines = configmap_yaml.split('\n')
    found_section = False
    for i, line in enumerate(lines):
        if 'storage_mount_path' in line:
            # Show context around this line
            start = max(0, i - 3)
            end = min(len(lines), i + 3)
            print('\nהקשר סביב השורה:')
            for j in range(start, end):
                marker = '>>> ' if j == i else '    '
                print(f'{marker}{lines[j]}')
            found_section = True
            break
    
    if not found_section:
        print('לא מצאתי את השורה ב-YAML (אולי היא מוברחת אחרת)')
        # Try to find it in the escaped format
        if 'storage_mount_path' in configmap_yaml:
            print('\nאבל השורה כן קיימת ב-YAML!')
            print('היא מופיעה בתוך שדה data.default_config.py כטקסט מוברח')
            print('בואו נחפש אותה:')
            # Extract just the default_config.py content
            if 'default_config.py:' in configmap_yaml:
                idx = configmap_yaml.find('default_config.py:')
                snippet = configmap_yaml[idx:idx+500]
                if 'storage_mount_path' in snippet:
                    print('\nקטע מהקובץ (מוברח):')
                    # Find the line
                    for line in snippet.split('\\n'):
                        if 'storage_mount_path' in line:
                            print(f'>>> {line} <<<')
                            break

print('\n' + '='*70)
print('הסבר: למה יש 2 מקומות?')
print('='*70)
print()
print('1. ConfigMap ב-Kubernetes:')
print('   - זה המקור - ההגדרה נשמרת כאן')
print('   - זה מוזרק ל-pod דרך volume mount')
print('   - הנתיב: /home/prisma/pz/config/py/default_config.py')
print()
print('2. הקובץ בתוך ה-POD:')
print('   - זה העתק של ה-ConfigMap')
print('   - Focus Server קורא את הקובץ הזה בזמן הרצה')
print('   - כל שינוי ב-ConfigMap יתעדכן אוטומטית ב-pod')
print()
print('='*70)
print('איך לשנות?')
print('='*70)
print()
print('אפשרות 1: לערוך את ה-ConfigMap (מומלץ)')
print('  kubectl edit configmap prisma-config -n panda')
print('  # חפש: storage_mount_path')
print('  # שנה: /prisma/root/recordings/segy -> /prisma/root/recordings')
print()
print('אפשרות 2: לראות את הקובץ המלא בתוך POD')
print(f'  kubectl exec -n panda {pod} -- cat /home/prisma/pz/config/py/default_config.py')
print('  # זה יראה את כל הקובץ (ארוך מאוד)')

ssh.disconnect()


