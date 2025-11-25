# Quick Start: הגדרת Runner על Slave Laptop
# Quick Start: Setup Runner on Slave Laptop

## 🚀 התחלה מהירה

### שלב 1: קבל Registration Token

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/new
2. בחר את מערכת ההפעלה (Windows/Linux)
3. העתק את ה-token

### שלב 2: הרץ את הסקריפט

**אפשרות 1: אינטראקטיבי (מומלץ)**
```powershell
py scripts\setup_runner_on_slave_laptop.py
```

הסקריפט יבקש ממך:
- SSH username
- Authentication method (Password/SSH Key)
- Registration token

**אפשרות 2: עם פרמטרים**
```powershell
# עם password
py scripts\setup_runner_on_slave_laptop.py --user admin --password mypass --token YOUR_TOKEN

# עם SSH key
py scripts\setup_runner_on_slave_laptop.py --user admin --key ~/.ssh/id_rsa --token YOUR_TOKEN
```

### שלב 3: וודא שה-Runner פעיל

בדוק ב-GitHub:
https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners

---

## ⚠️ פתרון בעיות

### המכונה לא מגיבה ל-ping:
- זה נורמלי - firewall יכול לחסום ping אבל לאפשר SSH
- נסה להתחבר דרך SSH ישירות

### SSH לא עובד:
```powershell
# נסה להתחבר ידנית
ssh user@10.50.0.36

# בדוק אם SSH service רץ על המכונה
# Windows: Get-Service sshd
# Linux: sudo systemctl status sshd
```

### Runner לא מופיע ב-GitHub:
1. ודא שה-token תקף (תקף ל-1 שעה)
2. בדוק לוגים:
   ```powershell
   # Windows
   ssh user@10.50.0.36
   cd C:\actions-runner
   Get-Content _diag\Runner_*.log -Tail 50
   
   # Linux
   ssh user@10.50.0.36
   cd /opt/actions-runner
   tail -50 _diag/Runner_*.log
   ```

---

## 📚 מידע נוסף

למדריך מפורט, ראה:
`docs/07_infrastructure/SETUP_SLAVE_LAPTOP_RUNNER.md`

