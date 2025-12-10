# Interrogator Confluence Pages - Analysis & Mapping to Automation Priorities

**Created:** December 8, 2024  
**Author:** Roy Avrahami  
**Purpose:** Map existing documentation to automation priorities from meeting

---

## 📚 Confluence Pages Overview

| # | Page | URL | Relevance to Automation |
|---|------|-----|------------------------|
| 1 | **InterrogatorQA - Product level overview** | [Link](https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/2098462722/InterrogatorQA+-+Product+level+overview) | 🔴 Critical - Architecture understanding |
| 2 | **InterrogatorQA Technical level overview** | [Link](https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/2098790423/InterrogatorQA+Technical+level+overview) | 🔴 Critical - Implementation details |
| 3 | **Logs Collector** | [Link](https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/2248114178/Logs+Collector) | 🟡 High - Debugging & verification |
| 4 | **Monitoring architecture** | [Link](https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/2338226184/Monitoring+architecture) | 🟡 High - Health checks & BIT |
| 5 | **Data Analysis Recovery Tools** | [Link](https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/2337177613/Data+Analysis+Recovery+Tools) | 🔴 Critical - Recovery testing |
| 6 | **Start using QA framework - easy start** | [Link](https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/2114355204/Start+using+QA+framework+-+easy+start) | 🔴 Critical - Getting started |

---

## 1. InterrogatorQA - Product Level Overview

### What to Look For:

| Item | Priority | Notes |
|------|----------|-------|
| **System Architecture Diagram** | 🔴 Critical | Understanding all components and their relationships |
| **Data Flow Paths** | 🔴 Critical | Signal → Processing → Alert → Recording flows |
| **Component List** | 🔴 Critical | All 12 core services (Supervisor, Preprocessor, etc.) |
| **Verticals** | 🟡 High | Power, Flow, Eagle, Dove, Shaked definitions |
| **Deployment Types** | 🟡 High | Fort, All-in-One, Cloud, On-Prem |

### Questions to Answer from This Page:

```markdown
□ What are all the data paths in the system?
□ Which components communicate with each other?
□ What is the role of each service?
□ How does data flow from Digitizer to NOC?
□ What are the external integrations (Focus Server, Control Center)?
```

### Mapping to Meeting Priorities:

| Meeting Priority | Information Expected |
|------------------|---------------------|
| **Path Mapping** | System architecture diagrams, data flow descriptions |
| **Path Simulation** | How components connect, what triggers each path |
| **Test Scenarios** | Business flows, use cases |

---

## 2. InterrogatorQA Technical Level Overview

### What to Look For:

| Item | Priority | Notes |
|------|----------|-------|
| **Framework Structure** | 🔴 Critical | `framework/`, `libs/`, `tests/`, `tools/` folders |
| **Test Types** | 🔴 Critical | Smoke, Longterm, Recoverability, Pretest |
| **PF Criteria** | 🟡 High | Pass/Fail criteria YAML files |
| **Configuration** | 🟡 High | How to configure tests for different environments |
| **Fixtures & Utilities** | 🔴 Critical | Reusable test components |

### Questions to Answer from This Page:

```markdown
□ How is the test framework structured?
□ What are the existing test suites and their purposes?
□ How do PF Criteria work?
□ What fixtures are available for testing?
□ How do I add a new test?
```

### Mapping to Meeting Priorities:

| Meeting Priority | Information Expected |
|------------------|---------------------|
| **Test Scenarios** | Existing test structure, what's covered |
| **BIT Testing** | How BIT tests are structured in the framework |
| **Alarms with SVC** | Supervisor interaction patterns |

### Expected Code Structure (Verify):

```
interrogatorqa/
├── framework/
│   ├── orchestrator.py      # Main test orchestration
│   ├── configurator.py      # Configuration management
│   ├── sv_cli.py           # Supervisor CLI interface (SVC!)
│   └── cyclic_checkers/    # Continuous monitoring
├── libs/
│   ├── algo_mock/          # Algorithm simulation
│   ├── control_center_mock/# CC simulation
│   └── alerts_player/      # Alert generation
├── tests/
│   ├── test_smoke.py       # Smoke tests
│   ├── test_longterm.py    # Long-term stability
│   └── test_recoverability.py # Recovery tests
├── pf_criteria/
│   ├── power/              # Power vertical criteria
│   └── flow/               # Flow vertical criteria
└── tools/
    └── analysis/           # Data analysis tools
```

---

## 3. Logs Collector

### What to Look For:

| Item | Priority | Notes |
|------|----------|-------|
| **Log Collection Methods** | 🟡 High | How to gather logs from all services |
| **Log Locations** | 🟡 High | Where each service writes logs |
| **Log Format** | 🟢 Medium | Structure of log entries |
| **Log Analysis Tools** | 🟡 High | Scripts/tools for parsing logs |
| **Centralized Logging** | 🟢 Medium | Aggregation systems (if any) |

### Questions to Answer from This Page:

```markdown
□ How do I collect logs from all Interrogator services?
□ Where are logs stored on the system?
□ How do I parse logs for specific events/errors?
□ What log patterns indicate failures?
□ How to use logs for test verification?
```

### Mapping to Meeting Priorities:

| Meeting Priority | Information Expected |
|------------------|---------------------|
| **Failure Injection & Recovery** | How to verify recovery via logs |
| **BIT Testing** | BIT results in logs |
| **NOC Issue Simulation** | Communication errors in logs |

### Log Verification Checklist (Template):

```python
# Expected log patterns for automation verification

# Service startup
PATTERN_SERVICE_START = r"Service (\w+) started successfully"

# Alert generation
PATTERN_ALERT_CREATED = r"Alert created: type=(\w+), severity=(\w+)"

# Recovery
PATTERN_RECOVERY_START = r"Recovery initiated for service (\w+)"
PATTERN_RECOVERY_COMPLETE = r"Service (\w+) recovered successfully"

# Errors
PATTERN_ERROR = r"ERROR|FATAL|CRITICAL"
PATTERN_CONNECTION_LOST = r"Connection lost to (\w+)"
```

---

## 4. Monitoring Architecture

### What to Look For:

| Item | Priority | Notes |
|------|----------|-------|
| **Monitoring Components** | 🔴 Critical | Telegraf, metrics collection |
| **Health Checks** | 🔴 Critical | What health endpoints exist |
| **Metrics** | 🟡 High | Available metrics for verification |
| **Dashboards** | 🟢 Medium | Visualization tools |
| **Alerting** | 🟡 High | System health alerts |

### Questions to Answer from This Page:

```markdown
□ What monitoring infrastructure exists?
□ How do I check system health programmatically?
□ What metrics are available for automation verification?
□ How do BITs report to monitoring?
□ What triggers system health alerts?
```

### Mapping to Meeting Priorities:

| Meeting Priority | Information Expected |
|------------------|---------------------|
| **BIT Testing** | How BIT integrates with monitoring |
| **BIT-NOC** | Health status reporting to NOC |
| **Failure Injection & Recovery** | Health metrics during failure/recovery |

### Expected Health Endpoints (To Verify):

```python
# Health check endpoints to use in automation

HEALTH_ENDPOINTS = {
    "supervisor": "/api/health/supervisor",
    "preprocessor": "/api/health/preprocessor",
    "bit": "/api/health/bit",
    "rabbitmq": "/api/health/rabbitmq",
    "mongodb": "/api/health/mongodb",
    "storage": "/api/health/storage",
}

# Metrics to monitor
METRICS = {
    "cpu_usage": "telegraf.cpu.usage_percent",
    "memory_usage": "telegraf.mem.used_percent",
    "disk_usage": "telegraf.disk.used_percent",
    "queue_depth": "rabbitmq.queue.messages",
    "alert_rate": "interrogator.alerts.rate",
}
```

---

## 5. Data Analysis Recovery Tools

### What to Look For:

| Item | Priority | Notes |
|------|----------|-------|
| **Recovery Procedures** | 🔴 Critical | How to recover from failures |
| **Recovery Tools** | 🔴 Critical | Scripts/utilities for recovery |
| **Data Analysis** | 🟡 High | Tools for analyzing system data |
| **Failure Scenarios** | 🔴 Critical | Documented failure types and responses |
| **RTO/RPO** | 🔴 Critical | Recovery time/point objectives |

### Questions to Answer from This Page:

```markdown
□ What recovery tools are available?
□ How to trigger recovery procedures?
□ What failure scenarios are documented?
□ What are the expected recovery times (RTO)?
□ What data loss is acceptable (RPO)?
□ How to verify successful recovery?
```

### Mapping to Meeting Priorities:

| Meeting Priority | Information Expected |
|------------------|---------------------|
| **Failure Injection & Recovery** | Recovery tools, procedures, verification |
| **NOC Issue Simulation** | NOC-related recovery procedures |
| **Test Scenarios** | Recovery test scenarios |

### Recovery Testing Framework (Template):

```python
# Recovery test structure

class RecoveryTest:
    """Base class for recovery testing"""
    
    def setup(self):
        """Capture baseline state before failure injection"""
        self.baseline_state = self.capture_system_state()
        self.baseline_metrics = self.capture_metrics()
    
    def inject_failure(self, failure_type: str):
        """Inject specific failure type"""
        # Network disconnect
        # Service crash
        # Storage failure
        # Power loss simulation
        pass
    
    def wait_for_recovery(self, timeout_seconds: int):
        """Wait for system to recover"""
        pass
    
    def verify_recovery(self) -> bool:
        """Verify system recovered correctly"""
        checks = [
            self.verify_all_services_running(),
            self.verify_data_flow_resumed(),
            self.verify_no_data_loss(),
            self.verify_external_connectivity(),
        ]
        return all(checks)
    
    def measure_rto(self) -> float:
        """Measure actual recovery time"""
        pass
```

---

## 6. Start Using QA Framework - Easy Start

### What to Look For:

| Item | Priority | Notes |
|------|----------|-------|
| **Prerequisites** | 🔴 Critical | Python version, dependencies |
| **Setup Instructions** | 🔴 Critical | Environment setup steps |
| **First Test Run** | 🔴 Critical | How to run your first test |
| **Configuration** | 🟡 High | Environment config, credentials |
| **Common Issues** | 🟡 High | Troubleshooting guide |

### Questions to Answer from This Page:

```markdown
□ What are the prerequisites (Python, tools, access)?
□ How do I set up my development environment?
□ How do I run my first test?
□ How do I configure for different environments (lab, staging, prod)?
□ What are common issues and how to solve them?
```

### Mapping to Meeting Priorities:

| Meeting Priority | Information Expected |
|------------------|---------------------|
| **All Priorities** | Foundation for all automation work |
| **Path Simulation** | How to run path tests |
| **BIT Testing** | How to run BIT tests |

### Expected Setup Steps (Template):

```bash
# Environment setup (verify with documentation)

# 1. Clone repository
git clone <nc_pz_repo_url>
cd nc_pz/interrogatorqa

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp config/template.yaml config/local.yaml
# Edit local.yaml with environment-specific settings

# 5. Run first test
pytest tests/test_smoke.py -v

# 6. Run with specific environment
pytest tests/test_smoke.py --env=staging
```

---

## 📊 Priority Matrix - What to Read First

Based on your meeting priorities, here's the recommended reading order:

| Priority | Page | Why |
|----------|------|-----|
| 1️⃣ | **Start using QA framework** | Foundation - need to run existing tests first |
| 2️⃣ | **Product level overview** | Understand system architecture and paths |
| 3️⃣ | **Technical level overview** | Understand framework structure for extension |
| 4️⃣ | **Data Analysis Recovery Tools** | Critical for failure/recovery testing |
| 5️⃣ | **Monitoring architecture** | BIT and health check integration |
| 6️⃣ | **Logs Collector** | Verification and debugging |

---

## 🎯 Information Extraction Checklist

When reading each page, extract and document:

### For Path Mapping & Simulation:

```markdown
□ List all data paths with start → end points
□ Identify triggers for each path
□ Document expected outputs
□ Find existing simulation tools/scripts
□ Note path dependencies
```

### For BIT Testing:

```markdown
□ List all BIT tests (name, purpose, trigger)
□ Document pass/fail criteria for each BIT
□ Find BIT integration with NOC
□ Identify BIT commands (CLI)
□ Note BIT scheduling/triggering methods
```

### For Failure & Recovery:

```markdown
□ List documented failure scenarios
□ Find injection methods for each failure type
□ Document expected recovery behavior
□ Note RTO for each scenario
□ Find verification methods
```

### For Alarms & SVC:

```markdown
□ Document all SVC commands
□ List alarm types and severities
□ Find alarm trigger methods
□ Document alarm flow to Focus Server/NOC
□ Note alarm verification methods
```

### For NOC Simulation:

```markdown
□ Find NOC communication protocols
□ Document NOC failure scenarios
□ Find simulation methods
□ Document expected behavior when NOC is down
□ Note recovery verification for NOC issues
```

---

## 📝 Notes Template for Each Page

Use this template when reading each Confluence page:

```markdown
## Page: [PAGE_NAME]

### Key Information Found:

**Architecture/Components:**
- 

**Paths/Flows:**
- 

**Tools/Commands:**
- 

**Configuration:**
- 

**Relevant to Priorities:**
- [ ] Path Mapping
- [ ] Path Simulation
- [ ] Failure Injection
- [ ] BIT Testing
- [ ] Alarms/SVC
- [ ] NOC Simulation

### Action Items:
1. 
2. 
3. 

### Questions Remaining:
1. 
2. 
3. 

### Code/Commands to Try:
```bash

```
```

---

## 🔗 Related Documentation to Find

Based on the pages above, also look for:

| Document | Purpose |
|----------|---------|
| **nc_pz repository README** | Code structure, setup |
| **Supervisor documentation** | SVC commands reference |
| **BIT specifications** | Full BIT test list |
| **Focus Server integration** | External communication protocols |
| **Control Center integration** | Command flow from NOC |
| **PF Criteria schema** | Pass/fail criteria format |

---

**Next Steps:**
1. Access each Confluence page and fill in the notes template
2. Create detailed documentation for each priority area
3. Schedule deep-dive sessions for gaps in documentation
4. Start with "Easy Start" page to get framework running

