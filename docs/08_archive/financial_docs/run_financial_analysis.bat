@echo off
chcp 65001 >nul
cd /d "C:\Projects\focus_server_automation"
python scripts\analyze_credit_card_expenses.py --data-dir "כרטיסי אשראי רועי" --income 37000 --mortgage 10000 --debt -83000 --output comprehensive_financial_analysis.txt
pause

