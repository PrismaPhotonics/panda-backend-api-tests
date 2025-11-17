# עדכון קוד PZ מ-Bitbucket

## 🎯 מטרה
עדכון קוד ה-PZ מ-Bitbucket repository לסביבת העבודה

---

## 📍 איפה הקוד נמצא?

### 1. Worker Node (10.10.100.113)
```
/home/prisma/pz/                    - הקוד הראשי
/home/prisma/debug-codebase/pz/     - גרסת debug
```

### 2. בתוך הפודים של Kubernetes
```
/home/prisma/pz/                    - בתוך Focus Server pod
```

---

## 🔄 שיטה 1: עדכון ב-Worker Node (המומלץ)

### צעדים:

#### 1. התחבר ל-Worker Node
```bash
# מה-Windows:
ssh root@10.10.100.3
ssh prisma@10.10.100.113
```

#### 2. נווט לתיקיית הקוד
```bash
cd /home/prisma/pz
```

#### 3. בדוק את הסטטוס הנוכחי
```bash
# בדוק באיזה branch אתה
git branch

# בדוק אם יש שינויים לא שמורים
git status

# בדוק את ה-remote
git remote -v
```

#### 4. שמור שינויים מקומיים (אם יש)
```bash
# אם יש שינויים שאתה רוצה לשמור:
git stash save "Local changes before pull - $(date +%Y%m%d_%H%M%S)"

# או אם אתה רוצה לבטל שינויים מקומיים:
git reset --hard HEAD
```

#### 5. עדכן את הקוד
```bash
# אפשרות 1: Pull מה-branch הנוכחי
git pull origin $(git branch --show-current)

# אפשרות 2: Pull מ-master/main
git pull origin master
# או
git pull origin main

# אפשרות 3: Pull branch ספציפי
git fetch origin
git checkout <branch-name>
git pull origin <branch-name>
```

#### 6. החזר שינויים מקומיים (אם שמרת ב-stash)
```bash
git stash pop
```

---

## 🔄 שיטה 2: Clone מחדש (אם אין repository מקומי)

```bash
# 1. התחבר ל-Worker Node
ssh root@10.10.100.3
ssh prisma@10.10.100.113

# 2. גבה את התיקייה הישנה
cd /home/prisma
mv pz pz_backup_$(date +%Y%m%d_%H%M%S)

# 3. Clone מחדש (צריך את ה-URL של הrepo)
git clone <BITBUCKET_REPO_URL> pz

# דוגמאות אפשריות:
# git clone https://bitbucket.org/prisma-photonics/pz.git
# git clone git@bitbucket.org:prisma-photonics/pz.git
# git clone https://<username>@bitbucket.org/prisma-photonics/pz.git

# 4. נווט לתיקייה החדשה
cd pz

# 5. בדוק שהכל תקין
git log -5
ls -la
```

---

## 🐋 שיטה 3: עדכון בפוד (דורש rebuild)

### אם השינויים צריכים להיכנס לפוד רץ:

```bash
# 1. התחבר ל-Worker Node
ssh root@10.10.100.3
ssh prisma@10.10.100.113

# 2. עדכן את הקוד המקומי (שיטה 1)
cd /home/prisma/pz
git pull origin master

# 3. בנה Docker image חדש (אם יש Dockerfile)
# (זה תלוי במבנה של הפרויקט)
docker build -t focus-server:latest .

# או אם יש סקריפט build:
./build.sh

# 4. עדכן את הפוד (אם זה ConfigMap)
kubectl delete configmap pz-config -n panda
kubectl create configmap pz-config --from-file=/home/prisma/pz/config -n panda

# 5. אתחל את הפוד (כדי שיטען את הקוד החדש)
kubectl delete pod -n panda $(kubectl get pods -n panda -l app.kubernetes.io/name=panda-panda-focus-server -o name)

# הפוד יעלה מחדש אוטומטית עם הקוד המעודכן
```

---

## 🔐 התחברות עם Credentials

### אם צריך credentials ל-Bitbucket:

#### Option 1: HTTPS עם username/password
```bash
git pull https://<username>:<password>@bitbucket.org/prisma-photonics/pz.git
```

#### Option 2: HTTPS עם Personal Access Token (מומלץ)
```bash
# צור Personal Access Token ב-Bitbucket:
# Settings → Personal Access Tokens → Create Token

git pull https://<username>:<token>@bitbucket.org/prisma-photonics/pz.git
```

#### Option 3: SSH Key (הכי מאובטח)
```bash
# 1. צור SSH key (אם אין)
ssh-keygen -t ed25519 -C "prisma@worker-node"

# 2. הצג את ה-public key
cat ~/.ssh/id_ed25519.pub

# 3. העתק את המפתח ל-Bitbucket:
#    Bitbucket → Settings → SSH Keys → Add Key

# 4. בדוק חיבור
ssh -T git@bitbucket.org

# 5. שנה את ה-remote ל-SSH
git remote set-url origin git@bitbucket.org:prisma-photonics/pz.git

# 6. Pull
git pull origin master
```

---

## 🔍 בדיקות אחרי העדכון

```bash
# 1. בדוק שהקוד עודכן
cd /home/prisma/pz
git log -3
git diff HEAD~1

# 2. בדוק שהקבצים נכונים
ls -la
ls -la config/py/

# 3. בדוק ש-Python syntax תקין
python3 -m py_compile config/py/default_config.py

# 4. אם יש requirements - התקן מחדש
pip3 install -r requirements.txt

# 5. בדוק שהפוד רץ עם הקוד החדש
kubectl get pods -n panda | grep focus-server
kubectl logs -n panda $(kubectl get pods -n panda -l app.kubernetes.io/name=panda-panda-focus-server -o name) --tail=50
```

---

## 📋 Checklist לעדכון

- [ ] התחבר ל-Worker Node (`ssh root@10.10.100.3` → `ssh prisma@10.10.100.113`)
- [ ] נווט לתיקיית הקוד (`cd /home/prisma/pz`)
- [ ] בדוק סטטוס (`git status`)
- [ ] שמור שינויים מקומיים אם יש (`git stash`)
- [ ] עדכן את הקוד (`git pull origin master`)
- [ ] בדוק שהעדכון הצליח (`git log`)
- [ ] אם צריך - עדכן את הפוד (`kubectl delete pod ...`)
- [ ] בדוק שהפוד עלה בהצלחה (`kubectl get pods -n panda`)
- [ ] בדוק לוגים שאין errors (`kubectl logs ...`)

---

## 🆘 Troubleshooting

### בעיה: "Permission denied" בעת pull
```bash
# פתרון: בדוק הרשאות
ls -la /home/prisma/pz/.git
sudo chown -R prisma:prisma /home/prisma/pz
```

### בעיה: "Your local changes would be overwritten"
```bash
# פתרון 1: שמור שינויים
git stash save "backup before pull"
git pull
git stash pop

# פתרון 2: בטל שינויים מקומיים
git reset --hard HEAD
git pull
```

### בעיה: "Authentication failed"
```bash
# פתרון: השתמש ב-Personal Access Token
git remote set-url origin https://<username>:<token>@bitbucket.org/prisma-photonics/pz.git
git pull
```

### בעיה: "No remote repository specified"
```bash
# פתרון: הוסף remote
git remote add origin <BITBUCKET_REPO_URL>
git pull origin master
```

---

## 📝 פקודות מהירות (Copy-Paste Ready)

### עדכון מהיר (אם הכל מוגדר):
```bash
# התחבר
ssh root@10.10.100.3
ssh prisma@10.10.100.113

# עדכן
cd /home/prisma/pz
git stash
git pull origin master
git stash pop

# בדוק
git log -3
```

### אם צריך לעדכן גם את הפוד:
```bash
# עדכן קוד
cd /home/prisma/pz
git pull origin master

# אתחל פוד
kubectl delete pod -n panda $(kubectl get pods -n panda -l app.kubernetes.io/name=panda-panda-focus-server -o name | head -1)

# בדוק שעלה
kubectl get pods -n panda -w
```

---

## 🔗 מידע נוסף

### Bitbucket Repository
אם אתה לא בטוח מה ה-URL של ה-repo:
```bash
cd /home/prisma/pz
git remote -v
```

זה יציג משהו כמו:
```
origin  https://bitbucket.org/prisma-photonics/pz.git (fetch)
origin  https://bitbucket.org/prisma-photonics/pz.git (push)
```

### Branches זמינים
```bash
# רשימת branches מקומיים
git branch

# רשימת branches מרוחקים
git branch -r

# רשימת כל ה-branches
git branch -a
```

### היסטוריה ושינויים
```bash
# 10 commits אחרונים
git log -10 --oneline

# שינויים בcommit האחרון
git show HEAD

# השוואה בין גרסאות
git diff HEAD~5..HEAD
```

---

**נוצר**: 2025-10-19  
**עודכן אחרון**: 2025-10-19  
**גרסה**: 1.0

