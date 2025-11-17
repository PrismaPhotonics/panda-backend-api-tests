# חקירת קוד PZ - בעיית "waiting for fiber"

**תאריך:** 2025-11-08  
**חוקר:** AI Assistant  
**בקשה:** לבדוק מה אוהד פיתח שגורם לבעיית "waiting for fiber"

---

## 📋 סיכום הממצאים

### 1. בדיקת Git History

**שינויים אחרונים (2 שבועות):**
- `6b2d08c7d` - "cleanup baby resources on failed initialization" (Sergey Fonaryov, 30/10/2025)
- `3bd8cfcb6` - "replace generic fiber to be according to the convention" (Navot Yaari, 30/10/2025)
- **לא נמצאו שינויים של אוהד ב-2 השבועות האחרונים**

### 2. בדיקת Focus Server Code

**קובץ:** `pz/microservices/focus_server/focus_server.py`

**ממצאים:**
- ה-endpoint `/config/{task_id}` (שורה 135-140) **לא מכיל validation**
- יש TODO comment: `# TODO: validate config` (שורה 138)
- ה-endpoint קורא ל-`run_new_baby()` שמשתמש ב-`focus_manager.prr` (שורה 66, 85, 91)
- אם `focus_manager.prr` הוא 0 או None, זה יכול לגרום לבעיות

**קובץ:** `pz/microservices/focus_server/focus_manager.py`

**ממצאים:**
- `FocusManager.__init__()` פותח recording כדי לאתחל metadata (שורות 32-38):
  ```python
  temp_rec = Recording.open_recording('amqp://')
  self.fiber_metadata = temp_rec.metadata
  self.sensors = self.fiber_metadata.num_samples_per_trace
  temp_rec.end_recording()
  ```
- אם ה-recording במצב "waiting for fiber", ה-metadata יכולה להיות לא תקינה
- `focus_manager.prr` נלקח מ-`focus_manager.fiber_metadata.prr`
- אם `prr` הוא 0 או None, זה יכול לגרום לבעיות בחישובים

### 3. השגיאה המדויקת

**מהלוגים:**
```
ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr
```

**השגיאה הזו לא נמצאה בקוד של:**
- `focus_server.py`
- `focus_manager.py`
- `baby_sitter.py`
- `baby_analyzer.py`

**מסקנה:** השגיאה כנראה מגיעה מ-`pz_core_libs` (ספרייה חיצונית) או מ-RecordingMetadata validation.

---

## 🔍 השערות לגבי מקור הבעיה

### השערה 1: RecordingMetadata Validation
- `RecordingMetadata` (מ-`pz_core_libs`) יכול להכיל validation חדש שבודק שכל השדות הנדרשים קיימים
- אם `prr` הוא 0 או None, ה-validation יכול לזרוק שגיאה
- זה יכול להיות שינוי ב-`pz_core_libs` שלא נמצא ב-repo הזה

### השערה 2: Focus Manager Initialization
- אם ה-recording במצב "waiting for fiber" כשהמערכת מתחילה, `focus_manager.fiber_metadata` יכולה להיות לא תקינה
- `focus_manager.prr` יכול להיות 0 או None
- כשמנסים להגדיר job, החישובים ב-`parse_task_configuration()` יכולים להיכשל

### השערה 3: Baby Analyzer Validation
- `baby_analyzer` יכול להכיל validation חדש שבודק metadata לפני יצירת job
- זה יכול להיות ב-`Recording.open_recording()` או ב-`BabyAnalyzer.initialize()`

---

## 🎯 המלצות לבדיקה נוספת

### 1. בדוק את pz_core_libs
```bash
# חפש את השגיאה ב-pz_core_libs
grep -r "Cannot proceed.*Missing required.*metadata" pz_core_libs/
grep -r "Missing required fiber metadata fields" pz_core_libs/
```

### 2. בדוק את RecordingMetadata
```bash
# חפש validation ב-RecordingMetadata
grep -r "def.*validate\|@.*validator\|model_validator" pz_core_libs/recording_metadata/
```

### 3. בדוק את Git History של pz_core_libs
```bash
cd pz_core_libs
git log --all --since="2 weeks ago" --oneline --grep="metadata\|validation\|prr\|fiber"
```

### 4. בדוק את הלוגים של Focus Server
```bash
# חפש את השגיאה בלוגים
kubectl logs -n panda panda-panda-focus-server-* | grep "Cannot proceed\|Missing required"
```

---

## 📝 מסקנות

1. **לא נמצאו שינויים של אוהד ב-2 השבועות האחרונים** ב-repo הזה
2. **השגיאה "Cannot proceed: Missing required fiber metadata fields: prr" לא נמצאה בקוד** של focus_server או baby_analyzer
3. **השגיאה כנראה מגיעה מ-pz_core_libs** (ספרייה חיצונית) או מ-RecordingMetadata validation
4. **הבעיה יכולה להיות קשורה ל-initialization של FocusManager** כשהמערכת במצב "waiting for fiber"

---

## 🔧 פעולות מומלצות

1. **בדוק את pz_core_libs** - זה המקום הסביר ביותר למצוא את השגיאה
2. **בדוק את Git History של pz_core_libs** - חפש שינויים אחרונים ב-RecordingMetadata validation
3. **בדוק את הלוגים של Focus Server** - חפש מתי השגיאה מופיעה לראשונה
4. **בדוק את מצב המערכת** - ודא ש-`focus_manager.fiber_metadata.prr` תקין כשהמערכת במצב "waiting for fiber"

---

## 📌 הערות נוספות

- ה-commit `6b2d08c7d` (cleanup baby resources) לא נראה קשור לבעיה - זה רק שינוי ב-cleanup logic
- ה-commit `0bcd7629b` (replace generic fiber) לא נראה קשור לבעיה - זה רק שינוי בשם של fiber description
- **הבעיה כנראה לא נגרמת משינוי בקוד של focus_server או baby_analyzer**, אלא משינוי ב-pz_core_libs או ב-RecordingMetadata validation

