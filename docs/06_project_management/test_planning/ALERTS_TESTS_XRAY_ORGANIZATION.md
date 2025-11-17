# ארגון טסטי Alerts לתיקיות Xray

**תאריך:** 2025-11-16  
**תיקיית בסיס:** `68d91b9f681e183ea2e83e16`

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

## Positive Tests (5 טסטים)

**תיקייה:** `Positive Tests`

| Key | Summary | Category |
|-----|---------|----------|
| PZ-14933 | Alert Generation - Successful SD Alert | Positive |
| PZ-14934 | Alert Generation - Successful SC Alert | Positive |
| PZ-14935 | Alert Generation - Multiple Alerts | Positive |
| PZ-14936 | Alert Generation - Different Severity Levels | Positive |
| PZ-14937 | Alert Generation - Alert Processing via RabbitMQ | Positive |

**JQL Query:**
```jql
project = PZ AND key IN (PZ-14933, PZ-14934, PZ-14935, PZ-14936, PZ-14937)
```

---

## Negative Tests (7 טסטים)

**תיקייה:** `Negative Tests`

| Key | Summary | Category |
|-----|---------|----------|
| PZ-14938 | Alert Generation - Invalid Class ID | Negative |
| PZ-14939 | Alert Generation - Invalid Severity | Negative |
| PZ-14940 | Alert Generation - Invalid DOF Range | Negative |
| PZ-14941 | Alert Generation - Missing Required Fields | Negative |
| PZ-14942 | Alert Generation - RabbitMQ Connection Failure | Negative |
| PZ-14943 | Alert Generation - Invalid Alert ID Format | Negative |
| PZ-14944 | Alert Generation - Duplicate Alert IDs | Negative |

**JQL Query:**
```jql
project = PZ AND key IN (PZ-14938, PZ-14939, PZ-14940, PZ-14941, PZ-14942, PZ-14943, PZ-14944)
```

---

## Edge Cases (8 טסטים)

**תיקייה:** `Edge Cases`

| Key | Summary | Category |
|-----|---------|----------|
| PZ-14945 | Alert Generation - Boundary DOF Values | Edge Case |
| PZ-14946 | Alert Generation - Minimum/Maximum Severity | Edge Case |
| PZ-14947 | Alert Generation - Zero Alerts Amount | Edge Case |
| PZ-14948 | Alert Generation - Very Large Alert ID | Edge Case |
| PZ-14949 | Alert Generation - Concurrent Alerts with Same DOF | Edge Case |
| PZ-14950 | Alert Generation - Rapid Sequential Alerts | Edge Case |
| PZ-14951 | Alert Generation - Alert with Maximum Fields | Edge Case |
| PZ-14952 | Alert Generation - Alert with Minimum Fields | Edge Case |

**JQL Query:**
```jql
project = PZ AND key IN (PZ-14945, PZ-14946, PZ-14947, PZ-14948, PZ-14949, PZ-14950, PZ-14951, PZ-14952)
```

---

## Load Tests (5 טסטים)

**תיקייה:** `Load Tests`

| Key | Summary | Category |
|-----|---------|----------|
| PZ-14953 | Alert Generation - High Volume Load | Load |
| PZ-14954 | Alert Generation - Sustained Load | Load |
| PZ-14955 | Alert Generation - Burst Load | Load |
| PZ-14956 | Alert Generation - Mixed Alert Types Load | Load |
| PZ-14957 | Alert Generation - RabbitMQ Queue Capacity | Load |

**JQL Query:**
```jql
project = PZ AND key IN (PZ-14953, PZ-14954, PZ-14955, PZ-14956, PZ-14957)
```

---

## Performance Tests (6 טסטים)

**תיקייה:** `Performance Tests`

| Key | Summary | Category |
|-----|---------|----------|
| PZ-14958 | Alert Generation - Response Time | Performance |
| PZ-14959 | Alert Generation - Throughput | Performance |
| PZ-14960 | Alert Generation - Latency | Performance |
| PZ-14961 | Alert Generation - Resource Usage | Performance |
| PZ-14962 | Alert Generation - End-to-End Performance | Performance |
| PZ-14963 | Alert Generation - RabbitMQ Performance | Performance |

**JQL Query:**
```jql
project = PZ AND key IN (PZ-14958, PZ-14959, PZ-14960, PZ-14961, PZ-14962, PZ-14963)
```

---

## Investigation (1 טסט)

**תיקייה:** `Investigation`

| Key | Summary | Category |
|-----|---------|----------|
| PZ-14964 | Deep Alert Logs Investigation | Investigation |

**JQL Query:**
```jql
project = PZ AND key = PZ-14964
```

---

## הוראות להוספה לתיקיות

1. פתח את הקישור הבא:
   ```
   https://prismaphotonics.atlassian.net/projects/PZ?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.xpandit.plugins.xray__testing-board#!page=test-repository&selectedFolder=68d91b9f681e183ea2e83e16
   ```

2. לכל קטגוריה:
   - פתח את התיקייה המתאימה (או צור אותה אם לא קיימת)
   - השתמש ב-JQL Query כדי למצוא את הטסטים
   - בחר את כל הטסטים מהרשימה
   - גרור ושחרר אותם לתיקייה המתאימה
   - או השתמש ב-'Move to Folder' מהתפריט

---

## הערות

- כל הטסטים כבר קיימים ב-Jira
- הטסטים מסודרים לפי קטגוריות
- ניתן להשתמש ב-JQL Queries כדי למצוא את הטסטים במהירות
- אם תיקייה לא קיימת, צור אותה ידנית בתיקיית הבסיס

