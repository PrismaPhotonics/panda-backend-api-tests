# מדריך שימוש ב-Token Manager האוטומטי
# ===========================================

## סקירה כללית

ה-Token Manager מספק פתרון אוטומטי מלא לניהול authentication tokens עבור Prisma API. הוא:
- מקבל token חדש אוטומטית דרך login
- שומר token בקובץ מקומי
- בודק אם ה-token עדיין תקף
- מחליף token אוטומטית אם הוא פג תוקף
- תומך במספר סביבות (staging, production)

---

## שימוש בסיסי

### 1. הגדרת Credentials

#### דרך 1: Environment Variables (מומלץ)
```powershell
# Windows PowerShell
$env:PRISMA_API_USERNAME = "your-username"
$env:PRISMA_API_PASSWORD = "your-password"

# Linux/Mac
export PRISMA_API_USERNAME="your-username"
export PRISMA_API_PASSWORD="your-password"
```

#### דרך 2: Command Line Arguments
```bash
py scripts/api/validate_api_endpoints.py --env staging --username "your-username" --password "your-password"
```

---

### 2. הרצת הסקריפט

הסקריפט יקבל token אוטומטית אם יש username/password:

```bash
# הסקריפט יקבל token אוטומטית
py scripts/api/validate_api_endpoints.py --env staging --username "prisma" --password "your-password"
```

**מה קורה:**
1. הסקריפט בודק אם יש token שמור בקובץ (`.tokens/staging_token.json`)
2. אם יש token תקף - משתמש בו
3. אם אין token או שהוא פג תוקף - מקבל token חדש דרך login
4. שומר את ה-token החדש בקובץ לשימוש עתידי

---

## מבנה הקבצים

### תיקיית Tokens

ה-tokens נשמרים בתיקייה `.tokens/` בפרויקט:

```
focus_server_automation/
├── .tokens/
│   ├── staging_token.json      # Token עבור staging
│   └── production_token.json   # Token עבור production
```

**הערה:** התיקייה `.tokens/` נמצאת ב-`.gitignore` ולא תישמר ב-git!

### מבנה קובץ Token

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "acquired_at": "2025-11-06T14:50:00.000000",
  "expires_at": "2025-11-06T14:55:00.000000",
  "base_url": "https://10.10.10.100/prisma/api",
  "username": "prisma"
}
```

---

## שימוש מתקדם

### 1. שימוש ישיר ב-TokenManager

```python
from src.utils.token_manager import TokenManager

# יצירת Token Manager
manager = TokenManager(
    base_url="https://10.10.10.100/prisma/api",
    username="prisma",
    password="your-password",
    verify_ssl=False
)

# קבלת token (מקובץ או חדש)
token = manager.get_token()

# כפיית קבלת token חדש
token = manager.get_token(force_refresh=True)

# מחיקת token שמור
manager.clear_token()
```

### 2. בדיקת תוקף Token

ה-TokenManager בודק אוטומטית אם ה-token תקף לפי ה-JWT expiration claim. אם ה-token פג תוקף, הוא מקבל token חדש אוטומטית.

### 3. שימוש ב-Token בסקריפטים אחרים

```python
from src.utils.token_manager import TokenManager
import requests

# קבלת token
manager = TokenManager(
    base_url="https://10.10.10.100/prisma/api",
    username=os.getenv('PRISMA_API_USERNAME'),
    password=os.getenv('PRISMA_API_PASSWORD')
)
token = manager.get_token()

# שימוש ב-token
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}
response = requests.get(
    'https://10.10.10.100/prisma/api/some-endpoint',
    headers=headers,
    verify=False
)
```

---

## פתרון בעיות

### בעיה: Token לא נשמר

**תסמינים:**
- הסקריפט מקבל token כל פעם מחדש
- לא רואה קובץ `.tokens/staging_token.json`

**פתרונות:**
1. בדוק הרשאות כתיבה בתיקיית הפרויקט
2. ודא שהתיקייה `.tokens/` נוצרת (נוצרת אוטומטית)
3. בדוק את ה-logs לפרטים

### בעיה: Token פג תוקף כל הזמן

**תסמינים:**
- הסקריפט מקבל token חדש כל פעם
- ה-token פג תוקף מהר מדי

**פתרונות:**
1. זה נורמלי - JWT tokens בדרך כלל פגי תוקף אחרי כמה דקות
2. ה-TokenManager מחליף אותם אוטומטית
3. אם זה מפריע, בדוק את ה-API configuration

### בעיה: Login נכשל

**תסמינים:**
```
[ERROR] Failed to acquire token - all login endpoints failed
```

**פתרונות:**
1. בדוק שה-username וה-password נכונים
2. בדוק שיש גישה ל-API server
3. בדוק את ה-network/VPN
4. נסה להתחבר דרך דפדפן כדי לוודא שה-credentials עובדים

---

## אבטחה

### המלצות אבטחה:

1. **אל תשמור credentials בקוד**
   - השתמש ב-Environment Variables
   - או בקובץ `.env` (לא ב-git!)

2. **ה-Token files נשמרים ב-`.gitignore`**
   - ה-tokens לא יישמרו ב-git
   - אבל הם עדיין על הדיסק - שמור עליהם!

3. **ה-Token files מכילים username**
   - אבל לא password
   - עדיין - שמור עליהם!

4. **למקרה של production:**
   - שקול להשתמש ב-Secrets Manager
   - או ב-encrypted storage

---

## דוגמאות שימוש

### דוגמה 1: הרצה פשוטה עם Auto-Token

```bash
# הגדר credentials
$env:PRISMA_API_USERNAME = "prisma"
$env:PRISMA_API_PASSWORD = "your-password"

# הרץ - token יקבל אוטומטית
py scripts/api/validate_api_endpoints.py --env staging
```

### דוגמה 2: כפיית קבלת Token חדש

```python
from src.utils.token_manager import TokenManager

manager = TokenManager(
    base_url="https://10.10.10.100/prisma/api",
    username="prisma",
    password="your-password"
)

# כפיית token חדש
token = manager.get_token(force_refresh=True)
```

### דוגמה 3: שימוש ב-Token בסקריפט מותאם אישית

```python
import os
from src.utils.token_manager import TokenManager
import requests

# קבלת token
manager = TokenManager(
    base_url=os.getenv('PRISMA_API_BASE_URL'),
    username=os.getenv('PRISMA_API_USERNAME'),
    password=os.getenv('PRISMA_API_PASSWORD')
)

token = manager.get_token()
if not token:
    print("Failed to get token")
    exit(1)

# שימוש ב-token
session = requests.Session()
session.headers['Authorization'] = f'Bearer {token}'
session.cookies.set('access-token', token)

response = session.get('https://10.10.10.100/prisma/api/some-endpoint', verify=False)
print(response.json())
```

---

## סיכום

ה-Token Manager מספק פתרון מלא לניהול authentication:

✅ **קבלה אוטומטית** - מקבל token דרך login  
✅ **שמירה מקומית** - שומר token בקובץ  
✅ **בדיקת תוקף** - בודק אם token תקף  
✅ **חידוש אוטומטי** - מחליף token אם פג תוקף  
✅ **תמיכה במספר סביבות** - staging, production, וכו'  

**השימוש הפשוט ביותר:**
```bash
# הגדר credentials
$env:PRISMA_API_USERNAME = "your-username"
$env:PRISMA_API_PASSWORD = "your-password"

# הרץ - הכל אוטומטי!
py scripts/api/validate_api_endpoints.py --env staging
```

---

**תאריך עדכון:** 2025-11-06  
**גרסה:** 1.0.0


