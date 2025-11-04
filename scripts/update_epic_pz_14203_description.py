"""
Update Epic PZ-14203 Description
==================================

Update Epic PZ-14203 description to include only BE and FE automation epics.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Remove scripts directory from path to avoid conflicts
scripts_dir = str(project_root / "scripts")
if scripts_dir in sys.path:
    sys.path.remove(scripts_dir)

from external.jira.jira_agent import JiraAgent

# Initialize agent
jira_agent = JiraAgent()

epic_key = "PZ-14203"

# Get epic details
epic = jira_agent.get_issue(epic_key)

print("=" * 80)
print(f"Updating Epic {epic_key}")
print("=" * 80)
print(f"Current Summary: {epic.get('summary', 'N/A')}")

# New description focusing only on BE and FE automation epics
new_description = """
## 🎯 Epic Summary

Focus Server & Panda Automation Project - Comprehensive automation testing framework.

This epic contains two main automation epics:

## 📊 Sub-Epics

### 1. Backend Automation - Focus Server API Tests
**Epic:** [PZ-14221](https://prismaphotonics.atlassian.net/browse/PZ-14221)
- Full API test coverage for Focus Server
- Kubernetes orchestration tests
- Infrastructure resilience tests
- Performance and load tests

### 2. Client/Frontend Automation - Panda App E2E Tests
**Epic:** [PZ-14220](https://prismaphotonics.atlassian.net/browse/PZ-14220)
- E2E testing framework setup (Appium)
- Panda UI regression tests
- Live mode E2E tests
- Historic mode E2E tests
- Error handling E2E tests

## 🔗 Related Epics

- **BE Epic:** [PZ-14221 - Backend Automation](https://prismaphotonics.atlassian.net/browse/PZ-14221)
- **FE Epic:** [PZ-14220 - Client/Frontend Automation](https://prismaphotonics.atlassian.net/browse/PZ-14220)

## 📋 Business Value

- Reduce manual testing effort by 80%+
- Enable continuous integration and deployment
- Ensure quality and reliability of Focus Server and Panda UI
- Enable rapid feedback on code changes
- Improve test coverage and maintainability
"""

# Update epic description
try:
    jira_agent.client.update_issue(
        issue_key=epic_key,
        description=new_description
    )
    
    # Add comment
    comment = (
        f"Updated Epic description to include only BE and FE automation epics:\n"
        f"- BE Epic: [PZ-14221|https://prismaphotonics.atlassian.net/browse/PZ-14221]\n"
        f"- FE Epic: [PZ-14220|https://prismaphotonics.atlassian.net/browse/PZ-14220]"
    )
    jira_agent.add_comment(epic_key, comment)
    
    print("\n[SUCCESS] Successfully updated Epic description")
    print(f"   URL: {epic.get('url', 'N/A')}")
    
except Exception as e:
    print(f"\n[ERROR] Failed to update Epic: {e}")

print("\n" + "=" * 80)

