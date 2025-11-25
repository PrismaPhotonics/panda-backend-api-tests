# איך לקבל GitHub Actions Runner Registration Token
# How to Get GitHub Actions Runner Registration Token

**תאריך:** 2025-01-XX  
**מטרה:** הסבר מפורט איך לקבל registration token להגדרת self-hosted runner

---

## 📋 שלב אחר שלב

## שלב 1: התחבר ל-GitHub

1. פתח דפדפן ולך ל: https://github.com
2. התחבר לחשבון שלך (אם אתה לא מחובר)

---

## שלב 2: לך ל-Repository Settings

1. לך ל-repository:
   ```
   https://github.com/PrismaPhotonics/panda-backend-api-tests
   ```

2. לחץ על **"Settings"** (בתפריט העליון של ה-repository)

   ![Settings location](https://docs.github.com/assets/images/help/repository/repo-actions-settings.png)

---

## שלב 3: לך ל-Actions → Runners

1. בתפריט השמאלי, תחת **"Actions"**, לחץ על **"Runners"**

   או לך ישירות ל:
   ```
   https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
   ```

---

## שלב 4: צור Runner חדש

1. לחץ על הכפתור **"New self-hosted runner"** (כפתור ירוק/כחול)

   ![New runner button](https://docs.github.com/assets/images/help/settings/actions-runner-add-runner.png)

---

## שלב 5: בחר מערכת הפעלה

1. GitHub יציג לך מסך עם הוראות התקנה
2. **בחר את מערכת ההפעלה** של ה-slave laptop:
   - **Windows** - אם ה-slave laptop הוא Windows
   - **Linux** - אם ה-slave laptop הוא Linux
   - **macOS** - אם ה-slave laptop הוא Mac

   ![Select OS](https://docs.github.com/assets/images/help/settings/actions-runner-os-selection.png)

---

## שלב 6: העתק את ה-Registration Token

1. לאחר בחירת מערכת ההפעלה, GitHub יציג:
   - הוראות התקנה
   - **Registration Token** (נראה כמו: `AXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`)

2. **העתק את ה-Token** - זה החשוב ביותר!

   ```
   לדוגמה:
   AXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```

   ⚠️ **חשוב:**
   - ה-token תקף **ל-1 שעה בלבד**
   - אחרי שעה, תצטרך לקבל token חדש
   - אל תשתף את ה-token עם אחרים

---

## שלב 7: השתמש ב-Token

השתמש ב-token הזה בסקריפט:

```powershell
# אפשרות 1: אינטראקטיבי
py scripts\setup_runner_on_slave_laptop.py
# כשהסקריפט שואל, הדבק את ה-token

# אפשרות 2: עם פרמטרים
py scripts\setup_runner_on_slave_laptop.py --token YOUR_TOKEN_HERE
```

---

## 📸 תמונות מסך (Screenshots)

### מיקום Settings:
```
Repository → Settings (בתפריט העליון)
```

### מיקום Runners:
```
Settings → Actions → Runners (בתפריט השמאלי)
```

### כפתור New Runner:
```
בדף Runners, לחץ על "New self-hosted runner"
```

---

## 🔗 קישורים ישירים

### לך ישירות ליצירת Runner:
```
https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/new
```

### לך לרשימת Runners:
```
https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
```

---

## ⚠️ פתרון בעיות

### לא רואה את הכפתור "New self-hosted runner":
- ודא שיש לך הרשאות **Admin** או **Maintain** ב-repository
- אם אין לך הרשאות, בקש מהמנהל להוסיף אותך

### Token לא עובד:
- ודא שהעתקת את כל ה-token (ללא רווחים)
- ודא שה-token לא פג תוקף (תקף ל-1 שעה)
- קבל token חדש

### לא רואה את התפריט "Runners":
- ודא שאתה ב-Settings של ה-repository
- ודא ש-Actions מופעל ב-repository

---

## 📝 הערות חשובות

1. **Token תקף ל-1 שעה בלבד**
   - אם עבר זמן, קבל token חדש

2. **Token הוא חד-פעמי**
   - כל runner צריך token משלו
   - אם אתה מוסיף runner נוסף, קבל token חדש

3. **Token הוא רגיש**
   - אל תשתף אותו
   - אל תעלה אותו ל-Git
   - השתמש בו רק פעם אחת להגדרת ה-runner

---

## 🎯 סיכום מהיר

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/new
2. בחר מערכת הפעלה (Windows/Linux)
3. העתק את ה-Token
4. השתמש ב-Token בסקריפט

---

## 📞 עזרה נוספת

אם יש בעיות:
- [GitHub Docs - Adding self-hosted runners](https://docs.github.com/en/actions/hosting-your-own-runners/adding-self-hosted-runners)
- [GitHub Docs - About self-hosted runners](https://docs.github.com/en/actions/hosting-your-own-runners/about-self-hosted-runners)

