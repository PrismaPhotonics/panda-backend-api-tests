# צ'קליסט הגדרת Runner - מה לעשות בדף GitHub

**URL:** https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/22

---

## ✅ מה לבדוק ולעדכן בדף הזה

### 1. בדוק את ה-Status של ה-Runner

**מה לראות:**
- ✅ **Status:** `Online` (ירוק) - הכל תקין
- ⚠️ **Status:** `Offline` (אדום) - צריך לבדוק למה

**אם Offline:**
- בדוק שהשירות רץ על המחשב: `Get-Service actions.runner.*`
- בדוק את ה-logs: `C:\actions-runner\_diag\Runner_*.log`

---

### 2. בדוק את ה-Labels

**מה לראות:**
- Labels: `self-hosted`, `Windows`, `X64`

**מה צריך להוסיף:**
- Label: `panda-backend-lab` (אם חסר)

**איך להוסיף:**
1. לחץ על **"Edit"** (כפתור בצד ימין)
2. במקטע **"Labels"**, לחץ על **"Add label"**
3. הזן: `panda-backend-lab`
4. לחץ **"Save"**

---

### 3. בדוק את ה-Name

**מה לראות:**
- Name: `panda-backend-lab` (או שם אחר)

**אם השם לא נכון:**
1. לחץ על **"Edit"**
2. שנה את ה-Name ל-`panda-backend-lab`
3. לחץ **"Save"**

---

### 4. בדוק את ה-Runner Group

**מה לראות:**
- Runner Group: `Default` (או שם אחר)

**זה בסדר** - לא צריך לשנות כלום.

---

### 5. בדוק את ה-Work Folder

**מה לראות:**
- Work Folder: `_work` (או נתיב אחר)

**זה בסדר** - לא צריך לשנות כלום.

---

## 🔧 מה לעשות אם יש בעיות

### בעיה: Runner לא Online

**פתרון:**
```powershell
# על המחשב במעבדה
cd C:\actions-runner
Get-Service actions.runner.*
# אם השירות לא רץ:
.\svc\start.cmd
```

### בעיה: Labels לא נכונים

**פתרון:**
1. בדף GitHub, לחץ על **"Edit"**
2. עדכן את ה-Labels:
   - `self-hosted`
   - `Windows`
   - `X64`
   - `panda-backend-lab` (אם רוצה)
3. לחץ **"Save"**

### בעיה: Runner לא מזהה Jobs

**פתרון:**
1. וודא שה-runner Online
2. וודא שה-labels תואמים ל-workflow:
   - ה-workflow משתמש ב: `runs-on: [self-hosted, Windows]`
   - ה-runner צריך להיות עם labels: `self-hosted`, `Windows`
3. בדוק שה-workflow קיים ב-branch הנכון

---

## ✅ אחרי שסיימת

לאחר שבדקת ועדכנת את הכל:

1. **וודא שה-runner Online** ✅
2. **וודא שה-labels נכונים** ✅
3. **דחוף את ה-workflow ל-GitHub:**
   ```powershell
   cd C:\Projects\focus_server_automation
   git add .github/workflows/focus-backend-tests.yml
   git commit -m "Add Focus Server Backend Tests workflow"
   git push origin chore/add-roy-tests
   ```

4. **הרץ את ה-workflow לבדיקה:**
   - לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
   - בחר: **Focus Server Backend Tests (Lab)**
   - לחץ: **Run workflow**

---

**עודכן לאחרונה:** 2025-11-19

