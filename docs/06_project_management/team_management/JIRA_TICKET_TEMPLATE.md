# Jira Ticket Template

**Created:** 2025-11-04  
**Purpose:** Standard template for creating tickets in Jira

---

## 📋 Full Template

```
Title: [Type] - [Short and precise description]

Description:
## 🎯 Goal
[Detailed description of the task goal. What do we want to achieve?]

## 📝 Steps to Execute
1. [Step 1 - specific and precise]
2. [Step 2 - specific and precise]
3. [Step 3 - specific and precise]

## ✅ Acceptance Criteria
- [ ] [Criterion 1 - measurable and testable]
- [ ] [Criterion 2 - measurable and testable]
- [ ] [Criterion 3 - measurable and testable]

## 🔗 Dependencies
- [Link to dependent ticket, if any]
- [Link to related tickets]

## 📎 Related Files
- `path/to/file1.py`
- `docs/path/to/doc1.md`

## 🏷️ Labels
[backend|frontend|infrastructure|automation|manual|bug|feature|regression|kubernetes|api|ui]

## 📊 Story Points
[X]

## 👤 Assignee
[Name of person assigned to task]

## 📅 Due Date
[Target date, if applicable]
```

---

## 📝 Ticket Types

### 1. Story - Feature or Test Group

```
Title: Story - [Feature description]

Description:
## 🎯 Goal
[Feature description and what it should do]

## 📝 User Story
As a [role]
I want [feature]
So that [benefit]

## 📝 Steps to Execute
1. [Step 1]
2. [Step 2]
3. [Step 3]

## ✅ Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

## 🧪 Tests
- [ ] Unit tests written
- [ ] Integration tests written
- [ ] E2E tests written (if applicable)

## 📚 Documentation
- [ ] Code documented
- [ ] User guide updated (if applicable)
- [ ] API docs updated (if applicable)
```

### 2. Task - Technical Task

```
Title: Task - [Task description]

Description:
## 🎯 Goal
[Description of the technical task]

## 📝 Steps to Execute
1. [Step 1]
2. [Step 2]
3. [Step 3]

## ✅ Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

## 🔧 Technical Details
[Technical details if applicable]
```

### 3. Bug - Found Bug

```
Title: Bug - [Short description of bug]

Description:
## 🐛 Summary
[Short description of the bug]

## 📝 Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

## 🔴 Current Behavior
[What happens now - the bug]

## ✅ Expected Behavior
[What should happen]

## 🌍 Environment
- Environment: [staging|production]
- Browser: [if applicable]
- OS: [if applicable]

## 📊 Priority
[High|Medium|Low]

## 🔗 Related
- Related Test: `tests/path/to/test.py::TestClass::test_name`
- Jira Marker: `@pytest.mark.jira("PZ-XXXX")`
```

### 4. Automation Task - Automation Task

```
Title: Automation - [Test Name]

Description:
## 🎯 Goal
Write automation for test: [Test Name]

## 📝 Test Steps (from manual test)
1. [Step 1 - from manual test]
2. [Step 2 - from manual test]
3. [Step 3 - from manual test]

## ✅ Expected Results
- [ ] [Expected result 1]
- [ ] [Expected result 2]
- [ ] [Expected result 3]

## 📝 Steps to Execute Automation
1. Analyze manual test
2. Write automation code
3. Run and validate
4. Integrate with CI/CD
5. Document

## ✅ Acceptance Criteria
- [ ] Automation written and working
- [ ] Automation runs successfully in CI/CD environment
- [ ] Documentation written
- [ ] Code review performed

## 🔗 Related
- Manual Test: [Link to manual test ticket]
- Test File: `tests/path/to/test_file.py`
```

---

## 🏷️ Recommended Labels

### By Technology
- `backend` - Backend tasks
- `frontend` - Frontend tasks
- `infrastructure` - Infrastructure
- `kubernetes` - K8s tests
- `api` - API tests
- `ui` - UI tests

### By Work Type
- `automation` - Automation
- `manual` - Manual testing
- `regression` - Regression tests
- `bug` - Bug
- `feature` - Feature

### By Priority
- `high-priority` - High priority
- `medium-priority` - Medium priority
- `low-priority` - Low priority
- `urgent` - Urgent

---

## 📊 Story Points

### T-Shirt Sizing
- XS (1 point) - Up to 1 hour
- S (2 points) - 1-4 hours
- M (3 points) - Half day
- L (5 points) - One day
- XL (8 points) - 2-3 days
- XXL (13 points) - Week+

---

## ✅ Checklist Before Creating Ticket

- [ ] Title is clear and precise
- [ ] Description is detailed
- [ ] Acceptance Criteria defined
- [ ] Labels appropriate
- [ ] Story Points estimated
- [ ] Assignee assigned
- [ ] Related tickets linked
- [ ] Related files attached

---

**Last Updated:** 2025-11-04  
**Users:** All team members

