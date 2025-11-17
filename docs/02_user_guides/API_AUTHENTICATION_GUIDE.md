# מדריך אימות (Authentication) ל-API Validation

## סקירה כללית

הסקריפט `validate_api_endpoints.py` תומך כעת באימות (authentication) כדי לבדוק endpoints שדורשים הרשאה. יש שלוש דרכים לספק אימות:

1. **Username/Password** - הסקריפט ינסה להתחבר אוטומטית
2. **Access Token** - אם יש לך כבר token/cookie
3. **Environment Variables** - להגדרה קבועה

---

## שיטות אימות

### 1. שימוש ב-Username ו-Password

הסקריפט ינסה להתחבר אוטומטית ל-endpoints שונים של login:

```bash
# Windows PowerShell
py scripts/api/validate_api_endpoints.py --env staging --username "your-username" --password "your-password"

# Linux/Mac
python scripts/api/validate_api_endpoints.py --env staging --username "your-username" --password "your-password"
```

**הערה:** הסקריפט ינסה את ה-endpoints הבאים:
- `/auth/login`
- `/api/auth/login`
- `/prisma/api/auth/login`

---

### 2. שימוש ב-Access Token (Cookie)

אם יש לך כבר access token (למשל, מ-cookie של דפדפן):

```bash
py scripts/api/validate_api_endpoints.py --env staging --access-token "your-token-value"
```

**איך להשיג את ה-Token:**

#### דרך 1: מדפדפן (Chrome/Edge)
1. התחבר לאתר דרך הדפדפן
2. לחץ F12 לפתיחת Developer Tools
3. לך ל-**Application** (Chrome) או **Storage** (Firefox)
4. בחר **Cookies** → בחר את הדומיין
5. מצא את ה-cookie בשם `access-token`
6. העתק את ה-Value

#### דרך 2: מדפדפן (Firefox)
1. התחבר לאתר דרך הדפדפן
2. לחץ F12 לפתיחת Developer Tools
3. לך ל-**Storage** → **Cookies**
4. מצא את ה-cookie בשם `access-token`
5. העתק את ה-Value

---

### 3. שימוש ב-Environment Variables

להגדרה קבועה, ניתן להגדיר משתני סביבה:

#### Windows PowerShell
```powershell
$env:PRISMA_API_USERNAME = "your-username"
$env:PRISMA_API_PASSWORD = "your-password"
# או
$env:PRISMA_API_ACCESS_TOKEN = "your-token-value"

py scripts/api/validate_api_endpoints.py --env staging
```

#### Linux/Mac (Bash)
```bash
export PRISMA_API_USERNAME="your-username"
export PRISMA_API_PASSWORD="your-password"
# או
export PRISMA_API_ACCESS_TOKEN="your-token-value"

python scripts/api/validate_api_endpoints.py --env staging
```

#### Windows (Permanent - System Environment Variables)
1. לחץ על **Start** → חפש "Environment Variables"
2. בחר **Edit the system environment variables**
3. לחץ **Environment Variables**
4. לחץ **New** ב-**User variables**
5. הוסף:
   - Name: `PRISMA_API_USERNAME`, Value: `your-username`
   - Name: `PRISMA_API_PASSWORD`, Value: `your-password`
   - או Name: `PRISMA_API_ACCESS_TOKEN`, Value: `your-token-value`

---

## דוגמאות שימוש

### דוגמה 1: בדיקה עם Username/Password
```bash
py scripts/api/validate_api_endpoints.py --env staging --username "admin" --password "password123" --prisma-only
```

### דוגמה 2: בדיקה עם Access Token
```bash
py scripts/api/validate_api_endpoints.py --env staging --access-token "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." --prisma-only
```

### דוגמה 3: בדיקה של שני ה-APIs עם Authentication
```bash
py scripts/api/validate_api_endpoints.py --env staging --username "admin" --password "password123"
```

### דוגמה 4: בדיקה רק של Focus Server (ללא authentication)
```bash
py scripts/api/validate_api_endpoints.py --env staging --focus-server-only
```

---

## פתרון בעיות

### בעיה: Authentication נכשל

**תסמינים:**
```
[WARN] Authentication failed - all login endpoints failed
```

**פתרונות:**

1. **בדוק את ה-credentials:**
   - ודא שה-username וה-password נכונים
   - ודא שיש לך הרשאות גישה ל-API

2. **נסה להשתמש ב-Access Token:**
   - התחבר דרך דפדפן והעתק את ה-cookie `access-token`
   - השתמש ב-`--access-token` במקום username/password

3. **בדוק את ה-Login Endpoint:**
   - ייתכן שה-API משתמש ב-endpoint אחר ל-login
   - בדוק את התיעוד של ה-API או פנה לתמיכה

4. **בדוק את ה-Network:**
   - ודא שיש לך גישה ל-API server
   - בדוק firewall/VPN

### בעיה: Endpoints עדיין מחזירים 401/403

**תסמינים:**
```
Status: 401
Status: 403
```

**פתרונות:**

1. **ודא שה-Authentication הצליח:**
   - חפש בה-log: `[OK] Authentication successful`
   - אם לא רואה את זה, ה-authentication נכשל

2. **בדוק את ה-Token:**
   - ייתכן שה-token פג תוקף
   - קבל token חדש דרך דפדפן

3. **בדוק הרשאות:**
   - ייתכן שהמשתמש שלך לא מספיק הרשאות
   - נסה עם משתמש אחר עם הרשאות גבוהות יותר

---

## אבטחה

### המלצות אבטחה:

1. **אל תזין passwords ב-command line אם יש אנשים אחרים לידך**
2. **השתמש ב-Environment Variables במקום command line arguments**
3. **אל תשמור credentials בקובץ**
4. **השתמש ב-Access Token אם אפשר (יותר בטוח מ-password)**
5. **ודא שה-`.gitignore` כולל קבצים עם credentials**

### איפה לא לשמור credentials:

- ❌ בקובץ Python
- ❌ בקובץ YAML/JSON ב-repository
- ❌ ב-command line history (אם אפשר)
- ❌ ב-commit messages

### איפה כן לשמור credentials:

- ✅ ב-Environment Variables (מערכת הפעלה)
- ✅ ב-Secrets Manager (אם יש)
- ✅ ב-`.env` file (לא ב-git)

---

## מידע נוסף

### איזה סוג Authentication ה-API משתמש?

לפי ה-Swagger spec, ה-Prisma Web App API משתמש ב:
- **Cookie-based authentication** - Cookie בשם `access-token`

### איך הסקריפט מטפל ב-Authentication?

1. אם סופק `--access-token`, הסקריפט משתמש בו ישירות כ-cookie
2. אם סופקו `--username` ו-`--password`, הסקריפט מנסה להתחבר ל-login endpoints
3. הסקריפט תומך גם ב-Bearer token (אם ה-API מחזיר `access_token` ב-JSON response)

---

## דוגמאות מתקדמות

### שימוש עם Script

צור קובץ `validate_with_auth.ps1`:

```powershell
# validate_with_auth.ps1
$env:PRISMA_API_USERNAME = Read-Host "Enter username"
$env:PRISMA_API_PASSWORD = Read-Host "Enter password" -AsSecureString
$plainPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($env:PRISMA_API_PASSWORD)
)
$env:PRISMA_API_PASSWORD = $plainPassword

py scripts/api/validate_api_endpoints.py --env staging
```

### שימוש עם .env file

צור קובץ `.env` (לא ב-git!):

```bash
PRISMA_API_USERNAME=your-username
PRISMA_API_PASSWORD=your-password
```

ואז בקוד Python:

```python
from dotenv import load_dotenv
import os

load_dotenv()
username = os.getenv('PRISMA_API_USERNAME')
password = os.getenv('PRISMA_API_PASSWORD')
```

---

## סיכום

הסקריפט תומך בשלוש דרכים לספק authentication:

1. **Command Line Arguments:** `--username`, `--password`, `--access-token`
2. **Environment Variables:** `PRISMA_API_USERNAME`, `PRISMA_API_PASSWORD`, `PRISMA_API_ACCESS_TOKEN`
3. **Browser Cookie:** העתק את `access-token` cookie מהדפדפן

הדרך המומלצת היא להשתמש ב-Environment Variables או ב-Access Token (יותר בטוח מ-password).

---

**תאריך עדכון:** 2025-11-06  
**גרסה:** 1.0.0

