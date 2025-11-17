# Kubernetes Agent - Quick Start
================================

**Agent אינטראקטיבי לניהול סביבות Kubernetes (staging ו-production/kefar saba)**

---

## 🚀 הפעלה מהירה

```bash
# הפעלה עם staging (ברירת מחדל)
python scripts/k8s_agent.py

# הפעלה עם production
python scripts/k8s_agent.py --env production
```

---

## 📋 תכונות עיקריות

✅ **תמיכה בשתי סביבות**: staging ו-production (kefar saba)  
✅ **ניטור מלא**: pods, jobs, deployments, cluster info  
✅ **מחיקה בטוחה**: אישור לפני כל פעולה הרסנית  
✅ **ניהול קונפיגורציה**: שינוי סביבה דינמי  
✅ **תמיכה ב-SSH fallback**: עבודה גם ללא גישה ישירה ל-K8s API  

---

## 📊 פקודות זמינות

### ניטור:
- **1.** List all pods
- **2.** List gRPC job pods
- **3.** List all jobs
- **4.** List deployments
- **5.** Show cluster info
- **6.** Get pod logs
- **7.** Get pod details

### מחיקה (עם אישור):
- **8.** Delete pod (by name)
- **9.** Delete gRPC job pods (all)
- **10.** Delete gRPC job pods (by pattern)
- **11.** Delete job (by name)
- **12.** Delete multiple pods (by pattern)

### ניהול:
- **13.** Restart pod
- **14.** Scale deployment
- **15.** Switch environment
- **16.** Reconnect

---

## 💡 דוגמאות שימוש

### ניקוי gRPC jobs:
```bash
python scripts/k8s_agent.py --env staging
# בתפריט: בחר 9 (Delete gRPC job pods)
```

### בדיקת pod:
```bash
# בתפריט: בחר 7 (Get pod details) או 6 (Get pod logs)
```

### מעבר בין סביבות:
```bash
# בתפריט: בחר 15 (Switch environment)
```

---

## ⚠️ אזהרות

- **כל פעולות המחיקה דורשות אישור מפורש!**
- **היזהר במיוחד בעת מחיקת pods בסביבת production!**
- **תמיד בדוק את ה-pods לפני מחיקה (פקודה 1 או 2)**

---

## 📚 תיעוד מלא

למדריך מפורט, ראה: `docs/02_user_guides/K8S_AGENT_GUIDE.md`

---

**עדכון אחרון:** 2025-11-09

