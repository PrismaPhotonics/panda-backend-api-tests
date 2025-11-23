# ✅ התקנת Runner - המשך

## שלב 1: הורדה - ✅ הושלם!

ה-runner הורד בהצלחה (גרסה v2.330.0).

## שלב 2: הגדרה

עכשיו צריך להגדיר את ה-runner עם token מ-GitHub:

```bash
# על worker-node:
cd /opt/actions-runner

# קבל token מ-GitHub:
# 1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/new
# 2. בחר "Linux"
# 3. העתק את ה-token

# הגדר את ה-runner (החלף <TOKEN> ב-token שקיבלת):
sudo ./config.sh \
  --url https://github.com/PrismaPhotonics/panda-backend-api-tests \
  --token <TOKEN_FROM_GITHUB> \
  --name staging-contract-tests-runner \
  --labels "self-hosted,Linux" \
  --work "_work" \
  --replace
```

## שלב 3: התקנה כשירות

```bash
# התקן כשירות:
sudo ./svc.sh install

# התחל את השירות:
sudo ./svc.sh start

# בדוק סטטוס:
sudo ./svc.sh status
```

## שלב 4: בדיקה

```bash
# בדוק שה-runner online ב-GitHub:
# לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners

# בדוק לוגים:
journalctl -u actions.runner.staging-contract-tests-runner.service -f
```

---

## Copy & Paste - הכל ביחד:

```bash
cd /opt/actions-runner

# קבל token מ-GitHub קודם!
# https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/new

sudo ./config.sh \
  --url https://github.com/PrismaPhotonics/panda-backend-api-tests \
  --token <TOKEN_FROM_GITHUB> \
  --name staging-contract-tests-runner \
  --labels "self-hosted,Linux" \
  --work "_work" \
  --replace

sudo ./svc.sh install
sudo ./svc.sh start
sudo ./svc.sh status
```

---

**עכשיו רק צריך token מ-GitHub והכל מוכן! 🚀**

