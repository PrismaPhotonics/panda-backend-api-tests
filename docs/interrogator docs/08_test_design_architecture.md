# InterrogatorQA - Test Design Architecture

**Page ID:** 1772322834  
**URL:** https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/1772322834  
**Source:** Inbar (Interrogator Team)  
**Extracted:** December 8, 2024

---

# Test Levels Definition

## 1. UNIT TESTS

**Scope:** Out-Of-Scope for QA team  
**Owner:** Development team  
**Delivery:** DevOps for CI/CD pipeline

---

## 2. COMPONENT TESTS

**Definition:** Test validates communication within single module (microService) treating it as a **Black Box**.

**Approach:**
- Not directly validating communication between classes
- Testing from outside using I/O interfaces
- Mocking outer Services
- Engaging any other module changes this to Integration Test

### Example - Fiber Inspector Component Test:

```
1. Mock PRP chunks for Fiber Inspector
2. On well-prepared data → Fiber Inspector should raise an Alert
3. Alert is dumped on output → Verify interpretation was correct
```

---

## 3. INTEGRATION TESTS

**Definition:** Testing performed to discover defects in the interfaces and interactions between modules or systems.

**In Prisma:** Modules = (micro)Services

### Two Aspects:

| Aspect | Description | Priority |
|--------|-------------|----------|
| **Functional** | Services cooperate correctly, data is consistent | Primary focus |
| **Performance** | Services capable to work with required speed, load | Skip for now |

### 2-Module Integration Test

**Pros:**
- Failed test limits issue search to two modules or particular interface

**Cons:**
- Multiplies number of tests comparing to 3-5 module testing at once
- May require creating mocks if we don't want redundant modules

---

## Basic Integration Test Scenario

```
┌─────────────────────────────────────────────────────────────────┐
│                    2-MODULE INTEGRATION TEST                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Step 1: TRANSMITTER                                             │
│  ┌──────────────┐                                                │
│  │ Player       │──▶ Play PRP Recording / Alert                  │
│  │ Service      │    (or any other source data)                  │
│  └──────────────┘                                                │
│         │                                                        │
│         ▼                                                        │
│  Step 2: RECEIVER                                                │
│  ┌──────────────┐                                                │
│  │ Target       │──▶ Read data and store for                     │
│  │ Service      │    integrity verification                      │
│  └──────────────┘                                                │
│         │                                                        │
│         ▼                                                        │
│  Step 3: VALIDATION                                              │
│  ┌──────────────┐                                                │
│  │ RabbitMQ     │──▶ Check message bindings and queues           │
│  │ Verification │                                                │
│  └──────────────┘                                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Pass/Fail Criteria

### 1. Data Reception
- Receiver should be able to read data and store them (Collector, Recorder)
- OR transmit further (Baby Analyzer, Fiber Inspector)

### 2. Data Consistency
| Check | Requirement |
|-------|-------------|
| File Size | Must be the same |
| Chunks | No missing chunks |
| Pixels | No missing pixels |
| Metadata | May change in allowed way |
| UUID | Should match dir/file name |

### 3. Queue Validation
- Routing Key names meet expectations
- Queue bindings meet expectations for modules and messages

---

# Integration Test Scenarios

## Path 1: PreProcessor Flow

| # | Scenario | Flow | Notes |
|---|----------|------|-------|
| 1 | PRP Recording | PreProcessor → playback digitizer data → Smart Recorder | |
| 2a | Unwrap | PreProcessor → playback digitizer data → Baby Analyzer | Check Power machines |
| 2b | Visualization | PreProcessor → Baby Analyzer → Spectrogram | Compare with tolerance |

## Path 2: Fiber Health

| # | Scenario | Flow | Notes |
|---|----------|------|-------|
| 3 | OTDR Processing | PreProcessor → play OTDR → Fiber Cut Inspector | |
| 4 | Fiber Alerts | Fiber Cut Inspector → cut Alerts → Alerts Queue | Can combine with #3 |

## Path 3: Recording

| # | Scenario | Flow | Notes |
|---|----------|------|-------|
| 5 | PRP Playback | Player → playback PRP → Smart Recorder | Include storage management (NAS) |

## Path 4: Data Engineering

| # | Scenario | Flow | Notes |
|---|----------|------|-------|
| 6 | LifeBoat | Life Boat → read alerts from MongoDB → store on disk | Mock Mongo with desired alerts |

---

# Component Tests (with AlgoMock)

**Note:** These use only one true module/Service, so they are **Component Tests**

| # | Scenario | Flow |
|---|----------|------|
| 7 | HeatMaps Recording | ALGO ML (Algo-Mock) → playback HeatMaps → Smart Recorder |
| 8 | Alert Creation | ALGO ML (Algo-Mock) → create Alert(s) → AlertsQueue (RabbitMQ) |
| 9 | Alert to MongoDB | Alerts Player → Alert → Collector → MongoDB |
| 10 | Alert to MARS | Alerts Player → Alert → Externalizer → MARS (check on Rabbit) |
| 11 | Alert to UI | Alerts Player → Alert → Externalizer → UI (check on Rabbit) |

---

# System Tests (with Supervisor)

**Note:** These use multiple modules with part of system running

## Supervisor Tests

| # | Test | Description | Priority |
|---|------|-------------|----------|
| 1a | Basic | Raise all services, send Keep Alive, messages consumed, graceful shutdown | 🔴 High |
| 1b | Config Variants | Only selected services run (customer real life cases) | 🟡 Medium |
| 1c | Chaos Testing | Kill specific service → Supervisor restarts | 🔴 High |
| 1d | Real Chaos | Random Service kill | 🟢 Later |
| 2 | BIT Test | To Be Specified | 🔴 High |

---

# E2E Tests (Ideas - Placeholder)

| # | Test | Description |
|---|------|-------------|
| 1 | LifeBoat E2E | LifeBoat → store swept data to S3 |
| 2 | Peripherals | Full peripherals flow |

---

# Acceptance Tests (Ideas - Placeholder)

*To be defined based on customer requirements*

---

# Mapping to Automation Priorities

| Priority | Relevant Scenarios |
|----------|-------------------|
| **1. Path Mapping** | Scenarios 1, 2a, 2b, 5 |
| **2. Failure Injection** | Supervisor Tests 1c, 1d |
| **3. BIT Testing** | Supervisor Test 2 |
| **4. Alarms with SVC** | Scenarios 4, 8, 9, 10, 11 |
| **5. NOC Simulation** | Scenarios 10, 11 |
| **6. Fiber Health** | Scenarios 3, 4 |

---

**Document Created:** December 8, 2024
