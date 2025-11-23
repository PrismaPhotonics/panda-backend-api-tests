# ✅ בדיקת התקנת Runner - סיכום

## מה רואים בלוגים:

### ✅ הצלחות:
1. **Runner Registration:** `√ Runner successfully added` ✅
2. **Settings Saved:** `√ Settings Saved` ✅
3. **Service Created:** השירות נוצר ב-systemd ✅
4. **Service Active:** `Active: active (running)` ✅
5. **Listener Running:** `Started listener process` ✅

### ⚠️ מה לבדוק:

1. **Labels:** ה-runner צריך להיות עם labels: `self-hosted,Linux`
2. **Online Status:** צריך להיות online ב-GitHub
3. **Workflow Match:** ה-workflow מחפש `runs-on: [self-hosted, Linux]`

---

## בדיקות נוספות:

### 1. בדוק שה-runner online ב-GitHub:
```bash
# לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
# צריך לראות: staging-contract-tests-runner עם סטטוס "Online" (ירוק)
```

### 2. בדוק את ה-labels:
```bash
# ב-GitHub → Settings → Actions → Runners → staging-contract-tests-runner
# צריך להיות labels: self-hosted, Linux
```

### 3. בדוק לוגים:
```bash
# על worker-node:
journalctl -u actions.runner.PrismaPhotonics-panda-backend-api-tests.staging-contract-tests-runner.service -f

# צריך לראות:
# - "Listening for Jobs"
# - "Connected to GitHub"
```

### 4. בדוק שה-runner יכול לגשת ל-Focus Server:
```bash
# על worker-node:
curl -k https://10.10.10.100/focus-server/channels
# צריך להחזיר JSON
```

### 5. בדוק שה-workflow מוגדר נכון:
```bash
# קובץ: .github/workflows/contract-tests.yml
# צריך להיות: runs-on: [self-hosted, Linux]
```

---

## סיכום - מה צריך להיות:

✅ **Runner מותקן:** `/opt/actions-runner`  
✅ **Service רץ:** `actions.runner.PrismaPhotonics-panda-backend-api-tests.staging-contract-tests-runner.service`  
✅ **Listener פעיל:** `Runner.Listener run --startuptype service`  
✅ **Labels:** `self-hosted, Linux`  
✅ **Network Access:** יכול לגשת ל-`10.10.10.100`  

---

## מה הלאה:

1. **ודא שה-runner online ב-GitHub** (הכי חשוב!)
2. **בדוק labels** - צריך להיות `self-hosted, Linux`
3. **הרץ workflow test** - push commit או trigger manual
4. **בדוק לוגים** - `journalctl -u actions.runner... -f`

---

## אם הכל תקין:

ה-contract tests ירוצו אוטומטית על כל push/PR! 🚀

---

## אם יש בעיות:

### Runner לא online:
```bash
# בדוק לוגים:
journalctl -u actions.runner.PrismaPhotonics-panda-backend-api-tests.staging-contract-tests-runner.service -n 50

# Restart:
sudo systemctl restart actions.runner.PrismaPhotonics-panda-backend-api-tests.staging-contract-tests-runner.service
```

### Labels לא נכונים:
```bash
# ב-GitHub → Settings → Actions → Runners → Edit
# הוסף: self-hosted, Linux
```

### Workflow לא מוצא runner:
- בדוק שה-workflow משתמש ב: `runs-on: [self-hosted, Linux]`
- בדוק שה-runner יש לו את ה-labels האלה

---

**הכל נראה טוב! רק צריך לוודא שה-runner online ב-GitHub!**

