# הגדרת Self-Hosted Runner (לוקלי עם VPN)
## Setup Self-Hosted Runner (Local with VPN)

**תאריך:** 2025-11-09  
**מטרה:** להריץ GitHub Actions על המחשב שלך עם VPN

---

## 🎯 למה צריך את זה

- ✅ החיבורים לסביבה דורשים VPN
- ✅ ה-VPN רץ על המחשב שלך
- ✅ GitHub-hosted runners לא יכולים לגשת ל-VPN שלך
- ✅ צריך self-hosted runner על המחשב שלך

---

## 📋 שלב 1: הורדת GitHub Actions Runner

### Windows:

1. **לך ל-GitHub Repository:**
   ```
   https://github.com/PrismaPhotonics/panda-backend-api-tests
   ```

2. **Settings → Actions → Runners:**
   - לחץ על **"New self-hosted runner"**
   - בחר **Windows** (או **Linux** אם אתה על Linux)

3. **הורד את ה-Runner:**
   - GitHub ייתן לך הוראות
   - או הורד ישירות:
     - **Windows x64:** https://github.com/actions/runner/releases/latest/download/actions-runner-win-x64-2.311.0.zip
     - **Linux x64:** https://github.com/actions/runner/releases/latest/download/actions-runner-linux-x64-2.311.0.zip

---

## 📋 שלב 2: התקנה

### Windows:

1. **פתח PowerShell כמנהל (Run as Administrator)**

2. **צור תיקייה:**
   ```powershell
   mkdir C:\actions-runner
   cd C:\actions-runner
   ```

3. **חלץ את ה-ZIP:**
   ```powershell
   # הורד את ה-runner (אם לא הורדת)
   Invoke-WebRequest -Uri https://github.com/actions/runner/releases/latest/download/actions-runner-win-x64-2.311.0.zip -OutFile actions-runner-win-x64-2.311.0.zip
   
   # חלץ
   Expand-Archive -Path actions-runner-win-x64-2.311.0.zip -DestinationPath .
   ```

4. **הרץ את ההתקנה:**
   ```powershell
   .\config.cmd --url https://github.com/PrismaPhotonics/panda-backend-api-tests --token YOUR_TOKEN
   ```
   
   **איפה להשיג את ה-Token:**
   - GitHub → Repository → Settings → Actions → Runners → New self-hosted runner
   - GitHub ייתן לך token (תוקף לכמה דקות)

5. **בחר אפשרויות:**
   ```
   Enter the name of the runner: [Enter] (default: שם המחשב)
   Enter the name of the work folder: [Enter] (default: _work)
   Enter additional labels: [Enter] (אופציונלי)
   ```

### Linux:

1. **צור תיקייה:**
   ```bash
   mkdir actions-runner && cd actions-runner
   ```

2. **הורד וחלץ:**
   ```bash
   curl -o actions-runner-linux-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/latest/download/actions-runner-linux-x64-2.311.0.tar.gz
   tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz
   ```

3. **הרץ את ההתקנה:**
   ```bash
   ./config.sh --url https://github.com/PrismaPhotonics/panda-backend-api-tests --token YOUR_TOKEN
   ```

---

## 📋 שלב 3: הרצה

### Windows:

```powershell
# הרץ את ה-runner
.\run.cmd
```

### Linux:

```bash
# הרץ את ה-runner
./run.sh
```

**הערה:** ה-runner צריך לרוץ כל הזמן. אפשר להגדיר אותו כ-service (ראה למטה).

---

## 📋 שלב 4: הגדרה כ-Service (אופציונלי אבל מומלץ)

### Windows:

```powershell
# התקן כ-service
.\svc.cmd install

# התחל את ה-service
.\svc.cmd start

# בדוק סטטוס
.\svc.cmd status
```

### Linux:

```bash
# התקן כ-service
sudo ./svc.sh install

# התחל את ה-service
sudo ./svc.sh start

# בדוק סטטוס
sudo ./svc.sh status
```

---

## 📋 שלב 5: עדכון ה-Workflow

ה-workflow כבר מוכן! קובץ: `.github/workflows/tests_simple_local.yml`

**השינוי העיקרי:**
```yaml
runs-on: self-hosted  # במקום ubuntu-latest
```

---

## ✅ בדיקה

1. **ודא שה-runner רץ:**
   - לך ל-GitHub → Repository → Settings → Actions → Runners
   - אתה אמור לראות את ה-runner שלך עם סטטוס "Idle" או "Online"

2. **הרץ את ה-Workflow:**
   - לך ל-Actions → "Tests - Simple (Local Runner with VPN)"
   - לחץ "Run workflow"
   - בחר branch והרץ

3. **ראה את התוצאות:**
   - ה-workflow ירוץ על המחשב שלך
   - תראה את הלוגים ב-GitHub Actions
   - ה-VPN שלך יהיה זמין לטסטים

---

## 🔧 פתרון בעיות

### בעיה: "Runner לא מופיע ב-GitHub"

**פתרון:**
1. ודא שה-runner רץ (`.\run.cmd` או `./run.sh`)
2. בדוק שה-token תקין
3. בדוק חיבור לאינטרנט

### בעיה: "Workflow לא רץ על ה-runner"

**פתרון:**
1. ודא שה-workflow משתמש ב-`runs-on: self-hosted`
2. בדוק שה-runner online ב-GitHub
3. בדוק labels (אם הוספת)

### בעיה: "VPN לא עובד"

**פתרון:**
1. ודא שה-VPN רץ לפני הרצת ה-workflow
2. בדוק שה-runner רץ תחת אותו משתמש שיש לו VPN
3. נסה להריץ טסט ידנית (ללא GitHub Actions) כדי לוודא שה-VPN עובד

---

## 📝 דרישות

### לפני התקנה:

- [ ] Python 3.12 מותקן
- [ ] Git מותקן
- [ ] VPN מותקן ופועל
- [ ] חיבור לאינטרנט
- [ ] הרשאות מנהל (להתקנת service)

### אחרי התקנה:

- [ ] Runner רץ ו-online ב-GitHub
- [ ] VPN פועל
- [ ] Workflow רץ בהצלחה

---

## 🎯 סיכום

**מה עשינו:**
1. ✅ הורדנו GitHub Actions Runner
2. ✅ התקנו אותו על המחשב שלך
3. ✅ הגדרנו אותו כ-service (אופציונלי)
4. ✅ עדכנו את ה-workflow לעבוד עם self-hosted runner

**מה זה נותן:**
- ✅ ה-workflow רץ על המחשב שלך
- ✅ יש גישה ל-VPN
- ✅ יכול להתחבר לסביבה
- ✅ הכל אוטומטי

---

**עודכן:** 2025-11-09

