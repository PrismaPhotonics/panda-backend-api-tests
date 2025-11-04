# Jira Integration Module

## Overview

Comprehensive Jira API integration module for the Focus Server Automation framework.

## Features

- ✅ Create issues (Tasks, Bugs, Stories, Epics, Sub-tasks)
- ✅ Read and retrieve issues
- ✅ Search issues using JQL
- ✅ Update issue fields and status
- ✅ Manage issue links and attachments
- ✅ Work with projects, fields, and metadata
- ✅ Template-based issue creation
- ✅ Predefined search filters

## Quick Start

```python
from external.jira import JiraClient

# Initialize client
client = JiraClient()

# Create an issue
issue = client.create_issue(
    summary="Bug in API endpoint",
    description="The /channels endpoint returns 500 error",
    issue_type="Bug",
    priority="High",
    labels=["bug", "api", "critical"]
)

# Search for issues
issues = client.search_issues("project = PZ AND status != Done")

# Get issue details
issue = client.get_issue("PZ-12345")
```

## Documentation

See `docs/06_project_management/jira/JIRA_INTEGRATION_GUIDE.md` for complete documentation.

## Configuration

Edit `config/jira_config.yaml` to set your Jira URL and API token.

## Scripts

See `scripts/jira/` for command-line scripts:
- `create_jira_issue.py` - Create new issues
- `search_jira_issues.py` - Search issues
- `get_jira_issue.py` - Get issue details
- `update_jira_issue.py` - Update issues

