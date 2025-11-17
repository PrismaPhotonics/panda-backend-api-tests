# חלוקת טסטי Alerts לתיקיות Xray

**תאריך:** 2025-11-16  
**סה"כ טסטים:** 32 טסטים

---

## Positive Tests (5 טסטים)

**תיקייה:** `Positive Tests`

| Key | Summary |
|-----|---------|
| PZ-14933 | Alert Generation - Successful SD Alert |
| PZ-14934 | Alert Generation - Successful SC Alert |
| PZ-14935 | Alert Generation - Multiple Alerts |
| PZ-14936 | Alert Generation - Different Severity Levels |
| PZ-14937 | Alert Generation - Alert Processing via RabbitMQ |

**JQL Query:**
```jql
project = PZ AND key IN (PZ-14933, PZ-14934, PZ-14935, PZ-14936, PZ-14937)
```

---

## Negative Tests (7 טסטים)

**תיקייה:** `Negative Tests`

| Key | Summary |
|-----|---------|
| PZ-14938 | Alert Generation - Invalid Class ID |
| PZ-14939 | Alert Generation - Invalid Severity |
| PZ-14940 | Alert Generation - Invalid DOF Range |
| PZ-14941 | Alert Generation - Missing Required Fields |
| PZ-14942 | Alert Generation - RabbitMQ Connection Failure |
| PZ-14943 | Alert Generation - Invalid Alert ID Format |
| PZ-14944 | Alert Generation - Duplicate Alert IDs |

**JQL Query:**
```jql
project = PZ AND key IN (PZ-14938, PZ-14939, PZ-14940, PZ-14941, PZ-14942, PZ-14943, PZ-14944)
```

---

## Edge Cases (8 טסטים)

**תיקייה:** `Edge Cases`

| Key | Summary |
|-----|---------|
| PZ-14945 | Alert Generation - Boundary DOF Values |
| PZ-14946 | Alert Generation - Minimum/Maximum Severity |
| PZ-14947 | Alert Generation - Zero Alerts Amount |
| PZ-14948 | Alert Generation - Very Large Alert ID |
| PZ-14949 | Alert Generation - Concurrent Alerts with Same DOF |
| PZ-14950 | Alert Generation - Rapid Sequential Alerts |
| PZ-14951 | Alert Generation - Alert with Maximum Fields |
| PZ-14952 | Alert Generation - Alert with Minimum Fields |

**JQL Query:**
```jql
project = PZ AND key IN (PZ-14945, PZ-14946, PZ-14947, PZ-14948, PZ-14949, PZ-14950, PZ-14951, PZ-14952)
```

---

## Load Tests (5 טסטים)

**תיקייה:** `Load Tests`

| Key | Summary |
|-----|---------|
| PZ-14953 | Alert Generation - High Volume Load |
| PZ-14954 | Alert Generation - Sustained Load |
| PZ-14955 | Alert Generation - Burst Load |
| PZ-14956 | Alert Generation - Mixed Alert Types Load |
| PZ-14957 | Alert Generation - RabbitMQ Queue Capacity |

**JQL Query:**
```jql
project = PZ AND key IN (PZ-14953, PZ-14954, PZ-14955, PZ-14956, PZ-14957)
```

---

## Performance Tests (6 טסטים)

**תיקייה:** `Performance Tests`

| Key | Summary |
|-----|---------|
| PZ-14958 | Alert Generation - Response Time |
| PZ-14959 | Alert Generation - Throughput |
| PZ-14960 | Alert Generation - Latency |
| PZ-14961 | Alert Generation - Resource Usage |
| PZ-14962 | Alert Generation - End-to-End Performance |
| PZ-14963 | Alert Generation - RabbitMQ Performance |

**JQL Query:**
```jql
project = PZ AND key IN (PZ-14958, PZ-14959, PZ-14960, PZ-14961, PZ-14962, PZ-14963)
```

---

## Investigation (1 טסט)

**תיקייה:** `Investigation`

| Key | Summary |
|-----|---------|
| PZ-14964 | Deep Alert Logs Investigation |

**JQL Query:**
```jql
project = PZ AND key = PZ-14964
```

---

## סיכום לפי תיקיות

| תיקייה | מספר טסטים | Range |
|--------|------------|-------|
| Positive Tests | 5 | PZ-14933 עד PZ-14937 |
| Negative Tests | 7 | PZ-14938 עד PZ-14944 |
| Edge Cases | 8 | PZ-14945 עד PZ-14952 |
| Load Tests | 5 | PZ-14953 עד PZ-14957 |
| Performance Tests | 6 | PZ-14958 עד PZ-14963 |
| Investigation | 1 | PZ-14964 |
| **סה"כ** | **32** | **PZ-14933 עד PZ-14964** |

---

## JQL Query לכל הטסטים

```jql
project = PZ AND key >= PZ-14933 AND key <= PZ-14964 AND type = Test ORDER BY key ASC
```

---

## הוראות להוספה

1. פתח את Xray Test Repository:
   ```
   https://prismaphotonics.atlassian.net/projects/PZ?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.xpandit.plugins.xray__testing-board#!page=test-repository&selectedFolder=68d91b9f681e183ea2e83e16
   ```

2. לכל תיקייה:
   - פתח את התיקייה (או צור אותה אם לא קיימת)
   - השתמש ב-JQL Query הרלוונטי כדי למצוא את הטסטים
   - בחר את כל הטסטים מהרשימה
   - גרור ושחרר אותם לתיקייה

---

## קישורים ישירים לטסטים

### Positive Tests
- [PZ-14933](https://prismaphotonics.atlassian.net/browse/PZ-14933)
- [PZ-14934](https://prismaphotonics.atlassian.net/browse/PZ-14934)
- [PZ-14935](https://prismaphotonics.atlassian.net/browse/PZ-14935)
- [PZ-14936](https://prismaphotonics.atlassian.net/browse/PZ-14936)
- [PZ-14937](https://prismaphotonics.atlassian.net/browse/PZ-14937)

### Negative Tests
- [PZ-14938](https://prismaphotonics.atlassian.net/browse/PZ-14938)
- [PZ-14939](https://prismaphotonics.atlassian.net/browse/PZ-14939)
- [PZ-14940](https://prismaphotonics.atlassian.net/browse/PZ-14940)
- [PZ-14941](https://prismaphotonics.atlassian.net/browse/PZ-14941)
- [PZ-14942](https://prismaphotonics.atlassian.net/browse/PZ-14942)
- [PZ-14943](https://prismaphotonics.atlassian.net/browse/PZ-14943)
- [PZ-14944](https://prismaphotonics.atlassian.net/browse/PZ-14944)

### Edge Cases
- [PZ-14945](https://prismaphotonics.atlassian.net/browse/PZ-14945)
- [PZ-14946](https://prismaphotonics.atlassian.net/browse/PZ-14946)
- [PZ-14947](https://prismaphotonics.atlassian.net/browse/PZ-14947)
- [PZ-14948](https://prismaphotonics.atlassian.net/browse/PZ-14948)
- [PZ-14949](https://prismaphotonics.atlassian.net/browse/PZ-14949)
- [PZ-14950](https://prismaphotonics.atlassian.net/browse/PZ-14950)
- [PZ-14951](https://prismaphotonics.atlassian.net/browse/PZ-14951)
- [PZ-14952](https://prismaphotonics.atlassian.net/browse/PZ-14952)

### Load Tests
- [PZ-14953](https://prismaphotonics.atlassian.net/browse/PZ-14953)
- [PZ-14954](https://prismaphotonics.atlassian.net/browse/PZ-14954)
- [PZ-14955](https://prismaphotonics.atlassian.net/browse/PZ-14955)
- [PZ-14956](https://prismaphotonics.atlassian.net/browse/PZ-14956)
- [PZ-14957](https://prismaphotonics.atlassian.net/browse/PZ-14957)

### Performance Tests
- [PZ-14958](https://prismaphotonics.atlassian.net/browse/PZ-14958)
- [PZ-14959](https://prismaphotonics.atlassian.net/browse/PZ-14959)
- [PZ-14960](https://prismaphotonics.atlassian.net/browse/PZ-14960)
- [PZ-14961](https://prismaphotonics.atlassian.net/browse/PZ-14961)
- [PZ-14962](https://prismaphotonics.atlassian.net/browse/PZ-14962)
- [PZ-14963](https://prismaphotonics.atlassian.net/browse/PZ-14963)

### Investigation
- [PZ-14964](https://prismaphotonics.atlassian.net/browse/PZ-14964)

---

**נוצר:** 2025-11-16

