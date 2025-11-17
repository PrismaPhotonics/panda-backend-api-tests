#!/usr/bin/env python3
"""
Inspect specific transaction files to see full details.
"""

import pandas as pd
from pathlib import Path

def main():
    data_dir = Path(r"כרטיסי אשראי רועי")
    
    # Files with 6,810 ILS charges
    target_files = [
        'transaction-details_export_1762890555383.xlsx',
        'transaction-details_export_1762890572657.xlsx'
    ]
    
    print("=" * 80)
    print("בדיקת קבצי כרטיסי אשראי - חיובים של 6,810 ILS")
    print("=" * 80)
    print()
    
    for file_name in target_files:
        file_path = data_dir / file_name
        if not file_path.exists():
            print(f"קובץ לא נמצא: {file_name}")
            continue
        
        print(f"קובץ: {file_name}")
        print("-" * 80)
        
        try:
            df = pd.read_excel(file_path)
            print(f"שורות: {len(df)}, עמודות: {len(df.columns)}")
            print(f"שמות עמודות: {list(df.columns)}")
            print()
            
            # Show all data
            print("כל הנתונים:")
            print(df.to_string())
            print()
            print("=" * 80)
            print()
            
        except Exception as e:
            print(f"שגיאה בקריאת הקובץ: {e}")
            print()

if __name__ == '__main__':
    main()

