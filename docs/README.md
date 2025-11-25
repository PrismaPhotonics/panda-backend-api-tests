# Focus Server Automation - Documentation Index

> Complete documentation for the Focus Server E2E Test Automation Framework

**Total Files:** 520+ | **Last Updated:** 2025-11-24

---

## 📚 Documentation Structure

### [01 - Getting Started](01_getting_started/) 📘 (36+ files)
Quick start guides, installation, and environment setup
- **[Quick Start Guide](01_getting_started/QUICK_START_NEW_PRODUCTION.md)**
- **[Quick Reference Card](01_getting_started/QUICK_REFERENCE_CARD.md)** ⭐ NEW
- **[Complete Setup](01_getting_started/NEW_PRODUCTION_ENVIRONMENT_COMPLETE_GUIDE.md)**
- **[How to Run Tests](01_getting_started/HOW_TO_RUN_TESTS.md)**
- K9s Connection Guides (4 documents)
- Monitoring & Logging Guides
- Recovery Procedures

### [02 - User Guides](02_user_guides/) 📗 (50 files)
Comprehensive how-to guides for testing and automation
- Real-time Pod Monitoring
- Job Lifecycle Management
- API Testing Guides
- Load & Performance Testing
- Story-specific Guides
- PZ Integration Guide

### [03 - Architecture](03_architecture/) 📙 (19 files)
System design, specifications, and architecture documents
- Technical Specifications
- API Specifications
- Integration Patterns
- Gap Analysis Documents
- Missing Specs Clarifications

### [04 - Testing](04_testing/) 📕 (87+ files)
Testing strategy, coverage, analysis, and reports
- **[Test Results](04_testing/test_results/)** (7+ execution reports)
  - **[Latest Failure Analysis](04_testing/test_results/TEST_FAILURES_ANALYSIS_2025-10-29.md)** (29 Oct 2025)
  - **[Hebrew Summary](04_testing/test_results/סיכום_תקלות_2025-10-29.md)**
- **[Xray Mapping](04_testing/xray_mapping/)** (24+ Xray documents + data files)
  - Complete test-to-Xray mapping
  - Coverage statistics (`tests_without_xray.csv`)
  - Integration guides
- **[Test Execution Guides](04_testing/)**
  - Alert Tests Documentation
  - How to Run Alerts Tests (`RUN_ALERTS_TESTS.txt`)
  - How to Run K8s Tests (`RUN_K8S_TESTS.txt`)
  - CI Test Instructions (`RUN_TESTS_CI.md`)
  - System Health Report (`health_report.md`)
- Test Analysis & Comparisons
- Duplicate Analysis
- Coverage Reports

### [05 - Development](05_development/) 📔 (1+ files)
Development guides and best practices
- **[Push Workflows Instructions](05_development/PUSH_WORKFLOWS_INSTRUCTIONS.md)**
- Contributing Guidelines (planned)
- Code Standards (planned)
- Debugging Guide (planned)

### [06 - Project Management](06_project_management/) 📓 (100+ files)
Project tracking, meetings, Jira, and presentations
- **[Jira Integration](06_project_management/jira/)** (30+ docs)
  - **[Bugs-to-Tests Mapping](06_project_management/jira/BUGS_TO_TESTS_MAPPING.md)** (15 bugs mapped)
  - **[Bug Integration Report](06_project_management/jira/JIRA_BUGS_INTEGRATION_COMPLETE.md)**
  - Test Cases Import Data (`jira_test_cases_import.csv`)
- **[Progress Reports](06_project_management/progress_reports/)** (15+ reports)
  - **[Documentation Migration](06_project_management/progress_reports/documentation_migration/)** (5 reports)
- **[Meetings](06_project_management/meetings/)** (22+ meeting docs)
  - Meeting Preparation Checklist
- **[Presentations](06_project_management/presentations/)** (23+ documents)
  - QPoint Presentations (Hebrew)
  - Presentation Package Guide
  - Presentation README
- **Executive Summary** (English)
- **Technical Statistics Appendix**

### [07 - Infrastructure](07_infrastructure/) 📒 (25+ files)
Infrastructure setup, configuration, and management
- **[Environment Master Doc](07_infrastructure/NEW_ENVIRONMENT_MASTER_DOCUMENT.md)**
- **[GitHub Actions Guide](07_infrastructure/README_GITHUB_ACTIONS.md)** ⭐ NEW
- **[RabbitMQ Guides](07_infrastructure/)** (6 comprehensive guides)
- **[MongoDB Documentation](07_infrastructure/)** (6 documents)
- Kubernetes Configuration
- gRPC Job Lifecycle
- Pod Monitoring

### [08 - Archive](08_archive/) 🗂️ (28 files)
Historical documents and deprecated content
- **[2025-10](08_archive/2025-10/)** - October 2025 legacy documents
- **[PDFs](08_archive/pdfs/)** - 9 PRISMA PDF manuals

---

## 🎯 Quick Access

### **For New Users:**
👉 **Start Here:** [Getting Started Guide](01_getting_started/QUICK_START_NEW_PRODUCTION.md)

### **For Running Tests:**
- [How to Run Tests](01_getting_started/HOW_TO_RUN_TESTS.md)
- [Test Coverage](04_testing/)
- [Latest Test Results](04_testing/test_results/TEST_FAILURES_ANALYSIS_2025-10-29.md)

### **For Development:**
- [Architecture Overview](03_architecture/)
- [User Guides](02_user_guides/)
- [Infrastructure Setup](07_infrastructure/)

### **For Project Tracking:**
- [Latest Progress](06_project_management/progress_reports/)
- [Meeting Notes](06_project_management/meetings/)
- [Bugs Found](06_project_management/jira/BUGS_TO_TESTS_MAPPING.md)

### **For Xray Integration:**
- [Xray Mapping](04_testing/xray_mapping/)
- [Xray Coverage](04_testing/xray_mapping/XRAY_COVERAGE_STATISTICS.md)
- [Integration Guide](04_testing/xray_mapping/XRAY_INTEGRATION_GUIDE.md)

---

## 📊 Statistics

### **Documentation Coverage:**
- **Total Files:** 520+
- **Getting Started:** 36+ comprehensive guides
- **User Guides:** 52+ how-to documents
- **Architecture:** 19 design documents
- **Testing:** 87+ test-related documents (includes analysis, execution guides, Xray mapping)
- **Project Management:** 100+ tracking documents (includes Jira, meetings, presentations)
- **Infrastructure:** 25+ setup guides (includes GitHub Actions)
- **Development:** 1+ workflow guides
- **Archive:** 40+ historical documents

### **Test Integration:**
- **Jira Bugs Mapped:** 15 (100% coverage)
- **Xray Tests Mapped:** 75+
- **Tests with Markers:** 120+
- **Latest Analysis:** 29 Oct 2025 (238/307 passed)

---

## 🔍 Search Tips

### **Find by Topic:**
```bash
# RabbitMQ guides:
ls docs/07_infrastructure/RABBITMQ*.md

# Xray mapping:
ls docs/04_testing/xray_mapping/

# Meeting notes:
ls docs/06_project_management/meetings/
```

### **Find by Date:**
```bash
# Latest documents:
ls -ltr docs/04_testing/test_results/

# October 2025 archive:
ls docs/08_archive/2025-10/
```

### **Find by Type:**
```bash
# All PDFs:
ls docs/08_archive/pdfs/

# All CSVs:
find docs/ -name "*.csv"
```

---

## 🗂️ Legacy Documentation

**Status:** ✅ All legacy documentation has been successfully migrated to `docs/` structure.

**Note:** New documentation should ONLY be added to the `docs/` structure above.

---

## 🔄 Maintenance

### **Last Reorganization:** 2025-11-24
### **Files Organized:** 520+
### **Structure Version:** 2.3
### **Recent Changes:**
- ✅ Moved 14 root-level docs to organized structure
- ✅ Created presentations/ subfolder
- ✅ Updated test execution guides
- ✅ Added GitHub Actions documentation
- ✅ Cleaned project root directory
### **Legacy Migration:** ✅ Complete - documentation/ folder deprecated
### **Next Review:** As needed

### **How to Contribute:**
1. Identify correct category (`docs/01_*` through `docs/08_*`)
2. Place document in that directory
3. Update relevant README.md
4. Link from this index if important

---

## 📞 Support

### **Questions About Documentation?**
- Check category READMEs for specific areas
- See [Complete Reorganization Report](06_project_management/progress_reports/documentation_migration/COMPLETE_PROJECT_REORGANIZATION.md)

### **Found a Bug?**
- See [Bugs to Tests Mapping](06_project_management/jira/BUGS_TO_TESTS_MAPPING.md)
- Check [Latest Test Analysis](04_testing/test_results/TEST_FAILURES_ANALYSIS_2025-10-29.md)

---

**[← Back to Project Root](../README.md)**

**Last Updated:** 2025-11-24 by QA Automation Team  
**Recent Changes:** Project root cleanup - 14 files reorganized into docs/ structure
