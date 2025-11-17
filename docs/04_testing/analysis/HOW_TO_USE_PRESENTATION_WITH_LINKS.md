# 📊 How to Use: Presentation with Code Links
## Complete Guide for Specs Gap Review Presentation

**Date:** October 22, 2025  
**Files Generated:**
- `Automation_Specs_Gap_Review_EN_2025-10-22.pptx`
- `tests_without_specs_EN_2025-10-22.csv`

---

## 🎯 What Was Created

### 1. PowerPoint Presentation
**File:** `Automation_Specs_Gap_Review_EN_2025-10-22.pptx`

**Contents:**
- **Slide 1:** Direct Dev Code Links (9 clickable links to code)
- **Slide 2:** QA Tests Without Specs Summary (10 tests listed)

### 2. Detailed CSV
**File:** `tests_without_specs_EN_2025-10-22.csv`

**Contents:**
- 16 rows (10 tests + 6 code functions)
- 6 columns: Test Name, Path, What It Checks, Missing Spec, Impact, Linked Code

---

## 📋 Step-by-Step Usage

### Step 1: Update Code Repository Links

**Edit:** `scripts/generate_presentation_with_links.py`

**Line 21:**
```python
# Current:
REPO_BASE_URL = "https://github.com/your-org/focus_server_automation/blob/main/"

# Change to YOUR repository:
# For GitHub:
REPO_BASE_URL = "https://github.com/your-company/focus-server/blob/main/"

# For Bitbucket Server:
REPO_BASE_URL = "https://bitbucket.company.com/projects/PZ/repos/focus-server/browse/"

# For Bitbucket Cloud:
REPO_BASE_URL = "https://bitbucket.org/your-workspace/focus-server/src/main/"

# For GitLab:
REPO_BASE_URL = "https://gitlab.com/your-group/focus-server/-/blob/main/"
```

### Step 2: Re-generate with Correct URLs

```bash
# From project root:
.\.venv\Scripts\python.exe scripts/generate_presentation_with_links.py
```

**Output:**
```
======================================================================
Generating Automation Specs Gap Review Materials
======================================================================

[OK] PowerPoint presentation created: documentation\analysis\Automation_Specs_Gap_Review_EN_2025-10-22.pptx
[OK] CSV file created: documentation\analysis\tests_without_specs_EN_2025-10-22.csv
     Rows: 16 tests/functions

======================================================================
Generation Complete!
======================================================================
```

### Step 3: Test the Links

1. Open `Automation_Specs_Gap_Review_EN_2025-10-22.pptx`
2. Go to Slide 1: "Direct Dev Code Links (Evidence)"
3. Click on "[view code →]" next to each issue
4. Verify it opens the correct file in your browser

**If links don't work:**
- Check that REPO_BASE_URL is correct
- Verify file paths match your repository structure
- Ensure line numbers haven't changed

---

## 🎨 Customizing the Presentation

### Adding More Slides

**Edit:** `scripts/generate_presentation_with_links.py`

**After line 143, add:**
```python
# ========================================================================
# Slide 3: Your Custom Slide
# ========================================================================
slide3 = prs.slides.add_slide(prs.slide_layouts[1])  # Title and content
title3 = slide3.shapes.title
title3.text = "Your Custom Title"
title3.text_frame.paragraphs[0].font.name = "Arial"

tf3 = slide3.placeholders[1].text_frame
tf3.clear()

custom_content = [
    "Point 1",
    "Point 2",
    "Point 3",
]

for i, line in enumerate(custom_content):
    p = tf3.paragraphs[0] if i == 0 else tf3.add_paragraph()
    p.text = line
    p.font.name = "Arial"
    p.font.size = Pt(20)
```

### Changing Colors

**Priority Colors (Slide 2):**
```python
# Line 137-142: Current colors
if "P95/P99" in line or "SLA" in line:
    p.font.color.rgb = RGBColor(220, 53, 69)  # Red
elif "outage" in line or "limit" in line:
    p.font.color.rgb = RGBColor(253, 126, 20)  # Orange
else:
    p.font.color.rgb = RGBColor(255, 193, 7)  # Yellow
```

**To change colors:**
```python
# Use RGB values (0-255)
p.font.color.rgb = RGBColor(R, G, B)

# Examples:
# Red:    RGBColor(220, 53, 69)
# Orange: RGBColor(253, 126, 20)
# Yellow: RGBColor(255, 193, 7)
# Green:  RGBColor(40, 167, 69)
# Blue:   RGBColor(0, 102, 204)
```

---

## 📊 Using the CSV File

### Option 1: Excel

1. Open Excel
2. File → Open → Select `tests_without_specs_EN_2025-10-22.csv`
3. Data → Text to Columns (if needed)
4. Use as a checklist during specs meeting

### Option 2: Google Sheets

1. Go to Google Sheets
2. File → Import → Upload → Select CSV
3. Share with team
4. Add columns: "Status", "Decision", "Owner"

### Option 3: Jira Import

1. Copy CSV content
2. Create Jira Epic: "Define Missing Specs"
3. Create subtasks from CSV rows
4. Assign to team members

**Suggested Jira Fields:**
```
Summary: [Row: Test Name]
Description: [Row: What It Checks + Missing Spec]
Priority: Based on Impact
Labels: missing-spec, automation-blocked
Epic Link: Define Missing Specs
```

---

## 🎤 Presenting the Material

### Opening (2 min)

**Show Slide 1:**
```
"Here's the evidence - 9 locations in our production code where specs are missing.
Each link goes directly to the code. Let's review them together."
```

**Click first link:**
```
"See line 395? This 50% value - nobody has confirmed if it's correct.
It could be 30%, could be 70%. We just don't know."
```

### Middle (15 min)

**Walk through each priority:**

**[P0] Issues (Red):**
- "These are blocking 34 tests"
- "Performance can't be validated without thresholds"

**[P1] Issues (Orange):**
- "These allow invalid configurations"
- "NFFT accepts any value, ignoring config"

**[P2-P3] Issues (Yellow):**
- "Lower priority but still affecting automation quality"

### Closing (3 min)

**Show Slide 2:**
```
"Here are 10 specific tests that can't enforce quality without specs.
They run, collect data, but can't fail on bad behavior."
```

**Transition to CSV:**
```
"I've prepared a detailed CSV with all 16 items.
Let's schedule a 2-hour meeting to go through them."
```

---

## 🔧 Troubleshooting

### Issue: Links Don't Work

**Cause:** REPO_BASE_URL incorrect

**Fix:**
1. Check your repository URL format
2. Test manually: `{REPO_BASE_URL}src/utils/validators.py`
3. Should open the file in browser

**Common formats:**
```
GitHub:    https://github.com/org/repo/blob/main/
Bitbucket: https://bitbucket.company.com/projects/X/repos/Y/browse/
GitLab:    https://gitlab.com/group/project/-/blob/main/
```

### Issue: PowerPoint Won't Open

**Cause:** python-pptx compatibility

**Fix:**
```bash
# Reinstall:
.\.venv\Scripts\python.exe -m pip uninstall python-pptx
.\.venv\Scripts\python.exe -m pip install python-pptx
```

**Alternative:** Convert to Google Slides:
1. Upload PPTX to Google Drive
2. Right-click → Open with → Google Slides
3. Edit and re-download as PPTX

### Issue: CSV Has Wrong Encoding

**Cause:** Excel encoding issues

**Fix in script (line 294):**
```python
# Current:
with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:

# Try:
with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
```

### Issue: Line Numbers Wrong

**Cause:** Code changed since script was created

**Fix:**
1. Search for the code pattern in your editor
2. Update line numbers in script (lines 58-83)
3. Re-run generator

---

## 📝 Checklist for Meeting

### Before Meeting (48h):

- [ ] Update REPO_BASE_URL with correct repository
- [ ] Re-generate presentation with real links
- [ ] Test all 9 code links - verify they work
- [ ] Share CSV with attendees
- [ ] Book conference room with screen sharing
- [ ] Send calendar invite with attachments

### During Meeting:

- [ ] Share screen
- [ ] Click through code links (Slide 1)
- [ ] Walk through tests summary (Slide 2)
- [ ] Reference CSV for details
- [ ] Document decisions in real-time
- [ ] Assign action items

### After Meeting:

- [ ] Update settings.py with decided values
- [ ] Create tickets for each spec gap
- [ ] Update code with confirmed specs
- [ ] Re-run affected tests
- [ ] Send meeting notes to team

---

## 📚 Reference: All Documents

### For Presentation:
1. ✅ `Automation_Specs_Gap_Review_EN_2025-10-22.pptx` - Generated slides
2. ✅ `tests_without_specs_EN_2025-10-22.csv` - Detailed list
3. ✅ `SLIDES_CONTENT_FOR_PRESENTATION.md` - 20 slide templates

### For Meeting:
4. ✅ `TOP_CODE_LINKS_FOR_SPECS.md` - Quick reference
5. ✅ `CODE_EVIDENCE_MISSING_SPECS.md` - Evidence (English)

### Deep Dive:
6. ✅ `CRITICAL_MISSING_SPECS_LIST.md` - Complete list (653 lines)
7. ✅ `specs_checklist_for_meeting.csv` - Excel format

### Scripts:
8. ✅ `scripts/generate_presentation_with_links.py` - Generator script

---

## 🎯 Quick Commands

### Generate Everything:
```bash
.\.venv\Scripts\python.exe scripts/generate_presentation_with_links.py
```

### View Files:
```bash
# PowerPoint:
start documentation\analysis\Automation_Specs_Gap_Review_EN_2025-10-22.pptx

# CSV in Excel:
start documentation\analysis\tests_without_specs_EN_2025-10-22.csv
```

### Count TODOs in Code:
```bash
grep -r "TODO.*spec" tests/ | wc -l
```

### Find Disabled Assertions:
```bash
grep -r "# assert" tests/ | grep -i "todo"
```

---

## ✅ Success Criteria

**Presentation is ready when:**
- [ ] All 9 code links work
- [ ] Slides render correctly
- [ ] CSV opens in Excel/Sheets
- [ ] Line numbers match actual code
- [ ] Colors display correctly

**Meeting was successful when:**
- [ ] All critical specs have decisions
- [ ] Action items assigned
- [ ] Timeline agreed
- [ ] Follow-up scheduled

**Implementation is complete when:**
- [ ] All hardcoded values moved to settings
- [ ] All assertions enabled
- [ ] All TODO comments removed
- [ ] All tests pass/fail correctly

---

**Ready to present!** 🎯

