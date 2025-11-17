# Focus Server QA Team - Processes & Workflows

**Team Lead:** Roy Avrahami  
**Created:** 2025-11-04  
**Last Updated:** 2025-11-05  
**Status:** ✅ Active  
**Version:** 1.1

---

## 📋 Objective

This document defines the **processes** and **workflows** for the Focus Server QA Team. It outlines how the team operates day-to-day, including sprint structure, ticket creation, code review, automation status tracking, and other operational processes.

---

## 📅 Sprint Structure

### Sprint Duration
- **Length:** 2 weeks
- **Kick-off:** Tuesday 08:00
- **Demo & Retrospective:** Tuesday 08:00 (end of sprint)

### Weekly Schedule

```
┌─────────────────────────────────────────────────────────────┐
│                    Sprint (2 weeks)                          │
├─────────────────────────────────────────────────────────────┤
│ Monday          │ Create tickets and write tasks             │
│ Tuesday (08:00) │ Sprint start - Kick-off meeting            │
│ Wednesday-Thursday │ Work on tasks                          │
│ Sunday          │ Week 1 summary                             │
│ Monday (Week 2) │ Review and feedback - Ready for Deploy     │
│ Tuesday (08:00) │ Sprint end - Demo and Retrospective       │
└─────────────────────────────────────────────────────────────┘
```

### Sprint Events

#### 1. Task Creation (Monday before Sprint)

**Participants:** All team members  
**Time:** Sunday evening (preparation), Monday by 16:00 (ticket creation)

**Process:**
1. **Sunday evening:** Each team member prepares task list for next sprint
2. **Monday (by 16:00):** Each team member creates Jira tickets with:
   - ✅ Detailed task description
   - ✅ Acceptance Criteria
   - ✅ Story Points (if applicable)
   - ✅ Labels (backend, frontend, infrastructure, etc.)
   - ✅ Automation labels (Automated, For_Automation) - if applicable
3. **Monday (16:00-17:00):** Joint Review meeting
   - Each team member presents their tasks
   - Discussion on priorities
   - Approval or changes to tasks

**Deliverables:**
- All sprint tickets created
- Tickets reviewed and approved
- Sprint backlog ready

---

#### 2. Sprint Kick-off (Tuesday 08:00)

**Participants:** All team members  
**Duration:** 30-45 minutes

**Agenda:**
1. Quick review of sprint tasks
2. Final work distribution
3. Risk and dependency identification
4. Agreement on Definition of Done
5. Q&A

**Deliverables:**
- Sprint plan confirmed
- Work distribution agreed
- Risks identified
- DoD agreed upon

---

#### 3. Week 1 Summary (Sunday)

**Participants:** Team Lead  
**Duration:** Individual preparation

**Content:**
- Progress update
- Blockers identification
- Adjustments needed

**Deliverables:**
- Week 1 summary report
- Blocker list (if any)
- Adjustment recommendations

---

#### 4. Review and Feedback (Monday Week 2)

**Participants:** All team members  
**Duration:** As needed

**Content:**
- Code review status
- Test execution status
- Deployment readiness
- Feedback on completed work

**Deliverables:**
- Review feedback
- Deployment readiness assessment
- Final adjustments

---

#### 5. Demo & Retrospective (Tuesday 08:00)

**Participants:** All team members  
**Duration:** 60-90 minutes

**Demo Agenda:**
1. Show completed work
2. Demonstrate new features/tests
3. Share metrics and results

**Retrospective Agenda:**
1. What went well?
2. What could be improved?
3. Action items for next sprint

**Deliverables:**
- Demo presentation
- Retrospective notes
- Action items list
- Sprint summary

---

## 🎫 Ticket Creation Process

### Ticket Creation Workflow

```
1. Team member prepares task list (Sunday evening)
   ↓
2. Team member creates Jira ticket (Monday by 16:00)
   ↓
3. Ticket includes: Description, Acceptance Criteria, Labels, Story Points
   ↓
4. Joint Review meeting (Monday 16:00-17:00)
   ↓
5. Ticket approved or modified
   ↓
6. Ticket ready for sprint
```

### Jira Ticket Template

**Title:** `[Type] - [Short description]`

**Description:**

```markdown
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
```

### Ticket Types

| Type | Usage | Example |
|------|-------|---------|
| **Story** | Feature or test group | "Automate API Endpoint Coverage" |
| **Task** | Technical task | "Setup Jenkins Slave" |
| **Bug** | Found bug | "PZ-13986: 200 Jobs Capacity Issue" |
| **Sub-task** | Small task part of larger Story | "Add health check test" |

### Recommended Labels

**Component Labels:**
- `backend` - Backend tasks
- `frontend` - Frontend tasks
- `infrastructure` - Infrastructure tasks

**Type Labels:**
- `automation` - Automation tasks
- `manual` - Manual testing tasks
- `bug` - Bug tickets
- `feature` - Feature tickets

**Technology Labels:**
- `kubernetes` - K8s tests
- `regression` - Regression tests
- `api` - API tests
- `ui` - UI tests

**Automation Status Labels:**
- `Automated` - Test has automation code implemented
- `For_Automation` - Test marked for automation but not yet implemented

### Story Points

Use Fibonacci sequence: 1, 2, 3, 5, 8, 13

**Guidelines:**
- **1-2 points:** Small tasks (few hours)
- **3-5 points:** Medium tasks (1-2 days)
- **8 points:** Large tasks (3-5 days)
- **13 points:** Very large tasks (1 week+) - consider breaking down

---

## 🏷️ Automation Status Tracking

### Automation Labels

**Status:** ✅ **Active** (Updated: 2025-11-05)

**Labels Added:**
- **`Automated`** - Applied to tests that have:
  - ✅ Xray/Jira markers in automation code
  - ✅ Actual test functions implemented
  - **Count:** 226 tests (as of 2025-11-05)

- **`For_Automation`** - Applied to tests that have:
  - ✅ Xray/Jira markers in automation code
  - ❌ No test function yet (markers only)
  - **Count:** 1 test (PZ-13879)

**Statistics (as of 2025-11-05):**
- **Total Tests Updated:** 227 tests
- **From CSV Files:** 151 tests updated
- **From Jira Test Repository:** 76 tests updated
- **Total Markers in Code:** 162 unique test IDs
- **Markers with Test Functions:** 160 (98.8%)
- **Markers without Test Functions:** 2 (1.2%)

### Automation Status Workflow

**Process:**
1. **Developer/QA writes automation code** with Xray/Jira markers
   - Example: `@pytest.mark.xray("PZ-12345")`
   - Example: `@pytest.mark.jira("PZ-12345")`

2. **Scripts scan automation code** for markers
   - `scripts/jira/add_automation_labels.py` - Scans all Python test files
   - `scripts/jira/add_labels_from_csv.py` - Scans CSV test files

3. **Scripts identify test functions:**
   - If marker has corresponding `def test_` function → `Automated` label
   - If marker exists but no test function → `For_Automation` label

4. **Scripts update Jira tests** with appropriate labels
   - Preserves existing labels
   - Adds new automation labels

5. **Team can track automation status** in Jira:
   - Filter by `Automated` label to see all automated tests
   - Filter by `For_Automation` label to see tests pending automation

### Scripts for Automation Status Management

**1. `scripts/jira/add_automation_labels.py`**
- Scans all Python test files for Xray/Jira markers
- Identifies tests with actual test functions
- Updates Jira tests with `Automated` or `For_Automation` labels
- **Usage:**
  ```bash
  python scripts/jira/add_automation_labels.py --dry-run  # Preview changes
  python scripts/jira/add_automation_labels.py --update   # Apply changes
  python scripts/jira/add_automation_labels.py --all-tests # Update all tests, not just Roy's
  ```

**2. `scripts/jira/add_labels_from_csv.py`**
- Reads CSV test files
- Matches tests with automation code markers
- Updates Jira tests with appropriate labels
- **Usage:**
  ```bash
  python scripts/jira/add_labels_from_csv.py --csv-files "file1.csv,file2.csv" --dry-run
  python scripts/jira/add_labels_from_csv.py --csv-files "file1.csv,file2.csv" --update
  ```

**3. `scripts/jira/check_all_markers.py`**
- Lists all markers found in automation code
- Shows which files contain markers
- **Usage:**
  ```bash
  python scripts/jira/check_all_markers.py
  ```

**4. `scripts/jira/analyze_markers_vs_jira.py`**
- Compares automation markers with Jira tests
- Identifies gaps (markers without Jira tests, Jira tests without markers)
- **Usage:**
  ```bash
  python scripts/jira/analyze_markers_vs_jira.py
  ```

**5. `scripts/jira/analyze_xray_test_repository.py`**
- Analyzes all tests in Xray Test Repository
- Generates comprehensive reports
- **Usage:**
  ```bash
  python scripts/jira/analyze_xray_test_repository.py
  ```

**6. `scripts/jira/analyze_csv_tests.py`**
- Analyzes Jira test CSV files
- Generates statistics and reports
- **Usage:**
  ```bash
  python scripts/jira/analyze_csv_tests.py --csv-files "file1.csv,file2.csv"
  ```

### Automation Status Best Practices

1. **Always add markers to test functions:**
   ```python
   @pytest.mark.xray("PZ-12345")
   def test_something():
       """Test something."""
       pass
   ```

2. **Run automation status scripts regularly:**
   - After adding new tests
   - After updating existing tests
   - Before sprint planning

3. **Review automation status in Jira:**
   - Check `For_Automation` label for tests pending automation
   - Verify `Automated` label is correctly applied

4. **Update automation status:**
   - When test is fully implemented → `Automated` label
   - When test is planned but not yet implemented → `For_Automation` label

---

## 🔄 Code Review Process

### When Review is Needed

- ✅ Every Pull Request
- ✅ Every new test
- ✅ Every significant code change
- ✅ CI/CD changes

### Code Review Workflow

```
1. Developer creates Pull Request
   ↓
2. PR includes: Description, Jira ticket link, Changes list
   ↓
3. Reviewer performs code review
   ↓
4. Reviewer writes comments (positive, constructive, suggestions)
   ↓
5. Discussion (if needed)
   ↓
6. Developer addresses comments
   ↓
7. Reviewer approves PR
   ↓
8. PR merged to main
```

### Review Process Steps

#### PR Creator Responsibilities:

1. **Create Pull Request in GitHub/GitLab**
   - Title: `[Type] - [Short description]`
   - Description includes:
     - What was changed
     - Why it was changed
     - How to test
     - Link to Jira ticket

2. **Link to Jira Ticket**
   - Include ticket number in PR title or description
   - Link to ticket in PR description

3. **List Main Changes**
   - Bullet points of key changes
   - Any breaking changes highlighted

#### Reviewer Responsibilities:

1. **Code Check:**
   - ✅ Code quality
   - ✅ Best Practices
   - ✅ Test Coverage
   - ✅ Documentation

2. **Write Comments:**
   - ✅ **Positive** - What's good
   - ✅ **Constructive** - What needs improvement
   - ✅ **Suggestions** - Improvement ideas

3. **Review Meeting (if needed):**
   - Discussion on complex comments
   - Explanation on design decisions
   - Clarification on requirements

4. **Approval:**
   - ✅ All comments addressed
   - ✅ Code approved
   - ✅ Merge to main

### Review Checklist

Before approving, verify:

- [ ] Code works (Tests pass)
- [ ] Sufficient Test Coverage
- [ ] Documentation exists
- [ ] Error Handling exists
- [ ] Logging exists
- [ ] Clean Code principles
- [ ] Follows Best Practices
- [ ] No Hardcoded Values
- [ ] Configuration is correct
- [ ] Jira ticket linked
- [ ] Automation labels updated (if applicable)
- [ ] All comments addressed

---

## 🚀 CI/CD Processes

**Owner:** Ron (until Knowledge Transfer complete)

### CI/CD Goals

**Full Automation:**
- ✅ Automated run on every PR
- ✅ Automated run on every Push to main
- ✅ Daily/nightly full runs

**Jenkins Slave in Office:**
- ✅ Physical setup in office
- ✅ SSH access
- ✅ Internal network access
- ✅ Run tests on internal systems

**Integration:**
- ✅ Jira/Xray - Status updates
- ✅ GitHub/GitLab - PR updates
- ✅ Slack/Email - Notifications

### Jenkins Pipeline Structure

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

### CI/CD Pipeline Workflow

```
1. Developer pushes code or creates PR
   ↓
2. Jenkins pipeline triggers automatically
   ↓
3. Pipeline stages execute:
   - Checkout code
   - Install dependencies
   - Run Backend tests
   - Run Frontend tests
   - Report to Xray
   ↓
4. Results published:
   - Test results to Jira/Xray
   - Notifications to Slack/Email
   - Reports available in Jenkins
   ↓
5. PR updated with test results
```

### CI/CD Tickets

High priority tickets for CI/CD infrastructure:

- `PZ-XXXX` - Setup Jenkins Master
- `PZ-XXXX` - Setup Jenkins Slave (in office)
- `PZ-XXXX` - Backend Tests Pipeline
- `PZ-XXXX` - Frontend Tests Pipeline
- `PZ-XXXX` - Integration with Jira/Xray
- `PZ-XXXX` - Automated PR Validation
- `PZ-XXXX` - Nightly Test Execution
- `PZ-XXXX` - Email/Slack Notifications

---

## 🔄 Automation Request Workflow (Tomer → Ron)

### Process:

```
1. Tomer identifies test that needs automation
   ↓
2. Tomer creates Jira ticket with:
   - Test name
   - Detailed steps (Step-by-step)
   - Expected results
   - Test scenarios
   - Priority
   ↓
3. Tomer mentions @Ron in ticket
   ↓
4. Ron creates automation task:
   - Title: "Automate: [Test Name]"
   - Description: Includes Tomer's steps
   - Labels: automation, frontend
   - Link to Tomer's original ticket
   ↓
5. Ron performs:
   - Test analysis
   - Automation writing
   - Execution and validation
   ↓
6. Ron updates Tomer on completion
7. Ron adds automation labels (Automated/For_Automation)
```

### Tomer's Ticket Template

**Title:** `Automation Request - [Test Name]`

**Description:**

```markdown
## Test Name
[Test Name]

## Detailed Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Expected Results
- [Expected result 1]
- [Expected result 2]

## Test Scenarios
- [Scenario 1]
- [Scenario 2]

## Priority
[High/Medium/Low]

## Additional Notes
[Any additional information]
```

### Ron's Automation Task Template

**Title:** `Automate: [Test Name]`

**Description:**

```markdown
## Automation Request
Link to Tomer's ticket: [Ticket Link]

## Original Test Steps
[Tomer's steps]

## Automation Approach
[How automation will be implemented]

## Acceptance Criteria
- [ ] Automation test written
- [ ] Test passes
- [ ] Test documented
- [ ] Test integrated into CI/CD
- [ ] Automation labels updated (Automated/For_Automation)

## Related
- Original request: [Tomer's ticket]
```

---

## 📚 Knowledge Transfer Process

**Owner:** Ron (for FE), Roy (for BE)  
**Status:** ⚠️ **URGENT - Ron leaving soon**

### Handover Process

**⚠️ CRITICAL:** Knowledge Transfer from Ron must be completed before he leaves. This is a top priority task.

#### Meeting 1: General Overview (2-3 hours)

**Content:**
- **Architecture:**
  - Project structure
  - Technologies (Playwright, pytest, etc.)
  - How everything connects

- **File Structure:**
  - Where everything is located
  - How to organize new files
  - Best Practices

- **Setup:**
  - How to run the project locally
  - How to configure environments
  - How to solve Setup problems

**Outcome:** General understanding of the project

---

#### Meeting 2: Practical Training (2-3 hours)

**Content:**
- **Running Tests:**
  - How to run specific tests
  - How to run tests by category
  - How to interpret results

- **Writing New Tests:**
  - Template for new test
  - Best Practices
  - Practical examples

- **Troubleshooting:**
  - Common problems
  - How to solve
  - Where to find information

**Outcome:** Ability to run and add tests

---

#### Meeting 3: Q&A and Deep Dive (2-3 hours)

**Content:**
- Open questions
- Deep dive into complex areas
- Practical work on examples

**Outcome:** Confidence in independent work

---

### Documentation to Create

**Frontend Automation:**
- `docs/02_user_guides/HOW_TO_RUN_FE_AUTOMATION.md` - How to run FE automation
- `docs/02_user_guides/HOW_TO_ADD_NEW_FE_TESTS.md` - How to add new FE tests
- `docs/02_user_guides/FE_AUTOMATION_TROUBLESHOOTING.md` - Troubleshooting guide
- `docs/03_architecture/FE_AUTOMATION_ARCHITECTURE.md` - FE automation architecture

**Backend Automation:**
- `docs/02_user_guides/HOW_TO_RUN_BE_AUTOMATION.md` - How to run BE automation
- `docs/02_user_guides/HOW_TO_ADD_NEW_BE_TESTS.md` - How to add new BE tests
- `docs/02_user_guides/BE_AUTOMATION_TROUBLESHOOTING.md` - Troubleshooting guide
- `docs/03_architecture/BE_AUTOMATION_ARCHITECTURE.md` - BE automation architecture

---

### Handover Checklist

- [ ] Meeting 1 completed
- [ ] Meeting 2 completed
- [ ] Meeting 3 completed
- [ ] All documents written
- [ ] All code documented
- [ ] Transferred to QA team
- [ ] Capability to extend tests
- [ ] Capability to solve common problems
- [ ] Capability to run automation fully
- [ ] CI/CD infrastructure documented
- [ ] Jenkins Slave setup documented
- [ ] Automation labels process documented

---

## 📊 Success Metrics & Tracking

### Sprint Metrics

Track these metrics per sprint:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Velocity** | [X] Story Points | Sum of completed story points |
| **Completion Rate** | [X]% | Completed tasks / Total tasks |
| **Code Quality** | 0 Critical Issues | Code review findings |
| **Test Coverage** | BE: ≥80%, FE: ≥80% | Coverage reports |
| **Bug Rate** | [X] bugs per sprint | Bug tickets created |
| **Automation Coverage** | ≥70% | Tests with `Automated` label / Total tests |

### Individual Metrics

#### Roy (Team Lead)

- [X] BE tickets created per sprint
- [X] K8s tests added per sprint
- [X] Test reviews performed per sprint
- [X] Sprint planning meetings
- [X] Automation labels updated per sprint

#### Tomer (Manual QA)

- [X] Manual tests performed per sprint
- [X] Documentation written (Xray TC's, Test Plans)
- [X] Tests transferred to automation
- [X] Test Plans in Confluence
- [X] Automation requests created per sprint

#### Ron (Frontend Automation)

- [X] Regression tests completed
- [X] CI/CD Pipeline active
- [X] Jenkins Slave active
- [X] Documentation written
- [X] Automation tasks from Tomer completed
- [X] Knowledge Transfer completed (before leaving)

---

## 📝 Related Documents

- [QA Team Work Plan](../programs/QA_TEAM_WORK_PLAN.md)
- [Automation Labels Update Summary](../../04_testing/xray_mapping/AUTOMATION_LABELS_UPDATE_SUMMARY.md)
- [Xray Test Repository Analysis](../../04_testing/xray_mapping/XRAY_TEST_REPOSITORY_ANALYSIS.md)
- [CSV Tests Analysis](../../04_testing/xray_mapping/TESTS_BY_ROY_AND_TOMER_ANALYSIS.md)
- [Jira Integration Guide](../jira/XRAY_IMPORT_GUIDE.md)
- [Test Results](../../04_testing/test_results/)
- [Infrastructure Tests](../../07_infrastructure/)

---

**Last Updated:** 2025-11-05  
**Owner:** QA Team Lead  
**Version:** 1.1

---

## 🔄 Version History

**Version 1.1 (2025-11-05):**
- ✅ Added Automation Status Tracking section
- ✅ Added Automation Labels documentation
- ✅ Added Scripts for Automation Status Management
- ✅ Updated Knowledge Transfer section (URGENT status)
- ✅ Updated Automation Request Workflow to include automation labels
- ✅ Updated Success Metrics to include Automation Coverage

**Version 1.0 (2025-11-04):**
- Initial version with Sprint Structure, Ticket Creation, Code Review, CI/CD, Knowledge Transfer

