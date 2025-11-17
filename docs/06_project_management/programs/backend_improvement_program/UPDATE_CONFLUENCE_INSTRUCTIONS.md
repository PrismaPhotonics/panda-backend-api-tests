# Instructions for Updating Confluence Page

## Overview

The strategic document `BACKEND_REFACTOR_QA_AUTOMATION_STRATEGY.md` has been updated and converted to Confluence Wiki Markup format.

## Files Created

1. **BACKEND_REFACTOR_QA_AUTOMATION_STRATEGY.confluence**
   - Confluence Wiki Markup format
   - Ready to copy-paste into Confluence
   - Location: `docs/06_project_management/programs/backend_improvement_program/`

2. **Scripts for Automation:**
   - `scripts/confluence/convert_markdown_to_confluence.py` - Convert Markdown to Confluence format
   - `scripts/confluence/update_confluence_page.py` - Update Confluence page via API
   - `scripts/confluence/find_confluence_page.py` - Find page information

## Method 1: Manual Update (Recommended)

### Steps:

1. **Open Confluence Page:**
   - Go to: https://prismaphotonics.atlassian.net/wiki/x/AwBegw
   - Click "Edit" button

2. **Switch to Wiki Markup Mode:**
   - Click "..." menu (top right)
   - Select "Insert" → "Markup"
   - Choose "Confluence Wiki"

3. **Copy Content:**
   - Open file: `BACKEND_REFACTOR_QA_AUTOMATION_STRATEGY.confluence`
   - Copy ALL content (Ctrl+A, Ctrl+C)

4. **Paste and Insert:**
   - Paste into Confluence markup editor
   - Click "Insert"
   - Review the rendered content

5. **Publish:**
   - Click "Publish" button
   - The page will be updated with all changes

## Method 2: API Update (Automated)

### Prerequisites:

1. **Install Required Library:**
   ```bash
   pip install atlassian-python-api
   ```

2. **Get Page Information:**
   - Find the Confluence space key (e.g., "QA", "ENG", "DEV")
   - Find the page title (e.g., "Backend Refactor & Long-Term QA/Automation Strategy Plan")
   - Or get the full page URL with page ID

### Run Update Script:

```bash
# Using space and title
py scripts/confluence/update_confluence_page.py \
  --url "https://prismaphotonics.atlassian.net/wiki/x/AwBegw" \
  --file "docs/06_project_management/programs/backend_improvement_program/BACKEND_REFACTOR_QA_AUTOMATION_STRATEGY.md" \
  --space "SPACE_KEY" \
  --title "Backend Refactor & Long-Term QA/Automation Strategy Plan"

# Or using full URL with page ID
py scripts/confluence/update_confluence_page.py \
  --url "https://prismaphotonics.atlassian.net/wiki/spaces/SPACE/pages/123456/Title" \
  --file "docs/06_project_management/programs/backend_improvement_program/BACKEND_REFACTOR_QA_AUTOMATION_STRATEGY.md"
```

### Find Page Information:

```bash
py scripts/confluence/find_confluence_page.py "https://prismaphotonics.atlassian.net/wiki/x/AwBegw"
```

## What Was Updated

The document now reflects:

- ✅ **Current Status Summary** - 75% completion
- ✅ **Phase A:** 100% COMPLETE (all 3 components)
- ✅ **Phase B:** 95% COMPLETE (Unit, Integration, Data Quality ✅)
- ✅ **Phase C:** 90% COMPLETE (Performance, Security, Resilience ✅)
- ✅ **Phase D:** 66% COMPLETE (Jira/Xray ✅, CI/CD ❌)
- ✅ **Current Statistics:** 42 test files, 101/113 Xray tests (89.4%), 314+ docs
- ✅ **Updated Timeline** with current status
- ✅ **Updated Success Metrics** with current values
- ✅ **Updated Immediate Next Steps**
- ✅ **Removed specific names** from RACI section

## Verification

After updating, verify:

1. ✅ All "To Be Built" statuses are updated to "COMPLETED" or "ONGOING"
2. ✅ Current statistics are displayed correctly
3. ✅ All links to test files and documentation work
4. ✅ Timeline shows correct status
5. ✅ Success Metrics show current values
6. ✅ RACI section has no specific names

## Notes

- The Confluence Wiki Markup format preserves most formatting
- Tables, code blocks, and links should render correctly
- Some complex Markdown features may need manual adjustment
- If formatting issues occur, use the Rich Text Editor to fine-tune

---

**Created:** 2025-11-05  
**Status:** ✅ Ready for Update

