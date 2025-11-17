# Jira Test Quality Update Guide
**Date:** 2025-11-09  
**Purpose:** Explain what "Update Jira Test Quality" means

---

## 📋 מה זה "עדכון איכות טסטים ב-Jira"?

זה אומר לשפר את **המידע והתיאורים** של הטסטים ב-Jira כדי שיהיו יותר ברורים, מפורטים ומועילים.

---

## 🎯 למה זה חשוב?

### בעיות נפוצות ב-Jira:
1. **תיאורים קצרים מדי** - לא ברור מה הטסט בודק
2. **חסרים פרטים טכניים** - לא ברור איך להריץ את הטסט
3. **חסרים סוגי טסטים** - לא ברור אם זה Unit/Integration/E2E
4. **חסרים קישורים** - לא ברור איפה הטסט בקוד
5. **חסרים דוגמאות** - לא ברור מה הקלט/פלט הצפוי

---

## 📝 מה צריך לעדכן?

### 1. תיאורים (Descriptions)
**לפני:**
```
Test API endpoint
```

**אחרי:**
```
Test GET /channels endpoint returns system channel bounds.

Steps:
1. Send GET request to /channels
2. Verify response contains min/max channel values
3. Verify response status is 200

Expected:
- Response contains channels.min and channels.max
- Status code is 200
- Response time < 100ms
```

### 2. סוגי טסטים (Test Types)
**לפני:**
- חסר סוג טסט

**אחרי:**
- **Test Type:** Integration
- **Test Level:** API
- **Priority:** High

### 3. קישורים לקוד (Links)
**לפני:**
- חסר קישור

**אחרי:**
- **Automation:** `tests/integration/api/test_api_endpoints_high_priority.py::test_get_channels_endpoint_success`
- **GitHub:** Link to test file

### 4. דוגמאות (Examples)
**לפני:**
- חסר דוגמה

**אחרי:**
```json
Request:
GET /channels

Response:
{
  "channels": {
    "min": 1,
    "max": 100
  }
}
```

### 5. תנאים מקדימים (Prerequisites)
**לפני:**
- חסר תנאים

**אחרי:**
- **Environment:** Staging/Production
- **Prerequisites:** Focus Server running, MongoDB connected
- **Data:** No special data required

---

## 🔧 איך לעדכן?

### שלב 1: זהה טסטים שצריכים שיפור
1. פתח Jira
2. חפש טסטים עם:
   - תיאורים קצרים
   - חסרים פרטים טכניים
   - חסרים סוגי טסטים
   - חסרים קישורים

### שלב 2: עדכן כל טסט
1. פתח את הטסט ב-Jira
2. לחץ על "Edit"
3. עדכן:
   - **Summary** - כותרת ברורה
   - **Description** - תיאור מפורט עם Steps/Expected
   - **Test Type** - Unit/Integration/E2E
   - **Priority** - High/Medium/Low
   - **Labels** - API, Infrastructure, etc.
   - **Links** - קישור לקוד האוטומציה

### שלב 3: הוסף מידע טכני
1. **Steps** - שלבים מפורטים
2. **Expected** - תוצאות צפויות
3. **Prerequisites** - תנאים מקדימים
4. **Examples** - דוגמאות קלט/פלט

---

## 📊 דוגמאות לעדכון

### דוגמה 1: API Test
**לפני:**
```
Test GET /channels
```

**אחרי:**
```
Test: GET /channels - Returns System Channel Bounds

Type: Integration Test
Level: API
Priority: High

Description:
Tests that GET /channels endpoint returns the system channel bounds (min/max).

Steps:
1. Send GET request to /channels endpoint
2. Verify response status is 200
3. Verify response contains channels.min and channels.max
4. Verify min < max
5. Verify response time < 100ms

Expected:
- Status code: 200
- Response contains: {"channels": {"min": 1, "max": 100}}
- Response time < 100ms

Automation:
- File: tests/integration/api/test_api_endpoints_high_priority.py
- Function: test_get_channels_endpoint_success
- Marker: @pytest.mark.xray("PZ-13762")
```

### דוגמה 2: Infrastructure Test
**לפני:**
```
Test MongoDB connection
```

**אחרי:**
```
Test: MongoDB Connection - Basic Connectivity

Type: Infrastructure Test
Level: Connectivity
Priority: Medium

Description:
Tests that MongoDB connection can be established and basic operations work.

Steps:
1. Connect to MongoDB using connection string
2. Verify connection is successful
3. List databases
4. Verify default database exists
5. Close connection

Expected:
- Connection established successfully
- Can list databases
- Default database (prisma) exists
- Connection closes gracefully

Prerequisites:
- MongoDB running on 10.10.100.108:27017
- Credentials: prisma/prisma
- Network access to MongoDB

Automation:
- File: tests/infrastructure/test_external_connectivity.py
- Function: test_mongodb_connection
- Marker: @pytest.mark.xray("PZ-13807")
```

---

## ⏱️ זמן משוער

### לכל טסט:
- **תיאור קצר → מפורט:** 5-10 דקות
- **הוספת סוג טסט:** 1 דקה
- **הוספת קישורים:** 2 דקות
- **הוספת דוגמאות:** 5 דקות

**סה"כ לכל טסט:** ~15 דקות

### לפרויקט כולו:
- **טסטים שצריכים שיפור:** ~50-100 טסטים
- **זמן משוער:** 1.5-2.5 שעות

---

## ✅ Checklist לעדכון

לכל טסט, ודא שיש:
- [ ] **Summary** - כותרת ברורה ומפורטת
- [ ] **Description** - תיאור מפורט עם Steps/Expected
- [ ] **Test Type** - Unit/Integration/E2E
- [ ] **Priority** - High/Medium/Low
- [ ] **Labels** - קטגוריות (API, Infrastructure, etc.)
- [ ] **Links** - קישור לקוד האוטומציה
- [ ] **Prerequisites** - תנאים מקדימים
- [ ] **Examples** - דוגמאות קלט/פלט (אם רלוונטי)

---

## 🎯 סיכום

**"עדכון איכות טסטים ב-Jira"** = לשפר את המידע והתיאורים של הטסטים ב-Jira כדי שיהיו יותר ברורים, מפורטים ומועילים.

**זה לא חובה קריטית** - הטסטים עובדים גם בלי זה, אבל זה עוזר מאוד להבנה ותחזוקה.

**זמן משוער:** 1.5-2 שעות עבודה ידנית ב-Jira UI

---

**Last Updated:** 2025-11-09

