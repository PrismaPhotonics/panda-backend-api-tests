# מדריך הגדרת SSH קבוע ל-K9s דרך 10.10.10.150

**תאריך:** 2025-11-02  
**מחבר:** Roy Avrahami  
**מטרה:** הגדרת חיבור SSH אוטומטי ללא הזנת סיסמה לחיבור ל-K9s דרך 10.10.10.150

---

## 📋 סקירה כללית

המדריך הזה מסביר איך להגדיר חיבור SSH קבוע ל-10.10.10.150 כך שלא תצטרך להזין public key בכל פעם שאתה רוצה להתחבר ל-k9s.

---

## ✅ שלבים מהירים (Quick Start)

### 1️⃣ הגדרת SSH Agent עם המפתח

הרץ את ה-script הבא פעם אחת:

```powershell
.\scripts\setup_ssh_agent_vm150.ps1
```

זה יעשה:
- ✅ יוודא שה-SSH Agent שירות רץ
- ✅ יוסיף את `vm_150_key` ל-SSH Agent
- ✅ יוודא שהמפתח נטען כראוי

### 2️⃣ בדיקת החיבור

בדוק שהחיבור עובד ללא הזנת סיסמה:

```powershell
.\scripts\connect_k9s_vm150.ps1 -Action test
```

### 3️⃣ התחברות ל-K9s

התחבר ל-K9s:

```powershell
.\scripts\connect_k9s_vm150.ps1 -Action connect
```

או ישירות:

```powershell
ssh vm-150
k9s
```

---

## 🔧 הגדרות מפורטות

### מה השתנה?

#### 1. SSH Config (`~/.ssh/config`)

הוספתי הגדרה חדשה:

```
Host vm-150
    HostName 10.10.10.150
    User prisma
    Port 22
    IdentityFile ~/.ssh/vm_150_key
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 3
    StrictHostKeyChecking accept-new
    ForwardAgent yes
```

**איך זה עוזר:**
- ✅ `IdentityFile` - מציין את המפתח הנכון
- ✅ `IdentitiesOnly yes` - משתמש רק במפתח הזה (לא מנסה מפתחות אחרים)
- ✅ `ServerAliveInterval` - שומר על החיבור חי
- ✅ `ForwardAgent yes` - מאפשר SSH agent forwarding (לחיבורים נוספים)

#### 2. SSH Agent Setup

ה-SSH Agent שומר את המפתח בזיכרון כך שלא תצטרך להזין אותו בכל פעם.

**איך זה עובד:**
1. SSH Agent הוא שירות Windows שרץ ברקע
2. המפתח נטען לזיכרון של ה-agent
3. כאשר אתה מתחבר ל-SSH, הוא משתמש במפתח מה-agent אוטומטית

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
   .\scripts\setup_ssh_agent_vm150.ps1
   ```

3. ודא שהמפתח הציבורי נמצא בשרת:
   - התחבר לשרת (עם סיסמה פעם אחת)
   - ודא שהקובץ `~/.ssh/authorized_keys` מכיל את המפתח הציבורי שלך

### בעיה: "Permission denied (publickey)"

**פתרון:**

1. **ודא שהמפתח הציבורי נמצא בשרת:**
   ```bash
   # בשרת 10.10.10.150
   cat ~/.ssh/authorized_keys
   ```
   
   אם המפתח לא שם, הוסף אותו:
   ```bash
   # Copy the public key from Windows
   echo "ssh-rsa AAAAB3...root@vm1" >> ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   chmod 700 ~/.ssh
   ```

2. **ודא הרשאות נכונות בשרת:**
   ```bash
   # בשרת 10.10.10.150
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/authorized_keys
   chown -R prisma:prisma ~/.ssh
   ```

### בעיה: SSH Agent לא שומר את המפתח אחרי restart

**פתרון:**

ה-SSH Agent שומר מפתחות רק בזמן שהוא רץ. כדי לטעון מחדש אוטומטית:

1. **צור Task Scheduler**:
   ```powershell
   $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File `"C:\Projects\focus_server_automation\scripts\setup_ssh_agent_vm150.ps1`""
   $trigger = New-ScheduledTaskTrigger -AtLogOn
   Register-ScheduledTask -TaskName "SSH Agent vm150 Setup" -Action $action -Trigger $trigger
   ```

2. **או הוסף ל-startup script** (פשוט יותר):
   - לחץ `Win+R`
   - הזן `shell:startup`
   - צור קיצור דרך ל-`setup_ssh_agent_vm150.ps1`

### בעיה: חיבור נקטע

**פתרון:**

הגדרות `ServerAliveInterval` ו-`ServerAliveCountMax` ב-SSH config אמורות לעזור, אבל אם זה עדיין קורה:

1. בדוק את ה-firewall:
   ```powershell
   Test-NetConnection 10.10.10.150 -Port 22
   ```

2. ודא שה-SSH server מקבל חיבורים:
   ```bash
   # בשרת
   sudo systemctl status ssh
   ```

---

## 📝 הפקודות הנפוצות

### התחברות ישירה ל-SSH

```powershell
# דרך SSH config alias (מומלץ)
ssh vm-150

# ישירות עם כתובת IP
ssh prisma@10.10.10.150
```

### בדיקת SSH Agent

```powershell
# רשימת מפתחות טעונים
ssh-add -l

# הוספת מפתח ידנית
ssh-add $env:USERPROFILE\.ssh\vm_150_key

# מחיקת מפתח מה-agent
ssh-add -d $env:USERPROFILE\.ssh\vm_150_key
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
   ssh vm-150
   k9s
   ```

2. **או השתמש ב-script:**
   ```powershell
   .\scripts\connect_k9s_vm150.ps1
   ```

### אחזקה

- **אחרי restart**: הרץ `.\scripts\setup_ssh_agent_vm150.ps1` שוב
- **לבדיקת חיבור**: הרץ `.\scripts\connect_k9s_vm150.ps1 -Action test`

---

## 📦 קבצים שנוצרו

1. **`C:\Users\roy.avrahami\.ssh\config`** - עודכן עם הגדרה ל-`vm-150`
2. **`scripts\setup_ssh_agent_vm150.ps1`** - Script להגדרת SSH Agent
3. **`scripts\connect_k9s_vm150.ps1`** - Script מהיר להתחברות ל-K9s
4. **`docs\01_getting_started\K9S_SSH_SETUP_VM150_HE.md`** - המדריך הזה

---

## ✅ סיכום

עכשיו יש לך:

- ✅ SSH Config מוגדר עם המפתח הנכון
- ✅ SSH Agent שומר את המפתח בזיכרון
- ✅ חיבור אוטומטי ללא הזנת סיסמה
- ✅ Scripts מהירים להתחברות

**פשוט הרץ:**
```powershell
ssh vm-150
k9s
```

וזה אמור לעבוד ללא הזנת סיסמה! 🎉

---

## 🔗 קישורים רלוונטיים

- [SSH Jump Host Setup](./SSH_JUMP_HOST_SETUP.md)
- [K9s Connection Guide](./K9S_CONNECTION_GUIDE.md)
- [K9s Quick Setup](./QUICK_K9S_SETUP.md)

---

**תאריך עדכון:** 2025-11-02  
**גרסה:** 1.0

