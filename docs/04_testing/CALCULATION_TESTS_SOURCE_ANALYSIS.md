# ניתוח מקורות - מאיפה הגיע המידע על טסטי החישובים?

**תאריך:** 29 אוקטובר 2025  
**שאלה:** מאיפה הסקתי/כרתי שצריך את הטסטים האלה?

---

## 🔍 התשובה הכנה

המידע הגיע משילוב של **3 מקורות**:

### 1️⃣ קוד קיים בפרויקט (40%)
### 2️⃣ מסמכי תיעוד קיימים (30%)  
### 3️⃣ ידע כללי על DSP ו-FFT (30%)

בואו נפרק בדיוק מה הגיע מאיפה:

---

## 📂 מקור #1: קוד קיים בפרויקט

### A. Models - `src/models/focus_server_models.py`

**מה מצאתי שם:**

```python
# Line 198-202
class ConfigureResponse(BaseModel):
    lines_dt: float = Field(..., description="DT in seconds between two consecutive spectrogram calculations")
    frequencies_amount: int = Field(..., description="Number of frequencies")
    channel_to_stream_index: Dict[str, int] = Field(...)
    stream_amount: int = Field(...)
```

**מה למדתי:**
- ✅ השרת **מחזיר** את `lines_dt` - אז צריך לבדוק שהוא נכון!
- ✅ השרת **מחזיר** את `frequencies_amount` - אז צריך לבדוק שהוא נכון!
- ✅ יש `channel_to_stream_index` mapping - צריך לבדוק את החישוב!

**מקור הטסטים שהגיעו מזה:**
- ✅ טסט #2: Time Resolution (lines_dt) - **ישירות מהמודל**
- ✅ טסט #3: Frequency Bins - **ישירות מהמודל**
- ✅ טסט #5-6: Channel Mapping - **ישירות מהמודל**

---

### B. PZ Code - Baby Analyzer

**קובץ:** `pz/microservices/baby_analyzer/processors/spectrogram_processor.py`

**מה מצאתי:**

```python
# Line 24-50
def __init__(self, n_fft: int, window_time: float = None, 
             fft_window_overlap: float = 0.5, ...):
    
    self.n_fft = n_fft
    self.max_freq_index = int(self.n_fft // 2)  # ← חישוב!
    
    if not 0 < fft_window_overlap <= 1:
        raise InvalidArgument(f'Overlap must be between 0 and 1')
    
    self.overlap = fft_window_overlap
```

**מה למדתי:**
- ✅ `max_freq_index = n_fft // 2` → זה הבסיס ל-`frequencies_amount = NFFT/2 + 1`
- ✅ Overlap מוגדר כאחוז (0-1), לא כמספר דגימות
- ✅ יש validation על overlap

**מקור הטסטים:**
- ✅ טסט #3: Frequency Bins - הנוסחה `n_fft // 2`
- ✅ טסט #10: Overlap Percentage - הvalidation

---

### C. MATLAB Code - `pz/math/prisma_mcr/slowtimeFFT.m`

**מה מצאתי:**

```matlab
% Line 8-12
while size(map,2) >= SysConf.system.FFT.npix
    f = fft(map(:,1:SysConf.system.FFT.npix), SysConf.system.FFT.npix, 2);
    absF2 = abs(f(:,1:SysConf.system.FFT.npix/2)).^2;  % ← רק חצי!
    mapOutFFT = cat(2, mapOutFFT, permute(absF2,[1 3 2]));
    map = map(:,(SysConf.system.FFT.npix - SysConf.system.FFT.overlap + 1):end);  % ← החישוב!
end
```

**מה למדתי:**
- ✅ `npix/2` → אישור ל-NFFT/2
- ✅ `npix - overlap + 1` → **זה החישוב של ההזזה בין חלונות!**
- ✅ זה הבסיס לחישוב `output_rate = PRR / (NFFT - Overlap)`

**מקור הטסטים:**
- ✅ טסט #4: Output Rate - **הנוסחה מהקוד הזה!**
- ✅ טסט #2: lines_dt - **הקשר ל-overlap**

---

### D. Configuration Files

**קובץ:** `config/usersettings.new_production_client.json` (שראית את המידע בתיעוד)

**מה מצאתי:**

```json
{
    "SensorsRange": 2222,        // ← מספר channels מקסימלי
    "FrequencyMax": 1000,        // ← תדר מקסימלי
    "nfftSingleChannel": [128, 256, 512, ..., 65536],  // ← NFFT options
    "Defaults": {
        "Nfft": 1024,
        "StartChannel": 11,
        "EndChannel": 109
    }
}
```

**מקור הטסטים:**
- ✅ טסט #9: FFT Window Size - **הרשימה מה-config**
- ✅ טסט #8: Nyquist - **FrequencyMax = 1000**

---

## 📚 מקור #2: מסמכי תיעוד קיימים

### A. Test Plan Documents

**קובץ:** `docs/06_project_management/COMPLETE_TEST_PLAN_DETAILED_PART1.md` (Line 944-980)

**מה כתוב שם:**

```markdown
### Trade-offs של NFFT

| NFFT | רזולוציית תדר | קצב עדכון (rows/sec) |
|------|---------------|---------------------|
| 128  | נמוכה (64 bins) | מאוד גבוה (~7.8) |
| 256  | נמוכה (128 bins) | גבוה (~3.9) |
| 512  | בינונית (256 bins) | בינוני (~2.0) |
| 1024 | טובה (512 bins) | בינוני (~0.98) |
| 2048 | גבוהה (1024 bins) | נמוך (~0.49) |
```

**מה למדתי:**
- ✅ NFFT=512 → 256 bins → הנוסחה `NFFT/2`
- ✅ קצבי עדכון (~7.8, ~3.9) → **אלה output rates!**
- ✅ Trade-off בין רזולוציה לקצב

**מקור הטסטים:**
- ✅ טסט #3: Frequency Bins - **הטבלה הזאת**
- ✅ טסט #4: Output Rate - **הקצבים בטבלה**

---

### B. Configuration Documentation

**קובץ:** `documentation/configuration` (Line 61-225)

**מה כתוב:**

```json
"Defaults": {
    "Nfft": 1024,
    "FrequencyMax": 1000
}

"nfftSingleChannel": [128, 256, 512, 1024, 2048, 4096, ...]
```

**מקור הטסטים:**
- ✅ ערכים תקפים לבדיקה

---

## 🎓 מקור #3: ידע כללי על DSP ו-FFT

### מה לקחתי מידע כללי?

#### A. נוסחאות סטנדרטיות ב-DSP:

```
1. Frequency Resolution = Sample_Rate / NFFT
   → במקרה שלנו: PRR / NFFT
   
2. Nyquist Frequency = Sample_Rate / 2
   → במקרה שלנו: PRR / 2
   
3. FFT Symmetry: רק NFFT/2 + 1 תדרים ייחודיים
   → לסיגנלים real-valued

4. Hop Length = NFFT - Overlap
   → זה סטנדרטי ב-STFT (Short-Time Fourier Transform)
```

**אלה עקרונות בסיסיים של עיבוד אותות!**

#### B. למה השתמשתי בידע הכללי?

כי ראיתי שהמודלים **מחזירים** את הערכים (`lines_dt`, `frequencies_amount`), אבל **לא ראיתי בקוד** איך הם מחושבים.

אז הנחתי (באופן סביר) שהם משתמשים בנוסחאות הסטנדרטיות של DSP.

---

## ⚠️ איפה צריך אישור?

### ✅ בטוח 100% (נמצא בקוד):
1. `lines_dt` קיים ב-Response
2. `frequencies_amount` קיים ב-Response
3. `channel_to_stream_index` קיים ב-Response
4. NFFT options: 128-65536
5. Max Frequency: 1000 Hz
6. Max Channels: 2222

### ❓ הנחות (צריך אימות):
1. **הנוסחה:** `lines_dt = (NFFT - Overlap) / PRR`
   - **מקור:** קוד MATLAB + ידע כללי DSP
   - **צריך לוודא:** לבדוק response אמיתי ולחשב לבד

2. **הנוסחה:** `frequency_resolution = PRR / NFFT`
   - **מקור:** ידע כללי DSP
   - **צריך לוודא:** לראות אם המערכת מחזירה את זה

3. **הנוסחה:** `frequencies_amount = NFFT / 2 + 1`
   - **מקור:** קוד Python (`n_fft // 2`) + ידע כללי
   - **צריך לוודא:** לבדוק response אמיתי

---

## 🎯 איך לוודא שזה נכון?

### שיטה 1: הרצת טסט אמיתי
```python
# שלח configure request
config = {
    "nfftSelection": 512,
    "channels": {"min": 1, "max": 8},
    "frequencyRange": {"min": 0, "max": 500},
    ...
}

response = api.configure(config)
metadata = api.get_metadata(response.job_id)

# בדוק מה באמת חוזר:
print(f"lines_dt: {metadata.lines_dt}")
print(f"frequencies_amount: {metadata.frequencies_amount}")
print(f"channel_to_stream_index: {metadata.channel_to_stream_index}")

# עכשיו תחשב בעצמך:
prr = 1000  # צריך לקבל מהמערכת
expected_lines_dt = (512 - 256) / prr  # אם overlap=256
expected_freq_bins = 512 // 2 + 1  # = 257

# השווה:
print(f"Expected lines_dt: {expected_lines_dt}")
print(f"Expected freq bins: {expected_freq_bins}")
```

### שיטה 2: בדיקה בקוד Backend
```bash
# חפש בקוד של Focus Server איך הוא מחשב:
grep -r "lines_dt" pz/microservices/focus_server/
grep -r "frequencies_amount" pz/microservices/focus_server/
grep -r "channel_to_stream_index" pz/microservices/focus_server/
```

### שיטה 3: שאל את גיא או נוגה
```
"מצאתי שהשרת מחזיר lines_dt ו-frequencies_amount.
איך הם מחושבים בדיוק?
האם יש spec document שמסביר את החישובים?"
```

---

## 📊 טבלת מקורות - לכל טסט

| # | שם הטסט | מקור המידע | רמת ודאות |
|---|---------|------------|-----------|
| 1 | Frequency Resolution | DSP ידע כללי + logic | ⚠️ 70% - צריך אימות |
| 2 | Time Resolution (lines_dt) | **Model (line 198)** + MATLAB | ✅ 95% - בקוד |
| 3 | Frequency Bins | **Model (line 202)** + Python code | ✅ 95% - בקוד |
| 4 | Output Rate | MATLAB code + DSP | ⚠️ 80% - נגזר מקוד |
| 5 | Channel Mapping (Single) | **Model (line 199)** + logic | ✅ 90% - בקוד |
| 6 | Channel Mapping (Multi) | **Model (line 199)** + logic | ✅ 90% - בקוד |
| 7 | Stream Amount | **Model (line 200)** | ✅ 100% - בקוד |
| 8 | Nyquist Calculation | Config (FrequencyMax=1000) | ✅ 90% - בconfig |
| 9 | FFT Window Size | Config (nfft options) | ✅ 100% - בconfig |
| 10 | Overlap Validation | Python code (line 48-49) | ✅ 100% - בקוד |
| 11 | Time Window Duration | DSP ידע כללי | ⚠️ 70% - צריך אימות |
| 12 | Data Rate | DSP ידע כללי | ⚠️ 60% - הערכה |
| 13 | Memory Usage | DSP ידע כללי | ⚠️ 60% - הערכה |
| 14 | Processing Time | ניסיון אמפירי | ⚠️ 50% - הערכה |
| 15 | Spectrogram Dimensions | DSP + logic | ⚠️ 70% - נגזר |

---

## 🔴 קטגוריות לפי מקור

### ✅ מהקוד/Config (ודאות גבוהה) - 7 טסטים
- טסט #2, #3, #5, #6, #7, #9, #10

**אלה בטוחים! יש להם בסיס ברור בקוד.**

### ⚠️ מנוסחאות DSP (צריך אימות) - 5 טסטים  
- טסט #1, #4, #8, #11, #15

**צריך לבדוק response אמיתי ולאמת!**

### ❓ הערכות (נמוכה) - 3 טסטים
- טסט #12, #13, #14

**אלה יותר "nice to have", פחות קריטיים**

---

## 💡 ההמלצה שלי

### מה לעשות עכשיו?

#### שלב 1: אימות (1-2 שעות)
```python
# הרץ טסט אמיתי ותבדוק מה חוזר:
config = {
    "nfftSelection": 512,
    "channels": {"min": 1, "max": 8},
    "frequencyRange": {"min": 0, "max": 500},
    "displayTimeAxisDuration": 30,
    "displayInfo": {"height": 768},
    "view_type": "0"  # MultiChannel
}

response = api.configure(config)
metadata = api.get_metadata(response.job_id)

# הדפס הכל:
print(json.dumps(metadata, indent=2))
```

#### שלב 2: השוואה
```python
# חשב בעצמך לפי הנוסחאות:
prr = 1000  # קבל מהשרת או מהconfig
nfft = 512
overlap = 256  # צריך לברר מה ה-default

# חישובים:
expected_lines_dt = (nfft - overlap) / prr
expected_freq_bins = nfft // 2 + 1
expected_channels = 8 - 1 + 1  # = 8

# השווה למה שחזר:
print(f"lines_dt: {metadata.lines_dt} vs {expected_lines_dt}")
print(f"freq bins: {metadata.frequencies_amount} vs {expected_freq_bins}")
```

#### שלב 3: שאל את גיא
```
"מצאתי שהשרת מחזיר:
- lines_dt
- frequencies_amount
- channel_to_stream_index

יש spec document שמסביר איך הם מחושבים?
או שאני צריך reverse-engineer מהקוד?"
```

---

## 🎯 סיכום

### מקורות המידע:

| מקור | אחוז | אמינות | דוגמה |
|------|------|---------|--------|
| **קוד Python/MATLAB** | 40% | ✅ גבוהה | lines_dt, frequencies_amount |
| **מסמכי תיעוד** | 30% | ✅ בינונית-גבוהה | NFFT trade-offs table |
| **ידע כללי DSP** | 30% | ⚠️ צריך אימות | Frequency resolution formula |

### התשובה הכנה:

**לא הכל כתוב במפורש במסמכים!**

חלק מהטסטים (כמו lines_dt, frequencies_amount, channel_mapping) - **ישירות מהקוד**.

חלק מהטסטים (כמו frequency resolution, output rate) - **הסקה לוגית** מהקוד + ידע כללי על עיבוד אותות.

**לכן - צריך לאמת את הנוסחאות עם גיא או עם הקוד האמיתי לפני יישום!**

---

## ✅ מה לעשות הלאה?

### אופציה 1: אימות מול גיא (מומלץ!)
שאל את גיא:
1. "יש spec שמסביר את החישובים?"
2. "איך lines_dt מחושב?"
3. "איך frequencies_amount מחושב?"

### אופציה 2: Reverse Engineering
הרץ טסטים אמיתיים, בדוק responses, וחשב לבד את הנוסחאות.

### אופציה 3: קרא את קוד Focus Server
```bash
# מצא איפה lines_dt מחושב:
grep -r "lines_dt" pz/microservices/focus_server/
```

---

**Bottom Line:**  
**40% מהמידע מהקוד הקיים, 60% הסקות והנחות שצריכות אימות!**

רוצה שנריץ טסט אמיתי ונבדוק מה באמת חוזר מהשרת?

