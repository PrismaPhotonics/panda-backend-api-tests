# Focus Server Automation - Documentation Index

> Complete documentation for the Focus Server E2E Test Automation Framework

**Total Files:** 512+ | **Last Updated:** 2025-11-04

---

## 📚 Documentation Structure

### [01 - Getting Started](01_getting_started/) 📘 (35 files)
Quick start guides, installation, and environment setup
- **[Quick Start Guide](01_getting_started/QUICK_START_NEW_PRODUCTION.md)**
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

### [04 - Testing](04_testing/) 📕 (81 files)
Testing strategy, coverage, analysis, and reports
- **[Test Results](04_testing/test_results/)** (7+ execution reports)
  - **[Latest Failure Analysis](04_testing/test_results/TEST_FAILURES_ANALYSIS_2025-10-29.md)** (29 Oct 2025)
  - **[Hebrew Summary](04_testing/test_results/סיכום_תקלות_2025-10-29.md)**
- **[Xray Mapping](04_testing/xray_mapping/)** (24 Xray documents + data files)
  - Complete test-to-Xray mapping
  - Coverage statistics
  - Integration guides
- Test Analysis & Comparisons
- Duplicate Analysis
- Coverage Reports

### [05 - Development](05_development/) 📔 (0 files)
Development guides and best practices (to be populated)
- Contributing Guidelines (planned)
- Code Standards (planned)
- Debugging Guide (planned)

### [06 - Project Management](06_project_management/) 📓 (91 files)
Project tracking, meetings, Jira, and presentations
- **[Jira Integration](06_project_management/jira/)** (30+ docs)
  - **[Bugs-to-Tests Mapping](06_project_management/jira/BUGS_TO_TESTS_MAPPING.md)** (15 bugs mapped)
  - **[Bug Integration Report](06_project_management/jira/JIRA_BUGS_INTEGRATION_COMPLETE.md)**
- **[Progress Reports](06_project_management/progress_reports/)** (15+ reports)
  - **[Documentation Migration](06_project_management/progress_reports/documentation_migration/)** (5 reports)
- **[Meetings](06_project_management/meetings/)** (21+ meeting docs)
- Presentations (19 documents)

### [07 - Infrastructure](07_infrastructure/) 📒 (24 files)
Infrastructure setup, configuration, and management
- **[Environment Master Doc](07_infrastructure/NEW_ENVIRONMENT_MASTER_DOCUMENT.md)**
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
- **Total Files:** 512+
- **Getting Started:** 35 comprehensive guides
- **User Guides:** 52+ how-to documents
- **Architecture:** 19 design documents
- **Testing:** 150+ test-related documents (includes analysis, tests_docs)
- **Project Management:** 100+ tracking documents (includes epics, milestones, confluence, summaries)
- **Infrastructure:** 24 setup guides
- **Archive:** 40+ historical documents (includes documentation_archive)

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

### **Last Reorganization:** 2025-11-04
### **Files Organized:** 512+
### **Structure Version:** 2.2
### **Legacy Migration:** ✅ Complete - documentation/ folder removed
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

**Last Updated:** 2025-10-29 by QA Automation Team
