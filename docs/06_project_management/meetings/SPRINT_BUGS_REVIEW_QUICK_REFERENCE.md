# 🐛 Quick Reference - Sprint Bugs Review
**תאריך:** 19 בנובמבר 2025

---

## 📊 מספרים מהירים

| מדד | ערך |
|-----|-----|
| **סה"כ באגים** | 28 |
| **באגים שתוקנו** | 0 (0%) |
| **באגים פתוחים** | 28 (100%) |
| **באגים חדשים** | 7 (מ-10/11) |

### חלוקה לפי עדיפות:
- 🔴 **Highest:** 6 (21%)
- 🟠 **High:** 10 (36%)
- 🟡 **Medium:** 12 (43%)

---

## 🔴 Highest Priority - חובה לתקן (6 באגים)

| ID | תיאור | אחראי | הערכה |
|----|-------|-------|-------|
| PZ-15003 | Spectrogram streaming rate לא לפי עיצוב | Oded | 2-3 ימים |
| PZ-14925 | Missing job_id label ב-K8s | Oded | 1-2 ימים |
| PZ-14846 | אין alert על disconnections | yonatan | 1 יום |
| PZ-14845 | אין אפשרות לפתוח analyzes אחרי crash | yonatan | 1-2 ימים |
| PZ-14843 | Z pool disconnect תחת עומס | yonatan | 2-3 ימים |
| PZ-14712 | Focus Server pod restarts (MongoDB) | yonatan | 2-3 ימים |

**סה"כ:** ~10-14 ימי עבודה

---

## 🟠 High Priority - מומלץ לתקן (10 באגים)

### API Validation (3) - Oded: 2-3 ימים
- PZ-14977: Alert API - missing required fields
- PZ-14976: Alert API - negative DOF values
- PZ-14975: Alert API - invalid Class ID

### MongoDB & Persistence (2): 3-5 ימים
- PZ-14926: Job config לא נשמר (Oded) - 1-2 ימים
- PZ-13983: MongoDB Indexes חסרים (Benny) - 2-3 ימים

### API Error Handling (3) - Benny: 3-4 ימים
- PZ-13669: SingleChannel View accepts multiple channels
- PZ-13667: Empty Status String in Configure Response
- PZ-13267: /configure returns 500 instead of 422

### אחר (2): 2-3 ימים
- PZ-13985: Live Metadata Missing Fields (Oded) - 1-2 ימים
- PZ-13984: Future Timestamp Validation (Ohad) - 1 יום

**סה"כ:** ~10-14 ימי עבודה

---

## 👥 חלוקה לפי אחראי

| אחראי | סה"כ | Highest | High | Medium | הערכה |
|-------|------|---------|------|--------|--------|
| **Oded** | 13 | 3 | 6 | 4 | 15-20 ימים |
| **yonatan** | 4 | 3 | 0 | 1 | 5-7 ימים |
| **Benny** | 7 | 1 | 3 | 3 | 8-10 ימים |
| **Ohad** | 1 | 0 | 1 | 0 | 1 יום |
| **ללא אחראי** | 3 | 0 | 1 | 2 | ? |

---

## 💬 נקודות דיבור מהירות

### פתיחה
- 28 באגים בסך הכל
- 7 באגים חדשים (מ-10/11)
- 0 באגים תוקנו ⚠️

### בעיות עיקריות
1. **API Validation** - הרבה בעיות validation
2. **MongoDB Issues** - בעיות connection ו-indexes
3. **Error Handling** - 500 במקום 422

### המלצות
- **חובה:** כל 6 Highest Priority (~10-14 ימים)
- **מומלץ:** כל 10 High Priority (~10-14 ימים)
- **סה"כ:** ~20-28 ימי עבודה

### שאלות לדיון
1. למה אף באג לא תוקן?
2. כמה זמן להקצות לתיקוני באגים?
3. איזה באגים חובה לתקן לפני Pre-FAT (30/11)?

---

## ⚠️ נקודות קריטיות

1. **Pre-FAT ב-30/11** - יש לנו 11 ימים
2. **0 באגים תוקנו** - צריך לטפל בזה
3. **Oded אחראי על 46%** - אולי צריך לחלק עבודה

---

**קישור ל-Jira:** https://prismaphotonics.atlassian.net/issues/?filter=13012

