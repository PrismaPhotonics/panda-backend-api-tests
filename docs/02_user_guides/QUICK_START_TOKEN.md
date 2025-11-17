# Quick Start Guide - Token Manager (FULLY AUTOMATIC)
# ====================================================

## Credentials עבור Staging Environment

**Username:** `prisma`  
**Password:** `prisma`

**הכל אוטומטי לחלוטין!** 🎉

---

## שימוש פשוט (100% אוטומטי)

### Windows PowerShell:

```powershell
# הגדר credentials (פעם אחת)
$env:PRISMA_API_USERNAME = "prisma"
$env:PRISMA_API_PASSWORD = "prisma"

# הרץ את הסקריפט - הכל אוטומטי!
py scripts/api/validate_api_endpoints.py --env staging
```

**מה קורה אוטומטית:**
1. ✅ הסקריפט בודק אם יש token שמור ב-`.tokens/staging_token.json`
2. ✅ אם יש token תקף → משתמש בו
3. ✅ אם אין token או שהוא פג תוקף → מקבל token חדש אוטומטית דרך `/prisma/api/auth/login`
4. ✅ שומר את ה-token לשימוש עתידי
5. ✅ הכל קורה מאחורי הקלעים - אין צורך בהתערבות ידנית!

### או עם Command Line Arguments:

```powershell
py scripts/api/validate_api_endpoints.py --env staging --username "prisma" --password "prisma"
```

---

## מה קורה מאחורי הקלעים?

1. **בדיקה ראשונית** - הסקריפט בודק אם יש token שמור ב-`.tokens/staging_token.json`
2. **בדיקת תוקף** - אם יש token, בודק אם הוא עדיין תקף (לפי JWT expiration)
3. **קבלת token חדש** - אם אין token או שהוא פג תוקף:
   - מתחבר ל-`/prisma/api/auth/login` עם username/password
   - מקבל `access-token` cookie
   - שומר את ה-token בקובץ
4. **שימוש ב-token** - משתמש ב-token לכל הבקשות הבאות

---

## בדיקה מהירה

לבדוק אם ה-token נוצר:

```powershell
# בדוק אם קיים קובץ token
Test-Path ".tokens\staging_token.json"

# צפה בתוכן הקובץ (ללא ה-token עצמו)
Get-Content ".tokens\staging_token.json" | ConvertFrom-Json | Select-Object username, acquired_at, expires_at
```

---

## הערות חשובות

✅ **הכל אוטומטי** - אין צורך בהתערבות ידנית  
✅ **ה-token נשמר אוטומטית** ב-`.tokens/staging_token.json`  
✅ **ה-token מתחדש אוטומטית** אם הוא פג תוקף  
✅ **הקובץ לא נשמר ב-git** (נמצא ב-`.gitignore`)  
✅ **ה-credentials נשמרים רק ב-Environment Variables** (לא בקוד!)  

---

## דוגמאות שימוש

### דוגמה 1: הרצה פשוטה (מומלץ)

```powershell
# הגדר credentials פעם אחת
$env:PRISMA_API_USERNAME = "prisma"
$env:PRISMA_API_PASSWORD = "prisma"

# הרץ - הכל אוטומטי!
py scripts/api/validate_api_endpoints.py --env staging
```

### דוגמה 2: בדיקת Prisma API בלבד

```powershell
$env:PRISMA_API_USERNAME = "prisma"
$env:PRISMA_API_PASSWORD = "prisma"
py scripts/api/validate_api_endpoints.py --env staging --prisma-only
```

### דוגמה 3: בדיקת Focus Server API בלבד

```powershell
py scripts/api/validate_api_endpoints.py --env staging --focus-server-only
```

---

## פתרון בעיות

### בעיה: Token לא מתקבל

**תסמינים:**
```
[WARN] Failed to acquire token automatically
```

**פתרונות:**
1. בדוק שה-username וה-password נכונים
2. בדוק שיש גישה ל-API server (`https://10.10.10.100`)
3. בדוק את ה-network/VPN

### בעיה: Token פג תוקף כל הזמן

**זה נורמלי!** ה-token מתחדש אוטומטית. אם זה מפריע, זה אומר שה-token פג תוקף מהר מדי (כ-5 דקות).

---

**תאריך:** 2025-11-06  
**גרסה:** 2.0.0 (Fully Automatic)

