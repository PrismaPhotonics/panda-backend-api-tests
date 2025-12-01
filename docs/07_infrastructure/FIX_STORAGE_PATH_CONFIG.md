# תיקון storage_mount_path ב-ConfigMap

## הבעיה

Focus Server מוגדר לחפש הקלטות ב-`/prisma/root/recordings/segy` אבל ההקלטות נמצאות ב-`/prisma/root/recordings`.

## הפתרון

צריך לשנות את ההגדרה ב-ConfigMap `prisma-config`.

---

## שיטה 1: עריכה ישירה (מומלץ)

### שלב 1: עריכת ה-ConfigMap

```bash
kubectl edit configmap prisma-config -n panda
```

### שלב 2: מצא את השורה הבאה:

```python
storage_mount_path = '/prisma/root/recordings/segy'
```

### שלב 3: שנה ל:

```python
storage_mount_path = '/prisma/root/recordings'
```

### שלב 4: שמור ויצא (ב-vi: `:wq`, ב-nano: `Ctrl+X` ואז `Y`)

### שלב 5: Restart את ה-pod

```bash
kubectl rollout restart deployment panda-panda-focus-server -n panda
```

---

## שיטה 2: הורדה, עריכה, עדכון

### שלב 1: הורדת ה-ConfigMap

```bash
kubectl get configmap prisma-config -n panda -o yaml > prisma-config.yaml
```

### שלב 2: עריכת הקובץ

פתח את `prisma-config.yaml` בעורך טקסט וחפש:

```python
storage_mount_path = '/prisma/root/recordings/segy'
```

שנה ל:

```python
storage_mount_path = '/prisma/root/recordings'
```

**חשוב:** בקובץ YAML, זה בתוך שדה `data.default_config.py` כטקסט מוברח (escaped).

אם אתה רואה:
```
storage_mount_path = \'/prisma/root/recordings/segy\'
```

שנה ל:
```
storage_mount_path = \'/prisma/root/recordings\'
```

### שלב 3: עדכון ה-ConfigMap

```bash
kubectl apply -f prisma-config.yaml
```

### שלב 4: Restart את ה-pod

```bash
kubectl rollout restart deployment panda-panda-focus-server -n panda
```

---

## שיטה 3: שימוש בסקריפט אוטומטי

```bash
$env:FOCUS_ENV = "staging"
py scripts/fix_storage_path_config.py
```

הסקריפט יבצע את כל השלבים אוטומטית.

---

## אימות שהתיקון עבד

### 1. בדוק שה-pod רץ מחדש

```bash
kubectl get pods -n panda | grep focus-server
```

### 2. בדוק את ההגדרה החדשה

```bash
kubectl exec -n panda <pod-name> -- cat /home/prisma/pz/config/py/default_config.py | grep storage_mount_path
```

צריך לראות:
```
storage_mount_path = '/prisma/root/recordings'
```

### 3. בדוק שה-API מחזיר הקלטות

```bash
# קבל pod name
POD_NAME=$(kubectl get pods -n panda | grep focus-server | awk '{print $1}')

# בדוק עם timestamps מ-Nov 26
kubectl exec -n panda $POD_NAME -- curl -s -X POST http://localhost:5000/recordings_in_time_range \
  -H "Content-Type: application/json" \
  -d '{"start_time": 1732641360, "end_time": 1732641600}'
```

צריך לראות מערך של timestamps, לא `[]`.

---

## הערות חשובות

1. **גיבוי:** לפני שינוי, מומלץ לגבות:
   ```bash
   kubectl get configmap prisma-config -n panda -o yaml > prisma-config-backup-$(date +%Y%m%d-%H%M%S).yaml
   ```

2. **זמן restart:** ה-pod יכול לקחת 1-2 דקות להתחיל מחדש.

3. **בדיקות:** אחרי התיקון, בדוק שה-API מחזיר הקלטות כמו שצריך.

4. **השפעה:** השינוי משפיע רק על Focus Server. שירותים אחרים לא מושפעים.

---

## בעיות נפוצות

### ה-pod לא מתחיל מחדש

```bash
# בדוק את ה-logs
kubectl logs -n panda <pod-name> --tail=50

# בדוק את ה-status
kubectl describe pod <pod-name> -n panda
```

### ה-API עדיין מחזיר `[]`

1. ודא שה-pod רץ מחדש
2. חכה 30 שניות אחרי ה-restart
3. בדוק שה-ConfigMap עודכן:
   ```bash
   kubectl get configmap prisma-config -n panda -o yaml | grep storage_mount_path
   ```

---

## סיכום

הבעיה הייתה שה-`storage_mount_path` היה מוגדר ל-`/prisma/root/recordings/segy` (collection של SEGY) במקום ל-`/prisma/root/recordings` (collection הראשית עם 53,211 הקלטות).

אחרי התיקון, Focus Server יחפש ב-collection הנכונה ויחזיר את ההקלטות.


