# InterrogatorQA - Additional Confluence Documentation

**Extracted:** December 8, 2024  
**Source:** Confluence - PRISMATEAM Space  
**Purpose:** Critical reference for BIT, Fiber Inspector, E2E Testing, and System Architecture

---

# 📚 Table of Contents

1. [BIT Tests Table - Complete Reference](#1-bit-tests-table---complete-reference)
2. [BIT Feature Design](#2-bit-feature-design)
3. [Independent Components BIT Redesign](#3-independent-components-bit-redesign)
4. [BIT Troubleshooting](#4-bit-troubleshooting)
5. [E2E End-to-End Functional Testing](#5-e2e-end-to-end-functional-testing)
6. [Fiber Inspector Design](#6-fiber-inspector-design)
7. [Interrogator Logs Collection](#7-interrogator-logs-collection)
8. [QA Testing Roadmap (6-Month Plan)](#8-qa-testing-roadmap-6-month-plan)
9. [Interrogator QA - Macro & Micro Analysis](#9-interrogator-qa---macro--micro-analysis)

---

# 1. BIT Tests Table - Complete Reference

**Page ID:** 840466458  
**URL:** https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/840466458

## Complete BIT Tests Reference

| Component | Error Code | Suite Name | Test Name | Meaning | Issue | Severity |
|-----------|------------|------------|-----------|---------|-------|----------|
| analyzer | 401 | externalizer | status_consumed_by_ui | Test if BIT status output queue to the UI is filling - UI not reading or too slow | UI BIT | medium |
| analyzer | 401 | externalizer | ui_backend_consumes_status | Test if UI is registered as consumer to read BIT output | UI BIT | medium |
| analyzer | 401 | heartbeats | control_center_grafana_available | Check if Control Center Grafana HTTP server is reachable | | medium |
| analyzer | 401 | heartbeats | control_center_rabbit_available | Check if Control Center Rabbit server is reachable | CC connection | medium |
| analyzer | 401 | matrix | collector_consumes | Test if collector is registered as consumer to read alerts from rabbit | mongo validity | medium |
| analyzer | 401 | matrix | gpu_mem_utilization | Check minimal GPU memory usage is reached | Algo not working | medium |
| analyzer | 401 | matrix | gpu_utilization | Check minimal GPU usage is reached | Algo not working | medium |
| analyzer | 401 | matrix | matrix_queue | Test if Algo(matrix) input queue is filling - Algo stuck or slow | Algo not working | **high** |
| analyzer | 401 | services | heartbeats | Tests if service is up for at least 5 mins | | medium |
| analyzer | 502 | collector | data_received_by_collector | Test if Collector input queue has any traffic | mongo validity | medium |
| analyzer | 502 | matrix | data_received_by_matrix | Test if Algo(matrix) input queue has any traffic | preprocessor/ML issue | **high** |
| analyzer | 504 | collector | mongo_does_not_fail_update_commands | Tests if there are errors writing to mongo | mongo corruption | medium |
| analyzer | 504 | externalizer | alerts_consumed_by_ui | Test if externalizer alert output queue to UI is filling | UI alerts not showing | **high** |
| analyzer | 504 | externalizer | ui_backend_consumes_alerts | Test if UI is registered as consumer to read externalizer output | UI alerts not showing | **high** |
| analyzer | 504 | matrix | externalizer_consumes | Test if externalizer is registered as consumer to read alerts from Algo | alerts not showing | **high** |
| analyzer | 504 | services | collector | Tests if service is up for at least 5 mins | collector not stable | medium |
| analyzer | 504 | services | externalizer | Tests if service is up for at least 5 mins | externalizer not stable | **high** |
| analyzer | 504 | services | heatmaps_recorder_<name> | Tests if service is up for at least 5 mins | recorder not stable | medium-high |
| analyzer | 504 | services | keepalive_consumed | Tests if supervisor is consuming keepalives | supervisor issue | medium-very high |
| analyzer | 504 | services | matrix | Tests if service is up for at least 5 mins | algo not stable | **high** |
| **interrogator** | 401 | *_recorder | *_recorder_input_rate | Test if recorder input rate is not 0 | recording data loss | medium |
| **interrogator** | 401 | *_recorder | *_recorder_queue_filling | Test if recorder input queue is filling - recorder stuck | recording data loss | medium |
| **interrogator** | 401 | services | *_recorder | Tests if service is up for at least 5 mins | recorder not stable | medium |
| **interrogator** | 401 | services | heartbeats | Tests if service is up for at least 5 mins | heartbeat not stable | low |
| **interrogator** | 501 | fiber_inspect | fiber_cut | Is fiber cut detected now | | medium-high |
| **interrogator** | 504 | services | peripherals | Tests if service is up for at least 5 mins | | **high** |
| **interrogator** | 504 | services | preprocessor | Tests if service is up for at least 5 mins | | **high** |
| **interrogator** | 504 | services | unwrap_baby | Tests if service is up for at least 5 mins | | **high** |

---

# 2. BIT Feature Design

**Page ID:** 639041541  
**URL:** https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/639041541

## Goals

The purpose of BIT is to:
1. Know that the system works as expected
2. Show status to the customer
3. Gather statistics about system state

## Error Catalog

| ID# | Error | Type | Meaning | Customer Action |
|-----|-------|------|---------|-----------------|
| 200 | OK | OK | All is in order | Enjoy the system |
| 501 | Fiber cut | warning | Fiber integrity compromised, coverage partial | Notify Prisma, coordinate fix |
| 502 | Machine offline/down | Fatal | Machine off or disconnected | Check power/network |
| 401 | Malfunction, operator action needed | caution | Malfunction detected, may be resolved with operator action | Perform requested action |
| 504 | Fatal Software malfunction | Fatal | Unrecoverable software error | Contact Prisma ASAP |
| 505 | Fatal Hardware malfunction | Fatal | Unrecoverable hardware error | Contact Prisma ASAP |
| 306 | Machine unstable | caution | Machine working partially (frequently restarting) | Contact Prisma ASAP |
| 301 | System self-healing | caution | Detection may be temporarily off, system is self healing | Track status |
| 401 | Machine in danger | caution | System OK but machine requires maintenance | Contact Prisma in working hours |
| 402 | Operator action recommended | caution | System OK but may degrade | Perform recommended action |

## BIT Architecture

1. On each machine, for each process in supervisor → BIT script runs subset of tests
2. Each machine forwards test results via telegraf and rabbit
3. Analyzer receives all test results, builds BIT status
4. Reports to web server and MARS according to predefined codes
5. Control Center pulls full state from analyzer

## BIT Tests Tree Structure

### NAS Tests
- Has SMB access
- Files readable
- Files writeable
- Storage capacity level

### Interrogator Tests
- **Fiber State Tests**: SNR test, Fiber cut detection, Optical components status
- **Supervisor Services**: Process states, Rabbit alive check
- **Data Forwarding**: Preprocessor sending data, Queue consumption
- **Status Forwarding**: Telegraf metrics received by analyzer

### Analyzer Tests
- **Data Received**: From interrogator, Rabbit performance
- **Algo**: Data consumed by algo, GPU usage within expected values
- **Services**: MongoDB check, Rabbit check
- **Externalizer**: MARS reachable, Webserver consumes alerts
- **Control Server**: Prometheus aggregated status, Rabbit heartbeat

---

# 3. Independent Components BIT Redesign

**Page ID:** 889782273  
**URL:** https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/889782273

## Key Changes

1. **BIT test** stays the same - service sends `bit stats` including `bit_count`
2. **BIT status** creates component status for each component on machine
3. **Removed error codes from component status** - only stay with suites for error codes
4. **System BIT** runs on analyzer machine:
   - Collects all `bit_count` metrics from Prometheus client
   - Collects all BIT tests from Prometheus client
   - Checks if total `bit_count` == number of BITs found
   - Checks all BITs passed, takes error codes of failed ones
   - Sends system status through rabbit to telegraf

## Component Trees

Each level only knows subcomponents of that level and error code for each missing subcomponent.

- **System Status** → knows analyzer and interrogator components
- **Component Status** → knows list of suite tests
- **Suite Tests** → knows individual tests

---

# 4. BIT Troubleshooting

**Page ID:** 714080322  
**URL:** https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/714080322

## BIT Troubleshooting in Control Center

**Available Graphs:**
1. **BIT error codes** - Shows error code of each logical component at that time
2. **Component BIT state** - Shows BIT result of each logical component
3. **Bit Tests - <component name>** - Shows BIT result of each test run

**Troubleshooting Steps:**
1. Look at a time you are interested in
2. See the error code as expected
3. Look at states of the components
4. Look at the bit tests graph of each component to see which test failed

**Note:** For fort systems, look at several views to have full picture. Analyzer gives best initial view.

---

# 5. E2E End-to-End Functional Testing

**Page ID:** 908230665  
**URL:** https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/908230665

## Scope

End-to-end functional testing for each vertical on predefined sites.

## Assumptions

1. Individual services functionality is validated
2. Integration Tests have passed successfully

## Expected Defects

1. Service crashes
2. Queues Overflow
3. Lost Frames
4. Recordings Corruptions (Waterfall, Heatmap)
5. Configuration problems
6. Upgrade or roll-back failures

## Environment

Real HW Lab Machine. At least one per vertical.

## Test Scenario

1. Execute for each vertical on predefined site configuration
2. Install new software version configured for specific customer site
3. Configure algorithms to generate dummy alerts periodically
4. Run pipeline for few minutes (enough for PRP, heatmaps, and alerts)

## Pass/Fail Criteria

1. **PRP and Heatmaps recordings created correctly**
   - All data that should be recorded exists
   - No time jumps (no missing frames)
   - No data corruptions
2. **Dummy Alert reaches MongoDB and UI correctly**
3. **All BIT Tests are good**

---

# 6. Fiber Inspector Design

**Page ID:** 877494299  
**URL:** https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/877494299

## Goals

Raise alert in case of detecting:
- **Fiber cut**
- **Layout change**
- **Visibility Change** - location from which there is not enough light for algo
- **Dark** - No reflections at all

## Event Types

| Event | Description |
|-------|-------------|
| **Fiber Cut** | Current last visibility DoF smaller than baseline AND new major loss close to this DoF |
| **Fiber Change** | Difference between current DB record and baseline record |
| **Fiber Visibility** | Location with reflections under algo minimum power changes from baseline |
| **Fiber Disconnect** | Visibility under 1km of fiber length |

**Hierarchy:** No Baseline > Disconnect > Change > Cut > Visibility

## BIT Integration

10 possible BIT codes:
- For each event type: code if active (caution) and code if detected but not dismissed (warning)

## Configuration Parameters

| Parameter | Units | Default | Meaning |
|-----------|-------|---------|---------|
| window_size | pixels | 80 | Spatial sliding window size |
| min_fiber_length | windows | 3 | |
| min_optical_signal | dB | 27 | |
| min_algo_signal | dB | 31 | |
| min_major_loss | dB | 4.5 | |
| max_internal_alerts | int | 8 | |
| max_internal_baselines | int | 8 | |

---

# 7. Interrogator Logs Collection

**Page ID:** 832405524  
**URL:** https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/832405524

## Collection Steps

### 1. Config Snapshot
```batch
set "TS=%DATE:/=-%%TIME::=-%" & robocopy "%prisma_config%" "%prisma_logs%\config_backup%TS%" /E /XF ".pt" ".pkl" ".ckpt" ".mat" ".f32" ".bin" "*.exe"
```

### 2. System Environment Variables
```batch
set > env.txt
```

### 3. Event Viewer
```powershell
Copy-Item "$env:SystemRoot\System32\winevt\Logs\*.evtx" -Destination "C:\prisma\Logs\" -Recurse
```

### 4. MongoDB Export
Using MongoDB Compass: Export each collection to JSON/CSV

### 5. Networking Info
```batch
cd %prisma_logs%
ipconfig > %computername%_ipconfig.txt
ipconfig /all > %computername%_ipconfig_all.txt
copy c:\Windows\System32\drivers\etc\hosts %computername%_hosts
netsh interface show interface > interfaces.txt
netsh interface ip dump > net-config.txt
netsh interface ipv4 show addresses > ipv4_addresses.txt
route print > routes.txt
arp -a > arp.txt
netstat -ano > netstat_all.txt
```

## Log Files Reference

| Log File | Description |
|----------|-------------|
| `supervisor.log` | Supervisor log, holds exit codes - **very important** |
| `rabbit.log` | RabbitMQ log |
| `telegraf.log` | Telegraf log |
| `mongod.log` | MongoDB log |
| `peripherals.log` | Peripherals log |
| `externalizer.log` | Externalizer log |
| `collector.log` | Collector log |
| `prp_recorder.log` | Smart recorder (PRP) log |
| `heatmaps_recorder_<ChannelName>.log` | Heatmap recorder logs |
| `preprocessor.log` | Preprocessor log |
| `pz.bit_<test/status>.log` | BIT test logs |
| `MatrixMS.<version>.log` | Algo logs - **very important** |

---

# 8. QA Testing Roadmap (6-Month Plan)

**Page ID:** 2362310668  
**URL:** https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/2362310668

## 6-Month Timeline Overview

```
 Month 1    Month 2   Month 3   Month 4   Month 5   Month 6
┌──────────┬──────────┬─────────┬──────────┬──────────┬──────────┐
│ MEMORY  │ HW &    │ API &   │  CHAOS  │  CI/CD  │ STABLE  │
│ + LONG  │ PERF    │ DATA    │  ENG    │         │ + DOCS  │
└──────────┴──────────┴─────────┴──────────┴──────────┴──────────┘
```

## Epic Breakdown

### EPIC 1: 48h Stability Test & Foundation (Month 1) - 300h
- **Story 1.1:** Memory Stability Monitoring (50h) - 8/24/48/72-hour monitoring
- **Story 1.2:** Long-term Storage Management (60h) - PRP recording validation
- **Story 1.3:** Long-term Stability (80h) - 48-72 hour continuous operation
- **Story 1.4:** Architecture Flexibility Assessment (110h) - Multi-vertical support

### EPIC 2: Hardware & Performance Testing (Month 2) - 520h
- **Story 2.1:** Hardware Integration (150h) - Physical fiber optic testing
- **Story 2.2:** Processing Latency Baseline (120h) - End-to-end processing time
- **Story 2.3:** Throughput Capacity (160h) - Maximum sustainable rate
- **Story 2.4:** Critical Modules Assessment (90h) - Module prioritization

### EPIC 3: API Compatibility & Data Quality (Month 3-4) - 400h
- **Story 3.1:** API Compatibility Testing (80h)
- **Story 3.2:** Service Communication (50h) - Distributed system testing
- **Story 3.3:** Integration Testing - Transient States (70h)
- **Story 3.4:** Data Engineering Events & LifeBoat (80h)
- **Story 3.5:** Collector Module Extension (30h)
- **Story 3.6:** Externalizer Module Extension (30h)
- **Story 3.7:** FiberCut Module Testing (30h)
- **Story 3.8:** LifeBoat Data Collection (30h)

### EPIC 4: Chaos Engineering (Month 4) - 300h
- **Story 4.1:** Infrastructure Failures (180h) - Disk exhaustion, network interruption
- **Story 4.2:** Load Boundaries (120h) - Performance degradation identification

### EPIC 5: Configuration & CI/CD (Month 5) - 180h
- **Story 5.1:** AutoConfig Testing (180h) - Configuration management testing

### EPIC 6: Stability & Documentation (Month 6) - 280h
- **Story 6.1:** System Stability Validation (180h) - E2E path verification
- **Story 6.2:** Documentation (100h) - Framework documentation

## Total Effort: 1,980h

---

# 9. Interrogator QA - Macro & Micro Analysis

**Page ID:** 2349170691  
**URL:** https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/2349170691

## MACRO VIEW: Prisma Edge System Components

| Component | Role | Description |
|-----------|------|-------------|
| **Optical Unit (Beacon)** | Fiber Interface | Connects system to fiber (laser, embedded hardware) |
| **Interrogator** | Signal Processing | Pre-Processor, Signal Generator, Digitizer |
| **Analyzer** | Intelligence | Algorithms, alerts, heatmaps, ML processing |
| **NAS/Storage** | Data Storage | Holds all recorded system data |
| **UI Host** | User Interface | Control Centre, Panda UI, Grafana, Prometheus |

## System Deployment Types

| Setup | Configuration | Use Case |
|-------|---------------|----------|
| **Fort** | Interrogator + Analyzer + NAS + UIHost (4 machines) | Eagle, Dove perimeter security |
| **All-In-One** | Single machine with both roles | Power, Flow, Shaked verticals |
| **Cloud/Online** | Remote access enabled | Standard deployment |
| **On-Prem** | No remote access | Secure installations |

## Core Interrogator Services

| Service | Purpose | Queue/Integration |
|---------|---------|-------------------|
| **Preprocessor** | Signal processing | Sends to ml_algo, smart_recorder, baby_analyzer |
| **Peripherals** | Hardware interface | Controls optical unit, digitizer |
| **Smart Recorder** | PRP data recording | Writes to NAS/storage |
| **Heatmap Recorders** | Heatmap data storage | Multiple types |
| **Baby Analyzer** | Decimation & unwrap | Intermediate signal processing |
| **Fiber Inspector** | Fiber health monitoring | OTDRX, OTDRY channels |
| **Data Manager** | Disk management | FIFO rollover, storage protection |
| **BIT** | System health | Status and test monitoring |
| **Telegraf** | Metrics collection | Sends to analyzer via RabbitMQ |

## Key RabbitMQ Queues

| Queue | Type | Source → Destination |
|-------|------|---------------------|
| `Algo_ml` | Service | preprocessor → ml_algo |
| `baby` | Service | preprocessor → baby_analyzer |
| `smart_recorder` | Limited Recovery | preprocessor → smart_recorder |
| `smart_recorder.heatMaps` | Machine Failure Recovery | preprocessor → heatmap recorders |
| `prisma-metrics` | Durable | BIT → telegraf |
| `prisma-metrics-forward` | Durable | interrogator-telegraf → analyzer-telegraf |
| `fiber_inspector.OTDRX/Y` | Service | preprocessor → fiber_inspector |

## InterrogatorQA Test Suites

| Suite | Duration | Purpose | When to Use |
|-------|----------|---------|-------------|
| **Smoke** | ~10-15 min | Quick validation | CI pre-merge |
| **Long-term** | Hours | Sustained behavior | Before release |
| **Reliability** | Medium | Service restart validation | Infrastructure changes |
| **Recoverability** | Varies | Crash detection | Stability investigations |
| **Pre-test** | Short | Environment validation | Initial setup |

## Cyclic Checkers

- Services Checker - Validates service states
- Queues Checker - Monitors RabbitMQ queue health
- Heartbeats Checker - Validates heartbeat messages
- Keep-Alive Checker - Validates keep-alive messages
- Critical Messages Checker - Validates critical message flow
- PRP Checker - Validates PRP messages
- Crash Monitor - Monitors for process crashes

## Key Tools & Resources

| Tool | Location | Purpose |
|------|----------|---------|
| **InterrogatorQA** | `interrogatorqa/` | Interrogator/Analyzer testing |
| **Logs Collector** | `interrogatorqa/tools/` | Log filtering by timestamp |
| **Preprocessor Tools** | `interrogatorqa/standalone/` | Performance & stability analysis |
| **AlgoMock** | `interrogatorqa/libs/algo_mock/` | Algorithm simulation |
| **Control Center Mock** | `interrogatorqa/libs/control_center_mock/` | CC simulation |
| **Alerts Player** | `interrogatorqa/libs/alerts_player/` | Alert playback |

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Test Files | 130+ | 150+ |
| Test Cases | 480+ | 500+ |
| Xray Integration | ~70% | 100% |
| CI/CD Integration | ~25% | 100% |
| Test Execution Time | ~60 min | <30 min |
| Test Reliability | ~85% pass | 95% pass |

---

**Document Created:** December 8, 2024  
**Last Updated:** December 8, 2024
