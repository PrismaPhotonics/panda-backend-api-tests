# NFFT Limits - סיכום מקסימומים

**תאריך:** 29 אוקטובר 2025  
**מקור:** `src/models/focus_server_models.py`

---

## 📊 NFFT מקסימלי לפי View Type

### 🔴 MultiChannel View
```python
MAX_NFFT_MULTICHANNEL = 2048
```

**מקסימום:** **2048**

**שימוש:**
- View Type = 0 (MultiChannel)
- View Type = 2 (Waterfall)

---

### 🔵 SingleChannel View
```python
MAX_NFFT_SINGLECHANNEL = 65536
```

**מקסימום:** **65,536** (פי 32 יותר!)

**שימוש:**
- View Type = 1 (SingleChannel)

---

## 🎯 ערכים תקפים (חזקות של 2)

```python
VALID_NFFT_POWER_OF_2 = [
    128,      # 2^7
    256,      # 2^8
    512,      # 2^9
    1024,     # 2^10
    2048,     # 2^11   ← Max MultiChannel
    4096,     # 2^12
    8192,     # 2^13
    16384,    # 2^14
    32768,    # 2^15
    65536     # 2^16   ← Max SingleChannel
]
```

---

## 📋 טבלת השוואה

| View Type | Max NFFT | Frequency Bins | Use Case |
|-----------|----------|----------------|----------|
| **MultiChannel (0)** | 2,048 | ~1,024 | ניטור מרובה ערוצים |
| **SingleChannel (1)** | 65,536 | ~32,768 | ניתוח מפורט של ערוץ אחד |
| **Waterfall (2)** | 2,048 | ~1,024 | מפת זמן-תדר |

---

## 💡 למה ההבדל?

### MultiChannel - מוגבל ל-2048
**סיבה:** עומס חישובי
```
אם יש 100 channels:
  100 channels × 2048 NFFT = 200,000 FFT points
  זה כבר עומס משמעותי!

אם היה NFFT=65536:
  100 channels × 65536 = 6,553,600 FFT points
  לא אפשרי בזמן אמת!
```

### SingleChannel - עד 65536
**סיבה:** רק ערוץ אחד
```
1 channel × 65536 NFFT = 65,536 FFT points
זה סביר למחשב אחד

מאפשר רזולוציה תדרית גבוהה מאוד:
  אם PRR = 1000 Hz:
  Frequency Resolution = 1000/65536 = 0.015 Hz (!!)
```

---

## 🧪 דוגמאות

### ✅ תקף - MultiChannel
```python
config = {
    "view_type": "0",  # MultiChannel
    "nfftSelection": 2048,  # ✓ Max allowed
    "channels": {"min": 1, "max": 100}
}
```

### ❌ לא תקף - MultiChannel
```python
config = {
    "view_type": "0",  # MultiChannel
    "nfftSelection": 4096,  # ✗ Too high! Max is 2048
    "channels": {"min": 1, "max": 100}
}
# → Expected: 400 Bad Request
```

### ✅ תקף - SingleChannel
```python
config = {
    "view_type": "1",  # SingleChannel
    "nfftSelection": 65536,  # ✓ Max allowed
    "channels": {"min": 5, "max": 5}
}
```

### ❌ לא תקף - SingleChannel
```python
config = {
    "view_type": "1",  # SingleChannel
    "nfftSelection": 131072,  # ✗ Too high! Max is 65536
    "channels": {"min": 5, "max": 5}
}
# → Expected: 400 Bad Request
```

---

## 📝 הערות חשובות

### 1. חייב להיות חזקה של 2
```python
# ✓ Valid:
[128, 256, 512, 1024, 2048, 4096, ...]

# ✗ Invalid:
[100, 300, 500, 1000, 1500, 3000, ...]
```

**למה?** אלגוריתמי FFT מהירים ביותר עם חזקות של 2 (Radix-2 FFT).

### 2. יש גם מינימום
```python
MIN_NFFT = 128  # קטן מזה לא מומלץ
```

### 3. Default Value
```python
DEFAULT_NFFT = 1024  # ערך ברירת מחדל
```

---

## 🔬 זיכרון ועומס

### חישוב זיכרון (בקירוב)

```python
# Per spectrogram frame:
memory_bytes = channels × (NFFT/2 + 1) × 4 bytes

# MultiChannel עם NFFT=2048:
100 channels × 1025 bins × 4 = ~410 KB per frame

# SingleChannel עם NFFT=65536:
1 channel × 32769 bins × 4 = ~131 KB per frame
```

### חישוב עומס CPU

```python
# FFT Complexity: O(N log N)

# MultiChannel עם 100 channels, NFFT=2048:
100 × 2048 × log2(2048) = 100 × 2048 × 11 = ~2,252,800 ops

# SingleChannel עם NFFT=65536:
1 × 65536 × log2(65536) = 65536 × 16 = ~1,048,576 ops

# למרות ש-SingleChannel משתמש ב-NFFT גבוה יותר,
# העומס הכולל קטן יותר (ערוץ אחד לעומת 100!)
```

---

## 🎯 המלצות לטסטים

### טסט #1: Validate Max NFFT per View Type
```python
def test_nfft_max_multichannel():
    """Test that MultiChannel rejects NFFT > 2048"""
    config = create_config(
        view_type="0",
        nfft=4096  # Too high!
    )
    
    with pytest.raises(APIError) as exc:
        api.configure(config)
    
    assert exc.value.status_code == 400
    assert "2048" in str(exc.value)

def test_nfft_max_singlechannel():
    """Test that SingleChannel rejects NFFT > 65536"""
    config = create_config(
        view_type="1",
        nfft=131072  # Too high!
    )
    
    with pytest.raises(APIError) as exc:
        api.configure(config)
    
    assert exc.value.status_code == 400
    assert "65536" in str(exc.value)
```

### טסט #2: Validate Power of 2
```python
def test_nfft_must_be_power_of_2():
    """Test that non-power-of-2 NFFT is rejected"""
    invalid_nfft = [100, 300, 500, 1000, 1500, 3000]
    
    for nfft in invalid_nfft:
        config = create_config(nfft=nfft)
        
        with pytest.raises(APIError) as exc:
            api.configure(config)
        
        assert exc.value.status_code == 400
        assert "power of 2" in str(exc.value).lower()
```

### טסט #3: Validate All Valid Values
```python
@pytest.mark.parametrize("nfft", [128, 256, 512, 1024, 2048])
def test_multichannel_accepts_all_valid_nfft(nfft):
    """Test that all valid NFFT values are accepted for MultiChannel"""
    config = create_config(
        view_type="0",
        nfft=nfft
    )
    
    response = api.configure(config)
    assert response.status_code == 200

@pytest.mark.parametrize("nfft", [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536])
def test_singlechannel_accepts_all_valid_nfft(nfft):
    """Test that all valid NFFT values are accepted for SingleChannel"""
    config = create_config(
        view_type="1",
        nfft=nfft,
        channels={"min": 5, "max": 5}
    )
    
    response = api.configure(config)
    assert response.status_code == 200
```

---

## 📊 סיכום

| Parameter | Value | Notes |
|-----------|-------|-------|
| **MultiChannel Max** | 2,048 | עד 11 bit |
| **SingleChannel Max** | 65,536 | עד 16 bit |
| **Minimum** | 128 | 7 bit |
| **Default** | 1,024 | 10 bit |
| **Constraint** | חזקה של 2 | 2^n |

---

**מקור:** `src/models/focus_server_models.py` (lines 34-36)  
**תאריך עדכון:** 29 אוקטובר 2025

