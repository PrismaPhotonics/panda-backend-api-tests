# התקנת Runner - URL מתוקן

## הבעיה:
ה-URL מחזיר HTML במקום קובץ tar.gz. צריך להשתמש ב-URL הנכון.

## פתרון - על worker-node:

```bash
# נקה
sudo rm -rf /opt/actions-runner
sudo mkdir -p /opt/actions-runner
cd /opt/actions-runner

# הורד את ה-runner עם URL נכון (ללא v לפני המספר):
sudo curl -L -o actions-runner.tar.gz https://github.com/actions/runner/releases/download/2.311.0/actions-runner-linux-x64-2.311.0.tar.gz

# או נסה את זה (latest):
sudo curl -L -o actions-runner.tar.gz https://github.com/actions/runner/releases/latest/download/actions-runner-linux-x64-2.311.0.tar.gz

# בדוק שהקובץ תקין:
file actions-runner.tar.gz
# צריך להראות: gzip compressed data

# אם עדיין HTML, נסה דרך API:
LATEST_VERSION=$(curl -s https://api.github.com/repos/actions/runner/releases/latest | grep '"tag_name":' | sed -E 's/.*"v([^"]+)".*/\1/')
echo "Latest version: $LATEST_VERSION"
sudo curl -L -o actions-runner.tar.gz "https://github.com/actions/runner/releases/download/v${LATEST_VERSION}/actions-runner-linux-x64-${LATEST_VERSION}.tar.gz"

# חלץ:
sudo tar xzf actions-runner.tar.gz
sudo rm actions-runner.tar.gz

# הגדר:
sudo ./config.sh \
  --url https://github.com/PrismaPhotonics/panda-backend-api-tests \
  --token <TOKEN_FROM_GITHUB> \
  --name staging-contract-tests-runner \
  --labels "self-hosted,Linux" \
  --replace

# התקן כשירות:
sudo ./svc.sh install
sudo ./svc.sh start

# בדוק:
sudo ./svc.sh status
```

---

## או: הורד ידנית דרך הדפדפן

1. לך ל: https://github.com/actions/runner/releases
2. מצא את הגרסה האחרונה (למשל v2.311.0)
3. הורד: `actions-runner-linux-x64-2.311.0.tar.gz`
4. העלה ל-worker-node:
   ```bash
   # דרך scp מהמחשב המקומי:
   scp actions-runner-linux-x64-2.311.0.tar.gz prisma@10.10.10.150:/tmp/
   
   # על worker-node:
   sudo mv /tmp/actions-runner-linux-x64-2.311.0.tar.gz /opt/actions-runner/
   cd /opt/actions-runner
   sudo tar xzf actions-runner-linux-x64-2.311.0.tar.gz
   ```

---

## Copy & Paste - נסה את זה:

```bash
cd /opt/actions-runner
sudo rm -f actions-runner.tar.gz

# נסה URL ללא v:
sudo curl -L -o actions-runner.tar.gz https://github.com/actions/runner/releases/download/2.311.0/actions-runner-linux-x64-2.311.0.tar.gz

# בדוק:
file actions-runner.tar.gz

# אם זה עדיין HTML, נסה latest:
sudo curl -L -o actions-runner.tar.gz https://github.com/actions/runner/releases/latest/download/actions-runner-linux-x64-2.311.0.tar.gz

# אם זה עדיין לא עובד, קבל גרסה דרך API:
LATEST=$(curl -s https://api.github.com/repos/actions/runner/releases/latest | grep -oP '"tag_name": "\K[^"]+' | head -1)
echo "Using version: $LATEST"
sudo curl -L -o actions-runner.tar.gz "https://github.com/actions/runner/releases/download/${LATEST}/actions-runner-linux-x64-${LATEST#v}.tar.gz"

# חלץ:
sudo tar xzf actions-runner.tar.gz
```

---

**נסה את ה-URL ללא `v` קודם - זה אמור לעבוד!**

