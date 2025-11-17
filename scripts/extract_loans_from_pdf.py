#!/usr/bin/env python3
"""
Extract loan information from specific PDF files.
Focus on tnuot.pdf files which contain bank statements.
"""

import sys
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    try:
        import PyPDF2
    except ImportError:
        print("Please install pdfplumber or PyPDF2: pip install pdfplumber PyPDF2")
        sys.exit(1)

def extract_text_from_pdf(file_path):
    """Extract text from PDF file."""
    text = ""
    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except:
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() or ""
        except Exception as e:
            print(f"Error reading {file_path.name}: {e}")
    return text

def extract_loan_info(text):
    """Extract loan information from bank statement text."""
    import re
    
    loan_info = {
        'loan_balance': None,
        'monthly_payment': None,
        'account_number': None,
        'large_amounts': []
    }
    
    # Find account number
    account_match = re.search(r'חשבון מספר[:\s]+([\d-]+)', text)
    if account_match:
        loan_info['account_number'] = account_match.group(1)
    
    # Look for "הלוואה ברגע" (current loan) - this indicates there's a loan
    has_loan = 'הלוואה ברגע' in text or 'הלוואה' in text
    
    if not has_loan:
        return loan_info
    
    # Extract all amounts from the document
    # Look for patterns like: "527302 -1,728.27" or large numbers
    amounts = []
    
    # Pattern 1: Negative amounts (loans appear as negative in bank statements)
    # Look for patterns like: "527302 -1,728.27" or "-17,004.08" or " -17,004.08"
    # Match negative numbers with optional spaces before the minus sign
    negative_patterns = [
        r'-([\d,\.]+)',  # Simple negative
        r'\s-([\d,\.]+)',  # Space before negative
        r'\(([\d,\.]+)\)',  # Parentheses (sometimes used for negative)
    ]
    
    for pattern in negative_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                amount = float(match.replace(',', ''))
                # In bank statements, large negative amounts indicate loan balances
                # Look for amounts between 5,000 and 100,000 (reasonable loan balances)
                if 5000 <= amount <= 100000:
                    amounts.append(amount)
            except:
                pass
    
    # Pattern 2: Large positive numbers (might be loan balances or account numbers)
    # Look for 5-7 digit numbers (account numbers are usually 6 digits, loan amounts can be similar)
    large_number_pattern = r'\b([\d]{5,7})\b'  # 5-7 digits as whole word
    large_matches = re.findall(large_number_pattern, text)
    for match in large_matches:
        try:
            amount = float(match)
            # Filter: account numbers are usually 6 digits starting with 5 or 2
            # Loan amounts are usually in range 10,000 - 1,000,000
            if 10000 <= amount <= 1000000:
                # Exclude numbers that look like account numbers (6 digits starting with 5 or 2)
                if not (len(match) == 6 and match[0] in ['5', '2']):
                    amounts.append(amount)
        except:
            pass
    
    # Pattern 3: Numbers with commas (formatted amounts)
    formatted_pattern = r'([\d]{1,3}(?:,[\d]{3})+\.?\d*)'
    formatted_matches = re.findall(formatted_pattern, text)
    for match in formatted_matches:
        try:
            amount = float(match.replace(',', ''))
            if 10000 <= amount <= 1000000:
                amounts.append(amount)
        except:
            pass
    
    # Pattern 3: Look for "יתרה" (balance) followed by number
    balance_patterns = [
        r'יתרה[:\s]+([\d,\.]+)',
        r'יתרת חוב[:\s]+([\d,\.]+)',
    ]
    
    for pattern in balance_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                amount = float(match.replace(',', ''))
                if 10000 <= amount <= 1000000:
                    amounts.append(amount)
            except:
                pass
    
    # Find the largest amount (likely the loan balance)
    if amounts:
        loan_info['large_amounts'] = sorted(set(amounts), reverse=True)[:10]
        loan_info['loan_balance'] = max(amounts)
    
    # Look for monthly payment patterns
    payment_patterns = [
        r'תשלום חודשי[:\s]+([\d,\.]+)',
        r'פירעון חודשי[:\s]+([\d,\.]+)',
    ]
    
    for pattern in payment_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                amount = float(match.replace(',', ''))
                if 100 <= amount <= 50000:
                    loan_info['monthly_payment'] = amount
                    break
            except:
                pass
    
    return loan_info

def search_mortgage_in_pdfs(data_dir):
    """Search for mortgage information in all PDF files."""
    import re
    
    pdf_files = list(data_dir.glob("*.pdf"))
    
    print("=" * 80)
    print("חיפוש משכנתא בקבצי PDF")
    print("=" * 80)
    print()
    
    mortgage_keywords = ['משכנתא', 'mortgage', 'משכנת', 'ריבית משכנתא']
    
    for pdf_file in pdf_files:
        text = extract_text_from_pdf(pdf_file)
        if not text:
            continue
        
        # Check if PDF contains mortgage keywords
        text_lower = text.lower()
        has_mortgage = any(keyword in text_lower for keyword in mortgage_keywords)
        
        if has_mortgage:
            print(f"נמצאה משכנתא בקובץ: {pdf_file.name}")
            print("-" * 80)
            
            # Find lines with mortgage keywords
            lines = text.split('\n')
            relevant_lines = []
            for i, line in enumerate(lines):
                if any(keyword in line.lower() for keyword in mortgage_keywords):
                    relevant_lines.append((i+1, line))
            
            if relevant_lines:
                print("שורות רלוונטיות:")
                for line_num, line in relevant_lines[:10]:
                    print(f"  שורה {line_num}: {line[:150]}")
            
            # Look for amounts near mortgage keywords
            amounts = []
            for i, line in enumerate(lines):
                if any(keyword in line.lower() for keyword in mortgage_keywords):
                    # Check this line and nearby lines for amounts
                    for j in range(max(0, i-2), min(len(lines), i+3)):
                        nearby_line = lines[j]
                        # Extract amounts
                        amount_patterns = [
                            r'([\d,]{4,})',  # 4+ digits
                            r'([\d,\.]+)',  # Any number with commas or dots
                        ]
                        for pattern in amount_patterns:
                            matches = re.findall(pattern, nearby_line)
                            for match in matches:
                                try:
                                    amount = float(match.replace(',', '').replace('.', ''))
                                    if 10000 <= amount <= 5000000:
                                        amounts.append(amount)
                                except:
                                    pass
            
            if amounts:
                amounts = sorted(set(amounts), reverse=True)
                print(f"\nסכומים שזוהו ליד המילה 'משכנתא':")
                for amount in amounts[:10]:
                    print(f"  {amount:,.0f} ₪")
            
            print()
            print("=" * 80)
            print()

def main():
    data_dir = Path(r"כרטיסי אשראי רועי")
    
    # First, search for mortgage in all PDFs
    search_mortgage_in_pdfs(data_dir)
    
    # Focus on tnuot.pdf files (bank statements)
    pdf_files = list(data_dir.glob("tnuot*.pdf"))
    
    print("=" * 80)
    print("חילוץ מידע על הלוואות מקבצי PDF מהבנק")
    print("=" * 80)
    print()
    
    total_loans = 0
    
    for pdf_file in pdf_files:
        print(f"קורא: {pdf_file.name}")
        print("-" * 80)
        
        text = extract_text_from_pdf(pdf_file)
        
        if not text:
            print("לא הצלחתי לחלץ טקסט מהקובץ")
            print()
            continue
        
        # Extract loan info
        loan_info = extract_loan_info(text)
        
        print(f"מספר חשבון: {loan_info['account_number'] or 'לא נמצא'}")
        print(f"יתרת הלוואה: {loan_info['loan_balance']:,.0f} ₪" if loan_info['loan_balance'] else "יתרת הלוואה: לא נמצאה")
        print(f"תשלום חודשי: {loan_info['monthly_payment']:,.0f} ₪" if loan_info['monthly_payment'] else "תשלום חודשי: לא נמצא")
        
        if loan_info['large_amounts']:
            print(f"סכומים גדולים שזוהו: {', '.join([f'{a:,.0f} ₪' for a in loan_info['large_amounts'][:10]])}")
        
        # Show all negative amounts found
        import re
        print("\nכל הסכומים השליליים הגדולים בקובץ:")
        negative_pattern = r'-([\d,\.]+)'
        all_negatives = re.findall(negative_pattern, text)
        large_negatives = []
        for match in all_negatives:
            try:
                amount = float(match.replace(',', ''))
                if amount > 1000:  # All significant negative amounts
                    large_negatives.append(amount)
            except:
                pass
        
        if large_negatives:
            large_negatives = sorted(set(large_negatives), reverse=True)
            print(f"נמצאו {len(large_negatives)} סכומים שליליים גדולים:")
            for i, amount in enumerate(large_negatives[:15], 1):
                print(f"  {i}. {amount:,.2f} ₪")
        
        # Show lines with "הלוואה" or large negative amounts
        print("\nשורות רלוונטיות מהקובץ:")
        lines = text.split('\n')
        relevant_lines = []
        for i, line in enumerate(lines):
            if 'הלוואה' in line or 'יתרה' in line:
                relevant_lines.append(f"שורה {i+1}: {line[:150]}")
            # Also show lines with large negative amounts
            elif any(f"-{int(amount)}" in line or f"-{amount:,.0f}" in line for amount in large_negatives[:3] if amount):
                relevant_lines.append(f"שורה {i+1}: {line[:150]}")
        
        if relevant_lines:
            for line in relevant_lines[:15]:
                print(f"  {line}")
        else:
            print("  לא נמצאו שורות רלוונטיות")
        
        if loan_info['loan_balance']:
            total_loans += loan_info['loan_balance']
        
        print()
        print("=" * 80)
        print()
    
    if total_loans > 0:
        print(f"סה\"כ הלוואות שזוהו: {total_loans:,.0f} ₪")
        print()

if __name__ == '__main__':
    main()

