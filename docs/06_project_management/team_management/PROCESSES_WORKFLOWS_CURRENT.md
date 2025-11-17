# Focus Server QA Team - Processes & Workflows

**Last Updated:** 2025-11-03T14:55:22.436Z
**Version:** 1

---

<p><strong>Team Lead:</strong> Roy Avrahami  <br /><strong>Created:</strong> 2025-11-04  <br /><strong>Status:</strong> ✅ Active  <br /><strong>Version:</strong> 1.0</p><hr /><h2>📋 Objective</h2><p>This document defines the <strong>processes</strong> and <strong>workflows</strong> for the Focus Server QA Team. It outlines how the team operates day-to-day, including sprint structure, ticket creation, code review, and other operational processes.</p><hr /><h2>📅 Sprint Structure</h2><h3><strong>Sprint Duration</strong></h3><ul><li><p><strong>Length:</strong> 2 weeks</p></li><li><p><strong>Kick-off:</strong> Tuesday 08:00</p></li><li><p><strong>Demo &amp; Retrospective:</strong> Tuesday 08:00 (end of sprint)</p></li></ul><h3><strong>Weekly Schedule</strong></h3><ac:structured-macro ac:name="code" ac:schema-version="1" ac:macro-id="ba880a89-e550-4ed3-8294-8a2ada7bef41"><ac:parameter ac:name="breakoutMode">wide</ac:parameter><ac:parameter ac:name="breakoutWidth">760</ac:parameter><ac:plain-text-body><![CDATA[┌─────────────────────────────────────────────────────────────┐
│                    Sprint (2 weeks)                          │
├─────────────────────────────────────────────────────────────┤
│ Monday          │ Create tickets and write tasks             │
│ Tuesday (08:00) │ Sprint start - Kick-off meeting            │
│ Wednesday-Thursday │ Work on tasks                          │
│ Sunday          │ Week 1 summary                             │
│ Monday (Week 2) │ Review and feedback - Ready for Deploy     │
│ Tuesday (08:00) │ Sprint end - Demo and Retrospective       │
└─────────────────────────────────────────────────────────────┘]]></ac:plain-text-body></ac:structured-macro><h3><strong>Sprint Events</strong></h3><h4><strong>1. Task Creation (Monday before Sprint)</strong></h4><p><strong>Participants:</strong> All team members  <br /><strong>Time:</strong> Sunday evening (preparation), Monday by 16:00 (ticket creation)</p><p><strong>Process:</strong></p><ol start="1"><li><p><strong>Sunday evening:</strong> Each team member prepares task list for next sprint</p></li><li><p><strong>Monday (by 16:00):</strong> Each team member creates Jira tickets with:</p><ul><li><p>✅ Detailed task description</p></li><li><p>✅ Acceptance Criteria</p></li><li><p>✅ Story Points (if applicable)</p></li><li><p>✅ Labels (backend, frontend, infrastructure, etc.)</p></li></ul></li><li><p><strong>Monday (16:00-17:00):</strong> Joint Review meeting</p><ul><li><p>Each team member presents their tasks</p></li><li><p>Discussion on priorities</p></li><li><p>Approval or changes to tasks</p></li></ul></li></ol><p><strong>Deliverables:</strong></p><ul><li><p>All sprint tickets created</p></li><li><p>Tickets reviewed and approved</p></li><li><p>Sprint backlog ready</p></li></ul><hr /><h4><strong>2. Sprint Kick-off (Tuesday 08:00)</strong></h4><p><strong>Participants:</strong> All team members  <br /><strong>Duration:</strong> 30-45 minutes</p><p><strong>Agenda:</strong></p><ol start="1"><li><p>Quick review of sprint tasks</p></li><li><p>Final work distribution</p></li><li><p>Risk and dependency identification</p></li><li><p>Agreement on Definition of Done</p></li><li><p>Q&amp;A</p></li></ol><p><strong>Deliverables:</strong></p><ul><li><p>Sprint plan confirmed</p></li><li><p>Work distribution agreed</p></li><li><p>Risks identified</p></li><li><p>DoD agreed upon</p></li></ul><hr /><h4><strong>3. Week 1 Summary (Sunday)</strong></h4><p><strong>Participants:</strong> Team Lead  <br /><strong>Duration:</strong> Individual preparation</p><p><strong>Content:</strong></p><ul><li><p>Progress update</p></li><li><p>Blockers identification</p></li><li><p>Adjustments needed</p></li></ul><p><strong>Deliverables:</strong></p><ul><li><p>Week 1 summary report</p></li><li><p>Blocker list (if any)</p></li><li><p>Adjustment recommendations</p></li></ul><hr /><h4><strong>4. Review and Feedback (Monday Week 2)</strong></h4><p><strong>Participants:</strong> All team members  <br /><strong>Duration:</strong> As needed</p><p><strong>Content:</strong></p><ul><li><p>Code review status</p></li><li><p>Test execution status</p></li><li><p>Deployment readiness</p></li><li><p>Feedback on completed work</p></li></ul><p><strong>Deliverables:</strong></p><ul><li><p>Review feedback</p></li><li><p>Deployment readiness assessment</p></li><li><p>Final adjustments</p></li></ul><hr /><h4><strong>5. Demo &amp; Retrospective (Tuesday 08:00)</strong></h4><p><strong>Participants:</strong> All team members  <br /><strong>Duration:</strong> 60-90 minutes</p><p><strong>Demo Agenda:</strong></p><ol start="1"><li><p>Show completed work</p></li><li><p>Demonstrate new features/tests</p></li><li><p>Share metrics and results</p></li></ol><p><strong>Retrospective Agenda:</strong></p><ol start="1"><li><p>What went well?</p></li><li><p>What could be improved?</p></li><li><p>Action items for next sprint</p></li></ol><p><strong>Deliverables:</strong></p><ul><li><p>Demo presentation</p></li><li><p>Retrospective notes</p></li><li><p>Action items list</p></li><li><p>Sprint summary</p></li></ul><hr /><h2>🎫 Ticket Creation Process</h2><h3><strong>Ticket Creation Workflow</strong></h3><ac:structured-macro ac:name="code" ac:schema-version="1" ac:macro-id="c34be298-8aaa-4be5-be2a-ea0937f90e91"><ac:parameter ac:name="breakoutMode">wide</ac:parameter><ac:parameter ac:name="breakoutWidth">760</ac:parameter><ac:plain-text-body><![CDATA[1. Team member prepares task list (Sunday evening)
   ↓
2. Team member creates Jira ticket (Monday by 16:00)
   ↓
3. Ticket includes: Description, Acceptance Criteria, Labels, Story Points
   ↓
4. Joint Review meeting (Monday 16:00-17:00)
   ↓
5. Ticket approved or modified
   ↓
6. Ticket ready for sprint]]></ac:plain-text-body></ac:structured-macro><h3><strong>Jira Ticket Template</strong></h3><p><strong>Title:</strong> <code>[Type] - [Short description]</code></p><p><strong>Description:</strong></p><ac:structured-macro ac:name="code" ac:schema-version="1" ac:macro-id="28359a43-ff29-4ad0-bde6-e46eb24e805b"><ac:parameter ac:name="language">markdown</ac:parameter><ac:parameter ac:name="breakoutMode">wide</ac:parameter><ac:parameter ac:name="breakoutWidth">760</ac:parameter><ac:plain-text-body><![CDATA[## Goal
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
[Additional notes]]]></ac:plain-text-body></ac:structured-macro><h3><strong>Ticket Types</strong></h3><table data-table-width="760" data-layout="default" ac:local-id="99cc4110-5725-4ae8-8cc5-8ae00de2dff5"><tbody><tr><th><p><strong>Type</strong></p></th><th><p><strong>Usage</strong></p></th><th><p><strong>Example</strong></p></th></tr><tr><td><p><strong>Story</strong> </p></td><td><p>Feature or test group </p></td><td><p>&quot;Automate API Endpoint Coverage&quot; </p></td></tr><tr><td><p><strong>Task</strong> </p></td><td><p>Technical task </p></td><td><p>&quot;Setup Jenkins Slave&quot; </p></td></tr><tr><td><p><strong>Bug</strong> </p></td><td><p>Found bug </p></td><td><p>&quot;PZ-13986: 200 Jobs Capacity Issue&quot; </p></td></tr><tr><td><p><strong>Sub-task</strong> </p></td><td><p>Small task part of larger Story </p></td><td><p>&quot;Add health check test&quot; </p></td></tr></tbody></table><h3><strong>Recommended Labels</strong></h3><p><strong>Component Labels:</strong></p><ul><li><p><code>backend</code> - Backend tasks</p></li><li><p><code>frontend</code> - Frontend tasks</p></li><li><p><code>infrastructure</code> - Infrastructure tasks</p></li></ul><p><strong>Type Labels:</strong></p><ul><li><p><code>automation</code> - Automation tasks</p></li><li><p><code>manual</code> - Manual testing tasks</p></li><li><p><code>bug</code> - Bug tickets</p></li><li><p><code>feature</code> - Feature tickets</p></li></ul><p><strong>Technology Labels:</strong></p><ul><li><p><code>kubernetes</code> - K8s tests</p></li><li><p><code>regression</code> - Regression tests</p></li><li><p><code>api</code> - API tests</p></li><li><p><code>ui</code> - UI tests</p></li></ul><h3><strong>Story Points</strong></h3><p>Use Fibonacci sequence: 1, 2, 3, 5, 8, 13</p><p><strong>Guidelines:</strong></p><ul><li><p><strong>1-2 points:</strong> Small tasks (few hours)</p></li><li><p><strong>3-5 points:</strong> Medium tasks (1-2 days)</p></li><li><p><strong>8 points:</strong> Large tasks (3-5 days)</p></li><li><p><strong>13 points:</strong> Very large tasks (1 week+) - consider breaking down</p></li></ul><hr /><h2>🔄 Code Review Process</h2><h3><strong>When Review is Needed</strong></h3><ul><li><p>✅ Every Pull Request</p></li><li><p>✅ Every new test</p></li><li><p>✅ Every significant code change</p></li><li><p>✅ CI/CD changes</p></li></ul><h3><strong>Code Review Workflow</strong></h3><ac:structured-macro ac:name="code" ac:schema-version="1" ac:macro-id="97f7f5b4-091e-40ca-9b30-887d16f166f0"><ac:parameter ac:name="breakoutMode">wide</ac:parameter><ac:parameter ac:name="breakoutWidth">760</ac:parameter><ac:plain-text-body><![CDATA[1. Developer creates Pull Request
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
8. PR merged to main]]></ac:plain-text-body></ac:structured-macro><h3><strong>Review Process Steps</strong></h3><h4><strong>PR Creator Responsibilities:</strong></h4><ol start="1"><li><p><strong>Create Pull Request in GitHub/GitLab</strong></p><ul><li><p>Title: <code>[Type] - [Short description]</code></p></li><li><p>Description includes:</p><ul><li><p>What was changed</p></li><li><p>Why it was changed</p></li><li><p>How to test</p></li><li><p>Link to Jira ticket</p></li></ul></li></ul></li><li><p><strong>Link to Jira Ticket</strong></p><ul><li><p>Include ticket number in PR title or description</p></li><li><p>Link to ticket in PR description</p></li></ul></li><li><p><strong>List Main Changes</strong></p><ul><li><p>Bullet points of key changes</p></li><li><p>Any breaking changes highlighted</p></li></ul></li></ol><h4><strong>Reviewer Responsibilities:</strong></h4><ol start="1"><li><p><strong>Code Check:</strong></p><ul><li><p>✅ Code quality</p></li><li><p>✅ Best Practices</p></li><li><p>✅ Test Coverage</p></li><li><p>✅ Documentation</p></li></ul></li><li><p><strong>Write Comments:</strong></p><ul><li><p>✅ <strong>Positive</strong> - What's good</p></li><li><p>✅ <strong>Constructive</strong> - What needs improvement</p></li><li><p>✅ <strong>Suggestions</strong> - Improvement ideas</p></li></ul></li><li><p><strong>Review Meeting (if needed):</strong></p><ul><li><p>Discussion on complex comments</p></li><li><p>Explanation on design decisions</p></li><li><p>Clarification on requirements</p></li></ul></li><li><p><strong>Approval:</strong></p><ul><li><p>✅ All comments addressed</p></li><li><p>✅ Code approved</p></li><li><p>✅ Merge to main</p></li></ul></li></ol><h3><strong>Review Checklist</strong></h3><p>Before approving, verify:</p><ul><li><p>[ ] Code works (Tests pass)</p></li><li><p>[ ] Sufficient Test Coverage</p></li><li><p>[ ] Documentation exists</p></li><li><p>[ ] Error Handling exists</p></li><li><p>[ ] Logging exists</p></li><li><p>[ ] Clean Code principles</p></li><li><p>[ ] Follows Best Practices</p></li><li><p>[ ] No Hardcoded Values</p></li><li><p>[ ] Configuration is correct</p></li><li><p>[ ] Jira ticket linked</p></li><li><p>[ ] All comments addressed</p></li></ul><hr /><h2>🔄 CI/CD Processes</h2><p><strong>Owner:</strong> Ron</p><h3><strong>CI/CD Goals</strong></h3><p><strong>Full Automation:</strong></p><ul><li><p>✅ Automated run on every PR</p></li><li><p>✅ Automated run on every Push to main</p></li><li><p>✅ Daily/nightly full runs</p></li></ul><p><strong>Jenkins Slave in Office:</strong></p><ul><li><p>✅ Physical setup in office</p></li><li><p>✅ SSH access</p></li><li><p>✅ Internal network access</p></li><li><p>✅ Run tests on internal systems</p></li></ul><p><strong>Integration:</strong></p><ul><li><p>✅ Jira/Xray - Status updates</p></li><li><p>✅ GitHub/GitLab - PR updates</p></li><li><p>✅ Slack/Email - Notifications</p></li></ul><h3><strong>Jenkins Pipeline Structure</strong></h3><ac:structured-macro ac:name="code" ac:schema-version="1" ac:macro-id="6d7fd14b-bad4-464a-9422-5c129ccb4f38"><ac:parameter ac:name="language">groovy</ac:parameter><ac:parameter ac:name="breakoutMode">wide</ac:parameter><ac:parameter ac:name="breakoutWidth">760</ac:parameter><ac:plain-text-body><![CDATA[pipeline {
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
}]]></ac:plain-text-body></ac:structured-macro><h3><strong>CI/CD Pipeline Workflow</strong></h3><ac:structured-macro ac:name="code" ac:schema-version="1" ac:macro-id="41536ff9-060d-4d6d-867e-becc7f8c52a1"><ac:parameter ac:name="breakoutMode">wide</ac:parameter><ac:parameter ac:name="breakoutWidth">760</ac:parameter><ac:plain-text-body><![CDATA[1. Developer pushes code or creates PR
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
5. PR updated with test results]]></ac:plain-text-body></ac:structured-macro><h3><strong>CI/CD Tickets</strong></h3><p>High priority tickets for CI/CD infrastructure:</p><ul><li><p><code>PZ-XXXX</code> - Setup Jenkins Master</p></li><li><p><code>PZ-XXXX</code> - Setup Jenkins Slave (in office)</p></li><li><p><code>PZ-XXXX</code> - Backend Tests Pipeline</p></li><li><p><code>PZ-XXXX</code> - Frontend Tests Pipeline</p></li><li><p><code>PZ-XXXX</code> - Integration with Jira/Xray</p></li><li><p><code>PZ-XXXX</code> - Automated PR Validation</p></li><li><p><code>PZ-XXXX</code> - Nightly Test Execution</p></li><li><p><code>PZ-XXXX</code> - Email/Slack Notifications</p></li></ul><hr /><h2>🔄 Automation Request Workflow (Tomer &rarr; Ron)</h2><h3><strong>Process:</strong></h3><ac:structured-macro ac:name="code" ac:schema-version="1" ac:macro-id="31d93e1e-e6c5-40bc-a338-b7fa2e55cea4"><ac:parameter ac:name="breakoutMode">wide</ac:parameter><ac:parameter ac:name="breakoutWidth">760</ac:parameter><ac:plain-text-body><![CDATA[1. Tomer identifies test that needs automation
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
6. Ron updates Tomer on completion]]></ac:plain-text-body></ac:structured-macro><h3><strong>Tomer's Ticket Template</strong></h3><p><strong>Title:</strong> <code>Automation Request - [Test Name]</code></p><p><strong>Description:</strong></p><ac:structured-macro ac:name="code" ac:schema-version="1" ac:macro-id="beaa701f-68c3-4506-a8e3-a2e1d9132390"><ac:parameter ac:name="language">markdown</ac:parameter><ac:parameter ac:name="breakoutMode">wide</ac:parameter><ac:parameter ac:name="breakoutWidth">760</ac:parameter><ac:plain-text-body><![CDATA[## Test Name
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
[Any additional information]]]></ac:plain-text-body></ac:structured-macro><h3><strong>Ron's Automation Task Template</strong></h3><p><strong>Title:</strong> <code>Automate: [Test Name]</code></p><p><strong>Description:</strong></p><ac:structured-macro ac:name="code" ac:schema-version="1" ac:macro-id="38c01c7f-2141-456f-ba64-c903b432672e"><ac:parameter ac:name="language">markdown</ac:parameter><ac:parameter ac:name="breakoutMode">wide</ac:parameter><ac:parameter ac:name="breakoutWidth">760</ac:parameter><ac:plain-text-body><![CDATA[## Automation Request
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

## Related
- Original request: [Tomer's ticket]]]></ac:plain-text-body></ac:structured-macro><hr /><h2>📚 Knowledge Transfer Process</h2><p><strong>Owner:</strong> Ron (for FE), Roy (for BE)</p><h3><strong>Handover Process</strong></h3><h4><strong>Meeting 1: General Overview (2-3 hours)</strong></h4><p><strong>Content:</strong></p><ul><li><p><strong>Architecture:</strong></p><ul><li><p>Project structure</p></li><li><p>Technologies (Playwright, pytest, etc.)</p></li><li><p>How everything connects</p></li></ul></li><li><p><strong>File Structure:</strong></p><ul><li><p>Where everything is located</p></li><li><p>How to organize new files</p></li><li><p>Best Practices</p></li></ul></li><li><p><strong>Setup:</strong></p><ul><li><p>How to run the project locally</p></li><li><p>How to configure environments</p></li><li><p>How to solve Setup problems</p></li></ul></li></ul><p><strong>Outcome:</strong> General understanding of the project</p><hr /><h4><strong>Meeting 2: Practical Training (2-3 hours)</strong></h4><p><strong>Content:</strong></p><ul><li><p><strong>Running Tests:</strong></p><ul><li><p>How to run specific tests</p></li><li><p>How to run tests by category</p></li><li><p>How to interpret results</p></li></ul></li><li><p><strong>Writing New Tests:</strong></p><ul><li><p>Template for new test</p></li><li><p>Best Practices</p></li><li><p>Practical examples</p></li></ul></li><li><p><strong>Troubleshooting:</strong></p><ul><li><p>Common problems</p></li><li><p>How to solve</p></li><li><p>Where to find information</p></li></ul></li></ul><p><strong>Outcome:</strong> Ability to run and add tests</p><hr /><h4><strong>Meeting 3: Q&amp;A and Deep Dive (2-3 hours)</strong></h4><p><strong>Content:</strong></p><ul><li><p>Open questions</p></li><li><p>Deep dive into complex areas</p></li><li><p>Practical work on examples</p></li></ul><p><strong>Outcome:</strong> Confidence in independent work</p><hr /><h3><strong>Documentation to Create</strong></h3><p><strong>Frontend Automation:</strong></p><ul><li><p><code>docs/02_user_guides/HOW_TO_RUN_FE_AUTOMATION.md</code> - How to run FE automation</p></li><li><p><code>docs/02_user_guides/HOW_TO_ADD_NEW_FE_TESTS.md</code> - How to add new FE tests</p></li><li><p><code>docs/02_user_guides/FE_AUTOMATION_TROUBLESHOOTING.md</code> - Troubleshooting guide</p></li><li><p><code>docs/03_architecture/FE_AUTOMATION_ARCHITECTURE.md</code> - FE automation architecture</p></li></ul><p><strong>Backend Automation:</strong></p><ul><li><p><code>docs/02_user_guides/HOW_TO_RUN_BE_AUTOMATION.md</code> - How to run BE automation</p></li><li><p><code>docs/02_user_guides/HOW_TO_ADD_NEW_BE_TESTS.md</code> - How to add new BE tests</p></li><li><p><code>docs/02_user_guides/BE_AUTOMATION_TROUBLESHOOTING.md</code> - Troubleshooting guide</p></li><li><p><code>docs/03_architecture/BE_AUTOMATION_ARCHITECTURE.md</code> - BE automation architecture</p></li></ul><hr /><h3><strong>Handover Checklist</strong></h3><ul><li><p>[ ] Meeting 1 completed</p></li><li><p>[ ] Meeting 2 completed</p></li><li><p>[ ] Meeting 3 completed</p></li><li><p>[ ] All documents written</p></li><li><p>[ ] All code documented</p></li><li><p>[ ] Transferred to QA team</p></li><li><p>[ ] Capability to extend tests</p></li><li><p>[ ] Capability to solve common problems</p></li><li><p>[ ] Capability to run automation fully</p></li></ul><hr /><h2>📊 Success Metrics &amp; Tracking</h2><h3><strong>Sprint Metrics</strong></h3><p>Track these metrics per sprint:</p><table data-table-width="760" data-layout="default" ac:local-id="634fa68f-b1f2-45f3-8b63-ea34e9283536"><tbody><tr><th><p><strong>Metric</strong></p></th><th><p><strong>Target</strong></p></th><th><p><strong>How to Measure</strong></p></th></tr><tr><td><p><strong>Velocity</strong> </p></td><td><p>[X] Story Points </p></td><td><p>Sum of completed story points </p></td></tr><tr><td><p><strong>Completion Rate</strong> </p></td><td><p>[X]% </p></td><td><p>Completed tasks / Total tasks </p></td></tr><tr><td><p><strong>Code Quality</strong> </p></td><td><p>0 Critical Issues </p></td><td><p>Code review findings </p></td></tr><tr><td><p><strong>Test Coverage</strong> </p></td><td><p>BE: &ge;80%, FE: &ge;80% </p></td><td><p>Coverage reports </p></td></tr><tr><td><p><strong>Bug Rate</strong> </p></td><td><p>[X] bugs per sprint </p></td><td><p>Bug tickets created </p></td></tr></tbody></table><h3><strong>Individual Metrics</strong></h3><h4><strong>Roy (Team Lead)</strong></h4><ul><li><p>[X] BE tickets created per sprint</p></li><li><p>[X] K8s tests added per sprint</p></li><li><p>[X] Test reviews performed per sprint</p></li><li><p>[X] Sprint planning meetings</p></li></ul><h4><strong>Tomer (Manual QA)</strong></h4><ul><li><p>[X] Manual tests performed per sprint</p></li><li><p>[X] Documentation written (Xray TC's, Test Plans)</p></li><li><p>[X] Tests transferred to automation</p></li><li><p>[X] Test Plans in Confluence</p></li></ul><h4><strong>Ron (Frontend Automation)</strong></h4><ul><li><p>[X] Regression tests completed</p></li><li><p>[X] CI/CD Pipeline active</p></li><li><p>[X] Jenkins Slave active</p></li><li><p>[X] Documentation written</p></li><li><p>[X] Automation tasks from Tomer completed</p></li></ul>