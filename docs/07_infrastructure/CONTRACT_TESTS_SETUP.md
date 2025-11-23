# הגדרת Contract Tests ב-GitHub Actions

## הבעיה

Contract tests צריכים גישה ל-Focus Server ב-`10.10.10.100` - זו כתובת IP פנימית ברשת המקומית.

**GitHub cloud runners (`ubuntu-latest`) לא יכולים לגשת לרשת הפנימית!**

## הפתרון

השתמש ב-**self-hosted runner** ברשת הפנימית.

---

## שלב 1: הגדרת Self-Hosted Linux Runner

### אוטומטי (מומלץ):

הרץ את הסקריפט על `worker-node` (10.10.10.150):

```bash
# SSH ל-worker-node
ssh prisma@10.10.10.150

# העתק את הסקריפט (או clone את ה-repo)
# הרץ:
sudo bash scripts/install_contract_tests_runner.sh
```

הסקריפט יעשה הכל אוטומטית:
- ✅ יוריד את ה-runner
- ✅ יתקין אותו
- ✅ יגדיר אותו עם ה-labels הנכונים
- ✅ יתקין אותו כשירות

### ידני:

אם אתה מעדיף לעשות זאת ידנית:

```bash
# על worker-node או מכונה אחרת ברשת הפנימית
cd /opt
sudo mkdir -p actions-runner
cd actions-runner

# הורד וחלץ
sudo curl -L -o actions-runner.tar.gz https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
sudo tar xzf actions-runner.tar.gz
sudo rm actions-runner.tar.gz

# הגדר (תצטרך token מ-GitHub)
sudo ./config.sh \
  --url https://github.com/PrismaPhotonics/panda-backend-api-tests \
  --token <TOKEN_FROM_GITHUB> \
  --name staging-contract-tests-runner \
  --labels "self-hosted,Linux" \
  --replace

# התקן כשירות
sudo ./svc.sh install
sudo ./svc.sh start
```

### בדיקה מהירה:

```bash
# בדוק שה-runner online
curl -k https://10.10.10.100/focus-server/channels

# בדוק סטטוס השירות
sudo systemctl status actions.runner.staging-contract-tests-runner.service
```

---

## שלב 2: הגדרת Secrets

ה-workflow משתמש ב-secrets הבאים (אופציונלי - יש defaults):

```bash
# ב-GitHub → Settings → Secrets → Actions:
FOCUS_SERVER_HOST = 10.10.10.100  # (default אם לא מוגדר)
FOCUS_SERVER_PORT = 443           # (default אם לא מוגדר)
FOCUS_API_PREFIX = /focus-server  # (default אם לא מוגדר)
VERIFY_SSL = false                # (default אם לא מוגדר)
REQUIRE_SERVER = true             # (default - הטסטים יכשלו אם אין שרת)
```

---

## שלב 3: הרצת הטסטים

### אוטומטי (על כל push/PR):
ה-workflow ירוץ אוטומטית על self-hosted runner.

### ידני:
1. לך ל-Actions → Contract Tests
2. לחץ "Run workflow"
3. בחר branch
4. `require_server`: `true` (default - יכשיל אם אין שרת)
5. לחץ "Run workflow"

---

## התנהגות

### אם יש שרת נגיש:
- ✅ הטסטים ירוצו
- ✅ יכשלו רק אם הטסטים עצמם נכשלים

### אם אין שרת נגיש:
- ❌ ה-workflow יכשל מיד עם הודעה ברורה
- ❌ הטסטים לא ירוצו

---

## פתרון בעיות

### בעיה: "Waiting for a runner to pick up this job..."

**פתרון:**
1. ודא שיש Linux self-hosted runner online
2. ודא שיש לו labels: `self-hosted`, `Linux`
3. בדוק שה-runner רץ: `sudo ./svc.sh status`

### בעיה: "Focus server unreachable"

**פתרון:**
1. ודא שה-runner ברשת הפנימית (יכול לגשת ל-`10.10.10.100`)
2. בדוק חיבור ידנית:
   ```bash
   curl -k https://10.10.10.100/focus-server/channels
   ```
3. אם זה לא עובד, ה-runner לא ברשת הפנימית

### בעיה: אין Linux runner

**פתרונות:**
1. הגדר Linux runner חדש (ראה שלב 1)
2. או שנה את ה-workflow להשתמש ב-Windows runner (אבל צריך להתאים את ה-scripts)

---

## סיכום

✅ **מה עשינו:**
1. שינינו את ה-workflow להשתמש ב-self-hosted Linux runner
2. הגדרנו `REQUIRE_SERVER=true` כברירת מחדל (הטסטים יכשלו אם אין שרת)
3. הוספנו הודעות שגיאה ברורות

✅ **מה צריך לעשות:**
1. להגדיר Linux self-hosted runner ברשת הפנימית
2. לוודא שהוא online ב-GitHub
3. להריץ את ה-workflow

---

**קובץ:** `.github/workflows/contract-tests.yml`

