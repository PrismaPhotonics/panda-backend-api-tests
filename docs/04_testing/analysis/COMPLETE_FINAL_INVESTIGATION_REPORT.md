# דוח חקירה סופי ומלא - "Cannot proceed: Missing required fiber metadata fields: prr"

**תאריך:** 2025-11-08  
**חוקר:** AI Assistant  
**מטרה:** למצוא את המקור המדויק של השגיאה "Cannot proceed: Missing required fiber metadata fields: prr"

---

## 📋 סיכום ביצוע

### ✅ כל המשימות הושלמו

1. ✅ **בדיקת pz_core_libs** - מצא repository ובדק את הקוד
2. ✅ **בדיקת Git History של pz_core_libs** - לא נמצאו commits של ohad
3. ✅ **חיפוש ה-validation code** - לא נמצא ב-pz_core_libs
4. ✅ **בדיקת Focus Server code** - חפש validation של prr
5. ✅ **בדיקת baby_analyzer code** - חפש validation של prr
6. ✅ **בדיקת Recording.open_recording()** - חפש validation של metadata
7. ✅ **בדיקת הלוגים בפירוט** - חפש stack traces
8. ✅ **בדיקת Runtime validation** - מצאתי LiveMetadata vs LiveMetadataFlat
9. ✅ **בדיקת pz_core_libs version** - איזה version מותקן ב-production
10. ✅ **בדיקת baby_analyzer __main__.py** - חפש validation של prr
11. ✅ **בדיקת SvClient.start()** - חפש exception handler

---

## 🔍 ממצאים עיקריים

### 1. השגיאה המדויקת לא נמצאה בקוד

**ממצא קריטי:** השגיאה `"Cannot proceed: Missing required fiber metadata fields: prr"` **לא נמצאה** באף אחד מהקבצים הבאים:
- ❌ `pz_core_libs` repository
- ❌ `pz/microservices/focus_server/` 
- ❌ `pz/microservices/baby_analyzer/`
- ❌ `src/utils/validators.py` (יש שם validation אחר: `"Invalid PRR: {metadata.prr} (must be > 0)"`)

**מסקנה:** השגיאה כנראה נוצרת באופן דינמי או מגיעה מ-exception handler שמזהה את השגיאה ומזריק אותה מחדש.

---

### 2. מקורות אפשריים לשגיאה

#### מקור 1: `SizeSetterProcessor.initialize()`

**מיקום:** `pz/microservices/baby_analyzer/processors/size_setter_processor.py:46-55`

**קוד:**
```python
def initialize(self, init_metadata: RecordingMetadata):
    super().initialize(init_metadata)
    self.in_traces = self.init_metadata.num_traces
    self.out_shape = (self.init_metadata.num_samples_per_trace, self.out_traces)
    self.working_chunk = None
    self.start_new_chunk = True

    chunk_length_ms = self.out_traces * (1 / self.init_metadata.prr) * 1000
    if chunk_length_ms < 1:
        raise InvalidArgument(f'Outgoing chunks must be at least 1ms in length, {chunk_length_ms}ms requested')
```

**בעיה:**
- אם `self.init_metadata.prr` הוא `0.0`, אז `1 / self.init_metadata.prr` יזרוק `ZeroDivisionError`
- אם `self.init_metadata.prr` הוא `None` או לא קיים, זה יזרוק `TypeError`

**איפה זה נקרא:**
- `pz/microservices/focus_server/prp_to_raw_consumer.py:76` - `self.size_setter.initialize(self.baby_recording.metadata)`
- `pz/microservices/baby_analyzer/babyanalyzer.py:138` - `processor.initialize(copy.deepcopy(metadata))`

---

#### מקור 2: `baby_input_loop.py`

**מיקום:** `pz/microservices/baby_analyzer/baby_input_loop.py:101`

**קוד:**
```python
def input_loop(self):
    logger.debug('Entering input loop.')
    chunk_dt = self.in_rec.metadata.num_traces / self.in_rec.metadata.prr
    # ...
```

**בעיה:**
- אם `self.in_rec.metadata.prr` הוא `0.0`, אז `self.in_rec.metadata.num_traces / self.in_rec.metadata.prr` יזרוק `ZeroDivisionError`
- אם `self.in_rec.metadata.prr` הוא `None` או לא קיים, זה יזרוק `TypeError`

---

#### מקור 3: `validate_metadata_consistency()`

**מיקום:** `src/utils/validators.py:327-359`

**קוד:**
```python
def validate_metadata_consistency(
    metadata: Union[LiveMetadataFlat, RecordingMetadata]
) -> bool:
    # ...
    # Validate PRR (must be > 0 if system is ready)
    if metadata.prr <= 0:
        raise ValidationError(f"Invalid PRR: {metadata.prr} (must be > 0)")
    # ...
```

**בעיה:**
- זה לא השגיאה המדויקת - השגיאה היא `"Cannot proceed: Missing required fiber metadata fields: prr"`, לא `"Invalid PRR: {metadata.prr} (must be > 0)"`

---

### 3. זרימת הקוד

#### זרימה 1: Focus Server → baby_analyzer

1. **`focus_server.py:135`** - `@app.post('/config/{task_id}')` מקבל request
2. **`focus_server.py:139`** - `run_new_baby(config_data, task_id)` נקרא
3. **`focus_server.py:50`** - `parse_task_configuration(configuration, task_id)` נקרא
4. **`focus_server.py:56`** - `focus_manager.sv_cli.start({"command": rpc_command_for_consumer, ...})` מריץ את `baby_analyzer`
5. **`focus_server.py:74`** - `RecordingToBuffer(task_id=task_id, stream_uri=stream_uri, start_running=True, ...)` נוצר
6. **`prp_to_raw_consumer.py:45`** - `self.thread.start()` מתחיל את `init_baby_recording()`
7. **`prp_to_raw_consumer.py:64`** - `Recording.open_recording(uri=self.stream_uri, ...)` נקרא
8. **`prp_to_raw_consumer.py:76`** - `self.size_setter.initialize(self.baby_recording.metadata)` נקרא
9. **`size_setter_processor.py:53`** - `chunk_length_ms = self.out_traces * (1 / self.init_metadata.prr) * 1000` - **אם `prr` הוא 0.0, זה יזרוק `ZeroDivisionError`**

---

#### זרימה 2: baby_analyzer initialization

1. **`baby_microservice.py:234`** - `baby.initialize()` נקרא
2. **`babyanalyzer.py:130`** - `initialize(init_metadata=None)` נקרא
3. **`babyanalyzer.py:138`** - `processor.initialize(copy.deepcopy(metadata))` נקרא לכל processor
4. **`size_setter_processor.py:46`** - `initialize(init_metadata)` נקרא
5. **`size_setter_processor.py:53`** - `chunk_length_ms = self.out_traces * (1 / self.init_metadata.prr) * 1000` - **אם `prr` הוא 0.0, זה יזרוק `ZeroDivisionError`**

---

### 4. Exception Handling

#### Exception Handler ב-baby_analyzer

**מיקום:** `pz/microservices/baby_analyzer/baby_microservice.py:249-254`

**קוד:**
```python
except Exception as ex:
    logger.exception(f'Exception raised during microservice operation: {ex}')
    report_error(ex)
    exit_err = ex
```

**מה זה עושה:**
- לוג את השגיאה
- קורא ל-`report_error(ex)` - שולח `PrpStatus` message ל-RabbitMQ
- שומר את השגיאה ב-`exit_err`

---

#### Exception Handler ב-Focus Server

**מיקום:** `pz/microservices/focus_server/focus_server.py:51-53`

**קוד:**
```python
except Exception as e:
    logger.exception(f"Error parsing configuration: {configuration}")
    return ORJSONResponse(content={"error": "Error parsing configuration"}, status_code=500)
```

**מה זה עושה:**
- לוג את השגיאה
- מחזיר `500 Internal Server Error`

**אבל:** זה לא מסביר את ההודעה `"Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"`.

---

### 5. השערה לגבי מקור השגיאה

**השערה:** השגיאה `"Cannot proceed: Missing required fiber metadata fields: prr"` כנראה נוצרת באופן דינמי על ידי exception handler שמזהה את השגיאה המקורית (כמו `ZeroDivisionError` או `InvalidArgument`) ומזריק אותה מחדש עם הודעה מותאמת.

**איפה זה יכול להיות:**
1. **Exception handler ב-FastAPI** - אולי יש middleware שמזהה את השגיאה ומזריק אותה מחדש
2. **Exception handler ב-`PrpStatus` message** - אולי יש handler שמזהה את השגיאה מ-`baby_analyzer` ומזריק אותה מחדש
3. **Exception handler ב-`RecordingToBuffer.init_baby_recording()`** - אולי יש try-except שמזהה את השגיאה ומזריק אותה מחדש

**אבל:** לא מצאתי exception handler כזה בקוד.

---

## 🎯 מסקנות

### 1. השגיאה המדויקת לא נמצאה בקוד

השגיאה `"Cannot proceed: Missing required fiber metadata fields: prr"` **לא נמצאה** באף אחד מהקבצים שנבדקו. זה אומר שהיא כנראה:
- נוצרת באופן דינמי על ידי exception handler
- מגיעה מ-external library או dependency
- נוצרת על ידי logging framework או error reporting system

---

### 2. מקורות אפשריים לשגיאה

השגיאה כנראה נגרמת על ידי אחד מהמקורות הבאים:

1. **`SizeSetterProcessor.initialize()`** - אם `prr` הוא 0.0, זה יזרוק `ZeroDivisionError`
2. **`baby_input_loop.py`** - אם `prr` הוא 0.0, זה יזרוק `ZeroDivisionError`
3. **Exception handler** - שמזהה את השגיאה ומזריק אותה מחדש עם הודעה מותאמת

---

### 3. הפתרון

**הפתרון המומלץ:**
1. **הוסף validation ב-`focus_server.py`** - בדוק אם `focus_manager.fiber_metadata.prr > 0` לפני ניסיון להגדיר job
2. **הוסף validation ב-`SizeSetterProcessor.initialize()`** - בדוק אם `prr > 0` לפני חישוב `chunk_length_ms`
3. **הוסף validation ב-`baby_input_loop.py`** - בדוק אם `prr > 0` לפני חישוב `chunk_dt`
4. **הוסף exception handler** - שמזהה את השגיאה ומחזיר הודעה ברורה יותר

---

## 📝 קבצים שנבדקו

### pz_core_libs
- ✅ `C:\Projects\pz-core-libs\src\pz_core_libs\recording_metadata\recording_metadata.py`
- ✅ `C:\Projects\pz-core-libs\src\pz_core_libs\recording_metadata\metadata_layers\prp2_layer.py`
- ✅ `C:\Projects\pz-core-libs\src\pz_core_libs\recording\recording.py`
- ✅ `C:\Projects\pz-core-libs\src\pz_core_libs\recording\backends\sources\mq_source.py`
- ✅ `C:\Projects\pz-core-libs\src\pz_core_libs\msgbus\sv_client.py`
- ✅ `C:\Projects\pz-core-libs\src\pz_core_libs\msgbus\prpcast_synchronous_consumer.py`

### Focus Server
- ✅ `pz/microservices/focus_server/focus_server.py`
- ✅ `pz/microservices/focus_server/focus_manager.py`
- ✅ `pz/microservices/focus_server/prp_to_raw_consumer.py`

### baby_analyzer
- ✅ `pz/microservices/baby_analyzer/babyanalyzer.py`
- ✅ `pz/microservices/baby_analyzer/baby_microservice.py`
- ✅ `pz/microservices/baby_analyzer/baby_input_loop.py`
- ✅ `pz/microservices/baby_analyzer/baby_sitter.py`
- ✅ `pz/microservices/baby_analyzer/processors/size_setter_processor.py`

### Automation Code
- ✅ `src/utils/validators.py`
- ✅ `src/models/focus_server_models.py`
- ✅ `src/apis/focus_server_api.py`

---

## 🔚 סיכום

**השגיאה:** `"Cannot proceed: Missing required fiber metadata fields: prr"`

**מקור אפשרי:**
- ❌ לא נמצא בקוד
- ✅ כנראה נוצרת באופן דינמי על ידי exception handler
- ✅ כנראה נגרמת על ידי `ZeroDivisionError` או `InvalidArgument` ב-`SizeSetterProcessor.initialize()` או `baby_input_loop.py`

**הפתרון:**
- ✅ הוסף validation ב-`focus_server.py` לפני ניסיון להגדיר job
- ✅ הוסף validation ב-`SizeSetterProcessor.initialize()` לפני חישוב `chunk_length_ms`
- ✅ הוסף validation ב-`baby_input_loop.py` לפני חישוב `chunk_dt`

---

**תאריך סיום:** 2025-11-08  
**סטטוס:** ✅ **חקירה הושלמה**

