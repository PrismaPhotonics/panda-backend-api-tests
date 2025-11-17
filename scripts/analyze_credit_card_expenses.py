#!/usr/bin/env python3
"""
Credit Card Expenses Analysis
=============================

Comprehensive analysis of credit card expenses to create a financial action plan.
Analyzes Excel files from credit card statements and generates detailed reports.

Author: Financial Analysis Tool
Date: 2025-01-XX
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from datetime import datetime
import re
import logging

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import PDF libraries
try:
    import PyPDF2
    PDF_AVAILABLE = True
    PDF_LIB = 'PyPDF2'
except ImportError:
    try:
        import pdfplumber
        PDF_AVAILABLE = True
        PDF_LIB = 'pdfplumber'
    except ImportError:
        PDF_AVAILABLE = False
        PDF_LIB = None
        logger.warning("PDF libraries not available. Install PyPDF2 or pdfplumber to read PDF files.")


class CreditCardAnalyzer:
    """
    Analyzes credit card expenses from Excel files.
    
    Handles multiple card formats and provides comprehensive financial analysis.
    """
    
    def __init__(self, data_dir: str):
        """
        Initialize analyzer with data directory.
        
        Args:
            data_dir: Path to directory containing credit card Excel files
        """
        self.data_dir = Path(data_dir)
        self.transactions = []
        self.loan_documents = []
        self.category_mapping = self._init_category_mapping()
        
    def _init_category_mapping(self) -> Dict[str, str]:
        """
        Initialize category mapping for expense classification.
        
        Returns:
            Dictionary mapping keywords to expense categories
        """
        return {
            'מזון': ['סופר', 'מכולת', 'שופרסל', 'ויקטורי', 'רמי לוי', 'מגה', 'אושר עד', 
                    'מזון', 'מסעדה', 'בורגר', 'פיצה', 'קפה', 'סטארבקס', 'ארומה'],
            'דלק': ['דלק', 'פז', 'סונול', 'דור אלון', 'תחנת', 'תדלוק'],
            'ביטוח': ['ביטוח', 'כלל', 'מגדל', 'הפניקס', 'מנורה'],
            'חינוך': ['גן', 'בית ספר', 'חינוך', 'לימודים', 'אוניברסיטה', 'מכללה'],
            'בריאות': ['רופא', 'בית מרקחת', 'פארם', 'בית חולים', 'קופת חולים', 'מכבי', 'מאוחדת', 'כללית'],
            'תחבורה': ['רכבת', 'אוטובוס', 'מונית', 'אובר', 'גט', 'תחבורה ציבורית'],
            'ביגוד': ['ביגוד', 'הלבשה', 'נעליים', 'אופנה'],
            'בידור': ['קולנוע', 'תיאטרון', 'קונצרט', 'בילוי', 'בידור'],
            'חשמל/מים': ['חשמל', 'מים', 'ארנונה', 'עירייה'],
            'אינטרנט/טלפון': ['בזק', 'פלאפון', 'סלקום', 'פרטנר', 'אינטרנט', 'טלפון'],
            'אחר': []  # Default category
        }
    
    def read_excel_file(self, file_path: Path) -> Optional[pd.DataFrame]:
        """
        Read Excel file and return DataFrame.
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            DataFrame with transactions or None if error
        """
        try:
            # Determine engine based on file extension
            if file_path.suffix == '.xls':
                engine = 'xlrd'
            else:
                engine = 'openpyxl'
            
            # First, try to find the header row by reading first few rows
            df_test = pd.read_excel(file_path, engine=engine, header=None, nrows=5)
            header_row = None
            
            # Look for row that contains "סכום חיוב" or similar amount keywords
            amount_keywords = ['סכום חיוב', 'סכום עסקה', 'סכום', 'amount']
            for idx in range(min(3, len(df_test))):
                row_values = df_test.iloc[idx].astype(str).str.lower()
                if any(keyword in ' '.join(row_values.values) for keyword in amount_keywords):
                    header_row = idx
                    break
            
            # Try reading with different encodings and sheet names
            try:
                if header_row is not None:
                    df = pd.read_excel(file_path, engine=engine, header=header_row)
                else:
                    df = pd.read_excel(file_path, engine=engine)
            except:
                # Fallback to openpyxl for xlsx files
                if file_path.suffix == '.xlsx':
                    if header_row is not None:
                        df = pd.read_excel(file_path, engine='openpyxl', header=header_row)
                    else:
                        df = pd.read_excel(file_path, engine='openpyxl')
                else:
                    raise
            
            # If empty, try first sheet explicitly
            if df.empty:
                if header_row is not None:
                    df = pd.read_excel(file_path, sheet_name=0, engine=engine, header=header_row)
                else:
                    df = pd.read_excel(file_path, sheet_name=0, engine=engine)
            
            logger.info(f"Successfully read {file_path.name}: {len(df)} rows, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.warning(f"Failed to read {file_path.name}: {e}")
            return None
    
    def detect_amount_column(self, df: pd.DataFrame) -> Optional[str]:
        """
        Detect the amount column in the DataFrame.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Name of amount column or None
        """
        # Common column names for amounts (Hebrew and English)
        # Priority order: more specific first
        amount_keywords_priority = [
            'סכום חיוב',  # Charge Amount (most specific)
            'סכום עסקה',  # Transaction Amount
            'סכום',  # Amount
            'amount', 'sum', 'total', 'מחיר', 'תשלום', 'חיוב', 
            'חיוב/זיכוי', 'עסקה', 'value', 'price', 'cost', 'שווי'
        ]
        
        # First, try to find by column name with priority
        for keyword in amount_keywords_priority:
            for col in df.columns:
                col_str = str(col).strip()
                col_lower = col_str.lower()
                # Check if column name contains the keyword
                if keyword.lower() in col_lower:
                    # Check if column contains numeric values
                    if pd.api.types.is_numeric_dtype(df[col]) or df[col].dtype == 'object':
                        try:
                            # Try to convert to numeric
                            numeric_values = pd.to_numeric(df[col], errors='coerce')
                            valid_numeric = numeric_values.notna()
                            if valid_numeric.sum() > len(df) * 0.3:  # At least 30% numeric
                                # Filter out columns that look like credit card numbers (4 digits)
                                # or transaction types (containing "תשלומים" or similar)
                                sample_values = df[col].dropna().head(10).astype(str)
                                # Check if values look like amounts (have decimals or are > 1000)
                                has_decimals = any('.' in str(v) for v in sample_values)
                                has_large_numbers = any(abs(pd.to_numeric(v, errors='coerce') or 0) > 1000 for v in sample_values if pd.to_numeric(v, errors='coerce') is not None)
                                # Exclude if all values are 4-digit integers (likely credit card numbers)
                                all_4_digit = all(len(str(v).replace('.', '').replace('-', '')) == 4 and '.' not in str(v) for v in sample_values if pd.to_numeric(v, errors='coerce') is not None)
                                
                                if (has_decimals or has_large_numbers) and not all_4_digit:
                                    return col
                        except:
                            pass
        
        # Second, try to find numeric columns that look like amounts
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        candidate_cols = []
        if len(numeric_cols) > 0:
            # Look for columns with values that could be amounts (typically > 0, reasonable range)
            for col in numeric_cols:
                col_data = df[col].dropna()
                if len(col_data) > 0:
                    # Exclude columns that look like credit card numbers (all values are exactly 4 digits)
                    sample_values = col_data.head(10)
                    all_4_digit = all(
                        len(str(int(v)).replace('-', '')) == 4 and 
                        int(v) >= 1000 and int(v) <= 9999 
                        for v in sample_values 
                        if pd.notna(v) and isinstance(v, (int, float)) and v == int(v)
                    )
                    if all_4_digit:
                        continue
                    
                    # Check if values are in reasonable range for amounts (10 to 100000)
                    if (col_data.abs() >= 10).sum() > len(col_data) * 0.5:
                        if (col_data.abs() <= 100000).sum() > len(col_data) * 0.8:
                            # Prefer columns with decimals or smaller values (more likely to be amounts)
                            has_decimals = any(v != int(v) for v in sample_values if pd.notna(v))
                            avg_value = col_data.abs().mean()
                            candidate_cols.append((col, has_decimals, avg_value))
            
            # Sort candidates: prefer columns with decimals, then smaller average values
            if candidate_cols:
                candidate_cols.sort(key=lambda x: (not x[1], x[2]))  # Decimals first, then by avg value
                return candidate_cols[0][0]
        
        # Third, try to find object columns that contain numeric amounts
        object_cols = df.select_dtypes(include=['object']).columns.tolist()
        for col in object_cols:
            try:
                # Skip if column name suggests it's not an amount (like credit card number)
                col_str = str(col).lower()
                if any(skip_word in col_str for skip_word in ['כרטיס', 'card', 'מספר', 'number', '4 ספרות']):
                    continue
                
                # Try to convert to numeric
                numeric_values = pd.to_numeric(df[col], errors='coerce')
                numeric_count = numeric_values.notna().sum()
                if numeric_count > len(df) * 0.3:  # At least 30% numeric
                    # Check if values are in reasonable range
                    valid_values = numeric_values[numeric_values.notna()]
                    if len(valid_values) > 0:
                        # Exclude if all values are 4-digit integers (credit card numbers)
                        sample_values = valid_values.head(10)
                        all_4_digit = all(
                            len(str(int(v)).replace('-', '')) == 4 and 
                            int(v) >= 1000 and int(v) <= 9999 
                            for v in sample_values 
                            if pd.notna(v) and isinstance(v, (int, float)) and v == int(v)
                        )
                        if all_4_digit:
                            continue
                            
                        if (valid_values.abs() >= 10).sum() > len(valid_values) * 0.5:
                            if (valid_values.abs() <= 100000).sum() > len(valid_values) * 0.8:
                                return col
            except:
                continue
        
        # Last resort: return first numeric column if exists
        if len(numeric_cols) > 0:
            return numeric_cols[0]
        
        return None
    
    def detect_date_column(self, df: pd.DataFrame) -> Optional[str]:
        """
        Detect the date column in the DataFrame.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Name of date column or None
        """
        date_keywords = ['תאריך', 'date', 'יום', 'תאריך עסקה']
        
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in date_keywords):
                return col
        
        # Try to find datetime columns
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                return col
        
        return None
    
    def detect_description_column(self, df: pd.DataFrame) -> Optional[str]:
        """
        Detect the description/merchant column.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Name of description column or None
        """
        desc_keywords = ['תיאור', 'description', 'merchant', 'ספק', 'עסקה', 'פרטים', 'שם']
        
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in desc_keywords):
                return col
        
        # If no match, return first text column
        text_cols = df.select_dtypes(include=['object']).columns
        if len(text_cols) > 0:
            return text_cols[0]
        
        return None
    
    def categorize_expense(self, description: str) -> str:
        """
        Categorize expense based on description.
        
        Args:
            description: Transaction description
            
        Returns:
            Category name
        """
        if pd.isna(description):
            return 'אחר'
        
        desc_lower = str(description).lower()
        
        for category, keywords in self.category_mapping.items():
            if category == 'אחר':
                continue
            if any(keyword.lower() in desc_lower for keyword in keywords):
                return category
        
        return 'אחר'
    
    def parse_transactions(self, df: pd.DataFrame, file_path: Path) -> List[Dict]:
        """
        Parse transactions from DataFrame.
        
        Args:
            df: DataFrame with transactions
            file_path: Source file path
            
        Returns:
            List of transaction dictionaries
        """
        transactions = []
        
        # Detect columns
        amount_col = self.detect_amount_column(df)
        date_col = self.detect_date_column(df)
        desc_col = self.detect_description_column(df)
        
        if not amount_col:
            logger.warning(f"No amount column found in {file_path.name}")
            return transactions
        
        logger.info(f"Using columns - Amount: {amount_col}, Date: {date_col}, Description: {desc_col}")
        
        # Process each row
        for idx, row in df.iterrows():
            try:
                # Extract amount
                amount = row[amount_col]
                if pd.isna(amount):
                    continue
                
                # Convert to numeric
                amount = pd.to_numeric(amount, errors='coerce')
                if pd.isna(amount) or amount == 0:
                    continue
                
                # Only process expenses (positive amounts typically mean expenses in credit cards)
                # Some systems use negative for expenses, some positive
                # We'll take absolute value and check sign later
                amount_abs = abs(amount)
                
                # Extract date
                date = None
                if date_col:
                    date = row[date_col]
                    if pd.notna(date):
                        try:
                            date = pd.to_datetime(date)
                        except:
                            date = None
                
                # Extract description
                description = None
                if desc_col:
                    description = str(row[desc_col]) if pd.notna(row[desc_col]) else 'לא צוין'
                else:
                    description = 'לא צוין'
                
                # Determine if it's an expense (not a refund/credit)
                # Check description for refund/credit keywords
                desc_lower = str(description).lower()
                is_refund = any(keyword in desc_lower for keyword in 
                               ['זיכוי', 'החזר', 'refund', 'credit', 'הפקדה', 'העברה'])
                
                # Typically expenses are positive in credit card statements
                # Negative amounts might be refunds/credits
                is_expense = (amount > 0 and not is_refund) or (amount < 0 and is_refund)
                
                # Identify loans and mortgages
                is_loan = any(keyword in desc_lower for keyword in 
                             ['הלוואה', 'loan', 'משכנתא', 'mortgage', 'פירעון', 'ריבית'])
                
                transaction = {
                    'date': date,
                    'amount': amount_abs if is_expense else -amount_abs,
                    'description': description,
                    'category': self.categorize_expense(description),
                    'file': file_path.name,
                    'is_expense': is_expense,
                    'is_income': not is_expense and not is_refund,
                    'is_loan': is_loan
                }
                
                transactions.append(transaction)
                
            except Exception as e:
                logger.warning(f"Error processing row {idx} in {file_path.name}: {e}")
                continue
        
        return transactions
    
    def read_pdf_file(self, file_path: Path) -> Optional[Dict]:
        """
        Read PDF file and extract loan information.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with loan information or None
        """
        if not PDF_AVAILABLE:
            logger.warning(f"PDF libraries not available. Skipping {file_path.name}")
            return None
        
        try:
            loan_info = {
                'file': file_path.name,
                'loans': [],
                'total_loans': 0,
                'monthly_payments': []
            }
            
            text_content = ""
            
            # Try pdfplumber first (better for text extraction)
            if PDF_LIB == 'pdfplumber' or 'pdfplumber' in globals():
                try:
                    import pdfplumber
                    with pdfplumber.open(file_path) as pdf:
                        for page in pdf.pages:
                            text_content += page.extract_text() or ""
                except:
                    pass
            
            # Fallback to PyPDF2
            if not text_content:
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        for page in pdf_reader.pages:
                            text_content += page.extract_text() or ""
                except:
                    pass
            
            if not text_content:
                logger.warning(f"Could not extract text from {file_path.name}")
                return None
            
            # Search for loan-related keywords
            loan_keywords = ['הלוואה', 'loan', 'משכנתא', 'mortgage', 'ריבית', 'interest', 
                           'תשלום חודשי', 'monthly payment', 'יתרה', 'balance', 'יתרת חוב',
                           'עובר ושב', 'תנועות בחשבון']
            
            text_lower = text_content.lower()
            
            # Check if PDF contains loan information
            has_loan_info = any(keyword in text_lower for keyword in loan_keywords)
            
            if not has_loan_info:
                return None
            
            # Special handling for bank statements (tnuot files)
            is_bank_statement = 'תנועות בחשבון' in text_content or 'עובר ושב' in text_content
            
            # Extract numbers that might be loan amounts or payments
            # Look for patterns like: "סכום: 100,000" or "יתרה: 50,000"
            amount_patterns = [
                r'יתרה[:\s]+([\d,\.]+)',
                r'יתרת חוב[:\s]+([\d,\.]+)',
                r'יתרת[:\s]+([\d,\.]+)',
                r'סכום הלוואה[:\s]+([\d,\.]+)',
                r'סכום[:\s]+([\d,\.]+)',
                r'תשלום חודשי[:\s]+([\d,\.]+)',
                r'תשלום[:\s]+([\d,\.]+)',
                r'ריבית[:\s]+([\d.]+)%',
                r'balance[:\s]+([\d,\.]+)',
                r'loan amount[:\s]+([\d,\.]+)',
                r'monthly payment[:\s]+([\d,\.]+)',
                r'([\d,]{4,})',  # Any number with 4+ digits (likely amounts)
            ]
            
            found_amounts = []
            seen_amounts = set()
            
            for pattern in amount_patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                for match in matches:
                    # Clean and convert to number
                    clean_match = str(match).replace(',', '').replace(' ', '').replace('.', '')
                    try:
                        amount = float(clean_match)
                        # Filter reasonable loan amounts (1,000 to 5,000,000)
                        # Exclude very specific numbers that are likely account numbers or codes
                        if 1000 <= amount <= 5000000:
                            # Exclude numbers that look like account numbers (very specific)
                            # Loan amounts are usually round numbers
                            if amount % 100 == 0 or amount % 1000 == 0:  # Round numbers
                                amount_rounded = round(amount, -2)  # Round to nearest 100
                                if amount_rounded not in seen_amounts:
                                    seen_amounts.add(amount_rounded)
                                    found_amounts.append(amount)
                    except:
                        pass
            
            # Special handling for bank statements - look for loan balance
            if is_bank_statement:
                # Look for "יתרה" (balance) followed by a number
                # Pattern: "יתרה" or "יתרת חוב" followed by number
                balance_patterns = [
                    r'יתרה[:\s]+([\d,\.]+)',
                    r'יתרת חוב[:\s]+([\d,\.]+)',
                    r'יתרת[:\s]+([\d,\.]+)',
                    r'הלוואה ברגע[:\s]+([\d,\.]+)',  # "הלוואה ברגע" = current loan
                ]
                
                for pattern in balance_patterns:
                    matches = re.findall(pattern, text_content, re.IGNORECASE)
                    for match in matches:
                        clean_match = str(match).replace(',', '').replace(' ', '').replace('.', '')
                        try:
                            amount = float(clean_match)
                            if 10000 <= amount <= 2000000:  # Reasonable loan balance range
                                amount_rounded = round(amount, -2)
                                if amount_rounded not in seen_amounts:
                                    seen_amounts.add(amount_rounded)
                                    found_amounts.append(amount)
                        except:
                            pass
                
                # Also look for large negative balances (which indicate loans)
                # In bank statements, loans appear as negative balances
                lines = text_content.split('\n')
                for line in lines:
                    # Look for patterns like: "527302 -1,728.27" (account number, negative balance)
                    # Or large negative amounts that might be loan balances
                    negative_pattern = r'-([\d,\.]{4,})'  # Negative numbers with 4+ digits
                    matches = re.findall(negative_pattern, line)
                    for match in matches:
                        try:
                            clean_num = float(match.replace(',', ''))
                            # Large negative amounts might be loan balances
                            if 10000 <= clean_num <= 2000000:
                                amount_rounded = round(clean_num, -2)
                                if amount_rounded not in seen_amounts:
                                    seen_amounts.add(amount_rounded)
                                    found_amounts.append(clean_num)
                        except:
                            pass
            
            # Also look for common loan-related numbers in context
            # Find lines with loan keywords and extract nearby numbers
            lines = text_content.split('\n')
            for i, line in enumerate(lines):
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in ['הלוואה', 'loan', 'משכנתא', 'mortgage', 'יתרה']):
                    # Look for numbers in this line and nearby lines
                    for j in range(max(0, i-1), min(len(lines), i+2)):
                        nearby_line = lines[j]
                        # Extract all numbers from this line
                        numbers = re.findall(r'[\d,]+', nearby_line)
                        for num_str in numbers:
                            try:
                                clean_num = float(num_str.replace(',', ''))
                                # Filter for reasonable loan amounts (1,000 to 5,000,000)
                                # Prefer round numbers (multiples of 100 or 1000)
                                if 1000 <= clean_num <= 5000000:
                                    # Prefer round numbers (likely loan amounts)
                                    if clean_num % 100 == 0 or clean_num % 1000 == 0:
                                        amount_rounded = round(clean_num, -2)
                                        if amount_rounded not in seen_amounts:
                                            seen_amounts.add(amount_rounded)
                                            found_amounts.append(clean_num)
                            except:
                                pass
            
            if found_amounts:
                # Filter out outliers - keep only reasonable loan amounts
                # Sort and take amounts that are in reasonable range
                sorted_amounts = sorted(found_amounts)
                # Remove outliers (amounts that are way larger than others)
                if len(sorted_amounts) > 1:
                    median = sorted_amounts[len(sorted_amounts) // 2]
                    # Keep amounts within 10x of median (reasonable range)
                    filtered_amounts = [a for a in sorted_amounts if a <= median * 10]
                    if filtered_amounts:
                        loan_info['found_amounts'] = filtered_amounts
                        loan_info['total_loans'] = max(filtered_amounts)
                    else:
                        loan_info['found_amounts'] = sorted_amounts[:5]  # Top 5 if all outliers
                        loan_info['total_loans'] = sorted_amounts[0]
                else:
                    loan_info['found_amounts'] = found_amounts
                    loan_info['total_loans'] = found_amounts[0]
                loan_info['text_preview'] = text_content[:500]  # First 500 chars
            
            logger.info(f"Extracted loan info from {file_path.name}: {len(found_amounts)} amounts found")
            return loan_info
            
        except Exception as e:
            logger.warning(f"Failed to read PDF {file_path.name}: {e}")
            return None
    
    def load_all_transactions(self) -> None:
        """
        Load all transactions from Excel files and PDF files in data directory.
        """
        logger.info(f"Loading transactions from: {self.data_dir}")
        
        # Find all Excel files (both .xlsx and .xls)
        excel_files = list(self.data_dir.glob('*.xlsx')) + list(self.data_dir.glob('*.xls'))
        logger.info(f"Found {len(excel_files)} Excel files")
        
        # Filter out duplicate files (files with (1), (2), etc. at the end)
        # These are usually duplicate copies of the same file
        files_to_load = []
        seen_base_names = set()
        
        for file_path in excel_files:
            base_name = file_path.stem  # Name without extension
            # Check if this is a duplicate (ends with (1), (2), etc.)
            import re
            match = re.match(r'^(.+?)\s*\(\d+\)$', base_name)
            if match:
                # This is a duplicate file - check if we already have the original
                original_name = match.group(1)
                original_path = file_path.parent / f"{original_name}{file_path.suffix}"
                if original_path.exists():
                    # Original exists, skip this duplicate
                    logger.info(f"Skipping duplicate file: {file_path.name} (original exists: {original_path.name})")
                    continue
                else:
                    # Original doesn't exist, use this one
                    files_to_load.append(file_path)
                    logger.info(f"Using duplicate file (original not found): {file_path.name}")
            else:
                # Not a duplicate, check if we should load it
                files_to_load.append(file_path)
        
        logger.info(f"Loading {len(files_to_load)} files (after filtering duplicates)")
        
        for file_path in files_to_load:
            df = self.read_excel_file(file_path)
            if df is not None and not df.empty:
                transactions = self.parse_transactions(df, file_path)
                self.transactions.extend(transactions)
                logger.info(f"Loaded {len(transactions)} transactions from {file_path.name}")
        
        # Find and process PDF files for loan information
        pdf_files = list(self.data_dir.glob('*.pdf'))
        logger.info(f"Found {len(pdf_files)} PDF files")
        
        self.loan_documents = []
        for file_path in pdf_files:
            loan_info = self.read_pdf_file(file_path)
            if loan_info:
                self.loan_documents.append(loan_info)
                logger.info(f"Found loan information in {file_path.name}")
        
        logger.info(f"Total transactions loaded: {len(self.transactions)}")
        logger.info(f"Total loan documents found: {len(self.loan_documents)}")
    
    def analyze_expenses(self) -> Dict:
        """
        Analyze all expenses and generate comprehensive statistics.
        
        Returns:
            Dictionary with analysis results
        """
        if not self.transactions:
            return {}
        
        df = pd.DataFrame(self.transactions)
        
        # Convert amounts to numeric
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        
        # Filter expenses
        expenses_df = df[df['is_expense'] == True].copy()
        expenses_df = expenses_df[expenses_df['amount'] > 0]
        
        # Filter income/credits
        income_df = df[df['is_income'] == True].copy()
        income_df = income_df[income_df['amount'] > 0]
        
        # Filter loans from transactions
        loans_df = df[df['is_loan'] == True].copy()
        
        # Extract loans from PDF documents
        pdf_loans = []
        pdf_total_loans = 0
        pdf_monthly_payments = []
        
        if hasattr(self, 'loan_documents') and self.loan_documents:
            for doc in self.loan_documents:
                if doc.get('found_amounts'):
                    amounts = doc['found_amounts']
                    # Filter reasonable amounts only
                    reasonable_amounts = [a for a in amounts if 1000 <= a <= 5000000]
                    if reasonable_amounts:
                        pdf_loans.extend(reasonable_amounts)
                        # Use sum of reasonable amounts, not max (might be outlier)
                        doc_total = sum(reasonable_amounts)
                        pdf_total_loans += doc_total
                    if doc.get('monthly_payments'):
                        pdf_monthly_payments.extend(doc['monthly_payments'])
        
        # Total expenses
        total_expenses = expenses_df['amount'].sum() if not expenses_df.empty else 0
        
        # Total income/credits
        total_income = income_df['amount'].sum() if not income_df.empty else 0
        
        # Total loans (from transactions + PDFs)
        total_loans = loans_df['amount'].sum() if not loans_df.empty else 0
        total_loans += pdf_total_loans
        
        # Monthly breakdown for expenses
        if 'date' in expenses_df.columns and expenses_df['date'].notna().any():
            expenses_df['month'] = pd.to_datetime(expenses_df['date']).dt.to_period('M')
            monthly_expenses = expenses_df.groupby('month')['amount'].sum()
        else:
            monthly_expenses = pd.Series()
        
        # Monthly breakdown for income
        if 'date' in income_df.columns and income_df['date'].notna().any():
            income_df['month'] = pd.to_datetime(income_df['date']).dt.to_period('M')
            monthly_income_cc = income_df.groupby('month')['amount'].sum()
        else:
            monthly_income_cc = pd.Series()
        
        # Category breakdown
        category_expenses = expenses_df.groupby('category')['amount'].sum().sort_values(ascending=False) if not expenses_df.empty else pd.Series()
        
        # Average monthly expense
        if len(monthly_expenses) > 0:
            avg_monthly = monthly_expenses.mean()
            period_months = len(monthly_expenses)
        else:
            # Estimate based on date range or assume 6 months
            if 'date' in expenses_df.columns and expenses_df['date'].notna().any():
                date_range = pd.to_datetime(expenses_df['date']).max() - pd.to_datetime(expenses_df['date']).min()
                period_months = max(1, date_range.days / 30)
            else:
                period_months = 6
            avg_monthly = total_expenses / period_months if period_months > 0 else 0
        
        # Top expenses
        top_expenses = expenses_df.nlargest(30, 'amount')[['date', 'amount', 'description', 'category']].to_dict('records') if not expenses_df.empty else []
        
        # Identify recurring expenses (same merchant/category monthly)
        recurring_expenses = {}
        if 'date' in expenses_df.columns and expenses_df['date'].notna().any():
            expenses_df['month'] = pd.to_datetime(expenses_df['date']).dt.to_period('M')
            for category in expenses_df['category'].unique():
                cat_df = expenses_df[expenses_df['category'] == category]
                monthly_avg = cat_df.groupby('month')['amount'].sum().mean()
                if monthly_avg > 500:  # Significant recurring expense
                    recurring_expenses[category] = monthly_avg
        
        # Identify anomalies (unusually large expenses)
        anomalies = []
        if not expenses_df.empty:
            mean_amount = expenses_df['amount'].mean()
            std_amount = expenses_df['amount'].std()
            # Expenses more than 2 standard deviations above mean
            threshold = mean_amount + (2 * std_amount)
            anomalies_df = expenses_df[expenses_df['amount'] > threshold].nlargest(20, 'amount')
            anomalies = anomalies_df[['date', 'amount', 'description', 'category']].to_dict('records')
        
        # Identify potentially unnecessary expenses
        unnecessary_keywords = ['מסעדה', 'בורגר', 'פיצה', 'קפה', 'סטארבקס', 'ארומה', 
                               'קולנוע', 'תיאטרון', 'בילוי', 'בידור', 'אופנה', 'ביגוד',
                               'נעליים', 'הלבשה', 'מנוי', 'סטרימינג', 'נטפליקס', 'ספוטיפיי']
        potentially_unnecessary = []
        if not expenses_df.empty:
            for idx, row in expenses_df.iterrows():
                desc_lower = str(row['description']).lower()
                if any(keyword.lower() in desc_lower for keyword in unnecessary_keywords):
                    if row['amount'] > 100:  # Only significant expenses
                        potentially_unnecessary.append({
                            'date': row['date'],
                            'amount': row['amount'],
                            'description': row['description'],
                            'category': row['category']
                        })
            # Sort by amount descending and take top 30
            potentially_unnecessary = sorted(potentially_unnecessary, key=lambda x: x['amount'], reverse=True)[:30]
        
        # Analyze credit card usage patterns
        credit_card_analysis = {}
        if 'file' in expenses_df.columns:
            # Group by file (card) to see spending per card
            card_spending = expenses_df.groupby('file')['amount'].sum().sort_values(ascending=False)
            credit_card_analysis['spending_per_card'] = card_spending.to_dict()
            credit_card_analysis['total_cards'] = len(card_spending)
            credit_card_analysis['avg_per_card'] = card_spending.mean()
        
        # Identify duplicate/recurring charges (same merchant, similar amount, different credit cards)
        duplicate_charges = []
        if not expenses_df.empty and 'description' in expenses_df.columns:
            # Group by description and find similar amounts
            desc_groups = expenses_df.groupby(expenses_df['description'].str.lower())
            for desc, group in desc_groups:
                if len(group) > 1:
                    amounts = group['amount'].tolist()
                    # Check if amounts are similar (within 10%)
                    if len(set(amounts)) <= 2:  # Same or very similar amounts
                        # Check if these are from different credit cards (not just duplicate files)
                        files = group['file'].tolist() if 'file' in group.columns else []
                        # Filter out duplicate files (files with (1) etc.)
                        unique_files = set()
                        for f in files:
                            if f:
                                import re
                                f_str = str(f)
                                # Remove (1), (2) etc. from filename
                                base_name = re.sub(r'\s*\(\d+\)\.xlsx?$', '', f_str)
                                # Also remove extension for comparison
                                base_name_no_ext = re.sub(r'\.xlsx?$', '', base_name)
                                unique_files.add(base_name_no_ext)
                        
                        # Only consider duplicates if they're from different credit cards
                        if len(unique_files) > 1:
                            total = group['amount'].sum()
                            if total > 500:  # Significant total
                                duplicate_charges.append({
                                    'description': desc,
                                    'count': len(group),
                                    'total_amount': total,
                                    'avg_amount': total / len(group),
                                    'dates': group['date'].tolist() if 'date' in group.columns else [],
                                    'files': list(unique_files)
                                })
            duplicate_charges = sorted(duplicate_charges, key=lambda x: x['total_amount'], reverse=True)[:20]
        
        analysis = {
            'total_expenses': total_expenses,
            'total_income_cc': total_income,
            'total_loans': total_loans,
            'total_transactions': len(expenses_df),
            'avg_monthly_expense': avg_monthly,
            'avg_monthly_income_cc': monthly_income_cc.mean() if len(monthly_income_cc) > 0 else 0,
            'monthly_breakdown': monthly_expenses.to_dict() if len(monthly_expenses) > 0 else {},
            'monthly_income_breakdown': monthly_income_cc.to_dict() if len(monthly_income_cc) > 0 else {},
            'category_breakdown': category_expenses.to_dict(),
            'top_expenses': top_expenses,
            'recurring_expenses': recurring_expenses,
            'period_months': period_months,
            'loans_breakdown': loans_df.groupby('description')['amount'].sum().to_dict() if not loans_df.empty else {},
            'pdf_loans': pdf_loans,
            'pdf_total_loans': pdf_total_loans,
            'pdf_monthly_payments': pdf_monthly_payments,
            'loan_documents': [doc for doc in (hasattr(self, 'loan_documents') and self.loan_documents or [])],
            'anomalies': anomalies,
            'potentially_unnecessary': potentially_unnecessary,
            'credit_card_analysis': credit_card_analysis,
            'duplicate_charges': duplicate_charges
        }
        
        return analysis
    
    def generate_comprehensive_action_plan(self, analysis: Dict, monthly_income: float, mortgage: float, current_debt: float) -> str:
        """
        Generate financial action plan based on analysis.
        
        Args:
            analysis: Expense analysis results
            monthly_income: Monthly net income
            mortgage: Monthly mortgage payment
            current_debt: Current bank debt (negative balance)
            
        Returns:
            Formatted action plan string
        """
        if not analysis:
            return "לא ניתן ליצור תוכנית פעולה - אין נתונים"
        
        total_expenses = analysis['total_expenses']
        avg_monthly = analysis['avg_monthly_expense']
        period_months = analysis['period_months']
        category_breakdown = analysis['category_breakdown']
        
        # Calculate monthly expenses
        monthly_expenses = avg_monthly
        total_monthly = monthly_expenses + mortgage
        
        # Calculate surplus/deficit
        monthly_surplus = monthly_income - total_monthly
        
        # Calculate time to pay off debt
        months_to_payoff = abs(current_debt) / monthly_surplus if monthly_surplus > 0 else float('inf')
        
        plan = []
        plan.append("=" * 80)
        plan.append("תוכנית פעולה פיננסית - אנליזה מעמיקה")
        plan.append("=" * 80)
        plan.append("")
        
        # Current situation - comprehensive
        plan.append("📊 מצב נוכחי - ניתוח מלא:")
        plan.append(f"  • חוב בבנק: {current_debt:,.0f} ₪")
        plan.append(f"  • הכנסה חודשית נטו (משכורות): {monthly_income:,.0f} ₪")
        plan.append(f"  • משכנתא חודשית: {mortgage:,.0f} ₪")
        plan.append(f"  • הוצאות ממוצעות חודשיות (מכרטיסי אשראי): {monthly_expenses:,.0f} ₪")
        if analysis.get('avg_monthly_income_cc', 0) > 0:
            plan.append(f"  • הכנסות ממוצעות חודשיות (מכרטיסי אשראי - החזרים/זיכויים): {analysis['avg_monthly_income_cc']:,.0f} ₪")
        if analysis.get('total_loans', 0) > 0:
            plan.append(f"  • הלוואות שזוהו: {analysis['total_loans']:,.0f} ₪")
        plan.append(f"  • סה\"כ הוצאות חודשיות: {total_monthly:,.0f} ₪")
        plan.append(f"  • עודף/גירעון חודשי: {monthly_surplus:,.0f} ₪")
        plan.append("")
        
        # Monthly trend analysis
        if analysis.get('monthly_breakdown'):
            plan.append("📈 מגמות חודשיות (הוצאות):")
            for month, amount in sorted(analysis['monthly_breakdown'].items())[-6:]:  # Last 6 months
                plan.append(f"  • {month}: {amount:,.0f} ₪")
            plan.append("")
        
        # Expense breakdown
        plan.append("💰 פילוח הוצאות לפי קטגוריות:")
        for category, amount in category_breakdown.items():
            percentage = (amount / total_expenses) * 100
            monthly_avg = amount / period_months
            plan.append(f"  • {category}: {monthly_avg:,.0f} ₪/חודש ({percentage:.1f}%)")
        plan.append("")
        
        # Recurring expenses
        if analysis.get('recurring_expenses'):
            plan.append("🔄 הוצאות חוזרות משמעותיות:")
            for category, monthly_avg in sorted(analysis['recurring_expenses'].items(), key=lambda x: x[1], reverse=True)[:10]:
                plan.append(f"  • {category}: {monthly_avg:,.0f} ₪/חודש")
            plan.append("")
        
        # Loans breakdown from transactions
        if analysis.get('loans_breakdown'):
            plan.append("💳 הלוואות ומשכנתאות שזוהו (מעסקאות):")
            for desc, amount in analysis['loans_breakdown'].items():
                plan.append(f"  • {desc[:60]}: {amount:,.0f} ₪")
            plan.append("")
        
        # Loans from PDF documents
        if analysis.get('loan_documents'):
            plan.append("📄 הלוואות שזוהו מקבצי PDF מהבנק:")
            total_pdf_loans = 0
            for doc in analysis['loan_documents']:
                if doc.get('found_amounts'):
                    amounts = doc['found_amounts']
                    total_pdf_loans += max(amounts) if amounts else 0
                    plan.append(f"  • {doc['file']}:")
                    plan.append(f"    - סכומים שזוהו: {', '.join([f'{a:,.0f} ₪' for a in amounts[:5]])}")
                    if doc.get('text_preview'):
                        # Extract key info from text preview
                        preview = doc['text_preview'][:200]
                        plan.append(f"    - תקציר: {preview}...")
            if total_pdf_loans > 0:
                plan.append(f"  • סה\"כ הלוואות מקבצי PDF: {total_pdf_loans:,.0f} ₪")
            plan.append("")
        
        # Combined loans summary
        total_all_loans = analysis.get('total_loans', 0) + analysis.get('pdf_total_loans', 0)
        if total_all_loans > 0:
            plan.append("💰 סיכום הלוואות כולל:")
            plan.append(f"  • הלוואות מעסקאות: {analysis.get('total_loans', 0):,.0f} ₪")
            plan.append(f"  • הלוואות מקבצי PDF: {analysis.get('pdf_total_loans', 0):,.0f} ₪")
            plan.append(f"  • סה\"כ הלוואות שזוהו: {total_all_loans:,.0f} ₪")
            plan.append("")
        
        # Anomalies
        if analysis.get('anomalies'):
            plan.append("🚨 אנומליות - הוצאות חריגות (גבוהות מהממוצע):")
            for i, anomaly in enumerate(analysis['anomalies'][:15], 1):
                date_str = anomaly.get('date', 'לא צוין')
                if hasattr(date_str, 'strftime'):
                    try:
                        if pd.notna(date_str):
                            date_str = date_str.strftime('%Y-%m-%d')
                        else:
                            date_str = 'לא צוין'
                    except (ValueError, AttributeError):
                        date_str = 'לא צוין'
                elif isinstance(date_str, str):
                    pass
                else:
                    date_str = str(date_str) if date_str is not None else 'לא צוין'
                plan.append(f"  {i}. {anomaly['amount']:,.0f} ₪ - {anomaly['description'][:60]} ({anomaly['category']}) - {date_str}")
            plan.append("")
        
        # Potentially unnecessary expenses
        if analysis.get('potentially_unnecessary'):
            plan.append("⚠️ הוצאות שניתן לוותר עליהן (בילויים, ביגוד, מנויים):")
            total_unnecessary = sum(exp['amount'] for exp in analysis['potentially_unnecessary'])
            monthly_unnecessary = total_unnecessary / period_months
            plan.append(f"  סה\"כ: {total_unnecessary:,.0f} ₪ | ממוצע חודשי: {monthly_unnecessary:,.0f} ₪")
            plan.append("  הוצאות הגדולות ביותר:")
            for i, exp in enumerate(analysis['potentially_unnecessary'][:20], 1):
                date_str = exp.get('date', 'לא צוין')
                if hasattr(date_str, 'strftime'):
                    try:
                        if pd.notna(date_str):
                            date_str = date_str.strftime('%Y-%m-%d')
                        else:
                            date_str = 'לא צוין'
                    except (ValueError, AttributeError):
                        date_str = 'לא צוין'
                elif isinstance(date_str, str):
                    pass
                else:
                    date_str = str(date_str) if date_str is not None else 'לא צוין'
                plan.append(f"    {i}. {exp['amount']:,.0f} ₪ - {exp['description'][:55]} ({exp['category']}) - {date_str}")
            plan.append("")
        
        # Duplicate charges
        if analysis.get('duplicate_charges'):
            plan.append("🔄 חיובים כפולים/חוזרים (אותו ספק, סכום דומה):")
            total_duplicates = sum(dup['total_amount'] for dup in analysis['duplicate_charges'])
            plan.append(f"  סה\"כ חיובים חוזרים: {total_duplicates:,.0f} ₪")
            for i, dup in enumerate(analysis['duplicate_charges'][:15], 1):
                plan.append(f"  {i}. {dup['description'][:50]}: {dup['count']} פעמים, {dup['avg_amount']:,.0f} ₪ כל פעם, סה\"כ {dup['total_amount']:,.0f} ₪")
            plan.append("")
        
        # Credit card analysis
        if analysis.get('credit_card_analysis'):
            cc_analysis = analysis['credit_card_analysis']
            plan.append("💳 ניתוח כרטיסי אשראי:")
            plan.append(f"  • מספר כרטיסים פעילים: {cc_analysis.get('total_cards', 0)}")
            plan.append(f"  • ממוצע הוצאות לכרטיס: {cc_analysis.get('avg_per_card', 0):,.0f} ₪")
            if cc_analysis.get('spending_per_card'):
                plan.append("  • הוצאות לפי כרטיס:")
                for card, amount in list(cc_analysis['spending_per_card'].items())[:5]:
                    card_name = card[:40] if len(card) > 40 else card
                    plan.append(f"    - {card_name}: {amount:,.0f} ₪")
            plan.append("")
        
        # Top expenses
        plan.append("🔝 20 ההוצאות הגדולות ביותר:")
        top_20 = analysis['top_expenses'][:20]
        for i, expense in enumerate(top_20, 1):
            date_str = expense.get('date', 'לא צוין')
            if hasattr(date_str, 'strftime'):
                try:
                    if pd.notna(date_str):
                        date_str = date_str.strftime('%Y-%m-%d')
                    else:
                        date_str = 'לא צוין'
                except (ValueError, AttributeError):
                    date_str = 'לא צוין'
            elif isinstance(date_str, str):
                pass
            else:
                date_str = str(date_str) if date_str is not None else 'לא צוין'
            plan.append(f"  {i}. {expense['amount']:,.0f} ₪ - {expense['description'][:60]} ({expense['category']}) - {date_str}")
        plan.append("")
        
        # Action plan
        plan.append("=" * 80)
        plan.append("📋 תוכנית פעולה:")
        plan.append("=" * 80)
        plan.append("")
        
        if monthly_surplus > 0:
            plan.append("✅ יש לך עודף חודשי - מצוין!")
            plan.append(f"  • עם עודף של {monthly_surplus:,.0f} ₪/חודש, החוב ייסגר תוך {months_to_payoff:.1f} חודשים")
            plan.append("")
            plan.append("🎯 המלצות:")
            plan.append(f"  1. הקצה {monthly_surplus * 0.8:,.0f} ₪/חודש לפירעון החוב (80% מהעודף)")
            plan.append(f"  2. שמור {monthly_surplus * 0.2:,.0f} ₪/חודש לחיסכון חירום (20% מהעודף)")
        else:
            plan.append("⚠️ יש לך גירעון חודשי - צריך לפעול מיידית!")
            deficit = abs(monthly_surplus)
            plan.append(f"  • הגירעון החודשי הוא: {deficit:,.0f} ₪")
            plan.append(f"  • זה מסביר את החוב של {current_debt:,.0f} ₪")
            plan.append("")
            plan.append("🚨 צעדים דחופים:")
            plan.append("  1. הפחתת הוצאות מיידית - ראה המלצות להלן")
            plan.append("  2. בדיקת אפשרויות להגדלת הכנסה")
            plan.append("  3. ייעוץ פיננסי מקצועי")
        
        plan.append("")
        plan.append("💡 המלצות להפחתת הוצאות:")
        
        # Category-specific recommendations
        sorted_categories = sorted(category_breakdown.items(), key=lambda x: x[1], reverse=True)
        
        for category, total_amount in sorted_categories[:5]:  # Top 5 categories
            monthly_amount = total_amount / period_months
            if monthly_amount > 1000:  # Only suggest for significant expenses
                plan.append(f"  • {category}: {monthly_amount:,.0f} ₪/חודש")
                if category == 'מזון':
                    plan.append("    - נסה להכין רשימת קניות מראש")
                    plan.append("    - הימנע מקניות אימפולסיביות")
                    plan.append("    - השתמש בקופונים והצעות")
                elif category == 'דלק':
                    plan.append("    - נסה לשלב נסיעות")
                    plan.append("    - בדוק מחירים בתחנות שונות")
                    plan.append("    - שקול תחבורה ציבורית לנסיעות קצרות")
                elif category == 'בידור':
                    plan.append("    - צמצם בילויים יקרים")
                    plan.append("    - חפש פעילויות חינמיות")
                elif category == 'אחר':
                    plan.append("    - סקור את ההוצאות הגדולות בקטגוריה זו")
                    plan.append("    - זהה הוצאות מיותרות")
        
        plan.append("")
        plan.append("📈 יעדים מדידים:")
        target_reduction = total_monthly * 0.85
        plan.append(f"  1. הפחתת הוצאות חודשיות ל-{target_reduction:,.0f} ₪ (הפחתה של 15%)")
        plan.append(f"  2. יצירת עודף חודשי של לפחות {monthly_income * 0.1:,.0f} ₪ (10% מההכנסה)")
        if monthly_surplus > 0:
            plan.append(f"  3. פירעון החוב תוך {months_to_payoff:.1f} חודשים")
        else:
            plan.append(f"  3. יצירת עודף חודשי תוך 3 חודשים")
            plan.append(f"  4. פירעון החוב תוך {max(18, abs(current_debt) / (monthly_income * 0.1)):.0f} חודשים (לאחר יצירת עודף)")
        
        plan.append("")
        plan.append("=" * 80)
        plan.append("💡 המלצות ספציפיות:")
        plan.append("=" * 80)
        plan.append("")
        
        # Recommendations based on analysis
        if analysis.get('potentially_unnecessary'):
            unnecessary_total = sum(exp['amount'] for exp in analysis['potentially_unnecessary'])
            unnecessary_monthly = unnecessary_total / period_months
            if unnecessary_monthly > 1000:
                plan.append("🎯 הפחתת הוצאות מיותרות:")
                plan.append(f"  • ניתן לחסוך {unnecessary_monthly:,.0f} ₪/חודש על ידי הפחתת בילויים וביגוד")
                plan.append("  • המלצה: צמצם בילויים ב-50% - זה יחסוך לך לפחות {:.0f} ₪/חודש".format(unnecessary_monthly * 0.5))
                plan.append("")
        
        if analysis.get('duplicate_charges'):
            duplicates_total = sum(dup['total_amount'] for dup in analysis['duplicate_charges'])
            duplicates_monthly = duplicates_total / period_months
            if duplicates_monthly > 500:
                plan.append("🔄 בדיקת חיובים חוזרים:")
                plan.append(f"  • נמצאו חיובים חוזרים בסך {duplicates_monthly:,.0f} ₪/חודש")
                plan.append("  • המלצה: בדוק אם יש מנויים שאתה לא משתמש בהם או חיובים כפולים")
                plan.append("")
        
        if analysis.get('credit_card_analysis'):
            cc_analysis = analysis['credit_card_analysis']
            if cc_analysis.get('total_cards', 0) > 3:
                plan.append("💳 המלצות לגבי כרטיסי אשראי:")
                plan.append(f"  • יש לך {cc_analysis['total_cards']} כרטיסים פעילים - זה יותר מדי!")
                plan.append("  • המלצה: שקול לסגור כרטיסים מיותרים כדי להקל על המעקב")
                plan.append("  • המלצה: השתמש בכרטיס אחד עיקרי למעקב קל יותר")
                plan.append("  • המלצה: בדוק אם יש כרטיסים עם עמלות גבוהות - שקול להחליף")
                plan.append("")
            elif cc_analysis.get('total_cards', 0) > 1:
                plan.append("💳 המלצות לגבי כרטיסי אשראי:")
                plan.append("  • המלצה: השתמש בכרטיס אחד עיקרי למעקב קל יותר")
                plan.append("  • המלצה: בדוק אם יש כרטיסים עם עמלות גבוהות - שקול להחליף")
                plan.append("")
        
        if analysis.get('anomalies'):
            anomalies_total = sum(anom['amount'] for anom in analysis['anomalies'])
            if anomalies_total > 10000:
                plan.append("🚨 התייחסות לאנומליות:")
                plan.append(f"  • נמצאו הוצאות חריגות בסך {anomalies_total:,.0f} ₪")
                plan.append("  • המלצה: סקור את ההוצאות החריגות - האם הן היו נחוצות?")
                plan.append("  • המלצה: בעתיד, חכה 24 שעות לפני הוצאות גדולות")
                plan.append("")
        
        plan.append("")
        plan.append("=" * 80)
        plan.append("📋 דרכי פעולה מפורטות:")
        plan.append("=" * 80)
        plan.append("")
        
        # Detailed action steps
        plan.append("שלב 1: עצירת הגירעון (חודש 1-2)")
        plan.append("  פעולות מיידיות:")
        plan.append("  1. הקפא כל הוצאה לא חיונית")
        plan.append("  2. סקור את 20 ההוצאות הגדולות - זהה מה ניתן לבטל/להפחית")
        plan.append("  3. צור תקציב נוקשה - לא יותר מ-27,000 ₪ הוצאות (מלבד משכנתא)")
        plan.append("  4. עקוב אחר כל הוצאה יומית")
        plan.append("")
        
        plan.append("שלב 2: הפחתת הוצאות (חודש 2-4)")
        plan.append("  פעולות:")
        plan.append("  1. הפחת הוצאות בקטגוריות הגדולות (ראה המלצות לעיל)")
        plan.append("  2. השווה מחירים לפני כל קנייה משמעותית")
        plan.append("  3. השתמש בקופונים והצעות")
        plan.append("  4. צמצם הוצאות חוזרות מיותרות")
        plan.append("")
        
        plan.append("שלב 3: יצירת עודף (חודש 4-6)")
        plan.append("  פעולות:")
        plan.append("  1. שמור על תקציב נוקשה")
        plan.append("  2. הקצה כל העודף לפירעון החוב")
        plan.append("  3. בדוק אפשרויות להגדלת הכנסה")
        plan.append("")
        
        plan.append("שלב 4: פירעון החוב (חודש 6-18)")
        plan.append("  פעולות:")
        plan.append("  1. המשך להקצות עודף לפירעון")
        plan.append("  2. שקול פירעון מוקדם אם יש אפשרות")
        plan.append("  3. התחל לחסוך לחיסכון חירום (לאחר פירעון 50% מהחוב)")
        plan.append("")
        
        plan.append("=" * 80)
        
        return "\n".join(plan)
    
    def generate_action_plan(self, analysis: Dict, monthly_income: float, mortgage: float, current_debt: float) -> str:
        """Alias for comprehensive action plan."""
        return self.generate_comprehensive_action_plan(analysis, monthly_income, mortgage, current_debt)
    
    def generate_report(self, output_file: str, monthly_income: float, mortgage: float, current_debt: float) -> None:
        """
        Generate comprehensive financial report.
        
        Args:
            output_file: Path to output report file
            monthly_income: Monthly net income
            mortgage: Monthly mortgage payment
            current_debt: Current bank debt
        """
        logger.info("Generating financial report...")
        
        # Load transactions
        self.load_all_transactions()
        
        # Analyze expenses
        analysis = self.analyze_expenses()
        
        # Generate action plan
        action_plan = self.generate_action_plan(analysis, monthly_income, mortgage, current_debt)
        
        # Write report
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(action_plan)
            f.write("\n\n")
            f.write("=" * 80)
            f.write("\nפרטים טכניים:\n")
            f.write("=" * 80)
            f.write(f"\nסה\"כ עסקאות שנטענו: {len(self.transactions)}\n")
            f.write(f"סה\"כ הוצאות: {analysis.get('total_expenses', 0):,.0f} ₪\n")
            f.write(f"סה\"כ הכנסות (מכרטיסי אשראי): {analysis.get('total_income_cc', 0):,.0f} ₪\n")
            f.write(f"סה\"כ הלוואות שזוהו: {analysis.get('total_loans', 0):,.0f} ₪\n")
            f.write(f"מספר חודשים: {analysis.get('period_months', 0):.1f}\n")
            f.write(f"\nקבצים שנטענו:\n")
            files_loaded = set(t['file'] for t in self.transactions)
            for file in sorted(files_loaded):
                f.write(f"  - {file}\n")
        
        logger.info(f"Report saved to: {output_path}")
        print(action_plan)


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze credit card expenses')
    parser.add_argument('--data-dir', type=str, 
                       default=r'כרטיסי אשראי רועי',
                       help='Directory containing credit card Excel files')
    parser.add_argument('--income', type=float, default=37000,
                       help='Monthly net income')
    parser.add_argument('--mortgage', type=float, default=10000,
                       help='Monthly mortgage payment')
    parser.add_argument('--debt', type=float, default=-83000,
                       help='Current bank debt (negative balance)')
    parser.add_argument('--output', type=str, default='financial_action_plan.txt',
                       help='Output report file')
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = CreditCardAnalyzer(args.data_dir)
    
    # Generate report
    analyzer.generate_report(
        output_file=args.output,
        monthly_income=args.income,
        mortgage=args.mortgage,
        current_debt=args.debt
    )


if __name__ == '__main__':
    main()

