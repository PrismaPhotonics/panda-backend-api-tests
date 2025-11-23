# בעיית רשת ב-Runner

## הבעיה:
ה-runner לא יכול לגשת ל-`10.10.10.100` מה-workflow, למרות שבדיקה ידנית עבדה.

## מה לבדוק:

### 1. בדוק שה-runner רץ תחת אותו משתמש שיכול לגשת:

```bash
# על worker-node:
# בדוק מי רץ את ה-runner:
ps aux | grep Runner.Listener

# בדוק network access מה-runner user:
sudo -u runner_user curl -k https://10.10.10.100/focus-server/channels
```

### 2. בדוק network routing:

```bash
# על worker-node:
# בדוק routing:
ip route get 10.10.10.100

# בדוק firewall:
sudo iptables -L -n | grep 10.10.10.100
# או:
sudo ufw status
```

### 3. בדוק שה-runner יכול לגשת:

```bash
# על worker-node, בתור המשתמש שרץ את ה-runner:
curl -k https://10.10.10.100/focus-server/channels
```

### 4. בדוק לוגים של ה-runner:

```bash
# על worker-node:
journalctl -u actions.runner.PrismaPhotonics-panda-backend-api-tests.staging-contract-tests-runner.service -f

# או:
cd /opt/actions-runner/_diag
ls -la
# בדוק את הלוגים שם
```

---

## פתרונות אפשריים:

### פתרון 1: וודא שה-runner רץ תחת prisma user

אם ה-runner רץ תחת משתמש אחר, הוא אולי לא יכול לגשת לרשת:

```bash
# בדוק את ה-service:
sudo systemctl cat actions.runner.PrismaPhotonics-panda-backend-api-tests.staging-contract-tests-runner.service

# אם צריך, שנה את ה-user:
sudo systemctl edit actions.runner.PrismaPhotonics-panda-backend-api-tests.staging-contract-tests-runner.service
# הוסף:
[Service]
User=prisma
Group=prisma
```

### פתרון 2: בדוק firewall rules

```bash
# אם יש firewall, פתח את הפורט:
sudo ufw allow from 10.10.10.0/24 to any port 443
```

### פתרון 3: בדוק network namespace

אם ה-runner רץ ב-container או network namespace שונה, הוא אולי לא יכול לגשת:

```bash
# בדוק network interfaces:
ip addr show

# בדוק routing:
ip route show
```

---

## Debugging מה-workflow:

ה-workflow עכשיו מדפיס:
- Hostname של ה-runner
- User שרץ את ה-workflow
- IP של ה-runner
- תוצאות ping ו-port check

זה יעזור להבין מה הבעיה.

---

**הרץ את ה-workflow שוב ותראה מה ה-debugging אומר!**

