# 📊 ניתוח מפורט - 12 הטסטים שנותרו

**תאריך:** 27 באוקטובר 2025  
**מטרה:** להחליט אם צריך לממש את הטסטים או לסגור אותם

---

## קבוצה 1: Integration Outage Tests (4 טסטים)

### PZ-13767: MongoDB Outage Handling
**מה זה בודק:**
- כשMongoDB נופל, המערכת מגיבה נכון
- Historic playback חוזר 503 (Service Unavailable)
- לא נוצרים jobs חלקיים או side effects

**האם קיים?**
✅ **כן!** ב-`test_mongodb_outage_resilience.py`

**פעולה נדרשת:**
רק להוסיף Xray marker `@pytest.mark.xray("PZ-13767")`

---

### PZ-13768: RabbitMQ Outage Handling
**מה זה בודק:**
- כשRabbitMQ נופל, המערכת מגיבה נכון
- ROI/Colormap commands נכשלים gracefully
- לא קורסת המערכת

**האם צריך?**
🟡 **תלוי ב-scope:**
- אם ROI הוא critical feature → **צריך**
- אם ROI הוא nice-to-have → **לא דחוף**

**החלטת הפגישה (PZ-13756):**
> ROI Change = NEW CONFIG REQUEST (לא דרך RabbitMQ)

**המלצה:**
⚠️ **עדיפות נמוכה** - RabbitMQ לא critical לפי החלטת הפגישה

---

### PZ-13603: Mongo Outage on History Configure
**מה זה בודק:**
- כשמבקשים historic playback ו-MongoDB down
- חוזר 503 (לא 200 או 500)
- לא מתחיל orchestration/baby

**האם קיים?**
✅ **כן!** ב-`test_mongodb_outage_resilience.py`

**פעולה נדרשת:**
רק להוסיף marker

---

### PZ-13602: RabbitMQ Outage on Live Configure  
**זהה ל-PZ-13768**

**המלצה:**
⚠️ **עדיפות נמוכה**

---

## קבוצה 2: Orchestration Tests (3 טסטים)

### PZ-13604: Orchestrator Error Triggers Rollback
**מה זה בודק:**
- אם baby/orchestrator נכשל → rollback מלא
- MongoDB נקי (לא נשארו tasks חלקיים)
- Kubernetes נקי (לא נשארו pods)

**האם קיים?**
✅ **כן!** ב-`test_mongodb_outage_resilience.py` (שורה 6)

**פעולה נדרשת:**
רק להוסיף marker

---

### PZ-13601: History with Empty Window Returns 400
**מה זה בודק:**
- בקשה ל-historic playback לtime range ללא data
- חוזר 400 Bad Request (לא 200)
- לא נוצר job

**האם צריך?**
🟢 **כן - טסט validation חשוב!**

**החלטה:**
✅ **צריך לממש** - ~20 דקות

---

### PZ-13600: Invalid Configure Does Not Launch Orchestration
**מה זה בודק:**
- config request לא תקין
- לא מתחיל orchestration/baby
- לא נוצרים pods ב-K8s
- validation לפני orchestration

**האם צריך?**
🟢 **כן - בדיקת safety חשובה!**

**החלטה:**
✅ **צריך לממש** - ~30 דקות

---

## קבוצה 3: API Quality Standards (8 טסטים)

### PZ-13299: 4xx Errors Do Not Log Stack Traces
**מה זה בודק:**
- שגיאת validation (400) → לא כותבת stack trace ללוג
- רק שגיאות server (500) כותבות stack trace
- logs נקיים ולא מלוכלכים

**האם צריך?**
🟡 **Nice to have, לא critical**

**החלטה:**
⚠️ **עדיפות נמוכה** - בדיקת איכות logging

---

### PZ-13298: OpenAPI Contract Alignment
**מה זה בודק:**
- ה-API תואם ל-OpenAPI spec
- כל ה-endpoints מתועדים
- Schema validation נכונה

**האם צריך?**
🟡 **Nice to have**

**החלטה:**
⚠️ **עדיפות נמוכה** - בדיקת documentation

---

### PZ-13297: Error Body Uniformity
**מה זה בודק:**
- כל השגיאות חוזרות בפורמט אחיד
- `{"error": "...", "message": "...", "code": 400}`
- עקביות בtructure

**האם צריך?**
🟡 **Nice to have**

**החלטה:**
⚠️ **עדיפות נמוכה**

---

### PZ-13296: Waterfall Behavior with Optional Fields Omitted
### PZ-13295: Time Validation Uses Epoch
### PZ-13294: Stream Endpoint Reachability
### PZ-13293: Metadata Readiness
### PZ-13292: Response Invariants
### PZ-13291: MULTICHANNEL Validation

**כל אלה:**
- בדיקות איכות API
- עקביות responses
- edge cases של ה-API

**החלטה:**
⚠️ **עדיפות נמוכה** - API quality, לא functionality

---

## קבוצה 4: Edge Cases ישנים (5 טסטים)

### PZ-13813: SingleChannel 1:1 Mapping
**מה זה בודק:**
- SingleChannel view מחזיר mapping 1:1

**האם קיים?**
✅ **כן!** ב-`test_singlechannel_view_mapping.py` (PZ-13861)

**החלטה:**
🔴 **כפילות** - PZ-13861 כבר מכסה את זה

---

### PZ-13770: /config Latency P95/P99
**מה זה בודק:**
- זהה ל-PZ-13920, 13921 שכבר ממומשים

**החלטה:**
🔴 **כפילות** - כבר יש PZ-13920, 13921

---

### PZ-13705: Historical vs Live Classification
### PZ-13687: MongoDB Recovery
### PZ-13599: Postgres Connectivity

**אלה טסטים ישנים:**
- אולי מתייחסים לגרסה ישנה של המערכת
- אולי לא רלוונטיים יותר

**החלטה:**
🟡 **לבדוק עם המנהל** - אולי outdated

---

## 📊 סיכום והמלצות

### ✅ צריך לממש (2 טסטים) - 30 דקות:
1. **PZ-13601:** History Empty Window → 400
2. **PZ-13600:** Invalid Config No Orchestration

**תוצאה:** כיסוי → 92%

---

### 🔄 צריך רק markers (3 טסטים) - 10 דקות:
1. **PZ-13767:** MongoDB Outage (קיים)
2. **PZ-13603:** Mongo Outage History (קיים)
3. **PZ-13604:** Orchestrator Rollback (קיים)

**תוצאה:** כיסוי → 94.4%

---

### 🔴 כפילויות/לא רלוונטי (4 טסטים):
1. **PZ-13813:** כפילות של PZ-13861
2. **PZ-13770:** כפילות של PZ-13920, 13921
3. **PZ-13768:** RabbitMQ outage - לא critical
4. **PZ-13602:** RabbitMQ outage - כבר יש PZ-13602 (connection)

**פעולה:** סגור ב-Jira כ-"Duplicate" או "Won't Do"

---

### ⚠️ עדיפות נמוכה (8 טסטים):
- **PZ-13291 עד PZ-13299:** API Quality Standards

**החלטה:**
- לא critical לפונקציונליות
- בדיקות איכות ועקביות
- אפשר לדחות לגרסה עתידית

---

## 🎯 המלצה סופית

### מיידי (40 דקות):
1. ✅ הוסף 3 markers לטסטי outage קיימים
2. ✅ בנה 2 טסטים חדשים (PZ-13601, 13600)

**תוצאה:** **94.4% כיסוי** (118/125)

---

### לסגור ב-Jira (4 טסטים):
- PZ-13813: Duplicate של PZ-13861
- PZ-13770: Duplicate של PZ-13920/21
- PZ-13768: Low priority (RabbitMQ)
- PZ-13602 (outage): Duplicate

**תוצאה:** **97.5% כיסוי** (118/121)

---

### לדחות (8 טסטים):
- PZ-13291-13299: API Quality (future version)

**Status ב-Jira:** "Backlog" או "Future"

---

## ✅ מסקנה

**מה צריך:**
- ✅ 3 markers (10 דקות)
- ✅ 2 טסטים חדשים (30 דקות)

**מה לא צריך:**
- 🔴 4 כפילויות (לסגור)
- ⚠️ 8 API quality (לדחות)

**תוצאה סופית:**
כיסוי של **94.4%** עם **40 דקות עבודה** ✅

---

**כמעט מושלם!** 🎉

