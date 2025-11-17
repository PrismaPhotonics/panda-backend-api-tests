# איך לבדוק שם משתמש ושם מחשב
## How to Check Username and Computer Name

---

## 🔍 בדיקה מהירה

### ב-PowerShell (שכבר פתוח):

```powershell
# שם המשתמש שלך
$env:USERNAME

# שם המחשב
$env:COMPUTERNAME

# או
hostname

# שם המשתמש המלא (עם domain אם יש)
whoami
```

---

## 📋 מה לעשות

### שלב 1: הרץ את הפקודות למעלה

```powershell
# הרץ את זה:
$env:USERNAME
$env:COMPUTERNAME
whoami
```

### שלב 2: קח את התוצאות

**דוגמה לתוצאות:**
```
PS C:\> $env:USERNAME
roy.avrahami

PS C:\> $env:COMPUTERNAME
PL5012

PS C:\> whoami
PL5012\roy.avrahami
```

### שלב 3: השתמש בזה ב-Runner

**אם `whoami` מחזיר:**
- `PL5012\roy.avrahami` → השתמש ב: `PL5012\roy.avrahami`
- `roy.avrahami` → השתמש ב: `.\roy.avrahami` או `roy.avrahami`

---

## ✅ מה להזין ב-Runner

**אם יש domain (כמו `PL5012\roy.avrahami`):**
```
PL5012\roy.avrahami
```

**אם אין domain (רק `roy.avrahami`):**
```
.\roy.avrahami
```
או פשוט:
```
roy.avrahami
```

---

## 🎯 TL;DR

```powershell
# הרץ את זה ב-PowerShell:
whoami
```

**התוצאה היא מה שצריך להזין ב-Runner!**

---

**עודכן:** 2025-11-09

