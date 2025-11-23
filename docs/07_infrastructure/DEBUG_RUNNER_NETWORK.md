# Debugging Runner Network Access

## מה רואים:

1. ✅ Runner רץ תחת `prisma` user - טוב
2. ⚠️ `curl -k https://10.10.10.100/focus-server/channels` לא החזיר כלום
3. ✅ Runner מחובר ל-GitHub ומאזין ל-jobs

## בדיקות נוספות:

### 1. בדוק שה-curl באמת עובד:

```bash
# על worker-node:
curl -k https://10.10.10.100/focus-server/channels
# צריך להחזיר: {"lowest_channel":1,"highest_channel":2337}

# אם זה לא עובד, נסה:
curl -v -k https://10.10.10.100/focus-server/channels 2>&1 | head -20
```

### 2. בדוק network connectivity:

```bash
# Ping test:
ping -c 3 10.10.10.100

# Port check:
timeout 3 bash -c "echo > /dev/tcp/10.10.10.100/443" && echo "Port 443 is open" || echo "Port 443 is closed"

# DNS check:
nslookup 10.10.10.100
```

### 3. בדוק מה ה-workflow רואה:

הרץ את ה-workflow שוב - ה-debugging החדש יראה:
- Hostname של ה-runner
- User שרץ את ה-workflow  
- IP של ה-runner
- תוצאות ping ו-port check

---

## פתרון אפשרי:

אם ה-curl לא עובד, אולי יש בעיית network או firewall. נסה:

```bash
# בדוק firewall:
sudo iptables -L -n | grep 10.10.10.100
sudo ufw status

# בדוק routing:
ip route get 10.10.10.100

# בדוק network interfaces:
ip addr show | grep -A 2 "eth0\|ens"
```

---

**הרץ את ה-workflow שוב ותראה מה ה-debugging אומר!**

