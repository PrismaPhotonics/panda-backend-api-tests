# רשימת Endpoints שעובדים (GET - קריאה בלבד)

**תאריך:** 2025-11-06  
**Environment:** staging  
**משתמש:** prisma  
**סטטוס:** ✅ עובדים ללא הרשאות מיוחדות

---

## Focus Server API (Yoshi)

**Base URL:** `https://10.10.10.100/focus-server/`

### ✅ Endpoints שעובדים:

| # | Method | Endpoint | תיאור | Response Time |
|---|--------|----------|-------|----------------|
| 1 | **GET** | `/channels` | קבלת רשימת ערוצים זמינים | 50.07ms |
| 2 | **GET** | `/live_metadata` | קבלת metadata של fiber חי | 2.33ms |

**הערה:** `POST /configure` גם עובד (מחזיר 422 - validation error, אבל ה-endpoint קיים).

---

## Prisma Web App API

**Base URL:** `https://10.10.10.100/prisma/api`  
**Site ID:** `prisma-210-1000`

### ✅ Endpoints שעובדים (כולם GET - קריאה בלבד):

| # | Method | Endpoint | תיאור | Response Time | Operation ID |
|---|--------|----------|-------|----------------|--------------|
| 1 | **GET** | `/login-configuration` | קבלת הגדרות login | 39.36ms | GetLoginConfiguration |
| 2 | **GET** | `/{siteId}/api/alert` | קבלת רשימת alerts | 54.46ms | AlertController_findAll |
| 3 | **GET** | `/{siteId}/api/alert/export-alerts` | ייצוא alerts | 6.99ms | AlertController_exportsAlerts |
| 4 | **GET** | `/{siteId}/api/alert/get-alert-status` | קבלת סטטוס alerts | 22.49ms | AlertController_getAlertStatus |
| 5 | **GET** | `/{siteId}/api/point/map-setup` | קבלת הגדרות מפה | 47.32ms | PointController_findAll |
| 6 | **GET** | `/{siteId}/api/region` | קבלת רשימת regions | 4.92ms | RegionController_getAllRegions |
| 7 | **GET** | `/{siteId}/api/site/get-sites` | קבלת רשימת sites | 4.37ms | SiteController_findAll |
| 8 | **GET** | `/{siteId}/api/user/config` | קבלת הגדרות משתמש | 9.89ms | GetLegacyUserConfiguration |

**סה"כ:** 8 endpoints

---

## סיכום לפי קטגוריה

### Alerts (3 endpoints):
- ✅ `GET /{siteId}/api/alert` - רשימת alerts
- ✅ `GET /{siteId}/api/alert/export-alerts` - ייצוא alerts
- ✅ `GET /{siteId}/api/alert/get-alert-status` - סטטוס alerts

### Regions (1 endpoint):
- ✅ `GET /{siteId}/api/region` - רשימת regions

### Sites (1 endpoint):
- ✅ `GET /{siteId}/api/site/get-sites` - רשימת sites

### Points/Maps (1 endpoint):
- ✅ `GET /{siteId}/api/point/map-setup` - הגדרות מפה

### Users (1 endpoint):
- ✅ `GET /{siteId}/api/user/config` - הגדרות משתמש

### Authentication (1 endpoint):
- ✅ `GET /login-configuration` - הגדרות login

### Focus Server (2 endpoints):
- ✅ `GET /channels` - רשימת ערוצים
- ✅ `GET /live_metadata` - metadata של fiber

---

## דפוסים

### ✅ מה עובד:
- **כל ה-GET endpoints** (קריאה בלבד)
- **לא דורשים הרשאות מיוחדות**
- **עובדים עם משתמש מוגבל** (`prisma`)

### ❌ מה לא עובד:
- **כל ה-DELETE endpoints** (מחיקה)
- **כל ה-POST endpoints** (יצירה/עדכון)
- **GET endpoints מסוימים** שדורשים הרשאות (כמו `/api/role`, `/api/user/get-all-users`)

---

## דוגמאות שימוש

### Focus Server API:
```python
import requests

# קבלת ערוצים
response = requests.get(
    "https://10.10.10.100/focus-server/channels",
    verify=False
)

# קבלת metadata
response = requests.get(
    "https://10.10.10.100/focus-server/live_metadata",
    verify=False
)
```

### Prisma Web App API:
```python
import requests

# צריך token (אוטומטי דרך TokenManager)
session = requests.Session()
session.cookies.set('access-token', 'YOUR_TOKEN', domain='10.10.10.100')

# קבלת alerts
response = session.get(
    "https://10.10.10.100/prisma/api/prisma-210-1000/api/alert",
    verify=False
)

# קבלת regions
response = session.get(
    "https://10.10.10.100/prisma/api/prisma-210-1000/api/region",
    verify=False
)
```

---

## הערות חשובות

1. **כל ה-endpoints שעובדים הם GET** - קריאה בלבד
2. **לא דורשים הרשאות מיוחדות** - עובדים עם משתמש מוגבל
3. **Focus Server API** - אין authentication כלל
4. **Prisma Web App API** - דורש token (אבל לא הרשאות מיוחדות)
5. **Site ID:** `prisma-210-1000` (חייב להיות ב-URL)

---

**סה"כ Endpoints שעובדים:** 10 (2 Focus Server + 8 Prisma Web App)

