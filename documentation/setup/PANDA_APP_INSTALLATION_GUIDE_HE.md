# 🐼 מדריך התקנה ותצורה - Panda Application

**תאריך:** 16 אוקטובר 2025  
**גרסה:** 1.2.41  
**סטטוס:** 📝 מדריך שלב-אחר-שלב

---

## 📌 סיכום הבעיה

האפליקציה **PandaAppInstaller-1.2.41.exe** לא נפתחת.  
יש לך קובץ תצורה נקי: `usersettings.cleaned.json`  
**מטרה:** להתקין את האפליקציה ולקנפג אותה עם הקובץ הנקי.

---

## 🔍 אבחון ראשוני - למה האפליקציה לא נפתחת?

יש כמה סיבות אפשריות:

### 1️⃣ **ההתקנה לא הושלמה**
- ✅ קובץ ה-`exe` הוא **Installer** ולא האפליקציה עצמה
- ❌ צריך **להריץ את ההתקנה** תחילה

### 2️⃣ **חסרות הרשאות Administrator**
- ⚠️ התקנה דורשת הרשאות מנהל

### 3️⃣ **קובץ התצורה לא במקום הנכון**
- אפליקציית Panda מחפשת `usersettings.json` במיקום ספציפי

### 4️⃣ **בעיות רשת/חיבור**
- האפליקציה לא מצליחה להתחבר ל-Backend/Frontend

---

## 🚀 תהליך ההתקנה המלא (שלב אחר שלב)

### **שלב 1: הרצת ההתקנה**

1. **אתר את הקובץ:**
   ```
   C:\Users\roy.avrahami\Downloads\PandaAppInstaller-1.2.41.exe
   ```

2. **הרץ כ-Administrator:**
   - לחץ ימני על הקובץ
   - בחר: **"Run as administrator"** / **"הרץ כמנהל"**

3. **עקוב אחרי אשף ההתקנה:**
   - בחר תיקיית יעד (ברירת מחדל: `C:\Program Files\Prisma\Panda` או `C:\Panda`)
   - **שים לב למיקום שבחרת!** תצטרך אותו בהמשך
   - אשר יצירת קיצורי דרך

4. **סיים את ההתקנה**

---

### **שלב 2: איתור האפליקציה המותקנת**

אחרי ההתקנה, בדוק אם האפליקציה הותקנה במיקומים הבאים:

```
📁 מיקומים נפוצים:
  - C:\Program Files\Prisma\Panda\
  - C:\Program Files (x86)\Prisma\Panda\
  - C:\Panda\
  - %LocalAppData%\Panda\
  - %AppData%\Panda\
```

**חפש קובץ הפעלה:**
- `Panda.exe`
- `PandaApp.exe`
- `FocusClient.exe`

אם מצאת - **מצוין!** עבור לשלב 3.  
אם לא מצאת - ייתכן שההתקנה נכשלה, נסה שוב או צור קשר עם התמיכה.

---

### **שלב 3: העתקת קובץ התצורה הנקי**

#### **אופציה א: באמצעות הסקריפט האוטומטי (מומלץ!)**

הרץ את הסקריפט שיצרתי:

```powershell
cd C:\Projects\focus_server_automation
python scripts\panda_app_setup_guide.py
```

**הסקריפט יבצע אוטומטית:**
- ✅ איתור מיקום התקנת Panda
- ✅ גיבוי של קובץ תצורה קיים (אם יש)
- ✅ העתקת `usersettings.cleaned.json` למיקום הנכון
- ✅ בדיקת קישוריות לרשת
- ✅ יצירת תיקיית `SavedData`
- ✅ הפעלת האפליקציה

---

#### **אופציה ב: ידנית (אם הסקריפט לא עובד)**

##### **3.1 מצא את תיקיית ההתקנה**

לדוגמה: `C:\Program Files\Prisma\Panda\`

##### **3.2 גבה קובץ קיים (אם יש)**

```powershell
# אם יש usersettings.json קיים:
Copy-Item "C:\Program Files\Prisma\Panda\usersettings.json" `
          "C:\Program Files\Prisma\Panda\usersettings.json.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
```

##### **3.3 העתק את הקובץ הנקי**

```powershell
# מ-Downloads לתיקיית Panda
Copy-Item "C:\Users\roy.avrahami\Downloads\usersettings.cleaned.json" `
          "C:\Program Files\Prisma\Panda\usersettings.json" -Force
```

**⚠️ שים לב:** אם התיקייה מוגנת, תצטרך הרשאות Administrator:

```powershell
# פתח PowerShell כ-Administrator
Start-Process powershell -Verb RunAs

# ואז הרץ את פקודת ההעתקה
```

---

### **שלב 4: בדיקת קישוריות לרשת**

לפני שמפעילים את האפליקציה, בדוק שהשרתים נגישים:

```powershell
# Backend
Test-NetConnection -ComputerName 10.10.100.100 -Port 443

# Frontend
Test-NetConnection -ComputerName 10.10.10.100 -Port 443

# FrontendApi
Test-NetConnection -ComputerName 10.10.10.150 -Port 30443
```

**תוצאה מצופה:**
```
TcpTestSucceeded : True
```

**אם יש כשל:**
- ❌ בדוק Firewall (Windows Defender / תוכנת אנטי-וירוס)
- ❌ בדוק שאתה מחובר לרשת הנכונה (VPN?)
- ❌ בדוק שכתובות ה-IP נכונות

---

### **שלב 5: יצירת תיקיית SavedData**

קובץ התצורה מגדיר:
```json
"SavedData": {
  "Folder": "C:\\Panda\\SavedData"
}
```

**יצור את התיקייה:**

```powershell
New-Item -Path "C:\Panda\SavedData" -ItemType Directory -Force
```

**ודא שיש לך הרשאות כתיבה:**

```powershell
# בדיקה
echo "test" > C:\Panda\SavedData\test.txt
Remove-Item C:\Panda\SavedData\test.txt
```

אם הצליחה - מצוין! אם נכשלה - תצטרך הרשאות Administrator.

---

### **שלב 6: הפעלת האפליקציה**

#### **6.1 הפעלה ראשונה**

```powershell
# הרץ את האפליקציה
& "C:\Program Files\Prisma\Panda\Panda.exe"
```

או:
- פתח את תיקיית ההתקנה
- לחץ פעמיים על `Panda.exe`

---

#### **6.2 מה לחפש אחרי הפעלה?**

##### ✅ **אם האפליקציה נפתחת בהצלחה:**

תראה:
1. **Console Logs** - לוגים מ-Serilog
2. **חלון ראשי** - ממשק המשתמש
3. **חיבור לשרת** - `[INF] Connected to Backend: https://10.10.100.100/focus-server/`

##### ❌ **אם יש שגיאות:**

בדוק בלוגים:
```
[ERR] Failed to connect to https://10.10.100.100/focus-server/
[ERR] Connection timeout after 500ms
[ERR] Certificate validation failed
```

**פתרונות:**

| שגיאה | פתרון |
|-------|--------|
| `Connection timeout` | הגדל `GrpcTimeout` מ-500 ל-1500 |
| `Certificate validation failed` | התקן TLS certificate או הוסף `IgnoreSslErrors: true` (רק ל-Dev!) |
| `Failed to connect` | בדוק Firewall/VPN |
| `Cannot write to SavedData` | הוסף הרשאות כתיבה לתיקייה |

---

### **שלב 7: Smoke Tests**

אחרי שהאפליקציה נפתחה, בדוק פעולות בסיסיות:

#### ✅ **Test 1: Live View**
- פתח תצוגת Live
- ראה שנתונים זורמים (Spectrogram מתעדכן)

#### ✅ **Test 2: Historical Data**
- בחר `TimeStatus: Historical`
- טען רשומה מהעבר
- ראה שהנתונים נטענים

#### ✅ **Test 3: Frequency Range**
- שנה את טווח התדרים: `StartFrequency_hz` → `EndFrequency_hz`
- ראה שהספקטרוגרמה מתעדכנת

#### ✅ **Test 4: SavedData**
- שמור configuration/layout
- סגור ופתח מחדש
- ראה שההגדרות נשמרו

אם כל הבדיקות עברו - **מזל טוב! ההתקנה הושלמה!** 🎉

---

## 🔧 פתרון בעיות נפוצות

### **בעיה 1: האפליקציה לא נפתחת בכלל**

**אבחון:**
```powershell
# הרץ מ-PowerShell כדי לראות שגיאות
& "C:\Program Files\Prisma\Panda\Panda.exe"
```

**סיבות אפשריות:**
- ❌ חסרה תלות (dependency): .NET Framework, Visual C++ Redistributable
- ❌ Antivirus חוסם את האפליקציה
- ❌ קובץ exe פגום

**פתרון:**
1. התקן [.NET 6.0 Runtime](https://dotnet.microsoft.com/download/dotnet/6.0)
2. התקן [Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)
3. הוסף חריגה ב-Antivirus
4. הורד מחדש את ה-Installer

---

### **בעיה 2: האפליקציה נפתחת אבל מיד נסגרת (Crash)**

**אבחון:**
- בדוק Event Viewer:
  ```
  eventvwr.msc → Windows Logs → Application
  ```
- חפש שגיאות של `Panda.exe`

**סיבות אפשריות:**
- ❌ קובץ `usersettings.json` לא תקין
- ❌ חסרות הרשאות לתיקיית SavedData

**פתרון:**
```powershell
# תקף JSON
python -m json.tool "C:\Program Files\Prisma\Panda\usersettings.json"

# אם יש שגיאה - החלף עם הגרסה הנקייה
Copy-Item "C:\Users\roy.avrahami\Downloads\usersettings.cleaned.json" `
          "C:\Program Files\Prisma\Panda\usersettings.json" -Force
```

---

### **בעיה 3: האפליקציה נפתחת אבל אין חיבור לשרת**

**תסמינים:**
```
[ERR] GRPC connection failed
[ERR] Backend unreachable: https://10.10.100.100/focus-server/
```

**פתרון:**

#### **3.1 בדוק Firewall**

```powershell
# הוסף כלל Firewall
New-NetFirewallRule -DisplayName "Panda App - HTTPS" `
                    -Direction Outbound -LocalPort 443 -Protocol TCP -Action Allow
```

#### **3.2 בדוק אם VPN נדרש**

אם השרת הוא פנימי בארגון - ייתכן שצריך VPN פעיל.

#### **3.3 הגדל Timeouts**

ערוך `usersettings.json`:
```json
"Communication": {
  "GrpcTimeout": 1500,              // במקום 500
  "GrpcStreamMinTimeout_sec": 900   // במקום 600
}
```

---

### **בעיה 4: שגיאות TLS/SSL Certificate**

**תסמינים:**
```
[ERR] The SSL connection could not be established
[ERR] The remote certificate is invalid
```

**פתרון:**

#### **אופציה א: התקן Certificate (מומלץ)**

```powershell
# ייבא certificate
certutil -addstore "Root" C:\Path\To\focus-server.crt
```

#### **אופציה ב: Bypass זמני (רק Dev!)**

הוסף ל-`usersettings.json`:
```json
"Communication": {
  "IgnoreSslErrors": true  // ⚠️ רק לפיתוח!
}
```

---

## 📊 התאמת ביצועים

אם האפליקציה איטית או צורכת הרבה CPU:

### **הגדרות לחומרה בינונית:**

```json
"NumLiveScreens": 12,     // במקום 30
"RefreshRate": 10,        // במקום 20
"Defaults": {
  "Nfft": 512,            // במקום 1024
  "NumLinesToDisplay": 100  // במקום 200
}
```

### **הגדרות לחומרה חזקה (Production Monitoring):**

```json
"NumLiveScreens": 30,
"RefreshRate": 20,
"Defaults": {
  "Nfft": 2048,
  "NumLinesToDisplay": 500
}
```

---

## 🧪 הרצת הסקריפט האוטומטי

הדרך הקלה ביותר - **הרץ את הסקריפט המקיף שיצרתי:**

```powershell
cd C:\Projects\focus_server_automation
python scripts\panda_app_setup_guide.py
```

**הסקריפט יבצע:**
1. 🔍 איתור התקנת Panda
2. 📋 גיבוי קובץ תצורה קיים
3. ✅ התקנת `usersettings.cleaned.json`
4. 🌐 בדיקת קישוריות רשת
5. 📁 יצירת תיקיית SavedData
6. 🚀 הפעלת האפליקציה
7. 📊 דוח מפורט

**Output לדוגמה:**

```
======================================================================
Panda Application Setup Helper
======================================================================

🔍 Scanning for Panda installation...
✅ Found installation at: C:\Program Files\Prisma\Panda
✅ Executable: C:\Program Files\Prisma\Panda\Panda.exe

🔍 Scanning for usersettings.json...
✅ Found config at: C:\Program Files\Prisma\Panda\usersettings.json

======================================================================
📋 Configuration Setup
======================================================================

✅ Found cleaned config: C:\Users\roy.avrahami\Downloads\usersettings.cleaned.json

Use this config? (Y/n): Y

✅ Backed up existing config to: ...usersettings.json.backup_20251016_153045
✅ Installed clean config to: C:\Program Files\Prisma\Panda\usersettings.json

🌐 Checking network connectivity...
  ✅ Backend: https://10.10.100.100/focus-server/ - Reachable
  ✅ Frontend: https://10.10.10.100/liveView - Reachable
  ✅ FrontendApi: https://10.10.10.150:30443/... - Reachable

📁 Checking SavedData folder: C:\Panda\SavedData
✅ SavedData folder exists
✅ SavedData folder is writable

======================================================================
Panda Application Setup & Diagnostic Report
======================================================================

📦 Installation
  ✅ Path: C:\Program Files\Prisma\Panda
  ✅ Executable: C:\Program Files\Prisma\Panda\Panda.exe

⚙️  Configuration
  ✅ Config: C:\Program Files\Prisma\Panda\usersettings.json

✅ No issues detected!

======================================================================

Launch Panda application now? (Y/n): Y

🚀 Attempting to launch: C:\Program Files\Prisma\Panda\Panda.exe
✅ Application launched successfully
   Check if window appears. If not, check logs for errors.

✅ Setup complete!
```

---

## 📁 מבנה קבצים סופי

אחרי התקנה נכונה, זה איך זה אמור להיראות:

```
C:\Program Files\Prisma\Panda\
│
├── Panda.exe                           ← האפליקציה הראשית
├── usersettings.json                   ← התצורה הנקייה שלך
├── usersettings.json.backup_YYYYMMDD   ← גיבוי אוטומטי
├── [DLL files...]
└── [Other resources...]

C:\Panda\SavedData\
├── (saved configurations)
└── (exported data)
```

---

## ✅ Checklist סופי

לפני שפונים לתמיכה, ודא שביצעת את כל השלבים:

- [ ] **הרצת Installer:** `PandaAppInstaller-1.2.41.exe` כ-Administrator
- [ ] **אימתת התקנה:** מצאת את `Panda.exe` או `PandaApp.exe`
- [ ] **העתקת תצורה:** `usersettings.cleaned.json` → `usersettings.json`
- [ ] **בדיקת רשת:** Backend/Frontend/FrontendApi נגישים
- [ ] **יצירת SavedData:** התיקייה `C:\Panda\SavedData` קיימת וניתנת לכתיבה
- [ ] **הפעלה:** האפליקציה נפתחת ללא שגיאות
- [ ] **Smoke Test:** Live View עובד והנתונים זורמים

---

## 🆘 תמיכה

אם אחרי כל הצעדים האפליקציה עדיין לא עובדת:

### **אסוף מידע:**

1. **Event Viewer Logs:**
   ```powershell
   eventvwr.msc → Windows Logs → Application
   ```

2. **Application Logs** (אם יש):
   ```
   C:\Program Files\Prisma\Panda\logs\
   %AppData%\Panda\logs\
   ```

3. **Screenshot של השגיאה**

4. **קובץ התצורה:**
   ```powershell
   Get-Content "C:\Program Files\Prisma\Panda\usersettings.json"
   ```

### **צור Bug Ticket:**

השתמש בתבנית:

```markdown
**Environment:** Windows 10/11, Panda v1.2.41
**Issue:** Application does not start / crashes / no connection
**Steps Taken:**
  - Installed with: PandaAppInstaller-1.2.41.exe
  - Copied: usersettings.cleaned.json → usersettings.json
  - Network check: [Backend/Frontend reachable: Yes/No]
  - SavedData: [exists: Yes/No, writable: Yes/No]

**Error Messages:**
[paste console output / Event Viewer errors]

**usersettings.json:**
[attach file]

**Screenshots:**
[attach]
```

---

## 📞 קישורים מהירים

| משאב | מיקום |
|------|-------|
| **Installer** | `C:\Users\roy.avrahami\Downloads\PandaAppInstaller-1.2.41.exe` |
| **Cleaned Config** | `C:\Users\roy.avrahami\Downloads\usersettings.cleaned.json` |
| **Setup Script** | `c:\Projects\focus_server_automation\scripts\panda_app_setup_guide.py` |
| **Config Validator** | `c:\Projects\focus_server_automation\scripts\validate_and_clean_usersettings.py` |
| **Documentation** | `c:\Projects\focus_server_automation\docs\USERSETTINGS_VALIDATION_REPORT_HE.md` |

---

## 🚀 Quick Start TL;DR

אם אתה רק רוצה להתחיל מהר:

```powershell
# 1. התקן את האפליקציה
Start-Process "C:\Users\roy.avrahami\Downloads\PandaAppInstaller-1.2.41.exe" -Verb RunAs

# 2. אחרי ההתקנה, הרץ את הסקריפט
cd C:\Projects\focus_server_automation
python scripts\panda_app_setup_guide.py

# 3. הסקריפט יטפל בהכל - פשוט עקוב אחרי ההוראות
```

**זהו - זה באמת פשוט!** 🎉

---

**הוכן על ידי:** QA Automation Architect  
**תאריך:** 16 אוקטובר 2025  
**גרסה:** 1.0  
**סטטוס:** ✅ **Production Ready**

