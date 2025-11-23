# 🚀 התקנת Runner - הוראות שלב אחר שלב

## ⚠️ חשוב: אתה צריך להיות על Linux machine!

הפקודות האלה עובדות רק על **Linux** (worker-node), לא ב-Windows PowerShell!

---

## שלב 1: התחבר ל-worker-node

### דרך jump host:

```powershell
# ב-PowerShell שלך (Windows):
ssh root@10.10.10.10

# אחרי שהתחברת ל-jump host, הרץ:
ssh prisma@10.10.10.150
```

**עכשיו אתה על worker-node (Linux)!**

---

## שלב 2: על worker-node - בדוק שאתה שם

```bash
# בדוק שאתה על worker-node
hostname
# צריך להראות: worker-node

# בדוק גישה ל-Focus Server
curl -k https://10.10.10.100/focus-server/channels
# אם זה עובד - מושלם!
```

---

## שלב 3: התקן את ה-runner

### אפשרות A: עם סקריפט מהיר

```bash
# על worker-node (Linux):
curl -L -o /tmp/setup.sh https://raw.githubusercontent.com/PrismaPhotonics/panda-backend-api-tests/main/scripts/setup_runner_on_worker_node.sh
chmod +x /tmp/setup.sh
bash /tmp/setup.sh
```

### אפשרות B: Clone את ה-repo

```bash
# על worker-node (Linux):
git clone https://github.com/PrismaPhotonics/panda-backend-api-tests.git
cd panda-backend-api-tests
sudo bash scripts/install_contract_tests_runner.sh
```

---

## שלב 4: קבל Token מ-GitHub

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/new
2. בחר **Linux**
3. העתק את ה-token (תקף ל-1 שעה)
4. הדבק בסקריפט כשהוא שואל

---

## סיכום - Copy & Paste:

```bash
# 1. התחבר דרך jump host (ב-PowerShell):
ssh root@10.10.10.10
ssh prisma@10.10.10.150

# 2. על worker-node - הרץ:
curl -L -o /tmp/setup.sh https://raw.githubusercontent.com/PrismaPhotonics/panda-backend-api-tests/main/scripts/setup_runner_on_worker_node.sh
chmod +x /tmp/setup.sh
bash /tmp/setup.sh

# 3. הדבק את ה-token מ-GitHub כשהוא שואל
```

---

## ✅ אחרי ההתקנה:

- ה-runner יהיה online ב-GitHub
- Contract tests ירוצו אוטומטית על כל push/PR
- אם אין שרת נגיש → ה-workflow יכשל עם הודעה ברורה

---

**זכור: כל הפקודות האלה צריכות לרוץ על Linux (worker-node), לא ב-Windows PowerShell!**

