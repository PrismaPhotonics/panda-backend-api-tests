# Getting Started

> Quick start guides, installation instructions, and environment setup

---

## 📋 Overview

Everything you need to get started with the Focus Server Automation Framework.

## 📁 Key Documents

### Installation & Setup
- **[NEW_PRODUCTION_ENVIRONMENT_COMPLETE_GUIDE.md](NEW_PRODUCTION_ENVIRONMENT_COMPLETE_GUIDE.md)** - Complete setup guide
- **[QUICK_START_NEW_PRODUCTION.md](QUICK_START_NEW_PRODUCTION.md)** - Quick start guide
- **[RUN_TESTS_NEW_PRODUCTION.md](RUN_TESTS_NEW_PRODUCTION.md)** - How to run tests

### K9s & Kubernetes Access
- **[K9S_CONNECTION_GUIDE.md](K9S_CONNECTION_GUIDE.md)** - Complete K9s connection guide
- **[K9S_CORRECT_CONNECTION.md](K9S_CORRECT_CONNECTION.md)** - Correct connection steps
- **[QUICK_K9S_SETUP.md](QUICK_K9S_SETUP.md)** - Quick K9s setup
- **[K9S_HEBREW_SUMMARY.md](K9S_HEBREW_SUMMARY.md)** - Hebrew K9s guide

### Monitoring & Logging
- **[MONITORING_LOGS_GUIDE.md](MONITORING_LOGS_GUIDE.md)** - Log monitoring guide
- **[LOGGING_QUICK_REFERENCE.md](LOGGING_QUICK_REFERENCE.md)** - Logging quick reference

### Recovery & Updates
- **[RECOVERY_COMMANDS.md](RECOVERY_COMMANDS.md)** - Recovery procedures
- **[UPDATE_PZ_CODE_FROM_BITBUCKET.md](UPDATE_PZ_CODE_FROM_BITBUCKET.md)** - Update PZ code

### Hebrew Archive
- Various Hebrew guides moved from project root

---

## 🚀 Quick Start (5 Minutes)

1. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure Environment:**
```bash
# Edit config/environments.yaml
# Set environment: new_production
```

3. **Run Your First Test:**
```bash
pytest tests/infrastructure/test_external_connectivity.py -v
```

4. **Access K9s (Optional):**
```bash
ssh root@10.10.100.3
ssh prisma@10.10.100.113
k9s
```

---

## 📚 Related Documentation

- [User Guides](../02_user_guides/) - How to use the framework
- [Architecture](../03_architecture/) - System design
- [Infrastructure](../07_infrastructure/) - Infrastructure details

---

**[← Back to Docs Home](../README.md)**

