# פתרון בעיה: Runner Service לא מתחיל

**בעיה:** `Cannot open actions.runner.* service`  
**פתרון:** הרצת Runner ישירות (לא כשירות)

---

## 🔧 פתרון מהיר: הרץ Runner ישירות

אם ה-service לא עובד, אתה יכול להריץ את ה-runner ישירות:

```powershell
# לך לתיקיית ה-runner
cd C:\actions-runner

# הרץ את ה-runner ישירות
.\run.cmd
```

**⚠️ חשוב:**
- ה-runner ירוץ כל עוד ה-PowerShell פתוח
- אם תסגור את החלון, ה-runner יעצור
- זה טוב לבדיקה, אבל לא מומלץ לשימוש קבוע

---

## 🔧 פתרון קבוע: תיקון ה-Service

אם אתה רוצה שה-runner ירוץ כשירות:

### שלב 1: הסר את ה-Service הישן

```powershell
cd C:\actions-runner

# אם יש תיקיית svc, הסר את ה-service
if (Test-Path .\svc) {
    .\svc\stop.cmd
    .\svc\uninstall.cmd
}
```

### שלב 2: התקן מחדש כשירות

```powershell
# פתח PowerShell כ-Administrator
cd C:\actions-runner

# התקן כשירות
.\config.cmd --runasservice

# או אם יש תיקיית svc:
.\svc\install.cmd
.\svc\start.cmd
```

---

## ✅ בדיקה: האם ה-Runner עובד?

### דרך 1: בדוק ב-GitHub

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/21
2. אחרי כמה שניות, ה-Status צריך להשתנות ל-**Online** (ירוק)

### דרך 2: הרץ Workflow לבדיקה

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/actions
2. בחר: **Smoke Tests**
3. לחץ: **Run workflow**
4. ה-workflow צריך להתחיל לרוץ תוך כמה שניות

---

## 💡 המלצה

**לשימוש זמני (מהבית):**
- הרץ את ה-runner ישירות עם `.\run.cmd`
- זה יעבוד כל עוד ה-PowerShell פתוח

**לשימוש קבוע:**
- תתקן את ה-service (ראה שלב 2)
- ה-runner ירוץ תמיד, גם אחרי הפעלה מחדש

---

**עודכן לאחרונה:** 2025-11-19

