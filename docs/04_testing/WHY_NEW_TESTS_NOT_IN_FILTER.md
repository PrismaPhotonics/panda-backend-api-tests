# למה PZ-14018 ו-PZ-14019 לא נראים בפילטר?

**תאריך:** 28 באוקטובר 2025  
**בעיה:** 2 הטסטים החדשים לא מופיעים בפילטר `test plan == PZ-13756`

---

## 🔍 הסיבה

**2 הטסטים החדשים (PZ-14018, PZ-14019) לא מקושרים ל-Test Plan PZ-13756!**

---

## 📊 בדיקה ב-CSV

### טסטים שכן מקושרים (דוגמה):
```
PZ-13909,...,PZ-13756,...
PZ-13907,...,PZ-13756,...
PZ-13906,...,PZ-13756,...
```
→ יש להם `PZ-13756` בעמודה "Test plan"

### הטסטים החדשים:
```
PZ-14019,...,,(EMPTY),...
PZ-14018,...,,(EMPTY),...
```
→ **אין** להם `PZ-13756` בעמודה "Test plan"!

---

## ✅ הפתרון

### צריך לקשר את 2 הטסטים ל-Test Plan:

#### **בJira - PZ-14018:**
1. פתח את https://prismaphotonics.atlassian.net/browse/PZ-14018
2. עבור ל**"Test plan"** field
3. הוסף: **PZ-13756**
4. שמור

#### **בJira - PZ-14019:**
1. פתח את https://prismaphotonics.atlassian.net/browse/PZ-14019
2. עבור ל**"Test plan"** field
3. הוסף: **PZ-13756**
4. שמור

---

## 🎯 איך לעשות את זה (Bulk):

### אופציה 1: דרך Jira Web:
1. פתח PZ-14018
2. ב-"Links" section → "Test plan"
3. בחר PZ-13756
4. חזור על זה ל-PZ-14019

### אופציה 2: Bulk Edit:
```jql
key in (PZ-14018, PZ-14019)
```

1. בחר שני הטיקטים
2. Bulk Edit
3. Add to field: "Test plan"
4. Value: PZ-13756
5. Apply

---

## 📋 אחרי הקישור

**הפילטר יראה:**
```
test plan == PZ-13756
```

**תוצאה:**
- ✅ PZ-13909
- ✅ PZ-13907
- ✅ PZ-13906
- ... (כל הטסטים הישנים)
- ✅ **PZ-14018** ← יופיע!
- ✅ **PZ-14019** ← יופיע!

**סה"כ:** 134 טסטים (132 ישנים + 2 חדשים)

---

## 🔗 קישורים מהירים

- **PZ-14018:** https://prismaphotonics.atlassian.net/browse/PZ-14018
- **PZ-14019:** https://prismaphotonics.atlassian.net/browse/PZ-14019
- **Test Plan:** https://prismaphotonics.atlassian.net/browse/PZ-13756

---

**הסיבה:** הטסטים נוצרו **ללא קישור ל-Test Plan**  
**הפתרון:** קשר אותם ל-PZ-13756 ב-Jira

---

**אחרי זה הם יופיעו בפילטר!** ✅

