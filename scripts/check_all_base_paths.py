"""
Check all base_paths in MongoDB and their GUID collections
"""
import sys
sys.path.insert(0, '.')
from config.config_manager import ConfigManager
import pymongo

cm = ConfigManager()
mongo_config = cm.get_database_config()

client = pymongo.MongoClient(
    host=mongo_config['host'],
    port=mongo_config['port'],
    username=mongo_config['username'],
    password=mongo_config['password'],
    authSource=mongo_config.get('auth_source', 'prisma')
)

db = client[mongo_config.get('database', 'prisma')]

print('='*70)
print('כל ה-base_paths ב-MongoDB:')
print('='*70)
base_paths = db['base_paths']
all_base_paths = list(base_paths.find())
print(f'סה"כ {len(all_base_paths)} base_paths')
print()

for i, doc in enumerate(all_base_paths, 1):
    base_path_val = doc.get('base_path', 'N/A')
    guid_val = doc.get('guid', 'N/A')
    is_archive_val = doc.get('is_archive', 'N/A')
    print(f'{i}. base_path: {base_path_val}')
    print(f'   guid: {guid_val}')
    print(f'   is_archive: {is_archive_val}')
    guid = doc.get('guid')
    if guid:
        collection = db[str(guid)]
        total = collection.count_documents({})
        completed = collection.count_documents({'deleted': False, 'end_time': {'$ne': None}})
        print(f'   recordings: {completed} מושלמים מתוך {total} סה"כ')
    print()

print('='*70)
print('בודק אילו collections יש ב-MongoDB (רק GUIDs):')
print('='*70)
all_collections = db.list_collection_names()
guid_collections = [c for c in all_collections if len(c) == 36 and c.count('-') == 4]
print(f'סה"כ {len(guid_collections)} collections עם GUID format')
for guid_col in guid_collections[:10]:  # Show first 10
    collection = db[guid_col]
    total = collection.count_documents({})
    completed = collection.count_documents({'deleted': False, 'end_time': {'$ne': None}})
    if total > 0:
        print(f'  {guid_col}: {completed} מושלמים מתוך {total} סה"כ')

client.close()

