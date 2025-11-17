#!/usr/bin/env python3
"""
Create a detailed and accurate financial action plan based on all available data.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from analyze_credit_card_expenses import CreditCardAnalyzer

def main():
    # Current date
    current_date = datetime(2025, 11, 12)
    
    # Accurate data from bank statements (from final_financial_analysis.md)
    bank_balance = -83561.65  # יתרת עו"ש
    monthly_income = 33237.86  # הכנסות חודשיות
    monthly_expenses_total = 92263.97  # הוצאות חודשיות כולל
    monthly_deficit = -59026.11  # גירעון חודשי
    
    mortgage_monthly = 17004.08  # החזר משכנתא חודשי
    loan_balance = 123825.68  # יתרת הלוואה
    loan_monthly_estimate = 2000  # הערכה לתשלום חודשי הלוואה
    
    # Load credit card transactions
    data_dir = Path(r"כרטיסי אשראי רועי")
    analyzer = CreditCardAnalyzer(data_dir)
    analyzer.load_all_transactions()
    
    # Analyze expenses
    analysis = analyzer.analyze_expenses()
    
    # Calculate other expenses (total - mortgage - loan)
    other_expenses = monthly_expenses_total - mortgage_monthly - loan_monthly_estimate
    
    # Get duplicate charges
    duplicate_charges = analysis.get('duplicate_charges', [])
    duplicate_total = sum(d['total_amount'] for d in duplicate_charges)
    duplicate_monthly = duplicate_total / 6 if duplicate_total > 0 else 0  # Assuming 6 months period
    
    # Get recurring expenses
    recurring_expenses = analysis.get('recurring_expenses', {})
    recurring_monthly = sum(recurring_expenses.values()) if recurring_expenses else 0
    
    # Get potentially unnecessary expenses
    unnecessary_expenses = analysis.get('potentially_unnecessary', [])
    unnecessary_total = sum(exp['amount'] for exp in unnecessary_expenses)
    unnecessary_monthly = unnecessary_total / 6 if unnecessary_total > 0 else 0
    
    # Create detailed action plan
    plan = []
    plan.append("=" * 80)
    plan.append("תוכנית פעולה פיננסית מפורטת ומדויקת")
    plan.append("=" * 80)
    plan.append("")
    plan.append(f"תאריך: {current_date.strftime('%d/%m/%Y')}")
    plan.append("")
    
    # Current situation
    plan.append("=" * 80)
    plan.append("מצב נוכחי - נתונים מדויקים מהבנק")
    plan.append("=" * 80)
    plan.append("")
    plan.append("יתרות וחשבונות:")
    plan.append(f"  • יתרת עו\"ש: {bank_balance:,.2f} ₪ (מינוס בבנק)")
    plan.append(f"  • מסגרת אשראי: 25,000 ₪")
    plan.append("")
    plan.append("הכנסות והוצאות חודשיות:")
    plan.append(f"  • הכנסה חודשית נטו: {monthly_income:,.2f} ₪")
    plan.append(f"  • הוצאות חודשיות כולל: {monthly_expenses_total:,.2f} ₪")
    plan.append(f"  • גירעון חודשי: {monthly_deficit:,.2f} ₪ ⚠️⚠️⚠️")
    plan.append("")
    plan.append("פילוח הוצאות חודשיות:")
    plan.append(f"  • משכנתא: {mortgage_monthly:,.2f} ₪ ({mortgage_monthly/monthly_expenses_total*100:.1f}%)")
    plan.append(f"  • הלוואה (הערכה): {loan_monthly_estimate:,.0f} ₪ ({loan_monthly_estimate/monthly_expenses_total*100:.1f}%)")
    plan.append(f"  • הוצאות אחרות: {other_expenses:,.2f} ₪ ({other_expenses/monthly_expenses_total*100:.1f}%) ⚠️")
    plan.append("")
    
    # Loans and mortgage
    plan.append("הלוואות ומשכנתאות:")
    plan.append(f"  • הלוואה ברגע: {loan_balance:,.2f} ₪")
    plan.append(f"    - קרן הלוואה: 125,000 ₪")
    plan.append(f"    - ריבית: 4.65%")
    plan.append(f"    - תאריך סיום: 10/10/31")
    plan.append("")
    plan.append(f"  • משכנתא: 2,526,341.91 ₪")
    plan.append(f"    - החזר חודשי: {mortgage_monthly:,.2f} ₪")
    plan.append(f"    - תאריך סיום: 10/10/2055")
    plan.append("")
    
    # Critical analysis
    plan.append("=" * 80)
    plan.append("ניתוח קריטי")
    plan.append("=" * 80)
    plan.append("")
    plan.append("בעיות קריטיות:")
    plan.append(f"  1. גירעון חודשי עצום: {abs(monthly_deficit):,.2f} ₪/חודש")
    plan.append(f"     • אתה מוציא {monthly_expenses_total/monthly_income:.1f}x מההכנסה שלך!")
    plan.append(f"     • כל חודש המינוס גדל ב-{abs(monthly_deficit):,.0f} ₪")
    plan.append("")
    plan.append(f"  2. הוצאות אחרות גבוהות מדי: {other_expenses:,.2f} ₪/חודש")
    plan.append(f"     • זה {other_expenses/monthly_income*100:.1f}% מההכנסה החודשית!")
    plan.append(f"     • צריך לחתוך לפחות {other_expenses - (monthly_income - mortgage_monthly - loan_monthly_estimate):,.0f} ₪/חודש")
    plan.append("")
    plan.append("  3. המשכנתא גבוהה:")
    plan.append(f"     • {mortgage_monthly/monthly_income*100:.1f}% מההכנסה החודשית רק על משכנתא")
    plan.append(f"     • עם הלוואה: {(mortgage_monthly + loan_monthly_estimate)/monthly_income*100:.1f}% מההכנסה על חובות")
    plan.append("")
    
    # Projections
    plan.append("תחזית אם לא ננקטת פעולה:")
    months = [1, 3, 6, 12]
    for m in months:
        projected_deficit = bank_balance + (monthly_deficit * m)
        plan.append(f"  • תוך {m} חודש{'ים' if m > 1 else ''}: {projected_deficit:,.0f} ₪")
    plan.append("")
    
    # Analysis from credit cards
    plan.append("=" * 80)
    plan.append("ניתוח מכרטיסי אשראי")
    plan.append("=" * 80)
    plan.append("")
    
    if duplicate_charges:
        plan.append(f"חיובים כפולים/חוזרים שזוהו: {len(duplicate_charges)} קבוצות")
        plan.append(f"  • סה\"כ חיובים כפולים: {duplicate_total:,.0f} ₪")
        plan.append(f"  • ממוצע חודשי: {duplicate_monthly:,.0f} ₪/חודש")
        plan.append("  • חיובים הגדולים ביותר:")
        for i, dup in enumerate(duplicate_charges[:5], 1):
            plan.append(f"    {i}. {dup['description'][:50]}: {dup['count']} פעמים, {dup['avg_amount']:,.0f} ₪ כל פעם, סה\"כ {dup['total_amount']:,.0f} ₪")
        plan.append("")
    
    if recurring_expenses:
        plan.append(f"הוצאות חוזרות משמעותיות: {len(recurring_expenses)} קטגוריות")
        for cat, monthly_avg in sorted(recurring_expenses.items(), key=lambda x: x[1], reverse=True)[:5]:
            plan.append(f"  • {cat}: {monthly_avg:,.0f} ₪/חודש")
        plan.append("")
    
    if unnecessary_expenses:
        plan.append(f"הוצאות שניתן לוותר עליהן: {len(unnecessary_expenses)} עסקאות")
        plan.append(f"  • סה\"כ: {unnecessary_total:,.0f} ₪")
        plan.append(f"  • ממוצע חודשי: {unnecessary_monthly:,.0f} ₪/חודש")
        plan.append("  • הוצאות הגדולות ביותר:")
        for i, exp in enumerate(unnecessary_expenses[:10], 1):
            plan.append(f"    {i}. {exp['amount']:,.0f} ₪ - {exp['description'][:50]}")
        plan.append("")
    
    # Action plan
    plan.append("=" * 80)
    plan.append("תוכנית פעולה מפורטת")
    plan.append("=" * 80)
    plan.append("")
    
    # Immediate actions
    plan.append("פעולות מיידיות (היום-השבוע):")
    plan.append("")
    plan.append("1. עצור כל הוצאה לא חיונית:")
    plan.append(f"   • אתה במינוס של {abs(bank_balance):,.0f} ₪")
    plan.append(f"   • כל יום המינוס גדל ב-{abs(monthly_deficit)/30:,.0f} ₪")
    plan.append("")
    plan.append("2. בדוק חיובים כפולים:")
    if duplicate_charges:
        plan.append(f"   • יש {len(duplicate_charges)} קבוצות של חיובים כפולים")
        plan.append(f"   • פוטנציאל החזר: עד {duplicate_total:,.0f} ₪")
        plan.append("   • פעולה: פנה לספקים להחזר חיובים כפולים")
    plan.append("")
    plan.append("3. ביטול מנויים וחיובים חוזרים מיותרים:")
    if recurring_expenses:
        plan.append(f"   • יש הוצאות חוזרות של {recurring_monthly:,.0f} ₪/חודש")
        plan.append("   • פעולה: סקור כל חיוב חוזר - האם אתה משתמש בשירות?")
        plan.append("   • ביטל מנויים מיותרים")
    plan.append("")
    plan.append("4. צור תקציב נוקשה:")
    plan.append("   • משכנתא: 17,004 ₪ (לא ניתן לשנות)")
    plan.append("   • הלוואה: 2,000 ₪")
    plan.append("   • הוצאות חיוניות: 10,000 ₪ (אוכל, דלק, ביטוחים)")
    plan.append(f"   • סה\"כ מקסימום: 29,004 ₪/חודש")
    plan.append(f"   • זה עדיין פחות מההכנסה ({monthly_income:,.0f} ₪) - יישאר עודף של {monthly_income - 29004:,.0f} ₪")
    plan.append("")
    
    # Short term
    plan.append("קצר טווח (החודש הקרוב):")
    plan.append("")
    plan.append("1. הפחת הוצאות ב-63,259 ₪/חודש:")
    plan.append(f"   • מהוצאות של {monthly_expenses_total:,.0f} ₪ ל-29,004 ₪")
    plan.append(f"   • זה יביא לאיזון תקציבי (הוצאות = הכנסות)")
    plan.append("")
    plan.append("2. עקוב אחר כל הוצאה יומית:")
    plan.append("   • רשום כל הוצאה")
    plan.append("   • בדוק לפני כל קנייה: האם זה חיוני?")
    plan.append("   • עצור כל הוצאה לא חיונית")
    plan.append("")
    plan.append("3. בדוק חיובים כפולים והחזר:")
    if duplicate_charges:
        plan.append(f"   • יש {len(duplicate_charges)} קבוצות של חיובים כפולים")
        plan.append(f"   • פנה לספקים להחזר")
        plan.append(f"   • פוטנציאל החזר: עד {duplicate_total:,.0f} ₪")
    plan.append("")
    
    # Medium term
    plan.append("בינוני טווח (3-6 חודשים):")
    plan.append("")
    plan.append("1. השג איזון תקציבי:")
    plan.append("   • הוצאות ≤ הכנסות")
    plan.append(f"   • הוצאות מקסימום: {monthly_income:,.0f} ₪/חודש")
    plan.append("")
    plan.append("2. התחל ליצור עודף חודשי:")
    plan.append(f"   • יעד: עודף של לפחות 5,000 ₪/חודש")
    plan.append(f"   • זה דורש הוצאות ≤ {monthly_income - 5000:,.0f} ₪/חודש")
    plan.append("")
    plan.append("3. התחל לפירעון המינוס:")
    plan.append(f"   • עם עודף של 5,000 ₪/חודש")
    plan.append(f"   • המינוס ייפרע תוך {abs(bank_balance)/5000:.0f} חודשים")
    plan.append("")
    plan.append("4. שקול הגדלת הכנסה:")
    plan.append(f"   • צריך לפחות {monthly_expenses_total * 0.9:,.0f} ₪/חודש נטו כדי לכסות את ההוצאות")
    plan.append("   • זה דורש הגדלת הכנסה ב-{monthly_expenses_total * 0.9 - monthly_income:,.0f} ₪/חודש")
    plan.append("")
    
    # Long term
    plan.append("ארוך טווח (6-12 חודשים):")
    plan.append("")
    plan.append("1. איזון תקציבי קבוע:")
    plan.append("   • הוצאות = הכנסות")
    plan.append("   • יצירת עודף חודשי קבוע")
    plan.append("")
    plan.append("2. פירעון המינוס:")
    plan.append(f"   • יעד: פירעון מלא של המינוס ({abs(bank_balance):,.0f} ₪)")
    plan.append(f"   • עם עודף של 5,000 ₪/חודש: תוך {abs(bank_balance)/5000:.0f} חודשים")
    plan.append("")
    plan.append("3. פירעון חלקי של החובות:")
    plan.append("   • שקול פירעון מוקדם חלקי של ההלוואה")
    plan.append("   • זה יקטין את התשלום החודשי")
    plan.append("")
    
    # Measurable goals
    plan.append("=" * 80)
    plan.append("יעדים מדידים")
    plan.append("=" * 80)
    plan.append("")
    
    months_goals = [
        (1, 30000, "דצמבר 2025"),
        (2, 29000, "ינואר 2026"),
        (3, 28000, "פברואר 2026"),
        (6, 27000, "מאי 2026"),
    ]
    
    for months, max_expenses, month_name in months_goals:
        remaining = monthly_income - max_expenses
        plan.append(f"{month_name} (חודש {months}):")
        plan.append(f"  • הוצאות מקסימום: {max_expenses:,} ₪")
        plan.append(f"  • עודף צפוי: {remaining:,.0f} ₪")
        if remaining > 0:
            projected_balance = bank_balance + (monthly_deficit * (months - 1)) + (remaining * 1)
            plan.append(f"  • יתרה צפויה: {projected_balance:,.0f} ₪")
        plan.append("")
    
    # Summary
    plan.append("=" * 80)
    plan.append("סיכום")
    plan.append("=" * 80)
    plan.append("")
    plan.append("מצב נוכחי:")
    plan.append(f"  • מינוס בבנק: {bank_balance:,.0f} ₪")
    plan.append(f"  • גירעון חודשי: {monthly_deficit:,.0f} ₪")
    plan.append(f"  • הוצאות אחרות: {other_expenses:,.0f} ₪/חודש")
    plan.append("")
    plan.append("הבעיה העיקרית:")
    plan.append(f"  • הוצאות של {other_expenses:,.0f} ₪/חודש מעבר למשכנתא והלוואה")
    plan.append(f"  • זה {other_expenses/monthly_income*100:.1f}% מההכנסה החודשית!")
    plan.append("")
    plan.append("הפתרון:")
    plan.append(f"  • הפחתת הוצאות ב-{other_expenses - (monthly_income - mortgage_monthly - loan_monthly_estimate):,.0f} ₪/חודש")
    plan.append(f"  • זה יביא לאיזון תקציבי")
    plan.append("")
    plan.append("הזמן:")
    plan.append(f"  • צריך לפעול מיידית!")
    plan.append(f"  • כל יום של דחייה מגדיל את המינוס ב-{abs(monthly_deficit)/30:,.0f} ₪")
    plan.append("")
    
    # Save plan
    output_file = Path("detailed_action_plan.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(plan))
    
    print('\n'.join(plan))
    print("")
    print(f"התוכנית נשמרה לקובץ: {output_file}")

if __name__ == '__main__':
    main()

