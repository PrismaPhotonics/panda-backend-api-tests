# חקירת Validation ב-pz_core_libs - בעיית "waiting for fiber"

**תאריך:** 2025-11-08  
**חוקר:** AI Assistant  
**מטרה:** למצוא את ה-validation ב-pz_core_libs שגורם לבעיה

---

## 📋 סיכום הממצאים

### 1. מיקום pz_core_libs

**מקור ההתקנה:**
- `git+ssh://git@github.com/PrismaPhotonics/pz-core-libs.git`
- מותקן דרך `requirements.txt` ב-PZ repository

**מיקום בקוד:**
- `pz/microservices/focus_server/focus_manager.py` - שורה 3: `from pz_core_libs.recording_metadata import RecordingMetadata`
- `pz/microservices/focus_server/focus_manager.py` - שורה 4: `from pz_core_libs.recording import Recording`
- `pz/microservices/focus_server/prp_to_raw_consumer.py` - שורה 9: `from pz_core_libs.recording import Recording`
- `pz/microservices/baby_analyzer/processors/size_setter_processor.py` - שורה 7: `from pz_core_libs.recording_metadata import RecordingMetadata`

### 2. נקודת הכניסה לשגיאה

**השגיאה נזרקת ב:**
1. `Recording.open_recording()` - כשמנסים לפתוח recording (שורה 64 ב-`prp_to_raw_consumer.py`)
2. או ב-`size_setter.initialize(self.baby_recording.metadata)` - כשמאתחלים את ה-processor (שורה 76 ב-`prp_to_raw_consumer.py`)

**השגיאה בלוגים:**
```
ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr
```

**השגיאה הראשונה:** `2025-11-08T18:13:28+0000`

### 3. מה קורה בקוד

**Flow של יצירת Job:**
1. `POST /config/{task_id}` → `config()` (שורה 135)
2. `config()` → `run_new_baby()` (שורה 139)
3. `run_new_baby()` → `parse_task_configuration()` (שורה 50)
4. `run_new_baby()` → יצירת `RecordingToBuffer` (שורה 74)
5. `RecordingToBuffer.__init__()` → `init_baby_recording()` (שורה 45, 49)
6. `init_baby_recording()` → `Recording.open_recording()` (שורה 64) ← **כאן כנראה נזרקת השגיאה**
7. `init_baby_recording()` → `size_setter.initialize(metadata)` (שורה 76) ← **או כאן**

---

## 🔍 מה צריך לבדוק ב-pz_core_libs

### 1. RecordingMetadata Class

**מיקום משוער:** `pz_core_libs/recording_metadata/__init__.py` או `pz_core_libs/recording_metadata/metadata.py`

**מה לחפש:**
- `@model_validator` או `@validator` decorators
- `def validate_prr` או `def validate_*` methods
- בדיקות של `prr > 0` או `prr <= 0`
- הודעות שגיאה: `"Cannot proceed"`, `"Missing required fiber metadata fields"`

**דוגמה למה לחפש:**
```python
@model_validator(mode='after')
def validate_prr(self):
    if self.prr <= 0:
        raise ValueError("Cannot proceed: Missing required fiber metadata fields: prr")
```

### 2. Recording.open_recording() Method

**מיקום משוער:** `pz_core_libs/recording/__init__.py` או `pz_core_libs/recording/recording.py`

**מה לחפש:**
- Validation של metadata לפני פתיחת recording
- בדיקות של `metadata.prr > 0`
- Exception handling שמזהה validation errors

### 3. Git History של pz-core-libs

**פקודות לבדיקה:**
```bash
# Clone the repository
git clone git@github.com:PrismaPhotonics/pz-core-libs.git
cd pz-core-libs

# Check recent commits related to validation
git log --all --since="3 weeks ago" --oneline --grep="validation\|prr\|metadata" -i

# Check changes in recording_metadata files
git log --all --since="3 weeks ago" --oneline -- "**/recording_metadata*"

# Check for specific error message
git log --all --since="3 weeks ago" --oneline -S "Cannot proceed" -S "Missing required"

# Check who added validation
git log --all --since="3 weeks ago" --oneline --author="ohad" -i
```

---

## 🎯 השערות לגבי מקור הבעיה

### השערה 1: RecordingMetadata Model Validator
- `RecordingMetadata` (Pydantic model) מכיל `@model_validator` שבודק ש-`prr > 0`
- כשהמערכת במצב "waiting for fiber" עם `prr=0.0`, ה-validation נכשל
- השגיאה נזרקת כשמנסים ליצור instance של `RecordingMetadata`

### השערה 2: Recording.open_recording() Validation
- `Recording.open_recording()` בודק את ה-metadata לפני פתיחת recording
- אם `metadata.prr <= 0`, הוא זורק שגיאה
- השגיאה נזרקת ב-`init_baby_recording()` כשקוראים ל-`Recording.open_recording()`

### השערה 3: SizeSetterProcessor.initialize() Validation
- `SizeSetterProcessor.initialize()` בודק ש-`metadata.prr > 0` לפני אתחול
- אם `prr=0`, הוא זורק שגיאה
- השגיאה נזרקת ב-`init_baby_recording()` כשקוראים ל-`size_setter.initialize()`

---

## 📝 פעולות מומלצות

### 1. Clone את pz-core-libs Repository

```bash
cd C:\Projects
git clone git@github.com:PrismaPhotonics/pz-core-libs.git
cd pz-core-libs
```

### 2. חפש את ה-Validation Code

```bash
# Search for the error message
grep -r "Cannot proceed.*Missing required" .
grep -r "Missing required fiber metadata fields" .

# Search for prr validation
grep -r "prr.*>.*0\|prr.*<=.*0" .
grep -r "@.*validator.*prr\|model_validator.*prr" .

# Search in recording_metadata files
find . -name "*recording_metadata*" -type f | xargs grep -l "prr\|validation"
```

### 3. בדוק את Git History

```bash
# Check recent commits
git log --all --since="3 weeks ago" --oneline

# Check commits by ohad
git log --all --since="3 weeks ago" --oneline --author="ohad" -i

# Check commits related to validation
git log --all --since="3 weeks ago" --oneline --grep="validation\|prr\|metadata" -i

# Check specific file changes
git log --all --since="3 weeks ago" --oneline -- "**/recording_metadata*"
```

### 4. בדוק את הקוד של RecordingMetadata

```bash
# Find RecordingMetadata class
find . -name "*.py" -type f | xargs grep -l "class RecordingMetadata"

# Check for validators
find . -name "*.py" -type f | xargs grep -l "@.*validator\|model_validator"
```

---

## 🔧 פתרון זמני (עד שמתקנים את pz_core_libs)

אם צריך להריץ טסטים גם במצב "waiting for fiber":

1. **Skip טסטים שמנסים להגדיר jobs** - כבר יש לנו את `skip_if_waiting_for_fiber` fixture
2. **לבדוק את מצב המערכת לפני הרצת טסטים** - כבר יש לנו את `check_metadata_ready` fixture
3. **לתת לשרת להחזיר 503** במקום לזרוק שגיאה ב-client - כבר תיקנו את זה

---

## 📌 מסקנות

1. **ה-validation כנראה ב-pz_core_libs** - לא בקוד של PZ ב-repo הזה
2. **השגיאה נזרקת כשמנסים לפתוח recording** - ב-`Recording.open_recording()` או ב-`size_setter.initialize()`
3. **צריך לבדוק את pz-core-libs repository** - זה המקום היחיד שבו אפשר למצוא את הקוד המדויק
4. **לא נמצאו שינויים של אוהד ב-PZ repo** - השינוי כנראה ב-pz_core_libs

---

## ✅ צעדים הבאים

1. **Clone את pz-core-libs repository** (אם יש גישה)
2. **חפש את ה-validation code** - `RecordingMetadata` class ו-`@model_validator` decorators
3. **בדוק את Git History** - חפש commits של אוהד או commits שקשורים ל-validation
4. **תקן את ה-validation** - או תאפשר מצב "waiting for fiber" או תזרוק שגיאה ברורה יותר

---

## 📝 קבצים שנוצרו

1. `docs/04_testing/analysis/PZ_CODE_INVESTIGATION_WAITING_FOR_FIBER.md` - דוח ראשוני
2. `docs/04_testing/analysis/WAITING_FOR_FIBER_INVESTIGATION_SUMMARY.md` - סיכום בעברית
3. `docs/04_testing/analysis/WAITING_FOR_FIBER_INVESTIGATION_20251108_202702.md` - דוח מפורט עם לוגים
4. `scripts/investigate_waiting_for_fiber.py` - סקריפט החקירה הראשי
5. `scripts/check_pz_core_libs_validation.py` - סקריפט לבדיקת pz_core_libs
6. `scripts/find_pz_core_libs_repo.py` - סקריפט לחיפוש repository
7. `scripts/analyze_focus_server_logs.py` - סקריפט לניתוח לוגים

---

## 🔗 קישורים רלוונטיים

- **pz-core-libs Repository:** `git@github.com:PrismaPhotonics/pz-core-libs.git`
- **Requirements:** `pz/share/requirements.txt` (שורה 200)
- **Focus Server Code:** `pz/microservices/focus_server/focus_server.py`
- **RecordingToBuffer:** `pz/microservices/focus_server/prp_to_raw_consumer.py`

