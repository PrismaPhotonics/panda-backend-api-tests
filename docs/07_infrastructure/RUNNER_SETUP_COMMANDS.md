# פקודות להגדרת Runner על Slave Laptop
# Runner Setup Commands for Slave Laptop

**תאריך:** 2025-01-XX  
**Token:** `BXBPK45XRW4YHLQ7DEJI6Y3JEWENK` (תקף ל-1 שעה)

---

## 🚀 אפשרות 1: שימוש בסקריפט Python (מומלץ)

### עם Password:
```powershell
py scripts\setup_runner_on_slave_laptop.py `
    --user YOUR_USERNAME `
    --password YOUR_PASSWORD `
    --token BXBPK45XRW4YHLQ7DEJI6Y3JEWENK
```

### עם SSH Key:
```powershell
py scripts\setup_runner_on_slave_laptop.py `
    --user YOUR_USERNAME `
    --key ~/.ssh/id_rsa `
    --token BXBPK45XRW4YHLQ7DEJI6Y3JEWENK
```

### אינטראקטיבי:
```powershell
py scripts\setup_runner_on_slave_laptop.py --token BXBPK45XRW4YHLQ7DEJI6Y3JEWENK
```

---

## 🖥️ אפשרות 2: הרצה ידנית על ה-Slave Laptop

אם אתה יכול להתחבר ישירות ל-slave laptop (10.50.0.36):

### שלב 1: התחבר ל-Slave Laptop
```powershell
ssh YOUR_USERNAME@10.50.0.36
```

### שלב 2: הורד והתקן Runner
```powershell
# צור תיקייה
mkdir actions-runner
cd actions-runner

# הורד את ה-runner
Invoke-WebRequest -Uri https://github.com/actions/runner/releases/download/v2.329.0/actions-runner-win-x64-2.329.0.zip -OutFile actions-runner-win-x64-2.329.0.zip

# חלץ
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::ExtractToDirectory("$PWD/actions-runner-win-x64-2.329.0.zip", "$PWD")

# הגדר את ה-runner
.\config.cmd --url https://github.com/PrismaPhotonics/panda-backend-api-tests --token BXBPK45XRW4YHLQ7DEJI6Y3JEWENK --name slave-laptop-runner --labels "self-hosted,Windows,slave-laptop" --work "_work" --replace

# התקן כשירות
.\svc.cmd install
.\svc.cmd start

# בדוק סטטוס
.\svc.cmd status
```

---

## 🔧 אפשרות 3: הרצה דרך SSH (מהמחשב שלך)

אם אתה רוצה להריץ את הפקודות מהמחשב שלך דרך SSH:

```powershell
# התחבר והרץ פקודות
ssh YOUR_USERNAME@10.50.0.36 "mkdir -p C:\actions-runner; cd C:\actions-runner; Invoke-WebRequest -Uri https://github.com/actions/runner/releases/download/v2.329.0/actions-runner-win-x64-2.329.0.zip -OutFile actions-runner.zip; Expand-Archive -Path actions-runner.zip -DestinationPath . -Force; Remove-Item actions-runner.zip"
```

אבל זה מסובך יותר - עדיף להשתמש בסקריפט Python.

---

## ✅ וידוא שה-Runner פעיל

לאחר ההתקנה, בדוק:

1. **ב-GitHub:**
   ```
   https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
   ```
   אתה אמור לראות את ה-runner עם סטטוס **"Online"** (ירוק)

2. **על המכונה:**
   ```powershell
   ssh YOUR_USERNAME@10.50.0.36
   cd C:\actions-runner
   .\svc.cmd status
   ```

---

## 📝 הערות

- **Token תקף ל-1 שעה** - אם עבר זמן, קבל token חדש מ-GitHub
- **Runner Name:** `slave-laptop-runner` (ניתן לשנות)
- **Installation Path:** `C:\actions-runner` (מומלץ על ידי GitHub)
- **Labels:** `self-hosted,Windows,slave-laptop` (לשימוש ב-workflows)

---

## 🎯 שימוש ב-Runner ב-Workflows

לאחר שה-runner פעיל, השתמש בו כך:

```yaml
jobs:
  test:
    runs-on: self-hosted  # או [self-hosted, slave-laptop]
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: pytest
```

