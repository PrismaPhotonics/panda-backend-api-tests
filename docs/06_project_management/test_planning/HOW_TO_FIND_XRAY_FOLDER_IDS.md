# איך למצוא Xray Folder IDs

**תאריך:** 2025-11-16

---

## שיטה 1: דרך Xray Test Repository UI

1. **פתח את Xray Test Repository:**
   ```
   https://prismaphotonics.atlassian.net/projects/PZ?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.xpandit.plugins.xray__testing-board#!page=test-repository&selectedFolder=68d91b9f681e183ea2e83e16
   ```

2. **פתח את DevTools (F12)**

3. **עבור לטאב Network**

4. **לחץ על כל תיקייה** (Positive Tests, Negative Tests, וכו')

5. **חפש בקשות API** שמכילות:
   - `testrepository`
   - `folder`
   - `folders`

6. **מצא את ה-Folder ID** באחת מהדרכים הבאות:
   - ב-URL של הבקשה: `.../folders/{FOLDER_ID}/...`
   - בתגובת ה-API: `{"id": "FOLDER_ID", ...}`
   - ב-Response body: `"folderId": "FOLDER_ID"`

---

## שיטה 2: דרך URL של התיקייה

כשאתה בתיקייה ב-Xray Test Repository, ה-URL מכיל את ה-folder ID:

```
https://prismaphotonics.atlassian.net/projects/PZ?selectedItem=...&selectedFolder={FOLDER_ID}
```

**דוגמה:**
- Base folder: `68d91b9f681e183ea2e83e16`
- Positive Tests: `{FOLDER_ID_FROM_URL}`
- Negative Tests: `{FOLDER_ID_FROM_URL}`
- וכו'...

---

## שיטה 3: דרך Jira API (אם זמין)

נסה את ה-endpoints הבאים:

```bash
# Endpoint 1
GET https://prismaphotonics.atlassian.net/rest/raven/1.0/api/testrepository/PZ/folders

# Endpoint 2
GET https://prismaphotonics.atlassian.net/rest/raven/2.0/api/testrepository/PZ/folders

# Endpoint 3
GET https://prismaphotonics.atlassian.net/rest/api/2/project/PZ/testrepository/folders
```

**Authentication:**
```bash
curl -u "roy.avrahami@prismaphotonics.com:YOUR_API_TOKEN" \
  "https://prismaphotonics.atlassian.net/rest/raven/1.0/api/testrepository/PZ/folders"
```

---

## רשימת תיקיות נדרשות

צריך למצוא את ה-Folder IDs של:

1. **Positive Tests** (5 טסטים)
2. **Negative Tests** (7 טסטים)
3. **Edge Cases** (8 טסטים)
4. **Load Tests** (5 טסטים)
5. **Performance Tests** (6 טסטים)
6. **Investigation** (1 טסט)

---

## אחרי שמצאת את ה-Folder IDs

הרץ את הסקריפט עם ה-IDs:

```bash
python scripts/jira/assign_alerts_tests_to_xray_folders.py \
  --folder-ids <positive_id>,<negative_id>,<edge_case_id>,<load_id>,<performance_id>,<investigation_id>
```

**דוגמה:**
```bash
python scripts/jira/assign_alerts_tests_to_xray_folders.py \
  --folder-ids abc123,def456,ghi789,jkl012,mno345,pqr678
```

---

## הערות

- אם תיקייה לא קיימת, צור אותה ידנית ב-Xray Test Repository
- ה-Folder IDs הם בדרך כלל מחרוזות hex (למשל: `68d91b9f681e183ea2e83e16`)
- אם לא מצאת דרך API, השתמש בשיטה 1 (DevTools)

