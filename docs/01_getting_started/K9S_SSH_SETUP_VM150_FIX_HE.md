# 🔧 תיקון: הגדרת SSH ל-K9s דרך Jump Host

**תאריך:** 2025-11-02  
**בעיה:** Connection timeout ל-10.10.10.150  
**פתרון:** שימוש ב-ProxyJump דרך jump host

---

## 🚨 הבעיה

כשניסית להתחבר ישירות ל-10.10.10.150 קיבלת:
```
ssh: connect to host 10.10.10.150 port 22: Connection timed out
```

**הסיבה:** השרת 10.10.10.150 לא נגיש ישירות מ-Windows שלך - צריך לעבור דרך **Jump Host** (10.10.10.10).

---

## ✅ הפתרון

### שלב 1: SSH Config עודכן

עדכנתי את ה-SSH config להשתמש ב-`ProxyJump`:

```
Host vm-150
    HostName 10.10.10.150
    User prisma
    ProxyJump staging-host    # דרך jump host
    IdentityFile ~/.ssh/vm_150_key
```

עכשיו כשאתה מריץ `ssh vm-150`, זה עובר אוטומטית דרך jump host.

### שלב 2: העתק את המפתח הציבורי לשרת

**חשוב:** המפתח הציבורי שלך צריך להיות בשרת 10.10.10.150.

**איך לעשות את זה:**

#### אופציה A: דרך Script (מומלץ)

```powershell
.\scripts\copy_vm150_key_to_server.ps1
```

ה-script יוביל אותך בתהליך.

#### אופציה B: ידנית

1. **הדפס את המפתח הציבורי:**
   ```powershell
   Get-Content C:\Users\roy.avrahami\.ssh\vm_150_key.pub
   ```

2. **העתק את המפתח** (כל השורה, כולל `ssh-rsa`)

3. **התחבר לשרת דרך jump host:**
   ```powershell
   ssh root@10.10.10.10
   # Password: ask team lead
   ```

4. **מהשרת jump host, התחבר ל-target:**
   ```bash
   ssh prisma@10.10.10.150
   # Accept host key if prompted
   ```

5. **בשרת 10.10.10.150, הוסף את המפתח:**
   ```bash
   mkdir -p ~/.ssh
   chmod 700 ~/.ssh
   echo "ssh-rsa AAAAB3...root@vm1" >> ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   ```

   **החלף `ssh-rsa AAAAB3...root@vm1` במפתח הציבורי שלך!**

6. **בדוק שהמפתח נוסף:**
   ```bash
   cat ~/.ssh/authorized_keys
   ```

### שלב 3: בדוק שהחיבור עובד

```powershell
.\scripts\connect_k9s_vm150.ps1 -Action test
```

**אמור לעבוד ללא הזנת סיסמה!**

### שלב 4: התחבר ל-K9s

```powershell
ssh vm-150
k9s
```

---

## 📝 הערות חשובות

### ⚠️ Windows vs Linux Commands

**ב-Windows PowerShell:**
```powershell
# ❌ לא יעבוד
chmod 600 ~/.ssh/authorized_keys

# ✅ זה פקודת Linux, לא Windows!
# הפקודות chmod רצות בשרת (Linux), לא ב-Windows
```

**ב-Linux/Server:**
```bash
# ✅ זה יעבוד
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

### 🔑 איפה מוסיפים את המפתח?

**המפתח הציבורי צריך להיות:**
- ✅ **בשרת 10.10.10.150** → `~/.ssh/authorized_keys` של משתמש `prisma`
- ❌ **לא ב-Windows** → Windows רק שומר את המפתח הפרטי

### 🚀 איך עובד ProxyJump?

כשאתה מריץ `ssh vm-150`:
1. SSH מתחבר ל-jump host (10.10.10.10) - **staging-host**
2. מ-jump host, SSH מתחבר ל-target (10.10.10.150) - **vm-150**
3. המפתח הפרטי מ-Windows עובר דרך jump host ל-target
4. הכל אוטומטי - אתה לא רואה את החיבור דרך jump host

---

## 🔗 סיכום השינויים

### קבצים שעודכנו:

1. **`~/.ssh/config`** - הוספתי `ProxyJump staging-host` ל-`vm-150`
2. **`scripts/copy_vm150_key_to_server.ps1`** - Script חדש להעתקת מפתח
3. **`scripts/setup_ssh_agent_vm150.ps1`** - עודכן הודעות

### מה לעשות עכשיו:

1. ✅ **הרץ:** `.\scripts\copy_vm150_key_to_server.ps1`
2. ✅ **בדוק:** `.\scripts\connect_k9s_vm150.ps1 -Action test`
3. ✅ **התחבר:** `ssh vm-150` ואז `k9s`

---

## 🆘 אם עדיין יש בעיות

### בעיה: "Permission denied (publickey)"

**פתרון:**
- ודא שהמפתח הציבורי נמצא ב-`~/.ssh/authorized_keys` בשרת
- ודא שההרשאות נכונות: `chmod 600 ~/.ssh/authorized_keys`

### בעיה: "Connection timed out" גם דרך jump host

**פתרון:**
- בדוק שה-jump host נגיש: `Test-NetConnection 10.10.10.10 -Port 22`
- בדוק שה-target נגיש מ-jump host (התחבר ל-jump host ובדוק)

### בעיה: "Host key verification failed"

**פתרון:**
```powershell
ssh-keygen -R 10.10.10.150
ssh-keygen -R 10.10.10.10
```

---

**עכשיו זה אמור לעבוד!** 🎉

