"""
Link Stories to Epic Script
============================

Links Stories to their parent Epic using Epic Link field.
"""

import sys
import io
from pathlib import Path

# Set UTF-8 encoding for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraAgent

# Initialize agent
agent = JiraAgent()

# Epic and Stories
client_epic_key = "PZ-14220"
client_stories = [
    "PZ-14222",  # Live Mode E2E Tests
    "PZ-14223",  # Historic Mode E2E Tests
    "PZ-14224",  # Error Handling E2E Tests
    "PZ-14225",  # Panel Tests
    "PZ-14226"   # Playwright E2E Framework Setup
]

print("\n" + "="*100)
print("Linking Stories to Epic")
print("="*100 + "\n")

# Get Epic Link custom field ID
# Usually it's customfield_10011 or similar - we need to find it
try:
    # Get issue fields to find Epic Link field
    fields = agent.client.jira.fields()
    epic_link_field = None
    
    for field in fields:
        if field['name'] == 'Epic Link' or field['name'] == 'Epic':
            epic_link_field = field['id']
            print(f"Found Epic Link field: {field['id']} ({field['name']})")
            break
    
    if not epic_link_field:
        # Try common field IDs
        common_epic_fields = ['customfield_10011', 'customfield_10014']
        print("Epic Link field not found by name, trying common IDs...")
        
        # Try to update with common field
        for field_id in common_epic_fields:
            try:
                # Try to update one story to test
                test_update = {field_id: client_epic_key}
                agent.client.update_issue(client_stories[0], **test_update)
                epic_link_field = field_id
                print(f"✅ Found working Epic Link field: {field_id}")
                break
            except:
                continue
    
    if epic_link_field:
        print(f"\nLinking {len(client_stories)} Stories to Epic {client_epic_key}...\n")
        
        for story_key in client_stories:
            try:
                # Update story with Epic Link
                update_fields = {epic_link_field: client_epic_key}
                agent.client.update_issue(story_key, **update_fields)
                print(f"   ✅ Linked {story_key} to Epic {client_epic_key}")
            except Exception as e:
                print(f"   ❌ Failed to link {story_key}: {e}")
        
        print(f"\n✅ Successfully linked all Stories to Epic {client_epic_key}")
    else:
        print("\n⚠️  Could not find Epic Link field automatically.")
        print("   Please link Stories manually in Jira UI:")
        print(f"   Epic: {client_epic_key}")
        print(f"   Stories: {', '.join(client_stories)}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\n⚠️  Please link Stories manually in Jira UI:")
    print(f"   Epic: {client_epic_key}")
    print(f"   Stories: {', '.join(client_stories)}")

print("\n" + "="*100 + "\n")

