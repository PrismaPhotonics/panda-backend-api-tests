# Best Practices: Creating Tests - Lessons Learned
## שיטות עבודה מומלצות: יצירת טסטים - לקחים שנלמדו

**תאריך:** 2025-11-13  
**חומרה:** CRITICAL  
**סטטוס:** ✅ מסמך חובה לפני יצירת טסטים חדשים

---

## 🚨 **הטעויות הקריטיות שעשיתי**

### **1. לא בדקתי איזה APIs קיימים לפני שימוש**

**הטעות:**
- יצרתי טסטים שמשתמשים ב-`get_task_metadata()` ו-`get_waterfall()`
- לא בדקתי אם ה-endpoints האלה מיושמים ב-backend
- לא בדקתי את הקוד הקיים כדי לראות איך טסטים אחרים עושים את זה

**התוצאה:**
- כל הטסטים נכשלו עם 404
- בזבוז זמן על debugging
- בלבול - נראה שיש בעיה ב-backend אבל זה באג בטסטים

### **2. לא בדקתי את הקוד הקיים**

**הטעות:**
- לא חיפשתי טסטים קיימים שמשתמשים ב-metadata endpoint
- לא בדקתי איך טסטים אחרים עושים את זה
- לא למדתי מהדפוסים הקיימים

**התוצאה:**
- יצרתי טסטים עם באגים שהיו יכולים להימנע בקלות
- לא השתמשתי ב-`get_job_metadata()` שכבר קיים ועובד

### **3. לא בדקתי את התיעוד**

**הטעות:**
- לא בדקתי את `docs/02_user_guides/FOCUS_SERVER_API_ENDPOINTS.md`
- לא ראיתי שה-endpoints לא קיימים
- לא קראתי את הטסטים הקיימים שמסומנים כ-SKIP

**התוצאה:**
- יצרתי טסטים ל-endpoints שלא קיימים
- בזבוז זמן על debugging

---

## ✅ **שיטות עבודה מומלצות - חובה לפני יצירת טסט**

### **1. בדוק איזה APIs קיימים**

**לפני שימוש ב-API, תמיד:**

1. **קרא את התיעוד:**
   ```bash
   # בדוק את התיעוד של ה-API
   docs/02_user_guides/FOCUS_SERVER_API_ENDPOINTS.md
   ```

2. **חפש טסטים קיימים:**
   ```bash
   # חפש טסטים שמשתמשים ב-API הזה
   grep -r "get_job_metadata\|get_task_metadata" be_focus_server_tests/
   ```

3. **בדוק את הקוד:**
   ```bash
   # בדוק את ה-implementation
   src/apis/focus_server_api.py
   ```

4. **בדוק אם יש SKIP:**
   ```bash
   # חפש טסטים שמסומנים כ-SKIP
   grep -r "@pytest.mark.skip" be_focus_server_tests/
   ```

### **2. למד מהטסטים הקיימים**

**לפני יצירת טסט חדש:**

1. **חפש טסטים דומים:**
   ```bash
   # חפש טסטים שעושים משהו דומה
   codebase_search "test uses get_job_metadata successfully"
   ```

2. **קרא את הטסטים הקיימים:**
   - איך הם משתמשים ב-API?
   - איך הם מטפלים ב-exceptions?
   - איך הם בודקים את התוצאות?

3. **העתק דפוסים שעובדים:**
   - אם יש טסט שעובד, השתמש באותו דפוס
   - אל תמציא דפוסים חדשים בלי סיבה

### **3. בדוק את ה-API לפני שימוש**

**לפני שימוש ב-API חדש:**

1. **קרא את ה-docstring:**
   ```python
   # תמיד קרא את ה-docstring
   help(focus_server_api.get_job_metadata)
   ```

2. **בדוק את ה-signature:**
   ```python
   # בדוק מה הפונקציה מחזירה
   inspect.signature(focus_server_api.get_job_metadata)
   ```

3. **בדוק את ה-exceptions:**
   ```python
   # בדוק איזה exceptions הפונקציה זורקת
   # קרא את הקוד ב-src/apis/focus_server_api.py
   ```

### **4. בדוק את התיעוד**

**לפני יצירת טסט:**

1. **קרא את התיעוד של ה-API:**
   - `docs/02_user_guides/FOCUS_SERVER_API_ENDPOINTS.md`
   - בדוק איזה endpoints קיימים
   - בדוק איזה endpoints לא קיימים

2. **קרא את הטסטים הקיימים:**
   - בדוק אם יש טסטים דומים
   - בדוק אם יש טסטים שמסומנים כ-SKIP

3. **קרא את ה-אנליזות:**
   - `docs/04_testing/analysis/`
   - בדוק אם יש בעיות ידועות

---

## 📋 **Checklist לפני יצירת טסט חדש**

### **לפני כתיבת הקוד:**

- [ ] קראתי את התיעוד של ה-API (`docs/02_user_guides/FOCUS_SERVER_API_ENDPOINTS.md`)
- [ ] בדקתי איזה endpoints קיימים
- [ ] חיפשתי טסטים קיימים שמשתמשים ב-API הזה
- [ ] קראתי את הטסטים הקיימים כדי ללמוד את הדפוסים
- [ ] בדקתי אם יש טסטים שמסומנים כ-SKIP
- [ ] קראתי את ה-docstring של הפונקציה
- [ ] בדקתי מה הפונקציה מחזירה
- [ ] בדקתי איזה exceptions הפונקציה זורקת
- [ ] בדקתי את הקוד ב-`src/apis/focus_server_api.py`

### **אחרי כתיבת הקוד:**

- [ ] הטסט משתמש ב-API הנכון
- [ ] הטסט מטפל ב-exceptions נכון
- [ ] הטסט בודק את התוצאות נכון
- [ ] הטסט עובד (הרצתי אותו)
- [ ] הטסט לא משתמש ב-APIs שלא קיימים

---

## 🎯 **דוגמאות**

### **❌ טעות - מה לא לעשות:**

```python
# לא לבדוק איזה API קיים
def test_something(self, focus_server_api):
    response = focus_server_api.configure_streaming_job(config)
    job_id = response.job_id
    
    # ❌ משתמש ב-API שלא קיים!
    metadata = focus_server_api.get_task_metadata(job_id)  # לא קיים!
    waterfall = focus_server_api.get_waterfall(job_id, 100)  # לא קיים!
```

### **✅ נכון - מה לעשות:**

```python
# לבדוק איזה API קיים לפני שימוש
def test_something(self, focus_server_api):
    response = focus_server_api.configure_streaming_job(config)
    job_id = response.job_id
    
    # ✅ משתמש ב-API שקיים ועובד!
    try:
        metadata = focus_server_api.get_job_metadata(job_id)  # קיים!
        # אם הגענו לכאן, ה-consumer קיים
    except APIError as e:
        # 404 = consumer לא קיים עדיין
        if "404" in str(e):
            # ממשיך לחכות
            pass
```

---

## 📝 **סיכום**

### **הכללים הקריטיים:**

1. **תמיד בדוק את התיעוד לפני שימוש ב-API**
2. **תמיד חפש טסטים קיימים שמשתמשים ב-API**
3. **תמיד למד מהטסטים הקיימים**
4. **תמיד בדוק אם ה-endpoint קיים לפני שימוש**
5. **תמיד השתמש ב-APIs שעובדים**

### **אם אתה לא בטוח:**

1. **חפש בקוד הקיים**
2. **קרא את התיעוד**
3. **בדוק את הטסטים הקיימים**
4. **שאל לפני שאתה יוצר טסט חדש**

---

**מחבר:** AI Assistant  
**תאריך:** 2025-11-13  
**סטטוס:** ✅ מסמך חובה לפני יצירת טסטים חדשים

