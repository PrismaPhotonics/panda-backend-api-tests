# 📚 MongoDB node2/node4 Issue - Documentation Index

**Last Updated:** October 21, 2025

---

## 🎯 Start Here

כדי להבין את הבעיה מהר, קרא לפי סדר:

### 1. 📋 סיכום דף אחד (1 minute read)
**File:** `MONGODB_NODE2_NODE4_ISSUE_SUMMARY.md`  
**Best for:** מנהלים, מי שצריך הבנה מהירה

### 2. 🚨 פעולות נדרשות (2 minute read)
**File:** `URGENT_JIRA_UPDATES_NEEDED.md`  
**Best for:** מי שצריך לעדכן את Jira

### 3. 🔍 מסמך טכני מלא (10 minute read)
**File:** `MONGODB_COLLECTIONS_CLARIFICATION.md`  
**Best for:** מפתחים, QA engineers, ארכיטקטים

---

## 📖 המסמכים המלאים

| קובץ | גודל | תיאור | קהל יעד |
|------|------|--------|---------|
| `MONGODB_NODE2_NODE4_ISSUE_SUMMARY.md` | קצר | סיכום מהיר - מה הבעיה ומה לעשות | כולם |
| `URGENT_JIRA_UPDATES_NEEDED.md` | בינוני | רשימת עדכונים נדרשים ב-Jira | Jira admins |
| `MONGODB_COLLECTIONS_CLARIFICATION.md` | ארוך | הסבר טכני מפורט + קוד + דוגמאות | Technical team |
| `README.md` (שורות 221-245) | קצר | הערה ב-README הראשי | כולם |
| `דוח_השוואה_JIRA_מול_אוטומציה.md` | עדכון | סעיפים 76-86, 64-69 | QA team |
| `TESTS_IN_CODE_MISSING_IN_XRAY.md` | עדכון | שורות 10-18 | QA team |

---

## 🗂️ מבנה התיעוד

```
MONGODB ISSUE DOCUMENTATION
│
├── 📄 MONGODB_NODE2_NODE4_ISSUE_SUMMARY.md
│   └── Quick 1-page summary
│
├── 📄 URGENT_JIRA_UPDATES_NEEDED.md
│   └── Action items for Jira updates
│
├── 📄 MONGODB_COLLECTIONS_CLARIFICATION.md
│   └── Full technical explanation
│       ├── Problem description
│       ├── Code examples
│       ├── Architecture explanation
│       └── Affected tests list
│
├── 📄 MONGODB_ISSUE_INDEX.md (this file)
│   └── Navigation guide
│
└── 📄 README.md (updated)
    └── Known Issues section added
```

---

## 🎓 מסלולי קריאה מומלצים

### For Managers / Team Leads
1. Read: `MONGODB_NODE2_NODE4_ISSUE_SUMMARY.md`
2. Review: `URGENT_JIRA_UPDATES_NEEDED.md`
3. Decision: Approve Jira updates

### For QA Engineers
1. Read: `MONGODB_COLLECTIONS_CLARIFICATION.md` (full document)
2. Review: Code in `tests/integration/infrastructure/test_mongodb_data_quality.py`
3. Action: Update test documentation

### For Jira Admins
1. Read: `URGENT_JIRA_UPDATES_NEEDED.md`
2. Reference: Example updates in the document
3. Action: Update 6 affected tickets

### For Developers (New Team Members)
1. Read: `README.md` - Known Issues section
2. Deep dive: `MONGODB_COLLECTIONS_CLARIFICATION.md`
3. Understand: Why GUID-based naming is used

---

## 🔗 קישורים מהירים

### קוד רלוונטי:
- **הקוד הנכון שלנו:** `tests/integration/infrastructure/test_mongodb_data_quality.py`
  - Method: `_get_recording_collection_name()` (lines 138-181)
  - Test: `test_required_collections_exist()` (lines 200-304)

### Jira tickets שצריכים עדכון:
- PZ-13598 - MongoDB Collections Exist
- PZ-13684 - node4 Schema Validation
- PZ-13685 - Recordings Metadata Completeness
- PZ-13686 - MongoDB Indexes Validation
- PZ-13687 - MongoDB Recovery
- PZ-13705 - Historical vs Live

---

## 📊 Timeline

| תאריך | אירוע |
|-------|-------|
| 2025-10-20 | Jira tests created (with node2/node4 references) |
| 2025-10-21 | Issue discovered during code review |
| 2025-10-21 | Full documentation created (this index) |
| 2025-10-21 | Waiting for Jira updates |

---

## ❓ FAQs

**Q: Which document should I read first?**  
A: `MONGODB_NODE2_NODE4_ISSUE_SUMMARY.md` - it's a 1-page overview.

**Q: I need to update Jira, what do I read?**  
A: `URGENT_JIRA_UPDATES_NEEDED.md` - it has specific instructions.

**Q: I want to understand the technical details?**  
A: `MONGODB_COLLECTIONS_CLARIFICATION.md` - full technical document.

**Q: Is our automation code wrong?**  
A: NO! Our code is CORRECT. Only Jira documentation needs updates.

**Q: Where did node2/node4 come from?**  
A: Unknown. Possibly old naming convention or documentation error.

---

## 📞 Who to Contact

| Question Type | Contact |
|---------------|---------|
| Technical questions | QA Automation Team |
| Jira updates | Jira Administrator |
| Architecture questions | Tech Lead |
| Process questions | QA Team Lead |

---

## ✅ Status

| Item | Status |
|------|--------|
| Issue discovered | ✅ Complete |
| Documentation created | ✅ Complete |
| Code validated | ✅ Correct (no changes needed) |
| Jira updates | ⏳ Pending |
| Team notified | ⏳ Pending |

---

**Created:** October 21, 2025  
**Maintained by:** QA Automation Team  
**Version:** 1.0

