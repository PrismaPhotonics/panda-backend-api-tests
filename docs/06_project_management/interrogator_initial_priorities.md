# Interrogator Automation - Initial Priorities & Discovery

**Created:** December 8, 2024  
**Author:** Roy Avrahami  
**Status:** Discovery Phase  
**Source:** Initial meeting with Interrogator team

---

## 📋 Summary of Initial Requirements

Based on the meeting, the following areas were identified as **first priorities** for the QA Automation team:

| # | Priority Area | Status | Notes |
|---|---------------|--------|-------|
| 1 | **Path Simulation** | 🔴 To Discover | How to simulate each data path |
| 2 | **Path Mapping** | 🔴 To Discover | Map all paths in the system |
| 3 | **Path Selection Logic** | 🔴 To Discover | Know which paths to run when |
| 4 | **Failure Injection & Recovery** | 🔴 To Discover | Inject failures, verify recovery |
| 5 | **BIT Testing** | 🔴 To Discover | Test Built-In Tests |
| 6 | **Test Scenarios Documentation** | 🔴 To Discover | Document all test scenarios |
| 7 | **BIT-NOC Testing** | 🔴 To Discover | BIT tests for NOC operations |
| 8 | **Alarms with SVC** | 🔴 To Discover | Test alarm flows via Supervisor CLI |
| 9 | **NOC Issue Simulation** | 🔴 To Discover | Simulate NOC-related failures |

---

## 1. Path Simulation & Mapping

### 1.1 What is a "Path"?

**Definition needed:** A "path" in Interrogator context likely refers to:
- Data flow paths (Signal → Processing → Alert → Recording)
- Communication paths between components
- Network paths (Interrogator → Focus Server → NOC)

### 1.2 Discovery Questions

| # | Question | Answer | Source |
|---|----------|--------|--------|
| 1.1 | What are all the data paths in the Interrogator system? | | |
| 1.2 | How is each path currently simulated/tested? | | |
| 1.3 | Are there existing simulation tools/scripts? | | |
| 1.4 | What inputs trigger each path? | | |
| 1.5 | What are the expected outputs for each path? | | |
| 1.6 | Which paths are critical vs. optional? | | |

### 1.3 Expected Path Types (To Verify)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        INTERROGATOR DATA PATHS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  PATH 1: Signal Acquisition                                                  │
│  ┌──────────┐    ┌─────────────┐    ┌──────────────┐                        │
│  │ Digitizer │───▶│ Preprocessor │───▶│ Baby Analyzer │                      │
│  └──────────┘    └─────────────┘    └──────────────┘                        │
│                                                                              │
│  PATH 2: Alert Generation                                                    │
│  ┌──────────────┐    ┌─────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ Baby Analyzer │───▶│ ML Algo │───▶│ Alert Engine │───▶│ Focus Server │    │
│  └──────────────┘    └─────────┘    └─────────────┘    └─────────────┘     │
│                                                                              │
│  PATH 3: Recording                                                           │
│  ┌─────────────┐    ┌───────────────┐    ┌─────────┐                        │
│  │ Preprocessor │───▶│ Smart Recorder │───▶│ Storage │                       │
│  └─────────────┘    └───────────────┘    └─────────┘                        │
│                                                                              │
│  PATH 4: Heatmap Generation                                                  │
│  ┌─────────────┐    ┌───────────────────┐    ┌─────────┐                    │
│  │ Preprocessor │───▶│ Heatmap Recorders │───▶│ Storage │                    │
│  └─────────────┘    └───────────────────┘    └─────────┘                    │
│                                                                              │
│  PATH 5: Fiber Health                                                        │
│  ┌───────────────┐    ┌─────────────┐    ┌─────────────┐                    │
│  │ Optical Unit  │───▶│ OTDR Module │───▶│ Fiber Inspector │                │
│  └───────────────┘    └─────────────┘    └─────────────┘                    │
│                                                                              │
│  PATH 6: NOC Communication                                                   │
│  ┌─────────────┐    ┌─────────────┐    ┌─────┐                              │
│  │ Interrogator │───▶│ Focus Server │───▶│ NOC │                             │
│  └─────────────┘    └─────────────┘    └─────┘                              │
│                                                                              │
│  PATH 7: Control Commands                                                    │
│  ┌─────┐    ┌────────────────┐    ┌─────────────┐    ┌──────────┐          │
│  │ NOC │───▶│ Control Center │───▶│ Interrogator │───▶│ Hardware │           │
│  └─────┘    └────────────────┘    └─────────────┘    └──────────┘          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.4 Path Selection Matrix (Template)

| Path | When to Run | Trigger | Duration | Priority |
|------|-------------|---------|----------|----------|
| Signal Acquisition | Every smoke test | Auto | 5 min | Critical |
| Alert Generation | Pre-release | Manual trigger | 15 min | Critical |
| Recording | Nightly | Scheduled | 30 min | High |
| Heatmap | Weekly | Scheduled | 1 hour | Medium |
| Fiber Health | On demand | Manual | 10 min | Medium |
| NOC Communication | Pre-release | Manual | 20 min | Critical |
| Control Commands | Pre-release | Manual | 15 min | High |

---

## 2. Failure Injection & Recovery Testing

### 2.1 Discovery Questions

| # | Question | Answer | Source |
|---|----------|--------|--------|
| 2.1 | What failure scenarios are currently tested? | | |
| 2.2 | How do you currently inject failures? (tools, scripts) | | |
| 2.3 | What is the expected recovery behavior for each failure? | | |
| 2.4 | What are the RTO (Recovery Time Objectives)? | | |
| 2.5 | What data loss is acceptable during failures? | | |
| 2.6 | How do you verify successful recovery? | | |

### 2.2 Failure Scenarios to Test (Template)

| # | Failure Type | Injection Method | Expected Recovery | RTO | Verification |
|---|--------------|------------------|-------------------|-----|--------------|
| F1 | Network disconnect (Analyzer ↔ Interrogator) | ? | Auto reconnect, resume data | ? | ? |
| F2 | Network disconnect (Interrogator ↔ Focus Server) | ? | Queue alerts, resend on reconnect | ? | ? |
| F3 | Storage/NAS failure | ? | Alert, graceful degradation | ? | ? |
| F4 | Disk full | ? | FIFO rollover, no data loss | ? | ? |
| F5 | Service crash (Supervisor) | ? | Auto restart | ? | ? |
| F6 | Service crash (Preprocessor) | ? | Auto restart, resume processing | ? | ? |
| F7 | Power loss | ? | Full system recovery | ? | ? |
| F8 | MongoDB failure | ? | Failover, no data loss | ? | ? |
| F9 | RabbitMQ failure | ? | Message persistence, recovery | ? | ? |
| F10 | NOC communication failure | ? | Queue commands, retry | ? | ? |

### 2.3 Recovery Verification Checklist (Template)

```
□ All services running (Supervisor status)
□ Data flow resumed (new signals being processed)
□ No data loss (compare pre/post failure counts)
□ Alerts being generated correctly
□ Recordings resuming
□ External communications restored
□ No error logs indicating ongoing issues
□ Performance back to baseline
```

---

## 3. BIT (Built-In Tests) Testing

### 3.1 Discovery Questions

| # | Question | Answer | Source |
|---|----------|--------|--------|
| 3.1 | What are all the BIT tests in Interrogator? | | |
| 3.2 | How are BITs triggered? (auto, manual, scheduled) | | |
| 3.3 | What does each BIT test verify? | | |
| 3.4 | What are the expected results for pass/fail? | | |
| 3.5 | How do BITs integrate with NOC? | | |
| 3.6 | Are there different BIT levels (quick, full, diagnostic)? | | |

### 3.2 BIT Types (To Document)

| BIT ID | Name | Description | Trigger | Pass Criteria | NOC Reporting |
|--------|------|-------------|---------|---------------|---------------|
| BIT-01 | ? | ? | ? | ? | ? |
| BIT-02 | ? | ? | ? | ? | ? |
| BIT-03 | ? | ? | ? | ? | ? |

### 3.3 BIT-NOC Integration

```
Questions to answer:
1. How does BIT status get reported to NOC?
2. What BIT failures trigger NOC alerts?
3. Can NOC trigger BITs remotely?
4. What is the BIT result format sent to NOC?
```

---

## 4. Alarms with SVC (Supervisor CLI)

### 4.1 Discovery Questions

| # | Question | Answer | Source |
|---|----------|--------|--------|
| 4.1 | What is SVC and what commands does it support? | | |
| 4.2 | How do you generate test alarms using SVC? | | |
| 4.3 | What alarm types can be triggered? | | |
| 4.4 | How do you verify alarm delivery to Focus Server/NOC? | | |
| 4.5 | Is there documentation for SVC commands? | | |

### 4.2 SVC Commands for Alarm Testing (Template)

```bash
# Template - fill in with actual commands

# List all available SVC commands
svc --help

# Generate test alarm
svc alarm --type <TYPE> --severity <SEVERITY> --zone <ZONE>

# Check alarm status
svc status --alarms

# Clear test alarms
svc alarm --clear --id <ALARM_ID>

# View alarm queue
svc queue --show

# Force alarm to Focus Server
svc alarm --send --destination focus_server
```

### 4.3 Alarm Types (To Document)

| Alarm Type | Severity Levels | Trigger Method | Expected Destination |
|------------|-----------------|----------------|---------------------|
| Intrusion | Critical/Major/Minor | ? | Focus Server → NOC |
| Vehicle Detection | ? | ? | ? |
| Fiber Cut | ? | ? | ? |
| System Health | ? | ? | ? |
| BIT Failure | ? | ? | ? |

---

## 5. NOC Issue Simulation

### 5.1 Discovery Questions

| # | Question | Answer | Source |
|---|----------|--------|--------|
| 5.1 | What NOC-related issues need to be simulated? | | |
| 5.2 | How do you currently simulate NOC connectivity issues? | | |
| 5.3 | What happens when NOC is unreachable? | | |
| 5.4 | How are commands queued when NOC is down? | | |
| 5.5 | What is the retry logic for NOC communication? | | |

### 5.2 NOC Issue Types (Template)

| Issue Type | Simulation Method | Expected Behavior | Verification |
|------------|-------------------|-------------------|--------------|
| NOC unreachable | Block network port | Queue alerts, retry | Check queue, verify delivery on reconnect |
| NOC slow response | Add latency | Timeout handling | Check timeout logs, verify no data loss |
| NOC rejects commands | Mock NOC with errors | Error handling, retry | Check error handling, alarm to operator |
| NOC overloaded | High volume test | Throttling, backpressure | Check queue management |

---

## 6. Test Scenarios Documentation

### 6.1 Scenario Categories

| Category | Description | Priority | Current Coverage |
|----------|-------------|----------|------------------|
| **Smoke Tests** | Basic functionality verification | Critical | ? |
| **Path Tests** | End-to-end data flow validation | Critical | ? |
| **BIT Tests** | Built-in test execution and validation | High | ? |
| **Alarm Tests** | Alarm generation and delivery | Critical | ? |
| **Recovery Tests** | Failure injection and recovery | High | ? |
| **NOC Integration** | NOC communication scenarios | High | ? |
| **Performance** | Load and stress testing | Medium | ? |

### 6.2 Scenario Template

```markdown
## Scenario: [SCENARIO_NAME]

### Objective
[What this scenario tests]

### Preconditions
- [ ] [Condition 1]
- [ ] [Condition 2]

### Test Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Expected Results
- [ ] [Expected result 1]
- [ ] [Expected result 2]

### Pass/Fail Criteria
- PASS: [Criteria]
- FAIL: [Criteria]

### Automation Status
- [ ] Manual only
- [ ] Automated
- [ ] Partially automated
```

---

## 7. Action Items

### Immediate (This Week)

| # | Action | Owner | Due Date | Status |
|---|--------|-------|----------|--------|
| 1 | Schedule deep-dive session on **Path Mapping** | Roy | | 🔴 |
| 2 | Get SVC documentation/commands reference | Roy | | 🔴 |
| 3 | Get list of all BIT tests | Roy | | 🔴 |
| 4 | Get documentation on failure scenarios tested | Roy | | 🔴 |
| 5 | Get access to NOC simulation environment | Roy | | 🔴 |

### Short-term (2 Weeks)

| # | Action | Owner | Due Date | Status |
|---|--------|-------|----------|--------|
| 6 | Complete Path Mapping document | Roy | | 🔴 |
| 7 | Document all BIT tests with pass/fail criteria | Roy | | 🔴 |
| 8 | Create failure injection test plan | Roy | | 🔴 |
| 9 | Document SVC alarm testing procedures | Roy | | 🔴 |

---

## 8. Resources Needed

### Documentation
- [ ] SVC (Supervisor CLI) command reference
- [ ] BIT test specifications
- [ ] Data path diagrams
- [ ] NOC integration specifications
- [ ] Alarm type definitions

### Access
- [ ] nc_pz repository
- [ ] Test environments
- [ ] NOC simulation tools
- [ ] Monitoring dashboards

### People
- [ ] Interrogator developer for path mapping session
- [ ] BIT expert for BIT testing walkthrough
- [ ] NOC integration expert for NOC simulation

---

## 9. Notes from Meeting

```
[Add notes from the meeting here]




```

---

## 10. Open Questions

| # | Question | Asked To | Answer | Date |
|---|----------|----------|--------|------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

---

**Next Review:** [Date]  
**Next Meeting:** [Date]

