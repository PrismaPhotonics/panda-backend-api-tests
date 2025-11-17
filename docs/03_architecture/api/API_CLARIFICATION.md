# הבהרה: שני APIs שונים במערכת
# ===================================

## סקירה כללית

במערכת יש **שני APIs שונים** שצריך להבדיל ביניהם:

---

## 1. Focus Server API (Yoshi) 🎯

**Base URL:** `https://10.10.10.100/focus-server/`

**תיאור:**  
זה ה-API של Focus Server עצמו - השרת שמטפל ב-streaming של נתונים, spectrograms, וכו'.

**Endpoints:**
- `GET /channels` - קבלת רשימת ערוצים זמינים
- `GET /live_metadata` - קבלת metadata של fiber חי
- `POST /configure` - הגדרת streaming job
- `GET /metadata/{job_id}` - קבלת metadata של job ספציפי

**Authentication:**  
❌ **אין authentication כלל** - אין username/password, אין tokens, אין cookies  
✅ **פתוח לגישה** - כל בקשה עובדת ללא authentication

**שימוש:**
```python
# Focus Server API
base_url = "https://10.10.10.100/focus-server"
response = requests.get(f"{base_url}/channels", verify=False)
```

---

## 2. Prisma Web App API (Web Panda) 🌐

**Base URL:** `https://10.10.10.100/prisma/api`

**תיאור:**  
זה ה-API של ה-Web Application - השרת שמטפל ב-users, roles, alerts, regions, וכו'.

**Endpoints:**
- `GET /login-configuration` - קבלת הגדרות login
- `POST /auth/login` - התחברות (מחזיר `access-token` cookie)
- `GET /{siteId}/api/role` - קבלת roles
- `GET /{siteId}/api/alert` - קבלת alerts
- `POST /{siteId}/api/region/add` - הוספת region
- וכו'...

**Authentication:**  
✅ **דורש authentication** - Cookie בשם `access-token` או Bearer token

**Login Endpoint:**
```
POST /prisma/api/auth/login
Content-Type: application/x-www-form-urlencoded

username=prisma&password=prisma
```

**Response:**
- Status: `201 Created`
- Cookie: `access-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- Cookie: `refresh-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

**שימוש:**
```python
# Prisma Web App API
base_url = "https://10.10.10.100/prisma/api"

# Login
session = requests.Session()
session.post(
    f"{base_url}/auth/login",
    data={"username": "prisma", "password": "prisma"},
    verify=False
)
# עכשיו session.cookies מכיל את access-token

# שימוש ב-API
response = session.get(f"{base_url}/prisma-210-1000/api/role", verify=False)
```

---

## ההבדלים העיקריים

| מאפיין | Focus Server API | Prisma Web App API |
|--------|------------------|-------------------|
| **Base URL** | `/focus-server/` | `/prisma/api` |
| **תפקיד** | Streaming, spectrograms | Users, roles, alerts, regions |
| **Authentication** | ❌ **אין כלל** - אין username/password | ✅ **דורש** (cookie `access-token`) |
| **Username/Password** | ❌ **לא קיים** | ✅ **נדרש** (`prisma` / `prisma`) |
| **Login Endpoint** | ❌ **אין** | ✅ `/prisma/api/auth/login` |
| **Swagger Spec** | לא קיים (עדיין) | קיים ב-`swagger_spec.json` |

---

## בקונפיגורציה (`config/environments.yaml`)

```yaml
focus_server:
  base_url: "https://10.10.10.100/focus-server/"      # Focus Server API
  frontend_url: "https://10.10.10.100/liveView"        # Frontend UI
  frontend_api_url: "https://10.10.10.100/prisma/api/internal/sites/prisma-210-1000"  # Prisma Web App API
```

**הערה:** `frontend_api_url` מכיל את ה-Prisma Web App API base URL + path ספציפי ל-site.

---

## בסקריפט `validate_api_endpoints.py`

הסקריפט בודק את שני ה-APIs בסדר הבא:

1. **Focus Server API** - בודק endpoints של Yoshi (`/channels`, `/live_metadata`, וכו')
   - אין authentication
   - רץ ראשון (אם לא מוגדר `--prisma-only`)

2. **Prisma Web App API** - בודק endpoints מה-Swagger spec
   - **CRITICAL: `/login-configuration` רץ ראשון לפני כל שאר ה-endpoints!**
   - זה prerequisite - כל שאר ה-endpoints תלויים בזה
   - אחרי `/login-configuration` → בודק את כל שאר ה-endpoints (`/{siteId}/api/...`)

**Authentication:**
- Focus Server API - לא משתמש ב-authentication (או authentication שונה)
- Prisma Web App API - משתמש ב-TokenManager לקבלת `access-token` cookie

**סדר הרצה:**
```
1. Focus Server API validation (אופציונלי)
2. Prisma Web App API validation:
   a. CRITICAL: GET /login-configuration (prerequisite - חובה!)
   b. כל שאר ה-endpoints
```

**Site ID:** `prisma-210-1000` (מ-`https://10.10.10.100/liveView?siteId=prisma-210-1000`)

---

## Token Manager

ה-TokenManager מיועד **רק ל-Prisma Web App API**:

```python
# TokenManager מקבל token עבור Prisma Web App API
token_manager = TokenManager(
    base_url="https://10.10.10.100/prisma/api",  # Prisma Web App API
    username="prisma",
    password="prisma"
)
token = token_manager.get_token()  # מקבל access-token cookie
```

**הערה חשובה:**  
❌ **Focus Server API לא משתמש ב-TokenManager** - אין authentication כלל, אין username/password, אין tokens.  
✅ **רק Prisma Web App API** משתמש ב-TokenManager לקבלת `access-token` cookie.

---

## סיכום

✅ **Focus Server API** (`/focus-server/`) - **אין authentication כלל** - אין username/password, אין tokens  
✅ **Prisma Web App API** (`/prisma/api`) - **דורש authentication** דרך `/auth/login` עם username/password  

הסקריפט `validate_api_endpoints.py` מטפל בשניהם נכון:
- **Focus Server API** - בודק **ללא authentication** (אין username/password, אין tokens)
- **Prisma Web App API** - בודק **עם authentication** (אוטומטי דרך TokenManager עם username/password)

---

**תאריך:** 2025-11-06

