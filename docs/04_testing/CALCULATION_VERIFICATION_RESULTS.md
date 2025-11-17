# תוצאות אימות חישובים - ממצאים קריטיים!

**תאריך:** 29 אוקטובר 2025  
**טסט:** Verification של נוסחאות חישוב מול מערכת אמיתית  
**סטטוס:** 🔴 **הנוסחאות לא נכונות!**

---

## 📊 תוצאות הבדיקה

### ✅ מה שעבד (1/6)
- **Channel Count** = max - min + 1 ✅ **נכון!**
  - Expected: 8
  - Actual: 8

### ❌ מה שלא עבד (5/6)

#### 1️⃣ Frequency Bins - **שגוי לגמרי!**
```
Expected: 257 (מהנוסחה: NFFT/2 + 1 = 512/2 + 1)
Actual:   32
Diff:     225 (!!)
```

**מסקנה:** הנוסחה `NFFT/2 + 1` **לא נכונה** למערכת הזו!

#### 2️⃣ lines_dt - **שגוי פי 6!**
```
Expected: 0.256 seconds (מהנוסחה: (NFFT - Overlap) / PRR)
Actual:   0.0390625 seconds
Diff:     0.217 seconds (פער של פי 6.5!)
```

**מסקנה:** הנוסחה `(NFFT - Overlap) / PRR` **לא נכונה**!

#### 3️⃣ Output Rate - **שגוי פי 6!**
```
Expected: 3.906 lines/sec
Actual:   25.6 lines/sec (!)
Diff:     21.7 lines/sec
```

**מסקנה:** המערכת מייצרת **פי 6 יותר lines!**

#### 4️⃣ Stream Amount - **לא תואם!**
```
Expected: 8 (stream לכל channel)
Actual:   3 (!)
```

**מסקנה:** המערכת **מאגדת channels לתוך streams!**

#### 5️⃣ Channel Mapping - **אגידה של channels!**
```
Expected: {1:0, 2:1, 3:2, 4:3, 5:4, 6:5, 7:6, 8:7}
Actual:   {1:0, 2:0, 3:0, 4:1, 5:1, 6:1, 7:2, 8:2}
```

**מסקנה:** כל 2-3 channels מאוגדים ל-stream אחד!

---

## 🔍 ניתוח מעמיק

### למה 32 frequency bins ולא 257?

**הנתונים:**
- קיבלנו `frequencies_amount = 32`
- בקשנו `NFFT = 512`
- לפי הנוסחה `NFFT/2 + 1 = 257`

**אפשרויות:**

#### אפשרות 1: Frequency Decimation
```
אם יש decimation של פקטור 8:
257 / 8 ≈ 32 ✓
```

#### אפשרות 2: NFFT אחר בפועל
```
אם frequencies_amount = 32:
32 = NFFT/2 + 1
NFFT = 62 (?)

אבל זה לא power of 2!
```

#### אפשרות 3: Frequency Range Filtering
```
frequencies_list: [0, 15.59, 31.19, 46.78, 62.38, ...]

אם זה עד 500 Hz (מה שביקשנו):
32 bins * 15.59 Hz/bin ≈ 500 Hz ✓

frequency resolution = 15.59 Hz
זה לא 1.953 Hz שציפינו!
```

**המסקנה הכי סבירה:**  
המערכת עושה **downsampling/decimation** כדי להתאים לטווח התדר המבוקש!

---

### למה lines_dt = 0.039 ולא 0.256?

**הנתונים:**
- `lines_dt = 0.0390625`
- זה בדיוק `1/25.6 = 0.0390625`

**חישוב הפוך:**
```
אם lines_dt = (NFFT - Overlap) / PRR:
0.0390625 = (NFFT - Overlap) / PRR

נניח PRR = 1000:
(NFFT - Overlap) = 0.0390625 * 1000 = 39.0625

אם Overlap = 0 (no overlap):
NFFT = 39 (??)

זה לא הגיוני! NFFT צריך להיות 512!
```

**אפשרות אחרת - PRR שונה:**
```
אם NFFT = 512, Overlap = 256:
lines_dt = (512 - 256) / PRR = 0.0390625
256 / PRR = 0.0390625
PRR = 256 / 0.0390625 = 6553.6 Hz (!!)

זה הרבה יותר גבוה מ-1000 Hz!
```

**המסקנה:**  
או ש-**PRR שלנו לא נכון** (לא 1000 Hz), או שיש **time compression/decimation**.

---

### למה Stream Amount = 3 ולא 8?

**הנתונים:**
```
Channel Mapping:
  Channels 1-3 → Stream 0
  Channels 4-6 → Stream 1
  Channels 7-8 → Stream 2
```

**פטרן:**
- Stream 0: 3 channels
- Stream 1: 3 channels
- Stream 2: 2 channels

**למה המערכת עושה את זה?**

#### אפשרות 1: אופטימיזציה של Bandwidth
```
במקום להעביר 8 streams נפרדים:
→ מאגדים ל-3 streams
→ חוסכים bandwidth וזיכרון
```

#### אפשרות 2: Hardware Limitation
```
אולי המערכת יכולה רק 3-4 streams concurrent?
```

#### אפשרות 3: View Type Specific
```
אולי MultiChannel view מאגד channels?
SingleChannel view אולי לא מאגד?
```

**המסקנה:**  
המערכת **אוטומטית מאגדת** channels לתוך מספר קטן יותר של streams. זה **לא 1:1 mapping**!

---

## 📋 רשימת שאלות קריטיות לגיא

### 1. מה זה NFFT בפועל?
```
❓ כשמבקשים NFFT=512, מה באמת קורה?
❓ יש decimation אוטומטי?
❓ NFFT משתנה לפי frequency range?
```

### 2. מה זה PRR (Pulse Repetition Rate)?
```
❓ מה הPRR האמיתי של המערכת?
❓ זה 1000 Hz? 6500 Hz? משתנה?
❓ איפה אפשר לראות את זה בAPI?
```

### 3. איך Frequency Bins מחושב?
```
❓ למה קיבלנו 32 bins ולא 257?
❓ זה תלוי בfrequency range שביקשנו?
❓ הנוסחה היא: bins = (freq_max - freq_min) / resolution?
```

### 4. למה lines_dt כל כך קטן?
```
❓ למה 0.039 sec ולא 0.256 sec?
❓ יש time compression?
❓ יש דגימה מחדש?
```

### 5. למה Channels מאוגדים ל-Streams?
```
❓ מה הלוגיקה של האיגוד?
❓ זה תמיד 3 streams?
❓ איך זה תלוי בview type?
❓ SingleChannel גם מאגד?
```

### 6. יש Spec Document?
```
❓ יש מסמך שמסביר את החישובים?
❓ יש API שמחזיר את הפרמטרים האמיתיים (PRR, etc)?
❓ יש endpoint ל-/system/info או /config?
```

---

## 🎯 מה הלאה?

### שלב 1: קבל מידע מגיא (קריטי!)
**לפני שממשיכים לכתוב טסטים**, צריך לברר:
1. מה הנוסחאות האמיתיות?
2. מה הערכים האמיתיים של PRR?
3. יש spec document?

### שלב 2: בדוק endpoints נוספים
```python
# אולי יש endpoint שמחזיר system info?
GET /system/info
GET /config
GET /sensors
GET /parameters

# אולי אפשר לראות מה הPRR:
GET /channels
```

### שלב 3: נסה תצורות שונות
```python
# נסה NFFT אחר:
NFFT = 256, 1024, 2048

# נסה frequency range שונה:
freq = 0-1000 (full range)

# נסה SingleChannel:
channels = {min: 5, max: 5}

# ראה אם הפטרנים משתנים
```

---

## 💡 תובנות חשובות

### ✅ מה למדנו:

1. **הנוסחאות הכלליות לא עובדות!**  
   - `NFFT/2 + 1` לא נכון
   - `(NFFT - Overlap) / PRR` לא נכון
   - `stream_amount = channel_amount` לא נכון

2. **המערכת עושה אופטימיזציות:**
   - Frequency decimation
   - Time compression
   - Channel grouping

3. **צריך להבין את הלוגיקה הפנימית**
   - לא אפשר reverse-engineer בלי spec
   - צריך documentation או source code

### ❌ מה לא יעבוד:

לא אפשר לכתוב טסטים שבודקים חישובים **בלי לדעת את הנוסחאות האמיתיות**!

---

## 📝 המלצות

### למנהל הפרויקט:

**לא לממש את טסטי החישובים עד שיש:**
1. ✅ Spec document רשמי
2. ✅ נוסחאות מאומתות
3. ✅ הבנה של הלוגיקה הפנימית

**במקום זאת, להתמקד ב:**
- ✅ טסטי Integration (API calls)
- ✅ טסטי Validation (input validation)
- ✅ טסטי Resilience (outages)
- ✅ טסטי E2E (user flows)

### לצוות הQA:

**מה כן אפשר לבדוק בלי החישובים:**
1. Response structure (fields exist?)
2. Data types (int, float, dict?)
3. Consistency (same input → same output?)
4. Ranges (values within bounds?)

**מה לא אפשר לבדוק:**
1. Calculation correctness ❌
2. Formula validation ❌
3. Mathematical accuracy ❌

---

## 🔴 סיכום

**הניסיון לאמת את הנוסחאות הראה:**

1. **הנוסחאות שלנו שגויות** (או לפחות לא מתאימות למערכת)
2. **המערכת עושה אופטימיזציות** שלא ידענו עליהן
3. **צריך spec רשמי מגיא** לפני שממשיכים

**המלצה:**  
לדחות את יישום טסטי החישובים (15 טסטים) עד שיש מידע רשמי מגיא.

**במקום זאת, להתמקד ב-3 הדרישות האחרות:**
- ✅ Resilience Tests (דרישה #2 מגיא)
- ✅ Data Flow Tests (דרישה #3 מגיא)
- ✅ Exception Handling Tests (דרישה #4 מגיא)

---

**תאריך בדיקה:** 29 אוקטובר 2025  
**נבדק על:** Production Environment (10.10.100.100)  
**Job ID:** 2-5756

