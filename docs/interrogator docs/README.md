# 📁 Interrogator Automation Documentation

**Owner:** Roy Avrahami - QA Team Lead  
**Created:** December 2024  
**Status:** Active - Phase 1 (Knowledge Acquisition)

---

## 📚 Documents Index

### Project Planning
| # | Document | Description | Language |
|---|----------|-------------|----------|
| 1 | [01_sow_statement_of_work.md](./01_sow_statement_of_work.md) | Statement of Work - Full project scope | English |
| 2 | [02_feasibility_study_he.md](./02_feasibility_study_he.md) | Feasibility study and recommendations | Hebrew |
| 3 | [03_discovery_meeting_agenda.md](./03_discovery_meeting_agenda.md) | Meeting agenda for knowledge transfer | Hebrew |
| 4 | [04_initial_priorities.md](./04_initial_priorities.md) | Initial priorities from first meeting | English |
| **9** | **[09_sow_phase1_focused.md](./09_sow_phase1_focused.md)** | **🆕 Phase 1 Focused SOW (Management Approved)** | **English** |

### Confluence Extracted Documentation
| # | Document | Description | Language |
|---|----------|-------------|----------|
| 5 | [05_confluence_pages_analysis.md](./05_confluence_pages_analysis.md) | Analysis of existing Confluence documentation | English |
| 6 | [06_confluence_extracted_content.md](./06_confluence_extracted_content.md) | Full extracted content from 6 Confluence pages | English |
| 7 | [07_additional_confluence_docs.md](./07_additional_confluence_docs.md) | BIT Tests, Fiber Inspector, E2E, Roadmap | English |
| 8 | [08_test_design_architecture.md](./08_test_design_architecture.md) | Test Design Levels & Integration Scenarios | English |

### Technical Reference
| # | Document | Description | Language |
|---|----------|-------------|----------|
| 10 | [10_critical_investigation_report.md](./10_critical_investigation_report.md) | **🔴 Critical issues & tech debt analysis** | English |
| 11 | [11_testing_methods_reference.md](./11_testing_methods_reference.md) | Testing methods & suite categories | English |
| 12 | [12_pf_criteria_reference.md](./12_pf_criteria_reference.md) | Pass/Fail criteria YAML reference | English |

---

## 🎯 Project Overview

### Goal
Transfer ownership of the **InterrogatorQA** automation framework from the Interrogator development team to the QA Automation team, and build comprehensive functional automation coverage.

### Current Status
- **Phase:** Phase 1 - Foundation & Critical Coverage (Focused SOW)
- **Owner:** Roy Avrahami (QA Team Lead)
- **Duration:** 5-6 months

### Phase 1 Scope (Management Approved)

| # | Work Package | Duration | Status |
|---|--------------|----------|--------|
| **WP1** | Data Path Mapping & Validation | 2 months | 🔴 Not Started |
| **WP2** | SVC Commands & Alerts Testing | 1 month | 🔴 Not Started |
| **WP3** | Failure Simulation & Resilience | 2-3 months | 🔴 Not Started |

### Key Challenges
- 🔴 Complex system (12 core services, 45+ microservices)
- 🔴 Limited documentation (partially addressed - see extracted docs)
- 🔴 Infrastructure-focused automation (missing functional tests)
- 🟡 Knowledge concentrated in few individuals

---

## 📋 Phase 1 Work Packages

### WP1: Data Path Mapping (2 months)
| Deliverable | Description |
|-------------|-------------|
| Path Inventory | Map all 6 core data flows |
| Config Manifest Parser | Extract active paths from effective_params.yaml |
| Path Validation Tests | Automated tests per data path |
| Queue Mapping | RabbitMQ queue→service relationships |

### WP2: SVC Commands (1 month)
| Deliverable | Description |
|-------------|-------------|
| SVC Commands Inventory | Document all Supervisor CLI commands |
| Command-Alert Matrix | Map commands to expected alerts |
| SVC Test Suite | Automated command verification |

### WP3: Failure Simulation (2-3 months)
| Deliverable | Description |
|-------------|-------------|
| Failure Framework | Chaos engineering capabilities |
| Fiber Issue Tests | Cut, attenuation, OTDR anomalies |
| Service Crash Tests | Recovery validation |
| Infrastructure Tests | Network, disk, DB failures |

---

## 🔗 Related Resources

### Confluence Pages
- [InterrogatorQA - Product level overview](https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/2098462722/InterrogatorQA+-+Product+level+overview)
- [InterrogatorQA Technical level overview](https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/2098790423/InterrogatorQA+Technical+level+overview)
- [Start using QA framework - easy start](https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/2114355204/Start+using+QA+framework+-+easy+start)
- [Logs Collector](https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/2248114178/Logs+Collector)
- [Monitoring architecture](https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/2338226184/Monitoring+architecture)
- [Data Analysis Recovery Tools](https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/2337177613/Data+Analysis+Recovery+Tools)

### Repositories
- `nc_pz` - Main Interrogator repository (Bitbucket)

---

## 📅 Timeline

| Phase | Duration | Focus | Owner |
|-------|----------|-------|-------|
| Phase 1 | Months 1-2 | Knowledge Acquisition | Roy |
| Phase 2 | Months 3-10 | Functional Coverage & Stabilization | Roy + New Hire |
| Phase 3 | Months 10-12 | CI/CD Integration | Automation Engineer |

---

## ✅ Next Steps

1. [ ] Read all Confluence documentation
2. [ ] Schedule deep-dive sessions with Inbar's team
3. [ ] Get access to nc_pz repository
4. [ ] Set up development environment
5. [ ] Create path mapping document
6. [ ] Document BIT tests
7. [ ] Start recruitment for Automation Engineer

---

**Last Updated:** December 8, 2024
