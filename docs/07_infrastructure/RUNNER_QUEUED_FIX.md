# פתרון: Workflows ב-Queued ולא מתחילים לרוץ

**בעיה:** Workflows ב-Queued עם "Waiting for a runner to pick up this job..."  
**סיבה:** ה-runner לא מזהה את ה-jobs כי ה-labels לא תואמים או ה-runner Offline

---

## 🔍 בדיקה מהירה

### 1. בדוק ב-GitHub את ה-Labels של ה-Runner

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
2. לחץ על ה-runner (PL5012)
3. בדוק את ה-Labels:
   - צריך להיות: `self-hosted`, `Windows`, `X64`
   - אם חסר label → לחץ על Edit והוסף אותו

---

### 2. בדוק שה-Runner Online

1. בדף ה-runner, בדוק את ה-Status:
   - ✅ **Online** (ירוק) = הכל תקין
   - ⚠️ **Offline** (אדום) = צריך לבדוק למה

---

### 3. בדוק את ה-Workflows

ה-workflows מחפשים runner עם labels:
```yaml
runs-on: [self-hosted, Windows, X64]
```

ה-runner צריך להיות עם כל ה-labels האלה.

---

## 🔧 פתרונות

### פתרון 1: עדכן את ה-Labels ב-GitHub

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
2. לחץ על ה-runner (PL5012)
3. לחץ על **Edit** (או על ה-gear icon ליד ה-labels)
4. ודא שה-labels הם:
   - `self-hosted`
   - `Windows`
   - `X64`
5. לחץ **Save**

---

### פתרון 2: ודא שה-Runner Online

אם ה-runner Offline:

1. ב-PowerShell שבו ה-runner רץ, ודא שאתה רואה:
   ```
   √ Connected to GitHub
   Listening for Jobs...
   ```

2. אם אתה לא רואה את זה:
   - עצור את ה-runner (Ctrl+C)
   - הרץ שוב: `.\run.cmd`

3. המתן 30-60 שניות
4. רענן את הדף ב-GitHub (F5)
5. בדוק שה-runner Online

---

### פתרון 3: Restart ה-Runner

1. ב-PowerShell שבו ה-runner רץ, לחץ **Ctrl+C** כדי לעצור
2. הרץ שוב:
   ```powershell
   cd C:\actions-runner
   .\run.cmd
   ```
3. המתן 30 שניות
4. נסה להריץ workflow שוב

---

## ✅ מה לעשות עכשיו

1. **בדוק את ה-Labels ב-GitHub:**
   - לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
   - לחץ על ה-runner
   - ודא שה-labels הם: `self-hosted`, `Windows`, `X64`

2. **ודא שה-Runner Online:**
   - בדוק את ה-Status ב-GitHub
   - אם Offline → Restart את ה-runner

3. **נסה להריץ Workflow שוב:**
   - לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
   - בחר: Smoke Tests
   - לחץ: Run workflow

---

## 💡 טיפ

אם ה-runner Online וה-labels נכונים אבל עדיין לא מזהה jobs:
- המתן 1-2 דקות
- רענן את הדף ב-GitHub
- נסה להריץ workflow שוב

---

**עודכן לאחרונה:** 2025-11-19

