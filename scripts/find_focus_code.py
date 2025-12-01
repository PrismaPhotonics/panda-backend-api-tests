"""Find Focus Server code location."""
import sys
sys.path.insert(0, '.')
from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager

cm = ConfigManager()
ssh = SSHManager(cm)
ssh.connect()

pod = 'panda-panda-focus-server-7c767d7688-z6n5p'

# Find Python files
print('='*70)
print('PYTHON FILES IN /home/prisma')
print('='*70)
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- find /home/prisma -name "*.py" -type f 2>/dev/null | head -40')
print(result.get('stdout', '') or 'No .py files')

# Home directory
print('\n' + '='*70)
print('HOME DIRECTORY')
print('='*70)
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- ls -la /home/prisma/')
print(result.get('stdout', ''))

# PZ directory
print('\n' + '='*70)
print('PZ DIRECTORY')
print('='*70)
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- ls -la /home/prisma/pz/ 2>/dev/null')
print(result.get('stdout', '') or 'No pz dir')

# Check site-packages for focus_server
print('\n' + '='*70)
print('SITE-PACKAGES - FOCUS SERVER')
print('='*70)
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- find / -path "*/site-packages/pz*" -type d 2>/dev/null | head -10')
print(result.get('stdout', '') or 'Not found')

# Check running process
print('\n' + '='*70)
print('RUNNING PROCESS')
print('='*70)
result = ssh.execute_command(f'kubectl exec -n panda {pod} -- ps aux | grep python')
print(result.get('stdout', ''))

ssh.disconnect()


