# הגדרת Focus Server Backend Tests - צ'קליסט

**תאריך:** 2025-11-19  
**Repository:** https://github.com/PrismaPhotonics/panda-backend-api-tests  
**Workflow:** `.github/workflows/focus-backend-tests.yml`

---

## ✅ צ'קליסט להגדרה

### שלב 1: הגדרת Self-Hosted Runner במעבדה

- [ ] **כנס ל-GitHub:**
  - לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/new
  - בחר: **OS: Windows**, **Architecture: x64**

- [ ] **על הלפטופ במעבדה (Windows 11 Pro):**
  - פתח **PowerShell כ-Run as Administrator**
  - הרץ את הפקודות ש-GitHub נתן לך:
    ```powershell
    # הורד והתקן את ה-runner
    mkdir C:\actions-runner
    cd C:\actions-runner
    # ... (המשך לפי ההוראות מ-GitHub)
    ```

- [ ] **הגדר Labels:**
  - בעת ההגדרה, הגדר את ה-labels הבאים:
    - `self-hosted`
    - `Windows`
    - `panda-backend-lab`

- [ ] **וודא שה-Runner Online:**
  - לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
  - תראה את ה-runner עם status **Online** (ירוק)

---

### שלב 2: יצירת קובץ ה-Workflow

- [ ] **וודא שהקובץ קיים:**
  - `.github/workflows/focus-backend-tests.yml`
  - הקובץ כבר נוצר עם התוכן הנכון ✅

- [ ] **וודא שה-branches נכונים:**
  - הקובץ כולל: `main`, `chore/add-roy-tests`
  - אם צריך לשנות - עדכן את השורה:
    ```yaml
    branches: [ main, chore/add-roy-tests ]
    ```

- [ ] **וודא שה-cron נכון:**
  - כרגע: `0 23 * * *` (23:00 UTC = 01:00 בלילה בארץ בחורף)
  - אם צריך לשנות - עדכן את השורה:
    ```yaml
    - cron: "0 23 * * *"
    ```

---

### שלב 3: בדיקה ידנית ראשונה

- [ ] **דחוף את ה-Workflow ל-GitHub:**
  ```powershell
  git add .github/workflows/focus-backend-tests.yml
  git commit -m "Add Focus Server Backend Tests workflow for lab runner"
  git push origin chore/add-roy-tests
  ```

- [ ] **הרץ את ה-Workflow ידנית:**
  1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
  2. בחר workflow: **Focus Server Backend Tests (Lab)**
  3. לחץ על **"Run workflow"**
  4. בחר branch: `chore/add-roy-tests` (או `main`)
  5. לחץ על **"Run workflow"**

- [ ] **וודא שה-Workflow רץ:**
  - ה-runner מזוהה: ✅
  - Checkout עובד: ✅
  - Python מוגדר: ✅
  - Dependencies מותקנים: ✅
  - Tests רצים: ✅
  - JUnit report נוצר: ✅
  - Artifact מועלה: ✅

---

### שלב 4: טוויקים אחרי הריצה הראשונה

- [ ] **אם יש בעיות עם ENV:**
  - הוסף secrets ב-GitHub:
    - לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/secrets/actions
    - הוסף: `FOCUS_BASE_URL`, `FOCUS_API_PREFIX`, `VERIFY_SSL`
  - עדכן את ה-workflow:
    ```yaml
    env:
      FOCUS_BASE_URL: ${{ secrets.FOCUS_BASE_URL }}
      FOCUS_API_PREFIX: ${{ secrets.FOCUS_API_PREFIX || '/focus-server' }}
      VERIFY_SSL: ${{ secrets.VERIFY_SSL || 'false' }}
    ```

- [ ] **אם יש בעיות עם גישה ל-K8s/MongoDB:**
  - וודא שה-VPN פעיל על הלפטופ במעבדה
  - וודא שה-runner רץ על המחשב הנכון
  - בדוק את ה-logs של ה-runner:
    ```
    C:\actions-runner\_diag\Runner_*.log
    ```

- [ ] **אם צריך לשנות את ה-Markers:**
  - כרגע: `smoke or high` (על push/PR)
  - כרגע: כל הבדיקות (על schedule/workflow_dispatch)
  - אם צריך לשנות - עדכן את השורות:
    ```yaml
    -m "smoke or high"  # או מה שאתה צריך
    ```

---

## 📋 מה ה-Workflow עושה

### על Push / Pull Request:
- מריץ: `pytest be_focus_server_tests/integration/api -m "smoke or high" -v`
- יוצר: `reports/junit-smoke.xml`
- מעלה artifact: `junit-report`

### על Schedule (לילה) / Workflow Dispatch (ידני):
- מריץ: `pytest be_focus_server_tests/ --monitor-pods -v`
- יוצר: `reports/junit-report.xml`
- מעלה artifact: `junit-report`

---

## 🔧 פתרון בעיות

### Runner לא מופיע:
- וודא שה-runner רץ: `Get-Service actions.runner.*`
- בדוק את ה-logs: `C:\actions-runner\_diag\Runner_*.log`

### Workflow לא רץ:
- וודא שה-workflow קיים ב-branch הנכון
- וודא שה-path filters נכונים (רק שינויים ב-`be_focus_server_tests/**` וכו')

### Tests נכשלים:
- בדוק את ה-logs של ה-step שנכשל
- וודא שה-dependencies מותקנים נכון
- וודא שה-Focus Server זמין (אם נדרש)

---

## 📝 הערות

- ה-workflow רץ על **self-hosted Windows runner** במעבדה
- דורש גישה ל-K8s, MongoDB, RabbitMQ (דרך VPN/LAN)
- Python 3.12
- Dependencies מ-`requirements.txt`

---

**עודכן לאחרונה:** 2025-11-19

