# How to Use MongoDB Bug Tickets

**Created:** October 16, 2025  
**Purpose:** Guide for importing and managing MongoDB bug tickets

---

## 📁 Files Created

| File | Purpose | Who Should Use |
|------|---------|----------------|
| `MONGODB_BUG_TICKETS.md` | **Full detailed tickets** (ready to copy-paste to Jira) | Developers, QA, Management |
| `MONGODB_BUGS_JIRA_IMPORT.csv` | **Quick CSV import** for Jira | Project Managers, Jira Admins |
| `HOW_TO_USE_BUG_TICKETS.md` | **This guide** | Everyone |

---

## 🚀 Quick Start (3 Options)

### Option 1: Manual Copy-Paste (Recommended for Detail)

**Best for:** Full context with all details

**Steps:**
1. Open `MONGODB_BUG_TICKETS.md`
2. Find the bug ticket section (e.g., "Bug Ticket #1")
3. Copy the entire section (from "### Summary" to "### Labels")
4. In Jira:
   - Click "Create Issue"
   - Select Issue Type: "Bug"
   - Paste into Description field
   - Set Priority, Severity, Assignee from ticket
   - Add Labels from ticket
   - Click "Create"

**Time:** ~3 minutes per ticket  
**Pros:** All details preserved, rich formatting  
**Cons:** Manual work

---

### Option 2: CSV Import (Fastest)

**Best for:** Quick bulk import

**Steps:**
1. In Jira, go to: **Issues → Import Issues from CSV**
2. Upload `MONGODB_BUGS_JIRA_IMPORT.csv`
3. Map CSV columns to Jira fields:
   - Summary → Summary
   - Issue Type → Issue Type
   - Priority → Priority
   - Description → Description
   - etc.
4. Click "Import"

**Time:** ~1 minute for all 3 tickets  
**Pros:** Very fast, bulk import  
**Cons:** Less formatting, may need manual cleanup

---

### Option 3: Create Issues via Jira API (Automated)

**Best for:** Integration with CI/CD

**Example Python Script:**
```python
from jira import JIRA

# Connect to Jira
jira = JIRA(
    server="https://your-company.atlassian.net",
    basic_auth=("your-email@company.com", "api-token")
)

# Bug #1: Missing Indexes
issue1 = jira.create_issue(
    project="PROJ",
    summary="Missing Critical Database Indexes (4 indexes)",
    description="See: MONGODB_BUG_TICKETS.md Bug Ticket #1",
    issuetype={"name": "Bug"},
    priority={"name": "Highest"},
    labels=["mongodb", "performance", "critical", "indexes"],
    assignee={"name": "devops-team"}
)

print(f"Created: {issue1.key}")
```

**Time:** Instant (once script is ready)  
**Pros:** Fully automated, repeatable  
**Cons:** Requires API setup

---

## 📋 Detailed Import Instructions

### For Each Bug Ticket:

#### Bug Ticket #1: Missing Critical Indexes

**Jira Fields:**
- **Issue Type:** Bug
- **Priority:** Highest ⏫
- **Severity:** Critical 🔴
- **Summary:** Missing Critical Database Indexes (4 indexes)
- **Component:** MongoDB, Performance
- **Labels:** `mongodb`, `performance`, `critical`, `indexes`, `data-quality`, `quick-win`
- **Assignee:** DevOps / DBA Team
- **Description:** Copy from `MONGODB_BUG_TICKETS.md` lines 7-320
- **Sprint:** Current Sprint (URGENT!)
- **Story Points:** 1 (3 minutes work)

**Attachments to Link:**
- `tests/integration/infrastructure/test_mongodb_data_quality.py`
- `scripts/quick_mongo_explore.py`
- `MONGODB_BUGS_REPORT.md`

---

#### Bug Ticket #2: Low Recognition Rate

**Jira Fields:**
- **Issue Type:** Bug
- **Priority:** High ⬆️
- **Severity:** Medium 🟡
- **Summary:** Low Recording Recognition Rate (61.3% vs >80% expected)
- **Component:** Focus Server, Data Processing
- **Labels:** `mongodb`, `data-quality`, `recordings`, `recognition`, `investigation-required`
- **Assignee:** Backend Development Team
- **Description:** Copy from `MONGODB_BUG_TICKETS.md` lines 326-660
- **Sprint:** Next Sprint
- **Story Points:** 13 (1-2 weeks)

**Sub-tasks to Create:**
1. Investigation (2 days, 5 points)
2. Algorithm Improvement (1 week, 8 points)
3. Testing & Deployment (optional)

---

#### Bug Ticket #3: Deleted Records Missing end_time

**Jira Fields:**
- **Issue Type:** Bug
- **Priority:** Low ⬇️
- **Severity:** Minor 🟢
- **Summary:** Deleted Recordings Missing end_time Field (24 records)
- **Component:** Focus Server, Recording Service
- **Labels:** `mongodb`, `data-quality`, `cleanup`, `minor`, `low-priority`
- **Assignee:** Backend Development Team
- **Description:** Copy from `MONGODB_BUG_TICKETS.md` lines 666-1012
- **Sprint:** Backlog
- **Story Points:** 3 (1 day)

---

## 🎯 Recommended Action Plan

### Week 1 (Current Sprint)
**Focus:** Bug #1 (Quick Win!)

```
Day 1:
├── Morning: Create Jira tickets for all 3 bugs
├── Afternoon: Fix Bug #1 (Missing Indexes) - 3 minutes!
└── Evening: Verify fix, deploy to production

Story Points: 1
Impact: MASSIVE (1000x performance improvement)
```

### Week 2-3 (Next Sprint)
**Focus:** Bug #2 Investigation

```
Week 2:
├── Day 1-2: Investigate unrecognized recordings
├── Day 3-5: Document findings, design solution
└── Sprint Review: Present findings

Week 3:
├── Day 1-5: Implement algorithm improvements
└── Deploy to staging

Story Points: 13
Impact: MEDIUM (38.7% more data accessible)
```

### Week 4+ (Backlog)
**Focus:** Bug #3 (When convenient)

```
Any Day:
├── Update deletion logic (2 hours)
├── Add unit tests (2 hours)
├── Deploy (1 hour)
└── Optional: One-time cleanup of existing 24 records

Story Points: 3
Impact: LOW (data quality improvement)
```

---

## ✅ Checklist for Jira Import

**Before Creating Tickets:**
- [ ] Read all 3 bug tickets in `MONGODB_BUG_TICKETS.md`
- [ ] Confirm issue severity and priority with team
- [ ] Identify correct assignees
- [ ] Check if similar tickets already exist

**While Creating Tickets:**
- [ ] Set correct Issue Type (Bug)
- [ ] Set Priority (Highest/High/Low)
- [ ] Add all relevant Labels
- [ ] Assign to correct team/person
- [ ] Link related files/attachments
- [ ] Add to appropriate Sprint/Backlog

**After Creating Tickets:**
- [ ] Link tickets to each other (Related to)
- [ ] Add tickets to project roadmap
- [ ] Notify assigned teams
- [ ] Schedule Bug #1 fix ASAP (it's 3 minutes!)
- [ ] Schedule Bug #2 investigation for next sprint
- [ ] Add Bug #3 to backlog

---

## 🔗 Ticket Relationships

**In Jira, link them:**

```
Bug #1 (Missing Indexes)
├── Blocks: Bug #2 (Low Recognition Rate)
│   └── Reason: Slow queries may affect recognition performance
└── Status: URGENT - Fix immediately

Bug #2 (Low Recognition Rate)
├── Blocked by: Bug #1 (should fix indexes first)
├── Requires: Investigation sub-task
└── Status: Scheduled for next sprint

Bug #3 (Missing end_time)
├── Related to: Bug #2 (data quality theme)
└── Status: Backlog (low priority)
```

---

## 📊 Sprint Planning

### Story Point Estimates

| Bug | Story Points | Effort | Impact | ROI |
|-----|--------------|--------|--------|-----|
| **#1** | 1 | 3 minutes | 🔴 CRITICAL | 🟢 Excellent |
| **#2** | 13 | 1-2 weeks | 🟡 MEDIUM | 🟡 Good |
| **#3** | 3 | 1 day | 🟢 LOW | 🟢 Good |
| **Total** | 17 | ~2 weeks | Mixed | Good |

### Recommended Sprint Allocation

**Sprint 1 (Current):**
- Bug #1: Missing Indexes (1 point) ← Do this NOW!

**Sprint 2 (Next):**
- Bug #2: Investigation (5 points)
- Bug #2: Implementation (8 points)

**Backlog:**
- Bug #3: Deletion logic (3 points)

---

## 📝 Sample Jira Descriptions

### Bug #1 (Short Version for Jira)

```
**Problem:**
Recording collection missing 4 critical indexes causing 1000x performance degradation.

**Impact:**
- Time range queries: 30-60 seconds (expected: <100ms)
- UUID lookups: 5-10 seconds (expected: <10ms)
- History playback: UNUSABLE

**Missing Indexes:**
1. start_time
2. end_time
3. uuid (UNIQUE)
4. deleted

**Fix:** Create 4 indexes (3 minutes, non-blocking)

**Verification:**
Run: `py -m pytest tests/integration/infrastructure/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_mongodb_indexes_exist_and_optimal -v`

**Full Details:** See MONGODB_BUG_TICKETS.md Bug Ticket #1
```

---

## 🎤 Presenting to Management

**Talking Points:**

**Bug #1 (Emphasize This!):**
> "We found a **critical performance issue** that's making history playback **1000 times slower** than it should be. The good news? **We can fix it in 3 minutes** and users will immediately see massive improvement."

**Bug #2:**
> "We're missing **38% of user recordings** - they're stored but not accessible. We need 1-2 weeks to investigate and fix the recognition algorithm."

**Bug #3:**
> "Minor data quality issue affecting 0.7% of deleted recordings. Low priority, can fix when convenient."

**Ask:**
> "Can we get approval to fix Bug #1 immediately? It's literally a 3-minute fix with huge impact."

---

## 📞 Communication Templates

### For Developers

**Slack Message:**
```
🐛 MongoDB Data Quality - 3 Bugs Found

Priority Issues:
1. 🔴 URGENT: Missing DB indexes (3 min fix, 1000x speedup!)
2. 🟡 Next Sprint: 61.3% recognition rate (need investigation)
3. 🟢 Backlog: 24 records missing end_time

Full details: MONGODB_BUG_TICKETS.md
Quick summary: MONGODB_BUGS_JIRA_IMPORT.csv

@devops Can we fix #1 today? It's literally 3 minutes.
@backend-team FYI on #2 and #3 for next sprint planning.
```

### For Management

**Email Template:**
```
Subject: MongoDB Performance Issue - Quick Win Available

Hi [Manager],

QA automation discovered 3 data quality issues in MongoDB:

1. ⏫ CRITICAL: Missing database indexes
   - Impact: 1000x slower queries, history feature unusable
   - Fix: 3 minutes (!)
   - ROI: Excellent
   - Request: Immediate approval to fix

2. ⬆️ MEDIUM: Low recognition rate (61.3%)
   - Impact: 38.7% of recordings not accessible
   - Fix: 1-2 weeks investigation + implementation
   - Request: Schedule for next sprint

3. ⬇️ LOW: Minor data quality issue
   - Impact: 0.7% of data (deleted recordings)
   - Fix: 1 day
   - Request: Add to backlog

Recommendation: Fix #1 immediately (huge impact, minimal effort).

Full details available in MONGODB_BUG_TICKETS.md.

Best regards,
[Your Name]
```

---

## ✅ Success Criteria

**After Importing to Jira:**

**You should have:**
- [x] 3 Bug tickets created
- [x] All tickets have correct Priority/Severity
- [x] Assignees notified
- [x] Tickets linked to each other
- [x] Bug #1 scheduled for immediate fix
- [x] Bug #2 in next sprint
- [x] Bug #3 in backlog

**Within 1 Day:**
- [x] Bug #1 FIXED and deployed
- [x] Users see 1000x performance improvement
- [x] History playback working smoothly

**Within 2 Weeks:**
- [x] Bug #2 investigation complete
- [x] Bug #2 implementation in progress
- [x] Recognition rate improving

**Within 1 Month:**
- [x] All bugs resolved or in progress
- [x] Automated tests passing
- [x] Users happy with improvements

---

## 📚 Related Documentation

**For Technical Details:**
- `MONGODB_BUG_TICKETS.md` - Full bug tickets (this is the main file!)
- `MONGODB_BUGS_REPORT.md` - Original technical analysis
- `MONGODB_ISSUES_WORKFLOW.md` - How to identify and report issues

**For Testing:**
- `tests/integration/infrastructure/test_mongodb_data_quality.py` - Automated tests
- `scripts/quick_mongo_explore.py` - Quick exploration script
- `scripts/check_live_vs_historical.py` - Classification checker

**For Management:**
- `EXECUTIVE_SUMMARY_MONGODB_ISSUES.md` - Executive summary
- `MONGODB_ACTION_ITEMS.md` - Action items and tasks

---

## 🎉 Quick Wins

**Do This First:**

```bash
# 1. Import Bug #1 to Jira (2 minutes)
# 2. Get approval (30 seconds)
# 3. Fix it (3 minutes):

mongo mongodb://root:prisma@10.10.10.103:27017/prisma?authSource=admin

use prisma
var col = "77e49b5d-e06a-4aae-a33e-17117418151c";

db.getCollection(col).createIndex({"start_time": 1}, {background: true});
db.getCollection(col).createIndex({"end_time": 1}, {background: true});
db.getCollection(col).createIndex({"uuid": 1}, {unique: true, background: true});
db.getCollection(col).createIndex({"deleted": 1}, {background: true});

# 4. Verify (30 seconds):
py -m pytest tests/integration/infrastructure/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_mongodb_indexes_exist_and_optimal -v

# 5. Celebrate! 🎉
```

**Total time: ~6 minutes**  
**Impact: Users immediately see 1000x faster history playback**

---

**Questions?** Contact QA Team  
**Created:** October 16, 2025  
**Status:** ✅ Ready to use

