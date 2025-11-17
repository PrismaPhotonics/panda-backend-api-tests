# 🔗 Local Code Links Guide
## How to Use the Presentation with Local Links

---

## ✅ **What Changed?**

Your PowerPoint presentation now contains **local file links** that open code directly in Cursor IDE!

### **Before (Web Links):**
```
https://github.com/org/repo/blob/main/src/utils/validators.py#L390
```
❌ Requires internet, repo access, manual copy-paste

### **After (Local Links):**
```
vscode://file/C:/Projects/focus_server_automation/src/utils/validators.py:390
```
✅ Opens instantly in Cursor at exact line!

---

## 🎯 **How to Use**

### **Step 1: Open the Presentation**
```
documentation\analysis\Automation_Specs_Gap_Review_LOCAL_LINKS.pptx
```

### **Step 2: Click Any "[view code →]" Link**

The link will:
1. Launch Cursor IDE (if not already open)
2. Open the exact file
3. Jump to the exact line number
4. Ready to review or edit!

---

## 📝 **Example Links in Presentation**

| Link Text | Opens |
|-----------|-------|
| [P0] #1: ROI change limit - hardcoded 50% | `validators.py:395` |
| [P0] #2: Performance assertions disabled | `test_performance_high_priority.py:146` |
| [P1] #3: NFFT validation too permissive | `validators.py:194` |
| [P1] #4: Frequency range - no absolute max/min | `focus_server_models.py:46` |
| [P2] #5: Sensor range - no min/max ROI size | `validators.py:116` |
| [P2] #6: Polling helper - hardcoded timeouts | `helpers.py:474` |
| [P2] #7: Default payloads mismatch config | `helpers.py:507` |
| [P3] Config validation tests with TODO | `test_config_validation_high_priority.py:475` |
| [P3] MongoDB outage resilience | `test_mongodb_outage_resilience.py` |

---

## 🔧 **Configuration**

The script is configured for your local setup:

### **Your Settings:**
```python
LINK_MODE = "local"  # ✅ Using local file links
LOCAL_PROJECT_PATH = r"C:\Projects\focus_server_automation"
```

### **To Switch Back to Web Links:**
Edit `scripts/generate_presentation_with_links.py`:
```python
LINK_MODE = "web"  # Change to web
REPO_BASE_URL = "https://github.com/your-org/focus_server_automation/blob/main/"
```

Then run:
```powershell
.\.venv\Scripts\python.exe scripts/generate_presentation_with_links.py
```

---

## 🎤 **Using in Presentations**

### **During Your Meeting:**

1. **Open PowerPoint in Slideshow Mode** (F5)
2. **Navigate to Slide 1** (Direct Dev Code Links)
3. **Click any "[view code →]" link**
4. **Cursor will open automatically** with the code

### **Pro Tips:**

✅ **Arrange Windows:**
- PowerPoint on left monitor
- Cursor on right monitor
- Click link → code appears instantly

✅ **Practice Navigation:**
- Test all links before the meeting
- Know which code sections to highlight
- Prepare talking points for each example

✅ **Backup Plan:**
- Keep `CODE_LOCATIONS_FOR_PRESENTATION.md` open
- If link fails, use Ctrl+P in Cursor
- Paste file path manually

---

## 🐛 **Troubleshooting**

### **Links Don't Open Cursor:**

**Problem:** Click does nothing or opens wrong app

**Solution 1:** Check default handler
```powershell
# Windows: vscode:// should open Cursor
# If not, reinstall Cursor or configure protocol handler
```

**Solution 2:** Manual open
- Copy file path from link tooltip
- Ctrl+P in Cursor
- Paste and press Enter

### **Opens VSCode Instead of Cursor:**

**Problem:** Links open VS Code, not Cursor

**Fix:** Update Windows protocol handler
```powershell
# Option 1: Reinstall Cursor as default
# Option 2: Change LINK_MODE to use absolute paths
```

### **Wrong Line Number:**

**Problem:** Opens file but wrong line

**Fix:** Code may have changed since presentation was created
- Regenerate presentation:
  ```powershell
  .\.venv\Scripts\python.exe scripts/generate_presentation_with_links.py
  ```

---

## 📊 **What's Included**

### **1. PowerPoint Presentation**
```
Automation_Specs_Gap_Review_LOCAL_LINKS.pptx
```
- **Slide 1:** Direct links to 9 code examples
- **Slide 2:** Summary of affected tests
- **All links:** Open locally in Cursor

### **2. CSV Report**
```
tests_without_specs_LOCAL_LINKS.csv
```
- 16 rows of detailed test information
- Can import to Excel/Google Sheets
- Columns: Test Name, Path, What It Checks, Missing Spec, Impact, Linked Code

---

## 🚀 **Ready to Present!**

Your presentation is configured for:
- ✅ Instant local file access
- ✅ No internet required
- ✅ Opens directly in Cursor IDE
- ✅ Jumps to exact line numbers

**Test it now:**
1. Open the PowerPoint
2. Click "[view code →]" on slide 1
3. Verify Cursor opens correctly

**Good luck with your presentation!** 🎯

---

## 📞 **Need Changes?**

### **Different Project Path?**
Edit line 32 in `scripts/generate_presentation_with_links.py`:
```python
LOCAL_PROJECT_PATH = r"C:\Your\New\Path\Here"
```

### **Want GitHub Links Instead?**
Edit line 29:
```python
LINK_MODE = "web"  # Change from "local" to "web"
```

### **Different File Name?**
Edit lines 42-43:
```python
DECK_PATH = OUTPUT_DIR / "YourFileName.pptx"
CSV_PATH = OUTPUT_DIR / "YourCSVName.csv"
```

Then regenerate:
```powershell
.\.venv\Scripts\python.exe scripts/generate_presentation_with_links.py
```

---

**Created:** 2025-10-22  
**Mode:** Local Links (Cursor IDE)  
**Path:** `C:\Projects\focus_server_automation`

