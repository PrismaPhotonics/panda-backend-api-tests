"""
סקריפט לתיקון storage_mount_path ב-ConfigMap
"""
import sys
sys.path.insert(0, '.')
import subprocess
import tempfile
import os
from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager

def main():
    print('='*70)
    print('תיקון storage_mount_path ב-ConfigMap')
    print('='*70)
    print()
    print('הבעיה:')
    print('  storage_mount_path = \'/prisma/root/recordings/segy\'')
    print()
    print('התיקון:')
    print('  storage_mount_path = \'/prisma/root/recordings\'')
    print()
    
    response = input('האם להמשיך עם התיקון? (yes/no): ')
    if response.lower() != 'yes':
        print('בוטל.')
        return
    
    cm = ConfigManager()
    ssh = SSHManager(cm)
    
    if not ssh.connect():
        print('❌ נכשל בחיבור SSH')
        return
    
    try:
        # 1. הורדת ה-ConfigMap הנוכחי
        print('\n' + '='*70)
        print('שלב 1: הורדת ConfigMap נוכחי')
        print('='*70)
        
        result = ssh.execute_command('kubectl get configmap prisma-config -n panda -o yaml')
        configmap_yaml = result.get('stdout', '')
        
        if not configmap_yaml:
            print('❌ לא הצלחתי להוריד את ה-ConfigMap')
            return
        
        # 2. שמירה לקובץ זמני
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(configmap_yaml)
            temp_file = f.name
        
        print(f'✅ ConfigMap נשמר ל: {temp_file}')
        
        # 3. עריכת הקובץ
        print('\n' + '='*70)
        print('שלב 2: עריכת הקובץ')
        print('='*70)
        
        with open(temp_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # החלפת ההגדרה
        old_value = "storage_mount_path = '/prisma/root/recordings/segy'"
        new_value = "storage_mount_path = '/prisma/root/recordings'"
        
        if old_value not in content:
            print(f'⚠️  לא מצאתי את הערך: {old_value}')
            print('בואו נחפש וריאציות...')
            
            # נסה למצוא את זה גם עם escape
            old_value_escaped = "storage_mount_path = \\'/prisma/root/recordings/segy\\'"
            if old_value_escaped in content:
                content = content.replace(old_value_escaped, 
                                         "storage_mount_path = \\'/prisma/root/recordings\\'")
                print('✅ מצאתי והחלפתי (עם escape)')
            else:
                # נסה עם double quotes
                old_value_double = 'storage_mount_path = "/prisma/root/recordings/segy"'
                new_value_double = 'storage_mount_path = "/prisma/root/recordings"'
                if old_value_double in content:
                    content = content.replace(old_value_double, new_value_double)
                    print('✅ מצאתי והחלפתי (עם double quotes)')
                else:
                    print('❌ לא מצאתי את הערך לשינוי!')
                    print('הקובץ נשמר ל:', temp_file)
                    print('אנא ערוך אותו ידנית.')
                    return
        else:
            content = content.replace(old_value, new_value)
            print('✅ הערך הוחלף בהצלחה')
        
        # 4. שמירת הקובץ המעודכן
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f'✅ הקובץ המעודכן נשמר')
        
        # 5. העלאת הקובץ המעודכן ל-Kubernetes
        print('\n' + '='*70)
        print('שלב 3: עדכון ConfigMap ב-Kubernetes')
        print('='*70)
        
        # העתקת הקובץ ל-server
        remote_file = f'/tmp/prisma-config-{os.getpid()}.yaml'
        
        # קריאת הקובץ והעברתו דרך SSH
        with open(temp_file, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        # כתיבה ל-server
        write_cmd = f'cat > {remote_file} << "EOF"\n{file_content}\nEOF'
        result = ssh.execute_command(write_cmd)
        
        if result.get('stderr'):
            print(f'⚠️  אזהרה: {result.get("stderr")[:200]}')
        
        # עדכון ה-ConfigMap
        apply_cmd = f'kubectl apply -f {remote_file}'
        result = ssh.execute_command(apply_cmd)
        
        if result.get('stderr') and 'error' in result.get('stderr', '').lower():
            print(f'❌ שגיאה בעדכון: {result.get("stderr")}')
            return
        
        print('✅ ConfigMap עודכן בהצלחה!')
        
        # 6. ניקוי
        ssh.execute_command(f'rm -f {remote_file}')
        os.unlink(temp_file)
        
        # 7. restart ה-pod
        print('\n' + '='*70)
        print('שלב 4: Restart של Focus Server pod')
        print('='*70)
        
        restart_cmd = 'kubectl rollout restart deployment panda-panda-focus-server -n panda'
        result = ssh.execute_command(restart_cmd)
        
        if result.get('stderr') and 'error' in result.get('stderr', '').lower():
            print(f'⚠️  אזהרה: {result.get("stderr")}')
        else:
            print('✅ Pod restart הוזמן')
        
        print('\n' + '='*70)
        print('✅ התיקון הושלם!')
        print('='*70)
        print()
        print('הערות:')
        print('1. ה-pod יתחיל מחדש אוטומטית')
        print('2. זה יכול לקחת 1-2 דקות')
        print('3. לבדוק שהכל עובד:')
        print('   kubectl get pods -n panda | grep focus-server')
        print('4. לבדוק שה-API עובד:')
        print('   kubectl exec -n panda <pod-name> -- cat /home/prisma/pz/config/py/default_config.py | grep storage_mount_path')
        
    except Exception as e:
        print(f'❌ שגיאה: {e}')
        import traceback
        traceback.print_exc()
    finally:
        ssh.disconnect()

if __name__ == '__main__':
    main()


