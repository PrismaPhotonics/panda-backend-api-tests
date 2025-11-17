#!/usr/bin/env python3
"""
Quick runner for financial analysis.
This script will attempt to run the analysis with proper error handling.
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from analyze_credit_card_expenses import CreditCardAnalyzer
    
    print("=" * 80)
    print("מתחיל אנליזה פיננסית מעמיקה...")
    print("=" * 80)
    print()
    
    # Configuration
    data_dir = r"כרטיסי אשראי רועי"
    monthly_income = 37000
    mortgage = 10000
    current_debt = -83000
    output_file = "comprehensive_financial_analysis.txt"
    
    # Create analyzer
    analyzer = CreditCardAnalyzer(data_dir)
    
    # Generate report
    analyzer.generate_report(
        output_file=output_file,
        monthly_income=monthly_income,
        mortgage=mortgage,
        current_debt=current_debt
    )
    
    print()
    print("=" * 80)
    print(f"הדוח נשמר ב: {output_file}")
    print("=" * 80)
    
except ImportError as e:
    print(f"שגיאה בייבוא: {e}")
    print("אנא וודא ש-pandas ו-openpyxl מותקנים:")
    print("  pip install pandas openpyxl xlrd")
    sys.exit(1)
except Exception as e:
    print(f"שגיאה: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

