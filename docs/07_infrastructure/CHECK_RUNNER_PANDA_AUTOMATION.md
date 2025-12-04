# בדיקת Runner: panda_automation

**Workflow:** `.github/workflows/smoke-tests.yml`  
**Required Labels:** `self-hosted`, `windows`, `panda_automation`  
**Issue:** PowerShell command not found

---

## 🔍 מה לבדוק בדף ה-Runners

### שלב 1: גישה לדף ה-Runners

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
2. **התחבר ל-GitHub** אם נדרש

---

### שלב 2: מצא את ה-Runner `panda_automation`

בדף ה-Runners, חפש runner בשם **`panda_automation`**.

**אם לא מוצא:**
- ❌ ה-runner לא קיים → צריך ליצור אותו
- ❌ ה-runner קיים אבל עם שם אחר → צריך לשנות את ה-workflow או את שם ה-runner

---

### שלב 3: בדוק את ה-Status

**Status אפשריים:**
- ✅ **Online** (ירוק) = Runner פעיל ומחובר
- ⚠️ **Idle** (כתום) = Runner ממתין ל-jobs
- ❌ **Offline** (אדום) = Runner לא מחובר

**מה צריך:** ✅ **Online** או ⚠️ **Idle**

---

### שלב 4: בדוק את ה-Labels

**Labels שצריכים להיות:**
1. ✅ `self-hosted` (חובה)
2. ✅ `windows` (חובה - case-sensitive!)
3. ✅ `panda_automation` (חובה)

**⚠️ חשוב:** ה-label `windows` חייב להיות **lowercase** (`windows`) ולא `Windows`!

**איך לבדוק:**
- בדף ה-runner, תראה רשימת Labels
- ודא שכל ה-3 Labels קיימים

**אם חסר label:**
1. לחץ על **Edit** (או על ה-gear icon)
2. לחץ **Add label**
3. הזן את ה-label החסר
4. לחץ **Save**

---

### שלב 5: בדוק את ה-OS

**OS שצריך להיות:** **Windows**

**איך לבדוק:**
- בדף ה-runner, תראה את ה-OS (Windows/Linux/macOS)
- אם זה Linux/macOS → זה הבעיה! ה-runner צריך להיות Windows

---

### שלב 6: בדוק את ה-PowerShell

**אם ה-runner הוא Windows:**
- PowerShell צריך להיות מותקן
- בדרך כלל ב: `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`

**אם ה-runner הוא Linux:**
- צריך PowerShell Core (`pwsh`)
- או לשנות את ה-workflow ל-`bash`

---

## 📋 טבלת בדיקה

| בדיקה | מה צריך | מה לבדוק |
|-------|---------|----------|
| **Runner קיים** | ✅ כן | האם יש runner בשם `panda_automation`? |
| **Status** | ✅ Online/Idle | מה ה-Status של ה-runner? |
| **Label: self-hosted** | ✅ כן | האם יש label `self-hosted`? |
| **Label: windows** | ✅ כן (lowercase!) | האם יש label `windows` (לא `Windows`)? |
| **Label: panda_automation** | ✅ כן | האם יש label `panda_automation`? |
| **OS** | ✅ Windows | מה ה-OS של ה-runner? |
| **PowerShell** | ✅ מותקן | האם PowerShell זמין? |

---

## 🔧 פתרונות לפי מצב

### מצב 1: Runner לא קיים

**פתרון:** צריך ליצור runner חדש

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/new
2. בחר **Windows** ו-**x64**
3. הורד והתקן את ה-runner עם השם `panda_automation`
4. הוסף את ה-labels: `self-hosted`, `windows`, `panda_automation`

**מדריך מפורט:** ראה `docs/07_infrastructure/github_actions_local_and_self_hosted.md`

---

### מצב 2: Runner קיים אבל Labels לא נכונים

**פתרון:** עדכן את ה-Labels

1. לחץ על ה-runner `panda_automation`
2. לחץ **Edit**
3. ודא שה-labels הם:
   - `self-hosted`
   - `windows` (lowercase!)
   - `panda_automation`
4. לחץ **Save**

---

### מצב 3: Runner הוא Linux במקום Windows

**פתרון 1:** שנה את ה-workflow ל-`pwsh` (PowerShell Core)

עדכן את `.github/workflows/smoke-tests.yml`:
```yaml
- name: Set up Python
  shell: pwsh  # Changed from powershell
  run: |
    # ... existing code ...
```

**פתרון 2:** שנה את ה-workflow ל-`bash`

עדכן את כל השלבים ל-`shell: bash` וכתוב מחדש את הפקודות.

---

### מצב 4: Runner הוא Windows אבל PowerShell לא נמצא

**פתרון 1:** התקן PowerShell Core

```powershell
# On the runner machine
winget install Microsoft.PowerShell
```

ואז שנה את ה-workflow ל-`shell: pwsh`

**פתרון 2:** ודא ש-PowerShell ב-PATH

```powershell
# On the runner machine
$env:PATH -split ';' | Select-String -Pattern "PowerShell"
# Should show: C:\Windows\System32\WindowsPowerShell\v1.0
```

---

### מצב 5: Runner Offline

**פתרון:** התחל את ה-runner

**אם ה-runner רץ כשירות:**
```powershell
# On the runner machine
Get-Service actions.runner.*
# If stopped:
Start-Service actions.runner.*
```

**אם ה-runner רץ ידנית:**
```powershell
# On the runner machine
cd C:\actions-runner
.\run.cmd
```

---

## 📝 מה לדווח

אחרי הבדיקה, דווח:

1. ✅ **Runner קיים?** (כן/לא)
2. ✅ **Status?** (Online/Idle/Offline)
3. ✅ **Labels?** (רשימת כל ה-labels)
4. ✅ **OS?** (Windows/Linux/macOS)
5. ✅ **PowerShell זמין?** (כן/לא)

---

## 🔗 קישורים שימושיים

- **Runners Page:** https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
- **Create New Runner:** https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/new
- **Workflow File:** `.github/workflows/smoke-tests.yml`
- **Runner Setup Guide:** `docs/07_infrastructure/github_actions_local_and_self_hosted.md`

---

**Generated:** 2025-12-02  
**Purpose:** Checklist for checking `panda_automation` runner configuration

