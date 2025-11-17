# מדריך מקיף - כל מסמכי הבדיקות של Focus Server
## רשימה מלאה למטרת העלאה ל-NotebookLM

תאריך יצירה: 27 אוקטובר 2025

---

## 📋 תוכן עניינים
1. [מסמכי תיעוד בדיקות מרכזיים](#1-מסמכי-תיעוד-בדיקות-מרכזיים)
2. [מצגות ותכנוני בדיקות](#2-מצגות-ותכנוני-בדיקות)
3. [ניתוחים והשוואות טסטים](#3-ניתוחים-והשוואות-טסטים)
4. [תיעוד Jira ו-Xray](#4-תיעוד-jira-ו-xray)
5. [ספציפיקציות חסרות ודרישות](#5-ספציפיקציות-חסרות-ודרישות)
6. [תיעוד טסטים - ארגון ומבנה](#6-תיעוד-טסטים---ארגון-ומבנה)
7. [מסמכי ארכיון רלוונטיים](#7-מסמכי-ארכיון-רלוונטיים)
8. [מדריכי הפעלה](#8-מדריכי-הפעלה)
9. [מסמכי README בתיקיות הטסטים](#9-מסמכי-readme-בתיקיות-הטסטים)

---

## 1. מסמכי תיעוד בדיקות מרכזיים
**תיקייה**: `documentation/testing/`

### 1.1 תיעוד כללי של סוויטות בדיקות
- `TEST_SUITE_INVENTORY.md` - מלאי מלא של כל סוויטות הבדיקות
- `TESTS_COMPARISON_TABLE.md` - טבלת השוואה בין בדיקות שונות
- `RECOMMENDED_ADDITIONAL_TESTS.md` - המלצות לבדיקות נוספות

### 1.2 ניתוח שגיאות ותיקונים
- `COMPLETE_TEST_ERRORS_ANALYSIS_EN.md` - ניתוח מלא של שגיאות בדיקה (אנגלית)
- `COMPLETE_TEST_ERRORS_ANALYSIS_HE.md` - ניתוח מלא של שגיאות בדיקה (עברית)
- `TEST_ERRORS_INDEX.md` - אינדקס של שגיאות בדיקה
- `TEST_FIX_SUMMARY.md` - סיכום תיקוני בדיקות
- `TEST_RUN_ANALYSIS_2025-10-23_17-10.md` - ניתוח הרצות בדיקה

### 1.3 בדיקות API
- `FOCUS_SERVER_API_ENDPOINTS.md` - תיעוד כל נקודות קצה של API
- `API_MIGRATION_LOG.md` - יומן מעבר API
- `API_MIGRATION_SUMMARY.md` - סיכום מעבר API
- `TESTS_FROM_CONFIG_ANALYSIS.md` - ניתוח בדיקות מקונפיגורציה

### 1.4 בדיקות Integration ו-Load
- `INTEGRATION_TESTS_ANALYSIS.md` - ניתוח בדיקות אינטגרציה
- `JOB_LIFECYCLE_AND_LOAD_TESTING_GUIDE.md` - מדריך בדיקות עומס ומחזור חיים של Job

### 1.5 בדיקות Live vs Historic
**תת-תיקייה**: `documentation/testing/live_historic/`
- `API_TEST_REPORT.md` - דוח בדיקות API
- `LIVE_VS_HISTORIC_MODE_ANALYSIS.md` - ניתוח מצבי Live מול Historic
- `LIVE_VS_HISTORIC_TESTING_SUMMARY.md` - סיכום בדיקות Live מול Historic
- `LIVE_VS_HISTORICAL_RECORDINGS.md` - תיעוד הקלטות

### 1.6 בדיקות SingleChannel View
- `SINGLECHANNEL_VIEW_TEST_QUICKSTART.md` - מדריך מהיר
- `SINGLECHANNEL_VIEW_TEST_SUMMARY.md` - סיכום בדיקות
- `SINGLECHANNEL_TEST_RESULTS.md` - תוצאות בדיקות
- `RUN_SINGLECHANNEL_TESTS.md` - הוראות הרצה

### 1.7 בדיקות Stress ו-Performance
- `PZ-13880_Stress_Test_Extreme_Values_DETAILED_BRIEFING.md` - תדריך מפורט לבדיקות קיצון

### 1.8 MongoDB
- `MONGODB_INDEXES_FIX_GUIDE.md` - מדריך תיקון אינדקסים
- `MONGODB_INDEXES_INVESTIGATION.md` - חקירת אינדקסים

### 1.9 Logging ו-Monitoring
- `ENHANCED_LOGGING_QUICKSTART.md` - מדריך מהיר
- `ENHANCED_LOGGING_SUMMARY.md` - סיכום מערכת לוגים
- `LOGGING_SYSTEM_IMPLEMENTATION.md` - יישום מערכת לוגים
- `ERROR_WARNING_LOGGING_UPDATE.md` - עדכון לוגים
- `REALTIME_POD_MONITORING.md` - ניטור Pod בזמן אמת

### 1.10 סיכומים ומסמכים למפגשים
- `DETAILED_TEST_ANALYSIS_FOR_MEETING.md` - ניתוח מפורט לפגישה
- `QUICK_REFERENCE_FOR_MEETING.md` - מדריך מהיר לפגישה
- `RESPONSES_TO_ROY_COMMENTS.md` - תשובות להערות רועי

### 1.11 תיעוד כללי
- `COMPLETE_TASKS_SUMMARY.md` - סיכום משימות שהושלמו
- `CONFIG_VALUES_UPDATE_SUMMARY.md` - סיכום עדכוני קונפיגורציה
- `EXAMPLE_OUTPUT.md` - דוגמאות פלט
- `INDEX_2025-10-23_WORK_SESSION.md` - אינדקס סשן עבודה

---

## 2. מצגות ותכנוני בדיקות
**תיקייה**: `documentation/presentations/`

### 2.1 תכנית בדיקה מפורטת (4 חלקים)
- `COMPLETE_TEST_PLAN_DETAILED_PART1.md` - חלק 1
- `COMPLETE_TEST_PLAN_DETAILED_PART2.md` - חלק 2
- `COMPLETE_TEST_PLAN_DETAILED_PART3.md` - חלק 3
- `COMPLETE_TEST_PLAN_DETAILED_PART4_SUMMARY.md` - חלק 4 וסיכום

### 2.2 מסמכי מאסטר
- `TEST_PLAN_MASTER_DOCUMENT.md` - מסמך מאסטר של תכנית בדיקה
- `INDEX_TEST_PLAN.md` - אינדקס תכנית בדיקה

### 2.3 ניתוחים והשוואות
- `TEST_COMPARISON_AND_ANALYSIS.md` - השוואה וניתוח בדיקות
- `Test_Plan_Analysis_and_Automation_Strategy.md` - ניתוח תכנית בדיקה ואסטרטגיית אוטומציה

### 2.4 חומרי מצגות
- `PRESENTATION_MATERIALS_SUMMARY.md` - סיכום חומרי מצגת
- `HTML_PRESENTATION_SUCCESS.md` - הצלחת מצגת HTML
- `PRESENTATION_WITH_LOCAL_LINKS_SUCCESS.md` - מצגת עם קישורים מקומיים
- `SLIDES_CONTENT_FOR_PRESENTATION.md` - תוכן שקופיות למצגת
- `CODE_LOCATIONS_FOR_PRESENTATION.md` - מיקומי קוד למצגת
- `README_PRESENTATIONS.md` - README למצגות
- `סיכום_חומרים_למצגת.md` - סיכום חומרים (עברית)

---

## 3. ניתוחים והשוואות טסטים
**תיקייה**: `documentation/analysis/`

### 3.1 מצגות PowerPoint ו-HTML
- `Automation_Specs_Gap_Review_EN_2025-10-22.pptx` - סקירת פערי ספציפיקציות (אנגלית)
- `Automation_Specs_Gap_Review_EN_GSlides_2025-10-22.odp` - גרסת Google Slides
- `Automation_Specs_Gap_Review_FULL_WITH_LINKS.pptx` - גרסה מלאה עם קישורים
- `Automation_Specs_Gap_Review_LOCAL_LINKS.pptx` - גרסה עם קישורים מקומיים
- `Automation_Specs_Gap_Review_Presentation.html` - גרסת HTML

### 3.2 מדריכי שימוש במצגות
- `HOW_TO_USE_PRESENTATION_WITH_LINKS.md` - איך להשתמש במצגת עם קישורים
- `HTML_PRESENTATION_GUIDE.md` - מדריך מצגת HTML
- `LOCAL_LINKS_GUIDE.md` - מדריך קישורים מקומיים
- `QUICK_START_FIXED_LINKS.md` - התחלה מהירה עם קישורים מתוקנים

### 3.3 קבצי CSV - השוואות וניתוחים
- `TESTS_TO_ADD_TO_CODE.csv` - בדיקות להוספה לקוד
- `TESTS_TO_ADD_TO_JIRA.csv` - בדיקות להוספה ל-Jira
- `tests_without_specs_EN_2025-10-22.csv` - בדיקות ללא ספציפיקציות (אנגלית)
- `tests_without_specs_LOCAL_LINKS.csv` - בדיקות ללא ספציפיקציות (עם קישורים)

### 3.4 ניתוחים (עברית)
- `דוח_השוואה_JIRA_מול_אוטומציה.md` - דוח השוואה
- `הסבר_קטגוריות_טסטים_חסרים.md` - הסבר קטגוריות
- `רשימת_ספסיפיקציות_נדרשות_לפגישה.md` - רשימת ספציפיקציות

### 3.5 ניתוחים נוספים
- `MISSING_IN_AUTOMATION_CODE.md` - מה חסר בקוד אוטומציה
- `TESTS_IN_CODE_MISSING_IN_XRAY_NO_WATERFALL.md` - בדיקות בקוד שחסרות ב-Xray

---

## 4. תיעוד Jira ו-Xray
**תיקיות**: `documentation/jira/` ו-`documentation/xray/`

### 4.1 דוחות סטטוס Jira
- `JIRA_TESTS_STATUS_REPORT.md` - דוח סטטוס בדיקות
- `סיכום_סטטוס_טסטים_JIRA.md` - סיכום סטטוס (עברית)

### 4.2 כרטיסי Jira
- `JIRA_TICKETS_FOCUS_SERVER_AUTOMATION.md` - כרטיסי אוטומציה
- `JIRA_TICKETS_FOCUS_SERVER_BUGS.md` - כרטיסי באגים
- `JIRA_XRAY_NEW_TESTS.md` - בדיקות חדשות ב-Xray

### 4.3 דוחות באגים
- `BUG_REPORT_20251009.md` - דוח באגים
- `BUG_TICKETS_AUTOMATION_FINDINGS.md` - ממצאי אוטומציה
- `BUG_TICKETS_CREATION_SUMMARY.md` - סיכום יצירת כרטיסי באג
- `BUG_TICKETS_README.md` - README לכרטיסי באג
- `BUG_TICKET_SINGLECHANNEL_VIEW_TEMPLATE.md` - תבנית כרטיס SingleChannel

### 4.4 MongoDB Bugs
- `MONGODB_BUG_TICKETS.md` - כרטיסי באג MongoDB
- `MONGODB_BUGS_REPORT.md` - דוח באגים MongoDB
- `MONGODB_BUGS_JIRA_IMPORT.csv` - יבוא באגים ל-Jira

### 4.5 בדיקות ספציפיות ב-Jira/Xray
- `PZ-13602_MISSING_FIELDS_ANALYSIS.md` - ניתוח שדות חסרים
- `PZ-13602_MISSING_FIELDS_SUMMARY_EN.md` - סיכום שדות חסרים (אנגלית)
- `T_DATA_001_SOFT_DELETE_REPORT.md` - דוח Soft Delete
- `T_DATA_002_HISTORICAL_VS_LIVE_REPORT.md` - דוח Historical vs Live
- `T_DATA_002_INDEX.md` - אינדקס T_DATA_002
- `T_DATA_002_XRAY_SUMMARY_HEBREW.md` - סיכום Xray (עברית)

### 4.6 יבוא ל-Xray
- `XRAY_IMPORT_GUIDE.md` - מדריך יבוא
- `XRAY_IMPORT_T_DATA_002.csv` - קובץ יבוא
- `XRAY_T_DATA_002_HISTORICAL_VS_LIVE.md` - תיעוד יבוא

### 4.7 Xray - בדיקות עדיפות גבוהה
**תיקייה**: `documentation/xray/`
- `HIGH_PRIORITY_TESTS_SUMMARY.md` - סיכום בדיקות עדיפות גבוהה
- `XRAY_9_MISSING_CRITICAL_TESTS_FULL_DOCUMENTATION.md` - 9 בדיקות קריטיות חסרות
- `XRAY_HIGH_PRIORITY_MISSING_TESTS.md` - בדיקות עדיפות גבוהה חסרות
- `XRAY_HIGH_PRIORITY_TESTS_DOCUMENTATION.md` - תיעוד בדיקות עדיפות גבוהה
- `XRAY_COMPLETE_TEST_DOCUMENTATION_SUMMARY.md` - סיכום תיעוד מלא
- `XRAY_CATEGORIES_REORGANIZATION_PLAN.md` - תכנית ארגון מחדש
- `XRAY_INTEGRATION_IMPLEMENTATION.md` - יישום אינטגרציית Xray

---

## 5. ספציפיקציות חסרות ודרישות
**תיקייה**: `documentation/specs/`

### 5.1 דוחות ספציפיקציות חסרות (אנגלית)
- `CRITICAL_MISSING_SPECS_LIST.md` - רשימת ספציפיקציות קריטיות חסרות
- `MISSING_SPECS_COMPREHENSIVE_REPORT.md` - דוח מקיף
- `MISSING_SPECS_INDEX.md` - אינדקס ספציפיקציות חסרות
- `CODE_EVIDENCE_MISSING_SPECS.md` - עדויות קוד לספציפיקציות חסרות
- `COMPLETE_MISSING_SPECS_CONFLUENCE.md` - ספציפיקציות חסרות ב-Confluence
- `TOP_CODE_LINKS_FOR_SPECS.md` - קישורי קוד מובילים

### 5.2 מסמכים לפגישות
- `CONFLUENCE_SPECS_MEETING.md` - מפגש Confluence
- `SPECS_REQUIREMENTS_FOR_MEETING.md` - דרישות לפגישה
- `specs_checklist_for_meeting.csv` - רשימת בדיקה לפגישה
- `MISSING_SPECS_TABLE.csv` - טבלת ספציפיקציות חסרות

### 5.3 מסמכים בעברית
- `ספציפיקציות_חסרות_לפרויקט_האוטומציה.md` - ספציפיקציות חסרות
- `סיכום_מהיר_SPECS_חסרים.md` - סיכום מהיר
- `מסמך_טכני_לפגישת_SPECS_מפורט.md` - מסמך טכני מפורט
- `הערות_לפגישת_SPECS_מסודרות.md` - הערות מסודרות
- `הסבר_טכני_מקצועי_לבעיות_SPECS.md` - הסבר טכני מקצועי
- `דוגמאות_קוד_חוסר_SPECS.md` - דוגמאות קוד

---

## 6. תיעוד טסטים - ארגון ומבנה
**תיקייה**: `documentation/tests_docs/`

### 6.1 מבנה ומיפוי
- `COMPLETE_TESTS_DIRECTORY_MAP.md` - מפה מלאה של תיקיית הטסטים
- `TESTS_FINAL_STRUCTURE.md` - מבנה סופי
- `TESTS_REORGANIZATION_COMPLETE.md` - השלמת ארגון מחדש

### 6.2 חקירות וגילויים
- `CRITICAL_MISSING_TESTS_DISCOVERY.md` - גילוי בדיקות קריטיות חסרות
- `WHAT_HAPPENED_TO_HIGH_PRIORITY_TESTS.md` - מה קרה לבדיקות עדיפות גבוהה

### 6.3 שחזור ומיקום (עברית)
- `TESTS_LOCATION_COMPLETE_HE.md` - מיקום מלא (עברית)
- `TESTS_RESTORED_SUCCESS.md` - הצלחת שחזור
- `שחזור_טסטים_הושלם_בהצלחה.md` - שחזור הושלם (עברית)
- `סיכום_חקירת_טסטים_חסרים.md` - סיכום חקירה (עברית)

---

## 7. מסמכי ארכיון רלוונטיים
**תיקייה**: `archive_docs/`

### 7.1 מסמכי Prisma (PDF)
- `PRISMA-Yoshi- REST API Documentation for focus webserver-151025-094916.pdf` - תיעוד REST API
- `PRISMATEAM-Focus Server – Parameterized Testing Plan-151025-095022.pdf` - תכנית בדיקה פרמטרית
- `PRISMATEAM-Focus Server – Integrations Map-151025-094814.pdf` - מפת אינטגרציות
- `PRISMA-PANDA Ubuntu 20.04 Server Installation and Configuration Guide-161025-150721.pdf` - מדריך התקנה
- `PRISMA-PandaGUI First Milestone Release Notes-161025-150838.pdf` - הערות שחרור Milestone 1
- `PRISMA-PandaGUI Second Milestone Release Notes-221025-135255.pdf` - הערות שחרור Milestone 2
- `PRISMA-How to create multiple alerts, delete all the alerts & edit alerts in Panda app_-161025-150856.pdf` - מדריך Alerts

### 7.2 קבצי CSV מ-Xray
- `Test plan (PZ-13756) by Roy Avrahami (Jira).csv` - תכנית בדיקה מ-Jira
- `Tests_xray_21_10_25.csv` - בדיקות Xray
- `xray_tests_21_10_25.csv` - בדיקות Xray (נוסף)

### 7.3 מדריכים ארכיוניים
- `SINGLECHANNEL_VIEW_TEST_GUIDE.md` - מדריך בדיקות SingleChannel (ארכיון)
- `RABBITMQ_AUTOMATION_GUIDE.md` - מדריך אוטומציה RabbitMQ
- `RABBITMQ_AUTOMATION_QUICK_START.md` - התחלה מהירה RabbitMQ
- `RABBITMQ_CONNECTION_GUIDE.md` - מדריך חיבור RabbitMQ
- `RABBITMQ_QUICK_REFERENCE.md` - מדריך מהיר RabbitMQ
- `COMPLETE_RABBITMQ_JOURNEY.md` - מסע מלא RabbitMQ
- `BIT_RABBITMQ_PATTERNS.md` - דפוסי RabbitMQ

### 7.4 מסמכים טכניים
- `TECHNICAL_SPECIFICATIONS_CLARIFICATIONS.md` - הבהרות ספציפיקציות טכניות
- `Critical Missing Specifications f.txt` - ספציפיקציות קריטיות חסרות
- `HOW_TO_DISCOVER_DATABASE_SCHEMA.md` - איך לגלות סכמת מסד נתונים
- `MONGODB_SCHEMA_REAL_FINDINGS.md` - ממצאים אמיתיים סכמת MongoDB

### 7.5 מדריכי התקנה וקונפיגורציה
- `PZ_INTEGRATION_GUIDE.md` - מדריך אינטגרציית PZ
- `QUICK_START_PZ.md` - התחלה מהירה PZ
- `AUTO_INFRASTRUCTURE_SETUP.md` - הקמת תשתית אוטומטית
- `📌_הוראות_עדכון_קונפיג.txt` - הוראות עדכון קונפיגורציה
- `Update_PandaApp_Config.ps1` - סקריפט עדכון קונפיגורציה

### 7.6 Logging ו-Security
- `ENHANCED_LOGGING_GUIDE.md` - מדריך Logging מתקדם
- `SECURITY_NOTES.md` - הערות אבטחה

### 7.7 סיכומים והשלמות
- `COMPLETE_PROJECT_STRUCTURE.md` - מבנה פרויקט מלא
- `FINAL_REORGANIZATION_SUMMARY.md` - סיכום ארגון מחדש סופי
- `CLEANUP_SUMMARY_20251021.md` - סיכום ניקיון
- `USERSETTINGS_VALIDATION_REPORT_HE.md` - דוח ולידציה (עברית)

---

## 8. מדריכי הפעלה
**תיקייה**: `documentation/guides/`

### 8.1 חיבור ל-Kubernetes
- `K9S_CONNECTION_GUIDE.md` - מדריך חיבור K9s
- `K9S_CORRECT_CONNECTION.md` - חיבור נכון ל-K9s
- `K9S_HEBREW_SUMMARY.md` - סיכום K9s (עברית)
- `QUICK_K9S_SETUP.md` - הקמה מהירה K9s

### 8.2 ניטור ולוגים
- `LOGGING_QUICK_REFERENCE.md` - מדריך מהיר Logging
- `MONITORING_LOGS_GUIDE.md` - מדריך ניטור לוגים
- `RECOVERY_COMMANDS.md` - פקודות שחזור

### 8.3 סביבת Production
- `NEW_PRODUCTION_ENVIRONMENT_COMPLETE_GUIDE.md` - מדריך מלא סביבת Production
- `QUICK_START_NEW_PRODUCTION.md` - התחלה מהירה Production

### 8.4 עדכון קוד
- `UPDATE_PZ_CODE_FROM_BITBUCKET.md` - עדכון קוד PZ מ-Bitbucket

---

## 9. מסמכי README בתיקיות הטסטים
**תיקייה**: `tests/`

### 9.1 תיעוד ארגון
- `tests/README.md` - README ראשי של תיקיית הטסטים
- `tests/TEST_REORGANIZATION_SUMMARY.md` - סיכום ארגון מחדש
- `tests/TESTS_LOCATION_GUIDE_HE.md` - מדריך מיקום (עברית)

### 9.2 תיעוד לפי קטגוריה
- `tests/data_quality/README.md` - בדיקות איכות נתונים
- `tests/infrastructure/README.md` - בדיקות תשתית
- `tests/integration/README.md` - בדיקות אינטגרציה
- `tests/integration/api/README.md` - בדיקות API
- `tests/integration/performance/PERFORMANCE_TESTS_STATUS.md` - סטטוס בדיקות ביצועים
- `tests/load/README.md` - בדיקות עומס
- `tests/performance/README.md` - בדיקות ביצועים
- `tests/security/README.md` - בדיקות אבטחה
- `tests/stress/README.md` - בדיקות לחץ

---

## 📊 סיכום סטטיסטי

### מסמכים לפי קטגוריות:
- **תיעוד בדיקות**: 37+ מסמכים
- **מצגות**: 15 מסמכים
- **ניתוחים**: 18 מסמכים (כולל 5 מצגות PowerPoint/HTML)
- **Jira/Xray**: 29 מסמכים
- **ספציפיקציות**: 16 מסמכים
- **תיעוד ארגון טסטים**: 9 מסמכים
- **מדריכים**: 10 מסמכים
- **ארכיון**: 30+ מסמכים (כולל 7 PDF-ים)
- **README בקוד**: 9 מסמכים

### **סה"כ: כ-173 מסמכים רלוונטיים לבדיקות**

---

## 🎯 המלצות להעלאה ל-NotebookLM

### שלב 1 - מסמכים עיקריים (חובה):
1. כל המסמכים בתיקייה `documentation/testing/`
2. כל המסמכים בתיקייה `documentation/presentations/`
3. כל המסמכים בתיקייה `documentation/xray/`
4. `TEST_PLAN_MASTER_DOCUMENT.md`
5. `TEST_COMPARISON_AND_ANALYSIS.md`

### שלב 2 - ניתוחים והשוואות:
1. כל המסמכים בתיקייה `documentation/analysis/`
2. קבצי CSV מתיקייה זו (מידע מובנה)

### שלב 3 - Jira ו-Specs:
1. כל המסמכים בתיקייה `documentation/jira/`
2. כל המסמכים בתיקייה `documentation/specs/`

### שלב 4 - מדריכים וארכיון:
1. כל המסמכים בתיקייה `documentation/guides/`
2. PDF-ים מתיקיית `archive_docs/` (מסמכי Prisma)
3. מדריכים רלוונטיים מתיקיית הארכיון

### שלב 5 - תיעוד קוד:
1. כל קבצי README מתיקיית `tests/`
2. `documentation/tests_docs/` - כל המסמכים

---

## 💡 הערות חשובות:

1. **קבצי PDF**: 7 מסמכי Prisma חשובים בארכיון - מכילים מפרטים טכניים רשמיים
2. **קבצי CSV**: מכילים נתונים מובנים מ-Xray ו-Jira - שימושיים לניתוח
3. **מסמכים דו-לשוניים**: חלק מהמסמכים קיימים גם באנגלית וגם בעברית
4. **מסמכי HTML/PowerPoint**: 5 מצגות שונות - מומלץ להעלות גם PDF אם אפשרי

---

## 📌 קובץ זה נוצר אוטומטית
תאריך: 27 אוקטובר 2025  
מטרה: סיכום מקיף לצורך העלאה ל-NotebookLM  
מקור: סריקת כל תיקיות הפרויקט הרלוונטיות לבדיקות

