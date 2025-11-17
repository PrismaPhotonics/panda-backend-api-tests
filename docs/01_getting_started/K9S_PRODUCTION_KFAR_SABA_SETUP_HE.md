# 🔗 התחברות ל-K9s בסביבת כפר סבא (Production)

**תאריך:** 2025-11-02  
**מחבר:** Roy Avrahami  
**סביבה:** Production (כפר סבא)  
**IP:** 10.10.100.100

---

## 📋 סקירה כללית

סביבת כפר סבא היא סביבת ה-production עם הכתובת IP `10.10.100.100`.

**תשתית:**
- **Focus Server:** `https://10.10.100.100/focus-server/`
- **Frontend:** `https://10.10.100.100/liveView`
- **MongoDB:** `10.10.100.108:27017`
- **RabbitMQ:** `10.10.100.107:5672`
- **Kubernetes:** `10.10.100.102:6443`

---

## ✅ שלבים מהירים (Quick Start)

### 1️⃣ הגדרת SSH Agent עם המפתח

הרץ את ה-script הבא פעם אחת:

```powershell
.\scripts\setup_ssh_agent_production.ps1
```

זה יעשה:
- ✅ יוודא שה-SSH Agent שירות רץ
- ✅ יוסיף את `panda_production_key` ל-SSH Agent
- ✅ יוודא שהמפתח נטען כראוי

### 2️⃣ התחברות ל-K9s

#### אופציה A: דרך Script (מומלץ)

```powershell
.\scripts\utilities\connect_k9s.ps1 -Mode connect
```

#### אופציה B: ידנית

```powershell
# שלב 1: התחבר ל-jump host
ssh root@10.10.100.3
# Password: ask team lead

# שלב 2: מהשרת jump host, התחבר ל-target
ssh prisma@10.10.100.113

# שלב 3: הרץ k9s
k9s -n panda
```

---

## 🔧 הגדרות מפורטות

### SSH Config (`~/.ssh/config`)

הוספתי הגדרה חדשה:

```
Host production-k9s
    HostName 10.10.100.113
    User prisma
    Port 22
    IdentityFile ~/.ssh/panda_production_key
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 3
    StrictHostKeyChecking accept-new
    ForwardAgent yes
```

**הערה:** מכיוון שה-jump host דורש password, התחברות ידנית מומלצת יותר מ-ProxyJump.

---

## 📝 מה לעשות עכשיו

### שלב 1: ודא שהמפתח הציבורי נמצא בשרת

אם אתה מקבל "Permission denied (publickey)", הוסף את המפתח הציבורי לשרת:

```bash
# בשרת 10.10.100.113
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "ssh-ed25519 ... roy.avrahami@prismaphotonics.com" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

או השתמש ב-script:

```powershell
.\scripts\copy_ssh_key_to_target_v2.ps1 -Environment production
```

### שלב 2: בדוק שהחיבור עובד

```powershell
# התחבר ידנית ובדוק
ssh root@10.10.100.3
ssh prisma@10.10.100.113
k9s -n panda
```

---

## 🚨 פתרון בעיות (Troubleshooting)

### בעיה: עדיין מבקש public key

**פתרון:**
1. ודא שה-SSH Agent רץ:
   ```powershell
   Get-Service ssh-agent
   ```

2. ודא שהמפתח נטען:
   ```powershell
   ssh-add -l
   ```
   
   אם אתה רואה "The agent has no identities", טען מחדש:
   ```powershell
   .\scripts\setup_ssh_agent_production.ps1
   ```

3. ודא שהמפתח הציבורי נמצא בשרת:
   ```bash
   # בשרת 10.10.100.113
   cat ~/.ssh/authorized_keys
   ```

### בעיה: "Permission denied (publickey)"

**פתרון:**

1. **ודא שהמפתח הציבורי נמצא בשרת:**
   ```bash
   # בשרת 10.10.100.113
   cat ~/.ssh/authorized_keys
   ```
   
   אם המפתח לא שם, הוסף אותו:
   ```bash
   # Copy המפתח הציבורי מ-Windows
   # C:\Users\roy.avrahami\.ssh\panda_production_key.pub
   echo "ssh-ed25519 ... roy.avrahami@prismaphotonics.com" >> ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   chmod 700 ~/.ssh
   ```

2. **ודא הרשאות נכונות בשרת:**
   ```bash
   # בשרת 10.10.100.113
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/authorized_keys
   chown -R prisma:prisma ~/.ssh
   ```

---

## 📝 הפקודות הנפוצות

### התחברות ישירה ל-SSH

```powershell
# דרך jump host (ידנית)
ssh root@10.10.100.3
ssh prisma@10.10.100.113

# דרך SSH config alias (אם ProxyJump עובד)
ssh production-k9s
```

### בדיקת SSH Agent

```powershell
# רשימת מפתחות טעונים
ssh-add -l

# הוספת מפתח ידנית
ssh-add $env:USERPROFILE\.ssh\panda_production_key

# מחיקת מפתח מה-agent
ssh-add -d $env:USERPROFILE\.ssh\panda_production_key
```

### ניהול SSH Agent Service

```powershell
# בדיקת סטטוס
Get-Service ssh-agent

# הפעלה
Start-Service ssh-agent

# עצירה
Stop-Service ssh-agent

# הגדרת auto-start
Set-Service ssh-agent -StartupType Automatic
```

---

## 🎯 מה לעשות אחרי ההגדרה?

### שימוש יומיומי

1. **התחבר ל-K9s:**
   ```powershell
   .\scripts\utilities\connect_k9s.ps1 -Mode connect
   ```
   
   או ידנית:
   ```powershell
   ssh root@10.10.100.3
   ssh prisma@10.10.100.113
   k9s -n panda
   ```

### אחזקה

- **אחרי restart**: הרץ `.\scripts\setup_ssh_agent_production.ps1` שוב
- **לבדיקת חיבור**: התחבר ידנית דרך jump host

---

## 📦 קבצים שנוצרו

1. **`C:\Users\roy.avrahami\.ssh\config`** - עודכן עם הגדרה ל-`production-k9s`
2. **`scripts\setup_ssh_agent_production.ps1`** - Script להגדרת SSH Agent
3. **`docs\01_getting_started\K9S_PRODUCTION_KFAR_SABA_SETUP_HE.md`** - המדריך הזה

---

## ✅ סיכום

עכשיו יש לך:

- ✅ SSH Config מוגדר עם המפתח הנכון
- ✅ SSH Agent שומר את המפתח בזיכרון
- ✅ Scripts להתחברות מהירה
- ✅ תיעוד בעברית

**פשוט הרץ:**
```powershell
.\scripts\utilities\connect_k9s.ps1 -Mode connect
```

או ידנית:
```powershell
ssh root@10.10.100.3
ssh prisma@10.10.100.113
k9s -n panda
```

---

## 🔗 קישורים רלוונטיים

- [K9s Connection Guide](./K9S_CONNECTION_GUIDE.md)
- [SSH Jump Host Setup](./SSH_JUMP_HOST_SETUP.md)
- [Production Environment Guide](./NEW_PRODUCTION_ENVIRONMENT_COMPLETE_GUIDE.md)

---

**תאריך עדכון:** 2025-11-02  
**גרסה:** 1.0

