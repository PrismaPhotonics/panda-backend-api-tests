# פתרון בעיה: Registration was not found or is not medium trust

**בעיה:** Runner לא יכול להתחבר ל-GitHub  
**סיבה:** ה-registration token פג או לא תקין  
**פתרון:** קבלת token חדש והגדרה מחדש

---

## 🔧 פתרון: הגדרה מחדש של Runner

### שלב 1: קבל Token חדש מ-GitHub

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/new
2. בחר: **Windows** ו-**x64**
3. תעתיק את ה-**token** ש-GitHub נותן לך (זה נראה כמו: `AXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`)

**או אם יש לך כבר runner:**
1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/21
2. לחץ על **...** (שלוש נקודות) → **Configure**
3. תעתיק את ה-token החדש

---

### שלב 2: הסר את ההגדרה הישנה

פתח **PowerShell** והרץ:

```powershell
cd C:\actions-runner

# עצור את ה-runner אם הוא רץ (לחץ Ctrl+C)
# או סגור את ה-PowerShell

# הסר את ההגדרה הישנה
.\config.cmd remove
```

כששואלים אותך:
- **Remove runner from server?** → לחץ **Y** (Yes)

---

### שלב 3: הגדר מחדש עם Token החדש

```powershell
cd C:\actions-runner

# הגדר מחדש (החלף את <YOUR_TOKEN> עם ה-token שקיבלת)
.\config.cmd --url https://github.com/PrismaPhotonics/panda-backend-api-tests --token <YOUR_TOKEN>
```

כששואלים אותך:
- **Enter name for this runner:** → לחץ **Enter** (להשאיר את השם הקיים: `PL5012`)
- **Enter labels:** → לחץ **Enter** (להשאיר את ה-labels הקיימים: `self-hosted,Windows,X64`)
- **Enter work folder:** → לחץ **Enter** (להשאיר את התיקייה הקיימת: `_work`)

---

### שלב 4: הרץ את ה-Runner

```powershell
cd C:\actions-runner

# הרץ את ה-runner
.\run.cmd
```

עכשיו אתה אמור לראות:
```
√ Connected to GitHub
Listening for Jobs...
```

**ללא שגיאות!**

---

## ✅ בדיקה: האם זה עובד?

### דרך 1: בדוק ב-GitHub

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/21
2. אחרי כמה שניות, ה-Status צריך להשתנות ל-**Online** (ירוק)

### דרך 2: הרץ Workflow לבדיקה

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
2. בחר: **Smoke Tests**
3. לחץ: **Run workflow**
4. ה-workflow צריך להתחיל לרוץ תוך כמה שניות

---

## ⚠️ אם עדיין יש בעיות

אם אחרי ההגדרה מחדש עדיין יש שגיאות:

1. **ודא שה-token תקין:**
   - ה-token צריך להיות ארוך (כ-40 תווים)
   - ה-token לא פג (GitHub נותן tokens שפוגים אחרי זמן מסוים)

2. **ודא שה-URL נכון:**
   - צריך להיות: `https://github.com/PrismaPhotonics/panda-backend-api-tests`

3. **בדוק את ה-logs:**
   ```powershell
   cd C:\actions-runner\_diag
   Get-ChildItem -Filter "Runner_*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Get-Content -Tail 50
   ```

---

**עודכן לאחרונה:** 2025-11-19

