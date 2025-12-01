"""
Check how Focus Server finds the GUID from base_paths
"""
import sys
sys.path.insert(0, '.')
from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager
import pymongo

cm = ConfigManager()
ssh = SSHManager(cm)
ssh.connect()

print('='*70)
print('בודק איך Focus Server מוצא GUID מ-base_paths')
print('='*70)
print()

# First, check what storage_mount_path is configured
print('1. מה ה-storage_mount_path מוגדר?')
print('-'*70)
result = ssh.execute_command('kubectl exec -n panda deployment/panda-panda-focus-server -- python3 -c "from pzpy.focus_server.default_config import Config; print(Config.Focus.storage_mount_path)"')
storage_mount_path = result.get('stdout', '').strip()
print(f'storage_mount_path = {storage_mount_path}')
print()

# Check what's in MongoDB base_paths
print('2. מה יש ב-MongoDB base_paths?')
print('-'*70)
mongo_config = cm.get_database_config()
client = pymongo.MongoClient(
    host=mongo_config['host'],
    port=mongo_config['port'],
    username=mongo_config['username'],
    password=mongo_config['password'],
    authSource=mongo_config.get('auth_source', 'prisma')
)
db = client[mongo_config.get('database', 'prisma')]
base_paths = db['base_paths']

for doc in base_paths.find():
    base_path_val = doc.get('base_path', 'N/A')
    guid_val = doc.get('guid', 'N/A')
    print(f'base_path: {base_path_val}')
    print(f'guid: {guid_val}')
    print()

client.close()

# Check if Focus Server is looking for the wrong base_path
print('3. האם Focus Server מחפש base_path שמתאים ל-storage_mount_path?')
print('-'*70)
print(f'storage_mount_path = {storage_mount_path}')
print(f'base_path ב-MongoDB = /prisma/root/recordings')
print()
if storage_mount_path != '/prisma/root/recordings':
    print('❌ יש אי התאמה!')
    print(f'   Focus Server מחפש: {storage_mount_path}')
    print(f'   אבל ב-MongoDB יש: /prisma/root/recordings')
    print()
    print('🔍 הבעיה: Focus Server כנראה מחפש ב-base_paths לפי base_path')
    print('   שמתאים ל-storage_mount_path, אבל זה לא נכון!')
    print()
    print('✅ הפתרון: Focus Server צריך פשוט לקחת את ה-GUID הראשון')
    print('   מ-base_paths (או לפי base_path מסוים) בלי קשר ל-storage_mount_path')
else:
    print('✅ יש התאמה')

ssh.disconnect()

