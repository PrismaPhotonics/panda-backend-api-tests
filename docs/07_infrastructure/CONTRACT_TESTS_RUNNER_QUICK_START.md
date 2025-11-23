# 🚀 Contract Tests Runner - Quick Start

## מה צריך לעשות עכשיו:

### שלב 1: התחברות ל-worker-node

```bash
# דרך jump host (כמו שעשית קודם):
# 1. התחבר ל-jump host
ssh root@10.10.10.10

# 2. משם התחבר ל-worker-node
ssh prisma@10.10.10.150

# עכשיו אתה על worker-node!
```

### שלב 2: התקנת Runner

```bash
# על worker-node:

# 1. Clone את ה-repo (אם עדיין לא)
git clone https://github.com/PrismaPhotonics/panda-backend-api-tests.git
cd panda-backend-api-tests

# 2. העתק את הסקריפט (או clone ישירות)
# אם אין git, תוריד את הסקריפט ידנית:
curl -o /tmp/install_runner.sh https://raw.githubusercontent.com/PrismaPhotonics/panda-backend-api-tests/main/scripts/install_contract_tests_runner.sh

# 3. הרץ את הסקריפט
sudo bash /tmp/install_runner.sh
# או אם יש לך את ה-repo:
sudo bash scripts/install_contract_tests_runner.sh
```

הסקריפט יבקש ממך:
- **Registration Token** מ-GitHub (תקף ל-1 שעה)

### שלב 3: קבלת Token מ-GitHub

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/new
2. בחר **Linux**
3. העתק את ה-token
4. הדבק בסקריפט

### שלב 4: בדיקה

```bash
# בדוק שה-runner online ב-GitHub
# לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners

# בדוק שה-runner יכול לגשת ל-Focus Server
curl -k https://10.10.10.100/focus-server/channels

# בדוק סטטוס השירות
sudo systemctl status actions.runner.staging-contract-tests-runner.service
```

---

## ✅ אחרי ההתקנה:

ה-workflow `.github/workflows/contract-tests.yml` כבר מוגדר להשתמש ב-runner הזה!

**הטסטים ירוצו אוטומטית על כל push/PR.**

---

## 🔧 פתרון בעיות

### Runner לא מופיע ב-GitHub:
```bash
# בדוק שה-runner רץ
sudo systemctl status actions.runner.staging-contract-tests-runner.service

# אם לא רץ, התחל אותו
sudo systemctl start actions.runner.staging-contract-tests-runner.service

# בדוק לוגים
journalctl -u actions.runner.staging-contract-tests-runner.service -f
```

### Runner לא יכול לגשת לשרת:
```bash
# בדוק חיבור
curl -k https://10.10.10.100/focus-server/channels

# אם זה לא עובד, ה-runner לא ברשת הפנימית
```

### Labels לא נכונים:
1. לך ל-GitHub → Settings → Actions → Runners
2. לחץ על ה-runner
3. לחץ Edit
4. ודא שיש: `self-hosted`, `Linux`

---

## 📝 קבצים חשובים:

- **סקריפט התקנה:** `scripts/install_contract_tests_runner.sh`
- **Workflow:** `.github/workflows/contract-tests.yml`
- **מדריך מפורט:** `docs/07_infrastructure/CONTRACT_TESTS_SETUP.md`

---

**מוכן? הרץ את הסקריפט! 🚀**

