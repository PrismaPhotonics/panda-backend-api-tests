# 🤖 מדריך התקנה אוטומטית מלאה - PandaApp

**תאריך:** 16 אוקטובר 2025  
**גרסה:** 1.0.0  
**סטטוס:** ✅ Production Ready - CI/CD Compatible

---

## 📌 סקירה כללית

יצרתי **שני סקריפטים מקצועיים** לאוטומציה מלאה של התקנת PandaApp:

| סקריפט | טכנולוגיה | ממשק | תכונות |
|--------|-----------|------|---------|
| **Install-PandaApp-Automated.ps1** | PowerShell | CLI | מקצועי, CI/CD ready, Silent mode |
| **panda_installer_gui.py** | Python | GUI/CLI | ממשק גרפי + CLI, Cross-platform |

---

## 🎯 מה הסקריפטים עושים?

### ✅ התקנה אוטומטית מלאה:

1. **בדיקת הרשאות:** מוודא Administrator privileges
2. **התקנת .NET 9.0:** הורדה והתקנה אוטומטית
3. **איתור Installer:** מחפש בתיקיות ברירת מחדל
4. **התקנת אפליקציה:** מריץ את ההתקנה (Silent/Interactive)
5. **העתקת תצורה:** מתקין `usersettings.json` עם גיבוי
6. **יצירת תיקיות:** יוצר `SavedData` ובודק הרשאות
7. **בדיקת רשת:** מאמת חיבור לכל ה-endpoints
8. **הפעלת אפליקציה:** מפעיל את PandaApp
9. **לוגים מפורטים:** שומר log מלא של כל התהליך

---

## 🚀 QuickStart - שתי דרכים להריץ

### **אופציה 1: PowerShell (מומלץ לאוטומציה)**

```powershell
# התקנה אוטומטית מלאה
cd C:\Projects\focus_server_automation
.\Install-PandaApp-Automated.ps1
```

### **אופציה 2: Python עם GUI**

```powershell
# התקנה עם ממשק גרפי
cd C:\Projects\focus_server_automation
python scripts\panda_installer_gui.py --gui
```

**זהו! הכל יקרה אוטומטית!** 🎉

---

## 📖 PowerShell Script - מדריך מפורט

### **מיקום:**
```
C:\Projects\focus_server_automation\Install-PandaApp-Automated.ps1
```

### **הרצה בסיסית:**

```powershell
# הפעלה אינטראקטיבית
.\Install-PandaApp-Automated.ps1

# או עם הרשאות מפורשות:
Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File .\Install-PandaApp-Automated.ps1" -Verb RunAs
```

---

### **פרמטרים מתקדמים:**

#### **1. Silent Mode (להתקנה שקטה - CI/CD)**

```powershell
.\Install-PandaApp-Automated.ps1 -SilentMode
```

**שימוש:**
- התקנות אוטומטיות במערכות רבות
- סקריפטי CI/CD
- Deployment מרוחק
- ללא prompts למשתמש

---

#### **2. ציון נתיבים ספציפיים**

```powershell
.\Install-PandaApp-Automated.ps1 `
    -InstallerPath "C:\Downloads\PandaAppInstaller-1.2.41.exe" `
    -ConfigPath "C:\Config\usersettings.production.json"
```

**שימוש:**
- כשהקבצים לא בתיקיות ברירת מחדל
- כשיש כמה גרסאות של Installer
- פריסת תצורות שונות (Dev/Staging/Production)

---

#### **3. דילוג על בדיקת רשת**

```powershell
.\Install-PandaApp-Automated.ps1 -SkipNetworkCheck
```

**שימוש:**
- התקנה offline
- רשת פנימית ללא גישה לendpoints
- בדיקות מקומיות

---

#### **4. קובץ לוג מותאם אישית**

```powershell
.\Install-PandaApp-Automated.ps1 -LogPath "C:\Logs\PandaInstall_$(Get-Date -Format 'yyyyMMdd').log"
```

**שימוש:**
- שמירת לוגים לתיקייה מרכזית
- לוגים עם timestamps
- אינטגרציה עם מערכת ניטור

---

#### **5. שילוב כל הפרמטרים (CI/CD מלא)**

```powershell
.\Install-PandaApp-Automated.ps1 `
    -SilentMode `
    -AutoUpdate `
    -SkipNetworkCheck `
    -InstallerPath "\\network\share\PandaAppInstaller-1.2.41.exe" `
    -ConfigPath "\\network\share\config\usersettings.json" `
    -LogPath "C:\Logs\PandaInstall.log"
```

---

### **שילוב ב-CI/CD Pipeline**

#### **GitLab CI Example:**

```yaml
# .gitlab-ci.yml
deploy_panda:
  stage: deploy
  tags:
    - windows
    - production
  script:
    - |
      pwsh -ExecutionPolicy Bypass -Command "
      & 'C:\Deploy\Install-PandaApp-Automated.ps1' `
        -SilentMode `
        -AutoUpdate `
        -InstallerPath '$CI_PROJECT_DIR\installers\PandaAppInstaller-1.2.41.exe' `
        -ConfigPath '$CI_PROJECT_DIR\config\usersettings.production.json' `
        -LogPath 'C:\Logs\PandaInstall_$CI_JOB_ID.log'
      "
  only:
    - production
```

#### **GitHub Actions Example:**

```yaml
# .github/workflows/deploy-panda.yml
name: Deploy PandaApp

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install PandaApp
        shell: pwsh
        run: |
          .\Install-PandaApp-Automated.ps1 `
            -SilentMode `
            -AutoUpdate `
            -InstallerPath "${{ github.workspace }}\installers\PandaAppInstaller-1.2.41.exe" `
            -ConfigPath "${{ github.workspace }}\config\usersettings.json" `
            -LogPath "C:\Logs\PandaInstall.log"
```

#### **Azure DevOps Pipeline Example:**

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main

pool:
  vmImage: 'windows-latest'

steps:
  - task: PowerShell@2
    displayName: 'Install PandaApp'
    inputs:
      targetType: 'filePath'
      filePath: '$(System.DefaultWorkingDirectory)\Install-PandaApp-Automated.ps1'
      arguments: '-SilentMode -AutoUpdate -InstallerPath "$(Build.SourcesDirectory)\installers\PandaAppInstaller-1.2.41.exe" -ConfigPath "$(Build.SourcesDirectory)\config\usersettings.json"'
      errorActionPreference: 'stop'
```

---

## 🐍 Python Script - מדריך מפורט

### **מיקום:**
```
C:\Projects\focus_server_automation\scripts\panda_installer_gui.py
```

### **הרצה בסיסית:**

#### **1. GUI Mode (ממשק גרפי)**

```powershell
cd C:\Projects\focus_server_automation
python scripts\panda_installer_gui.py --gui
```

**תקבל חלון עם:**
- בחירת קבצים (Browse buttons)
- Progress bar
- לוגים בזמן אמת
- כפתורי Install/Exit

---

#### **2. CLI Mode (שורת פקודה)**

```powershell
python scripts\panda_installer_gui.py --cli
```

---

#### **3. Silent Mode (בלי GUI)**

```powershell
python scripts\panda_installer_gui.py --silent
```

---

#### **4. עם פרמטרים**

```powershell
python scripts\panda_installer_gui.py `
    --cli `
    --silent `
    --installer "C:\Downloads\PandaAppInstaller-1.2.41.exe" `
    --config "C:\Config\usersettings.json" `
    --admin
```

---

### **דוגמאות שימוש מתקדמות:**

#### **התקנה אוטומטית עם Admin:**

```powershell
python scripts\panda_installer_gui.py --silent --admin
```

#### **GUI עם קבצים ספציפיים:**

```powershell
python scripts\panda_installer_gui.py `
    --gui `
    --installer "C:\Downloads\PandaAppInstaller-1.2.41.exe" `
    --config "C:\Downloads\usersettings.cleaned.json"
```

---

## 📊 השוואת הסקריפטים

| תכונה | PowerShell | Python |
|-------|-----------|---------|
| **ממשק** | CLI בלבד | GUI + CLI |
| **פלטפורמה** | Windows בלבד | Cross-platform |
| **תלויות** | PowerShell 5.1+ | Python 3.6+, tkinter |
| **Silent Mode** | ✅ מלא | ✅ מלא |
| **CI/CD Ready** | ✅✅ מצוין | ✅ טוב |
| **גודל** | ~700 שורות | ~800 שורות |
| **לוגים** | קובץ + Console | קובץ + Console + GUI |
| **קלות שימוש** | בינוני | קל (GUI) |
| **למתקדמים** | מומלץ | אופציונלי |

---

## 🎯 מתי להשתמש במה?

### **השתמש ב-PowerShell אם:**
- ✅ אתה עובד עם CI/CD pipelines
- ✅ אתה צריך deployment אוטומטי
- ✅ אתה מעדיף CLI
- ✅ אתה עובד ב-Windows בלבד
- ✅ אתה רוצה את השליטה המקסימלית

### **השתמש ב-Python GUI אם:**
- ✅ אתה רוצה ממשק גרפי ידידותי
- ✅ אתה מתקין ידנית (לא אוטומציה)
- ✅ אתה רוצה לראות progress בזמן אמת
- ✅ אתה לא נוח עם PowerShell
- ✅ אתה צריך cross-platform (עתיד)

---

## 🔍 מבנה הלוגים

### **פורמט:**

```
2025-10-16 14:30:00 - [INFO] - Installation started at 2025-10-16 14:30:00
2025-10-16 14:30:01 - [INFO] - Running with Administrator privileges
2025-10-16 14:30:02 - [INFO] - Checking for .NET 9.0 Desktop Runtime...
2025-10-16 14:30:03 - [SUCCESS] - .NET 9.0 already installed
2025-10-16 14:30:04 - [INFO] - Using installer: C:\Users\...\PandaAppInstaller-1.2.41.exe
2025-10-16 14:30:05 - [INFO] - Installing PandaApp...
2025-10-16 14:30:45 - [SUCCESS] - PandaApp installed successfully
2025-10-16 14:30:46 - [INFO] - Installing configuration file...
2025-10-16 14:30:47 - [SUCCESS] - Configuration file validated (valid JSON)
2025-10-16 14:30:48 - [SUCCESS] - Configuration installed successfully
2025-10-16 14:30:49 - [INFO] - Checking network connectivity...
2025-10-16 14:30:50 - [SUCCESS] - Backend (10.10.100.100:443) - Reachable
2025-10-16 14:30:51 - [SUCCESS] - Frontend (10.10.10.100:443) - Reachable
2025-10-16 14:30:52 - [SUCCESS] - FrontendApi (10.10.10.150:30443) - Reachable
2025-10-16 14:30:53 - [SUCCESS] - PandaApp started successfully (PID: 12345)
2025-10-16 14:30:54 - [INFO] - Installation completed successfully!
```

### **רמות לוג:**

| רמה | משמעות | צבע (Console) |
|------|---------|--------------|
| **INFO** | מידע כללי | לבן |
| **SUCCESS** | פעולה הצליחה | ירוק |
| **WARNING** | אזהרה (לא קריטי) | צהוב |
| **ERROR** | שגיאה (קריטי) | אדום |
| **DEBUG** | פרטים טכניים | אפור |

---

## 🛠️ פתרון בעיות

### **בעיה 1: "Script execution is disabled"**

```powershell
# פתרון:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# או הרץ עם bypass:
powershell -ExecutionPolicy Bypass -File .\Install-PandaApp-Automated.ps1
```

---

### **בעיה 2: "Administrator privileges required"**

```powershell
# פתרון - הרץ PowerShell כ-Administrator:
Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File '.\Install-PandaApp-Automated.ps1'" -Verb RunAs
```

---

### **בעיה 3: "Installer not found"**

**אופציה א': העתק לתיקייה נתמכת**
```powershell
Copy-Item "C:\Path\To\PandaAppInstaller-1.2.41.exe" "$env:USERPROFILE\Downloads\"
```

**אופציה ב': ציין נתיב מפורש**
```powershell
.\Install-PandaApp-Automated.ps1 -InstallerPath "C:\Custom\Path\PandaAppInstaller-1.2.41.exe"
```

---

### **בעיה 4: ".NET installation failed"**

```powershell
# התקן ידנית מהאתר הרשמי:
Start-Process "https://aka.ms/dotnet/9.0/windowsdesktop-runtime-win-x64.exe"

# אחרי ההתקנה הידנית - הרץ את הסקריפט שוב
.\Install-PandaApp-Automated.ps1
```

---

### **בעיה 5: Network endpoints not reachable**

```powershell
# אם אתה מתקין offline או ללא גישה לשרתים:
.\Install-PandaApp-Automated.ps1 -SkipNetworkCheck
```

---

## 📝 דוגמאות שימוש מעשיות

### **תרחיש 1: התקנה ראשונה במחשב חדש**

```powershell
# הכל אוטומטי - הקבצים בDownloads
cd C:\Projects\focus_server_automation
.\Install-PandaApp-Automated.ps1
```

---

### **תרחיש 2: פריסה לכמה מחשבים ברשת**

```powershell
# סקריפט deployment
$computers = @("PC001", "PC002", "PC003")

foreach ($computer in $computers) {
    Invoke-Command -ComputerName $computer -ScriptBlock {
        & "\\FileServer\Deploy\Install-PandaApp-Automated.ps1" `
            -SilentMode `
            -InstallerPath "\\FileServer\Installers\PandaAppInstaller-1.2.41.exe" `
            -ConfigPath "\\FileServer\Config\usersettings.json" `
            -LogPath "\\FileServer\Logs\$env:COMPUTERNAME.log"
    }
}
```

---

### **תרחיש 3: עדכון גרסה קיימת**

```powershell
# הסקריפט מזהה התקנה קיימת ויציע reinstall
.\Install-PandaApp-Automated.ps1 `
    -InstallerPath "C:\Downloads\PandaAppInstaller-1.3.0.exe" `
    -AutoUpdate
```

---

### **תרחיש 4: התקנה עם תצורות שונות לפי סביבה**

```powershell
# Production
.\Install-PandaApp-Automated.ps1 `
    -SilentMode `
    -ConfigPath "C:\Config\usersettings.production.json"

# Staging
.\Install-PandaApp-Automated.ps1 `
    -SilentMode `
    -ConfigPath "C:\Config\usersettings.staging.json"

# Development
.\Install-PandaApp-Automated.ps1 `
    -SilentMode `
    -ConfigPath "C:\Config\usersettings.development.json"
```

---

## ✅ Checklist התקנה

### **לפני ההרצה:**
- [ ] PowerShell 5.1+ או Python 3.6+ מותקן
- [ ] יש לך הרשאות Administrator
- [ ] קובץ Installer נמצא במחשב
- [ ] קובץ `usersettings.json` נקי מוכן
- [ ] יש חיבור לאינטרנט (להורדת .NET)

### **אחרי ההרצה:**
- [ ] .NET 9.0 מותקן (`dotnet --list-runtimes`)
- [ ] PandaApp מותקן ב-`C:\Program Files\Prisma\PandaApp`
- [ ] קובץ `usersettings.json` קיים ב-AppData
- [ ] תיקיית `C:\Panda\SavedData` קיימת
- [ ] האפליקציה נפתחת בלי שגיאות
- [ ] יש חיבור ל-Backend servers

---

## 🎓 טיפים ושיטות עבודה מומלצות

### **1. שמור גרסאות**
```powershell
# שמור את ה-Installer בשם עם גרסה
$installerDir = "C:\Deploy\PandaApp\Installers"
Copy-Item "PandaAppInstaller-1.2.41.exe" "$installerDir\PandaAppInstaller-1.2.41_$(Get-Date -Format 'yyyyMMdd').exe"
```

### **2. גרסיות תצורה**
```powershell
# נהל תצורות בGit
git add config/usersettings.*.json
git commit -m "Update PandaApp config for v1.2.41"
git tag -a panda-v1.2.41 -m "PandaApp v1.2.41 configuration"
```

### **3. לוגים מרכזיים**
```powershell
# שמור לוגים במקום מרכזי עם timestamp
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
.\Install-PandaApp-Automated.ps1 -LogPath "\\FileServer\Logs\PandaInstall_$env:COMPUTERNAME_$timestamp.log"
```

### **4. בדיקת תקינות post-install**
```powershell
# הרץ smoke tests אחרי התקנה
$exePath = "C:\Program Files\Prisma\PandaApp\PandaApp-1.2.41.exe"
if (Test-Path $exePath) {
    Write-Host "✓ Installation verified" -ForegroundColor Green
} else {
    Write-Host "✗ Installation failed" -ForegroundColor Red
}
```

---

## 📞 תמיכה ועזרה

### **אם משהו לא עובד:**

1. **בדוק את הלוג:**
   ```powershell
   Get-Content "C:\Temp\PandaApp-Install.log" -Tail 50
   ```

2. **הרץ בmode verbose:**
   ```powershell
   .\Install-PandaApp-Automated.ps1 -Verbose
   ```

3. **בדוק Event Viewer:**
   ```powershell
   eventvwr.msc
   # → Windows Logs → Application
   ```

4. **בדוק dependencies:**
   ```powershell
   # PowerShell version
   $PSVersionTable.PSVersion
   
   # .NET version
   dotnet --list-runtimes
   
   # Python version (if using Python script)
   python --version
   ```

---

## 📚 קישורים וקבצים

| משאב | מיקום |
|------|-------|
| **PowerShell Script** | `C:\Projects\focus_server_automation\Install-PandaApp-Automated.ps1` |
| **Python GUI Script** | `C:\Projects\focus_server_automation\scripts\panda_installer_gui.py` |
| **מדריך זה** | `C:\Projects\focus_server_automation\AUTOMATED_INSTALLATION_GUIDE_HE.md` |
| **מדריך ידני** | `C:\Projects\focus_server_automation\PANDA_APP_INSTALLATION_GUIDE_HE.md` |
| **תצורה נקייה** | `C:\Users\roy.avrahami\Downloads\usersettings.cleaned.json` |
| **לוג ברירת מחדל** | `C:\Temp\PandaApp-Install.log` |

---

## 🎉 סיכום

**יצרתי לך מערכת אוטומציה מלאה מקצועית לפריסת PandaApp!**

### **מה קיבלת:**
✅ סקריפט PowerShell production-grade  
✅ סקריפט Python עם GUI  
✅ תמיכה ב-CI/CD pipelines  
✅ Silent mode מלא  
✅ לוגים מפורטים  
✅ Error handling מקיף  
✅ Network validation  
✅ מדריכים מפורטים בעברית  

### **איך להתחיל:**
```powershell
# הדרך הכי פשוטה:
cd C:\Projects\focus_server_automation
.\Install-PandaApp-Automated.ps1

# זהו! הכל אוטומטי!
```

---

**הוכן על ידי:** QA Automation Architect  
**תאריך:** 16 אוקטובר 2025  
**גרסה:** 1.0.0  
**סטטוס:** ✅ **Production Ready** 🚀

