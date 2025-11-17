# How to Find Xray Folder ID
=============================

**Purpose:** Find the Xray folder ID needed to assign tests programmatically.

---

## Method 1: Browser DevTools (Recommended)

1. **Open Xray Test Repository:**
   ```
   https://prismaphotonics.atlassian.net/projects/PZ?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.xpandit.plugins.xray__testing-board#!page=test-repository
   ```

2. **Open Browser DevTools:**
   - Press `F12` or `Ctrl+Shift+I` (Windows/Linux)
   - Or `Cmd+Option+I` (Mac)

3. **Go to Network Tab:**
   - Click on "Network" tab in DevTools

4. **Navigate to Target Folder:**
   - Expand: `Panda MS3` → `BE Tests` → `Focus Server Tests`
   - Click on: `API Tests` folder

5. **Find Folder ID:**
   - Look for network requests containing "folder" or "testrepository"
   - Check the response JSON - look for `id` or `folderId` field
   - Or check the request URL - folder ID might be in the path

---

## Method 2: Check URL Parameters

1. **Navigate to folder in Xray Test Repository**

2. **Check browser URL:**
   - Look for parameters like `selectedFolder=XXXXX`
   - The folder ID might be in the URL hash or query parameters

---

## Method 3: Use Browser Console

1. **Open Xray Test Repository**

2. **Open Browser Console:**
   - Press `F12` → Go to "Console" tab

3. **Run JavaScript:**
   ```javascript
   // Try to find folder ID in page data
   // This depends on Xray implementation
   ```

---

## Method 4: Manual Assignment (If API Doesn't Work)

If you can't find the folder ID, use manual assignment:

1. **Open Xray Test Repository**

2. **Use JQL Query:**
   ```jql
   issue in (PZ-14750, PZ-14751, PZ-14752, PZ-14753, PZ-14754, PZ-14755, PZ-14756, PZ-14757, PZ-14758, PZ-14759, PZ-14760, PZ-14761, PZ-14762, PZ-14763, PZ-14764) AND type = Test
   ```

3. **Select all tests**

4. **Drag and drop to folder:**
   - Drag selected tests to `API Tests` folder

---

## Once You Have Folder ID

Run the script with folder ID:

```bash
python scripts/jira/assign_api_tests_to_xray_folder.py --folder-id <FOLDER_ID>
```

Or test first with dry-run:

```bash
python scripts/jira/assign_api_tests_to_xray_folder.py --folder-id <FOLDER_ID> --dry-run
```

