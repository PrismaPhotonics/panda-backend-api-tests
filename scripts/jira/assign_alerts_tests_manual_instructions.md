# הוראות ידניות להוספת טסטי Alerts לתיקיות Xray

**תאריך:** 2025-11-16

---

## שלב 1: פתיחת Xray Test Repository

פתח את הקישור הבא:
```
https://prismaphotonics.atlassian.net/projects/PZ?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.xpandit.plugins.xray__testing-board#!page=test-repository&selectedFolder=68d91b9f681e183ea2e83e16
```

---

## שלב 2: יצירת תיקיות (אם לא קיימות)

אם התיקיות לא קיימות, צור אותן בתיקיית הבסיס:

- **Positive Tests**
- **Negative Tests**
- **Edge Cases**
- **Load Tests**
- **Performance Tests**
- **Investigation**

---

## שלב 3: הוספת טסטים לתיקיות

### Positive Tests (5 טסטים)

**JQL Query:**
```jql
project = PZ AND key IN (PZ-14933, PZ-14934, PZ-14935, PZ-14936, PZ-14937)
```

**טסטים:**
- PZ-14933: Alert Generation - Successful SD Alert
- PZ-14934: Alert Generation - Successful SC Alert
- PZ-14935: Alert Generation - Multiple Alerts
- PZ-14936: Alert Generation - Different Severity Levels
- PZ-14937: Alert Generation - Alert Processing via RabbitMQ

**הוראות:**
1. פתח את התיקייה 'Positive Tests'
2. השתמש ב-JQL Query למעלה כדי למצוא את הטסטים
3. בחר את כל הטסטים מהרשימה
4. גרור ושחרר אותם לתיקייה 'Positive Tests'

---

### Negative Tests (7 טסטים)

**JQL Query:**
```jql
project = PZ AND key IN (PZ-14938, PZ-14939, PZ-14940, PZ-14941, PZ-14942, PZ-14943, PZ-14944)
```

**טסטים:**
- PZ-14938: Alert Generation - Invalid Class ID
- PZ-14939: Alert Generation - Invalid Severity
- PZ-14940: Alert Generation - Invalid DOF Range
- PZ-14941: Alert Generation - Missing Required Fields
- PZ-14942: Alert Generation - RabbitMQ Connection Failure
- PZ-14943: Alert Generation - Invalid Alert ID Format
- PZ-14944: Alert Generation - Duplicate Alert IDs

**הוראות:**
1. פתח את התיקייה 'Negative Tests'
2. השתמש ב-JQL Query למעלה כדי למצוא את הטסטים
3. בחר את כל הטסטים מהרשימה
4. גרור ושחרר אותם לתיקייה 'Negative Tests'

---

### Edge Cases (8 טסטים)

**JQL Query:**
```jql
project = PZ AND key IN (PZ-14945, PZ-14946, PZ-14947, PZ-14948, PZ-14949, PZ-14950, PZ-14951, PZ-14952)
```

**טסטים:**
- PZ-14945: Alert Generation - Boundary DOF Values
- PZ-14946: Alert Generation - Minimum/Maximum Severity
- PZ-14947: Alert Generation - Zero Alerts Amount
- PZ-14948: Alert Generation - Very Large Alert ID
- PZ-14949: Alert Generation - Concurrent Alerts with Same DOF
- PZ-14950: Alert Generation - Rapid Sequential Alerts
- PZ-14951: Alert Generation - Alert with Maximum Fields
- PZ-14952: Alert Generation - Alert with Minimum Fields

**הוראות:**
1. פתח את התיקייה 'Edge Cases'
2. השתמש ב-JQL Query למעלה כדי למצוא את הטסטים
3. בחר את כל הטסטים מהרשימה
4. גרור ושחרר אותם לתיקייה 'Edge Cases'

---

### Load Tests (5 טסטים)

**JQL Query:**
```jql
project = PZ AND key IN (PZ-14953, PZ-14954, PZ-14955, PZ-14956, PZ-14957)
```

**טסטים:**
- PZ-14953: Alert Generation - High Volume Load
- PZ-14954: Alert Generation - Sustained Load
- PZ-14955: Alert Generation - Burst Load
- PZ-14956: Alert Generation - Mixed Alert Types Load
- PZ-14957: Alert Generation - RabbitMQ Queue Capacity

**הוראות:**
1. פתח את התיקייה 'Load Tests'
2. השתמש ב-JQL Query למעלה כדי למצוא את הטסטים
3. בחר את כל הטסטים מהרשימה
4. גרור ושחרר אותם לתיקייה 'Load Tests'

---

### Performance Tests (6 טסטים)

**JQL Query:**
```jql
project = PZ AND key IN (PZ-14958, PZ-14959, PZ-14960, PZ-14961, PZ-14962, PZ-14963)
```

**טסטים:**
- PZ-14958: Alert Generation - Response Time
- PZ-14959: Alert Generation - Throughput
- PZ-14960: Alert Generation - Latency
- PZ-14961: Alert Generation - Resource Usage
- PZ-14962: Alert Generation - End-to-End Performance
- PZ-14963: Alert Generation - RabbitMQ Performance

**הוראות:**
1. פתח את התיקייה 'Performance Tests'
2. השתמש ב-JQL Query למעלה כדי למצוא את הטסטים
3. בחר את כל הטסטים מהרשימה
4. גרור ושחרר אותם לתיקייה 'Performance Tests'

---

### Investigation (1 טסט)

**JQL Query:**
```jql
project = PZ AND key = PZ-14964
```

**טסטים:**
- PZ-14964: Deep Alert Logs Investigation

**הוראות:**
1. פתח את התיקייה 'Investigation'
2. השתמש ב-JQL Query למעלה כדי למצוא את הטסט
3. גרור ושחרר אותו לתיקייה 'Investigation'

---

## סיכום

**סה"כ טסטים:** 32 טסטים
- **Positive Tests:** 5 טסטים
- **Negative Tests:** 7 טסטים
- **Edge Cases:** 8 טסטים
- **Load Tests:** 5 טסטים
- **Performance Tests:** 6 טסטים
- **Investigation:** 1 טסט

---

## הערות

- אם טסט לא נמצא, ודא שהוא נוצר ב-Jira
- אם תיקייה לא קיימת, צור אותה ידנית
- ניתן להשתמש ב-JQL Query כדי למצוא טסטים ספציפיים
- לאחר הוספה, ודא שכל הטסטים נמצאים בתיקיות הנכונות

