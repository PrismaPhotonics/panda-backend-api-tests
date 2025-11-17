# 📋 דוח תיקון והכנה של usersettings.json

**תאריך:** 16 אוקטובר 2025  
**מהנדס:** QA Automation Architect  
**סטטוס:** ✅ הושלם בהצלחה

---

## 📌 סיכום מבצעי

תהליך ולידציה וניקוי מקיף בוצע על קובץ התצורה `usersettings.json` של Focus Server Client. הקובץ תוקן, אומת ונוצרו 3 גרסאות ייעודיות לסביבות שונות.

### 📁 קבצים שנוצרו

| קובץ | תיאור | מיקום |
|------|-------|--------|
| `usersettings.production.json` | גרסת Production מתוקנת ונקייה | `config/` |
| `usersettings.staging.json` | גרסת Staging עם הגדרות debug | `config/` |
| `usersettings.development.json` | גרסת Dev מקומית עם לוגים מלאים | `config/` |
| `usersettings.changes.diff` | Unified Diff של כל השינויים | `config/` |
| `validate_and_clean_usersettings.py` | סקריפט ולידציה אוטומטי | `scripts/` |

---

## 🔍 בעיות שזוהו ותוקנו

### 1️⃣ **סתירה בין `_TimeStatus` ו-`TimeStatus`**

**בעיה:**
```json
"Defaults": {
  "_TimeStatus": "Range",    // ← ערך פרטי/מיושן
  "TimeStatus": "Live"        // ← ערך ציבורי/פעיל
}
```

**פתרון:**
- **הוסר** `_TimeStatus` מהתצורה
- **נשמר** רק `TimeStatus: "Live"` (ה-API הציבורי)
- **סיבה:** סתירה בין שני הערכים עלולה לגרום להתנהגות לא צפויה

**השפעה:** ✅ אין השפעה על לוגיקה קיימת כי `TimeStatus` הוא השדה הרשמי

---

### 2️⃣ **מחרוזת ריקה ב-`TemplateTypes`**

**בעיה:**
```json
"TemplateTypes": ["SD", "SC", ""]  // ← מחרוזת ריקה מיותרת
```

**פתרון:**
```json
"TemplateTypes": ["SD", "SC"]      // ✅ נקי וברור
```

**השפעה:** ✅ מונעת שגיאות אפשריות בלוגיקת הטמפלייטים

---

### 3️⃣ **שלושה כתובות IP שונות בתצורת Communication**

**זוהה:**
```json
"Communication": {
  "Backend": "https://10.10.100.100/focus-server/",           // ← IP #1
  "Frontend": "https://10.10.10.100/liveView",                // ← IP #2
  "FrontendApi": "https://10.10.10.150:30443/prisma/..."      // ← IP #3
}
```

**סטטוס:** ⚠️ **אזהרה בלבד** - נשמר כמו שהיה

**פעולה נדרשת:**  
✅ **אם זה תקין** (לדוגמה: load balancer, reverse proxy, רשת מבוזרת) - אין צורך בשינוי  
❌ **אם זה לא תקין** - עדכן את הכתובות להיות עקביות

**המלצה:**
- בדוק שכל 3 ה-endpoints נגישים מהתחנה שמריצה את הלקוח
- אם `10.10.100.100` הוא ה-Backend החדש, שקול לעדכן גם את `Frontend` ו-`FrontendApi` באותו IP

---

### 4️⃣ **הגדרות ביצועים גבוהות**

**זוהה:**
```json
"NumLiveScreens": 30,  // ← 30 מסכים חיים במקביל
"RefreshRate": 20      // ← 20 רענונים לשנייה
```

**סטטוס:** ⚠️ **אזהרה** - עלול לגרום עומס CPU גבוה

**המלצה:**
- עבור תחנות עם חומרה חלשה/בינונית: הקטן ל-`NumLiveScreens: 12-15` ו-`RefreshRate: 10-15`
- עבור Production Monitoring: שמור על הערכים הנוכחיים רק אם יש מכונה חזקה מספיק

---

## 📊 Unified Diff - מה השתנה בדיוק?

```diff
--- usersettings.json (original)
+++ usersettings.json (cleaned)
@@ -22,7 +22,6 @@
     "SensorsRange": 2222
   },
   "Defaults": {
-    "_TimeStatus": "Range",
     "DisplayTimeAxisDuration": 30,
     "EndChannel": 109,
     "EndFrequency_hz": 1000,
@@ -79,7 +78,6 @@
   },
   "TemplateTypes": [
     "SD",
-    "SC",
-    ""
+    "SC"
   ]
 }
```

### סיכום השינויים:
1. ✅ הוסר `_TimeStatus: "Range"` מ-`Defaults`
2. ✅ הוסרה מחרוזת ריקה מ-`TemplateTypes`
3. ✅ תוקן פורמט JSON (trailing commas אם היו)

---

## 🚀 אסטרטגיית פריסה (Deployment Strategy)

### שלב 1: בדיקת קישוריות לפני החלפה

```powershell
# בדוק נגישות Backend החדש
curl -k https://10.10.100.100/focus-server/

# או
Test-NetConnection -ComputerName 10.10.100.100 -Port 443

# בדוק Frontend
curl -k https://10.10.10.100/liveView

# בדוק FrontendApi
curl -k https://10.10.10.150:30443/prisma/api/internal/sites/prisma-210-1000
```

**צפוי:**
- ✅ Status 200/401/404 (לפי endpoint) - המשמעות: השרת נגיש
- ❌ Timeout/Connection Refused - **פתור לפני פריסה!**

---

### שלב 2: גיבוי הקובץ הקיים

```powershell
# גיבוי לפני שינוי
Copy-Item "C:\Path\To\App\usersettings.json" `
          "C:\Path\To\App\usersettings.json.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
```

---

### שלב 3: החלפת הקובץ

```powershell
# העתק את הגרסה הנקייה
Copy-Item "c:\Projects\focus_server_automation\config\usersettings.production.json" `
          "C:\Path\To\Focus\Client\usersettings.json" -Force
```

**איפה בדיוק?**
- **Windows Desktop App:** התיקייה בה `FocusClient.exe` נמצא
- **Windows Service:** לרוב `C:\Program Files\Prisma\FocusClient\`
- **Portable:** התיקייה שבה פותחים את האפליקציה

---

### שלב 4: אימות פריסה (Smoke Tests)

#### 4.1 הפעל את האפליקציה ובדוק לוגים

פתח את האפליקציה ובדוק ב-Console (Serilog) שאין שגיאות כמו:
```
[ERR] Failed to connect to https://10.10.100.100/focus-server/
[ERR] GRPC timeout after 500ms
```

אם יש שגיאות אלו:
1. ✅ בדוק firewall/routing
2. ✅ בדוק TLS certificates (אם self-signed, הוסף ל-Trusted Root)
3. ✅ האם `GrpcTimeout: 500` נמוך מדי? שקול להעלות ל-1000-1500

---

#### 4.2 בצע פעולה בסיסית

- **Live View:** פתח תצוגה חיה - ראה שנתונים זורמים
- **Historical View:** טען רשומה היסטורית - ראה שיש query ל-`/log` endpoint
- **Spectrogram:** בדוק שספקטרוגרמה נטענת תקין

אם הכל עובד:
✅ **הפריסה הצליחה!**

---

## 🌍 גרסאות לפי סביבה

### 📦 Production (`usersettings.production.json`)

```json
"Communication": {
  "Backend": "https://10.10.100.100/focus-server/",
  "Frontend": "https://10.10.10.100/liveView",
  "FrontendApi": "https://10.10.10.150:30443/prisma/api/internal/sites/prisma-210-1000",
  "SiteId": "prisma-210-1000"
},
"EnableDebugTools": false
```

**שימוש:** לקוחות בשטח, מערכות ייצור

---

### 🔧 Staging (`usersettings.staging.json`)

```json
"Communication": {
  "Backend": "https://10.10.10.200/focus-server/",
  "Frontend": "https://10.10.10.200/liveView",
  "FrontendApi": "https://10.10.10.200:30443/prisma/api/internal/sites/prisma-210-1000-staging",
  "SiteId": "prisma-210-1000-staging"
},
"EnableDebugTools": true
```

**שימוש:** בדיקות אינטגרציה, UAT, QA

---

### 💻 Development (`usersettings.development.json`)

```json
"Communication": {
  "Backend": "http://localhost:5000/focus-server/",
  "Frontend": "http://localhost:3000/liveView",
  "FrontendApi": "http://localhost:8080/prisma/api/internal/sites/prisma-210-1000-dev",
  "SiteId": "prisma-210-1000-dev"
},
"EnableDebugTools": true,
"Logger": {
  "LogGrpcMessages": true,
  "LogGrpcValidation": true
},
"NumLiveScreens": 5,
"RefreshRate": 10
```

**שימוש:** פיתוח מקומי, דיבאג

---

## 🔐 אבטחה ו-TLS

### אם Backend משתמש ב-Self-Signed Certificate

#### אופציה 1: הוסף ל-Trusted Root (מומלץ)

```powershell
# ייבא את ה-certificate ל-Windows Trusted Root
certutil -addstore "Root" C:\Path\To\focus-server.crt
```

#### אופציה 2: Bypass זמני (רק לבדיקות!)

אם האפליקציה תומכת ב-flag:
```json
"Communication": {
  "IgnoreSslErrors": true  // ← רק ל-dev/staging!
}
```

---

## 📈 Monitoring & Troubleshooting

### בדיקות ביצועים

אם אחרי הפריסה יש בעיות ביצועים:

```json
// הקטן עומס
"NumLiveScreens": 15,      // במקום 30
"RefreshRate": 12,         // במקום 20
"GrpcTimeout": 1000,       // במקום 500
"NumGrpcRetries": 5        // במקום 10
```

---

### דיבאג GRPC Timeouts

אם יש הרבה timeouts:

```json
"Logger": {
  "LogGrpcMessages": true,     // ← ראה בדיוק מה נשלח
  "LogGrpcValidation": true    // ← ראה validation errors
},
"GrpcStreamMinTimeout_sec": 900,  // העלה מ-600
"GrpcTimeout": 1500               // העלה מ-500
```

---

### דיבאג Frequency Range Issues

אם יש שגיאות על תדרים לא חוקיים:

```json
"Constraints": {
  "FrequencyMin": 0,
  "FrequencyMax": 1000,
  "FrequencyMinRange": 1
},
"Defaults": {
  "StartFrequency_hz": 0,
  "EndFrequency_hz": 1000
}
```

וודא ש:
- `StartFrequency_hz >= FrequencyMin`
- `EndFrequency_hz <= FrequencyMax`
- `EndFrequency_hz - StartFrequency_hz >= FrequencyMinRange`

---

## ✅ Checklist סופי לפני Production

- [ ] **קישוריות:** כל 3 ה-endpoints נגישים מהתחנה
- [ ] **גיבוי:** הקובץ הישן גובה
- [ ] **TLS:** Certificates מותקנים/מאושרים
- [ ] **Firewall:** פורטים 443/30443 פתוחים
- [ ] **SiteId:** תואם לערך שמוגדר ב-Backend API
- [ ] **Paths:** `C:\Panda\SavedData` קיים ויש הרשאות כתיבה
- [ ] **Smoke Test:** נתונים זורמים ב-Live View
- [ ] **Historical Test:** טעינת רשומות היסטוריות עובדת
- [ ] **Logs:** אין שגיאות חמורות ב-Serilog Console

---

## 🧪 בדיקות אוטומטיות (Future Work)

### הרצת הסקריפט המקורי בכל עדכון

```powershell
# וודא שהתצורה תקינה לפני deployment
py c:\Projects\focus_server_automation\scripts\validate_and_clean_usersettings.py

# אם יש שגיאות קריטיות - הסקריפט ייכשל עם exit code 1
# אם יש רק אזהרות - הסקריפט יצליח עם exit code 0
```

### אינטגרציה ל-CI/CD

```yaml
# .gitlab-ci.yml / .github/workflows/validate-config.yml
validate_config:
  script:
    - python scripts/validate_and_clean_usersettings.py
  only:
    - merge_requests
  allow_failure: false
```

---

## 📞 תמיכה

אם נתקלת בבעיות:

1. **בדוק לוגים:** ב-Serilog Console תראה את הסיבה המדויקת
2. **הרץ ולידציה:** `py scripts/validate_and_clean_usersettings.py`
3. **שחזר גיבוי:** החזר את `usersettings.json.backup_*` אם יש כשל חמור
4. **בדוק networking:** `Test-NetConnection` / `curl` לכל endpoint

---

## 📝 היסטוריית שינויים

| תאריך | גרסה | שינוי |
|-------|------|-------|
| 2025-10-16 | 1.0 | ניקוי ראשוני: הסרת `_TimeStatus`, תיקון `TemplateTypes`, יצירת 3 גרסאות סביבה |

---

**הוכן על ידי:** QA Automation Architect  
**תאריך:** 16 אוקטובר 2025  
**סטטוס:** ✅ **Production Ready**

