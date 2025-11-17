#!/usr/bin/env python3
"""
Find mortgage payments in transaction data.
Look for monthly payments around 10,000 ILS.
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from analyze_credit_card_expenses import CreditCardAnalyzer

def main():
    data_dir = Path(r"כרטיסי אשראי רועי")
    
    analyzer = CreditCardAnalyzer(data_dir)
    analyzer.load_all_transactions()
    
    print("=" * 80)
    print("חיפוש תשלומי משכנתא בעסקאות")
    print("=" * 80)
    print()
    
    # Look for transactions around 10,000 ILS (mortgage payment)
    mortgage_keywords = ['משכנתא', 'mortgage', 'משכנת', 'ריבית משכנתא', 'בית', 'דירה']
    
    # Filter transactions
    mortgage_candidates = []
    
    for transaction in analyzer.transactions:
        amount = abs(transaction.get('amount', 0))
        description = str(transaction.get('description', '')).lower()
        
        # Check if amount is around 10,000 (mortgage payment)
        if 9000 <= amount <= 11000:
            # Check if description contains mortgage keywords
            has_mortgage_keyword = any(keyword in description for keyword in mortgage_keywords)
            
            mortgage_candidates.append({
                'date': transaction.get('date'),
                'amount': amount,
                'description': transaction.get('description'),
                'has_keyword': has_mortgage_keyword,
                'file': transaction.get('file')
            })
    
    if mortgage_candidates:
        print(f"נמצאו {len(mortgage_candidates)} עסקאות שעשויות להיות תשלומי משכנתא:")
        print()
        
        # Group by amount
        from collections import defaultdict
        by_amount = defaultdict(list)
        for candidate in mortgage_candidates:
            by_amount[round(candidate['amount'], -2)].append(candidate)
        
        for amount, transactions in sorted(by_amount.items(), reverse=True):
            print(f"סכום: {amount:,.0f} ₪ ({len(transactions)} עסקאות)")
            for txn in transactions[:5]:  # Show first 5
                keyword_marker = "✓" if txn['has_keyword'] else " "
                print(f"  {keyword_marker} {txn['date']}: {txn['description'][:60]} ({txn['file']})")
            if len(transactions) > 5:
                print(f"  ... ועוד {len(transactions) - 5} עסקאות")
            print()
    else:
        print("לא נמצאו עסקאות של בערך 10,000 ₪ שעשויות להיות תשלומי משכנתא")
        print()
    
    # Also check for recurring payments around 10,000
    print("=" * 80)
    print("בדיקת תשלומים חוזרים של בערך 10,000 ₪")
    print("=" * 80)
    print()
    
    # Group transactions by amount (rounded to nearest 100)
    from collections import defaultdict
    by_amount = defaultdict(list)
    
    for transaction in analyzer.transactions:
        amount = abs(transaction.get('amount', 0))
        if 9000 <= amount <= 11000:
            rounded_amount = round(amount, -2)
            by_amount[rounded_amount].append(transaction)
    
    recurring_payments = {amt: txns for amt, txns in by_amount.items() if len(txns) >= 2}
    
    if recurring_payments:
        print("תשלומים חוזרים של בערך 10,000 ₪:")
        for amount, transactions in sorted(recurring_payments.items(), reverse=True):
            print(f"\n{amount:,.0f} ₪ - {len(transactions)} פעמים:")
            for txn in transactions[:6]:
                print(f"  {txn.get('date')}: {txn.get('description', '')[:70]}")
            if len(transactions) > 6:
                print(f"  ... ועוד {len(transactions) - 6} עסקאות")
    else:
        print("לא נמצאו תשלומים חוזרים של בערך 10,000 ₪")
    
    print()
    print("=" * 80)
    print("סיכום:")
    print("=" * 80)
    print(f"סה\"כ עסקאות שנטענו: {len(analyzer.transactions)}")
    print(f"עסקאות של בערך 10,000 ₪: {len(mortgage_candidates)}")
    print()
    print("הערה: המשכנתא עשויה להיות:")
    print("  1. חלק מההלוואות שזוהו (513,000 או 339,000)")
    print("  2. תשלום חודשי של 10,000 ₪ שלא מופיע בקבצי ה-PDF")
    print("  3. בחשבון בנק אחר שלא נסרק")

if __name__ == '__main__':
    main()

