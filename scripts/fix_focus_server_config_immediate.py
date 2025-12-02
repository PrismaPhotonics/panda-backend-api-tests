"""
תיקון מיידי של Focus Server ConfigMap - משנה storage_mount_path ל-/prisma/root/recordings
"""
import sys
sys.path.insert(0, '.')
import tempfile
import os
from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager

def fix_configmap():
    print('='*80)
    print('🔧 תיקון מיידי של Focus Server ConfigMap')
    print('='*80)
    print()
    
    cm = ConfigManager()
    ssh = SSHManager(cm)
    
    if not ssh.connect():
        print('❌ נכשל בחיבור SSH')
        return False
    
    try:
        # 1. הורדת ה-ConfigMap
        print('📥 מוריד ConfigMap...')
        result = ssh.execute_command('kubectl get configmap prisma-config -n panda -o yaml')
        configmap_yaml = result.get('stdout', '')
        
        if not configmap_yaml:
            print('❌ לא הצלחתי להוריד את ה-ConfigMap')
            return False
        
        # 2. החלפת הערך
        print('✏️  מעדכן את storage_mount_path...')
        
        # נסה כל הוריאציות האפשריות
        replacements = [
            ("storage_mount_path = '/prisma/root/recordings/segy'", 
             "storage_mount_path = '/prisma/root/recordings'"),
            ("storage_mount_path = \\'/prisma/root/recordings/segy\\'", 
             "storage_mount_path = \\'/prisma/root/recordings\\'"),
            ('storage_mount_path = "/prisma/root/recordings/segy"', 
             'storage_mount_path = "/prisma/root/recordings"'),
            ("storage_mount_path='/prisma/root/recordings/segy'", 
             "storage_mount_path='/prisma/root/recordings'"),
        ]
        
        updated = False
        for old_val, new_val in replacements:
            if old_val in configmap_yaml:
                configmap_yaml = configmap_yaml.replace(old_val, new_val)
                updated = True
                print(f'✅ מצאתי והחלפתי: {old_val[:50]}...')
                break
        
        if not updated:
            print('⚠️  לא מצאתי את הערך לשינוי!')
            print('בודק אם כבר מתוקן...')
            if '/prisma/root/recordings' in configmap_yaml and '/segy' not in configmap_yaml:
                print('✅ נראה שהקונפיגורציה כבר מתוקנת!')
                return True
            else:
                print('❌ לא מצאתי את הערך לשינוי')
                return False
        
        # 3. שמירה לקובץ זמני
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            f.write(configmap_yaml)
            temp_file = f.name
        
        # 4. העלאת הקובץ ל-server ועדכון ConfigMap
        print('📤 מעדכן את ConfigMap ב-Kubernetes...')
        remote_file = f'/tmp/prisma-config-fix-{os.getpid()}.yaml'
        
        # קריאת הקובץ והעברתו דרך SSH
        with open(temp_file, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        # כתיבה ל-server
        write_cmd = f'cat > {remote_file} << \'EOF\'\n{file_content}\nEOF'
        result = ssh.execute_command(write_cmd)
        
        if result.get('stderr') and 'error' in result.get('stderr', '').lower():
            print(f'⚠️  אזהרה בכתיבה: {result.get("stderr")[:200]}')
        
        # עדכון ה-ConfigMap
        apply_cmd = f'kubectl apply -f {remote_file}'
        result = ssh.execute_command(apply_cmd)
        
        if result.get('stderr') and 'error' in result.get('stderr', '').lower():
            print(f'❌ שגיאה בעדכון: {result.get("stderr")}')
            return False
        
        print('✅ ConfigMap עודכן בהצלחה!')
        
        # 5. ניקוי
        ssh.execute_command(f'rm -f {remote_file}')
        os.unlink(temp_file)
        
        # 6. Restart ה-pod
        print('🔄 מפעיל מחדש את Focus Server pod...')
        restart_cmd = 'kubectl rollout restart deployment panda-panda-focus-server -n panda'
        result = ssh.execute_command(restart_cmd)
        
        if result.get('stderr') and 'error' in result.get('stderr', '').lower():
            print(f'⚠️  אזהרה: {result.get("stderr")}')
        else:
            print('✅ Pod restart הוזמן')
        
        print()
        print('='*80)
        print('✅ התיקון הושלם בהצלחה!')
        print('='*80)
        print()
        print('📋 מה בוצע:')
        print('   1. ✅ עודכן storage_mount_path ל-/prisma/root/recordings')
        print('   2. ✅ ConfigMap עודכן ב-Kubernetes')
        print('   3. ✅ Focus Server pod יופעל מחדש')
        print()
        print('⏱️  זה יכול לקחת 1-2 דקות עד שה-pod יעלה מחדש')
        print()
        print('🔍 לבדיקה:')
        print('   kubectl get pods -n panda | grep focus-server')
        print('   kubectl logs -n panda deployment/panda-panda-focus-server --tail=50')
        
        return True
        
    except Exception as e:
        print(f'❌ שגיאה: {e}')
        import traceback
        traceback.print_exc()
        return False
    finally:
        ssh.disconnect()

if __name__ == '__main__':
    success = fix_configmap()
    sys.exit(0 if success else 1)

