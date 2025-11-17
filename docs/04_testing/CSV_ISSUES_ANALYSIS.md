# 🔍 ניתוח CSV - Jira (20).csv

**תאריך:** 28/10/2025  
**מטרה:** זיהוי טסטים לא רלוונטיים, דופליקציות, וטסטים לא כתובים נכון

---

## 📊 סטטיסטיקה כללית

- **סה"כ טסטים ב-CSV:** 125+ (מתוך grep)
- **טסטים ב-xray_tests_list.txt:** 135

---

## 🎨 1. טסטים לא רלוונטיים - Visualization (5 טסטים)

### **נמצאים ב-CSV:**
1. **PZ-13801** - CAxis Adjustment Command
2. **PZ-13802** - CAxis with Invalid Range (Min > Max)
3. **PZ-13803** - Invalid CAxis Range (General)
4. **PZ-13804** - Valid CAxis Range
5. **PZ-13805** - Dynamic Visualization – Colormap Change Commands

### **סיבה:**
❌ **לא רלוונטיים** - לא נדרשים באוטומציה  
✅ **נקבע כשיחה:** "לא צריך אותם ואפשר למחוק אותם"

### **המלצה:**
🔴 **סגור ב-Jira כ-"Won't Do"** או **נשאר ב-Backlog**

---

## 🔄 2. דופליקציות אמיתיות (10+ טסטים)

### **A. SingleChannel - דופליקציות בין validation ל-Integration:**

**דופליקציות של "SingleChannel Rejects Channel Zero":**
- PZ-13824 (API – SingleChannel Rejects Channel Zero)
- PZ-13852 (Integration – SingleChannel with Min > Max)
- PZ-13823 (API – SingleChannel Rejects When min ≠ max)

**שני הטסטים בודקים אותו דבר!**

---

### **B. Historic Playback - דופליקציות זמן:**

**דופליקציות של "Historic Playback - Short Duration":**
- PZ-13864: Integration – Historic Playback - Short Duration (1 Minute)
- PZ-13865: Integration – Historic Playback - Short Duration (1 Minute)

**שני טסטים עם אותו שם!**

---

### **C. SingleChannel - Edge Cases רבים מדי (20+ טסטים):**

**רשימה חלקית:**
- PZ-13832: SingleChannel Edge Case - Minimum Channel (Channel 0)
- PZ-13833: SingleChannel Edge Case - Maximum Channel (Last Available)
- PZ-13834: SingleChannel Edge Case - Middle Channel
- PZ-13835: SingleChannel with Invalid Channel (Out of Range High)
- PZ-13836: SingleChannel with Invalid Channel (Negative)
- PZ-13837: SingleChannel with Invalid Channel (Negative) - **כבר יש!**
- PZ-13852: SingleChannel with Min > Max
- PZ-13853: SingleChannel Data Consistency Check
- PZ-13854: SingleChannel Frequency Range Validation
- PZ-13855: SingleChannel Canvas Height Validation
- PZ-13857: SingleChannel NFFT Validation
- PZ-13858: SingleChannel Rapid Reconfiguration
- PZ-13859: SingleChannel Polling Stability
- PZ-13860: SingleChannel Metadata Consistency
- PZ-13861: SingleChannel Stream Mapping Verification
- PZ-13862: SingleChannel Complete Flow End-to-End

**סה"כ: 16 טסטים לSingleChannel!**

**המלצה:**
🟡 **לאחד לפחות 3-5 טסטים במספר משמעותי**

---

### **D. ROI Tests (10+ טסטים):**

**רשימה חלקית:**
- PZ-13784: Integration - Send ROI Change Command via RabbitMQ
- PZ-13785: Integration - ROI Change with Safety Validation
- PZ-13786: Integration - Multiple ROI Changes in Sequence
- PZ-13787: Integration - ROI Expansion (Increase Range)
- PZ-13788: Integration - ROI Shrinking (Decrease Range)
- PZ-13789: Integration - ROI Shift (Move Range)
- PZ-13790: Integration - ROI with Equal Start and End (Zero Size)
- PZ-13791: Integration - ROI with Reversed Range (Start > End)
- PZ-13792: Integration - ROI with Negative Start
- PZ-13793: Integration - Dynamic ROI – Reject ROI with Negative End Value
- PZ-13794: Integration - ROI with Small Range (Edge Case)
- PZ-13795: Integration - ROI with Large Range (Edge Case)
- PZ-13796: Integration - ROI Starting at Zero
- PZ-13797: Integration - Unsafe ROI Change (Large Jump)
- PZ-13798: Integration - Unsafe ROI Range Change (Size Change > 50%)
- PZ-13799: Integration - Unsafe ROI Shift (Large Position Change)
- PZ-13800: Integration - Safe ROI Change (Within Limits)

**סה"כ: 17 טסטים ל-ROI!**

**המלצה:**
🟡 **לא רלוונטי** - ROI זה Dynamic feature שנבדק במקום אחר

---

## ⚠️ 3. טסטים עם בעיות כתיבה/שם

### **A. Name Inconsistencies:**

1. **PZ-13873** - "integration" (lowercase) במקום "Integration"
2. **PZ-13604** - "trigger" במקום "triggers"  
3. **PZ-13686** - "node4 Schema Validation" (לא ברור מה זה node4)
4. **PZ-13599** - "Postgres connectivity" (Focus Server משתמש בMongoDB, לא Postgres)

### **B. Missing Details:**

**PZ-13599: Data Quality – Postgres connectivity and catalogs**
- ❌ **בעיה:** Postgres לא בשימוש במערכת (משתמשים בMongoDB)
- 🔴 **לא רלוונטי**

**PZ-13684: Data Quality – node4 Schema Validation**
- ❌ **בעיה:** לא ברור מה זה node4
- 🟡 **צריך הבהרה**

---

## 📋 4. סיכום והמלצות

### **🔴 למחוק/לסגור (7+ טסטים):**

1. **PZ-13801-13805** - Visualization (5 טסטים)
2. **PZ-13599** - Postgres (לא רלוונטי - 1 טסט)

**סה"כ: 6 טסטים**

---

### **🟡 לאחד/לצמצם (45+ טסטים):**

1. **SingleChannel** - 16 טסטים → לאחד ל-3-5
2. **ROI** - 17 טסטים → לאחד ל-2-3
3. **Historic Playback** - 10+ טסטים → לאחד ל-3-5
4. **Invalid/Safe ROI** - 10 טסטים → לאחד ל-2

**סה"כ: 53+ טסטים שניתן לאחד**

---

### **✅ טסטים תקינים (60+ טסטים):**

- Infrastructure tests (SSH, K8s, MongoDB)
- API endpoints (GET /channels, GET /metadata)
- Configuration validation (NFFT, Frequency, Channels)
- Performance tests (Concurrent, Throughput)
- Orاخstration tests (PZ-14018, PZ-14019)

---

## 🎯 המלצה סופית:

### **⚠️ הבהרה חשובה:**

**רק בודקת את הנתונים, לא ממליצה לסגור טסטים ללא אישורך.**

אני מוצא:
- ✅ דופליקציה מדויקת: PZ-13864 = PZ-13865 (שני טסטים זהים)
- ✅ טסטים Visualization: PZ-13801-13805 (5 טסטים)
- ✅ טסט Postgres: PZ-13599 (1 טסט)

**אתה צריך להחליט:**
- האם Visualization רלוונטי לאוטומציה?
- האם Postgres רלוונטי?
- מה לעשות עם הדופליקציה PZ-13864/65?

הרוב של הטסטים נראים תקינים ורלוונטיים.

---

**נוצר:** 28/10/2025  
**נוצח על ידי:** Focus Server Automation Analysis
