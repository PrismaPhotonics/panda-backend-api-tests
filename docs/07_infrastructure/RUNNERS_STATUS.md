# מצב Runners - GitHub Actions

**תאריך בדיקה:** 2025-01-23  
**Repository:** https://github.com/PrismaPhotonics/panda-backend-api-tests

---

## 📊 סיכום Runners

### Runner 21 (PL5012)
- **ID:** 21
- **Name:** PL5012
- **Status:** Active ✅ (לפי תיעוד)
- **Labels:** `self-hosted`, `Windows`, `X64`
- **URL:** https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/21
- **תואם ל-Workflows:** ✅ כן (כל ה-workflows משתמשים ב-`runs-on: [self-hosted, Windows]`)

### Runner 22
- **ID:** 22
- **Name:** panda-backend-lab (לפי תיעוד)
- **Status:** לא ידוע (צריך לבדוק)
- **Labels:** `self-hosted`, `Windows`, `X64` (לפי תיעוד)
- **URL:** https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/22
- **תואם ל-Workflows:** ✅ כן

---

## 🔍 Workflows שצריכים Runners

כל ה-workflows הבאים משתמשים ב-`runs-on: [self-hosted, Windows]`:

1. **Smoke Tests** (`.github/workflows/smoke-tests.yml`)
   - Timeout: 15 דקות
   - Triggers: `push`, `pull_request`, `workflow_dispatch`

2. **Regression Tests** (`.github/workflows/regression-tests.yml`)
   - Timeout: 60 דקות
   - Triggers: `push`, `pull_request`, `schedule` (23:00 UTC), `workflow_dispatch`

3. **Load and Performance Tests** (`.github/workflows/load-performance-tests.yml`)
   - Timeout: 120 דקות
   - Triggers: `schedule` (02:00 UTC), `workflow_dispatch`

---

## ✅ מה לבדוק עכשיו

### 1. בדוק את מצב ה-Runners ב-GitHub

**דרך 1: דרך GitHub UI**
1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
2. בדוק את ה-Status של כל runner:
   - ✅ **Online** (ירוק) = הכל תקין
   - ⚠️ **Offline** (אדום) = צריך לבדוק למה
   - ⚠️ **Idle** (כתום) = ממתין ל-jobs

**דרך 2: דרך Actions Tab**
1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
2. לחץ על **"Runners"** בתפריט השמאלי (תחת "Management")
3. תראה את כל ה-runners הזמינים

### 2. בדוק את ה-Labels

**Labels שצריכים להיות:**
- `self-hosted` (חובה)
- `Windows` (חובה)
- `X64` (מומלץ)

**איך לבדוק:**
1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
2. לחץ על runner ספציפי
3. בדוק את ה-Labels

### 3. בדוק את ה-Workflows האחרונים

**לבדוק:**
1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
2. בדוק את ה-runs האחרונים:
   - האם הם ב-**Queued**? (ממתין ל-runner)
   - האם הם ב-**In Progress**? (רץ על runner)
   - האם הם **Completed**? (הסתיים בהצלחה)

---

## 🔧 פתרון בעיות נפוצות

### בעיה: Workflows ב-Queued ולא מתחילים

**סיבות אפשריות:**
1. אין runner Online עם ה-labels הנכונים
2. ה-runner Offline
3. ה-labels לא תואמים

**פתרון:**
1. בדוק שה-runner Online: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
2. בדוק שה-labels נכונים: `self-hosted`, `Windows`
3. אם ה-runner Offline, התחל אותו על המחשב:
   ```powershell
   cd C:\actions-runner
   Get-Service actions.runner.*
   # אם השירות לא רץ:
   .\svc\start.cmd
   ```

### בעיה: Runner לא מזהה Jobs

**סיבות אפשריות:**
1. ה-labels לא תואמים
2. ה-runner Offline
3. ה-workflow לא קיים ב-branch הנכון

**פתרון:**
1. ודא שה-runner Online
2. ודא שה-labels תואמים:
   - Workflow משתמש ב: `runs-on: [self-hosted, Windows]`
   - Runner צריך להיות עם: `self-hosted`, `Windows`
3. ודא שה-workflow קיים ב-branch הנכון (`chore/add-roy-tests` או `main`)

### בעיה: Runner Offline

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
3. המתן 30-60 שניות
4. רענן את הדף ב-GitHub (F5)
5. בדוק שה-runner Online

---

## 📝 Checklist לבדיקה

- [ ] Runner 21 (PL5012) Online ב-GitHub
- [ ] Runner 22 Online ב-GitHub (אם קיים)
- [ ] Labels נכונים: `self-hosted`, `Windows`, `X64`
- [ ] Workflows האחרונים רצים בהצלחה
- [ ] אין workflows תקועים ב-Queued

---

## 🔗 קישורים שימושיים

- **Runners Settings:** https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
- **Actions:** https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
- **Runner 21:** https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/21
- **Runner 22:** https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/22

---

**עודכן לאחרונה:** 2025-01-23

