# הוראות הגדרת Runner - פתרון שגיאת 404

## בעיה: Token פג תוקף

אם אתה מקבל שגיאה 404, זה אומר שה-token פג תוקף.

## פתרון:

### שלב 1: קבל Token חדש

1. לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners/new?arch=x64&os=win
2. העתק את הפקודה החדשה עם ה-token החדש

### שלב 2: הרץ את הפקודה החדשה

```powershell
cd C:\actions-runner
.\config.cmd --url https://github.com/PrismaPhotonics/panda-backend-api-tests --token <TOKEN_HADASH>
```

### שלב 3: במהלך ההגדרה

כשתשאל אותך:

1. **Enter the name of the runner:**
   ```
   panda-backend-lab
   ```

2. **This will run as a service with SYSTEM account:**
   ```
   Y
   ```

3. **Enter runner group:**
   ```
   [לחץ Enter]
   ```

4. **Enter labels (comma-separated):**
   ```
   self-hosted,Windows,panda-backend-lab
   ```

5. **Enter work folder:**
   ```
   [לחץ Enter]
   ```

### שלב 4: התקן כשירות

```powershell
.\svc\install.cmd
.\svc\start.cmd
```

### שלב 5: וודא שהכל עובד

```powershell
# בדוק שהשירות רץ
Get-Service actions.runner.*

# בדוק ב-GitHub
# לך ל: https://github.com/PrismaPhotonics/panda-backend-api-tests/settings/actions/runners
# תראה את ה-runner עם status: Online
```

