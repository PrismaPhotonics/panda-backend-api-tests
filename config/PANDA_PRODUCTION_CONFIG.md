# 🐼 PandaApp - Production Configuration Reference

**תאריך:** 16 אוקטובר 2025  
**סביבה:** Production - New Environment (10.10.100.100)  
**גרסה:** PandaApp 1.2.41

---

## 📍 מיקומים קריטיים

### קובץ התצורה
```
C:\Panda\usersettings.json
```
**⚠️ חשוב:** הקובץ צריך להיות ב-`C:\Panda\` ולא ב-`C:\Program Files\...`!

זה מוגדר ב-`appsettings.json`:
```json
"UserConfigFile": "C:\\Panda\\usersettings.json"
```

### קבצי האפליקציה
- **EXE:** `C:\Program Files\Prisma\PandaApp\PandaApp-1.2.41.exe`
- **תיקיית נתונים:** `C:\Panda\SavedData`
- **תיקיית לוגים:** `C:\Panda\Logs`

---

## 🌐 כתובות הסביבה

### Backend
```
https://10.10.100.100/focus-server/
```
- **פורט:** 443 (HTTPS)
- **סטטוס:** ✅ נגיש

### Frontend
```
https://10.10.10.100/liveView
```
- **פורט:** 443 (HTTPS)
- **סטטוס:** ✅ נגיש

### FrontendApi
```
https://10.10.10.150:30443/prisma/api/internal/sites/prisma-210-1000
```
- **פורט:** 30443
- **סטטוס:** ⚠️ ייתכן ולא נגיש (לא קריטי)

### SiteId
```
prisma-210-1000
```

---

## 📝 קובץ התצורה המלא

```json
{
  "Communication": {
    "Backend": "https://10.10.100.100/focus-server/",
    "Frontend": "https://10.10.10.100/liveView",
    "GrpcStreamMinTimeout_sec": 600,
    "GrpcTimeout": 500,
    "LogEndpoint": "log",
    "NumGrpcRetries": 10,
    "SiteId": "prisma-210-1000",
    "FrontendApi": "https://10.10.10.150:30443/prisma/api/internal/sites/prisma-210-1000"
  },
  "SavedData": {
    "Folder": "C:\\Panda\\SavedData",
    "EnableSave": true,
    "EnableLoad": true
  },
  "Constraints": {
    "FrequencyMax": 1000,
    "FrequencyMin": 0,
    "FrequencyMinRange": 1,
    "MaxWindows": 30,
    "SensorsRange": 2222
  },
  "Defaults": {
    "DisplayTimeAxisDuration": 30,
    "EndChannel": 109,
    "EndFrequency_hz": 1000,
    "FixedThreshold": 0,
    "Nfft": 1024,
    "NumLinesToDisplay": 200,
    "SpatialCenterSize": 3,
    "SpatialWindowSize": 7,
    "SpectralCenterSize": 5,
    "SpectralWindowSize": 11,
    "StartChannel": 11,
    "StartFrequency_hz": 0,
    "StartTime": "2023-01-11T09:35:00",
    "TimeStatus": "Live",
    "TimeWindow": "30s",
    "ViewType": "MultiChannelSpectrogram"
  },
  "EnableDebugTools": false,
  "EnableReconnection": true,
  "FullScreen": false,
  "Logger": {
    "LogGrpcMessages": false,
    "LogGrpcValidation": false,
    "LogPaging": false,
    "LogWorkingQueue": false
  },
  "NumLiveScreens": 30,
  "NumTabs": 10,
  "RefreshRate": 20,
  "Serilog": {
    "WriteTo": [
      {
        "Args": {
          "outputTemplate": " [{Level:u3}] {Timestamp:HH:mm:ss.fff} {Message:lj}{NewLine}{Exception}"
        },
        "Name": "Console"
      }
    ]
  },
  "SplitScreen": true,
  "Options": {
    "nfftSingleChannel": [
      128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536
    ]
  },
  "TemplateTypes": ["SD", "SC"]
}
```

---

## ✅ בדיקת קישוריות

```powershell
# Backend
Test-NetConnection -ComputerName 10.10.100.100 -Port 443

# Frontend
Test-NetConnection -ComputerName 10.10.10.100 -Port 443

# FrontendApi (אופציונלי)
Test-NetConnection -ComputerName 10.10.10.150 -Port 30443
```

**תוצאה מצופה:**
```
TcpTestSucceeded : True
```

---

## 🔍 אימות נכון של התצורה

### בלוגים של PandaApp, צריך לראות:

✅ **נכון:**
```
[INF] 25-10-16 18:04:39.469 WebApp URL: https://10.10.10.100/liveView?siteId=prisma-210-1000
```

❌ **לא נכון:**
```
[INF] WebApp URL: http://localhost:3000/liveView
```

אם רואים `localhost` - הקובץ לא במקום הנכון או לא נקרא!

---

## 🔧 תיקונים שבוצעו

מהקובץ המקורי, תוקנו:

1. ❌ **הוסר `_TimeStatus: "Range"`**
   - סיבה: סתירה עם `TimeStatus: "Live"`

2. ❌ **תוקן פסיק מיותר אחרי `EnableLoad: true`**
   - סיבה: JSON לא תקין

3. ❌ **תוקן פסיק מיותר ב-`nfftSingleChannel`**
   - סיבה: trailing comma

4. ❌ **הוסרה מחרוזת ריקה מ-`TemplateTypes`**
   - מ: `["SD", "SC", ""]`
   - ל: `["SD", "SC"]`

---

## 🚀 פריסה מהירה

אם צריך לפרוס את התצורה הזו על מכונה חדשה:

```powershell
# 1. עצור את PandaApp
Stop-Process -Name "PandaApp*" -Force -ErrorAction SilentlyContinue

# 2. צור תיקיות
New-Item -Path "C:\Panda" -ItemType Directory -Force
New-Item -Path "C:\Panda\SavedData" -ItemType Directory -Force

# 3. העתק את הקובץ
Copy-Item "C:\Projects\focus_server_automation\config\usersettings.production.json" `
          "C:\Panda\usersettings.json" -Force

# 4. הפעל את האפליקציה
Start-Process "C:\Program Files\Prisma\PandaApp\PandaApp-1.2.41.exe"
```

---

## ⚙️ הגדרות ביצועים

### הגדרות נוכחיות:
- **NumLiveScreens:** 30
- **RefreshRate:** 20
- **MaxWindows:** 30

⚠️ **אזהרה:** הגדרות אלו עלולות לגרום עומס CPU גבוה.

### להקלה על ביצועים:
```json
"NumLiveScreens": 15,
"RefreshRate": 12,
"MaxWindows": 20
```

---

## 📞 פתרון בעיות

### בעיה: האפליקציה מתחברת ל-localhost
**פתרון:** הקובץ לא ב-`C:\Panda\usersettings.json`

### בעיה: שגיאת חיבור ל-Backend
**פתרון:** בדוק:
```powershell
Test-NetConnection -ComputerName 10.10.100.100 -Port 443
```

### בעיה: "Access Denied" בעת עדכון קובץ
**פתרון:** הרץ PowerShell כ-Administrator

### בעיה: אין נתונים/פונקציונליות
**אפשרויות:**
1. בדוק שהקובץ ב-`C:\Panda\` ולא ב-`Program Files`
2. אמת שהכתובות נגישות (test-netconnection)
3. בדוק לוגים ב-`C:\Panda\Logs\PandaApp.log`

---

## 📚 קבצים קשורים

- **סקריפט פריסה:** `scripts/panda_app_setup_guide.py`
- **מדריך מלא:** `PANDA_APP_INSTALLATION_GUIDE_HE.md`
- **תצורות סביבה:** `config/environments.yaml`

---

**עודכן לאחרונה:** 16 אוקטובר 2025  
**מאושר ועובד:** ✅

