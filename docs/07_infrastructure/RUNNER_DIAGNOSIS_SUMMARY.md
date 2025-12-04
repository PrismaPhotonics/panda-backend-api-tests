# Runner Diagnosis Summary - panda_automation

**Date:** 2025-12-02  
**Workflow Run:** Smoke Tests #289  
**Issue:** PowerShell command not found

---

## 🔍 מה גילינו מהריצה

### מהריצה #289:

1. ✅ **Workflow התחיל** - זה אומר שה-runner `panda_automation` קיים ומחובר
2. ❌ **כל השלבים נכשלו** עם `powershell: command not found`
3. ⚠️ **זמן ריצה:** 28 שניות - נכשל מיד בתחילת הריצה

### מסקנות:

- ה-runner **קיים** (אחרת ה-workflow לא היה מתחיל)
- ה-runner **מחובר** (ה-workflow התחיל לרוץ)
- הבעיה: **PowerShell לא נמצא** על ה-runner

---

## 🎯 מה צריך לבדוק בדף ה-Runners

### שלב 1: גישה לדף

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
2. התחבר ל-GitHub

### שלב 2: מצא את ה-Runner

חפש runner בשם: **`panda_automation`**

### שלב 3: בדוק את הפרטים הבאים

| פרט | מה לבדוק | מה צריך |
|-----|----------|----------|
| **Status** | Online/Idle/Offline | ✅ Online או Idle |
| **OS** | Windows/Linux/macOS | ✅ Windows |
| **Labels** | רשימת כל ה-labels | ✅ `self-hosted`, `windows`, `panda_automation` |
| **PowerShell** | האם מותקן | ✅ צריך להיות זמין |

---

## 🔧 פתרונות אפשריים

### פתרון 1: Runner הוא Windows אבל PowerShell לא ב-PATH

**תיקון:**
1. על המחשב שבו ה-runner רץ, בדוק:
   ```powershell
   Get-Command powershell -ErrorAction SilentlyContinue
   ```
2. אם לא נמצא, נסה:
   ```powershell
   C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe --version
   ```
3. אם זה עובד, עדכן את ה-workflow להשתמש בנתיב המלא או התקן PowerShell Core

### פתרון 2: Runner הוא Linux

**תיקון:** עדכן את ה-workflow ל-`pwsh` (PowerShell Core):

```yaml
- name: Set up Python
  shell: pwsh  # Changed from powershell
  run: |
    # ... existing code ...
```

או שנה ל-`bash`:

```yaml
- name: Set up Python
  shell: bash
  run: |
    python3 --version
    # ... rewrite commands for bash ...
```

### פתרון 3: Labels לא נכונים

**תיקון:**
1. בדף ה-runner, לחץ **Edit**
2. ודא שה-labels הם:
   - `self-hosted`
   - `windows` (lowercase!)
   - `panda_automation`
3. לחץ **Save**

---

## 📋 Checklist לבדיקה

- [ ] Runner `panda_automation` קיים
- [ ] Status: Online/Idle
- [ ] OS: Windows
- [ ] Label `self-hosted` קיים
- [ ] Label `windows` קיים (lowercase!)
- [ ] Label `panda_automation` קיים
- [ ] PowerShell זמין על ה-runner

---

## 🔗 קישורים

- **Runners Page:** https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
- **Workflow Run #289:** https://github.com/PrismaPhotonics/panda-backend-api-tests/actions/runs/19851454352
- **Workflow File:** `.github/workflows/smoke-tests.yml`
- **Detailed Issue Report:** `docs/07_infrastructure/GITHUB_ACTIONS_RUNNER_POWERSHELL_ISSUE.md`

---

**Next Steps:** בדוק את הדף ה-runners ודווח מה מצאת, ואז נוכל לתקן את הבעיה.

