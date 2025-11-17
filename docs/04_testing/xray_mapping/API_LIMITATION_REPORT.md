# Jira API Limitation Report - Test Plan PZ-14024

## Problem

The Jira Cloud API is returning only **100 test results** instead of the expected **237 tests** shown in Jira UI.

## Investigation Results

### Query Used
```jql
project = PZ AND issuetype = Test AND text ~ "PZ-14024"
```

### API Methods Tested

1. **`search_issues()`** - Deprecated, limited to 100 results
2. **`enhanced_search_issues()`** - Returns only 100 results, doesn't support pagination parameters
3. **REST API v2** - Removed (410 error)
4. **REST API v3** - Requires different format, still investigating

### Current Results

- **API Returns**: 100 tests
- **Jira UI Shows**: 237 tests
- **Missing**: 137 tests

## Root Cause

The Jira Cloud API has a **hard limit of 100 results per query** for text search queries. This is a known limitation of the Jira Cloud API.

## Possible Solutions

1. **Use Multiple Queries**: Split the query into multiple smaller queries with different filters
2. **Get All Tests and Filter Locally**: Get all tests in the project and filter them locally
3. **Use Jira Export Feature**: Export the test plan from Jira UI
4. **Contact Jira Support**: Request API limit increase or alternative method
5. **Use Xray API**: If available, use Xray-specific API endpoints

## Next Steps

1. Try using Xray API endpoints if available
2. Implement multiple query approach
3. Get all tests in project and filter locally
4. Contact Jira support about API limitations

## Test IDs Found (100 tests)

See `TEST_PLAN_PZ14024_ALL_TESTS.txt` for the complete list of 100 test IDs found.

