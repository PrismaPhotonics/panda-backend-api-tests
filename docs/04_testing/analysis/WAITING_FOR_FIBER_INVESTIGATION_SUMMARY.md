# סיכום חקירת בעיית "waiting for fiber"

**תאריך:** 2025-11-08  
**חוקר:** AI Assistant  
**סקריפט:** `scripts/investigate_waiting_for_fiber.py`

---

## 📊 תוצאות החקירה

### ✅ 1. בדיקת pz_core_libs

**תוצאה:** נמצא קובץ אחד עם שגיאה דומה (אבל לא הקובץ הנכון)

**קבצים שנמצאו:**
- `pz/microservices/backoffice_v2/services/known_locations.py`
  - שגיאה: `"cannot proceed without it"` (שורה 26)
  - זה לא קשור לבעיה שלנו - זה רק validation ב-backoffice service

**מסקנה:** השגיאה `"Cannot proceed: Missing required fiber metadata fields: prr"` **לא נמצאה בקוד של PZ** - כנראה מגיעה מ-`pz_core_libs` (package חיצוני).

---

### ✅ 2. בדיקת Git History של pz_core_libs

**תוצאה:** נמצאו 2 commits ב-2 השבועות האחרונים

**Commits שנמצאו:**
1. `3bd8cfcb6` - "Merged in replace-generic-fiber-to-be-according-to-the-convention" (PR #1441)
2. `0bcd7629b` - "replace generic fiber to be according to the convention" (Navot Yaari, 30/10/2025)

**מסקנה:** השינויים האלה לא קשורים לבעיה - הם רק שינויי שמות של fiber description.

**שינויים ב-recording_metadata:** לא נמצאו שינויים ב-2 השבועות האחרונים.

---

### ✅ 3. בדיקת הלוגים של Focus Server

**תוצאה:** נמצאו **250 רשומות לוג** עם השגיאה!

**פרטים:**
- Pod: `panda-panda-focus-server-78dbcfd9d9-kjj77`
- Namespace: `panda`
- מספר רשומות: 250 (מתוך 1000 שורות אחרונות)

**מסקנה:** השגיאה מופיעה בלוגים של Focus Server, מה שאומר שהיא מגיעה מהקוד של Focus Server או מ-`pz_core_libs`.

---

### ✅ 4. בדיקת מצב המערכת

**תוצאה:** המערכת במצב "waiting for fiber"

**פרטי Metadata:**
```json
{
  "prr": 0.0,
  "dx": null,
  "sw_version": "waiting for fiber",
  "fiber_description": "waiting for fiber",
  "number_of_channels": 2337,
  "fiber_start_meters": null,
  "fiber_length_meters": null
}
```

**מסקנה:** 
- `focus_manager.fiber_metadata.prr` = **0.0** (לא תקין!)
- `focus_manager.fiber_metadata.dx` = **null** (לא תקין!)
- המערכת במצב "waiting for fiber" - אין fiber פיזי מחובר

---

## 🎯 מסקנות עיקריות

### 1. מקור השגיאה
השגיאה `"Cannot proceed: Missing required fiber metadata fields: prr"` **לא נמצאה בקוד של PZ** ב-repo הזה. זה אומר שהיא כנראה מגיעה מ:
- `pz_core_libs` (package חיצוני) - RecordingMetadata validation
- או מ-validation ב-Focus Server שלא נמצא ב-repo הזה

### 2. הבעיה
כשהמערכת במצב "waiting for fiber":
- `prr` = 0.0 (צריך להיות > 0)
- `dx` = null (צריך להיות > 0)
- `sw_version` = "waiting for fiber"

כשמנסים להגדיר job, ה-validation ב-`pz_core_libs` בודק ש-`prr > 0` וזורק שגיאה.

### 3. מתי זה התחיל?
- לא נמצאו שינויים בקוד של PZ ב-2 השבועות האחרונים שגורמים לזה
- השגיאה מופיעה בלוגים (250 רשומות), מה שאומר שהיא קיימת כבר זמן מה
- כנראה השינוי היה ב-`pz_core_libs` (package חיצוני) ולא ב-repo הזה

---

## 🔧 המלצות לפתרון

### 1. בדוק את pz_core_libs
```bash
# אם יש repo נפרד ל-pz_core_libs:
cd <pz_core_libs_repo>
git log --all --since="2 weeks ago" --oneline --grep="metadata\|validation\|prr"
git log --all --since="2 weeks ago" --oneline -- "**/recording_metadata*"
```

### 2. בדוק את הלוגים בפירוט
```bash
# קבל את הלוגים המלאים
kubectl logs panda-panda-focus-server-78dbcfd9d9-kjj77 -n panda --tail=1000 | grep -i "cannot proceed\|missing required\|prr"
```

### 3. בדוק את RecordingMetadata validation
חפש ב-`pz_core_libs`:
- `RecordingMetadata` class
- `model_validator` או `@validator` decorators
- בדיקות של `prr > 0` או `dx > 0`

### 4. פתרון זמני
אם צריך להריץ טסטים גם במצב "waiting for fiber":
- אפשר להוסיף skip לטסטים שמנסים להגדיר jobs
- או לבדוק את מצב המערכת לפני הרצת טסטים

---

## 📝 קבצים שנוצרו

1. `docs/04_testing/analysis/PZ_CODE_INVESTIGATION_WAITING_FIBER.md` - דוח ראשוני
2. `docs/04_testing/analysis/WAITING_FOR_FIBER_INVESTIGATION_20251108_202702.md` - דוח מפורט עם JSON
3. `scripts/investigate_waiting_for_fiber.py` - סקריפט החקירה

---

## ✅ סיכום

**הבעיה:** המערכת במצב "waiting for fiber" עם `prr=0.0`, וה-validation ב-`pz_core_libs` זורק שגיאה כשמנסים להגדיר job.

**הסיבה:** כנראה שינוי ב-`pz_core_libs` (package חיצוני) שהוסיף validation חדש ל-RecordingMetadata.

**הפתרון:** צריך לבדוק את `pz_core_libs` ולמצוא את ה-validation שגורם לבעיה, או לטפל במצב "waiting for fiber" בצורה נכונה.

