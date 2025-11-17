# ✅ באגים שנוצרו ב-Jira - 2025-11-08

**תאריך:** 2025-11-08 16:01  
**סטטוס:** ✅ **כל 3 הטיקטים נוצרו בהצלחה!**

---

## 📋 סיכום

נוצרו **3 טיקטי באג** ב-Jira עבור בעיות Focus Server שגילינו היום:

| # | Ticket Key | Summary | Priority | Status |
|---|------------|---------|----------|--------|
| 1 | **PZ-14712** | Focus Server pod restarts due to MongoDB connection failure during initialization | High | Created |
| 2 | **PZ-14713** | /configure endpoint returns unclear error when system is waiting for fiber | Medium | Created |
| 3 | **PZ-14714** | /configure endpoint doesn't validate metadata availability before attempting configuration | Medium | Created |

---

## 🐛 טיקט #1: PZ-14712 - MongoDB Connection Failure

**URL:** https://prismaphotonics.atlassian.net/browse/PZ-14712

**Summary:** Focus Server pod restarts due to MongoDB connection failure during initialization

**Priority:** High

**Labels:** `infrastructure`, `mongodb`, `kubernetes`, `reliability`

**Components:** Focus Server, Infrastructure

**Custom Fields:**
- **Found by:** QA Cycle
- **Expected Result:** Pod should wait for MongoDB to be available or retry connection with backoff instead of crashing
- **Actual Results:** Pod crashes and restarts repeatedly until MongoDB connection is restored
- **Reproduction Steps:** 6 steps documented

**Description:**
כולל תיאור מפורט של הבעיה, שגיאה, ראיות, root cause, ופתרונות מומלצים (Init Container, Retry Logic, Readiness Probe).

**Acceptance Criteria:**
- [ ] Pod doesn't crash when MongoDB is temporarily unavailable
- [ ] Pod waits for MongoDB or retries connection with backoff
- [ ] No repeated restarts due to MongoDB connection issues
- [ ] Readiness probe or init container implemented

---

## 🐛 טיקט #2: PZ-14713 - Error Handling לא ברור

**URL:** https://prismaphotonics.atlassian.net/browse/PZ-14713

**Summary:** /configure endpoint returns unclear error when system is waiting for fiber

**Priority:** Medium

**Labels:** `api`, `error-handling`, `ux`, `configure-endpoint`

**Components:** Focus Server, API

**Custom Fields:**
- **Found by:** QA Cycle
- **Expected Result:** Return 400 Bad Request with structured error response explaining what went wrong, why it happened, and what the user should do
- **Actual Results:** Returns 503 Service Unavailable with minimal error information
- **Reproduction Steps:** 4 steps documented

**Description:**
כולל תיאור מפורט של הבעיה, current vs desired response, impact, ופתרון מומלץ.

**Acceptance Criteria:**
- [ ] Returns 400 Bad Request (not 503) when metadata is missing
- [ ] Returns structured JSON error response
- [ ] Error message is clear and actionable
- [ ] Error includes relevant metadata details
- [ ] Client applications can handle the error programmatically

---

## 🐛 טיקט #3: PZ-14714 - חוסר Validation של Metadata

**URL:** https://prismaphotonics.atlassian.net/browse/PZ-14714

**Summary:** /configure endpoint doesn't validate metadata availability before attempting configuration

**Priority:** Medium

**Labels:** `api`, `validation`, `metadata`, `configure-endpoint`

**Components:** Focus Server, API

**Custom Fields:**
- **Found by:** QA Cycle
- **Expected Result:** Check metadata availability before attempting configuration and return clear error immediately if metadata is not available
- **Actual Results:** Attempts configuration first, then returns error after discovering metadata is not available during processing
- **Reproduction Steps:** 5 steps documented

**Description:**
כולל תיאור מפורט של הבעיה, current vs desired flow, impact, benefits, ופתרון מומלץ.

**Acceptance Criteria:**
- [ ] Metadata is validated before attempting configuration
- [ ] Error is returned immediately if metadata is not available
- [ ] Appropriate HTTP status codes are used (503 for system not ready, 400 for invalid state)
- [ ] Error messages are clear and actionable
- [ ] Reduced processing time for invalid requests

---

## 📊 סיכום

### מה נוצר:

✅ **3 טיקטי באג** ב-Jira  
✅ **כל הפרטים המלאים** - תיאור, steps to reproduce, expected/actual behavior  
✅ **שדות מותאמים אישית** - Found by, Expected Result, Actual Results, Reproduction Steps  
✅ **Labels ו-Components** - מסווגים כראוי  
✅ **Acceptance Criteria** - ברורים ומדידים  

### קישורים:

- **Board:** https://prismaphotonics.atlassian.net/jira/software/c/projects/PZ/boards/21
- **PZ-14712:** https://prismaphotonics.atlassian.net/browse/PZ-14712
- **PZ-14713:** https://prismaphotonics.atlassian.net/browse/PZ-14713
- **PZ-14714:** https://prismaphotonics.atlassian.net/browse/PZ-14714

### מסמכים רלוונטיים:

- **מסמך ניתוח מפורט:** `docs/04_testing/analysis/BUGS_TO_OPEN_FOR_DEVELOPMENT_TEAM.md`
- **מסמך ניתוח MongoDB:** `docs/04_testing/analysis/MONGODB_CONNECTION_RESTARTS_ANALYSIS.md`
- **מסמך ניתוח PRR:** `docs/04_testing/analysis/PRR_ERROR_CURRENT_STATUS_2025-11-08.md`
- **סקריפט יצירה:** `scripts/jira/create_bug_tickets_2025_11_08.py`

---

## ✅ Checklist

- [x] זיהינו את הבעיות בבירור ✅
- [x] יש לנו ראיות (לוגים, שגיאות) ✅
- [x] יש לנו מסמך ניתוח מפורט ✅
- [x] יש לנו פתרונות מומלצים ✅
- [x] פתחנו את הטיקטים ב-Jira ✅
- [x] כל השדות החובה מולאו ✅
- [x] Labels ו-Components הוגדרו ✅
- [x] Acceptance Criteria נוספו ✅

---

**עודכן לאחרונה:** 2025-11-08 16:01  
**סטטוס:** ✅ **כל 3 הטיקטים נוצרו בהצלחה ב-Jira!**

