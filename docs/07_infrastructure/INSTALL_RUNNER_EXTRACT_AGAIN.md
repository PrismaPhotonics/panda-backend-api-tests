# חילוץ מחדש של ה-runner

## הבעיה:
אין קובץ `svc.sh` - החילוץ לא הצליח.

## פתרון:

```bash
# בדוק מה יש בתיקייה:
ls -la /opt/actions-runner/

# אם יש קובץ tar.gz, חלץ שוב:
cd /opt/actions-runner
sudo rm -rf *  # נקה הכל

# הורד שוב:
sudo curl -L -o actions-runner.tar.gz "https://github.com/actions/runner/releases/download/v2.330.0/actions-runner-linux-x64-2.330.0.tar.gz"

# בדוק שהקובץ תקין:
file actions-runner.tar.gz
# צריך להראות: gzip compressed data

# חלץ (עכשיו בלי sudo כי שינית בעלות):
tar xzf actions-runner.tar.gz

# בדוק שיש svc.sh:
ls -la svc.sh

# אם יש, שנה בעלות:
sudo chown -R prisma:prisma /opt/actions-runner

# עכשיו הרץ הגדרה:
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

## Copy & Paste:

```bash
cd /opt/actions-runner
ls -la

# אם אין קבצים, נקה והורד שוב:
sudo rm -rf *
sudo curl -L -o actions-runner.tar.gz "https://github.com/actions/runner/releases/download/v2.330.0/actions-runner-linux-x64-2.330.0.tar.gz"
file actions-runner.tar.gz

# חלץ:
tar xzf actions-runner.tar.gz
rm actions-runner.tar.gz

# בדוק שיש svc.sh:
ls -la svc.sh

# שנה בעלות:
sudo chown -R prisma:prisma /opt/actions-runner

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

**הרץ את זה ובדוק מה יש בתיקייה קודם!**

