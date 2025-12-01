"""Explain what Focus Server Config is and where it comes from."""
import sys
sys.path.insert(0, '.')
from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager

cm = ConfigManager()
ssh = SSHManager(cm)
ssh.connect()

pod = 'panda-panda-focus-server-7c767d7688-z6n5p'

print('='*70)
print('מה זה Focus Server Config?')
print('='*70)
print('זה קובץ Python configuration שנטען בזמן הרצה של Focus Server')
print('הוא מכיל את כל ההגדרות של המערכת (MongoDB, RabbitMQ, storage paths, וכו\')')
print()

print('='*70)
print('איפה הקובץ נמצא?')
print('='*70)
print('נתיב: /home/prisma/pz/config/py/..2025_12_01_13_02_15.3195021161/default_config.py')
print('זה קובץ בתוך ה-pod של Focus Server')
print()

result = ssh.execute_command('kubectl exec -n panda ' + pod + ' -- ls -la /home/prisma/pz/config/py/')
print(result.get('stdout', '') or 'Not found')

print('\n' + '='*70)
print('תוכן הקובץ - חלק Focus (ההגדרה הרלוונטית)')
print('='*70)
config_path = '/home/prisma/pz/config/py/..2025_12_01_13_02_15.3195021161/default_config.py'
result = ssh.execute_command('kubectl exec -n panda ' + pod + ' -- cat ' + config_path + ' 2>/dev/null | grep -A 20 "class Focus"')
print(result.get('stdout', '') or 'Not found')

print('\n' + '='*70)
print('איך Focus Server משתמש בזה?')
print('='*70)
print('ב-focus_manager.py, בשורה:')
print('  self.mongo_mapper = RecordingMongoMapper(self.storage_path)')
print('כאשר storage_path = Config.Focus.storage_mount_path')
print()

fs_path = '/home/prisma/.local/lib/python3.10/site-packages/focus_server'
result = ssh.execute_command('kubectl exec -n panda ' + pod + ' -- grep -B 5 -A 3 "storage_mount_path" ' + fs_path + '/focus_manager.py 2>/dev/null')
print(result.get('stdout', '') or 'Not found')

print('\n' + '='*70)
print('מאיפה הקובץ הזה מגיע?')
print('='*70)
print('1. זה חלק מ-ConfigMap או Volume ב-Kubernetes')
print('2. הוא מוזרק ל-pod בזמן ה-deployment')
print('3. הוא מכיל את כל ההגדרות הספציפיות לסביבה (staging/production)')
print()

print('='*70)
print('הבעיה שמצאנו:')
print('='*70)
print('storage_mount_path = \'/prisma/root/recordings/segy\'  <-- זה מה שמוגדר')
print('אבל ההקלטות נמצאות ב: /prisma/root/recordings')
print('לכן Focus Server מחפש ב-collection הלא נכונה!')

ssh.disconnect()


