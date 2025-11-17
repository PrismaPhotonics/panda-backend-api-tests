# רשימת טסטים חסרים - עדכון סופי

**תאריך:** 27 באוקטובר 2025  
**מקור:** xray_tests_list.txt (137 טסטים)

---

## סיכום

| קטגוריה | כמות |
|----------|------|
| **סה"כ טסטים ברשימה** | 137 |
| **ממומשים באוטומציה** | 101 |
| **Out of Scope** | 12 |
| **Backlog** | 9 |
| **Duplicates** | 2 |
| **לא ממומשים (אמיתיים)** | **13** |

---

## ❌ 13 טסטים שלא ממומשים

### 1. PZ-13879: Integration - Missing Required Fields (parent ticket)
**סטטוס:** Parent ticket  
**Sub-tickets:** PZ-13908, 13909, 13910, 13911, 13912 (כולם ממומשים)  
**פעולה:** סגור כ-"Parent" או הוסף marker ל-test class

---

### 2. PZ-13813: API - SingleChannel View Returns Correct 1:1 Mapping
**סטטוס:** Duplicate  
**מכוסה ב:** PZ-13861 (test_configure_singlechannel_mapping)  
**פעולה:** סגור כ-Duplicate

---

### 3. PZ-13770: Performance - /config Latency P95/P99
**סטטוס:** Duplicate  
**מכוסה ב:** PZ-13920, 13921  
**פעולה:** סגור כ-Duplicate

---

### 4. PZ-13768: Integration - RabbitMQ Outage Handling
**סטטוס:** Low priority  
**סיבה:** RabbitMQ לא critical (per PZ-13756)  
**פעולה:** Backlog או Won't Do

---

### 5. PZ-13705: Data Lifecycle - Historical vs Live Recordings Classification
**מה זה:** בדיקת סיווג recordings ב-MongoDB  
**פעולה נדרשת:** צריך לבנות - 30 דקות

---

### 6. PZ-13687: MongoDB Recovery - Recordings Indexed After Outage
**מה זה:** אחרי outage, recordings מתעדכנים נכון  
**פעולה נדרשת:** צריך לבנות - 40 דקות

---

### 7. PZ-13599: Data Quality - Postgres connectivity and catalogs
**מה זה:** בדיקת Postgres  
**סיבה:** אין Postgres במערכת?  
**פעולה:** בדוק אם רלוונטי, אם לא → Won't Do

---

### 8. PZ-13572: Security - Robustness to malformed inputs
**מה זה:** בדיקת אבטחה - inputs מעוותים  
**פעולה נדרשת:** צריך לבנות - 1 שעה

---

### 9. PZ-13571: Performance - /configure latency p95
**סטטוס:** Possible duplicate  
**מכוסה ב:** PZ-13920, 13921?  
**פעולה:** בדוק אם duplicate, אם לא → בנה

---

### 10. PZ-13570: E2E - Configure → Metadata → gRPC (mock)
**מה זה:** E2E test מלא  
**פעולה נדרשת:** צריך לבנות - 2 שעות

---

### 11. PZ-13558: API - Overlap/NFFT Escalation Edge Case
**מה זה:** edge case ספציפי  
**פעולה נדרשת:** צריך לבנות - 30 דקות

---

### 12. PZ-13557: API - Waterfall view handling
**מה זה:** בדיקת Waterfall view  
**פעולה נדרשת:** צריך לבנות - 40 דקות

---

### 13. PZ-13556: API - SingleChannel view mapping
**סטטוס:** Possible duplicate  
**מכוסה ב:** PZ-13861?  
**פעולה:** בדוק אם duplicate

---

## 📊 פירוט לפי פעולה נדרשת

### ✅ רק markers (1 טסט) - 5 דקות:
- PZ-13879: Parent ticket class marker

### 🔴 Duplicates לסגור (4 טסטים):
- PZ-13813 → PZ-13861
- PZ-13770 → PZ-13920, 13921
- PZ-13571 → PZ-13920, 13921
- PZ-13556 → PZ-13861

### ⚠️ לבדוק רלוונטיות (2 טסטים):
- PZ-13599: Postgres (אין Postgres?)
- PZ-13768: RabbitMQ outage (low priority)

### 🔨 לבנות (6 טסטים) - 5 שעות:
- PZ-13705: Classification (30 min)
- PZ-13687: Recovery (40 min)
- PZ-13572: Security (1 hour)
- PZ-13570: E2E gRPC (2 hours)
- PZ-13558: Overlap edge case (30 min)
- PZ-13557: Waterfall (40 min)

---

## 🎯 המלצה סופית

### פעולה מיידית (5 דקות):
סגור 4 duplicates ב-Jira

**תוצאה:** 101/109 = **92.7% כיסוי**

---

### פעולה לטווח קצר (5 שעות):
בנה 6 הטסטים הנותרים

**תוצאה:** 107/109 = **98.2% כיסוי**

---

### פעולה ב-Jira:
בדוק רלוונטיות של Postgres + RabbitMQ outage

**תוצאה אפשרית:** **100% כיסוי**

---

**נותרו באמת רק 6-8 טסטים לבנות!**

