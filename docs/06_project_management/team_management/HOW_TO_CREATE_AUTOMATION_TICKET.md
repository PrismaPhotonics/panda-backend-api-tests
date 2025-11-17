# How to Create Automation Ticket
## Guide for Manual QA

**Created:** 2025-11-04  
**For:** Tomer (Manual QA)  
**Purpose:** Process for creating tickets for tests that need automation

---

## 📋 Work Process

### Step 1: Identify Test That Needs Automation

**When to create a ticket?**
- ✅ New test that needs automation
- ✅ Manual test that repeats
- ✅ Regression test that needs automation
- ✅ Important test that needs automation

**Criteria:**
- Test is important (High/Medium Priority)
- Test repeats
- Test takes a long time to perform manually
- Test is sensitive to human errors

---

### Step 2: Write Detailed Test Description

**What to include:**

#### 1. Test Name
```
Test [Feature] - [Scenario]
```

**Example:**
```
Test Login - Successful login with valid credentials
```

#### 2. Test Description
```
This test checks [what the test checks].
```

**Example:**
```
This test checks that it's possible to log into the system with valid credentials.
```

#### 3. Detailed Steps (Step-by-Step)

**Format:**
```
1. [Step 1 - specific and precise]
   Expected: [what should happen]

2. [Step 2 - specific and precise]
   Expected: [what should happen]

3. [Step 3 - specific and precise]
   Expected: [what should happen]
```

**Example:**
```
1. Open browser and navigate to URL: https://10.10.10.100/liveView
   Expected: Login page appears

2. Enter username: admin
   Expected: Username appears in field

3. Enter password: password123
   Expected: Password appears (masked)

4. Click "Login" button
   Expected: Redirect to main page, message "Login successful"
```

#### 4. Expected Results

**What to include:**
- ✅ What should happen in each step
- ✅ What should appear on screen
- ✅ Error messages (if applicable)
- ✅ Error scenarios (if applicable)

**Example:**
```
Expected Results:
- Login page appears
- Username appears in field
- Password appears (masked)
- Redirect to main page
- Message "Login successful" appears
```

#### 5. Test Data

**What to include:**
- ✅ User credentials (if applicable)
- ✅ URLs (if applicable)
- ✅ Additional data (if applicable)

**Example:**
```
Test Data:
- Username: admin
- Password: password123
- URL: https://10.10.10.100/liveView
- Site ID: prisma-210-1000
```

#### 6. Test Environment

**What to include:**
- ✅ Environment: [staging|production]
- ✅ Browser: [Chrome|Firefox|Edge]
- ✅ OS: [Windows|Linux|Mac]
- ✅ Version: [if applicable]

**Example:**
```
Test Environment:
- Environment: staging
- Browser: Chrome 120
- OS: Windows 11
- Site ID: prisma-210-1000
```

#### 7. Priority

**When High Priority?**
- ✅ Critical test for feature
- ✅ Regression test
- ✅ Test that appears in Production

**When Medium Priority?**
- ✅ Important test but not critical
- ✅ Test for new feature

**When Low Priority?**
- ✅ Test for small feature
- ✅ Test for enhancement

---

### Step 3: Create Ticket in Jira

**Ticket Format:**

```
Title: Manual Test - [Test Name]

Description:
## 🎯 Goal
[Test description]

## 📝 Steps (Step-by-Step)
1. [Step 1]
   Expected: [Expected result]

2. [Step 2]
   Expected: [Expected result]

3. [Step 3]
   Expected: [Expected result]

## ✅ Expected Results
- [ ] [Expected result 1]
- [ ] [Expected result 2]
- [ ] [Expected result 3]

## 📊 Test Data
- [Data 1]: [Value]
- [Data 2]: [Value]

## 🌍 Test Environment
- Environment: [staging|production]
- Browser: [Chrome|Firefox|Edge]
- OS: [Windows|Linux|Mac]

## 📊 Priority
[High|Medium|Low]

## 🏷️ Labels
manual, automation-needed, frontend, [or other as needed]
```

---

### Step 4: Update Ron

**What to do:**
1. ✅ Mention Ron in ticket (@ron)
2. ✅ Send message in Slack/Email (if applicable)
3. ✅ Mark ticket as "Ready for Automation"

**Message Template:**
```
Hello Ron,

A new automation test ticket was created:
[Jira Ticket Link]

Test: [Test Name]
Priority: [High|Medium|Low]

Please review the ticket and create an appropriate automation task.

Thanks,
Tomer
```

---

## 📝 Complete Example

### Example: Login Test

```
Title: Manual Test - Successful login with valid credentials

Description:
## 🎯 Goal
This test checks that it's possible to log into the system with valid credentials.

## 📝 Steps (Step-by-Step)
1. Open Chrome browser and navigate to URL: https://10.10.10.100/liveView
   Expected: Login page appears

2. Enter username: admin
   Expected: Username appears in field

3. Enter password: password123
   Expected: Password appears (masked)

4. Click "Login" button
   Expected: Redirect to main page, message "Login successful"

## ✅ Expected Results
- [ ] Login page appears
- [ ] Username appears in field
- [ ] Password appears (masked)
- [ ] Redirect to main page
- [ ] Message "Login successful" appears

## ❌ Negative Test Cases (if applicable)
1. Login with invalid credentials
   Expected: Error message "Invalid username or password"

2. Login with empty username
   Expected: Error message "Username is required"

3. Login with empty password
   Expected: Error message "Password is required"

## 📊 Test Data
- Username: admin
- Password: password123
- URL: https://10.10.10.100/liveView
- Site ID: prisma-210-1000

## 🌍 Test Environment
- Environment: staging
- Browser: Chrome 120
- OS: Windows 11
- Site ID: prisma-210-1000

## 📊 Priority
High

## 🏷️ Labels
manual, automation-needed, frontend, ui, high-priority

## 🔗 Related
- Related Feature: [Link to feature]
- Related Bug: [Link to bug, if applicable]
```

---

## ✅ Checklist Before Creating Ticket

- [ ] Test name is clear and precise
- [ ] Test description is detailed
- [ ] Steps are detailed (Step-by-Step)
- [ ] Expected results are defined
- [ ] Test data is defined
- [ ] Test environment is defined
- [ ] Priority is defined
- [ ] Labels are appropriate
- [ ] Ron updated (@ron)
- [ ] Ticket marked as "Ready for Automation"

---

## 📚 Related Documents

- [Jira Ticket Template](JIRA_TICKET_TEMPLATE.md)
- [Team Processes and Sprint Management](TEAM_PROCESSES_AND_SPRINT_MANAGEMENT.md)

---

**Last Updated:** 2025-11-04  
**For:** Tomer (Manual QA)

