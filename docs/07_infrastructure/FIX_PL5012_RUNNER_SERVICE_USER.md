# תיקון: Runner Service רץ תחת משתמש שגוי
# Fix: Runner Service Running Under Wrong User

**תאריך:** 2025-11-27  
**Runner:** PL5012  
**בעיה:** ה-runner service רץ תחת `PL5012$` או `LocalSystem` במקום `roy.avrahami`

---

## 🚨 הבעיה

ה-runner service רץ תחת משתמש אחר מהמשתמש האינטראקטיבי שלך:

- **אתה רואה:** `pl5012\roy.avrahami` (כשאתה מחובר)
- **ה-runner service רץ תחת:** `PL5012$` או `LocalSystem`
- **התוצאה:** ה-SSH key לא נמצא כי הוא מחפש בנתיבים שונים

---

## 🔍 שלב 1: בדוק תחת איזה משתמש ה-Runner Service רץ

### דרך A: דרך Services.msc (GUI)

1. **פתח Services:**
   ```powershell
   services.msc
   ```

2. **חפש שירות בשם `actions.runner.*` או `GitHub Actions Runner`

3. **לחץ כפול על השירות** → לך לטאב **"Log On"**

4. **ראה את ה-"Log on as":**
   - `Local System` → הבעיה!
   - `PL5012$` → הבעיה!
   - `pl5012\roy.avrahami` → זה תקין ✅

### דרך B: דרך PowerShell

```powershell
# בדוק את ה-service configuration
Get-WmiObject Win32_Service | Where-Object {$_.Name -like "*actions.runner*"} | Select-Object Name, StartName, State

# או
sc qc actions.runner.PL5012*
```

**תוצאה צפויה:**
```
StartName: NT AUTHORITY\SYSTEM  ← זה LocalSystem (בעיה!)
StartName: PL5012$              ← זה Machine Account (בעיה!)
StartName: pl5012\roy.avrahami ← זה תקין ✅
```

---

## ✅ פתרון 1: שינוי המשתמש שהשירות רץ תחתיו (מומלץ)

### שלב 1: עצור את ה-Runner Service

```powershell
# עצור את ה-service
Stop-Service actions.runner.*

# או
sc stop actions.runner.PL5012*
```

### שלב 2: שנה את המשתמש

**דרך A: דרך Services.msc (GUI)**

1. פתח `services.msc`
2. לחץ כפול על השירות `actions.runner.*`
3. לך לטאב **"Log On"**
4. בחר **"This account"**
5. הזן: `pl5012\roy.avrahami`
6. הזן את הסיסמה
7. לחץ **OK**

**דרך B: דרך PowerShell**

```powershell
# שנה את המשתמש שהשירות רץ תחתיו
sc config actions.runner.PL5012* obj= "pl5012\roy.avrahami" password= "YOUR_PASSWORD"

# או דרך WMI
$service = Get-WmiObject Win32_Service | Where-Object {$_.Name -like "*actions.runner*"}
$service.Change($null, $null, $null, $null, $null, $false, "pl5012\roy.avrahami", "YOUR_PASSWORD")
```

### שלב 3: התחל את ה-Service מחדש

```powershell
# התחל את ה-service
Start-Service actions.runner.*

# או
sc start actions.runner.PL5012*
```

### שלב 4: בדוק שהכל עובד

```powershell
# בדוק שה-service רץ תחת המשתמש הנכון
Get-WmiObject Win32_Service | Where-Object {$_.Name -like "*actions.runner*"} | Select-Object Name, StartName, State
```

---

## ✅ פתרון 2: העתק את ה-SSH Key למיקום הנכון (זמני)

אם אתה לא יכול לשנות את המשתמש של השירות, העתק את ה-key למיקום שהשירות יכול לגשת אליו:

### אם ה-Service רץ תחת `PL5012$`:

```powershell
# צור תיקייה
New-Item -ItemType Directory -Force -Path "C:\Users\PL5012$\.ssh"

# העתק את ה-key
Copy-Item "C:\Users\roy.avrahami\.ssh\panda_staging_key" -Destination "C:\Users\PL5012$\.ssh\panda_staging_key"

# הגדר הרשאות
icacls "C:\Users\PL5012$\.ssh\panda_staging_key" /inheritance:r /grant:r "PL5012$:R"
```

### אם ה-Service רץ תחת `LocalSystem`:

**אופציה A: העתק ל-actions-runner directory (מומלץ)**

```powershell
# צור תיקייה
New-Item -ItemType Directory -Force -Path "C:\actions-runner\.ssh"

# העתק את ה-key
Copy-Item "C:\Users\roy.avrahami\.ssh\panda_staging_key" -Destination "C:\actions-runner\.ssh\panda_staging_key"

# הגדר הרשאות (כולם יכולים לקרוא)
icacls "C:\actions-runner\.ssh\panda_staging_key" /inheritance:r /grant:r "Everyone:R"
```

**אופציה B: שנה את הנתיב בקונפיג**

עדכן את `config/environments.yaml`:

```yaml
ssh:
  target_host:
    key_file: "C:/actions-runner/.ssh/panda_staging_key"  # נתיב מפורש במקום ~/.ssh
```

---

## ✅ פתרון 3: שינוי הנתיב בקונפיג (אם לא יכול לשנות משתמש)

אם אתה לא יכול לשנות את המשתמש של השירות, שנה את הנתיב בקונפיג:

### שלב 1: צור תיקייה גלובלית

```powershell
# צור תיקייה גלובלית
New-Item -ItemType Directory -Force -Path "C:\keys"

# העתק את ה-key
Copy-Item "C:\Users\roy.avrahami\.ssh\panda_staging_key" -Destination "C:\keys\panda_staging_key"

# הגדר הרשאות (כולם יכולים לקרוא)
icacls "C:\keys\panda_staging_key" /inheritance:r /grant:r "Everyone:R"
```

### שלב 2: עדכן את הקונפיג

עדכן את `config/environments.yaml`:

```yaml
ssh:
  target_host:
    key_file: "C:/keys/panda_staging_key"  # נתיב מפורש
```

### שלב 3: עדכן את הקוד (אם צריך)

אם הקוד משתמש ב-`~/.ssh`, עדכן אותו להשתמש בנתיב מפורש או environment variable.

---

## 🔍 שלב 2: בדוק שהתיקון עבד

לאחר התיקון, הרץ את ה-workflow שוב ובדוק:

1. **בדוק את ה-logs:**
   ```powershell
   # על PL5012
   Get-WmiObject Win32_Service | Where-Object {$_.Name -like "*actions.runner*"} | Select-Object Name, StartName
   ```

2. **הרץ את ה-workflow:**
   - לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
   - הרץ: **Smoke Tests**
   - בדוק שה-health checks עוברים

3. **בדוק את ה-logs:**
   - ה-health check צריך למצוא את ה-SSH key
   - SSH, Kubernetes, ו-RabbitMQ checks צריכים לעבור

---

## 📝 Checklist

- [ ] בדקתי תחת איזה משתמש ה-runner service רץ
- [ ] שיניתי את המשתמש של השירות ל-`pl5012\roy.avrahami` (אם אפשר)
- [ ] או העתקתי את ה-SSH key למיקום שהשירות יכול לגשת אליו
- [ ] או שיניתי את הנתיב בקונפיג לנתיב מפורש
- [ ] בדקתי שהשירות רץ תחת המשתמש הנכון
- [ ] הרצתי את ה-workflow ובדקתי שה-health checks עוברים

---

## 💡 המלצה

**הפתרון הטוב ביותר:** שנה את המשתמש של השירות ל-`pl5012\roy.avrahami`.

**למה?**
- ה-SSH key כבר קיים ב-`C:\Users\roy.avrahami\.ssh\`
- לא צריך להעתיק קבצים
- לא צריך לשנות קוד
- יותר בטוח (השירות רץ תחת משתמש ספציפי)

---

## 🔗 קישורים שימושיים

- **Runner Settings:** https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
- **Actions:** https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
- **Runner Troubleshooting:** `docs/07_infrastructure/RUNNER_TROUBLESHOOTING.md`

---

**עודכן:** 2025-11-27

