# ✅ סקריפט החקירה מוכן להרצה
## Investigation Script Ready to Run

**תאריך:** 2025-11-13  
**סטטוס:** ✅ מוכן להרצה

---

## 📋 מה תוקן

### 1. תיקון MongoDB Database Access ✅
- תוקן קריאה ל-`get_database()` עם שם database מפורש
- הוסף תמיכה ב-kubernetes_manager ל-MongoDBManager

### 2. תיקון Imports ✅
- כל ה-imports תקינים
- Path resolution תקין

### 3. Error Handling ✅
- טיפול טוב יותר בשגיאות
- הודעות ברורות

---

## 🚀 איך להריץ

### דרך 1: Python Script (מומלץ)

```bash
# מהשורש של הפרויקט
python scripts/investigate_consumer_creation_issue.py --job-id 19-7 --environment staging
```

### דרך 2: דרך pytest

```bash
# מהשורש של הפרויקט
pytest be_focus_server_tests/integration/data_quality/test_investigate_consumer_creation.py -v -s
```

---

## 📊 מה הסקריפט בודק

1. **Backend Logs** ✅
   - מוצא Backend pod
   - מביא לוגים אחרונים
   - מחפש job_id בלוגים

2. **MongoDB** ✅
   - מתחבר ל-MongoDB
   - מחפש Job ב-collections שונים
   - מחפש Consumer ב-collections שונים

3. **Consumer Service** ✅
   - מחפש Pods של Consumer Service
   - מביא לוגים מכל Pod
   - מחפש job_id בלוגים

4. **K8s Pods and Labels** ✅
   - מוצא Pods שמכילים job_id בשם
   - בודק Labels של כל Pod
   - מנתח האם יש job_id label

---

## 🔍 תוצאות צפויות

הסקריפט יציג:
- ✅ מה Backend רואה בלוגים
- ✅ האם Job נרשם ב-MongoDB
- ✅ האם Consumer נרשם ב-MongoDB
- ✅ האם Consumer Service רץ
- ✅ מה ה-Labels של ה-Pods
- 💡 המלצות לתיקון

---

## ⚠️ אם יש בעיות

### בעיה: Python לא נמצא
**פתרון:**
1. לוודא ש-Python מותקן
2. לוודא ש-Python ב-PATH
3. להשתמש ב-`py` במקום `python` (Windows)

### בעיה: Import errors
**פתרון:**
1. לוודא שאתה בשורש הפרויקט
2. לוודא ש-PYTHONPATH מוגדר נכון
3. להריץ: `$env:PYTHONPATH = $PWD`

### בעיה: MongoDB connection failed
**פתרון:**
1. לוודא ש-MongoDB זמין
2. לבדוק את ה-IP וה-Port ב-`config/environments.yaml`
3. לבדוק credentials

### בעיה: K8s connection failed
**פתרון:**
1. לוודא ש-SSH access מוגדר
2. לבדוק את ה-SSH credentials ב-`config/environments.yaml`
3. לבדוק ש-kubectl זמין דרך SSH

---

## 📝 הערות

- הסקריפט משתמש ב-SSH fallback ל-K8s (יותר אמין)
- הסקריפט מטפל בשגיאות בצורה יפה
- הסקריפט מציג המלצות ברורות

---

**מחבר:** AI Assistant  
**תאריך:** 2025-11-13

