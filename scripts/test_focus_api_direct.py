"""
Test Focus Server API directly to see what it returns
"""
import sys
sys.path.insert(0, '.')
from config.config_manager import ConfigManager
from src.apis.focus_server_api import FocusServerAPI
from datetime import datetime, timedelta
import time

cm = ConfigManager()
api = FocusServerAPI(cm)

print('='*70)
print('בודק מה Focus Server מחזיר דרך API')
print('='*70)
print()

# Get a time range from MongoDB
from be_focus_server_tests.fixtures.recording_fixtures import get_historic_time_range_from_mongodb

try:
    start_time, end_time = get_historic_time_range_from_mongodb(cm, duration_seconds=60)
    print(f'משתמש בטווח זמן מ-MongoDB:')
    print(f'  start_time: {start_time} ({datetime.fromtimestamp(start_time)})')
    print(f'  end_time: {end_time} ({datetime.fromtimestamp(end_time)})')
    print()
    
    # Try to configure historic job
    print('מנסה ליצור historic job...')
    print('-'*70)
    
    from src.models.focus_server_models import ConfigureRequest, ViewType
    
    config = ConfigureRequest(
        displayTimeAxisDuration=10,
        nfftSelection=1024,
        displayInfo={"height": 1000},
        channels={"min": 1, "max": 17},
        start_time=start_time,
        end_time=end_time,
        view_type=ViewType.MULTICHANNEL
    )
    
    try:
        response = api.configure_streaming_job(config)
        print(f'✅ הצלחה! Job ID: {response.job_id}')
        print(f'   Status: {response.status}')
    except Exception as e:
        print(f'❌ שגיאה: {e}')
        print(f'   סוג שגיאה: {type(e).__name__}')
        error_msg = str(e).lower()
        if "no recording found" in error_msg:
            print()
            print('='*70)
            print('🔍 הבעיה: Focus Server לא מוצא recordings!')
            print('='*70)
            print(f'   MongoDB GUID: 25b4875f-5785-4b24-8895-121039474bcd')
            print(f'   יש 41,244 recordings מושלמים ב-collection הזה')
            print(f'   אבל Focus Server לא מוצא אותם!')
            print()
            print('   זה אומר ש-Focus Server לא משתמש ב-GUID הנכון')
            print('   או שהוא מחפש ב-collection הלא נכון')
        
except Exception as e:
    print(f'❌ שגיאה בקבלת טווח זמן: {e}')
    import traceback
    traceback.print_exc()

