# 🐼 מדריך מהיר - סקריפטים ומדריכים של Panda

**תאריך:** 16 אוקטובר 2025  
**עודכן:** אחרי התקנה מוצלחת

---

## 📁 מפת הקבצים

### **1️⃣ קובץ ההתקנה המקורי**

```
📦 PandaAppInstaller-1.2.41.exe
📍 C:\Users\roy.avrahami\Downloads\
🎯 מטרה: התקנת אפליקציית Panda (נעשה ידנית)
✅ סטטוס: הותקן ב- C:\Program Files\Prisma\PandaApp\
```

**איך להריץ:**
```powershell
# לחץ ימני → Run as Administrator
# או:
Start-Process "C:\Users\roy.avrahami\Downloads\PandaAppInstaller-1.2.41.exe" -Verb RunAs
```

---

### **2️⃣ קובץ התצורה הנקי**

```
📄 usersettings.cleaned.json
📍 C:\Users\roy.avrahami\Downloads\
🎯 מטרה: תצורה נקייה עבור PandaApp
✅ סטטוס: הועתק ל- C:\Program Files\Prisma\PandaApp\usersettings.json
```

**תוכן:**
```json
{
  "Communication": {
    "Backend": "https://10.10.100.100/focus-server/",
    "Frontend": "https://10.10.10.100/liveView",
    "FrontendApi": "https://10.10.10.150:30443/prisma/api/internal/sites/prisma-210-1000",
    "SiteId": "prisma-210-1000"
  },
  "SavedData": {
    "Folder": "C:\\Panda\\SavedData"
  }
}
```

---

## 🔧 סקריפטים שיצרתי

### **3️⃣ סקריפט PowerShell - קונפיגורציה**

```
📜 setup_panda_config.ps1
📍 C:\Projects\focus_server_automation\
🎯 מטרה: קונפיגורציה אוטומטית של PandaApp
✅ סטטוס: הורץ בהצלחה
```

**מה הסקריפט עושה:**
1. בודק שהאפליקציה מותקנת
2. מגבה `usersettings.json` קיים (אם יש)
3. מעתיק `usersettings.cleaned.json` → `usersettings.json`
4. יוצר תיקיית `C:\Panda\SavedData`
5. מפעיל את PandaApp

**איך להריץ:**
```powershell
# מ-PowerShell רגיל (לא צריך venv)
Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File 'C:\Projects\focus_server_automation\setup_panda_config.ps1'" -Verb RunAs

# או ישירות עם הרשאות:
& "C:\Projects\focus_server_automation\setup_panda_config.ps1"
```

**Output לדוגמה:**
```
======================================================================
Panda App Configuration Setup
======================================================================

[INFO] Source config: C:\Users\roy.avrahami\Downloads\usersettings.cleaned.json
[INFO] Target location: C:\Program Files\Prisma\PandaApp\usersettings.json

[COPY] Copying cleaned config to PandaApp directory...
[SUCCESS] Config file copied successfully!

[FOLDER] Creating SavedData directory...
[SUCCESS] Created: C:\Panda\SavedData

======================================================================
Configuration Complete!
======================================================================

Launch PandaApp now? (Y/N): Y
[LAUNCH] Starting PandaApp...
[SUCCESS] PandaApp launched!
```

---

### **4️⃣ סקריפט Python - אבחון**

```
🐍 panda_app_setup_guide.py
📍 C:\Projects\focus_server_automation\scripts\
🎯 מטרה: אבחון בעיות והתקנה מודרכת
✅ סטטוס: זיהה שחסר .NET 9.0
```

**מה הסקריפט עושה:**
1. מחפש איפה PandaApp מותקן
2. בודק אם קיים `usersettings.json`
3. מאמת את תקינות ה-JSON
4. בודק קישוריות לשרתים (Backend/Frontend)
5. בודק תיקיית SavedData
6. מייצר דוח אבחון מפורט

**איך להריץ:**
```powershell
# מ-PowerShell (עם או בלי venv)
cd C:\Projects\focus_server_automation
py scripts\panda_app_setup_guide.py
```

**Output לדוגמה:**
```
======================================================================
Panda Application Setup Helper
======================================================================

🔍 Scanning for Panda installation...
✅ Found installation at: C:\Program Files\Prisma\PandaApp
✅ Executable: C:\Program Files\Prisma\PandaApp\PandaApp-1.2.41.exe

🔍 Scanning for usersettings.json...
✅ Found config at: C:\Program Files\Prisma\PandaApp\usersettings.json

🌐 Checking network connectivity...
  ✅ Backend: https://10.10.100.100/focus-server/ - Reachable
  ✅ Frontend: https://10.10.10.100/liveView - Reachable
  ✅ FrontendApi: https://10.10.10.150:30443/... - Reachable

📁 Checking SavedData folder: C:\Panda\SavedData
✅ SavedData folder exists
✅ SavedData folder is writable

======================================================================
✅ No issues detected!
======================================================================

Launch Panda application now? (Y/n): Y
🚀 Attempting to launch: C:\Program Files\Prisma\PandaApp\PandaApp-1.2.41.exe
✅ Application launched successfully
```

---

## 📖 מדריכים ותיעוד

### **5️⃣ מדריך התקנה מלא (עברית)**

```
📘 PANDA_APP_INSTALLATION_GUIDE_HE.md
📍 C:\Projects\focus_server_automation\
🎯 מטרה: מדריך שלב-אחר-שלב מפורט
✅ סטטוס: מדריך מלא של 594 שורות
```

**מה כולל:**
- 🔍 אבחון בעיות נפוצות
- 🚀 הוראות התקנה מפורטות
- ⚙️ תצורת רשת וקישוריות
- 🔧 פתרון בעיות (Troubleshooting)
- ✅ Smoke Tests
- 📊 אופטימיזציה של ביצועים

**איך לפתוח:**
```powershell
notepad "C:\Projects\focus_server_automation\PANDA_APP_INSTALLATION_GUIDE_HE.md"
```

---

### **6️⃣ מדריך .NET 9.0**

```
📗 INSTALL_DOTNET9_GUIDE_HE.md
📍 C:\Projects\focus_server_automation\
🎯 מטרה: הסבר על בעיית .NET 9.0 ופתרון
✅ סטטוס: הבעיה נפתרה - .NET 9.0.10 מותקן
```

**מה כולל:**
- אבחון הבעיה (Exit Code: -2147450730)
- הסבר למה דרוש .NET 9.0
- קישורי הורדה
- הוראות התקנה
- אימות שההתקנה הצליחה

---

### **7️⃣ דוח ולידציה של usersettings.json**

```
📙 USERSETTINGS_VALIDATION_REPORT_HE.md
📍 C:\Projects\focus_server_automation\docs\
🎯 מטרה: דוח מפורט על בעיות שתוקנו בקובץ תצורה
✅ סטטוס: 404 שורות של ניתוח ותיקונים
```

**מה כולל:**
- בעיות שזוהו (`_TimeStatus`, מחרוזת ריקה ב-`TemplateTypes`)
- שינויים שבוצעו (Unified Diff)
- אזהרות (3 IPs שונים, ביצועים גבוהים)
- אסטרטגיית פריסה
- Troubleshooting מפורט

---

## 🎯 תהליך ההתקנה המלא (מה שעשינו)

### **שלב 1: התקנת האפליקציה**
```
❌ ניסיון אוטומטי נכשל (הרשאות)
✅ התקנה ידנית: PandaAppInstaller-1.2.41.exe
✅ מותקן ב: C:\Program Files\Prisma\PandaApp\
```

### **שלב 2: זיהוי שהאפליקציה לא נפתחת**
```
✅ מצאנו את ה-shortcut: C:\ProgramData\Microsoft\Windows\Start Menu\Programs\PandaApp.lnk
✅ זיהינו שהאפליקציה מותקנת
❌ האפליקציה לא נפתחת
```

### **שלב 3: התקנת קובץ תצורה**
```
✅ הרצת setup_panda_config.ps1
✅ העתקה: usersettings.cleaned.json → usersettings.json
✅ יצירת תיקייה: C:\Panda\SavedData
```

### **שלב 4: בדיקת קישוריות**
```
✅ Backend: 10.10.100.100:443 - Reachable
✅ Frontend: 10.10.10.100:443 - Reachable
✅ FrontendApi: 10.10.10.150:30443 - Reachable
```

### **שלב 5: זיהוי בעיית .NET**
```
❌ Exit Code: -2147450730
🔍 Required: .NET 9.0
⚠️  Installed: .NET 8.0 only
```

### **שלב 6: התקנת .NET 9.0**
```
✅ הורדה: windowsdesktop-runtime-9.0-win-x64.exe (58 MB)
✅ התקנה: .NET 9.0.10 Desktop Runtime
✅ אימות: Microsoft.WindowsDesktop.App 9.0.10
```

### **שלב 7: הפעלה מוצלחת**
```
✅ PandaApp launched: PID 31696
✅ Memory: 856 MB (רץ ועובד)
✅ CPU: 22.9 seconds
```

---

## 🚀 Quick Reference - פקודות שימושיות

### **הפעלת PandaApp**
```powershell
# מ-Start Menu
Start-Process "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\PandaApp.lnk"

# ישירות
Start-Process "C:\Program Files\Prisma\PandaApp\PandaApp-1.2.41.exe"
```

### **בדיקת סטטוס**
```powershell
# בדוק אם PandaApp רץ
Get-Process -Name "PandaApp*"

# בדוק גרסת .NET
dotnet --list-runtimes | Select-String "9.0"
```

### **בדיקת קישוריות**
```powershell
# Backend
Test-NetConnection -ComputerName 10.10.100.100 -Port 443

# Frontend
Test-NetConnection -ComputerName 10.10.10.100 -Port 443

# FrontendApi
Test-NetConnection -ComputerName 10.10.10.150 -Port 30443
```

### **בדיקת תצורה**
```powershell
# הצג את התצורה
Get-Content "C:\Program Files\Prisma\PandaApp\usersettings.json" | ConvertFrom-Json

# אמת JSON
python -m json.tool "C:\Program Files\Prisma\PandaApp\usersettings.json"
```

---

## 🔧 פתרון בעיות מהיר

### **בעיה: האפליקציה לא נפתחת**
```powershell
# בדוק .NET 9.0
dotnet --list-runtimes | Select-String "9.0"

# אם חסר - התקן:
# https://aka.ms/dotnet/9.0/windowsdesktop-runtime-win-x64.exe
```

### **בעיה: שגיאת חיבור**
```powershell
# הגדל timeout ב-usersettings.json:
"Communication": {
  "GrpcTimeout": 1500  # במקום 500
}
```

### **בעיה: גישה נדחית ל-SavedData**
```powershell
# תן הרשאות:
icacls "C:\Panda\SavedData" /grant Users:(OI)(CI)F /T
```

---

## 📊 סיכום סטטוס נוכחי

| רכיב | סטטוס | מיקום/ערך |
|------|-------|-----------|
| **PandaApp** | ✅ מותקן ורץ | `C:\Program Files\Prisma\PandaApp\` |
| **usersettings.json** | ✅ קונפיג נקי | Backend: 10.10.100.100 |
| **.NET 9.0** | ✅ מותקן | Version 9.0.10 |
| **SavedData** | ✅ קיים וניתן לכתיבה | `C:\Panda\SavedData` |
| **Network** | ✅ כל ה-endpoints נגישים | Backend/Frontend/API |
| **Process** | ✅ רץ | PID: 31696, Memory: 856 MB |

---

## 📞 קישורים מהירים

| מה | איפה |
|----|------|
| **האפליקציה** | `C:\Program Files\Prisma\PandaApp\PandaApp-1.2.41.exe` |
| **התצורה** | `C:\Program Files\Prisma\PandaApp\usersettings.json` |
| **נתונים שמורים** | `C:\Panda\SavedData\` |
| **Shortcut** | `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\PandaApp.lnk` |
| **מדריך עברית** | `C:\Projects\focus_server_automation\PANDA_APP_INSTALLATION_GUIDE_HE.md` |
| **סקריפט PS** | `C:\Projects\focus_server_automation\setup_panda_config.ps1` |
| **סקריפט Python** | `C:\Projects\focus_server_automation\scripts\panda_app_setup_guide.py` |

---

## ✅ Checklist - מה שהושלם

- [x] התקנת PandaApp
- [x] העתקת קובץ תצורה נקי
- [x] יצירת תיקיית SavedData
- [x] בדיקת קישוריות רשת
- [x] זיהוי בעיית .NET 9.0
- [x] התקנת .NET 9.0.10
- [x] הפעלה מוצלחת של PandaApp
- [x] אימות שהתהליך רץ
- [ ] בדיקת Live View (ממתין לאישור משתמש)
- [ ] בדיקת Historical Data (ממתין לאישור משתמש)

---

**הוכן על ידי:** QA Automation Architect  
**תאריך:** 16 אוקטובר 2025  
**סטטוס:** ✅ **התקנה הושלמה בהצלחה**

