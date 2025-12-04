# למה זה קרה פתאום? - ניתוח הבעיה

**תאריך:** 2025-12-02  
**בעיה:** Workflow נכשל עם `powershell: command not found`  
**שאלה:** למה אתמול זה עבד והיום לא?

---

## 🔍 מה גילינו

### Commit האחרון (8e6a24c - 2025-12-02 08:18:53):

**הודעה:** "Convert test result handling to Python script"

**מה השתנה:**
- השלב "Fail workflow if tests failed" שונה מ-PowerShell ל-Python script
- נוצר קובץ `check_test_failures.py`
- **אבל:** השלב הזה **חסר `shell:`** - משתמש ב-default shell

---

## 🎯 למה זה קרה פתאום?

### תרחיש 1: Runner השתנה (הכי סביר) ⚠️

**מה קרה:**
1. אתמול: Runner היה Windows עם PowerShell מותקן
2. היום: Runner הוחלף/עודכן/הוסר PowerShell

**איך זה קרה:**
- Runner `panda_automation` הוחלף ב-runner אחר (Linux?)
- Runner עודכן וה-PowerShell הוסר
- Runner הוסר מה-labels `windows`

**איך לבדוק:**
1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
2. בדוק את ה-runner `panda_automation`:
   - מה ה-OS שלו? (Windows/Linux)
   - מה ה-Labels שלו?
   - מה ה-Status שלו?

---

### תרחיש 2: PowerShell הוסר מה-Runner

**מה קרה:**
- Runner עדיין Windows
- אבל PowerShell הוסר מה-PATH או הוסר מהמערכת

**איך זה קרה:**
- Windows Update הסיר PowerShell
- PATH השתנה
- PowerShell Core הותקן במקום PowerShell Desktop

**איך לבדוק:**
- בדוק על ה-runner אם PowerShell קיים:
  ```powershell
  Get-Command powershell -ErrorAction SilentlyContinue
  ```

---

### תרחיש 3: Labels השתנו

**מה קרה:**
- ה-label `windows` הוסר או השתנה ל-`Windows` (case-sensitive!)
- GitHub Actions לא מזהה את ה-runner כ-Windows

**איך זה קרה:**
- מישהו עדכן את ה-labels
- Runner הוסר והוסף מחדש עם labels שונים

**איך לבדוק:**
- בדוק את ה-labels של ה-runner:
  - צריך להיות: `self-hosted`, `windows` (lowercase!), `panda_automation`

---

## 📊 השוואה: אתמול vs היום

### אתמול (עבד):

```yaml
- name: Fail workflow if tests failed
  if: always()
  shell: powershell  # ✅ היה מוגדר
  env:
    RUN_TESTS_OUTCOME: ${{ steps.run-smoke-tests.outcome }}
  run: |
    # PowerShell code here...
```

### היום (נכשל):

```yaml
- name: Fail workflow if tests failed
  if: always()
  # ❌ אין shell: - משתמש ב-default
  env:
    RUN_TESTS_OUTCOME: ${{ steps.run-smoke-tests.outcome }}
  run: py check_test_failures.py  # Python script
```

**הבעיה:**
- כל השלבים האחרים עדיין משתמשים ב-`shell: powershell`
- אם PowerShell לא זמין, כל השלבים נכשלים

---

## 🔧 מה צריך לתקן

### תיקון 1: הוסף `shell:` לשלב האחרון

```yaml
- name: Fail workflow if tests failed
  if: always()
  shell: powershell  # ✅ הוסף את זה
  env:
    RUN_TESTS_OUTCOME: ${{ steps.run-smoke-tests.outcome }}
  run: py check_test_failures.py
```

**או** אם ה-runner הוא Linux:

```yaml
- name: Fail workflow if tests failed
  if: always()
  shell: bash  # ✅ אם Linux
  env:
    RUN_TESTS_OUTCOME: ${{ steps.run-smoke-tests.outcome }}
  run: python3 check_test_failures.py
```

---

### תיקון 2: שנה את כל השלבים ל-`pwsh`

**הכי בטוח:** שנה את כל `shell: powershell` ל-`shell: pwsh`:

```yaml
- name: Set up Python
  shell: pwsh  # ✅ PowerShell Core (עובד גם ב-Linux)
  run: |
    # ... existing code ...
```

**יתרונות:**
- עובד ב-Windows, Linux, macOS
- יותר מודרני
- טוב יותר ל-CI/CD

---

### תיקון 3: הוסף זיהוי Shell אוטומטי

```yaml
- name: Detect Shell
  id: detect-shell
  run: |
    if command -v pwsh &> /dev/null; then
      echo "shell=pwsh" >> $GITHUB_OUTPUT
    elif command -v powershell &> /dev/null; then
      echo "shell=powershell" >> $GITHUB_OUTPUT
    else
      echo "shell=bash" >> $GITHUB_OUTPUT
    fi

- name: Set up Python
  shell: ${{ steps.detect-shell.outputs.shell }}
  run: |
    # ... existing code ...
```

---

## 📋 Checklist לבדיקה

- [ ] בדוק את ה-runner `panda_automation` ב-GitHub
- [ ] בדוק מה ה-OS שלו (Windows/Linux)
- [ ] בדוק מה ה-Labels שלו (`self-hosted`, `windows`, `panda_automation`)
- [ ] בדוק מה ה-Status שלו (Online/Offline)
- [ ] בדוק אם PowerShell זמין על ה-runner
- [ ] בדוק את ה-commits האחרונים - מה השתנה

---

## 🎯 סיכום

**למה זה קרה:**
1. ✅ Commit אחרון שינה את השלב האחרון ל-Python (זה בסדר)
2. ❌ אבל כל השלבים האחרים עדיין משתמשים ב-`shell: powershell`
3. ❌ ה-runner כנראה השתנה/עודכן/הוחלף
4. ❌ PowerShell לא זמין יותר על ה-runner

**מה לעשות:**
1. ✅ בדוק את ה-runner ב-GitHub
2. ✅ תקן את השלב האחרון (הוסף `shell:`)
3. ✅ שנה את כל השלבים ל-`pwsh` (הכי בטוח)
4. ✅ או הוסף זיהוי shell אוטומטי

---

**Next Steps:** בואו נתקן את ה-workflow עכשיו!

