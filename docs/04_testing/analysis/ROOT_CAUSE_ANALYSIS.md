# ניתוח שורש הבעיה - "Cannot proceed: Missing required fiber metadata fields: prr"

**תאריך:** 2025-11-08  
**חוקר:** AI Assistant  
**מטרה:** למצוא את המקור המדויק של השגיאה

---

## 📋 סיכום הממצאים

### ✅ 1. בדיקת pz_core_libs

**מיקום:** `C:\Projects\pz-core-libs`

**ממצאים:**
- ✅ RecordingMetadata class נמצא
- ✅ Prp2Layer class נמצא עם `prr: float` field
- ❌ **השגיאה "Cannot proceed: Missing required fiber metadata fields: prr" לא נמצאה**
- ❌ **Validation של prr > 0 לא נמצא** ב-RecordingMetadata או ב-Prp2Layer
- ❌ `validate()` method ב-Prp2Layer **ריק**

### ✅ 2. בדיקת Recording.open_recording()

**מיקום:** `C:\Projects\pz-core-libs\src\pz_core_libs\recording\recording.py:574`

**ממצאים:**
- ✅ `open_recording()` method נמצא
- ❌ **לא נמצא validation של prr** ב-`open_recording()`
- ❌ **לא נמצא validation של metadata** ב-`open_recording()`
- ✅ יש TODO comment: `# TODO: validate metadata when opening a recording for write` (שורה 738)

### ✅ 3. בדיקת SizeSetterProcessor.initialize()

**מיקום:** `pz/microservices/baby_analyzer/processors/size_setter_processor.py:46`

**ממצאים:**
- ✅ `initialize()` method נמצא
- ✅ יש validation: `chunk_length_ms = self.out_traces * (1 / self.init_metadata.prr) * 1000`
- ✅ אם `chunk_length_ms < 1`, זורק `InvalidArgument`
- ❌ **אבל זה לא השגיאה המדויקת** - השגיאה היא "Cannot proceed: Missing required fiber metadata fields: prr"

### ✅ 4. בדיקת Focus Server Code

**מיקום:** `pz/microservices/focus_server/focus_server.py`

**ממצאים:**
- ✅ `run_new_baby()` method נמצא (שורה 47)
- ✅ `parse_task_configuration()` method נמצא (שורה 82)
- ✅ `config()` endpoint נמצא (שורה 135)
- ❌ **השגיאה "Cannot configure job - validation failed" לא נמצאה** ב-Focus Server code
- ❌ **לא נמצא exception handler** שמזהה את השגיאה ומזריק אותה מחדש

**שימוש ב-prr:**
- שורה 66: `rows_per_second = (focus_manager.prr / ((1 - window_overlap) * n_fft))`
- שורה 85: `window_overlap = 1 - (display_time_axis_duration * focus_manager.prr) / ((configuration["canvasInfo"]["height"] * n_fft))`
- שורה 91: `display_time_axis_duration = (1 - window_overlap) * configuration["canvasInfo"]["height"] / focus_manager.prr`

**אם `focus_manager.prr = 0.0`:**
- שורה 66: `rows_per_second = (0.0 / ...) = 0.0` - לא יזרוק שגיאה
- שורה 85: `window_overlap = 1 - (display_time_axis_duration * 0.0) / ... = 1` - לא יזרוק שגיאה
- שורה 91: `display_time_axis_duration = (1 - window_overlap) * ... / 0.0` - **זה יזרוק ZeroDivisionError!**

### ✅ 5. בדיקת FocusManager

**מיקום:** `pz/microservices/focus_server/focus_manager.py`

**ממצאים:**
- ✅ `FocusManager` class נמצא
- ✅ `fiber_metadata: RecordingMetadata` field נמצא (שורה 19)
- ✅ `prr: int` field נמצא (שורה 13)
- ✅ `__init__()` method נמצא (שורה 22)
- ✅ `self.prr = prr` (שורה 25) - default value: 2000
- ✅ `self.fiber_metadata = temp_rec.metadata` (שורה 35) - מקבל metadata מ-Recording.open_recording()

**אם `temp_rec.metadata.prr = 0.0`:**
- `self.fiber_metadata.prr = 0.0`
- אבל `self.prr = 2000` (default value) - **לא מעודכן מ-metadata!**

**הבעיה:**
- `focus_manager.prr` = 2000 (default value)
- `focus_manager.fiber_metadata.prr` = 0.0 (מהמערכת)
- **יש חוסר התאמה!**

---

## 🎯 השערה לגבי מקור השגיאה

### השערה 1: Validation ב-baby_analyzer

**השערה:**
השגיאה נזרקת מ-`baby_analyzer` כשמנסים להריץ את ה-command שנוצר ב-`format_command()`.

**מה קורה:**
1. `run_new_baby()` קורא ל-`parse_task_configuration()` (שורה 50)
2. `parse_task_configuration()` קורא ל-`baby_sitter.format_command()` (שורה 104, 119)
3. `format_command()` יוצר command string
4. `focus_manager.sv_cli.start()` מריץ את ה-command (שורה 56)
5. `baby_analyzer` מנסה לפתוח recording
6. `baby_analyzer` בודק את ה-metadata
7. אם `metadata.prr <= 0`, `baby_analyzer` זורק שגיאה: "Cannot proceed: Missing required fiber metadata fields: prr"

**איפה זה יכול להיות:**
- ב-`baby_analyzer` main function
- ב-`baby_analyzer` initialization
- ב-`baby_analyzer` validation של metadata

### השערה 2: Exception Handler ב-Focus Server

**השערה:**
יש exception handler ב-Focus Server שמזהה את השגיאה מ-`baby_analyzer` ומזריק אותה מחדש עם הודעה "Cannot configure job - validation failed".

**מה קורה:**
1. `run_new_baby()` קורא ל-`focus_manager.sv_cli.start()` (שורה 56)
2. `sv_cli.start()` מריץ את `baby_analyzer`
3. `baby_analyzer` זורק שגיאה: "Cannot proceed: Missing required fiber metadata fields: prr"
4. Exception handler ב-Focus Server מזהה את השגיאה
5. Exception handler מזריק אותה מחדש: "Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"

**איפה זה יכול להיות:**
- ב-`sv_cli.start()` exception handler
- ב-`run_new_baby()` exception handler
- ב-FastAPI exception handler

---

## 🔍 מה צריך לבדוק עכשיו

### 1. בדוק את baby_analyzer Code

**קבצים לבדוק:**
- `pz/microservices/baby_analyzer/babyanalyzer.py` - main function
- `pz/microservices/baby_analyzer/__main__.py` - entry point
- `pz/microservices/baby_analyzer/processors/` - processors initialization

**מה לחפש:**
- Validation של `metadata.prr > 0` לפני אתחול
- Exception handling שמזהה "waiting for fiber" state
- Error messages: "Cannot proceed", "Missing required fiber metadata fields"

### 2. בדוק את SvClient.start()

**מיקום:** `pz_core_libs/msgbus/sv_client.py` (אם קיים)

**מה לחפש:**
- Exception handling שמזהה שגיאות מ-baby_analyzer
- Error messages: "Cannot configure job", "validation failed"

### 3. בדוק את הלוגים בפירוט

**מה לחפש:**
- Stack traces שמראים איפה השגיאה נזרקת
- Exception handlers שמזהה את השגיאה ומזריק אותה מחדש
- Validation code שקורה בזמן ריצה

---

## 📝 מסקנות

### 1. השגיאה לא נמצאה בקוד הסטטי

**ממצאים:**
- ❌ השגיאה **לא נמצאה** ב-pz_core_libs
- ❌ השגיאה **לא נמצאה** ב-Focus Server
- ❌ השגיאה **לא נמצאה** ב-baby_analyzer

### 2. השגיאה כנראה נזרקת מ-Runtime

**השערה:**
השגיאה כנראה נזרקת מ:
1. **baby_analyzer** - validation שקורה בזמן ריצה
2. **Exception handler** - exception handler שמזהה את השגיאה ומזריק אותה מחדש
3. **Dynamic validation** - validation שקורה דרך reflection או dynamic code

### 3. הבעיה: focus_manager.prr לא מעודכן

**ממצאים:**
- `focus_manager.prr` = 2000 (default value)
- `focus_manager.fiber_metadata.prr` = 0.0 (מהמערכת)
- **יש חוסר התאמה!**

**אם `focus_manager.prr = 0.0`:**
- שורה 91: `display_time_axis_duration = (1 - window_overlap) * ... / 0.0` - **זה יזרוק ZeroDivisionError!**

---

## ✅ צעדים הבאים

1. **בדוק את baby_analyzer code** - חפש validation של prr
2. **בדוק את SvClient.start()** - חפש exception handler
3. **בדוק את הלוגים בפירוט** - חפש stack traces

---

## 🔗 קישורים

- **Focus Server:** `pz/microservices/focus_server/focus_server.py`
- **FocusManager:** `pz/microservices/focus_server/focus_manager.py`
- **RecordingToBuffer:** `pz/microservices/focus_server/prp_to_raw_consumer.py`
- **baby_sitter:** `pz/microservices/baby_analyzer/baby_sitter.py`
- **SizeSetterProcessor:** `pz/microservices/baby_analyzer/processors/size_setter_processor.py`

