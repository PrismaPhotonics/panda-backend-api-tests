# תיקון בעיות GitHub Actions

**תאריך:** 2025-11-19  
**Run:** https://github.com/PrismaPhotonics/panda-backend-api-tests/actions/runs/19502960959

---

## 🔍 בעיות שזוהו

### 1. "Create reports directory" - Exit Code 2 ✅ תוקן

**בעיה:** ה-step ניסה להשתמש ב-PowerShell syntax ב-Linux runner  
**תיקון:** שונה ל-`mkdir -p reports` בלבד

### 2. "Check Focus Server availability" ✅ תוקן

**בעיה:** ניסה לבדוק `runner.os` עם PowerShell syntax  
**תיקון:** שונה ל-bash syntax בלבד

### 3. "Install system dependencies" ✅ תוקן

**בעיה:** ניסה להתקין dependencies ל-Windows שלא נחוץ  
**תיקון:** הוסר ה-Windows check

### 4. "Run Smoke Tests" - Exit Code 2 ✅ תוקן

**בעיה:** pytest נכשל עם exit code 2 (collection/configuration error)  
**תיקון:** 
- הוסף `PYTHONPATH` כדי לוודא ש-imports עובדים
- הוסף step לבדיקת collection לפני הרצת הבדיקות
- שיפור טיפול בשגיאות עם הודעות ברורות יותר

---

## ✅ מה תוקן

1. ✅ `Create reports directory` - פשוט `mkdir -p reports`
2. ✅ `Check Focus Server availability` - bash בלבד
3. ✅ `Install system dependencies` - Linux בלבד
4. ✅ `Set PYTHONPATH` - הוסף step חדש להגדרת PYTHONPATH
5. ✅ `Verify test collection` - הוסף step לבדיקת collection לפני הרצה
6. ✅ `Run Smoke Tests` - שיפור טיפול בשגיאות עם exit codes

---

## 🚀 מה לעשות עכשיו

### שלב 1: דחוף את התיקונים

```powershell
git add .github/workflows/smoke-tests.yml
git commit -m "Fix smoke-tests.yml: Remove Windows-specific code for Linux runners"
git push origin chore/add-roy-tests
```

### שלב 2: הרץ שוב את ה-Workflow

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/actions/workflows/smoke-tests.yml
2. לחץ על "Run workflow"
3. בחר branch: `chore/add-roy-tests`
4. לחץ על "Run workflow"

---

## 📝 הערות

- ה-workflow עכשיו מיועד ל-Linux runners בלבד (`ubuntu-latest`)
- עבור self-hosted runners ב-Windows, צריך להוסיף תמיכה נפרדת
- ה-workflow כולל כעת:
  - הגדרת `PYTHONPATH` אוטומטית
  - בדיקת collection לפני הרצת הבדיקות
  - טיפול משופר בשגיאות עם הודעות ברורות
- Exit codes:
  - `0` = הצלחה
  - `1` = כשל בבדיקות
  - `2` = שגיאת collection/configuration (יודפס מידע נוסף)
  - `5` = אין בדיקות שנאספו (לא נכשל)

---

**עודכן לאחרונה:** 2025-11-19  
**Commit:** a3d83d0 - "Improve smoke-tests.yml: Add PYTHONPATH, test collection verification, and better error handling"

