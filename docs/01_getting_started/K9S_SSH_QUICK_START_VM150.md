# 🚀 התחברות מהירה ל-K9s דרך 10.10.10.150

**מדריך מהיר:** איך להתחבר ל-K9s בלי להזין סיסמה בכל פעם

---

## ✅ 3 שלבים פשוטים

### 1️⃣ הפעל Setup (פעם אחת)

```powershell
cd C:\Projects\focus_server_automation
.\scripts\setup_ssh_agent_vm150.ps1
```

**מה זה עושה?**
- ✅ מתקין את המפתח `vm_150_key` ב-SSH Agent
- ✅ מאפשר חיבור אוטומטי ללא סיסמה

### 2️⃣ בדוק שהחיבור עובד

```powershell
.\scripts\connect_k9s_vm150.ps1 -Action test
```

**אם זה עובד:** תראה "✅ Connection successful!"

**אם זה לא עובד:** עיין ב-[מדריך המלא](./K9S_SSH_SETUP_VM150_HE.md#-פתרון-בעיות-troubleshooting)

### 3️⃣ התחבר ל-K9s

```powershell
.\scripts\connect_k9s_vm150.ps1
```

או ישירות:

```powershell
ssh vm-150
k9s
```

---

## 📝 הערות חשובות

### ⚠️ אחרי Restart

אחרי restart של המחשב, צריך להריץ שוב את ה-setup:

```powershell
.\scripts\setup_ssh_agent_vm150.ps1
```

**או הגדר auto-start:** עיין ב-[מדריך המלא](./K9S_SSH_SETUP_VM150_HE.md#בעיה-ssh-agent-לא-שומר-את-המפתח-אחרי-restart)

### 🔑 המפתח צריך להיות בשרת

אם אתה מקבל "Permission denied (publickey)", ודא שהמפתח הציבורי שלך נמצא בשרת:

```bash
# בשרת 10.10.10.150
cat ~/.ssh/authorized_keys
```

אם המפתח לא שם, הוסף אותו:

```bash
# Copy מהמפתח הציבורי ב-Windows:
# C:\Users\roy.avrahami\.ssh\vm_150_key.pub

# בשרת:
echo "ssh-rsa AAAAB3...root@vm1" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

---

## 🔗 קישורים

- 📖 [מדריך מפורט](./K9S_SSH_SETUP_VM150_HE.md) - הסבר מלא של כל ההגדרות
- 🐳 [K9s Connection Guide](./K9S_CONNECTION_GUIDE.md) - כל המידע על K9s
- 🔐 [SSH Jump Host Setup](./SSH_JUMP_HOST_SETUP.md) - הגדרות SSH מתקדמות

---

**זה אמור להיות מספיק!** אם יש בעיות, עיין במדריך המפורט או ב-troubleshooting section.

