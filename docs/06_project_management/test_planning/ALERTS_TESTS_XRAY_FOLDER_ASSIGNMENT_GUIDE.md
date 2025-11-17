
# מדריך ידני להוספת טסטי Alerts לתיקיות ב-Xray Test Repository

**תאריך:** 1763285072.6922507
**תיקיית בסיס:** `68d91b9f681e183ea2e83e16`

---

## שלב 1: כניסה ל-Xray Test Repository

1. פתח את הקישור הבא:
   ```
   https://prismaphotonics.atlassian.net/projects/PZ?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.xpandit.plugins.xray__testing-board#!page=test-repository&selectedFolder=68d91b9f681e183ea2e83e16
   ```

2. ודא שאתה בתיקייה הנכונה (ID: `68d91b9f681e183ea2e83e16`)

---

## שלב 2: יצירת תיקיות לפי קטגוריות

אם התיקיות לא קיימות, צור אותן בתיקיית הבסיס:

### תיקיות ליצירה:

- **Positive Tests**

- **Negative Tests**

- **Edge Cases**

- **Load Tests**

- **Performance Tests**

- **Investigation**

---

## שלב 3: הוספת טסטים לתיקיות


### Positive Tests

**JQL Query למציאת הטסטים:**
```jql
project = PZ AND key IN (PZ-15000, PZ-15001, PZ-15002, PZ-15003, PZ-15004)
```

**טסטים להוספה (5):**
- PZ-15000
- PZ-15001
- PZ-15002
- PZ-15003
- PZ-15004

**הוראות:**
1. פתח את התיקייה 'Positive Tests'
2. השתמש ב-JQL Query למעלה כדי למצוא את הטסטים
3. בחר את כל הטסטים מהרשימה
4. גרור ושחרר אותם לתיקייה 'Positive Tests'
5. או השתמש ב-'Move to Folder' מהתפריט

---


### Negative Tests

**JQL Query למציאת הטסטים:**
```jql
project = PZ AND key IN (PZ-15010, PZ-15011, PZ-15012, PZ-15013, PZ-15014, PZ-15016, PZ-15017)
```

**טסטים להוספה (7):**
- PZ-15010
- PZ-15011
- PZ-15012
- PZ-15013
- PZ-15014
- PZ-15016
- PZ-15017

**הוראות:**
1. פתח את התיקייה 'Negative Tests'
2. השתמש ב-JQL Query למעלה כדי למצוא את הטסטים
3. בחר את כל הטסטים מהרשימה
4. גרור ושחרר אותם לתיקייה 'Negative Tests'
5. או השתמש ב-'Move to Folder' מהתפריט

---


### Edge Cases

**JQL Query למציאת הטסטים:**
```jql
project = PZ AND key IN (PZ-15020, PZ-15021, PZ-15022, PZ-15023, PZ-15024, PZ-15025, PZ-15026, PZ-15027)
```

**טסטים להוספה (8):**
- PZ-15020
- PZ-15021
- PZ-15022
- PZ-15023
- PZ-15024
- PZ-15025
- PZ-15026
- PZ-15027

**הוראות:**
1. פתח את התיקייה 'Edge Cases'
2. השתמש ב-JQL Query למעלה כדי למצוא את הטסטים
3. בחר את כל הטסטים מהרשימה
4. גרור ושחרר אותם לתיקייה 'Edge Cases'
5. או השתמש ב-'Move to Folder' מהתפריט

---


### Load Tests

**JQL Query למציאת הטסטים:**
```jql
project = PZ AND key IN (PZ-15030, PZ-15031, PZ-15032, PZ-15033, PZ-15034)
```

**טסטים להוספה (5):**
- PZ-15030
- PZ-15031
- PZ-15032
- PZ-15033
- PZ-15034

**הוראות:**
1. פתח את התיקייה 'Load Tests'
2. השתמש ב-JQL Query למעלה כדי למצוא את הטסטים
3. בחר את כל הטסטים מהרשימה
4. גרור ושחרר אותם לתיקייה 'Load Tests'
5. או השתמש ב-'Move to Folder' מהתפריט

---


### Performance Tests

**JQL Query למציאת הטסטים:**
```jql
project = PZ AND key IN (PZ-15040, PZ-15041, PZ-15042, PZ-15043, PZ-15044, PZ-15045)
```

**טסטים להוספה (6):**
- PZ-15040
- PZ-15041
- PZ-15042
- PZ-15043
- PZ-15044
- PZ-15045

**הוראות:**
1. פתח את התיקייה 'Performance Tests'
2. השתמש ב-JQL Query למעלה כדי למצוא את הטסטים
3. בחר את כל הטסטים מהרשימה
4. גרור ושחרר אותם לתיקייה 'Performance Tests'
5. או השתמש ב-'Move to Folder' מהתפריט

---


### Investigation

**JQL Query למציאת הטסטים:**
```jql
project = PZ AND key IN (PZ-15051)
```

**טסטים להוספה (1):**
- PZ-15051

**הוראות:**
1. פתח את התיקייה 'Investigation'
2. השתמש ב-JQL Query למעלה כדי למצוא את הטסטים
3. בחר את כל הטסטים מהרשימה
4. גרור ושחרר אותם לתיקייה 'Investigation'
5. או השתמש ב-'Move to Folder' מהתפריט

---


## שלב 4: אימות

לאחר הוספת כל הטסטים, ודא:
- כל הטסטים נמצאים בתיקיות הנכונות
- אין טסטים שנותרו ללא תיקייה
- המבנה נכון לפי קטגוריות

---

## סיכום

**סה"כ טסטים:** 32
- **Positive Tests:** 5 טסטים
- **Negative Tests:** 7 טסטים
- **Edge Cases:** 8 טסטים
- **Load Tests:** 5 טסטים
- **Performance Tests:** 6 טסטים
- **Investigation:** 1 טסטים

---

**הערות:**
- אם טסט לא נמצא, ודא שהוא נוצר ב-Jira
- אם תיקייה לא קיימת, צור אותה ידנית
- ניתן להשתמש ב-JQL Query כדי למצוא טסטים ספציפיים
