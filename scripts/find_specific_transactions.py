#!/usr/bin/env python3
"""
Find specific transactions in credit card files.
Search for duplicate/recurring charges by date and amount.
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
    print("חיפוש עסקאות ספציפיות - חיובים כפולים/חוזרים")
    print("=" * 80)
    print()
    
    # Target transactions to find
    target_transactions = [
        {'date': '28-04-2023', 'amount': 7143, 'count': 3},
        {'date': '05-11-2025', 'amount': 6810, 'count': 2},
        {'date': '30-10-2025', 'amount': 6810, 'count': 2},
        {'date': '02.09.25', 'amount': 4390, 'count': 2},
    ]
    
    # Also search for similar amounts
    similar_amounts = {
        7143: [7100, 7200],  # Around 7143
        6810: [6800, 6900],  # Around 6810
        4390: [4350, 4450],   # Around 4390
    }
    
    found_transactions = []
    
    for transaction in analyzer.transactions:
        amount = abs(transaction.get('amount', 0))
        date = transaction.get('date')
        description = transaction.get('description', '')
        file_name = transaction.get('file', '')
        
        # Check each target
        for target in target_transactions:
            target_date = target['date']
            target_amount = target['amount']
            
            # Check if date matches (flexible matching)
            date_match = False
            if date:
                date_str = str(date)
                # Try different date formats
                if target_date in date_str or date_str in target_date:
                    date_match = True
                # Also check if it's the same date in different format
                if target_date.replace('-', '').replace('.', '') in date_str.replace('-', '').replace('.', ''):
                    date_match = True
            
            # Check if amount matches (within 100 ILS)
            amount_match = False
            if abs(amount - target_amount) < 100:
                amount_match = True
            # Also check similar amounts
            if target_amount in similar_amounts:
                for similar in similar_amounts[target_amount]:
                    if abs(amount - similar) < 100:
                        amount_match = True
                        break
            
            if date_match and amount_match:
                found_transactions.append({
                    'target': target,
                    'transaction': transaction,
                    'amount': amount,
                    'date': date,
                    'description': description,
                    'file': file_name
                })
    
    # Group by target
    from collections import defaultdict
    grouped = defaultdict(list)
    for item in found_transactions:
        key = f"{item['target']['date']}_{item['target']['amount']}"
        grouped[key].append(item)
    
    # Print results
    for target in target_transactions:
        key = f"{target['date']}_{target['amount']}"
        matches = grouped.get(key, [])
        
        print(f"חיפוש: {target['date']} - {target['amount']:,.0f} ILS ({target['count']} פעמים)")
        print("-" * 80)
        
        if matches:
            print(f"נמצאו {len(matches)} עסקאות תואמות:")
            print()
            
            # Group by file (credit card)
            by_file = defaultdict(list)
            for match in matches:
                by_file[match['file']].append(match)
            
            for file_name, file_transactions in by_file.items():
                print(f"כרטיס אשראי: {file_name}")
                print(f"   נמצאו {len(file_transactions)} עסקאות בכרטיס זה")
                print()
                
                for i, match in enumerate(file_transactions, 1):
                    print(f"   {i}. תאריך: {match['date']}")
                    print(f"      סכום: {match['amount']:,.0f} ILS")
                    print(f"      תיאור: {match['description'][:80]}")
                    print()
        else:
            print("לא נמצאו עסקאות תואמות")
            print("מחפש עסקאות דומות...")
            
            # Search for similar amounts regardless of date
            similar_found = []
            for transaction in analyzer.transactions:
                amount = abs(transaction.get('amount', 0))
                if abs(amount - target['amount']) < 100:
                    similar_found.append(transaction)
            
            if similar_found:
                print(f"נמצאו {len(similar_found)} עסקאות בסכום דומה ({target['amount']:,.0f} ILS):")
                by_file = defaultdict(list)
                for txn in similar_found:
                    by_file[txn.get('file', '')].append(txn)
                
                for file_name, file_transactions in by_file.items():
                    print(f"   {file_name}: {len(file_transactions)} עסקאות")
                    for txn in file_transactions[:3]:  # Show first 3
                        print(f"      - {txn.get('date')}: {txn.get('description', '')[:60]}")
        
        print()
        print("=" * 80)
        print()
    
    # Summary
    print("סיכום:")
    print("-" * 80)
    total_found = len(found_transactions)
    print(f"סה\"כ עסקאות שנמצאו: {total_found}")
    
    if total_found > 0:
        by_file_summary = defaultdict(int)
        for item in found_transactions:
            by_file_summary[item['file']] += 1
        
        print("\nפילוח לפי כרטיסי אשראי:")
        for file_name, count in sorted(by_file_summary.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {file_name}: {count} עסקאות")
    
    # Save to file
    output_file = Path("duplicate_charges_details.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("פירוט חיובים כפולים/חוזרים - לפי כרטיסי אשראי\n")
        f.write("=" * 80 + "\n\n")
        
        for target in target_transactions:
            key = f"{target['date']}_{target['amount']}"
            matches = grouped.get(key, [])
            
            f.write(f"חיפוש: {target['date']} - {target['amount']:,.0f} ILS ({target['count']} פעמים)\n")
            f.write("-" * 80 + "\n")
            
            if matches:
                f.write(f"נמצאו {len(matches)} עסקאות תואמות:\n\n")
                
                by_file = defaultdict(list)
                for match in matches:
                    by_file[match['file']].append(match)
                
                for file_name, file_transactions in by_file.items():
                    f.write(f"כרטיס אשראי: {file_name}\n")
                    f.write(f"   נמצאו {len(file_transactions)} עסקאות בכרטיס זה\n\n")
                    
                    for i, match in enumerate(file_transactions, 1):
                        f.write(f"   {i}. תאריך: {match['date']}\n")
                        f.write(f"      סכום: {match['amount']:,.0f} ILS\n")
                        f.write(f"      תיאור: {match['description']}\n\n")
            else:
                f.write("לא נמצאו עסקאות תואמות\n")
            
            f.write("=" * 80 + "\n\n")
        
        f.write("סיכום:\n")
        f.write("-" * 80 + "\n")
        f.write(f"סה\"כ עסקאות שנמצאו: {total_found}\n\n")
        
        if total_found > 0:
            by_file_summary = defaultdict(int)
            for item in found_transactions:
                by_file_summary[item['file']] += 1
            
            f.write("פילוח לפי כרטיסי אשראי:\n")
            for file_name, count in sorted(by_file_summary.items(), key=lambda x: x[1], reverse=True):
                f.write(f"  - {file_name}: {count} עסקאות\n")
    
    print(f"\nהתוצאות נשמרו לקובץ: {output_file}")

if __name__ == '__main__':
    main()

