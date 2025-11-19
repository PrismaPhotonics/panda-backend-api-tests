# מדריך הגדרת GitHub Actions ל-panda-backend-api-tests

**תאריך:** 2025-11-19  
**Repository:** https://github.com/PrismaPhotonics/panda-backend-api-tests

---

## 📋 סקירה כללית

יצרנו שני workflows:

1. **`backend-tests-lab.yml`** - ל-self-hosted Windows runner במעבדה (גישה ל-K8s, MongoDB, RabbitMQ)
2. **`backend-tests-github.yml`** - ל-GitHub-hosted runner (ubuntu-latest) לבדיקות שלא דורשות VPN

---

## 🚀 שלב 1: הגדרת Self-Hosted Runner במעבדה

### 1.1 התקנת GitHub Runner על Windows 11 Pro

1. **כנס ל-GitHub Repository:**
   - לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/new
   - בחר **Windows** ו-**x64**

2. **הורד והתקן את ה-Runner:**
   ```powershell
   # צור תיקייה עבור ה-runner
   mkdir C:\actions-runner
   cd C:\actions-runner
   
   # הורד את ה-runner (החלף את ה-URL עם מה ש-GitHub נותן לך)
   Invoke-WebRequest -Uri https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-win-x64-2.311.0.zip -OutFile actions-runner-win-x64-2.311.0.zip
   
   # חלץ את ה-zip
   Expand-Archive -Path actions-runner-win-x64-2.311.0.zip -DestinationPath .
   
   # הגדר את ה-runner (החלף את ה-token עם מה ש-GitHub נותן לך)
   .\config.cmd --url https://github.com/PrismaPhotonics/panda-backend-api-tests --token <YOUR_TOKEN>
   ```

3. **במהלך ההגדרה, הגדר Labels:**
   ```
   Enter name for this runner: panda-backend-lab
   Enter labels (comma-separated): self-hosted,Windows,panda-backend-lab
   ```

4. **הרץ את ה-Runner כשירות:**
   ```powershell
   # התקן כשירות Windows
   .\svc\install.cmd
   
   # התחל את השירות
   .\svc\start.cmd
   ```

### 1.2 וידוא שה-Runner רץ

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
2. תראה את ה-runner עם status **Idle** (ירוק)

---

## 🔐 שלב 2: הגדרת GitHub Secrets

ה-workflows משתמשים ב-secrets הבאים. הגדר אותם ב-GitHub:

1. **לך ל:** https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/secrets/actions
2. **הוסף את ה-Secrets הבאים:**

   | Secret Name | Description | Example |
   |------------|-------------|---------|
   | `FOCUS_BASE_URL` | Base URL של Focus Server | `https://10.10.10.100` |
   | `FOCUS_API_PREFIX` | API prefix (אופציונלי) | `/focus-server` |
   | `VERIFY_SSL` | האם לוודא SSL (אופציונלי) | `false` |

---

## 📝 שלב 3: מבנה ה-Workflows

### 3.1 `backend-tests-lab.yml` (Self-Hosted Windows Runner)

**מטרה:** בדיקות שדורשות גישה ל-K8s, MongoDB, RabbitMQ במעבדה

**Triggers:**
- `push` ל-`main`, `develop`, `master`, `chore/add-roy-tests`
- `pull_request` ל-`main`
- `workflow_dispatch` (ידני) עם בחירת test suite
- `schedule` - כל לילה ב-23:00 UTC

**Test Suites:**
- **smoke** - בדיקות smoke ו-high priority
- **regression** - בדיקות regression (ללא slow/nightly)
- **nightly** - כל הבדיקות כולל slow/load/stress עם pod monitoring
- **all** - כל הבדיקות

**Runner Labels:**
```yaml
runs-on: [self-hosted, Windows, panda-backend-lab]
```

### 3.2 `backend-tests-github.yml` (GitHub-Hosted Runner)

**מטרה:** בדיקות שלא דורשות גישה ל-K8s/VPN

**Triggers:**
- `push` ל-`main`, `develop`, `master`, `chore/add-roy-tests`
- `pull_request` ל-`main`
- `workflow_dispatch` (ידני) עם בחירת test suite

**Test Suites:**
- **smoke** - בדיקות smoke ו-high priority
- **regression** - בדיקות regression (ללא slow/nightly)

**Runner:**
```yaml
runs-on: ubuntu-latest
```

---

## 🎯 שלב 4: הרצת Workflows

### דרך GitHub UI:

1. **לך ל:** https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
2. **בחר workflow:**
   - `Focus Server Backend Tests (Lab Runner)` - לבדיקות במעבדה
   - `Focus Server Backend Tests (GitHub Runner)` - לבדיקות ב-GitHub
3. **לחץ על "Run workflow"**
4. **בחר:**
   - **Branch:** `main` (או branch אחר)
   - **Test suite:** `smoke`, `regression`, `nightly`, או `all`
5. **לחץ על "Run workflow"**

### דרך Git Push:

```bash
# כל push ל-main/develop/master יגרום ל-workflow לרוץ אוטומטית
git push origin main
```

---

## 📊 שלב 5: צפייה בתוצאות

### בדיקת תוצאות:

1. **לך ל:** https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
2. **לחץ על ה-run הרלוונטי**
3. **צפה ב-logs:**
   - כל step מציג את ה-output שלו
   - אם יש כשלים, תראה את ה-error messages

### הורדת דוחות:

1. **בדף ה-run**, גלול למטה ל-**Artifacts**
2. **לחץ על ה-artifact** (למשל: `test-reports-smoke`)
3. **הורד את ה-zip** ופתח אותו
4. **פתח את ה-HTML report** בדפדפן

---

## 🔧 פתרון בעיות

### Runner לא מופיע ב-GitHub:

1. **וודא שה-runner רץ:**
   ```powershell
   # בדוק את סטטוס השירות
   Get-Service actions.runner.*
   ```

2. **בדוק את ה-logs:**
   ```powershell
   # ה-logs נמצאים ב:
   C:\actions-runner\_diag\Runner_*.log
   ```

### Workflow לא רץ:

1. **וודא שה-workflow קיים ב-branch הנכון:**
   - ה-workflow חייב להיות ב-`main` (או ב-branch שאתה דוחף אליו)

2. **וודא שה-path filters נכונים:**
   - ה-workflow רץ רק אם יש שינויים ב-paths שמוגדרים

### Tests נכשלים:

1. **בדוק את ה-logs** של ה-step שנכשל
2. **וודא שה-secrets מוגדרים נכון**
3. **וודא שה-Focus Server זמין** (אם זה נדרש)

---

## 📝 הערות חשובות

1. **Self-Hosted Runner:**
   - חייב להיות מחובר לרשת שיכולה לגשת ל-K8s/MongoDB/RabbitMQ
   - אם צריך VPN, וודא שה-VPN פעיל על המחשב
   - ה-runner רץ ברקע כשירות Windows

2. **GitHub-Hosted Runner:**
   - לא יכול לגשת ל-resources פנימיים (K8s, MongoDB וכו')
   - טוב לבדיקות שלא דורשות גישה פנימית
   - רץ על `ubuntu-latest` (Linux)

3. **Test Suites:**
   - **smoke** - מהיר, רץ על כל push/PR
   - **regression** - מקיף יותר, רץ לפני merge
   - **nightly** - כל הבדיקות, רץ בלילה או ידנית
   - **all** - כל הבדיקות ללא סינון

---

## ✅ Checklist להגדרה

- [ ] Self-hosted runner מותקן על Windows 11 Pro במעבדה
- [ ] Runner מופיע ב-GitHub עם labels נכונים
- [ ] GitHub Secrets מוגדרים (FOCUS_BASE_URL וכו')
- [ ] Workflows קיימים ב-`.github/workflows/`
- [ ] Workflows נדחפו ל-`main` branch
- [ ] בדיקה ידנית של workflow דרך GitHub UI
- [ ] בדיקה של push/PR trigger

---

**עודכן לאחרונה:** 2025-11-19

