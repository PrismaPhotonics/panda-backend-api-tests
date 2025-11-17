#!/usr/bin/env python3
"""
Debug column detection for transaction files.
"""

import pandas as pd
from pathlib import Path

def main():
    data_dir = Path(r"כרטיסי אשראי רועי")
    file_name = 'transaction-details_export_1762890555383.xlsx'
    file_path = data_dir / file_name
    
    print("=" * 80)
    print(f"בדיקת זיהוי עמודות - {file_name}")
    print("=" * 80)
    print()
    
    # Try reading with header
    df = pd.read_excel(file_path, header=None)
    
    print("שורות ראשונות (ללא header):")
    print(df.head(10).to_string())
    print()
    
    # Check row 2 (index 1) - might be header
    print("שורה 2 (אולי header):")
    print(df.iloc[1])
    print()
    
    # Try reading with header in row 2
    df_with_header = pd.read_excel(file_path, header=1)
    
    print("שמות עמודות (עם header בשורה 2):")
    for i, col in enumerate(df_with_header.columns):
        print(f"  {i}: {col}")
    print()
    
    print("שורות ראשונות (עם header):")
    print(df_with_header.head(5).to_string())
    print()
    
    # Check each column
    print("בדיקת כל עמודה:")
    print("-" * 80)
    for col in df.columns:
        print(f"\nעמודה: {col}")
        print(f"  סוג: {df[col].dtype}")
        sample = df[col].dropna().head(5)
        print(f"  דוגמאות: {list(sample)}")
        
        # Try to convert to numeric
        try:
            numeric = pd.to_numeric(df[col], errors='coerce')
            valid = numeric.notna()
            if valid.sum() > 0:
                valid_values = numeric[valid]
                print(f"  ערכים מספריים: {list(valid_values.head(5))}")
                print(f"  טווח: {valid_values.min():.2f} - {valid_values.max():.2f}")
        except:
            pass

if __name__ == '__main__':
    main()

