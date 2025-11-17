# מדריך מהיר להוספת טסטי Alerts לתיקיות Xray

**תאריך:** 2025-11-16

---

## שיטה מהירה: דרך UI

### שלב 1: פתיחת Xray Test Repository

פתח את הקישור:
```
https://prismaphotonics.atlassian.net/projects/PZ?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.xpandit.plugins.xray__testing-board#!page=test-repository&selectedFolder=68d91b9f681e183ea2e83e16
```

### שלב 2: הוספת טסטים לכל תיקייה

לכל קטגוריה, בצע:

1. **פתח את התיקייה** (או צור אותה אם לא קיימת)
2. **השתמש ב-JQL Query** כדי למצוא את הטסטים
3. **בחר את כל הטסטים** מהרשימה
4. **גרור ושחרר** אותם לתיקייה

---

## Positive Tests (5 טסטים)

**JQL:**
```jql
project = PZ AND key IN (PZ-14933, PZ-14934, PZ-14935, PZ-14936, PZ-14937)
```

**טסטים:**
- PZ-14933, PZ-14934, PZ-14935, PZ-14936, PZ-14937

---

## Negative Tests (7 טסטים)

**JQL:**
```jql
project = PZ AND key IN (PZ-14938, PZ-14939, PZ-14940, PZ-14941, PZ-14942, PZ-14943, PZ-14944)
```

**טסטים:**
- PZ-14938, PZ-14939, PZ-14940, PZ-14941, PZ-14942, PZ-14943, PZ-14944

---

## Edge Cases (8 טסטים)

**JQL:**
```jql
project = PZ AND key IN (PZ-14945, PZ-14946, PZ-14947, PZ-14948, PZ-14949, PZ-14950, PZ-14951, PZ-14952)
```

**טסטים:**
- PZ-14945, PZ-14946, PZ-14947, PZ-14948, PZ-14949, PZ-14950, PZ-14951, PZ-14952

---

## Load Tests (5 טסטים)

**JQL:**
```jql
project = PZ AND key IN (PZ-14953, PZ-14954, PZ-14955, PZ-14956, PZ-14957)
```

**טסטים:**
- PZ-14953, PZ-14954, PZ-14955, PZ-14956, PZ-14957

---

## Performance Tests (6 טסטים)

**JQL:**
```jql
project = PZ AND key IN (PZ-14958, PZ-14959, PZ-14960, PZ-14961, PZ-14962, PZ-14963)
```

**טסטים:**
- PZ-14958, PZ-14959, PZ-14960, PZ-14961, PZ-14962, PZ-14963

---

## Investigation (1 טסט)

**JQL:**
```jql
project = PZ AND key = PZ-14964
```

**טסטים:**
- PZ-14964

---

## סיכום

**סה"כ:** 32 טסטים

**זמן משוער:** 5-10 דקות

**שיטה:** גרור ושחרר דרך UI

