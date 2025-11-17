#!/usr/bin/env python3
"""
Check for real duplicate charges (between different credit cards, not duplicate files).
"""

import sys
from pathlib import Path
import re

sys.path.insert(0, str(Path(__file__).parent))

from analyze_credit_card_expenses import CreditCardAnalyzer

def main():
    data_dir = Path(r"כרטיסי אשראי רועי")
    
    analyzer = CreditCardAnalyzer(data_dir)
    analyzer.load_all_transactions()
    
    print("=" * 80)
    print("חיובים כפולים אמיתיים - רק בין כרטיסים שונים")
    print("=" * 80)
    print()
    print(f"סה\"כ עסקאות שנטענו: {len(analyzer.transactions)}")
    print()
    
    # Analyze
    analysis = analyzer.analyze_expenses()
    
    duplicate_charges = analysis.get('duplicate_charges', [])
    
    print(f"חיובים כפולים אמיתיים שזוהו: {len(duplicate_charges)}")
    print()
    print("-" * 80)
    print()
    
    if duplicate_charges:
        total_duplicates = sum(d['total_amount'] for d in duplicate_charges)
        print(f"סה\"כ חיובים כפולים אמיתיים: {total_duplicates:,.0f} ILS")
        print()
        
        for i, dup in enumerate(duplicate_charges, 1):
            print(f"{i}. {dup['description'][:60]}")
            print(f"   סכום: {dup['avg_amount']:,.0f} ILS")
            print(f"   מספר פעמים: {dup['count']}")
            print(f"   סה\"כ: {dup['total_amount']:,.0f} ILS")
            if dup.get('files'):
                print(f"   כרטיסי אשראי: {', '.join(dup['files'])}")
            if dup.get('dates'):
                dates_str = ', '.join([str(d) for d in dup['dates'][:3]])
                print(f"   תאריכים: {dates_str}")
            print()
    else:
        print("לא נמצאו חיובים כפולים אמיתיים בין כרטיסים שונים")
        print()
        print("זה אומר שרוב החיובים הכפולים היו בגלל קבצים כפולים,")
        print("לא חיובים כפולים אמיתיים!")

if __name__ == '__main__':
    main()

