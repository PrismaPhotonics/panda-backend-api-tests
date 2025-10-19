# 🔧 מדריך התקנת .NET 9.0 עבור PandaApp

**תאריך:** 16 אוקטובר 2025  
**בעיה:** PandaApp דורש .NET 9.0 אבל מותקן רק .NET 8.0  
**פתרון:** התקנת .NET 9.0 Desktop Runtime

---

## 🎯 מה קרה?

```
Exit Code: -2147450730
Required: .NET 9.0 Runtime
Installed: .NET 8.0 Runtime

❌ PandaApp לא יכול לרוץ ללא .NET 9.0
```

---

## 📥 הורדה והתקנה (2 דקות)

### **שלב 1: בחר את הקובץ הנכון**

בעמוד שנפתח, חפש את הסעיף:

```
.NET Desktop Runtime 9.0.x
```

**הורד:**
- **Windows x64:** `windowsdesktop-runtime-9.0.x-win-x64.exe`

או השתמש בקישור הישיר:
```
https://aka.ms/dotnet/9.0/windowsdesktop-runtime-win-x64.exe
```

---

### **שלב 2: הרץ את ה-Installer**

1. **פתח את הקובץ שהורדת**
2. **לחץ "Install"**
3. **המתן להתקנה** (30-60 שניות)
4. **לחץ "Close"** כשסיים

**זהו - פשוט מאוד!**

---

## ✅ אימות התקנה

אחרי ההתקנה, אמת שהכל תקין:

```powershell
dotnet --list-runtimes
```

**צפוי לראות:**
```
Microsoft.NETCore.App 8.0.15 [...]
Microsoft.NETCore.App 9.0.x [...]          ← חדש!
Microsoft.WindowsDesktop.App 8.0.15 [...]
Microsoft.WindowsDesktop.App 9.0.x [...]  ← חדש!
```

---

## 🚀 הפעלת PandaApp אחרי ההתקנה

```powershell
# חזור לפרויקט
cd C:\Projects\focus_server_automation

# הפעל את PandaApp
Start-Process "C:\Program Files\Prisma\PandaApp\PandaApp-1.2.41.exe" `
              -WorkingDirectory "C:\Program Files\Prisma\PandaApp"
```

או:
- פתח Start Menu
- חפש "PandaApp"
- לחץ Enter

**הפעם זה אמור לעבוד!** 🎉

---

## 🔍 אם עדיין לא עובד

### בדוק שההתקנה הצליחה:

```powershell
$net9 = dotnet --list-runtimes | Select-String "9.0"
if ($net9) {
    Write-Host "✅ .NET 9.0 installed: $net9" -ForegroundColor Green
} else {
    Write-Host "❌ .NET 9.0 NOT found - reinstall" -ForegroundColor Red
}
```

### אם עדיין חסר:
1. הורד שוב מהקישור הישיר למעלה
2. ודא שבחרת **Desktop Runtime** (לא SDK)
3. ודא שבחרת **x64** (לא x86 או ARM)

---

## 📊 השוואת גרסאות

| רכיב | נדרש | מותקן לפני | מותקן אחרי |
|------|------|-----------|-----------|
| .NET Core | 9.0 | 8.0 | 8.0 + 9.0 ✅ |
| Desktop Runtime | 9.0 | 8.0 | 8.0 + 9.0 ✅ |

**שים לב:** אפשר להחזיק מספר גרסאות במקביל - זה לא מחליף את 8.0!

---

## 🎯 למה .NET 9.0?

PandaApp-1.2.41 נבנה עם .NET 9.0 - גרסה עדכנית יותר עם:
- ביצועים משופרים
- תמיכה בפלטפורמות חדשות
- תיקוני אבטחה

זו הסיבה שהוא לא יכול לרוץ עם .NET 8.0 בלבד.

---

## 🔗 קישורים שימושיים

| משאב | קישור |
|------|--------|
| .NET 9.0 Downloads | https://dotnet.microsoft.com/download/dotnet/9.0 |
| Desktop Runtime Direct | https://aka.ms/dotnet/9.0/windowsdesktop-runtime-win-x64.exe |
| .NET Documentation | https://learn.microsoft.com/en-us/dotnet/ |

---

## ⏭️ צעדים הבאים

1. ✅ **התקן .NET 9.0** (הקישור פתוח)
2. ✅ **אמת התקנה** (`dotnet --list-runtimes`)
3. ✅ **הפעל PandaApp** (מ-Start Menu או PowerShell)
4. ✅ **בדוק Live View** עובד

---

**הוכן על ידי:** QA Automation Architect  
**תאריך:** 16 אוקטובר 2025  
**סטטוס:** ✅ **הבעיה זוהתה והפתרון מוכן**

