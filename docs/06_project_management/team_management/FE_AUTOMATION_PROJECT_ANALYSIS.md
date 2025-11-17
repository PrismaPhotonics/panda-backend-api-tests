# ניתוח פרויקט FE Automation - רון
## FE Automation Project Analysis - Complete Structure, Tools & Infrastructure

**תאריך:** 2025-11-09  
**פרויקט:** Panda Test Automation (FE Automation)  
**מיקום:** `C:\Projects\focus_server_automation\ron_project\`

---

## 📁 מבנה הספריות (Directory Structure)

### מבנה הפרויקט המלא:

```
ron_project/
├── blocksAndRepo/              # Page Object Model (POM) - אובייקטי דפים
│   ├── __init__.py
│   └── panda/                  # מודולים ספציפיים ל-Panda
│       ├── __init__.py
│       ├── alerts/             # אובייקטי דפים - Alerts
│       │   ├── __init__.py
│       │   ├── AlertsBlocks.py      # Building blocks ל-Alerts
│       │   ├── AlertsFilterRepo.py   # Repository - אלמנטים של פילטר
│       │   └── AlertsRepo.py         # Repository - אלמנטים של Alerts
│       ├── entities/           # מודלים של ישויות (Data Models)
│       │   ├── __init__.py
│       │   ├── Alert.py              # מודל Alert
│       │   ├── AlertsFilter.py       # מודל AlertsFilter
│       │   ├── AlertsTableColumns.py # מודל עמודות טבלה
│       │   ├── AlertTableLine.py     # מודל שורת טבלה
│       │   ├── InvestigateData.py    # מודל נתוני Investigation
│       │   ├── JournalAlertsTableLine.py
│       │   └── LiveViewAlertsFilter.py
│       ├── investigator/        # אובייקטי דפים - Investigation
│       │   ├── __init__.py
│       │   ├── InvestigatorBlocks.py  # Building blocks ל-Investigation
│       │   └── InvestigatorRepo.py    # Repository - אלמנטים
│       ├── login/               # אובייקטי דפים - Login
│       │   ├── __init__.py
│       │   └── PandaLoginBlocks.py    # Building blocks ל-Login
│       ├── map/                 # אובייקטי דפים - Map
│       │   ├── __init__.py
│       │   ├── MapBlocks.py          # Building blocks ל-Map
│       │   └── MapRepo.py            # Repository - אלמנטים
│       ├── PandaBaseBlocks.py   # Base building blocks משותפים
│       └── PandaNativeRepo.py   # Native repository - אלמנטים בסיסיים
│
├── common/                      # כלים ופונקציות משותפות
│   ├── appium/                 # Appium infrastructure
│   │   ├── AppiumServer.py     # ניהול Appium Server
│   │   ├── AppiumTools.py      # כלי עבודה ל-Appium (win/web)
│   │   ├── AppiumWeb.py        # WebView automation (Selenium)
│   │   └── AppiumWindows.py    # Windows automation (WinAppDriver)
│   ├── CommonOps.py            # פעולות משותפות (processes, files, etc.)
│   ├── Logging.py              # מערכת לוגים
│   ├── PythonHelper.py         # עזרים ב-Python
│   └── VideoRecorder.py        # הקלטת וידאו של טסטים (FFmpeg)
│
├── config/                      # קבצי קונפיגורציה
│   └── project.properties      # הגדרות פרויקט (paths, credentials, etc.)
│
├── tests/                       # קבצי בדיקות
│   ├── conftest.py             # Pytest fixtures ו-setup
│   └── panda/                  # בדיקות Panda
│       ├── regression/         # בדיקות רגרסיה
│       │   └── alerts/
│       │       └── CreateNewAnalyzeFromAlert.py
│       ├── sanity/             # בדיקות Sanity
│       │   ├── alerts/         # בדיקות Alerts
│       │   │   ├── TestAlerts.py
│       │   │   ├── TestAlertsFilter.py
│       │   │   └── TestAlertsNotes.py
│       │   ├── analyze_alert/  # בדיקות Analyze Alert
│       │   │   └── TestsAnalyzeAlerts.py
│       │   ├── frequencyFilter/ # בדיקות Frequency Filter
│       │   │   └── TestsFrequencyFilter.py
│       │   ├── investigations/  # בדיקות Investigations
│       │   │   └── TestInvestigations.py
│       │   ├── login/          # בדיקות Login
│       │   │   └── TestsLogin.py
│       │   ├── map/            # בדיקות Map
│       │   │   └── testMap.py
│       │   └── preDefinedAnalysisTemplates/ # בדיקות Templates
│       │       ├── from_tomer.json
│       │       ├── TemplatesSanity.json
│       │       └── TestAnalysisTemplate.py
│       ├── smoke/              # בדיקות Smoke
│       │   └── TestsSmoke.py
│       └── testHelpers/        # עזרי בדיקה
│           ├── ApiHelper.py    # עזרים ל-API calls
│           └── TestHelper.py   # עזרים כלליים
│
├── pytest.ini                  # הגדרות pytest
├── requirements.txt            # תלויות Python
└── README.md                   # תיעוד פרויקט
```

---

## 🛠️ כלים (Tools)

### 1. כלי אוטומציה (Automation Tools)

#### **Appium**
- **תפקיד:** אוטומציה של אפליקציות Windows Desktop
- **גרסה:** Appium-Python-Client
- **שימוש:**
  - WinAppDriver - לשליטה ב-Windows Native UI
  - WebView automation - לשליטה ב-WebView2 (embedded browser)
- **פורט:** 4723 (localhost)
- **קבצים:**
  - `common/appium/AppiumServer.py` - ניהול Appium Server
  - `common/appium/AppiumWindows.py` - Windows automation
  - `common/appium/AppiumWeb.py` - WebView automation
  - `common/appium/AppiumTools.py` - כלי עבודה משותפים

#### **Selenium**
- **תפקיד:** אוטומציה של WebView2 (embedded browser באפליקציה)
- **שימוש:** EdgeDriver לשליטה ב-WebView
- **פורט:** 9222 (remote debugging port)
- **קבצים:**
  - `common/appium/AppiumWeb.py` - Selenium WebDriver integration

#### **WinAppDriver**
- **תפקיד:** Windows Application Driver לשליטה ב-Native Windows UI
- **שימוש:** דרך Appium (לא ישירות)
- **קבצים:**
  - `common/appium/AppiumWindows.py` - WinAppDriver setup

### 2. כלי פיתוח (Development Tools)

#### **Python**
- **גרסה:** Python 3.x
- **שימוש:** שפת פיתוח ראשית

#### **pytest**
- **תפקיד:** Framework להרצת בדיקות
- **הגדרות:** `pytest.ini`
- **Markers:**
  - `@pytest.mark.smoke` - בדיקות Smoke
  - `@pytest.mark.sanity` - בדיקות Sanity
  - `@pytest.mark.regression` - בדיקות Regression
- **Fixtures:** מוגדרים ב-`tests/conftest.py`

#### **requests**
- **תפקיד:** HTTP client ל-API calls
- **שימוש:** שליחת alerts דרך API, authentication
- **קבצים:**
  - `tests/panda/testHelpers/ApiHelper.py`

### 3. כלי עזר (Utility Tools)

#### **FFmpeg**
- **תפקיד:** הקלטת וידאו של בדיקות
- **שימוש:** הקלטת מסך בזמן הרצת בדיקות
- **קבצים:**
  - `common/VideoRecorder.py`
- **פורמט:** MP4
- **תיקייה:** `videos/`

#### **OpenCV (opencv-python)**
- **תפקיד:** עיבוד תמונות
- **שימוש:** זיהוי אלמנטים, OCR (עם pytesseract)

#### **pytesseract**
- **תפקיד:** OCR - זיהוי טקסט בתמונות
- **שימוש:** קריאת טקסט מ-screenshots

#### **psutil**
- **תפקיד:** ניטור משאבי מערכת
- **שימוש:** ניטור זיכרון, CPU של אפליקציית Panda
- **קבצים:**
  - `common/CommonOps.py` - `start_resource_monitor()`

#### **pywin32**
- **תפקיד:** Windows API bindings
- **שימוש:** שליטה ב-Windows (חלונות, processes)
- **קבצים:**
  - `common/appium/AppiumWindows.py` - `win32gui` לזיהוי חלונות

### 4. כלי תצורה (Configuration Tools)

#### **configparser**
- **תפקיד:** קריאת קבצי `.properties`
- **שימוש:** קריאת `config/project.properties`
- **קבצים:**
  - `common/CommonOps.py` - `get_property()`

---

## 🏗️ תשתיות (Infrastructure)

### 1. אפליקציית Panda

#### **מיקום התקנה:**
```
C:\Program Files\Prisma\PandaApp\PandaApp-1.2.44.exe
```

#### **פרטים:**
- **גרסה:** 1.2.44 (מוגדר ב-`project.properties`)
- **Process Name:** `PandaApp-1.2.44.exe`
- **סוג:** Windows Desktop Application (WPF/WinUI)
- **WebView:** WebView2 (embedded browser)

#### **תיקיות משתמש:**
- **Templates:** `%APPDATA%\Roaming\Prisma\PandaApp\Templates.json`
- **Saved Data:** `C:\Panda\SavedData` (מוגדר ב-usersettings.json)

### 2. Appium Server

#### **פרטים:**
- **כתובת:** `http://127.0.0.1:4723`
- **סטטוס:** `/status` endpoint
- **הפעלה:** אוטומטית דרך `AppiumServer.py`
- **ניהול:** Start/Stop אוטומטי ב-`conftest.py`

### 3. WebView2 Remote Debugging

#### **פרטים:**
- **פורט:** 9222
- **כתובת:** `http://127.0.0.1:9222`
- **שימוש:** Selenium EdgeDriver מתחבר ל-WebView2
- **הגדרה:** Environment variable `WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS="--remote-debugging-port=9222"`

### 4. API Backend

#### **כתובת בסיס:**
```
https://10.10.100.100/prisma/api/
```

#### **Endpoints בשימוש:**

**1. Authentication:**
```
POST /auth/login
Body: {"username": "prisma", "password": "prisma"}
Response: Session cookies
```

**2. Push Alert:**
```
POST /prisma-210-1000/api/push-to-rabbit
Body: Alert JSON payload
```

#### **פרטי חיבור:**
- **Base URL:** `https://10.10.100.100/prisma/api/` (מ-`project.properties`)
- **Username:** `prisma` (default)
- **Password:** `prisma` (default)
- **SSL Verification:** Disabled (self-signed cert)

### 5. RabbitMQ

#### **פרטים:**
- **IP:** `10.10.10.102` (מ-`project.properties` - `externalRabbitIp`)
- **תפקיד:** Message Queue לשליחת alerts
- **שימוש:** שליחת alerts דרך API endpoint (`/api/push-to-rabbit`)

#### **Site ID:**
- **Site ID:** `prisma-210-1000` (מ-`project.properties`)

### 6. תשתיות נוספות (לא ישירות)

#### **Focus Server Backend:**
- **URL:** `https://10.10.100.100/focus-server/`
- **שימוש:** אפליקציית Panda מתחברת ל-Backend

#### **Frontend UI:**
- **URL:** `https://10.10.100.100/liveView`
- **שימוש:** אפליקציית Panda מציגה את ה-UI

---

## 📋 קבצי קונפיגורציה (Configuration Files)

### 1. `config/project.properties`

**תוכן:**
```properties
# Platform type
automationPlatform=windows

# Application path
appUnderTest="C:\Program Files\Prisma\PandaApp\PandaApp-1.2.44.exe"

# Login credentials
pandaLoginUser=prisma
pandaLoginPwd=prisma

# Process name
pandaProcName=PandaApp-1.2.44.exe

# External RabbitMQ IP
externalRabbitIp=10.10.10.102

# Site ID
alertGeneratorSiteId=prisma-210-1000

# App version
pandaAppVersion=1.2.44

# API Base URL
apiBaseUrl=https://10.10.100.100/prisma/api/

# Alert end time after push (seconds)
alertEndTimeAfterPush=170
```

### 2. `pytest.ini`

**תוכן:**
```ini
[pytest]
testpaths = tests
python_files = test_*.py *_test.py Test*.py
python_classes = Test*
python_functions = test_*

markers =
    smoke: smoke tests - quick validation tests
    sanity: sanity tests - core functionality tests
    regression: regression tests - comprehensive tests
```

### 3. `requirements.txt`

**תלויות:**
```
selenium
requests
Appium-Python-Client
pytest
pywin32
opencv-python
psutil
```

**הערה:** ייתכן שיש תלויות נוספות לא מפורטות (כמו `pytesseract`, `Pillow`)

---

## 🔄 תהליכי עבודה (Workflows)

### 1. תהליך הרצת בדיקה

```
1. Session Setup (conftest.py - suite_setup)
   ├── Kill existing PandaApp process
   ├── Start resource monitor (psutil)
   └── Start Appium Server (if not running)

2. Test Setup (conftest.py - per_test)
   ├── Start video recording (FFmpeg)
   ├── Launch PandaApp with WebView2 debugging
   ├── Connect WinAppDriver (Windows UI)
   ├── Connect EdgeDriver (WebView2)
   ├── Bypass certificate validation
   └── Auto-login (unless test is login test)

3. Test Execution
   ├── Use Building Blocks (AlertsBlocks, MapBlocks, etc.)
   ├── Interact with UI (win_driver / web_driver)
   └── Verify results

4. Test Teardown (conftest.py - per_test)
   ├── Take screenshot if failed
   ├── Stop video recording (keep if failed)
   ├── Quit drivers
   └── Kill PandaApp process

5. Session Teardown (conftest.py - suite_setup)
   ├── Stop resource monitor
   └── Stop Appium Server (if we started it)
```

### 2. תהליך שליחת Alert

```
1. Create Alert object (Alert.py)
   ├── alert_id
   ├── dof_m (distance)
   ├── classId
   └── severity

2. Authenticate with API
   ├── POST /auth/login
   └── Get session cookies

3. Push Alert to RabbitMQ
   ├── POST /prisma-210-1000/api/push-to-rabbit
   └── Alert JSON payload

4. Wait for alert to appear in UI
   └── Verify alert details in sidebar
```

### 3. תהליך Page Object Model

```
1. Repository Layer (Repo files)
   └── Define element locators (XPath, ID, etc.)

2. Building Blocks Layer (Blocks files)
   ├── Use AppiumTools (win_driver / web_driver)
   ├── Implement business logic
   └── Return entities/models

3. Test Layer
   ├── Use Building Blocks
   ├── Create test data
   └── Assert results
```

---

## 📊 סטטיסטיקות פרויקט

### קבצי בדיקה:
- **Sanity Tests:** 8 קבצים
- **Smoke Tests:** 1 קובץ
- **Regression Tests:** 1 קובץ
- **Total Test Files:** ~10 קבצים

### Page Objects:
- **Alerts:** 3 קבצים (Blocks + 2 Repos)
- **Login:** 1 קובץ (Blocks)
- **Map:** 2 קבצים (Blocks + Repo)
- **Investigator:** 2 קבצים (Blocks + Repo)
- **Base:** 2 קבצים (BaseBlocks + NativeRepo)
- **Total:** ~10 קבצי Page Objects

### Entities/Models:
- **7 קבצי מודלים** (Alert, AlertsFilter, etc.)

### Common Utilities:
- **8 קבצים** (Appium, Logging, Video, etc.)

---

## 🔧 תלויות חיצוניות (External Dependencies)

### 1. Appium Server
- **דרישה:** Appium Server מותקן ומריץ
- **פורט:** 4723
- **ניהול:** אוטומטי דרך `AppiumServer.py`

### 2. WinAppDriver
- **דרישה:** Windows Application Driver מותקן
- **שימוש:** דרך Appium (לא ישירות)

### 3. EdgeDriver
- **דרישה:** Microsoft Edge WebDriver
- **שימוש:** Selenium WebDriver לשליטה ב-WebView2

### 4. FFmpeg
- **דרישה:** FFmpeg מותקן ב-PATH
- **שימוש:** הקלטת וידאו של בדיקות

### 5. Tesseract OCR
- **דרישה:** Tesseract מותקן (עבור pytesseract)
- **שימוש:** OCR לזיהוי טקסט

---

## 🌐 חיבורי רשת (Network Connections)

### חיבורים מקומיים (Localhost):
- **Appium Server:** `http://127.0.0.1:4723`
- **WebView2 Debugging:** `http://127.0.0.1:9222`

### חיבורים חיצוניים (External):
- **API Backend:** `https://10.10.100.100/prisma/api/`
- **RabbitMQ:** `10.10.10.102` (לא ישירות, דרך API)

---

## 📝 הערות חשובות

### 1. ארכיטקטורת אוטומציה כפולה:
הפרויקט משתמש ב-**שני drivers**:
- **WinAppDriver** - לשליטה ב-Windows Native UI
- **Selenium EdgeDriver** - לשליטה ב-WebView2 (embedded browser)

### 2. WebView2 Remote Debugging:
האפליקציה מופעלת עם `--remote-debugging-port=9222` כדי לאפשר ל-Selenium להתחבר ל-WebView2.

### 3. Video Recording:
כל בדיקה מוקלטת בווידאו. הווידאו נשמר רק אם הבדיקה נכשלה.

### 4. Resource Monitoring:
הפרויקט עוקב אחר משאבי מערכת (זיכרון, CPU) של אפליקציית Panda בזמן הרצת בדיקות.

### 5. Auto-Login:
רוב הבדיקות מתחברות אוטומטית, למעט בדיקות Login ספציפיות.

---

**עודכן:** 2025-11-09  
**נוצר על ידי:** QA Automation Team

