# 🐛 הכנה לפגישת Sprint Bugs Review
**תאריך:** 19 בנובמבר 2025, 11:30-12:30  
**מארגן:** רוי אברהמי

---

## 📊 סיכום כללי - סטטיסטיקות

### מספרים עיקריים:
- **סה"כ באגים בספרינט:** 28 באגים
- **באגים שתוקנו:** 0 (0%)
- **באגים שנותרו פתוחים:** 28 (100%)
- **באגים חדשים בספרינט האחרון:** 7 באגים (נוצרו מ-10/11 ואילך)

### חלוקה לפי עדיפות:
| עדיפות | מספר באגים | אחוז |
|--------|------------|------|
| 🔴 **Highest** | 6 | 21% |
| 🟠 **High** | 10 | 36% |
| 🟡 **Medium** | 12 | 43% |

---

## 👥 חלוקה לפי אחראי (Assignee)

### Oded Aviyam (עודד אביאם) - 13 באגים
**Highest Priority (3):**
- PZ-15003: The spectrogram streaming rate is not as design
- PZ-14925: Missing job_id label in K8s Pods prevents Backend from finding Pods
- PZ-13640: Focus Server - Slow Response During MongoDB Outage (SLA Violation)

**High Priority (6):**
- PZ-14977: Alert API accepts requests with missing required fields without validation
- PZ-14976: Alert API accepts negative DOF values without validation
- PZ-14975: Alert API accepts invalid Class ID values without validation
- PZ-14926: Job configuration not saved to MongoDB after POST /configure
- PZ-13985: Live Metadata Missing Required Fields
- PZ-13268: Valid /configure sometimes 200, sometimes 500; CNI IP exhaustion

**Medium Priority (4):**
- PZ-14714: /configure endpoint doesn't validate metadata availability
- PZ-14713: /configure endpoint returns unclear error when waiting for fiber
- PZ-13503: Logic count 1 port & many open services as allocated error
- PZ-13238: Waterfall configuration fails when optional fields are omitted

### yonatan.rubin (יונתן רובין) - 4 באגים
**Highest Priority (3):**
- PZ-14846: On disconnections there's no alert on trying to open analyze from alert
- PZ-14845: When K9s crash unexpected there's no option to open new analyzes
- PZ-14843: Z pool disconnect under pressure

**Medium Priority (1):**
- PZ-14705: Live View/Investigations - There's no any type of map

### Benny Koren (בני קורן) - 7 באגים
**Highest Priority (1):**
- PZ-13983: MongoDB Indexes Missing

**High Priority (3):**
- PZ-13669: Focus Server - SingleChannel View Accepts Multiple Channels
- PZ-13667: Focus Server - Empty Status String in Configure Response
- PZ-13267: /configure returns 500 when frequencyRange=null (should be 422)

**Medium Priority (3):**
- PZ-13670: Focus Server - Job Cancellation Endpoint Returns 404
- PZ-13272: Response invariants broken
- PZ-13271: Response type mismatches vs. OpenAPI
- PZ-13269: Immediate GET /metadata/{job_id} after /configure returns 404 (race)

### Ohad Vaknin (אוהד וקנין) - 1 באג
**High Priority (1):**
- PZ-13984: Future Timestamp Validation Gap

### ללא אחראי - 3 באגים
**High Priority (1):**
- PZ-13986: 200 Jobs Capacity Issue

**Medium Priority (2):**
- PZ-13266: /configure returns 500 instead of 422 when required fields missing
- PZ-13272: Response invariants broken (duplicate?)

---

## 🏷️ חלוקה לפי קטגוריות (Labels)

### API & Validation Issues (8 באגים)
- בעיות validation ב-API
- שגיאות HTTP codes לא נכונים (500 במקום 422)
- חוסר validation על שדות חובה

### Infrastructure & Kubernetes (5 באגים)
- בעיות K8s labels
- בעיות MongoDB connection
- בעיות CNI IP exhaustion

### Data Integrity & Security (4 באגים)
- בעיות validation של נתונים
- בעיות אבטחה
- בעיות data quality

### UI/UX Issues (4 באגים)
- בעיות בממשק משתמש
- בעיות alerts
- בעיות disconnection handling

### Performance & Scaling (2 באגים)
- בעיות ביצועים
- בעיות קיבולת

---

## 🎯 המלצות להעברה לספרינט הבא

### 🔴 קריטי - חובה לתקן (Highest Priority - 6 באגים)

1. **PZ-15003** - Spectrogram streaming rate (Oded)
   - **למה קריטי:** בעיה ב-core functionality
   - **הערכה:** 2-3 ימים
   
2. **PZ-14925** - Missing job_id label in K8s (Oded)
   - **למה קריטי:** מונע מהבקאנד למצוא Pods
   - **הערכה:** 1-2 ימים
   
3. **PZ-14846** - No alert on disconnections (yonatan)
   - **למה קריטי:** בעיה ב-UX קריטית
   - **הערכה:** 1 יום
   
4. **PZ-14845** - No option to open new analyzes after crash (yonatan)
   - **למה קריטי:** בעיה ב-UX קריטית
   - **הערכה:** 1-2 ימים
   
5. **PZ-14843** - Z pool disconnect under pressure (yonatan)
   - **למה קריטי:** בעיית יציבות תחת עומס
   - **הערכה:** 2-3 ימים
   
6. **PZ-14712** - Focus Server pod restarts due to MongoDB (yonatan)
   - **למה קריטי:** בעיית יציבות קריטית
   - **הערכה:** 2-3 ימים

### 🟠 חשוב - מומלץ לתקן (High Priority - 10 באגים)

**קבוצה 1: API Validation (3 באגים) - Oded**
- PZ-14977, PZ-14976, PZ-14975
- **הערכה:** 2-3 ימים (כולם יחד)
- **למה חשוב:** בעיות אבטחה ו-data integrity

**קבוצה 2: MongoDB & Persistence (2 באגים)**
- PZ-14926: Job configuration not saved (Oded) - 1-2 ימים
- PZ-13983: MongoDB Indexes Missing (Benny) - 2-3 ימים

**קבוצה 3: API Error Handling (3 באגים)**
- PZ-13669, PZ-13667, PZ-13267 (Benny)
- **הערכה:** 3-4 ימים (כולם יחד)

**קבוצה 4: אחר (2 באגים)**
- PZ-13985: Live Metadata Missing Fields (Oded) - 1-2 ימים
- PZ-13984: Future Timestamp Validation (Ohad) - 1 יום

### 🟡 בינוני - לפי זמינות (Medium Priority - 12 באגים)
- ניתן לדחות אם אין זמן
- רוב הבעיות הן UX improvements או edge cases

---

## 💬 נקודות דיבור לפגישה

### פתיחה (2 דקות)
> "שלום לכולם, בואו נתחיל בסקירה של הספרינט האחרון. 
> 
> **סיכום מהיר:**
> - מצאנו **28 באגים** בסך הכל
> - **7 באגים חדשים** נפתחו בספרינט האחרון (מ-10/11)
> - **0 באגים תוקנו** - זה נושא שצריך לטפל בו
> 
> **חלוקה לפי עדיפות:**
> - 6 באגים ב-Highest priority (21%)
> - 10 באגים ב-High priority (36%)
> - 12 באגים ב-Medium priority (43%)"

### סקירת באגים שתוקנו (1 דקות)
> "**באגים שתוקנו:** 
> לצערנו, **אף באג לא תוקן** בספרינט האחרון. זה מצביע על כך ש:
> 1. יש עומס עבודה גבוה על הפיתוח
> 2. יש צורך להקצות זמן ייעודי לתיקוני באגים
> 3. אולי צריך לבדוק אם יש באגים שצריך לשנות את הסטטוס שלהם"

### סקירת באגים שנותרו פתוחים (5 דקות)

#### Highest Priority (6 באגים)
> "**באגים ב-Highest Priority - 6 באגים:**
> 
> **1. PZ-15003** - Spectrogram streaming rate לא לפי עיצוב (Oded)
>    - זה באג חדש מ-17/11, בעיה ב-core functionality
>    - הערכה: 2-3 ימים
> 
> **2. PZ-14925** - Missing job_id label ב-K8s (Oded)
>    - מונע מהבקאנד למצוא Pods - בעיה קריטית
>    - הערכה: 1-2 ימים
> 
> **3. PZ-14846** - אין alert על disconnections (yonatan)
>    - בעיית UX קריטית - משתמש לא יודע מה קורה
>    - הערכה: 1 יום
> 
> **4. PZ-14845** - אין אפשרות לפתוח analyzes חדשים אחרי crash (yonatan)
>    - בעיית UX קריטית נוספת
>    - הערכה: 1-2 ימים
> 
> **5. PZ-14843** - Z pool disconnect תחת עומס (yonatan)
>    - בעיית יציבות תחת עומס
>    - הערכה: 2-3 ימים
> 
> **6. PZ-14712** - Focus Server pod restarts בגלל MongoDB (yonatan)
>    - בעיית יציבות קריטית
>    - הערכה: 2-3 ימים
> 
> **סה"כ עבודה מוערכת:** ~10-14 ימי עבודה"

#### High Priority (10 באגים)
> "**באגים ב-High Priority - 10 באגים:**
> 
> **קבוצת API Validation (3 באגים - Oded):**
> - PZ-14977, PZ-14976, PZ-14975 - בעיות validation ב-Alert API
> - הערכה: 2-3 ימים (כולם יחד)
> - חשוב לתקן בגלל בעיות אבטחה ו-data integrity
> 
> **בעיות MongoDB & Persistence (2 באגים):**
> - PZ-14926: Job configuration לא נשמר (Oded) - 1-2 ימים
> - PZ-13983: MongoDB Indexes חסרים (Benny) - 2-3 ימים
> 
> **בעיות API Error Handling (3 באגים - Benny):**
> - PZ-13669, PZ-13667, PZ-13267
> - הערכה: 3-4 ימים (כולם יחד)
> 
> **אחר (2 באגים):**
> - PZ-13985: Live Metadata חסר שדות (Oded) - 1-2 ימים
> - PZ-13984: Future Timestamp Validation (Ohad) - 1 יום
> 
> **סה"כ עבודה מוערכת:** ~10-14 ימי עבודה"

#### Medium Priority (12 באגים)
> "**באגים ב-Medium Priority - 12 באגים:**
> 
> רוב הבעיות הן:
> - שיפורי UX
> - Edge cases
> - בעיות validation פחות קריטיות
> 
> **המלצה:** ניתן לדחות אם אין זמן, אבל כדאי לתקן לפני Pre-FAT"

### חלוקה לפי אחראי (3 דקות)
> "**חלוקת עבודה לפי אחראי:**
> 
> **Oded Aviyam** - 13 באגים (46% מהבאגים)
> - 3 Highest, 6 High, 4 Medium
> - הערכה: ~15-20 ימי עבודה
> 
> **yonatan.rubin** - 4 באגים
> - 3 Highest, 1 Medium
> - הערכה: ~5-7 ימי עבודה
> 
> **Benny Koren** - 7 באגים
> - 1 Highest, 3 High, 3 Medium
> - הערכה: ~8-10 ימי עבודה
> 
> **Ohad Vaknin** - 1 באג
> - 1 High
> - הערכה: ~1 יום
> 
> **ללא אחראי** - 3 באגים
> - צריך להקצות אחראי"

### המלצות להעברה לספרינט הבא (5 דקות)

> "**המלצות להעברה לספרינט הבא:**
> 
> **חובה להעביר (Highest Priority - 6 באגים):**
> - כל 6 הבאגים ב-Highest Priority
> - סה"כ: ~10-14 ימי עבודה
> - **סיבה:** בעיות קריטיות ב-core functionality, יציבות, ו-UX
> 
> **מומלץ להעביר (High Priority - 10 באגים):**
> - כל 10 הבאגים ב-High Priority
> - סה"כ: ~10-14 ימי עבודה
> - **סיבה:** בעיות אבטחה, data integrity, ו-API validation
> 
> **לפי זמינות (Medium Priority - 12 באגים):**
> - ניתן לדחות אם אין זמן
> - אבל כדאי לתקן לפני Pre-FAT (30/11)
> 
> **סה"כ עבודה מוערכת:** ~20-28 ימי עבודה
> 
> **המלצה:**
> 1. להקצות זמן ייעודי לתיקוני באגים בספרינט הבא
> 2. להתמקד ב-Highest ו-High Priority
> 3. לבדוק אם יש באגים שצריך לשנות עדיפות"

### תובנות ולמידה (3 דקות)

> "**תובנות מהספרינט האחרון:**
> 
> **1. בעיות חוזרות:**
> - **API Validation:** יש הרבה בעיות validation ב-API
>   - **המלצה:** לעשות code review ממוקד על validation
>   - **המלצה:** להוסיף automated tests ל-validation
> 
> - **MongoDB Issues:** יש כמה בעיות MongoDB
>   - **המלצה:** לבדוק את ה-MongoDB connection handling
>   - **המלצה:** לבדוק את ה-indexes
> 
> - **Error Handling:** יש בעיות ב-error handling
>   - **המלצה:** לסטנדרטיזציה של error codes (422 במקום 500)
> 
> **2. חלוקת עבודה:**
> - Oded אחראי על 46% מהבאגים - זה הרבה
>   - **המלצה:** לבדוק אם צריך לחלק עבודה
> 
> **3. תהליך:**
> - 0 באגים תוקנו - זה בעיה
>   - **המלצה:** להקצות זמן ייעודי לתיקוני באגים
>   - **המלצה:** לבדוק אם יש באגים שצריך לשנות סטטוס
> 
> **4. תזמון:**
> - Pre-FAT ב-30/11 - יש לנו 11 ימים
>   - **המלצה:** להתמקד ב-Highest Priority לפני Pre-FAT
>   - **המלצה:** לתכנן את הספרינט הבא בהתאם"

### שאלות לדיון (5 דקות)

> "**שאלות לדיון:**
> 
> 1. **תיקוני באגים:**
>    - למה אף באג לא תוקן בספרינט האחרון?
>    - איך נוודא שבספרינט הבא יתוקנו באגים?
> 
> 2. **עדיפויות:**
>    - האם העדיפויות נכונות?
>    - האם יש באגים שצריך לשנות עדיפות?
> 
> 3. **העברה לספרינט הבא:**
>    - כמה זמן להקצות לתיקוני באגים?
>    - איזה באגים חובה לתקן לפני Pre-FAT?
> 
> 4. **חלוקת עבודה:**
>    - האם החלוקה הנוכחית נכונה?
>    - האם צריך להעביר באגים בין אנשים?
> 
> 5. **תהליך:**
>    - האם התהליך הנוכחי עובד?
>    - מה אפשר לשפר?"

---

## 📋 Checklist לפני הפגישה

- [x] ניתוח כל הבאגים
- [x] חישוב סטטיסטיקות
- [x] הכנת המלצות
- [x] הכנת נקודות דיבור
- [ ] לפתוח את Jira ולבדוק את הבאגים
- [ ] לבדוק אם יש באגים שצריך לעדכן סטטוס
- [ ] להכין רשימת שאלות ספציפיות

---

## 🔗 קישורים רלוונטיים

- **Jira Filter:** https://prismaphotonics.atlassian.net/issues/?filter=13012
- **Pre-FAT Date:** 30 בנובמבר 2025
- **Sprint Start:** TBD

---

## 📝 הערות נוספות

### נושאים שצריך להעלות בפגישה:
1. **תהליך תיקוני באגים:** למה אף באג לא תוקן?
2. **תזמון:** Pre-FAT ב-30/11 - יש לנו 11 ימים
3. **עדיפויות:** האם העדיפויות נכונות?
4. **חלוקת עבודה:** האם החלוקה נכונה?

### נושאים שצריך לבדוק:
1. האם יש באגים שצריך לשנות סטטוס?
2. האם יש באגים שצריך לשנות עדיפות?
3. האם יש באגים שצריך להקצות אחראי?

---

**נוצר:** 19 בנובמבר 2025  
**מכין:** AI Assistant  
**סטטוס:** ✅ מוכן לפגישה

