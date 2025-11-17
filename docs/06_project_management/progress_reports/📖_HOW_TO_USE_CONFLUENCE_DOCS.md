# 📖 How to Use Confluence Documents

## 📂 Files Created

### 1. `CONFLUENCE_SPECS_MEETING.md`
**Format:** Markdown (readable in any editor)  
**Use:** Preview, share as PDF, or convert to Confluence  
**Best for:** Email, Slack, GitHub/Bitbucket

### 2. `CONFLUENCE_SPECS_MEETING_WITH_MACROS.confluence`
**Format:** Confluence Wiki Markup  
**Use:** Copy-paste directly into Confluence  
**Best for:** Official Confluence page

---

## 🚀 How to Upload to Confluence

### Option 1: Copy-Paste Wiki Markup (Recommended)

1. **Create new Confluence page**
   - Go to your Confluence space
   - Click "Create" → "Blank page"

2. **Switch to Wiki Markup**
   - Click the "..." menu (top right)
   - Select "Insert" → "Markup"
   - Choose "Confluence Wiki"

3. **Copy-paste the content**
   - Open `CONFLUENCE_SPECS_MEETING_WITH_MACROS.confluence`
   - Copy ALL content (Ctrl+A, Ctrl+C)
   - Paste into Confluence markup editor
   - Click "Insert"

4. **Publish**
   - The macros will render automatically
   - All colors, panels, and formatting will work

---

### Option 2: Convert Markdown to Confluence

1. **Open** `CONFLUENCE_SPECS_MEETING.md`

2. **Use online converter:**
   - Go to: https://markdown-to-confluence.com/
   - Or use: https://eucalyptus.atlassian.net/wiki/markdown-converter
   - Paste the markdown
   - Copy the Confluence output

3. **Paste** into Confluence editor

---

### Option 3: Import as Markdown (if supported)

Some Confluence versions support markdown import:
1. Create new page
2. Click "..." → "Import"
3. Select `CONFLUENCE_SPECS_MEETING.md`
4. Adjust formatting as needed

---

## 🎨 What You'll Get in Confluence

### Visual Elements:

**Info Panel (blue):**
```
{info:title=Goal}
Content here
{info}
```

**Warning Panel (yellow):**
```
{warning}
Critical issues
{warning}
```

**Tip Panel (green):**
```
{tip:title=Expected Outcome}
Success criteria
{tip}
```

**Status Tags:**
- {status:colour=Red|title=URGENT}
- {status:colour=Green|title=Ready}
- {status:colour=Yellow|title=High}

**Code Blocks:**
```python
def example():
    pass
```

**Tables with Headers:**
| Column 1 | Column 2 |
|----------|----------|
| Data     | Data     |

---

## ✅ Quick Start

### For Meeting Prep:

1. **Upload to Confluence** (use Option 1 above)
2. **Share link** with meeting attendees
3. **Ask them to review** Issues #1-3 before meeting
4. **Print** the summary table for reference

### During Meeting:

1. **Screen share** the Confluence page
2. **Go through** each issue systematically
3. **Take notes** directly in the page (edit mode)
4. **Update tables** with decided values in real-time
5. **Assign action items** at the bottom

### After Meeting:

1. **Update** the page with final decisions
2. **Create child pages** for each issue if needed
3. **Link** to related Jira tickets
4. **Archive** this page once specs are implemented

---

## 📊 Content Overview

### What's in the Document:

| Section | Purpose | Time |
|---------|---------|------|
| Meeting Objective | Set expectations | 5 min |
| The Problem | Show impact | 5 min |
| Issue #1-3 (Critical) | Get decisions | 60 min |
| Issue #4-7 (High/Med) | Get decisions | 45 min |
| Implementation Plan | Next steps | 20 min |

### Total: ~2.5 hours

---

## 🔗 Supporting Files to Attach

Attach these to the Confluence page:

1. **specs_checklist_for_meeting.csv**
   - Location: `documentation/specs/specs_checklist_for_meeting.csv`
   - 135 detailed questions

2. **CODE_EVIDENCE_MISSING_SPECS.md**
   - Location: `documentation/specs/CODE_EVIDENCE_MISSING_SPECS.md`
   - Full code examples

3. **PowerPoint Presentation** (optional)
   - Location: `documentation/analysis/Automation_Specs_Gap_Review_FULL_WITH_LINKS.pptx`
   - For visual presentation

---

## 💡 Pro Tips

### Before Publishing:

- [ ] Review all code file paths are correct
- [ ] Check that line numbers match your actual code
- [ ] Update the "Date: TBD" with actual meeting date
- [ ] Add your team's contact information
- [ ] Link to related Jira epics/tickets

### For Better Engagement:

- [ ] Add real screenshots of the code issues
- [ ] Link each code file path to your repo (GitHub/Bitbucket)
- [ ] Create a Jira epic and link it
- [ ] Set up a follow-up meeting before this meeting ends

### To Make it Official:

- [ ] Add meeting attendees with @mentions
- [ ] Set page permissions (who can view/edit)
- [ ] Add labels: `specs`, `testing`, `urgent`, `automation`
- [ ] Add to your team's space table of contents

---

## 🎯 After Meeting: Decision Template

Add this section to the Confluence page after the meeting:

```confluence
h2. ✅ Decisions Made

h3. Issue #1: Performance SLAs

{panel:title=Agreed Values|bgColor=#d4edda}
* POST /config P95: *300ms*
* POST /config P99: *800ms*
* Error rate threshold: *3%*
* Implementation: *Week of Oct 28*
* Owner: *@john.doe*
{panel}

h3. Issue #2: ROI Change Limit

{panel:title=Agreed Values|bgColor=#d4edda}
* Maximum change: *40%* (changed from 50%)
* Cooldown period: *5 seconds*
* Implementation: *Week of Oct 28*
* Owner: *@jane.smith*
{panel}

[Continue for all issues...]
```

---

## 📞 Need Help?

### Common Issues:

**Q: Macros don't render?**  
A: Make sure you're in "Wiki Markup" mode, not rich text editor

**Q: Tables look broken?**  
A: Check that table rows start with `|` and end with `|`

**Q: Code blocks aren't formatted?**  
A: Use `{code:python}` ... `{code}` syntax

**Q: Status badges don't show?**  
A: Use exact syntax: `{status:colour=Red|title=Text}`

---

## ✨ Example Confluence Page URL

After uploading, your page will look like:
```
https://your-company.atlassian.net/wiki/spaces/QA/pages/123456/Specs+Meeting+Missing+Test+Specifications
```

Share this URL with your team!

---

**Created:** October 22, 2025  
**Files:** 2 documents ready to use  
**Status:** ✅ Ready to publish

