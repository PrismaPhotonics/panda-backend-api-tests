# 🔧 MongoDB Indexes - Fix Guide

**תאריך:** 23 אוקטובר 2025  
**בעיה:** Indexes חסרים ב-GUID collection  
**השפעה:** 🔴 **HIGH** - Historic queries איטיים!

---

## 🎯 **הבעיה**

הטסטים מצאו שה-GUID collection (`d57c8adb-ea00-4666-83cb-0248ae9d602f`) חסר indexes קריטיים:

```
❌ start_time_1 - חסר!
❌ end_time_1 - חסר!
❌ uuid_1 - חסר!
❌ deleted_1 - חסר!
```

**תוצאה:**
- Historic queries → **COLLSCAN** (איטי מאוד!)
- Channel mapping → איטי
- Filtering deleted records → full scan

---

## ✅ **הפתרון המהיר (5 דקות)**

### **Step 1: התחבר ל-MongoDB**

```bash
mongo mongodb://prisma:prisma@10.10.100.108:27017/prisma
```

### **Step 2: בדוק את ה-GUID**

```javascript
// מצא את ה-GUID:
db.base_paths.findOne()

// תקבל:
{
  "_id": "...",
  "guid": "d57c8adb-ea00-4666-83cb-0248ae9d602f"  // ← זה ה-GUID
}
```

### **Step 3: צור את ה-Indexes**

**העתק והדבק:**

```javascript
// הגדר את ה-GUID (שנה אם צריך):
var guid = "d57c8adb-ea00-4666-83cb-0248ae9d602f";

// Index #1: start_time (קריטי לhistoric queries)
db[guid].createIndex(
  { "start_time": 1 }, 
  { 
    background: true, 
    name: "start_time_1" 
  }
);

// Index #2: end_time (קריטי לhistoric queries)
db[guid].createIndex(
  { "end_time": 1 }, 
  { 
    background: true, 
    name: "end_time_1" 
  }
);

// Index #3: uuid (קריטי, UNIQUE)
db[guid].createIndex(
  { "uuid": 1 }, 
  { 
    unique: true, 
    background: true, 
    name: "uuid_1" 
  }
);

// Index #4: deleted (optional, אבל recommended)
db[guid].createIndex(
  { "deleted": 1 }, 
  { 
    background: true, 
    name: "deleted_1" 
  }
);
```

### **Step 4: אמת שהכל בסדר**

```javascript
// בדוק indexes:
db[guid].getIndexes();

// צריך לראות 5 indexes:
// 1. _id_
// 2. start_time_1
// 3. end_time_1
// 4. uuid_1
// 5. deleted_1
```

**אם אתה רואה 5 indexes → ✅ הצלחת!**

---

## 🧪 **אימות התיקון**

### **Before (איטי):**

```javascript
// query לדוגמה:
db[guid].find({ start_time: { $gte: 1698000000 } }).explain("executionStats");

// תראה:
{
  "executionStats": {
    "stage": "COLLSCAN",              // ← רע! full collection scan
    "executionTimeMillis": 5000,      // ← איטי!
    "totalDocsExamined": 150000       // ← בודק הכל!
  }
}
```

### **After (מהיר!):**

```javascript
// אותו query:
db[guid].find({ start_time: { $gte: 1698000000 } }).explain("executionStats");

// עכשיו תראה:
{
  "executionStats": {
    "stage": "FETCH",
    "inputStage": {
      "stage": "IXSCAN",            // ← טוב! index scan
      "indexName": "start_time_1"   // ← משתמש ב-index!
    },
    "executionTimeMillis": 5,       // ← מהיר! (×1000 improvement!)
    "totalDocsExamined": 100        // ← רק מה שצריך!
  }
}
```

---

## 🚀 **הרץ טסטים מחדש**

```bash
# הרץ את הטסט:
pytest tests/data_quality/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_critical_indexes_exist -v

# צפוי לראות:
# ✅ Index on 'start_time' exists and is configured correctly
# ✅ Index on 'end_time' exists and is configured correctly
# ✅ Index on 'uuid' exists and is configured correctly
# ✅ Index on 'deleted' exists and is configured correctly
```

---

## 📋 **Script לאוטומציה**

אם אתה רוצה script שעושה את הכל אוטומטית:

```bash
#!/bin/bash
# create_mongodb_indexes.sh

MONGO_URI="mongodb://prisma:prisma@10.10.100.108:27017/prisma"

# Get GUID
GUID=$(mongo "$MONGO_URI" --quiet --eval "JSON.stringify(db.base_paths.findOne().guid)" | tr -d '"')

echo "Creating indexes on collection: $GUID"

# Create indexes
mongo "$MONGO_URI" --eval "
  var guid = '$GUID';
  
  print('Creating start_time index...');
  db[guid].createIndex({ start_time: 1 }, { background: true, name: 'start_time_1' });
  
  print('Creating end_time index...');
  db[guid].createIndex({ end_time: 1 }, { background: true, name: 'end_time_1' });
  
  print('Creating uuid index...');
  db[guid].createIndex({ uuid: 1 }, { unique: true, background: true, name: 'uuid_1' });
  
  print('Creating deleted index...');
  db[guid].createIndex({ deleted: 1 }, { background: true, name: 'deleted_1' });
  
  print('Done! Listing indexes:');
  printjson(db[guid].getIndexes());
"

echo "✅ Indexes created successfully!"
```

---

## ⚠️  **חשוב לדעת**

### **1. background: true**

הוספנו `background: true` בכל ה-indexes. זה אומר:
- ✅ המערכת ממשיכה לעבוד תוך כדי יצירת ה-index
- ⏱️ יכול לקחת יותר זמן (אבל לא חוסם!)

**אם ה-collection ריק/קטן:**
```javascript
// אפשר להוריד את background (יותר מהיר):
db[guid].createIndex({ start_time: 1 }, { name: 'start_time_1' });
```

### **2. unique: true על uuid**

ה-`uuid` index הוא `unique` - מבטיח שאין duplicates.

**אם הוספת ה-index נכשלת:**
```
Error: E11000 duplicate key error
```

→ יש recordings עם אותו uuid! **צריך לנקות קודם:**

```javascript
// מצא duplicates:
db[guid].aggregate([
  { $group: { _id: "$uuid", count: { $sum: 1 } } },
  { $match: { count: { $gt: 1 } } }
]);

// נקה duplicates (בזהירות!):
// ... (תלוי מה המדיניות)
```

### **3. אם יש הרבה data**

אם יש מיליוני documents, יצירת ה-indexes יכולה לקחת זמן:
- עם `background: true`: 5-30 דקות (תלוי בגודל)
- בלי `background`: 1-10 דקות (אבל חוסם!)

**מעקב אחרי progress:**
```javascript
// בחלון נפרד:
db.currentOp({ "command.createIndexes": { $exists: true } });
```

---

## 🎯 **סיכום**

| פעולה | זמן | קושי |
|-------|-----|------|
| צירת 4 indexes | 5-30 דק | קל |
| אימות | 1 דק | קל |
| הרצת טסטים | 2 דק | קל |
| **סה"כ** | **10-35 דק** | **קל!** |

**Impact:** 🚀 **×100-1000 improvement** בhistoric queries!

---

**נוצר:** 23 אוקטובר 2025  
**עודכן:** 23 אוקטובר 2025  
**סטטוס:** ✅ **מוכן לשימוש!**

