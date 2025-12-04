# דוגמאות ל-Schedules ב-GitHub Actions

מדריך לשימוש בכלי ניהול ה-schedules ב-MCP Sentinel.

## דוגמאות Cron Expressions

### יומי
- `0 8 * * *` - כל יום ב-8:00 בבוקר (UTC)
- `0 10 * * *` - כל יום ב-10:00 בבוקר (UTC)
- `0 0 * * *` - כל יום בחצות

### שבועי
- `0 9 * * 1` - כל יום שני ב-9:00 בבוקר
- `0 8 * * 0` - כל יום ראשון ב-8:00 בבוקר

### חודשי
- `0 8 1 * *` - יום ראשון של כל חודש ב-8:00 בבוקר

### כל X שעות
- `0 */6 * * *` - כל 6 שעות
- `0 */12 * * *` - כל 12 שעות

## Timezones נפוצים

- `UTC` - Coordinated Universal Time
- `Asia/Jerusalem` - ישראל
- `America/New_York` - EST/EDT
- `Europe/London` - GMT/BST

## דוגמאות שימוש ב-Cursor Chat

### הוספת schedule פשוט

```
"Add schedule to smoke-tests.yml: run daily at 8 AM UTC"
```

### הוספת schedule עם timezone

```
"Schedule smoke-tests.yml to run every day at 8 AM Israel time"
```

### הוספת schedule שבועי

```
"Add schedule to regression-tests.yml: run every Monday at 9 AM UTC"
```

### הסרת schedule

```
"Remove schedule from smoke-tests.yml"
```

### רשימת schedules

```
"List all scheduled workflows"
```

### קבלת YAML

```
"Get YAML content of smoke-tests.yml"
```

### עדכון YAML מלא

```
"Update workflow YAML for smoke-tests.yml"
```

## דוגמאות YAML

### לפני הוספת schedule:

```yaml
on:
  push:
    branches: [ main ]
  workflow_dispatch:
```

### אחרי הוספת schedule:

```yaml
on:
  push:
    branches: [ main ]
  workflow_dispatch:
  schedule:
    - cron: '0 8 * * *'
      timezone: 'UTC'
```

### מספר schedules:

```yaml
on:
  schedule:
    - cron: '0 8 * * *'      # כל יום ב-8:00
      timezone: 'UTC'
    - cron: '0 9 * * 1'      # כל יום שני ב-9:00
      timezone: 'Asia/Jerusalem'
```

## הערות חשובות

1. **GitHub Actions מוגבל ל-5 schedules לכל repository**
2. **Schedules רץ רק על default branch (בדרך כלל main)**
3. **Cron expressions משתמשים ב-UTC אם לא מצוין timezone**
4. **שינויים ב-YAML דורשים commit - הכלי עושה זאת אוטומטית**

## פתרון בעיות

### Schedule לא רץ

1. בדוק שה-workflow על default branch
2. בדוק שה-cron expression תקין
3. בדוק שה-timezone נכון
4. בדוק ב-GitHub Actions אם יש שגיאות

### שגיאת "Too many schedules"

- יש יותר מ-5 schedules ב-repository
- הסר schedules ישנים לפני הוספת חדשים

### שגיאת "Invalid cron expression"

- בדוק את הפורמט: `minute hour day month weekday`
- ודא שהערכים בטווח הנכון

