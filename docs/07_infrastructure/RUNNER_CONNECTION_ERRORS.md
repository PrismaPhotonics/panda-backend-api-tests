# פתרון: בעיות חיבור Runner ל-GitHub

**תאריך:** 2025-01-23  
**Runner:** PL5012  
**בעיות שזוהו:**
- `System.Net.Sockets.SocketException (11001): No such host is known`
- `Socket Error: ConnectionReset`
- ניסיון להתחבר ל-`https://broker.actions.githubusercontent.com` נכשל

---

## 🚨 הבעיות שזוהו

### בעיה 1: DNS Resolution Failed
```
System.Net.Sockets.SocketException (11001): No such host is known.
```

**משמעות:** המחשב לא יכול לפתור את שם ה-host `broker.actions.githubusercontent.com`

### בעיה 2: Connection Reset
```
Socket Error: ConnectionReset
```

**משמעות:** החיבור נקטע לפני שהתחבר

---

## ✅ פתרונות

### פתרון 1: בדוק חיבור לאינטרנט

```powershell
# בדוק חיבור בסיסי
Test-NetConnection -ComputerName github.com -Port 443

# בדוק DNS
Resolve-DnsName broker.actions.githubusercontent.com
```

**אם זה נכשל:**
- בדוק את החיבור לאינטרנט
- בדוק אם יש VPN שצריך להתחבר
- בדוק אם יש proxy שצריך להגדיר

---

### פתרון 2: בדוק Firewall

```powershell
# בדוק אם Windows Firewall חוסם
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*GitHub*" -or $_.DisplayName -like "*Actions*"}
```

**אם יש חוקים חוסמים:**
- פתח את ה-ports הנדרשים:
  - HTTPS (443) ל-`*.githubusercontent.com`
  - HTTPS (443) ל-`*.github.com`

---

### פתרון 3: בדוק Proxy Settings

אם אתה מאחורי proxy:

```powershell
# בדוק הגדרות proxy
[System.Net.WebRequest]::GetSystemWebProxy()

# הגדר proxy ל-runner (אם נדרש)
cd C:\actions-runner
.\config.cmd --proxyurl http://proxy-server:port --proxyusername user --proxypassword pass
```

---

### פתרון 4: בדוק DNS

```powershell
# נסה לפתור את ה-DNS
nslookup broker.actions.githubusercontent.com

# אם זה נכשל, נסה עם DNS אחר:
# Google DNS: 8.8.8.8
# Cloudflare DNS: 1.1.1.1
```

**לשנות DNS:**
1. פתח **Network Settings**
2. לחץ על ה-connection שלך
3. לחץ על **Properties**
4. בחר **Internet Protocol Version 4 (TCP/IPv4)**
5. לחץ **Properties**
6. בחר **Use the following DNS server addresses**
7. הזן: `8.8.8.8` ו-`8.8.4.4` (Google DNS)

---

### פתרון 5: Restart ה-Runner עם Debug Mode

```powershell
cd C:\actions-runner

# עצור את ה-service
Stop-Service actions.runner.*

# הרץ ישירות עם debug logging
.\run.cmd --debug
```

זה יראה יותר פרטים על מה קורה.

---

### פתרון 6: בדוק אם יש VPN/Network Issues

```powershell
# בדוק את ה-network interfaces
Get-NetIPAddress | Where-Object {$_.AddressFamily -eq 'IPv4'}

# בדוק את ה-routing table
Get-NetRoute | Where-Object {$_.DestinationPrefix -eq '0.0.0.0/0'}
```

---

## 🔍 בדיקה מהירה

**הרץ את הפקודות הבאות:**

```powershell
# 1. בדוק חיבור ל-GitHub
Test-NetConnection -ComputerName github.com -Port 443

# 2. בדוק DNS
Resolve-DnsName broker.actions.githubusercontent.com

# 3. בדוק חיבור ישיר
Invoke-WebRequest -Uri "https://github.com" -UseBasicParsing
```

**אם כל זה עובד:**
- הבעיה ספציפית ל-runner
- נסה restart (פתרון 5)

**אם זה לא עובד:**
- בעיית חיבור לאינטרנט/DNS
- בדוק proxy/VPN/firewall

---

## 💡 המלצה

**התחל עם:**
1. ✅ בדוק חיבור לאינטרנט (פתרון 1)
2. ✅ בדוק DNS (פתרון 4)
3. ✅ בדוק firewall (פתרון 2)

**אם כל זה תקין:**
- נסה restart עם debug mode (פתרון 5)

---

## 🔗 קישורים שימושיים

- **GitHub Actions Runner Requirements:** https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/about-self-hosted-runners#network-requirements
- **Runner Troubleshooting:** https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/troubleshooting

---

**עודכן לאחרונה:** 2025-01-23

