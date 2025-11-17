# שאלות לצוות - חקירת "Cannot proceed: Missing required fiber metadata fields: prr"

**תאריך:** 2025-11-08  
**מטרה:** להבין את מקור השגיאה המדויק ולמצוא את הפתרון

---

## 🔍 שאלות קריטיות

### 1. מקור השגיאה המדויק

**שאלה:** איפה בדיוק נוצרת השגיאה `"Cannot proceed: Missing required fiber metadata fields: prr"`?

**הקשר:**
- השגיאה לא נמצאה בקוד שנבדק (pz_core_libs, focus_server, baby_analyzer)
- השגיאה מופיעה בלוגים: `"Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"`
- כנראה נוצרת באופן דינמי על ידי exception handler

**מה לשאול:**
- האם יש exception handler שמזהה `ZeroDivisionError` או `InvalidArgument` ומזריק אותה מחדש עם הודעה מותאמת?
- האם יש logging framework או error reporting system שמשנה את הודעות השגיאה?
- האם יש middleware ב-FastAPI שמזהה שגיאות ומזריק אותן מחדש?

---

### 2. Exception Handling ב-Focus Server

**שאלה:** האם יש exception handler ב-`focus_server.py` או ב-FastAPI middleware שמזהה שגיאות מ-`baby_analyzer` ומזריק אותן מחדש?

**הקשר:**
- ב-`focus_server.py:51-53` יש exception handler שמזהה שגיאות ב-`parse_task_configuration()` ומחזיר `500 Internal Server Error`
- אבל לא נמצא exception handler שמזהה שגיאות מ-`baby_analyzer` ומזריק אותן מחדש עם הודעה `"Cannot configure job - validation failed"`

**מה לשאול:**
- האם יש exception handler ב-`run_new_baby()` שמזהה שגיאות מ-`baby_analyzer`?
- האם יש FastAPI exception handler או middleware שמזהה שגיאות ומזריק אותן מחדש?
- האם יש error reporting system שמזהה שגיאות ומזריק אותן מחדש?

---

### 3. שינויים אחרונים בקוד

**שאלה:** האם היו שינויים אחרונים בקוד שקשורים ל-validation של metadata או ל-exception handling?

**הקשר:**
- המשתמש אמר: "זה לא היה ככה עד לפני שבוע וחצי"
- המשתמש אמר: "אוהד דחף קוד חדש שכנראה הפעולה שלו או השינוי של הקוד גורם לכך שמקבלים את השגיאה של הfiber"

**מה לשאול:**
- האם היו שינויים אחרונים ב-`pz_core_libs` שקשורים ל-validation של `prr`?
- האם היו שינויים אחרונים ב-`baby_analyzer` שקשורים ל-validation של metadata?
- האם היו שינויים אחרונים ב-`focus_server` שקשורים ל-exception handling?
- האם היו שינויים אחרונים ב-`SizeSetterProcessor` או ב-`baby_input_loop`?
- האם היו שינויים אחרונים ב-`Recording.open_recording()` או ב-`MqSource`?

---

### 4. Exception Handler ב-baby_analyzer

**שאלה:** האם יש exception handler ב-`baby_analyzer` שמזהה שגיאות ומזריק אותן מחדש עם הודעה מותאמת?

**הקשר:**
- ב-`baby_microservice.py:249-254` יש exception handler שמזהה שגיאות ומזריק `PrpStatus` message ל-RabbitMQ
- אבל לא נמצא exception handler שמזהה `ZeroDivisionError` או `InvalidArgument` ומזריק אותן מחדש עם הודעה `"Cannot proceed: Missing required fiber metadata fields: prr"`

**מה לשאול:**
- האם יש exception handler ב-`baby_analyzer` שמזהה `ZeroDivisionError` או `InvalidArgument` ומזריק אותן מחדש?
- האם יש validation ב-`baby_analyzer` initialization שמזהה `prr <= 0` ומזריק שגיאה עם הודעה מותאמת?
- האם יש error reporting system שמזהה שגיאות ומזריק אותן מחדש?

---

### 5. Validation ב-SizeSetterProcessor

**שאלה:** האם יש validation ב-`SizeSetterProcessor.initialize()` שמזהה `prr <= 0` ומזריק שגיאה עם הודעה מותאמת?

**הקשר:**
- ב-`size_setter_processor.py:53` יש חישוב: `chunk_length_ms = self.out_traces * (1 / self.init_metadata.prr) * 1000`
- אם `prr` הוא 0.0, זה יזרוק `ZeroDivisionError`
- אבל לא נמצא validation שמזהה `prr <= 0` ומזריק שגיאה עם הודעה `"Cannot proceed: Missing required fiber metadata fields: prr"`

**מה לשאול:**
- האם יש validation ב-`SizeSetterProcessor.initialize()` שמזהה `prr <= 0` לפני החישוב?
- האם יש exception handler שמזהה `ZeroDivisionError` ומזריק אותה מחדש עם הודעה מותאמת?
- האם יש validation ב-`baby_analyzer` initialization שמזהה `prr <= 0` ומזריק שגיאה?

---

### 6. Validation ב-baby_input_loop

**שאלה:** האם יש validation ב-`baby_input_loop.py` שמזהה `prr <= 0` לפני החישוב?

**הקשר:**
- ב-`baby_input_loop.py:101` יש חישוב: `chunk_dt = self.in_rec.metadata.num_traces / self.in_rec.metadata.prr`
- אם `prr` הוא 0.0, זה יזרוק `ZeroDivisionError`
- אבל לא נמצא validation שמזהה `prr <= 0` לפני החישוב

**מה לשאול:**
- האם יש validation ב-`baby_input_loop.py` שמזהה `prr <= 0` לפני החישוב?
- האם יש exception handler שמזהה `ZeroDivisionError` ומזריק אותה מחדש עם הודעה מותאמת?

---

### 7. Validation ב-Recording.open_recording()

**שאלה:** האם יש validation ב-`Recording.open_recording()` שמזהה `prr <= 0` ומזריק שגיאה?

**הקשר:**
- ב-`recording.py:574` יש `open_recording()` method
- יש TODO comment: `# TODO: validate metadata when opening a recording for write` (שורה 738)
- אבל לא נמצא validation שמזהה `prr <= 0` ומזריק שגיאה

**מה לשאול:**
- האם יש validation ב-`Recording.open_recording()` שמזהה `prr <= 0` ומזריק שגיאה?
- האם יש validation ב-`MqSource` שמזהה `prr <= 0` ומזריק שגיאה?
- האם יש validation ב-`RecordingMetadata` שמזהה `prr <= 0` ומזריק שגיאה?

---

### 8. Exception Handler ב-PrpStatus

**שאלה:** האם יש exception handler ב-`PrpStatus` message שמזהה שגיאות ומזריק אותן מחדש עם הודעה מותאמת?

**הקשר:**
- ב-`baby_microservice.py:219-223` יש `report_error()` function שמזריק `PrpStatus` message ל-RabbitMQ
- אבל לא נמצא exception handler שמזהה שגיאות ומזריק אותן מחדש עם הודעה `"Cannot proceed: Missing required fiber metadata fields: prr"`

**מה לשאול:**
- האם יש exception handler ב-`PrpStatus` message שמזהה שגיאות ומזריק אותן מחדש?
- האם יש error reporting system שמזהה שגיאות ומזריק אותן מחדש?

---

### 9. Logging Framework

**שאלה:** האם יש logging framework או error reporting system שמשנה את הודעות השגיאה?

**הקשר:**
- השגיאה `"Cannot proceed: Missing required fiber metadata fields: prr"` לא נמצאה בקוד
- כנראה נוצרת באופן דינמי על ידי exception handler או logging framework

**מה לשאול:**
- האם יש logging framework שמזהה שגיאות ומזריק אותן מחדש עם הודעה מותאמת?
- האם יש error reporting system שמזהה שגיאות ומזריק אותן מחדש?
- האם יש middleware שמזהה שגיאות ומזריק אותן מחדש?

---

### 10. מצב "waiting for fiber"

**שאלה:** מה אמור לקרות כשהמערכת במצב "waiting for fiber" (prr=0.0)?

**הקשר:**
- כשהמערכת במצב "waiting for fiber", `prr` הוא 0.0
- זה גורם ל-`ZeroDivisionError` ב-`SizeSetterProcessor.initialize()` וב-`baby_input_loop.py`
- אבל לא ברור מה אמור לקרות - האם צריך לזרוק שגיאה או לחזור 503 Service Unavailable?

**מה לשאול:**
- מה אמור לקרות כשהמערכת במצב "waiting for fiber"?
- האם צריך לזרוק שגיאה או לחזור 503 Service Unavailable?
- האם צריך לבדוק את מצב המערכת לפני ניסיון להגדיר job?

---

## 📋 שאלות נוספות

### 11. Git History

**שאלה:** האם יש commits אחרונים ב-`pz_core_libs` או ב-`pz` שקשורים ל-validation של `prr`?

**מה לשאול:**
- האם יש commits אחרונים של ohad שקשורים ל-validation של `prr`?
- האם יש commits אחרונים שקשורים ל-exception handling?
- האם יש commits אחרונים שקשורים ל-`SizeSetterProcessor` או ל-`baby_input_loop`?

---

### 12. Production vs Development

**שאלה:** האם יש הבדלים בין production ל-development שקשורים ל-validation של `prr`?

**מה לשאול:**
- האם יש הבדלים בין production ל-development שקשורים ל-validation של `prr`?
- האם יש הבדלים בין production ל-development שקשורים ל-exception handling?
- האם יש הבדלים בין production ל-development שקשורים ל-`pz_core_libs` version?

---

### 13. Error Messages

**שאלה:** האם יש מקום בקוד שמזהה שגיאות ומזריק אותן מחדש עם הודעה `"Cannot proceed: Missing required fiber metadata fields: prr"`?

**מה לשאול:**
- האם יש מקום בקוד שמזהה `ZeroDivisionError` או `InvalidArgument` ומזריק אותן מחדש עם הודעה מותאמת?
- האם יש מקום בקוד שמזהה `prr <= 0` ומזריק שגיאה עם הודעה מותאמת?
- האם יש מקום בקוד שמזהה "waiting for fiber" state ומזריק שגיאה?

---

## 🎯 סיכום

### שאלות קריטיות (חובה לשאול)

1. ✅ **מקור השגיאה המדויק** - איפה בדיוק נוצרת השגיאה?
2. ✅ **Exception Handling** - האם יש exception handler שמזהה שגיאות ומזריק אותן מחדש?
3. ✅ **שינויים אחרונים** - האם היו שינויים אחרונים בקוד שקשורים ל-validation של metadata?

### שאלות חשובות (מומלץ לשאול)

4. ✅ **Validation ב-SizeSetterProcessor** - האם יש validation שמזהה `prr <= 0`?
5. ✅ **Validation ב-baby_input_loop** - האם יש validation שמזהה `prr <= 0`?
6. ✅ **מצב "waiting for fiber"** - מה אמור לקרות כשהמערכת במצב זה?

### שאלות נוספות (אופציונלי)

7. ✅ **Git History** - האם יש commits אחרונים שקשורים ל-validation?
8. ✅ **Production vs Development** - האם יש הבדלים בין production ל-development?
9. ✅ **Error Messages** - האם יש מקום בקוד שמזהה שגיאות ומזריק אותן מחדש?

---

**תאריך:** 2025-11-08  
**סטטוס:** ✅ **מוכן לשאול את הצוות**

