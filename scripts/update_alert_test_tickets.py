"""
Script to update alert test tickets:
1. Update Assignee to Roy Avrahami
2. Link all tests to Test Plan PZ-14024
3. Remove test numbers from titles (PZ-15000: Alert... -> Alert...)

Usage:
    python scripts/update_alert_test_tickets.py
"""

import sys
import os
from pathlib import Path
import re

# Add project root to path
project_root = Path(__file__).parent.parent

# Fix import conflict
import shutil
scripts_jira_init = project_root / "scripts" / "jira" / "__init__.py"
scripts_jira_init_backup = project_root / "scripts" / "jira" / "__init__.py.backup"
backup_created = False

if scripts_jira_init.exists():
    try:
        shutil.move(str(scripts_jira_init), str(scripts_jira_init_backup))
        backup_created = True
    except Exception:
        pass

try:
    sys.path.insert(0, str(project_root))
    
    from external.jira import JiraClient
    import logging
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
finally:
    if backup_created and scripts_jira_init_backup.exists():
        try:
            shutil.move(str(scripts_jira_init_backup), str(scripts_jira_init))
        except Exception:
            pass

# List of all test tickets created (PZ-14933 to PZ-14964, excluding skipped ones)
TEST_TICKETS = [
    "PZ-14933", "PZ-14934", "PZ-14935", "PZ-14936", "PZ-14937",  # Positive (PZ-15000-15004)
    "PZ-14938", "PZ-14939", "PZ-14940", "PZ-14941", "PZ-14942", "PZ-14943", "PZ-14944",  # Negative (PZ-15010-15017)
    "PZ-14945", "PZ-14946", "PZ-14947", "PZ-14948", "PZ-14949", "PZ-14950", "PZ-14951", "PZ-14952",  # Edge Cases (PZ-15020-15027)
    "PZ-14953", "PZ-14954", "PZ-14955", "PZ-14956", "PZ-14957",  # Load (PZ-15030-15034)
    "PZ-14958", "PZ-14959", "PZ-14960", "PZ-14961", "PZ-14962", "PZ-14963",  # Performance (PZ-15040-15045)
    "PZ-14964"  # Investigation (PZ-15051)
]

TEST_PLAN_KEY = "PZ-14024"


def get_user_account_id(client: JiraClient, username_or_email: str) -> str:
    """Get user account ID from username or email."""
    try:
        # Try to get user by username/email
        user = client.jira.user(username_or_email)
        if hasattr(user, 'accountId'):
            return user.accountId
        elif hasattr(user, 'key'):
            return user.key
        else:
            return username_or_email
    except Exception as e:
        logger.warning(f"Could not get account ID for {username_or_email}: {e}")
        # Try alternative: search for user
        try:
            users = client.jira.search_users(username_or_email)
            if users:
                user = users[0]
                if hasattr(user, 'accountId'):
                    return user.accountId
                elif hasattr(user, 'key'):
                    return user.key
        except Exception:
            pass
        return username_or_email


def link_test_to_test_plan(client: JiraClient, test_key: str, test_plan_key: str) -> bool:
    """Link a test to a Test Plan using Xray API."""
    try:
        # Method 1: Use Xray REST API to add test to Test Plan
        xray_api_url = f"{client.base_url}/rest/raven/1.0/api/testplan/{test_plan_key}/test"
        
        # Get test issue to verify it exists
        test_issue = client.jira.issue(test_key)
        
        # Use Xray API to add test to Test Plan
        # Xray API expects: POST /rest/raven/1.0/api/testplan/{testPlanKey}/test
        # Body: {"testKey": "PZ-XXXXX"}
        
        import requests
        from requests.auth import HTTPBasicAuth
        
        # Get auth from client
        auth = client.jira._session.auth if hasattr(client.jira._session, 'auth') else None
        
        if not auth:
            # Build auth from config
            email = client.email
            api_token = client.api_token
            auth = HTTPBasicAuth(email, api_token)
        
        payload = {"testKey": test_key}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(
            xray_api_url,
            json=payload,
            auth=auth,
            headers=headers,
            verify=client.verify_ssl
        )
        
        if response.status_code in [200, 201, 204]:
            logger.info(f"✅ Linked {test_key} to Test Plan {test_plan_key}")
            return True
        elif response.status_code == 400:
            # Test might already be linked
            logger.info(f"ℹ️  {test_key} might already be linked to Test Plan (status 400)")
            return True
        else:
            logger.warning(f"⚠️  Could not link {test_key} to Test Plan: {response.status_code} - {response.text[:200]}")
            # Try alternative method: create issue link
            return link_test_to_test_plan_via_link(client, test_key, test_plan_key)
            
    except Exception as e:
        logger.warning(f"⚠️  Error linking {test_key} to Test Plan: {e}")
        # Try alternative method
        return link_test_to_test_plan_via_link(client, test_key, test_plan_key)


def link_test_to_test_plan_via_link(client: JiraClient, test_key: str, test_plan_key: str) -> bool:
    """Link test to Test Plan using issue links (fallback method)."""
    try:
        # Create issue link: test "relates to" test plan
        # Note: This might not work for Xray Test Plans, but worth trying
        test_issue = client.jira.issue(test_key)
        test_plan_issue = client.jira.issue(test_plan_key)
        
        # Try to create a "relates to" link
        # Note: Jira Python library doesn't have direct link creation, so we'll use REST API
        import requests
        from requests.auth import HTTPBasicAuth
        
        email = client.email
        api_token = client.api_token
        auth = HTTPBasicAuth(email, api_token)
        
        link_url = f"{client.base_url}/rest/api/2/issueLink"
        payload = {
            "type": {"name": "Relates"},
            "inwardIssue": {"key": test_key},
            "outwardIssue": {"key": test_plan_key}
        }
        
        response = requests.post(
            link_url,
            json=payload,
            auth=auth,
            headers={"Content-Type": "application/json"},
            verify=client.verify_ssl
        )
        
        if response.status_code in [200, 201, 204]:
            logger.info(f"✅ Linked {test_key} to Test Plan {test_plan_key} via issue link")
            return True
        elif response.status_code == 400:
            # Link might already exist
            logger.info(f"ℹ️  Link might already exist for {test_key}")
            return True
        else:
            logger.warning(f"⚠️  Could not create link: {response.status_code}")
            return False
            
    except Exception as e:
        logger.warning(f"⚠️  Error creating link: {e}")
        return False


def remove_test_number_from_summary(summary: str) -> str:
    """Remove test number prefix from summary (e.g., 'PZ-15000: Alert...' -> 'Alert...')."""
    # Pattern: PZ-XXXXX: at the start
    pattern = r'^PZ-\d+:\s*'
    cleaned = re.sub(pattern, '', summary)
    return cleaned.strip()


def update_alert_test_tickets():
    """Update all alert test tickets."""
    logger.info("=" * 80)
    logger.info("Updating Alert Test Tickets")
    logger.info("=" * 80)
    
    # Initialize Jira client
    try:
        client = JiraClient()
        logger.info(f"Connected to Jira: {client.base_url}")
        logger.info(f"Project: {client.project_key}")
    except Exception as e:
        logger.error(f"Failed to initialize Jira client: {e}")
        return
    
    # Get Roy Avrahami's account ID
    logger.info("\nFinding Roy Avrahami's account ID...")
    assignee_id = get_user_account_id(client, "roy.avrahami@prismaphotonics.com")
    logger.info(f"Assignee ID: {assignee_id}")
    
    updated_count = 0
    assignee_updated = 0
    summary_updated = 0
    linked_count = 0
    failed_count = 0
    
    for test_key in TEST_TICKETS:
        try:
            logger.info(f"\n{'='*80}")
            logger.info(f"Processing: {test_key}")
            logger.info(f"{'='*80}")
            
            # Get current issue
            issue = client.get_issue(test_key)
            current_summary = issue['summary']
            current_assignee = issue.get('assignee')
            
            logger.info(f"Current Summary: {current_summary}")
            logger.info(f"Current Assignee: {current_assignee or 'Unassigned'}")
            
            # 1. Update Assignee
            if current_assignee != "Roy Avrahami":
                try:
                    client.update_issue(test_key, assignee=assignee_id)
                    logger.info(f"✅ Updated Assignee to Roy Avrahami")
                    assignee_updated += 1
                except Exception as e:
                    logger.warning(f"⚠️  Could not update assignee: {e}")
            
            # 2. Update Summary (remove test number)
            new_summary = remove_test_number_from_summary(current_summary)
            if new_summary != current_summary:
                try:
                    client.update_issue(test_key, summary=new_summary)
                    logger.info(f"✅ Updated Summary: {new_summary}")
                    summary_updated += 1
                except Exception as e:
                    logger.warning(f"⚠️  Could not update summary: {e}")
            
            # 3. Link to Test Plan
            if link_test_to_test_plan(client, test_key, TEST_PLAN_KEY):
                linked_count += 1
            
            updated_count += 1
            
        except Exception as e:
            logger.error(f"❌ Failed to update {test_key}: {e}")
            failed_count += 1
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total tickets: {len(TEST_TICKETS)}")
    logger.info(f"✅ Processed: {updated_count}")
    logger.info(f"✅ Assignee updated: {assignee_updated}")
    logger.info(f"✅ Summary updated: {summary_updated}")
    logger.info(f"✅ Linked to Test Plan: {linked_count}")
    logger.info(f"❌ Failed: {failed_count}")
    logger.info("=" * 80)
    
    # Close client
    client.close()
    
    logger.info("\n✅ Done!")


if __name__ == "__main__":
    update_alert_test_tickets()

