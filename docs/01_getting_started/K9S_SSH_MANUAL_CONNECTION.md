# 🔗 התחברות ידנית ל-K9s דרך Jump Host

**תאריך:** 2025-11-02  
**בעיה:** ProxyJump לא עובד עם password authentication  
**פתרון:** התחברות ידנית דרך jump host

---

## ⚠️ הערה חשובה

**אל תריץ פקודות Linux ב-Windows PowerShell!**

```powershell
# ❌ זה לא יעבוד ב-Windows PowerShell
chmod 600 ~/.ssh/authorized_keys  # זה פקודת Linux!
mkdir -p ~/.ssh                   # זה גם Linux syntax
```

**פקודות אלה צריכות להיות רק בשרת Linux!**

---

## ✅ התחברות ידנית (מומלץ עכשיו)

מכיוון ש-ProxyJump לא עובד עם password authentication, התחבר ידנית:

### שלב 1: התחבר ל-Jump Host

```powershell
ssh root@10.10.10.10
# Password: ask team lead
```

### שלב 2: מהשרת Jump Host, התחבר ל-Target

```bash
# עכשיו אתה ב-jump host (10.10.10.10)
ssh prisma@10.10.10.150
```

**אמור לעבוד ללא סיסמה** כי המפתח הציבורי כבר נוסף לשרת! ✅

### שלב 3: הרץ K9s

```bash
# עכשיו אתה ב-target server (10.10.10.150)
k9s
# או
k9s -n panda
```

---

## 🔧 חלופה: יצירת קיצור דרך

אם אתה רוצה פקודה אחת שתעבוד, תוכל ליצור alias ב-PowerShell:

```powershell
# הוסף ל-profiles:
notepad $PROFILE

# הוסף את זה:
function Connect-VM150 {
    ssh root@10.10.10.10 -t "ssh prisma@10.10.10.150 -t 'bash -l'"
}

function Connect-K9s {
    ssh root@10.10.10.10 -t "ssh prisma@10.10.10.150 -t 'k9s'"
}
```

אז תוכל להריץ:
```powershell
Connect-VM150   # להתחבר לשרת
Connect-K9s     # להתחבר ישירות ל-k9s
```

---

## 📝 סיכום

**המפתח הציבורי כבר בשרת** ✅  
**עכשיו תוכל להתחבר דרך jump host:**

```powershell
# 1. התחבר ל-jump host
ssh root@10.10.10.10

# 2. מהשרת jump host, התחבר ל-target
ssh prisma@10.10.10.150

# 3. הרץ k9s
k9s
```

**זה אמור לעבוד ללא סיסמה** כי המפתח כבר נוסף! 🎉

