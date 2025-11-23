# התקנת Runner - שלבים אחרונים

## אתה כבר הורדת את ה-runner! עכשיו:

### שלב 1: הגדרה (עם ה-token שקיבלת)

```bash
# על worker-node:
cd /opt/actions-runner

# הגדר עם ה-token מ-GitHub (החלף את ה-token):
sudo ./config.sh \
  --url https://github.com/PrismaPhotonics/panda-backend-api-tests \
  --token BXBPK45KXYLFHEJX22TGR7LJD5UX6 \
  --name staging-contract-tests-runner \
  --labels "self-hosted,Linux" \
  --work "_work" \
  --replace
```

**חשוב:** הוסף את ה-labels `self-hosted,Linux` כדי שה-workflow ימצא את ה-runner!

### שלב 2: התקן כשירות (מומלץ)

**לא להריץ `./run.sh`** - זה רק להרצה ידנית. במקום זה:

```bash
# התקן כשירות (ירוץ אוטומטית):
sudo ./svc.sh install

# התחל את השירות:
sudo ./svc.sh start

# בדוק סטטוס:
sudo ./svc.sh status
```

### שלב 3: בדיקה

```bash
# בדוק שה-runner online:
# לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners

# בדוק לוגים:
journalctl -u actions.runner.staging-contract-tests-runner.service -f
```

---

## Copy & Paste - הכל ביחד:

```bash
cd /opt/actions-runner

sudo ./config.sh \
  --url https://github.com/PrismaPhotonics/panda-backend-api-tests \
  --token BXBPK45KXYLFHEJX22TGR7LJD5UX6 \
  --name staging-contract-tests-runner \
  --labels "self-hosted,Linux" \
  --work "_work" \
  --replace

sudo ./svc.sh install
sudo ./svc.sh start
sudo ./svc.sh status
```

---

## ⚠️ חשוב:

- **לא להריץ `./run.sh`** - זה רק להרצה ידנית
- **השתמש ב-`svc.sh install`** - זה מתקין כשירות שירוץ אוטומטית
- **הוסף labels:** `self-hosted,Linux` - זה חשוב כדי שה-workflow ימצא את ה-runner

---

**אחרי זה, ה-runner יהיה online וה-contract tests ירוצו אוטומטית! 🚀**

