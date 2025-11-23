# תיקון בעיות הרשאות

## הבעיה:
התיקייה `/opt/actions-runner` שייכת ל-root, אבל צריך להריץ את `config.sh` בלי sudo.

## פתרון:

### אפשרות 1: שנה בעלות על התיקייה (מומלץ)

```bash
# שנה בעלות על התיקייה למשתמש prisma:
sudo chown -R prisma:prisma /opt/actions-runner

# עכשיו הרץ בלי sudo:
cd /opt/actions-runner
./config.sh \
  --url https://github.com/PrismaPhotonics/panda-backend-api-tests \
  --token BXBPK45KXYLFHEJX22TGR7LJD5UX6 \
  --name staging-contract-tests-runner \
  --labels "self-hosted,Linux" \
  --work "_work" \
  --replace

# אחרי זה, התקן כשירות (כאן כן צריך sudo):
sudo ./svc.sh install
sudo ./svc.sh start
sudo ./svc.sh status
```

### אפשרות 2: התקן בתיקיית הבית

```bash
# צור תיקייה בתיקיית הבית:
cd ~
mkdir -p actions-runner
cd actions-runner

# הורד שוב (או העתק מה-/opt):
curl -L -o actions-runner.tar.gz "https://github.com/actions/runner/releases/download/v2.330.0/actions-runner-linux-x64-2.330.0.tar.gz"
tar xzf actions-runner.tar.gz
rm actions-runner.tar.gz

# הגדר:
./config.sh \
  --url https://github.com/PrismaPhotonics/panda-backend-api-tests \
  --token BXBPK45KXYLFHEJX22TGR7LJD5UX6 \
  --name staging-contract-tests-runner \
  --labels "self-hosted,Linux" \
  --work "_work" \
  --replace

# התקן כשירות:
sudo ./svc.sh install
sudo ./svc.sh start
sudo ./svc.sh status
```

---

## Copy & Paste - פתרון מהיר:

```bash
# שנה בעלות:
sudo chown -R prisma:prisma /opt/actions-runner

# הרץ הגדרה:
cd /opt/actions-runner
./config.sh \
  --url https://github.com/PrismaPhotonics/panda-backend-api-tests \
  --token BXBPK45KXYLFHEJX22TGR7LJD5UX6 \
  --name staging-contract-tests-runner \
  --labels "self-hosted,Linux" \
  --work "_work" \
  --replace

# התקן כשירות:
sudo ./svc.sh install
sudo ./svc.sh start
sudo ./svc.sh status
```

---

**נסה את אפשרות 1 קודם - זה הכי פשוט!**

