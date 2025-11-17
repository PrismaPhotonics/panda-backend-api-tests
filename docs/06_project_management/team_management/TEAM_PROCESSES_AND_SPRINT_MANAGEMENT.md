# Team Processes and Sprint Management
## Focus Server QA Team

**Created:** 2025-11-04  
**Team Lead:** [Name]  
**Status:** ✅ Active

---

## 📋 Table of Contents

1. [Sprint Structure](#sprint-structure)
2. [Team Responsibilities](#team-responsibilities)
3. [Ticket Creation Process](#ticket-creation-process)
4. [Code Review Process](#code-review-process)
5. [CI/CD Processes](#cicd-processes)
6. [Knowledge Transfer](#knowledge-transfer)
7. [Kubernetes Tests](#kubernetes-tests)
8. [Success Metrics](#success-metrics)

---

## 📅 Sprint Structure

### Weekly Schedule

```
┌─────────────────────────────────────────────────────────────┐
│                    Sprint (2 weeks)                          │
├─────────────────────────────────────────────────────────────┤
│ Monday          │ Create tickets and write tasks             │
│ Tuesday (08:00)  │ Sprint start - Kick-off meeting          │
│ Wednesday-Thursday │ Work on tasks                          │
│ Sunday          │ Week 1 summary                             │
│ Monday (Week 2) │ Review and feedback - Ready for Deploy   │
│ Tuesday (08:00) │ Sprint end - Demo and Retrospective       │
└─────────────────────────────────────────────────────────────┘
```

### Task Creation Process (Monday before Sprint)

**Team Members:**
1. **Sunday evening:** Each team member prepares task list for next sprint
2. **Monday (by 16:00):**
   - ✅ Each team member creates Jira tickets with:
     - Detailed task description
     - Acceptance Criteria
     - Story Points (if applicable)
     - Labels (backend, frontend, infrastructure, etc.)
   - ✅ Tickets ready for Review
3. **Monday (16:00-17:00):** Joint Review meeting
   - Each team member presents their tasks
   - Discussion on priorities
   - Approval or changes to tasks

### Kick-off Meeting (Tuesday 08:00)

**Agenda:**
1. Quick review of sprint tasks
2. Final work distribution
3. Risk and dependency identification
4. Agreement on Definition of Done

---

## 👥 Team Responsibilities

### Tomer - Manual QA

**Responsibilities:**
- ✅ Manual testing of new features
- ✅ Updating Ron on tests that need automation
- ✅ Writing documentation for manual tests
- ✅ Review of client tests

**Workflow with Ron:**
1. Tomer identifies a new test that needs automation
2. Tomer opens a ticket in Jira with `automation-needed` and `frontend` labels
3. Tomer specifies in the ticket:
   - Test name
   - Detailed steps (Step-by-step)
   - Expected results
   - Test scenarios
   - Priority
4. Tomer updates Ron in the ticket (Mention in Jira)
5. Ron reads the ticket and creates an appropriate automation task

### Ron - Frontend & UI Automation

**Responsibilities:**
- ✅ Writing automation for FE/UI tests
- ✅ Completing all FE and Panda UI regression tests
- ✅ Building CI/CD infrastructure
- ✅ Building Jenkins Slave for office automation runs
- ✅ Project and automation documentation

**High Priority Tasks:**

#### 1. Complete Regression Tests
- **Goal:** Complete all FE/UI regression tests
- **Tickets:** Create a ticket for each group of tests to complete
- **Target Date:** [To be determined]
- **Success Criteria:**
  - ✅ All regression tests run successfully
  - ✅ Detailed documentation of all tests
  - ✅ CI/CD integration

#### 2. CI/CD Infrastructure
- **Goal:** Build complete automation infrastructure
- **Components:**
  - ✅ Jenkins Pipeline
  - ✅ Jenkins Slave in office
  - ✅ Integration with Jira/Xray
  - ✅ Automated runs on Pull Requests
- **Tickets:**
  - `PZ-XXXX` - Setup Jenkins Master
  - `PZ-XXXX` - Setup Jenkins Slave (in office)
  - `PZ-XXXX` - CI/CD Pipeline for FE Tests
  - `PZ-XXXX` - Integration with Jira/Xray
  - `PZ-XXXX` - Automated PR Validation

#### 3. Knowledge Transfer
- **Target Date:** [To be determined - before Ron leaves]
- **Process:**
  1. **Meeting 1:** General project overview
     - Architecture
     - File structure
     - Technologies
  2. **Meeting 2:** Practical training
     - How to run the automation
     - How to write new tests
     - How to solve common problems
  3. **Documentation:**
     - Ron will write "How to Run FE Automation" document
     - Ron will write "How to Add New Tests" document
     - Ron will write "Troubleshooting Guide" document
  4. **Handover Checklist:**
     - ✅ All documents written
     - ✅ All code documented
     - ✅ Transferred to QA team
     - ✅ Capability to extend tests

**Workflow with Tomer:**
1. Ron receives update from Tomer on a new test
2. Ron creates a task in Jira:
   - Title: "Automate: [Test Name]"
   - Description: Includes Tomer's steps
   - Labels: `automation`, `frontend`
   - Link to Tomer's original ticket
3. Ron performs:
   - Test analysis
   - Automation writing
   - Execution and validation
   - Update Tomer on completion

### [Name] - Team Lead & Backend Automation

**Responsibilities:**
- ✅ Team and process management
- ✅ Writing automation for Focus Server Backend
- ✅ Creating tickets for BE tests
- ✅ Code and test reviews
- ✅ Adding Kubernetes tests
- ✅ Review of Tomer's client tests

**High Priority Tasks:**

#### 1. BE Test Tickets
- **Process:**
  1. Analysis of Focus Server API
  2. Identification of areas needing coverage
  3. Create a ticket in Jira for each test group:
     - `PZ-XXXX` - API Endpoint Coverage
     - `PZ-XXXX` - Data Validation Tests
     - `PZ-XXXX` - Error Handling Tests
     - `PZ-XXXX` - Performance Tests
     - `PZ-XXXX` - Integration Tests
  4. Work on tickets by priority order

#### 2. Kubernetes Tests
- **Goal:** Add Kubernetes-focused tests to Focus Server BE tests
- **Existing Tests:** `tests/infrastructure/test_k8s_job_lifecycle.py`
- **Tests to Add:**
  - ✅ Pod Health Checks
  - ✅ Resource Limits & Requests Validation
  - ✅ Deployment Strategy Testing
  - ✅ Rolling Update Testing
  - ✅ Service Discovery Testing
  - ✅ ConfigMap & Secrets Testing
  - ✅ Persistent Volume Testing
  - ✅ Network Policies Testing
  - ✅ Autoscaling Testing
  - ✅ Pod Disruption Budget Testing
- **Tickets:**
  - `PZ-XXXX` - K8s Pod Health Monitoring
  - `PZ-XXXX` - K8s Resource Management Tests
  - `PZ-XXXX` - K8s Deployment Strategy Tests
  - `PZ-XXXX` - K8s Service Discovery Tests
  - `PZ-XXXX` - K8s Configuration Management Tests
  - `PZ-XXXX` - K8s Resilience Tests

#### 3. Review of Tomer's Tests
- **Process:**
  1. Tomer submits tests for review
  2. Team Lead reviews tests:
     - Code quality check
     - Coverage check
     - Best Practices check
     - Comments and improvements
  3. Joint meeting to discuss comments
  4. Tomer updates tests
  5. Final approval

---

## 🎫 Ticket Creation Process

### Jira Ticket Template

```
Title: [Type] - [Short description]

Description:
## Goal
[Description of the task goal]

## Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

## Dependencies
- [Link to dependent ticket, if any]

## Notes
[Additional notes]

## Labels
[backend|frontend|infrastructure|automation|manual|bug|feature]

## Story Points
[X]
```

### Ticket Types

1. **Story** - Feature or test group
2. **Task** - Technical task
3. **Bug** - Found bug
4. **Sub-task** - Small task part of larger Story

### Recommended Labels

- `backend` - Backend tasks
- `frontend` - Frontend tasks
- `infrastructure` - Infrastructure
- `automation` - Automation
- `manual` - Manual testing
- `kubernetes` - K8s tests
- `regression` - Regression tests
- `api` - API tests
- `ui` - UI tests

---

## 🔍 Code Review Process

### When Review is Needed?

- ✅ Every Pull Request
- ✅ Every new test
- ✅ Every significant code change
- ✅ CI/CD changes

### Review Process

1. **PR Creator:**
   - Create Pull Request in GitHub/GitLab
   - Detailed description of changes
   - Link to Jira ticket
   - List of main changes

2. **Reviewer:**
   - Code check:
     - ✅ Code quality
     - ✅ Best Practices
     - ✅ Test Coverage
     - ✅ Documentation
   - Write comments:
     - ✅ Positive - what's good
     - ✅ Constructive - what needs improvement
     - ✅ Improvement suggestions

3. **Review Meeting (if needed):**
   - Discussion on complex comments
   - Explanation on design decisions

4. **Approval:**
   - ✅ All comments addressed
   - ✅ Code approved
   - ✅ Merge to main

### Review Checklist

- [ ] Code works (Tests pass)
- [ ] Sufficient Test Coverage
- [ ] Documentation exists
- [ ] Error Handling exists
- [ ] Logging exists
- [ ] Clean Code
- [ ] Follows Best Practices
- [ ] No Hardcoded Values
- [ ] Configuration is correct

---

## 🚀 CI/CD Processes

### Owner: Ron

#### CI/CD Goals

1. **Full Automation:**
   - ✅ Automated run on every PR
   - ✅ Automated run on every Push to main
   - ✅ Daily/nightly full runs

2. **Jenkins Slave in Office:**
   - ✅ Physical setup in office
   - ✅ SSH access
   - ✅ Internal network access
   - ✅ Run tests on internal systems

3. **Integration:**
   - ✅ Jira/Xray - Status updates
   - ✅ GitHub/GitLab - PR updates
   - ✅ Slack/Email - Notifications

#### Jenkins Pipeline Structure

```groovy
pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        
        stage('Backend Tests') {
            steps {
                sh 'pytest tests/backend/ -v --junitxml=results.xml'
            }
        }
        
        stage('Frontend Tests') {
            steps {
                sh 'pytest tests/frontend/ -v --junitxml=results.xml'
            }
        }
        
        stage('Report to Xray') {
            steps {
                sh 'python scripts/report_to_xray.py results.xml'
            }
        }
    }
    
    post {
        always {
            publishTestResults testResultsPattern: 'results.xml'
        }
        success {
            echo 'Tests passed!'
        }
        failure {
            echo 'Tests failed!'
        }
    }
}
```

#### CI/CD Tickets

- `PZ-XXXX` - Setup Jenkins Master
- `PZ-XXXX` - Setup Jenkins Slave (in office)
- `PZ-XXXX` - Backend Tests Pipeline
- `PZ-XXXX` - Frontend Tests Pipeline
- `PZ-XXXX` - Integration with Jira/Xray
- `PZ-XXXX` - Automated PR Validation
- `PZ-XXXX` - Nightly Test Execution
- `PZ-XXXX` - Email/Slack Notifications

---

## 📚 Knowledge Transfer

### Handover Process (before Ron leaves)

#### Meeting 1: General Overview (2-3 hours)

**Content:**
1. **Architecture:**
   - Project structure
   - Technologies (Playwright, pytest, etc.)
   - How everything connects

2. **File Structure:**
   - Where everything is located
   - How to organize new files
   - Best Practices

3. **Setup:**
   - How to run the project locally
   - How to configure environments
   - How to solve Setup problems

**Outcome:** General understanding of the project

#### Meeting 2: Practical Training (2-3 hours)

**Content:**
1. **Running Tests:**
   - How to run specific tests
   - How to run tests by category
   - How to interpret results

2. **Writing New Tests:**
   - Template for new test
   - Best Practices
   - Practical examples

3. **Troubleshooting:**
   - Common problems
   - How to solve
   - Where to find information

**Outcome:** Ability to run and add tests

#### Meeting 3: Q&A and Deep Dive (2-3 hours)

**Content:**
1. Open questions
2. Deep dive into complex areas
3. Practical work on examples

**Outcome:** Confidence in independent work

#### Documentation

**Documents to Create:**

1. **`docs/02_user_guides/HOW_TO_RUN_FE_AUTOMATION.md`**
   - How to run the automation
   - How to configure environments
   - How to run specific tests

2. **`docs/02_user_guides/HOW_TO_ADD_NEW_FE_TESTS.md`**
   - Template for new test
   - Best Practices
   - Examples

3. **`docs/02_user_guides/FE_AUTOMATION_TROUBLESHOOTING.md`**
   - Common problems
   - Solutions
   - Resources

4. **`docs/03_architecture/FE_AUTOMATION_ARCHITECTURE.md`**
   - Detailed architecture
   - Flow diagram
   - Explanation of each component

#### Handover Checklist

- [ ] Meeting 1 completed
- [ ] Meeting 2 completed
- [ ] Meeting 3 completed
- [ ] All documents written
- [ ] All code documented
- [ ] Transferred to QA team
- [ ] Capability to extend tests
- [ ] Capability to solve common problems
- [ ] Capability to run automation fully

---

## ☸️ Kubernetes Tests

### Goal: Add Kubernetes-focused tests to Focus Server BE tests

### Existing Tests

**Location:** `tests/infrastructure/test_k8s_job_lifecycle.py`

**Current Coverage:**
- ✅ Job Creation → Pod Spawn
- ✅ Resource Allocation (CPU/Memory)
- ✅ Port Exposure and Service Discovery
- ✅ Job Cancellation and Cleanup
- ✅ Observability (Logs, Events, Metrics)

### Tests to Add

#### 1. Pod Health Checks
**Ticket:** `PZ-XXXX` - K8s Pod Health Monitoring

**Tests:**
- Pod liveness probe
- Pod readiness probe
- Pod startup probe
- Pod restart policy
- Pod health after failures

**Location:** `tests/infrastructure/test_k8s_pod_health.py`

#### 2. Resource Management
**Ticket:** `PZ-XXXX` - K8s Resource Management Tests

**Tests:**
- CPU requests/limits validation
- Memory requests/limits validation
- Resource quotas
- Resource constraints
- OOMKilled scenarios

**Location:** `tests/infrastructure/test_k8s_resources.py`

#### 3. Deployment Strategy
**Ticket:** `PZ-XXXX` - K8s Deployment Strategy Tests

**Tests:**
- Rolling update strategy
- Blue-Green deployment
- Canary deployment
- Rollback functionality
- Deployment health during updates

**Location:** `tests/infrastructure/test_k8s_deployment.py`

#### 4. Service Discovery
**Ticket:** `PZ-XXXX` - K8s Service Discovery Tests

**Tests:**
- Service creation and exposure
- Endpoint resolution
- Service-to-Pod communication
- DNS resolution
- Load balancing

**Location:** `tests/infrastructure/test_k8s_service_discovery.py`

#### 5. Configuration Management
**Ticket:** `PZ-XXXX` - K8s Configuration Management Tests

**Tests:**
- ConfigMap creation and usage
- Secrets management
- Environment variables injection
- Configuration updates
- Configuration rollback

**Location:** `tests/infrastructure/test_k8s_config.py`

#### 6. Resilience Tests
**Ticket:** `PZ-XXXX` - K8s Resilience Tests

**Tests:**
- Pod disruption budget
- Node failure handling
- Network partition handling
- Storage failure handling
- Auto-scaling behavior

**Location:** `tests/infrastructure/test_k8s_resilience.py`

### Template for New K8s Test

```python
"""
Integration Tests - Kubernetes [Feature Name]
=============================================

Test Coverage:
    1. [Test 1]
    2. [Test 2]
    3. [Test 3]

Author: QA Automation Architect
Date: [Date]
Related: [Jira Ticket]
"""

import pytest
from src.infrastructure.kubernetes_manager import KubernetesManager


@pytest.mark.kubernetes
@pytest.mark.infrastructure
class TestK8s[FeatureName]:
    """Test Kubernetes [feature] functionality."""
    
    def test_k8s_[feature]_[scenario](self, k8s_manager):
        """
        Test that [scenario] works correctly.
        
        Steps:
        1. [Step 1]
        2. [Step 2]
        3. [Step 3]
        
        Expected:
        - [Expected result 1]
        - [Expected result 2]
        """
        # Test implementation
        pass
```

### Priority Order for Addition

1. **High Priority:**
   - Pod Health Checks
   - Resource Management
   - Resilience Tests

2. **Medium Priority:**
   - Deployment Strategy
   - Service Discovery

3. **Low Priority:**
   - Configuration Management

---

## 📊 Success Metrics

### Sprint Metrics

- ✅ **Velocity:** [X] Story Points per sprint
- ✅ **Completion Rate:** [X]% of tasks completed
- ✅ **Code Quality:** 0 Critical Issues
- ✅ **Test Coverage:** [X]% coverage
- ✅ **Bug Rate:** [X] bugs per sprint

### Team Metrics

- ✅ **Tomer:**
  - [X] Manual tests performed
  - [X] Documentation written
  - [X] Tests transferred to automation

- ✅ **Ron:**
  - [X] Regression tests completed
  - [X] CI/CD Pipeline active
  - [X] Jenkins Slave active
  - [X] Documentation written

- ✅ **[Name]:**
  - [X] BE tickets created
  - [X] K8s tests added
  - [X] Test reviews performed

---

## 📝 Related Documents

- [Jira Integration Guide](../jira/XRAY_IMPORT_GUIDE.md)
- [Test Results](../../04_testing/test_results/)
- [Infrastructure Tests](../../07_infrastructure/)
- [Backend Improvement Program](../programs/backend_improvement_program/)

---

**Last Updated:** 2025-11-04  
**Owner:** QA Team Lead

