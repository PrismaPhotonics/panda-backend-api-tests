# איך לבדוק את pz_core_libs - מדריך מפורט

**תאריך:** 2025-11-08  
**מטרה:** למצוא את ה-validation ב-pz_core_libs שגורם לבעיית "waiting for fiber"

---

## 📍 מיקום pz_core_libs

**Repository URL:**
```
git+ssh://git@github.com/PrismaPhotonics/pz-core-libs.git
```

**Requirements:**
- `pz/share/requirements.txt` (שורה 200)

---

## 🔧 שלב 1: Clone את ה-Repository

```bash
# Navigate to Projects directory
cd C:\Projects

# Clone the repository
git clone git@github.com:PrismaPhotonics/pz-core-libs.git

# Enter the repository
cd pz-core-libs
```

**אם אין גישה ל-SSH:**
```bash
# Try HTTPS instead
git clone https://github.com/PrismaPhotonics/pz-core-libs.git
```

---

## 🔍 שלב 2: חפש את ה-Validation Code

### 2.1. חפש את השגיאה המדויקת

```bash
# Search for the exact error message
grep -r "Cannot proceed.*Missing required" .
grep -r "Missing required fiber metadata fields" .
grep -r "Cannot proceed" . | grep -i "prr\|metadata"
```

### 2.2. חפש Validation של prr

```bash
# Search for prr validation patterns
grep -r "prr.*>.*0\|prr.*<=.*0" .
grep -r "@.*validator.*prr\|model_validator.*prr" .
grep -r "def.*validate.*prr\|validate.*prr" .
```

### 2.3. חפש ב-RecordingMetadata Files

```bash
# Find recording_metadata files
find . -name "*recording_metadata*" -type f

# Search in recording_metadata files
find . -name "*recording_metadata*" -type f | xargs grep -l "prr\|validation\|Cannot proceed"

# Search for RecordingMetadata class
find . -name "*.py" -type f | xargs grep -l "class RecordingMetadata"
```

### 2.4. חפש Pydantic Validators

```bash
# Search for Pydantic validators
grep -r "@model_validator\|@field_validator\|@validator" .
grep -r "from pydantic import.*validator\|from pydantic import.*model_validator" .
```

---

## 📜 שלב 3: בדוק את Git History

### 3.1. בדוק Commits אחרונים

```bash
# All recent commits
git log --all --since="3 weeks ago" --oneline

# Commits by ohad
git log --all --since="3 weeks ago" --oneline --author="ohad" -i

# Commits by any author with "ohad" in name/email
git log --all --since="3 weeks ago" --oneline --author="ohad" -i --all
```

### 3.2. בדוק Commits שקשורים ל-Validation

```bash
# Commits related to validation
git log --all --since="3 weeks ago" --oneline --grep="validation" -i

# Commits related to prr
git log --all --since="3 weeks ago" --oneline --grep="prr" -i

# Commits related to metadata
git log --all --since="3 weeks ago" --oneline --grep="metadata" -i

# Commits related to "Cannot proceed"
git log --all --since="3 weeks ago" --oneline -S "Cannot proceed"

# Commits related to "Missing required"
git log --all --since="3 weeks ago" --oneline -S "Missing required"
```

### 3.3. בדוק שינויים ב-RecordingMetadata Files

```bash
# Changes in recording_metadata files
git log --all --since="3 weeks ago" --oneline -- "**/recording_metadata*"

# Changes in any file with "metadata" in name
git log --all --since="3 weeks ago" --oneline -- "*metadata*"

# Detailed changes
git log --all --since="3 weeks ago" --patch -- "*recording_metadata*"
```

### 3.4. בדוק שינויים ספציפיים

```bash
# Find when "Cannot proceed" was added
git log --all -S "Cannot proceed" --oneline

# Find when "Missing required fiber metadata fields" was added
git log --all -S "Missing required fiber metadata fields" --oneline

# Find when prr validation was added
git log --all -S "prr" --grep="validation\|validate" -i --oneline
```

---

## 🔬 שלב 4: בדוק את הקוד של RecordingMetadata

### 4.1. מצא את הקובץ

```bash
# Find RecordingMetadata class definition
find . -name "*.py" -type f | xargs grep -l "class RecordingMetadata"

# Find files that import RecordingMetadata
find . -name "*.py" -type f | xargs grep -l "from.*recording_metadata import RecordingMetadata"
```

### 4.2. בדוק את ה-Class Definition

```bash
# Show RecordingMetadata class with context
find . -name "*.py" -type f | xargs grep -A 50 "class RecordingMetadata"

# Show all validators in RecordingMetadata
find . -name "*.py" -type f | xargs grep -B 5 -A 20 "@.*validator\|model_validator" | grep -A 20 "class RecordingMetadata"
```

### 4.3. בדוק את ה-prr Field

```bash
# Find prr field definition
grep -r "prr.*:" . | grep -i "recording_metadata\|class.*metadata"

# Find prr validation
grep -r -A 10 -B 10 "prr" . | grep -i "validator\|validate\|>.*0\|<=.*0"
```

---

## 📊 שלב 5: ניתוח Commits ספציפיים

### 5.1. בדוק Commit ספציפי

```bash
# Show commit details
git show <commit-hash>

# Show commit with file changes
git show <commit-hash> --stat

# Show only the diff
git show <commit-hash> --no-stat
```

### 5.2. בדוק מתי הוספה Validation

```bash
# Find when validation was added to RecordingMetadata
git log --all --follow -p -- "*recording_metadata*" | grep -B 10 -A 10 "validator\|validate\|prr.*>"

# Find when "Cannot proceed" was first added
git log --all --reverse -S "Cannot proceed" --oneline | head -1
git show <first-commit-hash>
```

---

## 🎯 מה לחפש בקוד

### 1. RecordingMetadata Class

**מיקום משוער:** `pz_core_libs/recording_metadata/__init__.py` או `pz_core_libs/recording_metadata/metadata.py`

**דוגמה למה לחפש:**
```python
from pydantic import BaseModel, model_validator, field_validator

class RecordingMetadata(BaseModel):
    prr: float
    dx: Optional[float] = None
    sw_version: str
    # ... other fields
    
    @model_validator(mode='after')
    def validate_prr(self):
        if self.prr <= 0:
            raise ValueError("Cannot proceed: Missing required fiber metadata fields: prr")
        return self
```

### 2. Recording.open_recording() Method

**מיקום משוער:** `pz_core_libs/recording/__init__.py` או `pz_core_libs/recording/recording.py`

**דוגמה למה לחפש:**
```python
def open_recording(uri, **kwargs):
    # ... open recording ...
    metadata = RecordingMetadata(**metadata_dict)
    
    # Validation
    if metadata.prr <= 0:
        raise ValueError("Cannot proceed: Missing required fiber metadata fields: prr")
    
    return recording
```

---

## 📝 דוח ממצאים

לאחר הבדיקה, צור דוח עם:

1. **מיקום הקוד** - איפה נמצא ה-validation
2. **Git History** - מתי נוסף ה-validation, מי הוסיף אותו
3. **הקוד המדויק** - מה ה-validation בודק
4. **הפתרון** - איך לתקן את הבעיה

---

## ✅ Checklist

- [ ] Clone את pz-core-libs repository
- [ ] חפש את השגיאה "Cannot proceed: Missing required fiber metadata fields: prr"
- [ ] חפש validation של prr ב-RecordingMetadata
- [ ] בדוק את Git History - commits אחרונים
- [ ] בדוק commits של אוהד
- [ ] מצא את הקוד המדויק שגורם לבעיה
- [ ] תעד את הממצאים בדוח

---

## 🔗 קישורים

- **Repository:** `git@github.com:PrismaPhotonics/pz-core-libs.git`
- **Requirements:** `pz/share/requirements.txt` (שורה 200)
- **Focus Server:** `pz/microservices/focus_server/focus_server.py`
- **RecordingToBuffer:** `pz/microservices/focus_server/prp_to_raw_consumer.py`

