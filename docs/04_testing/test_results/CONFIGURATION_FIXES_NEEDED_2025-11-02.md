# תיקוני קונפיגורציה נדרשים - 2 בנובמבר 2025

## 1. תיקון כתובת Kubernetes API

### הבעיה
הטסטים מנסים להתחבר ל-`10.10.10.151:6443` במקום לכתובת הנכונה

### הפתרון
```yaml
# לעדכן בקובץ config/environments.yaml
kubernetes:
  api_server: "https://10.10.100.102:6443"  # במקום 10.10.10.151
```

### קבצים לעדכון:
- `src/infrastructure/kubernetes_manager.py`
- `tests/infrastructure/test_external_connectivity.py`
- כל מקום שמשתמש ב-Kubernetes API

---

## 2. תיקון חיבור MongoDB

### הבעיה
11 טסטים נכשלים בחיבור ל-MongoDB - `client` מחזיר None

### בדיקות נדרשות:
```python
# 1. לוודא שהכתובת נכונה
mongodb:
  host: "10.10.100.108"
  port: 27017
  username: "prisma"
  password: "prisma"
  database: "prisma"
  auth_source: "prisma"

# 2. לבדוק קישוריות
from pymongo import MongoClient
client = MongoClient(
    "mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma",
    serverSelectionTimeoutMS=5000
)
client.admin.command('ping')
```

### פתרונות אפשריים:
1. MongoDB לא זמין/לא רץ
2. Firewall חוסם את הפורט
3. Credentials שגויים
4. Auth source לא נכון

---

## 3. תיקון חיבור SSH

### הבעיה
הטסט `test_ssh_connection` נכשל

### הפתרון - נתיב החיבור הנכון:
```bash
# שלב 1: Jump Host
ssh root@10.10.100.3
# Password: PASSW0RD

# שלב 2: Target Host
ssh prisma@10.10.100.113
# Password: PASSW0RD
```

### עדכון בקוד:
```python
# src/infrastructure/ssh_manager.py
SSH_CONFIG = {
    "jump_host": {
        "host": "10.10.100.3",
        "username": "root",
        "password": "PASSW0RD"
    },
    "target_host": {
        "host": "10.10.100.113",
        "username": "prisma",
        "password": "PASSW0RD"
    }
}
```

---

## 4. תיקוני Validation בטסטים

### 4.1 תיקון channels.min (7 טסטים)

**הבעיה:** channels.min מקבל 0 במקום >= 1

**הפתרון:**
```python
# לפני (שגוי)
config = {
    "channels": {"min": 0, "max": 10}  # ❌
}

# אחרי (נכון)
config = {
    "channels": {"min": 1, "max": 10}  # ✅
}
```

**קבצים לתיקון:**
- `tests/stress/test_extreme_configurations.py`
- `tests/integration/api/test_historic_playback_additional.py`
- `tests/integration/api/test_historic_playback_e2e.py`

### 4.2 תיקון Waterfall View (2 טסטים)

**הבעיה:** displayTimeAxisDuration לא רלוונטי ל-Waterfall

**הפתרון:**
```python
# לפני (שגוי)
config = {
    "view_type": ViewType.WATERFALL,
    "display_time_axis_duration": 30  # ❌ לא רלוונטי
}

# אחרי (נכון)
config = {
    "view_type": ViewType.WATERFALL
    # להסיר את display_time_axis_duration
}
```

**קבצים לתיקון:**
- `tests/integration/api/test_view_type_validation.py`
- `tests/integration/api/test_waterfall_view.py`

### 4.3 תיקון Time Range Validation

**הבעיה:** end_time < start_time

**הפתרון:**
```python
# לפני (שגוי)
config = {
    "start_time": 1762071028,
    "end_time": 1762071028  # ❌ שווה או קטן
}

# אחרי (נכון)
config = {
    "start_time": 1762071028,
    "end_time": 1762071128  # ✅ גדול יותר
}
```

---

## 5. סדר עדיפויות לתיקון

| עדיפות | תיקון | השפעה | מורכבות |
|--------|-------|--------|---------|
| 1 | Kubernetes API | 2 טסטים | נמוכה |
| 2 | MongoDB Connection | 11 טסטים | בינונית |
| 3 | Channels Validation | 7 טסטים | נמוכה |
| 4 | Waterfall View | 2 טסטים | נמוכה |
| 5 | SSH Connection | 1 טסט | נמוכה |

## סקריפט תיקון מהיר

```python
#!/usr/bin/env python3
"""Quick fix script for configuration issues"""

import os
import re
from pathlib import Path

def fix_kubernetes_api():
    """Fix Kubernetes API address"""
    files = Path(".").rglob("*.py")
    for file in files:
        content = file.read_text()
        if "10.10.10.151" in content:
            new_content = content.replace("10.10.10.151", "10.10.100.102")
            file.write_text(new_content)
            print(f"Fixed: {file}")

def fix_channels_validation():
    """Fix channels.min = 0 issues"""
    test_files = Path("tests").rglob("test_*.py")
    for file in test_files:
        content = file.read_text()
        # Fix channels min:0 to min:1
        new_content = re.sub(
            r'"min":\s*0\s*,\s*"max"',
            '"min": 1, "max"',
            content
        )
        if new_content != content:
            file.write_text(new_content)
            print(f"Fixed channels in: {file}")

def fix_waterfall_view():
    """Remove displayTimeAxisDuration from Waterfall tests"""
    files = [
        "tests/integration/api/test_view_type_validation.py",
        "tests/integration/api/test_waterfall_view.py"
    ]
    for filepath in files:
        file = Path(filepath)
        if file.exists():
            content = file.read_text()
            # Remove display_time_axis_duration when view_type is WATERFALL
            # This needs manual review
            print(f"Review needed: {filepath}")

if __name__ == "__main__":
    print("Starting configuration fixes...")
    fix_kubernetes_api()
    fix_channels_validation()
    fix_waterfall_view()
    print("Done! Please review changes and run tests again.")
```

## המלצות

1. **לבצע את התיקונים בסדר העדיפות**
2. **לאחר כל תיקון - להריץ את הטסטים הרלוונטיים**
3. **לתעד את השינויים בקובץ CHANGELOG**
4. **לוודא שהתיקונים לא שוברים טסטים אחרים**
