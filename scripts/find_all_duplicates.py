#!/usr/bin/env python3
"""
Find all duplicate/recurring charges and show which credit card they're on.
"""

import sys
from pathlib import Path
from collections import defaultdict

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from analyze_credit_card_expenses import CreditCardAnalyzer

def main():
    data_dir = Path(r"כרטיסי אשראי רועי")
    
    analyzer = CreditCardAnalyzer(data_dir)
    analyzer.load_all_transactions()
    
    print("=" * 80)
    print("חיפוש כל החיובים הכפולים/חוזרים - לפי כרטיס אשראי")
    print("=" * 80)
    print()
    
    # Group transactions by description (merchant) and amount
    duplicates = defaultdict(list)
    
    for transaction in analyzer.transactions:
        if transaction.get('is_expense', False):
            amount = abs(transaction.get('amount', 0))
            description = str(transaction.get('description', '')).strip()
            date = transaction.get('date')
            file_name = transaction.get('file', '')
            
            if amount > 0 and description:
                # Create key: description + rounded amount
                key = (description.lower(), round(amount, -2))  # Round to nearest 100
                duplicates[key].append({
                    'amount': amount,
                    'date': date,
                    'description': description,
                    'file': file_name
                })
    
    # Find duplicates (more than one transaction with same key)
    duplicate_groups = []
    for key, transactions in duplicates.items():
        if len(transactions) > 1:
            total_amount = sum(t['amount'] for t in transactions)
            if total_amount > 500:  # Only significant amounts
                duplicate_groups.append({
                    'description': key[0],
                    'amount': key[1],
                    'count': len(transactions),
                    'total_amount': total_amount,
                    'transactions': transactions
                })
    
    # Sort by total amount
    duplicate_groups.sort(key=lambda x: x['total_amount'], reverse=True)
    
    # Save to file
    output_file = Path("all_duplicate_charges_by_card.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("כל החיובים הכפולים/חוזרים - לפי כרטיס אשראי\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"נמצאו {len(duplicate_groups)} קבוצות של חיובים כפולים/חוזרים\n\n")
        
        for i, group in enumerate(duplicate_groups[:30], 1):  # Top 30
            f.write(f"{i}. {group['description'][:60]}\n")
            f.write(f"   סכום: {group['amount']:,.0f} ILS\n")
            f.write(f"   מספר פעמים: {group['count']}\n")
            f.write(f"   סה\"כ: {group['total_amount']:,.0f} ILS\n")
            f.write(f"   ממוצע: {group['total_amount'] / group['count']:,.0f} ILS\n")
            f.write("\n")
            
            # Group by credit card
            by_card = defaultdict(list)
            for txn in group['transactions']:
                by_card[txn['file']].append(txn)
            
            f.write("   פילוח לפי כרטיסי אשראי:\n")
            for card_file, card_transactions in sorted(by_card.items()):
                f.write(f"      - {card_file}: {len(card_transactions)} עסקאות\n")
                for txn in card_transactions:
                    f.write(f"        * תאריך: {txn['date']}, סכום: {txn['amount']:,.0f} ILS\n")
            f.write("\n")
            f.write("-" * 80 + "\n\n")
        
        # Summary by card
        f.write("\n" + "=" * 80 + "\n")
        f.write("סיכום לפי כרטיס אשראי\n")
        f.write("=" * 80 + "\n\n")
        
        by_card_summary = defaultdict(lambda: {'count': 0, 'total': 0})
        for group in duplicate_groups:
            for txn in group['transactions']:
                card = txn['file']
                by_card_summary[card]['count'] += 1
                by_card_summary[card]['total'] += txn['amount']
        
        for card, stats in sorted(by_card_summary.items(), key=lambda x: x[1]['total'], reverse=True):
            f.write(f"{card}:\n")
            f.write(f"  - {stats['count']} עסקאות כפולות/חוזרות\n")
            f.write(f"  - סה\"כ: {stats['total']:,.0f} ILS\n\n")
    
    print(f"נמצאו {len(duplicate_groups)} קבוצות של חיובים כפולים/חוזרים")
    print(f"התוצאות נשמרו לקובץ: {output_file}")
    
    # Also print top 10
    print("\n10 החיובים הכפולים/חוזרים הגדולים ביותר:")
    print("-" * 80)
    for i, group in enumerate(duplicate_groups[:10], 1):
        print(f"{i}. {group['description'][:50]}")
        print(f"   {group['count']} פעמים, {group['amount']:,.0f} ILS כל פעם, סה\"כ {group['total_amount']:,.0f} ILS")
        
        # Show which cards
        cards = set(txn['file'] for txn in group['transactions'])
        print(f"   כרטיסים: {', '.join(cards)}")
        print()

if __name__ == '__main__':
    main()

