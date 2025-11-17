# למה יש 403 (Forbidden) במקום 401 (Unauthorized)?

## ההבדל בין Authentication ל-Authorization

### Authentication (אימות) - "מי אתה?"
- **מטרה:** לוודא שהמשתמש מזוהה (מי אתה?)
- **דוגמה:** username/password, token
- **Status Code:** `401 Unauthorized` (אם לא מזוהה)
- **מה קורה:** השרת בודק אם ה-token תקף, אם המשתמש קיים, וכו'

### Authorization (הרשאות) - "מה אתה יכול לעשות?"
- **מטרה:** לוודא שלמשתמש יש הרשאות לבצע פעולה ספציפית (מה אתה יכול לעשות?)
- **דוגמה:** הרשאות כמו `update_users`, `delete_alerts`, `manage_regions`
- **Status Code:** `403 Forbidden` (אם אין הרשאות)
- **מה קורה:** השרת בודק אם למשתמש יש את ההרשאה הנדרשת לפעולה

---

## מה קורה עם המשתמש `prisma`?

### ✅ Authentication עובד!
- ה-token תקף
- המשתמש מזוהה
- השרת יודע מי זה

### ❌ Authorization לא עובד!
- למשתמש `prisma` **אין הרשאות** לבצע פעולות מסוימות
- התשובה מהשרת:
  ```json
  {
    "statusCode": 403,
    "message": "The operation is forbidden due to missing permission: update_users. The actual permissions are: ."
  }
  ```
- **"The actual permissions are: ."** = אין הרשאות בכלל!

---

## למה endpoints מסוימים עובדים ואחרים לא?

### ✅ Endpoints שעובדים (8 endpoints):
- `GET /login-configuration` - לא דורש הרשאות
- `GET /{siteId}/api/alert` - קריאה בלבד, לא דורש הרשאות מיוחדות
- `GET /{siteId}/api/alert/export-alerts` - קריאה בלבד
- `GET /{siteId}/api/alert/get-alert-status` - קריאה בלבד
- `GET /{siteId}/api/point/map-setup` - קריאה בלבד
- `GET /{siteId}/api/region` - קריאה בלבד
- `GET /{siteId}/api/site/get-sites` - קריאה בלבד
- `GET /{siteId}/api/user/config` - קריאה בלבד

**דפוס:** כל ה-endpoints שעובדים הם **GET (קריאה בלבד)** - לא דורשים הרשאות מיוחדות.

### ❌ Endpoints שלא עובדים (15 endpoints):
- `DELETE /{siteId}/api/alert/delete` - דורש הרשאה למחוק alerts
- `DELETE /{siteId}/api/region/{id}` - דורש הרשאה למחוק regions
- `GET /{siteId}/api/role` - דורש הרשאה `update_users` (גם קריאה!)
- `GET /{siteId}/api/user/get-all-users` - דורש הרשאה לראות users
- `POST /{siteId}/api/region/add` - דורש הרשאה להוסיף regions
- `POST /{siteId}/api/region/update` - דורש הרשאה לעדכן regions
- `POST /{siteId}/api/user/*` - כל פעולות ה-users דורשות הרשאות
- וכו'...

**דפוס:** כל ה-endpoints שלא עובדים דורשים **הרשאות ספציפיות** (כמו `update_users`, `manage_regions`, וכו').

---

## למה זה קורה?

### הסיבה:
המשתמש `prisma` הוא משתמש **מוגבל** - יש לו הרשאות לקרוא נתונים מסוימים, אבל **לא** לבצע פעולות ניהול (מחיקה, עדכון, הוספה).

### זה נורמלי!
זה לא באג - זה **תכונת אבטחה**. לא כל משתמש צריך להיות admin.

---

## איך לפתור?

### אפשרות 1: להשתמש במשתמש עם הרשאות מלאות
אם יש לך משתמש admin עם הרשאות מלאות, השתמש בו:
```powershell
$env:PRISMA_API_USERNAME = "admin"
$env:PRISMA_API_PASSWORD = "admin_password"
```

### אפשרות 2: להוסיף הרשאות למשתמש `prisma`
אם אתה admin, תוכל להוסיף הרשאות למשתמש `prisma` דרך ה-UI או ה-API.

### אפשרות 3: לקבל את המצב הנוכחי
אם אתה רק רוצה לבדוק את ה-API, זה בסדר - 8 endpoints עובדים, וזה מספיק לבדיקה בסיסית.

---

## סיכום

| מה | סטטוס | הסבר |
|---|-------|------|
| **Authentication** | ✅ עובד | ה-token תקף, המשתמש מזוהה |
| **Authorization** | ❌ לא עובד | למשתמש `prisma` אין הרשאות לפעולות מסוימות |
| **403 Forbidden** | ✅ נורמלי | זה לא באג - זה אומר שהמשתמש לא מורשה |

**המסקנה:** הכל עובד נכון! המשתמש `prisma` פשוט לא מורשה לבצע פעולות מסוימות - זה תכונת אבטחה, לא באג.

---

**תאריך:** 2025-11-06

