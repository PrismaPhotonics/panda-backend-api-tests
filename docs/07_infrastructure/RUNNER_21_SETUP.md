# הגדרת Runner 21 (PL5012) - מדריך

**Runner ID:** 21  
**Runner Name:** PL5012  
**Status:** Active ✅  
**Labels:** `self-hosted`, `Windows`, `X64`  
**URL:** https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/21

---

## ✅ מה כבר מוכן

- ✅ Runner מותקן ו-Active
- ✅ Labels נכונים: `self-hosted`, `Windows`, `X64`
- ✅ Workflow מעודכן לעבוד עם ה-runner הזה

---

## 🔧 מה לבדוק

### 1. וודא שה-Runner Active

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/21
2. בדוק שה-Status הוא **Active** (ירוק/כתום)

### 2. בדוק את ה-Labels

**Labels צריכים להיות:**
- `self-hosted`
- `Windows`
- `X64`

**אם צריך להוסיף label נוסף:**
1. לחץ על **"Edit"**
2. במקטע **"Labels"**, לחץ על **"Add label"**
3. הזן את ה-label הרצוי
4. לחץ **"Save"**

---

## 📝 ה-Workflow

ה-workflow `.github/workflows/focus-backend-tests.yml` כבר מוגדר לעבוד עם ה-runner הזה:

```yaml
runs-on: [self-hosted, Windows]
```

זה יתאים ל-runner `PL5012` כי יש לו את ה-labels: `self-hosted`, `Windows`.

---

## 🚀 הרצת ה-Workflow

### דרך GitHub UI:

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
2. בחר: **Focus Server Backend Tests (Lab)**
3. לחץ: **Run workflow**
4. בחר branch: `chore/add-roy-tests` (או `main`)
5. לחץ: **Run workflow**

### דרך Git Push:

```powershell
# כל push ל-main/develop/master יגרום ל-workflow לרוץ אוטומטית
git push origin chore/add-roy-tests
```

---

## 🔍 בדיקת תוצאות

לאחר שהעבודה רצה:

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
2. לחץ על ה-run הרלוונטי
3. בדוק:
   - שה-runner מזוהה: `PL5012`
   - שה-tests רצים
   - שה-reports נוצרים

---

## 🔧 פתרון בעיות

### בעיה: Runner לא מזהה Jobs

**פתרון:**
1. וודא שה-runner Active ב-GitHub
2. וודא שה-labels תואמים:
   - Workflow משתמש ב: `runs-on: [self-hosted, Windows]`
   - Runner צריך להיות עם: `self-hosted`, `Windows`
3. בדוק שה-workflow קיים ב-branch הנכון

### בעיה: Runner לא Active

**פתרון:**
1. בדוק שהשירות רץ על המחשב:
   ```powershell
   Get-Service actions.runner.*
   ```
2. אם השירות לא רץ, התחל אותו:
   ```powershell
   cd C:\actions-runner
   .\svc\start.cmd
   ```

---

## ✅ Checklist

- [ ] Runner Active ב-GitHub
- [ ] Labels נכונים: `self-hosted`, `Windows`, `X64`
- [ ] Workflow נדחף ל-GitHub
- [ ] בדיקה ידנית של workflow דרך GitHub UI

---

**עודכן לאחרונה:** 2025-11-19

